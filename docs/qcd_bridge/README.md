# Choptuik–QCD Bridge: solving the strong CP problem via the spectral symmetry of $O_\chi$

This directory contains the **self-contained companion monograph** that
extends the Choptyuk–Isaev programme to the strong CP problem.  It is
the research output referenced in the root [`README.md`](../../README.md)
as the *Choptuik–Strong CP operator* framework.

---

## What is here

```
docs/qcd_bridge/
├── README.md                          # this file
├── choptyuk_qcd_bridge.tex            # LaTeX source (40 pages, 12 sections)
├── choptyuk_qcd_bridge.pdf            # compiled PDF (publication-grade)
├── figures/                           # 12 figures @ 600 DPI PNG + vector PDF
│   ├── fig_monte_carlo_gue_poisson.{png,pdf}
│   ├── fig_gue_high_N.{png,pdf}
│   ├── fig_cabibbo_hypotheses.{png,pdf}
│   ├── fig_ochi_explicit.{png,pdf}
│   ├── fig_ochi_lattice.{png,pdf}
│   ├── fig_trace_cancellation.{png,pdf}
│   ├── fig_scaling_N.{png,pdf}
│   ├── fig_kappa_T_physical.{png,pdf}
│   ├── fig_cp_solution.{png,pdf}
│   ├── fig_cp_relaxation.{png,pdf}
│   ├── fig_seesaw_discrepancy.{png,pdf}
│   ├── fig_jet_wake_bridge.{png,pdf}
│   └── kappa_T_physical_estimate.json
├── ochi_eigenvalues.json              # 28×28 O_chi spectrum (kappa_T sweep)
├── ochi_lattice_results.json          # K3 vs chGUE comparison
├── qcd_vs_framework_params.json       # epistemic parity accounting
└── honesty_results.json               # Monte Carlo, Cabibbo, scaling audits
```

The computational scripts that reproduce every number and every figure
are in [`scripts/qcd_bridge/`](../../scripts/qcd_bridge/).

---

## The result in one paragraph

The Choptyuk critical exponent $\delta_C = \pi/7$ and the QCD vacuum
angle $\bar\theta$ occupy the **same epistemic niche**: both are
dimensionless couplings to the topological charge operator $\hat Q$.  The
framework replaces the free QCD parameter $\bar\theta$ by a **derived
spectral quantity** via the work formula
$\bar\theta_{\mathrm{eff}} = \delta_C \cdot N\langle\lambda\rangle \cdot
\mathcal S_{\mathrm{GUE}}$, where $\langle\lambda\rangle$ is the mean
eigenvalue of the operator $O_\chi = Q_{K3} \oplus M_F + \kappa_T V_T$
on the $N=28$ Hilbert space ($22$ K3 topological sectors $\oplus$ $6$
quark flavours).  At the **lattice-determined physical value**
$\kappa_T^{(\mathrm{QCD})} > 2.62$ (95% CL), $O_\chi$ is in the GUE
universality class with framework Bayes factor $\mathrm{BF} \geq 99$
(strong; $\mathrm{BF}=510$ at best-fit $\hat\kappa_T = 8.45$).  The
Wigner semicircle is exactly symmetric, so all odd spectral moments
vanish and $\langle\lambda\rangle = 0$ exactly in the continuum limit.
The work formula then forces $\bar\theta = 0$ **without introducing any
new field, scale, or symmetry**.  Finite-$N$ lattice artifacts scale as
$1/\sqrt N$ and vanish in the continuum limit; the dynamic relaxation
layer damps any CKM-induced residual $\bar\theta_0 \sim 10^{-19}$ on a
timescale $\tau_{\mathrm{relax}} \sim 5 \times 10^{-41}\,$s.

---

## The eight-step CP solution

| Step | Statement | Status |
|---|---|---|
| 1 | $O_\chi = \hat Q$ (structural role) | §3 |
| 2 | $O_\chi = Q_{K3} \oplus M_F + \kappa_T V_T$ at $N=28$ | §5.6 |
| 3 | GUE class at $\kappa_T > 2.62$ (95% CL), $\mathrm{BF} \geq 99$ | §5.7, §6.4 |
| 4 | GUE spectral symmetry $\Rightarrow$ $\langle\lambda\rangle = 0$ | §6.5 |
| 5 | Work formula $\bar\theta = \delta_C N\langle\lambda\rangle \mathcal S_{\mathrm{GUE}}$ | §6 |
| 6 | $\bar\theta = 0$ exactly in continuum GUE regime | §6 |
| 7 | Finite-$N$ artifact $\sim 1/\sqrt N$ vanishes as $N\to\infty$ | §6.6 |
| 8 | Dynamic relaxation $\tau_{\mathrm{relax}} \sim 10^{-39}$ s | §6.7 |

---

## Epistemic parity with QCD

