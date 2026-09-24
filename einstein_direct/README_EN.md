# einstein_direct — Direct Solution of the Choptuik Problem from the Classical Einstein Equations

**Module status: v3 (zoom campaign v2). Hilbert-action derivation machine-verified; 2nd-order characteristic solver validated; fixed-grid critical point and mass-scaling floor analyzed; multi-zoom regridding machine rebuilt (v2) and pushed to z ≈ 5.2 with the remaining depth wall precisely diagnosed.**

This folder contains a complete, self-contained numerical laboratory that solves the
**Choptuik critical collapse problem** (massless scalar field, spherical symmetry)
*directly* — i.e. from the classical Einstein equations obtained by varying the
Hilbert action with the Hilbert stress–energy tensor — without any spectral
constructions, ansätze or fitted parameters.

Everything below is reproducible on an ordinary laptop (and on a phone via
Termux, see §10) with Python ≥ 3.9, NumPy, SciPy, SymPy and pytest.

---

## Table of contents

1. [Physics background](#1-physics-background)
2. [What "direct" means here](#2-what-direct-means-here)
3. [Machine-verified derivation (SymPy)](#3-machine-verified-derivation-sympy)
4. [The 1+1 double-null system and the solver](#4-the-11-double-null-system-and-the-solver)
5. [Validation suite](#5-validation-suite)
6. [Fixed-grid campaign: critical amplitude and the mass-scaling floor](#6-fixed-grid-campaign)
7. [Multi-zoom regridding machine v2](#7-multi-zoom-regridding-machine-v2)
8. [The depth wall: precise diagnosis and fix roadmap](#8-the-depth-wall)
9. [Honest comparison with the b_Ch = γ hypothesis](#9-honest-comparison-with-the-b_Ch--γ-hypothesis)
10. [Running everything (incl. Termux on Android)](#10-running-everything)
11. [File map](#11-file-map)
12. [References](#12-references)

---

## 1. Physics background

**Critical gravitational collapse.** Take a massless scalar field Φ in
3+1-dimensional general relativity, spherical symmetry, and a one-parameter
family of smooth initial data `Φ(u₀, v) = A·exp(-(v-v_p)²/(2σ²))` (a Gaussian
pulse sent into collapse). Choptuik (1993) discovered that between black-hole
formation (large `A`) and complete dispersal (small `A`) there is a critical
amplitude `A*` with two astonishing universal properties:

* **Critical exponent.** For supercritical data the black-hole mass vanishes
  according to a power law
  `M_BH = C · (A - A*)^γ`, with `γ ≈ 0.374` universal (independent of the
  initial-data family).
* **Discrete self-similarity (DSS).** The near-critical solution repeats itself
  on ever smaller scales: the echoing period is `Δ ≈ 0.737` in ln-scale, i.e.
  each echo shrinks the spacetime structure by a factor `e^Δ ≈ 2.09`. After
  `N` echoes the curvature grows like `e^{2κNΔ}` with a wiggle exponent
  `κ ≈ 0.185`.

The critical solution accumulates at a point; resolving `N` echoes requires
resolving scales down by `e^{NΔ}` — for `N ≈ 10` echoes that is 4+ decades of
linear scale. This is why the problem is a standard benchmark for adaptive
mesh refinement in numerical relativity.

**Why this module exists.** The surrounding repository (`choptuik_ac_bc`)
contains a spinor-framework monograph that proposes `b_Ch = 1 - cos(2π/7) =
0.37651` as the value of the Choptuik exponent — a 0.67 % deviation from the
literature value `γ ≈ 0.374`. Deciding whether that 0.67 % means anything
requires an *actual* independent numerical solution of the collapse problem —
which the repository previously did not contain. This module builds one from
first principles and reports **honestly** what its resolution can and cannot
decide.

## 2. What "direct" means here

No shortcuts are taken anywhere in the pipeline:

* The field equations are **derived symbolically** from the Einstein–Hilbert
  action with the *Hilbert* stress–energy tensor (not the "improved" or
  potential-based forms) — the same `T_μν` that the monograph's framework
  must reproduce.
* The reduction to 1+1 dimensions is done by the computer: every equation that
  the solver integrates has been **checked against SymPy** and against the
  exact Roberts–Oshiro solution to ~50 significant digits.
* The solver uses **no fitted constants**: `κ = 8πG = 2` (the Burko 1996
  normalization, `4πG = 1`) is the only scale choice, and it is a units
  convention, not a parameter.
* Every claimed number in this README is written to `results/*.json` by the
  scripts that produce it.

## 3. Machine-verified derivation (SymPy)

`sympy_derivation.py` performs and checks the full chain:

1. **Hilbert action** `S = (2κ)⁻¹ ∫ √-g R - ½ ∫ √-g (∇Φ)²`.
2. Variation with respect to `g^{μν}` → Einstein equations with the **Hilbert
   TÉI** `T_μν = ∂_μφ ∂_νφ - ½ g_μν (∇φ)²`. (A subtlety worth archiving:
   the coefficient 2 in the `r_uu` constraint below is routinely dropped in
   hand derivations; the machine keeps it.)
3. **Double-null ansatz** `ds² = -α²(u,v) du dv + r²(u,v) dΩ²`, `ω := ln α`,
   Misner–Sharp mass `m`. The `φφ`/`θθ` components are checked to be
   equivalent (`R_φφ = sin²θ R_θθ`), and the Bianchi identity
   `∇_μT^μ_ν = Φ_μ □φ` is verified symbolically — the wave equation is not put
   in by hand, it *follows*.
4. The resulting closed 1+1 system (see §4) is evaluated on the **exact
   Roberts–Oshiro solution** (in Burko's corrected form; the original Roberts
   form contains a coordinate-transform error, see gr-qc/9608061). Maximum
   residual over all five equations: **4·10⁻⁴¹** (mpmath, 50 digits).

The full log is `results/derivation_log.txt`, the machine summary is
`results/derivation_results.json`.

## 4. The 1+1 double-null system and the solver

The system integrated by `solver.py` (machine output of §3):

```
(SC)  Φ_uv  = -(r_u Φ_v + r_v Φ_u) / r
(UV)  r_uv  = -(r_u r_v + α²/4) / r  =  -α² m / (2 r²)
(C1)  r_uu  = 2 ω_u r_u - (κ/2) r Φ_u²        ← the coefficient 2 matters!
(C2)  r_vv  = 2 ω_v r_v - (κ/2) r Φ_v²
(TH)  ω_uv  = α² m / (2 r³) - (κ/2) Φ_u Φ_v
 m   ≡ (r/2)(1 + 4 r_u r_v / α²)              (Misner–Sharp)
```

Regularizing identities used to keep the system well-behaved at the center
`r = 0` (where `r` changes sign in the mirror extension):

```
(r²)_uv = -α²/2,     P := r r_u :  P_v = -α²/4,
m_u = -κ r² Φ_u² r_v / α²,   m_v = -κ r² Φ_v² r_u / α²
```

**Numerical method.** Goursat characteristic march over `v`-rows, RK2-Heun
predictor–corrector with an iterated implicit trapezoid solve of the `t = Φ_v`
ODE along `u` (vectorized log-cumsum recurrence), exact center regularity
`t = s` (`s = Φ_u`), explicit mirror march for `u > v`, Misner–Sharp mass
evolved by the regularizing identities (no catastrophic cancellation), NaN
masking, apparent-horizon detection from `q = r_v` zero crossings at resolved
radius `r > 8 du`, and run-level stops on AH-mass saturation. The grid-level
safeguard `r_floor = du/2` in every `1/r^k` denominator removes a real
stiffness discovered during this session (see §7.3): the *evolved* mass in the
`r → 0` cell is inconsistent with `r ~ 10⁻¹⁴`, which previously produced spikes
`w = α²m/(2r³) ~ 10²⁰` that leaked through `cumtrapz` into `ω_v` and blew up
the mirror half of the solution.

## 5. Validation suite

`pytest tests/test_einstein_direct.py` (all green, ~1.5 s):

| Test | What it proves |
|---|---|
| `test_flat_space_machine_precision` | `A = 0` evolution stays Minkowski to `8.8·10⁻¹⁵` |
| `test_roberts_solution_satisfies_system` | the exact solution closes the machine-derived system |
| `test_subcritical_disperses` | `A = 0.03` disperses, no horizon, clean completion |
| `test_supercritical_forms_horizon` | `A = 0.45` forms an AH with `M ≈ 0.041` (≈39 % of the pulse energy, physically sensible), AH mass `< 0.05` |
| `test_misner_sharp_definition_consistency` | the mass definition and its evolution agree to `1e-10` |

Convergence (measured in session 1 on the Roberts evolution): 2nd order,
`p = 2.03–2.09` for `r`, `1.99` for `Φ`; the C1 constraint violation decreases
quadratically with the grid.

## 6. Fixed-grid campaign

`choptuik_scaling.py` (results in `results/choptuik_scaling.json`):

* **Critical amplitude** by bisection at `N = 1600`: `A* = 0.0805333`.
* **Mass scaling**: the measured black-hole masses *floor* at `M ≈ 4·du`
  (horizon nucleation threshold: an apparent horizon is only trusted at
  `r > 8·du`, so a black hole with `2M < 8·du` is unresolvable). The fixed
  grid therefore measures `γ_num = 0.11 ± 0.11` — **a resolution artifact, not
  physics**, and the honest conclusion of session 1.

This floor is exactly what the multi-zoom machine (§7) is designed to break:
each zoom stage shrinks `du` by `λ ≈ 3–6`, so the mass floor drops
exponentially with the number of zooms.

## 7. Multi-zoom regridding machine v2

`zoom_solver.py` implements adaptive regridding in the spirit of Choptuik's
original work. One *run* consists of stages; when the active structure
compresses, the window is re-centered, shrunk, and the fields are interpolated
(cubic, 2-D) from a row buffer onto the new grid; the evolution continues.
The log-scale depth `z = Σ ln(du_old/du_new)` measures the total scale reach;
DSS echoes live at equal spacing `Δ` in `z`.

### 7.1 What v2 fixed relative to v1

1. **Trigger redesigned.** v1 triggered on a gradient scale `L_grad` that the
   *regular converging wave* (`t ~ 1/r` near the center) defeats: the maximum
   of `|Φ_u|` sits at the mask boundary and the measured "width" is a
   mask artifact (~10 cells) from the first row. v2 triggers on
   **width < 45 cells AND width shrinking** (compared within-stage, 20 rows
   apart) — the `1/r` artifact has constant cell-width and can never fire it.
   Additionally the width measurement masks the clamp zone (`r > 12·du`).
2. **Drift-aware window placement.** The collapsing feature drifts toward
   `+u`; v2 places the feature at 30 % from the window's left edge, forces the
   window to **contain the center line** `u = v` (the domain of dependence of
   the collapse), and clips into the parent domain. v1 centered the window and
   then permanently lost the zoom right (the "u_hi" refusal) once the feature
   approached the right edge.
3. **Telescoping v-budget.** v1 allowed the new stage's `v`-range to exceed
   the covered buffer and silently *extrapolated* garbage into the restart.
   v2 caps `v_hi ≤ parent v_hi` and marches the parent forward to cover the
   new window before interpolating.
4. **v-extension.** If a stage's `v`-grid is exhausted without a trigger, the
   window is translated forward (`λ = 1`) instead of killing the run.
5. **First-sustained AH mass.** The black-hole mass is frozen at the first
   horizon that persists ≥ 6 rows (`M_AH`), while the running maximum
   (`M_AH_max`) is kept only as a diagnostic. Post-formation accretion no
   longer contaminates the scaling observable.
6. **DSS tracking.** Every row records `v, mx = max 2m/r, Q = max 2m/r²,
   L_grad, width, u_focus, du, z` — the raw material for echo-peak analysis
   (`echo_peaks`, `echo_period_from_peaks`).

### 7.2 Result: chain depth

With the v2 machine the near-critical runs march **cleanly through 3 zooms to
`z ≈ 5.2`** (v1 managed 2 zooms and `z ≈ 1.5`), with the mass aspect bounded
(`mx ≤ 0.082`, no junk explosions) — see
`results/zoom_campaign.json`, field `runs`.

### 7.3 Real bugs found and fixed this session (for the record)

* **`r_floor` stiffness (solver-level, fixed).** In the `r → 0` cell the
  *evolved* `m` is not consistent with `r ~ 1e-14`; the denominators
  `m/(2r³)`, `m/(2r²)` produced spikes `w ~ 10²⁰` that `cumtrapz` smeared into
  `ω_v = d` over the whole mirror half (`d ~ 3·10¹⁷`), after which
  `q_v = 2dq` exploded. Fix: `r_floor = du/2` in all `1/r^k` denominators;
  validated to leave the strong-field benchmark unchanged (`M = 0.04109` vs
  `0.04108`).
* **`w/d` recompute trap.** Recomputing `w` and `d` *after* the `t`-march
  propagates the march's fresh central junk through `w ~ s·t` into `d`. The
  validated order (compute `w, d` before the `t`-solve) must be preserved.
* **Center heals: helpful for strong fields, harmful for the zoom chain.**
  The per-cell parity heal (`t,s ← (t+s)/2`) and the deep restart heal
  (even-limit reconstruction + `m ∝ r³`) both pass the validation suite and
  clean the restart row (post-zoom C1 ~ 10⁻¹³ near the center), but for
  near-critical collapse they **suppress the central compression** and shorten
  the chain. They are therefore flag-controlled (`heal_enabled`) and disabled
  inside the zoom machine; the flagship test `A = 0.45` keeps them on.

## 8. The depth wall

At `z ≈ 5.2` (3 zooms) every run terminates in a NaN/"singularity" stop before
the genuine horizon forms. The diagnosis, established by direct field dumps
this session, is precise:

1. **The center closure is incomplete.** The exact regularity condition is not
   `t = s` but `p·t + q·s = O(r)`; at `r = 0` this reduces to `t = s` *and*
   `p = -q`. The clamp enforces only `t = s` while the numerical `p + q ≠ 0`
   at the center cells, so the SC evolution develops the explosive term
   `s_v = -(p+q)s/r ~ 2c'·s` — with the contraction rate `c' ~ 1/ℓ` of the
   collapsing configuration, this term grows exactly when the physics gets
   interesting. Marching `t` outward from the center (stable for the `1/r`
   mode) was implemented and is *not sufficient by itself*: the `s`-equation
   stiffness remains because the `s₁ − t₁` radial-slope relation is not
   imposed.
2. **The `1/r` mode cannot be filtered locally.** The implicit edge→center
   march amplifies its homogeneous mode ∝ `1/r`; but the *physical* converging
   wave also amplifies ∝ `1/r`, so a two-parameter fit `t−s = A/r + B·r`
   subtracts physics along with the junk (verified: strong-pulse validation
   breaks).
3. **Restart contamination scales up.** The parent's clamp layer
   `[0, 5·du_parent]` becomes `5λ·du_child` cells after interpolation — the
   inherited junk zone *grows* by `λ` per zoom in cell terms.

**Fix roadmap (v3, the path to percent-level γ and Δ):** implement the
**center ODE** — integrate the regular expansion at the center
(`Φ₀(v), s₀ = t₀ = Φ̇₀/2`, plus the radial second derivatives) as an internal
boundary condition, march `t` outward, and derive the `s₁ − t₁` closure from
the center system (this is the essence of Choptuik's 1993 scheme). With that
closure the restarts become clean, the chain is expected to reach
`z ≈ 10–12` (5–7 zooms, 6–8 echoes), which is exactly the depth needed for
percent-level `γ` and a reliable `Δ` from echo-peak spacing.

## 9. Honest comparison with the b_Ch = γ hypothesis

| Quantity | Value | Status |
|---|---|---|
| `γ` (literature, Choptuik 1993 / Gundlach) | `0.374 ± 0.004` | reference |
| `b_Ch = 1 − cos(2π/7)` | `0.37651` | monograph hypothesis (+0.67 %) |
| `γ` measured here (fixed grid) | `0.11 ± 0.11` | **invalid** — mass floor `M ≈ 4·du` |
| `γ` measured here (zoom chain) | — | **not achieved**: depth wall at `z ≈ 5.2`, needs `z ≈ 10–12` |
| `Δ` measured here | — | **not achieved**: echo peaks at `z ≤ 5.2` are dominated by restart transients |

**Bottom line.** The 0.67 % gap between `b_Ch` and `γ` remains an *open
numerical question* for this codebase. Nothing measured so far supports or
refutes it; deciding it requires the v3 center-ODE treatment described in §8.
This module deliberately refuses to fake the comparison.

## 10. Running everything

### Desktop

```bash
cd einstein_direct
pip install numpy scipy sympy pytest        # ~1 min
pytest tests/ -q                            # validation, ~2 s
python3 choptuik_scaling.py --n-bisect 800  # fixed-grid campaign, ~10 min
python3 zoom_campaign.py                    # zoom prototype campaign, ~4 min
python3 figures.py                          # RU/EN figures, ~1 min
```

### Android (Termux)

See `../termux/` in the ZIP: `01_termux_install.sh`, `02_termux_run.sh`,
`03_push_to_github.sh`. Short version:

```bash
pkg update && pkg install python git clang libjpeg-turbo
pip install numpy scipy sympy pytest
bash 02_termux_run.sh      # runs the validation + a reduced campaign
bash 03_push_to_github.sh  # clones/locates the repo, syncs einstein_direct/, commits, pushes
```

Notes for Termux: `numpy`/`scipy` install from the Termux `science-repo`
packages (`pkg install python-numpy python-scipy`) when wheels are unavailable;
the push script stores a GitHub PAT once via `git credential store` and never
echoes it. The full campaign runs on a phone in ~1–2 h; the reduced profile
(`--quick`) takes ~15 min.

## 11. File map

```
einstein_direct/
├── sympy_derivation.py     # Hilbert action → 1+1 system, machine checks (mpmath 50 digits)
├── solver.py               # double-null characteristic solver (validated, 2nd order)
├── roberts_test.py         # Roberts–Oshiro convergence harness
├── choptuik_scaling.py     # fixed-grid bisection A* + mass-scaling fit
├── zoom_solver.py          # multi-zoom machine v2 + DSS tracking + echo peak tools
├── zoom_campaign.py        # honest zoom campaign driver (staged, JSON output)
├── figures.py              # RU/EN publication figures (300 dpi)
├── report_ru.pdf / .tex    # 7-page RU report (Tectonic)
├── report_en.pdf / .tex    # 7-page EN report (Tectonic)
├── tests/test_einstein_direct.py   # 5 regression tests
└── results/
    ├── derivation_results.json / derivation_log.txt   # machine derivation, residuals 1e-41
    ├── roberts_test.json                              # convergence orders
    ├── choptuik_scaling.json                          # A* = 0.0805333, fixed-grid floor analysis
    └── zoom_campaign.json                             # zoom v2 campaign: z reached, verdicts, wall diagnosis
```

## 12. References

1. Choptuik, *Critical Behavior in Gravitational Collapse*, PRL **70**, 9 (1993);
   Phys. Rev. D **54**, 6040 (1996) — critical exponent, echoing, AMR method.
2. Gundlach, *Understanding critical collapse of a scalar field*, Phys. Rev. D
   **55**, 695 (1997) — `Δ = 0.7372841`, `κ = 0.18482`, `[γ = 0.37374]`.
3. Roberts, Gen. Rel. Grav. **21**, 907 (1989); Oshiro et al. 1994; **Burko**,
   gr-qc/9608061 — corrected Roberts–Oshiro solution in double-null coordinates
   (the form validated here).
4. Garfinkle & Duncan — critical collapse with regridding; the center-treatment
   issues of §8 are the known hard part of characteristic regridding.
5. The monograph repository `choptuik_ac_bc` — the `b_Ch = 1 − cos(2π/7)`
   hypothesis under test.
