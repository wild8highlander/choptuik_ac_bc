/-
Copyright (c) 2025. All rights reserved.
-/
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Calculus.Deriv.Inv
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import SeptinalYM.Slater

/-!
# Числовой лист: `cSept ≤ 28.1067`

Замыкание JW-цепочки: точная константа
`cSept = 2·Σ_k |cos(2πk/22)| = 28.1066967…` не превосходит округлённой 28.1067.

Инструменты:
* цепочка MVT-мажорант Тейлора (`monotoneOn_of_deriv_nonneg`): чередующиеся
  частичные суммы рядов синуса и косинуса мажорируются друг другом; финальный
  лист `cos_le_taylor8` (через `x¹⁶/16!`) имеет ошибку хвоста `x¹⁸/18! < 10⁻¹²`;
* `pi_gt_d20` (mathlib): `π > 3.14159265358979323846`;
* попарная симметрия слагаемых (`cos_add_pi`, `cos_pi_sub`) сводит сумму по
  22 модам к `2·(1 + 2·Σ_{j=1}^{5} cos(πj/11))`;
* пять десятичных мажорант при точках `r_j` = округлённое вниз `j·π₋/11`,
  запас ~10⁻⁹ на слагаемое; суммарный запас ≈ 3.2·10⁻⁶.

Сертификация: `scripts/verify_csept.py`, `scripts/pick_cj.py`.
-/

namespace Septinal

open Real Set
open scoped Real

/-! ## MVT-шаблон -/

/-- Шаг MVT: функция с нулём в 0 и неотрицательной производной на `[0,2]`
неотрицательна на всём отрезке. -/
private theorem mvt_step (f : ℝ → ℝ) (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2)
    (hdiff : Differentiable ℝ f) (hge : ∀ t, 0 ≤ t → t ≤ 2 → 0 ≤ deriv f t)
    (h0 : f 0 = 0) : 0 ≤ f x := by
  have hmono : MonotoneOn f (Icc (0 : ℝ) 2) :=
    monotoneOn_of_deriv_nonneg (convex_Icc 0 2) hdiff.continuous.continuousOn
      hdiff.differentiableOn (fun t ht => by
        simp only [interior_Icc, Set.mem_Ioo] at ht
        exact hge t ht.1.le ht.2.le)
  have hxmem : x ∈ Icc (0 : ℝ) 2 := ⟨hx, hx2⟩
  have h0mem : (0 : ℝ) ∈ Icc (0 : ℝ) 2 := ⟨le_refl 0, by norm_num⟩
  calc 0 = f 0 := h0.symm
    _ ≤ f x := hmono h0mem hxmem hx

/-- Дифференцируемость `t ^ n / k` при `k ≠ 0`. -/
private theorem diff_div_const (n : ℕ) (k : ℝ) (hk : k ≠ 0) :
    Differentiable ℝ (fun t => t ^ n / k) := by
  have h3 : Differentiable ℝ (fun t => t ^ n * k⁻¹) :=
    Differentiable.mul (differentiable_id.pow n) (differentiable_const k⁻¹)
  have h4 : (fun t : ℝ => t ^ n / k) = (fun t : ℝ => t ^ n * k⁻¹) := by
    funext t
    field_simp
  rw [h4]
  exact h3

/-! ## Цепочка тейлоровских мажорант на `[0, 2]` -/

