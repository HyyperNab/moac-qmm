"""FastAPI service layer for MOAC QMM.

Full-stack surface: exposes the engine, the homeostasis optimizer and
the neural PK predictor over HTTP with seeded, deterministic runs.

Install with ``pip install 'moac-qmm[api]'`` and run with
``uvicorn moac_qmm.api:app``.

SPOF #39 eliminated: the kernel had no machine-to-machine surface;
every consumer had to be a Python process. The API is optional (extra)
so the core install stays dependency-light.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError

from moac_qmm import QMMEngine, StableHomeostasisOptimizer, __version__
from moac_qmm.deep_learning import NeuralPKPredictor

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MOAC QMM API",
    version=__version__,
    description=(
        "Strata-Oblivion Kernel — 29-dimensional medical decision engine. "
        "Research and educational simulation only. NOT A MEDICAL DEVICE."
    ),
)


class SimulateRequest(BaseModel):
    """Engine simulation request."""

    telemetry: dict[str, Any] = Field(default_factory=dict)
    seed: int = Field(42, ge=0, le=2**32 - 1)


class OptimizeRequest(BaseModel):
    """Homeostasis optimizer request."""

    telemetry: dict[str, Any] = Field(default_factory=dict)


class PredictRequest(BaseModel):
    """Neural PK prediction request."""

    features: dict[str, Any] = Field(default_factory=dict)
    seed: int = Field(42, ge=0, le=2**32 - 1)


def _parse_or_422(telemetry: dict[str, Any]) -> None:
    """Fail closed on invalid telemetry with a clean 422."""
    from moac_qmm.types import PatientTelemetry

    try:
        PatientTelemetry(**telemetry)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    """Readiness probe."""
    return {"status": "ready", "version": __version__}


@app.get("/version")
def version() -> dict[str, str]:
    """Kernel version."""
    return {"version": __version__}


@app.post("/v1/simulate")
def simulate(request: SimulateRequest) -> dict[str, Any]:
    """Run the full 29-dimensional tensor collision.

    Returns the result dict. Kernel aborts surface as HTTP 200 with an
    ``error`` field (matching the library contract); invalid telemetry
    returns HTTP 422.
    """
    _parse_or_422(request.telemetry)
    engine = QMMEngine(request.telemetry, seed=request.seed)
    return engine.execute()


@app.post("/v1/optimize")
def optimize(request: OptimizeRequest) -> dict[str, Any]:
    """Compute the stable homeostasis vector (prescriptions)."""
    _parse_or_422(request.telemetry)
    return StableHomeostasisOptimizer.calculate_optimal_vector(request.telemetry)


@app.post("/v1/predict")
def predict(request: PredictRequest) -> dict[str, Any]:
    """Run neural PK prediction (heuristic fallback when untrained)."""
    predictor = NeuralPKPredictor(seed=request.seed)
    return predictor.predict(request.features)


__all__ = ["app"]
