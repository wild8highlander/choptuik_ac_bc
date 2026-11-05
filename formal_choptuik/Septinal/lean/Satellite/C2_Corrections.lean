/-
  Septinial braking satellite · C2: the three corrections of the septinial
  family, following the ★ section of choptuik_ac_bc README_ru.md.
  The three corrections are ONE structural pair β(d) = d²/2, α(d) = d⁵/22
  applied to the three septinial phases δ_A = π/2, δ_B = π/3, δ_C = π/7
  (theorems in Satellite.Dial), plus the structural divisor k = 22 = b₂(K3),
  the Choptuik constant b_Ch = 1 − cos(2π/7) and the three-term record.
  Here: the sector-C analytic constants, exact rational/integer skeletons and
  honest bracketing theorems in ℝ.  Zero sorry.  Twins: scripts/*.py.
-/
import Mathlib

open Real

namespace Satellite.Corrections

/-! ### Structural constants (declared inputs, class II) -/

/-- The structural divisor k = 22 = b₂(K3), fixed before any fitting. -/
def k : ℕ := 22

theorem k_betti : k = 22 := rfl

/-! ### Integer skeletons of the quanta (class I, by computation) -/

theorem denom_A : (2 : ℕ)^5 * k = 704 := by norm_num [k]

theorem denom_B : (3 : ℕ)^5 * k = 5346 := by norm_num [k]

theorem denom_C : (7 : ℕ)^5 * k = 369754 := by norm_num [k]

/-- The vibration term's carrier: π/1200, 1200 = 2⁴ · 75. -/
theorem vib_carrier : (16 : ℕ) * 75 = 1200 := by norm_num

theorem carrier_98 : (2 : ℕ) * 49 = 98 := by norm_num

/-! ### The Choptuik constant b_Ch = 1 − cos(2π/7) (sector C) -/

/-- The Choptuik constant in its exact septinial form (repo anchor). -/
noncomputable def b_Ch : ℝ := 1 - Real.cos (2 * π / 7)

/-- cos is strictly decreasing on [0, π]; 2π/7 < π/3 gives the upper
bracket cos(2π/7) > cos(π/3) = 1/2. -/
theorem cos_septinial_gt_half : 1 / 2 < Real.cos (2 * π / 7) := by
  have hpi : (0 : ℝ) < π := Real.pi_pos
  have h1 : 2 * π / 7 < π / 3 := by linarith
  have h2 : 2 * π / 7 < π := by linarith
  have h3 : (0 : ℝ) ≤ 2 * π / 7 := by positivity
  have h4 : (π / 3 : ℝ) ≤ π := by linarith
  have h5 := Real.cos_lt_cos_of_nonneg_of_le_pi h3 h4 h1
  rwa [Real.cos_pi_div_three] at h5

/-- Bracketing theorem: 1 − √2/2 < b_Ch < 1/2 (cos(π/4) = √2/2,
cos(π/2) = 0 sandwich cos(2π/7) from both sides). -/
theorem b_Ch_bounds : 1 - √2 / 2 < b_Ch ∧ b_Ch < 1 / 2 := by
  have hpi : (0 : ℝ) < π := Real.pi_pos
  have h1 : π / 4 < 2 * π / 7 := by linarith
  have h2 : 2 * π / 7 < π / 2 := by linarith
  have h3 : (0 : ℝ) ≤ π / 4 := by positivity
  have h4 : (2 * π / 7 : ℝ) ≤ π := by linarith
  have h5 := Real.cos_lt_cos_of_nonneg_of_le_pi h3 h4 h1
  rw [Real.cos_pi_div_four] at h5
  have h6 := cos_septinial_gt_half
  constructor
  · rw [b_Ch]; linarith
  · rw [b_Ch]; linarith

/-! ### The three-term record γ₃ = b_Ch − π/1200 (class II rule, recorded) -/

/-- The three-term record: 1 − cos(2π/7) − π/1200 (vibration term π/1200). -/
noncomputable def gamma3 : ℝ := b_Ch - π / 1200

theorem gamma3_bounds : 1 - √2 / 2 - 1 / 4 < gamma3 ∧ gamma3 < 1 / 2 := by
  have hpi : (0 : ℝ) < π := Real.pi_pos
  have hp1 : π ≤ 4 := Real.pi_le_four
  have hp2 : π / 1200 < 1 / 4 := by linarith
  have hb := b_Ch_bounds
  constructor
  · rw [gamma3]; linarith
  · rw [gamma3]; linarith

/-! ### Sector-C companions (recorded claims of the repo, class II) -/

/-- QNM factor 1 − 1/(1200π²) (recorded; numerics via Python twin). -/
noncomputable def qnm : ℝ := 1 - 1 / (1200 * π ^ 2)

/-- Strong CP reading of the sector: θ̄_eff = 0 (recorded claim). -/
def theta_eff : ℝ := 0

end Satellite.Corrections
