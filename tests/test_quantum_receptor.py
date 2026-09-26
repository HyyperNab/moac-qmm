"""Quantum receptor unit tests."""

from __future__ import annotations

import numpy as np
import pytest

from moac_qmm.exceptions import QuantumReceptorFailure
from moac_qmm.models import QuantumDrugReceptor


@pytest.fixture
def receptor() -> QuantumDrugReceptor:
    return QuantumDrugReceptor(n_receptors=2000, n_simulations=500, rng=np.random.default_rng(7))


class TestQuantumDrugReceptor:
    def test_occupancy_within_bounds(self, receptor: QuantumDrugReceptor) -> None:
        result = receptor.calc_stochastic_occupancy(ligand_conc=0.04, kd=0.8)
        assert 0.0 <= result["mean_occupancy"] <= 1.0
        assert 0.0 <= result["p_therapeutic_effect"] <= 1.0

    def test_high_ligand_high_occupancy(self, receptor: QuantumDrugReceptor) -> None:
        result = receptor.calc_stochastic_occupancy(ligand_conc=1000.0, kd=0.8)
        assert result["mean_occupancy"] > 0.9

    def test_competitor_reduces_occupancy(self, receptor: QuantumDrugReceptor) -> None:
        alone = receptor.calc_stochastic_occupancy(ligand_conc=5.0, kd=1.0)
        competed = receptor.calc_stochastic_occupancy(ligand_conc=5.0, kd=1.0, competitor_conc=50.0)
        assert competed["mean_occupancy"] < alone["mean_occupancy"]

    def test_deterministic_with_same_seed(self) -> None:
        r1 = QuantumDrugReceptor(2000, 300, rng=np.random.default_rng(42))
        r2 = QuantumDrugReceptor(2000, 300, rng=np.random.default_rng(42))
        a = r1.calc_stochastic_occupancy(0.5, 0.8)
        b = r2.calc_stochastic_occupancy(0.5, 0.8)
        assert a["mean_occupancy"] == b["mean_occupancy"]

    def test_strict_gate_raises_when_insufficient(self) -> None:
        strict_receptor = QuantumDrugReceptor(2000, 300, rng=np.random.default_rng(1))
        with pytest.raises(QuantumReceptorFailure):
            strict_receptor.calc_stochastic_occupancy(ligand_conc=0.04, kd=0.8, strict=True)

    def test_lenient_gate_records_insufficiency(self, receptor: QuantumDrugReceptor) -> None:
        result = receptor.calc_stochastic_occupancy(ligand_conc=0.04, kd=0.8, strict=False)
        assert result.get("receptor_insufficient") == 1.0

    def test_ci_brackets_mean(self, receptor: QuantumDrugReceptor) -> None:
        result = receptor.calc_stochastic_occupancy(ligand_conc=5.0, kd=0.8)
        lo, hi = result["ci_95"]  # type: ignore[misc, index]
        assert lo <= result["mean_occupancy"] <= hi
