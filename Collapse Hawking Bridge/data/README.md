# data

Derived, committed data tables of the **Collapse-Hawking Bridge** — everything
the figures, the docs and the results ledger quote numerically lives under
`data/bridge/`, and nothing in this folder is computed at read time.

![v2.1.0](https://img.shields.io/badge/version-2.1.0-8C6D1F)
![status](https://img.shields.io/badge/status-committed-gold)
![provenance](https://img.shields.io/badge/provenance-verdicts_%E2%86%92_tables-gold)
![tests](https://img.shields.io/badge/tests-63_passed-brightgreen)

**TL;DR**

- Thirteen files in `data/bridge/`: ten core tables (nine CSV + one JSON summary)
  plus three campaign tables copied verbatim from the C2/C3b verdicts.
- Single provenance chain: four campaign verdicts → `scripts/rebuild_data.py`
  (stages [1/5]…[5/5]) → these tables. No circularity, no hand edits.
- `bridge_master.csv` is the central artifact: 15 rows × 23 columns mapping each
  born black hole (5 input scales × 3 ensemble members) to its thermodynamics.
- Honest negatives are first-class data: junk rows and the fixed-grid mass
  floor are committed, not hidden — and `floor_M(N) ≈ (13 ± 1)/N` is now a measured
  result across N = 800/1600/3200.
- Rebuilding is deterministic: `make data` must be a byte-level no-op on a clean checkout, campaign tables included.

---

## Table of contents

- [Provenance chain](#provenance-chain)
- [What lives here](#what-lives-here)
- [Reading the tables](#reading-the-tables)
- [The campaign tables: verdict rows, verbatim](#the-campaign-tables-verdict-rows-verbatim)
- [Honesty flags, junk rows, and the floor ladder](#honesty-flags-junk-rows-and-the-floor-ladder)
- [Regeneration and determinism](#regeneration-and-determinism)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)
- [See also](#see-also)
- [Краткое резюме (Russian)](#краткое-резюме-russian)

## Provenance chain

Data flows in one direction only; there is no circularity anywhere in the chain.

```
campaigns/run_c1.py   ──►  campaigns/reference/c1_verdict.json   (validation, A* ladder, born spectrum)
campaigns/run_c2.py   ──►  campaigns/reference/c2_verdict.json   (both branches around the threshold)
campaigns/run_c3.py   ──►  campaigns/reference/c3_verdict.json   (Δ·γ check)
campaigns/run_c3b.py  ──►  campaigns/reference/c3b_verdict.json  (concentrated resolution, N=1600/3200)
                                   │
                                   ▼
              scripts/rebuild_data.py            (stages [1/5] … [5/5])
                                   │
        float-exact recomputation       +       verdict rows copied VERBATIM
        (chbridge bridge/page/ladder)           (no rounding, no reordering)
                                   │
                                   ▼
     ten core tables + summary JSON   +   campaign_c2_subcritical.csv
                                          campaign_c2_bifurcation.csv
                                          campaign_c3b_ladder.csv
                                   └──►  figures · docs · results
```

All four engine verdicts carry `project_version "2.1.0"` (re-run fresh; physics byte-identical to the committed values); the committed wall times are
C1 48.36 s, C2 23.69 s, C3 13.69 s, C3b 96.81 s (each verdict's own
`wall_total_s` field). The verdicts under `campaigns/reference/` are the law:
the only place where raw campaign numbers live. The provenance principle is
stated in `scripts/rebuild_data.py` and enforced by tests: the script never
invents physics — it re-derives tables from the verdicts, copies campaign rows
verbatim, and this folder holds the derived view.

## What lives here

Row counts are data rows (the header line is not counted).

| File | Rows | Written by | Quoted / consumed by |
|---|---:|---|---|
| `born_spectrum.csv` | 44 | `chbridge.bridge.write_outputs` — stage [1/5] | [methods](../docs/methods.md), [validation](../docs/validation.md) |
| `bridge_master.csv` | 15 | `chbridge.bridge.write_outputs` — stage [1/5] | `tests/test_hawking.py` (cross-check row), [theory](../docs/theory.md) |
| `collapse_verdict_summary.json` | — | `chbridge.bridge.write_outputs` — stage [1/5] | [RESULTS.md](../results/RESULTS.md) |
| `page_curve_grid.csv` | 720 | `chbridge.page.write_outputs` — stage [2/5] | `scripts/make_figures.py` (`fig_page`) |
| `page_members.csv` | 15 | `chbridge.page.write_outputs` — stage [2/5] | [theory](../docs/theory.md), [methods](../docs/methods.md) |
| `page_haar_check.csv` | 18 | `chbridge.page.write_outputs` — stage [2/5] | [methods](../docs/methods.md), [validation](../docs/validation.md), [RESULTS.md](../results/RESULTS.md) |
| `scale_ladder_accel.csv` | 7 | `chbridge.ladder.write_outputs` — stage [3/5] | [theory](../docs/theory.md) |
| `scale_ladder_length.csv` | 8 | `chbridge.ladder.write_outputs` — stage [3/5] | `scripts/make_figures.py` (`fig_ladder`) |
| `scale_ladder_curvature.csv` | 5 | `chbridge.ladder.write_outputs` — stage [3/5] | [theory](../docs/theory.md) |
| `bridge_constants.csv` | 8 | `chbridge.ladder.write_outputs` — stage [3/5] | [RESULTS.md](../results/RESULTS.md) |
| `campaign_c2_subcritical.csv` | 13 | `rebuild_data.py::campaign_tables` — stage [4/5] | `tests/test_campaigns.py` (row pins) |
| `campaign_c2_bifurcation.csv` | 13 | `rebuild_data.py::campaign_tables` — stage [4/5] | `tests/test_campaigns.py` (row pins) |
| `campaign_c3b_ladder.csv` | 12 | `rebuild_data.py::campaign_tables` — stage [4/5] | `tests/test_campaigns.py` (row pins) |

## Reading the tables

### `born_spectrum.csv` — the born spectrum

44 rows = 26 scan points at grid N=400 plus 18 at N=800 (amplitude scans of
campaign C1, ~3.2 decades in ε at N=400, ~2.5 at N=800). Columns: `grid`
(engine resolution), `A` (pulse amplitude, code units 4πG = 1), `eps`
(ε = A − A*), `M_code`, `f_tilde` (born mass fraction f̃ = M_code/M_code_sat),
`stop` (stop reason), `sane` (physically interpretable).

Stop-reason census over the 44 rows:

| `stop` | Rows | Meaning |
|---|---:|---|
| `AH mass saturated` | 28 | apparent horizon reached the saturated code mass |
| `completed` | 10 | march finished with a resolved sub/supercritical outcome |
| `junk row (mass outside physical scale)` | 6 | mass outside the physical scale — kept and flagged |

### `bridge_master.csv` — the central table

15 rows = 5 input scales × 3 ensemble members. Input scales: Planck
m_P = 2.176434e-08 kg, Asteroid 1e12 kg, CMB 4.50e22 kg, Earth 5.9722e24 kg,
Solar 1.98892e30 kg. Ensemble members (from the summary JSON): `near_floor`
(ε = 4.436687e-04, f̃ = 0.2877, M_code = 0.022852), `mid` (ε = 1.311134e-02,
f̃ = 0.2684, M_code = 0.021326), `saturated` (ε = 5.011872e-01, f̃ = 1.0,
M_code = 0.079443).

Column dictionary — 23 columns in six groups:

| Group | Column | Meaning |
|---|---|---|
| identity (7) | `input_scale` | one of the five input scales above |
| | `M_in_kg` | input mass, SI kg |
| | `member` | `near_floor` / `mid` / `saturated` |
| | `eps` | distance from critical amplitude, engine code units |
| | `f_tilde` | born mass fraction of the member |
| | `M_BH_kg` | born black-hole mass, M_BH = f̃ · M_in, SI kg |
| | `M_BH_over_M_in` | mass ratio (equals `f_tilde` by construction) |
| geometry (4) | `r_s_m` | Schwarzschild radius 2GM/c², metres |
| | `r_s_over_lP` | radius in Planck lengths |
| | `rho_mean_kg_m3` | mean density inside the horizon, ~ M⁻² |
| | `surface_grav_m_s2` | horizon surface gravity κ = c⁴/(4GM) |
| thermo (2) | `T_H_K` | Hawking temperature, kelvin |
| | `S_BH_over_kB` | Bekenstein–Hawking entropy in units of k_B |
| radiation (5) | `P_H_W` | Hawking luminosity, watts |
| | `t_evap_s` | semiclassical evaporation time, seconds |
| | `t_evap_human` | the same, human-readable (e.g. `2.67e12 yr`) |
| | `t_Page_s` | Page time (1 − 2^(−3/2)) · t_evap, seconds |
| | `t_Page_human` | the same, human-readable |
| curvature (2) | `K_horizon_m4` | Kretschmann scalar K at the horizon, m⁻⁴ |
| | `K_horizon_over_KP` | K relative to the Planck curvature 1/l_P⁴ |
| comparison (3) | `f_QNM_l2_Hz` | l=2 fundamental QNM frequency (M·ω_R = 0.3737) |
| | `f_QNM_corr_Hz` | the same with the shift 1/(1200π²) = 8.44343e-5 applied |
| | `T_H_over_T_CMB` | Hawking temperature over the CMB temperature (2.72548 K) |

### Page-model tables

- `page_curve_grid.csv` (720 rows) — S_BH(t) and S_rad(t) for the CMB input
  scale, fully sampled: 3 members × 240 time points; normalized curves
  (`*_norm`, units of S_0) plus absolute entropies in k_B. Unitary flux rule:
  S_rad = S_BH before the Page time, S_rad = S_0 − S_BH after.
- `page_members.csv` (15 rows) — per-scale member sheet: S_0, T_H, t_evap,
  t_Page and the constant ratio t_Page/t_evap = 0.646447.
- `page_haar_check.csv` (18 rows) — exact Page/Haar formula vs seeded
  Monte-Carlo for 18 partitions (N_total 4…7, 3000/1200 samples,
  seed 20260101). Max deviation committed in the file: 0.004208 bits.

### Scale ladders

- `scale_ladder_length.csv` (8 rows): l_P … c/H0, one log axis.
- `scale_ladder_accel.csv` (7 rows): a0, cH0, cH0/2π, surface gravities.
- `scale_ladder_curvature.csv` (5 rows): horizon curvature vs the Planck value.
- `bridge_constants.csv` (8 rows): the project invariants with their status
  (anchor, exact, comparison) in the `source` column.

### `collapse_verdict_summary.json` — C1 at a glance

| Key | Value (committed) |
|---|---|
| `a_star_grid` | A*_N200 = 0.10510483, A*_N400 = 0.08820114, A*_N800 = 0.08053436 |
| `a_star_reference_N1600` / `a_star_drift_N800_vs_reference` | 0.0777437257766724 (remediated ladder, F-1) / 2.7906e-03 |
| `roberts_convergence_orders` | 2.0313, 2.0933 |
| `M_code_sat` / `mass_floor_N800_code` | 0.079443 / 0.022852 (near-floor member mass) |
| `f_tilde_range_resolved` | [0.28765, 1.0] |
| `gamma_campaign` | "honestly unmeasurable: fixed-grid floor dominates (C3 floor-biased gamma_eff = 0.005 +- 0.035 at N=800; C3b per-grid remediation concurs: 0.041 / 0.060 at N=1600/3200, floor-dominated)" |
| `gamma_Ch_anchor` / `b_Ch` | 0.374 / 0.3765101981412664 — the 0.67% gap is |γ_Ch − b_Ch|/b_Ch (literature vs the project's own hypothesis constant; the former `b_Ch_lit` key was a rounded copy of b_Ch and is removed at v2.2.0) |
| `junk_rows` / `M_CMB_kg` / `members` | 6 / 4.5016e22 / the three members above |

## The campaign tables: verdict rows, verbatim

Stage [4/5] of `scripts/rebuild_data.py` (`campaign_tables`) writes the three
campaign tables. Their defining rule: **the CSV cells are the JSON cells** —
no recomputation, no rounding, no reordering. A campaign whose verdict file is
absent is skipped with a printed note (`skipped: c2_verdict.json not found —
run its campaign first`), so `make data` works on partial checkouts; the
remaining tables are still written.

### `campaign_c2_subcritical.csv` — branch S: dispersal (C2, N=800)

13 rows from `c2_verdict.json → subcritical.rows`. Subcritical branch:
A = A*_800 − eps with A*_800 = 0.08053436, eps spanning [10^−1.2, 10^−4.2].
The field disperses; no apparent horizon forms.

| Column | Meaning |
|---|---|
| `eps` | distance below the threshold amplitude |
| `A` | pulse amplitude A*_800 − eps |
| `q_max` | peak compactness max(2m/r) reached during the run |
| `v_qmax` | engine time v of that peak (critical-slowdown observable) |
| `n_peaks` | local maxima of q(v) — the echo counter on the dispersing side |
| `q_final_over_qmax` | residual compactness, final over peak |
| `flipped` / `stop` | `False` / `completed` on all 13 committed rows |

The physics the table pins: `q_max` grows strictly monotonically as eps → 0
(0.0158 → 0.5845 across the scan) and stays below 1 — the approach to the
horizon without crossing it. The fitted slowdown slope (`v_qmax` vs ln eps)
is −0.03345 (r² = 0.714) and the echo accumulation rate is
0.1908986733640667 per e-fold, below the 1/Δ anchor 1/3.44 = 0.2907; the fits
live in the verdict, not here.

### `campaign_c2_bifurcation.csv` — branch X: the born bifurcation (C2, N=800)

13 rows from `c2_verdict.json → bifurcation.rows`. Supercritical branch:
A = A*_800 + eps; a horizon forms and its mass saturates or settles.

| Column | Meaning |
|---|---|
| `eps` | distance above the threshold amplitude |
| `A` | pulse amplitude A*_800 + eps |
| `M_code` | apparent-horizon mass in code units |
| `f_tilde` | M_code / M_sat, with M_sat = the largest sane mass of THIS scan = 0.03518978551089466 |
| `stop` / `sane` | `AH mass saturated` (8 rows) or `completed` (5); `sane` True ×10, False ×3 |

The junk rows carry overflowing masses (1.83e7, 9.05e3, 5.73e6 code units —
the fixed grid lying at small eps); they keep `sane=False`, an empty
`f_tilde`, and their place in the table. The scan summary lives in the
verdict: eps_half = 0.004859801757908699, the eps where f̃ crosses 0.5 — a
floor-robust width of the bifurcation window.

### `campaign_c3b_ladder.csv` — the resolution ladder (C3b, N=1600/3200)

12 rows from `c3b_verdict.json → gamma_ladder`: 7 rows at N=1600 and 5 rows
at N=3200, both concentrated on the critical eps window (eps ≤ 0.0316).

| Column | Meaning |
|---|---|
| `N` | engine grid resolution, 1600 or 3200 |
| `eps` | distance above the committed A*_800 |
| `A` | pulse amplitude |
| `M_code` | apparent-horizon mass in code units |
| `stop` | `AH mass saturated` on all 12 rows |
| `sane` | `True` on all 12 rows |

On each grid, the smallest sane mass is the campaign's `floor_M`:
8.574765e-03 at N=1600 and 4.244867e-03 at N=3200 (v2.0.1 per-grid
remediation, F-2). The fitted exponents (gamma_eff = 0.0410 / 0.0605,
floor-dominated r² = 0.33 / 0.41) stay in the verdict; the table holds
the rows they were fitted from. The 2.0.0 exponents (0.1113 / 0.1205) — retracted artifacts (F-2);
the committed per-grid values are 0.0410 / 0.0605 —
were artifacts of the mislabeled eps axis and are retracted.

## Honesty flags, junk rows, and the floor ladder

- `sane = True` marks rows that are physically interpretable at their grid;
  all sane rows satisfy 0 < f̃ ≤ 1 (or, in the subcritical table, 0 < q_max < 1).
- `sane = False` marks junk rows. Six are committed in `born_spectrum.csv`,
  three in `campaign_c2_bifurcation.csv`, each with a `stop` string saying
  why. Junk rows are data, not noise: they document where the fixed-grid
  engine stops being trustworthy.
- `flipped = True` is reserved for subcritical runs that formed an apparent
  horizon anyway (A*_800 is a fixed-grid quantity, so the closest eps can
  cross it). No committed run flipped — all 13 rows carry `False`, and
  `flipped_runs = 0` is pinned by `tests/test_campaigns.py`; had one flipped,
  the row would have been kept verbatim, not discarded.
- The fixed-grid mass floor of the C1 scan is likewise committed: the N=800
  scan contains sane masses down to M_code = 1.55e-2 (the scaling figure's
  floor guide), and `mass_floor_N800_code = 0.022852` is the near-floor member.

The single most consequential measured trend of the deep-grid campaigns: the fixed-grid mass
floor is a function of resolution, and it sinks like 1/N.

| N | floor_M [code units] | Source |
|---:|---|---|
| 800 | 1.55e-2 | campaign C1 (`CAMPAIGN["mass_floor_N800"]`) |
| 1600 | 8.574765e-03 | campaign C3b (v2.0.1 per-grid, F-2), `gamma_ladder.N1600.floor_M` |
| 3200 | 4.244867e-03 | campaign C3b (v2.0.1 per-grid, F-2), `gamma_ladder.N3200.floor_M` |

(The 2.0.0 floors 7.104e-3/3.842e-3 were measured on the mislabeled eps
axis and are retracted; the `floor_M ~ (13 ± 1)/N` law is the current
statement — the `12/N` heuristic slogan is
retracted — with per-grid thresholds the floor is quoted per grid, not
fitted to a power law.)
The C3 verdict "gamma is unmeasurable at the fixed grid" is therefore a floor
statement, not a death certificate: the floor is a knob, and C3b turned it.

## Regeneration and determinism

Regenerate everything from the committed verdicts:

```console
$ make data                      # or: python3 scripts/rebuild_data.py
[1/5] bridge tables ...
      born spectrum rows: 44
      master table rows : 15 (5 input scales x 3 ensemble members)
      a* agreement vs reference (N=1600): 1.06e-06
[2/5] page tables ...
      grid points: 720, haar partitions: 18, max |S_formula - S_MC| = 0.0042 bits
[3/5] ladder tables ...
      ladders: 7 accel, 8 length, 5 curvature
      a0 / (cH0/2pi) = 1.1470
      |gamma_Ch - b_Ch| / b_Ch = 0.67%
[4/5] campaign tables (C2 branches, C3b resolution ladder) ...
      wrote campaign_c2_subcritical.csv
      wrote campaign_c2_bifurcation.csv
      wrote campaign_c3b_ladder.csv
[5/5] consistency spot-check ...
      C2: 13 subcritical runs (0 flipped), slowdown slope = -0.0334, echo rate = 0.1909 /e-fold
      C2: M_sat(N=800) = 0.03519, eps_half = 4.8598e-03
      C3b N1600: gamma_eff = 0.0410 (floor_M = 8.5748e-03)
      C3b N3200: gamma_eff = 0.0605 (floor_M = 4.2449e-03)
      C3b: P_anchor = 1.28656 -> PASS, P_engine_deep = None (honest negative kept)

all outputs -> .../data/bridge
```

Determinism guarantee:

- The script is float-exact: the same verdict JSON produces the same bytes,
  campaign tables included. Verified for this README: `md5sum` over all of
  `data/bridge/` before and after a rebuild — identical.
- `tests/test_bridge.py::test_rebuild_determinism` writes the tables twice and
  asserts byte-identity of `bridge_master.csv`.
- On a clean checkout, `make data && git diff --stat data/` must print nothing.
  If it does not, something above this folder changed — fix that, never the CSV.

Quick sanity checks you can run anywhere:

```console
$ python3 -c "import csv; d='data/bridge/'; f=lambda n: len(list(csv.DictReader(open(d+n)))); print(f('bridge_master.csv'), f('campaign_c3b_ladder.csv'))"
15 12
```

## Honesty notes

- Nothing in this folder is a fit result. `gamma_Ch = 0.374` is a literature
  anchor, `b_Ch` is exact, and their 0.67% closeness is a comparison, never a fit.
- Campaign C2 deliberately does NOT re-fit the critical exponent — C3 owns
  that committed measurement; C2 commits the shape (the f̃ table, eps_half)
  only. `gamma_eff` at N=1600/3200 (0.0410 / 0.0605, v2.0.1 per-grid
  remediation F-2) is a floor-biased effective exponent, still far below
  γ_Ch = 0.374: no table here claims a settled critical exponent; the
  settled claim is the floor ladder.
- `v_qmax` in the subcritical table is sampled by 40 engine snapshots per run;
  the sampling step is visible as quantization (the 13 rows carry only two
  distinct `v_qmax` values). Peak counts carry the same limitation.
- The campaign CSVs are verbatim copies of verdict rows; if a number here and
  a number in `campaigns/reference/` ever disagree, the JSON wins — rerun
  `make data`.
- `a0/(cH0/2π) = 1.1470` is a numerical coincidence stored for completeness —
  the table itself labels it "a NUMERICAL coincidence … not a derivation".
- The Page-model member profile (f̃ = 0.287708 / 0.268393) and the verdict-born
  profile (f̃ = 0.287652 / 0.268447) agree to four significant figures but are
  not bit-identical; both are committed as written, in their own tables.
- Campaign C3 quantifies the Δ·γ product; only its anchor-side value
  (3.44 × 0.374 = 1.28656, PASS at 1.3% from the 1.27 target, tolerance 0.05)
  is committed here indirectly via `bridge_constants.csv`. The deep-grid
  engine product remains `None` — an honest negative, kept.

## FAQ

**Why is the same CSV in two places?**
It is not. Tables live only in `data/bridge/`; raw campaign outputs live only
in `campaigns/reference/`. The three `campaign_*.csv` files are one-directional
verbatim copies of verdict rows; the JSON verdict remains the law.

**Can I edit the CSVs?**
No. They are derived artifacts; rerun `make data` instead. If a number must
change, the change belongs in the verdict JSON or in `chbridge/`, and the
tables follow.

**Why are junk rows committed at all?**
Because a dataset that silently drops its failures lies about its own
resolution limits. The nine flagged rows, the `flipped` column and the floor
ladder document exactly where the fixed grids stop being trustworthy.

**How do I know the tables are current?**
Run `make data`. It must be a no-op. Any diff means the tables and the
verdicts disagree, and the verdicts win.

**Where do the figures come from?**
`scripts/make_figures.py` reads `page_curve_grid.csv` and
`scale_ladder_length.csv` from this folder and the campaign verdicts directly;
see [figures](../figures/README.md).

## See also

- [Campaign C1: run_c1.py](../campaigns/run_c1.py) · [C2: run_c2.py](../campaigns/run_c2.py) · [C3b: run_c3b.py](../campaigns/run_c3b.py) — verdict producers
- [rebuild_data.py](../scripts/rebuild_data.py) — the only writer of this folder
- [results/RESULTS.md](../results/RESULTS.md) — the living results ledger
- [docs/methods.md](../docs/methods.md) and [docs/validation.md](../docs/validation.md)
- [tests/test_campaigns.py](../tests/test_campaigns.py) — what pins the campaign tables

## Краткое резюме (Russian)

Папка `data/bridge/` содержит тринадцать производных таблиц: десять базовых
(спектр рождения 44 строки, мост 15×23, Пейдж 720/15/18, три лестницы,
константы, JSON-резюме C1) и три кампанные — субкритическая ветвь C2 (13
строк), бифуркационная ветвь C2 (13 строк), лестница разрешений C3b (12
строк, N=1600/3200). Кампанные таблицы переписываются из вердиктов дословно,
без пересчёта и перестановок; отсутствующий вердикт аккуратно пропускается,
чтобы `make data` работал и на частичной выгрузке. Источник чисел один —
четыре движковых вердикта в `campaigns/reference/` (все с project_version 2.1.0, физика байт-идентична);
пишет таблицы только `scripts/rebuild_data.py`, и перезапуск обязан быть
побайтно идентичным. Мусорные строки, флаг flipped и лестница массового пола
floor_M ≈ (13 ± 1)/N — первоклассные результаты; гамма-экспонента здесь заново не
подгоняется — измерение принадлежит кампании C3. Ручное редактирование запрещено: число меняется только через вердикт и повторную генерацию.
