"""Biophysical model layer — the 23 v28 tensors, production-hardened.

Every module here is a faithful port of the v28 single-file kernel with
three production changes:

1. ``print()`` side-effects → :mod:`logging` (library-safe, capturable).
2. Stochastic models accept an injected ``numpy.random.Generator``
   (deterministic, thread-safe; no global RNG state).
3. Full type annotations + explicit constant imports (no wildcards).
"""

from moac_qmm.models.anti_persona import AntiPersonaEscapeV2
from moac_qmm.models.autophagy import AutophagyApoptosisToggle
from moac_qmm.models.chrono import ChronopharmacologyModulator
from moac_qmm.models.clearance import RenalHepaticClearance
from moac_qmm.models.cytokine import CytokineStormVector
from moac_qmm.models.ddi import DrugDrugInteractionTensor
from moac_qmm.models.epigenetic import EpigeneticAgeClock
from moac_qmm.models.game_theory import PathogenGameTheory
from moac_qmm.models.genomic import GenomicTensor
from moac_qmm.models.hpa import HPAAxisModel
from moac_qmm.models.hypoxia import HypoxiaTensor
from moac_qmm.models.microbiome import MicrobiomeMetabolizer
from moac_qmm.models.nti import NarrowTherapeuticIndexEngine
from moac_qmm.models.nutrients import NutrientSubstrateMatrix
from moac_qmm.models.organ_crosstalk import OrganCrosstalkTensor
from moac_qmm.models.pk_solver import MultiCompartmentPK, TimeSeriesPKSolver
from moac_qmm.models.qsense import QSenseGovernor, SpofLedger
from moac_qmm.models.quantum_receptor import QuantumDrugReceptor
from moac_qmm.models.sleep import SleepArchitectureTensor
from moac_qmm.models.toxins import ExogenousToxinLoad
from moac_qmm.models.vagal import VagalToneVoltage

__all__ = [
    "AntiPersonaEscapeV2",
    "AutophagyApoptosisToggle",
    "ChronopharmacologyModulator",
    "CytokineStormVector",
    "DrugDrugInteractionTensor",
    "EpigeneticAgeClock",
    "ExogenousToxinLoad",
    "GenomicTensor",
    "HPAAxisModel",
    "HypoxiaTensor",
    "MicrobiomeMetabolizer",
    "MultiCompartmentPK",
    "NarrowTherapeuticIndexEngine",
    "NutrientSubstrateMatrix",
    "OrganCrosstalkTensor",
    "PathogenGameTheory",
    "QSenseGovernor",
    "QuantumDrugReceptor",
    "RenalHepaticClearance",
    "SleepArchitectureTensor",
    "SpofLedger",
    "TimeSeriesPKSolver",
    "VagalToneVoltage",
]
