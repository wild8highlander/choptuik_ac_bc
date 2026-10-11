# Theory — the Collapse-Hawking Bridge

This document states, in one place, the physical content of the project:
what is measured, what is mapped, what is compared, and what is honestly
not (yet) measurable.  It is the reference for everything the code does;
the code, in turn, refuses to assert anything that is not here or in
`docs/methods.md`.

---

## 1. The two pillars

**Critical collapse.** A massless scalar field in spherical symmetry,
evolved on a double-null grid, exhibits critical behaviour at the
threshold of black-hole formation (Choptuik 1993).  For a one-parameter
family of initial pulses with amplitude `A`, there exists a critical
amplitude `A*` such that:

- `A < A*`  — the pulse disperses (subcritical, no horizon);
- `A > A*`  — a black hole forms with mass `M_BH ~ (A - A*)^gamma`;
- the approach to `A*` shows discrete self-similarity (DSS): the
  inner evolution echoes with period `Delta` in log-time.

Both `gamma` and `Delta` are dimensionless numbers — universal for the
matter model, independent of the initial family.

**Black-hole thermodynamics.** A Schwarzschild hole of mass `M` carries
closed-form thermodynamics (Hawking 1975, Bekenstein 1973):

| quantity | formula | scaling |
|---|---|---|
| Hawking temperature | `T_H = hbar c^3 / (8 pi G M k_B)` | `~ 1/M` |
| Bekenstein-Hawking entropy | `S_BH = k_B c^3 A / (4 G hbar)` | `~ M^2` |
| Hawking luminosity (photons) | `P_H = hbar c^6 / (15360 pi G^2 M^2)` | `~ 1/M^2` |
| evaporation time | `t_evap = 5120 pi G^2 M^3 / (hbar c^4)` | `~ M^3` |
| surface gravity | `kappa = c^4 / (4 G M)` | `~ 1/M` |
| mean density at horizon | `rho = 3M / (4 pi r_s^3)` | `~ 1/M^2` |

The unitary entropy-flux model adds the Page time
(`t_Page = (1 - 2^{-3/2}) t_evap = 0.6464466 t_evap`): before it, the
radiation entropy equals the coarse-grained horizon entropy (young hole,
entanglement-dominated); after it, the radiation entropy is `S0 - S_BH`
(old hole, isometry wins) and the curve turns over — the Page curve.

## 2. The bridge object

The engine measures, in geometric code units (`4 pi G = 1`), the born
spectrum `M_code(eps)`, `eps = A - A*`.  Divide by the saturated
(strongly supercritical) mass `M_code_sat` — physically the total mass
of the pulse — and everything dimensionful drops out:

```
f~(eps) = M_code(eps) / M_code_sat ,      0 < f~ <= 1
```

`f~` is the dimensionless profile of *how a black hole is born*.  The
bridge maps it onto physical masses with a single input scale:

```
M_BH(eps; M_in) = M_in * f~(eps)
```

The claim of the project is that this mapping is the whole story: the
dimensionless birth profile is universal, and the scale is the only
thing the initial data contribute.  Committed members of the born
ensemble (campaign C1, N=800): `near_floor` (f~ = 0.2877), `mid`
(f~ = 0.2684), `saturated` (f~ = 1.0).

## 3. The contact point with cosmology

Setting `T_H(M) = T_CMB = 2.72548 K` gives the unique mass whose Hawking
temperature matches today's microwave background:

```
M_CMB = hbar c^3 / (8 pi G k_B T_CMB) = 4.5016e22 kg  ~  0.61 lunar masses
```

Such a hole is *exactly* in equilibrium with the CMB today: colder holes
(M > M_CMB) absorb more than they emit and grow; hotter ones (M < M_CMB)
evaporate.  This is the thermodynamic anchor of the whole master table —
the `CMB input` scale.

## 4. The septinial family (project hypothesis, honestly labeled)

The engine family carries an exact substructure inherited from the
Klein quartic — the genus-3 surface

```
x^3 y + y^3 z + z^3 x = 0 ,
```

whose automorphism group PSL(2,7) has order `168 = 84(g-1)` — the
Hurwitz bound, attained (Hurwitz 1893).  The spinor phases of the
framework are

```
delta_A = pi/2 ,   delta_B = pi/3 ,   delta_C = pi/7   (the septinial sector)
```

and the septinial constant is **exact**:

```
b_Ch = 1 - cos(2 pi / 7) = 2 sin^2(pi/7) = 0.37651019814126640...
```

The *comparison* (never a fit, never a derivation):

```
|gamma_Ch - b_Ch| / b_Ch = 0.67 % ,    gamma_Ch = 0.374 (literature anchor)
```

**Status.** This is a framework coincidence of unexplained depth, not a
result.  The project commits it as data, tests nothing on top of it in
v1.0.0, and derives no physics from it.  Any future claim must come
with a mechanism, not a percentage.

