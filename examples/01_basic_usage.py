"""Basic usage — run the full tensor collision on a healthy profile."""

from moac_qmm import QMMEngine

telemetry = {
    "genetics": {"CYP2C19": "*1/*1"},
    "primary_drug": "Esomeprazole",
    "primary_drug_class": "PPI",
    "drug_params": {
        "dose": 40,
        "kd": 0.8,
        "protein_bound": 0.95,
        "vd": 0.25,
        "cyp_pathway": ["CYP2C19"],
        "therapeutic_min": 0.5,
    },
    "drug_stack": [{"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19"]}],
    "gfr": 90,
    "albumin": 4.0,
    "current_ph": 5.0,
    "spo2": 98,
    "hrv_rmssd": 50,
    "hour": 8.0,
    "pathogen_name": "H. pylori",
    "pathogen_k": 0.1,
    "immune_v": 2.0,
    "exposure_hours": 2,
    "pathogen_strategy": "PLANKTONIC_FAST",
    "age": 35,
    "biological_age": 35,
    "telomere_kb": 10.0,
    "cortisol_8am": 15,
    "cortisol_nadir": 3,
    "dhea_s": 200,
    "total_sleep_hours": 8,
    "n3_percentage": 18,
    "mtor_activity": 0.6,
    "ampk_activity": 0.4,
    "microbiome_diversity": 3.5,
    "pathobionts": [],
    "nutrients": {
        "glutamine": 0.5,
        "zinc": 8,
        "vitamin_c": 75,
        "vitamin_a": 900,
        "arginine": 4,
        "n3_index": 8,
    },
    "organ_states": {"gut": 1, "liver": 1, "kidney": 1, "heart": 1, "lung": 1, "brain": 1},
}

engine = QMMEngine(telemetry, seed=42)
result = engine.execute()

if "error" in result:
    raise SystemExit(f"Engine aborted: {result['error']}")

print(f"Ragnar hash : {result['hash']}")
print(f"Restitution  : {result['restitution']:.3f}")
print(f"Clearance    : {result['clearance']['clearance_rate']:.3f}")
print(f"IL-6         : {result['cytokine']['IL-6']:.1f} pg/mL")
print(f"Receptor occ.: {result['receptor_occupancy']['mean_occupancy']:.1%}")
print(f"Surviving priors: {len(result['surviving_priors'])}/10")
print(f"\nPhases executed: {len(result['events'])}")
