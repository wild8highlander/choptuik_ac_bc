# Methods — the numerical machinery of the package

Everything here is deterministic: the only randomness in the whole
package is `numpy.default_rng(20261010)` (committed seed, Part A of
`qhb/constants.py`).  Re-running any campaign reproduces its verdict
bit-for-bit; wall times vary.

---

## 1. The G-model (gap) — `qhb/gap.py`

**Static chain.** Dirichlet chain of N sites, `x_n` centred grid with
step `h = L/(N+1)`, `L = sqrt(8 q_pk / kappa)` (the well ends where
the potential does).  On-site potential `q_n = (kappa/2) x_n^2 - q_pk`.
Continuum-consistent hopping `J = 1/h^2` (with J fixed the effective
mass would diverge and the "gap" would be a band-edge artifact
scaling as h — the committed convention avoids this).  Kinetic
operator `J(2I - adjacency) >= 0`.  Spectrum by tridiagonal
eigensolver (`scipy.linalg.eigh_tridiagonal`, numpy fallback).
Committed geometry: `kappa = 0.05`, `q_pk = 0.4` (a shallow well),
`N = 64`.

**Two-band reduction.** The two lowest levels `|0>, |1>` with static
splitting `Delta_0 = E1 - E0`.

**Drive.** `H(t) = (Delta_0/2) sigma_z + v(t) sigma_x + w(t) sigma_z`
with `v(t) = sum_k b_k cos(omega_k t + phi_k)` (Berry, transverse),
`w(t) = sum_k a_k cos(omega_k t + psi_k)` (braking, longitudinal),
`omega = (2,3,7) * Omega_0`, `Omega_0 = 2`, septinial phases
`phi = psi = (pi/2, pi/3, pi/7)`.

**Floquet.** `U(T0)` built from `M = 1920` piecewise-constant exact
2x2 exponentials (closed form `exp(-i V dt) = cos(w dt) I -
i sin(w dt)/w (cz sz + cx sx)`; unitarity 5.6e-20).  Quasi-energies
from eigenphases folded to `[0, Omega_0)`; gap = the smaller of the
two spacings.  Committed M-convergence: second order
(`p_eff ~ 2`), gap error at M = 1920 is `~7e-9`.

**The rigid trio.** The committed family: `b_k = beta * BERRY_TRIO_k`,
`a_k = beta * BRAKING_TRIO_k` — the three corrections act as ONE
dynamic object with a fixed internal composition (the exact quanta),
scanned by the single amplitude beta.

## 2. The trio engine — `engine/solver.py`

**Dynamics.** Three equal masses, softened Newtonian gravity
(`eps^2 = 1e-2`, committed regularisation — escape statistics, not
micro-dynamics, are the observable), 2D, RK4 fixed step
`dt = 2e-3`, `t_end = 12`, escape radius `R_esc = 12`.

**Early-escape freezing.** A trial whose any body crosses `R_esc` is
flagged and removed from the force computation at the crossing step —
the honest stop.  Survivor energy drift is reported on `V0 = 0` runs
(committed: `2.0e-5` relative); for `V0 > 0` the wall does physical
work and the drift metric is not a quality measure (carried note).

**Ensemble.** `N = 300` trials, seeded `default_rng(20261010)`, drawn
into the committed weakly-bound band `E in [-0.6, -0.05)` (zero total
momentum and position per trial; 18187 draws rejected at packaging —
honest bookkeeping).

**Wall.** `U(r,t) = V0 (1 + cos(Omega t)) max(0, (r - R_b)/w)^2`,
`R_b = 8, w = 1, p = 2` — the gap standing as an oscillating barrier.

**Escape statistic.** `P_esc = fraction of trials escaped by t_end`;
binomial standard error `sqrt(p(1-p)/N)`.

**Lyapunov.** Benettin largest exponent, one tangent vector per
trial, renormalisation every 50 steps, analytic Jacobian of the
softened force plus the wall gradient (committed: free median 0.2615,
trapped median 0.2885 — the wall does not change the chaos).

