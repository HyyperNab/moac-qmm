"""Frozen public API manifest.

The exported surface of every public (non-internal) module is frozen
here. ``scripts/validate_manifest.py`` and ``tests/test_manifest.py``
fail the build when the surface drifts without a deliberate manifest
update. This is the interface gate between kernel generations.
"""

from __future__ import annotations

FROZEN_API: dict[str, frozenset[str]] = {
    "moac_qmm": frozenset(
        {
            "QMMEngine",
            "StableHomeostasisOptimizer",
            "PatientTelemetry",
            "__version__",
        }
    ),
    "moac_qmm.models": frozenset(
        {
            "GenomicTensor",
            "RenalHepaticClearance",
            "DrugDrugInteractionTensor",
            "QuantumDrugReceptor",
            "CytokineStormVector",
            "VagalToneVoltage",
            "HPAAxisModel",
            "HypoxiaTensor",
            "MicrobiomeMetabolizer",
            "NutrientSubstrateMatrix",
            "ChronopharmacologyModulator",
            "EpigeneticAgeClock",
            "AutophagyApoptosisToggle",
            "MultiCompartmentPK",
            "TimeSeriesPKSolver",
            "SleepArchitectureTensor",
            "ExogenousToxinLoad",
            "OrganCrosstalkTensor",
            "NarrowTherapeuticIndexEngine",
            "PathogenGameTheory",
            "AntiPersonaEscapeV2",
            "QSenseGovernor",
            "SpofLedger",
        }
    ),
    "moac_qmm.deep_learning": frozenset(
        {
            "NeuralPKPredictor",
            "BayesianCalibration",
            "BetaDistribution",
            "GaussianConjugate",
            "AdaptivePayoffMatrix",
            "ReinforcementLearningOptimizer",
            "OutcomeTracker",
        }
    ),
    "moac_qmm.constants": frozenset(
        {
            "VOLTAGE_ANCHOR_MG",
            "CRITICAL_PH_THRESHOLD",
            "DIC_ENTROPY_TRIPWIRE",
            "LAGOM_NBE_MINIMUM",
            "HYPOXIA_CYP450_FLOOR",
            "SPO2_NOMINAL",
            "ALBUMIN_NORMAL",
            "GFR_NORMAL",
            "HEPATIC_FLOW_NORMAL",
            "IL6_STORM_THRESHOLD",
            "TNF_ALPHA_LETHAL",
            "HRV_VAGAL_FLOOR",
            "MTOR_AUTOPHAGY_THRESHOLD",
            "MICROBIOME_DIVERSITY_FLOOR",
            "CHRONO_PPI_OPTIMAL_WINDOW",
            "PROTEIN_BINDING_CRITICAL",
            "RECEPTOR_OCCUPANCY_THRESHOLD",
            "N3_SLEEP_MINIMUM_HOURS",
            "GLYMPHATIC_CLEARANCE_RATE",
            "CORTISOL_AWAKENING_PEAK",
            "DHEA_NORMAL",
            "NTI_WARFARIN_INR_TARGET",
            "NTI_DIGOXIN_THERAPEUTIC",
            "LEAD_TOXIC_THRESHOLD",
            "MERCURY_TOXIC_THRESHOLD",
            "ALCOHOL_CYP2E1_INDUCTION",
            "ALLELE_FREQUENCIES",
        }
    ),
    "moac_qmm.exceptions": frozenset(
        {
            "StrataRejection",
            "EdgeCaseCascade",
            "CytokineStormDetected",
            "HypoxiaCascade",
            "NutrientDepletionKill",
            "OrganCrosstalkFailure",
            "ToxinOverloadKill",
            "SleepDeprivationKill",
            "NTIToxicityKill",
            "QuantumReceptorFailure",
            "PathogenDominanceNash",
            "CalibrationError",
            "ModelNotTrainedError",
        }
    ),
    "moac_qmm.evidence": frozenset(
        {
            "EVIDENCE_REGISTER",
            "EvidenceTier",
            "QUARANTINED",
        }
    ),
}


def _public_names(module: str) -> set[str]:
    import importlib

    mod = importlib.import_module(module)
    exported = getattr(mod, "__all__", None)
    if exported is not None:
        return set(exported)
    return {n for n in dir(mod) if not n.startswith("_")}


def validate() -> list[str]:
    """Return a list of manifest violations (empty when the API is frozen clean)."""
    violations: list[str] = []
    for module, expected in FROZEN_API.items():
        actual = _public_names(module)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            violations.append(f"{module}: missing exports {missing}")
        if extra:
            violations.append(f"{module}: undeclared exports {extra}")
    return violations


__all__ = ["FROZEN_API", "validate"]
