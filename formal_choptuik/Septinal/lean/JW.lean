import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FieldSimp

import SeptinalYM.MatrixAux

/-!
# Слой Джордана–Вигнера: чётность, мажораны, CAR

Фундамент формализации оценки `‖V‖ ≤ 28.1067·|J|`. Точная многоточичная норма
XX+YY-цепочки на 22-цикле выводится разложением по секторам чётности и
диагонализацией квадратичной формы мажоран; здесь строится нижний слой:

* `weight`, `par` — вес и чётность конфигурации; `parity_flipTwo` —
  переворот двух различных битов сохраняет чётность (вес меняется на ±2 или 0);
* `rayleigh_sector_bound` — если форма матрицы, сохраняющей чётность,
  ограничена константой `C` на обоих секторах, то она ограничена `C` и на всём
  `ℋ_Sept` (секторы ортогональны: носители не пересекаются);
* `majVia` — мажораны `γ_{2s} = W_s σx_s` (`majX`), `γ_{2s+1} = W_s σy_s`
  (`majY`) как операторы на `Vec`; строка `W_s = Π_{u<s} σz_u` учитывается
  знаком `(-1)^(wBelow s x)`; `majVia_sq` (`γ² = 1`), `majVia_anticomm`
  (`{γ_a, γ_b} = 0` при разных слотах), `majX_majY_self`
  (`{γ_{2s}, γ_{2s+1}} = 0`);
* `bondTerm_mulVec_eq` — связь одного ребра с мажоранами:
  `bondTerm s = i(γ_{2s}γ_{2s+3} − γ_{2s+1}γ_{2s+2})` для внутренних рёбер
  `(s, s+1)`, `s + 1 < 22`. Ребро-обмотка `(21, 0)` содержит оператор чётности
  (фаза граничного условия φ ∈ {0, π} спектра) — обрабатывается на следующем
  слое вместе с диагонализацией.

Диагонализация квадратичной формы мажоран (преобразование Фурье по модам,
спектр `ε_k = 4cos((2πk+φ)/22)`, норма `2Σ_k|cos(2πk/22)| = 28.106697`) —
следующий слой; интерфейс `septinal_gap_jw` готов принять результат.
-/

open scoped Real
open scoped Matrix

namespace Septinal

/-! ## Степени (−1) -/

/-- `(−1)^{2k} = 1`. -/
theorem negOne_pow_two_mul (k : ℕ) : ((-1 : ℂ) ^ (2 * k)) = 1 := by
  induction k with
  | zero => simp
  | succ k ih =>
      have h : (2 : ℕ) * (k + 1) = (2 * k) + 2 := by ring
      rw [h, pow_add, ih, pow_two]
      norm_num

/-- `(−1)^n · (−1)^n = 1`. -/
theorem negOne_sq (w : ℕ) : ((-1 : ℂ) ^ w) * ((-1 : ℂ) ^ w) = 1 := by
  have h : (2 : ℕ) * w = w + w := by ring
  have h2 : ((-1 : ℂ) ^ w) * ((-1 : ℂ) ^ w) = ((-1 : ℂ) ^ (w + w)) := (pow_add _ w w).symm
  rw [h2, ← h, negOne_pow_two_mul]

/-- `(−1)^{w·2} = 1`. -/
theorem negOne_pow_mul_two (w : ℕ) : ((-1 : ℂ) ^ (w * 2)) = 1 := by
  rw [mul_comm, negOne_pow_two_mul]

/-- `(−1)^w · (−1)^{w+δ} = (−1)^δ`. -/
theorem negOne_two_add (w δ : ℕ) :
    ((-1 : ℂ) ^ w) * ((-1 : ℂ) ^ (w + δ)) = ((-1 : ℂ) ^ δ) := by
  have h : w + (w + δ) = (2 * w) + δ := by ring
  have h2 : ((-1 : ℂ) ^ w) * ((-1 : ℂ) ^ (w + δ)) = ((-1 : ℂ) ^ (w + (w + δ))) :=
    (pow_add _ w (w + δ)).symm
  rw [h2, h, pow_add, negOne_pow_two_mul, one_mul]

/-! ## Вес и чётность конфигурации -/

/-- Вес конфигурации: число единичных битов. -/
def weight (x : Cfg) : ℕ := ∑ u : Slot, (if x u = 1 then 1 else 0)

/-- Знак чётности: `(−1)^{вес}`. -/
def par (x : Cfg) : ℂ := (-1 : ℂ) ^ weight x

theorem ind_flip (b : Fin 2) :
    ((if (1 - b : Fin 2) = 1 then 1 else 0 : ℕ) + (if b = 1 then 1 else 0)) = 1 := by
  fin_cases b <;> simp

/-- Чётность степени: `(−1)^{вес}` равна `±1`. -/
theorem par_cases (x : Cfg) : par x = 1 ∨ par x = -1 := by
  have hsq : par x * par x = 1 := by
    unfold par
    have h2 : ((-1 : ℂ) ^ weight x) * ((-1 : ℂ) ^ weight x)
        = ((-1 : ℂ) ^ (weight x + weight x)) := (pow_add _ _ _).symm
    rw [h2]
    have h : (2 : ℕ) * weight x = weight x + weight x := by ring
    rw [← h, negOne_pow_two_mul]
  exact mul_self_eq_one_iff.mp hsq

/-- `(1 : ℂ) ≠ −1`. -/
theorem one_ne_neg_one_C : ¬((1 : ℂ) = -1) := by
  intro hc
  have hre : (1 : ℂ).re = ((-1 : ℂ)).re := congrArg Complex.re hc
  rw [Complex.neg_re, Complex.one_re] at hre
  linarith

