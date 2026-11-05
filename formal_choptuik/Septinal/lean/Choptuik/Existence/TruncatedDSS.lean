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

import Mathlib.Tactic
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Defs
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Algebra.Order.Archimedean.Basic
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
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro y
    have hcoef : (-(50 / 39 : ℝ)) < 0 := by norm_num
    have h50 : (0 : ℝ) ≤ 50 / 39 := by norm_num
    have hval : ‖truncInv y‖ = 50 / 39 * ‖y‖ := by
      simp only [truncInv, LinearMap.smul_apply, LinearMap.id_apply, smul_eq_mul,
        Real.norm_eq_abs, abs_mul, abs_of_neg (by norm_num : (-(50 / 39 : ℝ)) < 0)]
      ring
    rw [hval]
  · intro x x' hx hx'
    simp only [Real.norm_eq_abs, truncDeriv, LinearMap.smul_apply,
      LinearMap.id_apply, smul_eq_mul, truncatedResidual]
    have hbx : |x - 13 / 10| <= 1 / 10 := by simpa [Real.norm_eq_abs] using hx
    have hbx' : |x' - 13 / 10| <= 1 / 10 := by simpa [Real.norm_eq_abs] using hx'
    have hfact : 1 / 2 - 3 / 10 * x ^ 2 - (1 / 2 - 3 / 10 * x' ^ 2)
        - -(39 / 50) * (x - x')
        = (x - x') * ((3 / 10) * (26 / 10 - x - x')) := by
      ring
    rw [hfact, abs_mul]
    have hcoef : |(3 / 10) * (26 / 10 - x - x')| <= 3 / 50 := by
      rw [abs_mul, abs_of_nonneg (by norm_num : (0:ℝ) ≤ (3/10:ℝ))]
      have h1 : |26 / 10 - x - x'| <= 2 / 10 := by
        rw [abs_le]; constructor <;> nlinarith [abs_le.mp hbx, abs_le.mp hbx']
      calc (3/10) * |26/10 - x - x'| <= (3/10) * (2/10) :=
            mul_le_mul_of_nonneg_left h1 (by norm_num)
        _ = 3/50 := by norm_num
    calc |x - x'| * |(3 / 10) * (26 / 10 - x - x')|
        <= |x - x'| * (3 / 50) := mul_le_mul_of_nonneg_left hcoef (abs_nonneg _)
      _ = (3 / 50 : ℝ) * |x - x'| := by ring
  · norm_num [truncatedResidual, Real.norm_eq_abs]
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
    ring
  have hright : ∀ w : ℝ, truncDeriv (truncInv w) = w := by
    intro w
    simp only [truncInv, truncDeriv, LinearMap.smul_apply, LinearMap.id_apply,
      smul_eq_mul]
    ring
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
    · exact sub_eq_zero.mp (abs_eq_zero.mp h.symm)
    · exact absurd hle (by
        have h3 : (42/50:ℝ) * |x - y| < |x - y| := by
          have h4 : (42/50:ℝ) * |x - y| < 1 * |x - y| :=
            mul_lt_mul_of_pos_right hlt h
          rwa [one_mul] at h4
        linarith)
  have hbx : |x - 13 / 10| ≤ 1 / 10 := by simpa [Real.norm_eq_abs] using hball
  have hby : |y - 13 / 10| ≤ 1 / 10 := by
    rw [abs_le]; constructor <;> linarith [hywin.1, hywin.2]
  have hx0 : truncatedResidual x = 0 := hx
  have hy0 : truncatedResidual y = 0 := hy
  have hkey2 : ‖truncDeriv (x - y)‖ ≤ (3/50) * ‖x - y‖ := by
    have hl := hlip x y hbx hby
    rw [hx0, hy0] at hl
    have h2 : (0:ℝ) - 0 - truncDeriv (x - y) = -truncDeriv (x - y) := by ring
    rw [h2] at hl
    have h3 : ‖-truncDeriv (x - y)‖ = ‖truncDeriv (x - y)‖ := by rw [norm_neg]
    rwa [h3] at hl
  have hchain : |x - y| ≤ (42/50) * |x - y| := by
    have h1 : |x - y| = (50/39) * ‖truncDeriv (x - y)‖ := by
      calc |x - y| = |truncInv (truncDeriv (x - y))| :=
            congrArg (fun w : ℝ => |w|) (hleft (x - y)).symm
        _ = |-(50/39:ℝ) * truncDeriv (x - y)| := by
            simp only [truncInv, LinearMap.smul_apply, LinearMap.id_apply,
              smul_eq_mul]
        _ = (50/39) * ‖truncDeriv (x - y)‖ := by
            rw [abs_mul, abs_of_neg (by norm_num : (-(50/39:ℝ)) < 0),
              Real.norm_eq_abs]
            ring
    have h2 : (50/39) * ‖truncDeriv (x - y)‖ ≤ (42/50) * ‖x - y‖ := by
      have h2a : (50/39) * ‖truncDeriv (x - y)‖
          ≤ (50/39) * ((3/50) * ‖x - y‖) :=
        mul_le_mul_of_nonneg_left hkey2 (by norm_num)
      have h2b : (50/39) * ((3/50) * ‖x - y‖) = (3/39) * ‖x - y‖ := by ring
      have h2c : (3/39 : ℝ) ≤ 42/50 := by norm_num
      calc (50/39) * ‖truncDeriv (x - y)‖
          ≤ (50/39) * ((3/50) * ‖x - y‖) := h2a
        _ = (3/39) * ‖x - y‖ := h2b
        _ ≤ (42/50) * ‖x - y‖ :=
              mul_le_mul_of_nonneg_right h2c (norm_nonneg _)
    conv_lhs => rw [h1]
    exact h2
  exact (hzero hchain).symm

end Choptuik.Existence
