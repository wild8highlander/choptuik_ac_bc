# einstein_direct — Direct Solution of the Choptuik Problem from the Classical Einstein Equations

This folder is the core verification laboratory of the repository. It contains a
complete, self-contained numerical and symbolic pipeline that solves the
**Choptuik critical collapse problem** (massless scalar field, spherical
symmetry) *directly* — that is, from the classical Einstein equations obtained
by varying the **Hilbert action** with the Hilbert stress–energy tensor —
without any spectral constructions, ansätze, or fitted parameters.

The guiding discipline of every machine in this folder is the same:

> **hypothesis → machine confirmation → honest caveats and limitations.**

Nothing in the results below is tuned to the literature values. Where an
agreement with a published number is found, it is *reported*; where a
disagreement or a wall is found, it is *reported as well*. The honest negative
results (for example, the mass-scaling floor of the fixed-grid campaign) are
considered results of equal standing with the positive ones.

A much larger, per-campaign verification dossier with all key numbers, tables,
verdicts and reproduction commands lives in
[`verification/README.md`](../verification/README.md). The deep technical
ledger with all 29 sections is [README_EN.md](README_EN.md) in this folder.

---

## 1. What is verified here (executive summary)

### 1.1 Symbolic layer (SymPy + mpmath, 50-digit precision)

- **Hilbert action → Einstein equations in 1+1 double-null coordinates.**
  The full variation of the action with the Hilbert stress–energy tensor is
  carried out symbolically; the resulting system of equations, constraints and
  gauge conditions is verified against the exact Roberts–Oshiro solution with
  residuals of order **10⁻⁴¹** across all five independent structures.
- **Independent re-derivation of the same equations from a different starting
  point** (direct equation-of-motion route) agrees expression-by-expression,
  so the solver input does not depend on a single algebraic path.
- **The center (spinor) hierarchy.** A machine-derived hierarchy of central
  expansion coefficients (O1–O5 and beyond) with exact weights; the Taylor
  patch of the solver evolves these coefficients as internal boundary data.
- **The log-time tower and its spectrum.** Reduction of the verified tower to
  an exact linear system; the characteristic polynomial is obtained in exact
  arithmetic (in Q(√3) at the baseline point); convergence and repulsion
  sectors are separated exactly, including the ±i phantom pair, which is
  confirmed to 40 digits as a pseudospectral artifact rather than a physical
  mode.
- **Third-order tables and the weight rule.** The (p, n)-tables of the third
  order satisfy the exact factorization rule
  `(l+p)...(l+p+n-1)·F` with coefficient 1 on all second-derivative slots
  *derived*, not assumed; the cubic pencil is prolongation-invariant
  (`M3^T M3 = (1+l²) M2^T M2` exactly).
- **The clock-pair theorem (exact, on every brick).** On the static chain the
  two clock candidates (UV book and mass-defect book) share a unique common
  root; the GCD factorization is exact at **12 of 12** rungs of the brick
  ladder δ_k = π/k, with `τ*(δ) = 27/(2−δ²)` — the same closed form as the
  holonomy-corrected family.

### 1.2 Numerical layer (characteristic solver in double null coordinates)

- **Flat-space stability 10⁻¹⁴**; the 2nd-order characteristic march (RK2
  Heun) passes 5/5 regression tests and the full validation suite.
- **Fixed-grid campaign:** bisection of the critical amplitude
  `A* = 0.0805333` at N = 1600; the mass-scaling exponent comes out as
  **γ = 0.109 ± 0.105** against the literature **γ_Ch = 0.374** — an honest
  negative result traced to the mass floor M ≈ 4·du at horizon nucleation
  (documented, not hidden).
- **Multi-zoom regridding machine:** a chain of window regriddings reaches
  log-scale depth **z ≈ 5.9** with the regular center closure and **z ≈ 9.35**
  with the annulus-parity machine (stable stages); the remaining depth wall is
  diagnosed mechanism-by-mechanism.
- **CSS echo period in the data:** Δ ≈ 3.44, consistent with the
  Gundlach–Hodgson value 3.44 ± 0.02; the DSS wiggle fit gives
  `Δ = 6·ln(16/9) = 3.452` as the cycle normalization.
- **Thorne hoop link measured in the data:** `M3/(R1·t0²) = 0.6687` against
  the exact book value 2/3 — a **0.3%** agreement without any fitting.
- **Finite-amplitude echo machine (the PDE machine suite):** three static
  families (flat line, half-tower, one-brick book) are used as the background
  carrier of "living" clocks; the near-critical campaigns measure the clock
  books `κ = ln(64/9)` and `W2/t0² → 4/3` on the eps ladder with the full
  instrumentation of gates, floors and mirror-ring extractors.

