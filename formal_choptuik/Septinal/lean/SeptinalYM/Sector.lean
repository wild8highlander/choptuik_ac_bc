/-
Copyright (c) 2025. All rights reserved.
-/
import SeptinalYM.Gap
import SeptinalYM.Slater

/-!
# Мост к секторным оценкам: цепочка прыжков и её норма (пункт 4 JW-программы)

Замыкающее звено между слоем мажоран (`JW.lean`) и свободнофермионной
диагонализацией (`Slater.lean`). Взаимодействие `V J` — это скаляр `J`,
умноженный на сумму рёбер `bondTerm s`; поэтому квадратичная форма связи
в точности равна `J`-кратной форме цепочки:

`⟨v|V J|v⟩ = J·Σ_s ⟨v|bondTerm s|v⟩`  (`qform_V_eq_sum`),

без всяких гипотез на `v`. Следовательно, JW-оценка
`‖⟨v|V J|v⟩‖ ≤ C·|J|·‖v‖²` равносильна оценке нормы формы цепочки
`|Σ_s ⟨v|bondTerm s|v⟩| ≤ C·‖v‖²`.

Цепочка `Σ_s bondTerm s` сохраняет число частиц (`chain_weight`: ненулевой
перенос есть переворот двух битов), поэтому её спектральный анализ
распадается на секторы фиксированного веса. На секторе `m` частиц базис
Слейтеровских определителей `Ψ_S` (модуль `Slater.lean`, `|S| = m`)
диагонализует цепочку: `A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S`, откуда норма на секторе
равна `max_{|S|=m} |Σ_{k∈S} ε_k| ≤ cSept = 2·Σ_k|cos(2πk/22)| = 28.106697…`
(`subset_abs_le`, `subset_max_attained`, `cSept_eq_two_abs_cos`; числовая
сертификация — `scripts/verify_csept.py`).

Собственно спектральные факты (ортонормированность базиса по Коши–Бине
и диагональность) выделены в гипотезы `hchain`:
* `septinal_gap_of_chain` — из оценки нормы цепочки константой `cSept`
  и числового неравенства `cSept ≤ 28.1067` выводится зазор
  (`septinal_gap_gen` с `C = 28.1067`);
* `septinal_gap_jw_chain` — та же оценка замыкает обе секторные гипотезы
  `septinal_gap_jw_via_sectors` (каждая — частный случай оценки на всём
  пространстве).
-/

namespace Septinal

open scoped Real
open scoped Matrix

/-! ## Точный мост: форма связи через форму цепочки -/

/-- **Точное разложение формы связи по рёбрам**: `⟨v|V J|v⟩ = J·Σ_s ⟨v|bondTerm s|v⟩`.
Никаких гипотез на `v` не нужно. -/
theorem qform_V_eq_sum (J : ℝ) (v : Vec) :
    qform (V J) v = ((J : ℝ) : ℂ) * ∑ s : Slot, qform (bondTerm s) v := by
  rw [V, qform_smul, qform_sum]

/-- Норма формы связи равна `|J|`-кратной норме формы цепочки. -/
theorem qform_V_norm_eq (J : ℝ) (v : Vec) :
    ‖qform (V J) v‖ = |J| * ‖∑ s : Slot, qform (bondTerm s) v‖ := by
  rw [qform_V_eq_sum, norm_mul, Complex.norm_real, Real.norm_eq_abs]

/-- **Мост нормы**: если форма цепочки ограничена константой `C`
(`|Σ_s ⟨v|bondTerm s|v⟩| ≤ C·‖v‖²` — свободнофермионная оценка, фрагменты
«Коши–Бине» и «диагональность»), то `‖⟨v|V J|v⟩‖ ≤ C·|J|·‖v‖²`. -/
theorem qform_V_le_of_chain (J : ℝ) (C : ℝ) (v : Vec)
    (hchain : ∀ u : Vec, ‖∑ s : Slot, qform (bondTerm s) u‖ ≤ C * nrm2 u) :
    ‖qform (V J) v‖ ≤ C * |J| * nrm2 v := by
  have hform : C * |J| * nrm2 v = |J| * (C * nrm2 v) := by ring
  rw [qform_V_norm_eq]
  calc |J| * ‖∑ s : Slot, qform (bondTerm s) v‖ ≤ |J| * (C * nrm2 v) :=
      mul_le_mul_of_nonneg_left (hchain v) (abs_nonneg J)
    _ = C * |J| * nrm2 v := hform.symm

/-! ## Цепочка сохраняет число частиц -/

/-- Ненулевой перенос ребра — переворот двух различных битов. -/
theorem bondTerm_ne_cases (s : Slot) (x y : Cfg) (h : bondTerm s x y ≠ 0) :
    y = flipTwo s (s + 1) x ∧ x s ≠ x (s + 1) := by
  by_cases h1 : y = flipTwo s (s + 1) x
  · by_cases h2 : x s = x (s + 1)
    · have hz : bondTerm s x y = 0 := by
        simp only [bondTerm, Matrix.of_apply, if_pos h1]
        rw [if_neg (not_not.mpr h2)]
      exact absurd hz h
    · exact ⟨h1, h2⟩
  · exact absurd h (by simp only [bondTerm, Matrix.of_apply, if_neg h1]; norm_num)

