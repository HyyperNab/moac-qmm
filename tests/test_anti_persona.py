"""Anti-persona escape model unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import EdgeCaseCascade
from moac_qmm.models import AntiPersonaEscapeV2


class TestAntiPersonaEscapeV2:
    def test_short_healthy_exposure_no_vectors(self) -> None:
        model = AntiPersonaEscapeV2()
        vectors = model.predict_escape_vectors("H. pylori", "Esomeprazole", 2.0, False)
        assert sum(vectors.values()) == 0

    def test_subtherapeutic_long_exposure_cascades(self) -> None:
        model = AntiPersonaEscapeV2()
        with pytest.raises(EdgeCaseCascade):
            model.predict_escape_vectors("H. pylori", "Esomeprazole", 48.0, True)

    def test_long_therapeutic_exposure_only_biofilm(self) -> None:
        model = AntiPersonaEscapeV2()
        vectors = model.predict_escape_vectors("H. pylori", "Esomeprazole", 48.0, False)
        assert vectors == {"biofilm_qs": True}

    def test_beta_lactamase_induction(self) -> None:
        model = AntiPersonaEscapeV2()
        vectors = model.predict_escape_vectors("E. coli", "Amoxicillin", 5.0, True)
        assert vectors.get("enzyme_degradation") is True
        assert vectors.get("persister") is None  # 5h < 6h persister threshold
        assert sum(vectors.values()) == 2  # enzyme + biofilm only

    def test_rebound_phenotype_ultrarapid(self) -> None:
        model = AntiPersonaEscapeV2()
        assert "Dose escalation" in model.predict_rebound_phenotype("Esomeprazole", 0.35)

    def test_rebound_phenotype_poor_metabolizer(self) -> None:
        model = AntiPersonaEscapeV2()
        assert "Poor metabolizer" in model.predict_rebound_phenotype("Esomeprazole", 2.1)

    def test_rebound_phenotype_standard(self) -> None:
        model = AntiPersonaEscapeV2()
        result = model.predict_rebound_phenotype("Esomeprazole", 1.0)
        assert result == "Standard counter-measure sufficient."
