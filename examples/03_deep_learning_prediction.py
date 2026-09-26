"""Deep learning prediction — train the neural PK model on synthetic data."""

import numpy as np

from moac_qmm.deep_learning import NeuralPKPredictor

# Synthetic training data: 10 features → 3 PK targets
rng = np.random.default_rng(42)
n = 200
X = rng.random((n, 10)) * np.array(
    [80, 80, 120, 5, 2000, 1, 1, 100, 100, 1]  # age, bio_age, gfr, albumin, ...
)
y = np.column_stack(
    [
        (X[:, 2] / 90) * 0.3 + X[:, 5] * 0.5,  # clearance ~ gfr + cyp activity
        rng.random(n) * 10,  # t_half (noisy)
        0.25 * (1 + (4.0 - X[:, 3]) * 0.3),  # vd ~ albumin
    ]
)

predictor = NeuralPKPredictor(hidden_size=32, learning_rate=0.01, seed=42)
history = predictor.train(X, y, epochs=200)
print(f"Training complete. Final loss: {history[-1]:.6f}")

result = predictor.predict(
    {
        "age": 52,
        "bio_age": 61,
        "gfr": 72,
        "albumin": 3.2,
        "hepatic_flow": 1100,
        "cyp2c19_activity": 0.35,
        "cyp3a4_activity": 1.0,
        "spo2": 94,
        "body_weight": 70,
        "sex": 0,
    }
)

print("\nNeural PK prediction (trained):")
for key in ("clearance_rate", "t_half", "vd"):
    value = result[key]
    uncertainty = result[f"{key}_uncertainty"]
    print(f"  {key:<16} {value:8.3f}  ±{uncertainty:.3f}")
print(f"  confidence      {result['confidence']:8.1%}")
print(f"  MC samples      {result['n_mc_samples']}")

# Untrained model → heuristic fallback (never hard-fails)
fallback = NeuralPKPredictor()
heuristic = fallback.predict({"gfr": 72, "albumin": 3.2, "cyp2c19_activity": 0.35})
print(
    f"\nHeuristic fallback: clearance={heuristic['clearance_rate']:.3f} "
    f"(confidence {heuristic['confidence']:.0%}, heuristic={heuristic['heuristic']})"
)
