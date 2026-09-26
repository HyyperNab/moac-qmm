"""Constants ↔ evidence register integrity gate.

Ground Truth or Silence: every exported constant must carry an honest
provenance tier. None may claim verified status without a DOI.
"""

from __future__ import annotations

import moac_qmm.constants as constants
from moac_qmm.evidence import EVIDENCE_REGISTER, QUARANTINED, EvidenceTier


class TestEvidenceRegister:
    def test_every_exported_constant_is_registered(self) -> None:
        exported = set(constants.__all__)
        registered = set(EVIDENCE_REGISTER)
        assert exported == registered, (
            f"constants/evidence drift: missing={exported - registered} "
            f"extra={registered - exported}"
        )

    def test_no_constant_claims_verified_primary_without_doi(self) -> None:
        for name, (tier, note) in EVIDENCE_REGISTER.items():
            if tier is EvidenceTier.VERIFIED_PRIMARY:
                assert "doi" in note.lower(), f"{name} claims verified without a DOI"

    def test_quarantined_constants_are_registered(self) -> None:
        assert QUARANTINED.issubset(set(EVIDENCE_REGISTER))

    def test_allele_frequencies_sum_approximately_to_one(self) -> None:
        for gene, freqs in constants.ALLELE_FREQUENCIES.items():
            assert 0.9 <= sum(freqs.values()) <= 1.1, f"{gene} frequencies sum != 1"
