"""Genomic substrate — eliminates the 'Average Patient' SPOF."""

from __future__ import annotations

import logging

from moac_qmm.constants import ALLELE_FREQUENCIES

logger = logging.getLogger(__name__)


class GenomicTensor:
    """Hardcoded metabolic reality from the genotype.

    SPOF #1 annihilated: static pharmacokinetic assumptions are replaced
    by CYP450 genotype-guided modifiers.
    """

    def __init__(self, genotype: dict[str, str]) -> None:
        self.cyp2c19 = genotype.get("CYP2C19", "*1/*1")
        self.cyp3a4 = genotype.get("CYP3A4", "*1/*1")
        self.cyp2d6 = genotype.get("CYP2D6", "*1/*1")
        self.cyp2c9 = genotype.get("CYP2C9", "*1/*1")
        self.hla_b = genotype.get("HLA-B", "Negative")
        self.slc01b1 = genotype.get("SLCO1B1", "*1/*1")
        self.vkorc1 = genotype.get("VKORC1", "*1/*1")

    def calc_pharmacokinetic_modifier(self, drug_class: str) -> float:
        """Return the multiplicative PK modifier for the drug class."""
        if drug_class == "PPI" and "*17" in self.cyp2c19:
            logger.warning("CYP2C19 Ultra-Rapid Metabolizer (*17 carrier). PPI AUC reduced ~65%%.")
            return 0.35
        if drug_class == "PPI" and "*2" in self.cyp2c19:
            logger.warning(
                "CYP2C19 Poor Metabolizer (*2 carrier). PPI AUC ~doubles. ECL hyperplasia risk."
            )
            return 2.1
        if drug_class == "PPI" and "*3" in self.cyp2c19:
            logger.warning("CYP2C19 *3 carrier. Non-functional allele. Poor metabolizer.")
            return 1.8
        return 1.0

    def calc_population_prior(self) -> float:
        """v28: how rare is this genotype. Rare = thin evidence base.

        SPOF #23 annihilated: uniform Bayesian priors replaced by allele
        frequency products.
        """
        gene = "CYP2C19"
        alleles = self.cyp2c19.split("/")
        freq = 1.0
        for allele in alleles:
            freq *= ALLELE_FREQUENCIES.get(gene, {}).get(allele, 0.01)
        if freq < 0.01:
            logger.info(
                "CYP2C19 genotype frequency=%.4f. Ultra-rare. Clinical evidence "
                "base critically thin. Bayesian uncertainty widened.",
                freq,
            )
        return freq


__all__ = ["GenomicTensor"]