/-- Сумма по всем слотам с точностью до двух точек: замена `F` на `G`,
совпадающих вне `{s, t}`, меняет сумму на `F s + F t − G s − G t`
(аддитивная форма). -/
theorem sum_univ_two_points {F G : Slot → ℕ} (s t : Slot) (hst : s ≠ t)
    (h : ∀ u : Slot, u ≠ s → u ≠ t → F u = G u) :
    (∑ u : Slot, F u) + (G s + G t) = (∑ u : Slot, G u) + (F s + F t) := by
  have hsmem : s ∉ (Finset.univ.erase s : Finset Slot) := by simp
  have h1 : ∑ u : Slot, F u = F s + ∑ u ∈ (Finset.univ.erase s), F u := by
    rw [Finset.add_sum_erase Finset.univ F (Finset.mem_univ s)]
  have h2 : ∑ u : Slot, G u = G s + ∑ u ∈ (Finset.univ.erase s), G u := by
    rw [Finset.add_sum_erase Finset.univ G (Finset.mem_univ s)]
  have htmem : t ∈ (Finset.univ.erase s : Finset Slot) :=
    Finset.mem_erase.2 ⟨Ne.symm hst, Finset.mem_univ t⟩
  have h3 : ∑ u ∈ (Finset.univ.erase s : Finset Slot), F u
      = F t + ∑ u ∈ ((Finset.univ.erase s).erase t), F u := by
    rw [Finset.add_sum_erase (Finset.univ.erase s) F htmem]
  have h4 : ∑ u ∈ (Finset.univ.erase s : Finset Slot), G u
      = G t + ∑ u ∈ ((Finset.univ.erase s).erase t), G u := by
    rw [Finset.add_sum_erase (Finset.univ.erase s) G htmem]
  have hEq : ∑ u ∈ ((Finset.univ.erase s).erase t : Finset Slot), F u
      = ∑ u ∈ ((Finset.univ.erase s).erase t : Finset Slot), G u := by
    refine Finset.sum_congr rfl fun u hu => ?_
    have hu1 : u ≠ s := by
      intro hc
      rw [hc] at hu
      simp at hu
    have hu2 : u ≠ t := by
      intro hc
      rw [hc] at hu
      simp at hu
    exact h u hu1 hu2
  rw [h1, h2, h3, h4, hEq]; ring

/-- Переворот двух различных битов: вес меняется на `2 − 2·(индикаторы)`. -/
theorem weight_flipTwo (s t : Slot) (hst : s ≠ t) (x : Cfg) :
    weight (flipTwo s t x)
      + 2 * ((if x s = 1 then 1 else 0) + (if x t = 1 then 1 else 0)) = weight x + 2 := by
  have hout : ∀ u : Slot, u ≠ s → u ≠ t →
      ((if flipTwo s t x u = 1 then 1 else 0 : ℕ)) = (if x u = 1 then 1 else 0) := by
    intro u hu1 hu2
    simp only [flipTwo, if_neg (not_or.mpr ⟨hu1, hu2⟩)]
  have hsum := sum_univ_two_points s t hst hout
  have hFs : ((if flipTwo s t x s = 1 then 1 else 0 : ℕ) + (if x s = 1 then 1 else 0)) = 1 := by
    have hxs : flipTwo s t x s = 1 - x s := by simp [flipTwo]
    rw [hxs]
    exact ind_flip (x s)
  have hFt : ((if flipTwo s t x t = 1 then 1 else 0 : ℕ) + (if x t = 1 then 1 else 0)) = 1 := by
    have hxt : flipTwo s t x t = 1 - x t := by simp [flipTwo]
    rw [hxt]
    exact ind_flip (x t)
  simp only [weight]
  omega

/-- Переворот двух различных битов сохраняет чётность. -/
theorem parity_flipTwo (s t : Slot) (hst : s ≠ t) (x : Cfg) :
    par (flipTwo s t x) = par x := by
  have h := weight_flipTwo s t hst x
  unfold par at *
  have e1 : ((-1 : ℂ) ^ weight (flipTwo s t x))
        * ((-1 : ℂ) ^ (2 * ((if x s = 1 then 1 else 0) + (if x t = 1 then 1 else 0))))
      = ((-1 : ℂ) ^ (weight (flipTwo s t x)
        + 2 * ((if x s = 1 then 1 else 0) + (if x t = 1 then 1 else 0)))) := (pow_add _ _ _).symm
  have e2 : ((-1 : ℂ) ^ weight x) * ((-1 : ℂ) ^ 2)
      = ((-1 : ℂ) ^ (weight x + 2)) := (pow_add _ _ _).symm
  have h2 : ((-1 : ℂ) ^ weight (flipTwo s t x))
        * ((-1 : ℂ) ^ (2 * ((if x s = 1 then 1 else 0) + (if x t = 1 then 1 else 0))))
      = ((-1 : ℂ) ^ weight x) * ((-1 : ℂ) ^ 2) := by
    rw [e1, e2, h]
  have hp2 : ((-1 : ℂ) ^ (2 : ℕ)) = 1 := by norm_num
  rw [negOne_pow_two_mul, hp2] at h2
  simpa using h2

/-! ## Секторное разложение квадратичной формы -/

/-- Положительный сектор: носитель в конфигурациях чётного веса. -/
noncomputable def sectorPos (v : Vec) : Vec := fun x => if par x = 1 then v x else 0

/-- Отрицательный сектор: носитель в конфигурациях нечётного веса. -/
noncomputable def sectorNeg (v : Vec) : Vec := fun x => if par x = -1 then v x else 0

theorem sectorPos_neg_support (v : Vec) : ∀ x : Cfg, par x = -1 → sectorPos v x = 0 := by
  intro x hx
  show (if par x = 1 then v x else 0) = 0
  rw [if_neg (show ¬(par x = 1) from by rw [hx]; norm_num)]

theorem sectorNeg_pos_support (v : Vec) : ∀ x : Cfg, par x = 1 → sectorNeg v x = 0 := by
  intro x hx
  show (if par x = -1 then v x else 0) = 0
  rw [if_neg (show ¬(par x = -1) from by rw [hx]; norm_num)]

theorem sector_decomp (v : Vec) : v = sectorPos v + sectorNeg v := by
  funext x
  rcases par_cases x with h | h
  · show v x = (if par x = 1 then v x else 0) + (if par x = -1 then v x else 0)
    rw [if_pos h, if_neg (show ¬(par x = -1) from by rw [h]; norm_num)]
    ring
  · show v x = (if par x = 1 then v x else 0) + (if par x = -1 then v x else 0)
    rw [if_neg (show ¬(par x = 1) from by rw [h]; norm_num), if_pos h]
    ring

