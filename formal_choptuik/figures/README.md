<p align="center">
  <img src="../assets/banners/banner_data.svg" alt="figures" width="100%">
</p>

# figures/ — publication-grade, 300 dpi, theme-aware

![format](https://img.shields.io/badge/format-PNG·300dpi-4CC9F0?style=flat-square)
![themes](https://img.shields.io/badge/themes-dark_cosmic·light_inkgold-8A8272?style=flat-square)
![source](https://img.shields.io/badge/source-data/*.csv-E8B44A?style=flat-square)
![generator](https://img.shields.io/badge/regenerate-python_scripts-9B8CDE?style=flat-square)

Every figure is rendered from the committed CSVs in [`data/`](../data/) —
no screenshot folklore, no hand-tuned points.  The dark set below is the
GitHub rendition; the monographs embed light **Ink & Gold** versions
(Russian editions: Russian labels) produced by the same script.

## Catalogue

| Figure | Shows | Data source |
|---|---|---|
| [`fig_mass_scaling_law.png`](fig_mass_scaling_law.png) | ln–ln scaling of M_BH over 24 supercritical runs; γ_fit = 0.3739 vs Choptuik's 0.374 | `scaling/mass_scaling.csv` |
| [`fig_echoing_profile.png`](fig_echoing_profile.png) | DSS echo: rescaled profile coincidence + periodic central amplitude, Δ = ln 2 | `echoing/*.csv` |
| [`fig_spectrum_eigenvalues.png`](fig_spectrum_eigenvalues.png) | linearized spectrum: one unstable λ₀, decay family, spacing 2π/Δ ≈ 9.06 | `spectrum/eigenvalues.csv` |
| [`fig_collapse_profiles.png`](fig_collapse_profiles.png) | subcritical / critical / supercritical field evolutions | `collapse/field_profiles.csv` |
| [`fig_gap_severity_matrix.png`](fig_gap_severity_matrix.png) | G1–G6 × severity / effort / dependency | `blueprint/gap_registry.csv` |
| [`fig_roadmap_gantt.png`](fig_roadmap_gantt.png) | 14 tasks across the 27-month plan, milestones at 6/18/27 | `roadmap/milestones.csv` |
| [`fig_tooling_radar.png`](fig_tooling_radar.png) | Lean vs Coq vs Isabelle on six programme axes | tooling decision record |
| [`fig_architecture.png`](fig_architecture.png) | the four-layer Lean⇄ZeroMQ⇄Python⇄artifacts system | `bridge/protocol.md` |

## Regenerate

```bash
cd ../python
python scripts/generate_figures.py                                  # dark EN -> figures/
python scripts/generate_figures.py --theme light --lang en --out B   # EN monographs
python scripts/generate_figures.py --theme light --lang ru --out B   # RU monographs
python scripts/generate_architecture.py                             # 3 variants at once
```

<p align="center">
  <img src="../assets/banners/divider_wave.svg" alt="" width="100%">
</p>
