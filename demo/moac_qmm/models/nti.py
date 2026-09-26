"""Narrow therapeutic index engine — SPOF #21 annihilated.

Dedicated engine for NTI drugs (warfarin, digoxin). Requires
genotype-guided precision dosing.

Production defect fix (D-07): v28 passed CYP2C19 status where CYP2C9 was
required for warfarin metabolism. ``GenomicTensor`` now carries a
dedicated ``cyp2c9`` field and the engine passes it here.
"""

from __future__ import annotations

import logging
from typing import Any

from moac_qmm.constants import NTI_DIGOXIN_THERAPEUTIC, NTI_WARFARIN_INR_TARGET
from moac_qmm.exceptions import NTIToxicityKill

logger = logging.getLogger(__name__)


class NarrowTherapeuticIndexEngine:
    """Genotype-guided NTI dosing and toxicity gates."""

    def check_warfarin(
        self,
        vkorc1_genotype: str,
        cyp2c9_genotype: str,
        vitamin_k_intake: float,  # noqa: ARG002 — parity; reserved for v30
        inr_current: float,
        interacting_drugs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Warfarin sensitivity, metabolism and interaction screening."""
        if "*2" in vkorc1_genotype or "*3" in vkorc1_genotype:
            sensitivity = 2.0
            logger.warning(
                "VKORC1 %s: Increased sensitivity. Standard dose → bleeding risk.",
                vkorc1_genotype,
            )
        else:
            sensitivity = 1.0

        if "*2" in cyp2c9_genotype or "*3" in cyp2c9_genotype:
            metabolism_rate = 0.5
            logger.warning(
                "CYP2C9 %s: Slow metabolism. Accumulation → INR overshoot.",
                cyp2c9_genotype,
            )
        else:
            metabolism_rate = 1.0

        interactions = interacting_drugs or []
        interaction_multiplier = 1.0
        if "Amiodarone" in interactions:
            interaction_multiplier *= 0.5
            logger.warning("Amiodarone: Warfarin clearance -50%%. Reduce dose 50%%.")
        if "Fluconazole" in interactions:
            interaction_multiplier *= 0.7
            logger.warning("Fluconazole: CYP2C9 inhibition.")

        if inr_current > NTI_WARFARIN_INR_TARGET[1]:
            msg = (
                f"[NTI-KILL] INR={inr_current:.1f} > {NTI_WARFARIN_INR_TARGET[1]}. "
                f"Bleeding risk. Vitamin K + FFP required."
            )
            logger.critical(msg)
            raise NTIToxicityKill(msg)
        if inr_current < NTI_WARFARIN_INR_TARGET[0]:
            logger.warning(
                "INR=%.1f < %.1f. Thrombosis risk.", inr_current, NTI_WARFARIN_INR_TARGET[0]
            )

        dose_factor = 1.0 / (sensitivity * (1.0 / metabolism_rate) * (1.0 / interaction_multiplier))

        return {
            "sensitivity": sensitivity,
            "metabolism_rate": metabolism_rate,
            "interaction_multiplier": interaction_multiplier,
            "recommended_dose_factor": dose_factor,
            "inr_in_range": NTI_WARFARIN_INR_TARGET[0] <= inr_current <= NTI_WARFARIN_INR_TARGET[1],
        }

    def check_digoxin(
        self,
        digoxin_level: float,
        gfr: float,
        potassium: float,
        interacting_drugs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Digoxin level, renal adjustment and interaction screening."""
        if digoxin_level > NTI_DIGOXIN_THERAPEUTIC[1]:
            msg = (
                f"[NTI-KILL] Digoxin={digoxin_level:.1f} ng/mL > "
                f"{NTI_DIGOXIN_THERAPEUTIC[1]}. Arrhythmia risk. "
                f"Digoxin Fab antibodies required."
            )
            logger.critical(msg)
            raise NTIToxicityKill(msg)
        if potassium < 3.5:
            logger.warning("K+=%.1f mEq/L. Hypokalemia potentiates digoxin toxicity.", potassium)

        interactions = interacting_drugs or []
        if "Verapamil" in interactions:
            logger.warning("Verapamil: P-gp inhibition → digoxin clearance -50%%.")

        return {
            "level_in_range": (
                NTI_DIGOXIN_THERAPEUTIC[0] <= digoxin_level <= NTI_DIGOXIN_THERAPEUTIC[1]
            ),
            "renal_adjustment_needed": gfr < 60,
        }


__all__ = ["NarrowTherapeuticIndexEngine"]
