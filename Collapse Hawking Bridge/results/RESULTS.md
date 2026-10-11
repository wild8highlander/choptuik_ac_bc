# Results — the living ledger

The one-page ledger of everything the project measured, at **v2.2.0**
(the honest-verdict edition: verdict semantics fixed per the external
audit — anchor arithmetic is not a measurement). Machine-readable sources:
`campaigns/reference/*.json|csv`, `data/bridge/*.csv`. Update this file
whenever a campaign verdict changes — the ledger is prose, the verdicts
are law.

[![version](https://img.shields.io/badge/version-2.2.0-8C6D1F)](../CHANGELOG.md)
[![pytest](https://img.shields.io/badge/pytest-69_passed-brightgreen)](../tests/README.md)
[![prereg](https://img.shields.io/badge/PREREGISTRATION-frozen_v2.2.0-4A6B4A)](../PREREGISTRATION.md)
[![C6](https://img.shields.io/badge/C6-drift_law_T10-C9A84C)](scaling_drift/REPORT.md)
[![audit](https://img.shields.io/badge/IVP--15-remediated-8C6D1F)](../independent_verification/RESULTS.md)

---

## Headline numbers (v2.2.0)

| # | quantity | value | source |
|---|---|---|---|
| 1 | A* (N=800) — a **fixed-grid observable** | **0.0805332422** | a_star_ladder.json (F-1) |
| 2 | A* ladder, five grids | 0.1051042795 / 0.0882034349 / 0.0805332422 / 0.0777437258 / 0.0768211603 | a_star_ladder.{json,csv} |
| 3 | **ladder drift N800→N1600** (the stale `1.06e-6` agreement is retracted, F-1) | **2.79e-3** | c6_drift_verdict.json |
| 4 | drift effective orders `p_eff` (climbing) | **1.140 / 1.459 / 1.596** | c6_drift_verdict.json |
| 5 | Roberts-Oshiro convergence orders | **2.03 / 2.09** | c1_verdict.json |
| 6 | born-ensemble members f~ | **0.2877 / 0.2684 / 1.0** | collapse_verdict_summary.json |
| 7 | CMB contact mass `T_H = T_CMB` | **4.5016e22 kg** (~0.61 lunar) | chbridge.hawking |
| 8 | Page fraction `t_Page/t_evap` | **0.6464466** | exact, `1 - 2^{-3/2}` |
| 9 | Haar check, max \|S_formula − S_MC\| | **0.0042 bits** | page_haar_check.csv |
| 10 | septinial constant `b_Ch = 1−cos(2π/7)` | **0.37651019814126640** | exact |
| 11 | framework gap \|γ_Ch − b_Ch\|/b_Ch | **0.67%** | comparison, not a fit |
| 12 | `Δ·γ` anchor product | **1.28656** vs target 1.27 — **ANCHOR_ARITHMETIC**: consistency of the project's own anchors within the frozen tolerance (1.3%), NOT a measurement; engine level INCONCLUSIVE | C3 + PREREGISTRATION.md |
| 13 | subcritical compactness approach | **q_max: 0.0158 → 0.5845, monotone** | C2, c2_verdict.json |
| 14 | critical slowdown (subcritical branch) | **v_qmax = 0.510 − 0.0334 ln(ε)**, r²=0.71 | C2 |
| 15 | echo accumulation rate | **0.1909 peaks/e-fold** vs anchor 1/Δ = 0.2907 | C2 |
| 16 | born bifurcation half-width | **ε½ = 4.86e-3** (M_sat = 0.0352) | C2 |
| 17 | **floor law** `floor_M(N)` (per-grid F-2) | **≈ (13 ± 1)/N**: 0.0155 / 8.575e-3 / 4.245e-3 | C1+C3b |
| 18 | γ, Δ at every committed depth | honestly unmeasurable — per-grid `γ_eff = 0.041/0.060` (floor-dominated, r² 0.33/0.41); < 3 peaks up to N=3200; the 2.0.0 `~0.12` was an artifact, **retracted** | c3b_verdict.json |
| 19 | **T10 exact channel** (`κ*α²h²/(8s)`) | **κ\* = 2728.60, s = 413.8**; share 2.6e-3…9.1e-3 (sub-dominant; the rest is a labeled hypothesis) | c6_drift_verdict.json |
| 20 | continuum threshold `A*_inf` | **NOT claimable** (two-term extrapolation rejected by its own p_eff trajectory) | c6_drift_verdict.json |
| 21 | 50-digit constant layer | **7/7 PASS** | chbridge.validate |

Two properties of this table matter as much as the numbers: the honest
negatives (rows 18–20) are kept in the headline, not buried, and rows
10–11 are comparisons — the septinial coincidences are never presented
as derivations.

## Verdicts

All four engine verdicts carry `project_version 2.1.0` and fresh
timestamps from the v2.1.0 re-run; **the physics is byte-identical to
the 2.0.1 committed values** (verified field-by-field at packaging),
and the C6 drift verdict is deterministic over committed inputs.

- **C1** (engine validation, born spectrum): complete, committed,
  deterministic. 45 engine runs, ~48 s wall.
- **C2** (two branches): subcritical dispersal + born bifurcation,
  26 engine runs, ~24 s wall. Junk rows and flip-mechanism kept
  verbatim.
- **C3** (Δ·γ): anchor product classified **ANCHOR_ARITHMETIC** (v2.2.0
  reclassification of the former "anchor-level PASS" — both factors are
  anchors, so the comparison to 1.27 is arithmetic, not evidence);
  engine-level honest negative with full diagnostics committed, products
  reported INCONCLUSIVE, never silent. 31 engine runs, ~14 s wall.
- **C3b** (concentrated resolution): per-grid thresholds bisected
  fresh (F-2); the floor ladder is the first-class result; both
  engine-level negatives re-confirmed at N=1600/3200. 16 engine runs,
  ~334 s wall.
- **C6** (the resolution-drift law, theorem T10): deterministic
  analysis of the committed ladder + machine-verification of the two
  exact lemmas + channel calibration on committed artifacts. No engine
  march; ~2 s wall. Report: [scaling_drift/REPORT.md](scaling_drift/REPORT.md).

## Honesty register

1. Junk rows: present in verdicts, flagged, never dropped (C1 spectra,
   C2 bifurcation: 3 junk rows with raw overflowing masses).
2. Mass floor: carried as a first-class number — a measured floor LAW
   (`floor_M ≈ (13 ± 1)/N` on the per-grid F-2 values).
3. γ, Δ at fixed grid AND at concentrated deep grids: committed as
   nulls/per-grid floor-dominated values with reasons — the anchor
   0.374 is not reachable by this instrument in the reachable band.
4. Septinial coincidences: comparisons, zero derivation claims.
5. Photon-only evaporation: idealisation, documented in docs/methods.
6. C2's `v_qmax` is sampled at 40 engine snapshots per run; the
   quantization of the slowdown data is the instrument, stated openly.
7. No continuum threshold: the A* ladder drift is a theorem (T10);
   every `A*_N` is a fixed-grid observable.
8. The dominant drift channel (march-error amplification under
   near-critical lingering) is a labeled hypothesis — the exact
   parabolic-tension channel is measured and sub-dominant.
9. Verdict semantics (v2.2.0): the anchor product of Δ·γ is
   `ANCHOR_ARITHMETIC`, never a physics PASS; unmeasured products are
   `INCONCLUSIVE`, never silent; target/tolerance frozen by
   [PREREGISTRATION.md](../PREREGISTRATION.md) before the next engine
   run.

## Roadmap (post-2.1)

See [ROADMAP.md](ROADMAP.md) for the staged plan; the short list:

- C4: QNM ringdown of the born ensemble vs the septinial correction
  `ω → ω(1 − 1/(1200π²))`.
- C5: multi-family universality of f~(ε) (second pulse profile).
- Engine upgrade path: beat the floor law `(13 ± 1)/N` and the drift's
  dominant channel with true AMR near the accumulation point — the
  explicit target is an engine-level γ compatible with 0.374 and ≥ 3
  resolved echo peaks, judged against the criteria frozen in
  [PREREGISTRATION.md](../PREREGISTRATION.md).

## Краткое резюме (Russian)

Реестр результатов v2.2.0. Двадцать одна заголовочная строка; каждая
несёт адрес вердикта в `campaigns/reference/`. Новое в v2.2.0: строка 12
переклассифицирована (якорное произведение Δ·γ — ANCHOR_ARITHMETIC, не
измерение; движковый уровень INCONCLUSIVE); критерии опровержения
предрегистрированы в PREREGISTRATION.md до следующего прогона движка;
снят самоссылочный ярлык b_Ch_lit (пункт аудита №4). Все четыре
движковых вердикта повторно прогнаны на v2.2.0 — физика байт-идентична.
Регистр честности расширен до девяти пунктов.
