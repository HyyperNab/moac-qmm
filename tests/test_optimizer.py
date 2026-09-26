"""Homeostasis optimizer unit tests."""

from __future__ import annotations

from typing import Any

from moac_qmm import StableHomeostasisOptimizer
from moac_qmm.types import PatientTelemetry


class TestStableHomeostasisOptimizer:
    def test_healthy_profile_needs_nothing(self, healthy_telemetry: dict[str, Any]) -> None:
        # healthy fixture still has mild catabolic cortisol — expect sparse output
        prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(healthy_telemetry)
        assert isinstance(prescriptions, dict)
        assert "renal" not in prescriptions
        assert "albumin" not in prescriptions
        assert "detox" not in prescriptions

    def test_edge_case_gets_full_prescription_set(
        self, edge_case_telemetry: dict[str, Any]
    ) -> None:
        prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(edge_case_telemetry)
        assert "renal" in prescriptions
        assert "albumin" in prescriptions
        assert "ph" in prescriptions
        assert "hypoxia" in prescriptions
        assert "vagal" in prescriptions
        assert "sleep" in prescriptions
        assert "hpa" in prescriptions
        assert "tissue_mode" in prescriptions
        assert "detox" in prescriptions
        assert "chrono" in prescriptions

    def test_ultrarapid_genotype_gets_dose_adjustment(
        self, edge_case_telemetry: dict[str, Any]
    ) -> None:
        prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(edge_case_telemetry)
        assert "ppi_dose" in prescriptions
        assert "Rabeprazole" in prescriptions["ppi_dose"]["alternative"]

    def test_microbiome_prescription_when_dysbiotic(self) -> None:
        telemetry = PatientTelemetry(microbiome_diversity=1.5)
        prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(telemetry)
        assert "microbiome" in prescriptions

    def test_accepts_model_instance(self, healthy_telemetry: dict[str, Any]) -> None:
        model = PatientTelemetry(**healthy_telemetry)
        assert isinstance(StableHomeostasisOptimizer.calculate_optimal_vector(model), dict)

    def test_nutrient_deficiency_detected(self) -> None:
        telemetry = PatientTelemetry(
            nutrients={
                "glutamine": 0.1,
                "zinc": 1.0,
                "vitamin_c": 10.0,
                "vitamin_a": 100.0,
                "arginine": 0.5,
                "n3_index": 2.0,
            }
        )
        prescriptions = StableHomeostasisOptimizer.calculate_optimal_vector(telemetry)
        assert "nutrients" in prescriptions
        assert "glutamine" in prescriptions["nutrients"]
