"""QSense governor and Bayesian SPOF ledger — SPOF #23 annihilated.

SPOF #36 eliminated: the v28 kernel hardcoded a ledger path under
``/var/moac/logs`` — an unwritable, undeclared filesystem SPOF. The
ledger is now purely in-memory per engine run; persistence belongs to
the :class:`~moac_qmm.deep_learning.outcome_tracker.OutcomeTracker`
layer where it is explicit and configurable.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class QSenseGovernor:
    """Lagom throttle: friction budget for the drug stack."""

    def apply_lagom_throttle(self, stack_size: int, entropy: float) -> int:
        """Cap the stack when entropy is low and the stack is massive."""
        if stack_size > 3 and entropy < 0.2:
            logger.info("Friction violation. Entropy low, stack massive. Purging.")
            return 3
        return stack_size


class SpofLedger:
    """Bayesian ledger of SPOF assumption priors.

    Priors are weighted by genotype population frequency: rare genotypes
    thin the evidence base for the 'average patient' assumption.
    """

    def __init__(self, allele_frequency: float = 1.0) -> None:
        evidence_factor = min(1.0, allele_frequency * 100)
        self.priors: dict[str, float] = {
            "linear_healing": 0.9,
            "average_patient": 0.95 * evidence_factor,
            "static_pathogen": 0.85,
            "time_independent_pk": 0.9,
            "single_drug_interaction": 0.8,
            "organ_independence": 0.9,
            "receptor_determinism": 0.95,
            "toxin_free": 0.85,
            "sleep_irrelevant": 0.80,
            "hpa_stable": 0.90,
        }

    def bayesian_update(self, condition: str, actual_outcome: bool) -> None:
        """Slash the prior tenfold when the assumption failed."""
        if not actual_outcome:
            self.priors[condition] = self.priors.get(condition, 0.5) * 0.1
            logger.info(
                "SPOF updated. Prior for '%s' slashed to %.4f",
                condition,
                self.priors[condition],
            )

    def get_surviving_priors(self) -> dict[str, float]:
        """Assumptions that survived the collision (prior > 0.1)."""
        return {k: v for k, v in self.priors.items() if v > 0.1}


__all__ = ["QSenseGovernor", "SpofLedger"]
