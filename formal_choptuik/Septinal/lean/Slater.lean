/-
Copyright (c) 2025. All rights reserved.
-/
import SeptinalYM.Fourier
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

/-!
# Многобитовый слой (пункт 3 JW-программы): спектр, максимум по модам, константа

Слой, которого ждёт JW-оценка `septinal_gap_jw_via_sectors`:

* **Одночастичный спектр** прыжкового оператора: `eps k = 4·cos(2πk/22)`
  (= `2ω^k + 2ω^{-k}` по `hop_fourier_eigen`). Сумма спектра равна нулю —
  элементарное спаривание `k ↔ k+11` (без геометрических прогрессий).
* **Максимум по занятым модам** — ключевой шаг сведения: для любого набора
  занятых мод `S` выполнено `|Σ_{k∈S} ε_k| ≤ Σ_{k: ε_k > 0} ε_k`, и равенство
  достигается на `S = {k : ε_k > 0}` (`subset_abs_le`, `subset_max_attained`).
  Доказательство опирается на `sum_neg_part_eq` (отрицательная часть спектра
  даёт минус положительную) и `sum_pos_eq_half_abs` (при нулевой сумме
  положительная часть равна половине суммы модулей).
* **Точная константа** `cSept = Σ_{ε>0} ε = 2·Σ_k |cos(2πk/22)|`
  (`cSept_eq_two_abs_cos`); численно `cSept = 28.1066967333...` ≤ 28.1067
  (перебор всех 2^22 подмножеств и 40-значная арифметика в
  `scripts/verify_csept.py`; антипериодический сектор даёт 28.0351 < 28.1067,
  поэтому константа покрывает оба сектора чётности).
* **Каркас Слейтеровских определителей**: одночастичные моды `psi` и
  определители `slater S x`. Ортонормированность определителей
  (Коши–Бине) и их диагональность `A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S` — следующий
  шаг формализации (см. STATUS_ОТЧЁТ.md).
-/

namespace Septinal

open Complex Real
open scoped Real Matrix

/-! ## Техническая лемма о расщеплении суммы фильтром -/

/-- Сумма по множеству расщепляется на сумму по фильтру и по дополнению. -/
theorem sum_filter_split {α : Type*} {M : Type*} [AddCommMonoid M] {f : α → M}
    (s : Finset α) (p : α → Prop) [DecidablePred p] :
    ∑ k ∈ s, f k = ∑ k ∈ s.filter p, f k + ∑ k ∈ s.filter (fun k => ¬ p k), f k := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    by_cases hpa : p a
    · have e1 : (insert a s).filter p = insert a (s.filter p) := by
        simp [Finset.filter_insert, hpa]
      have e2 : (insert a s).filter (fun k => ¬ p k) = s.filter (fun k => ¬ p k) := by
        simp [Finset.filter_insert, hpa]
      rw [Finset.sum_insert ha, ih, e1, e2,
        Finset.sum_insert (fun hc => ha (Finset.mem_filter.1 hc).1)]
      abel
    · have e1 : (insert a s).filter p = s.filter p := by
        simp [Finset.filter_insert, hpa]
      have e2 : (insert a s).filter (fun k => ¬ p k)
          = insert a (s.filter (fun k => ¬ p k)) := by
        simp [Finset.filter_insert, hpa]
      rw [Finset.sum_insert ha, ih, e1, e2,
        Finset.sum_insert (fun hc => ha (Finset.mem_filter.1 hc).1)]
      abel

/-! ## Одночастичный спектр и его сумма -/

/-- Одночастичные собственные значения прыжкового оператора (амплитуда 2 на
каждом ребре цикла): `ε_k = 4·cos(2πk/22)`. -/
noncomputable def eps (k : ℕ) : ℝ := 4 * Real.cos (2 * Real.pi * k / numSlots)

/-- Спаривание спектра: `ε_{k+11} = −ε_k` — моды через полпериода. -/
theorem eps_add_eleven (k : ℕ) : eps (k + 11) = -(eps k) := by
  unfold eps
  have hcast : ((k + 11 : ℕ) : ℝ) = ((k : ℕ) : ℝ) + 11 := by
    rw [Nat.cast_add]
    ring
  rw [show numSlots = 22 from rfl, hcast]
  rw [show (2 : ℝ) * Real.pi * (((k : ℕ) : ℝ) + 11) / ((22 : ℕ) : ℝ)
      = 2 * Real.pi * ((k : ℕ) : ℝ) / ((22 : ℕ) : ℝ) + Real.pi from by ring]
  rw [Real.cos_add_pi, mul_neg]

