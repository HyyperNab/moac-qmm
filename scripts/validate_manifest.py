#!/usr/bin/env python3
"""Frozen-API manifest gate.

Exits non-zero when the exported surface of any public module drifts from
`moac_qmm.manifest.FROZEN_API`. Run from the repo root:

    python scripts/validate_manifest.py
"""

from __future__ import annotations

import sys

from moac_qmm.manifest import validate


def main() -> int:
    violations = validate()
    if violations:
        print("API MANIFEST VIOLATIONS:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        print(
            "\nIf this change is deliberate, update src/moac_qmm/manifest.py "
            "in the same PR and document it in CHANGELOG.md.",
            file=sys.stderr,
        )
        return 1
    print("API manifest: frozen surface intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