**Validation anchor (the Roberts of this engine).** Two-body ellipse
`e = 0.5, a = 1, mu = 2` with negligible softening: measured period
`4.442883` vs Kepler `4.442883`, relative error `1.3e-9` — clean RK4
accuracy (`engine.solver.kepler_period_check`, pinned by a test).

## 3. The W-model (Wu door) — `qhb/wu.py`, `engine.solver.wu_mc`

Linear two-rate mean field: `dN_+/dt = Gamma_b - Gamma(1-alpha) N_+`,
`dN_-/dt = Gamma_b - Gamma(1+alpha) N_-`; freeze-out at `t_f = 1/H`,
`x = Gamma/H`.  Closed form `N_± = (Gamma_b/(Gamma u_±))(1 -
e^{-x u_±})`, `u_± = 1 -/+ alpha`; the residual
`r = (N_+ - N_-)/(N_+ + N_-)` is the exact rational function of
theorem T7.

**Stochastic realisation.** `N_± ~ Poisson(Gamma_b t_f (1 - e^{-x
u_±})/x u_±)` (thinned Poisson births) — 200 000 realisations per
cell, seed 20261010; committed max |r_MC - r_formula| = 3.3e-4.

## 4. The period-sampled Floquet spectroscopy (C4 detector)

Build the exact period propagator `U(T0)`; iterate `|psi_n> = U^n|0>`
and sample `S_n = <psi_n|sigma_z|psi_n>` ONCE per period.  The
quasi-energy beat advances `delta = Delta_F * T0` rad per sample
(`< pi` for every committed gap — no aliasing, but the folding rule
is carried anyway).  FFT of the window (zero-padded x8), quadratic
log-peak interpolation in the low band, folded estimate
`gap_meas = f_hat/T0`.  Resolution envelope `2/N` in gap units;
honest resolution criteria: beats >= 3 AND error < resolution/2.

## 5. The drift ladder (C5)

`Delta_N` by exact tridiagonal eigensolver on
`N in {32, 64, 128, 256, 512}`; two-parameter fit
`Delta_N = Delta_cont - C h^2`; climbing effective orders
`p_eff = log(d1/d2)/log 2` on successive absolute differences; exact
channel `C_exact = s * kappa/8` with
`s = d(Delta_0)/d(q_pk)` by central finite difference (committed
`s = -1.00398294`; the sign is real — the widening of the well with
depth dominates the shallow excited level, verified by direct scan).

## 6. The v1.1.0 campaigns (C6-C8)

**C6 — the physical mapping (closed form, no engine).** Each branch
anchor T (a literature comparison value) maps through the exact
Schwarzschild chain: `f = k_B T / h` (the contact frequency),
`M = hbar c^3 / (8 pi G k_B T)` (the mass whose Hawking temperature is
exactly T), `f_gap = Delta_0 f`, `E_gap = h f_gap`.  The machine gates
are the round trip `T_H(M) = T` (rel dev < 1e-12, measured 1.4e-16),
strict mass monotonicity in T, the linear-ratio identity (arithmetic,
carried) and the order window `Lambda_QCD / E_gap(QCD) in (1, 10)`.
The branch honesty tags travel inside the verdict rows.

**C7 — the anharmonic trio (engine v1.1.0).** The pair potential gains
the Cornell-like linear term `U_conf(r) = sigma * r_soft`,
`r_soft = sqrt(r^2 + eps^2)`; the force contribution on body i is
`sigma * d_ij / r_soft` (a constant-magnitude attraction), and the
analytic Benettin Jacobian of the term is
`sigma * (I / r_soft - d d^T / r_soft^3)`.  At `sigma = 0` the code
path is byte-identical to v1.0.0 (the regression gate re-measures the
committed C2 free-trio count with dev 0.0).  The sealing boundary
`V0*(sigma, Omega)` is the minimal V0 with `P_esc <= 0.05` on the
committed ladder (linear interpolation between cells, the C2
convention); the finite-time sealing level 0.05 replaces the C2 1/e
level because the free trio already sits below 1/e.

