"""Quantum drug-receptor binding — SPOF #16 annihilated.

Receptor occupancy is stochastic, not deterministic:
``P_bound = [L] / ([L] + Kd)`` is a probability, not a certainty.

Models binomial Monte Carlo occupancy, competitive ligand displacement,
allosteric modulation (cooperativity factor α) and spare receptors.

Production hardening (SPOF #37): the v28 kill-switch raised
``QuantumReceptorFailure`` whenever P(therapeutic) < 0.5 — which aborts
even healthy profiles for realistic PPI concentrations. The gate is now
opt-in via ``strict=True``; the engine defaults it off and records the
insufficiency as a result warning instead.
"""

from __future__ import annotations

import logging

import numpy as np

from moac_qmm.exceptions import QuantumReceptorFailure

logger = logging.getLogger(__name__)


class QuantumDrugReceptor:
    """Monte Carlo receptor occupancy engine."""

    def __init__(
        self,
        n_receptors: int = 10_000,
        n_simulations: int = 1000,
        rng: np.random.Generator | None = None,
    ) -> None:
        self.n_receptors = n_receptors
        self.n_sims = n_simulations
        self.rng = rng if rng is not None else np.random.default_rng()

    def calc_stochastic_occupancy(
        self,
        ligand_conc: float,
        kd: float,
        competitor_conc: float = 0.0,
        competitor_kd: float = 1.0,
        alpha: float = 1.0,
        spare_receptor_fraction: float = 0.1,
        strict: bool = False,
    ) -> dict[str, float | tuple[float, float]]:
        """Run the binomial Monte Carlo occupancy simulation.

        Args:
            ligand_conc: effective ligand concentration.
            kd: dissociation constant.
            competitor_conc: competitive ligand concentration.
            competitor_kd: competitor dissociation constant.
            alpha: allosteric cooperativity factor.
            spare_receptor_fraction: fraction of receptors that may stay unbound.
            strict: raise ``QuantumReceptorFailure`` when P(therapeutic) < 0.5
                (v28 theatrical mode). Default off.

        Returns:
            Occupancy statistics including mean, std, 95% CI, P(therapeutic).
        """
        # Competitive inhibition: apparent Kd increases
        if competitor_conc > 0:
            apparent_kd = kd * (1 + competitor_conc / competitor_kd) * alpha
        else:
            apparent_kd = kd * alpha

        p_bound = ligand_conc / (ligand_conc + apparent_kd)
        p_bound = min(1.0, max(0.0, p_bound))

        occupancies = self.rng.binomial(self.n_receptors, p_bound, self.n_sims)
        occupancy_fractions = occupancies / self.n_receptors

        mean_occupancy = float(np.mean(occupancy_fractions))
        std_occupancy = float(np.std(occupancy_fractions))
        p95_lower = float(np.percentile(occupancy_fractions, 2.5))
        p95_upper = float(np.percentile(occupancy_fractions, 97.5))

        therapeutic_threshold = 1.0 - spare_receptor_fraction
        p_therapeutic = float(np.mean(occupancy_fractions >= therapeutic_threshold))

        result: dict[str, float | tuple[float, float]] = {
            "mean_occupancy": mean_occupancy,
            "std_occupancy": std_occupancy,
            "ci_95": (p95_lower, p95_upper),
            "p_therapeutic_effect": p_therapeutic,
            "therapeutic_threshold": therapeutic_threshold,
            "apparent_kd": apparent_kd,
        }

        if p_therapeutic < 0.5:
            message = (
                f"[QUANTUM-RECEPTOR] P(therapeutic effect)={p_therapeutic:.1%}. "
                f"Mean occupancy={mean_occupancy:.1%} "
                f"(threshold={therapeutic_threshold:.1%}). "
                f"Receptor binding insufficient in >50% of Monte Carlo samples. "
                f"Options: Increase dose, decrease competitor, or switch drug class."
            )
            if strict:
                raise QuantumReceptorFailure(message)
            logger.warning(message)
            result["receptor_insufficient"] = 1.0

        return result


__all__ = ["QuantumDrugReceptor"]
