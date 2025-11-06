"""Minimal ML pipeline: generate data, train simple linear regression, save model.

No external ML libraries required. Uses closed-form simple linear regression.

Run:
  python3 data-engineering-and-ml-pipelines/ml-pipeline/train_model.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import random
from statistics import mean
import json
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
STORE = ROOT / "model_store"
STORE.mkdir(parents=True, exist_ok=True)


@dataclass
class SimpleLinearModel:
    slope: float
    intercept: float

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept


def generate_data(n: int = 200) -> tuple[list[float], list[float]]:
    xs = [random() * 10 for _ in range(n)]
    ys = [3.0 * x + 2.0 + (random() - 0.5) * 0.8 for x in xs]
    return xs, ys


def fit_simple_linear_regression(xs: list[float], ys: list[float]) -> SimpleLinearModel:
    x_bar = mean(xs)
    y_bar = mean(ys)
    num = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys))
    den = sum((x - x_bar) ** 2 for x in xs) or 1e-12
    slope = num / den
    intercept = y_bar - slope * x_bar
    return SimpleLinearModel(slope=slope, intercept=intercept)


def save_model(model: SimpleLinearModel, fp: Path) -> None:
    dt = datetime.now(timezone.utc)
    payload = {
        "type": "simple_linear_regression",
        "slope": round(model.slope, 6),
        "intercept": round(model.intercept, 6),
        "created_at": dt.isoformat().replace("+00:00", "Z"),
    }
    with fp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main() -> None:
    xs, ys = generate_data()
    model = fit_simple_linear_regression(xs, ys)
    out = STORE / "model.json"
    save_model(model, out)
    print(f"Saved model to {out} (slope={model.slope:.3f}, intercept={model.intercept:.3f})")


if __name__ == "__main__":
    main()
