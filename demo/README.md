# MOAC QMM — Live Demo (Vercel)

A one-page interactive demo of the **real** MOAC QMM v29.1.0 kernel: the
actual Python engine runs in a Vercel serverless function (FastAPI/ASGI +
numpy + pydantic, uv-managed). No mocks, no pre-recorded results — every
collision you run is computed live and deterministic by seed.

```
demo/
├── index.py             # FastAPI entrypoint (auto-detected by Vercel)
├── moac_qmm/            # vendored kernel package (verbatim copy of src/moac_qmm)
├── public/              # static → served from the Vercel CDN
│   ├── index.html       # landing page: intro, how-it-works, disclaimer, demo
│   └── assets/
│       ├── style.css    # design system (no frameworks)
│       └── app.js       # demo client: presets, API calls, phase-trace renderer
├── pyproject.toml       # dependencies (uv/Vercel Python flow)
├── uv.lock              # reproducible dependency lock
├── requirements.txt     # pip fallback for local dev
└── README.md
```

Zero-config: no `vercel.json` needed. Vercel detects the FastAPI app at
`index.py`, installs from `pyproject.toml`/`uv.lock`, and serves
`public/` from the CDN.

## Deploy

```bash
cd demo
vercel deploy --prod          # logged in
# or, without an account:
vercel deploy --temporary    # live URL, claimable for 60 minutes
```

## Local development

```bash
cd demo
uvicorn index:app --reload --port 8000
# API at http://localhost:8000/api/health
# note: public/ is Vercel-CDN behaviour — use `vercel dev` for full fidelity
```

## Serverless hardening

- Monte Carlo work caps: `n_simulations ≤ 4000`, `n_receptors ≤ 40 000`
- telemetry body capped at 80 keys; pydantic validation → HTTP 422
- engine aborts return 200 + `error` field (library contract)
- stateless: no persistence, no patient-data logging, no cookies
- deterministic: same telemetry + seed → same Ragnar hash, local or live

## Sync the vendored kernel

After changing the package, refresh the vendored copy:

```bash
rm -rf demo/moac_qmm
cp -r src/moac_qmm demo/moac_qmm
find demo/moac_qmm -name __pycache__ -type d -exec rm -rf {} +
```

⚠️ **Not a medical device** — research and educational simulation only.
