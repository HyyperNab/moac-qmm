"""Pathogen game theory unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import PathogenDominanceNash
from moac_qmm.models import PathogenGameTheory


class TestPathogenGameTheory:
    def test_v28_payoff_matrix_has_no_pure_nash(self) -> None:
        """The v28 matrix deliberately contains no pure equilibrium.

        This is the kernel's core statement: against a strategic
        pathogen there is no stable deterministic treatment.
        """
        game = PathogenGameTheory()
        result = game.find_nash_equilibrium()
        assert result["count"] == 0
        assert result["nash_equilibria"] == []

    def test_minimax_prefers_biofilm_disruption(self) -> None:
        game = PathogenGameTheory()
        minimax = game.calc_minimax_strategy()
        assert minimax["minimax_treatment"] == "BIOFILM_DISRUPT"
        assert minimax["worst_case_pathogen_payoff"] == 7

    def test_mixed_strategy_nash_normalizes(self) -> None:
        game = PathogenGameTheory()
        mixed = game.calc_mixed_strategy_nash(iterations=100)
        assert sum(mixed["pathogen_mixed"].values()) == pytest.approx(1.0)
        assert sum(mixed["treatment_mixed"].values()) == pytest.approx(1.0)

    def test_dominant_pathogen_strategy_raises(self) -> None:
        game = PathogenGameTheory()
        with pytest.raises(PathogenDominanceNash):
            game.evaluate_pathogen_dominance("PERSISTER_DORMANT", "BACTERICIDAL_HIGH")

    def test_non_dominant_strategy_evaluates(self) -> None:
        game = PathogenGameTheory()
        result = game.evaluate_pathogen_dominance("PLANKTONIC_FAST", "PHAGE_THERAPY")
        assert result["switch_needed"] is True  # PERSISTER_DORMANT dominates PHAGE

    def test_strategy_lists_are_stable(self) -> None:
        game = PathogenGameTheory()
        assert len(game.PATHOGEN_STRATEGIES) == 5
        assert len(game.TREATMENT_STRATEGIES) == 5
        assert game.PAYOFF_MATRIX.shape == (5, 5, 2)
