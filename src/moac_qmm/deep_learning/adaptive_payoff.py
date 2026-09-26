"""Adaptive payoff matrix — SPOF #26 annihilated.

The game-theory payoff matrix is no longer hardcoded. It learns from
treatment outcomes via gradient-free hill climbing. The pathogen's
payoff adjusts inversely (zero-sum assumption).

Production defect fix (D-10): pure-equilibrium detection used float
equality on learned payoffs; now tolerant via ``np.isclose``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class AdaptivePayoffMatrix:
    """Payoff matrix that learns from observed outcomes."""

    pathogen_strategies: list[str] = field(
        default_factory=lambda: [
            "PLANKTONIC_FAST",
            "BIOFILM_FORTIFY",
            "PERSISTER_DORMANT",
            "EFFLUX_PUMP_UPREG",
            "TARGET_MUTATE",
        ]
    )
    treatment_strategies: list[str] = field(
        default_factory=lambda: [
            "BACTERICIDAL_HIGH",
            "BACTERIOSTATIC_MAINT",
            "BIOFILM_DISRUPT",
            "PHAGE_THERAPY",
            "IMMUNE_POTENTIATE",
        ]
    )

    # Initial payoff matrix [pathogen, treatment] = [p_payoff, t_payoff]
    _initial_payoffs: np.ndarray = field(
        default_factory=lambda: np.array(
            [
                [[2, 8], [6, 4], [3, 7], [1, 9], [4, 6]],
                [[7, 3], [8, 2], [3, 7], [5, 5], [6, 4]],
                [[9, 1], [9, 1], [6, 4], [8, 2], [7, 3]],
                [[6, 4], [7, 3], [5, 5], [4, 6], [6, 4]],
                [[8, 2], [9, 1], [7, 3], [3, 7], [8, 2]],
            ]
        )
    )

    def __post_init__(self) -> None:
        self.payoff_matrix = self._initial_payoffs.copy().astype(float)
        self.n_updates = 0
        self.learning_rate = 0.1
        self.update_history: list[dict[str, Any]] = []

    def update_from_outcome(
        self,
        pathogen_strategy: str,
        treatment_strategy: str,
        treatment_success: bool,
        magnitude: float = 1.0,
    ) -> None:
        """Update the payoff matrix from an observed treatment outcome."""
        p_idx = self._safe_index(pathogen_strategy, self.pathogen_strategies)
        t_idx = self._safe_index(treatment_strategy, self.treatment_strategies)

        old_p, old_t = self.payoff_matrix[p_idx, t_idx]

        if treatment_success:
            self.payoff_matrix[p_idx, t_idx, 1] = min(10, old_t + self.learning_rate * magnitude)
            self.payoff_matrix[p_idx, t_idx, 0] = max(
                0, old_p - self.learning_rate * magnitude * 0.5
            )
        else:
            self.payoff_matrix[p_idx, t_idx, 1] = max(0, old_t - self.learning_rate * magnitude)
            self.payoff_matrix[p_idx, t_idx, 0] = min(
                10, old_p + self.learning_rate * magnitude * 0.5
            )

        self.n_updates += 1
        self.update_history.append(
            {
                "update": self.n_updates,
                "pathogen": pathogen_strategy,
                "treatment": treatment_strategy,
                "success": treatment_success,
                "old_t_payoff": float(old_t),
                "new_t_payoff": float(self.payoff_matrix[p_idx, t_idx, 1]),
            }
        )

    @staticmethod
    def _safe_index(name: str, names: list[str]) -> int:
        try:
            return names.index(name)
        except ValueError:
            return 0

    def get_payoff(self, pathogen_strategy: str, treatment_strategy: str) -> tuple[float, float]:
        """Current (pathogen_payoff, treatment_payoff)."""
        p_idx = self._safe_index(pathogen_strategy, self.pathogen_strategies)
        t_idx = self._safe_index(treatment_strategy, self.treatment_strategies)
        p, t = self.payoff_matrix[p_idx, t_idx]
        return float(p), float(t)

    def find_nash_equilibria(self) -> list[dict[str, Any]]:
        """Find pure Nash equilibria in the current (learned) payoff matrix."""
        n_p = len(self.pathogen_strategies)
        n_t = len(self.treatment_strategies)
        equilibria: list[dict[str, Any]] = []

        for i in range(n_p):
            for j in range(n_t):
                p_payoff = self.payoff_matrix[i, j, 0]
                t_payoff = self.payoff_matrix[i, j, 1]

                p_best = max(self.payoff_matrix[i2, j, 0] for i2 in range(n_p))
                t_best = max(self.payoff_matrix[i, j2, 1] for j2 in range(n_t))

                if np.isclose(p_payoff, p_best) and np.isclose(t_payoff, t_best):
                    equilibria.append(
                        {
                            "pathogen": self.pathogen_strategies[i],
                            "treatment": self.treatment_strategies[j],
                            "p_payoff": float(p_payoff),
                            "t_payoff": float(t_payoff),
                        }
                    )
        return equilibria

    def calc_minimax(self) -> dict[str, Any]:
        """Minimax strategy on learned payoffs."""
        n_p = len(self.pathogen_strategies)
        n_t = len(self.treatment_strategies)

        worst_cases: list[dict[str, Any]] = []
        for j in range(n_t):
            worst_p = max(self.payoff_matrix[i, j, 0] for i in range(n_p))
            worst_idx = int(np.argmax([self.payoff_matrix[i, j, 0] for i in range(n_p)]))
            t_vs_worst = float(self.payoff_matrix[worst_idx, j, 1])
            worst_cases.append(
                {
                    "treatment": self.treatment_strategies[j],
                    "worst_pathogen_payoff": float(worst_p),
                    "treatment_payoff_vs_worst": t_vs_worst,
                }
            )

        best = min(worst_cases, key=lambda x: x["worst_pathogen_payoff"])
        return {
            "minimax_treatment": best["treatment"],
            "worst_case_pathogen_payoff": best["worst_pathogen_payoff"],
            "treatment_payoff_vs_worst": best["treatment_payoff_vs_worst"],
            "all_strategies": worst_cases,
        }


__all__ = ["AdaptivePayoffMatrix"]
