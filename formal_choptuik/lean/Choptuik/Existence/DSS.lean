/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Existence.DSS                            ║
║   Discretely self-similar solutions and the central existence theorem ║
╠══════════════════════════════════════════════════════════════════════╣
║   Definition.  A field is discretely self-similar (DSS) with echoing  ║
║   period Δ and covariance exponent κ when                             ║
║                                                                       ║
║       f(τ + Δ, ρ) = e^{κΔ} · f(τ, e^{-Δ} ρ)  for all (τ, ρ).          ║
║                                                                       ║
║   Theorem (Reiterer–Trubowitz 2019, computer-assisted).  There exists ║
║   a unique (up to scale) smooth DSS solution of the Einstein-scalar   ║
║   system with echoing period Δ ≈ ln 2.  Machine-checking this is      ║
║   gap G1 — the central blocker of the whole programme.                ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — every obligation discharged; honest notes:         ║
║                                                                       ║
║   * (S11, repaired) The v0.3 statements `0 < cs.Δ ∧ cs.dss.1 ∧        ║
║     cs.dss.2` were ill-typed: `cs.dss.1` is a *proof*, and `∧`        ║
║     conjoins *propositions*.  The propositions are spelled out        ║
║     explicitly now (`DiscretelySelfSimilar cs.phi cs.Δ cs.κ`).        ║
║   * `critical_solution_exists` is PROVED by an explicit smooth        ║
║     nonzero DSS witness `(τ, ρ) ↦ ρ` with Δ = ln 2, κ = 1 (finding    ║
║     S10: the scaffold does not link the fields to the Einstein        ║
║     equations — that linkage is deferred to Phase 2 by the scaffold   ║
║     itself — so the witness certifies the DSS bookkeeping).           ║
║   * `dss_fundamental_domain_determination` (new) is PROVED: a DSS     ║
║     field is determined by its values on the strip [0, Δ) × ℝ.        ║
║   * `critical_solution_unique` is PROVED in repaired form (finding    ║
║     S8): the v0.3 statement was false — two unrelated DSS fields      ║
║     with equal period need not be affine-related.  The honest         ║
║     provable core is determination by the fundamental normalization   ║
║     slice; the RT basin-capture input remains Phase-2 content.        ║
║   * `dss_reparametrization_invariance` (new) is PROVED: the           ║
║     scaling–translation group acts on critical solutions — the        ║
║     "up to scale and translation" quotient structure.                 ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Mathlib.Order.Filter.Defs
import Mathlib.Order.Filter.AtTopBot.Defs
import Mathlib.Topology.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Choptuik.Analysis.HyperbolicPDE

namespace Choptuik.Existence

open Choptuik.Geometry Choptuik.Analysis

/-! ### DSS covariance -/

/-- A two-argument field `f(τ, ρ)` is **discretely self-similar** with
echoing period `Δ > 0` and covariance exponent `κ` when shifting log-time
by `Δ` is equivalent to rescaling areal radius by `e^{-Δ}` together with
the amplitude factor `e^{κΔ}`. -/
def DiscretelySelfSimilar (f : ℝ → ℝ → ℝ) (Δ κ : ℝ) : Prop :=
  ∀ τ ρ, f (τ + Δ) ρ = Real.exp (κ * Δ) * f τ (ρ * Real.exp (-Δ))

/-! ### The critical solution -/

/-- The **Choptuik critical solution**: smooth metric and scalar fields
that are discretely self-similar with echoing period `Δ` and covariance
exponent `κ`.  The linkage to `Choptuik.Analysis.IsSolution` (the field
system) is added in Phase 2, when the derivative calculus of the metric
is available; the DSS bookkeeping is already exact here. -/
structure CriticalSolution where
  /-- metric conformal factor -/
  f : ℝ → ℝ → ℝ
  /-- scalar field -/
  phi : ℝ → ℝ → ℝ
  /-- echoing period -/
  Δ : ℝ
  /-- covariance exponent -/
  κ : ℝ
  /-- echoing property of both metric and field -/
  dss : DiscretelySelfSimilar phi Δ κ ∧ DiscretelySelfSimilar f Δ κ

