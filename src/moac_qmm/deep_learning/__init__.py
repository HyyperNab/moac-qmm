"""Deep learning layer for MOAC QMM.

Eliminates SPOFs #24-28:
    24. NeuralPKPredictor — replaces hardcoded PK parameters
    25. BayesianCalibration — calibrates predictions against outcomes
    26. AdaptivePayoffMatrix — learns game-theory payoffs from results
    27. ReinforcementLearningOptimizer — Q-learning for treatment policy
    28. OutcomeTracker — persistent feedback loop
"""

from moac_qmm.deep_learning.adaptive_payoff import AdaptivePayoffMatrix
from moac_qmm.deep_learning.bayesian_calibration import (
    BayesianCalibration,
    BetaDistribution,
    GaussianConjugate,
)
from moac_qmm.deep_learning.neural_pk import NeuralPKPredictor
from moac_qmm.deep_learning.outcome_tracker import OutcomeTracker
from moac_qmm.deep_learning.rl_optimizer import ReinforcementLearningOptimizer

__all__ = [
    "AdaptivePayoffMatrix",
    "BayesianCalibration",
    "BetaDistribution",
    "GaussianConjugate",
    "NeuralPKPredictor",
    "OutcomeTracker",
    "ReinforcementLearningOptimizer",
]
