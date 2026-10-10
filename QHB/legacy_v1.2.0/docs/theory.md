# Theory — the Quark-Hawking Bridge

This document states the physical content of the package in one place:
what is measured, what is mapped, what is compared, and what is
honestly not (yet) measurable.  It is the reference for everything the
code does.  **The confinement mechanism of the package is a marked
HYPOTHESIS; every theorem below is a machine-checked fact about the
committed toy models, not a derivation of QCD.**

---

## 0. The riddle and the proposal

Quarks are never observed alone — only inside hadrons (confinement).
QCD gives overwhelming numerical evidence (lattice) but no analytic
proof; the statement is part of the Yang–Mills mass-gap millennium
problem.  The proposal of this package, inherited from the
Collapse-Hawking Bridge (CHB), is a four-link mechanism:

> **H1.** Quark triplets are welded at maximal density — the
> critical-collapse regime of CHB, where the born mass tends to zero
> and the mean horizon density tends to the Planck density.
> **H2.** The three dynamic corrections of the septinial family
> (Berry quanta `pi^2/8, pi^2/18, pi^2/98` and braking quanta
> `pi^5/704, pi^5/5346, pi^5/369754` of the `pi/2, pi/3, pi/7`
> sectors) are not decorations: they DRIVE the sampled geometry and
> open a real spectral gap `Delta_F` (the mass-gap analog).
> **H3.** Hawking pairs leave the horizon; the weak channel is
> parity-asymmetric (Wu 1957), so a residual imbalance of matter
> survives annihilation — the Wu door.
> **H4.** A triplet bound at maximal density cannot shed a member:
> the unsolved three-body problem shares energy chaotically, and the
> gap stands as an oscillating geometric wall — bound chaos, i.e.
> confinement in the toy model.

Each link is developed numerically in its own campaign (C1, C3, C2
respectively; the bridge mapping ties them to masses).

## 1. The two inherited pillars (from CHB v2.1.0)

**Critical collapse.** At the threshold of black-hole formation the
mass scales as `M ~ (A - A*)^gamma` with the universal exponent
`gamma_Ch = 0.374` (literature anchor; CHB), the inner evolution
echoes with period `Delta = 3.44 +- 0.02`, and the born spectrum is
the dimensionless profile `f~(eps) = M_code(eps)/M_code_sat` with the
committed members `f~ = 0.2877 / 0.2684 / 1.0` (CHB campaign C1).

**Black-hole thermodynamics.** Closed-form Schwarzschild relations:
`T_H = hbar c^3 / (8 pi G M kB) ~ 1/M`, `S_BH ~ M^2`,
`t_evap ~ M^3`, Page fraction `1 - 2^{-3/2}` — all inherited verbatim
in `qhb/bridge.py`.

The bridge mapping is taken over unchanged:

```
M_BH(eps; M_in) = M_in * f~(eps)
```

## 2. The three corrections (theorem T1 layer, exact)

From the Einstein Direct block `spinor_corrections.json` (cross-
referenced by CHB), the spinor phases of the Klein-quartic family are

```
delta_A = pi/2,   delta_B = pi/3,   delta_C = pi/7
```

with beta(d) = d^2/2 (Berry quanta) and alpha(d) = d^5/22 (braking
quanta, k = b2(K3) = 22):

```
bA = pi^2/8,   bB = pi^2/18,   bC = pi^2/98
aA = pi^5/704, aB = pi^5/5346, aC = pi^5/369754
```

All six are exact and verified at 50 digits (`qhb/validate.py`,
check 1).  **In this package they are the drive**: the Berry quanta
modulate the geometry transversally, the braking quanta
longitudinally.

## 3. The G-model and the gap law (theorems T2/T3, campaign C1)

The committed model (full spec in `methods.md`): a Dirichlet chain of
N = 64 sites carrying the sampled parabolic well
`q_n = (kappa/2) x_n^2 - q_pk` (continuum-consistent hopping
`J = 1/h^2`), its two lowest levels reduced to a two-band system, and
the three corrections applied as a three-tone drive at
`omega = (2,3,7) * Omega_0`, `Omega_0 = 2`, with the septinial phases.

