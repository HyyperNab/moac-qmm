"""Epigenetic age clock — SPOF #11 annihilated."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class EpigeneticAgeClock:
    """Biological age determines repair velocity and telomere integrity."""

    def __init__(self, chronological_age: int, methylation_pace: float = 1.0) -> None:
        self.chrono_age = chronological_age
        self.methylation_pace = methylation_pace
        self.bio_age = int(chronological_age * methylation_pace)

    def calc_repair_velocity(self) -> float:
        """Repair velocity decays linearly beyond biological age 60."""
        if self.bio_age > 60:
            velocity = max(0.2, 1.0 - (self.bio_age - 40) * 0.02)
            logger.info(
                "Bio age=%d (chrono=%d). Repair velocity=%.2f.",
                self.bio_age,
                self.chrono_age,
                velocity,
            )
            return velocity
        return 1.0

    def calc_telomere_integrity(self, telomere_kb: float = 10.0) -> float:
        """Telomere integrity fraction; senescence below 5 kb."""
        if telomere_kb < 5.0:
            logger.warning("Telomere=%.1fkb. Replicative senescence.", telomere_kb)
            return 0.1
        return min(1.0, telomere_kb / 10.0)


__all__ = ["EpigeneticAgeClock"]
