# campaigns — measurements, not simulations

![v2.1.0](https://img.shields.io/badge/version-2.1.0-8C6D1F) ![C1](https://img.shields.io/badge/C1-45_runs%20%2F%2048_s-blue) ![C2](https://img.shields.io/badge/C2-26_runs%20%2F%2024_s-blue) ![C3](https://img.shields.io/badge/C3-31_runs%20%2F%2014_s-blue) ![C3b](https://img.shields.io/badge/C3b-16_runs%20%2F%20334_s-blue) ![C6](https://img.shields.io/badge/C6-drift_law_T10-C9A84C) ![invariant](https://img.shields.io/badge/Δ·γ_anchor-1.28656_PASS-brightgreen)

**TL;DR**

- A campaign here is a *measurement protocol*: a script that drives the
  engine through a fixed ladder of runs and commits a self-describing
  JSON verdict. Console output is a courtesy; the verdict is the law.
- **C1** — engine validation, the A* grid-honesty ladder, born-spectrum
  scans, evolution profiles (45 runs, ~48 s).
- **C2** — the two branches around the threshold: subcritical dispersal
  (compactness approach, critical slowdown, echo counter) and the
  supercritical born bifurcation `f~(eps)` with `eps_half` (26 runs,
  ~24 s).
- **C3** — the Delta*gamma ~ 1.27 invariant: anchor-level **PASS**
  (1.28656, 1.3% from target), engine-level honest negative with full
  diagnostics (31 runs, ~14 s).
- **C3b** — concentrated resolution: deep grids (N = 1600/3200) on the
  critical window; the **floor ladder** `floor_M ~ (13 ± 1)/N` is the
  first-class result; both engine-level negatives re-confirmed (16
  runs, ~97 s).
- All four verdicts carry `project_version 2.1.0` and were re-run fresh
  from the clean-slate build; C1 physics is byte-identical to v1.0.0.
- Verdicts are committed under `reference/`; the derived tables in
  `data/bridge/` are rebuilt from them by `scripts/rebuild_data.py`.

**Contents**

- [Runbook](#runbook)
- [Campaign C1](#campaign-c1)
- [Campaign C2](#campaign-c2)
- [Campaign C3](#campaign-c3)
- [Campaign C3b](#campaign-c3b)
- [Verdict schema](#verdict-schema)
- [Adding a campaign](#adding-a-campaign)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)

---

## Runbook

```bash
make c1            # full C1 campaign, ~1 min, fresh verdicts
make c2            # C2 two branches, ~30 s (needs c1_verdict.json)
make c3            # C3 invariant check, ~15 s (needs c1_verdict.json)
make c3b           # C3b concentrated resolution, ~2 min (needs c1_verdict.json)
make data          # rebuild data/bridge from committed verdicts
make test          # 60 tests pin the committed numbers
```

Re-running a campaign on the same machine produces bit-identical
physics (pure NumPy float arithmetic, no RNG); wall times vary.  If you
re-run C1 and the verdict changes, that is a bug — file it.

Dependency chain: C1 first (it commits `A*_800`); C2, C3, C3b each
reuse that committed `A*_800` so all spectra stay commensurable.

## Campaign C1

`run_c1.py` — the reference campaign.  Five stages, five output blocks:

| stage | what | committed result (v2.1.0) |
|---:|---|---|
| 1 | Roberts-Oshiro validation, N=200/400/800 | orders **2.031 / 2.093** |
| 2 | bisection `A*_N`, N=200/400/800 | **0.10510483 / 0.08820114 / 0.08053436**; remediated reference ladder (F-1, `a_star_ladder.csv`): N=1600 **0.07774373**, N=3200 **0.07682116** — the threshold DRIFTS with N (2.79e-3 over N800->N1600); the stale 2.0.0 claim of a 1.06e-6 agreement is retracted |
| 3 | amplitude scans: 26 rows N=400 + 18 rows N=800 | born spectrum, `M_code_sat = 0.0794` (N=400), floor `1.55e-2` |
| 4 | evolution profiles (sub/supercritical) | `profiles_sub_supercritical.json` |
| 5 | verdict + CSVs | `c1_verdict.json`, `amplitude_scan_N400.csv`, `amplitude_scan_N800.csv` |

The grid-honesty ladder is the point of stage 2: the drift of `A*_N`
across grids *is* the fixed-grid floor made visible, which is why all
three values are committed, not just the finest one.

Spectrum rows carry a `stop` reason (`completed`, `AH mass saturated`,
junk flag) and a `sane` boolean (`0 < M_code < 0.1`).  Junk rows are
kept with their raw overflowing masses verbatim — see
`honest_notes.junk_examples` in the verdict.

## Campaign C2

`run_c2.py` — the two branches around the committed threshold.  C1
found *where* the threshold is; C2 measures what happens on *both*
sides of it.

**Branch S — subcritical dispersal** (13 runs, `A = A*_800 - eps`,
eps in [10^-1.2, 10^-4.2]; the upper bound keeps `A > 0` so the pulse
family stays the same — negative-amplitude runs are excluded by
construction, not filtered afterwards):

| measurable | committed result (v2.1.0) |
|---|---|
| peak compactness `q_max = max(2m/r)` | grows **monotonically** 0.0158 -> 0.5845 as eps -> 0, never crossing the horizon value 1 |
| critical slowdown | `v_qmax = 0.510 - 0.0334*ln(eps)`, **r^2 = 0.714** — the DSS logarithmic approach, measured |
| echo counter `n_peaks` | **0.1909 peaks / e-fold** (r^2 = 0.714) against the anchor `1/Delta = 0.2907` — same order, below it, honestly |
| residual compactness | `q_final/q_max` committed per row |

**Branch X — supercritical born bifurcation** (13 runs,
`A = A*_800 + eps`, eps in [10^-0.5, 10^-4.0]):

| measurable | committed result (v2.1.0) |
|---|---|
| saturation mass `M_sat` (this scan) | **0.03518979** (C1's N=400 value 0.0794 kept as cross-check; saturation is grid-dependent like everything else) |
| bifurcation half-width | **`eps_half = 4.8598e-3`** — the log-eps interpolation of the `f~ = 0.5` crossing; a floor-robust width indicator |
| bifurcation depth | `f~_min = 0.384` in the sub-window eps < 1e-2 |
| junk rows | 3 rows with overflowing masses, kept with `sane=false` |

The exponent fit is deliberately **not** repeated here — C3 owns that
committed measurement; C2 maps the *shape* of the bifurcation.
Subcritical runs that form an apparent horizon would be kept verbatim
with `flipped=true` (none at the committed range, and the mechanism is
tested: the first draft of this campaign did flip two rows and they
were kept, not deleted).

Outputs: `c2_verdict.json`, `subcritical_scan.csv`,
`bifurcation_ftilde.csv`.

## Campaign C3

`run_c3.py` — the Delta*gamma invariant check
(`Delta * gamma =? 1.27`, tolerance 0.05).  Three products:

| product | inputs | v2.1.0 verdict |
|---|---|---|
| `P_anchor` | `Delta_lit = 3.44` x `gamma_Ch = 0.374` | **1.28656 -> PASS** (1.3% from target) |
| `P_mixed` | measured `Delta_eff` x anchor `gamma_Ch` | not measurable (peaks < 3) |
| `P_engine` | measured `Delta_eff` x measured `gamma_eff` | not measurable (grid floor) |

The two measurements behind the engine products:

- **gamma_eff** — supercritical scan `eps in [6.3e-5, 1e-1]` (16 points,
  N=800), log-log fit over sane non-junk rows.  Committed outcome:
  **flat** (`0.005 +- 0.035`, `r^2 = 0.003`) — the mass floor wins
  across ~4 decades of eps; gamma is not percent-measurable at fixed
  grid.  The scan rows are committed in the verdict (`scan_rows`).
- **Delta_eff** — log-time echo detector: peaks of
  `q(v) = max_r(2m/r)` recorded every row; estimate
  `Delta = -mean diff ln(v* - v_k)` with `v*` proxied by the
  apparent-horizon time `v_ah`.  Committed outcome: **2 peaks per run**
  at `eps = 1e-3 / 3e-4 / 1e-4` — below the 3-peak minimum; per-run
  peak tables are in the verdict.

**Standing conclusion:** the invariant is confirmed at anchor level and
unconfirmed at engine level; C3b (below) is the concentrated-resolution
retry — and the negatives survive it.

## Campaign C3b

`run_c3b.py` — deep grids spent *only* on the critical window.  The
honest definition of "adaptive" here: no AMR rewrite of the engine;
resolution is *concentrated* (N = 1600/3200 on a narrow eps band and on
echo runs nearest each grid's OWN threshold — v2.0.1 F-2 remediation:
the 2.0.0 run reused A*_N800 as the deep-grid base, mislabeling eps by
+2.8e-3 and biasing gamma_eff to ~0.11; retracted).

| product | committed result (v2.0.1) |
|---|---|
| **per-grid thresholds** | `A*_N1600 = 0.07774434`, `A*_N3200 = 0.07682177` (freshly bisected, committed in `a_star_per_grid`) |
| **floor ladder** | **0.0155 (N=800, C1) > 8.574765e-3 (N=1600) > 4.244867e-3 (N=3200)** — the first-class result |
| gamma ladder | `gamma_eff = 0.0410 +- 0.0262` (N=1600, r^2=0.33) -> `0.0605 +- 0.0417` (N=3200, r^2=0.41) — floor-dominated, honestly weak; does NOT approach the anchor 0.374 |
| delta ladder | 1-2 peaks per run at N=1600/3200 — **no run resolves >= 3 peaks at any depth**; `delta_eff` stays null |
| `P_engine_deep` | **null** (honest negative kept with reason strings) |
| `P_anchor` | **1.28656 -> PASS** (re-confirmed) |

Interpretation discipline: C3b does *not* overturn C3's negatives — it
reinforces them with 27 deeper per-grid runs and keeps the floor ladder
as the first-class result, which is what any future engine upgrade must
beat.

Outputs: `c3b_verdict.json`, `c3b_gamma_ladder.csv`.

## Campaign C6

`run_c6_drift.py` — the resolution-drift law (theorem T10, new at
v2.1.0).  No engine march: the campaign is a deterministic analysis of
committed artifacts (the F-1 ladder, the C1 profiles, the C2
subcritical scan) that (i) measures the ladder's drift signature,
(ii) stress-tests the naive extrapolation and rejects it, (iii)
machine-verifies the two exact lemmas of the parabolic-tension
mechanism (chord flattening κh²/8; chord-chain arc deficit), and (iv)
calibrates the exact-channel coefficients κ\* = 2728.60 and
s = 413.8, computing the channel's share of the observed drift.

| product | committed result (v2.1.0) |
|---|---|
| ladder signature | drifts 1.69e-2 → 9.23e-4 per doubling; `p_eff = 1.140 / 1.459 / 1.596` — strictly climbing, faster than 1/N |
| extrapolation | two-term law fits R² = 0.999 yet is **REJECTED** by its own p_eff trajectory — `A*_inf` NOT claimable |
| Lemma A | worst-alignment deficit == κh²/8 to 2.0e-9; average == κh²/24 (exact) |
| Lemma B | chord chain == midpoint-rule sum to 1.9e-16; strictly shorter than the arc (compression under tension) |
| calibration | κ\* = 2728.60 (supercritical profile, v = 0.5853); s = 413.8 (two deepest C2 rows); exact-channel share 2.6e-3…9.1e-3 |
| verdict | the drift EXISTS, is POSITIVE (from above), leading exact channel O(h²); the dominant channel is a labeled hypothesis |

Why it matters: this campaign converts the audit's F-1 embarrassment
into a theorem — one formula evaluated at scalar-scaled grids MUST
return different values, because grid-sampled parabolic structures
stretch and compress under the curvature of their tension.  Artifacts:
`c6_drift_verdict.json`, `c6_drift_channels.csv`,
`c6_parabola_check.csv`; derivation in `docs/scaling_law.md`; report
with figures in `results/scaling_drift/`.

## Verdict schema

All five verdicts share the self-describing envelope:

```json
{
  "campaign": "chb_c2",
  "engine": "engine/solver.py — double-null characteristic march (Goursat, RK2-Heun)",
  "project_version": "2.1.0",
  "units": "4 pi G = 1 (kappa = 2), geometric engine units",
  "family": {"u0": -1.0, "v_p": 0.5, "sigma": 0.1, "v0": 0.0, ...},
  "timestamp": "...", "wall_total_s": 23.7
}
```

C1 adds: `validation` (per-grid errors + orders), `a_star_grid`,
`scan_N400` / `scan_N800` (with full row lists), `scaling_fit` (with
its floor comment), `honest_notes` (junk examples, floor statement, A*
convergence string).  C2 adds: `subcritical` (rows + `slowdown_fit` +
`echo_rate_fit`), `bifurcation` (rows + `summary`), `honest_notes`.
C3 adds: `gamma`, `delta` (with `per_eps_rows`), `products` (with
per-product verdict strings), `target`, `scan_rows`.  C3b adds:
`method` (the concentrated-resolution definition), `gamma_ladder`,
`delta_ladder`, `products`, `honest_notes`.  C6 adds:
`ladder_analysis`, `extrapolation_stress_test`, `parabola_checks`,
`tension_calibration`, `sensitivity_calibration`,
`channel_decomposition`, `theorem`, `honest_notes`.

Rules the schema enforces:

1. Every number lives at exactly one address (verdict path + key).
2. Every honest negative carries a human-readable reason string.
3. `wall_total_s` and `timestamp` are mandatory — a verdict is an
   experiment record, not just a result.
4. Verdicts are append-only history of *measurements*: re-runs replace
   a verdict only with a fresh timestamp and a CHANGELOG entry.

## Adding a campaign

Copy the C2/C3 template (argparse knobs, stages with printed progress,
JSON verdict into `reference/`, honest-notes block).  Campaigns stay in
engine code units; any physical mapping belongs to `chbridge`.  The
project version reflects the release train (see CHANGELOG.md); verdict
schema changes are CHANGELOG events.

## Honesty notes

- `A*_N` values are grid-dependent by nature — and the dependence is a
  theorem (C6/T10), not an embarrassment.  Only the ladder as a whole
  is the result.  Do not quote `A*_800` without its ladder, and never
  quote an `A*_inf` extrapolated from it.
- The C3 and C3b engine-level negatives are results, not failures;
  removing them from the verdicts would be data falsification.
- The anchors (`gamma_Ch`, `echo_delta`, `1/Delta`) are never fit
  targets; no stage of any campaign optimizes toward them.
- C2's slowdown/echo fits are measured at 40 compactness samples per
  run; the sampling step is part of the instrument, not noise to hide.

## FAQ

**Q: Can I run C1 at higher resolution?**
A: `python3 campaigns/run_c1.py` is parameter-free by design (the
committed ladder is N=200/400/800).  For a custom ladder, copy the
script into your own campaign per CONTRIBUTING.md — do not overwrite
the committed verdicts.

**Q: Why do C2, C3 and C3b need `c1_verdict.json`?**
A: They measure *around* the committed `A*_800`; reusing it guarantees
that all four campaigns' spectra are commensurable.

**Q: C3b used deeper grids — why not call it AMR?**
A: Because it is not.  The engine is untouched; only the *allocation*
of resolution is concentrated on the critical window.  The verdict
`method.definition_of_adaptive` carries this exact sentence.

**Q: Which campaign should I cite for the floor?**
A: C3b (`floor_M ~ (13 ± 1)/N` on the per-grid F-2 values); C1's `mass_floor_N800 = 0.0155` is the
N=800 point of the same ladder.

**Q: What is the minimum I must run to reproduce the paper numbers?**
A: `make data && make test && make validate` — the derived tables,
their pins, and the 50-digit layer, in under a minute.  Fresh campaigns
(`make c1 && make c2 && make c3 && make c3b`) are the full pipeline.

## See also

- [engine/](../engine/README.md) — the measured instrument
- [data/](../data/README.md) — where derived tables live
- [docs/methods.md](../docs/methods.md) — protocols in full detail
- [results/RESULTS.md](../results/RESULTS.md) — the ledger

---

## Краткое резюме (Russian)

Кампании — протоколы измерений на движке с фиксацией машинных
вердиктов; все движковые вердикты несут версию проекта 2.1.0 и получены
свежим прогоном (физика байт-идентична зафиксированной). **C1** (45
прогонов, ~48 с): валидация Робертса–Оширо (порядки 2.03/2.09),
ремедиационная лестница честности сетки A* по пяти сеткам (дрейф 2.79e-3
от N=800 к N=1600 — честный; старое заявление 1.06e-6 отозвано, F-1),
спектры рождения. **C2** (26 прогонов,
~24 с): две ветви вокруг порога — докритическая (монотонный рост
пиковой компактности 0.0158 → 0.5845, критическое замедление
v_qmax = 0.510 − 0.0334·ln(eps), r² = 0.71; накопление эхо 0.1909
пиков/е-фолд при якоре 1/Δ = 0.2907) и сверхкритическая бифуркация
(M_sat = 0.0352, полуширина eps_half = 4.86e-3). **C3** (31 прогон,
~14 с): инвариант Δ·γ ≈ 1.27 — якорное произведение **1.28656 → PASS**
(1.3%), движковый уровень — честный негатив. **C3b** (16 прогонов,
~334 с): концентрированное разрешение (N=1600/3200, пороги по каждой
сетке) — первый класс
результатов: лестница пола **floor_M ~ (13 ± 1)/N** на пороговых
значениях каждой сетки (0.0155 → 8.57e-3 → 4.24e-3); гамма-фиты
определяются полом (γ_eff = 0.041/0.060; якорь 0.374 не
достигается — пол правит в достижимой полосе), эхо-негатив подтверждён
на всех глубинах, P_engine_deep = null. **C6** (~2 с, без марша
движка): закон дрейфа с разрешением — теорема T10: сплющивание κh²/8,
ломаная короче дуги, A*_N − A*_конт = κ*h²/(8s) > 0; A*_∞ не
утверждается. Вердикты самодостаточны: схема,
юниты, честные примечания, времена выполнения. Спектры в кодовых
единицах; физическое отображение — только в `chbridge`.
