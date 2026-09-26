"""Multi-compartment and time-series PK solvers — SPOF #4, #22 annihilated."""

from __future__ import annotations

import logging
import math
from typing import TypedDict

logger = logging.getLogger(__name__)


class TherapeuticWindow(TypedDict):
    """Typed result of the therapeutic-window classification."""

    fraction_subtherapeutic: float
    fraction_supratherapeutic: float
    peak: float
    trough: float
    subtherapeutic: bool
    supratherapeutic: bool


class MultiCompartmentPK:
    """Two-compartment pharmacokinetic model.

    Central (plasma) ↔ Peripheral (tissue) with micro-constants
    k10, k12, k21. Euler integration with configurable step size.
    """

    @staticmethod
    def solve_two_compartment(
        dose: float,
        bioavailability: float,
        k10: float,
        k12: float,
        k21: float,
        v_central: float,
        v_peripheral: float,
        duration_hours: float = 72,
        dt: float = 0.1,
        dosing_interval: float = 24,
        num_doses: int = 3,
    ) -> dict[str, list[float]]:
        """Integrate the two-compartment ODE system over ``duration_hours``."""
        n_steps = int(duration_hours / dt)
        t = [0.0] * n_steps
        c_central = [0.0] * n_steps
        c_peripheral = [0.0] * n_steps

        c_central[0] = (dose * bioavailability) / v_central
        next_dose_time = dosing_interval
        remaining_doses = num_doses - 1

        for i in range(1, n_steps):
            t[i] = t[i - 1] + dt

            if t[i] >= next_dose_time and remaining_doses > 0:
                c_central[i - 1] += dose * bioavailability / v_central
                next_dose_time += dosing_interval
                remaining_doses -= 1

            dc_c = (
                -k10 * c_central[i - 1]
                - k12 * c_central[i - 1]
                + k21 * c_peripheral[i - 1] * (v_peripheral / v_central)
            )
            dc_p = k12 * c_central[i - 1] * (v_central / v_peripheral) - k21 * c_peripheral[i - 1]

            c_central[i] = max(0.0, c_central[i - 1] + dc_c * dt)
            c_peripheral[i] = max(0.0, c_peripheral[i - 1] + dc_p * dt)

        return {"time": t, "central": c_central, "peripheral": c_peripheral}

    @staticmethod
    def check_therapeutic_window(
        curve: dict[str, list[float]],
        therapeutic_min: float,
        therapeutic_max: float | None = None,
    ) -> TherapeuticWindow:
        """Classify the curve against the therapeutic window."""
        central = curve["central"]
        sub_count = sum(1 for c in central if c < therapeutic_min)
        supra_count = sum(1 for c in central if therapeutic_max and c > therapeutic_max)
        total = len(central)

        fraction_sub = sub_count / total
        fraction_supra = (supra_count / total) if therapeutic_max else 0.0

        if fraction_sub > 0.3:
            logger.warning(
                "%.0f%% subtherapeutic. Resistance selection pressure: MAXIMUM.",
                fraction_sub * 100,
            )
        if therapeutic_max and fraction_supra > 0.1:
            logger.warning(
                "%.0f%% supratherapeutic. Toxicity risk: ELEVATED.",
                fraction_supra * 100,
            )

        return TherapeuticWindow(
            fraction_subtherapeutic=fraction_sub,
            fraction_supratherapeutic=fraction_supra,
            peak=max(central),
            trough=min(central[1:]) if len(central) > 1 else 0.0,
            subtherapeutic=fraction_sub > 0.3,
            supratherapeutic=bool(therapeutic_max and fraction_supra > 0.1),
        )


class TimeSeriesPKSolver:
    """One-compartment multi-dose solver (v27, retained for parity)."""

    @staticmethod
    def solve_multi_dose(
        clearance_rate: float,
        vd: float,
        dose: float,
        dosing_interval: float,
        num_doses: int,
        bioavailability: float = 1.0,
    ) -> list[dict[str, float]]:
        """Analytic one-compartment multi-dose concentration curve."""
        k_elim = clearance_rate / vd
        concentration = 0.0
        curve: list[dict[str, float]] = []
        for dose_num in range(num_doses):
            concentration += (dose * bioavailability) / vd
            steps = 20
            dt = dosing_interval / steps
            for s in range(steps):
                concentration *= math.exp(-k_elim * dt)
                t = dose_num * dosing_interval + s * dt
                curve.append({"time": t, "concentration": concentration})
        return curve

    @staticmethod
    def check_subtherapeutic_window(curve: list[dict[str, float]], therapeutic_min: float) -> bool:
        """True when >30% of the curve sits below the therapeutic minimum."""
        sub_count = sum(1 for point in curve if point["concentration"] < therapeutic_min)
        fraction_sub = sub_count / len(curve)
        if fraction_sub > 0.3:
            logger.warning(
                "%.0f%% subtherapeutic. RESISTANCE SELECTION PRESSURE: MAXIMUM.",
                fraction_sub * 100,
            )
            return True
        return False


__all__ = ["MultiCompartmentPK", "TimeSeriesPKSolver"]
