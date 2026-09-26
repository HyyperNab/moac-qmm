"""Edge-case patient — the v28 demonstration profile.

Ultra-rapid CYP2C19 metabolizer, compromised organs, chronic toxin load,
biofilm pathogen, deep-learning layer enabled. This is the profile the
v28 kernel was originally demonstrated with.
"""

import json
from pathlib import Path

from moac_qmm import QMMEngine, StableHomeostasisOptimizer

here = Path(__file__).parent
telemetry = json.loads((here / "telemetry_edge_case.json").read_text(encoding="utf-8"))

# ── Full collision with the learning layer ──
engine = QMMEngine(telemetry, seed=42)
result = engine.execute()

print("=" * 79)
print("MOAC QMM v29.1 — EDGE CASE PROFILE")
print("=" * 79)

if "error" in result:
    print(f"ENGINE ABORT: {result['error']}")
else:
    print(f"Ragnar hash      : {result['hash']}")
    print(f"PK modifier      : {result['pk_modifier']} (CYP2C19 *17/*17)")
    print(
        f"Neural PK        : {result['neural_pk']['clearance_rate']:.3f} "
        f"(confidence {result['neural_pk']['confidence']:.0%})"
    )
    print(f"Restitution      : {result['restitution']:.3f}")
    print(f"Escape vectors   : {sum(result['escape_vectors'].values())}/5")
    print(f"RL recommendation: {result['rl_recommendation']}")
    print(f"Minimax strategy : {result['minimax']['minimax_treatment']}")

# ── Reverse-engineer the stable state ──
print()
print("=" * 79)
print("STABLE HOMEOSTASIS VECTOR")
print("=" * 79)
prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(telemetry)
for category, details in prescriptions.items():
    print(f"\n[{category.upper()}]")
    for key, value in details.items():
        if isinstance(value, list):
            for item in value:
                print(f"  • {item}")
        else:
            print(f"  {key}: {value}")