/-- Сумма одночастичного спектра равна нулю. -/
theorem sum_eps_zero : ∑ k ∈ Finset.range numSlots, eps k = 0 := by
  have h22 : numSlots = 22 := rfl
  rw [h22, show (22 : ℕ) = 11 + 11 from rfl, Finset.sum_range_add]
  have hterm : ∀ k : ℕ, k ∈ Finset.range 11 → eps (11 + k) = -(eps k) := by
    intro k _
    rw [Nat.add_comm 11 k]
    exact eps_add_eleven k
  rw [Finset.sum_congr rfl hterm, Finset.sum_neg_distrib]
  abel

/-! ## Положительная и отрицательная части спектра -/

/-- **Разбиение спектра**: отрицательная часть спектра в сумме даёт ровно
минус положительную часть (следствие нулевой суммы). -/
theorem sum_neg_part_eq {ε : ℕ → ℝ} (hsum : ∑ k ∈ Finset.range numSlots, ε k = 0) :
    ∑ k ∈ (Finset.range numSlots).filter (fun k => ε k < 0), ε k
      = -(∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k) := by
  classical
  have h1 := sum_filter_split (Finset.range numSlots) (fun k => 0 < ε k)
    (f := fun k => ε k)
  have h2 : ∑ k ∈ (Finset.range numSlots).filter (fun k => ¬(0 < ε k)), ε k
      = ∑ k ∈ (Finset.range numSlots).filter (fun k => ε k < 0), ε k
        + ∑ k ∈ (Finset.range numSlots).filter
            (fun k => ¬(0 < ε k) ∧ ¬(ε k < 0)), ε k := by
    have h2a := sum_filter_split
      ((Finset.range numSlots).filter (fun k => ¬(0 < ε k)))
      (fun k => ε k < 0) (f := fun k => ε k)
    have e1 : ((Finset.range numSlots).filter (fun k => ¬(0 < ε k))).filter
        (fun k => ε k < 0)
          = (Finset.range numSlots).filter (fun k => ε k < 0) := by
      ext k
      simp only [Finset.mem_filter, Finset.mem_range, not_lt]
      constructor
      · rintro ⟨⟨hr, h2⟩, h3⟩
        exact ⟨hr, h3⟩
      · rintro ⟨hr, h3⟩
        exact ⟨⟨hr, le_of_lt h3⟩, h3⟩
    have e2 : ((Finset.range numSlots).filter (fun k => ¬(0 < ε k))).filter
        (fun k => ¬(ε k < 0))
          = (Finset.range numSlots).filter (fun k => ¬(0 < ε k) ∧ ¬(ε k < 0)) := by
      ext k
      simp only [Finset.mem_filter, Finset.mem_range, not_lt]
      constructor
      · rintro ⟨⟨hr, h2⟩, h3⟩
        exact ⟨hr, ⟨h2, h3⟩⟩
      · rintro ⟨hr, h4⟩
        exact ⟨⟨hr, h4.1⟩, h4.2⟩
    rw [h2a, e1, e2]
  have hZ0 : ∑ k ∈ (Finset.range numSlots).filter
      (fun k => ¬(0 < ε k) ∧ ¬(ε k < 0)), ε k = 0 :=
    Finset.sum_eq_zero fun k hk => by
      have h2 := (Finset.mem_filter.1 hk).1
      have h3 := (Finset.mem_filter.1 hk).2
      simp only [not_lt] at h3
      rw [le_antisymm h3.1 h3.2]
  rw [h1, h2, hZ0, add_zero] at hsum
  linarith

