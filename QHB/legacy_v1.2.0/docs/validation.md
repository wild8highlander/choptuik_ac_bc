# Validation — every committed number with its address

Rule of the package (inherited from CHB): *machine-readable or it did
not happen*.  Each row below names the verdict file that carries the
number; the pytest suite pins all of them.

## 1. The 50-digit layer

`python3 -m qhb.validate` — **9/9 PASS** (mpmath dps=50):

| # | check | verdict |
|---|---|---|
| 1 | six correction quanta (T1 layer) | PASS (max rel dev 7.8e-17) |
| 2 | b_Ch identity + 0.67% gap (inherited) | PASS (0.6667%) |
| 3 | QCD contact M_QCD (T8) | PASS (T-chain dev < 1e-12) |
| 4 | CMB contact M_CMB (inherited) | PASS |
| 5 | Wu residual limits (T7) | PASS (all three limits) |
| 6 | Gascheau 1/27 vs 1/3 (T4) | PASS (growth sqrt(3/2)) |
| 7 | Planck units | PASS (max rel dev 3.9e-17) |
| 8 | T_QCD MeV->K chain | PASS |
| 9 | Page fraction identity (inherited) | PASS |

## 2. Campaign C1 — the gap law (T2/T3)

Source: `campaigns/reference/c1_verdict.json`.

| quantity | value |
|---|---|
| static gap `Delta_0` (N=64) | **0.523004556028** |
| response `s = dDelta/dq_pk` | **-1.00398294** |
| `B2` (quadratic law, window [0, 0.2]) | **-5.49670294e-2** |
| fit quality `r^2` | **0.99999982** |
| max residual on window | 4.7e-7 |
| `B2_A(pi/2)` | -5.05483488e-2 |
| `B2_B(pi/3)` | -4.40077100e-3 |
| `B2_C(pi/7)` | -2.71009207e-5 |
| cross-term share | 1.3e-4 (honest window) |
| T2 b-flip evenness dev | **0.0 (exact)** |
| T2 a-only all-order dev | **0.0 (exact)** |
| T2 a-flip residual (genuine ab-cross) | 1.5e-6 at beta=0.4 |
| b=0 identity dev | 0.0 |
| M-convergence p_eff | ~2 (second order) |

## 3. Campaign C2 — the trap (T4/T5/T6)

Source: `campaigns/reference/c2_verdict.json`.

| quantity | value |
|---|---|
| Gascheau `nu` (equal masses) | 1/3 > 1/27 — **UNSTABLE (exact)** |
| growth rate | sqrt(3/2) = 1.2247 |
| ensemble | 300 trials, band [-0.6, -0.05), 18187 draws rejected |
| **P_esc free (V0=0)** | **0.2433 ± 0.0248 — honest negative** |
| P_esc, every V0 >= 0.1 cell | < 1e-4 (all four Omegas) |
| Lyapunov free / trapped (medians) | 0.2615 / 0.2885 — **bound chaos** |
| survivor E-drift (V0=0) | 2.0e-5 |
| Kepler validation (e=0.5) | rel err 1.3e-9 |

## 4. Campaign C3 — the Wu door (T7)

Source: `campaigns/reference/c3_verdict.json`.

| quantity | value |
|---|---|
| max \|r_formula - r_MC\| (30 cells x 200k) | **3.3e-4** |
| r at the Wu anchor (0.9, x=100) | **0.899996** |
| x required to leave only eta = 6.1e-10 | ~1e9 (honest scope note) |

## 5. Campaign C4 — the floor law (T9)

Source: `campaigns/reference/c4_verdict.json`.

| quantity | value |
|---|---|
| reference gap (M=3840) | 0.5093674355 |
| T_sim = 20 | **UNRESOLVED** (beats 1.53 < 3) — honest negative |
| T_sim = 40..320 | resolved; errors 4.6e-3 → 3.2e-5 |
| resolution envelope | err <= 2/N — holds on all resolved rows |
| measured err exponent | 2.39 (interpolation noise below the envelope) |

## 6. Campaign C5 — the drift law (T10)

Source: `campaigns/reference/c5_verdict.json`.

