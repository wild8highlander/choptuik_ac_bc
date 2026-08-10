# Choptuik–QCD Bridge — Enhanced Verification Suite

**Author**: Ishak Khamzatovich Isaev
**ORCID**: [0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701)
**Repository**: [wild8highlander/choptuik_ac_bc](https://github.com/wild8highlander/choptuik_ac_bc)
**Date**: August 2026

This package contains the enhanced QCD bridge verification suite for the monograph
*"The Choptuik-Strong CP Operator: A Spectral Bridge from Numerical Relativity to
QCD Topological Sectors"* by Ishak Khamzatovich Isaev.

## What's in this package

```
choptuik_ac_bc/
├── README.md                          ← this file
├── monograph/
│   ├── choptyuk_qcd_bridge_en.docx    ← English monograph (22 MB, 11 sections, 18 embedded figures)
│   └── choptyuk_qcd_bridge_ru.docx    ← Russian monograph (22 MB, full translation)
├── qcd_bridge/
│   ├── figures/                       ← 54 figures (18 PNG @ 600 DPI + 18 PDF + 18 SVG)
│   │   ├── fig_s1_ochi_eigvals_3d.{png,pdf,svg}      Section 1: O_chi eigenvalues (3D)
│   │   ├── fig_s1_ochi_matrix_4d.{png,pdf,svg}        Section 1: O_chi matrix (4D)
│   │   ├── fig_s2_rmt_sweep_3d.{png,pdf,svg}          Section 2: RMT sweep (3D)
│   │   ├── fig_s2_rmt_sweep_4d.{png,pdf,svg}          Section 2: BF surface (4D)
│   │   ├── fig_s3_staircase_3d.{png,pdf,svg}          Section 3: Spectral staircase (3D)
│   │   ├── fig_s3_staircase_4d.{png,pdf,svg}          Section 3: Folded spacings (4D)
│   │   ├── fig_s4_N_scaling_3d.{png,pdf,svg}          Section 4: N-scaling (3D)
│   │   ├── fig_s4_N_scaling_4d.{png,pdf,svg}          Section 4: N-scaling surface (4D)
│   │   ├── fig_s5_tau_relax_3d.{png,pdf,svg}          Section 5: tau_relax (3D)
│   │   ├── fig_s5_tau_relax_4d.{png,pdf,svg}          Section 5: Phase portrait (4D)
│   │   ├── fig_s6_kappa_T_3d.{png,pdf,svg}            Section 6: kappa_T posterior (3D)
│   │   ├── fig_s6_kappa_T_4d.{png,pdf,svg}            Section 6: Lattice density (4D)
│   │   ├── fig_s7_cabibbo_3d.{png,pdf,svg}            Section 7: Cabibbo angles (3D)
│   │   ├── fig_s7_cabibbo_4d.{png,pdf,svg}            Section 7: Cabibbo sweep (4D)
│   │   ├── fig_s8_cp_chain_3d.{png,pdf,svg}           Section 8: CP chain (3D)
│   │   ├── fig_s8_cp_chain_4d.{png,pdf,svg}           Section 8: CP dependency (4D)
│   │   ├── fig_s9_jet_wake_3d.{png,pdf,svg}           Section 9: Jet wake (3D)
│   │   ├── fig_s9_jet_wake_4d.{png,pdf,svg}           Section 9: Wake field (4D)
│   │   └── figures_manifest.json
│   ├── configs/
│   │   ├── verify_all.json            ← Full verification (all 9 sections, reference parameters)
│   │   ├── verify_section_3_8.json    ← Section-specific verification (edit sections array)
│   │   └── verify_custom.json         ← Custom mode (arbitrary parameters, N → ∞)
│   ├── data/                          ← (empty, populated by runs)
│   └── reports/                       ← (empty, populated by runs)
├── code/
│   ├── python/                        ← Canonical implementation
│   │   ├── qcd_bridge_engine.py       ← Core engine: 9 sections, all formulas
│   │   ├── report_engine.py           ← 7-format report generator (TXT/CSV/MD/PDF/HTML/DOCX/JSON)
│   │   ├── generate_figures_3d_4d.py  ← 3D + 4D figure generator (600 DPI PNG + PDF + SVG)
│   │   ├── run.py                     ← CLI with 5 modes, EN/RU i18n
│   │   └── web_runner.py              ← Bridge for Next.js web app (subprocess)
│   ├── julia/
│   │   └── qcd_bridge_engine.jl       ← Julia mirror (LinearAlgebra, StatsBase, JSON)
│   ├── java/
│   │   ├── qcd_bridge_engine.java     ← Java mirror (pure stdlib, Jacobi eigensolver)
│   │   └── qcd_bridge/                ← Compiled .class files (after javac)
│   └── web/                           ← Next.js 16 web app
│       ├── src/
│       │   ├── app/                   ← Routes: /, /api/run, /api/report, /api/figures/[section]
│       │   ├── components/qcd/        ← 8 React components (Home, Section, ParamPanel, etc.)
│       │   └── lib/qcd/               ← 8 modules (compute, i18n, linalg, types, etc.)
│       ├── package.json
│       └── README.md
└── ci_workflows/                      ← Fixed GitHub Actions workflows (see below)
```

## Quick start

### Python (recommended)

```bash
cd code/python/
pip install numpy scipy matplotlib python-docx reportlab

# Full verification (all 9 sections, all 7 report formats)
python run.py --mode verify_all --output-dir ../../qcd_bridge/reports

# Section-specific verification
python run.py --mode verify_section --sections 3,8 --formats json,pdf,docx

# Custom parameters (arbitrary precision, N → ∞ via streaming)
python run.py --mode custom --config ../../qcd_bridge/configs/verify_custom.json

# Regenerate all 3D/4D figures only
python run.py --mode figures

# Interactive menu (EN)
python run.py --lang en

# Interactive menu (RU)
python run.py --lang ru
```

### Julia

```bash
cd code/julia/
julia --project=. -e 'using Pkg; Pkg.add(["JSON", "StatsBase"])'
julia qcd_bridge_engine.jl                    # verify_all
julia qcd_bridge_engine.jl --section 3,8      # verify_section
julia qcd_bridge_engine.jl --custom 12.0      # custom kappa_T
```

### Java

```bash
cd code/java/
# Compile (requires JDK 17+)
javac qcd_bridge_engine.java

# Run
java qcd_bridge_engine                    # verify_all
java qcd_bridge_engine --section 3,8      # verify_section
java qcd_bridge_engine --custom 12.0      # custom kappa_T
```

### Web app (Next.js)

```bash
cd code/web/
npm install   # or: bun install
npm run dev   # http://localhost:3000

# Production build
npm run build && npm start
```

The web app provides:
- Real-time 3D/4D visualization (Plotly.js) — parameters update the chart instantly
- Interactive parameter panel (kappa_T, N, n_flavors, seed, section selection)
- All 9 sections with custom visualizations
- Report download in 7 formats (TXT/CSV/MD/PDF/HTML/DOCX/JSON)
- EN/RU language toggle
- "Run via Python" button for canonical NumPy/LAPACK computation

## The 9 sections

| # | Section | Key result |
|---|---------|-----------|
| 1 | O_chi operator construction | 28×28 Hermitian matrix, N = 22 (K3) + 6 (flavors) |
| 2 | RMT universality sweep | BF(GUE/Poisson) crossover at κ_T ≈ 1.5 |
| 3 | Spectral staircase vs Wigner | GUE classification confirmed |
| 4 | N-scaling of ⟨λ⟩ | 1/√N artifact verified, vanishes as N → ∞ |
| 5 | τ_relax dynamics | τ_relax ≈ 5×10⁻⁴¹ s (hbar/Λ_QCD) |
| 6 | κ_T physical estimate | 95% CL lower bound κ_T > 2.62, BF = 99 (strong) |
| 7 | Cabibbo angle coincidence | θ_C^pred ≈ 0.3303 rad, θ_C^meas ≈ 0.2278 rad |
| 8 | CP 8-step solution chain | θ̄ = 0 exactly, no new fields/scales/symmetries |
| 9 | Jet wake bridge | χ_eff = δ_C · Λ_QCD⁴ ≈ 7.18×10⁻⁴ GeV⁴ |

## Report formats

All implementations produce reports with the structure: **RESULTS first, then LOGS**.

| Format | Python | Julia | Java | Web |
|--------|--------|-------|------|-----|
| TXT    | ✓      | ✓     | ✓    | ✓   |
| CSV    | ✓      |       |      | ✓   |
| MD     | ✓      |       |      | ✓   |
| PDF    | ✓      |       |      | ✓   |
| HTML   | ✓      |       |      | ✓   |
| DOCX   | ✓      |       |      | ✓   |
| JSON   | ✓      | ✓     | ✓    | ✓   |

## CI workflow fixes

The original repository had YAML syntax errors in `.github/workflows/`:
the `branches:` field was missing its opening bracket (`branches: ain]`
instead of `branches: [main]`). This was actually a terminal display
artifact (the `[m` sequence was being interpreted as an ANSI color reset
code), but the workflows have been verified to parse correctly with
PyYAML: `push.branches = ['main']` and `pull_request.branches = ['main']`.

Fixed/verified workflows are in `ci_workflows/`:
- ci.yml, lint.yml, pages.yml, scorecard.yml, link-check.yml

## Citation

```bibtex
@misc{choptyuk_qcd_bridge_2026,
  title         = {The Choptuik-Strong CP Operator: A Spectral Bridge from
                   Numerical Relativity to QCD Topological Sectors},
  author        = {Isaev, Ishak Khamzatovich},
  year          = {2026},
  note          = {Enhanced verification suite with 3D/4D figures, 4-language
                   implementations (Python/Julia/Java/Web), and EN/RU monographs}
}
```

## License

Isaev Proprietary License — see the parent repository.

## Contact

- ORCID: [0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701)
- GitHub: [wild8highlander/choptuik_ac_bc](https://github.com/wild8highlander/choptuik_ac_bc)
