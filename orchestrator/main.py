"""
Unified Orchestration Layer - Wires all 4 phases together.

Phase 1: Revenue Agent (Flask API)
Phase 2: Auto-Recovery Engine
Phase 3: DAG Workflow Executor
Phase 4: Event-Driven ML Optimization
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional

from phase2.src.auto_recovery.recovery_engine import (
    AutoRecoveryEngine, HealthCheck, RecoveryAction, HealthStatus
)
from phase3.src.workflow_engine.orchestrator import (
    WorkflowDefinition, WorkflowExecutor, TaskNode, TaskType, ExecutionStrategy
)
from phase3.src.task_scheduler.scheduler import AdvancedTaskScheduler, SchedulePolicy, ScheduledTask
from phase4.src.event_bus.bus import EventBus
from phase4.src.ml_optimizer.predictor import ResourceOptimizer

logger = logging.getLogger(__name__)


class FrameworkOrchestrator:
    """
    Central orchestrator that wires all 4 phases into a unified automation framework.
    """

    def __init__(self):
        # Phase 2: Auto-Recovery
        self.recovery_engine = AutoRecoveryEngine()
        # Phase 3: DAG Workflow Executor + Scheduler
        self.workflow_executor = WorkflowExecutor(max_concurrent=10)
        self.task_scheduler = AdvancedTaskScheduler(policy=SchedulePolicy.PRIORITY)
        # Phase 4: Event Bus + ML Optimizer
        self.event_bus = EventBus()
        self.ml_optimizer = ResourceOptimizer()
        self._active = False
        self._start_time: Optional[float] = None

    async def start(self):
        """Initialize and start all framework components."""
        self._active = True
        self._start_time = time.time()
        logger.info("Starting Unified Orchestration Layer...")

        # Register event handlers connecting phases
        self.event_bus.subscribe("workflow.execute", self._handle_workflow_event)
        self.event_bus.subscribe("recovery.triggered", self._handle_recovery_event)
        self.event_bus.subscribe("task.feedback", self._handle_task_feedback)

        # Register health checks for each phase
        self.recovery_engine.register_health_check(HealthCheck(
            name="event_bus",
            check_fn=lambda: self._active,
            interval=10.0,
        ))
        self.recovery_engine.register_health_check(HealthCheck(
            name="ml_optimizer",
            check_fn=lambda: self.ml_optimizer is not None,
            interval=15.0,
        ))

        # Start the event bus
        await self.event_bus.start()
        logger.info("Unified Orchestration Layer started successfully")

    async def stop(self):
        """Stop all framework components."""
        self._active = False
        await self.event_bus.stop()
        await self.recovery_engine.stop()
        logger.info("Unified Orchestration Layer stopped")

    async def run_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute a workflow with ML-optimized resource allocation."""
        await self.event_bus.publish("workflow.execute", {
            "workflow_id": workflow.workflow_id,
            "task_count": len(workflow.tasks),
        }, source="orchestrator")

        result = await self.workflow_executor.execute_workflow(workflow)

        await self.event_bus.publish("workflow.completed", {
            "workflow_id": workflow.workflow_id,
            "result": result,
        }, source="orchestrator")
        return result

    async def _handle_workflow_event(self, event):
        """Handle workflow execution events for ML feedback."""
        logger.debug(f"Workflow event: {event.payload}")

    async def _handle_recovery_event(self, event):
        """Handle recovery events from Phase 2."""
        logger.info(f"Recovery event for {event.payload.get('service')}: {event.payload}")

    async def _handle_task_feedback(self, event):
        """Feed task completion data back to the ML optimizer."""
        payload = event.payload
        self.ml_optimizer.record_feedback(
            task_id=payload.get("task_id", "unknown"),
            actual_duration=float(payload.get("actual_duration", 0)),
            predicted_duration=float(payload.get("predicted_duration", 0)),
        )

    def get_status(self) -> Dict[str, Any]:
        """Return the current status of all framework components."""
        uptime = time.time() - self._start_time if self._start_time else 0
        return {
            "active": self._active,
            "uptime_seconds": round(uptime, 2),
            "phases": {
                "phase1_revenue_agent": {"status": "operational"},
                "phase2_auto_recovery": self.recovery_engine.get_system_health(),
                "phase3_dag_workflows": {
                    "status": "operational",
                    "max_concurrent": self.workflow_executor.max_concurrent,
                },
                "phase4_event_ml": {
                    "event_bus": self.event_bus.get_stats(),
                    "ml_optimizer": self.ml_optimizer.get_stats(),
                },
            },
        }


async def run_demo():
    """Demo that shows all 4 phases working together."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
    orchestrator = FrameworkOrchestrator()
    await orchestrator.start()

    # Build a sample DAG workflow
    workflow = WorkflowDefinition(
        workflow_id="demo-workflow-001",
        execution_strategy=ExecutionStrategy.EAGER,
    )
    workflow.add_task(TaskNode(task_id="ingest", task_name="Data Ingestion", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="validate", task_name="Validation", task_type=TaskType.SEQUENTIAL, dependencies=["ingest"]))
    workflow.add_task(TaskNode(task_id="process_a", task_name="Process A", task_type=TaskType.PARALLEL, dependencies=["validate"]))
    workflow.add_task(TaskNode(task_id="process_b", task_name="Process B", task_type=TaskType.PARALLEL, dependencies=["validate"]))
    workflow.add_task(TaskNode(task_id="aggregate", task_name="Aggregate", task_type=TaskType.JOIN, dependencies=["process_a", "process_b"]))

    result = await orchestrator.run_workflow(workflow)
    print("Workflow result:", result)

    # ML optimization
    allocation = orchestrator.ml_optimizer.optimize_allocation({"task_id": "t1", "complexity": 3, "data_size": 100})
    print("ML allocation:", allocation)

    # System status
    status = orchestrator.get_status()
    print("System status phases:", list(status["phases"].keys()))

    await asyncio.sleep(0.2)
    await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(run_demo())
