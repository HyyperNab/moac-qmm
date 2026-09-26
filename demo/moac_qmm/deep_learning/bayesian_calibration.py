"""Bayesian calibration — SPOF #25 annihilated.

Calibrates model predictions against observed outcomes using conjugate
prior updating. Replaces point estimates with calibrated distributions.

Beta-Bernoulli conjugate model for binary outcomes (treatment
success/failure) and Normal-Inverse-Gamma style conjugate updating for
continuous outcomes (clearance rate, half-life).

Production defect fix (D-09): ``credible_interval`` ignored its
``confidence`` argument (hardcoded z=1.96); now resolved via
``statistics.NormalDist``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import NormalDist

import numpy as np


@dataclass
class BetaDistribution:
    """Beta distribution for binary outcome calibration."""

    alpha: float = 1.0  # prior pseudo-count of successes
    beta: float = 1.0  # prior pseudo-count of failures

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))

    def update(self, observed_success: bool) -> None:
        """Bayesian update with an observed outcome."""
        if observed_success:
            self.alpha += 1
        else:
            self.beta += 1

    def credible_interval(self, confidence: float = 0.95) -> tuple[float, float]:
        """Approximate credible interval via the normal plug-in."""
        z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
        std = float(np.sqrt(self.variance))
        return (max(0.0, self.mean - z * std), min(1.0, self.mean + z * std))


@dataclass
class GaussianConjugate:
    """Conjugate model for continuous outcomes.

    Tracks a running posterior mean and variance, updated with each
    observation.
    """

    prior_mean: float = 0.0
    prior_variance: float = 1.0
    prior_strength: float = 1.0  # number of pseudo-observations
    observations: list[float] = field(default_factory=list)

    def update(self, observed_value: float) -> None:
        """Bayesian update with a continuous observation."""
        self.observations.append(observed_value)
        n = len(self.observations)
        emp_mean = float(np.mean(self.observations))
        emp_var = float(np.var(self.observations)) if n > 1 else self.prior_variance

        strength = self.prior_strength + n
        posterior_mean = (self.prior_mean * self.prior_strength + emp_mean * n) / strength
        posterior_var = emp_var + self.prior_variance / strength

        self.prior_mean = posterior_mean
        self.prior_variance = posterior_var
        self.prior_strength = strength

    @property
    def mean(self) -> float:
        return self.prior_mean

    @property
    def uncertainty(self) -> float:
        return float(np.sqrt(self.prior_variance))


class BayesianCalibration:
    """Calibrates model predictions against real outcomes.

    Every prediction gets a confidence interval that narrows as more
    outcomes are observed.
    """

    def __init__(self) -> None:
        self.binary_calibrators: dict[str, BetaDistribution] = {}
        self.continuous_calibrators: dict[str, GaussianConjugate] = {}
        self.n_observations = 0

    def calibrate_binary(
        self, condition: str, predicted_prob: float, observed_success: bool
    ) -> float:
        """Calibrate a binary prediction; returns the calibrated probability."""
        if condition not in self.binary_calibrators:
            # Initialize with the model's prediction as prior
            self.binary_calibrators[condition] = BetaDistribution(
                alpha=max(1.0, predicted_prob * 10),
                beta=max(1.0, (1 - predicted_prob) * 10),
            )

        self.binary_calibrators[condition].update(observed_success)
        self.n_observations += 1

        return self.binary_calibrators[condition].mean

    def calibrate_continuous(
        self, parameter: str, predicted_value: float, observed_value: float
    ) -> tuple[float, float]:
        """Calibrate a continuous prediction; returns (mean, uncertainty)."""
        if parameter not in self.continuous_calibrators:
            self.continuous_calibrators[parameter] = GaussianConjugate(
                prior_mean=predicted_value,
                prior_variance=abs(predicted_value) * 0.3 + 0.1,
                prior_strength=1.0,
            )

        self.continuous_calibrators[parameter].update(observed_value)
        self.n_observations += 1

        cal = self.continuous_calibrators[parameter]
        return cal.mean, cal.uncertainty

    def get_confidence(self, parameter: str) -> tuple[float, float]:
        """Calibrated mean and uncertainty for a parameter."""
        if parameter in self.continuous_calibrators:
            gaussian = self.continuous_calibrators[parameter]
            return gaussian.mean, gaussian.uncertainty
        if parameter in self.binary_calibrators:
            beta = self.binary_calibrators[parameter]
            ci = beta.credible_interval()
            return beta.mean, (ci[1] - ci[0]) / 2
        return 0.5, 0.5  # uninformed prior

    def summary(self) -> dict[str, object]:
        """Calibration summary statistics."""
        return {
            "total_observations": self.n_observations,
            "binary_conditions": len(self.binary_calibrators),
            "continuous_parameters": len(self.continuous_calibrators),
            "conditions": {
                name: {"mean": cal.mean, "ci_95": cal.credible_interval()}
                for name, cal in self.binary_calibrators.items()
            },
            "parameters": {
                name: {"mean": cal.mean, "uncertainty": cal.uncertainty}
                for name, cal in self.continuous_calibrators.items()
            },
        }


__all__ = ["BayesianCalibration", "BetaDistribution", "GaussianConjugate"]
