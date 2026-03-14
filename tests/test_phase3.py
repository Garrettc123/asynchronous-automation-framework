"""Tests for Phase 3: DAG Workflow Orchestration"""
import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase3.src.workflow_engine.orchestrator import (
    WorkflowDefinition, WorkflowExecutor, TaskNode, TaskType,
    ExecutionStrategy, TaskStatus
)
from phase3.src.task_scheduler.scheduler import (
    AdvancedTaskScheduler, SchedulePolicy, ScheduledTask, ResourceRequirement, ResourceType
)


def test_import_orchestrator():
    """Test that orchestrator can be imported."""
    assert WorkflowDefinition is not None
    assert WorkflowExecutor is not None


def test_task_type_enum():
    """Test TaskType enum values."""
    assert TaskType.SEQUENTIAL.value == "sequential"
    assert TaskType.PARALLEL.value == "parallel"


def test_execution_strategy_enum():
    """Test ExecutionStrategy enum values."""
    assert ExecutionStrategy.EAGER.value == "eager"
    assert ExecutionStrategy.PRIORITY.value == "priority"


def test_workflow_add_task():
    """Test adding tasks to a workflow."""
    workflow = WorkflowDefinition(workflow_id="test-wf-001")
    task = TaskNode(task_id="t1", task_name="Task 1", task_type=TaskType.SEQUENTIAL)
    workflow.add_task(task)
    assert "t1" in workflow.tasks


def test_workflow_validate_valid():
    """Test that a valid DAG passes validation."""
    workflow = WorkflowDefinition(workflow_id="valid-wf")
    workflow.add_task(TaskNode(task_id="a", task_name="A", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="b", task_name="B", task_type=TaskType.SEQUENTIAL, dependencies=["a"]))
    valid, error = workflow.validate()
    assert valid is True
    assert error is None


def test_workflow_validate_cycle():
    """Test that a cyclic dependency is detected."""
    workflow = WorkflowDefinition(workflow_id="cycle-wf")
    workflow.add_task(TaskNode(task_id="a", task_name="A", task_type=TaskType.SEQUENTIAL, dependencies=["b"]))
    workflow.add_task(TaskNode(task_id="b", task_name="B", task_type=TaskType.SEQUENTIAL, dependencies=["a"]))
    valid, error = workflow.validate()
    assert valid is False
    assert error is not None


def test_workflow_topological_sort():
    """Test topological sort produces correct wave ordering."""
    workflow = WorkflowDefinition(workflow_id="topo-wf")
    workflow.add_task(TaskNode(task_id="a", task_name="A", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="b", task_name="B", task_type=TaskType.SEQUENTIAL, dependencies=["a"]))
    workflow.add_task(TaskNode(task_id="c", task_name="C", task_type=TaskType.SEQUENTIAL, dependencies=["a"]))
    workflow.add_task(TaskNode(task_id="d", task_name="D", task_type=TaskType.SEQUENTIAL, dependencies=["b", "c"]))
    waves = workflow.topological_sort()
    # a must be in first wave
    assert "a" in waves[0]
    # d must be in last wave
    assert "d" in waves[-1]
    # b and c should be in the same intermediate wave
    flat = [t for wave in waves for t in wave]
    assert flat.index("b") > flat.index("a")
    assert flat.index("c") > flat.index("a")
    assert flat.index("d") > flat.index("b")
    assert flat.index("d") > flat.index("c")


@pytest.mark.asyncio
async def test_execute_simple_workflow():
    """Test executing a simple linear workflow."""
    workflow = WorkflowDefinition(workflow_id="exec-wf-001")
    workflow.add_task(TaskNode(task_id="t1", task_name="Task 1", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="t2", task_name="Task 2", task_type=TaskType.SEQUENTIAL, dependencies=["t1"]))
    executor = WorkflowExecutor(max_concurrent=5)
    result = await executor.execute_workflow(workflow)
    assert result["tasks_executed"] == 2
    assert result["tasks_completed"] == 2
    assert result["tasks_failed"] == 0


@pytest.mark.asyncio
async def test_execute_parallel_workflow():
    """Test executing a workflow with parallel tasks."""
    workflow = WorkflowDefinition(workflow_id="parallel-wf")
    workflow.add_task(TaskNode(task_id="root", task_name="Root", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="p1", task_name="Parallel 1", task_type=TaskType.PARALLEL, dependencies=["root"]))
    workflow.add_task(TaskNode(task_id="p2", task_name="Parallel 2", task_type=TaskType.PARALLEL, dependencies=["root"]))
    workflow.add_task(TaskNode(task_id="join", task_name="Join", task_type=TaskType.JOIN, dependencies=["p1", "p2"]))
    executor = WorkflowExecutor()
    result = await executor.execute_workflow(workflow)
    assert result["tasks_executed"] == 4
    assert result["tasks_completed"] == 4


@pytest.mark.asyncio
async def test_execute_workflow_with_handler():
    """Test executing a workflow where tasks have handlers."""
    call_order = []

    async def task_a():
        call_order.append("a")
        return "result_a"

    async def task_b():
        call_order.append("b")
        return "result_b"

    workflow = WorkflowDefinition(workflow_id="handler-wf")
    workflow.add_task(TaskNode(task_id="a", task_name="A", task_type=TaskType.SEQUENTIAL, handler=task_a))
    workflow.add_task(TaskNode(task_id="b", task_name="B", task_type=TaskType.SEQUENTIAL, handler=task_b, dependencies=["a"]))
    executor = WorkflowExecutor()
    result = await executor.execute_workflow(workflow)
    assert result["tasks_completed"] == 2
    assert call_order == ["a", "b"]


def test_task_scheduler_import():
    """Test that task scheduler can be imported."""
    assert AdvancedTaskScheduler is not None


@pytest.mark.asyncio
async def test_schedule_task():
    """Test scheduling a task."""
    scheduler = AdvancedTaskScheduler(policy=SchedulePolicy.PRIORITY)
    task = ScheduledTask(task_id="sched-t1", priority=5)
    await scheduler.schedule_task(task)
    assert scheduler.queue.qsize() == 1
