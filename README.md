# Spinor Corrections b-C & a-C and the Choptyuk Problem

[![License: Proprietary](https://img.shields.io/badge/License-Isaev%20Proprietary-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Julia 1.9+](https://img.shields.io/badge/Julia-1.9+-955880.svg)](https://julialang.org/)
[![Java 17+](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![CI](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/ci.yml/badge.svg)](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/ci.yml)
[![Lint](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/lint.yml/badge.svg)](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/lint.yml)
[![Pages](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/pages.yml/badge.svg)](https://wild8highlander.github.io/choptuik_ac_bc/)
[![Release](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/release.yml/badge.svg)](https://github.com/wild8highlander/choptuik_ac_bc/releases/latest)
[![DOI](https://img.shields.io/badge/Zenodo-Archive-orange.svg?logo=zenodo)](https://zenodo.org/search?q=choptuik_ac_bc)
[![GitHub](https://img.shields.io/badge/GitHub-choptuik__ac__bc-181717?logo=github)](https://github.com/wild8highlander/choptuik_ac_bc)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/wild8highlander/choptuik_ac_bc/badge)](https://securityscorecards.dev/viewer/?uri=github.com/wild8highlander/choptuik_ac_bc)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

> **Monograph**: *Spinor corrections b-C and a-C and the solution of the Choptyuk problem*
> by **Ishak Khamzatovich Isaev**
> — Rigorous computation of spectral invariants on the Klein quartic curve with applications to LIGO/Virgo quasi-normal mode predictions.

---

## Overview

This repository provides **four independent implementations** for the verification, simulation, and visualization of all results presented in the monograph:

| Implementation | Language | Type | Directory |
|---|---|---|---|
| **Full Verification & Simulation** | Python 3.10+ | CLI with interactive menu | [`python/`](python/) |
| **Full Verification & Simulation** | Julia 1.9+ | REPL with interactive menu | [`julia/`](julia/) |
| **Web Application** | Java 17+ (Spring Boot) | REST API + Web UI | [`java-webapp/`](java-webapp/) |
| **Interactive Visualization** | Next.js 15 + React | Real-time dashboard | [`interactive-viz/`](interactive-viz/) |

All implementations share:
- Interactive parameter configuration (all values customizable, including arbitrary precision)
- Hypothesis testing with custom spinor structures and group configurations
- Multi-format report generation: **DOCX, PDF, TXT, MD, CSV, HTML, JSON**
- High-resolution plots: **600 DPI PNG** + **vector PDF/SVG**
- Complete execution logs appended to every report
- Structured output directory for all artifacts

---

## Mathematical Background

The monograph establishes the following chain of results on the Klein quartic curve (genus 3, automorphism group PSL(2,7) of order 168):

### Core Constants

| Constant | Formula | Value |
|---|---|---|
| Spinor phase δ_A | π/2 | 1.570796 |
| Spinor phase δ_B | π/3 | 1.047198 |
| Spinor phase δ_C | π/7 | 0.448799 |
| First eigenvalue λ₁(Δ) | Bourque–Strohmaier 2024 | 3.838 |
| Trivial Dirac λ₁(D²_σ₀) | λ₁(Δ) + R/4 | 3.338 |

### The Choptyuk Formula

**b-C correction** (1st order, Berry phase):
```
Δ_bC = λ₁(D²_σ₀) + δ_C²/2 = 3.438710
```

**a-C correction** (2nd order, braking):
```
δ_eff = δ_C⁵/22 ≈ 1/1200 = 0.000828
```

**Unified Choptyuk formula** (base):
```
Δ_Ch = λ₁(D²_σ₀) + δ_C²/2 − δ_C⁵/22 = 3.437883
```

**With higher orders**:
```
Δ_Ch = Δ_Ch(base) + δ_C⁴/8 + δ_C⁶/2 = 3.447040
```

**Choptyuk constant**:
```
b_Ch = 1 − cos(2π/7) = 2·sin²(π/7) ≈ 0.377
```

### Applications

- **64 spinor structures** on the Klein curve — full enumeration and spectral analysis
- **Bolza and Bring surfaces** — comparative spectral invariants
- **LIGO/Virgo QNM predictions** — quasi-normal mode corrections for GW150914, GW170104, GW170814, GW190521

---

## Quick Start

### Python (Recommended for quick verification)

```bash
cd python/
pip install -r requirements.txt
python run.py
```

### Julia

```bash
cd julia/
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. run.jl
```

### Java Web Application

```bash
cd java-webapp/
mvn clean package
java -jar target/choptyuk-webapp.jar
# Open http://localhost:8080
```

### Interactive Visualization

```bash
cd interactive-viz/
npm install
npm run dev
# Open http://localhost:3000
```

**Online demo**: [https://wild8highlander.github.io/choptuik_ac_bc/](https://wild8highlander.github.io/choptuik_ac_bc/)

### Using Makefile (One Command)

```bash
make all          # Run verification + simulation + plots + reports
make verify       # Run verification only
make viz-dev      # Start interactive visualization
make setup        # Set up all environments
make docker-run   # Run via Docker
```

### Using Docker

```bash
docker build -t choptyuk-verify -f docker/Dockerfile .
docker run --rm -v $(pwd)/output:/app/output choptyuk-verify
```

### Using Dev Container

Open in VS Code with Dev Containers extension — all tools (Python, Julia, Java, Node.js) pre-installed.

---

## Project Structure

```
choptuik_ac_bc/
├── README.md                    # This file
├── LICENSE                      # Isaev Proprietary License
├── CITATION.cff                 # Citation metadata
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
├── .gitignore                   # Git ignore rules
├── .github/                     # GitHub templates & CI
│   ├── workflows/               # GitHub Actions CI/CD
│   └── ISSUE_TEMPLATE/          # Issue templates
├── docs/                        # Documentation
│   └── monograph/               # Original monograph files (EN/RU, DOCX/PDF)
├── python/                      # Python implementation
│   ├── run.py                   # Entry point with interactive menu
│   ├── requirements.txt         # Dependencies
│   ├── setup.py                 # Package setup
│   ├── config/                  # Default configurations
│   ├── presets/                 # Preset parameter sets
│   ├── src/                     # Source modules
│   │   ├── core/                # Core mathematical computations
│   │   ├── verification/        # Verification procedures
│   │   ├── simulation/          # Simulation engine
│   │   ├── visualization/       # Plot generation
│   │   ├── reporting/           # Report generation (7 formats)
│   │   └── ui/                  # Interactive CLI menu
│   └── tests/                   # Unit tests
├── julia/                       # Julia implementation
│   ├── run.jl                   # Entry point
│   ├── Project.toml             # Julia project
│   ├── config/                  # Configurations
│   ├── presets/                 # Presets
│   ├── src/                     # Source modules
│   └── test/                    # Tests
├── java-webapp/                 # Java Spring Boot web application
│   ├── pom.xml                  # Maven configuration
│   └── src/                     # Source code
├── interactive-viz/             # Next.js real-time visualization
│   ├── package.json             # NPM configuration
│   └── src/                     # Source code
└── scripts/                     # Utility scripts
```

---

## Report Formats

Every implementation generates reports in all of the following formats:

| Format | Extension | Description |
|---|---|---|
| Microsoft Word | `.docx` | Formatted document with tables and figures |
| Portable Document | `.pdf` | Publication-ready PDF |
| Plain Text | `.txt` | Human-readable text report |
| Markdown | `.md` | GitHub-compatible markdown |
| Comma-Separated | `.csv` | Tabular data for analysis |
| HTML | `.html` | Styled web report |
| JSON | `.json` | Machine-readable structured data |

Each report contains:
1. **Results section** — computed constants, deviations, comparison tables
2. **Execution log** — complete timestamped log of all computations

---

## Visualization Output

All plots are generated in two high-resolution formats:
- **PNG** at 600 DPI — for screen display and documents
- **PDF/SVG** — vector format for publication

Plot types include:
- Spinor phase diagrams
- Spectral eigenvalue landscapes
- 64 spinor structure heatmaps
- QNM frequency comparison charts
- Deviation analysis plots
- Convergence diagrams

---

## Verification Results (Reference)

| Constant | Computed | Observed | Deviation |
|---|---|---|---|
| Δ_bC | 3.438710 | 3.443 | 0.125% |
| Δ_Ch (base) | 3.437883 | 3.443 | 0.149% |
| Δ_Ch (full) | 3.447040 | 3.443 | 0.117% |
| b_Ch | 0.376510 | 0.377 | 0.130% |

---

## Citation

If you use this code in your research, please cite:

```bibtex
@book{isaev2024spinor,
  title     = {Spinor corrections b-C and a-C and the solution of the Choptyuk problem},
  author    = {Isaev, Ishak Khamzatovich},
  year      = {2024},
  address   = {Nalchik, Kabardino-Balkarian Republic},
  note      = {Monograph with verified computational implementations}
}
```

### Zenodo Archive

A permanent DOI-backed archive of this software is available on Zenodo.
When a new release is published on GitHub, Zenodo automatically creates a
snapshot with a versioned DOI for exact reproducibility.

[![DOI](https://img.shields.io/badge/Zenodo-Archive-orange.svg?logo=zenodo)](https://zenodo.org/search?q=choptuik_ac_bc)

---

## Author

**Ishak Khamzatovich Isaev**

- Email: [aslan08_05@mail.ru](mailto:aslan08_05@mail.ru)
- GitHub: [@wild8highlander](https://github.com/wild8highlander)
- Location: Nalchik, Kabardino-Balkarian Republic

---

## License

This project is licensed under the **Isaev Proprietary License** — see the [LICENSE](LICENSE) file for details.

**Summary:** This is a proprietary license. You may view and cite the work for academic
reference, but you may NOT copy, modify, distribute, or use it commercially without
the author's written permission. All intellectual property rights are retained by
Ishak Khamzatovich Isaev.

---

## Reproducibility

This project is designed for **full computational reproducibility**:

- **Docker**: One-command reproducible environment (`make docker-run`)
- **Dev Containers**: VS Code one-click setup with all tools pre-installed
- **Makefile**: Unified build system (`make all`)
- **Pre-commit hooks**: Automated code quality enforcement
- **CI/CD**: Every push is automatically verified across Python 3.10-3.12, Julia 1.9-1.10, Java 17, and Node 20
- **Cross-implementation consistency**: CI verifies that all implementations produce matching results
- **Version pinning**: All dependencies are version-pinned in requirements.txt, Project.toml, pom.xml, package.json
- **Zenodo DOI**: Permanent archived snapshots for each release

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. Quick workflow:

1. Fork → Branch → Commit → PR
2. CI runs automatically (Python + Julia + Java + Viz)
3. All verification tests must pass
4. Deviations from reference values must remain within tolerance
5. New features require corresponding tests

---

## Acknowledgments

- Bourque & Strohmaier (2024) for the rigorous computation of λ₁(Δ) on the Klein quartic
- LIGO/Virgo Collaboration for gravitational wave observational data
- The PSL(2,7) symmetry group and its role in the spinor structure classification
