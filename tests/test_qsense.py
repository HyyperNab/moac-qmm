"""QSense governor and SPOF ledger unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.models import QSenseGovernor, SpofLedger


class TestQSenseGovernor:
    def test_small_stack_untouched(self) -> None:
        assert QSenseGovernor().apply_lagom_throttle(2, 0.05) == 2

    def test_massive_low_entropy_stack_purged(self) -> None:
        assert QSenseGovernor().apply_lagom_throttle(7, 0.1) == 3

    def test_massive_high_entropy_stack_untouched(self) -> None:
        assert QSenseGovernor().apply_lagom_throttle(7, 0.5) == 7


class TestSpofLedger:
    def test_all_priors_initialized(self) -> None:
        ledger = SpofLedger(allele_frequency=1.0)
        assert len(ledger.priors) == 10

    def test_failed_assumption_slashes_prior(self) -> None:
        ledger = SpofLedger()
        before = ledger.priors["linear_healing"]
        ledger.bayesian_update("linear_healing", False)
        assert ledger.priors["linear_healing"] == pytest.approx(before * 0.1)

    def test_survived_assumption_unchanged(self) -> None:
        ledger = SpofLedger()
        ledger.bayesian_update("linear_healing", True)
        assert ledger.priors["linear_healing"] > 0.8

    def test_slashed_priors_do_not_survive(self) -> None:
        ledger = SpofLedger()
        ledger.bayesian_update("linear_healing", False)
        assert "linear_healing" not in ledger.get_surviving_priors()

    def test_rare_genotype_thins_average_patient_prior(self) -> None:
        common = SpofLedger(allele_frequency=0.42)  # *1/*1
        rare = SpofLedger(allele_frequency=0.005)  # ultra-rare genotype
        assert rare.priors["average_patient"] < common.priors["average_patient"]
