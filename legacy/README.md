# Legacy Reference — v28 Kernel

`moac_qmm_v28.py` is the original single-file kernel artifact
("MOAC QMM v28 — Strata-Oblivion Total Annihilation Kernel"), preserved
**verbatim** for provenance.

It is:

- **Not imported by the package** — it exists for reference only
- **Not linted or typed** — excluded from all quality gates
- **The source of truth for the physics** — every constant, threshold and
  formula in `src/moac_qmm/models/` is a faithful port from this file

Production differences from the artifact (all documented in
[docs/spof_register.md](../docs/spof_register.md)):

1. `print()` → `logging` (library-safe output)
2. Global `np.random` → injected, seeded `numpy.random.Generator`
3. The theatrical receptor kill-switch is opt-in (`strict_receptor_gate`)
4. No hardcoded `/var/moac/logs` ledger path
5. God-object `QMM_GodObjectV28` → decomposed 25-phase `QMMEngine`
6. Unvalidated dict telemetry → pydantic `PatientTelemetry`

The artifact runs standalone with numpy only:
`python legacy/moac_qmm_v28.py`
