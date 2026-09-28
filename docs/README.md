# docs

Reference documentation for the framework: the REST API specification, the
system architecture description, the archived monograph manuscripts with
their verification code and results, and the self-contained QCD-bridge
companion monograph. Nothing here is generated at build time — these files
are the citable, versioned reference texts of the repository.

## What is inside

| Path | Contents |
|------|----------|
| `api/REST_API.md` | Full REST reference for the Java web app: base URL `http://localhost:8080`, `GET /api/verify` (verification suite JSON with spinor phases, formula deviations, `all_passed`), `GET /api/reports?format=json|html|csv|txt|md`, simulation and enhanced endpoints |
| `architecture/ARCHITECTURE.md` | Architecture overview with a Mermaid diagram: theory (Klein quartic, spinor phases, Dirac operator, formula) → four independent implementations (Python, Julia, Java, Next.js) → CI/CD layer; the core data-flow pipeline from curve parameters to QNM predictions |
| `monograph/` | The braking-monograph manuscripts in DOCX + PDF (English and Russian, final and enhanced renderings), LaTeX sources `monograph_enhanced_en.tex` / `_ru.tex`, 16 figures (`figures/fig_*.png`), and the verification artifacts: `original_verification_code.py`, `original_verification_results.json`, `verification_results_enhanced.json` |
| `qcd_bridge/` | Self-contained companion monograph "Choptuik–QCD bridge" with its own `README.md`, LaTeX source + compiled PDF, 12 figure pairs (PNG + PDF) in `figures/`, and four JSON result files (`ochi_eigenvalues.json`, `ochi_lattice_results.json`, `qcd_vs_framework_params.json`, `honesty_results.json`) |

### Committed data files in `docs/qcd_bridge/`

| File | Contents |
|------|----------|
| `ochi_eigenvalues.json` | 28×28 O_chi spectrum across the κ_T sweep |
| `ochi_lattice_results.json` | K3 vs chGUE comparison results |
| `qcd_vs_framework_params.json` | Epistemic-parity accounting between the QCD and framework parameter sets |
| `honesty_results.json` | Monte Carlo, Cabibbo and scaling audit outputs backing the honesty sections of the text |
| `figures/kappa_T_physical_estimate.json` | Lattice-bound estimate behind the κ_T figure |

## How to use

These are reference documents; the computational entry points they describe
live elsewhere:

```bash
# verification suite described by REST_API.md / ARCHITECTURE.md
cd python && python run.py --mode verify --non-interactive

# reproduce the monograph's own verification artifacts
python3 docs/monograph/original_verification_code.py

# QCD-bridge computations referenced by docs/qcd_bridge/
python3 code/python/run.py --mode verify_all --non-interactive
```

The LaTeX sources in `monograph/` and `qcd_bridge/` can be recompiled with
any standard TeX distribution (`pdflatex monograph_enhanced_en.tex`).

## Notes

- `docs/monograph/original_verification_code.py` is the historical
  verification script whose committed output is
  `original_verification_results.json`; the enhanced result set is kept
  alongside it in `verification_results_enhanced.json` so the two stages of
  the verification campaign remain auditable.
- The monograph figures are 600 DPI PNGs; identical figures are regenerated
  by the engines (see `python/src/visualization/` and
  `code/python/generate_figures_3d_4d.py`).
- The JSON files in `docs/qcd_bridge/` (eigenvalue spectra, lattice
  comparison, honesty audits) are the data behind the companion monograph's
  figures and are loaded by the computational scripts.
- The MkDocs-based documentation site built from `docs-site/` is the
  rendered web version of the API and mathematics material.