theorem nrm2_sector (v : Vec) : nrm2 v = nrm2 (sectorPos v) + nrm2 (sectorNeg v) := by
  unfold nrm2
  rw [← sum_add_distrib' Finset.univ]
  refine Finset.sum_congr rfl fun x _ => ?_
  rcases par_cases x with h | h
  · show (‖v x‖ : ℝ) ^ 2
      = (‖(if par x = 1 then v x else 0)‖ : ℝ) ^ 2 + (‖(if par x = -1 then v x else 0)‖ : ℝ) ^ 2
    rw [if_pos h, if_neg (show ¬(par x = -1) from by rw [h]; norm_num), norm_zero]
    ring
  · show (‖v x‖ : ℝ) ^ 2
      = (‖(if par x = 1 then v x else 0)‖ : ℝ) ^ 2 + (‖(if par x = -1 then v x else 0)‖ : ℝ) ^ 2
    rw [if_neg (show ¬(par x = 1) from by rw [h]; norm_num), if_pos h, norm_zero]
    ring

set_option maxHeartbeats 4000000 in
/-- Кросс-члены исчезают: носители секторов не пересекаются, а матрица
сохраняет чётность. -/
theorem qform_sector_of_commute (A : Matrix Cfg Cfg ℂ)
    (hcomm : ∀ x y : Cfg, A x y ≠ 0 → par x = par y) (v : Vec) :
    qform A v = qform A (sectorPos v) + qform A (sectorNeg v) := by
  have h1 : qform A v = qform A (sectorPos v + sectorNeg v) :=
    congrArg (qform A) (sector_decomp v)
  have hexpand : ∀ x : Cfg,
      (star (sectorPos v x) + star (sectorNeg v x))
          * ((A *ᵥ sectorPos v) x + (A *ᵥ sectorNeg v) x)
        = star (sectorPos v x) * ((A *ᵥ sectorPos v) x)
          + star (sectorPos v x) * ((A *ᵥ sectorNeg v) x)
          + star (sectorNeg v x) * ((A *ᵥ sectorPos v) x)
          + star (sectorNeg v x) * ((A *ᵥ sectorNeg v) x) := by
    intro x; ring
  rw [h1]
  unfold qform
  simp only [Matrix.mulVec_add, Pi.add_apply, star_add]
  rw [Finset.sum_congr rfl fun x _ => hexpand x]
  rw [sum_add_distrib' Finset.univ, sum_add_distrib' Finset.univ, sum_add_distrib' Finset.univ]
  have hcross1 : ∑ x, star (sectorPos v x) * ((A *ᵥ sectorNeg v) x) = 0 := by
    refine Finset.sum_eq_zero fun x _ => ?_
    by_contra hne
    have hstar : star (sectorPos v x) ≠ 0 := fun hc => hne (by rw [hc, zero_mul])
    have hvx : sectorPos v x ≠ 0 := by
      intro hc
      apply hstar
      rw [hc]; simp
    have hsum : (A *ᵥ sectorNeg v) x ≠ 0 := fun hc => hne (by rw [hc, mul_zero])
    have hex : ∃ y, A x y * sectorNeg v y ≠ 0 := by
      by_contra hall
      push_neg at hall
      exact hsum (by rw [Matrix.mulVec, dotProduct]; exact Finset.sum_eq_zero fun y _ => hall y)
    obtain ⟨y, hy⟩ := hex
    have hAy : A x y ≠ 0 := fun hc => hy (by rw [hc, zero_mul])
    have hvy : sectorNeg v y ≠ 0 := fun hc => hy (by rw [hc, mul_zero])
    have hparxy := hcomm x y hAy
    have hpy : par y = -1 := by
      by_cases h : par y = -1
      · exact h
      · rw [sectorNeg, if_neg h] at hvy; exact absurd hvy (by simp)
    have hpx : par x = 1 := by
      by_cases h : par x = 1
      · exact h
      · rw [sectorPos, if_neg h] at hvx; exact absurd hvx (by simp)
    have hcon : par y = 1 := hparxy.symm.trans hpx
    rw [hcon] at hpy
    exact one_ne_neg_one_C hpy
  have hcross2 : ∑ x, star (sectorNeg v x) * ((A *ᵥ sectorPos v) x) = 0 := by
    refine Finset.sum_eq_zero fun x _ => ?_
    by_contra hne
    have hstar : star (sectorNeg v x) ≠ 0 := fun hc => hne (by rw [hc, zero_mul])
    have hvx : sectorNeg v x ≠ 0 := by
      intro hc
      apply hstar
      rw [hc]; simp
    have hsum : (A *ᵥ sectorPos v) x ≠ 0 := fun hc => hne (by rw [hc, mul_zero])
    have hex : ∃ y, A x y * sectorPos v y ≠ 0 := by
      by_contra hall
      push_neg at hall
      exact hsum (by rw [Matrix.mulVec, dotProduct]; exact Finset.sum_eq_zero fun y _ => hall y)
    obtain ⟨y, hy⟩ := hex
    have hAy : A x y ≠ 0 := fun hc => hy (by rw [hc, zero_mul])
    have hvy : sectorPos v y ≠ 0 := fun hc => hy (by rw [hc, mul_zero])
    have hparxy := hcomm x y hAy
    have hpy : par y = 1 := by
      by_cases h : par y = 1
      · exact h
      · rw [sectorPos, if_neg h] at hvy; exact absurd hvy (by simp)
    have hpx : par x = -1 := by
      by_cases h : par x = -1
      · exact h
      · rw [sectorNeg, if_neg h] at hvx; exact absurd hvx (by simp)
    have hcon : par y = -1 := hparxy.symm.trans hpx
    rw [hcon] at hpy
    exact one_ne_neg_one_C hpy.symm
  rw [hcross1, hcross2]
  abel

set_option maxHeartbeats 4000000 in
/-- **Секторное сведение.** Если квадратичная форма матрицы `A`, сохраняющей
чётность (`A x y ≠ 0 → par x = par y`), ограничена константой `C` на обоих
секторах чётности, то она ограничена `C` на всём пространстве. -/
theorem rayleigh_sector_bound (A : Matrix Cfg Cfg ℂ)
    (hcomm : ∀ x y : Cfg, A x y ≠ 0 → par x = par y) (C : ℝ)
    (hpos : ∀ u : Vec, (∀ x : Cfg, par x = -1 → u x = 0) → ‖qform A u‖ ≤ C * nrm2 u)
    (hneg : ∀ u : Vec, (∀ x : Cfg, par x = 1 → u x = 0) → ‖qform A u‖ ≤ C * nrm2 u)
    (v : Vec) : ‖qform A v‖ ≤ C * nrm2 v := by
  have hq := qform_sector_of_commute A hcomm v
  have h1 : ‖qform A v‖ ≤ ‖qform A (sectorPos v)‖ + ‖qform A (sectorNeg v)‖ := by
    rw [hq]; exact norm_add_le _ _
  have h2 := hpos (sectorPos v) (sectorPos_neg_support v)
  have h3 := hneg (sectorNeg v) (sectorNeg_pos_support v)
  rw [nrm2_sector v]
  linarith

/-! ## Мажораны -/

/-- Переворот одного бита (частный случай `flipTwo` с совпадающими слотами). -/
def flipOne (s : Slot) (x : Cfg) : Cfg := flipTwo s s x

theorem flipOne_invol (s : Slot) (x : Cfg) : flipOne s (flipOne s x) = x :=
  flipTwo_invol s s x

theorem flipOne_comm (s t : Slot) (hst : s ≠ t) (x : Cfg) :
    flipOne s (flipOne t x) = flipOne t (flipOne s x) := by
  funext u
  simp only [flipOne, flipTwo]
  by_cases hu : u = s
  · subst hu
    simp [hst]
  · by_cases hu2 : u = t
    · subst hu2
      simp [hst, hu]
    · simp [hu, hu2]

theorem flipOne_pair (s t : Slot) (hst : s ≠ t) (x : Cfg) :
    flipOne t (flipOne s x) = flipTwo s t x := by
  funext u
  simp only [flipOne, flipTwo]
  by_cases hu : u = s
  · subst hu
    simp [hst]
  · by_cases hu2 : u = t
    · subst hu2
      simp [hst, hu]
    · simp [hu, hu2]

/-- Число единичных битов строго ниже слота `s` (строка Джордана–Вигнера). -/
def wBelow (s : Slot) (x : Cfg) : ℕ :=
  ∑ u ∈ Finset.univ.filter (fun u : Slot => (u : ℕ) < (s : ℕ)), (if x u = 1 then 1 else 0)

theorem wBelow_flip_self (s : Slot) (x : Cfg) : wBelow s (flipOne s x) = wBelow s x := by
  unfold wBelow
  refine Finset.sum_congr rfl fun u hu => ?_
  have hu' : (u : ℕ) < (s : ℕ) := (Finset.mem_filter.1 hu).2
  have hus : u ≠ s := by
    intro hc
    rw [hc] at hu'
    simp at hu'
  simp only [flipOne, flipTwo, if_neg (not_or.mpr ⟨hus, hus⟩)]

/-- Строка для `s+1` отличается от строки для `s` ровно вкладом слота `s`. -/
theorem wBelow_suc_split (s : Slot) (hs : (s : ℕ) + 1 < numSlots) (x : Cfg) :
    wBelow (s + 1) x = wBelow s x + (if x s = 1 then 1 else 0) := by
  have hval : ((s + 1 : Slot) : ℕ) = (s : ℕ) + 1 := by
    have e1 : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + ((1 : Fin numSlots) : ℕ)) % numSlots :=
      Fin.val_add s 1
    have e2 : ((1 : Fin numSlots) : ℕ) = 1 := by simp
    rw [e1, e2]
    have h1 := s.isLt
    exact Nat.mod_eq_of_lt (by omega)
  unfold wBelow
  have hset : Finset.univ.filter (fun u : Slot => (u : ℕ) < ((s + 1 : Slot) : ℕ))
      = insert s (Finset.univ.filter (fun u : Slot => (u : ℕ) < (s : ℕ))) := by
    ext u
    have hval' := hval
    simp only [Finset.mem_filter, Finset.mem_univ, Finset.mem_insert, true_and]
    by_cases hus : (u : ℕ) = (s : ℕ)
    · rw [Fin.ext hus]
      exact iff_of_true (by rw [hval']; omega) (by simp)
    · have hnus : ¬(u = s) := fun hc => hus (congrArg Fin.val hc)
      rcases lt_or_gt_of_ne hus with hlt | hgt
      · exact iff_of_true (by rw [hval']; omega) (Or.inr hlt)
      · exact iff_of_false (by rw [hval']; omega)
          (by have h1 : ¬((u : ℕ) < (s : ℕ)) := by omega
              simpa [hnus] using h1)
  rw [hset, Finset.sum_insert
    (by simp : s ∉ Finset.univ.filter fun u : Slot => (u : ℕ) < (s : ℕ))]
  ring

theorem wBelow_suc_flip (s : Slot) (hs : (s : ℕ) + 1 < numSlots) (x : Cfg) :
    wBelow (s + 1) (flipOne s x) = wBelow s x + (if x s = 0 then 1 else 0) := by
  rw [wBelow_suc_split s hs (flipOne s x), wBelow_flip_self]
  have hfs : flipOne s x s = 1 - x s := by simp [flipOne, flipTwo]
  rw [hfs]
  rcases bit_cases (x s) with hb | hb <;> simp [hb]

/-- Строка для `t` при перевороте бита `s < t`: знак меняется на противоположный. -/
theorem wBelow_flip_lt (s t : Slot) (hst : (s : ℕ) < (t : ℕ)) (x : Cfg) :
    wBelow t (flipOne s x) + 2 * (if x s = 1 then 1 else 0) = wBelow t x + 1 := by
  unfold wBelow at *
  have hsmem : s ∈ Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ)) := by
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]; exact hst
  have hnot : s ∉ (Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ))).erase s := by simp
  have hset : Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ))
      = insert s ((Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ))).erase s) :=
    (Finset.insert_erase hsmem).symm
  rw [hset, Finset.sum_insert hnot, Finset.sum_insert hnot]
  have hcongr : ∑ u ∈ (Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ))).erase s,
      (if flipOne s x u = 1 then 1 else 0)
      = ∑ u ∈ (Finset.univ.filter (fun u : Slot => (u : ℕ) < (t : ℕ))).erase s,
      (if x u = 1 then 1 else 0) := by
    refine Finset.sum_congr rfl fun u hu => ?_
    have hus : u ≠ s := by
      intro hc
      rw [hc] at hu
      simp at hu
    simp only [flipOne, flipTwo, if_neg (not_or.mpr ⟨hus, hus⟩)]
  rw [hcongr]
  have hfs : flipOne s x s = 1 - x s := by simp [flipOne, flipTwo]
  rcases bit_cases (x s) with hb | hb <;> rw [hfs, hb] <;> simp <;> ring