**T2 (exact + machine).** The gap is EXACTLY even under the global
Berry flip `b -> -b` (`U(-b) = sigma_z U(b) sigma_z`; measured dev
0.0).  The braking channel alone opens NOTHING at any order
(integer-tone cancellation; measured dev 0.0 — the braking quanta act
only jointly with the Berry drive, through the Magnus commutator
`[w sigma_z, v sigma_x]`).  The residual a-flip asymmetry
`~1.5e-6` at beta = 0.4 is the genuine odd-in-a response — carried as
data.

**T3 (machine law).** On the committed window `beta in [0, 0.2]`:

```
Delta_F = Delta_0 + B2 * beta^2 ,   Delta_0 = 0.523004556028,
B2 = -5.49670294e-2 ,  r^2 = 0.99999982
```

The drive CLOSES the gap (B2 < 0): the dynamic corrections shift the
geometry — exactly the mechanism the hypothesis proposes.  The
per-sector responses carry the septinial hierarchy:

```
B2_A(pi/2) = -5.05483488e-2 ,  B2_B(pi/3) = -4.40077100e-3 ,
B2_C(pi/7) = -2.71009207e-5    (hierarchy ~ 1865 : 1)
```

Beyond the window the response is quartic-dominated (the wing rows
are carried unfitted — the honest pre-asymptotic story).

## 4. The three-body trap (theorems T4/T5/T6, campaign C2)

**T4 (exact, classical).** The equilateral Lagrange solution is
linearly unstable for equal masses: the Gascheau criterion
`nu = (m1m2 + m2m3 + m3m1)/(sum m)^2 < 1/27` fails, since equal
masses give `nu = 1/3`.  Growth rate `sqrt(3/2)` per mean motion.
**No static rigid triangle exists** — the honest negative that kills
any naive "rigid triangle" story.

**T5 (measured negative).** On the committed weakly-bound ensemble
(E in [-0.6, -0.05), N = 300, seed 20261010) the free Newtonian trio
unbinds: `P_esc = 0.2433 +- 0.0248`.  Static gravity does not
confine.

**T6 (measured law).** With the oscillating geometric wall
`U(r,t) = V0 (1 + cos(Omega t)) max(0, (r - R_b)/w)^2`
(R_b = 8, w = 1, p = 2) standing at the committed gap scale, escape
collapses to `P_esc < 1e-4` at every committed `V0 >= 0.4` cell, for
every `Omega in {0,1,2,4}`.  The Benettin exponents stay positive and
comparable (free 0.262, trapped 0.289, medians): **the wall does not
change the chaos — it changes the EXIT.  Bound chaos is the committed
confinement picture of the toy model.**

## 5. The Wu door (theorem T7, campaign C3)

Linear two-rate model: two species born at the Hawking rate
`Gamma_b`, annihilating at `Gamma(1 -/+ alpha)`; freeze-out at
`t_f = 1/H`.  The closed-form residual is exact:

```
f(u) = (1 - e^{-x u})/u ,  x = Gamma/H
r(alpha, x) = [f(1-alpha) - f(1+alpha)] / [f(1-alpha) + f(1+alpha)]
```

Limits (50-digit layer): `r(0, x) = 0`, `r(alpha, inf) = alpha`,
`r(alpha, 0) = 0`.  The seeded realisation (200k per cell) agrees to
`max dev = 3.3e-4`.  At the Wu anchor (alpha = 0.9, approximate
literature anchor) and x = 100: `r = 0.899996` — the door opens
almost fully.  **Honest scope:** leaving only the PDG
`eta = 6.1e-10` requires `x ~ 1e9`; the model realizes the Sakharov
ingredients qualitatively (CP violation, out-of-equilibrium), NOT
baryogenesis (B is conserved in the toy).  The door is a door.

## 6. The two contact points (theorem T8, closed form)

Setting `T_H(M) = T` for the two anchor temperatures:

