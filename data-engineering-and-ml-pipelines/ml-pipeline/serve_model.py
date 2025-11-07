"""Serve a trained model with FastAPI.

Start (from repo root):
    uvicorn serve_model:app --reload --app-dir data-engineering-and-ml-pipelines/ml-pipeline
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
from fastapi import FastAPI, HTTPException, Query


ROOT = Path(__file__).resolve().parent
MODEL_FP = ROOT / "model_store" / "model.json"

app = FastAPI(title="Widgetizer ML Demo", version="0.1.0")


def load_model() -> dict:
    if not MODEL_FP.exists():
        raise FileNotFoundError("Model file not found. Train it first (train_model.py)")
    return json.loads(MODEL_FP.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/predict")
def predict(x: float = Query(..., description="Input feature value")) -> dict:
    try:
        model = load_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    m = float(model.get("slope", 0.0))
    b = float(model.get("intercept", 0.0))
    y = m * x + b
    return {"x": x, "y": y, "model": {"slope": m, "intercept": b}}
