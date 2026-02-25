"""
Demo 04 - ML Model Lifecycle
===============================
Demonstrates model training, validation, versioning, and monitoring.

Instructor talking points:
- Model lifecycle: train -> validate -> deploy -> monitor
- Track experiments with parameters, metrics, and artifacts
- Validation gates before deployment
- Monitor for data drift and performance degradation
- Reproducibility via versioned data + code + config

Run: python main.py
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ============================================================================
# Simple ML model (no external deps needed)
# ============================================================================

@dataclass
class Dataset:
    """A labeled dataset for training and evaluation."""
    name: str
    features: list[list[float]]
    labels: list[float]
    version: str = "1.0"

    @property
    def size(self) -> int:
        return len(self.labels)

    def split(self, ratio: float = 0.8) -> tuple[Dataset, Dataset]:
        """Split dataset into train and test sets."""
        n = int(self.size * ratio)
        return (
            Dataset(f"{self.name}_train", self.features[:n], self.labels[:n], self.version),
            Dataset(f"{self.name}_test", self.features[n:], self.labels[n:], self.version),
        )


class LinearModel:
    """Simple linear regression model for demo purposes."""

    def __init__(self):
        self.weights: list[float] = []
        self.bias: float = 0.0
        self.is_trained: bool = False

    def train(self, features: list[list[float]], labels: list[float],
              learning_rate: float = 0.001, epochs: int = 100) -> dict:
        """Train model using gradient descent."""
        n_features = len(features[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        n = len(labels)

        history = {"loss": []}

        for epoch in range(epochs):
            # Forward pass
            total_loss = 0.0
            grad_w = [0.0] * n_features
            grad_b = 0.0

            for i in range(n):
                pred = sum(w * x for w, x in zip(self.weights, features[i])) + self.bias
                error = pred - labels[i]
                total_loss += error ** 2

                for j in range(n_features):
                    grad_w[j] += (2 / n) * error * features[i][j]
                grad_b += (2 / n) * error

            # Update weights
            for j in range(n_features):
                self.weights[j] -= learning_rate * grad_w[j]
            self.bias -= learning_rate * grad_b

            mse = total_loss / n
            history["loss"].append(mse)

        self.is_trained = True
        return history

    def predict(self, features: list[list[float]]) -> list[float]:
        """Make predictions."""
        return [
            sum(w * x for w, x in zip(self.weights, f)) + self.bias
            for f in features
        ]


# ============================================================================
# Experiment tracking
# ============================================================================

@dataclass
class Experiment:
    """Tracks a single ML experiment."""
    id: str
    model_name: str
    parameters: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    dataset_version: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "RUNNING"
    artifacts: list[str] = field(default_factory=list)

    def log_metric(self, name: str, value: float) -> None:
        self.metrics[name] = round(value, 6)

    def log_param(self, name: str, value: Any) -> None:
        self.parameters[name] = value


class ExperimentTracker:
    """Registry for ML experiments (like MLflow/W&B)."""

    def __init__(self):
        self.experiments: list[Experiment] = []

    def create(self, model_name: str) -> Experiment:
        exp_id = f"exp-{len(self.experiments) + 1:03d}"
        exp = Experiment(id=exp_id, model_name=model_name)
        self.experiments.append(exp)
        return exp

    def best_experiment(self, metric: str, lower_is_better: bool = True) -> Experiment | None:
        candidates = [e for e in self.experiments if metric in e.metrics and e.status == "COMPLETED"]
        if not candidates:
            return None
        return min(candidates, key=lambda e: e.metrics[metric] * (1 if lower_is_better else -1))

    def summary(self) -> str:
        lines = [
            f"{'ID':<10} {'Model':<20} {'Status':<12} {'MSE':>10} {'MAE':>10} {'R2':>8}",
            f"{'-'*10} {'-'*20} {'-'*12} {'-'*10} {'-'*10} {'-'*8}",
        ]
        for exp in self.experiments:
            mse = exp.metrics.get("mse", "-")
            mae = exp.metrics.get("mae", "-")
            r2 = exp.metrics.get("r2", "-")
            mse_str = f"{mse:.6f}" if isinstance(mse, float) else str(mse)
            mae_str = f"{mae:.6f}" if isinstance(mae, float) else str(mae)
            r2_str = f"{r2:.4f}" if isinstance(r2, float) else str(r2)
            lines.append(
                f"{exp.id:<10} {exp.model_name:<20} {exp.status:<12} "
                f"{mse_str:>10} {mae_str:>10} {r2_str:>8}"
            )
        return "\n".join(lines)


# ============================================================================
# Validation gates
# ============================================================================

@dataclass
class ValidationGate:
    """A gate that must pass before model deployment."""
    name: str
    check: str  # metric comparison
    threshold: float
    passed: bool = False
    actual_value: float = 0.0

    def evaluate(self, metrics: dict) -> bool:
        metric_name, operator = self.check.rsplit("_", 1)
        value = metrics.get(metric_name, float("inf"))
        self.actual_value = value

        if operator == "lt":
            self.passed = value < self.threshold
        elif operator == "gt":
            self.passed = value > self.threshold
        elif operator == "lte":
            self.passed = value <= self.threshold
        else:
            self.passed = False

        return self.passed


def evaluate_deployment_gates(metrics: dict) -> list[ValidationGate]:
    """Check if model meets deployment criteria."""
    gates = [
        ValidationGate("MSE threshold", "mse_lt", 50.0),
        ValidationGate("MAE threshold", "mae_lt", 5.0),
        ValidationGate("R-squared minimum", "r2_gt", 0.8),
    ]

    for gate in gates:
        gate.evaluate(metrics)

    return gates


# ============================================================================
# Model monitoring (drift detection)
# ============================================================================

def detect_drift(
    reference_predictions: list[float],
    current_predictions: list[float],
    threshold: float = 0.1,
) -> dict:
    """Detect prediction drift between reference and current data."""
    ref_mean = sum(reference_predictions) / len(reference_predictions)
    cur_mean = sum(current_predictions) / len(current_predictions)

    ref_std = math.sqrt(sum((x - ref_mean) ** 2 for x in reference_predictions) / len(reference_predictions))
    cur_std = math.sqrt(sum((x - cur_mean) ** 2 for x in current_predictions) / len(current_predictions))

    mean_shift = abs(cur_mean - ref_mean) / (ref_std + 1e-10)
    std_ratio = cur_std / (ref_std + 1e-10)

    drift_detected = mean_shift > threshold * 10 or abs(std_ratio - 1.0) > threshold

    return {
        "reference_mean": round(ref_mean, 4),
        "current_mean": round(cur_mean, 4),
        "mean_shift_z": round(mean_shift, 4),
        "std_ratio": round(std_ratio, 4),
        "drift_detected": drift_detected,
        "action": "RETRAIN" if drift_detected else "OK",
    }


# ============================================================================
# Evaluation metrics
# ============================================================================

def compute_metrics(actual: list[float], predicted: list[float]) -> dict:
    """Compute regression metrics."""
    n = len(actual)
    errors = [a - p for a, p in zip(actual, predicted)]
    sq_errors = [e ** 2 for e in errors]
    abs_errors = [abs(e) for e in errors]

    mse = sum(sq_errors) / n
    mae = sum(abs_errors) / n
    rmse = math.sqrt(mse)

    actual_mean = sum(actual) / n
    ss_total = sum((a - actual_mean) ** 2 for a in actual)
    ss_residual = sum(sq_errors)
    r2 = 1 - (ss_residual / ss_total) if ss_total > 0 else 0.0

    return {"mse": mse, "mae": mae, "rmse": rmse, "r2": r2}


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Demo: ML Model Lifecycle ===\n")

    random.seed(42)

    # Generate synthetic data: y = 3*x1 + 2*x2 + noise
    n_samples = 200
    features = [[random.gauss(0, 1), random.gauss(0, 1)] for _ in range(n_samples)]
    labels = [3 * f[0] + 2 * f[1] + random.gauss(0, 0.5) for f in features]

    dataset = Dataset("sales_prediction", features, labels, version="1.0")
    train_data, test_data = dataset.split(0.8)

    print(f"  Dataset: {dataset.name} v{dataset.version}")
    print(f"  Total: {dataset.size}, Train: {train_data.size}, Test: {test_data.size}")
    print()

    # --- Experiment Tracking ---
    print("--- Experiment Tracking ---\n")
    tracker = ExperimentTracker()

    # Experiment 1: Low learning rate
    exp1 = tracker.create("linear_regression")
    exp1.log_param("learning_rate", 0.001)
    exp1.log_param("epochs", 50)
    exp1.dataset_version = dataset.version

    model1 = LinearModel()
    model1.train(train_data.features, train_data.labels, learning_rate=0.001, epochs=50)
    predictions1 = model1.predict(test_data.features)
    metrics1 = compute_metrics(test_data.labels, predictions1)
    for k, v in metrics1.items():
        exp1.log_metric(k, v)
    exp1.status = "COMPLETED"
    print(f"  {exp1.id}: lr=0.001, epochs=50 -> MSE={metrics1['mse']:.4f}, R2={metrics1['r2']:.4f}")

    # Experiment 2: Higher learning rate, more epochs
    exp2 = tracker.create("linear_regression")
    exp2.log_param("learning_rate", 0.01)
    exp2.log_param("epochs", 200)
    exp2.dataset_version = dataset.version

    model2 = LinearModel()
    model2.train(train_data.features, train_data.labels, learning_rate=0.01, epochs=200)
    predictions2 = model2.predict(test_data.features)
    metrics2 = compute_metrics(test_data.labels, predictions2)
    for k, v in metrics2.items():
        exp2.log_metric(k, v)
    exp2.status = "COMPLETED"
    print(f"  {exp2.id}: lr=0.01, epochs=200 -> MSE={metrics2['mse']:.4f}, R2={metrics2['r2']:.4f}")

    # Experiment 3: Optimal settings
    exp3 = tracker.create("linear_regression")
    exp3.log_param("learning_rate", 0.05)
    exp3.log_param("epochs", 500)
    exp3.dataset_version = dataset.version

    model3 = LinearModel()
    model3.train(train_data.features, train_data.labels, learning_rate=0.05, epochs=500)
    predictions3 = model3.predict(test_data.features)
    metrics3 = compute_metrics(test_data.labels, predictions3)
    for k, v in metrics3.items():
        exp3.log_metric(k, v)
    exp3.status = "COMPLETED"
    print(f"  {exp3.id}: lr=0.05, epochs=500 -> MSE={metrics3['mse']:.4f}, R2={metrics3['r2']:.4f}")
    print()

    print("--- Experiment Summary ---\n")
    print(tracker.summary())
    print()

    # --- Deployment Gates ---
    best = tracker.best_experiment("mse")
    if best:
        print(f"--- Deployment Gates (Best: {best.id}) ---\n")
        gates = evaluate_deployment_gates(best.metrics)
        all_passed = True
        for gate in gates:
            status = "PASS" if gate.passed else "FAIL"
            print(f"  [{status}] {gate.name}: {gate.actual_value:.4f} "
                  f"{'<' if 'lt' in gate.check else '>'} {gate.threshold}")
            if not gate.passed:
                all_passed = False

        print()
        if all_passed:
            print(f"  Model {best.id} APPROVED for deployment")
        else:
            print(f"  Model {best.id} BLOCKED - gates not met")
    print()

    # --- Monitoring / Drift Detection ---
    print("--- Model Monitoring (Drift Detection) ---\n")

    # Normal predictions (no drift)
    normal_features = [[random.gauss(0, 1), random.gauss(0, 1)] for _ in range(100)]
    normal_preds = model3.predict(normal_features)

    drift_result = detect_drift(predictions3, normal_preds)
    print(f"  Normal traffic: {drift_result}")

    # Drifted predictions (shifted distribution)
    drifted_features = [[random.gauss(5, 2), random.gauss(3, 2)] for _ in range(100)]
    drifted_preds = model3.predict(drifted_features)

    drift_result = detect_drift(predictions3, drifted_preds)
    print(f"  Drifted traffic: {drift_result}")

    print("\n--- ML Lifecycle Best Practices ---")
    print("1. Track ALL experiments: params, metrics, data version")
    print("2. Deployment gates: no model goes live without passing checks")
    print("3. Version data alongside code and config")
    print("4. Monitor for drift: distributions shift in production")
    print("5. Automate retraining triggers when drift is detected")
    print("6. A/B test new models before full rollout")


if __name__ == "__main__":
    main()
