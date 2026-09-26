# SPOF Register — Complete Elimination Ledger

Every Single Point of Failure identified and annihilated across MOAC QMM
versions. v29.1.0 extends the register with production-infrastructure SPOFs
found while turning the draft into a shippable module.

## Legend

- ❌ = SPOF exists (unresolved)
- ✅ = SPOF annihilated
- ⚠️ = Partially resolved

## Domain SPOFs (v26 → v29)

| # | SPOF | v26 | v27 | v28 | v29.1 | Resolution Module |
|---|------|:---:|:---:|:---:|:-----:|-------------------|
| 1 | Static PK modifier | ❌ | ✅ | ✅ | ✅ | `GenomicTensor` |
| 2 | No Vd tensor | ❌ | ✅ | ✅ | ✅ | `RenalHepaticClearance` |
| 3 | No protein binding DDI | ❌ | ✅ | ✅ | ✅ | `DrugDrugInteractionTensor` |
| 4 | Single-shot execution | ❌ | ✅ | ✅ | ✅ | `MultiCompartmentPK` |
| 5 | No organ perfusion | ❌ | ✅ | ✅ | ✅ | `RenalHepaticClearance` |
| 6 | No hypoxia model | ❌ | ✅ | ✅ | ✅ | `HypoxiaTensor` |
| 7 | No microbiome | ❌ | ✅ | ✅ | ✅ | `MicrobiomeMetabolizer` |
| 8 | No nutrient substrates | ❌ | ✅ | ✅ | ✅ | `NutrientSubstrateMatrix` |
| 9 | Trivial anti-persona | ❌ | ✅ | ✅ | ✅ | `AntiPersonaEscapeV2` + `PathogenGameTheory` |
| 10 | No chronopharmacology | ❌ | ✅ | ✅ | ✅ | `ChronopharmacologyModulator` |
| 11 | No epigenetic age | ❌ | ✅ | ✅ | ✅ | `EpigeneticAgeClock` |
| 12 | No endocrine model | ❌ | ⚠️ | ✅ | ✅ | `HPAAxisModel` |
| 13 | No autophagy toggle | ❌ | ✅ | ✅ | ✅ | `AutophagyApoptosisToggle` |
| 14 | No cytokine model | ❌ | ✅ | ✅ | ✅ | `CytokineStormVector` |
| 15 | No vagal tone | ❌ | ✅ | ✅ | ✅ | `VagalToneVoltage` |
| 16 | Receptor determinism | ❌ | ❌ | ✅ | ✅ | `QuantumDrugReceptor` |
| 17 | No HPA axis | ❌ | ❌ | ✅ | ✅ | `HPAAxisModel` |
| 18 | No organ crosstalk | ❌ | ❌ | ✅ | ✅ | `OrganCrosstalkTensor` |
| 19 | No sleep architecture | ❌ | ❌ | ✅ | ✅ | `SleepArchitectureTensor` |
| 20 | No exogenous toxins | ❌ | ❌ | ✅ | ✅ | `ExogenousToxinLoad` |
| 21 | No NTI engine | ❌ | ❌ | ✅ | ✅ | `NarrowTherapeuticIndexEngine` |
| 22 | Single compartment PK | ❌ | ❌ | ✅ | ✅ | `MultiCompartmentPK` |
| 23 | Uniform priors | ❌ | ❌ | ✅ | ✅ | `SpofLedger` |
| 24 | Hardcoded PK params | ❌ | ❌ | ❌ | ✅ | `NeuralPKPredictor` |
| 25 | No model calibration | ❌ | ❌ | ❌ | ✅ | `BayesianCalibration` |
| 26 | Static game payoffs | ❌ | ❌ | ❌ | ✅ | `AdaptivePayoffMatrix` |
| 27 | No outcome learning | ❌ | ❌ | ❌ | ✅ | `ReinforcementLearningOptimizer` |
| 28 | No feedback loop | ❌ | ❌ | ❌ | ✅ | `OutcomeTracker` |
| 29 | Unvalidated inputs | ❌ | ❌ | ❌ | ✅ | `PatientTelemetry` (pydantic) |

## Production SPOFs (v29.1.0 — eliminated while shipping the draft)

These SPOFs existed in the v29 draft artifact. None of them would have
surfaced without actually building and running the project.

| # | SPOF | Failure mode | Resolution |
|---|------|--------------|------------|
| 30 | Draft imported a `models/` package that was never written | **ImportError — the draft did not build at all** | 21 model modules ported from the v28 kernel |
| 31 | Wildcard imports (`from constants import *`) | namespace pollution, silent shadowing | explicit imports everywhere |
| 32 | Global `numpy.random` state | non-deterministic "deterministic" hash, thread races | injected, seeded `numpy.random.Generator` |
| 33 | `print()` inside library code | side-effects pollute API consumers, untestable | `logging` + structured `events` in the result |
| 34 | Engine wrote to filesystem implicitly | undeclared I/O SPOF | injectable `OutcomeTracker`, explicit persistence |
| 35 | Version strings scattered as literals | version drift across CLI/engine/spec | single source `moac_qmm._version` |
| 36 | Hardcoded ledger path `/var/moac/logs/...` | unwritable path, undeclared SPOF | in-memory ledger; persistence explicit |
| 37 | Theatrical receptor kill-switch (P(therapeutic) < 0.5 always raised) | **healthy patients always aborted** — draft tests never ran | opt-in `strict_receptor_gate` (default off) |
| 38 | `pickle` model persistence | RCE vector on model load | JSON persistence |
| 39 | No machine-to-machine surface | every consumer had to be a Python process | FastAPI service layer (`[api]` extra) |
| 40 | `pyproject.toml` used a non-existent build backend | `pip install` fails | `setuptools.build_meta` |
| 41 | Epsilon decay was a no-op (`epsilon_decay_unused()` → 1.0) | RL exploration never decayed | configured decay applied (D-11) |
| 42 | RL recommended from an untrained zero Q-table | every recommendation was action 0 | engine pre-trains 200 episodes before recommending (D-08) |
| 43 | Predictions logged twice per run | corrupted outcome tracking | single log under the seal id (D-14) |
| 44 | Warfarin check used CYP2C19 instead of CYP2C9 | wrong genotype → wrong dose factor | dedicated `cyp2c9` field (D-07) |
| 45 | `credible_interval` ignored its `confidence` argument | wrong intervals at any level ≠ 95% | `statistics.NormalDist().inv_cdf` (D-09) |
| 46 | Nash detection used float equality on learned payoffs | learned equilibria silently vanished | `np.isclose` (D-10) |
| 47 | Bare `%` in lazy logging strings | `ValueError: incomplete format` at warning time | doubled `%%` literals, caught by tests |
| 48 | No provenance discipline on constants | plausible-looking magic numbers read as science | per-constant evidence tiers + integrity test |
| 49 | No frozen API contract | silent breaking changes between generations | `manifest.py` + `validate_manifest` gate |

## Future SPOFs (v30 candidates)

| # | SPOF | Description |
|----|------|-------------|
| 50 | No GPU acceleration | Neural network uses numpy. Torch backend optional. |
| 51 | No federated learning | Model weights are local. No multi-site training. |
| 52 | No causal inference | Correlations only. No do-calculus. |
| 53 | No three-compartment PK | Biliary recirculation absent. |
| 54 | No continuous glucose model | No insulin/glucose dynamics. |
| 55 | No pharmacovigilance database | DDI checks are hardcoded. |
| 56 | No ancestry-stratified allele priors | Population frequencies vary by ancestry. |
