# API Reference

Install and run:

```bash
pip install 'moac-qmm[api]'
uvicorn moac_qmm.api:app --host 0.0.0.0 --port 8000
```

Interactive OpenAPI docs: `http://localhost:8000/docs`

## Probes

### `GET /healthz`
Liveness probe. → `{"status": "ok"}`

### `GET /readyz`
Readiness probe. → `{"status": "ready", "version": "29.1.0"}`

### `GET /version`
→ `{"version": "29.1.0"}`

## Endpoints

### `POST /v1/simulate`

Runs the full 29-dimensional tensor collision.

Request:

```json
{
  "telemetry": { "gfr": 90, "current_ph": 5.0, "...": "..." },
  "seed": 42
}
```

Response (success): the full engine result — `pk_modifier`, `clearance`,
`toxin_derate`, `cyp_derate`, `allostatic_load`, `organ_states`,
`ddi_warnings`, `chrono_efficacy`, `bioavailability_modifier`,
`ppi_microbiome_shift`, `cytokine`, `restitution`, `receptor_occupancy`,
`pk_window`, `nti_warfarin?`, `nti_digoxin?`, `escape_vectors`,
`nash_equilibria`, `minimax`, `rl_recommendation?`, `calibration?`,
`lagom_stack_size`, `hash`, `version`, `compiled_state`,
`surviving_priors`, `events`.

Response (kernel abort): HTTP 200 with `{"error": "...", "version": "...",
"events": [...]}` — kernel aborts are *results*, not transport errors.

Errors: HTTP 422 when telemetry fails validation (pydantic errors).

### `POST /v1/optimize`

Request: `{"telemetry": {...}}`

Response: the prescription set from the `StableHomeostasisOptimizer` —
category → {current, target, interventions}. Empty object when the telemetry
is already stable.

### `POST /v1/predict`

Request: `{"features": {"age": 52, "gfr": 72, "...": "..."}, "seed": 42}`

Response: neural PK prediction — `clearance_rate`, `t_half`, `vd`, per-output
`*_uncertainty`, `confidence`, `n_mc_samples`, and `heuristic: true` when the
untrained biophysical fallback was used.

## Determinism

Every stochastic component is seeded from the request's `seed` (default 42).
The same request body always yields the same `hash`.
