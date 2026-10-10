# Changelog — Quark-Hawking Bridge

## 1.2.0 — the evidence block C9–C11 + the Evidence Engine (2026-10-10)

The package learns to separate the proven, the measured, the compared
and the hypothesised.  Three new committed campaigns, three new
theorems, a claims registry and a three-check audit extension:

- **C9 — the gap phase map.**  The committed G-model is mapped over
  the whole searched (beta, q_pk) plane (beta in [0, 10], q_pk in
  [0.2, 1.0], the regime bound Delta_0 <= Omega_0/2 honestly excludes
  the shallow-well branch).  Every cell is OPEN against the committed
  detector floor 2/N: **the gap never closes on the searched range**
  (a finite-range statement).  The measured phase feature is the
  NARROWING VALLEY — the gap reaches a minimum (Delta_F,min = 0.182,
  beta* = 3.3583 at the committed geometry) and REOPENS (quasi-energy
  band structure); the valley is grid-refinement reproducible (dev
  0.0002 < 0.05) and N-stable (< 0.001).  Machine-found counterexample
  to the naive window extrapolation: the quadratic law forecasts
  closure at beta_c = 2.9910; the measured gap there is 6.3x the floor.
  Gates P1–P4 all PASS (~11 s);
- **C10 — the competing models (factorial ablation).**  The three
  septinial sectors are switched off in all 8 combinations: the causal
  map is **A 91.95% / B 8.00% / C 0.049%** of |B2|, additive to
  1.3e-4 (max cross-share), with the T2 evenness holding on every
  transverse configuration (machine zeros) and the braking-only drive
  exactly invisible.  The septinial C sector is structurally present
  and causally a spectator in magnitude — carried, not hidden.  The
  out-of-window forecast gate quantifies the wing: the quadratic
  fitted on [0, 0.1] fails beyond it (error share 0.3% -> 2.3%,
  residual power 4.07 — the quartic wing of C1, now a forecast
  statement).  Gates Q1–Q3 PASS (~4 s);
- **C11 — the vortex anchor and the static barrier.**  The classical
  three-vortex problem (Kirchhoff 1876) enters the package as its own
  code layer (`qhb/vortex.py`), implemented from the classical
  equations with the package's own paths:
  **T11 (exact)** — the stability contrast: the SAME equilateral
  triangle that is Gascheau-unstable under 1/r attraction (T4) is a
  rigidly rotating NEUTRALLY stable relative equilibrium of the
  Kirchhoff problem (omega = Gamma_tot/(2 pi a^2) = 3/(2 pi);
  spectrum {0, 0, ±i-omega, ±i-omega}, max |Re| = 2.8e-17; the
  characteristic polynomial `lambda^2 (lambda^2+omega^2)^2` proven
  symbolically in SymPy with dev 0); the rotation is rigid to 1.5e-14
  over three full rotations.  **T12 (measured)** — the invariant wall:
  on the classical Aref (1979) manifold (I = H = P = Q = 0, machine
  zeros at 50 digits) the mixed-sign trio stays bound WITHOUT ANY WALL
  (r_max = 2.7654 << 12, invariants pinned to 1.5e-12).  **T13
  (exact)** — the static barrier: with the wall frozen (Omega = 0) the
  committed engine obeys the exact radius bound
  r <= R_b + w sqrt((E0 + 3/sqrt(soft2))/(2 V0)); escape is EXACTLY
  impossible at V0 >= 1.6 (V* = 0.9359375) — the first EXACT
  confinement statement of the package; at Omega > 0 the wall pumps
  energy (median |dE| = 0.146) and the C2/C7 sealing stays
  finite-time.  All gates PASS (~35 s);
- **the Evidence Engine.**  `results/claims_registry.json` +
  `results/CLAIMS.md` + `qhb/claims.py`: **27 claims** in five
  statuses (exact / measured-law / honest-negative / hypothesis /
  comparison), each with a five-field uncertainty budget (statistical,
  discretization, solver, parameter, model) and a pre-committed
  falsification criterion; validated at build time;
- **the audit IVP-08 -> IVP-11.**  Three new hostile checks: IVP09
  (the phase-map gate: fresh cells + an independent valley bisection),
  IVP10 (the competing-model gates at doubled Floquet resolution) and
  IVP11 (the vortex layer: the SymPy charpoly dev 0, the 50-digit Aref
  zeros, the eigenvalue gate).  **11/11 PASS**;
