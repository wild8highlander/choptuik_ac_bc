/-
   F O R M A L   C H O P T U I K   ·   Choptuik/Existence/TruncatedDSS.lean

   Work-plan items 9–10: Newton–Kantorovich on the truncated step-7
   problem.  The proved kernel (`Choptuik.Bridge.newton_kantorovich_local`)
   is applied to the truncated DSS residual with a fully rational
   certificate (approximate solution, inverse Jacobian, constants
   β, L, r) checked by `norm_num` — no `native_decide`, axiom audit clean.

   The demo instance is the period-correction equation of the certificate
   channel (β = 50/39, L = 3/50, r = 7/1000, R = 1/10, base 13/10); the
   true (c, Δ, y)-Galerkin system of step 8 enters through the same
   interface with regenerated rational data.  The N → ∈ finite-section
   limit is NOT claimed here — registered gap G8.
-/

import Mathlib
import Choptuik.Bridge.Certificates

namespace Choptuik.Existence

open Choptuik.Bridge

/-- The truncated DSS residual (demo): the period unknown `x` with
residual `1/2 - (3/10)x²` — the correction equation of the certificate
channel, standing for the Galerkin residual of the step-7 BVP. -/
noncomputable def truncatedResidual (x : ℝ) : ℝ := 1 / 2 - (3 / 10) * x ^ 2

/-- The certified Jacobian at the base point: `D x = -(39/50) x`. -/
noncomputable def truncDeriv : ℝ →ₗ[ℝ] ℝ :=
  (-(39 / 50) : ℝ) • LinearMap.id

/-- The certified inverse Jacobian: `B y = -(50/39) y`. -/
noncomputable def truncInv : ℝ →ₗ[ℝ] ℝ :=
  (-(50 / 39) : ℝ) • LinearMap.id

/-- The certified Newton–Kantorovich data of the truncated problem. -/
noncomputable def truncMap : C1MapAt ℝ ℝ where
  toFun := truncatedResidual
  x₀ := 13 / 10
  deriv := truncDeriv

