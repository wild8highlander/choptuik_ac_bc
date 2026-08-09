# QCD Bridge — a-C ↔ θ_QCD numerical study

This directory contains a research companion to the Choptyuk--Isaev monograph
investigating whether the **spinorial braking correction a-C** of the Choptyuk
formula could be related — by analogy or by rescaling — to the QCD vacuum
angle θ whose experimental bound from the neutron EDM is |θ| < 10⁻¹⁰.

## Contents

| File | Purpose |
|------|---------|
| `choptyuk_qcd_bridge.pdf` | Final research monograph (24 pages, arXiv-style) |
| `choptyuk_qcd_bridge.tex` | LaTeX source |
| `v2_section.tex` | § VII — Higgs-scale bridge derivation + phenomenology |
| `qcd_bridge.bib` | Bibliography |
| `qcd_bridge_results.json` | Numerical results of original E1–E5 experiments |
| `qcd_observables_results.json` | v2 CP-odd observables + Monte Carlo |
| `figures/` | Publication-quality figures (PNG, 110–220 dpi) |

The companion Jupyter notebook is at
[`../../notebooks/qcd_bridge_experiments.ipynb`](../../notebooks/qcd_bridge_experiments.ipynb),
and the reproducible Python scripts at
[`../../scripts/qcd_bridge/qcd_bridge_experiments.py`](../../scripts/qcd_bridge/qcd_bridge_experiments.py)
and
[`../../scripts/qcd_bridge/qcd_observables_with_aC.py`](../../scripts/qcd_bridge/qcd_observables_with_aC.py).

## Headline findings

### Stage 1 — Numerical coincidences (E1–E5)

Three numerical coincidences emerge, each requiring an unexplained parameter:

1. **δ = π/168** (full PSL(2,7) group order), **b = 22**: `δ⁵/b ≈ 1.04 × 10⁻¹⁰`
   — within 4% of the θ bound. *Unjustified:* replaces a generator by a group order.
2. **a_C · (Λ_QCD / M_Pl)^(1/3) ≈ 2.1 × 10⁻¹⁰** — within a factor of 2.
   *Unjustified:* the 1/3 exponent has no derivation.
3. **a_C · (Λ_QCD / M_Higgs)^(5/2) ≈ 8.5 × 10⁻¹¹** — within 7%.
   *Unjustified at stage 1:* the 5/2 exponent had no derivation.

The direct identification is **refuted** (7 orders of magnitude gap, CP-even vs
CP-odd, discrete vs continuous). The bridge hypothesis remained numerological
at this stage.

### Stage 2 — Higgs-scale bridge: derivation and phenomenology (v2)

The v2 extension (§ VII of the monograph) closes the gap on the third
coincidence:

- **The 5/2 exponent is structurally motivated** by the Cohen–Kaplan–Nelson
  sphaleron rate scaling `Γ_sph(T) ~ α_W^5 T^4 (M_H/T)^(5/2)`, evaluated
  at `T = Λ_QCD`.
- The **Choptyuk-augmented QCD Lagrangian** is introduced:
  `L_QCD^Ch = L_QCD + (g_s^2 / 32π^2) θ_Ch tr(F ∧ F̃)`,
  with `θ_Ch := a_C · (Λ_QCD / M_H)^(5/2) ≈ 8.46 × 10⁻¹¹`.
- **Falsifiable prediction**: `d_n^Ch = 2.4 × 10⁻¹⁶ · θ_Ch ≈ 2.0 × 10⁻²⁶ e·cm`,
  sitting **13% above** the current nEDM@PSI bound (1.8 × 10⁻²⁶ e·cm).
- **Monte Carlo** (200k samples, propagating Λ_QCD and lattice-QCD uncertainties)
  gives `P(d_n > 1.8 × 10⁻²⁶ e·cm) = 0.54` — i.e. essentially a coin flip
  against the current bound.
- **Falsification timeline**: SNS nEDM (2026–2027) and n2EDM@PSI (2027–2028)
  will measure d_n at 10⁻²⁷ – 10⁻²⁸ e·cm sensitivity, decisively testing
  the bridge hypothesis.

## Reproducing

```bash
# from repo root

# Stage 1 — original E1-E5 experiments
python scripts/qcd_bridge/qcd_bridge_experiments.py
# → writes results to docs/monograph/qcd_bridge/qcd_bridge_results.json
# → writes figures to docs/monograph/qcd_bridge/figures/

# Stage 2 — CP-odd observables + Monte Carlo with a_C inserted into QCD
python scripts/qcd_bridge/qcd_observables_with_aC.py
# → writes results to scripts/qcd_bridge/qcd_observables_results.json
# → writes figures to scripts/qcd_bridge/figures_v2/
#   (also copied into docs/monograph/qcd_bridge/figures/)

# Compile the monograph (requires tectonic)
cd docs/monograph/qcd_bridge/
tectonic choptyuk_qcd_bridge.tex
# → produces choptyuk_qcd_bridge.pdf (24 pages)
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
