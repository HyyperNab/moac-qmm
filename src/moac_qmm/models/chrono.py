"""Chronopharmacology modulator — SPOF #10 annihilated."""

from __future__ import annotations

import logging
import math

from moac_qmm.constants import CHRONO_PPI_OPTIMAL_WINDOW

logger = logging.getLogger(__name__)


class ChronopharmacologyModulator:
    """Circadian biology modulates drug efficacy and immune function."""

    def __init__(self, current_hour: float = 8.0) -> None:
        self.hour = current_hour % 24.0

    def calc_ppi_efficacy_window(self) -> float:
        """PPI efficacy multiplier by dosing hour."""
        if CHRONO_PPI_OPTIMAL_WINDOW[0] <= self.hour <= CHRONO_PPI_OPTIMAL_WINDOW[1]:
            return 1.0
        if 9.0 < self.hour < 12.0:
            return 0.6
        logger.warning("PPI at hour %.0f. Outside window (6-9 AM). Efficacy ~30%%.", self.hour)
        return 0.3

    def calc_cortisol_immune_modulation(self) -> float:
        """Cortisol-driven immune dampening across the circadian phase."""
        cortisol_relative = 0.5 * (1 + math.cos(2 * math.pi * (self.hour - 8) / 24))
        return 1.0 - 0.3 * cortisol_relative


__all__ = ["ChronopharmacologyModulator"]
