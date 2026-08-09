# QCD Bridge — a-C ↔ θ_QCD numerical study

This directory contains a research companion to the Choptyuk--Isaev monograph
investigating whether the **spinorial braking correction a-C** of the Choptyuk
formula could be related — by analogy or by rescaling — to the QCD vacuum
angle θ whose experimental bound from the neutron EDM is |θ| < 10⁻¹⁰.

## Contents

| File | Purpose |
|------|---------|
| `choptyuk_qcd_bridge.pdf` | Final research monograph (~30 pages, arXiv-style) |
| `choptyuk_qcd_bridge.tex` | LaTeX source |
| `qcd_bridge.bib` | Bibliography |
| `qcd_bridge_results.json` | All numerical results (E1–E5) as JSON |
| `figures/` | Publication-quality figures (PNG, 220 dpi) |

The companion Jupyter notebook is at
[`../../notebooks/qcd_bridge_experiments.ipynb`](../../notebooks/qcd_bridge_experiments.ipynb),
and the reproducible Python script at
[`../../scripts/qcd_bridge/qcd_bridge_experiments.py`](../../scripts/qcd_bridge/qcd_bridge_experiments.py).

## Headline findings

Three numerical coincidences emerge, each requiring an unexplained parameter:

1. **δ = π/168** (full PSL(2,7) group order), **b = 22**: `δ⁵/b ≈ 1.04 × 10⁻¹⁰`
   — within 4% of the θ bound. *Unjustified:* replaces a generator by a group order.
2. **a_C · (Λ_QCD / M_Pl)^(1/3) ≈ 2.1 × 10⁻¹⁰** — within a factor of 2.
   *Unjustified:* the 1/3 exponent has no derivation.
3. **a_C · (Λ_QCD / M_Higgs)^(5/2) ≈ 8.5 × 10⁻¹¹** — within 7%.
   *Unjustified:* the 5/2 exponent is even less natural.

The direct identification is **refuted** (7 orders of magnitude gap, CP-even vs
CP-odd, discrete vs continuous). The bridge hypothesis remains numerological
but not refuted at the structural level.

## Reproducing

```bash
# from repo root
python scripts/qcd_bridge/qcd_bridge_experiments.py
# → writes results to docs/monograph/qcd_bridge/qcd_bridge_results.json
# → writes figures to docs/monograph/qcd_bridge/figures/

# Compile the monograph
cd docs/monograph/qcd_bridge/
tectonic choptyuk_qcd_bridge.tex
```

## Citation

If you use this material in your research, please cite both the original
Choptyuk monograph and this companion note:

```bibtex
@book{isaev2024spinor,
  title     = {Spinor corrections b-C and a-C and the solution of the Choptyuk problem},
  author    = {Isaev, Ishak Khamzatovich},
  year      = {2024},
  url       = {https://github.com/wild8highlander/choptuik_ac_bc}
}
```
