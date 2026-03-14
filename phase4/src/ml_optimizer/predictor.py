"""
Phase 4: ML-Powered Predictive Resource Optimization
Optimizes task allocation and ML models based on live event streams.
"""
import logging
import math
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    task_id: str
    predicted_duration: float
    cpu_limit: str
    memory_limit: str
    timeout: int
    confidence: float
    timestamp: float = field(default_factory=time.time)


class ResourceOptimizer:
    """Linear-regression-based resource optimizer that learns from feedback."""

    def __init__(self):
        self.model_weights = {"cpu": 0.5, "mem": 0.3, "complexity": 2.5, "data_size": 0.1}
        self._feedback_history: List[Dict[str, Any]] = []
        self._prediction_count = 0

    def predict_duration(self, task_features: Dict[str, Any]) -> float:
        """Predict task execution duration using learned weights."""
        base_time = 10.0
        complexity = task_features.get("complexity", 1)
        data_size = task_features.get("data_size", 0)
        cpu_cores = task_features.get("cpu_cores", 1)
        cpu_factor = 1.0 / max(cpu_cores, 1)
        duration = base_time + (complexity * self.model_weights["complexity"]) + (data_size * self.model_weights["data_size"])
        duration *= cpu_factor
        return max(duration, 1.0)

    def optimize_allocation(self, task_features: Dict[str, Any]) -> OptimizationResult:
        """Determine optimal resource allocation for a task."""
        duration = self.predict_duration(task_features)
        complexity = task_features.get("complexity", 1)
        self._prediction_count += 1

        cpu_limit = "250m" if complexity < 2 else ("500m" if complexity < 5 else "1000m")
        memory_limit = "128Mi" if complexity < 2 else ("256Mi" if complexity < 5 else "512Mi")
        confidence = min(0.95, 0.5 + (len(self._feedback_history) * 0.01))

        return OptimizationResult(
            task_id=task_features.get("task_id", "unknown"),
            predicted_duration=round(duration, 2),
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            timeout=int(duration * 1.5),
            confidence=round(confidence, 3),
        )

    def record_feedback(self, task_id: str, actual_duration: float, predicted_duration: float):
        """Record actual vs predicted duration to improve future predictions."""
        error = actual_duration - predicted_duration
        self._feedback_history.append({
            "task_id": task_id,
            "actual": actual_duration,
            "predicted": predicted_duration,
            "error": error,
            "timestamp": time.time(),
        })
        # Simple online learning: adjust complexity weight
        if len(self._feedback_history) > 5:
            recent = self._feedback_history[-5:]
            avg_error = sum(f["error"] for f in recent) / len(recent)
            adjustment = avg_error * 0.01
            self.model_weights["complexity"] = max(0.1, self.model_weights["complexity"] + adjustment)

    def get_stats(self) -> Dict[str, Any]:
        """Return optimizer statistics."""
        if not self._feedback_history:
            return {"predictions": self._prediction_count, "feedback_count": 0, "mae": None}
        errors = [abs(f["error"]) for f in self._feedback_history]
        mae = sum(errors) / len(errors)
        return {
            "predictions": self._prediction_count,
            "feedback_count": len(self._feedback_history),
            "mae": round(mae, 4),
            "weights": self.model_weights,
        }