theorem negOne_wBelow_flip_lt (s t : Slot) (hst : (s : ℕ) < (t : ℕ)) (x : Cfg) :
    ((-1 : ℂ) ^ wBelow t (flipOne s x)) = -((-1 : ℂ) ^ wBelow t x) := by
  have h := wBelow_flip_lt s t hst x
  have e1 : ((-1 : ℂ) ^ wBelow t (flipOne s x)) * ((-1 : ℂ) ^ (2 * (if x s = 1 then 1 else 0)))
      = ((-1 : ℂ) ^ (wBelow t (flipOne s x) + 2 * (if x s = 1 then 1 else 0))) :=
    (pow_add _ _ _).symm
  have e2 : ((-1 : ℂ) ^ wBelow t x) * ((-1 : ℂ) ^ 1)
      = ((-1 : ℂ) ^ (wBelow t x + 1)) := (pow_add _ _ _).symm
  have h2 : ((-1 : ℂ) ^ wBelow t (flipOne s x)) * ((-1 : ℂ) ^ (2 * (if x s = 1 then 1 else 0)))
      = ((-1 : ℂ) ^ wBelow t x) * ((-1 : ℂ) ^ 1) := by rw [e1, e2, h]
  rw [negOne_pow_two_mul, pow_one] at h2
  simpa using h2