**C8 — the pairwise Wu door (deterministic ODE).** The committed
nondimensional system is `dn_+/dt = 1 - lambda(1-alpha) n_+ n_-`,
`dn_-/dt = 1 - lambda(1+alpha) n_+ n_-` with `N_* = Gamma_b / H`,
`tau = H t`, freeze-out at `tau_f = 1`, `n(0) = 0`.  Exact structural
facts: alpha = 0 makes the two right-hand sides identical (bitwise
equal trajectories, r = 0.0), and `d(n_+ - n_-)/dt = 2 lambda alpha
n_+ n_- >= 0` (monotone imbalance).  Numerics: RK4 with a 256..2048
convergence ladder (measured order 3.987) and a 50-digit mpmath
`odefun` cross-check at the anchor cell (dev 3.9e-16).  The T7 closed
form does NOT extend — the model has no closed form; that is an exact
structural negative, not a numerical caveat.

## 7. Determinism and reproducibility

- pure float arithmetic in the gap layer (no RNG at all);
- all MC under `default_rng(20261010)`;
- verdicts JSON are the law; `scripts/rebuild_data.py` regenerates
  every derived table from them byte-deterministically (pinned by a
  test);
- campaigns C1/C3/C4/C5 run in seconds; C2 in ~3.5 minutes.

## 8. The v1.2.0 campaigns (C9-C11)

**C9 — the gap phase map (no new parameters).**  The map is the
committed G-model evaluated on a grid: `q_pk in {0.2, ..., 1.0}` (the
regime bound `Delta_0 <= Omega_0/2 = 1` excludes the shallow-well
branch — the two-band reduction itself leaves its validity there) and
`beta in [0, 10]` step 0.25 (41 points; M = 1920 Floquet steps as
committed).  Each cell is classified against the C4 detector floor
`2/N` (N = 64): OPEN / SUBFLOOR / DEGENERATE.  The valley locus is
located by a coarse grid scan plus ternary bisection to 1e-3; the
refinement gate re-runs the bisection at M = 3840 (2x) and the N-gate
re-runs the whole valley at N in {32, 64, 128}.  The counterexample
block evaluates the naive quadratic extrapolation (the C1 window
coefficients, no refit) at its own forecast closure point.

**C10 — the competing models (mask ablation).**  The competing models
ARE masks of the committed drive: for each of the 8 sector subsets the
Berry/braking amplitudes outside the mask are set to exact zero and
the quadratic response is measured on the committed window (21
points, zero-intercept least squares `B2 = sum(shift*b^2)/sum(b^4)`).
Additivity compares each multi-sector B2 against the sum of its
single-sector parts.  The forecast block fits the quadratic on the
sub-window [0, 0.1] only (6 points) and evaluates it at
`beta in {0.3, 0.4, 0.5, 0.6, 0.8}` against the measured wing; the
residual power is the log-log slope of |error| between the first and
last forecast point.  No external data enters anywhere — the
comparison is structural, inside the committed toy.

**C11 — the vortex anchor (own classical layer).**  `qhb/vortex.py`
implements the classical Kirchhoff (1876) point-vortex equations
`dr_k/dt = (1/2pi) sum_{j!=k} Gamma_j zhat x (r_k - r_j)/|r_k - r_j|^2`
with an own fixed-step RK4 integrator (dt = 1e-3) and the four
classical invariants I, H, P, Q.  The triangle block integrates three
full rotations (39,478 steps) and measures rigidity, invariants and
the accumulated rotation angle (unwrapped per-sample increments).  The
linearization is the EXACT analytic corotating Jacobian (no finite
differences; entries in qhb/vortex.py); its spectrum and the
characteristic-polynomial identity `lambda^2 (lambda^2 + omega^2)^2`
are machine-checked, and the symbolic proof is re-derived in SymPy by
the audit (IVP11).  The Aref block launches the classical
right-isosceles (1, 1, -1) configuration (all four invariants vanish
exactly — 50-digit check in IVP11) and integrates t = 12.  The static
barrier block reuses the COMMITTED trio engine at Omega = 0 on the
committed ensemble (300 trials, seed 20261010) with the exact radius
bound evaluated per trial; the oscillating complement re-runs the
(V0 = 0.8, Omega = 2) cell and measures the per-trial |dE| (wall
work).
