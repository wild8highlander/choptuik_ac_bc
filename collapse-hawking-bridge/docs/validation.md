# Validation ledger — v1.1.0

Every number below is committed in a machine-readable verdict
(`campaigns/reference/`, `data/bridge/`) and pinned by the pytest suite
(`tests/`).  This page is the human-readable summary; the verdicts are
the primary artifacts.

---

## 1. Engine validation (Roberts-Oshiro regression)

| grid N | max err r | err Phi (rel) | order (r) |
|-------:|----------:|--------------:|----------:|
| 200 | 4.686e-05 | 6.085e-04 | — |
| 400 | 1.146e-05 | 1.530e-04 | 2.031 |
| 800 | 2.687e-06 | 3.847e-05 | 2.093 |

Second-order convergence is clean; the constraint maxima at N=800 are
`c1 = 4.28e-4`, `c2 = 2.39e-7`, `mdef = 1.14e-6` (v2.0.1 monitor: the
C1 residual is reported per zone — march vs center — and in two forms,
pointwise and integral `c1_int = 7.2e-6`; on the Roberts family both
converge at 2nd order, while on the Gaussian family the discrete C1
bookkeeping is O(1) and is now honestly reported as such — the carried
field c never feeds the evolution slopes).  Source:
`campaigns/reference/c1_verdict.json:validation`.

## 2. Critical amplitude: the grid-honesty ladder

| grid N | A*_N | wall |
|-------:|-----:|-----:|
| 200 | 0.10510483 | 2.2 s |
| 400 | 0.08820114 | 5.6 s |
| 800 | **0.08053436** | ~46 s |
| remediated ladder, N=1600 (v2.0.1, F-1) | 0.07774373 | — |
| remediated ladder, N=3200 (v2.0.1, F-1) | 0.07682116 | — |

The threshold DRIFTS: `|A*_800 - A*_1600| = 2.79e-3` and it does not
stabilise at N=3200.  The stale 2.0.0 claim of a `1.06e-6` agreement
with `0.0805333` did not reproduce under blind bisection (audit IVP-09)
and is retracted.  The ladder itself (the drift across grids) is part
of the result: it *is* the fixed-grid floor made visible.
Sources: `c1_verdict.json:a_star_grid`, `a_star_ladder.json`.

## 3. Born spectrum and the ensemble

- 44 scan rows committed (26 at N=400 spanning ~3.2 decades in eps;
  18 at N=800 spanning ~2.5 decades).
- Saturated mass `M_code_sat = 0.0794`; mass floor at N=800
  `1.55e-2` (f~ = 0.2877).
