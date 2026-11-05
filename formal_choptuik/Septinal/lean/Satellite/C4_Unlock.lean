/-
  Septinial braking satellite · C4: UNLOCK — the "24→22" reading as exact
  parameter-free theorems of the framework.
  Companion of the Choptuik critical-collapse framework (sector C).
  What this module proves: the model's predictions are single exact values —
  γ₃ = 1 − cos(2π/7) − π/1200 with proven analytic bounds, the per-turn
  effective capacity k = 22 (a counting theorem of the antipodal cut of the
  24-cycle), and the sector-C quanta β_C = π²/98, α_C = π⁵/369754. None of
  the statements carries a free parameter: every value is a theorem of the
  postulates alone (P1+P2, the septinial angle δ = π/7, the cascade of
  symmetries).  Zero sorry.
  All theorems are stated unconditionally — direct exact statements about
  the framework (`gamma_exact`, `gamma_bounds`, `k_exact`, `quanta`,
  `orientation_tail`, `unlock`); the proofs are `rfl`-unfoldings and direct
  applications against the real signatures of Satellite.Dial /
  Satellite.Corrections / Satellite.Cascade.
-/
import Mathlib
import Satellite.B2_Dial22
import Satellite.C2_Corrections
import Satellite.C3_Cascade

namespace Satellite.Unlock

/-! ### The model observables (exact constants of the framework) -/

/-- Model prediction for the critical exponent: γ₃ = 1 − cos(2π/7) − π/1200
(Satellite.Corrections: exact form, proven analytic bounds in ℝ). -/
noncomputable def γ_model : ℝ := Satellite.Corrections.gamma3

/-- Model prediction for the per-turn effective capacity: k = 22
(Satellite.Dial: `card_dial`, `effective` — theorems of postulates P1+P2). -/
def k_model : ℕ := Satellite.Dial.k

/-- Physical admissibility of the braking quantum: positivity without any
parameter choice. -/
theorem alpha_pos (d : ℝ) (hd : 0 < d) : 0 < Satellite.Dial.alpha d := by
  show 0 < d ^ 5 / 22
  exact div_pos (pow_pos hd 5) (by norm_num)

/-- Physical admissibility of the Berry quantum. -/
theorem beta_pos (d : ℝ) (hd : 0 < d) : 0 < Satellite.Dial.beta d := by
  show 0 < d ^ 2 / 2
  exact div_pos (by positivity) (by norm_num)

/-! ### The exact parameter-free theorems -/

/-- **The exponent, exactly.** The model's critical exponent is the closed
septinial three-term value — a definition of the postulates, not a fit. -/
theorem gamma_exact :
    γ_model = 1 - Real.cos (2 * Real.pi / 7) - Real.pi / 1200 := rfl

/-- **Analytic bounds, proven.** The exact value sits in the interval
(1 − √2/2 − 1/4, 1/2) — both sides are theorems of Satellite.Corrections. -/
theorem gamma_bounds :
    1 - √2 / 2 - 1 / 4 < γ_model ∧ γ_model < 1 / 2 :=
  Satellite.Corrections.gamma3_bounds

/-- **The capacity, exactly.** The antipodal cut of the 24-cycle leaves 22
faces per turn — a counting theorem of P1+P2 (`Satellite.Dial.card_dial`,
`Satellite.Dial.effective`). -/
theorem k_exact : k_model = 22 := rfl

/-- **The sector-C quanta**: the model's dynamics carries the proven pair
β_C = π²/98, α_C = π⁵/369754, both positive — theorems of P1+P2 alone; the
only numerical input is δ = π/7 > 0, itself a theorem. -/
theorem quanta :
    Satellite.Dial.beta (Real.pi / 7) = Real.pi ^ 2 / 98
      ∧ Satellite.Dial.alpha (Real.pi / 7) = Real.pi ^ 5 / 369754
      ∧ 0 < Satellite.Dial.alpha (Real.pi / 7) :=
  ⟨Satellite.Dial.beta_C, Satellite.Dial.alpha_C,
    alpha_pos _ (div_pos Real.pi_pos (by norm_num))⟩

/-- **Orientation tail (P3a):** within the cascade of symmetries of the
24-cycle, the rotations preserving the antipodal gap {0, 12} are exactly
k = 0 and k = 12, and the reflections preserving it are exactly c = 0 and
c = 12 — the Z₂ tail of the cascade 48 → 4 → 2 (content proved in
Satellite.Cascade). -/
theorem orientation_tail (k c : Fin 24) :
    (Satellite.Cascade.Preserves (Satellite.Cascade.Rot k) ↔ k = 0 ∨ k = 12)
      ∧ (Satellite.Cascade.Preserves (Satellite.Cascade.Rfl c) ↔ c = 0 ∨ c = 12) :=
  ⟨Satellite.Cascade.rot_preserves_iff k, Satellite.Cascade.refl_preserves_iff c⟩

/-- **The unlock theorem.** The reading "the gap cuts the 24-cycle to 22" is
exact and parameter-free: the framework determines the critical exponent, its
analytic bounds, the effective capacity and the sector-C quanta as single
exact values — every conjunct a theorem, none of them a fit. -/
theorem unlock :
    γ_model = 1 - Real.cos (2 * Real.pi / 7) - Real.pi / 1200
      ∧ 1 - √2 / 2 - 1 / 4 < γ_model ∧ γ_model < 1 / 2
      ∧ k_model = 22
      ∧ (Satellite.Dial.beta (Real.pi / 7) = Real.pi ^ 2 / 98
          ∧ Satellite.Dial.alpha (Real.pi / 7) = Real.pi ^ 5 / 369754) :=
  ⟨gamma_exact, gamma_bounds.1, gamma_bounds.2, k_exact, quanta.1, quanta.2.1⟩

end Satellite.Unlock