```
CMB contact (inherited): T_CMB = 2.72548 K   ->  M = 4.5016e22 kg
QCD contact (T8):        T_QCD = 155.16 MeV  ->  M = 6.8140e10 kg
```

The QCD contact is the black hole whose Hawking temperature equals
the deconfinement crossover: the hole that BOILS QUARKS.  Literature
comparison: primordial holes of the QCD epoch `~ 1e11 kg` — same
order (ratio 0.68), comparison only, 0.67%-style honesty.

## 7. The spectral floor (theorem T9, campaign C4)

A gap that cannot be measured does not exist for the detector.  The
committed period-sampled Floquet spectroscopy resolves the beat only
when at least 3 beats fit the window and the peak error is under half
the Fourier resolution `2/N`.  Committed: unresolved at `T_sim = 20`
(beats 1.53 < 3 — the CHB echo language), resolved at 40–320 with the
errors riding the `2/N` envelope (measured exponent 2.39 is
interpolation noise below the envelope; carried as data).

## 8. The gap-drift law (theorem T10, campaign C5)

The heir of CHB T10: the SAMPLED geometry shifts the gap.  Lemma A
(exact, inherited): a sampled parabola loses `kappa h^2/8` of its
peak (worst alignment; the committed centred chain IS the worst
alignment — machine-verified to 0.0).  With the measured response
`s = d(Delta)/d(q_pk) = -1.00398294`:

```
Delta_N -> Delta_cont ,   Delta_cont - Delta_N = C h^2 + O(h^3)
C_measured = +3.0089e-2 ,  C_exact = s*kappa/8 = -6.275e-3
exact-channel share = -0.209  (the Lemma-A channel OPPOSES the
kinetic-dispersion channel — honest, signed)
p_eff = 1.948 -> 1.974 -> 1.987  (climbing to 2)
```

`Delta_cont` is fitted for display and **NOT claimed** (two-term
extrapolation of a pre-asymptotic ladder — mirrors the CHB `A*_inf`
negative).  Note the sign mirror: the CHB threshold ladder
approached the continuum from above, the gap ladder approaches from
below — the sign is carried, not hidden.

## 8b. The physical mapping: three branches (C6, v1.1.0)

The marked scale hypothesis (the code-unit gap rides a contact
temperature into Hz) is now a THREE-branch comparison with per-branch
honesty tags: `Lambda_QCD = 332 MeV` — a renormalisation scale, the
weakest claim; `T_QCD = 155.16 MeV` — the only true temperature, the
committed T8 contact; `v_EW = 246.22 GeV` — a VEV, not a bath
temperature, the least honest branch.  The mapped gap quantum at the
QCD contact is **E_gap = 81.1 MeV**, within one decade of Lambda_QCD
(ratio 4.09) — an explicitly non-derivational order comparison.

## 8c. The anharmonic trio and the pairwise door (C7/C8, v1.1.0)

Two mechanism-level bridges landed with the roadmap block:

- **The flux tube (C7).** A Cornell-like linear core `sigma * r_soft`
  joins the toy.  The regression gate is EXACT (dev 0.0 against the
  committed C2 count).  Three laws: the escape channel closes
  monotonically (P_esc 0.2433 -> 0.0033 by sigma = 0.05); the wall
  boundary V0* SHRINKS x7.1-x7.6 as sigma goes 0 -> 0.02 (the core
  replaces the oscillating wall of T6); bound chaos survives without
  any wall (median Lyapunov 0.264, 100% positive) — confinement does
  not freeze the dynamics.
- **The pairwise door (C8).** Pairwise annihilation with the trigger
  asymmetry replaces the linear mean field.  The T7 closed form does
  NOT extend (exact structural negative); the machine replacements are
  the bitwise no-door check, the monotone-imbalance identity, the RK4
  ladder (p_eff 3.987) and the 50-digit cross-check (3.9e-16).  The
  door STAYS, the SHAPE MOVES: r_pair climbs to 0.988 at lambda = 100
  (alpha = 0.9) — the linear alpha-limit is left: the toy accumulates
  the FULL imbalance.

