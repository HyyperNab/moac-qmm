"""Organ crosstalk tensor — SPOF #18 annihilated.

Organs don't fail independently. They form a cascading network:
gut-liver, gut-kidney, liver-brain, heart-kidney, lung-gut axes.
"""

from __future__ import annotations

import logging
from typing import ClassVar

from moac_qmm.exceptions import OrganCrosstalkFailure

logger = logging.getLogger(__name__)


class OrganCrosstalkTensor:
    """Directed degradation graph over organ states (0=failure, 1=optimal)."""

    EDGES: ClassVar[list[tuple[str, str, float]]] = [
        ("gut", "liver", 0.3),
        ("liver", "brain", 0.25),
        ("gut", "kidney", 0.2),
        ("kidney", "heart", 0.4),
        ("heart", "kidney", 0.3),
        ("lung", "gut", 0.3),
        ("kidney", "liver", 0.15),
        ("liver", "kidney", 0.2),
    ]

    def __init__(self, organ_states: dict[str, float] | None = None) -> None:
        self.organs = organ_states or {
            "gut": 1.0,
            "liver": 1.0,
            "kidney": 1.0,
            "heart": 1.0,
            "lung": 1.0,
            "brain": 1.0,
        }

    def calc_crosstalk_cascade(self) -> dict[str, float]:
        """Propagate degradation along the edges; may raise multi-organ kill."""
        adjusted = dict(self.organs)
        cascade_log: list[str] = []

        for source, target, coeff in self.EDGES:
            source_state = self.organs.get(source, 1.0)
            degradation = (1.0 - source_state) * coeff
            adjusted[target] = max(0.0, adjusted.get(target, 1.0) - degradation)

            if degradation > 0.1:
                cascade_log.append(
                    f"[CROSSTALK] {source}→{target}: degradation={degradation:.2f} "
                    f"({source}={source_state:.1f} → {target}={adjusted[target]:.2f})"
                )

        failing = [o for o, s in adjusted.items() if s < 0.3]
        if len(failing) >= 2:
            msg = (
                f"[CROSSTALK-KILL] Multi-organ failure: {failing}. "
                f"Cascading collapse. ICU + organ support required."
            )
            logger.critical(msg)
            raise OrganCrosstalkFailure(msg)

        for entry in cascade_log:
            logger.warning(entry)

        return adjusted


__all__ = ["OrganCrosstalkTensor"]
