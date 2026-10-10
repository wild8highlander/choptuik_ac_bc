# The Asymmetry Lock (C12) — why the gap is permanent and quarks are not free

## 1. The physical question

Because the Universe's matter–antimatter asymmetry is **complete** (antibaryons
are absent on cosmological scales; η_B = 6.1e-10, Planck 2018), the confinement
story has one more consistency requirement: the mass gap must survive every
admissible perturbation from the matter sector. If the gap could close, free
color charges would propagate, scatter in the quantum field, screen the linear
potential and "fill the gaps" — leading to isolated macroscopic quark
accumulations that are not observed.

## 2. T14 — the asymmetric lock (exact)

Model: the gap potential U₀ carries the closure cost B₀ = Δ_F,min = 0.181777
(N2); the matter sector adds η·U₁ with sup-norm ‖U₁‖∞ ≤ 1. The barrier loss is
U₁(0) − U₁(x*) ≤ 2 for any profile — the worst case (the step profile) attains
exactly 2. Hence:

    barrier(η) = B₀ − 2η > 0   ⇔   η < η_crit = Δ_F,min/2 = 0.0908885.

The η-phase map (41 log-spaced points × 9 profiles) is OPEN for every
η < η_crit and CLOSED beyond — the boundary passes exactly through η_crit.
The cosmological value sits at

    margin = η_crit / η_B = 148 997 540.98 ≈ 1.49×10⁸ (log₁₀ = 8.173),

i.e. the baryon asymmetry is nine orders of magnitude too small to threaten
the gap. SymPy verifies the worst-case inequality symbolically (IVP-12).

## 3. T15 — no free quarks (honest-negative + comparison)

Three independent closures:

1. **Production**: the tunneling window is closed — T(0) = 9.21e-13 < 1e-12
   (T9); the anchored static barrier V* = 0.9359375 excludes classical escape
   for all sampled energies (T13, 0/300).
2. **Filling is self-limiting**: free quarks would screen and fill the gap
   wells, but filling raises the local closure cost (negative feedback). The
   toy dynamics shows 0 saturated wells in 10⁶ steps at η_B, while the positive
   control at η = 0.5 > η_crit cascades (100 wells saturated).
3. **Combinatorics**: even granting per-attempt probability T(0) ≈ 9.2e-13, a
   macroscopic object of N ~ 10³⁰ quarks has probability < 10^(−1.2×10³¹);
   even 30 simultaneous tunneled quarks: 10^(−361).

Experimental nugget searches bound the free-quark fraction below ~1e-27 per
nucleon — consistent with the model prediction of zero (comparison status
only, C12-EXP).

**Conclusion**: with complete matter–antimatter asymmetry the gap is permanent
within the model class, and quarks cannot exist as separate asymptotic states.
The observed world — bound hadrons only — is the forced outcome, not a
coincidence.

## 4. What would falsify the lock

- A CLOSED cell at η ≤ η_B in the C12 map.
- A resolved escape channel with T > 1e-12 at admissible energies.
- A nugget detection above the comparison bound.
