#!/usr/bin/env python3
from __future__ import annotations
"""
Tiny Jobs API to support the Architecture and API Design lab.
- POST /jobs with Idempotency-Key header creates or returns an existing job
- GET /jobs/{id} returns the job or 404
"""
import time
import uuid
from typing import Dict, Optional

try:
    from fastapi import FastAPI, HTTPException, Header
    from fastapi.responses import JSONResponse
    import uvicorn
except Exception:
    FastAPI = object  # type: ignore
    HTTPException = Exception  # type: ignore
    Header = lambda *a, **k: None  # type: ignore
    JSONResponse = dict  # type: ignore
    uvicorn = None  # type: ignore


class Store:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict] = {}
        self._idem: Dict[str, str] = {}

    def create_or_get(self, idem_key: str, dataset: str, model: str) -> tuple[Dict, bool]:
        if idem_key in self._idem:
            job_id = self._idem[idem_key]
            return self._jobs[job_id], False
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "dataset": dataset,
            "model": model,
            "status": "PENDING",
            "created_at": time.time(),
        }
        self._jobs[job_id] = job
        self._idem[idem_key] = job_id
        return job, True

    def get(self, job_id: str) -> Optional[Dict]:
        return self._jobs.get(job_id)


def create_app() -> FastAPI:
    app = FastAPI(title="Jobs API (lab)")
    store = Store()

    @app.post("/jobs")
    def submit_job(
        payload: Dict,
        idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    ):
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

        # Complete code per lab instructions
        return payload

    @app.get("/jobs/{job_id}")
    def get_job(job_id: str):
        # Complete code per lab instructions
        return job_id

    return app


# Expose a module-level `app` so `uvicorn app:app` works
app = create_app()

if __name__ == "__main__" and uvicorn is not None:
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
