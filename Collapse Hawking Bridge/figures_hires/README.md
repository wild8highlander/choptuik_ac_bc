# figures_hires/ — the 600 dpi suite

Version 2.0.0 · 68 PNG · 17 figure types × 2 languages × 2 themes

---

## Purpose

The standard suite (`../figures/`) ships 300 dpi figures — ideal for
screens and the web companion. This directory is the **print
architecture**: every measurement architecture of every committed
campaign gets its own ultra-high-resolution figure at **600 dpi**
(4440 × 2880 px for single panels, ~6600 × 4560 for the two 2×2
landscapes), suitable for journal submission, posters and zoom-in
inspection without pixelation.

One figure = one measurement architecture. The mapping is explicit:

| file | architecture | campaign | what is measured |
|------|--------------|----------|------------------|
| `hq_01_a_star_ladder` | bisection search | C1 | A*(N) ladder at N=200/400/800/1600/3200 (F-1 remediation): the threshold DRIFTS with resolution — the stale 1.06e-6 agreement band is retracted |
| `hq_02_amplitude_scan_N400` | fixed-N amplitude scan | C1 | M_code(ε), 26 runs, junk kept |
| `hq_03_amplitude_scan_N800` | fixed-N amplitude scan | C1 | M_code(ε), 18 runs, floor band |
| `hq_04_scan_compare` | cross-resolution audit | C1 | N400 vs N800 overlay; the floor, not the engine, saturates the far band |
| `hq_05_born_spectrum` | spectrum assembly | C1 | full born spectrum + anchor slope γ_Ch = 0.374 + floor line |
| `hq_06_subcritical_qmax` | dispersal diagnostics | C2-sub | q_max(ε) monotone 0.0158 → 0.5845, horizon line q = 1 |
| `hq_07_critical_slowdown` | time-series sampling | C2-sub | v_qmax vs ln ε, fit b = −0.0334, r² = 0.71, 40-snapshot quantization |
| `hq_08_echo_accumulation` | peak counting | C2-sub | n_peaks vs ln(1/ε): 0.1909/e-fold vs anchor 1/Δ = 0.2907 |
| `hq_09_compactness_decay` | endpoint diagnostic | C2-sub | q_final/q_max along the branch |
| `hq_10_born_bifurcation` | bifurcation scan | C2-sup | f~(ε), ε½ = 4.86e-3, junk rows marked |
| `hq_11_bifurcation_slope` | derivative measurement | C2-sup | local d ln f~/d ln ε on committed rows |
| `hq_12_dgamma_anchor` | anchor comparison | C3 | Δ·γ = 1.28656 vs target 1.27 ± 0.05 — PASS 1.3% |
| `hq_13_floor_law` | resolution ladder | C1+C3b | floor_M ≈ (13 ± 1)/N at N = 800/1600/3200 (per-grid F-2 floors, read from the verdict) |
| `hq_14_gamma_eff_convergence` | concentrated resolution | C3b | γ_eff 0.0410 → 0.0605 (per-grid F-2, floor-dominated) vs anchor 0.374 — honest negative |
| `hq_15_thermo_landscape` | bridge mapping | all | T_H, S_BH, t_evap, P_H over 5 input scales × 3 members |
| `hq_16_page_detail` | Page model + Haar audit | bridge | Page curves, τ* = 1 − 2^(−3/2), Haar max dev 0.0042 bits |
| `hq_17_ro_validation` | engine self-test | C1 | Roberts–Oshiro error vs N, orders 2.03/2.09, slope −2 guide |

## Layout

```
figures_hires/
├── en/
│   ├── light/   17 PNG (print, cream background)
│   └── dark/    17 PNG (screens, ink background)
├── ru/
│   ├── light/   17 PNG
│   └── dark/    17 PNG
└── README.md    (this file)
```

File naming is stable across languages and themes — only the directory
changes. This lets documents reference `figures_hires/en/light/hq_12_dgamma_anchor.png`
and switch language/theme by path prefix alone.

## Ink & Gold identity

All figures pass through `../scripts/figstyle.py` (the same module as
the 300 dpi suite): one gold accent `#8C6D1F` (light) / `#C9A84C`
(dark) marks THE point of each figure — the contact point, the Page
time, the anchor line, the tolerance band. Near-monochrome ink for
everything else. No chartjunk, no decorative color, gridlines at
α = 0.35. The palette is documented token-by-token in the parent
`../figures/README.md`.

## Regeneration

