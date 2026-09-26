# Changelog

All notable changes to MOAC QMM are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/).

## [29.1.0] — 2026-09-26

The production-hardening release. Same physics as v29.0.0, hardened into a
shippable module. The v29.0.0 draft artifact never actually built — every
item below was found and fixed while making the draft run.

### Fixed — build blockers (draft did not run)

- **SPOF #30**: ported the 21 missing `models/` modules from the v28 kernel
  (the draft imported a package that was never written → `ImportError`).
- **SPOF #40**: replaced the non-existent `setuptools.backends._legacy`
  build backend with `setuptools.build_meta`.
- **SPOF #47**: fixed bare `%` in lazy logging format strings
  (`ValueError: incomplete format` at warning time).

### Fixed — correctness defects

- **D-07**: warfarin dosing was driven by CYP2C19 status instead of CYP2C9;
  `GenomicTensor` now carries a dedicated `cyp2c9` field.
- **D-08**: RL recommendations were drawn from an untrained zero Q-table;
  the engine now pre-trains 200 episodes against the active payoff matrix.
- **D-09**: `BetaDistribution.credible_interval` ignored its `confidence`
  argument; z-values now resolve via `statistics.NormalDist`.
- **D-10**: adaptive Nash detection used float equality on learned payoffs;
  now `np.isclose`.
- **D-11**: RL epsilon decay was a no-op (`epsilon_decay_unused()` returned
  1.0); the configured decay is applied.
- **D-12**: RL used the global `numpy.random` state; now an injectable,
  seedable `numpy.random.Generator`.
- **D-13**: `OutcomeTracker.get_accuracy_metrics` contained dead
  correction-matching code; mean relative error is now computed correctly.
- **D-14**: the engine logged every prediction twice (phase-24 id + final
  seal); now exactly one log per run, under the seal id.

### Changed — production hardening

- **SPOF #32**: global RNG → injected, seeded generators. `execute()` is
  now deterministic for a given `(telemetry, seed)` pair — the Ragnar hash
  is finally reproducible.
- **SPOF #33**: all `print()` side-effects replaced by `logging` plus a
  structured `events` list in the engine result (25 phase records).
- **SPOF #34**: `OutcomeTracker` is injectable; the engine never writes to
  the filesystem silently. Persistence via `log_path`/`save`/`load` (JSONL).
- **SPOF #35**: version strings derive from a single source
  (`moac_qmm/_version.py`).
- **SPOF #36**: removed the hardcoded `/var/moac/logs` ledger path; the
  SPOF ledger is in-memory per run.
- **SPOF #37**: the v28 receptor kill-switch (P(therapeutic) < 0.5 → abort)
  aborted **every realistic profile**, including healthy ones. It is now
  opt-in via `strict_receptor_gate` (default off, recorded as a warning).
- **SPOF #38**: model persistence switched from `pickle` (RCE vector) to
  JSON.
- **SPOF #39**: added an optional FastAPI service layer
  (`pip install 'moac-qmm[api]'`): `/v1/simulate`, `/v1/optimize`,
  `/v1/predict`, probes and OpenAPI docs.
- **SPOF #48**: every constant now carries an honest provenance tier in the
  evidence register (`moac_qmm.evidence`); an integrity test keeps the
  register and `constants.py` in lockstep. No fabricated citations.
- **SPOF #49**: the public API surface is frozen in `moac_qmm.manifest` and
  enforced by `scripts/validate_manifest.py` + tests.

### Added

- Full test suite: 152 tests, 91% coverage (models, engine, deep learning,
  API, optimizer, evidence and manifest gates).
- CLI flags: `--seed` for deterministic runs, `--quiet`, `--output`.
- Telemetry fields: `strict_receptor_gate`, `inr`, `vitamin_k_intake`,
  `digoxin_level` (NTI monitoring).
- `TherapeuticWindow` TypedDict; organ-state validation (fail-closed).
- Docs: architecture, SPOF register (now 49 entries + v30 roadmap),
  deep-learning guide, API reference, evidence register.
- CI: ruff + mypy + pytest on Python 3.10-3.12 × Linux/macOS/Windows,
  manifest gate, PyPI release on tag.
- v28 kernel preserved verbatim under `legacy/` for provenance.

## [29.0.0] — draft

Deep-learning layer (NeuralPKPredictor, BayesianCalibration,
AdaptivePayoffMatrix, ReinforcementLearningOptimizer, OutcomeTracker),
pydantic telemetry schema, engine facade, CLI, CI scaffolding.
**Never shipped**: the artifact could not be installed or imported
(models package missing, build backend invalid).

## [28.0.0]

The Strata-Oblivion single-file kernel: 23-dimensional tensor matrix,
quantum receptor Monte Carlo, HPA axis, organ crosstalk, exogenous toxins,
sleep architecture, NTI engine, multi-compartment PK, allele priors,
game-theoretic pathogen, homeostasis optimizer. Preserved verbatim in
`legacy/moac_qmm_v28.py`.

## [27.0.0]

Vd, protein binding, organ perfusion, hypoxia, microbiome, nutrients,
anti-persona, chrono, epigenetic, autophagy, cytokine storm, vagal tone.

## [26.0.0]

Initial kernel: static-PK elimination, biochem friction, time-series PK.