/-! ## Операторы мажоран -/

/-- Локальный знак мажораны: `lsig false b = 1` (σx), `lsig true 0 = −i`,
`lsig true 1 = i` (σy). -/
def lsig (a : Bool) (b : Fin 2) : ℂ :=
  if a then (if b = 0 then -Complex.I else Complex.I) else 1

/-- Мажорана типа `a` в слоте `s`: `a = false` даёт `γ_{2s} = W_s σx_s`,
`a = true` — `γ_{2s+1} = W_s σy_s`, где `W_s = Π_{u<s} σz_u` — строка,
учитываемая знаком `(-1)^(wBelow s x)`. -/
def majVia (a : Bool) (s : Slot) (v : Vec) : Vec := fun x =>
  ((-1 : ℂ) ^ wBelow s x) * lsig a (x s) * v (flipOne s x)

/-- Мажорана `γ_{2s} = W_s σx_s`. -/
def majX (s : Slot) : Vec → Vec := majVia false s

/-- Мажорана `γ_{2s+1} = W_s σy_s`. -/
def majY (s : Slot) : Vec → Vec := majVia true s

theorem majVia_add (a : Bool) (s : Slot) (v w : Vec) :
    majVia a s (v + w) = majVia a s v + majVia a s w := by
  funext x
  simp only [majVia, Pi.add_apply, mul_add]

theorem majVia_smul (a : Bool) (s : Slot) (c : ℂ) (v : Vec) :
    majVia a s (c • v) = c • majVia a s v := by
  funext x
  simp only [majVia, Pi.smul_apply, smul_eq_mul]
  ring

theorem lsig_sq (a : Bool) (b : Fin 2) : lsig a b * lsig a (1 - b) = 1 := by
  cases a <;> fin_cases b <;> simp [lsig] <;> norm_num

theorem lsig_self_pair (b : Fin 2) :
    lsig false b * lsig true (1 - b) + lsig true b * lsig false (1 - b) = 0 := by
  fin_cases b <;> simp [lsig] <;> norm_num

