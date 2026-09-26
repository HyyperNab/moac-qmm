"""Narrow therapeutic index engine unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import NTIToxicityKill
from moac_qmm.models import NarrowTherapeuticIndexEngine


class TestNarrowTherapeuticIndexEngine:
    def test_normal_genotype_full_dose(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        result = engine.check_warfarin("*1/*1", "*1/*1", vitamin_k_intake=100, inr_current=2.5)
        assert result["recommended_dose_factor"] == pytest.approx(1.0)
        assert result["inr_in_range"] is True

    def test_vkorc1_sensitivity_halves_dose(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        result = engine.check_warfarin("*2/*2", "*1/*1", vitamin_k_intake=100, inr_current=2.5)
        assert result["sensitivity"] == 2.0
        assert result["recommended_dose_factor"] == pytest.approx(0.5)

    def test_inr_above_target_raises(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        with pytest.raises(NTIToxicityKill):
            engine.check_warfarin("*1/*1", "*1/*1", vitamin_k_intake=100, inr_current=4.0)

    def test_amiodarone_halves_clearance(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        result = engine.check_warfarin(
            "*1/*1",
            "*1/*1",
            vitamin_k_intake=100,
            inr_current=2.5,
            interacting_drugs=["Amiodarone"],
        )
        assert result["interaction_multiplier"] == pytest.approx(0.5)

    def test_digoxin_in_range(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        result = engine.check_digoxin(digoxin_level=1.2, gfr=90, potassium=4.2)
        assert result["level_in_range"] is True
        assert result["renal_adjustment_needed"] is False

    def test_digoxin_overdose_raises(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        with pytest.raises(NTIToxicityKill):
            engine.check_digoxin(digoxin_level=3.0, gfr=90, potassium=4.2)

    def test_renal_adjustment_flagged(self) -> None:
        engine = NarrowTherapeuticIndexEngine()
        result = engine.check_digoxin(digoxin_level=1.0, gfr=45, potassium=4.2)
        assert result["renal_adjustment_needed"] is True
