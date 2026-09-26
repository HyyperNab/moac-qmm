"""Homeostasis optimization — what telemetry would survive every phase?"""

from moac_qmm import StableHomeostasisOptimizer

compromised = {
    "genetics": {"CYP2C19": "*17/*17"},
    "gfr": 55,
    "albumin": 3.1,
    "current_ph": 3.2,
    "spo2": 93,
    "hrv_rmssd": 14,
    "hour": 23,
    "cortisol_8am": 32,
    "dhea_s": 70,
    "total_sleep_hours": 5,
    "n3_percentage": 6,
    "mtor_activity": 0.2,
    "ampk_activity": 0.9,
    "microbiome_diversity": 1.9,
    "toxins": {"lead": 6.5, "mercury": 4.0},
    "nutrients": {"glutamine": 0.2, "zinc": 3.0},
}

prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(compromised)

print("INTERVENTIONS REQUIRED FOR STABLE HOMEOSTASIS")
print("=" * 60)
for category, details in prescriptions.items():
    print(f"\n┌─ {category.upper()} ─┐")
    for key, value in details.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    • {item}")
        else:
            print(f"  {key}: {value}")

print(f"\n{len(prescriptions)} intervention categories identified.")
