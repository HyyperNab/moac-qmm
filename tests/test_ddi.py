"""DDI tensor unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import StrataRejection
from moac_qmm.models import DrugDrugInteractionTensor


class TestDrugDrugInteractionTensor:
    def test_no_interaction_single_drug(self) -> None:
        ddi = DrugDrugInteractionTensor()
        stack = [{"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19"]}]
        assert ddi.check_interactions(stack) == []

    def test_cyp_competition_warning(self) -> None:
        ddi = DrugDrugInteractionTensor()
        stack = [
            {"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19"]},
            {"name": "Omeprazole", "protein_bound": 0.50, "cyp_pathway": ["CYP2C19"]},
        ]
        warnings = ddi.check_interactions(stack)
        assert any("CYP450 competition" in w for w in warnings)

    def test_protein_displacement_war_is_fatal(self) -> None:
        ddi = DrugDrugInteractionTensor()
        stack = [
            {"name": "Warfarin", "protein_bound": 0.99, "cyp_pathway": ["CYP2C9"]},
            {"name": "Phenytoin", "protein_bound": 0.95, "cyp_pathway": ["CYP2C9"]},
        ]
        with pytest.raises(StrataRejection):
            ddi.check_interactions(stack)

    def test_one_high_binder_is_tolerated(self) -> None:
        ddi = DrugDrugInteractionTensor()
        stack = [
            {"name": "Warfarin", "protein_bound": 0.99, "cyp_pathway": []},
            {"name": "Metformin", "protein_bound": 0.10, "cyp_pathway": []},
        ]
        assert ddi.check_interactions(stack) == []
