/-
Copyright (c) 2025. All rights reserved.
-/
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import SeptinalYM.Slater

/-!
# Фрагмент 3 (часть 1): кофакторная механика для диагональности A·Ψ_S

Ключевая структура доказательства диагональности
`A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S` (Кондон–Слейтер для однотелого оператора прыжка
на 22-цикле):

* каждый нетривиальный член `(bondTerm s *ᵥ Ψ_S)(x)` — определитель матрицы
  Слейтера `M(x)` с одним столбцом (столбцом прыгающей частицы), поточечно
  умноженным на `ω^{±k}` по строкам-модам: `ψ_k(u±1) = ω^{±k}·ψ_k(u)`;
* разложение такого определителя по этому столбцу (`scaled_column_det`) даёт
  `Σ_τ ω^{±k_τ}·M_{τ,j₀}·C_{τ,j₀}`;
* группировка по строкам-модам и разложение Лапласа по строке
  (`row_cofactor_sum`: `Σ_j M_{i,j}·C_{i,j} = det M`) сводит всё к
  `(Σ_{k∈S} (ω^k + ω^{-k}))·det M = (Σ_{k∈S} ε_k)·Ψ_S(x)`;
* слагаемые с заблокированными прыжками (сосед занят) сокращаются попарно:
  для занятой пары `(j, j+1)` столбцы пропорциональны
  (`M_{·,j+1} = ω^k·M_{·,j}`), и сумма «неправильных кофакторов»
  `Σ_τ [M_{τ,j+1}·C_{τ,j} + M_{τ,j}·C_{τ,j+1}] = 0` — определитель матрицы
  с двумя равными столбцами (`wrong_cofactor_zero`).

Здесь собраны чисто алгебраические блоки: `cof`, `scaled_column_det`,
`wrong_cofactor_zero`, `row_cofactor_sum`, `psi_shift`. Сборка диагональности
(перекладка индексов сортированных носителей) — следующий шаг.
-/

namespace Septinal

open Matrix

/-! ## Кофакторы -/

/-- Кофактор: знаковый минор (совпадает с членами разложения Лапласа
`Matrix.det_succ_row` / `det_succ_column`). -/
noncomputable def cof {n : ℕ} (M : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (i j : Fin n.succ) : ℂ :=
  (-1) ^ ((i : ℕ) + (j : ℕ)) * (M.submatrix i.succAbove j.succAbove).det

/-- Определитель матрицы, у которой столбец `j₀` поточечно умножен на `d`,
равен `Σ_i d_i · M_{i,j₀} · C_{i,j₀}` (разложение по этому столбцу). -/
theorem scaled_column_det {n : ℕ} (M : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (j₀ : Fin n.succ) (d : Fin n.succ → ℂ) :
    (Matrix.of fun i j => if j = j₀ then d i * M i j else M i j).det
      = ∑ i, d i * M i j₀ * cof M i j₀ := by
  rw [Matrix.det_succ_column (Matrix.of fun i j => if j = j₀ then d i * M i j else M i j) j₀]
  refine Finset.sum_congr rfl fun i _ => ?_
  have hsub : (Matrix.of fun i j => if j = j₀ then d i * M i j else M i j).submatrix
        i.succAbove j₀.succAbove
      = M.submatrix i.succAbove j₀.succAbove := by
    ext a b
    simp only [Matrix.submatrix_apply, Matrix.of_apply]
    rw [if_neg (Fin.succAbove_ne j₀ b)]
  rw [hsub, Matrix.of_apply, if_pos rfl, cof]
  ring

/-- «Неправильное» разложение по кофакторам чужого столбца равно нулю:
столбец `j` против кофакторов столбца `j' ≠ j` — определитель матрицы
с двумя равными столбцами. -/
theorem wrong_cofactor_zero {n : ℕ} (M : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (j j' : Fin n.succ) (hjj : j ≠ j') :
    ∑ i, M i j * cof M i j' = 0 := by
  have hsub : ∀ i : Fin n.succ, (Matrix.of fun i k => if k = j' then M i j else M i k).submatrix
        i.succAbove j'.succAbove
      = M.submatrix i.succAbove j'.succAbove := by
    intro i
    ext a b
    simp only [Matrix.submatrix_apply, Matrix.of_apply]
    rw [if_neg (Fin.succAbove_ne j' b)]
  have hcol : ∀ i, (Matrix.of fun i k => if k = j' then M i j else M i k) i j
      = (Matrix.of fun i k => if k = j' then M i j else M i k) i j' := by
    intro i
    simp [hjj]
  have hdet : (Matrix.of fun i k => if k = j' then M i j else M i k).det = 0 := by
    rw [← Matrix.det_transpose]
    exact Matrix.det_zero_of_row_eq (i := j) (j := j') hjj (by
      funext i
      simp only [Matrix.transpose_apply]
      exact hcol i)
  have hexp : ∑ i, M i j * cof M i j'
      = (Matrix.of fun i k => if k = j' then M i j else M i k).det := by
    rw [Matrix.det_succ_column (Matrix.of fun i k => if k = j' then M i j else M i k) j']
    exact Finset.sum_congr rfl fun i _ => by
      have h2 : (Matrix.of fun i k => if k = j' then M i j else M i k) i j' = M i j := by simp
      rw [h2, hsub i, cof]
      ring
  rw [hexp, hdet]

/-- Разложение Лапласа по строке `i` в кофакторной форме:
`Σ_j M_{i,j} · C_{i,j} = det M`. -/
theorem row_cofactor_sum {n : ℕ} (M : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (i : Fin n.succ) : ∑ j, M i j * cof M i j = M.det := by
  rw [Matrix.det_succ_row M i]
  exact Finset.sum_congr rfl fun j _ => by rw [cof]; ring

/-! ## Сдвиг мод Фурье -/

/-- Ключевое свойство мод: сдвиг занятого сайта на +1 умножает столбец
поточечно на `ω^k`: `ψ_k(u+1) = ω^{k mod 22} · ψ_k(u)`. -/
theorem psi_shift (k : ℕ) (u : Slot) :
    psi k (u + 1) = omega ^ (k % numSlots) * psi k u := by
  unfold psi
  rw [val_suc]
  have hmod : (k * ((Fin.val u + 1) % numSlots)) % numSlots
      = ((k * Fin.val u) % numSlots + k % numSlots) % numSlots := by
    have e1 : (k * ((Fin.val u + 1) % numSlots)) % numSlots
        = (k * (Fin.val u + 1)) % numSlots :=
      Nat.ModEq.mul_left k (Nat.mod_modEq (Fin.val u + 1) numSlots)
    have e2 : (k * (Fin.val u + 1)) % numSlots
        = ((k * Fin.val u) % numSlots + k % numSlots) % numSlots := by
      rw [Nat.mul_add, Nat.add_mod, Nat.mul_one]
    exact e1.trans e2
  rw [hmod, omega_pow_mod ((k * Fin.val u) % numSlots + k % numSlots), pow_add]
  ring


end Septinal
