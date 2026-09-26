"""Drug-drug interaction tensor — SPOF #3 annihilated."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from moac_qmm.constants import PROTEIN_BINDING_CRITICAL
from moac_qmm.exceptions import StrataRejection

logger = logging.getLogger(__name__)


class DrugDrugInteractionTensor:
    """Generalized DDI matrix — albumin competition + CYP450 competition."""

    CYP_INHIBITORS: ClassVar[dict[str, list[str]]] = {
        "CYP3A4": ["Ketoconazole", "Clarithromycin", "Ritonavir", "Grapefruit"],
        "CYP2C19": ["Fluconazole", "Fluvoxamine", "Omeprazole"],
        "CYP2D6": ["Paroxetine", "Fluoxetine", "Bupropion"],
    }

    def check_interactions(self, stack: list[dict[str, Any]]) -> list[str]:
        """Return DDI warnings for the stack; may raise on lethal displacement."""
        warnings: list[str] = []
        cyp_map: dict[str, list[str]] = {}
        for drug in stack:
            for isoform in drug.get("cyp_pathway", []):
                cyp_map.setdefault(isoform, []).append(str(drug["name"]))

        for isoform, drugs in cyp_map.items():
            if len(drugs) > 1:
                warnings.append(
                    f"[DDI-WARN] CYP450 competition: {drugs} all metabolized by "
                    f"{isoform}. Clearance bottleneck → accumulation → toxicity."
                )

        high_binders = [d for d in stack if float(d.get("protein_bound", 0)) > 0.90]
        if len(high_binders) > 1:
            warnings.append(
                f"[DDI-WARN] Albumin displacement war: "
                f"{[d['name'] for d in high_binders]} all >90% protein-bound. "
                f"Free fraction spike imminent."
            )
            avg_bound = sum(float(d.get("protein_bound", 0)) for d in high_binders) / len(
                high_binders
            )
            total_displacement = 1.0 - (1.0 - avg_bound)
            if total_displacement > PROTEIN_BINDING_CRITICAL:
                msg = (
                    f"[DDI-KILL] Protein binding displacement > "
                    f"{PROTEIN_BINDING_CRITICAL * 100:.0f}%. "
                    f"Free fraction explosion. Lethal toxicity window."
                )
                logger.error(msg)
                raise StrataRejection(msg)
        return warnings


__all__ = ["DrugDrugInteractionTensor"]
