"""Evidence register — per-constant provenance tiers.

Ground Truth or Silence: this kernel's biophysical constants originate
from the v28 research artifact WITHOUT accompanying citations. We refuse
to fabricate references. Every constant is therefore registered with an
honest provenance tier and must never be presented as clinically
verified.

Tiers
-----
``VERIFIED_PRIMARY``
    Peer-reviewed primary source, verified against the paper.
    (Currently: none.)
``SECONDARY_REVIEW_UNVERIFIED``
    Claimed origin (e.g. "1000 Genomes / PharmGKB") that was NOT
    verified against the source. Approximate — re-verify before use.
``HEURISTIC_KERNEL``
    Modelling assumption authored into the kernel. No citation exists.
``STRUCTURAL``
    Internal game-theory / architecture constant. No clinical claim.

A test enforces that every exported constant in :mod:`moac_qmm.constants`
is registered here. Constants may never claim ``VERIFIED_PRIMARY``
without a DOI note attached in the same PR.
"""

from __future__ import annotations

from enum import Enum


class EvidenceTier(str, Enum):
    """Provenance tiers for kernel constants."""

    VERIFIED_PRIMARY = "verified_primary"
    SECONDARY_REVIEW_UNVERIFIED = "secondary_review_unverified"
    HEURISTIC_KERNEL = "heuristic_kernel"
    STRUCTURAL = "structural"


_KERNEL = (
    EvidenceTier.HEURISTIC_KERNEL,
    "v28 kernel assumption. No citation provided in source artifact. "
    "Do not treat as clinically validated.",
)


def _h(note: str) -> tuple[EvidenceTier, str]:
    return (EvidenceTier.HEURISTIC_KERNEL, f"v28 kernel assumption. {note}")


def _s(note: str) -> tuple[EvidenceTier, str]:
    return (EvidenceTier.STRUCTURAL, f"Internal model constant. {note}")


EVIDENCE_REGISTER: dict[str, tuple[EvidenceTier, str]] = {
    "VOLTAGE_ANCHOR_MG": _h(
        "NMDA stability floor; never used in computation, retained for parity."
    ),
    "CRITICAL_PH_THRESHOLD": _h("Minimal gastric pH for epithelial restitution."),
    "DIC_ENTROPY_TRIPWIRE": _h("Waterhouse-Friderichsen 3-sigma threshold."),
    "LAGOM_NBE_MINIMUM": _s("Net Biomass Efficiency floor (Lagom boundary)."),
    "HYPOXIA_CYP450_FLOOR": _h("SpO2 fraction below which CYP450 is oxygen-starved."),
    "SPO2_NOMINAL": _s("Reference SpO2 for derate normalisation."),
    "ALBUMIN_NORMAL": _h("Normal serum albumin g/dL. Textbook-plausible, unverified."),
    "GFR_NORMAL": _h("Normal GFR mL/min/1.73m². Textbook-plausible, unverified."),
    "HEPATIC_FLOW_NORMAL": _h("Normal portal+arterial hepatic flow mL/min."),
    "IL6_STORM_THRESHOLD": _h("IL-6 pg/mL cytokine storm onset."),
    "TNF_ALPHA_LETHAL": _h("TNF-α pg/mL tissue necrosis risk."),
    "HRV_VAGAL_FLOOR": _h("RMSSD ms parasympathetic collapse floor."),
    "MTOR_AUTOPHAGY_THRESHOLD": _h("mTOR/AMPK ratio below which tissue enters demolition mode."),
    "MICROBIOME_DIVERSITY_FLOOR": _h("Shannon diversity index floor."),
    "CHRONO_PPI_OPTIMAL_WINDOW": _h("Hour window for PPI efficacy peak."),
    "PROTEIN_BINDING_CRITICAL": _h("Protein-bound fraction above which displacement is lethal."),
    "RECEPTOR_OCCUPANCY_THRESHOLD": _h("Receptor occupancy required for therapeutic effect."),
    "N3_SLEEP_MINIMUM_HOURS": _h("Deep sleep minimum for GH + glymphatic function."),
    "GLYMPHATIC_CLEARANCE_RATE": _h("Fraction of neurotoxin clearance during N3."),
    "CORTISOL_AWAKENING_PEAK": _h("Cortisol µg/dL at ~8 AM."),
    "DHEA_NORMAL": _h("Normal DHEA-S µg/dL."),
    "NTI_WARFARIN_INR_TARGET": _h("Warfarin INR therapeutic target."),
    "NTI_DIGOXIN_THERAPEUTIC": _h("Digoxin ng/mL therapeutic range."),
    "LEAD_TOXIC_THRESHOLD": _h("Blood lead µg/dL toxicity threshold."),
    "MERCURY_TOXIC_THRESHOLD": _h("Blood mercury µg/L toxicity threshold."),
    "ALCOHOL_CYP2E1_INDUCTION": _h("Chronic alcohol g/day inducing CYP2E1."),
    "ALLELE_FREQUENCIES": (
        EvidenceTier.SECONDARY_REVIEW_UNVERIFIED,
        "Claimed origin 1000 Genomes / PharmGKB; NOT verified against those "
        "sources. Population frequencies vary by ancestry — approximate only.",
    ),
}

# Constants with no computation behind them in v29 (parity-only) may be
# quarantined here; the register test treats a missing entry as failure.
QUARANTINED: frozenset[str] = frozenset()

__all__ = ["EVIDENCE_REGISTER", "QUARANTINED", "EvidenceTier"]
