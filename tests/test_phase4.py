"""Tests for Phase 4: Event-Driven ML Optimization"""
import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase4.src.event_bus.bus import EventBus, Event
from phase4.src.ml_optimizer.predictor import ResourceOptimizer, OptimizationResult


def test_import_event_bus():
    """Test that EventBus can be imported."""
    assert EventBus is not None
    assert Event is not None


def test_import_resource_optimizer():
    """Test that ResourceOptimizer can be imported."""
    assert ResourceOptimizer is not None
    assert OptimizationResult is not None


def test_event_dataclass():
    """Test Event dataclass creation."""
    event = Event(event_type="test.event", payload={"key": "value"})
    assert event.event_type == "test.event"
    assert event.payload == {"key": "value"}
    assert event.event_id is not None
    assert event.timestamp > 0


def test_event_bus_subscribe():
    """Test subscribing to event types."""
    bus = EventBus()
    handler = lambda event: None
    bus.subscribe("test.event", handler)
    assert "test.event" in bus._subscribers
    assert handler in bus._subscribers["test.event"]


def test_event_bus_unsubscribe():
    """Test unsubscribing from event types."""
    bus = EventBus()
    handler = lambda event: None
    bus.subscribe("test.event", handler)
    bus.unsubscribe("test.event", handler)
    assert handler not in bus._subscribers.get("test.event", [])


@pytest.mark.asyncio
async def test_event_bus_publish_and_receive():
    """Test that published events are received by subscribers."""
    bus = EventBus()
    received = []

    async def handler(event):
        received.append(event)

    bus.subscribe("data.ready", handler)
    await bus.start()
    await bus.publish("data.ready", {"value": 42})
    await asyncio.sleep(0.2)
    await bus.stop()

    assert len(received) == 1
    assert received[0].payload["value"] == 42


@pytest.mark.asyncio
async def test_event_bus_wildcard_subscriber():
    """Test wildcard '*' subscriber catches all events."""
    bus = EventBus()
    all_events = []

    async def catch_all(event):
        all_events.append(event.event_type)

    bus.subscribe("*", catch_all)
    await bus.start()
    await bus.publish("event.a", {})
    await bus.publish("event.b", {})
    await asyncio.sleep(0.2)
    await bus.stop()

    assert "event.a" in all_events
    assert "event.b" in all_events


def test_event_bus_get_stats():
    """Test event bus statistics."""
    bus = EventBus()
    stats = bus.get_stats()
    assert "processed" in stats
    assert "errors" in stats
    assert "queue_size" in stats


def test_event_bus_get_history():
    """Test event history is initially empty."""
    bus = EventBus()
    history = bus.get_history()
    assert isinstance(history, list)


def test_resource_optimizer_predict_duration():
    """Test duration prediction."""
    optimizer = ResourceOptimizer()
    duration = optimizer.predict_duration({"complexity": 1})
    assert duration > 0
    duration_high = optimizer.predict_duration({"complexity": 10})
    assert duration_high > duration


def test_resource_optimizer_optimize_allocation():
    """Test resource allocation optimization."""
    optimizer = ResourceOptimizer()
    result = optimizer.optimize_allocation({"task_id": "t1", "complexity": 3})
    assert isinstance(result, OptimizationResult)
    assert result.cpu_limit in ("250m", "500m", "1000m")
    assert result.timeout > 0
    assert 0 < result.confidence <= 1.0


def test_resource_optimizer_record_feedback():
    """Test feedback recording for online learning."""
    optimizer = ResourceOptimizer()
    optimizer.record_feedback("t1", actual_duration=15.0, predicted_duration=12.0)
    stats = optimizer.get_stats()
    assert stats["feedback_count"] == 1


def test_resource_optimizer_stats():
    """Test optimizer statistics."""
    optimizer = ResourceOptimizer()
    stats = optimizer.get_stats()
    assert "predictions" in stats
    assert "feedback_count" in stats
    assert "mae" in stats
