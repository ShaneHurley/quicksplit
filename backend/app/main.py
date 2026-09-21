"""
Application entrypoint.

Serves the REST API under /api/v1. Static SPA mounting arrives in Phase 7.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, profiles, sets, study
from app.db.session import init_db

app = FastAPI(title="QuickSplit", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router, prefix="/api/v1")
app.include_router(sets.router, prefix="/api/v1")
app.include_router(study.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# Create tables at import time so TestClient and scripts work without lifespan.
init_db()


@app.on_event("startup")
def on_startup() -> None:
    """Re-assert schema on process boot (uvicorn workers / packaged binary)."""
    init_db()


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    """Liveness probe used by install checks and packaging."""
    return {"status": "ok", "service": "quicksplit"}