| quantity | value |
|---|---|
| ladder Delta_N (N=32..512) | 0.521692 → 0.523453 (from BELOW) |
| p_eff | **1.948 / 1.974 / 1.987** (climbing to 2) |
| C_measured | +3.0089e-2 |
| C_exact = s*kappa/8 | **-6.275e-3 (opposing channel)** |
| exact-channel share | **-0.209** (honest, signed) |
| Lemma A machine check | dev 0.0 — PASS (even and odd N) |
| Delta_cont | **NOT claimed** (two-term fit, honest negative) |

## 7. The multilang twins

`multilang/` — JavaScript, C, C++ verified **14/14 PASS** each
(reference outputs committed; the 14th check is the vortex Lagrange
rate); Go, Rust, Julia carried as sources.

## 8. Campaign C9 — the phase map (v1.2.0)

Source: `campaigns/reference/c9_verdict.json`.

| quantity | value |
|---|---|
| map grid | 9 q_pk x 41 beta (beta in [0, 10], M = 1920) |
| phase of every cell | **OPEN** against the floor 2/N = 0.03125 |
| map minimum `Delta_F` | 0.124449 (q_pk = 1.0) — **no closure (finite range)** |
| valley at q_pk = 0.4 | beta* = 3.3583, `Delta_F,min` = 0.181777 |
| P2 refinement dev | 0.0002 < 0.05 — PASS |
| P3 N-stability shifts | 0.0006 / 0.0000 < 0.1 — PASS |
| counterexample `beta_c` | 2.9910 (naive forecast); measured 0.1978 = **6.3 x floor** |

## 9. Campaign C10 — the competing models (v1.2.0)

Source: `campaigns/reference/c10_verdict.json`.

| quantity | value |
|---|---|
| causal shares A / B / C | **91.95% / 8.00% / 0.049%** |
| B2 (ABC, zero-intercept estimator) | -5.49846380e-2 (agrees with C1 to 3.2e-4 rel) |
| braking-only B2 | **0.0 exactly** (all-order invisible) |
| b-flip evenness, all 7 transverse configs | **machine zeros** |
| max additivity cross-share | **1.3e-4 < 1%** — PASS |
| out-of-window error share (beta = 0.3 -> 0.8) | 0.3% -> 2.3% (monotone) |
| effective residual power | **4.07** (the quartic wing) |

## 10. Campaign C11 — the vortex anchor and the static barrier (v1.2.0)

Source: `campaigns/reference/c11_verdict.json`.

| quantity | value |
|---|---|
| T11 spectrum (exact Jacobian) | {0, 0, ±iω, ±iω}, ω = 3/(2π) |
| max \|Re\| on the imaginary pairs | **2.8e-17** |
| zero-pair magnitude (solver noise) | 4.7e-9 < 1e-6 |
| char-poly identity `λ²(λ²+ω²)²` | dev **1.75e-16** (machine); **0** (SymPy, IVP11) |
| rotation: ω dev / rigidity / inv drift | 1.6e-14 / 1.5e-14 / 2.1e-14 |
| Aref launch invariants (50 digits) | **0.0** (all four) |
| Aref drift / r_max (t = 12) | 1.5e-12 / **2.7654 << 12** |
| static barrier V* | **0.9359375** (exact formula) |
| static cells (Ω=0): P_esc | **0/300** at V0 = 0.4, 0.8, 1.6 |
| bound margins / E drift (abs) | ≥ 2.76 / ≤ 7.6e-5 |
| oscillating wall work (0.8, 2) | median \|dE\| = **0.146** (> 0) |

## 11. The Evidence Engine registry

`results/claims_registry.json` + `qhb/claims.py` — **27 claims**, five
statuses (exact / measured-law / honest-negative / hypothesis /
comparison), each with a five-field uncertainty budget and a
pre-committed falsification criterion.  Validated by
`tests/test_vortex_claims.py` (a broken registry breaks the build).

## 12. Determinism

All campaigns are seeded (`20261010`) or RNG-free; re-running a
campaign reproduces its verdict bit-for-bit (except wall times).  The
derived tables in `data/qhb/` rebuild byte-deterministically from the
committed verdicts (`scripts/rebuild_data.py`, pinned by a test).