## 8d. The gap phase map and the causal map (C9/C10, v1.2.0)

**The phase map (C9).** The window law T3 is a WINDOW law; campaign C9
maps the whole searched drive range.  Over the committed
`(beta, q_pk)` plane (beta in [0, 10], q_pk in [0.2, 1.0], the regime
bound `Delta_0 <= Omega_0/2 = 1` honestly excludes the shallow-well
branch) every cell is OPEN against the detector floor `2/N` — the gap
NEVER closes on the searched range (a finite-range statement, never a
proof of eternal openness).  The measured phase feature is the
NARROWING VALLEY: the gap reaches a minimum (`Delta_F,min = 0.182` at
the committed geometry, `beta* = 3.3583`) and REOPENS — quasi-energy
band structure the window law cannot see.  The valley is
grid-refinement reproducible (dev 0.0002 < 0.05) and N-stable
(shifts < 0.001).  The campaign also carries a machine-found
counterexample: the quadratic law extrapolated beyond its window
forecasts closure at `beta_c = 2.9910`; the measured gap there is
`0.1978 = 6.3 x` the floor.  Window laws are window laws.

**The causal map (C10).** A factorial ablation of the three septinial
sectors (8 configurations) measures the quadratic response of each:
`A` carries 91.95%, `B` 8.00%, `C` 0.049% of `|B2|`; the leading
response is additive (max cross-share 1.3e-4 < 1%) and the T2 evenness
holds on every transverse configuration (machine zeros).  The honest
reading: the septinial C sector is STRUCTURALLY present (the family)
but a causal spectator in magnitude; the sector hierarchy 1865 : 1 is
the committed carrier.  The out-of-window forecast gate quantifies how
fast the quadratic fitted on [0, 0.1] fails beyond it: error share
0.3% -> 2.3% by beta = 0.8, residual power 4.07 (the quartic wing).

## 8e. The vortex anchor and the static barrier (C11, v1.2.0)

Campaign C11 adds the classical contrast layer and the first EXACT
confinement statement of the package.

**T11 (exact): the stability contrast.**  In the classical three-vortex
problem (Kirchhoff 1876) the SAME equilateral triangle that is linearly
unstable under `1/r` attraction (T4) is a rigidly rotating relative
equilibrium with `omega = Gamma_tot/(2 pi a^2) = 3/(2 pi) =
0.477464829...` (unit circulations, unit side), and its corotating-frame
linearization is NEUTRAL: the exact analytic Jacobian has spectrum

```
{0, 0, +i omega, -i omega, +i omega, -i omega}
```

every eigenvalue on the imaginary axis or at the origin (machine:
max |Re| = 2.8e-17 on the imaginary pairs; the symbolic characteristic
polynomial is EXACTLY `lambda^2 (lambda^2 + omega^2)^2` — SymPy,
dev 0; IVP11).  The measured rotation is rigid to 1.5e-14 over three
full rotations with `omega` measured = exact to 1.6e-14 and all four
invariants drifting below 2.2e-14.  Reading for H4: "three-ness" does
not create the escape channel — the INTERACTION decides; the trap is a
property of the physics, not of the triangle.

**T12 (measured): the invariant wall.**  The mixed-sign (1, 1, -1)
right-isosceles launch annihilates all four classical invariants at
once (`I = H = P = Q = 0`, machine zeros at 50 digits) — the classical
Aref (1979) collapse manifold.  On it the trio evolves NON-rigidly,
bound WITHOUT ANY WALL on the committed horizon: `r_max = 2.7654 << 12`
at `t = 12`, invariants pinned to 1.5e-12.  Confinement by invariants —
the topological complement of the geometric wall (the angular impulse
`I = sum Gamma_k |r_k|^2` is the classical prototype of the Chaplygin
topological integral).  Honest scope: the manifold is measure-zero;
the collapse separatrix itself is classical and is NOT integrated.

**T13 (exact, for the committed engine): the static barrier.**  With
the wall frozen (`Omega = 0`) the engine energy is conserved and the
wall potential grows without bound, so every solution of the committed
softened engine obeys the exact radius bound

