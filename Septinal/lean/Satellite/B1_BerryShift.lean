/-
  Septinial braking satellite · B1: the Berry quantum in the canonical
  two-level normal form (model level).  Companion of choptuik_ac_bc (sector C).
  Declared model: the two-level system with quadrature coupling δ/√2 and unit
  level separation; its characteristic polynomial is X² − X − δ²/2, so the
  lower level shifts by λ₋(δ) = (1 − √(1+2δ²))/2 = −δ²/2 + R(δ) with the
  explicit remainder 0 < R(δ) ≤ δ⁴/4.
  Theorems (class I, of the declared normal form): the closed forms, the
  eigenvalue identity, and both remainder bounds.  Zero sorry.
  Twin: scripts/b1_berry_model.py (SymPy exact series: −δ²/2 + δ⁴/4 − δ⁶/4 + …).
-/
import Mathlib

namespace Satellite.Berry

/-- Lower level of the normal form: exact closed form. -/
noncomputable def lambdaLower (δ : ℝ) : ℝ := (1 - √(1 + 2 * δ^2)) / 2

/-- First-order (Berry) term of the shift. -/
noncomputable def firstOrder (δ : ℝ) : ℝ := -δ^2 / 2

/-- The explicit remainder R(δ) = λ₋(δ) − (−δ²/2). -/
noncomputable def remainder (δ : ℝ) : ℝ := lambdaLower δ - firstOrder δ

theorem sqrt_ge_one (δ : ℝ) : 1 ≤ √(1 + 2 * δ^2) := by
  have h : (1:ℝ) ≤ 1 + 2 * δ^2 := by linarith [sq_nonneg (δ:ℝ)]
  calc 1 = √1 := (Real.sqrt_one).symm
  _ ≤ √(1 + 2 * δ^2) := Real.sqrt_le_sqrt h

/-- The workhorse rewriting: √(1+2δ²)·√(1+2δ²) = 1 + 2δ². -/
theorem sq_sqrt_one_plus (δ : ℝ) :
    √(1 + 2 * δ^2) * √(1 + 2 * δ^2) = 1 + 2 * δ^2 := by
  have h : √(1 + 2 * δ^2) ^ 2 = 1 + 2 * δ^2 :=
    Real.sq_sqrt (by linarith [sq_nonneg (δ:ℝ)])
  calc √(1 + 2 * δ^2) * √(1 + 2 * δ^2) = √(1 + 2 * δ^2) ^ 2 := by ring
  _ = 1 + 2 * δ^2 := h

/-- Rationalized form: λ₋(δ) = −δ²/(1 + √(1+2δ²)). -/
theorem lambdaLower_rationalized (δ : ℝ) :
    lambdaLower δ = -δ^2 / (1 + √(1 + 2 * δ^2)) := by
  have hs : 0 ≤ 1 + 2 * δ^2 := by linarith [sq_nonneg (δ:ℝ)]
  have hkey : (1 - √(1 + 2 * δ^2)) * (1 + √(1 + 2 * δ^2)) = -2 * δ^2 := by
    calc (1 - √(1 + 2 * δ^2)) * (1 + √(1 + 2 * δ^2))
        = 1 + √(1 + 2 * δ^2) - (√(1 + 2 * δ^2) + √(1 + 2 * δ^2) * √(1 + 2 * δ^2)) := by ring
      _ = 1 - (1 + 2 * δ^2) := by rw [sq_sqrt_one_plus]; ring
      _ = -2 * δ^2 := by ring
  rw [lambdaLower]
  field_simp [hkey]
  ring

/-- λ₋(δ) is the lower root of the characteristic polynomial X² − X − δ²/2. -/
theorem lambdaLower_is_lower_root (δ : ℝ) :
    lambdaLower δ ^ 2 - lambdaLower δ - δ^2 / 2 = 0 := by
  have hs : 0 ≤ 1 + 2 * δ^2 := by linarith [sq_nonneg (δ:ℝ)]
  have hkey : (1 - √(1 + 2 * δ^2)) ^ 2 = 2 - 2 * √(1 + 2 * δ^2) + 2 * δ^2 := by
    calc (1 - √(1 + 2 * δ^2)) ^ 2 = 1 - 2 * √(1 + 2 * δ^2) + √(1 + 2 * δ^2) * √(1 + 2 * δ^2) := by ring
      _ = 2 - 2 * √(1 + 2 * δ^2) + 2 * δ^2 := by rw [sq_sqrt_one_plus]; ring
  rw [lambdaLower]
  field_simp [hkey]
  ring

/-- Exact remainder: R(δ) = δ⁴/(1 + √(1+2δ²))². -/
theorem remainder_eq (δ : ℝ) : remainder δ = δ^4 / (1 + √(1 + 2 * δ^2)) ^ 2 := by
  have hs : 0 ≤ 1 + 2 * δ^2 := by linarith [sq_nonneg (δ:ℝ)]
  have h := lambdaLower_rationalized δ
  have hkey : (√(1 + 2 * δ^2) - 1) * (1 + √(1 + 2 * δ^2)) = 2 * δ^2 := by
    calc (√(1 + 2 * δ^2) - 1) * (1 + √(1 + 2 * δ^2))
        = √(1 + 2 * δ^2) + √(1 + 2 * δ^2) * √(1 + 2 * δ^2) - (1 + √(1 + 2 * δ^2)) := by ring
      _ = 2 * δ^2 := by rw [sq_sqrt_one_plus]; ring
  rw [remainder, h, firstOrder]
  have hstep : -δ^2 / (1 + √(1 + 2 * δ^2)) - -δ^2 / 2
      = δ^2 * ((√(1 + 2 * δ^2) - 1) * (1 + √(1 + 2 * δ^2)))
        / (2 * (1 + √(1 + 2 * δ^2)) ^ 2) := by
    field_simp; ring
  rw [hstep, hkey]
  field_simp
  ring

/-- Positivity: 0 < R(δ) for δ ≠ 0. -/
theorem remainder_pos (δ : ℝ) (hδ : δ ≠ 0) : 0 < remainder δ := by
  rw [remainder_eq]
  refine div_pos ?_ ?_ <;> positivity

/-- Upper bound: R(δ) ≤ δ⁴/4. -/
theorem remainder_le (δ : ℝ) : remainder δ ≤ δ^4 / 4 := by
  rw [remainder_eq]
  have h2 : (2:ℝ) ≤ 1 + √(1 + 2 * δ^2) := by linarith [sqrt_ge_one δ]
  have h4 : (4:ℝ) ≤ (1 + √(1 + 2 * δ^2)) ^ 2 := by nlinarith [h2, h2]
  have hδ4 : 0 ≤ δ^4 := by positivity
  rw [div_le_div_iff₀ (by positivity : (0:ℝ) < (1 + √(1 + 2 * δ^2)) ^ 2)
    (by norm_num : (0:ℝ) < 4)]
  nlinarith [h4, hδ4]

end Satellite.Berry
