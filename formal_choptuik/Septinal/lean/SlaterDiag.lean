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



/-! ## Перекладка сортированных носителей -/

/-- Связь `.get`-формы сортированного списка (как в определении `slater`)
с `orderEmbOfFin`. -/
theorem sort_get_eq_orderEmbOfFin (U : Finset Slot) {k : ℕ} (h : U.card = k) (j : Fin k) :
    (U.sort (· ≤ ·)).get (Fin.cast (h.symm.trans (Finset.length_sort (· ≤ ·)).symm) j)
      = (U.orderEmbOfFin h j : Slot) := by
  rw [List.get_eq_getElem, Finset.orderEmbOfFin_apply]
  simp

/-- Мощность конечного множества при замене элемента `u₀ ↦ v` сохраняется. -/
theorem card_replace (U : Finset Slot) (u₀ : Slot) (hu : u₀ ∈ U) (v : Slot) (hv : v ∉ U) :
    ((U \ {u₀} : Finset Slot) ∪ {v}).card = U.card := by
  have hpos : 1 ≤ U.card := by
    have h5 := Finset.card_le_card (Finset.singleton_subset_iff.mpr hu)
    rwa [Finset.card_singleton] at h5
  rw [Finset.card_union_of_disjoint (Finset.disjoint_singleton_right.mpr (by simp [hv])),
    Finset.card_sdiff (Finset.singleton_subset_iff.mpr hu),
    Finset.card_singleton, Finset.card_singleton]
  exact Nat.sub_add_cancel hpos

