"""
Demo 04 - REST API Design with FastAPI
=======================================
Demonstrates proper API design: HTTP semantics, RFC 7807 errors,
cursor pagination, OpenAPI documentation, and versioning.

Instructor talking points:
- Correct HTTP methods and status codes
- RFC 7807 Problem Details for errors
- Cursor-based pagination for large datasets
- Auto-generated OpenAPI docs (Swagger UI at /docs)
- Input validation with Pydantic

Run:
    pip install fastapi uvicorn pydantic
    uvicorn app:app --reload
    # Then open http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Jobs API",
    version="1.0.0",
    docs_url="/swagger",
    description="Demo API showing best practices for REST design",
)


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------
class JobRequest(BaseModel):
    """Request to create a new job."""
    name: str = Field(..., min_length=1, max_length=200, description="Job name")
    priority: int = Field(default=1, ge=1, le=5, description="Priority 1-5")
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class JobResponse(BaseModel):
    """Response for a single job."""
    id: str
    name: str
    priority: int
    tags: list[str]
    status: str
    created_at: str


class PaginatedResponse(BaseModel):
    """Cursor-paginated list response."""
    data: list[JobResponse]
    next_cursor: str | None = None
    total: int


# ---------------------------------------------------------------------------
# RFC 7807 Problem Details
# ---------------------------------------------------------------------------
class ProblemDetail(BaseModel):
    """RFC 7807 error response."""
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
    code: str | None = None
    errors: list[dict[str, str]] | None = None


def problem_response(
    status_code: int,
    title: str,
    detail: str,
    code: str | None = None,
    errors: list[dict[str, str]] | None = None,
    instance: str | None = None,
) -> JSONResponse:
    """Return an RFC 7807 Problem Details response."""
    body = ProblemDetail(
        type=f"https://api.example.com/problems/{code or 'error'}",
        title=title,
        status=status_code,
        detail=detail,
        code=code,
        errors=errors,
        instance=instance,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


# ---------------------------------------------------------------------------
# In-memory store (for demo purposes)
# ---------------------------------------------------------------------------
JOBS: dict[str, dict[str, Any]] = {}


def seed_data():
    """Pre-populate some jobs for pagination demo."""
    for i in range(1, 26):
        job_id = str(uuid.uuid4())
        JOBS[job_id] = {
            "id": job_id,
            "name": f"Job {i:03d}",
            "priority": (i % 5) + 1,
            "tags": [f"tag-{i % 3}"],
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


seed_data()


# ---------------------------------------------------------------------------
# Cursor helpers
# ---------------------------------------------------------------------------
def encode_cursor(job_id: str) -> str:
    return base64.urlsafe_b64encode(json.dumps({"id": job_id}).encode()).decode()


def decode_cursor(cursor: str) -> str:
    return json.loads(base64.urlsafe_b64decode(cursor))["id"]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/v1/jobs", response_model=PaginatedResponse, tags=["Jobs"])
def list_jobs(
    limit: int = Query(default=10, ge=1, le=100, description="Page size"),
    cursor: str | None = Query(default=None, description="Pagination cursor"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status"),
):
    """List jobs with cursor-based pagination.

    Demonstrates:
    - Cursor pagination (no offset drift)
    - Query parameter filtering
    - Consistent response envelope
    """
    all_jobs = list(JOBS.values())

    # Apply filter
    if status_filter:
        all_jobs = [j for j in all_jobs if j["status"] == status_filter]

    # Apply cursor
    if cursor:
        try:
            after_id = decode_cursor(cursor)
            ids = [j["id"] for j in all_jobs]
            start_idx = ids.index(after_id) + 1
            all_jobs = all_jobs[start_idx:]
        except (ValueError, KeyError):
            return problem_response(400, "Bad Request", "Invalid cursor", code="invalid_cursor")

    total = len(all_jobs)
    page = all_jobs[:limit]
    next_cursor = encode_cursor(page[-1]["id"]) if len(all_jobs) > limit else None

    return PaginatedResponse(
        data=[JobResponse(**j) for j in page],
        next_cursor=next_cursor,
        total=total,
    )


@app.post("/v1/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED, tags=["Jobs"])
def create_job(req: JobRequest):
    """Create a new job.

    Demonstrates:
    - POST for creation
    - 201 Created status code
    - Pydantic validation with RFC 7807 error responses
    """
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "name": req.name,
        "priority": req.priority,
        "tags": req.tags,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    JOBS[job_id] = job
    return JobResponse(**job)


@app.get("/v1/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
def get_job(job_id: str):
    """Retrieve a single job by ID.

    Demonstrates:
    - GET for retrieval
    - 404 with RFC 7807 when not found
    """
    job = JOBS.get(job_id)
    if not job:
        return problem_response(
            404, "Not Found",
            f"Job {job_id} does not exist.",
            code="job_not_found",
            instance=f"/v1/jobs/{job_id}",
        )
    return JobResponse(**job)


@app.patch("/v1/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
def update_job(job_id: str, updates: dict[str, Any]):
    """Partially update a job.

    Demonstrates:
    - PATCH for partial updates
    - Field-level validation errors in RFC 7807
    """
    job = JOBS.get(job_id)
    if not job:
        return problem_response(
            404, "Not Found", f"Job {job_id} does not exist.",
            code="job_not_found",
        )

    allowed = {"name", "priority", "tags", "status"}
    invalid = set(updates.keys()) - allowed
    if invalid:
        return problem_response(
            422, "Validation Failed",
            "One or more fields are invalid.",
            code="validation_failed",
            errors=[{"field": f, "message": "unknown field"} for f in invalid],
            instance=f"/v1/jobs/{job_id}",
        )

    valid_statuses = {"queued", "running", "completed", "failed"}
    if "status" in updates and updates["status"] not in valid_statuses:
        return problem_response(
            422, "Validation Failed",
            f"status must be one of {valid_statuses}",
            code="validation_failed",
            errors=[{"field": "status", "message": f"must be one of {valid_statuses}"}],
        )

    job.update(updates)
    return JobResponse(**job)


@app.delete("/v1/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Jobs"])
def delete_job(job_id: str):
    """Delete a job.

    Demonstrates:
    - DELETE with 204 No Content
    - Idempotent (deleting non-existent returns 204)
    """
    JOBS.pop(job_id, None)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "jobs_count": len(JOBS)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