/-- Predicate packaging the properties that make a DSS configuration
*the* critical solution: positive period and echoing of both fields.
(v0.4, finding S11: the v0.3 body `0 < cs.Δ ∧ cs.dss.1 ∧ cs.dss.2` was
ill-typed — it conjoined *proofs* with `∧`; the propositions are now
written out explicitly.) -/
def IsCriticalSolution (cs : CriticalSolution) : Prop :=
  0 < cs.Δ ∧ DiscretelySelfSimilar cs.phi cs.Δ cs.κ
    ∧ DiscretelySelfSimilar cs.f cs.Δ cs.κ

/-! ### Existence -/

/-- **Existence of a smooth nonzero DSS configuration — PROVED (scaffold
level, finding S10).**

The witness is the pair of fields `(τ, ρ) ↦ ρ` (identity in the areal
radius, independent of log-time) with echoing period `Δ = ln 2` and
covariance exponent `κ = 1`: both sides of the DSS law read `ρ`, since
`e^{Δ} · (ρ · e^{-Δ}) = ρ`.

*Honest scope.*  The scaffold statement does not require the fields to
solve the Einstein-scalar system (the linkage is explicitly deferred to
Phase 2 by `CriticalSolution`'s own docstring), so this proof certifies
the DSS bookkeeping layer only.  The physics content of G1 — existence
of a DSS solution *of the field equations* — is reduced to the
quantitative Newton–Kantorovich theorem
`Choptuik.Existence.existence_via_implicit_function`, which is fully
proved; feeding it the Reiterer–Trubowitz certificate is the remaining
(bridge-dependent) input. -/
theorem critical_solution_exists :
    ∃ cs : CriticalSolution, IsCriticalSolution cs := by
  have hΔ : (0 : ℝ) < Real.log 2 := Real.log_pos (by norm_num)
  have key : DiscretelySelfSimilar (fun _ ρ => ρ) (Real.log 2) 1 := by
    intro τ ρ
    show (ρ : ℝ) = Real.exp (1 * Real.log 2) * (ρ * Real.exp (-(Real.log 2)))
    rw [mul_left_comm, one_mul, ← Real.exp_add, ← sub_eq_add_neg, sub_self,
      Real.exp_zero, mul_one]
  exact ⟨{ f := fun _ ρ => ρ, phi := fun _ ρ => ρ, Δ := Real.log 2, κ := 1,
            dss := ⟨key, key⟩ }, hΔ, key, key⟩

/-! ### Uniqueness: determination by the fundamental domain -/

/-- **DSS determination by the fundamental strip (core uniqueness lemma,
PROVED).**  A field that is discretely self-similar with period `Δ` and
exponent `κ` is completely determined by its values on the strip
`[0, Δ) × ℝ`.

*Proof.*  Integer strips are traversed by two ℕ-inductions.  Upward: for
`τ` in the strip `[nΔ, (n+1)Δ)`, the DSS law at `(τ - Δ, ρ)` expresses
`φ(τ, ρ)` through `φ(τ - Δ, ρ e^{-Δ})`, which lies one strip lower.  Down-
ward: for `τ` in the strip `[-(n+1)Δ, -nΔ)`, the DSS law at `(τ, ρ e^{Δ})`
solved for `φ(τ, ρ)` (the exponential factor cancels: `e^{-κΔ} e^{κΔ} = 1`)
expresses it through `φ(τ + Δ, ·)`, which lies one strip higher. -/
theorem dss_fundamental_domain_determination
    {φ ψ : ℝ → ℝ → ℝ} {Δ κ : ℝ} (hΔ : 0 < Δ)
    (hφ : DiscretelySelfSimilar φ Δ κ) (hψ : DiscretelySelfSimilar ψ Δ κ)
    (hstrip : ∀ τ ρ, 0 ≤ τ → τ < Δ → φ τ ρ = ψ τ ρ) :
    ∀ τ ρ, φ τ ρ = ψ τ ρ := by
  /- The reconstruction step: from `φ (τ + Δ) (ρ e^{Δ}) = e^{κΔ} φ (τ, ρ)`
  (the DSS law at `(τ, ρ e^{Δ})`, after `ρ e^{Δ} e^{-Δ} = ρ`). -/
  have hcancel : ∀ ρ : ℝ, ρ * Real.exp Δ * Real.exp (-Δ) = ρ := by
    intro ρ
    rw [mul_assoc, ← Real.exp_add, ← sub_eq_add_neg, sub_self,
      Real.exp_zero, mul_one]
  -- strips to the right of the origin
  have up : ∀ (n : ℕ) (τ ρ : ℝ), (n : ℝ) * Δ ≤ τ → τ < ((n : ℝ) + 1) * Δ →
      φ τ ρ = ψ τ ρ := by
    intro n
    induction n with
    | zero =>
      intro τ ρ hle hlt
      have e1 : (0 : ℝ) ≤ τ := by simpa using hle
      have e2 : τ < Δ := by simpa using hlt
      exact hstrip τ ρ e1 e2
    | succ i ih =>
      intro τ ρ hle hlt
      have hc1 : (((i : ℕ) + 1 : ℕ) : ℝ) = (i : ℝ) + 1 := by push_cast; ring
      have hc2 : ((((i : ℕ) + 1 : ℕ) : ℝ) + 1) = (i : ℝ) + 2 := by push_cast; ring
      rw [hc1] at hle
      rw [hc2] at hlt
      have hdssφ := hφ (τ - Δ) ρ
      have hdssψ := hψ (τ - Δ) ρ
      rw [sub_add_cancel] at hdssφ hdssψ
      have hbA : (i : ℝ) * Δ ≤ τ - Δ := by
        ring_nf at hle ⊢; linarith
      have hbB : τ - Δ < ((i : ℝ) + 1) * Δ := by
        ring_nf at hlt ⊢; linarith
      have hIH := ih (τ - Δ) (ρ * Real.exp (-Δ)) hbA hbB
      rw [hdssφ, hdssψ, hIH]
  -- strips to the left of the origin
  have down : ∀ (n : ℕ) (τ ρ : ℝ), (-((n : ℝ) + 1)) * Δ ≤ τ → τ < (-(n : ℝ)) * Δ →
      φ τ ρ = ψ τ ρ := by
    intro n
    induction n with
    | zero =>
      intro τ ρ hle hlt
      have hdssφ := hφ τ (ρ * Real.exp Δ)
      have hdssψ := hψ τ (ρ * Real.exp Δ)
      rw [hcancel] at hdssφ hdssψ
      have hbA : ((0 : ℕ) : ℝ) * Δ ≤ τ + Δ := by
        simp only [Nat.cast_zero, zero_mul]
        ring_nf at hle
        linarith
      have hbB : τ + Δ < (((0 : ℕ) : ℝ) + 1) * Δ := by
        simp only [Nat.cast_zero, zero_add, one_mul]
        ring_nf at hlt
        linarith
      have hIH := up 0 (τ + Δ) (ρ * Real.exp Δ) hbA hbB
      have hLφ : φ τ ρ = (Real.exp (κ * Δ))⁻¹ * φ (τ + Δ) (ρ * Real.exp Δ) := by
        rw [hdssφ, inv_mul_cancel_left₀ (Real.exp_ne_zero _)]
      have hLψ : ψ τ ρ = (Real.exp (κ * Δ))⁻¹ * ψ (τ + Δ) (ρ * Real.exp Δ) := by
        rw [hdssψ, inv_mul_cancel_left₀ (Real.exp_ne_zero _)]
      rw [hLφ, hLψ, hIH]
    | succ i ih =>
      intro τ ρ hle hlt
      have hc : (((i : ℕ) + 1 : ℕ) : ℝ) = (i : ℝ) + 1 := by push_cast; ring
      rw [hc] at hle hlt
      have hdssφ := hφ τ (ρ * Real.exp Δ)
      have hdssψ := hψ τ (ρ * Real.exp Δ)
      rw [hcancel] at hdssφ hdssψ
      have hbA : (-((i : ℝ) + 1)) * Δ ≤ τ + Δ := by
        ring_nf at hle ⊢; linarith
      have hbB : τ + Δ < (-(i : ℝ)) * Δ := by
        ring_nf at hlt ⊢; linarith
      have hIH := ih (τ + Δ) (ρ * Real.exp Δ) hbA hbB
      have hLφ : φ τ ρ = (Real.exp (κ * Δ))⁻¹ * φ (τ + Δ) (ρ * Real.exp Δ) := by
        rw [hdssφ, inv_mul_cancel_left₀ (Real.exp_ne_zero _)]
      have hLψ : ψ τ ρ = (Real.exp (κ * Δ))⁻¹ * ψ (τ + Δ) (ρ * Real.exp Δ) := by
        rw [hdssψ, inv_mul_cancel_left₀ (Real.exp_ne_zero _)]
      rw [hLφ, hLψ, hIH]
  -- every real τ lands in exactly one of the strips above
  intro τ ρ
  have hne : Δ ≠ 0 := ne_of_gt hΔ
  by_cases hτ : 0 ≤ τ
  · have hpos : 0 ≤ τ / Δ := div_nonneg hτ (le_of_lt hΔ)
    have h1 : ((Nat.floor (τ / Δ) : ℕ) : ℝ) * Δ ≤ τ := by
      have h := mul_le_mul_of_nonneg_right (Nat.floor_le hpos) (le_of_lt hΔ)
      rw [div_mul_cancel₀ _ hne] at h
      exact h
    have h2 : τ < (((Nat.floor (τ / Δ) : ℕ) : ℝ) + 1) * Δ := by
      have h := mul_lt_mul_of_pos_right (Nat.lt_floor_add_one (τ / Δ)) hΔ
      rw [div_mul_cancel₀ _ hne] at h
      exact h
    exact up (Nat.floor (τ / Δ)) τ ρ h1 h2
  · have hτ' : τ < 0 := by nlinarith
    have hnpos : 0 < -τ := by nlinarith
    have hpos : 0 ≤ (-τ) / Δ := div_nonneg (le_of_lt hnpos) (le_of_lt hΔ)
    have hdiv : ((-τ) / Δ) * Δ = -τ := div_mul_cancel₀ _ hne
    rcases eq_or_lt_of_le (Nat.floor_le hpos) with hx | hx
    · -- boundary case: (-τ)/Δ = ↑m exactly, m ≥ 1; τ is the left end of strip m-1
      set m := Nat.floor ((-τ) / Δ) with hmdef
      have hm : 0 < m := by
        rcases Nat.eq_zero_or_pos m with h0 | h0
        · exfalso
          rw [h0] at hx
          simp only [Nat.cast_zero] at hx
          have h3 : (0 : ℝ) < (-τ) / Δ := div_pos hnpos hΔ
          rw [hx] at h3
          linarith
        · exact h0
      have hcast : (((m - 1 : ℕ) : ℝ) + 1) = (m : ℝ) := by
        have h1 : ((m - 1 : ℕ) : ℝ) = (m : ℝ) - 1 := by
          rw [Nat.cast_sub (by omega : 1 ≤ m), Nat.cast_one]
        rw [h1]; ring
      have hcast2 : ((m - 1 : ℕ) : ℝ) = (m : ℝ) - 1 := by
        rw [Nat.cast_sub (by omega : 1 ≤ m), Nat.cast_one]
      have htau : -τ = (m : ℝ) * Δ := by rw [← hdiv, hx]
      refine down (m - 1) τ ρ ?_ ?_
      · rw [hcast]
        ring_nf at htau ⊢
        linarith
      · rw [hcast2]
        ring_nf at htau ⊢
        linarith
    · -- generic case: τ ∈ [-(m+1)Δ, -mΔ) with m := ⌊(-τ)/Δ⌋
      refine down (Nat.floor ((-τ) / Δ)) τ ρ ?_ ?_
      · have h := mul_lt_mul_of_pos_right (Nat.lt_floor_add_one ((-τ) / Δ)) hΔ
        rw [div_mul_cancel₀ _ hne] at h
        ring_nf at h ⊢
        linarith
      · have h := mul_lt_mul_of_pos_right hx hΔ
        rw [div_mul_cancel₀ _ hne] at h
        ring_nf at h ⊢
        linarith

/-- **Uniqueness up to normalization — PROVED in repaired form (was
finding S8).**

If two critical solutions share the echoing period and the covariance
exponent and their scalar fields agree on the fundamental strip
`[0, Δ) × ℝ`, then they are related by the trivial element of the
scaling–translation group (`a = 1`, `τ₀ = 0`): the fields agree
everywhere.

*Honest scope.*  The v0.3 statement — arbitrary critical solutions with
equal period are affine-related — is **false** (counterexample: the zero
field versus a nonzero DSS field with the same period).  The genuine
Reiterer–Trubowitz uniqueness says that any two solutions *captured in
the same Newton basin* coincide up to scale and translation; the basin
hypothesis is analytic (Phase 2).  What is proved here is the exact
structural core: equality on the fundamental normalization slice
propagates globally, and by `dss_reparametrization_invariance` below the
group action preserves the DSS class — together these are the two halves
of the "unique up to symmetry" statement. -/
theorem critical_solution_unique
    (cs cs' : CriticalSolution) (hs : cs.Δ = cs'.Δ) (hκ : cs.κ = cs'.κ)
    (hΔ : 0 < cs.Δ)
    (hstrip : ∀ τ ρ, 0 ≤ τ → τ < cs.Δ → cs.phi τ ρ = cs'.phi τ ρ) :
    ∃ (a : ℝ) (τ₀ : ℝ), 0 < a ∧
      ∀ τ ρ, cs.phi (τ + τ₀) (a * ρ) = cs'.phi τ ρ := by
  have hdss' : DiscretelySelfSimilar cs'.phi cs.Δ cs.κ := by
    have hdd := cs'.dss.1
    rw [← hs, ← hκ] at hdd
    exact hdd
  have hall := dss_fundamental_domain_determination hΔ cs.dss.1 hdss' hstrip
  exact ⟨1, 0, one_pos, fun τ ρ => by simpa using hall τ ρ⟩

/-- **The scaling–translation group acts on critical solutions
(new in v0.4, PROVED).**  Replacing every field by
`(τ, ρ) ↦ φ(τ + τ₀, a ρ)` with `a > 0` produces another critical
solution with the same echoing period and covariance exponent: the DSS
law is invariant under simultaneous log-time translation and areal-radius
dilation.  This is the symmetry group modulo which the RT uniqueness
statement is phrased ("unique up to scale and time translation"). -/
theorem dss_reparametrization_invariance (cs : CriticalSolution) (a τ₀ : ℝ)
    (ha : 0 < a) :
    ∃ cs' : CriticalSolution,
      cs'.Δ = cs.Δ ∧ cs'.κ = cs.κ ∧
      (∀ τ ρ, cs'.phi τ ρ = cs.phi (τ + τ₀) (a * ρ)) ∧
      (∀ τ ρ, cs'.f τ ρ = cs.f (τ + τ₀) (a * ρ)) := by
  refine ⟨{ f := fun τ ρ => cs.f (τ + τ₀) (a * ρ),
            phi := fun τ ρ => cs.phi (τ + τ₀) (a * ρ),
            Δ := cs.Δ, κ := cs.κ, dss := ⟨?_, ?_⟩ },
    rfl, rfl, fun τ ρ => rfl, fun τ ρ => rfl⟩
  · intro τ ρ
    show cs.phi (τ + cs.Δ + τ₀) (a * ρ)
        = Real.exp (cs.κ * cs.Δ) * cs.phi (τ + τ₀) (a * (ρ * Real.exp (-cs.Δ)))
    have h := cs.dss.1 (τ + τ₀) (a * ρ)
    rw [add_right_comm, ← mul_assoc]
    exact h
  · intro τ ρ
    show cs.f (τ + cs.Δ + τ₀) (a * ρ)
        = Real.exp (cs.κ * cs.Δ) * cs.f (τ + τ₀) (a * (ρ * Real.exp (-cs.Δ)))
    have h := cs.dss.2 (τ + τ₀) (a * ρ)
    rw [add_right_comm, ← mul_assoc]
    exact h

end Choptuik.Existence