Related exact quantities of the same family, committed for
completeness: the Berry quantum of the septinial sector
`bC_quantum = pi^2/98`, the braking quantum `aC_quantum = pi^5/369754`,
the clock theorems `tau*(0) = 27/4`, `tau*(1 brick) = 1323/(196-pi^2) =
7.107920...`, and the additive Berry screening `kappa_berry = 2 -
pi^2/98`.

## 5. The Delta*gamma invariant (project hypothesis)

Both dimensionless observables of the critical side enter one product:

```
Delta * gamma  =?  1.27      (project target)
```

Anchor arithmetic: `3.44 (Gundlach-Hodgson; engine data) x 0.374
(literature) = 1.28656` — 1.3% from the target, inside the frozen
tolerance `0.05`.  v2.2.0 verdict semantics (external audit, point 10):
both factors of P_anchor are anchors, so this comparison is
**ANCHOR_ARITHMETIC** — a consistency statement about the project's own
constants, NOT a measurement and NOT evidence for the hypothesis; the
tolerance itself was chosen post hoc in v1.x and is frozen since v2.2.0
by `PREREGISTRATION.md`.  Campaign C3 (see `docs/validation.md`,
`results/`) tests this at three levels:

| product | inputs | verdict (v2.2.0 semantics) |
|---|---|---|
| `P_anchor` | literature/engine anchors | **ANCHOR_ARITHMETIC** (1.28656, within the frozen tolerance; not a measurement) |
| `P_mixed` | measured `Delta_eff` x anchor `gamma_Ch` | **INCONCLUSIVE** (peaks < 3) |
| `P_engine` | measured `Delta_eff` x measured `gamma_eff` | **INCONCLUSIVE** (grid floor) |
| `P_engine_deep` (C3b, N=3200) | both re-measured at deep grids | **INCONCLUSIVE** (negatives re-confirmed) |

The honest engine-level negative is a *result*: at fixed grid the mass
floor dominates the smallest resolved masses, the scaling fit comes out
flat (`gamma_eff = 0.005 +- 0.035, r^2 = 0.003`), and the echo detector
resolves fewer than three peaks per run.  Campaign C3b then spent deep
grids (N = 1600/3200) on the critical window: the floor sank as
`floor_M ~ 12/N`, the gamma fit TIGHTENED (r² 0.816 -> 0.957) but
stabilised near 0.12 — the asymptotic regime behind the floor stayed
out of reach, and no run resolved >= 3 echo peaks at any depth.  The
honest summary is therefore: the anchor arithmetic is consistent with
the frozen target, and **the hypothesis is UNTESTED at engine level
after two concentrated attacks** (INCONCLUSIVE, not refuted) — beating
the floor law is the explicit engine-upgrade target, judged against
the criteria frozen in `PREREGISTRATION.md`.

### 5.1. What the two branches add (C2, v1.1.0)

The threshold is not just a point where the mass vanishes — C2 measured
both sides of it with the same instrument:

- **Subcritical side:** the peak compactness `q_max` climbs
  monotonically toward the horizon value 1 (0.0158 -> 0.5845 across
  the committed window) without ever forming an apparent horizon; the
  pulse lingers logarithmically longer as eps -> 0
  (`v_qmax = 0.510 - 0.0334 ln(eps)`, r² = 0.714) — the DSS
  accumulation approach, visible from the dispersing side; and the
  compactness oscillation count grows at `0.1909` peaks per e-fold of
  scale, the same order as the anchor rate `1/Delta = 0.2907`.  These
  are the *approach laws* of criticality: they corroborate the DSS
  picture without any fit to its constants.
- **Supercritical side:** the born bifurcation `f~(eps) = M/M_sat` is
  mapped as a shape (not an exponent), summarised by the half-width
  `eps_half = 4.86e-3` — the distance from threshold at which a born
  black hole carries half the saturation mass of the family.

## 6. What the bridge does NOT claim

- No derivation of `gamma`, `Delta`, or `a0` from group theory is
  claimed anywhere in v1.1.0; the septinial constants are committed as
  exact framework data and *compared*, never fitted.
- No claim is made that `f~(eps)` is known beyond the resolved window;
  below the floor the spectrum is honestly unknown, and C3b quantified
  exactly how the floor recedes (`floor_M ~ 12/N`) without reaching
  the asymptotic scaling regime.
- The Page curves are a *model* (unitary entropy flux), not a
  derivation from quantum gravity; what is checked exactly is the Haar
  averaging formula, not the flux ansatz.

## 7. Sources for the standard results

The closed-form thermodynamics and the critical-collision phenomenology
used here are standard; primary anchors: Bekenstein (1973); Hawking
(1975); Page (1976, 1993); Sen (1996); Choptuik (1993); Gundlach (1999);
Gundlach & Hodgson (2002); Roberts (1989) for the exact test solution.
Full list in the root README.
