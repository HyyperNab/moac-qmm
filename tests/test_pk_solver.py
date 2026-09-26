"""PK solver unit tests (2-compartment + time-series)."""

from __future__ import annotations

import math

import pytest

from moac_qmm.models import MultiCompartmentPK, TimeSeriesPKSolver


class TestMultiCompartmentPK:
    def test_initial_concentration(self) -> None:
        curve = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=1.0,
            k12=0.15,
            k21=0.10,
            v_central=0.15,
            v_peripheral=0.10,
            duration_hours=2,
            dt=0.1,
        )
        assert curve["central"][0] == 40 / 0.15

    def test_elimination_decays_central(self) -> None:
        curve = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=5.0,
            k12=0.0,
            k21=0.0,
            v_central=0.15,
            v_peripheral=0.10,
            duration_hours=4,
            dt=0.1,
        )
        assert curve["central"][-1] < curve["central"][0]

    def test_concentrations_never_negative(self) -> None:
        curve = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=3.0,
            k12=0.5,
            k21=0.5,
            v_central=0.15,
            v_peripheral=0.10,
            duration_hours=24,
            dt=0.5,
        )
        assert min(curve["central"]) >= 0.0
        assert min(curve["peripheral"]) >= 0.0

    def test_multi_dose_peak_exceeds_single(self) -> None:
        single = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=0.5,
            k12=0.1,
            k21=0.1,
            v_central=0.15,
            v_peripheral=0.1,
            duration_hours=48,
            dt=0.1,
            num_doses=1,
        )
        multi = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=0.5,
            k12=0.1,
            k21=0.1,
            v_central=0.15,
            v_peripheral=0.1,
            duration_hours=48,
            dt=0.1,
            num_doses=3,
        )
        assert max(multi["central"]) > max(single["central"])

    def test_therapeutic_window_flags(self) -> None:
        curve = MultiCompartmentPK.solve_two_compartment(
            dose=40,
            bioavailability=1.0,
            k10=0.05,
            k12=0.01,
            k21=0.01,
            v_central=0.15,
            v_peripheral=0.1,
            duration_hours=72,
            dt=0.5,
        )
        window = MultiCompartmentPK.check_therapeutic_window(curve, 1000.0, None)
        assert window["subtherapeutic"] is True
        assert window["fraction_subtherapeutic"] == 1.0


class TestTimeSeriesPKSolver:
    def test_curve_length(self) -> None:
        curve = TimeSeriesPKSolver.solve_multi_dose(
            clearance_rate=1.0,
            vd=0.25,
            dose=40,
            dosing_interval=24,
            num_doses=3,
        )
        assert len(curve) == 3 * 20

    def test_accumulation_between_doses(self) -> None:
        curve = TimeSeriesPKSolver.solve_multi_dose(
            clearance_rate=0.05,
            vd=0.25,
            dose=40,
            dosing_interval=24,
            num_doses=3,
        )
        first_peak = curve[0]["concentration"]
        last_peak = max(p["concentration"] for p in curve if p["time"] >= 48)
        assert last_peak > first_peak

    def test_decay_within_interval(self) -> None:
        # v28 semantics: samples are appended AFTER each decay step,
        # so the first recorded point is already decayed once.
        curve = TimeSeriesPKSolver.solve_multi_dose(
            clearance_rate=1.0,
            vd=0.25,
            dose=40,
            dosing_interval=24,
            num_doses=1,
        )
        k_elim = 1.0 / 0.25
        dt = 24 / 20
        assert curve[0]["concentration"] == pytest.approx((40 / 0.25) * math.exp(-k_elim * dt))
        assert curve[-1]["concentration"] == pytest.approx(
            (40 / 0.25) * math.exp(-k_elim * dt * 20), rel=0.01
        )

    def test_subtherapeutic_detection(self) -> None:
        curve = TimeSeriesPKSolver.solve_multi_dose(
            clearance_rate=1.0,
            vd=0.25,
            dose=40,
            dosing_interval=24,
            num_doses=3,
        )
        assert TimeSeriesPKSolver.check_subtherapeutic_window(curve, 1e9) is True
        assert TimeSeriesPKSolver.check_subtherapeutic_window(curve, 0.0) is False
