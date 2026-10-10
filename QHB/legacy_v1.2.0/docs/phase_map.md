# The gap phase map (theorem-support document for C9, v1.2.0)

The gap law T3 (`Delta_F = Delta_0 + B2 beta^2`, window [0, 0.2]) is a
WINDOW law.  Campaign C9 maps the whole searched drive range and turns
the honest scope note into measured structure.  This document states
the committed definitions, the phase classification, the valley law and
the counterexample, in the same style as `gap_law.md`.

---

## 1. The map and its regime bound

The committed two-band reduction is valid while the static splitting
does not reach the Floquet band edge:

```
Delta_0(q_pk) <= Omega_0 / 2 = 1     (the regime bound)
```

With the committed geometry family this means `q_pk >= 0.2`
(`Delta_0(0.2) = 0.9548 < 1`; the shallow-well branch `q_pk < 0.2`
would leave the two-band regime and is honestly EXCLUDED, not mapped).
The committed map is the grid

```
q_pk in {0.2, 0.3, ..., 1.0}   (9 rows)
beta in [0, 10], step 0.25      (41 columns, M = 1920 Floquet steps)
```

Each cell carries the committed detector floor of C4, `2/N = 0.03125`
(N = 64): a gap below it exists but the committed spectroscopy cannot
separate it.

## 2. The phase classification

| class | definition |
|---|---|
| OPEN | `Delta_F >= 2/N` (resolvable by the committed detector) |
| SUBFLOOR | `0 < Delta_F < 2/N` (exists, below the envelope) |
| DEGENERATE | `Delta_F < 1e-10` (machine-zero quasi-energy splitting) |

**Committed result: every one of the 369 cells is OPEN.**  The gap
never closes on the searched range — a FINITE-RANGE statement (the
verdict carries the beta_max = 10 boundary; no claim of eternal
openness is made anywhere in the package).

## 3. The narrowing valley (the measured phase feature)

For every row the gap reaches a minimum and REOPENS — the quasi-energy
band structure of the driven two-level system that the window law
cannot see:

| q_pk | beta*(valley) | Delta_F,min | vs floor |
|---|---|---|---|
| 0.2 | 8.7340 | 0.298595 | 9.6 x |
| 0.3 | 3.4077 | 0.221090 | 7.1 x |
| 0.4 (committed) | **3.3583** | **0.181777** | 5.8 x |
| 0.6 | 3.2904 | 0.145315 | 4.7 x |
| 1.0 | 3.2362 | 0.124432 | 4.0 x |

Reproducibility gates (both PASS): the 2x-refined grid (M = 3840)
reproduces every committed valley locus to 0.0002 < 0.05; the N-ladder
(32/64/128) moves the committed-geometry locus by < 0.001 < 0.1 per
doubling (the discretization budget of the map itself).

## 4. The naive-window counterexample (machine-found)

The committed window coefficients (C1, no refit) extrapolated beyond
the window forecast closure — `Delta_F` falling under the detector
floor — at

```
beta_c = sqrt((Delta_0 - 2/N) / |B2|) = 2.9910   (q_pk = 0.4)
```

The measured map at that point: `Delta_F(2.9910) = 0.197764` —
**6.3 x the floor**.  The forecast is FALSIFIED inside the searched
range, and the valley (section 3) never comes within 5.8x of the floor
either.  What is falsified is the EXTRAPOLATION, never T3 itself: T3
is a window law and its window scope marker is exactly what C9 turns
into measured structure.

## 5. Verdict addresses

| object | address |
|---|---|
| the map, the classification, the gates | `campaigns/reference/c9_verdict.json` |
| the valley table | `data/qhb/phase_valley.csv` |
| the counterexample block | `data/qhb/phase_counterexample.json` |
| the independent re-derivation | `independent_verification/results/IVP09.json` |
| the build pins | `tests/test_campaigns_v12.py::TestC9PhaseMap` |
| the claims | `results/claims_registry.json` CLM-17/18/19 |

## 6. Honest notes

1. No closure is finite-range; the map's beta_max = 10 is part of the
   committed statement.
2. The floor 2/N is the DETECTOR envelope (C4): SUBFLOOR cells would
   be cells where a real spectroscopy campaign at this resolution
   could not separate the gap — the classification couples the physics
   to its measurement honestly.
3. The regime bound Delta_0 <= Omega_0/2 is a property of the
   committed two-band reduction, not of the chain: the shallow-well
   branch is excluded from the MAP, not from physics.
