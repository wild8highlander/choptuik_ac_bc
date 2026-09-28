# monograph

Publication-ready manuscripts of the **Choptuik–Strong CP operator** study:
a spectral bridge from numerical relativity to QCD topological sectors,
authored by Ishak Khamzatovich Isaev. This folder holds the two final
word-processor renderings of the text — one in English, one in Russian — with
identical structure and numbering.

## What is inside

| File | Contents |
|------|----------|
| `choptyuk_qcd_bridge_en.docx` | English manuscript: *The Choptuik–Strong CP Operator — A Spectral Bridge from Numerical Relativity to QCD Topological Sectors* |
| `choptyuk_qcd_bridge_ru.docx` | Russian-language edition of the same manuscript (identical structure and numbering) |

## Section map

Both editions follow the same nine-section plan, which is also the section
numbering used by every engine and report in the repository:

| § | Section |
|---|---------|
| 1 | Introduction and motivation |
| 2 | Mathematical foundations |
| 3 | The O_chi operator and its structural role |
| 4 | Spectral analysis and RMT universality |
| 5 | The κ_T sweep and Bayes-factor classification |
| 6 | N-scaling and the 1/√N artifact |
| 7 | The Cabibbo angle coincidence |
| 8 | The 8-step CP solution chain |
| 9 | Jet wake bridge |

Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701).

## How to use

There is nothing to execute here — the `.docx` files are read-only
deliverables. The verified companions of this text live elsewhere in the
repository:

- **Reproduce every number** of the nine sections:
  `python code/python/run.py --mode verify_all --non-interactive`
  (engine in `code/python/qcd_bridge_engine.py`).
- **Static 3D/4D figures, animations and reports** generated from the
  manuscripts: see the `qcd_bridge/` folder (`figures/`, `animations/`,
  `reports/`).
- **An independent Java implementation** of the same nine sections:
  `code/java/qcd_bridge_engine.java`; a Julia port: `code/julia/qcd_bridge_engine.jl`.
- A related LaTeX/PDF companion with its own figure set is available under
  `docs/qcd_bridge/`.

## Notes

- The manuscripts are the reference source for the physical constants used by
  all engines: δ_C = π/7, N_HILBERT = 28 (22 K3 + 6 N_f), κ_T lower bound
  2.62, best fit 8.45, τ_relax = 5.0·10⁻⁴¹ s.
- Report files in `qcd_bridge/reports/` and `qcd_bridge/reports_java/` were
  produced from the Python and Java engines respectively and mirror the
  monograph section numbering, so text and computation can be checked side by
  side.
- License: Isaev Proprietary (see `LICENSE` in the repository root).
