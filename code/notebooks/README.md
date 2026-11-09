# notebooks

A single self-contained Jupyter notebook that walks through the core
verification of the spinor-correction framework cell by cell. It is the
quickest interactive way to see every reference constant computed live —
spinor phases, Klein quartic geometry, the Dirac eigenvalue via the
Lichnerowicz formula, the unified Choptyuk formula, and the plots that
summarise them.

## What is inside

| File | Contents |
|------|----------|
| `choptyuk_verification.ipynb` | 18 cells (markdown + Python) reproducing the monograph's verification chain: spinor phases δ_A = π/2, δ_B = π/3, δ_C = π/7; Klein quartic invariants (genus 3, automorphism group PSL(2,7) of order 168); the unified formula with b-C and a-C corrections; publication-quality figures (bar charts, unit-circle phase diagrams, sweeps) |

### Cell-by-cell outline

| Cells | Topic |
|-------|-------|
| 1–2 | Title, framework summary, imports and publication-quality matplotlib configuration |
| 3–5 | Spinor phases and Klein curve geometry: δ_A, δ_B, δ_C, genus, automorphism order, Euler characteristic, scalar curvature; Figure with bar chart, unit circle and phase relations |
| 6–7 | The unified Choptyuk formula: b-C correction (first order, Berry phase) and a-C braking (second order), evaluated and plotted |
| middle cells | Parameter sweeps over the spinor phase δ_C and the Laplacian eigenvalue λ₁, with convergence plots |
| closing cells | Summary table of computed vs reference values and the verification verdict |

The notebook uses only `numpy`, `matplotlib` and the standard library — all
computations are performed inline so each claim can be edited and re-run in
place.

## How to run

```bash
# dependencies are shared with the python/ package
python3 -m pip install -r python/requirements.txt

# open the notebook (Jupyter is preinstalled in the dev container)
jupyter notebook notebooks/choptyuk_verification.ipynb
```

Then execute the cells top to bottom (`Run All`). Every figure is regenerated
in-notebook; nothing is loaded from the `output/` directory, so the notebook
is safe to run in a fresh clone.

## Notes

- The notebook is a teaching/inspection surface, not the canonical pipeline:
  for CI-grade verification use `python run.py --mode verify --non-interactive`
  from the `python/` folder (see its README).
- The `.devcontainer` image installs JupyterLab and forwards port 8888, so the
  notebook can also be run inside the container without local installs.
- Cells intentionally restate constants as literals (e.g. λ₁ = 3.838,
  R = −2) so that the arithmetic is fully transparent; the typed
  implementations of the same quantities live in `python/src/core/`.
- Figures are produced with `matplotlib` at the notebook's own publication
  settings; the committed file contains no stored outputs, so a fresh
  "Run All" is the expected workflow.
- If you change a constant in one cell, re-run from that cell downward — the
  later sweeps depend on the phase values defined earlier in the notebook.
