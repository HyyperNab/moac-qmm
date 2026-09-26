"""MOAC QMM live-demo API — Vercel serverless (FastAPI/ASGI).

Runs the REAL Strata-Oblivion Kernel (vendored ``api/moac_qmm`` package)
inside a serverless function. The same engine, constants and physics as
the GitHub package — not a mock.

Public-internet hardening (this endpoint is world-reachable):
- Monte Carlo work caps: n_simulations ≤ 4_000, n_receptors ≤ 40_000
  (the schema already bounds telemetry; caps are re-applied defensively)
- engine aborts return 200 + ``error`` field (library contract)
- invalid telemetry returns 422
- stateless: nothing is persisted, nothing is logged about patients
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError

from moac_qmm import QMMEngine, StableHomeostasisOptimizer, __version__
from moac_qmm.types import PatientTelemetry

MAX_TELEMETRY_KEYS = 80
CAP_N_SIMULATIONS = 4_000
CAP_N_RECEPTORS = 40_000

app = FastAPI(
    title="MOAC QMM Live Demo API",
    version=__version__,
    description=(
        "Strata-Oblivion Kernel — 29-dimensional medical decision engine. "
        "Research and educational simulation only. NOT A MEDICAL DEVICE."
    ),
)


class SimulateRequest(BaseModel):
    telemetry: dict[str, Any] = Field(default_factory=dict)
    seed: int = Field(42, ge=0, le=2**32 - 1)


class OptimizeRequest(BaseModel):
    telemetry: dict[str, Any] = Field(default_factory=dict)


def _validated(telemetry: dict[str, Any]) -> PatientTelemetry:
    """Fail closed on oversized or invalid telemetry with a clean 422."""
    if len(telemetry) > MAX_TELEMETRY_KEYS:
        raise HTTPException(
            status_code=422,
            detail=f"telemetry exceeds {MAX_TELEMETRY_KEYS} keys",
        )
    try:
        model = PatientTelemetry(**telemetry)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422, detail=exc.errors(include_url=False)
        ) from exc

    # Public-endpoint compute caps (defensive re-application)
    model.n_simulations = min(model.n_simulations, CAP_N_SIMULATIONS)
    model.n_receptors = min(model.n_receptors, CAP_N_RECEPTORS)
    return model


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness + version probe."""
    return {"status": "ok", "version": __version__}


@app.post("/api/simulate")
def simulate(request: SimulateRequest) -> dict[str, Any]:
    """Run the full 25-phase tensor collision."""
    model = _validated(request.telemetry)
    engine = QMMEngine(model, seed=request.seed)
    result = engine.execute()
    # Events carry no sensitive data and keep the payload compact enough;
    # trim the PK curve arrays (engine does not expose them) — nothing to do.
    return result


@app.post("/api/optimize")
def optimize(request: OptimizeRequest) -> dict[str, Any]:
    """Reverse-engineer the stable homeostasis vector (prescriptions)."""
    model = _validated(request.telemetry)
    return StableHomeostasisOptimizer.calculate_optimal_vector(model)
