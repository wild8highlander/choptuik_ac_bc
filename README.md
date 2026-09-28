# choptuik_ac_bc — Machine-Verified Verification Repository

**Critical collapse (Choptuik problem), spinor corrections, and the direct
route from the Hilbert action to the Einstein equations — with every claim
re-checked by machines.**

[![License: Proprietary](https://img.shields.io/badge/License-Isaev%20Proprietary-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Julia 1.9+](https://img.shields.io/badge/Julia-1.9+-955880.svg)](https://julialang.org/)
[![Java 17+](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

> Author: **Ishak Khamzatovich Isaev** · ORCID 0009-0003-7299-0701
> Monograph: *Spinor corrections b-C and a-C and the solution of the Choptuik
> problem* — rigorous computation of spectral invariants on the Klein quartic
> curve with applications to LIGO/Virgo quasi-normal mode predictions.

---

## 1. What this repository is

This repository is a **verification laboratory**. Its purpose is to check
computations — symbolic derivations, numerical critical-collapse campaigns,
spectral towers and static censuses — by machine, and to publish the results
together with their honest caveats.

The core discipline, applied everywhere:

> **hypothesis → machine confirmation → honest caveats and limitations.**

Nothing is fitted to literature values. Agreements with published constants
(γ_Ch = 0.374, b_Ch = 0.37651, the spinor ladder π/30) are *reported as
comparisons*; walls, floors and negative verdicts are *kept as first-class
results*. Each campaign writes machine-readable JSON outputs, and a pytest
suite re-checks the major theorems from those outputs.

The flagship of the repository is the [`einstein_direct/`](einstein_direct/)
laboratory: a complete, self-contained pipeline that solves the **Choptuik
critical collapse problem** (massless scalar field, spherical symmetry)
*directly* from the classical Einstein equations obtained by varying the
**Hilbert action** — without spectral constructions, ansätze or fitted
parameters.

---

## 2. The verification dossier

The single most detailed document of the repository is the verification
dossier:

**[`verification/README.md`](verification/README.md)** — a very large,
self-contained English dossier covering *every* verification campaign:
what is verified, by which machine, with which method, which numbers came
out, what the verdict is, which caveats apply, and the exact commands to
reproduce it.

Highlights of what has been verified (all numbers are machine outputs, none
are fitted):

| Verification | Result |
|---|---|
| Hilbert action → Einstein equations (SymPy, 50 digits) | residuals ≈ **10⁻⁴¹** vs the exact Roberts–Oshiro solution |
| Solver validation | flat space **10⁻¹⁴**; 5/5 regression tests |
| Critical amplitude (fixed grid, N = 1600) | **A\* = 0.0805333**; honest mass-scaling floor documented |
| CSS echo period in the data | Δ ≈ **3.44** (Gundlach–Hodgson 3.44 ± 0.02) |
| Thorne hoop link in the data | M3/(R1·t0²) = **0.6687** vs exact 2/3 (**0.3%**) |
| Log-time tower books | τ_UV = 9/4 and τ_Mdef = 9/16, ratio **exactly 4** |
| Clock-pair theorem | exact on **12/12** bricks, `τ*(δ) = 27/(2−δ²)` |
| One-brick Berry screening (δ_C = π/7) | closes ln τ\* from **−2.57%** to **+0.062%** |
| Global static census | **zero** non-degenerate static branches beyond the known families; the static structure is exhausted exactly |
| Nonlinear DAE march | the only solution manifold through the critical point is the flat line of equilibria |
| Verification suite | **21/21 tests** re-checking machine theorems |

---

## 3. Repository map

| Directory | Content |
|---|---|
| [`einstein_direct/`](einstein_direct/) | **core verification laboratory**: machine-verified derivation, characteristic solver, zoom campaigns, the PDE machine suite (finite-amplitude echo on three static families), brick ladder, global static census, JSON results, 300 dpi figures, pytest suite |
| [`verification/`](verification/) | the big verification dossier (English) |
| [`python/`](python/) | full verification & simulation suite for the monograph (Python, CLI with interactive menu) |
| [`julia/`](julia/) | full verification & simulation suite (Julia, REPL with interactive menu) |
| [`java-webapp/`](java-webapp/) | web application (Spring Boot REST API + web UI) |
| [`interactive-viz/`](interactive-viz/) | interactive visualization (Next.js + React dashboard) |
| [`code/`](code/) | compact cross-language code companions (Python/Julia/Java/web) |
| [`audit_transfer/`](audit_transfer/) | the "audit and transfer" appendix: audited core, lemma article, figures, LaTeX sources |
| [`qcd_bridge/`](qcd_bridge/) | QCD-bridge artifacts and evidence |
| [`dsi_lab/`](dsi_lab/) | DSI laboratory notebooks and results |
| [`monograph/`](monograph/), [`docs/`](docs/) | the monograph PDFs and documentation |
| [`docs-site/`](docs-site/) | MkDocs documentation site sources |
| [`notebooks/`](notebooks/) | computational notebooks |
| [`scripts/`](scripts/) | repository-level runners and utility scripts |
| [`termux/`](termux/) | run the whole pipeline on Android (Termux) and publish from the phone |
| [`docker/`](docker/), [`.devcontainer/`](.devcontainer/) | containerized environments |

Each directory carries its own detailed `README.md` (English).

---

## 4. Quick start

### 4.1 The verification suite (fast, ~seconds)

```bash
cd einstein_direct
python3 -m pip install numpy scipy sympy matplotlib pytest
python3 -m pytest tests/ -q
# 21 passed
```

### 4.2 The symbolic derivation (machine-verified)

```bash
cd einstein_direct
python3 sympy_derivation.py     # Hilbert action → Einstein equations
python3 roberts_test.py         # exact-solution regression
```

### 4.3 Numerical campaigns

```bash
python3 choptuik_scaling.py --n-bisect 1200     # fixed grid: A*, scaling
python3 zoom_campaign_regular.py                # zoom campaign, ~5–8 min
python3 grid_machine_annulus.py                 # the PDE machine suite
python3 global_static_search.py                 # static census
```

### 4.4 Monograph verification suites

```bash
python3 -m pip install -r python/requirements.txt   # see python/README.md
(cd python && python3 main.py)                      # interactive CLI

julia --project=julia -e 'include("julia/main.jl")' # interactive REPL
```

### 4.5 On a phone (Termux)

```bash
bash termux/01_termux_install.sh      # once per device
bash termux/02_termux_run.sh          # full pipeline (~1 h)
bash termux/02_termux_run.sh --quick  # ~15 min, same protocol, coarser grids
```

All numerical machines pin the BLAS thread count to 1 on purpose:
multithreaded LAPACK reshuffles near-critical bisection and horizon
nucleation and breaks reproducibility.

---

## 5. Scientific background in one minute

A spherically symmetric massless scalar field, numerically evolved in
1+1 double-null coordinates, shows **critical collapse**: below a critical
amplitude A the pulse disperses, above it a black hole forms, and near the
critical amplitude the black-hole mass scales as
`M ∝ (A − A*)^γ` with a universal γ ≈ 0.374 (Choptuik). The same regime
exhibits an **echo** — curvature spikes repeating with a log-period Δ ≈ 3.44.

This repository attacks the problem *directly*: derive the 1+1 double-null
Einstein system from the Hilbert action symbolically (machine-verified),
evolve it with a validated characteristic solver, push log-scale depth by
multi-zoom regridding, and measure the echo, the clocks and the static
backgrounds — reporting agreements *and* disagreements with equal honesty.
Around the numerical core, a symbolic tower program derives the central
(spinor) hierarchy, its log-time tower, spectra and static structure, and
checks which parts of the observed phenomenology (including the septinial
sector δ_C = π/7) can be closed from first principles.

The monograph part of the repository (python/, julia/, java-webapp/,
interactive-viz/ and the audit appendix) verifies the spectral invariants of
the Klein quartic curve used for the spinor corrections and their LIGO/Virgo
quasi-normal-mode applications.

---

## 6. Documentation index

| Document | Content |
|---|---|
| [`verification/README.md`](verification/README.md) | **the verification dossier** (very large, English) |
| [`einstein_direct/README.md`](einstein_direct/README.md) | the core laboratory: summary, file map, how to run |
| [`einstein_direct/README_EN.md`](einstein_direct/README_EN.md) | the deep 29-section technical ledger |
| [`einstein_direct/INSTALL_AND_PUSH.md`](einstein_direct/INSTALL_AND_PUSH.md) | installation and running notes |
| folder `README.md` files | one detailed English readme per directory |

## 7. License and citation

The repository is distributed under the proprietary license in
[LICENSE](LICENSE) (author: I. Kh. Isaev). For citation use
[CITATION.cff](CITATION.cff) or the ORCID above. Bug reports and
reproduction issues are welcome through the issue tracker; the
[CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md) policies apply.
