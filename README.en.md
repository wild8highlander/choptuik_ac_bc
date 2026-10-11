<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/choptyuk_logo_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo/choptyuk_logo_light.png">
  <img alt="Choptuik AC-BC — Spinor corrections b-C &amp; a-C, the Choptyuk problem, and the Direct Einstein programme" src="assets/logo/choptyuk_logo_dark.png" width="100%">
</picture>

# Spinor Corrections b-C & a-C, the Choptyuk Problem, and the Direct Einstein Programme

**Choptuik AC-BC is a single machine-verified research programme:** from the spectral
invariants of the Klein quartic curve and the spinor corrections **b-C / a-C** — through
Choptuik critical gravitational collapse, attacked *directly* from the Einstein equations —
to black-hole thermodynamics (the Collapse–Hawking Bridge) and quark confinement
(the Quark–Hawking Bridge).

**Author & maintainer:** Ishak Khamzatovich Isaev — GitHub [@wild8highlander](https://github.com/wild8highlander) ·
ORCID [0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701) · Nalchik, Kabardino-Balkarian Republic *(sole author of all materials)*

[![License: Isaev Proprietary](https://img.shields.io/badge/License-Isaev%20Proprietary-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)](python/)
[![Julia 1.9+](https://img.shields.io/badge/Julia-1.9+-955880.svg?logo=julia)](julia/)
[![Java 17+](https://img.shields.io/badge/Java-17+-orange.svg?logo=openjdk)](java-webapp/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg?logo=next.js)](Interactive%20Viz/)
[![Lean 4 + Mathlib](https://img.shields.io/badge/Lean%204-Mathlib-6b2c8f.svg?logo=lean&logoColor=white)](QHB/monolith/lean/)
[![CI](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/ci.yml/badge.svg)](https://github.com/wild8highlander/choptuik_ac_bc/actions/workflows/ci.yml)
[![DOI](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.15152720-blue.svg?logo=zenodo)](https://doi.org/10.5281/zenodo.15152720)
[![Tests: ED](https://img.shields.io/badge/Tests%20ED-58%2F58%20%2B10-brightgreen.svg)](Einstein%20Direct/tests/)
[![Tests: CHB](https://img.shields.io/badge/Tests%20CHB-63%2F63-brightgreen.svg)](Collapse%20Hawking%20Bridge/tests/)
[![Tests: QHB](https://img.shields.io/badge/Tests%20QHB-154%20collected-brightgreen.svg)](QHB/tests/)

> 🇬🇧 **Language:** this is the compact English edition. The full flagship README is in Russian:
> [`README.md`](README.md). Russian mirrors inside packages:
> [`Collapse Hawking Bridge/README.ru.md`](Collapse%20Hawking%20Bridge/README.ru.md) · [`QHB/README.ru.md`](QHB/README.ru.md)

> [!IMPORTANT]
> **The discipline of the repository — one rule, applied everywhere:**
> **hypothesis → machine confirmation → honest caveats.**
> Nothing is fitted to literature values. Agreements with published constants
> (γ_Ch = 0.374, b_Ch = 0.37651, the echo period Δ ≈ 3.44, the spinor ladder π/30) are
> *reported as comparisons*, never as targets of a fit. Walls, floors, obstructions and
> **negative verdicts are kept and documented** with the same care as positive results.
> Mistakes found later are **retracted publicly** (ERRATUM). Every campaign writes
> machine-readable JSON, and a pytest suite re-checks the theorems from those files.
> *Machine-readable or it did not happen.*

---

## The repository in numbers

| Metric | Value | Note |
|---|---|---|
| Tracked files | **1 793** (~369 MB) | 7 programming languages |
| Source code | **274** Python · **19** Julia · **21** Java · 82 TSX + 25 TS · C/C++/Rust/Go/JS twins | cross-language verification |
| Automated tests | **360+** pytest (58+10 Einstein Direct · 63 CHB · 154 QHB · 78 `python/` · dsi_lab) + **16** Julia testsets + **18** closed Lean kernels | every test pins numbers from JSON verdicts |
| JSON campaign verdicts | **94** (47 Einstein Direct · 29 CHB · 31 QHB) | each with the full run configuration |
| Monographs & publications | **71** DOCX · **110** PDF (incl. the **80**-file cycle of 20 theorems) | |
| Figures | **513** PNG (300–600 DPI, RU/EN × light/dark) | "Ink & Gold" style, generated from JSON |
| Animations | **46** (23 GIF + 23 MP4) | CHB 4×RU/EN · QCD Bridge 9×4D · QHB legacy 3×RU/EN |
| Research programmes | **8** + infrastructure | see the map in the Russian README |
| Machine theorems | **20** (theorems12) + **10** (CHB T1–T10) + **20** (QHB T1–T20) | each with a verdict and a falsifier |
| Independent audits | IVP-15 (CHB) · IVP-12 (QHB) · IVP-11 (legacy) · OPEN9 (ED) | blind checks outside the committed results |
| GitHub Actions workflows | **11** | CI matrix, lint, Pages, Release, Scorecard, … |
| Runs on a phone | ✅ Termux/Android | open9 standalone + push kit |
| License | Isaev Proprietary (individual) | [LICENSE](LICENSE) |

## The science in 60 seconds

A massless scalar field evolved in 1+1 double-null coordinates shows **critical
collapse**: below a critical amplitude $A^*$ the pulse disperses, above it a black hole
forms, and near the threshold the mass scales as $M \propto (A-A^*)^{\gamma}$ with the
universal exponent **γ ≈ 0.374** (Choptuik 1993). The same regime exhibits an **echo** —
curvature spikes repeating with log-period **Δ ≈ 3.44**.

This repository attacks the problem *directly*: the 1+1 double-null Einstein system is
derived symbolically from the Hilbert action (SymPy, residuals ≈ 10⁻⁴¹ against the exact
Roberts–Oshiro solution), evolved with a validated characteristic solver, and pushed to
log-scale depth **z = 9.35** by multi-zoom regridding — reporting agreements *and*
disagreements with equal honesty. Around the numerical core stands a **symbolic tower**:
the central hierarchy O1–O5, the exact spectrum {0, −1, −1, −2, −3}, the clock-pair
theorem $\tau^*(\delta) = 27/(4-\delta^2)$ on 12/12 bricks.

The **monograph line** computes the spectral invariants of the Klein quartic curve
(genus 3, PSL(2,7) of order 168) and builds the spinor corrections **b-C / a-C** to the
Dirac operator, with applications to LIGO/Virgo QNM frequencies and the strong CP problem.
The **2026 bridges** extend this universality further: the **Collapse–Hawking Bridge**
(dimensionless birth profile → Hawking thermodynamics, IVP-15 audited) and the
**Quark–Hawking Bridge** (confinement as false-vacuum escape, T(0) = 9.21×10⁻¹³ as the
no-free-quarks gate, 18 closed Lean/Mathlib kernels).

## ★ The three corrections and their universality

One structural pair — Berry quantum $\beta(d)=d^2/2$ and braking quantum
$\alpha(d)=d^5/22$ (with the structural divisor $k=b_2(K3)=22$) — applied to the three
septinial phases $\pi/2,\ \pi/3,\ \pi/7$, produces **all** correction constants of the
programme:

| Sector | Phase | Berry | Braking | Where it appears |
|---|---|---|---|---|
| **A** | π/2 | $\pi^2/8$ | $\pi^5/704$ | QHB bridge temperature: correction **+11.280569950484875 %** at β* (100-digit mpmath, Lean kernel T4) |
| **B** | π/3 | $\pi^2/18$ | $\pi^5/5346$ | spectral-sector hierarchy of the gap law: **≈ 1865 : 1** (r² = 0.99999982) |
| **C** | π/7 | $\pi^2/98$ | $\pi^5/369754$ | the Choptyuk constant $b_{Ch}=1-\cos(2\pi/7)=0.37651019814126640$; unified formula $\Delta_{Ch}$; QNM factor $1-1/(1200\pi^2)$; anchor $\Delta\cdot\gamma$; strong CP $\bar\theta_{eff}=0$ |

Each appearance is checked by its own machine verdict — and each remains a
*comparison*, never a fit. Full derivations step by step: the Russian README,
section «Три поправки и их универсальность».

## Programmes

| # | Programme | Directory | Highlights |
|---|---|---|---|
| I | **Monograph suite** (4 implementations) | [`python/`](python/) · [`julia/`](julia/) · [`java-webapp/`](java-webapp/) · [`Interactive Viz/`](Interactive%20Viz/) | Klein quartic, Dirac operator, 64 spinor structures, 7-format reports; **78** pytest + **16** Julia testsets |
| II | **Einstein Direct** | [`Einstein Direct/`](Einstein%20Direct/) | Hilbert action → Einstein equations (10⁻⁴¹); z = 9.35 depth record; clock-pair theorem; OPEN9 closed 9/9; **58+10 tests**, 47 JSON verdicts |
| III | **theorems12** | [`theorems12/`](theorems12/) | **20 theorem-monographs** (EN + RU, DOCX + PDF = 80 files), every statement traceable to a machine output |
| IV | **Collapse Hawking Bridge** v2.1.0 | [`Collapse Hawking Bridge/`](Collapse%20Hawking%20Bridge/) | $M_{BH}=M_{in}\cdot\tilde f(\varepsilon)$; campaigns C1–C3b+C6; audit **IVP-15** (3 FAILs found → remediated); Page curve; CMB contact 4.5016e22 kg; **63 tests**, 7-language twins (7.08e-13), 68 hi-res figures, 14-sheet workbook |
| V | **QHB — Quark–Hawking Bridge** v2.3.0 | [`QHB/`](QHB/) | confinement = false-vacuum escape; campaigns C1–C12; registry of **30 claims** with falsifiers; **Lean 4 / Mathlib: 18 closed kernels**, CI fails on `sorryAx`; external bounds X1–X13; Iron-QA gates; **154 collected tests** |
| VI | **QCD Bridge Suite** (Strong CP) | [`docs/qcd_bridge/`](docs/qcd_bridge/) · [`code/`](code/) · [`QCD Bridge/`](QCD%20Bridge/) | $\bar\theta_{eff}=\delta_C\,N\langle\lambda\rangle\,\mathcal S_{GUE}=0$ (BF ≥ 99 at κ_T > 2.62); 9 sections; **55 figures + 19 4D animations**; 7-format reports × 2 engines |
| VII | **DSI laboratory** | [`dsi_lab/`](dsi_lab/) | 7 deterministic experiments; findings D1 (Hurwitz tower) and E1 (GUE centering) |
| VIII | **Audit & Transfer appendix** | [`audit_transfer/`](audit_transfer/) | monograph audit (typos E1–E7); closure $c_{K3}=1-\cos(2\pi/22)$; stability lemma Sh.3 (F ≥ n/2, sharpness 5n/7) |

> [!WARNING]
> Status disclaimers: the QNM values are a *hypothesis-model estimate*, not a prediction;
> the strong-CP chain is a *hypothetical framework*, not an established solution;
> $A^*_\infty$ is *not claimed* (the drift is honest); Δ_eff = 0.611 ± 0.446 is honestly
> **not DSS** (3.44 excluded at 6.3σ).

## Quick start

```bash
# Einstein Direct verification suite (seconds)
cd "Einstein Direct" && python3 -m pytest tests/ -q            # 58 passed

# Collapse Hawking Bridge
cd "Collapse Hawking Bridge" && make test validate data        # 63 passed, 7/7 mpmath, byte-identical data

# QHB (canonical + Lean)
cd QHB && make all && python3 -m pytest tests/ -q              # 154 collected
cd monolith/lean && lake build && lake env lean QHB_AxiomAudit.lean   # 18 kernels, no sorryAx

# Monograph stack (4 implementations)
cd python && pip install -r requirements.txt && python run.py  # interactive CLI
cd "Interactive Viz" && npm install && npm run dev             # http://localhost:3000
```

Online demo: <https://wild8highlander.github.io/choptuik_ac_bc/> ·
Full reproduction index (claim → command → JSON): the Russian README,
section «Индекс воспроизведения» · Verification dossier: [`verification/README.md`](verification/README.md).

## Honesty ledger (headline entries)

| Verdict | Statement | Where |
|---|---|---|
| **Proven (exact)** | Clock-pair theorem $\tau^*(\delta)=27/(4-\delta^2)$ on 12/12 bricks | ED v17/v18, theorems12 №1–2 |
| **Proven (exact)** | Static structure exhausted: factorization + census, 0 new branches | ED v18, theorems12 №3/№9 |
| **Proven (exact)** | CHB: Page τ* = 1−2^(−3/2); CMB contact 4.5016e22 kg; drift law T10 | CHB theorems T1–T3, T9–T10 |
| **Proven (exact)** | QHB: T19 splitting identity (Mathlib); vortex spectrum {0, 0, ±iω, ±iω} | QHB Lean kernels |
| **Confirmed** | One brick closes ln τ* to +0.062% | ED v11/v17 |
| **Confirmed** | Depth wall is window-policy sensitive (z 1.78 → 7.20 → 8.56 by root anchor) | ED v21/v22 |
| **Rejected** | The tick does NOT select the brick (minimum at k = 12) | ED v18 |
| **Rejected** | DSS for the 4-peak quartet: Δ_eff = 0.611 ± 0.446, 3.44 excluded at 6.3σ | ED v22 |
| **Retracted** | v16 "static backbone" (ERRATUM [A0]); v17 [C3] basis-dependent r_max (ERRATUM); CHB false 1.06e-6 convergence (F-1); QHB T20 sign (erratum v2.3.0) | honesty ledgers of the packages |

## Citation

```bibtex
@book{isaev2024spinor,
  title   = {Spinor corrections b-C and a-C and the solution of the Choptyuk problem},
  author  = {Isaev, Ishak Khamzatovich},
  year    = {2024},
  address = {Nalchik, Kabardino-Balkarian Republic}
}
```

Zenodo DOI: [10.5281/zenodo.15152720](https://doi.org/10.5281/zenodo.15152720) ·
machine-readable metadata: [`CITATION.cff`](CITATION.cff).

## License & authorship

**Isaev Proprietary License** — see [LICENSE](LICENSE): you may view and cite the work
for academic reference, but you may NOT copy, modify, distribute, or use it commercially
without the author's written permission. This is a **single-author repository** — all
research, code, verification campaigns and documentation are the work of
Ishak Khamzatovich Isaev ([@wild8highlander](https://github.com/wild8highlander));
governance model: [GOVERNANCE.md](GOVERNANCE.md) · support: [SUPPORT.md](SUPPORT.md).

## Acknowledgments

Bourque & Strohmaier (2024) for λ₁(Δ) on the Klein quartic · Choptuik (1993) and the
critical-collapse community (Gundlach, Garfinkle, Duncan, Brady, Hirschmann, Hod) ·
Gundlach & Hodgson for the echo reference 3.44 ± 0.02 · Thorne (hoop-conjecture mass
route) and Misner–Sharp (mass definitions) · the LIGO/Virgo Collaboration · the PSL(2,7)
symmetry group · the Sakharov conditions as the reading lens · the SymPy, NumPy, mpmath,
Julia and Lean 4 / Mathlib communities.

---

<p align="center"><sub>
🇷🇺 <b>Full README (Russian, flagship):</b> <a href="README.md">README.md</a> — mind maps, animations, all 20 theorems, campaign ledgers, GitHub features map.
</sub></p>
