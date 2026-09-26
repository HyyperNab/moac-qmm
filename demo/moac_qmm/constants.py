"""Universal biophysical constants and Lagom boundaries.

Every constant in this module must be registered in
:mod:`moac_qmm.evidence` with an honest provenance tier.
No constant in this kernel is clinically verified — see docs/EVIDENCE.md.
"""

from __future__ import annotations

# ── Core thresholds ──
VOLTAGE_ANCHOR_MG = 0.85  # mmol/L: NMDA stability floor
CRITICAL_PH_THRESHOLD = 4.0  # Minimal pH for epithelial restitution
DIC_ENTROPY_TRIPWIRE = 0.88  # 3-sigma Waterhouse-Friderichsen threshold
LAGOM_NBE_MINIMUM = 0.20  # Net Biomass Efficiency floor

# ── Hypoxia ──
HYPOXIA_CYP450_FLOOR = 0.40  # SpO2 below this → CYP450 oxygen-starved
SPO2_NOMINAL = 98.0  # Reference SpO2 for CYP450 derate normalisation

# ── Clearance ──
ALBUMIN_NORMAL = 4.0  # g/dL normal serum albumin
GFR_NORMAL = 90.0  # mL/min/1.73m²
HEPATIC_FLOW_NORMAL = 1500.0  # mL/min portal + arterial

# ── Cytokine ──
IL6_STORM_THRESHOLD = 80.0  # pg/mL — cytokine storm onset
TNF_ALPHA_LETHAL = 50.0  # pg/mL — tissue necrosis risk

# ── Vagal ──
HRV_VAGAL_FLOOR = 20.0  # RMSSD ms — parasympathetic collapse floor

# ── Autophagy ──
MTOR_AUTOPHAGY_THRESHOLD = 0.5  # mTOR/AMPK ratio below this = demolition mode

# ── Microbiome ──
MICROBIOME_DIVERSITY_FLOOR = 2.5  # Shannon diversity index floor

# ── Chrono ──
CHRONO_PPI_OPTIMAL_WINDOW: tuple[float, float] = (6.0, 9.0)  # PPI efficacy peak

# ── Protein binding ──
PROTEIN_BINDING_CRITICAL = 0.90  # Free fraction spike if displacement > 90%

# ── Receptor ──
RECEPTOR_OCCUPANCY_THRESHOLD = 0.80  # occupancy required for therapeutic effect

# ── Sleep ──
N3_SLEEP_MINIMUM_HOURS = 1.5  # deep sleep minimum for GH + glymphatic
GLYMPHATIC_CLEARANCE_RATE = 0.65  # fraction of neurotoxin clearance during N3

# ── HPA ──
CORTISOL_AWAKENING_PEAK = 25.0  # µg/dL at ~8 AM
DHEA_NORMAL = 200.0  # µg/dL

# ── NTI ──
NTI_WARFARIN_INR_TARGET: tuple[float, float] = (2.0, 3.0)
NTI_DIGOXIN_THERAPEUTIC: tuple[float, float] = (0.8, 2.0)  # ng/mL

# ── Toxins ──
LEAD_TOXIC_THRESHOLD = 5.0  # µg/dL blood lead
MERCURY_TOXIC_THRESHOLD = 5.0  # µg/L blood mercury
ALCOHOL_CYP2E1_INDUCTION = 40.0  # g/day chronic → CYP2E1 upregulation

# ── Population allele frequencies ──
# Claimed origin: 1000 Genomes / PharmGKB. Values were NOT verified against
# those sources (tier: SECONDARY_REVIEW_UNVERIFIED). Treat as approximate.
ALLELE_FREQUENCIES: dict[str, dict[str, float]] = {
    "CYP2C19": {"*1": 0.65, "*2": 0.15, "*3": 0.05, "*17": 0.15},
    "CYP2D6": {"*1": 0.60, "*4": 0.20, "*5": 0.05, "*10": 0.15},
    "CYP3A4": {"*1": 0.85, "*22": 0.10, "*other": 0.05},
    "SLCO1B1": {"*1": 0.70, "*5": 0.15, "*15": 0.10, "*17": 0.05},
    "VKORC1": {"*1": 0.37, "*2": 0.37, "*3": 0.26},
}

__all__ = [
    "ALBUMIN_NORMAL",
    "ALCOHOL_CYP2E1_INDUCTION",
    "ALLELE_FREQUENCIES",
    "CHRONO_PPI_OPTIMAL_WINDOW",
    "CORTISOL_AWAKENING_PEAK",
    "CRITICAL_PH_THRESHOLD",
    "DHEA_NORMAL",
    "DIC_ENTROPY_TRIPWIRE",
    "GFR_NORMAL",
    "GLYMPHATIC_CLEARANCE_RATE",
    "HEPATIC_FLOW_NORMAL",
    "HRV_VAGAL_FLOOR",
    "HYPOXIA_CYP450_FLOOR",
    "IL6_STORM_THRESHOLD",
    "LAGOM_NBE_MINIMUM",
    "LEAD_TOXIC_THRESHOLD",
    "MERCURY_TOXIC_THRESHOLD",
    "MICROBIOME_DIVERSITY_FLOOR",
    "MTOR_AUTOPHAGY_THRESHOLD",
    "N3_SLEEP_MINIMUM_HOURS",
    "NTI_DIGOXIN_THERAPEUTIC",
    "NTI_WARFARIN_INR_TARGET",
    "PROTEIN_BINDING_CRITICAL",
    "RECEPTOR_OCCUPANCY_THRESHOLD",
    "SPO2_NOMINAL",
    "TNF_ALPHA_LETHAL",
    "VOLTAGE_ANCHOR_MG",
]
