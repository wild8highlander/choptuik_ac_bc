# IVP-11 — the audit report

**Committed verdict at v1.2.0 packaging: 11/11 PASS**
(at 1.0.0 the protocol was eight checks, all PASS; at 1.2.0 three
new hostile checks joined).

| IVP | check | verdict |
|:--|:--|:--|
| IVP01 | release integrity (verdicts exist, sha256 committed) | **PASS** |
| IVP02 | canonical job (fresh interpreter, exact match) | **PASS** |
| IVP03 | dependency audit (ast-scan vs declared) | **PASS** |
| IVP04 | 50-digit rederivation of closed forms | **PASS** |
| IVP05 | dimensions audit (SI gates) | **PASS** |
| IVP06 | symbolic layer (Gascheau + Lemma A, SymPy) | **PASS** |
| IVP07 | convergence orders (p_eff ladders) | **PASS** |
| IVP08 | seed determinism (bit-identical MC) | **PASS** |
| IVP09 | the phase-map gate (fresh cells + an own valley bisection) | **PASS** |
| IVP10 | the competing-model gates (doubled Floquet resolution M = 3840) | **PASS** |
| IVP11 | the vortex layer (SymPy charpoly dev 0 + 50-digit Aref zeros + the eigenvalue gate) | **PASS** |

## The v1.2.0 checks in detail

- **IVP09** re-derives the C9 no-closure statement from scratch: a
  fresh tranche of 50 map cells (every committed row) is recomputed
  and every cell must stay above the detector floor 2/N; the valley
  locus at the committed geometry is re-bisected by an independent
  ternary search (no campaign imports) and must match the committed
  beta* to 0.01 (measured dev: below 0.01).
- **IVP10** re-derives the C10 extremes at doubled Floquet resolution
  (M = 3840): the braking-only configuration must stay an exact zero,
  the septinial C sector must stay below 1e-4 of |B2| (the spectator
  statement), and the b-flip evenness must hold with machine zeros on
  A, B, C and ABC.
- **IVP11** is the vortex layer audit: the exact characteristic
  polynomial of the corotating linearization is derived symbolically
  in SymPy over Q(sqrt(3), pi) and must equal
  `lambda^2 (lambda^2 + omega^2)^2` identically (measured dev: 0);
  the Aref launch invariants vanish at 50 digits (mpmath, measured
  0.0); the numeric eigenvalue gate holds (max |Re| = 2.8e-17).

## What the audit fixes in the package's posture

- IVP02 recomputes `Delta_0`, `s` and the beta = 0.2 Floquet gap in a
  fresh interpreter and matches the committed verdict exactly — the
  committed C1 numbers are not stale.
- IVP03 forced an honest dependency declaration (pytest and sympy are
  declared dev dependencies; relative imports are not external).
- IVP05 caught a wrong SI expectation in the protocol itself during
  packaging (the Schwarzschild radius of the CMB contact is
  6.7e-5 m, not kilometres) — the gate was corrected, the package was
  right.  The audit corrects itself first.
- IVP06 proves symbolically that `1 - 27*nu < 0` for `nu = 1/3`
  (the Gascheau verdict) and that the worst-alignment flattening of a
  centred sampled parabola is exactly `kappa h^2/8`.

## Scope note

The audit verifies the PACKAGE against ITS OWN committed claims —
determinism, integrity, arithmetic, dimensions, convergence.  It does
not (and cannot) verify the physical hypothesis of the package; the
hypothesis remains marked as a hypothesis everywhere.
