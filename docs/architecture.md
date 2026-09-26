# Architecture

## The layer model

```
┌──────────────────────────────────────────────────────────────┐
│  Consumers                                                   │
│  cli.py (click + rich)      api.py (FastAPI)   library API   │
└──────────────┬────────────────────┬────────────────┬──────────┘
               │                    │                │
┌──────────────▼────────────────────▼────────────────▼──────────┐
│  engine.py — QMMEngine (25-phase tensor collision)            │
│  · validates telemetry (PatientTelemetry, pydantic)            │
│  · injects one seeded numpy Generator (SPOF #32)               │
│  · emits structured phase events + logging (SPOF #33)          │
│  · compiles the Ragnar state string → SHA-256 seal             │
└──────┬───────────────────────────────────┬────────────────────┘
       │                                   │
┌──────▼──────────────────┐   ┌────────────▼───────────────────┐
│  models/ (23 tensors)   │   │  deep_learning/ (5 modules)    │
│  genomic, clearance,    │   │  neural_pk (MC-Dropout MLP)    │
│  ddi, quantum_receptor, │   │  bayesian_calibration          │
│  cytokine, vagal, hpa,  │   │  adaptive_payoff               │
│  hypoxia, microbiome,  │   │  rl_optimizer (Q-learning)     │
│  nutrients, chrono,    │   │  outcome_tracker (JSONL)        │
│  epigenetic, autophagy,│   └─────────────────────────────────┘
│  pk_solver (2-comp),   │
│  sleep, toxins,        │   ┌─────────────────────────────────┐
│  organ_crosstalk, nti, │   │  constants.py + evidence.py     │
│  game_theory,          │   │  every constant carries an      │
│  anti_persona, qsense  │   │  honest provenance tier         │
└───────────────────────┘   └─────────────────────────────────┘
```

## Engine pipeline

`QMMEngine.execute()` runs 25 phases. Each phase appends a structured event
`{"phase": n, "title": ..., "lines": [...]}` to `result["events"]` and logs at
INFO; models emit WARN/CRITICAL via standard `logging` only (no `print`
side-effects — SPOF #33).

| Phase | Computation | Kernel exceptions |
|------:|-------------|-------------------|
| 1 | Genomic PK modifier + allele prior | — |
| 2 | Neural PK (optional, heuristic fallback) | — |
| 3 | Renal/hepatic clearance + organ risk | `StrataRejection` |
| 4 | Toxin CYP derate, CYP2E1, GSH | `ToxinOverloadKill` |
| 5 | Hypoxia CYP derate, anaerobic shift, HIF-1α | `HypoxiaCascade` |
| 6 | HPA circadian cortisol, allostatic load | `StrataRejection` |
| 7 | Organ crosstalk cascade | `OrganCrosstalkFailure` |
| 8 | DDI (CYP competition, albumin displacement) | `StrataRejection` |
| 9 | Chrono efficacy + immune modulation | — |
| 10 | Microbiome bioavailability + PPI shift | — |
| 11 | Epigenetic repair velocity + tissue mode | — |
| 12 | Sleep: GH pulse, glymphatic, consolidation | — |
| 13 | Cytokine ODE (6 h integration) | `CytokineStormDetected` |
| 14 | Vagal tone → spasm modification | — |
| 15 | Nutrient restitution capacity (Liebig) | — |
| 16 | Composite restitution | — |
| 17 | Quantum receptor Monte Carlo | `QuantumReceptorFailure` (opt-in strict) |
| 18 | 2-compartment PK + therapeutic window | — |
| 19 | NTI warfarin/digoxin checks | `NTIToxicityKill` |
| 20 | Anti-persona escape + Nash/minimax | `EdgeCaseCascade`, `PathogenDominanceNash` |
| 21 | RL pre-training + recommendation | — |
| 22 | Bayesian calibration summary | — |
| 23 | Lagom throttle | — |
| 24 | Ragnar compilation + SHA-256 seal | — |
| 25 | Outcome tracking (single log) | — |

Kernel exceptions are caught by `execute()` and returned as
`{"error": ...}` (or re-raised with `raise_on_abort=True`).

## Determinism

All stochastic components (receptor Monte Carlo, RL exploration, MC-Dropout)
draw from injected `numpy.random.Generator` instances seeded from the
engine's `seed` parameter. **Same (telemetry, seed) → same hash.** The global
`numpy.random` state is never touched (SPOF #32).

## Interface freeze

`manifest.py` freezes the exported names of every public module.
`scripts/validate_manifest.py` and `tests/test_manifest.py` fail the build on
drift — the interface gate between kernel generations.

## Production rules

1. **No print** — logging only. Console rendering belongs to the CLI.
2. **No global RNG** — inject `numpy.random.Generator`.
3. **No silent persistence** — `OutcomeTracker` writes only when given a path.
4. **No pickle** — model persistence is JSON (SPOF #38).
5. **No wildcard imports** — explicit symbols only.
6. **No fabricated citations** — constants carry honest evidence tiers.
7. **Single version source** — `moac_qmm/_version.py`.
