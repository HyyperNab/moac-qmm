"""Run a full MOAC QMM simulation with the v28 edge-case patient profile."""

from __future__ import annotations

import json
from pathlib import Path

from moac_qmm import QMMEngine, StableHomeostasisOptimizer

TELEMETRY: dict[str, object] = {
    "genetics": {
        "CYP2C19": "*17/*17",
        "CYP3A4": "*1/*1",
        "CYP2D6": "*1/*1",
        "HLA-B": "Negative",
        "SLCO1B1": "*1/*1",
        "VKORC1": "*1/*1",
    },
    "primary_drug": "Esomeprazole",
    "primary_drug_class": "PPI",
    "route": "oral",
    "drug_params": {
        "name": "Esomeprazole",
        "dose": 40,
        "interval": 24,
        "therapeutic_min": 0.5,
        "therapeutic_max": 5.0,
        "renal_fraction": 0.2,
        "hepatic_extraction": 0.8,
        "protein_bound": 0.95,
        "vd": 0.25,
        "cyp_pathway": ["CYP2C19", "CYP3A4"],
        "kd": 0.8,
    },
    "drug_stack": [
        {"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19", "CYP3A4"]},
        {"name": "Clarithromycin", "protein_bound": 0.70, "cyp_pathway": ["CYP3A4"]},
        {"name": "Magnesium_Bisglycinate", "protein_bound": 0.10, "cyp_pathway": []},
        {"name": "Alginate", "protein_bound": 0.05, "cyp_pathway": []},
    ],
    "k12": 0.15,
    "k21": 0.10,
    "v_central": 0.15,
    "v_peripheral": 0.10,
    "age": 52,
    "biological_age": 61,
    "methylation_pace": 1.17,
    "telomere_kb": 6.2,
    "gfr": 72,
    "hepatic_flow": 1100,
    "albumin": 3.2,
    "organ_states": {
        "gut": 0.4,
        "liver": 0.65,
        "kidney": 0.7,
        "heart": 0.85,
        "lung": 0.75,
        "brain": 0.9,
    },
    "current_ph": 3.5,
    "spasm_prob": 0.3,
    "spo2": 94.0,
    "tissue_po2": 28.0,
    "hrv_rmssd": 18.0,
    "cortisol_nadir": 12.0,
    "cortisol_8am": 28.0,
    "dhea_s": 85.0,
    "pathogen_name": "Helicobacter pylori",
    "pathogen_k": 0.3,
    "immune_v": 1.2,
    "biofilm": False,
    "exposure_hours": 18,
    "th1_th2_ratio": 1.5,
    "pathogen_strategy": "BIOFILM_FORTIFY",
    "microbiome_diversity": 2.1,
    "pathobionts": ["Enterococcus faecalis"],
    "ppi_exposure_weeks": 8,
    "nutrients": {
        "glutamine": 0.3,
        "zinc": 4.0,
        "vitamin_c": 60.0,
        "vitamin_a": 700.0,
        "arginine": 2.0,
        "n3_index": 4.0,
    },
    "mtor_activity": 0.3,
    "ampk_activity": 0.8,
    "hour": 22.0,
    "total_sleep_hours": 5.5,
    "n3_percentage": 8.0,
    "rem_percentage": 15.0,
    "sleep_efficiency": 0.72,
    "awakenings": 5,
    "toxins": {"lead": 3.2, "mercury": 2.0, "alcohol_chronic": 45.0},
    "use_neural_pk": True,
    "use_bayesian_calibration": True,
    "use_adaptive_payoff": True,
    "use_rl_optimizer": True,
}


def main() -> None:
    engine = QMMEngine(TELEMETRY, seed=42)  # type: ignore[arg-type]
    result = engine.execute()

    out = Path("simulation_result.json")
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    if "error" in result:
        print(f"ENGINE ABORT: {result['error']}")
        print(f"Phase trace ({len(result['events'])} phases) saved to {out}")
        return

    print(f"Ragnar hash: {result['hash']}")
    print(f"Result saved to {out}")

    prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(
        TELEMETRY  # type: ignore[arg-type]
    )
    print(f"\nHomeostasis optimizer: {len(prescriptions)} intervention categories")


if __name__ == "__main__":
    main()