/-- Замена элемента монотонного перечисления, направление `+1`
(сайт `u₀` заменяется свободным соседом `u₀ + 1`; случай `v = 0`, т.е.
циклический переход `21 ↦ 0`, здесь не покрывается). -/
theorem orderEmb_replace_succ (U : Finset Slot) (u₀ : Slot) (hu : u₀ ∈ U)
    (v : Slot) (hv : v ∉ U) (hadj : v = u₀ + 1) (hnb : (v : ℕ) ≠ 0) :
    (fun j : Fin U.card =>
        if (U.orderEmbOfFin rfl j : Slot) = u₀ then v else (U.orderEmbOfFin rfl j : Slot))
      = (U \ {u₀} ∪ {v}).orderEmbOfFin (card_replace U u₀ hu v hv) := by
  refine Finset.orderEmbOfFin_unique (card_replace U u₀ hu v hv) ?_ ?_
  · intro j
    by_cases hj : (U.orderEmbOfFin rfl j : Slot) = u₀
    · rw [if_pos hj]
      simp
    · rw [if_neg hj]
      have hmem : (U.orderEmbOfFin rfl j : Slot) ∈ U := Finset.orderEmbOfFin_mem U rfl j
      simp [hmem, hj, hv]
  · intro a b hab
    dsimp only
    by_cases ha : (U.orderEmbOfFin rfl a : Slot) = u₀
    · by_cases hb : (U.orderEmbOfFin rfl b : Slot) = u₀
      · exfalso
        have hEq : (U.orderEmbOfFin rfl a : Slot) = (U.orderEmbOfFin rfl b : Slot) := by
          rw [ha, hb]
        exact hab.ne ((U.orderEmbOfFin rfl).injective hEq)
      · rw [if_pos ha, if_neg hb]
        subst hadj
        have hmon : ((U.orderEmbOfFin rfl a : Slot) : ℕ) <
            ((U.orderEmbOfFin rfl b : Slot) : ℕ) :=
          (U.orderEmbOfFin rfl).strictMono hab
        have hmem : ((U.orderEmbOfFin rfl b : Slot) : Slot) ∈ U :=
          Finset.orderEmbOfFin_mem U rfl b
        have hne : ((U.orderEmbOfFin rfl b : Slot) : Slot) ≠ (u₀ + 1 : Slot) := by
          intro hc
          exact hv (hc ▸ hmem)
        have ha1 : ((U.orderEmbOfFin rfl a : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val ha
        have hne1 : ((U.orderEmbOfFin rfl b : Slot) : ℕ) ≠ ((u₀ + 1 : Slot) : ℕ) := by
          intro hc
          exact hne (Fin.val_injective hc)
        have hsuc : ((u₀ + 1 : Slot) : ℕ) = (u₀.val + 1) % 22 := by
          rw [val_suc u₀]
        have hg : ((u₀ + 1 : Slot) : ℕ) < ((U.orderEmbOfFin rfl b : Slot) : ℕ) := by omega
        exact hg
    · by_cases hb : (U.orderEmbOfFin rfl b : Slot) = u₀
      · rw [if_neg ha, if_pos hb]
        subst hadj
        have hmon : ((U.orderEmbOfFin rfl a : Slot) : ℕ) <
            ((U.orderEmbOfFin rfl b : Slot) : ℕ) :=
          (U.orderEmbOfFin rfl).strictMono hab
        have hb1 : ((U.orderEmbOfFin rfl b : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val hb
        have hsuc : ((u₀ + 1 : Slot) : ℕ) = (u₀.val + 1) % 22 := by
          rw [val_suc u₀]
        have hns : numSlots = 22 := rfl
        have h20 : (u₀ : ℕ) ≤ 20 := by
          by_contra hc
          have h21 : (u₀ : ℕ) = 21 := by have := u₀.isLt; omega
          have h22 : (u₀.val + 1) % numSlots = 0 := by omega
          rw [val_suc u₀] at hnb
          exact hnb h22
        have hg : ((U.orderEmbOfFin rfl a : Slot) : ℕ) < ((u₀ + 1 : Slot) : ℕ) := by
          rw [hsuc]
          omega
        exact hg
      · rw [if_neg ha, if_neg hb]
        simpa using (U.orderEmbOfFin rfl).strictMono hab

/-- Замена элемента монотонного перечисления, направление `−1`
(сайт `u₀` заменяется свободным соседом `u₀ − 1`; случай `u₀ = 0`, т.е.
циклический переход `0 ↦ 21`, здесь не покрывается). -/
theorem orderEmb_replace_pred (U : Finset Slot) (u₀ : Slot) (hu : u₀ ∈ U)
    (v : Slot) (hv : v ∉ U) (hadj : v = u₀ - 1) (hnb : (u₀ : ℕ) ≠ 0) :
    (fun j : Fin U.card =>
        if (U.orderEmbOfFin rfl j : Slot) = u₀ then v else (U.orderEmbOfFin rfl j : Slot))
      = (U \ {u₀} ∪ {v}).orderEmbOfFin (card_replace U u₀ hu v hv) := by
  refine Finset.orderEmbOfFin_unique (card_replace U u₀ hu v hv) ?_ ?_
  · intro j
    by_cases hj : (U.orderEmbOfFin rfl j : Slot) = u₀
    · rw [if_pos hj]
      simp
    · rw [if_neg hj]
      have hmem : (U.orderEmbOfFin rfl j : Slot) ∈ U := Finset.orderEmbOfFin_mem U rfl j
      simp [hmem, hj, hv]
  · intro a b hab
    dsimp only
    by_cases ha : (U.orderEmbOfFin rfl a : Slot) = u₀
    · by_cases hb : (U.orderEmbOfFin rfl b : Slot) = u₀
      · exfalso
        have hEq : (U.orderEmbOfFin rfl a : Slot) = (U.orderEmbOfFin rfl b : Slot) := by
          rw [ha, hb]
        exact hab.ne ((U.orderEmbOfFin rfl).injective hEq)
      · rw [if_pos ha, if_neg hb]
        subst hadj
        have hmon : ((U.orderEmbOfFin rfl a : Slot) : ℕ) <
            ((U.orderEmbOfFin rfl b : Slot) : ℕ) :=
          (U.orderEmbOfFin rfl).strictMono hab
        have ha1 : ((U.orderEmbOfFin rfl a : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val ha
        have hspr : ((u₀ - 1 : Slot) : ℕ) = (u₀.val + 21) % 22 := by
          rw [val_pred u₀]
        have hg : ((u₀ - 1 : Slot) : ℕ) < ((U.orderEmbOfFin rfl b : Slot) : ℕ) := by omega
        exact hg
    · by_cases hb : (U.orderEmbOfFin rfl b : Slot) = u₀
      · rw [if_neg ha, if_pos hb]
        subst hadj
        have hmon : ((U.orderEmbOfFin rfl a : Slot) : ℕ) <
            ((U.orderEmbOfFin rfl b : Slot) : ℕ) :=
          (U.orderEmbOfFin rfl).strictMono hab
        have hb1 : ((U.orderEmbOfFin rfl b : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val hb
        have hmem : ((U.orderEmbOfFin rfl a : Slot) : Slot) ∈ U :=
          Finset.orderEmbOfFin_mem U rfl a
        have hne : ((U.orderEmbOfFin rfl a : Slot) : Slot) ≠ (u₀ - 1 : Slot) := by
          intro hc
          exact hv (hc ▸ hmem)
        have hne1 : ((U.orderEmbOfFin rfl a : Slot) : ℕ) ≠ ((u₀ - 1 : Slot) : ℕ) := by
          intro hc
          exact hne (Fin.val_injective hc)
        have hspr : ((u₀ - 1 : Slot) : ℕ) = (u₀.val + 21) % 22 := by
          rw [val_pred u₀]
        have hns : numSlots = 22 := rfl
        have hg : ((U.orderEmbOfFin rfl a : Slot) : ℕ) < ((u₀ - 1 : Slot) : ℕ) := by omega
        exact hg
      · rw [if_neg ha, if_neg hb]
        simpa using (U.orderEmbOfFin rfl).strictMono hab



/-! ## Матрица Слейтера и её определитель -/

/-- Частота `i`-й моды набора `S` (в порядке возрастания). -/
noncomputable def modeOf (S : Finset Slot) (i : Fin S.card) : ℕ :=
  ((S.sort (· ≤ ·)).get (Fin.cast (Finset.length_sort (· ≤ ·)).symm i)).toNat

/-- Матрица Слейтера: строка `i` — мода `modeOf S i`, столбец `j` — сайт —
`j`-й (по возрастанию) элемент носителя `supp x`. -/
noncomputable def slaterMat (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card) :
    Matrix (Fin S.card) (Fin S.card) ℂ :=
  Matrix.of fun i j =>
    psi (modeOf S i)
      (((supp x).sort (· ≤ ·)).get
        (Fin.cast (h.symm.trans (Finset.length_sort (· ≤ ·)).symm) j))

/-- Определитель Слейтера — определитель матрицы `slaterMat`. -/
theorem slater_eq_det (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card) :
    slater S x = (slaterMat S x h).det := by
  rw [slater, dif_pos h]
  congr 1



/-! ## Столбец прыжка -/

/-- Столбцовая форма матрицы Слейтера через `orderEmbOfFin`. -/
theorem slaterMat_entry_emb (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (i j : Fin S.card) :
    slaterMat S x h i j = psi (modeOf S i) ((supp x).orderEmbOfFin h j) := by
  simp only [slaterMat, Matrix.of_apply, modeOf]
  rw [sort_get_eq_orderEmbOfFin (supp x) h j]

/-- Перечисление носителя с заменой `u₀ ↦ v = u₀ + 1` (без цикла 21 ↦ 0)
в покардинальной форме: позиция `j₀` даёт `v`, остальные позиции — как в `U`. -/
theorem orderEmb_replace_succ_index (U : Finset Slot) (u₀ : Slot) (hu : u₀ ∈ U)
    (v : Slot) (hv : v ∉ U) (hadj : v = u₀ + 1) (hnb : (v : ℕ) ≠ 0)
    {k : ℕ} (hk : U.card = k) (j₀ : Fin k) (hj₀ : (U.orderEmbOfFin hk j₀ : Slot) = u₀)
    (j : Fin k) :
    ((U \ {u₀} ∪ {v}).orderEmbOfFin ((card_replace U u₀ hu v hv).trans hk) j : Slot)
      = if j = j₀ then v else (U.orderEmbOfFin hk j : Slot) := by
  have hfun : (fun j : Fin k => if j = j₀ then v else (U.orderEmbOfFin hk j : Slot))
      = (U \ {u₀} ∪ {v}).orderEmbOfFin ((card_replace U u₀ hu v hv).trans hk) := by
    refine Finset.orderEmbOfFin_unique ((card_replace U u₀ hu v hv).trans hk) ?_ ?_
    · intro j
      by_cases hj : j = j₀
      · subst hj
        rw [if_pos rfl]
        simp
      · rw [if_neg hj]
        have hmem : (U.orderEmbOfFin hk j : Slot) ∈ U := Finset.orderEmbOfFin_mem U hk j
        have hne : (U.orderEmbOfFin hk j : Slot) ≠ u₀ := by
          intro hcc
          exact hj ((U.orderEmbOfFin hk).injective (by rw [hcc, hj₀]))
        simp [hmem, hne, hv]
    · intro a b hab
      dsimp only
      by_cases ha : a = j₀
      · by_cases hb : b = j₀
        · exfalso
          subst ha
          subst hb
          exact hab.ne rfl
        · rw [if_pos ha, if_neg hb]
          subst hadj
          have hmon : ((U.orderEmbOfFin hk a : Slot) : ℕ) <
            ((U.orderEmbOfFin hk b : Slot) : ℕ) :=
            (U.orderEmbOfFin hk).strictMono hab
          have haE : (U.orderEmbOfFin hk a : Slot) = u₀ := by rw [ha, hj₀]
          have ha1 : ((U.orderEmbOfFin hk a : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val haE
          have hmem : (U.orderEmbOfFin hk b : Slot) ∈ U := Finset.orderEmbOfFin_mem U hk b
          have hne : (U.orderEmbOfFin hk b : Slot) ≠ (u₀ + 1 : Slot) := by
            intro hcc
            exact hv (hcc ▸ hmem)
          have hne1 : ((U.orderEmbOfFin hk b : Slot) : ℕ) ≠ ((u₀ + 1 : Slot) : ℕ) := by
            intro hc
            exact hne (Fin.val_injective hc)
          have hsuc : ((u₀ + 1 : Slot) : ℕ) = (u₀.val + 1) % 22 := by
            rw [val_suc u₀]
          have hg : ((u₀ + 1 : Slot) : ℕ) < ((U.orderEmbOfFin hk b : Slot) : ℕ) := by omega
          exact hg
      · by_cases hb : b = j₀
        · rw [if_neg ha, if_pos hb]
          subst hadj
          have hmon : ((U.orderEmbOfFin hk a : Slot) : ℕ) <
            ((U.orderEmbOfFin hk b : Slot) : ℕ) :=
            (U.orderEmbOfFin hk).strictMono hab
          have hbE : (U.orderEmbOfFin hk b : Slot) = u₀ := by rw [hb, hj₀]
          have hb1 : ((U.orderEmbOfFin hk b : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val hbE
          have hsuc : ((u₀ + 1 : Slot) : ℕ) = (u₀.val + 1) % 22 := by
            rw [val_suc u₀]
          have hns : numSlots = 22 := rfl
          have h20 : (u₀ : ℕ) ≤ 20 := by
            by_contra hc
            have h21 : (u₀ : ℕ) = 21 := by have := u₀.isLt; omega
            have h22 : (u₀.val + 1) % numSlots = 0 := by omega
            rw [val_suc u₀] at hnb
            exact hnb h22
          have hg : ((U.orderEmbOfFin hk a : Slot) : ℕ) < ((u₀ + 1 : Slot) : ℕ) := by
            rw [hsuc]
            omega
          exact hg
        · rw [if_neg ha, if_neg hb]
          exact (U.orderEmbOfFin hk).strictMono hab
  rw [← hfun]

/-- Столбец прыжка (матричная форма): при замене занятого сайта
`u₀ ↦ v = u₀ + 1` (без цикла 21 ↦ 0) матрица с носителем
`supp x \ {u₀} ∪ {v}` равна `slaterMat S x h` со столбцом `j₀`
(позиция `u₀`), поточечно умноженным на `ω^{k_i}` по строкам-модам. -/
theorem slaterMat_replace_succ_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀mem : u₀ ∈ supp x) (v : Slot) (hvnot : v ∉ supp x)
    (hadj : v = u₀ + 1) (hnb : (v : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    (Matrix.of fun i j =>
        psi (modeOf S i)
          (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀mem v hvnot).trans h) j))
      = Matrix.of fun i j =>
          if j = j₀ then omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j := by
  ext i j
  simp only [Matrix.of_apply, slaterMat_entry_emb]
  by_cases hj : j = j₀
  · rw [hj, if_pos rfl,
      orderEmb_replace_succ_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j₀,
      if_pos rfl, hadj, psi_shift, hj₀]
  · rw [if_neg hj,
      orderEmb_replace_succ_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j,
      if_neg hj]

/-- Транспорт заменённого столбца в определитель (форма `n.succ` для
разложения Лапласа). -/
theorem det_replace_column {n : ℕ} (M : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (j₀ : Fin n.succ) (d : Fin n.succ → ℂ)
    (M' : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (h : ∀ i j, M' i j = if j = j₀ then d i * M i j else M i j) :
    M'.det = ∑ i, d i * M i j₀ * cof M i j₀ := by
  have hmeq : M' = Matrix.of fun i j => if j = j₀ then d i * M i j else M i j := by
    ext i j
    exact h i j
  rw [hmeq, scaled_column_det]

end Septinal
