"""Exogenous toxin load — SPOF #20 annihilated."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from moac_qmm.constants import (
    ALCOHOL_CYP2E1_INDUCTION,
    LEAD_TOXIC_THRESHOLD,
    MERCURY_TOXIC_THRESHOLD,
)
from moac_qmm.exceptions import ToxinOverloadKill

logger = logging.getLogger(__name__)


class ExogenousToxinLoad:
    """Heavy metals, pesticides, alcohol.

    Lead → ALAD inhibition → CYP450 synthesis impaired.
    Mercury → glutathione depletion → oxidative stress.
    Alcohol → CYP2E1 induction → accelerated co-substrate metabolism.
    """

    TOXIN_EFFECTS: ClassVar[dict[str, dict[str, Any]]] = {
        "lead": {
            "threshold": LEAD_TOXIC_THRESHOLD,
            "effects": [
                "ALAD inhibition",
                "Heme synthesis disruption",
                "CYP450 synthesis impaired",
            ],
            "cyp_derate": 0.7,
            "neuro_toxicity": True,
        },
        "mercury": {
            "threshold": MERCURY_TOXIC_THRESHOLD,
            "effects": [
                "Glutathione depletion",
                "Oxidative stress",
                "Mitochondrial dysfunction",
            ],
            "cyp_derate": 0.85,
            "neuro_toxicity": True,
        },
        "alcohol_chronic": {
            "threshold": ALCOHOL_CYP2E1_INDUCTION,
            "effects": ["CYP2E1 induction", "Glutathione depletion", "NAD+ depletion"],
            "cyp_derate": 1.0,
            "cyp2e1_induction": 3.0,
            "hepatotoxic": True,
        },
    }

    def __init__(self, toxins: dict[str, float] | None = None) -> None:
        self.toxins = toxins or {}

    def calc_toxin_cyp_derate(self) -> float:
        """Multiplicative CYP derate across toxic loads; may kill."""
        total_derate = 1.0
        for toxin_name, level in self.toxins.items():
            if toxin_name in self.TOXIN_EFFECTS:
                config = self.TOXIN_EFFECTS[toxin_name]
                threshold = float(config["threshold"])
                if level > threshold:
                    effects = ", ".join(str(e) for e in config["effects"])
                    logger.warning(
                        "%s=%.1f > threshold %.1f. Effects: %s.",
                        toxin_name,
                        level,
                        threshold,
                        effects,
                    )
                    total_derate *= float(config.get("cyp_derate", 1.0))

                    if config.get("neuro_toxicity") and level > threshold * 2:
                        msg = (
                            f"[TOXIN-KILL] {toxin_name} at {level:.1f} "
                            f"(2x toxic threshold). Neurotoxicity cascade. "
                            f"Chelation therapy required."
                        )
                        logger.critical(msg)
                        raise ToxinOverloadKill(msg)

                    if config.get("hepatotoxic"):
                        logger.warning(
                            "%s is hepatotoxic. Hepatic clearance further compromised.",
                            toxin_name,
                        )
        return total_derate

    def calc_cyp2e1_induction(self) -> float:
        """Chronic alcohol induces CYP2E1 (relevant for paracetamol toxicity)."""
        alcohol = self.toxins.get("alcohol_chronic", 0)
        if alcohol > ALCOHOL_CYP2E1_INDUCTION:
            induction = float(self.TOXIN_EFFECTS["alcohol_chronic"]["cyp2e1_induction"])
            logger.warning(
                "CYP2E1 induced %.1fx by chronic alcohol (%.0f g/day). "
                "WARNING: Paracetamol → NAPQI toxic metabolite production %.1fx. "
                "Hepatic necrosis risk. Reduce paracetamol dose by %.0f%%.",
                induction,
                alcohol,
                induction,
                (1 - 1 / induction) * 100,
            )
            return induction
        return 1.0

    def calc_glutathione_depletion(self) -> float:
        """Mercury + alcohol both deplete GSH."""
        gsh_fraction = 1.0
        mercury = self.toxins.get("mercury", 0)
        alcohol = self.toxins.get("alcohol_chronic", 0)

        if mercury > MERCURY_TOXIC_THRESHOLD:
            gsh_fraction *= 0.6
        if alcohol > ALCOHOL_CYP2E1_INDUCTION:
            gsh_fraction *= 0.5

        if gsh_fraction < 0.5:
            logger.warning(
                "Glutathione depleted to %.0f%%. Oxidative stress uncontrolled. "
                "NAC supplementation required.",
                gsh_fraction * 100,
            )
        return gsh_fraction


__all__ = ["ExogenousToxinLoad"]
