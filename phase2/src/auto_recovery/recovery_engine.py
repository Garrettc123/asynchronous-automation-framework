"""
Phase 2: Auto-Recovery Engine
Detects system failures and automatically recovers from them.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    RESTART = "restart"
    FAILOVER = "failover"
    SCALE_UP = "scale_up"
    CIRCUIT_BREAK = "circuit_break"
    ALERT = "alert"


@dataclass
class HealthCheck:
    name: str
    check_fn: Callable
    interval: float = 30.0
    timeout: float = 5.0
    failure_threshold: int = 3
    recovery_threshold: int = 2


@dataclass
class ServiceState:
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check: float = field(default_factory=time.time)
    last_recovery: Optional[float] = None
    recovery_count: int = 0


class AutoRecoveryEngine:
    """Monitors services and automatically recovers from failures."""

    def __init__(self):
        self._health_checks: Dict[str, HealthCheck] = {}
        self._service_states: Dict[str, ServiceState] = {}
        self._recovery_handlers: Dict[RecoveryAction, Callable] = {}
        self._active = False
        self._recovery_log: List[Dict[str, Any]] = []

    def register_health_check(self, check: HealthCheck):
        """Register a health check for a service."""
        self._health_checks[check.name] = check
        self._service_states[check.name] = ServiceState(name=check.name)
        logger.info(f"Registered health check: {check.name}")

    def register_recovery_handler(self, action: RecoveryAction, handler: Callable):
        """Register a handler for a recovery action."""
        self._recovery_handlers[action] = handler

    async def start(self):
        """Start the auto-recovery engine."""
        self._active = True
        logger.info("Auto-Recovery Engine started")
        await asyncio.gather(*[
            self._run_check_loop(name, check)
            for name, check in self._health_checks.items()
        ])

    async def stop(self):
        """Stop the auto-recovery engine."""
        self._active = False
        logger.info("Auto-Recovery Engine stopped")

    async def _run_check_loop(self, name: str, check: HealthCheck):
        """Run periodic health checks for a service."""
        while self._active:
            await self._perform_check(name, check)
            await asyncio.sleep(check.interval)

    async def _perform_check(self, name: str, check: HealthCheck):
        """Execute a single health check."""
        state = self._service_states[name]
        try:
            if asyncio.iscoroutinefunction(check.check_fn):
                result = await asyncio.wait_for(check.check_fn(), timeout=check.timeout)
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, check.check_fn),
                    timeout=check.timeout,
                )
            if result:
                state.consecutive_failures = 0
                state.consecutive_successes += 1
                if (state.status != HealthStatus.HEALTHY
                        and state.consecutive_successes >= check.recovery_threshold):
                    state.status = HealthStatus.HEALTHY
                    logger.info(f"Service {name} recovered to HEALTHY")
            else:
                state.consecutive_successes = 0
                state.consecutive_failures += 1
                await self._evaluate_recovery(name, check, state)
        except asyncio.TimeoutError:
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            logger.warning(f"Health check timeout for {name}")
            await self._evaluate_recovery(name, check, state)
        except Exception as e:
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            logger.error(f"Health check error for {name}: {e}")
            await self._evaluate_recovery(name, check, state)
        finally:
            state.last_check = time.time()

    async def _evaluate_recovery(self, name: str, check: HealthCheck, state: ServiceState):
        """Evaluate whether recovery action is needed."""
        if state.consecutive_failures >= check.failure_threshold:
            old_status = state.status
            state.status = HealthStatus.CRITICAL
            if old_status != HealthStatus.CRITICAL:
                logger.warning(f"Service {name} is CRITICAL after {state.consecutive_failures} failures")
                await self._trigger_recovery(name, state)
        elif state.consecutive_failures > 0:
            state.status = HealthStatus.DEGRADED

    async def _trigger_recovery(self, name: str, state: ServiceState):
        """Trigger recovery actions for a failed service."""
        action = RecoveryAction.RESTART
        state.last_recovery = time.time()
        state.recovery_count += 1

        log_entry = {
            "service": name,
            "action": action.value,
            "timestamp": state.last_recovery,
            "recovery_count": state.recovery_count,
        }
        self._recovery_log.append(log_entry)
        logger.info(f"Triggering {action.value} for {name} (attempt #{state.recovery_count})")

        if action in self._recovery_handlers:
            try:
                handler = self._recovery_handlers[action]
                if asyncio.iscoroutinefunction(handler):
                    await handler(name)
                else:
                    handler(name)
            except Exception as e:
                logger.error(f"Recovery handler failed for {name}: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get current health status of all monitored services."""
        statuses = {
            name: {
                "status": state.status.value,
                "consecutive_failures": state.consecutive_failures,
                "recovery_count": state.recovery_count,
                "last_check": state.last_check,
            }
            for name, state in self._service_states.items()
        }
        overall = (
            HealthStatus.HEALTHY.value
            if all(s.status == HealthStatus.HEALTHY for s in self._service_states.values())
            else HealthStatus.DEGRADED.value
        )
        return {"overall": overall, "services": statuses, "recovery_log": self._recovery_log[-10:]}
