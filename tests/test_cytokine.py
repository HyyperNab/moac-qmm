"""Cytokine storm vector unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import CytokineStormDetected
from moac_qmm.models import CytokineStormVector


class TestCytokineStormVector:
    def test_quiescent_pathogen_keeps_homeostasis(self) -> None:
        vector = CytokineStormVector()
        state = vector.step(pathogen_vector=0.0, immune_v=1.0)
        assert state["IL-6"] < 20
        assert state["TNF-α"] < 20

    def test_storm_raises_when_both_thresholds_breached(self) -> None:
        vector = CytokineStormVector()
        vector.il6 = 200.0
        vector.tnf_alpha = 200.0
        with pytest.raises(CytokineStormDetected):
            vector.step(pathogen_vector=0.5, immune_v=1.0)

    def test_vagal_suppression_damps_tnf(self) -> None:
        high_vagal = CytokineStormVector()
        low_vagal = CytokineStormVector()
        high_vagal.step(pathogen_vector=0.5, immune_v=1.0, vagal_suppression=0.5)
        low_vagal.step(pathogen_vector=0.5, immune_v=1.0, vagal_suppression=1.0)
        assert high_vagal.tnf_alpha < low_vagal.tnf_alpha

    def test_cortisol_damps_production(self) -> None:
        stressed = CytokineStormVector()
        relaxed = CytokineStormVector()
        stressed.step(pathogen_vector=0.5, immune_v=1.0, cortisol_level=40.0)
        relaxed.step(pathogen_vector=0.5, immune_v=1.0, cortisol_level=0.0)
        assert stressed.il6 < relaxed.il6

    def test_history_records_steps(self) -> None:
        vector = CytokineStormVector()
        for _ in range(3):
            vector.step(pathogen_vector=0.1, immune_v=1.0)
        assert len(vector.history) == 3

    def test_immune_phenotype_classification(self) -> None:
        vector = CytokineStormVector()
        assert "TH1-dominant" in vector.evaluate_immune_phenotype(5.0)
        assert "TH2-dominant" in vector.evaluate_immune_phenotype(0.2)
        assert "Balanced" in vector.evaluate_immune_phenotype(1.0)
