"""Exception hierarchy for the Strata-Oblivion Kernel.

Every kernel abort carries a human-readable reason string. The engine
converts these into a structured ``{"error": ...}`` result unless the
caller opts into ``raise_on_abort``.
"""

from __future__ import annotations


class StrataRejection(Exception):
    """Hard rejection — biological constraint violated."""


class EdgeCaseCascade(Exception):
    """Edge case cascade — systemic failure imminent."""


class CytokineStormDetected(Exception):
    """IL-6/TNF-α storm detected — macrophage activation syndrome."""


class HypoxiaCascade(Exception):
    """CYP450 oxygen-starved — drug clearance → zero."""


class NutrientDepletionKill(Exception):
    """Critical nutrient below Liebig's Minimum — restitution impossible."""


class OrganCrosstalkFailure(Exception):
    """Multi-organ failure — cascading collapse."""


class ToxinOverloadKill(Exception):
    """Exogenous toxin exceeds 2x toxic threshold."""


class SleepDeprivationKill(Exception):
    """N3 sleep critically deficient — glymphatic failure."""


class NTIToxicityKill(Exception):
    """Narrow therapeutic index drug outside safe range."""


class QuantumReceptorFailure(Exception):
    """P(therapeutic effect) below gate in strict Monte Carlo mode."""


class PathogenDominanceNash(Exception):
    """Pathogen has dominant strategy — treatment cannot win."""


class CalibrationError(Exception):
    """Bayesian calibration failed — insufficient data."""


class ModelNotTrainedError(Exception):
    """Deep learning model has not been trained."""


__all__ = [
    "CalibrationError",
    "CytokineStormDetected",
    "EdgeCaseCascade",
    "HypoxiaCascade",
    "ModelNotTrainedError",
    "NTIToxicityKill",
    "NutrientDepletionKill",
    "OrganCrosstalkFailure",
    "PathogenDominanceNash",
    "QuantumReceptorFailure",
    "SleepDeprivationKill",
    "StrataRejection",
    "ToxinOverloadKill",
]
