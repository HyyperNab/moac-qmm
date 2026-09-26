"""Renal/hepatic clearance unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.models import RenalHepaticClearance


@pytest.fixture
def clearance() -> RenalHepaticClearance:
    return RenalHepaticClearance(gfr=90, hepatic_flow=1500, albumin=4.0, biological_age=35)


class TestRenalHepaticClearance:
    def test_clearance_components(self, clearance: RenalHepaticClearance) -> None:
        drug = {"renal_fraction": 0.2, "hepatic_extraction": 0.8, "vd": 0.25}
        data = clearance.calc_total_clearance(drug)
        assert data["renal_component"] == pytest.approx(0.2)
        assert data["hepatic_component"] == pytest.approx(0.8)
        assert data["clearance_rate"] == pytest.approx(1.0)
        assert data["age_penalty"] == pytest.approx(1.0)

    def test_free_fraction(self, clearance: RenalHepaticClearance) -> None:
        drug = {"protein_bound": 0.95}
        data = clearance.calc_total_clearance(drug)
        assert data["free_fraction"] == pytest.approx(0.05)

    def test_half_life_formula(self, clearance: RenalHepaticClearance) -> None:
        drug = {"renal_fraction": 0.2, "hepatic_extraction": 0.8, "vd": 0.25}
        data = clearance.calc_total_clearance(drug)
        assert data["t_half"] == pytest.approx(0.693 * 0.25 / 1.0)

    def test_hypoalbuminemia_increases_vd(self) -> None:
        normal = RenalHepaticClearance(90, 1500, 4.0, 35)
        low = RenalHepaticClearance(90, 1500, 2.0, 35)
        drug = {"vd": 0.25}
        vd_normal = normal.calc_total_clearance(drug)["vd_adjusted"]
        vd_low = low.calc_total_clearance(drug)["vd_adjusted"]
        assert vd_low > vd_normal

    def test_age_penalty_decays_after_40(self) -> None:
        old = RenalHepaticClearance(90, 1500, 4.0, 80)
        data = old.calc_total_clearance({"vd": 0.25})
        assert data["age_penalty"] == pytest.approx(0.6)  # 1 - (80-40)*0.01

    def test_age_penalty_floors_at_half(self) -> None:
        ancient = RenalHepaticClearance(90, 1500, 4.0, 110)
        data = ancient.calc_total_clearance({"vd": 0.25})
        assert data["age_penalty"] == pytest.approx(0.5)

    def test_gfr_below_30_is_a_kill(self) -> None:
        failing = RenalHepaticClearance(gfr=25, hepatic_flow=1500, albumin=4.0, biological_age=50)
        assert "KILL" in failing.evaluate_organ_failure_risk()

    def test_low_hepatic_flow_is_a_warning(self) -> None:
        failing = RenalHepaticClearance(90, 400, 4.0, 50)
        assert "WARN" in failing.evaluate_organ_failure_risk()

    def test_healthy_profile_is_stable(self, clearance: RenalHepaticClearance) -> None:
        assert clearance.evaluate_organ_failure_risk() == "STABLE"