/-- **Общая лемма слоя**: при нулевой сумме спектра положительная часть
равна половине суммы модулей: `Σ_{ε>0} ε = (Σ |ε|)/2`. -/
theorem sum_pos_eq_half_abs {ε : ℕ → ℝ}
    (hsum : ∑ k ∈ Finset.range numSlots, ε k = 0) :
    ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k
      = (∑ k ∈ Finset.range numSlots, |ε k|) / 2 := by
  classical
  have hneg := sum_neg_part_eq hsum
  have habsA : ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), |ε k|
      = ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k :=
    Finset.sum_congr rfl fun k hk => abs_of_pos (Finset.mem_filter.1 hk).2
  have habsB : ∑ k ∈ (Finset.range numSlots).filter (fun k => ¬(0 < ε k)), |ε k|
      = ∑ k ∈ (Finset.range numSlots).filter (fun k => ¬(0 < ε k)), -(ε k) := by
    refine Finset.sum_congr rfl fun k hk => ?_
    have h3 : ¬(0 < ε k) := (Finset.mem_filter.1 hk).2
    simp only [not_lt] at h3
    exact abs_of_nonpos h3
  have habsB2 : ∑ k ∈ (Finset.range numSlots).filter (fun k => ¬(0 < ε k)), -(ε k)
      = -(∑ k ∈ (Finset.range numSlots).filter (fun k => ε k < 0), ε k) := by
    have hsplit := sum_filter_split
      ((Finset.range numSlots).filter (fun k => ¬(0 < ε k)))
      (fun k => ε k < 0) (f := fun k => -(ε k))
    have hZ0 : ∑ k ∈ ((Finset.range numSlots).filter (fun k => ¬(0 < ε k))).filter
        (fun k => ¬(ε k < 0)), -(ε k) = 0 :=
      Finset.sum_eq_zero fun k hk => by
        have h2 := (Finset.mem_filter.1 hk).1
        have h3 := (Finset.mem_filter.1 hk).2
        simp only [not_lt] at h3
        exact neg_eq_zero.2 (le_antisymm (not_lt.mp (Finset.mem_filter.1 h2).2) h3)
    have e1 : ((Finset.range numSlots).filter (fun k => ¬(0 < ε k))).filter
        (fun k => ε k < 0) = (Finset.range numSlots).filter (fun k => ε k < 0) := by
      ext k
      simp only [Finset.mem_filter, Finset.mem_range, not_lt]
      constructor
      · rintro ⟨⟨hr, h2⟩, h3⟩
        exact ⟨hr, h3⟩
      · rintro ⟨hr, h3⟩
        exact ⟨⟨hr, le_of_lt h3⟩, h3⟩
    rw [hsplit, e1, hZ0, add_zero, Finset.sum_neg_distrib]
  have habs : ∑ k ∈ Finset.range numSlots, |ε k|
      = ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), |ε k|
        + ∑ k ∈ (Finset.range numSlots).filter (fun k => ¬(0 < ε k)), |ε k| :=
    sum_filter_split (Finset.range numSlots) (fun k => 0 < ε k)
      (f := fun k => |ε k|)
  rw [habs, habsA, habsB, habsB2, hneg]
  ring

/-! ## Максимум по занятым модам -/