### 1.3 Static structure (exact and exhaustive)

- **Factorization theorem (exact):** the rest system on the chain splits into
  *two* equations; `UV_xi3 = 2·R1h·Mdef_xi5` identically, and the C1-chain
  vanishes identically — so the intersection of the static set with the chain
  is exactly `{R1h = 0} ∪ {T0h = 0} ∪ {T0h = T0h*}`.
- **Global static census:** a 2501-cell scan plus 56 Gauss–Newton seeds and a
  300-start free Newton search *off* the chain find **zero** non-degenerate
  static branches beyond the known families; the static kernel is
  one-dimensional (the flat-line tangent). The static structure around the
  critical scale is **exhausted exactly**.
- **The nonlinear DAE march** proves that the only solution manifold through
  the critical point is the flat line of equilibria; the linear M2 direction
  (Jordan-2) is a linearization artifact with no nonlinear flow behind it.

---

## 2. The three static families (the carrier of the living clocks)

The tower of the center admits three exactly-known static configurations,
and the whole echo machinery of the PDE machine is run against this
background:

| Family | Definition | Clock statement |
|---|---|---|
| Flat line | `R1h = 0`, the a-pure kernel direction | carries `F = r = V = 0` exactly; the only non-degenerate branch |
| Half-tower | `R1h → 0` degenerate corner | ring amplitudes vanish; ring clock dead |
| One-brick book | single survivor brick `δ_C = π/7` | moves the unique clock root `τ* = 27/(2κ)` to the observed value |

The survivor brick `δ_C = π/7` is *selected independently* of the tick
obstruction: the intermediate-brick campaign (ladder δ_k = π/k, k = 2…14)
shows the tick obstruction is **non-monotone** in δ, is **not a power law**,
and its minimum is at k = 12, not at k = 7. The brick selection principle is
therefore *not* explained by the tick; it remains an independent (septinial)
sector fact.

---

## 3. Directory map

### 3.1 Derivation and solver core

| File | Role |
|---|---|
| `sympy_derivation.py` | Hilbert action → 1+1 double-null Einstein system (machine-verified) |
| `solver.py` | the characteristic solver: 2nd-order march, annulus parity, Taylor patch, measurement instrumentation |
| `zoom_solver.py` | multi-stage regridding (zoom) machinery on top of the solver |
| `roberts_test.py` | Roberts–Oshiro exact-solution regression |
| `choptuik_scaling.py` | fixed-grid bisection + mass-scaling driver |
| `figures.py` | base campaign figures (RU/EN, 300 dpi) |

### 3.2 Center closure and zoom campaigns

| File | Role |
|---|---|
| `zoom_campaign.py` | the prototype zoom campaign (honest status quo of the wall) |
| `zoom_campaign_regular.py` | regular center closure protocol + spinor wall diagnostics |
| `zoom_campaign_taylor.py` | central Taylor patch: ODE-evolved t0/d0 as internal boundary data |
| `sympy_center.py` | machine derivation of the central (spinor) hierarchy for the Taylor patch |
| `sympy_center_o6.py`, `sympy_center_o6_nsolve.py` | O6+ sector of the center; nsolve verdict on the truncated tower |
| `center_modes.py` | z-reduction of the center tower; CSS fixed-point clock from the tower itself |

### 3.3 Spinor analysis and the π/15, π/30 exponents

| File | Role |
|---|---|
| `spinor_analysis.py` | Z₂ mirror-parity decomposition of the center; π/15, π/30 diagnostics |
| `spinor_figures.py` | spinor campaign figures (RU/EN) |
| `spinor_ladder.py` | the spinor ladder of exponents and its relations |
| `sympy_spinor_corrections.py` | embedding of the b-C / a-C / a-B corrections into the towers |
| `s4_berry_one_brick.py` | the one-brick Berry screening: κ = 2 − π²/98 |

### 3.4 The PDE machine suite (finite-amplitude echo on static families)

| File | Role |
|---|---|
| `grid_machine_annulus.py` | annulus parity + echo-aware fits → percent-level τ* (no anchors) |
| `grid_machine_hexcheck.py` | hexcheck campaign: κ = ln(64/9) and W2/t0² → 4/3 on the eps ladder |
| `grid_machine_mirror.py` | mirror-ring pairs (ξ, −ξ): clean W2/t0² measurement |
| `probe_channel_trace.py` | line-by-line tracer of the stage-death channel j = 19–20 |
| `hexcheck_figures.py` | hexcheck campaign figures (RU/EN, 300 dpi) |

### 3.5 Hexcycle, DAE march, static census

