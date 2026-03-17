"""Tests for Phase 2: Auto-Recovery Engine"""
import asyncio
import time
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase2.src.auto_recovery.recovery_engine import (
    AutoRecoveryEngine, HealthCheck, RecoveryAction, HealthStatus, ServiceState
)


def test_import_recovery_engine():
    """Test that recovery engine can be imported."""
    assert AutoRecoveryEngine is not None
    assert HealthCheck is not None
    assert RecoveryAction is not None
    assert HealthStatus is not None


def test_health_status_enum():
    """Test HealthStatus enum values."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.CRITICAL.value == "critical"
    assert HealthStatus.UNKNOWN.value == "unknown"


def test_recovery_action_enum():
    """Test RecoveryAction enum values."""
    assert RecoveryAction.RESTART.value == "restart"
    assert RecoveryAction.FAILOVER.value == "failover"


def test_register_health_check():
    """Test registering a health check."""
    engine = AutoRecoveryEngine()
    check = HealthCheck(name="test_service", check_fn=lambda: True)
    engine.register_health_check(check)
    assert "test_service" in engine._health_checks
    assert "test_service" in engine._service_states


def test_get_system_health_initial():
    """Test initial system health state."""
    engine = AutoRecoveryEngine()
    check = HealthCheck(name="svc_a", check_fn=lambda: True)
    engine.register_health_check(check)
    health = engine.get_system_health()
    assert "overall" in health
    assert "services" in health
    assert "svc_a" in health["services"]


@pytest.mark.asyncio
async def test_perform_check_healthy():
    """Test that a passing health check marks service healthy."""
    engine = AutoRecoveryEngine()
    check = HealthCheck(name="ok_service", check_fn=lambda: True, recovery_threshold=1)
    engine.register_health_check(check)
    await engine._perform_check("ok_service", check)
    state = engine._service_states["ok_service"]
    assert state.consecutive_successes >= 1
    assert state.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_perform_check_failure():
    """Test that a failing health check increments failure counter."""
    engine = AutoRecoveryEngine()
    check = HealthCheck(name="bad_service", check_fn=lambda: False, failure_threshold=1)
    engine.register_health_check(check)
    await engine._perform_check("bad_service", check)
    state = engine._service_states["bad_service"]
    assert state.consecutive_failures >= 1


@pytest.mark.asyncio
async def test_trigger_recovery():
    """Test that recovery action is triggered and logged."""
    engine = AutoRecoveryEngine()
    check = HealthCheck(name="failing_svc", check_fn=lambda: False, failure_threshold=1)
    engine.register_health_check(check)
    state = engine._service_states["failing_svc"]
    state.consecutive_failures = 1
    await engine._trigger_recovery("failing_svc", state)
    assert len(engine._recovery_log) == 1
    assert engine._recovery_log[0]["service"] == "failing_svc"


def test_register_recovery_handler():
    """Test registering a recovery handler."""
    engine = AutoRecoveryEngine()
    handler = lambda name: None
    engine.register_recovery_handler(RecoveryAction.RESTART, handler)
    assert RecoveryAction.RESTART in engine._recovery_handlers
