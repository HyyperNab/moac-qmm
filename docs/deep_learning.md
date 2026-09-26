# Deep Learning Layer

The v29 learning layer eliminates SPOFs #24-28. It is deliberately
**numpy-only** — no torch dependency — because the models are small and the
deployment surface should stay minimal.

## Modules

### NeuralPKPredictor — SPOF #24

3-layer MLP (input → 32 hidden → 32 hidden → 3 outputs) with ReLU and
Xavier initialization, trained by mini-batch gradient descent.

- **Inputs (10):** age, bio_age, gfr, albumin, hepatic_flow,
  cyp2c19_activity, cyp3a4_activity, spo2, body_weight, sex
- **Outputs (3):** clearance_rate, t_half, vd
- **Uncertainty:** MC-Dropout approximation — 50 stochastic forward passes
  with 10% dropout; the std across passes is the epistemic uncertainty and
  `confidence = 1 / (1 + uncertainty / |mean|)`
- **Fallback:** biophysical heuristics when untrained (`heuristic: true` in
  the result) — the engine never hard-fails on an untrained model
- **Persistence:** JSON (never pickle — SPOF #38)
- **Determinism:** `seed` constructor parameter; same seed → same weights,
  same dropout masks, same predictions

### BayesianCalibration — SPOF #25

- **Binary outcomes:** Beta-Bernoulli conjugate model. The first prediction
  seeds the prior (`alpha = 10·p`, `beta = 10·(1-p)`), every observation
  updates it.
- **Continuous outcomes:** Gaussian conjugate running model per parameter.
- `get_confidence(name)` → `(mean, uncertainty)`; credible intervals resolve
  the z-value from `statistics.NormalDist` for any confidence level (D-09).

### AdaptivePayoffMatrix — SPOF #26

The 5×5 game payoff matrix becomes a *learned* matrix. On every observed
outcome:

- success → treatment payoff +0.1·magnitude, pathogen payoff −0.05·magnitude
- failure → treatment payoff −0.1·magnitude, pathogen payoff +0.05·magnitude

Pure-equilibrium detection uses `np.isclose` so learned (non-integer) payoffs
are still comparable (D-10).

### ReinforcementLearningOptimizer — SPOF #27

Tabular Q-learning over 40 states
(5 pathogen strategies × 2 immune × 2 biofilm × 2 subtherapeutic)
and 5 actions (treatment strategies).

- reward = `t_payoff − 0.5 · p_payoff` from the active payoff matrix
- epsilon-greedy exploration with **working** decay `ε ← max(0.05, 0.995·ε)`
  (the draft's decay was a no-op — D-11)
- injectable RNG via `with_seed(seed)`; deterministic training (D-12)
- the engine pre-trains 200 episodes before recommending, so recommendations
  never come from a zero Q-table (D-08)

### OutcomeTracker — SPOF #28

Every engine run logs exactly one prediction under its Ragnar seal id
(D-14). When the actual outcome arrives, `log_outcome` computes numeric
corrections and `get_accuracy_metrics` reports mean relative error.

Persistence is **explicit**: pass `log_path` (JSONL streaming) or call
`save`/`load` (JSON snapshot). The engine itself never touches the
filesystem (SPOF #34).

## Integration in the engine

```python
telemetry = {
    ...
    "use_neural_pk": True,             # phase 2
    "use_bayesian_calibration": True,  # phase 22
    "use_adaptive_payoff": True,       # phase 20 (learned matrix)
    "use_rl_optimizer": True,          # phase 21 (pre-trained)
}
engine = QMMEngine(telemetry, seed=42)
result = engine.execute()
result["neural_pk"]        # PK prediction + uncertainty
result["rl_recommendation"]  # learned treatment strategy
result["calibration"]      # calibration summary
```

All deep-learning modules are **optional** — with all flags off the engine
runs the pure analytical pipeline with zero extra cost.
