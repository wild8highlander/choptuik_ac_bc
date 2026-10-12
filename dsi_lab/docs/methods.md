# Methods — how the DSI laboratory verifies

## Determinism

Every experiment is seeded (`RNG_SEED = 42`, a single
`numpy.random.default_rng` per module) and uses only deterministic
linear algebra: QR, SVD, explicit group enumeration, L-BFGS with fixed
restart schedules. There is no wall-clock branching, no parallelism, no
network access. A fresh run must reproduce the committed
`results/*.json` to the relative tolerance `RESULTS_RTOL = 1e-10`;
anything larger is treated as a **verification finding**, not noise —
that is the package's contract with itself.

## What is recomputed, what is audited

The package separates three activity types:

1. **Recompute** — the experiments rebuild their numbers from scratch
   (`python3 run_all.py`) and overwrite `results/*.json`; the
   `git diff` afterwards is the determinism check.
2. **Audit** — `python3 -m dsilab.validate` reads the committed JSONs
   and re-derives every verdict (13 checks: the trace-theorem gap, the
   tree identity, DSI-4 deviation, finding D1, finding E1, the census,
   theorems A/B/C). It never recomputes — it checks that the *committed*
   numbers say what the README says they say.
3. **Cross-language self-test** — `multilang/` recomputes a ten-number
   exact core in C, C++, JavaScript (byte-identical, verified) and
   Rust/Go/Julia (sources), so the theorem block can be checked without
   Python at all.

## Tolerances and what they mean

| constant | value | meaning |
|----------|-------|---------|
| `RESULTS_RTOL` | 1e-10 | reproduction tolerance of committed JSONs |
| `TRACE_GAP_MAX` | 6.0e-8 | ceiling for the sharp-trace-theorem gap (committed max 5.920e-8; README prose rounds to 5.9e-8) |
| `IDENTITY_ERR_A_MAX` | 5.9e-16 | the F = 3n − 2p − 2q + 3r identity error (machine epsilon scale) |
| `THEOREM_B_ABS_TOL`, `THEOREM_C_ABS_TOL` | 1e-9 | exactness of F = n + 2·rank and F = 2n |

## The honest-status discipline

The package practices the same honesty policy as the monographs:

- **proved** — exact rational/integer arithmetic (the census, the ladder,
  the convergent identities, the weighted-tree formula);
- **verified** — machine-precision checks with fixed seeds (theorems
  A/B/C at 5.9e-16, the trace-theorem floor at 5.9e-8);
- **refuted** — statements the data kills, kept publicly (the sofic
  √ε-law, the repo's Hurwitz row);
- **hypothesis** — everything the package assumes structurally, always
  labeled: the b₂ pattern on higher Hurwitz surfaces, V_T as the
  T-violation model, DSI-4 as an observation rather than a derivation.

Findings D1 and E1 are corrections *produced by* the package and are
kept in the committed verdicts as first-class results.

## Reproduction recipes

```bash
cd dsi_lab
python3 -m pip install -r requirements.txt

make test          # 51+ fast theorem checks (~2 min)
make validate      # audit the committed verdicts (seconds)
make run           # all 7 experiments, deterministic (~5-15 min)
make quick         # experiments 2, 6, 7 (fastest)
make verify        # test + validate + run, logged to logs/
make figures       # regenerate the summary figure
make logo          # regenerate logo + avatars
make animations    # regenerate the 8 animations (en+ru)
make monograph     # rebuild the EN/RU monograph PDFs (tectonic)
make multilang     # build & run the C/C++/JS twins, diff outputs
make clean
```

After `make run`, `git diff --stat results/` must be empty for the
committed seeds — if it is not, the difference is the finding, and the
package asks you to report it rather than to re-seed around it.

## Android/Termux

Everything above works identically on Termux (`pkg install make python
numpy`); the Makefile targets were chosen to be Termux-friendly, and the
multilang twins need nothing beyond a C compiler (`pkg install clang`).