/-- `γ² = 1` для мажораны любого типа. -/
theorem majVia_sq (a : Bool) (s : Slot) (v : Vec) : majVia a s (majVia a s v) = v := by
  funext x
  simp only [majVia]
  have h1 : wBelow s (flipOne s x) = wBelow s x := wBelow_flip_self s x
  have h2 : (flipOne s x) s = 1 - x s := by simp [flipOne, flipTwo]
  rw [h1, h2, flipOne_invol]
  have e1 : ((-1 : ℂ) ^ wBelow s x) * lsig a (x s)
        * (((-1 : ℂ) ^ wBelow s x) * lsig a (1 - x s) * v x)
      = (((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ wBelow s x))
        * (lsig a (x s) * lsig a (1 - x s) * v x) := by ring
  rw [e1, negOne_sq, one_mul, lsig_sq, one_mul]

/-- `{γ_{2s}, γ_{2s+1}} = 0` — антикоммутатор мажоран одного слота. -/
theorem majX_majY_self (s : Slot) (v : Vec) :
    majX s (majY s v) + majY s (majX s v) = 0 := by
  funext x
  simp only [majX, majY, majVia, Pi.add_apply, Pi.zero_apply]
  have h1 : wBelow s (flipOne s x) = wBelow s x := wBelow_flip_self s x
  have h2 : (flipOne s x) s = 1 - x s := by simp [flipOne, flipTwo]
  rw [h1, h2, flipOne_invol]
  have e1 : ((-1 : ℂ) ^ wBelow s x) * lsig false (x s)
        * (((-1 : ℂ) ^ wBelow s x) * lsig true (1 - x s) * v x)
      + ((-1 : ℂ) ^ wBelow s x) * lsig true (x s)
        * (((-1 : ℂ) ^ wBelow s x) * lsig false (1 - x s) * v x)
      = (((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ wBelow s x))
        * ((lsig false (x s) * lsig true (1 - x s) + lsig true (x s) * lsig false (1 - x s))
          * v x) := by
    ring
  rw [e1, negOne_sq, one_mul, lsig_self_pair, zero_mul]

/-- Явный вид композиции мажоран разных слотов (порядок `s`, затем `t`). -/
theorem majVia_majVia_apply (a b : Bool) (s t : Slot) (v : Vec) (x : Cfg) :
    (majVia a s (majVia b t v)) x
      = ((-1 : ℂ) ^ wBelow s x) * lsig a (x s)
        * (((-1 : ℂ) ^ wBelow t (flipOne s x))
          * lsig b ((flipOne s x) t) * v (flipOne t (flipOne s x))) := by
  simp only [majVia]

/-- Переворот бита `t ≥ s` не меняет строку для `s`. -/
theorem wBelow_flip_ge (s t : Slot) (hst : (s : ℕ) ≤ (t : ℕ)) (x : Cfg) :
    wBelow s (flipOne t x) = wBelow s x := by
  unfold wBelow
  refine Finset.sum_congr rfl fun u hu => ?_
  have hu' : (u : ℕ) < (s : ℕ) := (Finset.mem_filter.1 hu).2
  have hut : u ≠ t := by
    intro hc
    rw [hc] at hu'
    omega
  simp only [flipOne, flipTwo, if_neg (not_or.mpr ⟨hut, hut⟩)]

/-- Антикоммутация мажоран разных слотов при `s < t` (строка переворачивает
знак); типы `a`, `b` произвольны. -/
theorem majVia_anticomm_lt (s t : Slot) (hst : (s : ℕ) < (t : ℕ)) (a b : Bool) (v : Vec) :
    majVia a s (majVia b t v) + majVia b t (majVia a s v) = 0 := by
  funext x
  simp only [Pi.add_apply, Pi.zero_apply]
  have hne : s ≠ t := by
    intro hc
    rw [hc] at hst
    simp at hst
  have hcom : flipOne t (flipOne s x) = flipOne s (flipOne t x) := (flipOne_comm s t hne x).symm
  have hbt : (flipOne s x) t = x t := by simp [flipOne, flipTwo, Ne.symm hne]
  have hbs : (flipOne t x) s = x s := by simp [flipOne, flipTwo, hne]
  have hstr : ((-1 : ℂ) ^ wBelow t (flipOne s x)) = -((-1 : ℂ) ^ wBelow t x) :=
    negOne_wBelow_flip_lt s t hst x
  have hwt : ((-1 : ℂ) ^ wBelow s (flipOne t x)) = ((-1 : ℂ) ^ wBelow s x) :=
    congrArg (fun n : ℕ => (-1 : ℂ) ^ n) (wBelow_flip_ge s t (le_of_lt hst) x)
  rw [majVia_majVia_apply, majVia_majVia_apply, hcom, hstr, hwt, hbt, hbs]
  show _ = (0 : ℂ)
  ring

/-- **Антикоммутация мажоран разных слотов** (все четыре комбинации типов). -/
theorem majVia_anticomm (s t : Slot) (hst : s ≠ t) (a b : Bool) (v : Vec) :
    majVia a s (majVia b t v) + majVia b t (majVia a s v) = 0 := by
  rcases Nat.lt_or_ge (s : ℕ) (t : ℕ) with h | h
  · exact majVia_anticomm_lt s t h a b v
  · have hne : (s : ℕ) ≠ (t : ℕ) := by
      intro hc
      apply hst
      exact Fin.ext hc
    have h2 := majVia_anticomm_lt t s (by omega) b a v
    rw [add_comm]
    exact h2

/-! ## Связь bondTerm с мажоранами -/

/-- Значение `(s + 1 : Slot)` в натуральных числах при `s + 1 < 22`. -/
theorem suc_val (s : Slot) (hs : (s : ℕ) + 1 < numSlots) : ((s + 1 : Slot) : ℕ) = (s : ℕ) + 1 := by
  have e1 : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + ((1 : Fin numSlots) : ℕ)) % numSlots :=
    Fin.val_add s 1
  have e2 : ((1 : Fin numSlots) : ℕ) = 1 := by simp
  rw [e1, e2]
  have h1 := s.isLt
  exact Nat.mod_eq_of_lt (by omega)

theorem suc_ne (s : Slot) (hs : (s : ℕ) + 1 < numSlots) : (s + 1 : Slot) ≠ s := by
  intro hc
  have hc2 : ((s + 1 : Slot) : ℕ) = (s : ℕ) := by
    rw [Fin.ext_iff] at hc
    exact hc
  rw [suc_val s hs] at hc2
  omega

/-- Композиция `γ_{2s} γ_{2t+1}` (затем X-мажорана слота `s`, Y-мажорана `t`)
с уже свёрнутой строкой: строка для `t` распадается на строку для `s` и
множитель `(−1)^δ`. -/
theorem majX_majY_apply' (s t : Slot) (v : Vec) (x : Cfg) {δ : ℕ}
    (hwt : ((-1 : ℂ) ^ wBelow t (flipOne s x))
      = ((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ δ)) :
    (majX s (majY t v)) x
      = (((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ wBelow s x))
        * (((-1 : ℂ) ^ δ) * (lsig true ((flipOne s x) t) * v (flipOne t (flipOne s x)))) := by
  simp only [majX, majY]
  rw [majVia_majVia_apply, hwt]
  simp [lsig]
  ring

/-- Композиция `γ_{2s+1} γ_{2t}` с уже свёрнутой строкой. -/
theorem majY_majX_apply' (s t : Slot) (v : Vec) (x : Cfg) {δ : ℕ}
    (hwt : ((-1 : ℂ) ^ wBelow t (flipOne s x))
      = ((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ δ)) :
    (majY s (majX t v)) x
      = (((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ wBelow s x))
        * (((-1 : ℂ) ^ δ) * (lsig true (x s) * v (flipOne t (flipOne s x)))) := by
  simp only [majX, majY]
  rw [majVia_majVia_apply, hwt]
  simp [lsig]
  ring

/-- **Связь ребра с мажоранами (внутренние рёбра цикла).** При `s + 1 < 22`
действие `bondTerm s` на вектор совпадает с
`i·(γ_{2s}γ_{2s+3} − γ_{2s+1}γ_{2s+2})`:
`(bondTerm s *ᵥ v) x = i·((γ_{2s}(γ_{2s+3} v)) x − (γ_{2s+1}(γ_{2s+2} v)) x)`.
Ребро-обмотка `(21, 0)` содержит оператор чётности и обрабатывается на
следующем слое. -/
theorem bondTerm_mulVec_eq (s : Slot) (hs : (s : ℕ) + 1 < numSlots) (v : Vec) (x : Cfg) :
    (bondTerm s *ᵥ v) x
      = Complex.I * ((majX s (majY (s + 1) v)) x - (majY s (majX (s + 1) v)) x) := by
  rw [mulVec_bondTerm s v x]
  have hδ : ((-1 : ℂ) ^ wBelow (s + 1) (flipOne s x))
      = ((-1 : ℂ) ^ wBelow s x) * ((-1 : ℂ) ^ (if x s = 0 then 1 else 0)) := by
    rw [wBelow_suc_flip s hs x, pow_add]
  have hbt : (flipOne s x) (s + 1) = x (s + 1) := by
    simp only [flipOne, flipTwo,
      if_neg (not_or.mpr ⟨suc_ne s hs, suc_ne s hs⟩)]
  rw [majX_majY_apply' s (s + 1) v x hδ, majY_majX_apply' s (s + 1) v x hδ,
    flipOne_pair s (s + 1) (Ne.symm (suc_ne s hs)) x, hbt]
  rcases bit_cases (x s) with hb | hb <;>
    rcases bit_cases (x (s + 1)) with hb2 | hb2 <;>
    rw [hb, hb2] <;> simp [lsig] <;> ring_nf <;> rw [Complex.I_sq, negOne_pow_mul_two] <;> ring


/-! ## Чётность связи: V сохраняет чётность (пункт JW-программы 4) -/

/-- `(s+1 : Slot) ≠ s` всегда: цикл длины 22 ≥ 2. -/
theorem suc_ne_all (s : Slot) : (s + 1 : Slot) ≠ s := by
  intro hc
  have hc2 : ((s + 1 : Slot) : ℕ) = (s : ℕ) := by
    rw [Fin.ext_iff] at hc
    exact hc
  have e1 : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + ((1 : Fin numSlots) : ℕ)) % numSlots :=
    Fin.val_add s 1
  have e2 : ((1 : Fin numSlots) : ℕ) = 1 := by simp
  rw [e1, e2] at hc2
  rcases Nat.lt_or_ge (s : ℕ) 21 with hlt | hge
  · rw [Nat.mod_eq_of_lt (by have h22 : numSlots = 22 := rfl; have := s.isLt; omega)] at hc2
    omega
  · have hs21 : (s : ℕ) = 21 := by
      have h22 : numSlots = 22 := rfl
      have h1 := s.isLt
      omega
    rw [hs21] at hc2
    have h22 : numSlots = 22 := rfl
    rw [h22] at hc2
    simp at hc2

/-- Элемент `bondTerm s x y ≠ 0` соединяет конфигурации одинаковой чётности:
ненулевой перенос есть переворот двух битов, а он сохраняет чётность. -/
theorem bondTerm_parity (s : Slot) (x y : Cfg) (h : bondTerm s x y ≠ 0) : par x = par y := by
  by_cases hy : y = flipTwo s (s + 1) x
  · rw [hy, parity_flipTwo s (s + 1) (Ne.symm (suc_ne_all s)) x]
  · exact absurd h (by simp [bondTerm, hy])

/-- Переворот одного бита меняет вес на `±1`: `w' + 2·[x s = 1] = w + 1`. -/
theorem weight_flipOne (s : Slot) (x : Cfg) :
    weight (flipOne s x) + 2 * (if x s = 1 then 1 else 0) = weight x + 1 := by
  have hne : s ≠ (s + 1 : Slot) := Ne.symm (suc_ne_all s)
  have hout : ∀ u : Slot, u ≠ s → u ≠ (s + 1 : Slot) →
      ((if flipOne s x u = 1 then 1 else 0 : ℕ)) = (if x u = 1 then 1 else 0) := by
    intro u hu1 _
    simp only [flipOne, flipTwo, if_neg (not_or.mpr ⟨hu1, hu1⟩)]
  have hsum := sum_univ_two_points s (s + 1) hne hout
  have hFs : ((if flipOne s x s = 1 then 1 else 0 : ℕ) + (if x s = 1 then 1 else 0)) = 1 := by
    have hfs : flipOne s x s = 1 - x s := by simp [flipOne, flipTwo]
    rw [hfs]
    exact ind_flip (x s)
  have hFt : ((if flipOne s x (s + 1) = 1 then 1 else 0 : ℕ))
      = (if x (s + 1) = 1 then 1 else 0) := by
    have hfl : flipOne s x (s + 1) = x (s + 1) := by
      show (if (s + 1 : Slot) = s ∨ (s + 1 : Slot) = s then 1 - x (s + 1) else x (s + 1))
        = x (s + 1)
      rw [if_neg (show ¬((s + 1 : Slot) = s ∨ (s + 1 : Slot) = s) from
        not_or.mpr ⟨Ne.symm hne, Ne.symm hne⟩)]
    rw [hfl]
  simp only [weight]
  omega

/-- Переворот одного бита меняет чётность. -/
theorem par_flipOne (s : Slot) (x : Cfg) : par (flipOne s x) = -par x := by
  have h := weight_flipOne s x
  unfold par at *
  have e1 : ((-1 : ℂ) ^ weight (flipOne s x)) * ((-1 : ℂ) ^ (2 * (if x s = 1 then 1 else 0)))
      = ((-1 : ℂ) ^ (weight (flipOne s x) + 2 * (if x s = 1 then 1 else 0))) :=
    (pow_add _ _ _).symm
  have e2 : ((-1 : ℂ) ^ weight x) * ((-1 : ℂ) ^ 1) = ((-1 : ℂ) ^ (weight x + 1)) :=
    (pow_add _ _ _).symm
  have h2 : ((-1 : ℂ) ^ weight (flipOne s x)) * ((-1 : ℂ) ^ (2 * (if x s = 1 then 1 else 0)))
      = ((-1 : ℂ) ^ weight x) * ((-1 : ℂ) ^ 1) := by rw [e1, e2, h]
  rw [negOne_pow_two_mul, pow_one] at h2
  simpa using h2

/-- Взаимодействие `V J` сохраняет чётность: ненулевые элементы матрицы
соединяют конфигурации одинаковой чётности. -/
theorem V_parity_commute (J : ℝ) (x y : Cfg) (h : (V J) x y ≠ 0) : par x = par y := by
  by_contra hpar
  have hall : ∀ s : Slot, bondTerm s x y = 0 := by
    intro s
    by_cases hc : bondTerm s x y = 0
    · exact hc
    · exact absurd (bondTerm_parity s x y hc) hpar
  have hsum : ∑ s : Slot, bondTerm s x y = 0 := Finset.sum_eq_zero (fun s _ => hall s)
  have hv : (V J) x y = ((J : ℝ) : ℂ) * ∑ s : Slot, bondTerm s x y := by
    rw [V, Matrix.smul_apply, Finset.sum_apply, Finset.sum_apply, smul_eq_mul]
  exact h (by rw [hv, hsum, mul_zero])


/-! ## Ребро-обмотка (21, 0): мажораны с оператором чётности (пункт JW-программы 1) -/

/-- Вес `x` распадается на строку последнего слота и его бит. -/
theorem weight_eq_wBelow_add_last (x : Cfg) :
    weight x = wBelow 21 x + (if x 21 = 1 then 1 else 0) := by
  have h21 : ((21 : Slot) : ℕ) = 21 := rfl
  unfold weight wBelow
  have hcompl : (Finset.univ.filter fun u : Slot => (u : ℕ) < ((21 : Slot) : ℕ))ᶜ
      = {(21 : Slot)} := by
    ext u
    simp only [Finset.mem_compl, Finset.mem_filter, Finset.mem_univ,
      Finset.mem_singleton, true_and]
    constructor
    · intro h
      have h1 := u.isLt
      have h22 : numSlots = 22 := rfl
      have h4 : (u : ℕ) = 21 := by
        have h5 : ((21 : Slot) : ℕ) = 21 := rfl
        have h6 : (u : ℕ) < numSlots := u.isLt
        have h7 : numSlots = 22 := rfl
        omega
      exact Fin.val_inj.mp h4
    · intro h hc
      rw [h] at hc
      simp at hc
  rw [← Finset.sum_add_sum_compl
    (Finset.univ.filter fun u : Slot => (u : ℕ) < ((21 : Slot) : ℕ))
    (fun u : Slot => (if x u = 1 then 1 else 0)), hcompl, Finset.sum_singleton]

/-- Для последнего слота `(−1)^{строка} · чётность = (−1)^{бит}`:
промежуточные биты сокращаются. -/
theorem powBelow_mul_par_last (x : Cfg) :
    ((-1 : ℂ) ^ wBelow 21 x) * par x = (-1 : ℂ) ^ (if x 21 = 1 then 1 else 0) := by
  have hw := weight_eq_wBelow_add_last x
  unfold par at *
  have e1 : ((-1 : ℂ) ^ wBelow 21 x) * ((-1 : ℂ) ^ weight x)
      = ((-1 : ℂ) ^ (wBelow 21 x + weight x)) := (pow_add _ _ _).symm
  rw [e1, hw]
  have h2 : wBelow 21 x + (wBelow 21 x + (if x 21 = 1 then 1 else 0))
      = (2 * wBelow 21 x) + (if x 21 = 1 then 1 else 0) := by ring
  rw [h2, pow_add, negOne_pow_two_mul, one_mul]

/-- Скрученная мажорана слота 0: строка Джордана–Вигнера замыкается через
оператор чётности `P = (−1)^N`, т.е. `γ_{2·22+a} = P·γ_a`. -/
def majTw (a : Bool) (v : Vec) : Vec := fun x =>
  par x * lsig a (x 0) * v (flipOne 0 x)

/-- Числовое ядро кросс-случаев: `I² = −1`, поэтому правая часть равна `2w`. -/
theorem bondTerm_cross_mul (w : ℂ) : w * 2 = -(w * Complex.I ^ (2 : ℕ) * 2) := by
  have hI : Complex.I ^ (2 : ℕ) = -1 := by norm_num
  rw [hI]
  ring

/-- **Ребро-обмотка (21, 0)**: с учётом замыкания строки через чётность,
`bondTerm 21 = i(γ_{42}·(Pγ_1) − γ_{43}·(Pγ_0))`. -/
theorem bondTerm_last_mulVec_eq (v : Vec) (x : Cfg) :
    (bondTerm 21 *ᵥ v) x
      = Complex.I * ((majX 21 (majTw true v)) x - (majY 21 (majTw false v)) x) := by
  rw [mulVec_bondTerm 21 v x, show ((21 + 1 : Slot)) = 0 from by decide]
  have hz0 : (flipOne 21 x) 0 = x 0 := by
    simp [flipOne, flipTwo]
  have hX : (majX 21 (majTw true v)) x
      = ((-1 : ℂ) ^ wBelow 21 x) * par (flipOne 21 x)
        * (lsig true (x 0) * v (flipOne 0 (flipOne 21 x))) := by
    simp only [majX, majVia, majTw]
    rw [hz0, show lsig false (x 21) = 1 from rfl]
    ring
  have hY : (majY 21 (majTw false v)) x
      = ((-1 : ℂ) ^ wBelow 21 x) * par (flipOne 21 x)
        * (lsig true (x 21) * v (flipOne 0 (flipOne 21 x))) := by
    simp only [majY, majVia, majTw]
    rw [hz0, show lsig false (x 0) = 1 from rfl]
    ring
  rw [hX, hY, flipOne_pair 21 0 (Ne.symm (suc_ne_all 21)) x, par_flipOne, mul_neg,
    powBelow_mul_par_last]
  rcases bit_cases (x 21) with hb | hb <;>
    rcases bit_cases (x 0) with hb2 | hb2 <;>
    rw [hb, hb2] <;> simp [hb, hb2, lsig, Complex.I]
  all_goals
    refine Complex.ext ?_ ?_
    · simp [Complex.mul_re, Complex.neg_re, Complex.sub_re]
      ring
    · simp [Complex.mul_im, Complex.neg_im, Complex.sub_im]
      ring

end Septinal