- **data** 8 new tables (phase_map, phase_valley,
  phase_counterexample, ablation, forecast, ablation_additivity,
  barrier_cells, vortex_anchor) — byte-deterministic; **figures** 3
  new 300-dpi architectures (40 total) + 5 new hires (100 @600dpi);
- **twins** JS/C/C++ 14/14 each (the vortex Lagrange rate joins the
  block; Go/Rust/Julia sources updated);
- **tests**: 94 passed (34 new pins: the C9–C11 verdicts, the vortex
  layer units, the claims registry); docs gain `docs/phase_map.md` and
  the T11–T13 theory sections; the roadmap closes C9–C11 + the
  Evidence Engine.

## 1.1.0 — the roadmap campaigns C6–C8 (2026-10-10)

The three roadmap campaigns land, each with its committed deterministic
verdict and its honesty marks:

- **C6 — the physical mapping (three branches).** The marked scale
  hypothesis (code-unit gap -> Hz through a contact temperature) is
  promoted to a three-branch comparison: Lambda_QCD = 332 MeV (a
  renormalisation scale — comparison device), the QCD crossover
  155.16 MeV (the only true temperature; the committed T8 contact) and
  the electroweak VEV 246.22 GeV (the least honest branch — marked).
  Exact gates: round trip T_H(M) = T to 1.4e-16, mass monotonicity,
  the linear-ratio identity (carried as arithmetic), the order window
  Lambda/E_gap(QCD) = 4.09.  The mapped gap quantum at the QCD contact:
  E_gap = 81.1 MeV (comparison only, NOT a derivation of Lambda_QCD);
- **C7 — the anharmonic trio.** The engine gains a Cornell-like
  confining core U_conf = sigma * r_soft (backward compatible; the
  sigma = 0 regression gate reproduces the C2 free-trio count with dev
  0.0 EXACTLY).  Three committed laws: L1 the flux tube closes the
  finite-time escape channel (P_esc 0.2433 -> 0.06 at sigma = 0.02 ->
  0.0033 at 0.05, monotone); L2 the wall boundary V0* SHRINKS by ~7.1x
  (Omega = 0) / ~7.6x (Omega = 2) as sigma goes 0 -> 0.02 — the core
  replaces the wall; L3 bound chaos without any wall (median Lyapunov
  0.264, 100% positive);
- **C8 — the Wu door with pair-consuming kinetics.** The linear mean
  field is replaced by pairwise annihilation with the trigger
  asymmetry; the T7 closed form does NOT extend (an exact structural
  negative).  The machine checks: alpha = 0 gives r = 0.0 bitwise,
  the imbalance is monotone, the RK4 ladder measures p_eff = 3.987,
  and the 50-digit mpmath cross-check agrees to 3.9e-16.  The door
  stays and the shape moves: r_pair climbs to 0.988 at lambda = 100
  (alpha = 0.9) — the linear alpha-limit 0.9 is left behind (the FULL
  imbalance of the toy);
- **data** 6 new tables (mapping_branches, anharmonic_free/grid,
  anharmonic_boundary, pairwise_residual, pairwise_checks) —
  byte-deterministic from the verdicts; **figures** 3 new hires
  architectures (80 @600dpi total); **workbook** +3 sheets (15);
- **tests**: 55 passed (9 new pins); the honesty ledger and the
  roadmaps are updated (C6–C8 closed; the engine modernisation and
  the interactive delivery remain).

## 1.0.0 — the first public build (2026-10-09)

The full research package for the confinement hypothesis built on the
three septinial corrections:

- **core** `qhb/`: constants (A/B/C), the G-model gap, the Gascheau
  layer, the Wu door, the bridge with both contact points (QCD + CMB),
  the ladders, the 50-digit layer (9/9 PASS);
- **engine** `engine/`: the vectorised trio with the oscillating wall,
  early-escape freezing, Benettin Lyapunov, the Poisson Wu realisation,
  the Kepler anchor (1.3e-9);
- **campaigns C1–C5** with committed deterministic verdicts;
- **theorems T1–T10** including the exact negatives (Gascheau; the free
  trio unbinds; the unresolved floor tail; the unclaimed Delta_cont)
  and the honest signed channel share (-0.209);
- **figures** 28 @300dpi + 68 @600dpi (RU/EN x light/dark) + logo;
- **animations** 12 (3 x RU/EN, GIF+MP4);
- **workbook** 12 sheets; **twins** 13/13 x3 verified + 3 sources;
- **monograph** 2 volumes x RU/EN x DOCX+PDF (postcheck 0 errors);
- **audit IVP-08**: 8/8 PASS; **tests**: 46 passed.
