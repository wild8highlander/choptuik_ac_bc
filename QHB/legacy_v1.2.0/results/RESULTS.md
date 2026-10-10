# Results — the living ledger

The one-page register of everything the Quark-Hawking Bridge measured,
at **v1.2.0**.  Machine-readable sources: `campaigns/reference/*.json`,
`data/qhb/*`.  Update this file whenever a verdict changes — the ledger
is prose, the verdicts are law.

[![version](https://img.shields.io/badge/version-1.2.0-8C6D1F)](../CHANGELOG.md)
[![pytest](https://img.shields.io/badge/pytest-94_passed-brightgreen)](../tests/README.md)
[![validate](https://img.shields.io/badge/mpmath-9%2F9_PASS-blue)](#the-50-digit-layer)
[![audit](https://img.shields.io/badge/IVP--11-11%2F11_PASS-8C6D1F)](../independent_verification/RESULTS.md)
[![claims](https://img.shields.io/badge/claims_registry-27_validated-1A1A1A)](CLAIMS.md)

---

## Headline numbers (v1.2.0)

| # | quantity | value | source |
|---|---|---|---|
| 1 | static gap `Delta_0` (N=64, committed geometry) | **0.523004556028** | c1_verdict.json |
| 2 | response `s = dDelta/dq_pk` | **-1.00398294** (sign real, carried) | c1_verdict.json |
| 3 | **gap law** `Delta_F = Delta_0 + B2 beta^2` | **B2 = -5.49670294e-2, r^2 = 0.99999982** (window [0, 0.2]) | c1_verdict.json |
| 4 | per-sector hierarchy `|B2_A| : |B2_B| : |B2_C|` | **-5.05e-2 / -4.40e-3 / -2.71e-5** (~1865 : 1) | c1_verdict.json |
| 5 | T2 b-flip evenness / a-only all-order | **0.0 / ~1e-15** (exact machine zeros) | c1_verdict.json |
| 6 | T2 a-flip residual (genuine ab-cross) | 1.5e-6 at beta=0.4 (data) | c1_verdict.json |
| 7 | Gascheau (equal masses) | **nu = 1/3 > 1/27 — UNSTABLE (exact)** | c2_verdict.json |
| 8 | **P_esc free trio (V0=0)** | **0.2433 ± 0.0248 — honest negative** | c2_verdict.json |
| 9 | P_esc, all V0 >= 0.4 cells, all Omegas | **< 1e-4 — the wall seals** | c2_verdict.json |
| 10 | Lyapunov free / trapped (medians) | **0.2615 / 0.2885 — bound chaos** | c2_verdict.json |
| 11 | Wu closed form vs MC (30 cells x 200k) | **max dev 2.5e-3** | c3_verdict.json |
| 12 | r at the Wu anchor (alpha=0.9, x=100) | **0.899996** — the door opens | c3_verdict.json |
| 13 | x required to leave only eta | **1.36e-9** (honest scope) | c3_verdict.json |
| 14 | QCD contact `M_QCD` (T_H = 155.16 MeV) | **6.8140e10 kg** (0.68 x 1e11 lit. comp.) | qhb.bridge (T8) |
| 15 | CMB contact (inherited) | 4.5016e22 kg | qhb.bridge |
| 16 | floor law: unresolved tail | **T_sim = 20: beats 1.53 < 3 — honest negative** | c4_verdict.json |
| 17 | floor envelope | **err <= 2/N holds on all resolved rows** | c4_verdict.json |
| 18 | **drift law** `Delta_cont - Delta_N = C h^2` | **C = +3.0089e-2, p_eff 1.948→1.974→1.987** | c5_verdict.json |
| 19 | exact channel `s*kappa/8` | **-6.275e-3, share -0.209 (opposing, signed)** | c5_verdict.json |
| 20 | Lemma A machine check | **dev 0.0** (even and odd N) | c5_verdict.json |
| 21 | `Delta_cont` | **NOT claimed** (two-term fit, honest negative) | c5_verdict.json |
| 22 | 50-digit constant layer | **9/9 PASS** | qhb.validate |
| 23 | twins JS/C/C++ | **13/13 each** | multilang/ |
| 24 | engine Kepler anchor (e=0.5) | rel err **1.3e-9** | tests |
| 25 | **C6: the mapped gap quantum at the QCD contact** | **E_gap = 81.1 MeV** (comparison only) | c6_verdict.json |
| 26 | C6: order window `Lambda/E_gap(QCD)` | **4.09** (same decade — NOT a derivation) | c6_verdict.json |
| 27 | C6: the three-branch round trip `T_H(M) = T` | max rel dev **1.4e-16** | c6_verdict.json |
| 28 | **C7: the sigma-extension regression gate** | **dev 0.0 exactly** (C2 anchor re-verified) | c7_verdict.json |
| 29 | **C7: the flux tube seals** | P_esc **0.2433 → 0.06 (sigma=0.02) → 0.0033 (0.05)**, monotone | c7_verdict.json |
| 30 | **C7: the wall boundary V0\* shrinks** | **x7.1 (Omega=0) / x7.6 (Omega=2)** as sigma: 0→0.02 | c7_verdict.json |
| 31 | C7: bound chaos WITHOUT the wall | median Lyapunov **0.264**, 100% positive | c7_verdict.json |
| 32 | **C8: the exact no-door check** | r(alpha=0) = **0.0** (bitwise) | c8_verdict.json |
| 33 | C8: RK4 convergence | **p_eff = 3.987** (pinned to 4) | c8_verdict.json |
| 34 | C8: 50-digit mpmath cross-check | dev **3.9e-16** | c8_verdict.json |
| 35 | **C8: the pairwise door** | **0.988 at lambda=100 (alpha=0.9)** — the linear limit 0.9 is LEFT (shape moves) | c8_verdict.json |
| 36 | C8: T7 closed form extends? | **NO — exact structural negative** | c8_verdict.json |
| 37 | **C9: no closure on the whole searched map** | every cell OPEN; map min **0.124449** > floor 2/N (finite-range statement) | c9_verdict.json |
| 38 | **C9: the narrowing valley** | beta* = **3.3583**, Delta_F,min = **0.181777** at the committed geometry; REOPENS | c9_verdict.json |
| 39 | C9: valley reproducibility | refinement dev **0.0002 < 0.05**; N-shifts **< 0.001** | c9_verdict.json |
| 40 | **C9: the naive-window counterexample** | forecast closure at beta_c = 2.9910 — **FALSIFIED**: measured 0.1978 = 6.3 × floor | c9_verdict.json |
| 41 | **C10: the causal map of the drive** | **A 91.95% / B 8.00% / C 0.049%** — additive (max cross 1.3e-4) | c10_verdict.json |
| 42 | C10: braking-only drive | B2 = **0.0 exactly** (all-order invisible) | c10_verdict.json |
| 43 | **C10: out-of-window forecast failure** | err share 0.3% → 2.3% (beta 0.3→0.8); residual power **4.07** (the quartic wing) | c10_verdict.json |
| 44 | **T11: the stability contrast (exact)** | vortex triangle spectrum **{0, 0, ±iω, ±iω}**, max \|Re\| = 2.8e-17; charpoly dev **0** (SymPy) | c11_verdict.json |
| 45 | T11: the rigid rotation (measured) | rigidity **1.5e-14**, ω dev **1.6e-14**, inv drift 2.1e-14 | c11_verdict.json |
| 46 | **T12: the invariant wall (measured)** | Aref manifold I=H=P=Q=0 (50-digit zeros); r_max **2.7654 << 12** — **bound WITHOUT any wall** | c11_verdict.json |
| 47 | **T13: the static barrier (exact)** | **V* = 0.9359375**: escape impossible at V0 ≥ 1.6, Ω=0; measured 0/300, margins ≥ 2.76 | c11_verdict.json |
| 48 | T13: the oscillating complement | median \|dE\| = **0.146** — the wall pumps energy; the C2/C7 seal is finite-time | c11_verdict.json |
| 49 | the Evidence Engine registry | **27 claims, 5 statuses, validated** | claims_registry.json |
| 50 | the independent audit | **IVP-11: 11/11 PASS** | IVP results |

Three properties matter as much as the numbers: the honest negatives
(rows 6, 8, 9, 13, 16, 19, 21, 36 and the CLM-27 hypothesis) stand in
the headline, not the basement; the signed quantities carry their
signs; and the confinement mechanism itself is a marked hypothesis —
the theorems are facts about the committed toy models.

## The v1.1.0 campaigns (C6–C8, the roadmap block)

**C6 — the physical mapping (three branches).** The marked scale
hypothesis now compares THREE contact anchors, each with its own
honesty tag: `Lambda_QCD = 332 MeV` (a renormalisation scale — the
weakest claim), `T_QCD = 155.16 MeV` (the only true temperature — the
committed T8 contact) and `v_EW = 246.22 GeV` (a VEV, not a bath
temperature — the least honest branch).  The mapped gap quantum at the
QCD contact is E_gap = 81.1 MeV; it sits within one decade of
Lambda_QCD (ratio 4.09) — an explicitly non-derivational comparison.

**C7 — the anharmonic trio.** The engine gained a Cornell-like
confining core `U_conf = sigma * r_soft`, backward compatible: the
sigma = 0 regression gate reproduces the committed C2 free-trio escape
count with dev **0.0 exactly**.  Three committed laws: the flux tube
closes the finite-time escape channel (monotone, sigma\* = 0.05); the
sealing boundary `V0*` SHRINKS by x7.1–x7.6 as sigma goes 0 → 0.02
(the core replaces the wall); bound chaos survives without any wall
(median 0.264, 100% of trials positive).

**C8 — the pairwise Wu door.** The linear mean field is replaced by
pairwise annihilation with the trigger asymmetry.  The T7 closed form
does NOT extend (an exact structural negative — the model has no
closed form).  In its place: the exact no-door check (alpha = 0 gives
r = 0.0 bitwise), the monotone-imbalance identity, the RK4 ladder
(p_eff = 3.987) and a 50-digit mpmath cross-check (dev 3.9e-16).
The door STAYS and the SHAPE MOVES: r_pair climbs to 0.988 at
lambda = 100 (alpha = 0.9) — the linear alpha-limit is left behind:
the pairwise toy accumulates the FULL imbalance.

## The v1.2.0 campaigns (C9–C11, the evidence block)

**C9 — the gap phase map.**  The window law T3 is mapped over the
whole searched `(beta, q_pk)` plane: every cell OPEN against the
committed detector floor 2/N, the gap narrowing to a reproducible
VALLEY (beta* = 3.3583 at the committed geometry) and REOPENING —
quasi-energy band structure — and a machine-found counterexample to
the naive quadratic extrapolation (forecast closure at beta_c = 2.9910
falsified by a factor 6.3 above the floor).  A finite-range statement,
carried honestly.

**C10 — the competing models.**  A factorial ablation of the three
septinial sectors: the causal map A 91.95% / B 8.00% / C 0.049% with
additivity to 1.3e-4, the exact invisibility of the braking-only
drive, and the quantified out-of-window failure of the quadratic
forecast (the quartic wing, residual power 4.07).  The septinial C
sector is structurally present and causally a spectator in magnitude —
carried, not hidden.

**C11 — the vortex anchor and the static barrier.**  The classical
three-vortex layer (Kirchhoff 1876; Aref 1979), implemented from the
classical equations with the package's own code paths: T11 — the same
equilateral triangle that is Gascheau-unstable under 1/r attraction is
a NEUTRALLY stable relative equilibrium of the Kirchhoff problem
(spectrum {0, 0, ±iω, ±iω}, the characteristic polynomial
`lambda^2 (lambda^2+omega^2)^2` proven symbolically, dev 0); T12 — on
the classical Aref manifold (all four invariants vanish at 50 digits)
the trio stays bound WITHOUT ANY WALL (r_max 2.7654 << 12); T13 — with
the wall frozen (Omega = 0) escape is EXACTLY impossible for V0 ≥ 1.6
(the bound V* = 0.9359375, a theorem about the committed softened
engine), while at Omega > 0 the wall pumps energy (median |dE| = 0.146)
and the C2/C7 sealing stays a finite-time statement.  The first EXACT
confinement statement of the package.

## Verdicts

- **C1** (gap law): complete, committed, deterministic (~1 s).
- **C2** (trap): 36 cells x 300 trials, committed (~3.5 min).
- **C3** (Wu door): 30 cells x 200k, committed (~1 s).
- **C4** (floor): period-sampled Floquet spectroscopy, committed (~1 s).
- **C5** (drift): exact eigensolver ladder, committed (~1 s).
- **C6** (mapping): closed-form three-branch comparison, committed (~1 s).
- **C7** (anharmonic): 44 cells x 300 trials + Benettin, committed (~5 min).
- **C8** (pairwise door): deterministic ODE grid + mpmath, committed (~10 s).
- **C9** (phase map): 9x41 grid + valley bisections + gates, committed (~11 s).
- **C10** (competing models): 8-config ablation + forecast gates, committed (~4 s).
- **C11** (vortex anchor): Kirchhoff RK4 + exact Jacobian + engine barrier cells, committed (~35 s).

All eleven verdicts are committed; C1–C8 carry `project_version 1.1.0`
(their numbers are unchanged and re-verified by the audit and the C7
regression gate), C9–C11 carry `project_version 1.2.0`; re-running any
campaign reproduces its verdict bit-for-bit (except wall times).

## The 50-digit layer

`python3 -m qhb.validate` — 9/9 PASS: the six correction quanta, the
inherited b_Ch comparison, both contact points, the Wu limits, the
Gascheau criterion, the Planck units, the T_QCD chain and the Page
fraction.

## The audit

IVP-11 — 11/11 PASS (see `independent_verification/RESULTS.md`): the
original eight checks plus IVP09 (the phase-map gate with a fresh
bisection), IVP10 (the competing-model gates at doubled Floquet
resolution) and IVP11 (the vortex layer: the SymPy characteristic
polynomial dev 0, the 50-digit Aref zeros, the eigenvalue gate).
