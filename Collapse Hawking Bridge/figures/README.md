# figures

Committed figure set of the **Collapse-Hawking Bridge** — 28 PNG files:
7 figures × 2 languages (`en`, `ru`) × 2 themes (`light`, `dark`), rendered at
300 dpi through the shared "Ink & Gold" style module.

![v2.2.0](https://img.shields.io/badge/version-2.2.0-8C6D1F)
![figures](https://img.shields.io/badge/figures-28_PNG-gold)
![dpi](https://img.shields.io/badge/resolution-300_dpi-gold)
![style](https://img.shields.io/badge/style-Ink_%26_Gold-gold)

**TL;DR**

- Seven figures: Hawking thermodynamics, Page curves, scale ladder,
  born-spectrum scaling, engine validation, the bridge map, and — new —
  `fig_branches`: the two branches around the critical threshold
  (subcritical approach and supercritical bifurcation).
- Full parity across languages and themes: same geometry, translated labels,
  print and screen palettes.
- Every pixel is derived from committed verdicts and tables; the rendering
  script computes no new physics.
- One command regenerates all 28 files deterministically: `make figures`.
- The gold accent always marks the one point that matters — it is never decoration.

---

## Table of contents

- [Layout](#layout)
- [Catalog](#catalog)
- [The seven figures](#the-seven-figures)
- [Regeneration](#regeneration)
- [Ink & Gold style tokens](#ink--gold-style-tokens)
- [Language and theme policy](#language-and-theme-policy)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)
- [See also](#see-also)
- [Краткое резюме (Russian)](#краткое-резюме-russian)

## Layout

```text
figures/
├── en/
│   ├── light/
│   │   ├── fig_hawking.png      (~236 KB)
│   │   ├── fig_page.png         (~174 KB)
│   │   ├── fig_ladder.png       (~102 KB)
│   │   ├── fig_scaling.png      (~163 KB)
│   │   ├── fig_validation.png   (~154 KB)
│   │   ├── fig_map.png          (~172 KB)
│   │   └── fig_branches.png     (~200 KB)
│   └── dark/                    (same seven files)
└── ru/
    ├── light/                   (same seven files)
    └── dark/                    (same seven files)
```

28 files total, each roughly 100–240 KB (the folder is 4.9 MB).
`fig_hawking` and `fig_branches` are two-panel figures (11.5 × 5.0 in);
the other five are single-panel (8.0 × 5.2 in).

## Catalog

| Figure | What it shows | Data source |
|---|---|---|
| `fig_hawking` | Hawking temperature T_H(M) and Bekenstein–Hawking entropy S_BH(M), log–log, with the CMB contact point at 4.50e22 kg | closed-form relations in `chbridge/hawking.py`, mass grid 10¹⁰…10³³ kg |
| `fig_page` | radiation entropy S_rad/S_0 vs t/t_evap for the three ensemble members; gold dashed line at the Page time | [data/bridge/page_curve_grid.csv](../data/bridge/page_curve_grid.csv) |
| `fig_ladder` | the length scale ladder, 8 bars from l_P to the Hubble radius c/H0, log axis | [data/bridge/scale_ladder_length.csv](../data/bridge/scale_ladder_length.csv) |
| `fig_scaling` | born spectrum M_code(ε) at N=800 (sane rows); gold dashed anchor slope γ_Ch = 0.374; dotted fixed-grid floor guide at 1.55e-2 | [campaigns/reference/c1_verdict.json](../campaigns/reference/c1_verdict.json), `scan_N800` rows |
| `fig_validation` | engine regression: max\|r − r_exact\| vs grid N, with the slope −2 reference; convergence orders 2.03 / 2.09 annotated | `c1_verdict.json`, `validation` array |
| `fig_map` | the bridge schematic: collapse-engine box → thermodynamics box, gold arrow carrying M_BH = M_in · f̃(ε); Δ·γ and b_Ch-vs-γ annotations | none — schematic quoting committed constants |
| `fig_branches` | two panels around A*_800: subcritical q_max(ε) approaching the horizon compactness q = 1 (gold dashed); supercritical f̃(ε) with the gold vertical marker at ε_1/2 = 4.86e-3 and the dotted saturation line f̃ = 1 | [campaigns/reference/c2_verdict.json](../campaigns/reference/c2_verdict.json), `subcritical.rows` + `bifurcation.rows` (sane only) |

## The seven figures

**fig_hawking — Hawking thermodynamics vs mass.** Two log–log panels: T_H
against M (top) and S_BH/k_B against M (bottom). The CMB temperature 2.72548 K
is a dashed horizontal guide; the gold dot marks the contact point
T_H = T_CMB at M = 4.50e22 kg (about 0.61 lunar masses). The power laws
(T ~ 1/M, S ~ M²) are visible as straight lines; nothing is fitted.

**fig_page — Page curves of the born ensemble.** Radiation entropy normalized
by S_0 for the three members: near_floor (gold), mid (ink), saturated (muted).
Before the Page time S_rad = S_BH; after it S_rad = S_0 − S_BH. The gold
dashed vertical is the Page time (1 − 2^(−3/2))·t_evap ≈ 0.6464·t_evap, where
both branches meet at S_0/2.

**fig_ladder — Scale ladder (lengths).** Horizontal log-scale bars from the
Planck length l_P = 1.616e-35 m through the born-hole radii, the CMB-mass
Schwarzschild radius, the Earth-mass and solar radii, up to the Hubble radius
c/H0 = 1.367e26 m. A one-glance sanity sheet for the whole bridge.

**fig_scaling — Born spectrum and the critical anchor.** Black-hole code mass
M_code against the distance from threshold ε = A − A*, double logarithmic.
Filled ink markers: sane engine rows at N=800. Open markers: the
floor-saturated band. The gold dashed line is the literature anchor slope
γ_Ch = 0.374 drawn through the mid member; the dotted horizontal is the
fixed-grid mass floor at 1.55e-2. The figure shows the anchor for comparison —
the campaign verdict itself is that γ is honestly unmeasurable at fixed grid.

**fig_validation — Engine validation (Roberts–Oshiro).** The max norm of
r − r_exact against grid resolution N, on log–log axes. The gold dashed
reference has slope −2; the measured convergence orders 2.03 (N=200→400) and
2.09 (N=400→800) are annotated in gold. Errors: 4.686e-5 → 1.146e-5 → 2.687e-6.

**fig_map — The Collapse-Hawking Bridge.** Two panels-as-boxes: the critical
collapse engine (the F-1 remediation ladder A* = 0.10510 / 0.08820 /
0.080533 / 0.077744 / 0.076821 — the threshold drifts with resolution,
2.79e-3 over N800->N1600; the stale 1.06e-6 agreement claim is retracted —
born spectrum with the floor kept) and BH thermodynamics
(T_H ~ 1/M, S_BH ~ M², t_Page = 0.6464·t_evap, CMB contact, Page curve with the
Haar check). The gold arrow between them carries the single mapping
M_BH = M_in · f̃(ε). The footer quotes the two standing comparisons:
Δ·γ ≈ 1.27 (target, C3) and b_Ch = 0.37651 vs γ_Ch = 0.374 (0.67%).

**fig_branches — The two branches around the threshold.** Two panels fed by
campaign C2, both against the distance from the committed A*_800.
Left (subcritical branch, ε = A* − A): peak compactness q_max = max(2m/r) for
13 dispersing runs, none flipped; q_max rises from 0.0158 at ε = 6.3e-2 to
0.5845 at ε = 6.3e-5, visibly climbing toward the gold dashed horizon line
q = 1 it never crosses on this grid. Right (supercritical branch, ε = A − A*):
the born bifurcation f̃(ε) = M/M_sat as ink points — the 10 sane rows of the
13-row scan — on log–log axes; the gold vertical is the committed half-width
ε_1/2 = 4.8598e-03 where f̃ crosses 0.5, and the dotted horizontal marks
saturation f̃ = 1.

Provenance at a glance — which committed artifact each figure reads:

| Figure | Reads | Writes nothing |
|---|---|---|
| `fig_hawking` | `chbridge.hawking` closed forms | — |
| `fig_page` | `data/bridge/page_curve_grid.csv` | — |
| `fig_ladder` | `data/bridge/scale_ladder_length.csv` | — |
| `fig_scaling` | `campaigns/reference/c1_verdict.json` | — |
| `fig_validation` | `campaigns/reference/c1_verdict.json` | — |
| `fig_map` | committed constants only | — |
| `fig_branches` | `campaigns/reference/c2_verdict.json` | — |

## Regeneration

```console
$ make figures                              # = python3 scripts/make_figures.py --all
wrote figures/en/light/fig_hawking.png
wrote figures/en/light/fig_page.png
wrote figures/en/light/fig_ladder.png
wrote figures/en/light/fig_scaling.png
wrote figures/en/light/fig_validation.png
wrote figures/en/light/fig_map.png
wrote figures/en/light/fig_branches.png
wrote figures/en/dark/fig_hawking.png
...
wrote figures/ru/dark/fig_branches.png

28 figures written (7 x 2 lang x 2 theme)
```

Partial regeneration:

```console
$ python3 scripts/make_figures.py --lang en --theme dark
...
7 figures written (7 x 1 lang x 1 theme)

$ python3 scripts/make_figures.py --lang ru --theme light --dpi 600
```

| Flag | Values | Default |
|---|---|---|
| `--all` | — | off |
| `--lang` | `en`, `ru` | `en` |
| `--theme` | `light`, `dark` | `light` |
| `--dpi` | any integer | 300 |

Determinism: the script reads committed verdicts and committed tables and
calls closed-form functions only. Same inputs, same pixels (spot-checked:
PNGs md5-identical across a full regeneration). After a clean regeneration,
`git status figures/` must be silent; any diff means an input above this
folder changed.

## Ink & Gold style tokens

All figures are rendered through `scripts/figstyle.py`; there is no other
matplotlib styling anywhere in the repository.

| Token | Light (print) | Dark (screen) | Role |
|---|---|---|---|
| `bg` | `#FAF7F0` | `#10101A` | figure background |
| `panel` | `#FFFFFF` | `#171724` | axes panel |
| `ink` | `#1A1A24` | `#E8E2D0` | text, primary curves |
| `gold` | `#8C6D1F` | `#C9A84C` | THE point: contact, Page time, anchor, horizon, ε_1/2 |
| `gold_soft` | `#C9A84C` | `#E3C878` | secondary gold (bars, guides) |
| `muted` | `#6B6455` | `#8A8574` | de-emphasized series and guides |
| `grid` | `#D8D2C4` | `#2A2A3A` | gridlines, spines |
| `ok` | `#3A6B4F` | `#7FBF9A` | pass markers |
| `bad` | `#8C3A2F` | `#D97B6C` | fail markers |

The three style rules enforced by the module:

1. `constrained_layout` everywhere; no `tight_layout`, no `subplots_adjust`.
2. No gridline louder than 0.35 alpha; no chartjunk.
3. The gold accent marks the one point the figure exists to show — the CMB
   contact, the Page time, the anchor slope, the horizon q = 1, ε_1/2 —
   never decoration.

Supporting rcParams: DejaVu Sans with Noto Sans SC fallback, base font 11,
titles 13, axes facecolor = `panel`, saved facecolor = `bg`.

## Language and theme policy

- **EN default, RU full parity.** Both languages ship all seven figures in
  both themes; labels come from a single per-language dictionary in
  `figstyle.py`, so no figure can drift between languages.
- **Light for print, dark for screens.** The themes differ only in token
  values — geometry, data, and annotations are identical.
- Cyrillic rendering is safe: the font fallback chain includes Noto Sans SC
  for CJK-bearing environments, DejaVu Sans everywhere else.

## Honesty notes

- The rendering script "never computes new physics, only visualises committed
  results" — its own docstring. Every curve traces to a verdict or a table in
  [data/bridge/](../data/bridge/).
- `fig_branches` shows the two branch curves only. The slowdown fit
  (slope −0.0334), the echo accumulation rate (0.1909 /e-fold) and the v_qmax
  series live in `c2_verdict.json` and the ledger — they are deliberately not
  drawn.
- `fig_branches` (right panel) plots only the sane bifurcation rows: 3 junk
  rows with overflowing masses are excluded from the plot but kept in the
  verdict, exactly as committed.
- `fig_scaling` plots only rows flagged `sane`; junk rows are excluded by the
  same flag the tables carry, and the floor band is drawn with open markers
  rather than hidden.
- The anchor slope in `fig_scaling` and the footer constants in `fig_map` are
  comparisons against literature anchors, not fits. The figure set shows the
  γ anchor without claiming a measured γ.
- No figure is hand-touched after generation; if a figure is wrong, the fix
  belongs in the inputs or in `make_figures.py`.

## FAQ

**Why no SVG?**
PNG is committed for stability: the rendered repository is reproducible and
diffable without a browser or a rasterizer, and matplotlib's PNG output is
byte-stable across regeneration. `make_figures.py` can be extended to other
formats if a use case appears.

**Why 300 dpi?**
Print-ready at typical column widths, yet repo-friendly: each file stays in
the 100–240 KB range, so the 28-file set costs about 5 MB, not tens.

**Where do axis labels come from?**
From the per-language dictionaries in `scripts/figstyle.py` (`LANG["en"]`,
`LANG["ru"]`). Adding a language means adding one dictionary, not touching
seven plot functions.

**Why does `fig_scaling` show two marker styles?**
Filled ink markers are sane engine points; open markers mark the
floor-saturated band where the fixed grid, not the physics, sets the mass.

**Can I add an eighth figure?**
Yes, via [CONTRIBUTING.md](../CONTRIBUTING.md): write a function taking the
token dict and the language dict, register it in the `FIGS` map of
`scripts/make_figures.py`, and all four language-theme variants are generated
automatically. The figure must read committed inputs only.

## See also

- [figstyle.py](../scripts/figstyle.py) — the token source of truth
- [make_figures.py](../scripts/make_figures.py) — the only writer of this folder
- [rebuild_data.py](../scripts/rebuild_data.py) — writes the tables two figures read
- [data/README.md](../data/README.md) — the tables behind `fig_page` and `fig_ladder`
- [campaigns/run_c1.py](../campaigns/run_c1.py) — producer of the verdicts behind three figures
- [campaigns/run_c2.py](../campaigns/run_c2.py) — producer of `c2_verdict.json` behind `fig_branches`
- [results/RESULTS.md](../results/RESULTS.md) — the numbers each figure visualizes

## Краткое резюме (Russian)

Папка `figures/` содержит 28 PNG-файлов: семь рисунков в двух языках (en, ru)
и двух темах (light, dark), рендер 300 dpi. Набор: термодинамика Хокинга
с точкой контакта с реликтовым излучением, кривые Пейджа трёх членов
ансамбля, лестница масштабов длин, спектр рождения с якорным наклоном
γ_Ch = 0.374, валидация движка на точном решении (порядок ≈ 2), схема моста
и новый двухпанельный `fig_branches` — докритическая ветвь q_max(ε),
поднимающаяся к линии горизонта q = 1, и сверхкритическая бифуркация f̃(ε)
с золотой отметкой ε_1/2 = 4.86e-3. Все рисунки строятся через единый стиль
«Ink & Gold» (модуль `figstyle.py`): приглушённая тушь, один золотой акцент
на смысловой точке рисунка, никаких излишеств. Данные — только из
зафиксированных вердиктов и таблиц; скрипт новой физики не считает.
Перегенерация одной командой `make figures` детерминирована; вручную
рисунки не редактируются.
