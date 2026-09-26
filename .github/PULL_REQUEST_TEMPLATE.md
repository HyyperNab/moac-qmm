## Description

<!-- Brief description of what this PR does -->

## SPOF Annihilated

<!-- Which Single Point of Failure does this eliminate? -->

- SPOF #: ___
- Description: ___

## Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New SPOF elimination (non-breaking)
- [ ] Breaking change (existing API changes — manifest update required)
- [ ] Documentation update
- [ ] Test improvement

## Checklist

- [ ] Tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Type check passes (`make type-check`)
- [ ] Manifest gate passes (`make manifest`) — or `manifest.py` updated deliberately
- [ ] SPOF register updated (`docs/spof_register.md`)
- [ ] Evidence register updated for any new/changed constants (`src/moac_qmm/evidence.py`)
- [ ] CHANGELOG.md updated
- [ ] No real patient data or secrets committed