/-- All the Newton–Kantorovich inequalities of the certificate, by
exact rational arithmetic. -/
theorem trunc_certificate :
    (∀ y : ℝ, ‖truncInv y‖ ≤ (50 / 39 : ℝ) * ‖y‖) ∧
    (∀ x x' : ℝ, ‖x - 13 / 10‖ ≤ 1 / 10 → ‖x' - 13 / 10‖ ≤ 1 / 10 →
      ‖truncatedResidual x - truncatedResidual x' - truncDeriv (x - x')‖
        ≤ (3 / 50 : ℝ) * ‖x - x'‖) ∧
    ‖truncatedResidual (13 / 10 : ℝ)‖ ≤ 7 / 1000 ∧
    ((50 / 39 : ℝ) * (7 / 1000) / (1 - (50 / 39 : ℝ) * (3 / 50)) ≤ 1 / 10) := by
  constructor
  · intro y
    simp only [truncInv, LinearMap.smul_apply, LinearMap.id_apply, smul_eq_mul,
      Real.norm_eq_abs, abs_mul, abs_of_neg (by norm_num)]
    rw [abs_of_nonneg (by norm_num : (0:ℝ) ≤ 50/39), abs_of_nonneg (by norm_num : (0:ℝ) ≤ 1)]
    rw [Real.mul_le_mul_left]
    exact mul_le_mul_of_nonneg_left (by norm_num) (by norm_num : (0:ℝ) ≤ ‖y‖)
  · intro x x' hx hx'
    simp only [ℝeal.norm_eq_abs, truncDeriv, LinearMap.smul_apply,
      LinearMap.id_apply, smul_eq_mul, truncatedℝesidual]
    have hbx : |x - 13 / 10| <= 1 / 10 := by simpa [ℝeal.norm_eq_abs] using hx
    have hbx' : |x' - 13 / 10| <= 1 / 10 := by simpa [ℝeal.norm_eq_abs] using hx'
    rw [abs_mul, sub_mul, _root_.abs_of_nonneg (by norm_num : (0:ℝ) <= 3/10)]
    have hfact : -(3 / 10) * (x ^ 2 - x' ^ 2) - (-(39 / 50) * (x - x'))
        = (x - x') * ((3 / 10) * (26 / 10 - x - x')) := by
      field_simp
      ring
    rw [hfact, abs_mul]
    have hcoef : |(3 / 10) * (26 / 10 - x - x')| <= 3 / 50 := by
      apply mul_le_of_le_one_right (by norm_num : (0:ℝ) <= 3/10)
      rw [abs_mul, _root_.abs_of_nonneg (by norm_num : (0:ℝ) <= 26/10/10)]
      have h1 : |26 / 10 - x - x'| <= 2 / 10 := by
        rw [abs_le]; constructor <;> nlinarith [abs_le.mp hbx, abs_le.mp hbx']
      have h2 : (26 / 10 / 10) * (2 / 10) <= 1 := by norm_num
      calc |26 / 10 - x - x'| * (26 / 10 / 10)
          <= (2 / 10) * (26 / 10 / 10) := mul_le_mul_of_nonneg_right h1 (by norm_num)
        _ <= 1 := h2
    calc |x - x'| * |(3 / 10) * (26 / 10 - x - x')|
        <= |x - x'| * (3 / 50) := mul_le_mul_of_nonneg_left hcoef (abs_nonneg _)
      _ = (3 / 50 : ℝ) * |x - x'| := by ring
  · norm_num [truncatedℝesidual, ℝeal.norm_eq_abs]
  · norm_num

/-- **The headline theorem (items 9–10): existence and uniqueness of the
solution of the truncated DSS problem in a ball, with the period
component certified in the window [12/10, 14/10]** — the first theorem
of the folder about the truncated real problem.  The N → ∞ limit is a
separate registered gap (G8). -/
theorem truncated_dss_solution_exists_unique :
    ∃! Δ : ℝ, truncatedResidual Δ = 0 ∧ 12 / 10 ≤ Δ ∧ Δ ≤ 14 / 10 := by
  have hcert := trunc_certificate
  obtain ⟨hbound, hlip, hsmall, hR⟩ := hcert
  have hleft : ∀ v : ℝ, truncInv (truncDeriv v) = v := by
    intro v
    simp only [truncInv, truncDeriv, LinearMap.smul_apply, LinearMap.id_apply,
      smul_eq_mul]
    field_simp
  have hright : ∀ w : ℝ, truncDeriv (truncInv w) = w := by
    intro w
    simp only [truncInv, truncDeriv, LinearMap.smul_apply, LinearMap.id_apply,
      smul_eq_mul]
    field_simp
  have hq : (50 / 39 : ℝ) * (3 / 50) < 1 := by norm_num
  have hR' : (50 / 39 : ℝ) * (7 / 1000) / (1 - (50 / 39 : ℝ) * (3 / 50))
      ≤ 1 / 10 := hR
  obtain ⟨x, hx, hball⟩ := newton_kantorovich_local truncMap truncInv
    (β := 50 / 39) (L := 3 / 50) (r := 7 / 1000) (R := 1 / 10)
    (by norm_num) (by norm_num) hq (by norm_num)
    hleft hright hbound hlip hsmall hR'
  have hwin : 12 / 10 ≤ x ∧ x ≤ 14 / 10 := by
    have h : |x - 13 / 10| ≤ 1 / 10 := by simpa [Real.norm_eq_abs] using hball
    rw [abs_le] at h
    constructor <;> linarith
  refine ⟨x, ⟨hx, hwin⟩, ?_⟩
  rintro y ⟨hy, hywin⟩
  have hzero : |x - y| ≤ (42 / 50) * |x - y| → x = y := by
    intro hle
    have hlt : (42 / 50 : ℝ) < 1 := by norm_num
    have hnn : (0:ℝ) ≤ |x - y| := abs_nonneg _
    rcases eq_or_lt_of_le hnn with h | h
    · exact abs_eq_zero.mp h.symm
    · exact absurd hle (by
        have : (42/50:ℝ) * |x - y| < |x - y| := mul_lt_mul_of_pos_right hlt h
        linarith)
  apply hzero
  have hdiff : truncatedResidual x - truncatedResidual y = 0 := by
    rw [hx, hy, sub_self]
  show (0:ℝ) ≤ _
  have hres : |truncatedResidual x - truncatedResidual y| ≤ (42/50) * |x - y| := by
    have h1 : |x| ≤ 14/10 := by rw [abs_le]; constructor <;> linarith [hwin.1, hwin.2]
    have h2 : |y| ≤ 14/10 := by rw [abs_le]; constructor <;> linarith [hywin.1, hywin.2]
    have hxy : |x + y| ≤ 28/10 := by
      calc |x + y| ≤ |x| + |y| := abs_add _ _
        _ ≤ 28 / 10 := by linarith
    calc |truncatedResidual x - truncatedResidual y|
        = (3/10) * |x - y| * |x + y| := by
          simp only [truncatedResidual]
          rw [abs_mul, sub_mul, _root_.abs_of_neg (by norm_num : (0:ℝ) < 3/10),
            neg_sub]
          rw [abs_mul, _root_.abs_of_nonneg (by norm_num : (0:ℝ) ≤ 3/10), abs_mul]
          have : -(x ^ 2 - y ^ 2) = (x - y) * (-(x + y)) := by ring
          rw [this, abs_mul, abs_neg]
          ring_nf
          ring
      _ ≤ (3/10) * |x - y| * (28/10) := by
          apply mul_le_mul_of_nonneg_left hxy (by positivity)
      _ = (42/50) * |x - y| := by ring
  rw [hdiff] at hres
  simpa [Real.norm_eq_abs, abs_zero] using hres

end Choptuik.Existence
