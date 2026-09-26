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
10. [v3.2: the spinor (even/odd) center closure](#10-v32-the-spinor-evenodd-center-closure)
11. [Spinor analysis: the π/15 and π/30 exponents](#11-spinor-analysis-the-π15-and-π30-exponents)
12. [Running everything (incl. Termux on Android)](#12-running-everything)
13. [File map](#13-file-map)
14. [References](#14-references)
15. [v5: the central Taylor patch — machine-derived center hierarchy, ODE-internal boundary data, spinor ladder](#15-v5-the-central-taylor-patch)
16. [v6-fundamentals: convergence and repulsion from first principles (Thorne/MTW mass route, log-time tower, exact spectrum)](#16-v6-fundamentals-convergence-and-repulsion-from-first-principles)
17. [v6.1: closing the depth-wall channels — stable stages, the Thorne link seen in data, and the O6+ verdict](#17-v61-closing-the-depth-wall-channels)

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
| `γ` measured here (zoom chain) | — | **not achieved**: depth wall at `z ≈ 5.9` (v3.2), needs `z ≈ 10–12` |
| `Δ` measured here | — | **not achieved**: no clean echo train at `z ≤ 5.9` (see §11) |

**Bottom line.** The 0.67 % gap between `b_Ch` and `γ` remains an *open
numerical question* for this codebase. Nothing measured so far supports or
refutes it; deciding it requires the central Taylor patch (v5) described in
§10. This module deliberately refuses to fake the comparison.

Note however the **product compensation** discovered in §11: the spinor
framework's `γ·Δ = b_Ch·(7π/30)` differs from the literature pair
`γ·Δ` by only **0.04 %**, while `γ` and `Δ` separately differ by 0.6–0.7 %.

## 10. v3.2: the spinor (even/odd) center closure

The v2 wall diagnosis said: the clamp `t = s` imposes an *incomplete*
regularity condition. This session implemented the complete one and
re-examined the wall with it.

**The regular center expansion** (with mirror coordinate `x = (v−u)/2 ~ r`):

```
Φ = Φ0(y) + a(y)·x² + …          (scalar field is EVEN in x)
t = Φ_v = t0 + a·x + O(x³)       s = Φ_u = t0 − a·x + O(x³)
     └── even part E = (t+s)/2 ──┘  └─ odd part O = (t−s)/2 = a·x ─┘
slope link:  s₁ − t₁ = −2a        (a ≠ 0 — this is the killed sector!)
p + q is ODD, (p+q)(0) = 0        m is ODD, m ~ m₃·r³
c + d is EVEN with (c+d)(0) = c(0) = d(0) = 0
```

The v2 clamp `t = s` **forces a = 0** — it deletes the odd ("spinor")
sector; during fast compression `s_v = −(p·t + q·s)/r ≈ 2c'·s/r` then
blows up. The mirror map `(u,v) → (v,u)` (r → −r, s ↔ t, p ↔ −q, c ↔ d)
is a Z₂ flip, and the E/O decomposition is exactly the parity expansion
under it — the language of the monograph's spinor functions.

**What v3.2 implements** (all flag-gated, base runs unchanged — 5/5 tests
still pass, strong-field benchmark unchanged):

1. `center_closure = "regular"` — per-row central-zone reconstruction:
   even part `E` by paired half-sum averaging; odd part fitted on the
   annulus `[R_zone, 4R_zone]` as `O(r) = a·r + C/r` (two-parameter LSQ);
   the regular `a·r` kept, the parasitic `1/r` mode **discarded**.
2. Smooth taper `w(k) = (1−(k/K)²)²` — no discontinuity at the zone edge
   (v3.0 without the taper made the chain *shorter*; the zone edge itself
   became a junk source — an instructive failure, kept in the log).
3. Mass: cubic law `m = m₃r³` with `m₃` matched at the zone edge
   (kills the constant mass offset whose `2Δm/r` diverges).
4. Parity projection: even part of `(p+q)` removed (regularity: odd),
   center value of `(c+d)` removed.
5. Factor-2 bug fixed in the v2 `_center_heal` (it averaged the sums
   `(t+s)` instead of the half-sums — the even part was doubled in the zone).

**Results** (`results/zoom_campaign_v3.json`, `results/spinor_analysis.json`):

| Metric | v2 (clamp) | v3.2 (regular) |
|---|---|---|
| junk `M_AH` explosion at stop | up to `3.56` | **`6.6·10⁻⁵`** (suppressed) |
| ring `[R_zone, 4R_zone]` at stop | junky | **stable** until stop |
| chain depth | `z ≈ 5.2` (3 zooms) | **`z ≈ 5.85` (4 zooms, ε=10⁻⁴)** |
| `(p+q)` even-parity violation, inner ring | `1.00` | **`0.35`** (3× better) |
| percent-level γ, Δ | not achieved | **still not achieved** |

**The wall, restated in spinor language.** The zone reconstruction now
keeps the spinor (odd) sector alive and the ring stays clean — but the
*raw march outside any zone* carries O(1) parity violations
(`s↔t: 0.93`, `m-odd: 1.00` at the outer ring), and the even part `E`
at the center still runs away after 2–3 restarts. No *local* zone cleaner
can fix a *global* march; the fix must be built into the evolution
itself — the **central Taylor patch** (Choptuik 1993): evolve the
expansion coefficients `(Φ0, a, …)` as the inner boundary condition.
That is the v5 roadmap, and it matches the monograph's thesis: stable
modes need *fundamental-level* derivations, not more regridding.

## 11. Spinor analysis: the π/15 and π/30 exponents

Per the author's guidance, the whole echo path is carried by **spinor
functions with exponents π/15 and π/30 with parameter scaling**. Module
`spinor_analysis.py` (output: `results/spinor_analysis.json`, figure
`figures/*/fig_spinor.png`) tests what is testable today:

**(a) Z₂ mirror parity of the center** — verified numerically at
`A = 0.075` (sub-critical, strong compression): scalar pairs `s↔t`,
`m ~ r³` hold to discretization accuracy inside the reconstruction zone;
the clamp closure shows a maximal `(p+q)` even violation `1.00` (killed
spinor sector), the v3 closure reduces it to `0.35`.

**(b) Framework relations** (exact arithmetic, no fitting):

| # | Relation | Value | Literature | Deviation |
|---|---|---|---|---|
| R1 | `γ = b_Ch = 1 − cos(2π/7)` | `0.376510` | `0.374` | `+0.67 %` |
| R2 | `Δ = 7π/30` | `0.733038` | `0.7376` | `−0.62 %` |
| R3 | `ω_wiggle = 4π/Δ = 120/7` | `17.142857` | `17.035` | `+0.63 %` |
| R4 | `γ·Δ` (product) | `0.275996` | `0.275876` | **`+0.044 %`** |

R3 is a sharp falsifiable prediction: the wiggle frequency becomes the
**rational number 120/7** — the heptadic 7 reappears in the fine
structure of the mass scaling. R4 is the curious fact that the R1 and R2
deviations *compensate* in the product `γ·Δ` to 0.04 % — consistent with
a common spinor normalization behind both constants.

**(c) Δ from the zoom runs** — the geometric echo-train estimator
(`v_n → v*`, `v* − v_n ~ e^{−nΔ}`) is implemented and applied; **no clean
echo train exists in our data** (`z ≤ 5.9`): the detector now rejects
noise trains honestly (Δ = n/a in the JSON). This is a data-depth limit,
not a method limit.

**(d) Parameter scaling** — the screaming-mode estimator `Q_n ~ e^{κζ_n}`
is implemented; on the current data it is contaminated by restarts and is
reported as order-of-magnitude only.

**Honest resolution limit.** Modulations with frequencies π/15 and π/30
in the log-scale variable ζ have periods 30 and 60 in ζ — i.e. ~40–80
echoes. Our chain reaches 2–7 echoes (`z ≈ 3.6–5.9`); resolving the
spinor modulation requires `z ≥ 30` — **one and a half orders of
magnitude deeper** than today. This quantifies the author's point: the
full path *requires* the spinor functions with π/15, π/30 exponents and
parameter scaling; brute-force zooming alone cannot get there.

## 12. Running everything (desktop and Termux)

### Desktop

```bash
cd einstein_direct
pip install numpy scipy sympy pytest        # ~1 min
pytest tests/ -q                            # validation, ~2 s
python3 choptuik_scaling.py --n-bisect 800  # fixed-grid campaign, ~10 min
python3 zoom_campaign.py                    # zoom prototype campaign, ~4 min
python3 zoom_campaign_v3.py                 # v3.2 protocol campaign, ~5 min
python3 spinor_analysis.py                  # spinor module: parity A/B, R1-R4, ~5 min
python3 spinor_figures.py                   # spinor figures (RU/EN), ~10 s
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

## 13. File map

```
einstein_direct/
├── sympy_derivation.py     # Hilbert action → 1+1 system, machine checks (mpmath 50 digits)
├── solver.py               # double-null characteristic solver (validated, 2nd order)
│                           #   + v3.2 center closures: clamp | regular (spinor E/O)
├── roberts_test.py         # Roberts–Oshiro convergence harness
├── choptuik_scaling.py     # fixed-grid bisection A* + mass-scaling fit
├── zoom_solver.py          # multi-zoom machine + DSS tracking + echo peak tools
├── zoom_campaign.py        # honest zoom campaign driver v2 (JSON output)
├── zoom_campaign_v3.py     # v3.2 protocol campaign with spinor diagnostics
├── spinor_analysis.py      # Z2 parity A/B, framework relations R1-R4, Δ/κ estimators
├── spinor_figures.py       # fig_spinor RU/EN (parity bar + R1-R4 deviations)
├── figures.py              # RU/EN publication figures (300 dpi)
├── report_ru.pdf / .tex    # 7-page RU report (Tectonic)
├── report_en.pdf / .tex    # 7-page EN report (Tectonic)
├── tests/test_einstein_direct.py   # 5 regression tests
└── results/
    ├── derivation_results.json / derivation_log.txt   # machine derivation, residuals 1e-41
    ├── roberts_test.json                              # convergence orders
    ├── choptuik_scaling.json                          # A* = 0.0805333, fixed-grid floor analysis
    ├── zoom_campaign.json                             # zoom v2 campaign: z reached, verdicts, wall diagnosis
    ├── zoom_campaign_v3.json                          # v3.2 protocol: spinor diagnostics at the wall
    └── spinor_analysis.json                           # parity A/B, R1-R4, Δ/κ honest status
```

## 14. References

1. Choptuik, *Critical Behavior in Gravitational Collapse*, PRL **70**, 9 (1993);
   Phys. Rev. D **54**, 6040 (1996) — critical exponent, echoing, AMR method;
   the central-regularity treatment that §10/§13 point toward.
2. Gundlach, *Understanding critical collapse of a scalar field*, Phys. Rev. D
   **55**, 695 (1997) — `Δ = 0.7372841`, `κ = 0.18482`, `[γ = 0.37374]`.
3. Roberts, Gen. Rel. Grav. **21**, 907 (1989); Oshiro et al. 1994; **Burko**,
   gr-qc/9608061 — corrected Roberts–Oshiro solution in double-null coordinates
   (the form validated here).
4. Garfinkle & Duncan — critical collapse with regridding; the center-treatment
   issues of §8/§10 are the known hard part of characteristic regridding.
5. The monograph repository `choptuik_ac_bc` — the `b_Ch = 1 − cos(2π/7)`
   hypothesis under test, and the spinor framework with the π/15, π/30
   exponents (§11).


---

## 15. v5: the central Taylor patch

### 15.1 The machine-derived center hierarchy (sympy_center.py)

Session 5's fundamental step: the REGULAR CENTER is described by a Taylor
series in the signed radius `xi = x - x*(v)` (x = (v-u)/2, x*(v) -- the center
worldline, chi = dx*/dy -- its drift), split by the Z2 mirror parity into the
scalar (even) and SPINOR (odd) sectors:

```
r     = R1*xi + R3*xi^3          Phi = P0 + P2*xi^2 + P4*xi^4   (even)
omega = W0 + W2*xi^2              m   = M3*xi^3                  (odd)
```

Substituting the series into all five bulk equations and expanding in xi
(SymPy `sp.series` on the rational residuals -- `expand+coeff` is WRONG for
them), each order gives an ODE/constraint. All forms are machine-verified
(`results/center_hierarchy.json`, `hierarchy_forms_verified: true`):

| Tag | Relation | Source |
|-----|----------|--------|
| O1 | `t0' = 3*P2 - 2*(R1'/R1)*t0 = 3*P2 - 4*d0*t0` | SC, order xi^0 |
| O2 | `R1' = 2*d0*R1` | C2 (and C1 -- cross-checked), xi^0 |
| O3 | `d0' = M3/R1 + W2 - kappa*t0^2` | TH, xi^0 (**+W2 found by the machine**, missed by hand derivation) |
| O4 | `M3 = (R1'^2 - 6*R1*R3)/(2*R1) + R1*W2` | Mdef, xi^3 (gauge R1^2 = A0) |
| O5 | `P2'' = 20*P4 + 8*R3*P2/R1 - 2*(R1'/R1)*P2' - 2*(R3'/R1)*P0' + 2*(R3*R1'/R1^2)*P0'` | SC, xi^2 -- the spinor-mode coupling |
| gauge | `(1 - chi^2)*R1^2 = alpha2(0)` | Mdef, xi^1 |

Checks: flat space (all residuals 0), flat symmetric wave (P0'' = 6*P2 gives
SC xi^0 = 0), C1-C2 consistency at xi^0. Numeric verification of the
measurement pipeline on a subcritical run (A = 0.02): one-step Heun residuals
O2 ~= 1.1e-3, O1 ~= 2.8e-2 (median, relative).

This is the "fundamental-level derivation for the stable modes": the E-mode
amplitude t0 is DRIVEN by the spinor slope P2 (O1), and the spinor mode P2 is
driven by the even sector (O5). Some solutions MUST blow up (decays/assemblies
are critical special cases of the Einstein equations) -- the hierarchy
separates the stable ladder from the blow-up sector.

### 15.2 The patch (solver.py, center_closure="taylor")

Per row on zoom stages:

1. Ring fits (physical side, r in [R_zone, 4*R_zone], R_zone = max(8*du,
   1.2*R_heal)): linear + linearized-cubic fit of r(x) -> R1, R3, x*; chi
   from consecutive x*; paired even/odd fits in the zone with the EXACT xi
   per point (offset-aware); (c+d)/2 -> d0; (d-c)/2 -> W2; M3 from m/xi^3.
2. ODE evolution of the internal boundary data: t0 by O1 (Heun predictor +
   0.5 relaxation to the fitted E0), d0 by O3. R1 is recorded as a DIAGNOSTIC
   only -- writing p(i0) from the fitted R1 creates a feedback loop (fit of
   the already-patched r-profile -> p(i0) -> new r-distortion), observed as
   R1 drifting to 0.906 with C1 exploding to 0.5.
3. Zone rebuild (v5-minimal, the scope that survives): t,s from E_zone (the
   paired even part, k = 1..K; **E(0) = t0 -- the ODE-evolved value** -- the
   key difference from v3.2) + O = P2*xi + P4o*xi^3 (the C/xi parasite mode
   is separated by the fit and DISCARDED); m = M3*xi^3 (edge-matched
   median); a hard projection of the even part of (p+q) -- the source of the
   E-mode explosion E_v = -(p+q)*E/r -- with a 4-parameter fit that accounts
   for the center offset x* (a naive projection injects a constant R1'*delta);
   the center point: t = s = t0, c = d = d0. p, q, r, alpha2 are NOT touched:
   their raw march maintains the discrete C1 constraint (a full series
   rebuild of p,q breaks C1: 1e-8 -> 0.5 -- measured).
4. Sanitize: every fit carries residual+boost guards; a failed fit disables
   that block for the row instead of injecting junk (restart rows carry
   interpolation junk -- an unguarded O-fit once injected P2 = 4.3e13 and
   killed the run within 2 rows).

Also new in v5: the zone covers the FULL radius (K = 2*R_zone/du cells --
xi steps du/2 per cell, the v3.2 code covered only half), and the zoom
stages march t OUTWARD from the center on both sides (`march_from_center`;
the 1/r homogeneous mode decays outward). A subtle bug fixed on the way:
the closure dispatch used to live inside the edge-march branch only, so
activating march_from_center silently DISABLED the center closure.

### 15.3 What v5 achieved, and what it did not (honest)

Achieved:
- Mass junk at the center: mdef ~ 2.9e-6 (super-clean); the gauge relation
  R1^2 = alpha2(0) holds at the 1e-2 level along the chains.
- Depth: z = 7.19 (7 zooms; patch with the edge-march configuration,
  eps = 3e-5) vs the v3.2 record of 6.05. The final configuration
  (patch + center-march) gives z ~ 4.2-4.5 on the same eps ladder: the
  depth is CHAOS-sensitive, and single-threaded BLAS is required for
  reproducibility (multithreaded LAPACK reshuffles near-critical AH
  nucleation and changes the fate of the run).
- The spinor ladder module (spinor_ladder.py): the pi/15, pi/30 phase
  table (the ladder quantum is pi/30, an echo is 7 quanta, pi/15 is 2
  quanta; resolving pi/15 needs z >= 30, pi/30 needs z >= 60), mode-growth
  fits (kappa_t0, kappa_P2 -- order of magnitude only), an echo-harmonics
  fitter, and numeric O1/O3 residuals along the chains.

NOT achieved (the wall moved, it did not vanish):
- Percent-level gamma and Delta: the AH capture is still unreliable -- the
  q = 0 crossing either happens after the 2m/r > 2 stop fires, or is
  junk-contaminated; M(eps) could be measured for only a fraction of the
  eps ladder, and the gamma fit needs >= 3 clean points.
- The depth wall is now OUTSIDE the patch zone: the raw march in the mirror
  region breaks the mirror parity of m (m_mirror ~ -12.7 vs m_phys ~ +4.2)
  at |r| ~ 100*du. The v6 roadmap: (a) parity projection in an ANNULUS
  outside the zone (mirror-antisymmetrization of the raw march), (b) a
  robust AH capture (store ALL sane crossings; freeze at the last sustained
  one; relax the r > 8*du threshold).

Files: `sympy_center.py`, `spinor_ladder.py`, `zoom_campaign_v5.py`,
`results/center_hierarchy.json`, `results/spinor_ladder.json`,
`results/zoom_campaign_v5.json`.

---

## 16. v6-fundamentals: convergence and repulsion from first principles

Module: `center_modes.py` → `results/center_modes.json`,
`figures/fig_ru/fig_modes.png`, `figures/fig_en/fig_modes.png`.

The task (author's directive): return to the Hilbert equation, use the
Kip Thorne / MTW-style mass bookkeeping, take the empirical constants as
ANCHORS ONLY, and compute the convergence (stable modes) and the repulsion
(unstable/blow-up channels) so that the numbers come out of first principles.
No fitting anywhere; γ_lit, b_Ch, Δ_sp enter only as comparison anchors.

### 16.1 The Thorne route: exact mass identities (machine-verified)

Starting from the Hilbert-derived double-null system (Mdef, UV, C1, C2),
SymPy derives (residuals exactly 0, with p eliminated through the Misner–Sharp
definition and q_u = p_v via the mixed partial r_uv):

- the null flux laws of the mass function:
  **m_v = −2 r² p t²/α²** and **m_u = −2 r² q s²/α²**;
- the central mass–slope link (regular center, general drift χ):
  **M3 = 2 R1 t0² / (3 (1−χ)²)** — exact at EVERY y, not only in CSS;
- the central gauge follows from m(0) = 0 (Mdef at ξ⁰):
  **(1−χ²) R1² = A0**;
- the hoop threshold 2m/r = 1 gives the horizon radius in center coordinates
  **ξ_AH = sqrt(R1/(2 M3))** (s-free; CSS value sqrt(3/(4τ))).

### 16.2 The log-time tower (machine reduction of the verified O1–O5)

Substituting X = x̂(z)·s^(−p) (z = −ln s, s = y*−y; the exponent table
p = 0,0,0,2,2,2,2,4) into the verified hierarchy is s-PURE — every term of
every equation carries one power of s (machine-checked: O1:2, O2:1, O3:2,
O5:4, O4:2). The autonomous z-tower has a CSS fixed point

    d0* = 0,  t̂0* = 3P̂2*,  Ŵ2* = (4/3)τ,  M̂3*/R̂1* = (2/3)τ,  R̂3*/R̂1* = (2/9)τ,

with τ = t̂0*² — WITHOUT the Thorne link the point has two free moduli; the
mass-flux link closes it to exactly ONE amplitude parameter. This is the
analytic role of the Thorne route: it closes the fundamental level.

### 16.3 The spectrum: convergence and repulsion (exact)

Linearization of the closed tower (levels 0–2, deep sources frozen):

- **τ → 0:** char = λ(λ+1)²(λ+2)(λ+3) — the EXACT fundamental spectrum
  **{0, −1, −1, −2, −3}**: integer convergence exponents — the
  "fundamental-level conclusions for the stable modes" (the O-mode slope pair
  −2, −3 is exact); the 0 is the family direction (deeper levels decide);
- **τ > 0:** exactly ONE growing root λ⁺(τ) — the repulsion channel — inside
  the codim-1 window 0 < τ ≤ **27/80** (char(0,τ) = 8τ(80τ−27)/27 → τ₂ = 27/80
  EXACT); λ⁺(27/80) = 1.5091, so the closed tower alone gives
  **γ = Δ_sp/λ⁺ ≥ 0.4857**;
- **exact points:** char(2) = 8(2τ−1)(8τ−45)/27 → **λ⁺ = 2 at τ = 1/2** (and
  τ = 45/8) — the same "2" as the Riccati coefficient 2d0² of O3;
- **τ > 27/80:** a second growing root appears — the "decays/assemblies"
  blow-up channel (the expected physics of the private cases).

### 16.4 Anchors (comparison only, no fitting)

- κ_obs = Δ_sp/γ: **1.947** (b_Ch) and **1.960** (γ_lit) vs λ⁺(τ₂) = 1.509:
  the deficit **+0.44…+0.45 in κ** is the quantitative measure of what the
  deeper tower levels (O6+) must contribute for the percent-level γ;
- formal amplitudes where λ⁺ = κ_obs: τ ≈ 0.481–0.486 (outside the codim-1
  window — there the truncation is already invalid; fixing τ is the job of
  the full tower);
- indicative: at τ = 0.48, γ_pred = 0.377 vs b_Ch = 0.376510 (0.13%) —
  NOT a measurement (two-mode regime), a family-curve reading.

### 16.5 Empirics

- the Thorne link on clean regular runs (n = 800): M3/M3_pred median ≈ 1.6
  with a wide spread — the exact identity becomes a STRICT center-quality
  metric: ratio > 1 measures the ξ-junk (the 1/r mode, m/ξ³ = M1/ξ² + M3)
  and the ring-fit systematics; tightening it to percent level is a v6 goal
  (the same wall as the percent-level γ);
- ξ_AH (hoop) on the v5 critical chain: median 4.83 — O(1) in ξ-units, as
  the CSS prediction sqrt(3/(4τ)) demands;
- numeric O1 residual on the chain: median 2.5e-2; the taylor-patch t0
  transients after zoom restarts break the instantaneous identity (honest;
  the identity is exact for solutions of the system).

Run: `python3 center_modes.py` (~1 min; SymPy + one zoom chain).

---

## 17. v6.1: closing the depth-wall channels

**Session goal.** v6 mapped the full v5 death chain and left one killer
channel: the compounding of the raw t-march at rows j≈19–20 of a zoom stage.
This session closed that channel with seven principled fixes (v6.1) and ran
the O6+ numeric analysis. No fitting anywhere — every fix is a discrete
image of an exact continuum statement.

### 17.1 The seven fixes (each traced to a measured death mechanism)

1. **Annulus wiring (aliasing bug).** In the v6 corrector `st_new["t"]`
   aliased the parent row's array: the annulus re-march mutated the PARENT
   t, its result was then discarded (`st_new["t"] = t_new`), and Phi absorbed
   a half-weight injection from the mutated parent (broken t-sandwich).
   Now: `t_new` → Phi (from the clean parent) → annulus acts on the NEW t →
   Phi corrected consistently (`Phi += 0.5 dv Δt`), the discrete sandwich
   `Phi_v = (t_old+t_new)/2` holds exactly.
2. **d_edge feedback cap.** The edge Goursat data for omega
   (`d_edge = (r_vv + κ/2 r t²)/(2q)`) is a SECOND derivative of interpolated
   data — noise amplification ~1/dv² ≈ 3e8 at deep stages. Junk d_edge ≈
   −1e4…−1e6 drove the edge q as q′ = 2dq (|2 dv d| > 1 already at d ≈ −6e3):
   q oscillated through zero (0.53 → 0.14 → 0.0024 → −0.23 → +2.68 measured),
   the small q made d_edge larger — a positive feedback loop that flipped
   alpha² sign within one row. Physical scale of ω_v at the edge is O(1–30);
   the cap |d_edge| ≤ 1e3 touches only junk and opens the loop.
3. **AH trap filter.** The apparent-horizon detection accepted junk q-crossings
   of the annulus (m crushed by the tower blend to ~1e-10) — false
   "AH formed" stops with M_frozen ≈ 1e-10. Added the physical trapping
   condition |2m/r − 1| < 0.5 at the crossing.
4. **P2 early-accept.** A passing O-fit on a restart row (the BEST data of a
   stage — fresh interpolation) was discarded by the early-rows rule
   (tay_rows ≤ 6). The relayed P2 = 0 then self-locked: the zone rebuild with
   P2 = 0 flattened the odd structure, subsequent fits saw a plane
   (res_O ≈ 1.0 measured), P2 stayed 0 forever → zero tau-rows. Now the
   res/boost/zone-boost gates alone decide fit validity.
5. **Zone-rebuild gate.** The t,s series rebuild used RAW pair averages
   unconditionally (the fit gates protected only the coefficients) — junk
   pairs were injected into the zone. Plus a rate gate: E0_free (the ξ→0
   extrapolation of the zone data) is physically ~t0; doubling per row was
   a rebuild feedback loop (t0: 0.065 → 35 in 8 rows measured). The zone
   now keeps its previous series on a failed/junk-fit row.
6. **Cross mode: t := mirror(s).** The fundamental conflict: the raw march
   crushed t outside the zone (t_out → 0.002 while s_out ≈ 1 — an O(1)
   mirror-asymmetric pair), while the parity projection pulled t back to
   O(1) — a march/projection battle (t_out: 0.002 → 3.0 → 1.3e3 in two rows).
   The exact CSS relation t(ξ) = s(−ξ) resolves it: s is the trusted evolved
   field (not touched), t is re-slaved to its mirror with the annulus taper.
   This satisfies BOTH parities exactly and removes the march's C/ξ mode.
7. **Two-sided r-fit + axis gate.** The x* intercept was fitted on the +r
   side only — the cubic wave on the ring biased the intercept by ~10 du
   (measured: x* − x[i0] = 10.5 du at the death stage) — every pair,
   projection and cross-assign was built around a WRONG mirror axis and
   injected O(1). Now the ring uses |r| (both sides; r(ξ) is odd, anchoring
   the intercept), and a gate requires |x[i0] − x*| ≤ 2.5 du.

### 17.2 Result: stable stages, record depth, the Thorne link in data

- The j≈19–20 channel is CLOSED: eps = 1e-2 and 1e-3 runs end by
  **v-exhaustion, not death** — 5 zooms, z = 9.10 / 9.35 (record; v6 died at
  z = 3.83 after 2 zooms, v5 at z ≈ 4.2–4.5).
- P2 unlocked → 40–181 tau-rows per stable run, continuous z_cont up to 7.9
  (v6: exactly 1 tau-row).
- **The Thorne link is visible in discrete data for the first time**
  (eps = 1e-2): M3/(R1 t0²) = 0.6687 vs the exact 2/3 = 0.6667 — 0.3%
  agreement (v6 empirical median was ≈ 1.6, i.e. the junk level).
- |d0·s| → 4e-5 (CSS target 0) on the same run.

### 17.3 Honest: tau* is still NOT measured

- The W2 measurement is still crushed (W2/t0² → 0 against the CSS target
  4/3): the (d−c) ring signal is buried under the cumtrapz-junk floor of d.
  With W2 off the tower manifold, tau_row = t0⁴/(9 P2²) is an off-manifold
  proxy — the tau* fits return garbage (honestly recorded in
  `results/grid_machine_v6.json`).
- Small eps (3e-4, 1e-4) and 3e-3 die at zoom 1 (z = 1.78): the near-critical
  branch is the next fix cycle (v7: source dynamics W2/R3/P4 — the machine
  is now stable enough to iterate on it).
- BLAS is pinned to 1 thread in the campaign/probe modules (reproducibility:
  multi-thread LAPACK reshuffles near-critical trajectories).

### 17.4 The O6+ verdict (nsolve): no exact CSS point in the truncated tower

`sympy_center_o6.py` machine-derived 7 verified source-dynamics levels
(all residuals 0: SC[ξ⁴]→P4′, UV[ξ³]→R5, C2[ξ²,ξ³]/C1[ξ²,ξ³]→W2′,
TH[ξ²]→M5, Mdef[ξ⁵]→R3′). `sympy_center_o6_nsolve.py` builds the fixed-point
system from the RAW purified z-coefficients (the first attempt used the
solved N-levels, which divide by dR1 — poles/zoo at the fixed point; lesson
recorded). Verdict, machine-exact:

- the O1–O5 subsystem is consistent: D0*=0, P2h*=T0/3, W2h*=(4/3)tau,
  R3h*=(2/9)tau all DERIVE as equations — one free amplitude (tau), as in
  §16;
- adding UV[ξ³] forces **T0² = 9/4** (tau = 2.25); adding Mdef[ξ⁵] forces
  **T0² = 9/16** (tau = 0.5625); together — only the trivial R3 = 0 branch.
  The system is INCOMPATIBLE: the truncated tower has NO exact CSS fixed
  point;
- interpretation: the W2/R3/P4 sources never freeze — the source dynamics is
  essential, and binding the amplitude requires the full (untruncated)
  analysis. This is the quantitative form of the "+0.44 kappa deficit"
  localization of §16.

Run: `python3 sympy_center_o6_nsolve.py` (~1 min; `results/center_o6_nsolve.json`).
Campaign: `python3 grid_machine_v6.py 1e-2,3e-3,1e-3,3e-4,1e-4`
(`results/grid_machine_v6.json`).

## 18. v8: the Poincare hexagonal transformation cycle (dynamics instead of the truncated tower)

The O6 verdict of section 17's analysis: the UV[xi^3] branch forces
T0^2 = 9/4 (tau3 = (3/2)^2), the Mdef[xi^5] branch forces T0^2 = 9/16
(tau5 = (3/4)^2); together only the trivial R3 = 0 survives — the truncated
tower has no exact CSS solution, the sources are fundamentally dynamical.
`sympy_hexcycle.py` formalizes the answer: instead of a static truncation, a
dynamical six-station cycle (pyramid -> cone -> truncated cone -> parabolic
pivot -> bowl -> log closure -> pyramid) circulating on a C6 shape dial by
the Poincare quasi-velocity equations. The two incompatible branches become
steps of two DIFFERENT books of the cycle:

- **amplitude book**: the CORE pair (3/2)^2 = tau3, the ring pairs
  (4/3)^2 = 1/tau5, the full cycle kappa_cyc = ln(tau3/tau5^2) = ln(64/9) =
  1.9617 vs the anchor kappa_obs = Delta_sp/gamma = 1.9600 (+0.085%); the
  frozen-tower deficit lambda+(27/80) = 1.5091 (+0.451 in kappa) is filled
  to 100.4%;
- **echo clock**: -ln(tau5) = ln(16/9) per hexagon side,
  Delta_cyc = 6 ln(16/9) = 12 ln(4/3) = 24 ln(2/sqrt3) = 3.4522 vs
  Delta = 3.44 (Choptuik 1993; inside the +/-0.02 corridor);
- **hexagonal log computations are exact geometry**: the ring step 4/3 =
  (2/sqrt3)^2 — the square of the hexagon's own circumradius/inradius ratio;
  the O6 branches are themselves squares (sqrt(tau3) = 3/2, sqrt(tau5) = 3/4,
  ratio 2 — the pyramid doubling);
- **gamma_cyc = Delta_sp/kappa_cyc = 0.373683** (gamma_lit = 0.374, -0.085%;
  b_Ch -0.75%);
- **the attractor is a limit cycle (DSS, not CSS)**: the return map lands on
  the pyramid exactly (max-norm error 0), the scale drops by e^Delta ~ 31.6
  per cycle — a structural explanation of Choptuik's observation.

The machine: 15/15 symbolic identities; Poincare = Euler-Lagrange (abelian
dial group), the locking V'(k*pi/3) = 0 of all six stations, p_theta = const
in the free circulation; the free-circulation period equals Delta_cyc
exactly (<1e-12), the locked one (V6 = 0.05) shifts by +0.253% (an honest
O(V6) effect); the per-cycle book step is measured numerically to 1e-9.
Model axioms (the 2+4 zone split, the global clock) and limitations are
stated honestly. Reports: `hexcycle_report_ru.pdf` /
`hexcycle_report_en.pdf`; RU/EN 300-dpi figures (`fig_hexcycle*.png`).

```bash
python3 sympy_hexcycle.py        # the cycle machine: symbols + books + circulation, ~5 s
python3 hexcycle_figures.py      # RU/EN 300-dpi figures, ~30 s
```

## 19. v8-campaign: checking kappa = ln(64/9) and W2/t0^2 -> 4/3

The hexcycle (section 18) made two quantitative predictions for the
near-critical tau* campaign: the amplitude book kappa = ln(64/9) =
1.9616585 and the ring W2/t0^2 -> 4/3 = 1/sqrt(tau5). `grid_machine_v8.py`
runs the check on the stable v6.1 chains (z ~ 9.1-9.35) with full
measurement instrumentation, and it changed the diagnosis of everything
that was blocking the tau* measurement:

- **clock bug**: `dv_ode == 0` after the first row of every stage (the
  chi section overwrote `tay["v_prev"]` before the ODE read it) — the
  center ODEs O1/O3 were dead since v5. Flag-fixed (`tay_ode_fix`);
  legacy is reproduced exactly.
- **gate freeze**: the E/O fit gates use a max-res metric that the zone
  edge (dynamic range ~1000) crushes to ~1 on deep rows, so the gates
  fail everywhere and the P2/W2 relays freeze at stage-1 values. The
  fresh book is therefore built from RAW pre-gate fits:
  tau_fresh = E0_free^4/(9 P2_raw^2), with MAD outlier rejection.
- **live tower**: with the clock alive, three closures of the center
  dynamics (blind ODE with self-referential P2; Riccati clock; width
  clock) all blow up t0 within 1-2 stages, because the E0_free anchor is
  poisoned by the zone rebuild (E_zone[0] = t0). The center book on this
  grid is always series-mediated — the v5 wall reopened at the P4 level;
  an independent dynamical confirmation of the O6 source-dynamics
  verdict. In the live tower W2 is enforced by the machine-verified CSS
  equation W2* = kappa t0^2 - M3*/R1 (4/3 at chi=0).

Verdicts (results/grid_machine_v8.json, honest statuses):
- kappa = ln(64/9): **blocked** — the unstable-mode departure does not
  grow inside the deep window (lambda_fit at the grid edge; the chain
  rides the DSS limit cycle and departs only inside the final junk
  explosion); the M(eps) gamma channel is unavailable (AH never
  nucleates, M_frozen = 0).
- Delta: **indicative** — model B Delta = 0.73 (-0.4% vs Delta_sp =
  7pi/30), model A 0.77 (+5.0%); the book is noisy (amp ~ 3 in ln tau).
  The geometric Q-peak echo on the zoom-ladder clock gives Delta =
  1.732 +/- 0.451, i.e. Delta_cyc/Delta_Q ~ 2.0 — the pyramid doubling
  of the hexcycle book (indicative, 26% error).
- W2/t0^2 -> 4/3: **blocked** — the raw (d-c) signal is ~1e13 t0^2
  above the target under the d-junk floor in all three channels (raw
  fit, dc-pair, d0-clock). The channel requires P4 dynamics (O6+) or a
  clean d-field.

Run: `python3 grid_machine_v8.py` (~3 min; `results/grid_machine_v8.json`),
figures: `python3 v8_figures.py`.

## 20. P4 closure (O6+): the shape cycle in Einstein and Hilbert equations

Machine: `sympy_p4_einstein_hilbert.py` -> `results/p4_einstein_hilbert.json`.

**How the cycle lives in the classical Einstein equations (all SymPy-exact):**

- The double-null residuals ARE `G = kappa T`: `G_uu - kappa T_uu = -(2/r) * C1-form`,
  `G_vv - kappa T_vv = -(2/r) * C2-form`, `G_uv = -(2/r) * (UV + r(TH - st))`,
  `Mdef` = mass constraint, `SC = -(alpha^2/4) box Phi`. The six stations are
  regimes of ONE tensor, not new physics.
- `T_uv == 0` identically: the null-null sector of the Hilbert tensor is empty;
  the scalar sources enter only through the uu/vv sectors (C1/C2) and the TH mixing.
- Hilbert identity (fresh 4D derivation): `nabla_mu T^{mu}_nu = (box Phi) nabla_nu Phi`
  — the source dynamics IS the Bianchi/Hilbert conservation law. This is where
  "sources must flow" lives in the classical equations.

**The ring and the clock are derived, not postulated** (core O1-O5 chain on the
frozen point): `Mdef[xi^3] -> D0 = 0`; `{UV[xi^1], C2[xi^1]} -> R3h = (2/9) T0^2 R1h`,
`W2h = (4/3) T0^2 R1h` (the ring `4/3 = (2/sqrt 3)^2`); `C2[xi^2] -> P2h = T0/3` (clock).

**AUDIT of the session-8 fixed point (important correction).** The old raw-coefficient
build silently zeroed the second derivatives of the sources (`W2''`, `R3''`, `P4''`)
and `R5'`: the `TBL_F` substitution `R5(y) -> R5h/S^4` collapses `Derivative(R5(y),y)`
to 0, and only `P2''` had an explicit z-table. With corrected adiabatic tables
(`F'' -> (5 dF + 6 F)/S^(p+1)`, second flows = 0):

- the `UV[xi^3]` and `Mdef[xi^5]` branches MERGE into one common root
  **tau* = 27/4**: the frozen CSS point of the O6 tower EXISTS (unique);
- the session-8 incompatibility (tau = 9/4 vs 9/16) and the two-branch book
  construction `kappa_cyc = ln(64/9)` built on it were artifacts of that drop;
- at tau* = 27/4 the amplitudes are `T0h = 3 sqrt(3)/2`, `W2h = 9`, `R3h = 3/2`,
  `P2h = sqrt(3)/2 = sin(pi/3)` — the hexagonal ratio appears on its own;
- spectrum: `lambda+(tau)` is monotone; `lambda+ = kappa_obs ~ 1.96` at
  `tau ~ 0.486`; at `tau* = 27/4` (off-grid) `lambda+ ~ 8` — the truncated-tower
  point is NOT the critical attractor by spectrum.

**Prolongation (O7) closes the adiabatic dynamics.** Preserving the core along the
flow (`dW2 = (8/3) T0 dT0 R1 + (4/3) T0^2 dR1`, etc.) kills the drifting-source
points: V1/V2 (tower alone) violate preservation (`sigma_W2 - 2 sigma_T0 - sigma_R1
= -1.53`), V3 (tower + prolongation, 18 eq / 17 unk) finds exactly ONE closed
point — the frozen one at `tau* = 27/4` (all flows 0). Genuine source dynamics
therefore requires second-order flows (dd != 0): a genuine LIMIT CYCLE (DSS),
not a drifting CSS point.

**Pure d-field (ring parity on (d-c)).** `c = d_u omega, d = d_v omega`; the mirror
`(u,v) -> (v,u)` swaps c and d; `(d-c) = omega_xi = 2 W2 xi` is odd on the ring.
Extractor `W2 = [(d-c)(xi) - (d-c)(-xi)]/(4 xi)` kills even junk EXACTLY (SymPy
check). v8 rows: the measured dc-pairs are asymmetric (`leak ~ 0.92`) and
even-dominated (`odd/even ~ 0.28`) — the W2/t0^2 channel needs exact mirror pairs
(v9 instrumentation).

Honest notes: the hexcycle book FORMULAS of session 11 (`ln(64/9)`, `6 ln(16/9)`)
were built on the artifact branches and need rework; the ring `4/3`, the DSS
picture and the v8 Delta-signals do not depend on the audit.

Run: `python3 sympy_p4_einstein_hilbert.py` (~15 s; `results/p4_einstein_hilbert.json`).

## 21. v9 mirror-ring pairs + exact char polynomial at tau* + monodromy books

Machines: `grid_machine_v9.py` -> `results/grid_machine_v9.json`;
`sympy_spectrum_tau_star.py` -> `results/spectrum_tau_star.json`.

**(1) v9 instrumentation (`solver._mirror_probe_v9`, flag `tay_diag_v9`, measurement-only).**
Per row: the ring dump (k = 1..K, both sides, exact xi, dc = d-c, cd = c+d) and
STRICT mirror pairs: cubic interpolation of each side SEPARATELY into the mirror
targets +-xi_t, then the P4-B extractor
`W2_pair = [(d-c)(+xi) - (d-c)(-xi)]/(4 xi)`. Channel B (junk-free): the series
`c_ser = (r_uu + (kappa/2) r s^2)/(2 p)` built from the row fits (C1 form), with
the mirror fit `D = c_ser(xi) - c_ser(-xi) = -(2 W2 xi + 4 W4 xi^3)` -> `W2_ser`.

Results (legacy legs eps = 1e-3 / 1e-2, live leg eps = 1e-2):
- the EVEN junk is side-symmetric to a median relative difference of
  `3.2e-8 .. 3.8e-7` (against `leak ~ 0.92` of the v8 pairs) and is killed by the
  extractor EXACTLY — the mirror instrumentation works as designed;
- the W2/t0^2 measurement stays **BLOCKED**: the ODD marsh junk of (d-c) is
  chaotic (per-row fits of the mirror differences do not close, res ~ 0.4-0.6),
  its linear-in-xi component is degenerate with the signal `2 W2 xi`, and the
  per-pair floor `|W2_pair|/t0^2` is 1.4 (eps=1e-3) to 2.3e+2 (eps=1e-2) against
  the target 4/3;
- channel B is symbolically EXACT (see below) but its input `R3` (the cubic
  coefficient of the ring r-fit) is junk on marsh data (`R3/t0^2 ~ 1e3..1e5`
  against CSS 2/9) and enters the linear coefficient degenerately.

**(2) C1 route to the ring (new machine identity, SymPy-exact).** The series
reconstruction of `c = omega_u = (r_uu + (kappa/2) r s^2)/(2 p)` gives
`c_lin = -[(3/2) R3 + (kappa/2) R1 E0^2]/[(1+chi) R1]`, hence at the CSS inputs
(`R3 = (2/9) tau R1`, `E0 = t0`, `chi = 0`, `kappa = 2`):
`W2 = -c_lin = (4/3) t0^2` — the ring 4/3 from the C1 null equation, a THIRD
machine route (after the O3 route `W2* = kappa t0^2 - M3*/R1` and the corrected
chain `W2h/T0h^2 = 4/3`), independent of R1 and d0.

**(3) Exact char polynomial at tau* = 27/4.**
- OLD core (torne link, sources frozen at CSS): substituting `tau = 27/4` into
  the stored quintic gives the exact polynomial with real roots
  `{-11.587049, -6.634885, -0.590872, +2.399389, +9.413416}`;
  **lambda+_old(27/4) = 9.4134160947** (the session-11 log-grid interpolation
  ~7.99 was low; and it was an artifact of freezing the sources).
- CORRECTED tower (audit tables, 12 tower equations with live first flows + 6
  chain-preservation prolongations = 18 equations on 9 amplitudes + 8 flows;
  the pencil `M(lam) = J_a + lam J_v P` with the flow->amplitude projection P,
  since `M5h` has no flow): the exact characteristic polynomial
  `char(lam) = det(M^T M)` (Cauchy-Binet sum of squared 9x9 minors; computed by
  EXACT rational interpolation on 25 points over Q(sqrt 3)) is
  `lam^4 * Q12(lam)` with Q12 of degree 12 irreducible over Q.
  Real-rank-drop set on the real axis: **{0} only** (verified twice: sigma_min
  scan and nroots; `dim ker J_a = 1` marginal direction). ALL complex roots of
  char are PHANTOMS: `sum(minors)^2` may vanish over C without a rank drop, and
  the complex-lambda SVD check shows full rank for every one of them
  (rel sigma_min ~ 1e-4..1e-6; max 3.4e-4).

**Verdict: the corrected tower point tau* = 27/4 is spectrally INERT — an
isolated algebraic vertex of the constraint landscape (no real exponential
modes at all), not an exponential repeller.** The old-core `lambda+ = 9.41`
was an artifact of frozen sources. Consequently there is no `gamma_pred` from
the point: the cycle dynamics lives in the LIMIT CYCLE (DSS), not in the
vertex — consistent with the session-11 prolongation verdict and with the v8
campaign signals.

**(4) Monodromy books of the corrected system (replacing the two-branch books).**
- amplitude book: `kappa_book = ln(tau*) = ln(27/4) = 3 ln 3 - 2 ln 2
  = 4 ln(3/2) + ln(4/3)` (both decompositions machine-checked) = 1.9095425,
  i.e. -2.57% against `kappa_obs(gamma_lit) = 1.9599954` and -1.92% against the
  b_Ch anchor — the single-branch replacement of the artifact `ln(64/9)`;
- station ladder of the corrected chain at tau* (exact):
  `W2h/R3h = 6 = 2*3`, `W2h/T0h^2 = 4/3`, `R3h/T0h^2 = 2/9`, `P2h/T0h = 1/3`,
  `T0h/P2h = 3`, `P2h = sin(pi/3)`, `R5h = 183/40`, `M5h = -105/4`,
  `P4h = 153 sqrt(3)/10`;
- monodromy identity: the product of the six loop ratios
  `R1h -> T0h -> P2h -> R3h -> W2h -> R5h -> R1h` equals **1 exactly**
  (machine-checked) — the amplitude monodromy around the six-station cycle is
  the identity (return to the pyramid);
- the clock book is NOT derivable from the chain (honest): the measured clocks
  of the v8 campaign stand (model B Delta ~ 0.73 ~ Delta_sp - 0.4%; Q-echo
  doubling `Delta_cyc/Delta_Q ~ 2`); `Delta_cyc = 6 ln(16/9)` of session 11 is
  an artifact-book. Surviving books: the ring 4/3, the DSS picture, the v8
  Delta-signals, the tent-lattice observation.

Honest notes: the W2/t0^2 -> 4/3 prediction remains closed at the marsh level
(dynamics-level reconstruction = O6+ is required); the C1 route gives the ring
as an identity of the CSS series, not as an independent marsh measurement.

Run: `python3 grid_machine_v9.py` (~110 s) and `python3 sympy_spectrum_tau_star.py`
(~15 s); tests 5/5 pass.

## 22. v11: the three repo corrections (b-C, a-C, a-B) embedded in the towers

Machine: `sympy_spinor_corrections.py` -> `results/spinor_corrections.json`.

**The question (author).** Maybe there is an "error" somewhere in the Einstein
equations, to be repaired so that the closure on pi/30 works — and the real
gap is that we deliberately never embedded the three computed corrections of
the repository (b-C Berry, a-C braking, a-B) as natural functions and
formulas. Maybe they will correct the towers?

**(0) The corrections as exact functions (repo anchors, machine cross-check OK).**
Spinor phases of Gamma(2,3,7): `delta_A = pi/2, delta_B = pi/3, delta_C = pi/7`.
Berry `beta(d) = d^2/2`, braking `alpha(d) = d^5/22` (k = b2(K3) = 22):
`bC = pi^2/98 = 0.100710`, `aC = (pi/7)^5/22 = 8.2763e-4 (~1/1200)`,
`aB = (pi/3)^5/22 = 0.057243` — cross-checked against
`docs/monograph/verification_results_enhanced.json` to < 1e-9.

**(1) Doors audit: there is NO error in the equations — there is a STRUCTURE.**
With per-channel couplings (kappa_C1 in C1: (k/2) r s^2, kappa_C2 in C2:
(k/2) r t^2, kappa_TH in TH: (k/2) s t) the symbolic rebuild shows:
- **SC/UV/Mdef are kappa-FREE** (zero leaks): the wave equation, the
  cross-constraint and the Misner-Sharp definition are pure geometry —
  nothing to "repair" there;
- the channel map is exact: C1_xi{1,2,3} <- kappa_C1 only; C2_xi{1,2,3} <-
  kappa_C2 only; TH_xi2 <- kappa_TH only;
- **RING CONSISTENCY (new machine theorem):** the C1 residuals at the chain
  point vanish if and only if **kappa_C1 = kappa_C2** (machine factored);
- **BRANCH CONSISTENCY:** the residual branches
  `UV_xi3 = -2 T0h^2 (8 k2^2 T0h^2 - 93 k2 - 15 kT)` and
  `Mdef_xi5 = -2 T0h^2 (4 k2^2 T0h^2 - 39 k2 - 15 kT)` share their positive
  root if and only if **kappa_C2 = kappa_TH** (difference
  `15 (k2 - kT)/(8 k2^2)`).

**Consequence: a holonomy correction can modify the tower ONLY as a UNIFORM
renormalization kappa -> kappa_hol of the scalar coupling in all three
channels.** Any asymmetric embedding (e.g. a-B in C1 only) kills the CSS
point: the C1 residual becomes 0.386 at the uncorrected point (machine
demonstration), the branches split. This is a PREDICTION of the tower about
the admissible form of the corrections — obtained, not assumed.

**(2) The corrected family is EXACT: `tau*(kappa) = 27/(2 kappa)`.**
Under the uniform renormalization the corrected point exists for every
kappa > 0 and the chain gives:
- `T0h^2 = 27/(2 kappa)` (so the uncorrected point is the kappa = 2 member);
- **holonomy-invariant station ladder** (kappa-free at the point):
  `R3h = 3/2`, `W2h = 9`, `R5h = 183/40`, `M5h = -105/4`,
  mass link `M3*/R1* = 9/2`, clock `P2h/T0h = 1/3`;
- what MOVES: the log-time base `tau*` itself, hence `P2h = T0h/3`,
  `P4h ~ kappa^{-1/2}`, and the T0h-relative ratios
  `W2h/T0h^2 = 2 kappa/3` (the ring 4/3 is the kappa = 2 member —
  the v9 target becomes `2 kappa_hol/3`), `R3h/T0h^2 = kappa/9`;
- amplitude book: `ln tau* = ln(27/(2 kappa))`.

**(3) Do the corrections close the books? (honest numbers, no fitting).**
The book closure `ln tau* = kappa_obs` requires `kappa_req = 27/(2 e^{kappa_obs})`
= **1.901597** (gamma_lit anchor; 1.926609 for the b_Ch anchor) — i.e. a
**uniform shift Delta kappa / kappa = -4.92%** from the bare kappa = 2:
- multiplicative monograph-sign embedding `kappa = 2(1 + bC - aC)` = 2.19976:
  book -7.43% (moves AWAY);
- opposite sign (screening) `kappa = 2(1 - bC + aC)` = 1.80024: book +2.79%
  (overshoots);
- **additive Berry screening `kappa = 2 - bC` = 2 - pi^2/98** = 1.899290:
  `tau* = 7.10792`, book = 1.961210 = **+0.062%** against
  kappa_obs(gamma_lit) (and -0.12% coupling distance to kappa_req); with the
  braking terms subtracted as well (`2 - bC + aC`, `2 - bC/2 - aC`): +0.11%,
  +0.43%... — the b_C-sized uniform screening lands ON the book closure;
- braking-only embeddings (`2(1 - aB)`, `2(1 - aC - aB)`): +0.43% / +0.48%;
- sign-combination scan over the four correction values (81 combos,
  **multiple-testing caveat**): best -0.26%..-0.43%; the additive-Berry
  screening is not one of the 81 (it is a half-weight scheme) and beats them
  all.
  All these are OBSERVATIONS of distance, not derivations: the sign and the
  add/multiply convention of the holonomy coupling are NOT fixed by the
  monograph; what the machine fixes is (a) the uniformity requirement and
  (b) the response family tau* = 27/(2 kappa).

**(4) pi/30 closure tests.**
- the tower chain still does NOT produce pi/30 exactly: the clock 1/3 and the
  station ladder are rational; the echo book remains measured (v8);
- the pencil spectrum in the corrected points (numeric QEP + sigma_min
  phantom filter, session-14 protocol reproduced: 4 genuine lambda = 0 modes
  + 12 phantoms in ALL points): the phantom Im lambda sit NEAR the spinor
  ladder — baseline best hit `Im lambda = 0.1080 ~ 1*pi/30` (3.10%),
  screening point `0.10745` (2.60%), monograph-sign point `0.91564 ~
  9*pi/30` (2.85%) — proximity, NOT closure (nothing within 1%).

**Verdict.** (i) The Einstein equations need no repair: SC/UV/Mdef are
coupling-free geometry and the derivation is machine-clean. (ii) The towers
are corrected by the repo corrections in exactly ONE admissible way — a
uniform holonomy renormalization of the scalar coupling; the corrected family
`tau* = 27/(2 kappa)` is exact, the station ladder is invariant. (iii) The
corrections are of the RIGHT SIZE to close the kappa book: a uniform
screening of b_C = pi^2/98 moves ln(tau*) from -2.57% to +0.06% of
kappa_obs — an observation-level closure with the convention (add vs
multiply, sign) honestly open. (iv) No exact pi/30 identity appears: the
phantom-ladder proximity stays at 2.6-3.5%, and the echo book remains a
measurement, not a derivation.

Run: `python3 sympy_spinor_corrections.py` (~15 s).

## 23. v12: the baryon-asymmetry reading + the one-brick phantom test

Machine: `s4_berry_one_brick.py` -> `results/spinor_corrections_one_brick.json`.

**The hypothesis (author).** "Maybe it is all about baryon asymmetry:
everything rises evenly, and the deviation happens in ONE brick of the tower,
so that complete annihilation does not occur. Pure mathematics is far from
physics."

**Sakharov mapping (structural; mechanism, NOT numbers).** The three
conditions of matter survival have exact tower counterparts, all
machine-established in previous sessions:
1. *departure from equilibrium* <-> criticality / the limit cycle: the
   frozen point tau* is spectrally inert (no real modes, not an attractor);
   the dynamics lives in the second flows (DSS) — the system never settles;
2. *C/CP violation* <-> the spinor phases delta_A = pi/2, delta_B = pi/3,
   delta_C = pi/7: the machine lets exactly ONE correction survive the
   admissible embedding — bC = pi^2/98, the Berry brick of the pi/7 phase
   (the septimal sector of b_Ch) — while asymmetric static insertion of the
   others is lethal (C1 residual 0.386): "one brick deviates";
3. *B-violation* <-> monodromy != 1: statically the six-station contour
   returns EXACTLY (product of ratios = 1, log-sum 1.2e-125) — complete
   phase annihilation, the sterile "pure mathematics" world the author
   warns about. A non-exact return can only be produced by the dynamic
   sector.

**Machine facts (this run).**
- The REAL sector annihilates EXACTLY in every corrected point: zero real
  exponential modes; the 4 genuine modes are numerically-zero neutral
  oscillations (|lambda| ~ 2e-3). What survives the annihilation is the
  imaginary (phase) sector — the 12 "phantoms" of the session-12 protocol.
- Under the baryon-asymmetry reading this INVERTS the phantom verdict:
  the phantom sector is not garbage to filter but the surviving asymmetric
  residue of the spectrum — the tower's own "baryon asymmetry". (Labeled
  as interpretation, not derivation.)
- Phantom Im lambda vs the spinor ladder k*pi/30 across schemes:
  baseline +3.10%, monograph-sign +3.43% (9pi/30: -2.85%), two-brick
  screening +2.60%, and — the previously MISSING run — the one-brick
  additive Berry scheme kappa = 2 - bC (tau* = 7.10792):
  **Im lambda = 0.107731 = +2.88%** from pi/30 (k = 6: +3.15%,
  k = 8: +4.94%). The one brick moves the residue TOWARD the ladder;
  no closure (nothing within 1%; multiple-testing caveat on all scheme
  comparisons).

**Verdict.** The hypothesis is machine-consistent in both halves that can
be tested statically: the surviving one-brick structure is real (the
machine's own admissibility theorem), and "complete annihilation" is the
exact static fact (monodromy = 1, no real modes). But a STATIC brick cannot
close pi/30: the residual ~2.9% gap is exactly the part of the asymmetry
that statics cannot produce — it must live in the second flows / limit
cycle, where a phase residue can accumulate from cycle to cycle (the
tower's "B-violation") without killing the point. That is the next
campaign: O6+ second flows as limit-cycle variables, with the sharp
question — does the cycle generate a monodromy phase residue delta_mono
!= 0, and is it the same residue as the phantom Im lambda gap?

Caveats: eta_b ~ 6e-10 is a measured number of a different universe — we
borrow the mechanism, not the number; no numerology is claimed anywhere.

Run: `python3 s4_berry_one_brick.py` (~20 s; rebuilds the symbolic payload,
runs the pencil at the one-brick point).

## 24. v13: second flows as limit-cycle variables — the linear verdict

Machine: `sympy_second_flows.py` -> `results/second_flows_limit_cycle.json`;
verification: `second_flows_verify.py` (Newton + mpmath) and
`second_flows_exact.py` -> `results/second_flows_verified.json`,
`results/second_flows_exact.json`.

**The question (author, after the baryon-asymmetry reading).** Does the
dynamic sector produce a monodromy phase residue delta_mono != 0 — the
tower's "B-violation" — and is it the same residue as the ~2.9% phantom
gap to pi/30?

**(0) Construction: the de-adiabatized source tables.** The session-11 audit
closed the second z-coefficients of the sources adiabatically:
W2'' -> (5 dW2 + 6 W2h)/S^4 etc. The coefficient structure 5,6 = (l+2)(l+3)
and 9,20 = (l+4)(l+5) shows the adiabatic table is the true polynomial form
(l^2 + 5l + 6)F with the l^2 term dropped; the machinery itself contains the
precedent P2'' -> (ddQ + 5Q + 6P2h)/S^4. De-adiabatization with coefficient 1:
W2'' -> (ddW2 + 5 dW2 + 6 W2h)/S^4, R3'' -> (ddR3 + ...)/S^4,
P4'' -> (ddP4 + 9 dP4 + 20 P4h)/S^6, dd* := d^2(amp)/dtau^2. T0/D0/R1 are NOT
touched (their tables are exact lower levels, not adiabatic closures); ddQ is
a vestige (P2'' is pre-substituted by the exact O5 — no equation contains it).
- regression: dd = 0 reproduces the adiabatic system EXACTLY (12/12);
- frozen-point residuals 1e-23..1e-24 at both points (kappa = 2 and the
  one-brick 2 - pi^2/98, tau* = 27/(2 kappa));
- **the l^2-sector is LIVE: rank C = 3 EXACTLY (symbolic) at both points.**

**(1) The true quadratic pencil.** With the limit-cycle ansatz
A(tau) = A* + a e^{l tau} (flows = l a, second flows = l^2 a) the 18-equation
system (12 tower + 6 prolongs) becomes the polynomial pencil
M(l) = Ja + l*Jv*P + l^2*J2*P2 (18x9). Rank drops = genuine modes.

**(2) The verification instrument (three layers, honest).**
- session-14 protocol (rel sigma_min < 1e-8 on float candidates) is NOT
  calibrated for the l^2-sector: at |l| ~ 1e5 the l^2-dominance makes the
  relative test too lenient (the "7 genuine modes" of the first run were
  threshold artifacts);
- Newton polish of l on sigma_min(M(l)) + mpmath: every nonzero candidate
  STALLS at rel 1e-9..1e-13 (12+ orders above the true-kernel behavior
  1e-21..0) — near-zeros, not modes;
- **the exact instrument (baseline, all values in Q(sqrt3)):** the char
  polynomial det(M^T M) built by exact rational interpolation (45 points,
  cross-checked at l = 1/2): **char = 9 l^4 Q18(l), degree 22, multiplicity
  of l = 0 is 4 — EXACTLY the lambda^4 structure of the session-14 linear
  pencil.** The de-adiabatization did NOT change the kernel.

**(3) Verdict.**
- the ONLY genuine mode at both points is **l = 0** (the marginal scale
  direction; at one-brick rel40 = 0 exactly);
- all 18 nonzero exact roots at baseline are PHANTOMS (rel40 = 2.3e-06..
  3.8e-04 — 24+ orders above the genuine floor 1e-30);
- **delta_mono = 0 at linear order**: no true complex pair means no
  amplitude-independent monodromy residue per echo. The tower's
  "B-violation" is NOT a linear phenomenon;
- the near-pi/30 structure of the phantoms (sessions 14-16) is a property of
  the NEAR-KERNEL GEOMETRY (pseudospectrum), not of true dynamics: the
  softest baseline phantom sits at l = -0.102 +/- 0.122i (rel40 2.3e-06);
  observation, no claim.

**Consequence for the baryon-asymmetry reading.** The static world is
"completely annihilated" at linear order EVEN with live second flows: the
exact spectrum contains only the marginal direction. If the DSS limit cycle
exists (the session-10 picture), it is a FINITE-AMPLITUDE nonlinear object.
Honest next options: (a) third-order tables (the pattern (l+a)(l+b)(l+c)F
generalizes); (b) an independent dd-evolution law (a closure choice — to be
justified, not fitted); (c) measure delta_mono directly from the march
(v10/v11 instrumentation) instead of deriving it. The ~2.9% phantom gap to
pi/30 remains a pseudospectral observation, not a linear residue.

Run: `python3 sympy_second_flows.py` (~40 s), then
`python3 second_flows_exact.py` (~35 s, the decisive instrument).

## 25. v14: third-order tables, the justified dd-closure, delta_mono measured by the march

The three honest next steps of §24, all executed. Machines:
`sympy_third_order.py` -> `results/third_order_tables.json` (~12 s);
`sympy_dd_closure.py` -> `results/dd_closure.json` (~36 s);
`march_delta_mono.py` -> `results/march_delta_mono.json` (~37 s).

### 25.1 (a) Third-order tables: the weight-rule theorem

**Theorem (exact, SymPy).** For a profile of weight p, f(tau)*s^-p with
ds/dy = -1 (tau = -ln s), the n-th y-derivative table is
d^n/dy^n[f s^-p] = s^-p-n * Sum_k c_{n,k}(p) f^(k)(tau), where the
coefficients c_{n,k}(p) are CONSTANTS (purity is part of the theorem) and in
the mode basis factorize EXACTLY as (l+p)(l+p+1)...(l+p+n-1). Verified for
all (p, n) in {0,1,2,4}x{1,2,3}; in particular c_{n,n} = 1 for ALL (n, p):
**the coefficient-1 choice of the dd-slots (session 17, borrowed from the
ddQ precedent) is now DERIVED, not borrowed.**

All machine tables (P0/T0, W0/D0, P2/ddQ, W2, R3, P4, R5) are re-derived
from the profile ansatz as theorems, and the NEW third-order tables are
built — each one is the EXACT y-derivative of the second-order table
(d/dy[G s^-k] = (G' + kG) s^-k-1):
- W2''' / R3''' -> (ddd + 9 dd + 26 d + 24 amp)/s^5 — (l+2)(l+3)(l+4);
- P4''' -> (ddd + 15 dd + 74 d + 120 amp)/s^7 — (l+4)(l+5)(l+6);
- R5'' -> (dd + 9 d + 20 amp)/s^6 — (l+4)(l+5).
Regression: the leading slot coefficient is 1 in ALL generations (third,
second, machine ddQ); dd = 0 reduces the second tables to the adiabatic
audit tables exactly.

### 25.2 The cubic pencil: prolongation-invariance of the spectrum

The prolonged system {F = 0, dF/dtau = 0} has the cubic pencil
M3(l) = [M2(l); l*M2(l)] (36x9), hence M3^T M3 = (1 + l^2) M2^T M2 EXACTLY
(structural identity, verified on exact rational l and on an exact small
matrix): **char3 = (1 + l^2)^9 * char2; rank drops of M3 == rank drops of
M2.** The candidates l = +/-i spawned by (1 + l^2) are PHANTOMS (mpmath
40-digit sigma_min filter: rel40 = 2.3e-05); l = 0 stays GENUINE.
**The third order adds NO genuine linear dynamics — delta_mono = 0 is
robust to the third-order closure. The ~2.9% phantom gap to pi/30 is out of
linear statics' reach.**

### 25.3 (b) The independent dd-evolution law: the prolongation closure

The state is x = (a[9], v[8], dd[3]) = 20 with constraints J1s x = 0
(J1s = [Ja | Jv | J2], 18x20, rank 14) and kinematics a' = P~v (M5h' free).
Justification chain (exact): the residuals are Bianchi-reduced Einstein
identities in y -> their y-prolongation is an identity -> on purified forms
d/dy = (1/s) d/dtau (weight rule) -> the y-prolongation IS the
tau-prolongation = constraint preservation. The closure is therefore NOT a
choice: differentiate the constraints and solve.

Machine facts (baseline kappa = 2, EXACT in Q(sqrt3); one-brick numeric
float64 with clean singular gaps):
- the prolongation d/dtau(J1s x) = 0 has 9 unknowns (M5h', ddT0, ddD0, ddQ,
  ddR1, ddR5, dddW2, dddR3, dddP4; the derivatives of dW2/dR3/dP4 ARE the
  state dd); the unknown matrix Uk (18x9) has rank 9 EXACTLY — **the
  closure is UNIQUE**;
- solvability = hidden constraints Op (v, dd) = 0, rank 5 (9x11);
- the level-2 manifold ker[J1s; Op'] is 3-dimensional; the level-3
  violations Op (v', dd') have rank 1 on it and cut it to **dim M2 = 2**;
  on M2 the evolution is invariant (level-4 violations = 0 EXACTLY);
- **the closed evolution on M2 is B = [[0, -350/61], [0, 0]] EXACTLY:
  B^2 = 0, spec(B) = {0, 0}** — a nilpotent Jordan block of size 2 (statics
  + LINEAR secular drift, no exponentials, no oscillations);
- one-brick: the same structure (rank Uk = 9, dim M2 = 2, |B^2| = 3.9e-13
  at ||B||^2-scaled tolerance, eigenvalues ~ 2.5e-7 ~ 0);
- alternatives (machine facts): C0 (dd = 0) is admissible ONLY on the
  frozen set (the branch equations UV_xi3 = -16 R1h^3 T0h^2 (4T0h^2-27)/27
  and Mdef_xi5 = -8 R1h^2 T0h^2 (4T0h^2-27)/27 share the factor 4T0h^2-27;
  the C1 rows vanish identically; R1h is the flat direction — a 1-dimensional
  frozen manifold); C-chain (flows slaved to the chain) gives only the
  frozen point (session 13, honest citation); **C-prolongation is the ONLY
  justified closure.**

The three routes now agree: the exact pencil (char = 9 l^4 Q18), the exact
index reduction (dim M2 = 2, Jordan-2), and the march (25.4).

### 25.4 (c) delta_mono MEASURED by the march (v10-generation instrumentation)

Two independent marches of the closed linear DAE:
- (m1) coordinate: y' = B y on M2 (B exact from 25.3);
- (m2) ambient: x' = V(x) in R^20 with the closure RE-IMPLEMENTED from the
  raw matrices (Uk-solve at every RK4 stage + projection onto M2), with
  constraint-drift monitoring.

Measurements (baseline; one-brick in parentheses):
- growth law: log-log slope 1.0225 (0.9587) -> asymptotically 1: LINEAR
  secular growth (Jordan-2), NOT an exponential, NOT an oscillation;
- the propagator over one echo Delta_sp = 0.7330382858376652 (v8, model B):
  coordinate eig = (1, 1) EXACTLY at baseline; ambient
  eig = 1 +/- 2.7e-8 i (1 +/- 2.3e-7 i) — the splitting of a DEFECTIVE
  double eigenvalue under roundoff is ~sqrt(eps), an honest numerical FLOOR,
  not a signal; |eig| - 1 < 2.8e-14 (9.3e-14);
- **delta_mono per echo: growth < 2.8e-14 (9.3e-14), phase < 2.7e-8
  (2.3e-7)** — the march CONFIRMS the derived verdict delta_mono = 0 by an
  independent pipeline (ODE integration instead of the spectral one);
- cross-validation m1 vs m2: relative max 4.7e-12 (6.6e-11); constraint
  drift 1.5e-12 (1.7e-11); projection corrections ~1e-13;
- the phantom-gap scale 3.0e-3 (2.9% of pi/30) is 1e4..1e5 times LARGER
  than the march bound — **the gap is NOT reproduced by the linear
  dynamics; it is not a linear monodromy residue.**

### 25.5 Verdict of the session

(a) the pattern (l+a)(l+b)(l+c)F generalizes EXACTLY (weight rule); the
third-order tables exist and are verified — and add nothing to the linear
spectrum (prolongation-invariance); (b) the independent dd-law EXISTS and is
FORCED: the prolongation closure is the unique solution of the identity-
derived constraint preservation (rank Uk = 9), alternatives are degenerate
by machine facts, no fitting anywhere; (c) delta_mono is now MEASURED, not
only derived: 0 with honest bounds (growth ~1e-13, phase ~1e-7 per echo —
the phase bound set by the defectiveness floor). **The baryon-asymmetry
residue of the tower is a FINITE-AMPLITUDE phenomenon: the entire linear
world (statics + de-adiabatized second flows + third-order prolongation)
annihilates exactly. Next campaign: the nonlinear march of the DAE.**

Run: `python3 sympy_third_order.py`, `python3 sympy_dd_closure.py`
(requires the .npy export for (c)), `python3 march_delta_mono.py`.
