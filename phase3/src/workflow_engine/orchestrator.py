"""
Phase 3: Workflow Orchestration Engine - DAG-based task execution
"""
import asyncio
import logging
import time
from collections import defaultdict, deque
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    BRANCH = "branch"
    JOIN = "join"
    TRIGGER = "trigger"


class ExecutionStrategy(Enum):
    EAGER = "eager"
    PRIORITY = "priority"
    BATCH = "batch"
    LAZY = "lazy"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskNode:
    task_id: str
    task_name: str
    task_type: TaskType
    handler: Any = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 1
    timeout: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None


@dataclass
class WorkflowDefinition:
    workflow_id: str
    tasks: Dict[str, TaskNode] = field(default_factory=dict)
    execution_strategy: ExecutionStrategy = ExecutionStrategy.EAGER
    max_parallel_tasks: int = 10

    def add_task(self, task: TaskNode):
        self.tasks[task.task_id] = task

    def validate(self):
        """Validate that the workflow DAG has no cycles."""
        visited = set()
        stack = set()
        for task_id in self.tasks:
            if task_id not in visited:
                if self._detect_cycle(task_id, visited, stack):
                    return False, "Circular dependency detected"
        # Check all dependencies reference existing tasks
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    return False, f"Task {task_id} depends on unknown task {dep}"
        return True, None

    def _detect_cycle(self, v, visited, stack):
        visited.add(v)
        stack.add(v)
        for neighbor in self.tasks[v].dependencies:
            if neighbor not in visited:
                if self._detect_cycle(neighbor, visited, stack):
                    return True
            elif neighbor in stack:
                return True
        stack.remove(v)
        return False

    def topological_sort(self) -> List[List[str]]:
        """Return tasks grouped into parallel execution waves via Kahn's algorithm."""
        in_degree: Dict[str, int] = {t: 0 for t in self.tasks}
        dependents: Dict[str, List[str]] = defaultdict(list)

        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                in_degree[task_id] += 1
                dependents[dep].append(task_id)

        waves: List[List[str]] = []
        queue = deque([t for t, d in in_degree.items() if d == 0])
        while queue:
            wave = list(queue)
            waves.append(wave)
            queue.clear()
            for task_id in wave:
                for dependent in dependents[task_id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        return waves


class WorkflowExecutor:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute a workflow using topological sort for correct dependency ordering."""
        logger.info(f"Executing workflow: {workflow.workflow_id}")
        valid, error = workflow.validate()
        if not valid:
            raise ValueError(error)

        waves = workflow.topological_sort()
        results: Dict[str, TaskResult] = {}

        for wave_idx, wave in enumerate(waves):
            logger.debug(f"Executing wave {wave_idx}: {wave}")
            wave_tasks = [
                self._execute_task(workflow.tasks[task_id], results)
                for task_id in wave
            ]
            wave_results = await asyncio.gather(*wave_tasks, return_exceptions=True)
            for task_id, result in zip(wave, wave_results):
                if isinstance(result, Exception):
                    results[task_id] = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        error=str(result),
                    )
                else:
                    results[task_id] = result

        completed = sum(1 for r in results.values() if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in results.values() if r.status == TaskStatus.FAILED)

        return {
            "workflow_id": workflow.workflow_id,
            "status": "completed" if failed == 0 else "partial_failure",
            "tasks_executed": len(results),
            "tasks_completed": completed,
            "tasks_failed": failed,
            "results": {tid: {"status": r.status.value, "error": r.error} for tid, r in results.items()},
        }

    async def _execute_task(self, task: TaskNode, prior_results: Dict[str, TaskResult]) -> TaskResult:
        """Execute a single task with semaphore limiting concurrency.

        Args:
            task: The task node to execute.
            prior_results: Results from previously completed tasks, available
                           for handlers that need upstream outputs (e.g. fan-in joins).

        Note: task.timeout applies to the handler execution only, not semaphore
        wait time. Under heavy load, tasks may queue waiting for the semaphore.
        """
        result = TaskResult(task_id=task.task_id, status=TaskStatus.RUNNING)
        async with self._semaphore:
            try:
                if task.handler is not None:
                    if asyncio.iscoroutinefunction(task.handler):
                        output = await asyncio.wait_for(task.handler(), timeout=task.timeout)
                    else:
                        output = task.handler()
                else:
                    output = {"task": task.task_id, "simulated": True}
                result.status = TaskStatus.COMPLETED
                result.output = output
            except asyncio.TimeoutError:
                result.status = TaskStatus.FAILED
                result.error = f"Task {task.task_id} timed out after {task.timeout}s"
            except Exception as e:
                result.status = TaskStatus.FAILED
                result.error = str(e)
            finally:
                result.end_time = time.time()
                result.duration = result.end_time - result.start_time
        return result
