"""Frozen API manifest gate — the interface freeze between generations."""

from __future__ import annotations

from moac_qmm.manifest import validate


class TestManifest:
    def test_public_api_matches_frozen_manifest(self) -> None:
        violations = validate()
        assert not violations, f"API surface drifted: {violations}"

    def test_manifest_covers_all_public_packages(self) -> None:
        from moac_qmm.manifest import FROZEN_API

        assert "moac_qmm" in FROZEN_API
        assert "moac_qmm.models" in FROZEN_API
        assert "moac_qmm.deep_learning" in FROZEN_API
        assert "moac_qmm.constants" in FROZEN_API
        assert "moac_qmm.exceptions" in FROZEN_API
        assert "moac_qmm.evidence" in FROZEN_API
