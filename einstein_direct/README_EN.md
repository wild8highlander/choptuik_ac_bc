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
