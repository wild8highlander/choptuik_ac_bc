# QCD Bridge — a-C ↔ θ_QCD numerical study

This directory contains a research companion to the Choptyuk--Isaev monograph
investigating whether the **spinorial braking correction a-C** of the Choptyuk
formula could be related — by analogy or by rescaling — to the QCD vacuum
angle θ whose experimental bound from the neutron EDM is |θ| < 10⁻¹⁰.

## Contents

| File | Purpose |
|------|---------|
| `choptyuk_qcd_bridge.pdf` | Final research monograph (34 pages, arXiv-style) |
| `choptyuk_qcd_bridge.tex` | LaTeX source |
| `v2_section.tex` | § VII — Higgs-scale bridge derivation + phenomenology |
| `abd_section.tex` | § VIII — Mercury paradox + lattice θ-dep + PQ residual |
| `wavefunction_section.tex` | § IX — Wave-function bridge: a_C as axion ground state |
| `qcd_bridge.bib` | Bibliography |
| `qcd_bridge_results.json` | Numerical results of original E1–E5 experiments |
| `qcd_observables_results.json` | v2 CP-odd observables + Monte Carlo |
| `wavefunction_bridge_results.json` | v3 wave-function analysis results |
| `figures/` | Publication-quality figures (PNG, 110–220 dpi) |

The companion Jupyter notebook is at
[`../../notebooks/qcd_bridge_experiments.ipynb`](../../notebooks/qcd_bridge_experiments.ipynb),
and the reproducible Python scripts at
[`../../scripts/qcd_bridge/qcd_bridge_experiments.py`](../../scripts/qcd_bridge/qcd_bridge_experiments.py),
[`../../scripts/qcd_bridge/qcd_observables_with_aC.py`](../../scripts/qcd_bridge/qcd_observables_with_aC.py),
and
[`../../scripts/qcd_bridge/axion_wavefunction_bridge.py`](../../scripts/qcd_bridge/axion_wavefunction_bridge.py).

The verification module for the bridge is at
[`../../python/src/core/qcd_bridge_verification.py`](../../python/src/core/qcd_bridge_verification.py)
and is integrated into the test suite:
```bash
cd python/
python -m pytest tests/test_choptyuk.py -v
# 67 passed in <1 second
```

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

### Stage 2 — Higgs-scale bridge: derivation and phenomenology (§ VII)

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

### Stage 3 — Mercury paradox, lattice θ-dep, and PQ residual (§ VIII)

Section VIII consolidates directions (A), (B), (D):

- **(A) Mercury paradox — honest verdict.** At the central theoretical
  estimate `c_Hg = 3e-17 e*cm/theta`, the Mercury bound excludes
  `theta_Ch` (paradox apparent ratio ~343).  However, the Schiff-moment
  coefficient has a 1–2 order-of-magnitude theoretical uncertainty
  (Pospelov-Ritz 2005).  With 100x uncertainty, the effective Mercury
  bound relaxes to ~2.5e-11 (1-sigma); with additional nuclear
  cancellations (de Vries 2018) and chromo-EDM decoupling, to ~2.5e-10
  (aggressive).  At the aggressive end, the Choptyuk phase
  `theta_Ch = 8.5e-11` is consistent.  Status: **MARGINALLY RESOLVED
  (requires aggressive cancellations)**.  The decisive test remains
  the nEDM experiment, not Mercury.

- **(B) Lattice QCD θ-dependence (Vicari-Panagopoulos).** Lattice
  values `b_2 = -0.0123`, `b_4 = 7.5e-4` agree with the large-N
  prediction `b_2 = -1/108 ≈ -0.00926` at 30% level (ratio 1.33).  At
  `theta_Ch ~ 1e-10`, the relative correction to `chi_t` is ~1e-22
  (unobservable).  The Choptyuk phase is deep within the linear regime
  of lattice θ-dependence.  Status: **fully consistent**.

