import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Complex.Norm
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.ConjTranspose
import Mathlib.Data.Finset.Max
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FieldSimp

import SeptinalYM.MatrixAux
import SeptinalYM.JW

/-!
# Септинальный зазор (лемма 3 плана)

Оценка `H₀` — комбинаторный подсчёт по битам, без спектральной теоремы:

* `qform_H0_ge` — для `v ⊥ vac`: `Re⟨v|H₀|v⟩ ≥ (E_vac + Δ₀)·‖v‖²`;
* `septinal_gap` — существует `Δ > 0`: `Re⟨v|H_Sept|v⟩ ≥ (E_vac + Δ)·‖v‖²`
  при `|J| < Δ₀/44`.

Уточнение формулировки плана: зазор отсчитывается **от уровня вакуума**
`E_vac < 0`; абсолютная форма «⟨v|H|v⟩ ≥ Δ > 0» неверно поставлена.
Оценка `Δ = Δ₀ − 44|J|` сильнее консервативной формы плана `Δ₀ − 2‖V‖`.
-/

open scoped Real
open scoped Matrix

namespace Septinal

/-- Уровень вакуума: `E_vac = ½Σ_s(1 − √(1+2δ_s²)) < 0`. -/
noncomputable def Evac (phase : Slot → ℝ) : ℝ :=
  ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2)))) / 2