```bash
python3 scripts/hires_figures.py --all                    # 68 files, ~25 s
python3 scripts/hires_figures.py --lang en --theme dark   # one slice
python3 scripts/hires_figures.py --lang ru --dpi 300      # fast preview
```

Expected console tail: `68 hires figures written (17 x 2 lang x 2 theme @ 600 dpi)`.
The script never computes new physics — every number is read from the
committed verdicts (`../campaigns/reference/`) and derived tables
(`../data/bridge/`). Re-running is byte-stable up to PNG metadata
timestamps.

## Sizing guidance for downstream use

| use | theme | dpi | file size band |
|-----|-------|-----|----------------|
| journal figure (single column ~3.5 in) | light | 600 (as-is) | 250–450 KB |
| poster A2 full-width | light | 600 (as-is) | 250–700 KB |
| dark-mode web | dark | 600 (as-is, downscale in CSS) | 250–600 KB |
| slide deck | either | 300 is sufficient → use `../figures/` | 100–240 KB |

## Honesty notes

1. `hq_11_bifurcation_slope` shows a *numerical derivative* of committed
   f~ rows (numpy.gradient on log-log coordinates) — it is a view of the
   data, not a new measurement.
2. `hq_12_dgamma_anchor` draws the *anchor-level* product Δ_lit·γ_Ch =
   1.28656 (C3 PASS). The engine-level measurement remains an honest
   negative (γ unmeasurable on the reachable band) — see `hq_14`.
3. `hq_13_floor_law` overlays the 12/N guide as a *fit summary* of the
   three per-grid committed floors (F-2 values, read from the verdict),
   with 9.6/N and 14.4/N as a visual envelope; the envelope is a guide,
   not a confidence interval.
4. `hq_15_thermo_landscape` plots the 15 mapped (scale, member) rows of
   `bridge_master.csv` per panel; the dashed line in the T_H panel is
   T_CMB = 2.72548 K (contact reference).
5. Junk rows appear in `hq_02`, `hq_03`, `hq_10` as red × markers — kept
   verbatim, flagged, never dropped (the package's honesty discipline).

## FAQ

**Q: Why 600 dpi and not vector PDF/SVG?** The whole figure suite is
raster by design decision (byte-stability across matplotlib versions,
no font-embedding drift between machines). At 600 dpi a single-panel
PNG has 4440 px of width — beyond what any A4 print needs; at that
density raster artifacts are invisible.

**Q: Why is dark theme also 600 dpi?** Uniformity costs ~11 MB total
here and lets dark-mode documents (and the web companion's dark
section) reference the same numbering scheme without a second
pipeline.

**Q: Can I get a figure that is not in the 17?** The catalog mirrors
the *measurement architectures*, not every possible view. If a new
architecture enters via a new campaign (C4 ringdown, C5 second
family), its figures are added here with the next `hq_` number.

**Q: Do the hires figures re-derive anything?** No. `hires_figures.py`
imports the same committed verdicts as the 300 dpi suite and the test
pins of `../tests/test_campaigns.py`. Nothing in this directory can
drift from the verdicts without a test failing.

**Q: Which figures belong to which theorem?** hq_01/hq_17 → T4
(second-order convergence); hq_05 → T3 (spectrum + anchor); hq_06 →
T7 (subcritical monotonicity); hq_07 → T7 (slowdown law); hq_08 → T8
(echo bound); hq_10 → T1 of campaign results (bifurcation); hq_12 →
T6 (Δ·γ); hq_13 → T5 (floor law); hq_16 → T1/T2 (Page fraction, Haar);
see `../monograph/` for the formal statements.

## Краткое резюме (RU)

Каталог `figures_hires/` — печатная (600 dpi, 4440×2880) версия
визуального каталога: 17 типов графиков × 2 языка × 2 темы = 68 PNG
(23 МБ). Один график — одна измерительная архитектура кампаний C1,
C2 (обе ветви), C3, C3b: лестница бисекции A*, сканирования амплитуды
N=400/800, дисперсная диагностика q_max, критическое замедление,
эхо-пики, бифуркация f~ с ε½, якорное произведение Δ·γ, закон пола
(13±1)/N, γ_eff по сеткам F-2 на концентрированных сетках, термоландшафт, кривые Пейджа
и валидация Робертса–Оширо. Регенерация: `python3 scripts/hires_figures.py --all`.
Все числа взяты из зафиксированных вердиктов; мусорные строки помечены,
но сохранены; честные негативы визуализируются как негативы.
