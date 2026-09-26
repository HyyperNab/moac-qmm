"""Sleep architecture tensor — SPOF #19 annihilated."""

from __future__ import annotations

import logging

from moac_qmm.constants import GLYMPHATIC_CLEARANCE_RATE, N3_SLEEP_MINIMUM_HOURS

logger = logging.getLogger(__name__)


class SleepArchitectureTensor:
    """Deep sleep (N3) is when GH peaks, immune memory consolidates,
    and the glymphatic system clears neurotoxins."""

    def __init__(
        self,
        total_sleep_hours: float = 7.0,
        n3_percentage: float = 15.0,
        rem_percentage: float = 22.0,
        sleep_efficiency: float = 0.85,
        awakenings: int = 2,
    ) -> None:
        self.total_sleep = total_sleep_hours
        self.n3_pct = n3_percentage
        self.rem_pct = rem_percentage
        self.efficiency = sleep_efficiency
        self.awakenings = awakenings

    def calc_n3_hours(self) -> float:
        """Effective deep-sleep hours."""
        return self.total_sleep * self.efficiency * (self.n3_pct / 100)

    def calc_gh_pulse(self) -> float:
        """Growth hormone release scales with N3 duration."""
        n3_hours = self.calc_n3_hours()
        gh_peak = n3_hours * 1.3
        if gh_peak < 1.0:
            logger.warning(
                "N3=%.1fh. GH pulse=%.1f ng/mL. Tissue repair hormone insufficient.",
                n3_hours,
                gh_peak,
            )
        return gh_peak

    def calc_glymphatic_clearance(self) -> float:
        """Glymphatic flow is 60-80% active only during N3."""
        n3_hours = self.calc_n3_hours()
        if n3_hours < N3_SLEEP_MINIMUM_HOURS:
            logger.warning(
                "N3=%.1fh < %.1fh minimum. Glymphatic clearance insufficient. "
                "Neurotoxin accumulation.",
                n3_hours,
                N3_SLEEP_MINIMUM_HOURS,
            )
            return 0.2
        return min(1.0, n3_hours / 2.0) * GLYMPHATIC_CLEARANCE_RATE

    def calc_immune_consolidation(self) -> float:
        """T-cell trafficking to lymph nodes during sleep."""
        if self.total_sleep < 6.0:
            logger.warning(
                "Total sleep=%.1fh. Immune memory consolidation impaired. "
                "Vaccine response reduced ~50%%.",
                self.total_sleep,
            )
            return 0.5
        return 1.0

    def calc_sleep_fragmentation_penalty(self) -> float:
        """Frequent awakenings disrupt sleep architecture."""
        if self.awakenings > 4:
            logger.warning(
                "%d awakenings. Sleep fragmented. Sympathetic overdrive between arousals.",
                self.awakenings,
            )
            return 0.6
        return 1.0


__all__ = ["SleepArchitectureTensor"]
