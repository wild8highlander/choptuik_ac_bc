# scripts

Deterministic tooling of the **Collapse-Hawking Bridge**: these scripts
derive every data table from committed campaign verdicts and render every
figure from them. They invent no physics.

![version](https://img.shields.io/badge/version-2.1.0-8C6D1F)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![tests](https://img.shields.io/badge/pytest-63_passed-brightgreen)
![validate](https://img.shields.io/badge/validate-7%2F7_PASS-brightgreen)
![figures](https://img.shields.io/badge/figures-28_PNG_+68_hires+logo-gold)
![status](https://img.shields.io/badge/status-v2.1.0-blue)

## TL;DR

- `rebuild_data.py` runs five stages — bridge, page and ladder tables,
  campaign tables (three `campaign_*.csv` files copying verdict rows
  verbatim), and a consistency spot-check — filling `data/bridge/` with
  13 tables; a rerun is byte-identical (pinned by
  `tests/test_bridge.py::test_rebuild_determinism`).
- `make_figures.py` renders 28 PNGs: 7 figures x {en, ru} x {light, dark},
  300 dpi; the two-panel `fig_branches` draws the branches around the
  threshold from `c2_verdict.json`.
- `figstyle.py` is the single source of visual style: the "Ink & Gold"
  tokens, EN/RU label dictionaries (28 identical keys each, including the
  nine `branch_*` keys), layout and save helpers.
- `hires_figures.py` renders 68 PNGs @ 600 dpi (17 architectures ×
  RU/EN × light/dark) — verdict-driven; `--figs` regenerates a selection.
- `make_animations.py` renders the 8 launch animations (MP4 h264 + GIF).
- `make_logo.py` draws the package logo (light/dark, PNG 600 dpi + SVG)
  from pure matplotlib geometry — deterministic, no external assets.
- `make_c6_figures.py` renders the T10 report figures (drift ladder +
  the two lemmas) into `results/scaling_drift/figures/`.
- `build_workbook.py` assembles the 14-sheet Excel workbook
  (optional `workbook` extra: openpyxl).
- Provenance is one-directional: verdicts -> tables -> figures/results;
  a script never computes new physics.

## Contents

1. [The provenance principle](#the-provenance-principle)
2. [Catalog](#catalog)
3. [rebuild_data.py](#rebuild_datapy)
4. [make_figures.py](#make_figurespy)
5. [figstyle.py](#figstylepy)
6. [Runbook (copy-paste)](#runbook-copy-paste)
7. [Determinism](#determinism)
8. [Honesty notes](#honesty-notes)
9. [FAQ](#faq)
10. [See also](#see-also)
11. [Краткое резюме (Russian)](#краткое-резюме-russian)

---

## The provenance principle

Every number in the repository flows in one direction. The scripts sit
in the middle of the chain and are deliberately unable to close it:

```
campaigns/run_c1.py  ->  campaigns/reference/c1_verdict.json
campaigns/run_c2.py  ->  campaigns/reference/c2_verdict.json
campaigns/run_c3.py  ->  campaigns/reference/c3_verdict.json
campaigns/run_c3b.py ->  campaigns/reference/c3b_verdict.json
                                |
                                v   rebuild_data.py ([1/5]-[3/5] recomputed,
                                |   [4/5] verbatim copy)
chbridge.bridge / page / ladder  ->  data/bridge/*.csv, *_summary.json
                                |
                                v   make_figures.py (visualisation only)
data/bridge/*.csv  ->  figures/<lang>/<theme>/fig_*.png, results/RESULTS.md
```

Consequences:

- the verdict JSON files are the only physics source the scripts read;
- a table edited by hand is not a table (it will be overwritten, and the
  tests will fail on the mismatch); the campaign stage recomputes
  nothing: the CSV cells are the JSON cells;
- figure code may compute plot coordinates (log grids, anchor lines),
  never new physical claims.

## Catalog

| file | role | reads | writes | typical run |
|---|---|---|---|---|
| `rebuild_data.py` | derives all 13 data tables from the committed verdicts | `campaigns/reference/c1_verdict.json` (required), `c2_verdict.json` / `c3b_verdict.json` (stages 4-5), `chbridge.{bridge,page,ladder}` | 13 files in `data/bridge/` | ~2 s |
| `make_figures.py` | renders the complete figure set | `campaigns/reference/*`, `data/bridge/*`, `figstyle` | 28 PNGs in `figures/` | ~15 s (`--all`) |
| `figstyle.py` | shared style module (tokens, labels, layout) | `matplotlib` | nothing (rcParams in memory) | not run directly |

The campaign runners `run_c2.py` and `run_c3b.py` live in `campaigns/`,
next to `run_c1.py` and `run_c3.py`: they own the physics; the scripts
here only consume the committed verdicts.

---

## rebuild_data.py

### Purpose

Recompute every derived table in `data/bridge/` in one pass, in five
stages: `[1/5]` bridge, `[2/5]` page, `[3/5]` ladder, `[4/5]` campaign
tables (verdict rows committed verbatim), `[5/5]` a consistency spot-check
reprinting the committed C2/C3b numbers. Deterministic: rerunning on the
same verdicts must be a no-op. Run: `python3 scripts/rebuild_data.py`
(or `make data`).

### Inputs

- `campaigns/reference/c1_verdict.json` — required (scan rows, A* ladder,
  honest notes); stages [1/5]-[3/5] recompute from it float-exactly;
- `campaigns/reference/c2_verdict.json`, `c3b_verdict.json` — read by
  stages [4/5] and [5/5]; a missing verdict is skipped with a note, so
  `make data` works on partial checkouts;
- `chbridge.bridge`, `chbridge.page`, `chbridge.ladder` — the writers
  that turn verdicts plus closed-form constants into tables.

### Outputs (13 files)

| stage | file | shape |
|---|---|---|
| 1/5 | `born_spectrum.csv` | 44 rows (26 N=400 + 18 N=800) |
| 1/5 | `bridge_master.csv` | 15 rows x 23 columns |
| 1/5 | `collapse_verdict_summary.json` | C1-derived summary dict |
| 2/5 | `page_curve_grid.csv` | 720 rows |
| 2/5 | `page_members.csv` | 15 rows |
| 2/5 | `page_haar_check.csv` | 18 rows |
| 3/5 | `scale_ladder_accel.csv` | 7 rows |
| 3/5 | `scale_ladder_length.csv` | 8 rows |
| 3/5 | `scale_ladder_curvature.csv` | 5 rows |
| 3/5 | `bridge_constants.csv` | 8 rows |
| 4/5 | `campaign_c2_subcritical.csv` | 13 rows, verbatim `c2_verdict` `subcritical.rows` |
| 4/5 | `campaign_c2_bifurcation.csv` | 13 rows, verbatim `c2_verdict` `bifurcation.rows` |
| 4/5 | `campaign_c3b_ladder.csv` | 12 rows (7 @ N=1600 + 5 @ N=3200), verbatim `c3b_verdict` `gamma_ladder` |

### Expected console output (captured verbatim)

```text
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

all outputs -> <repo>/data/bridge
```

### Invariants

- **Determinism.** No wall-clock, no network, no unseeded randomness. The
  only Monte Carlo step (Page Haar check) runs with `rng(20260101)` and
  fixed sample counts 3000/1200, so its output is fixed too.
- **The verbatim rule.** Stage [4/5] copies, it does not compute — no
  recomputation, no rounding, no reordering; the CSV cells are the JSON
  cells. A missing verdict is skipped with a note instead of an error
  (`skipped: c2_verdict.json not found — run its campaign first`).
- **No-op guarantee + verdicts stay in JSON.** Rerunning on unchanged
  verdicts rewrites the same bytes (md5-verified over all 13 files in the
  runbook; pinned by `tests/test_bridge.py::test_rebuild_determinism`),
  and the script writes `data/bridge/` only, never `campaigns/reference/`.

---

## make_figures.py

### Purpose

Regenerate every figure of the project from committed artifacts: seven
figures x two languages (en, ru) x two themes (light, dark) = 28 PNG
files, 300 dpi, under `figures/<lang>/<theme>/`.

### Usage

```bash
python3 scripts/make_figures.py --all                    # all 28
python3 scripts/make_figures.py --lang en --theme dark   # one slice (7 PNGs)
python3 scripts/make_figures.py --dpi 200                # custom resolution
# or: make figures; flags: --lang en|ru (en), --theme light|dark (light), --dpi int (300)
```

### Figure catalog

| figure | shows | data source |
|---|---|---|
| `fig_hawking` | T_H and S_BH vs mass; CMB contact at 4.50e22 kg | computed from `chbridge.hawking` (two panels) |
| `fig_page` | Page curves of the three ensemble members; Page time marker | `data/bridge/page_curve_grid.csv` |
| `fig_ladder` | scale ladder (lengths), horizontal log bars | `data/bridge/scale_ladder_length.csv` |
| `fig_scaling` | born spectrum M(eps); anchor slope gamma_Ch = 0.374; floor | `c1_verdict.json` `scan_N800` |
| `fig_validation` | Roberts-Oshiro convergence, err vs N, slope -2 | `c1_verdict.json` `validation` |
| `fig_map` | the bridge map: engine -> f~ -> thermodynamics | committed constants (static text) |
| `fig_branches` | two panels: subcritical q_max(eps) approaching the horizon compactness q = 1 (gold dashed); supercritical f~(eps) with the gold eps_half = 4.86e-3 marker and the dotted saturation line f~ = 1 | `c2_verdict.json` `subcritical.rows` + `bifurcation.rows` (sane only) |

### Expected console output

One `wrote` line per PNG, `fig_branches` last within each slice:

```text
wrote figures/en/light/fig_hawking.png
...                                      (one line per PNG)
wrote figures/ru/dark/fig_branches.png

28 figures written (7 x 2 lang x 2 theme)
```

### Invariants

- **No new physics.** The script reads verdicts and tables; the only
  quantities it evaluates are plot grids (e.g. a log-spaced mass axis)
  and the anchor line at gamma_Ch = 0.374.
- **Style always through `figstyle`.** Every figure is created with
  `figstyle.style(theme)`, `figstyle.new_fig()` and saved with
  `figstyle.finish(fig, path, dpi)`; EN and RU label sets live in
  `figstyle.LANG`, and both languages ship both themes.

---

## figstyle.py

### Purpose

The visual identity of the figure set: "Ink & Gold" — one accent gold on
near-monochrome ink backgrounds, two themes (light for print, dark for
screens), two languages. Every figure passes through this module, which
keeps the 28 PNGs visually coherent. `LANG["en"]` and `LANG["ru"]` each
define 28 label keys (identical key sets, verified programmatically),
including the nine `branch_*` keys of `fig_branches`: `branch_sub_title`,
`branch_sub_y`, `branch_sub_x`, `branch_horizon`, `branch_bif_title`,
`branch_bif_y`, `branch_bif_x`, `branch_eps_half`, `branch_sat`.

### Token table

| token | light | dark | role |
|---|---|---|---|
| `bg` | `#FAF7F0` | `#10101A` | figure background |
| `panel` | `#FFFFFF` | `#171724` | axes panel |
| `ink` | `#1A1A24` | `#E8E2D0` | text, curves |
| `gold` | `#8C6D1F` | `#C9A84C` | THE accent (contact point, Page time, anchor line, horizon q = 1, eps_half) |
| `gold_soft` | `#C9A84C` | `#E3C878` | secondary accent (bars, guides) |
| `muted` | `#6B6455` | `#8A8574` | reference lines, de-emphasis |
| `grid` | `#D8D2C4` | `#2A2A3A` | gridlines (alpha 0.35) |
| `ok` / `bad` | `#3A6B4F` / `#8C3A2F` | `#7FBF9A` / `#D97B6C` | pass/fail markers |

### API

| call | returns | does |
|---|---|---|
| `style(theme="light")` | token dict | applies the theme rcParams (fonts, colors, sizes) |
| `new_fig(w=8.0, h=5.2)` | figure | constrained-layout figure — the only layout engine used |
| `finish(fig, path, dpi=300)` | — | saves the PNG, closes the figure |

### Style rules

1. `constrained_layout` everywhere; no `tight_layout`, no
   `subplots_adjust`.
2. No gridline louder than alpha 0.35; no chartjunk.
3. The gold accent marks the one point of the figure — never decoration.

---

## Runbook (copy-paste)

All commands below assume the repository root as the working directory.
Expected outputs were captured live on the reference machine (updated at v2.1.0).

```bash
# 0. environment (editable install of chbridge)
make install
```

```bash
# 1. derive all 13 data tables from the committed verdicts
python3 scripts/rebuild_data.py
# -> the [1/5]..[5/5] block above, then "all outputs -> .../data/bridge"  (~2 s)
```

```bash
# 2. prove determinism: rerun must rewrite identical bytes
md5sum data/bridge/* > /tmp/before.md5 && python3 scripts/rebuild_data.py \
  && md5sum -c /tmp/before.md5
# -> 13 lines "…: OK", nothing modified
```

```bash
# 3. regenerate the full figure set (or one slice: --lang en --theme dark
#    -> 7 lines + "7 figures written (7 x 1 lang x 1 theme)")
python3 scripts/make_figures.py --all
# -> 28 "wrote figures/..." lines + "28 figures written (7 x 2 lang x 2 theme)"  (~15 s)
```

```bash
# 4. 50-digit re-verification of every constant
python3 -m chbridge.validate
# -> 7 PASS rows, then "7/7 checks PASS (mpmath dps=50, chbridge v2.1.0)"

# 5. the test suite
python3 -m pytest tests/
# -> "63 passed" in ~1 s
```

```bash
# 7. optional — refresh the law itself, then rebuild the tables.
#    Campaigns live in campaigns/ and OVERWRITE their verdicts.
python3 campaigns/run_c1.py        # ~2-4 min; committed wall: 48.4 s / 45 runs
python3 campaigns/run_c2.py        # ~1 min;    committed wall: 23.7 s / 26 runs
python3 campaigns/run_c3b.py       # ~2 min;    committed wall: 96.8 s
python3 campaigns/run_c3.py        # ~1-2 min;  committed wall: 13.6 s / 31 runs
python3 scripts/rebuild_data.py    # then re-derive the tables (step 1)
```

## Determinism

- `rebuild_data.py`: float-exact recomputation from the verdicts (stages
  1-3) plus verbatim copies (stage 4); seeded RNG only (`20260101`);
  md5-stable across runs — 13/13 files checked above, pinned by
  `test_rebuild_determinism`.
- `make_figures.py`: byte-identical for the same matplotlib version and
  dpi (spot-checked: two PNGs md5-identical across a full `--all`
  regeneration); the committed 28 PNGs used the flags above.
- Wall-clock appears nowhere in script output; the only wall times live
  inside the verdict JSONs (`wall_total_s`) as run metadata, never as
  physics.

## Honesty notes

- The scripts do not validate physics; they transport it. Validation
  lives in `chbridge.validate` (7/7 at 50 digits) and `tests/`.
- The `[5/5]` spot-check reprints committed summary numbers (slowdown
  slope -0.0334, echo rate 0.1909 /e-fold, M_sat 0.03519, eps_half
  4.8598e-03, gamma_eff per grid, P_anchor 1.28656) — for eyeballing
  only; it derives nothing and re-fits nothing.
- `P_engine_deep` prints as `None`: an honest negative (the deep-grid
  echo detector still resolves fewer than three peaks per run).
- `fig_map` carries static text (A* ladder, CMB contact, b_Ch vs gamma_Ch)
  mirroring committed values; a verdict change means regenerating it — and
  updating the static strings — deliberately, by hand.
- `fig_branches` draws the two branch curves only; the slowdown fit, the
  echo rate and the v_qmax series stay in `c2_verdict.json` and the
  ledger, never on canvas. Runtimes (~2 s, ~15 s, ~1 s) were measured on
  the reference machine; absolute seconds vary, ordering does not.
- Test count: the suite defines 60 tests across 7 files;
  `tests/test_campaigns.py` pins the committed C2/C3b verdict numbers and
  the campaign CSV copies. `pytest --collect-only` is authoritative.

## FAQ

**Can I add a script here?**
See `../CONTRIBUTING.md`: read committed verdicts only, write derived
artifacts, stay deterministic, and pin every emitted number with a test.

**Why do figures read CSVs instead of recomputing from the engine?**
Provenance. One direction, no circularity: engine -> verdict -> tables ->
figures; the same tables back the figures, the tests and the ledger, so a
discrepancy is impossible by construction.

**Can I edit the CSVs in `data/bridge/` by hand?**
No — they are derived artifacts, including the three `campaign_*.csv`
files (verbatim copies of verdict rows). Change the verdict, then
rebuild; the tables follow.

**Why is `figstyle.py` a separate module?**
One style source for 28 PNGs: tokens, fonts, EN/RU labels and the save
path live in one place, so themes and languages cannot drift apart.

**Does `rebuild_data.py` require running the campaigns first?**
No — the committed verdicts ship with the repository. If a C2/C3b verdict
is missing, stage [4/5] prints the skip note and the remaining stages
still rebuild. Rerun a campaign only to refresh the law itself.

## See also

- [RESULTS.md — the living ledger](../results/RESULTS.md)
- [campaigns — the runners behind the verdicts](../campaigns/README.md), incl. [`run_c2.py`](../campaigns/run_c2.py) / [`run_c3b.py`](../campaigns/run_c3b.py)
- [data tables and the column dictionary](../data/README.md) · [figure catalog and style policy](../figures/README.md) · [test suite inventory](../tests/README.md)
- [methods](../docs/methods.md) and [validation](../docs/validation.md) — engine, campaigns, what holds
- [CONTRIBUTING — how to extend the project](../CONTRIBUTING.md) · [root README](../README.md)

## Краткое резюме (Russian)

Папка `scripts/` содержит три инструмента, воспроизводящих весь числовой
и графический материал проекта. `rebuild_data.py` проходит пять стадий
([1/5]..[5/5]) и наполняет `data/bridge/` тринадцатью таблицами: десять
пересчитываются из вердиктов с точностью до бита, три (`campaign_*.csv`)
копируются дословно из вердиктов C2/C3b; повторный запуск побайтово
идентичен (md5-проверка, тест-закрепление). Стадия [5/5] перепечатывает
зафиксированные числа C2/C3b — только для сверки. `make_figures.py`
строит 28 рисунков — 7 сюжетов, включая двухпанельный `fig_branches`
(докритическая ветвь q_max(eps) и сверхкритическая бифуркация f~(eps)),
— языки en/ru, темы light/dark, 300 dpi — строго из вердиктов и таблиц.
`figstyle.py` задает стиль «Ink & Gold»: один золотой акцент на смысловой
точке, две темы, два языка, словари по 28 меток, только constrained_layout.
Скрипты не создают физику: они пересчитывают зафиксированные результаты и
визуализируют их. Проверка констант — `python3 -m chbridge.validate`
(7/7 PASS).