/-- Биты на ненулевом ребре различны, поэтому ровно один из них равен 1. -/
theorem weight_indicator_sum_ne (x : Cfg) {s t : Slot} (hst : x s ≠ x t) :
    ((if x s = 1 then 1 else 0 : ℕ)) + (if x t = 1 then 1 else 0) = 1 := by
  rcases bit_cases (x s) with hb | hb
  · have ht : x t = 1 := by
      rcases bit_cases (x t) with hb2 | hb2
      · rw [hb, hb2] at hst
        exact absurd hst (by decide)
      · exact hb2
    rw [hb, ht]; simp
  · have ht : x t = 0 := by
      rcases bit_cases (x t) with hb2 | hb2
      · exact hb2
      · rw [hb, hb2] at hst
        exact absurd hst (by decide)
    rw [hb, ht]; simp

/-- Каждое ребро цепочки сохраняет вес конфигурации. -/
theorem bondTerm_weight (s : Slot) (x y : Cfg) (h : bondTerm s x y ≠ 0) :
    weight y = weight x := by
  obtain ⟨hfl, hbits⟩ := bondTerm_ne_cases s x y h
  have hw := weight_flipTwo s (s + 1) (Ne.symm (suc_ne_all s)) x
  have hind := weight_indicator_sum_ne x hbits
  rw [← hfl] at hw
  linarith

/-- **Цепочка сохраняет число частиц**: ненулевой элемент матрицы
`A = Σ_s bondTerm s` соединяет конфигурации равного веса. -/
theorem chain_weight (x y : Cfg) (h : (∑ s : Slot, bondTerm s) x y ≠ 0) :
    weight y = weight x := by
  by_contra hw
  have hall : ∀ s : Slot, bondTerm s x y = 0 := by
    intro s
    by_cases hc : bondTerm s x y = 0
    · exact hc
    · exact absurd (bondTerm_weight s x y hc) hw
  refine h ?_
  rw [Finset.sum_apply, Finset.sum_apply]
  exact Finset.sum_eq_zero fun s _ => hall s

/-! ## Замыкание JW-цепочки через норму свободнофермионной цепочки -/

/-- **Замыкание зазора (форма с константой `cSept`).** Свободнофермионная
оценка нормы цепочки `|Σ_s ⟨v|bondTerm s|v⟩| ≤ cSept·‖v‖²` (фрагменты
«Коши–Бине» и «диагональность»: базис Слейтеровских определителей
диагонализует цепочку на каждом секторе веса, максимум `|Σ_{k∈S} ε_k|`
по занятым модам равен `cSept = Σ_{ε>0} ε`) вместе с числовым неравенством
`cSept ≤ 28.1067` (сертификация `scripts/verify_csept.py`) даёт зазор
`Δ = Δ₀ − 28.1067·|J| > 0` при `|J| < Δ₀/28.1067`. -/
theorem septinal_gap_of_chain (phase : Slot → ℝ) (J : ℝ)
    (hchain : ∀ v : Vec, ‖∑ s : Slot, qform (bondTerm s) v‖ ≤ cSept * nrm2 v)
    (hnum : cSept ≤ 28.1067) (hJ : |J| < cmin phase / 28.1067) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥ Evac phase * nrm2 v + Δ * nrm2 v := by
  refine septinal_gap_gen phase J 28.1067 (by norm_num) ?_ hJ
  intro v
  calc ‖qform (V J) v‖ ≤ cSept * |J| * nrm2 v := qform_V_le_of_chain J cSept v hchain
    _ ≤ 28.1067 * |J| * nrm2 v := by
        exact mul_le_mul_of_nonneg_right
          (mul_le_mul_of_nonneg_right hnum (abs_nonneg J)) (nrm2_nonneg v)

/-- **Замыкание секторного сведения (`septinal_gap_jw_via_sectors`).**
Оценка нормы цепочки константой `28.1067` на всём пространстве даёт обе
секторные гипотезы сразу (каждая секторная гипотеза — частный случай
оценки на всём пространстве, носитель сектора не используется), и полная
JW-цепочка замыкается: остаётся единственный аналитический лист —
свободнофермионная диагонализация цепочки (базис Слейтера: Коши–Бине +
диагональность), дающий `hchain`. -/
theorem septinal_gap_jw_chain (phase : Slot → ℝ) (J : ℝ)
    (hchain : ∀ v : Vec, ‖∑ s : Slot, qform (bondTerm s) v‖ ≤ 28.1067 * nrm2 v)
    (hJ : |J| < cmin phase / 28.1067) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥ Evac phase * nrm2 v + Δ * nrm2 v :=
  septinal_gap_jw phase J (fun v => qform_V_le_of_chain J 28.1067 v hchain) hJ

/-- Секторные гипотезы `septinal_gap_jw_via_sectors` выполняются при наличии
оценки нормы цепочки: положительный сектор. -/
theorem sector_pos_bound_of_chain (J : ℝ)
    (hchain : ∀ v : Vec, ‖∑ s : Slot, qform (bondTerm s) v‖ ≤ 28.1067 * nrm2 v)
    (u : Vec) (h : ∀ x : Cfg, par x = -1 → u x = 0) :
    ‖qform (V J) u‖ ≤ 28.1067 * |J| * nrm2 u :=
  qform_V_le_of_chain J 28.1067 u hchain

/-- Секторные гипотезы `septinal_gap_jw_via_sectors` выполняются при наличии
оценки нормы цепочки: отрицательный сектор. -/
theorem sector_neg_bound_of_chain (J : ℝ)
    (hchain : ∀ v : Vec, ‖∑ s : Slot, qform (bondTerm s) v‖ ≤ 28.1067 * nrm2 v)
    (u : Vec) (h : ∀ x : Cfg, par x = 1 → u x = 0) :
    ‖qform (V J) u‖ ≤ 28.1067 * |J| * nrm2 u :=
  qform_V_le_of_chain J 28.1067 u hchain

end Septinal
