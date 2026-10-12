# dsilab/ — the reusable core of the seven experiments

Version 2.0.0 · standalone · numpy + stdlib only · no parent-repo imports

---

## What this package is

`dsilab` extracts the reusable mathematics of the seven experiments into
one importable, typed, tested package, so that the theorems have a single
canonical implementation instead of copies scattered across the
experiment scripts. Nothing here is fitted or invented: every constant is
an exact quantity of the b-C/a-C framework or a committed verdict
threshold, and every function is verified by the pytest suite.

## Modules

| module | contents | used by |
|--------|----------|---------|
| `constants.py` | c_K3 = 9/224, b_Ch, e-floor 5/7, verdict thresholds, seeds | everything |
| `leavitt.py` | the Kunz defect F, the G(P,Q) identity, Kunz-tree operators, weighted-tree and scaled-permutation formulas | exp1, exp7 |
| `census.py` | GL(3,2) = PSL(2,7) enumeration, the {7,3} census V/E/F, the genus-family discriminator c(g) | exp6 |
| `convergents.py` | continued fractions of the measured c_K3, convergents, the census filter | exp2 |
| `validate.py` | committed-verdict audit: re-derives every claim from `results/*.json` | `make validate`, CI |

## Quick start

```bash
python3 -m dsilab.validate          # audit the committed verdicts
python3 -m pytest tests/ -q         # the full theorem suite
```

```python
from dsilab import leavitt_F, kunz_tree_trimmed, census_identity
n, F = kunz_tree_trimmed(5)         # exact F = n + 2 (theorem B)
print(n, F)                          # 31 33.0
print(census_identity())             # {'V': 56, 'E': 84, 'F': 24, ...}
```

## The honest-status convention

The package keeps the monograph discipline: **proved** (exact rational or
integer arithmetic), **verified** (machine-precision numerical checks with
fixed seeds) and **refuted** (the sofic √ε-law, the repo's Hurwitz row)
are always distinguished. `validate.py` speaks only in terms of committed
JSON verdicts — if a fresh run disagrees with the committed numbers by
more than `RESULTS_RTOL = 1e-10`, that is a *finding*, not a nuisance.