- Junk rows: **kept and flagged** (4 examples with raw overflowing
  masses committed verbatim in the verdict's `honest_notes`).
- Ensemble members: `near_floor` f~ = 0.2877, `mid` f~ = 0.2684,
  `saturated` f~ = 1.0.

## 4. Thermodynamic consistency (mpmath, 50 digits)

| check | result |
|---|---|
| `b_Ch = 1 - cos(2pi/7) = 2 sin^2(pi/7)` | PASS (16 digits) |
| `b_Ch` vs `gamma_Ch = 0.374` | gap 0.66670% |
| `PAGE_FRACTION = 1 - 2^{-3/2}` | PASS |
| `S ~ M^2`, `T ~ 1/M`, `t ~ M^3` | PASS (rel 1e-9) |
| CMB contact round-trip `T_H(M_CMB) = T_CMB` | PASS, `M_CMB = 4.5016e22 kg` |
| Planck units cross-consistency | PASS (rel 1e-12) |
| `Delta*gamma` anchor = 1.28656 vs target 1.27 | dev 0.01656 (< tol 0.05) |
| Kretschmann scale law `K(M) M^4 = const` | PASS (rel 1e-9) |

Source: `python3 -m chbridge.validate`; enforced by
`tests/test_ladder.py::test_validate_all_pass`.

## 5. Page model

- Curve kink identity: at `t_Page`, `S_BH = S_rad = S0/2` from both
  branches (exact, `tests/test_page.py`).
- Haar check: 18 partitions, `N_total = 4..7`, seeded MC (3000/1200
  samples), **max deviation 0.0042 bits**.
  Source: `data/bridge/page_haar_check.csv`.

## 6. Campaign C3 — the Delta*gamma invariant

| product | value | verdict |
|---|---:|---|
| `P_anchor = Delta_lit * gamma_Ch` | **1.28656** | **PASS** (1.3% from 1.27, tol 0.05) |
| `P_mixed = Delta_eff * gamma_Ch` | — | not measurable (peaks < 3 per run) |
| `P_engine = Delta_eff * gamma_eff` | — | not measurable (grid floor) |

Engine-level honest negatives (all committed in
`campaigns/reference/c3_verdict.json`):

- scaling fit over 14 sane rows (N=800): `gamma_eff = 0.005 +- 0.035`,
  `r^2 = 0.003` — the spectrum is floor-flat across ~4 decades of eps;
- echo detector (log-time, `v*` proxied by `v_ah`): 2 peaks per run at
  `eps = 1e-3 / 3e-4 / 1e-4` — below the 3-peak minimum for an
  estimate.

**Standing conclusion at v1.1.0:** the invariant `Delta * gamma ~ 1.27`
is confirmed at anchor level and unconfirmed at engine level — and the
engine level was attacked twice (C3 at N=800, C3b at N=1600/3200); the
negatives survived both attacks.

## 7. Campaign C2 — the two branches around the threshold

Committed in `campaigns/reference/c2_verdict.json` (26 runs, ~24 s,
N=800, A = A*_800 +- eps):

| branch | check | result |
|---|---|---|
| S (subcritical) | compactness approach | `q_max` grows **monotonically** 0.0158 -> 0.5845 as eps -> 0; never crosses 1 |
| S (subcritical) | critical slowdown | `v_qmax = 0.510 - 0.0334 ln(eps)`, r² = 0.714 (n = 13) — measured logarithmic approach |
| S (subcritical) | echo accumulation | **0.1909 peaks/e-fold** (r² = 0.714) vs anchor `1/Delta = 0.2907` — same order, below it, honestly |
| X (supercritical) | born bifurcation | `M_sat = 0.03518979` (this scan), **eps_half = 4.8598e-3**, f~_min = 0.384 |
| X (supercritical) | junk discipline | 3 overflowing rows kept with `sane=false`, empty `f_tilde` |

The exponent fit is deliberately NOT repeated in C2 (C3 owns it); the
flip mechanism (a subcritical run forming an apparent horizon) is
implemented, flagged and kept verbatim — zero flips at the committed
range.

## 8. Campaign C3b — concentrated resolution

Committed in `campaigns/reference/c3b_verdict.json` (v2.0.1: 27 runs,
~346 s; each grid bisects its OWN threshold A*_N first — the F-2
remediation; "adaptive" means concentrated allocation of resolution,
no AMR rewrite — the definition is carried inside the verdict):

| check | result |
|---|---|
| **per-grid thresholds** | `A*_N1600 = 0.07774434`, `A*_N3200 = 0.07682177` (drift vs N800: `-2.79e-3` / `-3.71e-3`) |
| **floor ladder** | `0.0155 (N=800, C1) > 8.574765e-3 (N=1600) > 4.244867e-3 (N=3200)` |
| gamma ladder | `0.0410 +- 0.0262` (r²=0.33, N=1600) -> `0.0605 +- 0.0417` (r²=0.41, N=3200): floor-dominated, honestly weak fits — does NOT approach the anchor 0.374 |
| delta ladder | 1-2 peaks per run at both depths — `delta_eff` stays null |
| products | `P_anchor = 1.28656 -> PASS` (re-confirmed); `P_engine_deep = null` (honest negative kept) |

v2.0.1 correction: the 2.0.0 gamma ladder (`0.1113 -> 0.1205`, r² 0.82/
0.96) reused A*_N800 as the deep-grid base, mislabeling eps by +2.8e-3;
it was an artifact (audit finding F-2/IVP-11) and is retracted. With
per-grid thresholds C3b does not overturn C3 — it REINFORCES the
honest negative: the exponent stays floor-dominated far from gamma_Ch,
and the floor ladder remains the explicit target any engine upgrade
must beat.

## 9. Test suite inventory

| file | covers | tests |
|---|---|---:|
| `tests/test_constants.py` | exact identities, committed campaign values | 10 |
| `tests/test_hawking.py` | closed-form thermodynamics, CMB contact, kink | 9 |
| `tests/test_page.py` | Page curves, Haar formula + seeded MC | 7 |
| `tests/test_bridge.py` | spectrum, members, master table, determinism | 8 |
| `tests/test_ladder.py` | ladders, Kretschmann, 50-digit layer | 7 |
| `tests/test_engine.py` | Roberts regression at N=200, units | 2 |
| `tests/test_campaigns.py` | C2/C3b verdict pins, envelope, mirrors, tables | 17 |
| **total** | | **60** |

`python3 -m pytest tests/ -q` -> **60 passed** (v1.1.0);
`python3 -m pytest tests/ --co` is the authoritative count.

## 10. What is deliberately NOT validated

- No fit targets the anchors `gamma_Ch`, `b_Ch`, `Delta`; they appear
  only as comparisons (see `docs/theory.md` sections 4-5).
- Below the mass floor the spectrum is unknown and nothing is claimed.
- The asymptotic scaling regime (gamma = 0.374) is NOT validated at
  engine level: C2/C3/C3b jointly show the floor governs every
  reachable eps band up to N=3200.
- Greybody-corrected evaporation (species thresholds) is out of scope;
  committed lifetimes are photon-only idealisations.
