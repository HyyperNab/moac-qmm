"""Pathogen game theory — SPOF #9 full expansion.

The pathogen is a STRATEGIC OPPONENT. 5×5 payoff matrix of pathogen
strategies vs. treatment strategies with Nash equilibrium, minimax and
mixed-strategy computation (fictitious play).
"""

from __future__ import annotations

from typing import Any, ClassVar

import numpy as np

from moac_qmm.exceptions import PathogenDominanceNash


class PathogenGameTheory:
    """Adversarial game-theoretic pathogen model."""

    PATHOGEN_STRATEGIES: ClassVar[list[str]] = [
        "PLANKTONIC_FAST",
        "BIOFILM_FORTIFY",
        "PERSISTER_DORMANT",
        "EFFLUX_PUMP_UPREG",
        "TARGET_MUTATE",
    ]

    TREATMENT_STRATEGIES: ClassVar[list[str]] = [
        "BACTERICIDAL_HIGH",
        "BACTERIOSTATIC_MAINT",
        "BIOFILM_DISRUPT",
        "PHAGE_THERAPY",
        "IMMUNE_POTENTIATE",
    ]

    # PAYOFF_MATRIX[i][j] = [pathogen_payoff, treatment_payoff]
    # pathogen_payoff: 0=eliminated, 10=dominant
    # treatment_payoff: 0=total failure, 10=total success
    PAYOFF_MATRIX: ClassVar[np.ndarray] = np.array(
        [
            # BACT_C  BACT_S  BIOFILM  PHAGE  IMMUNE
            [[2, 8], [6, 4], [3, 7], [1, 9], [4, 6]],  # PLANKTONIC_FAST
            [[7, 3], [8, 2], [3, 7], [5, 5], [6, 4]],  # BIOFILM_FORTIFY
            [[9, 1], [9, 1], [6, 4], [8, 2], [7, 3]],  # PERSISTER_DORMANT
            [[6, 4], [7, 3], [5, 5], [4, 6], [6, 4]],  # EFFLUX_PUMP_UPREG
            [[8, 2], [9, 1], [7, 3], [3, 7], [8, 2]],  # TARGET_MUTATE
        ]
    )

    def find_nash_equilibrium(self) -> dict[str, Any]:
        """Enumerate pure-strategy Nash equilibria."""
        nash_equilibria: list[dict[str, Any]] = []
        n_p = len(self.PATHOGEN_STRATEGIES)
        n_t = len(self.TREATMENT_STRATEGIES)

        for i in range(n_p):
            for j in range(n_t):
                p_payoff = self.PAYOFF_MATRIX[i, j][0]
                t_payoff = self.PAYOFF_MATRIX[i, j][1]

                p_best = max(self.PAYOFF_MATRIX[i2, j][0] for i2 in range(n_p))
                t_best = max(self.PAYOFF_MATRIX[i, j2][1] for j2 in range(n_t))

                if p_payoff == p_best and t_payoff == t_best:
                    nash_equilibria.append(
                        {
                            "pathogen_strategy": self.PATHOGEN_STRATEGIES[i],
                            "treatment_strategy": self.TREATMENT_STRATEGIES[j],
                            "pathogen_payoff": int(p_payoff),
                            "treatment_payoff": int(t_payoff),
                        }
                    )

        return {"nash_equilibria": nash_equilibria, "count": len(nash_equilibria)}

    def calc_minimax_strategy(self) -> dict[str, Any]:
        """Minimax: treatment that minimizes the pathogen's maximum payoff."""
        n_p = len(self.PATHOGEN_STRATEGIES)
        n_t = len(self.TREATMENT_STRATEGIES)

        treatment_worst_case: list[dict[str, Any]] = []
        for j in range(n_t):
            worst_p_payoff = max(self.PAYOFF_MATRIX[i, j][0] for i in range(n_p))
            worst_p_idx = int(np.argmax([self.PAYOFF_MATRIX[i, j][0] for i in range(n_p)]))
            t_payoff_vs_worst = int(self.PAYOFF_MATRIX[worst_p_idx, j][1])
            treatment_worst_case.append(
                {
                    "treatment": self.TREATMENT_STRATEGIES[j],
                    "worst_case_pathogen_payoff": int(worst_p_payoff),
                    "treatment_payoff_vs_worst": t_payoff_vs_worst,
                }
            )

        best = min(treatment_worst_case, key=lambda x: x["worst_case_pathogen_payoff"])

        return {
            "minimax_treatment": best["treatment"],
            "worst_case_pathogen_payoff": best["worst_case_pathogen_payoff"],
            "treatment_payoff_vs_worst": best["treatment_payoff_vs_worst"],
            "all_strategies": treatment_worst_case,
        }

    def calc_mixed_strategy_nash(self, iterations: int = 1000) -> dict[str, dict[str, float]]:
        """Approximate mixed-strategy Nash via fictitious play."""
        n_p = len(self.PATHOGEN_STRATEGIES)
        n_t = len(self.TREATMENT_STRATEGIES)

        p_p = np.ones(n_p) / n_p
        p_t = np.ones(n_t) / n_t

        for _ in range(iterations):
            # Pathogen best response
            p_expected = np.zeros(n_p)
            for i in range(n_p):
                for j in range(n_t):
                    p_expected[i] += p_t[j] * self.PAYOFF_MATRIX[i, j][0]
            best_p = int(np.argmax(p_expected))
            p_p = p_p * 0.99
            p_p[best_p] += 0.01
            p_p /= p_p.sum()

            # Treatment best response
            t_expected = np.zeros(n_t)
            for j in range(n_t):
                for i in range(n_p):
                    t_expected[j] += p_p[i] * self.PAYOFF_MATRIX[i, j][1]
            best_t = int(np.argmax(t_expected))
            p_t = p_t * 0.99
            p_t[best_t] += 0.01
            p_t /= p_t.sum()

        return {
            "pathogen_mixed": {self.PATHOGEN_STRATEGIES[i]: float(p_p[i]) for i in range(n_p)},
            "treatment_mixed": {self.TREATMENT_STRATEGIES[j]: float(p_t[j]) for j in range(n_t)},
        }

    def evaluate_pathogen_dominance(
        self, current_pathogen_strategy: str, current_treatment: str
    ) -> dict[str, Any]:
        """Evaluate whether the pathogen is playing a dominant strategy."""
        treatment_idx = (
            self.TREATMENT_STRATEGIES.index(current_treatment)
            if current_treatment in self.TREATMENT_STRATEGIES
            else 0
        )

        payoffs = {
            self.PATHOGEN_STRATEGIES[i]: int(self.PAYOFF_MATRIX[i, treatment_idx][0])
            for i in range(len(self.PATHOGEN_STRATEGIES))
        }

        best_pathogen = max(payoffs, key=lambda k: payoffs[k])
        current_payoff = payoffs.get(current_pathogen_strategy, 0)

        if current_pathogen_strategy == best_pathogen and payoffs[best_pathogen] > 7:
            msg = (
                f"[GAME-THEORY-KILL] Pathogen playing dominant strategy "
                f"'{best_pathogen}' with payoff {payoffs[best_pathogen]}/10. "
                f"Treatment '{current_treatment}' cannot win. "
                f"Switch to minimax-optimal strategy."
            )
            raise PathogenDominanceNash(msg)

        return {
            "current_strategy": current_pathogen_strategy,
            "best_response": best_pathogen,
            "current_payoff": current_payoff,
            "best_payoff": payoffs[best_pathogen],
            "switch_needed": current_pathogen_strategy != best_pathogen,
        }


__all__ = ["PathogenGameTheory"]
