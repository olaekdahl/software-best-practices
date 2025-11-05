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
    from fastapi import FastAPI, HTTPException, Header, Depends, Body, Response
    from fastapi.responses import JSONResponse, PlainTextResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
    import uvicorn
except Exception:
    FastAPI = object  # type: ignore
    HTTPException = Exception  # type: ignore
    Header = lambda *a, **k: None  # type: ignore
    JSONResponse = dict  # type: ignore
    Response = object  # type: ignore
    PlainTextResponse = dict  # type: ignore
    HTTPBearer = object  # type: ignore
    HTTPAuthorizationCredentials = object  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda *a, **k: None  # type: ignore
    uvicorn = None  # type: ignore


class JobRequest(BaseModel):
    dataset: str = Field(..., description="Dataset identifier")
    model: str = Field(..., description="Model to run")


class JobResponse(BaseModel):
    id: str
    dataset: str
    model: str
    status: str
    created_at: float


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
    app = FastAPI(title="Jobs API (lab)", version="0.1.0")
    store = Store()
    bearer_scheme = HTTPBearer(auto_error=False)

    @app.post("/jobs", response_model=JobResponse)
    def submit_job(
        response: Response,
        payload: JobRequest,
        idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
        auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    ):
        # Simple auth requirement to match bearerAuth in OpenAPI (no validation for demo)
        if auth is None:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

        job, created = store.create_or_get(idempotency_key, payload.dataset, payload.model)
        # Set dynamic status code while letting FastAPI serialize the dict per response_model
        if response is not None:
            response.status_code = 201 if created else 200
        return job

    @app.get("/jobs/{job_id}", response_model=JobResponse)
    def get_job(job_id: str, auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)):
        if auth is None:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        job = store.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Not found")
        return job

    # Override OpenAPI to inject license/servers/security to align with linted spec
    original_openapi = app.openapi

    def custom_openapi():
        schema = original_openapi()
        # License
        schema.setdefault("info", {}).setdefault("license", {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        })
        # Servers
        schema["servers"] = [
            {"url": "https://api.mycompany.com", "description": "Production"},
            {"url": "https://staging.mycompany.com", "description": "Staging"},
        ]
        # Security Schemes and global requirement
        components = schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes.setdefault("bearerAuth", {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        })
        schema["security"] = [{"bearerAuth": []}]
        return schema

    app.openapi = custom_openapi  # type: ignore

    @app.get("/openapi.yaml", response_class=PlainTextResponse, include_in_schema=False)
    def openapi_yaml():
        try:
            import yaml  # type: ignore
        except Exception:  # pragma: no cover
            raise HTTPException(status_code=500, detail="PyYAML not installed")
        return PlainTextResponse(yaml.safe_dump(app.openapi(), sort_keys=False), media_type="application/yaml")

    return app


# Expose a module-level `app` so `uvicorn app:app` works
app = create_app()

if __name__ == "__main__" and uvicorn is not None:
    # Use import string for proper reload support (avoids uvicorn warning)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