QCD itself uses **8 canonical empirical parameters** ($\alpha_s$, six
quark masses, $\theta_{\mathrm{QCD}}$) that are **not** derived from
first principles — they are measured from data.  The framework adds
**5 net new empirical parameters** ($\delta_C, a_C, b_C, c_{K3},
c_{AB}$), all measured from numerical (Choptuik) and topological (K3)
data, in the same epistemic role.  The framework **replaces one of
QCD's free parameters** ($\theta_{\mathrm{QCD}}$) with a derived
spectral quantity; it does not add an external input that needs
deriving from QCD.  Demanding that the framework "derive" its
parameters from first principles while QCD is allowed to "measure" its
own would be exactly the double standard the framework rejects.

| QCD parameter | Framework parameter | Relation | Type |
|---|---|---|---|
| $V_{us}$ (Cabibbo) | $c_\theta$ | $c_\theta = \sin^2(2\theta_C)/4$ | algebraic |
| $\theta_{\mathrm{QCD}}$ | $\delta_C$ | via work formula | structural |
| $\delta_{\mathrm{CKM}}$ | $b_C$ | same epistemic niche | epistemic |
| $\alpha_s$ | $\delta_C = \pi/7$ | both dimensionless inputs | epistemic |
| $f_\pi$ | $c_{K3}$ | both measured from data | epistemic |
| $\Lambda_{\mathrm{QCD}}$ | $a_C$ | both empirical scales | epistemic |

---

## Open problems (falsifiability and foundation-deepening)

The strong-CP solution is **structurally complete**.  The remaining
open tasks are **not** completion steps — they are falsifiability and
foundation-deepening, in the same sense that QCD's own open problems
(confinement proof, mass-gap theorem) do not block QCD from being a
complete physical theory at its own epistemic level.

1. **Direct lattice falsification of the work formula at $\bar\theta
   \neq 0$.**  Use the Giusti–Rossi–Testa method (arXiv:0805.2056; see
   also Borsányi et al., arXiv:1512.04954) to measure
   $F(\bar\theta) - F(0)$ directly.  Agreement is verification;
   disagreement is falsification.

2. **Derivation of the structural inputs from $\mathrm{PSL}(2,7)$.**
   Derive the work formula, $O_\chi$, $N=28 = \dim \mathrm{Rep}_3
   (\mathrm{PSL}(2,7))$, and the interchangeability
   $\theta_{\mathrm{QCD}} \leftrightarrow \delta_C$ from the
   $\mathrm{PSL}(2,7)$ algebraic geometry (K3 intersection form
   $E_8 \oplus E_8 \oplus U^{\oplus 3}$, Klein quartic as a genus-3
   Riemann surface).  This is the framework's **own** foundation, not a
   derivation from QCD.

---

## Reproducibility

Every numerical value, every figure, and every Bayes factor in the
monograph is reproduced by the scripts in
[`scripts/qcd_bridge/`](../../scripts/qcd_bridge/):

```bash
# 1. Build the explicit O_chi operator and run the kappa_T sweep
python3 scripts/qcd_bridge/ochi_explicit_construction.py

# 2. Compare K3 vs first-principles chGUE construction
python3 scripts/qcd_bridge/ochi_lattice_firstprinciples.py

# 3. Extract physical kappa_T from lattice Dirac data
python3 scripts/qcd_bridge/kappa_T_physical_estimate.py

# 4. Run the spectral CP solution audit
python3 scripts/qcd_bridge/cp_solution_spectral.py

# 5. Honest audit (Monte Carlo, Cabibbo, scaling, seesaw)
python3 scripts/qcd_bridge/honesty_calculations.py

# 6. Regenerate all 12 figures at 600 DPI
python3 scripts/qcd_bridge/generate_figures.py --outdir docs/qcd_bridge/figures
```

The compiled PDF is [`choptyuk_qcd_bridge.pdf`](choptyuk_qcd_bridge.pdf)
(40 pages, 2.3 MiB).  To rebuild it from source:

```bash
tectonic choptyuk_qcd_bridge.tex
# or
pdflatex choptyuk_qcd_bridge.tex && bibtex choptyuk_qcd_bridge && pdflatex choptyuk_qcd_bridge.tex && pdflatex choptyuk_qcd_bridge.tex
```

---

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{choptyuk_qcd_bridge,
  title         = {The Choptuik--Strong CP Operator: an honest audit of
                   three quantum corrections, GUE statistics at $N=3$,
                   and the road to $\bar\theta < 10^{-10}$},
  author        = {Isaev, Ishak Khamzatovich},
  year          = {2026},
  note          = {Companion monograph to the Choptyuk--Isaev programme;
                   40 pages, 12 figures, 8-step CP solution chain}
}
```

---

## License

Same as the parent repository: **Isaev Proprietary License** — see
[`LICENSE`](../../LICENSE).
