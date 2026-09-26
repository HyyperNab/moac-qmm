"""Genomic tensor unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.models import GenomicTensor


class TestGenomicTensor:
    def test_ppi_ultrarapid_metabolizer_modifier(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*17/*17"})
        assert tensor.calc_pharmacokinetic_modifier("PPI") == 0.35

    def test_ppi_poor_metabolizer_star2(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*1/*2"})
        assert tensor.calc_pharmacokinetic_modifier("PPI") == 2.1

    def test_ppi_poor_metabolizer_star3(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*3/*3"})
        assert tensor.calc_pharmacokinetic_modifier("PPI") == 1.8

    def test_normal_genotype_modifier_is_neutral(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*1/*1"})
        assert tensor.calc_pharmacokinetic_modifier("PPI") == 1.0
        assert tensor.calc_pharmacokinetic_modifier("Antibiotic") == 1.0

    def test_population_prior_star17(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*17/*17"})
        assert tensor.calc_population_prior() == pytest.approx(0.15 * 0.15)

    def test_population_prior_normal_genotype(self) -> None:
        tensor = GenomicTensor({"CYP2C19": "*1/*1"})
        assert tensor.calc_population_prior() == pytest.approx(0.65 * 0.65)

    def test_cyp2c9_field_exists_for_warfarin(self) -> None:
        # D-07 fix: dedicated CYP2C9 field
        tensor = GenomicTensor({"CYP2C9": "*1/*2"})
        assert tensor.cyp2c9 == "*1/*2"

    def test_defaults(self) -> None:
        tensor = GenomicTensor({})
        assert tensor.cyp2c19 == "*1/*1"
        assert tensor.hla_b == "Negative"