/-- **Оценка на произвольном наборе занятых мод**: `|Σ_{k∈S} ε_k| ≤ Σ_{ε>0} ε`.
Верхняя граница — отбрасывание неположительных слагаемых; нижняя —
симметрично через отрицательную часть спектра и `sum_neg_part_eq`. -/
theorem subset_abs_le {ε : ℕ → ℝ} (hsum : ∑ k ∈ Finset.range numSlots, ε k = 0)
    (S : Finset (Fin numSlots)) :
    |∑ k ∈ S, ε (k : ℕ)|
      ≤ ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k := by
  classical
  set A : Finset ℕ := (Finset.range numSlots).filter (fun k => 0 < ε k) with hA
  set C : Finset ℕ := (Finset.range numSlots).filter (fun k => ε k < 0) with hC
  -- разложение суммы по S на положительные и остальные слагаемые
  have hsplit : ∑ k ∈ S, ε (k : ℕ)
      = ∑ k ∈ S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ)), ε (k : ℕ)
        + ∑ k ∈ S.filter (fun (k : Fin numSlots) => ¬(0 < ε (k : ℕ))), ε (k : ℕ) :=
    sum_filter_split (α := Fin numSlots) S
      (fun (k : Fin numSlots) => 0 < ε (k : ℕ)) (f := fun k => ε (k : ℕ))
  have hSA : ∀ k ∈ S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ)),
      (k : ℕ) ∈ A := fun k hk =>
    Finset.mem_filter.2 ⟨Finset.mem_range.2 (Fin.isLt k),
      (Finset.mem_filter.1 hk).2⟩
  have hrest : ∀ k ∈ S.filter (fun (k : Fin numSlots) => ¬(0 < ε (k : ℕ))),
      ε (k : ℕ) ≤ 0 := by
    intro k hk
    have h3 : ¬(0 < ε (k : ℕ)) := (Finset.mem_filter.1 hk).2
    simp only [not_lt] at h3
    exact h3
  -- верхняя граница
  have hup : ∑ k ∈ S, ε (k : ℕ) ≤ ∑ k ∈ A, ε k := by
    have h2 : ∑ k ∈ S.filter (fun (k : Fin numSlots) => ¬(0 < ε (k : ℕ))),
        ε (k : ℕ) ≤ 0 :=
      Finset.sum_nonpos hrest
    have h3 : ∑ k ∈ S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ)),
        ε (k : ℕ) ≤ ∑ k ∈ A, ε k := by
      have hinj : Set.InjOn (fun (k : Fin numSlots) => (k : ℕ))
          (S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ))) := fun a _ b _ h =>
        Fin.ext h
      rw [← Finset.sum_image (s := S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ)))
        (g := fun (k : Fin numSlots) => (k : ℕ)) hinj]
      have himg : (S.filter (fun (k : Fin numSlots) => 0 < ε (k : ℕ))).image
          (fun (k : Fin numSlots) => (k : ℕ)) ⊆ A := by
        intro k hk
        rcases Finset.mem_image.1 hk with ⟨j, hj, rfl⟩
        exact hSA j hj
      exact Finset.sum_le_sum_of_subset_of_nonneg himg fun k hk _ =>
        le_of_lt (Finset.mem_filter.1 hk).2
    rw [hsplit]
    linarith
  -- нижняя граница: −Σ_S ε ≤ Σ_A ε
  have hdown : -(∑ k ∈ S, ε (k : ℕ)) ≤ ∑ k ∈ A, ε k := by
    have h1 : ∑ k ∈ S, -(ε (k : ℕ)) = -(∑ k ∈ S, ε (k : ℕ)) := Finset.sum_neg_distrib
    have h2 : ∑ k ∈ S, -(ε (k : ℕ))
        = ∑ k ∈ S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0), -(ε (k : ℕ))
          + ∑ k ∈ S.filter (fun (k : Fin numSlots) => ¬(ε (k : ℕ) < 0)),
              -(ε (k : ℕ)) :=
      sum_filter_split (α := Fin numSlots) S
        (fun (k : Fin numSlots) => ε (k : ℕ) < 0) (f := fun k => -(ε (k : ℕ)))
    have h3 : ∑ k ∈ S.filter (fun (k : Fin numSlots) => ¬(ε (k : ℕ) < 0)),
        -(ε (k : ℕ)) ≤ 0 :=
      Finset.sum_nonpos fun k hk => by
        have h4 : ¬(ε (k : ℕ) < 0) := (Finset.mem_filter.1 hk).2
        simp only [not_lt] at h4
        linarith
    have hSC : ∀ k ∈ S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0),
        (k : ℕ) ∈ C := fun k hk =>
      Finset.mem_filter.2 ⟨Finset.mem_range.2 (Fin.isLt k),
        (Finset.mem_filter.1 hk).2⟩
    have h5 : ∑ k ∈ S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0), -(ε (k : ℕ))
        ≤ ∑ k ∈ C, -(ε (k : ℕ)) := by
      have hinj : Set.InjOn (fun (k : Fin numSlots) => (k : ℕ))
          (S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0)) := fun a _ b _ h =>
        Fin.ext h
      have himgsum : ∑ k ∈ (S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0)).image
            (fun (k : Fin numSlots) => (k : ℕ)), -(ε k)
          = ∑ k ∈ S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0), -(ε (k : ℕ)) :=
        Finset.sum_image hinj
      rw [← himgsum]
      have himg : (S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0)).image
          (fun (k : Fin numSlots) => (k : ℕ)) ⊆ C := by
        intro k hk
        rcases Finset.mem_image.1 hk with ⟨j, hj, rfl⟩
        exact hSC j hj
      exact Finset.sum_le_sum_of_subset_of_nonneg himg fun k hk _ =>
        neg_nonneg.2 (le_of_lt (Finset.mem_filter.1 hk).2)
    have h6 : ∑ k ∈ C, -(ε (k : ℕ)) = -(∑ k ∈ C, ε k) := Finset.sum_neg_distrib
    have h7 : ∑ k ∈ C, ε k = -(∑ k ∈ A, ε k) := sum_neg_part_eq hsum
    calc -(∑ k ∈ S, ε (k : ℕ)) = ∑ k ∈ S, -(ε (k : ℕ)) := h1.symm
      _ ≤ ∑ k ∈ S.filter (fun (k : Fin numSlots) => ε (k : ℕ) < 0), -(ε (k : ℕ)) := by
          rw [h2]; linarith
      _ ≤ ∑ k ∈ C, -(ε (k : ℕ)) := h5
      _ = -(∑ k ∈ C, ε k) := h6
      _ = ∑ k ∈ A, ε k := by rw [h7]; ring
  -- сборка: |Σ_S ε| ≤ Σ_A ε (форма abs_le в mathlib v4.21: −b ≤ a ∧ a ≤ b)
  exact abs_le.2 ⟨by linarith [hdown], hup⟩

