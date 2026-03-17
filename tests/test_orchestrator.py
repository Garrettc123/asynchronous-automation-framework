"""Tests for the Unified Orchestration Layer"""
import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.main import FrameworkOrchestrator
from phase3.src.workflow_engine.orchestrator import (
    WorkflowDefinition, TaskNode, TaskType, ExecutionStrategy
)


def test_import_orchestrator():
    """Test that FrameworkOrchestrator can be imported."""
    assert FrameworkOrchestrator is not None


def test_orchestrator_instantiation():
    """Test that all components are initialized."""
    orch = FrameworkOrchestrator()
    assert orch.recovery_engine is not None
    assert orch.workflow_executor is not None
    assert orch.task_scheduler is not None
    assert orch.event_bus is not None
    assert orch.ml_optimizer is not None


@pytest.mark.asyncio
async def test_orchestrator_start_stop():
    """Test starting and stopping the orchestrator."""
    orch = FrameworkOrchestrator()
    await orch.start()
    assert orch._active is True
    assert orch._start_time is not None
    await asyncio.sleep(0.1)
    await orch.stop()
    assert orch._active is False


@pytest.mark.asyncio
async def test_orchestrator_run_workflow():
    """Test running a workflow through the orchestrator."""
    orch = FrameworkOrchestrator()
    await orch.start()

    workflow = WorkflowDefinition(workflow_id="orch-test-001")
    workflow.add_task(TaskNode(task_id="step1", task_name="Step 1", task_type=TaskType.SEQUENTIAL))
    workflow.add_task(TaskNode(task_id="step2", task_name="Step 2", task_type=TaskType.SEQUENTIAL, dependencies=["step1"]))

    result = await orch.run_workflow(workflow)
    assert result["tasks_completed"] == 2

    await asyncio.sleep(0.1)
    await orch.stop()


@pytest.mark.asyncio
async def test_orchestrator_get_status():
    """Test getting the unified system status."""
    orch = FrameworkOrchestrator()
    await orch.start()
    await asyncio.sleep(0.05)

    status = orch.get_status()
    assert "phases" in status
    assert "phase1_revenue_agent" in status["phases"]
    assert "phase2_auto_recovery" in status["phases"]
    assert "phase3_dag_workflows" in status["phases"]
    assert "phase4_event_ml" in status["phases"]

    await orch.stop()


@pytest.mark.asyncio
async def test_orchestrator_event_bus_integration():
    """Test event bus subscription from orchestrator."""
    orch = FrameworkOrchestrator()
    await orch.start()

    # Publish a task.feedback event and verify ML optimizer receives it
    await orch.event_bus.publish("task.feedback", {
        "task_id": "integration_test",
        "actual_duration": 20.0,
        "predicted_duration": 15.0,
    })
    await asyncio.sleep(0.2)

    stats = orch.ml_optimizer.get_stats()
    assert stats["feedback_count"] >= 1

    await orch.stop()
