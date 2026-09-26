# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 29.1.x  | ✅ |
| < 29.1  | ❌ (single-file v28 artifact is reference-only) |

## Reporting a Vulnerability

Report vulnerabilities privately via
[GitHub security advisories](https://github.com/HyyperNab/moac-qmm/security/advisories/new).
Please do not open public issues for security problems. Expect a response
within 7 days.

## Hardening posture

- **No pickle, no eval, no shell-outs** anywhere in the kernel. Model
  persistence is JSON (`NeuralPKPredictor.save/load`).
- **No network calls** in the core engine or CLI.
- **No secrets** are required or stored. No environment variables are
  mandatory.
- **No filesystem writes** unless explicitly configured: the engine writes
  nothing; `OutcomeTracker(log_path=...)` writes JSONL only where told to.
- **Input validation**: all telemetry passes through pydantic
  `PatientTelemetry` (fail-closed, HTTP 422 at the API layer).
- **Dependency surface** is minimal by design: core requires numpy + pydantic
  only. CLI/API extras add click/rich and fastapi/uvicorn.

## Threat notes for API deployments

- The simulate endpoints are CPU-bound (Monte Carlo). Deploy behind rate
  limiting; `n_simulations` is capped by the schema (≤ 100,000) and `seed`
  is bounded (≤ 2³²−1).
- The API is stateless — no patient data is stored. If *you* log request
  bodies, patient telemetry is PHI under GDPR/HIPAA: handle accordingly.