/-- **Максимум достигается** на наборе `S = {k : ε_k > 0}`: сумма
неотрицательна, поэтому модуль равен самой сумме. -/
theorem subset_max_attained {ε : ℕ → ℝ} (hsum : ∑ k ∈ Finset.range numSlots, ε k = 0) :
    |∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k|
      = ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < ε k), ε k :=
  abs_of_nonneg (Finset.sum_nonneg fun k hk =>
    (Finset.mem_filter.1 hk).2.le)

/-! ## Точная константа JW-оценки -/

/-- **Константа JW-оценки**: сумма положительной части одночастичного
спектра прыжкового оператора. -/
noncomputable def cSept : ℝ :=
  ∑ k ∈ (Finset.range numSlots).filter (fun k => 0 < eps k), eps k

/-- Константа в симметричной форме: `cSept = 2·Σ_k |cos(2πk/22)|`.
Численно `cSept = 28.1066967333...` ≤ 28.1067 (см. `scripts/verify_csept.py`;
антипериодический сектор даёт 28.0351 < 28.1067). -/
theorem cSept_eq_two_abs_cos :
    cSept = 2 * ∑ k ∈ Finset.range numSlots, |Real.cos (2 * Real.pi * k / numSlots)| := by
  rw [cSept, sum_pos_eq_half_abs sum_eps_zero]
  have habs : ∀ k ∈ Finset.range numSlots,
      |eps k| = 4 * |Real.cos (2 * Real.pi * k / numSlots)| := by
    intro k _
    unfold eps
    rw [abs_mul, abs_of_nonneg (a := (4 : ℝ)) (by norm_num)]
  have hsumabs : ∑ k ∈ Finset.range numSlots, |eps k|
      = 4 * ∑ k ∈ Finset.range numSlots, |Real.cos (2 * Real.pi * k / numSlots)| := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl habs
  rw [hsumabs]
  ring

/-! ## Каркас Слейтеровских определителей -/

/-- Одночастичная мода Фурье с нормировкой: `ψ_k(u) = ω^{k·u}/√22`. -/
noncomputable def psi (k : ℕ) : Slot → ℂ :=
  fun u => omega ^ ((k * (u : ℕ)) % numSlots) / ((Real.sqrt 22 : ℝ) : ℂ)

/-- Носитель конфигурации: занятые слоты. -/
def supp (x : Cfg) : Finset Slot := Finset.univ.filter (fun u => x u = 1)

/-- **Слейтеровский определитель** набора мод `S` на конфигурации `x`:
при `|supp x| = |S|` — определитель матрицы `ψ_k(u)`, где столбцы —
моды из `S` (в порядке возрастания), строки — занятые слоты `supp x`
(в порядке возрастания); иначе нуль. Многобитовое пространство распадается
на секторы по числу частиц; на секторе `m` частиц определители наборов
`S` мощности `m` образуют искомый базис. Диагональность
`A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S` и ортонормированность (Коши–Бине) — следующий
шаг формализации. -/
noncomputable def slater (S : Finset Slot) (x : Cfg) : ℂ :=
  if h : (supp x).card = S.card then
    Matrix.det
      (Matrix.of fun i : Fin S.card => fun j : Fin S.card =>
        psi (((S.sort (· ≤ ·)).get
              (Fin.cast (Finset.length_sort (· ≤ ·)).symm i))).toNat
          (((supp x).sort (· ≤ ·)).get
              (Fin.cast (h.symm.trans (Finset.length_sort (· ≤ ·)).symm) j)))
  else 0

end Septinal