/-- Синус ≥ кубическая частичная сумма. -/
theorem sin_ge_cubic (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    x - x ^ 3 / 6 ≤ Real.sin x := by
  have h0 : Real.sin (0:ℝ) - (0:ℝ) + (0:ℝ) ^ 3 / 6 = 0 := by
    rw [Real.sin_zero]; norm_num
  have h := mvt_step (fun t => Real.sin t - t + t ^ 3 / 6) x hx hx2
    ((Real.differentiable_sin.sub differentiable_id).add
      (diff_div_const 3 6 (by norm_num)))
    (by
      intro t _ _
      simp [Real.deriv_sin, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [one_sub_sq_div_two_le_cos t])
    h0
  have h' : (0 : ℝ) ≤ Real.sin x - x + x ^ 3 / 6 := h
  linarith

/-- Косинус ≤ четвёртая частичная сумма. -/
theorem cos_le_quartic (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    Real.cos x ≤ 1 - x ^ 2 / 2 + x ^ 4 / 24 := by
  have h0 : (1:ℝ) - (0:ℝ) ^ 2 / 2 + (0:ℝ) ^ 4 / 24 - Real.cos (0:ℝ) = 0 := by
    rw [Real.cos_zero]; norm_num
  have h := mvt_step (fun t => 1 - t ^ 2 / 2 + t ^ 4 / 24 - Real.cos t) x hx hx2
    (((differentiable_const (1 : ℝ)).sub
      (diff_div_const 2 2 (by norm_num))).add
      (diff_div_const 4 24 (by norm_num))).sub
      Real.differentiable_cos
    (by
      intro t _ _
      simp [Real.deriv_cos, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [sin_ge_cubic t (by linarith) (by linarith)])
    h0
  have h' : (0 : ℝ) ≤ 1 - x ^ 2 / 2 + x ^ 4 / 24 - Real.cos x := h
  linarith

/-- Синус ≤ пятая частичная сумма. -/
theorem sin_le_quintic (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    Real.sin x ≤ x - x ^ 3 / 6 + x ^ 5 / 120 := by
  have h0 : (0:ℝ) - (0:ℝ) ^ 3 / 6 + (0:ℝ) ^ 5 / 120 - Real.sin (0:ℝ) = 0 := by
    rw [Real.sin_zero]; norm_num
  have h := mvt_step (fun t => t - t ^ 3 / 6 + t ^ 5 / 120 - Real.sin t) x hx hx2
    ((((differentiable_id).sub
      (diff_div_const 3 6 (by norm_num))).add
      (diff_div_const 5 120 (by norm_num))).sub
      Real.differentiable_sin)
    (by
      intro t _ _
      simp [Real.deriv_sin, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [cos_le_quartic t (by linarith) (by linarith)])
    h0
  have h' : (0 : ℝ) ≤ x - x ^ 3 / 6 + x ^ 5 / 120 - Real.sin x := h
  linarith

/-- Косинус ≥ шестая частичная сумма. -/
theorem cos_ge_sixtic (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    1 - x ^ 2 / 2 + x ^ 4 / 24 - x ^ 6 / 720 ≤ Real.cos x := by
  have h0 : Real.cos (0:ℝ) - (1:ℝ) + (0:ℝ) ^ 2 / 2 - (0:ℝ) ^ 4 / 24 + (0:ℝ) ^ 6 / 720 = 0 := by
    rw [Real.cos_zero]; norm_num
  have h := mvt_step (fun t => Real.cos t - 1 + t ^ 2 / 2 - t ^ 4 / 24 + t ^ 6 / 720) x hx hx2
    ((((Real.differentiable_cos.sub (differentiable_const (1 : ℝ))).add
      (diff_div_const 2 2 (by norm_num))).sub
      (diff_div_const 4 24 (by norm_num))).add
      (diff_div_const 6 720 (by norm_num)))
    (by
      intro t _ _
      simp [Real.deriv_sin, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [sin_le_quintic t (by linarith) (by linarith)])
    h0
  have h' : (0 : ℝ) ≤ Real.cos x - 1 + x ^ 2 / 2 - x ^ 4 / 24 + x ^ 6 / 720 := h
  linarith

/-- Синус ≥ седьмая частичная сумма. -/
theorem sin_ge_septic (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    x - x ^ 3 / 6 + x ^ 5 / 120 - x ^ 7 / 5040 ≤ Real.sin x := by
  have h0 : Real.sin (0:ℝ) - (0:ℝ) + (0:ℝ) ^ 3 / 6 - (0:ℝ) ^ 5 / 120 + (0:ℝ) ^ 7 / 5040 = 0 := by
    rw [Real.sin_zero]; norm_num
  have h := mvt_step (fun t => Real.sin t - t + t ^ 3 / 6 - t ^ 5 / 120 + t ^ 7 / 5040) x hx hx2
    ((((Real.differentiable_sin.sub differentiable_id).add
      (diff_div_const 3 6 (by norm_num))).sub
      (diff_div_const 5 120 (by norm_num))).add
      (diff_div_const 7 5040 (by norm_num)))
    (by
      intro t _ _
      simp [Real.deriv_cos, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [cos_ge_sixtic t (by linarith) (by linarith)])
    h0
  have h' : (0 : ℝ) ≤ Real.sin x - x + x ^ 3 / 6 - x ^ 5 / 120 + x ^ 7 / 5040 := h
  linarith

/-- **Финальный тейлоровский лист**: косинус ≤ девятая частичная сумма
(через `x¹⁶/16!`), ошибка хвоста `x¹⁸/18! < 10⁻¹²` при `x ≤ 2`. -/
theorem cos_le_taylor8 (x : ℝ) (hx : 0 ≤ x) (hx2 : x ≤ 2) :
    Real.cos x ≤ 1 - x ^ 2 / 2 + x ^ 4 / 24 - x ^ 6 / 720 + x ^ 8 / 40320
      - x ^ 10 / 3628800 + x ^ 12 / 479001600 - x ^ 14 / 87178291200
      + x ^ 16 / 20922789888000 := by
  have h0 : (1:ℝ) - (0:ℝ) ^ 2 / 2 + (0:ℝ) ^ 4 / 24 - (0:ℝ) ^ 6 / 720 + (0:ℝ) ^ 8 / 40320
      - (0:ℝ) ^ 10 / 3628800 + (0:ℝ) ^ 12 / 479001600 - (0:ℝ) ^ 14 / 87178291200
      + (0:ℝ) ^ 16 / 20922789888000 - Real.cos (0:ℝ) = 0 := by
    rw [Real.cos_zero]; norm_num
  have hd : Differentiable ℝ (fun t : ℝ => 1 - t ^ 2 / 2 + t ^ 4 / 24 - t ^ 6 / 720
      + t ^ 8 / 40320 - t ^ 10 / 3628800 + t ^ 12 / 479001600 - t ^ 14 / 87178291200
      + t ^ 16 / 20922789888000 - Real.cos t) := by
    have h2' : Differentiable ℝ (fun (t : ℝ) => t ^ 2 / 2) :=
      diff_div_const 2 2 (by norm_num)
    have h4' : Differentiable ℝ (fun (t : ℝ) => t ^ 4 / 24) :=
      diff_div_const 4 24 (by norm_num)
    have h6' : Differentiable ℝ (fun (t : ℝ) => t ^ 6 / 720) :=
      diff_div_const 6 720 (by norm_num)
    have h8' : Differentiable ℝ (fun (t : ℝ) => t ^ 8 / 40320) :=
      diff_div_const 8 40320 (by norm_num)
    have h10' : Differentiable ℝ (fun (t : ℝ) => t ^ 10 / 3628800) :=
      diff_div_const 10 3628800 (by norm_num)
    have h12' : Differentiable ℝ (fun (t : ℝ) => t ^ 12 / 479001600) :=
      diff_div_const 12 479001600 (by norm_num)
    have h14' : Differentiable ℝ (fun (t : ℝ) => t ^ 14 / 87178291200) :=
      diff_div_const 14 87178291200 (by norm_num)
    have h16' : Differentiable ℝ (fun (t : ℝ) => t ^ 16 / 20922789888000) :=
      diff_div_const 16 20922789888000 (by norm_num)
    exact (((((((((differentiable_const (1 : ℝ)).sub h2').add h4').sub h6').add h8').sub h10')
      .add h12').sub h14').add h16').sub Real.differentiable_cos
  have h := mvt_step (fun t : ℝ => 1 - t ^ 2 / 2 + t ^ 4 / 24 - t ^ 6 / 720 + t ^ 8 / 40320
      - t ^ 10 / 3628800 + t ^ 12 / 479001600 - t ^ 14 / 87178291200
      + t ^ 16 / 20922789888000 - Real.cos t) x hx hx2 hd
    (by
      intro t _ _
      simp [Real.deriv_cos, deriv_sub, deriv_add, deriv_mul, deriv_pow,
        deriv_const, deriv_id']
      ring_nf
      linarith [sin_ge_septic t (by linarith) (by linarith)])
    h0
  have h' : (0 : ℝ) ≤ 1 - x ^ 2 / 2 + x ^ 4 / 24 - x ^ 6 / 720 + x ^ 8 / 40320
      - x ^ 10 / 3628800 + x ^ 12 / 479001600 - x ^ 14 / 87178291200
      + x ^ 16 / 20922789888000 - Real.cos x := h
  linarith

/-! ## Попарная симметрия суммы по 22 модам -/

/-- Слагаемые `k` и `11 + k` равны: `cos(π + θ) = −cos θ`. -/
theorem abs_cos_mirror (k : ℕ) :
    |Real.cos (2 * Real.pi * (11 + k) / 22)|
      = |Real.cos (2 * Real.pi * k / 22)| := by
  have h1 : 2 * Real.pi * (11 + k) / 22 = Real.pi + (2 * Real.pi * k / 22) := by ring
  have h2 : Real.pi + (2 * Real.pi * k / 22) = 2 * Real.pi * k / 22 + Real.pi := by ring
  rw [h1, h2, Real.cos_add_pi]
  exact abs_neg _

theorem abs_cos_sum_22 :
    ∑ k ∈ Finset.range 22, |Real.cos (2 * Real.pi * k / 22)|
      = 2 * ∑ k ∈ Finset.range 11, |Real.cos (2 * Real.pi * k / 22)| := by
  have hsplit : ∑ k ∈ Finset.range 22, |Real.cos (2 * Real.pi * k / 22)|
      = (∑ k ∈ Finset.range 11, |Real.cos (2 * Real.pi * k / 22)|)
        + ∑ k ∈ Finset.range 11, |Real.cos (2 * Real.pi * (11 + k) / 22)| := by
    rw [show (22 : ℕ) = 11 + 11 from rfl]
    exact Finset.sum_range_add (fun k : ℕ => |Real.cos (2 * Real.pi * k / 22)|) 11 11
  rw [hsplit, Finset.sum_congr rfl (fun k _ => abs_cos_mirror k)]
  ring

/-- Косинус положителен для `j ≤ 5`: угол `2πj/22 ≤ 5π/11 < π/2`. -/
theorem cos_pos_small (j : ℕ) (hj : j ≤ 5) :
    0 < Real.cos (2 * Real.pi * j / 22) := by
  have hx0 : (0 : ℝ) ≤ 2 * Real.pi * j / 22 := by positivity
  have hle : 2 * Real.pi * j / 22 < Real.pi / 2 := by
    have h11 : (2 : ℝ) * Real.pi * j < Real.pi * 11 := by
      nlinarith [Real.pi_pos, hj]
    have h2' : Real.pi * 11 = Real.pi / 2 * 22 := by field_simp; ring
    rw [div_lt_iff₀ (by norm_num : (0 : ℝ) < 22), h2']
    linarith
  have h4 : Real.cos (Real.pi / 2) < Real.cos (2 * Real.pi * j / 22) :=
    Real.cos_lt_cos_of_nonneg_of_le_pi_div_two hx0 (le_refl _) hle
  have h2 : Real.cos (Real.pi / 2) = 0 := Real.cos_pi_div_two
  linarith

theorem abs_cos_sum_11 :
    ∑ k ∈ Finset.range 11, |Real.cos (2 * Real.pi * k / 22)|
      = 1 + 2 * ∑ j ∈ Finset.range 5, Real.cos (2 * Real.pi * (j + 1) / 22) := by
  have hstep1 : ∑ k ∈ Finset.range 11, |Real.cos (2 * Real.pi * k / 22)|
      = |Real.cos (2 * Real.pi * 0 / 22)|
        + ∑ k ∈ Finset.range 10, |Real.cos (2 * Real.pi * (1 + k) / 22)| := by
    rw [show (11 : ℕ) = 1 + 10 from rfl]
    exact Finset.sum_range_add (fun k : ℕ => |Real.cos (2 * Real.pi * k / 22)|) 1 10
  have h0 : |Real.cos (2 * Real.pi * 0 / 22)| = 1 := by
    simp [Real.cos_zero]
  have hpair : ∑ k ∈ Finset.range 10, |Real.cos (2 * Real.pi * (1 + k) / 22)|
      = 2 * ∑ j ∈ Finset.range 5, Real.cos (2 * Real.pi * (j + 1) / 22) := by
    have hsplit : ∑ k ∈ Finset.range 10, |Real.cos (2 * Real.pi * (1 + k) / 22)|
        = (∑ k ∈ Finset.range 5, |Real.cos (2 * Real.pi * (1 + k) / 22)|)
          + ∑ k ∈ Finset.range 5, |Real.cos (2 * Real.pi * (1 + (5 + k)) / 22)| := by
      rw [show (10 : ℕ) = 5 + 5 from rfl]
      exact Finset.sum_range_add (fun k : ℕ => |Real.cos (2 * Real.pi * (1 + k) / 22)|) 5 5
    have hrefl : ∑ k ∈ Finset.range 5, |Real.cos (2 * Real.pi * (1 + (5 + k)) / 22)|
        = ∑ k ∈ Finset.range 5, |Real.cos (2 * Real.pi * (1 + (4 - k)) / 22)| :=
      Finset.sum_range_reflect
        (fun k => |Real.cos (2 * Real.pi * (1 + (5 + k)) / 22)|) 5
    have hmirror : ∀ k ∈ Finset.range 5,
        |Real.cos (2 * Real.pi * (1 + (4 - k)) / 22)|
          = |Real.cos (2 * Real.pi * (1 + k) / 22)| := by
      intro k _
      have hk : k ≤ 4 := Nat.lt_succ_iff.mp (Finset.mem_range.mp k)
      have h10 : 1 + (4 - k) + (1 + k) = 11 := by omega
      have h1 : 2 * Real.pi * (1 + (4 - k)) / 22 = Real.pi - 2 * Real.pi * (1 + k) / 22 := by
        have he : 2 * Real.pi * (1 + (4 - k)) / 22 + 2 * Real.pi * (1 + k) / 22 = Real.pi := by
          rw [h10]
          field_simp
        linarith
      rw [h1, Real.cos_pi_sub, abs_neg]
    have habs : ∀ j ∈ Finset.range 5, |Real.cos (2 * Real.pi * (j + 1) / 22)|
        = Real.cos (2 * Real.pi * (j + 1) / 22) := fun j hj =>
      abs_of_nonneg (le_of_lt (cos_pos_small (j + 1) (by omega)))
    rw [hsplit, hrefl, Finset.sum_congr rfl hmirror, Finset.sum_congr rfl habs]
    ring
  rw [hstep1, h0, hpair]

/-! ## Пять десятичных мажорант -/

/-- Нижняя граница π из mathlib. -/
theorem piLo_le_pi : (3.14159265358979323846 : ℝ) ≤ Real.pi := le_of_lt Real.pi_gt_d20

/-- Мажоранта косинуса при `j ≥ 1`, `j ≤ 5`: точка `r ≤ j·π₋/11`, десятичная
мажоранта `c` для тейлоровского многочлена в `r`. -/
theorem cos_angle_le (j : ℕ) (r c : ℝ) (hj : 1 ≤ j) (hj5 : j ≤ 5)
    (hr : r ≤ 3.14159265358979323846 * j / 11)
    (hr2 : r ≤ 2)
    (hT : 1 - r ^ 2 / 2 + r ^ 4 / 24 - r ^ 6 / 720 + r ^ 8 / 40320
      - r ^ 10 / 3628800 + r ^ 12 / 479001600 - r ^ 14 / 87178291200
      + r ^ 16 / 20922789888000 ≤ c) :
    Real.cos (2 * Real.pi * j / 22) ≤ c := by
  have hreq : (2 : ℝ) * Real.pi * j / 22 = Real.pi * j / 11 := by ring
  have hple : 3.14159265358979323846 * j / 11 ≤ Real.pi * j / 11 :=
    div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_right piLo_le_pi
      (by exact_mod_cast hj.le)) (by norm_num)
  have hposr : (0 : ℝ) ≤ 3.14159265358979323846 * j / 11 := by positivity
  have hlt : 2 * Real.pi * j / 22 ≤ Real.pi := by
    have h22 : (2 : ℝ) * Real.pi * j ≤ Real.pi * 22 := by
      nlinarith [Real.pi_pos, hj5]
    have h2' : Real.pi * 22 = 2 * Real.pi * 22 / 2 := by field_simp; ring
    rw [hreq, div_le_iff₀ (by norm_num : (0 : ℝ) < 11), h2']
    linarith
  have hbound : 3.14159265358979323846 * j / 11 < 2 * Real.pi * j / 22 := by
    have h12 : 3.14159265358979323846 * j < Real.pi * j := by
      nlinarith [Real.pi_gt_d20, Real.pi_pos, hj]
    rw [hreq, lt_div_iff₀ (by norm_num : (0 : ℝ) < 11)]
    nlinarith [h12, Real.pi_pos, hj]
  refine le_trans ?_ (le_trans (cos_le_taylor8 r (by linarith) hr2) hT)
  exact le_of_lt (Real.cos_lt_cos_of_nonneg_of_le_pi hposr hlt
    (lt_of_le_of_lt (le_trans hr hple) hbound)).symm.le

/-- **Числовой лист**: `cSept ≤ 28.1067`. -/
theorem cSept_le_numeric : cSept ≤ 28.1067 := by
  rw [cSept_eq_two_abs_cos, abs_cos_sum_22, abs_cos_sum_11]
  have h1 : Real.cos (2 * Real.pi * (0 + 1) / 22) ≤ 0.959492974 :=
    cos_angle_le 1 0.285599332 0.959492974 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num)
  have h2 : Real.cos (2 * Real.pi * (1 + 1) / 22) ≤ 0.841253533 :=
    cos_angle_le 2 0.571198664 0.841253533 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num)
  have h3 : Real.cos (2 * Real.pi * (2 + 1) / 22) ≤ 0.654860735 :=
    cos_angle_le 3 0.856797996 0.654860735 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num)
  have h4 : Real.cos (2 * Real.pi * (3 + 1) / 22) ≤ 0.415415014 :=
    cos_angle_le 4 1.142397328 0.415415014 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num)
  have h5 : Real.cos (2 * Real.pi * (4 + 1) / 22) ≤ 0.142314839 :=
    cos_angle_le 5 1.427996660 0.142314839 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num)
  have hsum : ∑ j ∈ Finset.range 5, Real.cos (2 * Real.pi * (j + 1) / 22)
      ≤ 0.959492974 + 0.841253533 + 0.654860735 + 0.415415014 + 0.142314839 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_succ,
      Finset.sum_range_succ, Finset.sum_range_zero]
    linarith
  calc 2 * (1 + 2 * ∑ j ∈ Finset.range 5, Real.cos (2 * Real.pi * (j + 1) / 22))
      ≤ 2 * (1 + 2 * (0.959492974 + 0.841253533 + 0.654860735 + 0.415415014
          + 0.142314839)) :=
        mul_le_mul_of_nonneg_left (by
          exact add_le_add_left (mul_le_mul_of_nonneg_left hsum (by norm_num)) 1)
          (by norm_num)
    _ ≤ 28.1067 := by norm_num

end Septinal
