# Contributing to MOAC QMM

PRs that eliminate new Single Points of Failure are the lifeblood of this
project. Here is the contract.

## Medical & scientific rules (non-negotiable)

1. **No fabricated citations.** New or changed constants must carry an
   honest entry in `src/moac_qmm/evidence.py` (see
   [docs/EVIDENCE.md](docs/EVIDENCE.md)). The integrity test enforces this.
2. **Not a medical device.** Never weaken the disclaimer, never suggest
   clinical use, never accept dosing claims in docs or examples.
3. **No real patient data** in issues, PRs, tests or examples. Synthetic
   telemetry only.

## Development setup

```bash
git clone https://github.com/HyyperNab/moac-qmm.git
cd moac-qmm
pip install -e ".[dev]"
pre-commit install
```

## The gate ladder (all must pass)

```bash
make lint        # ruff check
make type-check  # mypy
make test        # pytest + coverage (91% floor — don't regress it)
make manifest    # frozen API surface gate
```

CI runs the same ladder on Python 3.10/3.11/3.12 × Linux/macOS/Windows.

## Engineering rules

1. **No print** in library code — `logging` only. Console rendering lives
   in the CLI.
2. **No global RNG** — inject `numpy.random.Generator`, accept a `seed`.
3. **No silent persistence** — filesystem writes only when explicitly
   configured.
4. **No pickle** — JSON for model/state persistence.
5. **No wildcard imports.**
6. **One version source** — `moac_qmm/_version.py`.
7. **Frozen manifest** — changing the public API requires updating
   `moac_qmm/manifest.py` and the CHANGELOG in the same PR.

## SPOF-driven workflow

1. Identify the failure mode (one SPOF per PR).
2. Write the failing test first.
3. Implement the elimination.
4. Document it in `docs/spof_register.md` with the next SPOF number.
5. Update `CHANGELOG.md`.

## Commit style

Conventional commits, imperative mood:

```
feat(models): add three-compartment PK solver (SPOF #53)
fix(engine): pass CYP2C9 genotype to warfarin check (D-07)
docs(spof): register SPOF #37 receptor kill-switch
```

## Testing a specific module

```bash
pytest tests/test_genomic.py -v
pytest -k "deterministic"
```
