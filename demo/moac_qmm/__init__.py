"""MOAC QMM — Strata-Oblivion Kernel.

A multi-dimensional medical decision engine. Research and educational
simulation only — **not a medical device**.
"""

from moac_qmm._version import __version__
from moac_qmm.engine import QMMEngine
from moac_qmm.optimizer import StableHomeostasisOptimizer
from moac_qmm.types import PatientTelemetry

__all__ = [
    "PatientTelemetry",
    "QMMEngine",
    "StableHomeostasisOptimizer",
    "__version__",
]
