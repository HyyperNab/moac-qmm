# MOAC QMM — Strata-Oblivion Kernel

> A 29-dimensional medical decision engine that collides pharmacogenomics,
> thermodynamics, game-theoretic infectiology and deep learning into a single
> deterministic homeostasis vector. Zero assumptions. Zero Single Points of Failure.

[![CI](https://github.com/HyyperNab/moac-qmm/actions/workflows/ci.yml/badge.svg)](https://github.com/HyyperNab/moac-qmm/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)
[![Not a medical device](https://img.shields.io/badge/NOT%20A%20MEDICAL%20DEVICE-red)](https://github.com/HyyperNab/moac-qmm#%EF%B8%8F-medical-disclaimer)

---

## ⚠️ Medical Disclaimer

This software is a **research and educational simulation tool**. It is **not**
a medical device, not FDA-approved, not CE-marked, and must **never** be used
for clinical decision-making. Every biophysical constant in this kernel is an
unverified modelling assumption — see [docs/EVIDENCE.md](docs/EVIDENCE.md).
Always consult a licensed physician.

---

## Overview

Traditional medical models assume an "average patient" with static
pharmacokinetics. This is a **Single Point of Failure (SPOF)** — the #1 cause
of treatment failure in patients with pharmacogenomic edge cases.

MOAC QMM replaces linear pathways with a **29-dimensional tensor matrix**
that simultaneously calculates interactions across every biological variable:

| # | Dimension | Module |
|---|-----------|--------|
| 1 | Pharmacogenomics | `GenomicTensor` |
| 2-3 | Renal/Hepatic Clearance + Vd | `RenalHepaticClearance` |
| 4 | Protein Binding DDI | `DrugDrugInteractionTensor` |
| 5 | Quantum Receptor Binding (MC) | `QuantumDrugReceptor` |
| 6 | Cytokine Storm (ODE) | `CytokineStormVector` |
| 7 | Vagal Tone | `VagalToneVoltage` |
| 8 | HPA Axis (circadian) | `HPAAxisModel` |
| 9 | Hypoxia / HIF-1α | `HypoxiaTensor` |
| 10 | Microbiome | `MicrobiomeMetabolizer` |
| 11 | Nutrient Substrates (Liebig) | `NutrientSubstrateMatrix` |
| 12 | Chronopharmacology | `ChronopharmacologyModulator` |
| 13 | Epigenetic Age | `EpigeneticAgeClock` |
| 14 | Autophagy/Apoptosis (mTOR/AMPK) | `AutophagyApoptosisToggle` |
| 15-16 | Multi-Compartment PK (2-comp ODE) | `MultiCompartmentPK` |
| 17 | Sleep Architecture (N3/GH/glymphatic) | `SleepArchitectureTensor` |
| 18 | Exogenous Toxins | `ExogenousToxinLoad` |
| 19 | Organ Crosstalk (cascade graph) | `OrganCrosstalkTensor` |
| 20 | Narrow Therapeutic Index | `NarrowTherapeuticIndexEngine` |
| 21 | Game-Theoretic Pathogen (5×5, Nash/minimax) | `PathogenGameTheory` |
| 22 | Anti-Persona Escape (5 vectors) | `AntiPersonaEscapeV2` |
| 23 | Allele Frequency Priors + Ledger | `SpofLedger` |
| 24 | Neural PK Prediction (MC-Dropout MLP) | `NeuralPKPredictor` |
| 25 | Bayesian Calibration (conjugate) | `BayesianCalibration` |
| 26 | Adaptive Payoff Matrix | `AdaptivePayoffMatrix` |
| 27 | RL Treatment Optimizer (Q-learning) | `ReinforcementLearningOptimizer` |
| 28 | Outcome Tracking | `OutcomeTracker` |
| 29 | Uncertainty Quantification | deep learning layer |

The v28 payoff matrix deliberately contains **no pure Nash equilibrium** —
against a strategic pathogen there is no stable deterministic treatment. The
engine recommends the minimax strategy (`BIOFILM_DISRUPT` for the default
matrix) and learns payoffs from outcomes.

## Installation

```bash
pip install moac-qmm            # core: numpy + pydantic only
pip install 'moac-qmm[cli]'     # + rich terminal output
pip install 'moac-qmm[api]'     # + FastAPI service layer
```

From source:

```bash
git clone https://github.com/HyyperNab/moac-qmm.git
cd moac-qmm
pip install -e ".[dev]"
```

## Quick Start

```python
from moac_qmm import QMMEngine

telemetry = {
    "genetics": {"CYP2C19": "*17/*17"},
    "primary_drug": "Esomeprazole",
    "primary_drug_class": "PPI",
    "drug_params": {"dose": 40, "kd": 0.8, "protein_bound": 0.95,
                    "vd": 0.25, "cyp_pathway": ["CYP2C19"]},
    "drug_stack": [{"name": "Esomeprazole", "protein_bound": 0.95,
                    "cyp_pathway": ["CYP2C19"]}],
    "gfr": 72, "albumin": 3.2, "current_ph": 3.5,
    "spo2": 94.0, "hrv_rmssd": 18.0, "hour": 22.0,
    "pathogen_name": "Helicobacter pylori",
    "pathogen_k": 0.3, "immune_v": 1.2,
    "exposure_hours": 18, "pathogen_strategy": "BIOFILM_FORTIFY",
    "age": 52, "biological_age": 61,
}

engine = QMMEngine(telemetry, seed=42)
result = engine.execute()

if "error" in result:
    print(f"Engine aborted: {result['error']}")
else:
    print(f"Ragnar hash: {result['hash']}")
    print(f"Receptor occupancy: {result['receptor_occupancy']['mean_occupancy']:.1%}")
    print(f"Restitution: {result['restitution']:.3f}")
    # Full phase trace:
    for event in result["events"]:
        print(f"Phase {event['phase']:>2}: {event['title']}")
```

Runs are **deterministic** for a given `(telemetry, seed)` pair — the same
input always produces the same Ragnar hash.

## CLI

```bash
# Full 25-phase simulation with rich phase trace
moac-qmm run --telemetry patient.json --seed 42 --output result.json

# Reverse-engineer the stable homeostasis vector (prescriptions)
moac-qmm optimize --telemetry patient.json

# Neural PK prediction (heuristic fallback when untrained)
moac-qmm predict --features patient_features.json
```

## REST API

```bash
pip install 'moac-qmm[api]'
uvicorn moac_qmm.api:app --port 8000
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Liveness probe |
| `/readyz` | GET | Readiness probe (+version) |
| `/version` | GET | Kernel version |
| `/v1/simulate` | POST | Full 29-dimensional collision |
| `/v1/optimize` | POST | Homeostasis prescriptions |
| `/v1/predict` | POST | Neural PK prediction |

```bash
curl -X POST localhost:8000/v1/simulate \
  -H 'Content-Type: application/json' \
  -d '{"telemetry": {"gfr": 90, "current_ph": 5.0}, "seed": 42}'
```

Invalid telemetry → HTTP 422. Kernel aborts → HTTP 200 with an `error` field
(matching the library contract). Interactive docs at `/docs`.

## Deep Learning Layer

```python
from moac_qmm.deep_learning import (
    NeuralPKPredictor, BayesianCalibration,
    AdaptivePayoffMatrix, ReinforcementLearningOptimizer, OutcomeTracker,
)

predictor = NeuralPKPredictor(seed=42)
# Train on (n, 10) features → (n, 3) targets: clearance, t_half, vd
predictor.train(X, y, epochs=200)
pk = predictor.predict({"age": 52, "gfr": 72, "cyp2c19_activity": 0.35})
# → clearance_rate, t_half, vd + per-output MC-Dropout uncertainty + confidence
```

Enable inside the engine via telemetry flags: `use_neural_pk`,
`use_bayesian_calibration`, `use_adaptive_payoff`, `use_rl_optimizer`.

## Testing & Quality Gates

```bash
make test          # pytest + coverage
make lint          # ruff check
make type-check    # mypy
make manifest      # frozen API surface gate
make build         # sdist + wheel
```

CI runs ruff + mypy + pytest on Python 3.10/3.11/3.12 across
Linux/macOS/Windows on every push and PR.

## Documentation

- [Architecture](docs/architecture.md) — engine pipeline and model layer
- [SPOF Register](docs/spof_register.md) — every eliminated failure mode
- [Deep Learning](docs/deep_learning.md) — the v29 learning layer
- [API Reference](docs/api_reference.md) — REST endpoints
- [Evidence Register](docs/EVIDENCE.md) — per-constant provenance tiers
- [CHANGELOG](CHANGELOG.md)

## Provenance

The v28 single-file kernel is preserved verbatim in
[`legacy/moac_qmm_v28.py`](legacy/moac_qmm_v28.py) for reference. The
production package is a faithful port — same physics, same constants, same
phase semantics — hardened for production (see the
[SPOF register](docs/spof_register.md)).

## Limitations

- All biophysical constants are **unverified kernel assumptions** (see the
  [evidence register](docs/EVIDENCE.md)) — the model is qualitative, not
  quantitative
- Cytokine ODE is first-order; no delay differential equations
- No drug-drug interaction database — hardcoded common interactions only
- Population allele frequencies are claimed (1000 Genomes / PharmGKB) but
  were not verified against those sources and vary by ancestry
- Two-compartment PK only; no biliary recirculation
- RL/Q-learning and payoff learning are in-memory per run unless you inject
  persistent `OutcomeTracker` / pre-trained models explicitly

## License

MIT — see [LICENSE](LICENSE).

## Contributing

PRs that eliminate new SPOFs are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md).