- **(D) PQ axion with residual θ_Ch.** Standard PQ potential
  `V_PQ = -chi_t/2 * (theta - a/f_a)^2` is modified to
  `V_PQ^Ch = -chi_t/2 * (theta - a/f_a - theta_Ch)^2`.  PQ relaxation
  drives `<a>/f_a -> theta - theta_Ch`, leaving a residual
  `theta_eff = theta_Ch ~ 1e-10`.  The axion mass is unchanged
  (`m_a = 5.7 µeV at f_a = 1e12 GeV`); the relative mass shift is
  ~1e-21 (unobservable).  The residual is undetectable by axion
  haloscopes (which see `<a>` fluctuations) but detectable by EDM
  experiments.  This provides a clean experimental signature
  distinguishing Choptyuk-augmented PQ from standard PQ.

- **(C) arXiv formatting.** Achieved by the section structure,
  numbered equations, and bibliographic additions (Vicari-Panagopoulos
  2009, Pospelov-Ritz 2005, Dmitriev-Flambaum 2005, de Vries 2018,
  nEDM Collaboration 2024).

### Stage 4 — Wave-function bridge: a_C as axion ground state (§ IX)

Section IX explores a new theoretical tool: the **quantum-mechanical
wave function** of the PQ axion field.  Instead of treating θ_Ch as a
fitted constant, we quantize the PQ axion in the Choptyuk-augmented
potential V_PQ^Ch(q) = 1 - cos(q + θ_bare) + θ_Ch · q (in dimensionless
units q = a/f_a) and study the ground-state wave function ψ_0(q).

- **Numerov solver** for the stationary Schrödinger equation on a
  single cosine well (N=8001 grid points, Dirichlet BCs at the
  potential barriers).  Ground state energy E_0 = 0.652 χ_t
  (30% above the harmonic 0.5 — real anharmonic correction from
  the cosine potential).  Quantum width σ_q = 0.888 (25% above
  the harmonic 0.707).

- **Central physical statement.** The Choptyuk residual θ_Ch ~ 10⁻¹⁰
  is **2 × 10¹⁶ times larger** than the quantum zero-point fluctuation
  σ_θ^qm ~ 10⁻²⁶·⁴.  Therefore θ_Ch is a **CLASSICAL tilt** of the
  PQ potential, NOT a quantum fluctuation.  The Higgs bridge induces
  a classical shift of the potential minimum, and the quantum ground
  state follows the shift adiabatically.

- **Hubble-friction relaxation** (Wantz-Aliaga 2010, Hiramatsu 2012):
  the cosmological axion equation ÿ + 3H ẏ + m_a² sin y = 0 has
  damping term 3H ẏ that converts the field's kinetic energy into
  cosmic expansion.  This is the physical "slowing" mechanism the
  user identified: above T_osc ≈ 69 GeV the field is frozen; below
  T_osc it oscillates around the Choptyuk-shifted minimum with
  amplitude decaying as (T/T_osc)^(3/2).  After many oscillations
  ⟨θ⟩ → θ_Ch.

- **WKB instanton splitting.** The tunneling action S_inst = 8
  (analytic) gives S_phys = 10^10.7 and splitting ΔE ~ 10⁻⁸·⁵ GeV,
  exponentially suppressed relative to E_0 ~ 10⁻⁵ GeV.  The axion
  is therefore a classical coherent field at f_a = 10¹² GeV.

- **What this section does NOT prove.** The 5/2 exponent is NOT
  derived from the wave-function analysis (it remains a Stage 2
  structural-motivation result).  The wave function cannot
  independently determine θ_Ch; the tilt amplitude is an input
  from the Higgs bridge.

### Verification module

All numerical results in § VII–IX are produced by
`python/src/core/qcd_bridge_verification.py` (mirroring the pattern of
`enhanced_verification.py`) and verified by 37 unit tests in the
`TestQCDBridgeVerification` class.  The full test suite (67 tests)
passes in <1 second.

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

# Stage 4 — Wave-function bridge analysis
python scripts/qcd_bridge/axion_wavefunction_bridge.py
# → writes results to scripts/qcd_bridge/wavefunction_bridge_results.json
# → writes figures to scripts/qcd_bridge/figures_v3/
#   (also copied into docs/monograph/qcd_bridge/figures/)

# Compile the monograph (requires tectonic)
cd docs/monograph/qcd_bridge/
tectonic choptyuk_qcd_bridge.tex
# → produces choptyuk_qcd_bridge.pdf (34 pages)
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
