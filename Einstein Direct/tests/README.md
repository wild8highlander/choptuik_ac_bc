# tests/ — the Verification Suite

This folder contains the pytest suite that re-checks the major machine
theorems of the parent folder from the committed JSON results. It is the
executable form of the project discipline: **a claim is only kept if a test
can re-verify it**.

## How to run

```bash
python3 -m pytest tests/ -q
# 21 passed
```

The suite is fast (a few seconds): it loads the JSONs from `../results/` and
re-checks theorems on them; the heavy machines themselves are NOT re-run here.

## What is covered (21 tests)

- **Solver validation**: exact Roberts–Oshiro regression; flat-space
  stability; supercritical forms horizon nucleation.
- **Symbolic layer**: derivation residuals; the clock-pair theorem (unique
  common root of the clock books, exact GCD factorization); third-order
  weight rule; the dd-prolongation closure; the exact spectrum at the
  critical scale; the b-C / a-C / a-B correction embedding.
- **Static structure**: the nonlinear DAE march verdict (the flat line is the
  only solution manifold through the critical point); the compensated book of
  the figure cycle lying in `S = {F = 0, r = 0}` on all booked scales; the
  degenerate corner rejection; the exit-rate verdict (every landed point with
  `|V| > 1e-3` leaves the static set).
- **Brick ladder and census**: the clock-pair theorem exact on every brick of
  the ladder; the tick obstruction non-monotone (no power law); the global
  static census finding no new branches; the relative anchor
  (one-brick < baseline) surviving on the invariant norm.

## Conventions

- Every test docstring states the machine theorem it re-verifies and the
  tolerance; tolerances are copied from the machine outputs, not tightened.
- If a test fails, the JSONs and the code must be re-generated together —
  hand-editing a JSON to make a test pass is forbidden by the honesty policy.