```
r_i(t) <= R_b + w * sqrt( (E0 + 3/sqrt(soft2)) / (2 V0) )
```

(softened pair floor `-3/sqrt(soft2)` carried exactly).  Escape —
crossing `R_ESC = 12` — is therefore IMPOSSIBLE whenever
`V0 > V* = (E0_max + 3/sqrt(soft2)) w^2 / (2 (R_ESC - R_b)^2) =
0.9359375` on the committed band.  The committed C2 cells with
`V0 >= 1.6` at `Omega = 0` are EXACTLY sealed — a theorem about the
engine equations, not a Monte-Carlo frequency (measured: 0/300 escapes
with bound margins >= 2.76, energy drift abs <= 7.6e-5).  The honest
stratification that T13 produces:

```
V0 >= V* (Omega = 0):  escape impossible            (exact, proven)
V0 <  V* (Omega = 0):  escape allowed by the bound, NOT OBSERVED
                       (0/300 on the committed horizon)
Omega > 0:             the wall pumps energy (median |dE| = 0.146);
                       the C2/C7 sealing is a FINITE-TIME statement
```

The oscillating wall does work — the static seal is exact, the
oscillating seal is measured.  Both marks travel with the numbers.

## 9. What is NOT claimed (the honest scope)

1. The G-model gap is NOT the Yang–Mills mass gap; the mapping of the
   code-unit gap to physical scales is a marked hypothesis (a scale
   choice through the QCD contact, comparison to `Lambda_QCD` only).
2. The trio trap is NOT QCD confinement; it demonstrates a MECHANISM
   (dynamic wall + chaotic energy sharing) inside a softened
   Newtonian toy.
3. The Wu door does not reproduce cosmogenesis.
4. `Delta_cont`, like CHB's `A*_inf`, is not claimed.
5. The no-closure statement of C9 is finite-range; the invariant wall
   of T12 is a measure-zero manifold; the static barrier of T13 is a
   theorem about the committed SOFTENED engine equations.

## 10. References

1. Wu, C. S. et al. (1957). Experimental test of parity conservation
   in beta decay. *Phys. Rev.* 105, 1413.
2. Lee, T. D., Yang, C. N. (1956). Question of parity conservation
   in weak interactions. *Phys. Rev.* 104, 254.
3. Gascheau, G. (1843). Sur l'équilibre d'un système de trois points
   matériels qui s'attirent mutuellement. *C. R. Acad. Sci.* 16.
4. Routh, E. J. (1875). On the stability of a given state of motion.
5. Choptuik, M. W. (1993). Critical behavior in gravitational
   collapse. *Phys. Rev. Lett.* 70, 9.
6. Hawking, S. W. (1975). Particle creation by black holes.
   *Commun. Math. Phys.* 43, 199.
7. Page, D. N. (1993). Average entropy of a subsystem.
   *Phys. Rev. Lett.* 71, 1291.
8. Borsanyi, S. et al. (2020). Calculation of the axion mass based on
   high-temperature lattice quantum chromodynamics. *Nature* 539, 69
   (the 155 MeV crossover anchor).
9. Isaev, I. Kh. (2026). Collapse-Hawking Bridge v2.1.0 — the parent
   package of this research.
10. PDG (2024). Review of Particle Physics (the eta_baryon anchor).
11. Kirchhoff, G. (1876). Vorlesungen über mathematische Physik:
    Mechanik. Leipzig: Teubner (the point-vortex equations).
12. Groebli, M. (1877). Spezielle Probleme der Bewegungslehre. Bern.
13. Aref, H. (1979). Motion of three vortices revisited. *Phys.
    Fluids* 22, 393 — the collapse manifold `I = H = P = Q = 0`.
14. Synge, J. L. (1949). On the motion of three vortices. *Can. J.
    Math.* 1, 257 (the linear stability classification).
15. Chaplygin, S. A. — the classical three-vortex special cases; the
    topological-integral prototype `I = sum Gamma |r|^2`.