/-- Переразложение: `½Σ_s(1 − c_sτ_s(x)) = E_vac + ½Σ_s c_s(1 − τ_s(x))`. -/
theorem diag_expand (phase : Slot → ℝ) (x : Cfg) :
    ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)))) / 2 =
      Evac phase + (∑ s, √(1 + 2 * phase s ^ 2) * (1 - tau (x s))) / 2 := by
  unfold Evac
  have hkey : (∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)))
      = (∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2)))
        + (∑ s : Slot, √(1 + 2 * phase s ^ 2) * (1 - tau (x s))) := by
    refine Eq.trans (Finset.sum_congr rfl fun s _ => ?_) (sum_add_distrib' Finset.univ _ _)
    rcases tau_cases (x s) with ⟨hτ, hb⟩ | ⟨hτ, hb⟩
    · rw [hτ]; ring
    · rw [hτ]; ring
  rw [hkey, add_div]

/-- Для конфигурации `x ≠ vac` найдётся слот с битом 1. -/
theorem exists_bit_one {x : Cfg} (hx : x ≠ vac) : ∃ s : Slot, x s = 1 := by
  by_contra hcon
  push_neg at hcon
  refine hx ?_
  funext u
  rcases bit_cases (x u) with h0 | h1
  · simp [h0, vac]
  · exact absurd h1 (hcon u)

/-- Вес конфигурации: `Σ_s [x_s = 1] ≥ 1` при `x ≠ vac`. -/
theorem weight_ge_one {x : Cfg} (hx : x ≠ vac) :
    1 ≤ ∑ s, (if x s = 1 then 1 else (0 : ℝ)) := by
  obtain ⟨s0, hs0⟩ := exists_bit_one hx
  calc (1 : ℝ) = if x s0 = 1 then 1 else 0 := by rw [hs0]; simp
    _ ≤ ∑ s, (if x s = 1 then 1 else (0 : ℝ)) :=
      Finset.single_le_sum (f := fun s : Slot => if x s = 1 then 1 else (0 : ℝ))
        (fun i _ => by by_cases h : x i = 1 <;> simp [h]) (Finset.mem_univ s0)

/-- Оценка массы: `2‖v‖² ≤ Σ_s Σ_x (1 − τ_s(x))·‖v_x‖²` для `v ⊥ vac`
(вес каждой непустой конфигурации ≥ 1, вакуумная — нулевая). -/
theorem count_bound (phase : Slot → ℝ) (v : Vec) (hv : v vac = 0) :
    2 * nrm2 v ≤ ∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 := by
  have hper : ∀ (s : Slot) (x : Cfg),
      (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2
        = 2 * (if x s = 1 then (‖v x‖ : ℝ) ^ 2 else 0) := by
    intro s x
    have h01 : (0 : Fin 2) ≠ 1 := by decide
    rcases tau_cases (x s) with ⟨hτ, hb⟩ | ⟨hτ, hb⟩
    · rw [hτ, hb, if_neg h01, mul_zero, sub_self, zero_mul]
    · rw [hτ, hb, if_pos rfl]
      ring
  have hmass : ∀ x : Cfg,
      (‖v x‖ : ℝ) ^ 2 ≤ (‖v x‖ : ℝ) ^ 2 * (∑ s, (if x s = 1 then 1 else (0 : ℝ))) := by
    intro x
    by_cases hxv : x = vac
    · subst hxv
      rw [hv]
      simp
    · exact le_mul_of_one_le_right (sq_nonneg _) (weight_ge_one hxv)
  have hreindex : ∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2
      = 2 * ∑ x, (‖v x‖ : ℝ) ^ 2 * (∑ s, (if x s = 1 then 1 else (0 : ℝ))) := by
    simp only [hper, ← Finset.mul_sum]
    rw [Finset.sum_comm]
    refine congrArg (fun t : ℝ => 2 * t) (Finset.sum_congr rfl fun x _ => ?_)
    simp only [Finset.mul_sum, mul_ite, mul_one, mul_zero]
  have hstep : nrm2 v ≤ ∑ x, (‖v x‖ : ℝ) ^ 2 * (∑ s, (if x s = 1 then 1 else (0 : ℝ))) := by
    rw [nrm2]
    exact Finset.sum_le_sum fun x _ => hmass x
  rw [hreindex]
  exact mul_le_mul_of_nonneg_left hstep (by norm_num)

/-- Вещественность квадратичной формы эрмитовой матрицы:
`Re⟨v|M|v⟩ ≥ −‖⟨v|M|v⟩‖`. -/
theorem qform_re_ge_neg_abs (M : Matrix Cfg Cfg ℂ) (v : Vec) :
    (qform M v).re ≥ -‖qform M v‖ := by
  have h1 : -(qform M v).re ≤ |(qform M v).re| := by
    rcases le_or_gt 0 ((qform M v).re) with h | h
    · rw [abs_of_nonneg h]
      linarith
    · rw [abs_of_neg h]
  have h2 : |(qform M v).re| ≤ ‖qform M v‖ := Complex.abs_re_le_norm _
  linarith

/-- Ключевая оценка диагональной части: для `v ⊥ vac` (т.е. `v vac = 0`)
`Re⟨v|H₀|v⟩ ≥ (E_vac + Δ₀)·‖v‖²`. -/
theorem qform_H0_ge (phase : Slot → ℝ) (v : Vec) (hv : v vac = 0) :
    (qform (H0 phase) v).re ≥ Evac phase * nrm2 v + cmin phase * nrm2 v := by
  rw [qform_H0_val, Complex.ofReal_re]
  have hsplit : ∀ x : Cfg,
      ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)))) / 2 * (‖v x‖ : ℝ) ^ 2
        = Evac phase * (‖v x‖ : ℝ) ^ 2
          + ((∑ s, √(1 + 2 * phase s ^ 2) * (1 - tau (x s)) : ℝ)) / 2 * (‖v x‖ : ℝ) ^ 2 := by
    intro x
    rw [diag_expand phase x]; ring
  have h1 : ∑ x, Evac phase * (‖v x‖ : ℝ) ^ 2 = Evac phase * nrm2 v := by
    simp only [nrm2, Finset.mul_sum]
  have h2 : (∑ x, ((∑ s, √(1 + 2 * phase s ^ 2) * (1 - tau (x s)) : ℝ)) / 2 * (‖v x‖ : ℝ) ^ 2)
      = (∑ s, √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) * (2:ℝ)⁻¹ := by
    have hpx : ∀ x : Cfg,
        ((∑ s, √(1 + 2 * phase s ^ 2) * (1 - tau (x s)) : ℝ)) / 2 * (‖v x‖ : ℝ) ^ 2
          = (∑ s, (√(1 + 2 * phase s ^ 2) * (1 - tau (x s))) * (‖v x‖ : ℝ) ^ 2) / 2 := by
      intro x
      rw [div_mul_eq_mul_div, ← Finset.sum_mul]
    rw [Finset.sum_congr rfl fun x _ => hpx x, sum_div_two, Finset.sum_comm (β := ℝ)]
    refine congrArg (fun t : ℝ => t * (2:ℝ)⁻¹) (Finset.sum_congr rfl fun s _ => ?_)
    calc ∑ x, (√(1 + 2 * phase s ^ 2) * (1 - tau (x s))) * (‖v x‖ : ℝ) ^ 2
        = ∑ x, √(1 + 2 * phase s ^ 2) * ((1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) :=
          Finset.sum_congr rfl fun x _ => mul_assoc _ _ _
      _ = √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
  have hSnonneg : ∀ s : Slot, 0 ≤ ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 := by
    intro s
    refine Finset.sum_nonneg fun x _ => ?_
    rcases tau_cases (x s) with ⟨hτ, hb⟩ | ⟨hτ, hb⟩
    · rw [hτ]; nlinarith [sq_nonneg (‖v x‖ : ℝ)]
    · rw [hτ]; nlinarith [sq_nonneg (‖v x‖ : ℝ)]
  have hmono : (∑ s, √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2)
      ≥ cmin phase * ∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 := by
    have step1 : ∀ s : Slot,
        cmin phase * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2
          ≤ √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 :=
      fun s => mul_le_mul_of_nonneg_right (cmin_le phase s) (hSnonneg s)
    calc cmin phase * ∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2
        = ∑ s, cmin phase * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 :=
          Finset.mul_sum _ _ _
      _ ≤ ∑ s, √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 :=
          Finset.sum_le_sum fun s _ => step1 s
  have hcount : cmin phase * (2 * nrm2 v)
      ≤ cmin phase * ∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2 := by
    refine mul_le_mul_of_nonneg_left ?_ (le_trans (by norm_num) (one_le_cmin phase))
    exact count_bound phase v hv
  have hfinal : cmin phase * nrm2 v
      ≤ (∑ s, √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) * (2:ℝ)⁻¹ := by
    calc cmin phase * nrm2 v
        = cmin phase * (2 * nrm2 v) * (2:ℝ)⁻¹ := by ring
      _ ≤ cmin phase * (∑ s, ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) * (2:ℝ)⁻¹ :=
          mul_le_mul_of_nonneg_right hcount (by positivity)
      _ ≤ (∑ s, √(1 + 2 * phase s ^ 2) * ∑ x, (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) * (2:ℝ)⁻¹ :=
          mul_le_mul_of_nonneg_right hmono (by positivity)
  have h0 : ∑ x : Cfg,
      ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s))) / 2) * (‖v x‖ : ℝ) ^ 2
      = Evac phase * nrm2 v
        + (∑ s : Slot, √(1 + 2 * phase s ^ 2) * ∑ x : Cfg,
            (1 - tau (x s)) * (‖v x‖ : ℝ) ^ 2) * (2:ℝ)⁻¹ := by
    rw [Finset.sum_congr rfl fun x _ => hsplit x, sum_add_distrib', h1, h2]
  linarith

/-- **Обобщённая лемма 3.** Если константа связи `C > 0` допускает оценку
`‖⟨v|V J|v⟩‖ ≤ C·|J|·‖v‖²` и `|J| < Δ₀/C`, то у септинального гамильтониана
есть зазор над уровнем вакуума: существует `Δ > 0` (а именно `Δ = Δ₀ − C|J|`)
с `Re⟨v|H_Sept|v⟩ ≥ (E_vac + Δ)·‖v‖²` для всех `v ⊥ vac`.
Параметризация константой отделяет комбинаторную часть доказательства
(`qform_H0_ge`) от оценки нормы взаимодействия: улучшение последней
(например, до JW-константы `28.1067`) автоматически усиливает порог. -/
theorem septinal_gap_gen (phase : Slot → ℝ) (J C : ℝ) (hC : 0 < C)
    (hV : ∀ v : Vec, ‖qform (V J) v‖ ≤ C * |J| * nrm2 v)
    (hJ : |J| < cmin phase / C) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥ Evac phase * nrm2 v + Δ * nrm2 v := by
  have hJC : C * |J| < cmin phase := by
    calc C * |J| < C * (cmin phase / C) := mul_lt_mul_of_pos_left hJ hC
      _ = cmin phase := by field_simp
  have hΔpos : 0 < cmin phase - C * |J| := by
    have h1 := one_le_cmin phase
    linarith
  refine ⟨cmin phase - C * |J|, hΔpos, fun v hv => ?_⟩
  have h0 := qform_H0_ge phase v hv
  have hVn : (C * |J|) * nrm2 v + (qform (V J) v).re ≥ 0 := by
    have h1 := qform_re_ge_neg_abs (V J) v
    have h2 := hV v
    linarith
  have hq : (qform (HSept phase J) v).re
      = (qform (H0 phase) v).re + (qform (V J) v).re := by
    rw [HSept, qform_add, Complex.add_re]
  have hΔ : (cmin phase - C * |J|) * nrm2 v
      = cmin phase * nrm2 v - C * |J| * nrm2 v := by ring
  linarith

/-- **Лемма 3 плана (`septinal_gap`), грубая константа `C = 44`.** При
`|J| < Δ₀/44` у септинального гамильтониана есть зазор над уровнем вакуума:
существует `Δ > 0` (а именно `Δ = Δ₀ − 44|J|`) с `Re⟨v|H_Sept|v⟩ ≥
(E_vac + Δ)·‖v‖²` для всех `v ⊥ vac`. -/
theorem septinal_gap (phase : Slot → ℝ) (J : ℝ) (hJ : |J| < cmin phase / 44) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥ Evac phase * nrm2 v + Δ * nrm2 v :=
  septinal_gap_gen phase J 44 (by norm_num) (fun v => qform_V_le J v) hJ

/-- **JW-порог плана (`C = 28.1067`).** Точная норма взаимодействия
XX+YY-цепочки на 22-цикле по Джордану–Вигнеру равна
`2·Σ_k |cos(2πk/22)| = 28.106697·|J|` (формула верифицирована прямой
диагонализацией при N = 4, 6, 8, 10 в `scripts/verify_septinal.py`;
формализация JW-диагоналирования в Lean — отдельный следующий шаг).
При условии этой оценки зазор положителен уже при `|J| < Δ₀/28.1067 ≈ 0.0421`
вместо `Δ₀/44 ≈ 0.0269`. -/
theorem septinal_gap_jw (phase : Slot → ℝ) (J : ℝ)
    (hJW : ∀ v : Vec, ‖qform (V J) v‖ ≤ 28.1067 * |J| * nrm2 v)
    (hJ : |J| < cmin phase / 28.1067) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥ Evac phase * nrm2 v + Δ * nrm2 v :=
  septinal_gap_gen phase J 28.1067 (by norm_num) hJW hJ

end Septinal

/-! ## Сведение JW-оценки к секторам чётности -/

/-- **Секторное сведение JW-оценки.** Так как `V J` сохраняет чётность
(`V_parity_commute`), оценка квадратичной формы на всём пространстве
равносильна паре оценок на секторах чётности. Осталось доказать секторные
оценки диагонализацией мажоран (Фурье по модам) — это следующий слой. -/
theorem septinal_gap_jw_via_sectors (phase : Slot → ℝ) (J : ℝ)
    (hpos : ∀ u : Septinal.Vec, (∀ x, Septinal.par x = -1 → u x = 0) →
      ‖Septinal.qform (Septinal.V J) u‖ ≤ 28.1067 * |J| * Septinal.nrm2 u)
    (hneg : ∀ u : Septinal.Vec, (∀ x, Septinal.par x = 1 → u x = 0) →
      ‖Septinal.qform (Septinal.V J) u‖ ≤ 28.1067 * |J| * Septinal.nrm2 u) :
    ∀ v : Septinal.Vec, ‖Septinal.qform (Septinal.V J) v‖ ≤ 28.1067 * |J| * Septinal.nrm2 v :=
  Septinal.rayleigh_sector_bound (Septinal.V J) (Septinal.V_parity_commute J) _ hpos hneg
