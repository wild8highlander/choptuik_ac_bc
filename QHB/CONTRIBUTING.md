# Contributing to Quark-Hawking Bridge

Thank you for considering a contribution to a falsification-first research
artifact. The rules below keep the release *iron*: every number in prose has a
machine layer, and every claim has a falsifier.

## Ground rules

1. **Falsifier first.** Any new claim (C/T/P/X series) must ship with a
   one-line falsifier recorded in the same JSON layer as the numbers.
2. **Machine layer is the source of truth.** Prose (README, RESULTS, monograph)
   is generated from or cross-checked against `data/` and `monolith/**`. Update
   JSON and prose in the same PR.
3. **Pinned seeds.** Monte Carlo additions must use the pinned seed family
   (777xxx) and report σ-budgets.
4. **Statuses are sacred.** `exact` / `measured` / `honneg` upgrades require a
   closed kernel or an exact symbolic derivation, not a nicer plot.

## Local Iron-QA (all must pass)

```bash
python tools/check_json.py       # every JSON parses
python tools/check_numbers.py    # master numbers vs machine layers
python tools/check_release.py    # VERSION/CHANGELOG/README/checksums/links
python tools/check_lean_kernels.py
pytest tests/test_constants.py tests/test_artifacts.py -q
```

## Lean / Mathlib

The formalization lives in `monolith/lean/`. Build:

```bash
cd monolith/lean
lake update
lake exe cache get!
lake build
lake env lean QHB_AxiomAudit.lean   # axiom audit must stay sorry-free
```

## Pull requests

Use the PR template. CI runs Python canon checks, consistency checks, and the
Lean/Mathlib verification. A PR that upgrades a status without a closed kernel
will be rejected regardless of how good the prose looks.
