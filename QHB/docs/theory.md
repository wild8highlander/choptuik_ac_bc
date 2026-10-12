# Theory — the QHB model class

## 1. Scope and honesty rules

The package studies a **dimensionally reduced model class** ("the bridge
sector") inspired by two parents: a Yang–Mills-like confining sector with a
mass gap coordinate Δ, and a thermal sector anchored by classical vortex
dynamics. The package never claims lattice-QCD results; every number belongs
to the model class and is pinned by the normalization conditions below.
Statements are separated into five statuses (see RESULTS): exact, measured-law,
honest-negative, hypothesis, comparison.

## 2. Normalization conditions N1–N8

- **N1** vortex units Γ = a = 1 ⇒ ω = 3/(2π) = 0.477464829275686…
- **N2** gap units: C9 valley floor pinned at β*= 3.3583, Δ_F,min = 0.181777;
  the valley profile is quadratic, Δ_F(β) = Δ_F,min + 0.35(β − β*)².
- **N3** naive-window falsifier β_c = 2.9910 with the measured gap ratio 6.3;
  this fixes the detector threshold Δ_thresh = Δ_F(β_c)/6.3 = 0.0363485.
- **N4** detector cutoff E_max = 2.5 (beyond it the tail is unresolved, T5).
- **N5** confinement box L_box = 12 (the Aref escape radius of C11).
- **N6** cosmological comparison η_B = 6.1e-10 (Planck 2018).
- **N7** anchored static barrier V* = 0.9359375 (T13).
- **N8** seeds: 20250918 / 777001 / 515003 / 902107 (pins in `qhb/pins.py`).

## 3. Gap sector (C1, C9, C12)

The finite-volume gap is Δ_F(β, L) = Δ_F(β)·(1 − 0.35/L + 0.03/L²). The 9×41
phase map shows all 369 cells OPEN: within the explored window the gap never
approaches the detector threshold; the statement is finite-range by
construction. The continuum gap is a flagged hypothesis (HYPO-CONT), never a
claim.

The C12 asymmetry lock models the matter sector as a perturbation η·U₁ with
unit sup-norm added to the gap potential. The closure cost is B₀ = Δ_F,min
(N2). For any profile the barrier loss is at most 2η (worst case attained by
the step profile), hence the gap survives every η < η_crit = Δ_F,min/2 =
0.0908885 — a margin of 1.49×10⁸ over η_B. Physically: the baryon asymmetry is
nine orders of magnitude too small to close the gap.

## 4. String and thermal sector (C2, C3, C7)

The Wilson law W = exp(−σRT) is exact in the class; σ(β) = 0.25·(Δ/Δ_min)^1.5.
The bridge temperature carries the parent project's quantum spin corrections:
T_c = √σ/(2π)·(1 + (π²/8)β⁻² + (π⁵/704)β⁻⁴); the coefficients are verified at
100 digits. The WKB window of the linear barrier uses the reduced coordinate
with effective mass m_eff = 1/2: S(E) = (2/(3σ))(σL − E)^{3/2}; the window is
closed (T(0) = 9.21e-13 < 1e-12).

## 5. Vortex anchor (C11)

Kirchhoff point-vortex equations with equal circulations are implemented from
scratch. The equilateral triangle is a relative equilibrium rotating at
ω = 3/(2π). The corotating-frame Jacobian spectrum is {0, 0, ±iω, ±iω} with the
symbolic characteristic polynomial λ²(4π²λ²+9)²/(16π⁴) — neutral stability
(T11). For H < 0 the motion is bounded with the exact radius 2√I (T12); the
pinned run measures r_max = 2.7654 with the invariant drift < 1e-14. The
anchored slow coordinate s carries V(s) = V*·s²·e^{2−2s} whose unique maximum
V* = 0.9359375 sits exactly at s = 1 (T13); all 300 sampled trajectories have
E < V* and none escapes.

## 6. Free quarks (T15)

Combining T14 (gap persistence), T13 (anchored barrier) and T9 (closed
tunneling window): a free color charge has no admissible production channel in
the model class. The observational route is also closed: if free quarks
existed, they would scatter, screen and fill the gap wells, producing
macroscopic accumulations; the toy fill dynamics is self-limiting (negative
feedback: filling raises the local closure cost), 0 saturated wells in 10⁶
steps at η_B, while the positive control at η = 0.5 > η_crit cascades. The
combinatorial bound for a 10³⁰-quark object is < 10^(−1.2×10³¹). Experimental
nugget searches (n < ~1e-27 per nucleon) are consistent — comparison status
only.

## 7. What would change our mind

- One CLOSED cell in the C9/C12 maps at admissible η.
- A resolved tail shape beyond E_max (C4).
- An escape with E < V* (C11) or Re λ ≠ 0 in the vortex spectrum.
- A nugget detection above the comparison bound.