| File | Role |
|---|---|
| `sympy_hexcycle.py` | the Poincaré hexagonal transformation cycle of the figures |
| `hexcycle_figures.py` | hexcycle figures (station wheel, dynamics/books) |
| `dae_nonlinear_core.py` | nonlinear DAE core: full F(x), x-dependent Jacobians, exact prolongation |
| `march_dae_nonlinear.py` | the nonlinear DAE march (flat-line verdict) |
| `march_delta_mono.py` | δ_mono measured by two independent marches |
| `hexcycle_dae.py` | the figure cycle embedded in the nonlinear DAE tower (global predictor) |
| `global_static_search.py` | the exhaustive global static census (scan + multi-start Newton) |

### 3.6 Brick ladder, clock closure, second flows

| File | Role |
|---|---|
| `brick_scan_tick.py` | intermediate bricks: tick obstruction vs δ on the ladder δ_k = π/k |
| `clock_closure_t1c.py` | clock closure through the one-brick T1c source form + erratum audit |
| `sympy_second_flows.py`, `second_flows_exact.py`, `second_flows_verify.py` | second flows as limit-cycle variables (linear verdict) |
| `sympy_third_order.py` | third-order tables and the weight rule |
| `sympy_dd_closure.py` | the independent dd-evolution law and prolongation closure |
| `sympy_spectrum_tau_star.py` | exact spectrum of the corrected system at τ* |
| `sympy_p4_einstein_hilbert.py` | P4 closure: the shape cycle in Einstein *and* Hilbert equations |

### 3.7 Data and tests

| Path | Role |
|---|---|
| `results/*.json` | machine-readable results of every campaign (one JSON per machine) |
| `figures/fig_ru/`, `figures/fig_en/` | 300 dpi figures, Russian and English variants |
| `tests/test_einstein_direct.py` | the pytest verification suite (21 tests) covering all major machine theorems |
| `report_en.pdf`, `report_ru.pdf` (+ `.tex`) | the first written report of the folder |
| `hexcycle_report_en.pdf`, `hexcycle_report_ru.pdf` (+ `.tex`) | the hexcycle report |

---

## 4. How to run

Everything runs on an ordinary laptop and on a phone (Termux) with
Python ≥ 3.9, NumPy, SciPy, SymPy, matplotlib and pytest.

```bash
# 1. machine-verified derivation + solver validation
python3 sympy_derivation.py
python3 roberts_test.py

# 2. fixed-grid campaign (bisection + scaling)
python3 choptuik_scaling.py --n-bisect 1200

# 3. zoom campaigns (from prototype to stable chains)
python3 zoom_campaign.py
python3 zoom_campaign_regular.py        # ~5–8 min
python3 zoom_campaign_taylor.py         # ~20–40 min

# 4. the PDE machine suite
python3 grid_machine_annulus.py         # full eps ladder
python3 grid_machine_hexcheck.py        # hexcheck campaign
python3 grid_machine_mirror.py          # mirror-ring pairs

# 5. symbolic campaigns
python3 sympy_center.py
python3 sympy_hexcycle.py
python3 sympy_p4_einstein_hilbert.py
python3 sympy_third_order.py
python3 sympy_dd_closure.py
python3 sympy_second_flows.py
python3 sympy_spinor_corrections.py
python3 sympy_spectrum_tau_star.py

# 6. DAE march and static census
python3 march_dae_nonlinear.py
python3 march_delta_mono.py
python3 hexcycle_dae.py
python3 global_static_search.py
python3 brick_scan_tick.py
python3 clock_closure_t1c.py

# 7. the verification suite
python3 -m pytest tests/ -q             # 21 tests
```

All machines are single-threaded on purpose
(`OPENBLAS/OMP/MKL/NUMEXPR_NUM_THREADS = 1`): multithreaded LAPACK reshuffles
near-critical bisection and horizon nucleation and breaks reproducibility.

---

## 5. Honesty policy

- **No fitting to literature values.** γ_Ch = 0.374, b_Ch = 0.37651 and the
  spinor ladder π/30 are used only as *comparison anchors*, always labelled as
  such in the outputs.
- **Negative results are kept.** The fixed-grid mass floor, the depth wall,
  the frozen-tower verdicts, the tick non-selection of the brick, the 0/18
  static carriers — all of these are first-class results and are included in
  the JSONs and in the verification dossier.
- **Every number is traceable.** Each campaign writes a JSON into
  `results/`; the pytest suite re-checks the major theorems from those JSONs.
- **Known limitations are stated** next to each verdict: truncated towers,
  pseudospectral artifacts, Newton-path dependence, Puiseux branch jumps at
  soft poles, and the boundary between what the symbolic layer proves and
  what the numerical layer only measures.
