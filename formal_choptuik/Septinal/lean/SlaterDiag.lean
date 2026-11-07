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


/-! ## Сдвиг фазы влево и транспорт определителя -/

/-- Сдвиг фазы влево: `ψ_k(u−1) = ω^{−k}·ψ_k(u)`; равномерно по `u`
(включая цикл `0 ↦ 21`), так как `val_pred` — модульное равенство. -/
theorem psi_pred_shift (k : ℕ) (u : Slot) :
    psi k (u - 1) = omega ^ (numSlots - k % numSlots) * psi k u := by
  have h1 := psi_shift k (u - 1)
  rw [pred_add_one] at h1
  have hpow : (omega ^ (k % numSlots)) * omega ^ (numSlots - k % numSlots) = 1 := by
    have hsum : k % numSlots + (numSlots - k % numSlots) = numSlots := by
      rw [show numSlots = 22 from rfl]
      omega
    rw [← pow_add, hsum, omega_pow_numSlots]
  have hne : omega ^ (k % numSlots) ≠ 0 := by
    intro hc
    rw [hc, zero_mul] at hpow
    exact zero_ne_one hpow
  have hinv : (omega ^ (k % numSlots))⁻¹ = omega ^ (numSlots - k % numSlots) := by
    calc (omega ^ (k % numSlots))⁻¹
        = (omega ^ (k % numSlots))⁻¹
            * (omega ^ (k % numSlots) * omega ^ (numSlots - k % numSlots)) := by
          rw [hpow, mul_one]
      _ = ((omega ^ (k % numSlots))⁻¹ * omega ^ (k % numSlots))
            * omega ^ (numSlots - k % numSlots) := (mul_assoc _ _ _).symm
      _ = omega ^ (numSlots - k % numSlots) := by
          rw [inv_mul_cancel₀ hne, one_mul]
  calc psi k (u - 1) = (omega ^ (k % numSlots))⁻¹ * psi k u := by
        rw [h1, inv_mul_cancel_left₀ hne]
    _ = omega ^ (numSlots - k % numSlots) * psi k u := by rw [hinv]

/-- Перечисление носителя с заменой `u₀ ↦ v = u₀ − 1` (без цикла 0 ↦ 21)
в покардинальной форме: позиция `j₀` даёт `v`, остальные — как в `U`. -/
theorem orderEmb_replace_pred_index (U : Finset Slot) (u₀ : Slot) (hu : u₀ ∈ U)
    (v : Slot) (hv : v ∉ U) (hadj : v = u₀ - 1) (hnb : (u₀ : ℕ) ≠ 0)
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
          have hspr : ((u₀ - 1 : Slot) : ℕ) = (u₀.val + 21) % 22 := by
            rw [val_pred u₀]
          have hg : ((u₀ - 1 : Slot) : ℕ) < ((U.orderEmbOfFin hk b : Slot) : ℕ) := by omega
          exact hg
      · by_cases hb : b = j₀
        · rw [if_neg ha, if_pos hb]
          subst hadj
          have hmon : ((U.orderEmbOfFin hk a : Slot) : ℕ) <
              ((U.orderEmbOfFin hk b : Slot) : ℕ) :=
            (U.orderEmbOfFin hk).strictMono hab
          have hbE : (U.orderEmbOfFin hk b : Slot) = u₀ := by rw [hb, hj₀]
          have hb1 : ((U.orderEmbOfFin hk b : Slot) : ℕ) = (u₀ : ℕ) := congrArg Fin.val hbE
          have hmem : ((U.orderEmbOfFin hk a : Slot) : Slot) ∈ U :=
            Finset.orderEmbOfFin_mem U hk a
          have hne : ((U.orderEmbOfFin hk a : Slot) : Slot) ≠ (u₀ - 1 : Slot) := by
            intro hc
            exact hv (hc ▸ hmem)
          have hne1 : ((U.orderEmbOfFin hk a : Slot) : ℕ) ≠ ((u₀ - 1 : Slot) : ℕ) := by
            intro hc
            exact hne (Fin.val_injective hc)
          have hspr : ((u₀ - 1 : Slot) : ℕ) = (u₀.val + 21) % 22 := by
            rw [val_pred u₀]
          have hns : numSlots = 22 := rfl
          have hg : ((U.orderEmbOfFin hk a : Slot) : ℕ) < ((u₀ - 1 : Slot) : ℕ) := by omega
          exact hg
        · rw [if_neg ha, if_neg hb]
          exact (U.orderEmbOfFin hk).strictMono hab
  rw [← hfun]

/-- Столбец прыжка влево (без цикла): при замене занятого сайта `u₀ ↦
v = u₀ − 1` (без цикла 0 ↦ 21) матрица с носителем `supp x \ {u₀} ∪ {v}`
равна `slaterMat S x h` со столбцом `j₀`, поточечно умноженным на
`ω^{−k_i}` по строкам-модам. -/
theorem slaterMat_replace_pred_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀mem : u₀ ∈ supp x) (v : Slot) (hvnot : v ∉ supp x)
    (hadj : v = u₀ - 1) (hnb : (u₀ : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    (Matrix.of fun i j =>
        psi (modeOf S i)
          (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀mem v hvnot).trans h) j))
      = Matrix.of fun i j =>
          if j = j₀ then omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j := by
  ext i j
  simp only [Matrix.of_apply, slaterMat_entry_emb]
  by_cases hj : j = j₀
  · rw [hj, if_pos rfl,
      orderEmb_replace_pred_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j₀,
      if_pos rfl, hadj, psi_pred_shift, hj₀]
  · rw [if_neg hj,
      orderEmb_replace_pred_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j,
      if_neg hj]



/-! ## Позиции экстремумов в перечислении носителя -/

/-- Позиция максимума `21` в перечислении носителя — последняя, и единственна. -/
theorem orderEmbOfFin_max21 (U : Finset Slot) (hu : (21 : Slot) ∈ U) {k : ℕ}
    (hk : U.card = k) :
    (U.orderEmbOfFin hk (Fin.mk (k - 1) (by
        have h1 : 0 < U.card := Finset.card_pos.mpr ⟨21, hu⟩
        rw [hk] at h1; omega)) : Slot)
      = 21 ∧ ∀ i : Fin k, (U.orderEmbOfFin hk i : Slot) = 21 → (i : ℕ) = k - 1 := by
  have hbound : ∀ i : Fin k, ((U.orderEmbOfFin hk i : Slot) : ℕ) ≤ 21 := by
    intro i
    have hns : numSlots = 22 := rfl
    have := (U.orderEmbOfFin hk i).isLt
    omega
  have hrange : (21 : Slot) ∈ Set.range ⇑(U.orderEmbOfFin hk) := by
    rw [Finset.range_orderEmbOfFin]
    exact hu
  obtain ⟨i₀, hi₀⟩ := Set.mem_range.mp hrange
  set jmax : Fin k := Fin.mk (k - 1) (by
    have h1 : 0 < U.card := Finset.card_pos.mpr ⟨21, hu⟩
    rw [hk] at h1; omega) with hjmax
  have hjmaxv : (jmax : ℕ) = k - 1 := rfl
  constructor
  · by_cases hcase : (i₀ : ℕ) = k - 1
    · have hEq : jmax = i₀ := Fin.ext (by rw [hjmaxv, hcase])
      rw [hEq]
      exact hi₀
    · have hlt : (i₀ : ℕ) < k - 1 := by have := i₀.isLt; omega
      have hnat : ((U.orderEmbOfFin hk i₀ : Slot) : ℕ) <
          ((U.orderEmbOfFin hk jmax : Slot) : ℕ) :=
        Fin.lt_def.mp ((U.orderEmbOfFin hk).strictMono
          (Fin.lt_def.2 (by rw [hjmaxv]; exact hlt)))
      rw [hi₀] at hnat
      have h21 : ((21 : Slot) : ℕ) = 21 := rfl
      rw [h21] at hnat
      have hb := hbound jmax
      omega
  · intro i hi
    by_contra hc
    have hilt : (i : ℕ) < k - 1 := by have := i.isLt; omega
    have hlt2 : (i : ℕ) + 1 < k := by omega
    have hnat : ((U.orderEmbOfFin hk i : Slot) : ℕ) <
        ((U.orderEmbOfFin hk (⟨(i : ℕ) + 1, hlt2⟩ : Fin k) : Slot) : ℕ) :=
      Fin.lt_def.mp ((U.orderEmbOfFin hk).strictMono
        (Fin.lt_def.2 (by show (i : ℕ) < (i : ℕ) + 1; exact Nat.lt_succ_self _)))
    rw [hi] at hnat
    have h21 : ((21 : Slot) : ℕ) = 21 := rfl
    rw [h21] at hnat
    have hb := hbound (⟨(i : ℕ) + 1, hlt2⟩ : Fin k)
    omega

/-- Позиция минимума `0` в перечислении носителя — первая, и единственна. -/
theorem orderEmbOfFin_min0 (U : Finset Slot) (hu : (0 : Slot) ∈ U) {k : ℕ}
    (hk : U.card = k) :
    (U.orderEmbOfFin hk (Fin.mk 0 (by
        have h1 : 0 < U.card := Finset.card_pos.mpr ⟨0, hu⟩
        rw [hk] at h1; omega)) : Slot)
      = 0 ∧ ∀ i : Fin k, (U.orderEmbOfFin hk i : Slot) = 0 → (i : ℕ) = 0 := by
  have hrange : (0 : Slot) ∈ Set.range ⇑(U.orderEmbOfFin hk) := by
    rw [Finset.range_orderEmbOfFin]
    exact hu
  obtain ⟨i₀, hi₀⟩ := Set.mem_range.mp hrange
  set jmin : Fin k := Fin.mk 0 (by
    have h1 : 0 < U.card := Finset.card_pos.mpr ⟨0, hu⟩
    rw [hk] at h1; omega) with hjmin
  have hjminv : (jmin : ℕ) = 0 := rfl
  constructor
  · by_cases hcase : (i₀ : ℕ) = 0
    · have hEq : jmin = i₀ := Fin.ext (by rw [hjminv, hcase])
      rw [hEq]
      exact hi₀
    · have hpos : 0 < (i₀ : ℕ) := by omega
      have hnat : ((U.orderEmbOfFin hk jmin : Slot) : ℕ) <
          ((U.orderEmbOfFin hk i₀ : Slot) : ℕ) :=
        Fin.lt_def.mp ((U.orderEmbOfFin hk).strictMono
          (Fin.lt_def.2 (by rw [hjminv]; exact hpos)))
      rw [hi₀] at hnat
      have h0 : ((0 : Slot) : ℕ) = 0 := rfl
      rw [h0] at hnat
      omega
  · intro i hi
    by_contra hc
    have hipos : 0 < (i : ℕ) := by omega
    have hnat : ((U.orderEmbOfFin hk jmin : Slot) : ℕ) <
        ((U.orderEmbOfFin hk i : Slot) : ℕ) :=
      Fin.lt_def.mp ((U.orderEmbOfFin hk).strictMono
        (Fin.lt_def.2 (by rw [hjminv]; exact hipos)))
    rw [hi] at hnat
    have h0 : ((0 : Slot) : ℕ) = 0 := rfl
    rw [h0] at hnat
    omega

/-! ## Циклические прыжки: перечисление носителя при `21 ↦ 0` и `0 ↦ 21` -/

/-- Циклическая замена `21 ↦ 0` (прыжок через границу вправо): позиция `0`
нового перечисления даёт `0`, позиция `j ≥ 1` — элемент старой позиции
`j − 1`; занятая позиция `21` выпадает (она последняя по
`orderEmbOfFin_max21`). -/
theorem orderEmb_wrap21_index (U : Finset Slot) (hu : (21 : Slot) ∈ U)
    (hv : (0 : Slot) ∉ U) {k : ℕ} (hk : U.card = k) (j : Fin k) :
    ((U \ {21} ∪ {0}).orderEmbOfFin ((card_replace U 21 hu 0 hv).trans hk) j : Slot)
      = if (j : ℕ) = 0 then (0 : Slot)
        else (U.orderEmbOfFin hk
          (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega)) : Slot) := by
  have hfun : (fun j : Fin k => if (j : ℕ) = 0 then (0 : Slot)
        else (U.orderEmbOfFin hk
          (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega)) : Slot))
      = (U \ {21} ∪ {0}).orderEmbOfFin ((card_replace U 21 hu 0 hv).trans hk) := by
    refine Finset.orderEmbOfFin_unique ((card_replace U 21 hu 0 hv).trans hk) ?_ ?_
    · intro j
      by_cases hj : (j : ℕ) = 0
      · rw [if_pos hj]
        simp
      · rw [if_neg hj]
        have hmem : (U.orderEmbOfFin hk
            (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega)) : Slot) ∈ U :=
          Finset.orderEmbOfFin_mem U hk _
        have hne21 : (U.orderEmbOfFin hk
            (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega)) : Slot) ≠ (21 : Slot) := by
          intro hcc
          have hpos := (orderEmbOfFin_max21 U hu hk).2 _ hcc
          have hval : (((Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega) : Fin k) : ℕ))
              = (j : ℕ) - 1 := rfl
          have := j.isLt
          omega
        simp only [Finset.mem_union, Finset.mem_sdiff, Finset.mem_singleton]
        exact Or.inl ⟨hmem, hne21⟩
    · intro a b hab
      dsimp only
      have hval : (a : ℕ) < (b : ℕ) := hab
      by_cases hb0 : (b : ℕ) = 0
      · exfalso
        have := b.isLt
        omega
      · by_cases ha0 : (a : ℕ) = 0
        · rw [if_pos ha0, if_neg hb0]
          have hmem : (U.orderEmbOfFin hk
              (Fin.mk ((b : ℕ) - 1) (by have := b.isLt; omega)) : Slot) ∈ U :=
            Finset.orderEmbOfFin_mem U hk _
          have hne0 : (U.orderEmbOfFin hk
              (Fin.mk ((b : ℕ) - 1) (by have := b.isLt; omega)) : Slot) ≠ (0 : Slot) := by
            intro hcc
            exact hv (hcc ▸ hmem)
          have hb1 : ((U.orderEmbOfFin hk
              (Fin.mk ((b : ℕ) - 1) (by have := b.isLt; omega)) : Slot) : ℕ) ≠ 0 :=
            fun hc => hne0 (Fin.val_injective hc)
          have hg : (0 : ℕ) < ((U.orderEmbOfFin hk
              (Fin.mk ((b : ℕ) - 1) (by have := b.isLt; omega)) : Slot) : ℕ) := by omega
          exact hg
        · rw [if_neg ha0, if_neg hb0]
          exact (U.orderEmbOfFin hk).strictMono
            (Fin.lt_def.2 (by show ((a : ℕ) - 1) < ((b : ℕ) - 1); omega))
  rw [← hfun]

/-- Циклическая замена `0 ↦ 21` (прыжок через границу влево): позиция
`j < k−1` нового перечисления даёт элемент старой позиции `j + 1`,
последняя позиция `k−1` даёт `21`; занятая позиция `0` выпадает (первая по
`orderEmbOfFin_min0`). -/
theorem orderEmb_wrap01_index (U : Finset Slot) (hu : (0 : Slot) ∈ U)
    (hv : (21 : Slot) ∉ U) {k : ℕ} (hk : U.card = k) (j : Fin k) :
    ((U \ {0} ∪ {21}).orderEmbOfFin ((card_replace U 0 hu 21 hv).trans hk) j : Slot)
      = if h : (j : ℕ) = k - 1 then (21 : Slot)
        else (U.orderEmbOfFin hk
          (Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega)) : Slot) := by
  have hfun : (fun j : Fin k => if h : (j : ℕ) = k - 1 then (21 : Slot)
        else (U.orderEmbOfFin hk
          (Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega)) : Slot))
      = (U \ {0} ∪ {21}).orderEmbOfFin ((card_replace U 0 hu 21 hv).trans hk) := by
    refine Finset.orderEmbOfFin_unique ((card_replace U 0 hu 21 hv).trans hk) ?_ ?_
    · intro j
      by_cases hj : (j : ℕ) = k - 1
      · rw [dif_pos hj]
        simp
      · rw [dif_neg hj]
        have hmem : (U.orderEmbOfFin hk
            (Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega)) : Slot) ∈ U :=
          Finset.orderEmbOfFin_mem U hk _
        have hne0 : (U.orderEmbOfFin hk
            (Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega)) : Slot) ≠ (0 : Slot) := by
          intro hcc
          have hpos2 := (orderEmbOfFin_min0 U hu hk).2 _ hcc
          have hval : (((Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega) : Fin k) : ℕ))
              = (j : ℕ) + 1 := rfl
          have := j.isLt
          omega
        simp only [Finset.mem_union, Finset.mem_sdiff, Finset.mem_singleton]
        exact Or.inl ⟨hmem, hne0⟩
    · intro a b hab
      dsimp only
      have hval : (a : ℕ) < (b : ℕ) := hab
      by_cases haL : (a : ℕ) = k - 1
      · exfalso
        have := b.isLt
        omega
      · by_cases hbL : (b : ℕ) = k - 1
        · rw [dif_neg haL, dif_pos hbL]
          have hmem : (U.orderEmbOfFin hk
              (Fin.mk ((a : ℕ) + 1) (by have := a.isLt; omega)) : Slot) ∈ U :=
            Finset.orderEmbOfFin_mem U hk _
          have hne21 : (U.orderEmbOfFin hk
              (Fin.mk ((a : ℕ) + 1) (by have := a.isLt; omega)) : Slot) ≠ (21 : Slot) := by
            intro hcc
            exact hv (hcc ▸ hmem)
          have hns : numSlots = 22 := rfl
          have hL1 : ((U.orderEmbOfFin hk
              (Fin.mk ((a : ℕ) + 1) (by have := a.isLt; omega)) : Slot) : ℕ) ≠ 21 :=
            fun hc => hne21 (Fin.val_injective hc)
          have his := (U.orderEmbOfFin hk
              (Fin.mk ((a : ℕ) + 1) (by have := a.isLt; omega)) : Slot).isLt
          have hg : ((U.orderEmbOfFin hk
              (Fin.mk ((a : ℕ) + 1) (by have := a.isLt; omega)) : Slot) : ℕ) < 21 := by omega
          exact hg
        · rw [dif_neg haL, dif_neg hbL]
          exact (U.orderEmbOfFin hk).strictMono
            (Fin.lt_def.2 (by show ((a : ℕ) + 1) < ((b : ℕ) + 1); omega))
  rw [← hfun]

/-- Столбец циклического прыжка вправо `21 ↦ 0`: матрица с носителем
`supp x \ {21} ∪ {0}` равна матрице Слейтера с заменённым последним
столбцом (позиция `21`): на месте `0` — столбец сайта `0` (фаза
`ω^{k_i}` от столбца `21`), остальные столбцы сдвинуты на одну позицию
вправо. -/
theorem slaterMat_wrap21_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hu : (21 : Slot) ∈ supp x)
    (hv : (0 : Slot) ∉ supp x) :
    (Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
        psi (modeOf S i)
          (((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
            ((card_replace (supp x) 21 hu 0 hv).trans h) j))
      = Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
          if (j : ℕ) = 0
          then omega ^ (modeOf S i % numSlots)
              * slaterMat S x h i (Fin.mk (S.card - 1) (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨21, hu⟩
                  omega))
          else slaterMat S x h i (Fin.mk ((j : ℕ) - 1) (by
                  have := j.isLt; omega)) := by
  ext i j
  simp only [Matrix.of_apply, slaterMat_entry_emb]
  rw [orderEmb_wrap21_index (supp x) hu hv h j]
  by_cases hj : (j : ℕ) = 0
  · rw [if_pos hj, if_pos hj]
    have hlast : ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have h1 : 0 < S.card := by
          rw [← h]; exact Finset.card_pos.mpr ⟨21, hu⟩
        omega)) : Slot) = 21 :=
      (orderEmbOfFin_max21 (supp x) hu h).1
    rw [hlast]
    have heq : ((21 : Slot) + 1) = (0 : Slot) := rfl
    rw [← heq, psi_shift]
  · rw [if_neg hj, if_neg hj]

/-- Столбец циклического прыжка влево `0 ↦ 21`: матрица с носителем
`supp x \ {0} ∪ {21}` равна матрице Слейтера с заменённым первым столбцом
(позиция `0`): на последнем месте `k−1` — столбец сайта `21` (фаза
`ω^{−k_i}` от столбца `0`), остальные столбцы сдвинуты на одну позицию
влево. -/
theorem slaterMat_wrap01_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hu : (0 : Slot) ∈ supp x)
    (hv : (21 : Slot) ∉ supp x) :
    (Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
        psi (modeOf S i)
          (((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
            ((card_replace (supp x) 0 hu 21 hv).trans h) j))
      = Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
          if hj : (j : ℕ) = S.card - 1
          then omega ^ (numSlots - modeOf S i % numSlots)
              * slaterMat S x h i (Fin.mk 0 (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨0, hu⟩
                  exact h1))
          else slaterMat S x h i (Fin.mk ((j : ℕ) + 1) (by
                  have := j.isLt; omega)) := by
  ext i j
  simp only [Matrix.of_apply, slaterMat_entry_emb]
  rw [orderEmb_wrap01_index (supp x) hu hv h j]
  by_cases hj : (j : ℕ) = S.card - 1
  · rw [dif_pos hj, dif_pos hj]
    have hzero : ((supp x).orderEmbOfFin h (Fin.mk 0 (by
        have h1 : 0 < S.card := by
          rw [← h]; exact Finset.card_pos.mpr ⟨0, hu⟩
        exact h1)) : Slot) = 0 :=
      (orderEmbOfFin_min0 (supp x) hu h).1
    rw [hzero]
    have heq : ((0 : Slot) - 1) = (21 : Slot) := rfl
    rw [← heq, psi_pred_shift]
  · rw [dif_neg hj, dif_neg hj]

/-! ## Циклические det-леммы: знак перестановки столбцов -/

private theorem neg_one_pow_two_mul (n : ℕ) : ((-1 : ℂ) ^ (2 * n)) = 1 := by
  rw [pow_mul, pow_two]
  norm_num

/-- Циклический прыжок вправо `21 ↦ 0` (определитель): если `M'` получена
из `M` заменой последнего столбца масштабированным столбцом сайта `0`,
поставленным на позицию `0` (остальные столбцы сдвинуты вправо), то
`det M' = (−1)^n · Σ_i d_i · M_{i,last} · C_{i,last}` — знак циклической
перестановки столбцов. -/
theorem det_wrap_right {n : ℕ} (M M' : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (d : Fin n.succ → ℂ)
    (h : ∀ i j, M' i j = if j = 0 then d i * M i (Fin.last n)
      else M i (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega))) :
    M'.det = (-1) ^ n * ∑ i, d i * M i (Fin.last n) * cof M i (Fin.last n) := by
  have hdet : M'.det = ∑ i, M' i 0 * cof M' i 0 := by
    rw [Matrix.det_succ_column M' 0]
    exact Finset.sum_congr rfl fun i _ => by rw [cof]; ring
  have hcol : ∀ i : Fin n.succ, M' i 0 = d i * M i (Fin.last n) := by
    intro i
    rw [h i 0, if_pos rfl]
  have hcof : ∀ i : Fin n.succ, cof M' i 0 = (-1) ^ n * cof M i (Fin.last n) := by
    intro i
    rw [cof, cof]
    have hsub : M'.submatrix i.succAbove (0 : Fin n.succ).succAbove
        = M.submatrix i.succAbove (Fin.last n).succAbove := by
      ext a b
      simp only [Matrix.submatrix_apply]
      rw [Fin.succAbove_zero, Fin.succAbove_last]
      rw [h _ (Fin.succ b), if_neg (Fin.succ_ne_zero b)]
      rfl
    rw [hsub]
    have hzero : ((0 : Fin n.succ) : ℕ) = 0 := rfl
    have hlastv : ((Fin.last n : Fin n.succ) : ℕ) = n := rfl
    have hpexp : n + ((i : ℕ) + n) = (i : ℕ) + (n + n) := by omega
    have hsign : ((-1 : ℂ) ^ ((i : ℕ) + ((0 : Fin n.succ) : ℕ)))
        = (-1 : ℂ) ^ n * ((-1 : ℂ) ^ ((i : ℕ) + ((Fin.last n : Fin n.succ) : ℕ))) := by
      rw [hzero, Nat.add_zero, hlastv, ← pow_add, hpexp, ← Nat.two_mul, pow_add,
        neg_one_pow_two_mul, mul_one]
    rw [hsign]
    ring
  rw [hdet, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [hcol i, hcof i]
  ring

/-- Циклический прыжок влево `0 ↦ 21` (определитель): если `M'` получена
из `M` заменой первого столбца масштабированным столбцом сайта `21`,
поставленным на последнюю позицию (остальные столбцы сдвинуты влево), то
`det M' = (−1)^n · Σ_i d_i · M_{i,0} · C_{i,0}` — знак циклической
перестановки столбцов. -/
theorem det_wrap_left {n : ℕ} (M M' : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (d : Fin n.succ → ℂ)
    (h : ∀ i j, M' i j = if hj : j = Fin.last n then d i * M i 0
      else M i (Fin.mk ((j : ℕ) + 1) (by
              have hn : ¬((j : ℕ) = n) := fun hc =>
                hj (Fin.ext (by
                  rw [show ((Fin.last n : Fin n.succ) : ℕ) = n from rfl]
                  exact hc))
              have := j.isLt; omega))) :
    M'.det = (-1) ^ n * ∑ i, d i * M i 0 * cof M i 0 := by
  have hdet : M'.det = ∑ i, M' i (Fin.last n) * cof M' i (Fin.last n) := by
    rw [Matrix.det_succ_column M' (Fin.last n)]
    exact Finset.sum_congr rfl fun i _ => by rw [cof]; ring
  have hcol : ∀ i : Fin n.succ, M' i (Fin.last n) = d i * M i 0 := by
    intro i
    rw [h i (Fin.last n), dif_pos rfl]
  have hcof : ∀ i : Fin n.succ, cof M' i (Fin.last n) = (-1) ^ n * cof M i 0 := by
    intro i
    rw [cof, cof]
    have hsub : M'.submatrix i.succAbove (Fin.last n).succAbove
        = M.submatrix i.succAbove (0 : Fin n.succ).succAbove := by
      ext a b
      simp only [Matrix.submatrix_apply]
      rw [Fin.succAbove_last, Fin.succAbove_zero]
      rw [h _ (Fin.castSucc b)]
      rw [dif_neg (by
        intro hc
        have hcs : ((Fin.castSucc b : Fin n.succ) : ℕ) = (b : ℕ) := rfl
        have hlv : ((Fin.last n : Fin n.succ) : ℕ) = n := rfl
        have hvc := congrArg Fin.val hc
        have := b.isLt
        omega)]
      rfl
    rw [hsub]
    have hlastv : ((Fin.last n : Fin n.succ) : ℕ) = n := rfl
    have hzero : ((0 : Fin n.succ) : ℕ) = 0 := rfl
    have hsign : ((-1 : ℂ) ^ ((i : ℕ) + ((Fin.last n : Fin n.succ) : ℕ)))
        = (-1 : ℂ) ^ n * ((-1 : ℂ) ^ ((i : ℕ) + ((0 : Fin n.succ) : ℕ))) := by
      rw [hlastv, hzero, pow_add, Nat.add_zero]
      ring
    rw [hsign]
    ring
  rw [hdet, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [hcol i, hcof i]
  ring

/-! ## Stage 3: цели — диагональность A·Ψ_S, чётные секторы, Коши–Бине -/

/-- Скалярное произведение состояний: `⟨f, g⟩ = Σ_x conj(f x)·g x`. -/
noncomputable def slaterIP (f g : Cfg → ℂ) : ℂ := ∑ x, star (f x) * g x

/-- Антипериодическая фаза твиста: `ζ = exp(πi/22)`, `ζ^{22} = −1`. -/
noncomputable def zeta : ℂ := Complex.exp (Real.pi * Complex.I / numSlots)

/-- Твистованые моды: `ψ̃_k(u) = ζ^u·ψ_k(u)` — делают оператор цепочки
диагональным во ВСЕХ секторах, включая чётные (дополнительный множитель
`ζ^{±1}` на границе 21↦0 / 0↦21 компенсирует знак `(−1)^{k−1}`). -/
noncomputable def psiTwist (k : ℕ) (u : Slot) : ℂ := zeta ^ (u : ℕ) * psi k u

/-! ### Твист: три базовые леммы (антипериодичность, сдвиг, граничный сдвиг) -/

/-- Антипериодичность твиста: `ζ^{22} = −1` (антипериодическое условие
на замыкании цикла; именно оно даёт механизм паритета в чётных секторах). -/
theorem zeta_pow_numSlots : zeta ^ numSlots = -1 := by
  unfold zeta
  rw [show numSlots = 22 from rfl, ← Complex.exp_nat_mul]
  have heq : ((22 : ℕ) : ℂ) * (Real.pi * Complex.I / (22 : ℕ)) = Real.pi * Complex.I := by
    field_simp
  rw [heq]
  exact Complex.exp_pi_mul_I

/-- Сдвиг твистованных мод вдали от замыкания (`u ≠ 21`):
`ψ̃_k(u+1) = ζ · ω^k · ψ̃_k(u)` — фаза `ζ` накапливается равномерно. -/
theorem psiTwist_shift (k : ℕ) (u : Slot) (hu : (u : ℕ) + 1 < numSlots) :
    psiTwist k (u + 1) = zeta * omega ^ (k % numSlots) * psiTwist k u := by
  unfold psiTwist
  rw [val_suc, Nat.mod_eq_of_lt hu, psi_shift, pow_succ]
  ring

/-- Сдвиг твистованных мод через границу `21 ↦ 0`: лишний знак `−1`
(из-за антипериодичности `ζ^{22} = −1` сдвиг `ψ̃` НЕ равномерен по циклу:
`ψ̃_k(0) = −ζ · ω^k · ψ̃_k(21)`). Именно этот минус и есть механизм
паритета: у нетвистованных мод знак границы `(−1)^{k−1}`, у твистованных
он умножается на `−1` и становится `(−1)^k`. -/
theorem psiTwist_shift_wrap (k : ℕ) :
    psiTwist k ((21 : Slot) + 1)
      = -zeta * omega ^ (k % numSlots) * psiTwist k (21 : Slot) := by
  unfold psiTwist
  have hnew : ((21 : Slot) + 1 : Slot) = 0 := by decide
  have h21v : ((21 : Slot) : ℕ) = 21 := rfl
  have h0v : ((0 : Slot) : ℕ) = 0 := rfl
  rw [hnew, h0v, h21v, pow_zero, one_mul]
  have hshift0 : psi k (0 : Slot) = omega ^ (k % numSlots) * psi k (21 : Slot) := by
    rw [← hnew]
    exact psi_shift k 21
  rw [hshift0]
  have hz21 : zeta * zeta ^ 21 = -1 := by
    rw [← pow_succ', show ((21 : ℕ) + 1) = numSlots from rfl]
    exact zeta_pow_numSlots
  have hz : (-zeta) * zeta ^ 21 = 1 := by rw [neg_mul, hz21, neg_neg]
  calc omega ^ (k % numSlots) * psi k (21 : Slot)
      = ((-zeta) * zeta ^ 21) * (omega ^ (k % numSlots) * psi k (21 : Slot)) := by
        rw [hz, one_mul]
    _ = -zeta * omega ^ (k % numSlots) * (zeta ^ 21 * psi k (21 : Slot)) := by ring

/-! ## Hop-вклады: носитель при перескоке и разложения определителя -/

/-- Версия `det_wrap_right` с условием на натуральное значение индекса
(удобна для склейки с матричными леммами, использующими `(j : ℕ) = 0`):
знак циклической перестановки `(−1)^n`. -/
theorem det_wrap_right_fin {n : ℕ} (M M' : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (d : Fin n.succ → ℂ)
    (h : ∀ i j, M' i j = if (j : ℕ) = 0 then d i * M i (Fin.mk n (by omega))
      else M i (Fin.mk ((j : ℕ) - 1) (by have := j.isLt; omega))) :
    M'.det = (-1) ^ n * ∑ i, d i * M i (Fin.mk n (by omega))
      * cof M i (Fin.mk n (by omega)) := by
  refine det_wrap_right M M' d ?_
  intro i j
  by_cases hj : (j : ℕ) = 0
  · rw [if_pos (show (j : Fin n.succ) = 0 from Fin.val_injective hj)]
    have h1 := h i j
    rw [if_pos hj] at h1
    exact h1
  · rw [if_neg (show ¬((j : Fin n.succ) = 0) from fun hc => hj (congrArg Fin.val hc))]
    have h1 := h i j
    rw [if_neg hj] at h1
    exact h1

/-- Версия `det_wrap_left` с условием на натуральное значение индекса
(удобна для склейки с матричными леммами, использующими `(j : ℕ) = n`):
знак циклической перестановки `(−1)^n`. -/
theorem det_wrap_left_fin {n : ℕ} (M M' : Matrix (Fin n.succ) (Fin n.succ) ℂ)
    (d : Fin n.succ → ℂ)
    (h : ∀ i j, M' i j = if hj : (j : ℕ) = n then d i * M i (Fin.mk 0 (by omega))
      else M i (Fin.mk ((j : ℕ) + 1) (by have := j.isLt; omega))) :
    M'.det = (-1) ^ n * ∑ i, d i * M i (Fin.mk 0 (by omega))
      * cof M i (Fin.mk 0 (by omega)) := by
  refine det_wrap_left M M' d ?_
  intro i j
  by_cases hj : (j : ℕ) = n
  · rw [dif_pos (show (j : Fin n.succ) = Fin.last n from Fin.ext hj)]
    have h1 := h i j
    rw [dif_pos hj] at h1
    exact h1
  · rw [dif_neg (show ¬((j : Fin n.succ) = Fin.last n) from fun hc => hj (congrArg Fin.val hc))]
    have h1 := h i j
    rw [dif_neg hj] at h1
    exact h1

/-- Симметричность переворота пары: `flipTwo s t x = flipTwo t s x`. -/
theorem flipTwo_comm (s t : Slot) (x : Cfg) : flipTwo s t x = flipTwo t s x := by
  funext u
  by_cases hu : u = s
  · simp [flipTwo, hu]
  · by_cases hu2 : u = t
    · simp [flipTwo, hu2]
    · simp [flipTwo, hu, hu2]

/-- Носитель при перевороте пары битов `(s, t)`: если `x s = 1`, `x t = 0`,
`s ≠ t`, то занятый сайт `s` заменяется свободным `t`. -/
theorem supp_flipTwo_swap (s t : Slot) (hst : s ≠ t) (x : Cfg) (hs : x s = 1)
    (ht : x t = 0) :
    supp (flipTwo s t x) = (supp x \ {s} : Finset Slot) ∪ {t} := by
  unfold supp
  ext u
  simp only [Finset.mem_filter, Finset.mem_univ, Finset.mem_union, Finset.mem_sdiff,
    Finset.mem_singleton]
  by_cases hu : u = s
  · have hfl : flipTwo s t x s = 1 - x s := by simp [flipTwo]
    rw [hu, hfl, hs]
    simp [hst]
  · by_cases hu2 : u = t
    · have hfl : flipTwo s t x t = 1 - x t := by simp [flipTwo]
      rw [hu2, hfl, ht]
      simp
    · have hsame : flipTwo s t x u = x u := by
        simp only [flipTwo, if_neg (not_or.mpr ⟨hu, hu2⟩)]
      rw [hsame]
      simp [hu, hu2]

/-- Занятость бита из принадлежности носителю. -/
theorem mem_supp (x : Cfg) (u : Slot) (hu : u ∈ supp x) : x u = 1 := by
  unfold supp at hu
  simpa using hu

/-- Свободность бита из непринадлежности носителю. -/
theorem not_mem_supp (x : Cfg) (u : Slot) (hu : u ∉ supp x) : x u = 0 := by
  rcases bit_cases (x u) with hb | hb
  · exact hb
  · exact absurd (by unfold supp; simpa using hb) hu

/-- **Значение Ψ_S на конфигурации с перескоком вправо** `u₀ ↦ v = u₀+1`
(без цикла 21 ↦ 0): разложение по столбцу `j₀` (позиция `u₀`),
коэффициент `ω^{k_i}`. -/
theorem slater_hop_succ (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀ : u₀ ∈ supp x) (v : Slot) (hv : v ∉ supp x) (hadj : v = u₀ + 1)
    (hnb : (v : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    slater S (flipTwo u₀ v x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j).det := by
  have hsupp : supp (flipTwo u₀ v x) = ((supp x \ {u₀} : Finset Slot) ∪ {v}) :=
    supp_flipTwo_swap u₀ v (by intro hc; exact hv (hc ▸ hU₀)) x (mem_supp _ _ hU₀)
      (not_mem_supp _ _ hv)
  have hc : (supp (flipTwo u₀ v x)).card = S.card := by
    rw [hsupp]
    exact (card_replace (supp x) u₀ hU₀ v hv).trans h
  have hproj : ∀ j : Fin S.card,
      ((supp (flipTwo u₀ v x)).orderEmbOfFin hc j : Slot)
        = (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀ v hv).trans h) j : Slot) := by
    intro j
    have hf : (fun j' : Fin S.card =>
          ((supp (flipTwo u₀ v x)).orderEmbOfFin hc j' : Slot))
        = ((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀ v hv).trans h) := by
      refine Finset.orderEmbOfFin_unique
        ((card_replace (supp x) u₀ hU₀ v hv).trans h) ?_ ?_
      · intro j'
        rw [← hsupp]
        exact Finset.orderEmbOfFin_mem _ _ _
      · intro a b hab
        exact ((supp (flipTwo u₀ v x)).orderEmbOfFin hc).strictMono hab
    exact congrFun hf j
  have hmat' : slaterMat S (flipTwo u₀ v x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psi (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMat_entry_emb]
    rw [hproj j]
  calc slater S (flipTwo u₀ v x)
      = (slaterMat S (flipTwo u₀ v x) hc).det := slater_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psi (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j).det :=
        congrArg Matrix.det
          (slaterMat_replace_succ_matrix S x h u₀ hU₀ v hv hadj hnb j₀ hj₀)

/-- **Значение Ψ_S на конфигурации с перескоком влево** `u₀ ↦ v = u₀−1`
(без цикла 0 ↦ 21): коэффициент `ω^{−k_i}`. -/
theorem slater_hop_pred (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀ : u₀ ∈ supp x) (v : Slot) (hv : v ∉ supp x) (hadj : v = u₀ - 1)
    (hnb : (u₀ : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    slater S (flipTwo u₀ v x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j).det := by
  have hsupp : supp (flipTwo u₀ v x) = ((supp x \ {u₀} : Finset Slot) ∪ {v}) :=
    supp_flipTwo_swap u₀ v (by intro hc; exact hv (hc ▸ hU₀)) x (mem_supp _ _ hU₀)
      (not_mem_supp _ _ hv)
  have hc : (supp (flipTwo u₀ v x)).card = S.card := by
    rw [hsupp]
    exact (card_replace (supp x) u₀ hU₀ v hv).trans h
  have hproj : ∀ j : Fin S.card,
      ((supp (flipTwo u₀ v x)).orderEmbOfFin hc j : Slot)
        = (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀ v hv).trans h) j : Slot) := by
    intro j
    have hf : (fun j' : Fin S.card =>
          ((supp (flipTwo u₀ v x)).orderEmbOfFin hc j' : Slot))
        = ((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀ v hv).trans h) := by
      refine Finset.orderEmbOfFin_unique
        ((card_replace (supp x) u₀ hU₀ v hv).trans h) ?_ ?_
      · intro j'
        rw [← hsupp]
        exact Finset.orderEmbOfFin_mem _ _ _
      · intro a b hab
        exact ((supp (flipTwo u₀ v x)).orderEmbOfFin hc).strictMono hab
    exact congrFun hf j
  have hmat' : slaterMat S (flipTwo u₀ v x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psi (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMat_entry_emb]
    rw [hproj j]
  calc slater S (flipTwo u₀ v x)
      = (slaterMat S (flipTwo u₀ v x) hc).det := slater_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psi (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j).det :=
        congrArg Matrix.det
          (slaterMat_replace_pred_matrix S x h u₀ hU₀ v hv hadj hnb j₀ hj₀)

/-- Вклад ребра `s` (перескок вправо `s ↦ s+1`, без цикла 21 ↦ 0):
`(bondTerm s · Ψ_S)(x) = 2·det M(j₀ ← ω^k·M_{·,j₀})` — определитель матрицы
Слейтера со столбцом `j₀` (позиция `s`), поточечно умноженным на `ω^{k_i}`,
при `x s = 1`, `x (s+1) = 0`. -/
theorem bondTerm_hop_succ (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h0 : x (s + 1) = 0) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀
          else slaterMat S x h i j).det := by
  rw [mulVec_bondTerm, if_pos (show x s ≠ x (s + 1) from by rw [h1, h0]; exact one_ne_zero),
    slater_hop_succ S x h s (by unfold supp; simpa [h1] using Finset.mem_univ s)
      (s + 1 : Slot)
      (by intro hc
          have hmem := mem_supp _ _ hc
          rw [h0] at hmem
          exact zero_ne_one hmem)
      rfl hnb j₀ hj₀]

/-- Для внутреннего ребра (`s + 1 < 22`) сосед слева от `s+1` — это `s`:
`(s+1) − 1 = s`. -/
theorem slot_pred_suc (s : Slot) (hs : (s : ℕ) + 1 < numSlots) :
    ((s + 1 : Slot) - 1 : Slot) = s := by
  apply Fin.val_injective
  have h22 : numSlots = 22 := rfl
  have hv1 : (((s + 1 : Slot) - 1 : Slot) : ℕ) = (((s + 1 : Slot) : ℕ) + 21) % numSlots :=
    val_pred (s + 1 : Slot)
  have hv2 : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + 1) % numSlots := val_suc s
  have e1 : (s : ℕ) + 1 + 21 = (s : ℕ) + numSlots := by
    show (s : ℕ) + 22 = (s : ℕ) + 22
    omega
  rw [hv1, hv2, Nat.mod_eq_of_lt hs, e1,
    Nat.add_mod_right (s : ℕ) numSlots, Nat.mod_eq_of_lt s.isLt]

/-- Вклад ребра `s` (перескок влево `s+1 ↦ s`, без цикла 0 ↦ 21):
`(bondTerm s · Ψ_S)(x) = 2·det M(j₁ ← ω^{−k}·M_{·,j₁})` при
`x (s+1) = 1`, `x s = 0`, где `j₁` — позиция `s+1`. -/
theorem bondTerm_hop_pred (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x (s + 1) = 1) (h0 : x s = 0) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₁ : Fin S.card) (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if j = j₁ then omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₁
          else slaterMat S x h i j).det := by
  have hs21 : (s : ℕ) + 1 < numSlots := by
    by_contra hcon
    have hlt := s.isLt
    have heq : (s : ℕ) + 1 = numSlots := by omega
    have hv : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + 1) % numSlots := val_suc s
    rw [heq, Nat.mod_self] at hv
    exact hnb hv
  rw [mulVec_bondTerm,
    if_pos (show x s ≠ x (s + 1) from by rw [h0, h1]; exact fun hc => one_ne_zero hc.symm),
    flipTwo_comm s (s + 1) x,
    slater_hop_pred S x h (s + 1 : Slot)
      (by unfold supp; simpa [h1] using Finset.mem_univ (s + 1 : Slot))
      s
      (by intro hc
          have hmem := mem_supp _ _ hc
          rw [h0] at hmem
          exact zero_ne_one hmem)
      (slot_pred_suc s hs21).symm hnb j₁ hj₁]

/-! ## Твист: граничные леммы для чётных секторов -/

/-- Сдвиг твистованной моды влево через границу `0 ↦ 21`: лишний знак `−1`
(обратная форма `psiTwist_shift_wrap`). -/
theorem psiTwist_pred_wrap (k : ℕ) :
    psiTwist k (21 : Slot)
      = (-zeta)⁻¹ * (omega ^ (k % numSlots))⁻¹ * psiTwist k (0 : Slot) := by
  have h := psiTwist_shift_wrap k
  have hz : (-zeta) * omega ^ (k % numSlots) ≠ 0 := by
    refine mul_ne_zero ?_ ?_
    · intro hc
      rw [neg_eq_zero] at hc
      unfold zeta at hc
      exact Complex.exp_ne_zero _ hc
    · intro hc
      have hpow : omega ^ (k % numSlots) * omega ^ (numSlots - k % numSlots) = 1 := by
        have hlt : k % numSlots < numSlots := Nat.mod_lt _ (by norm_num [numSlots])
        rw [← pow_add, Nat.add_sub_cancel' hlt.le, omega_pow_numSlots]
      rw [hc, zero_mul] at hpow
      exact zero_ne_one hpow
  calc psiTwist k (21 : Slot)
      = ((-zeta) * omega ^ (k % numSlots))⁻¹
          * ((-zeta) * omega ^ (k % numSlots)) * psiTwist k (21 : Slot) := by
        rw [inv_mul_cancel₀ hz, one_mul]
    _ = ((-zeta) * omega ^ (k % numSlots))⁻¹ * psiTwist k ((21 : Slot) + 1) := by
        rw [h, mul_assoc]
    _ = ((-zeta) * omega ^ (k % numSlots))⁻¹ * psiTwist k (0 : Slot) := by
        rw [show ((21 : Slot) + 1) = (0 : Slot) from rfl]
    _ = (-zeta)⁻¹ * (omega ^ (k % numSlots))⁻¹ * psiTwist k (0 : Slot) := by
        rw [mul_inv]

/-- **Цель Stage 3 (гипотеза Odd).** Оператор прыжков цепочки
`A = Σ_s bondTerm s` диагонализуется слейтеровскими определителями:
при нечётном `|S|`
`A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S` на всех конфигурациях веса `|S|`
(без требования `supp x = S`). Все детерминантные кирпичи готовы:
scaled_column_det, wrong_cofactor_zero, row_cofactor_sum,
slaterMat_replace_succ/pred_matrix, det_replace_column,
det_wrap_right/left (знак `(−1)^n = +1` при нечётных). -/
theorem slater_diag_odd (S : Finset Slot) (hOdd : Odd S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slater S y)
      = (∑ i : Fin S.card, (eps (modeOf S i) : ℂ)) • (fun y => slater S y) := by
  sorry

/-- Слейтеровские определители с твистованными модами. -/
noncomputable def slaterTwist (S : Finset Slot) (x : Cfg) : ℂ :=
  if h : (supp x).card = S.card then
    (Matrix.of fun i j => psiTwist (modeOf S i)
      ((supp x).orderEmbOfFin h j)).det
  else 0

/-! ## Твистованные матрицы: граничные леммы для чётных секторов -/

/-- Твистованная матрица Слейтера: строка `i` — мода `modeOf S i`,
столбец `j` — сайт `(supp x).orderEmbOfFin h j`. -/
noncomputable def slaterMatTwist (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card) :
    Matrix (Fin S.card) (Fin S.card) ℂ :=
  Matrix.of fun i j => psiTwist (modeOf S i) ((supp x).orderEmbOfFin h j)

/-- Твистованный определитель — определитель твистованной матрицы. -/
theorem slaterTwist_eq_det (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card) :
    slaterTwist S x = (slaterMatTwist S x h).det := by
  rw [slaterTwist, dif_pos h]
  rfl

/-- Столбец циклического прыжка вправо `21 ↦ 0` в твистованном базисе:
на месте `0` — столбец сайта `0 = ζ^{0}ψ(0)`, равный `(−ζ)·ω^{k_i}·ψ̃_{k_i}(21)`
(лишний минус из антипериодичности, `psiTwist_shift_wrap`), остальные
столбцы сдвинуты вправо. Именно этот множитель `−ζ` вместе со знаком
циклической перестановки `(−1)^{k−1}` из `det_wrap_right_fin` даёт в чётных
секторах суммарный знак `(−1)^{k−1}·(−1) = (−1)^k = +1`. -/
theorem slaterMatTwist_wrap21_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hu : (21 : Slot) ∈ supp x)
    (hv : (0 : Slot) ∉ supp x) :
    (Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
        psiTwist (modeOf S i)
          (((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
            ((card_replace (supp x) 21 hu 0 hv).trans h) j))
      = Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
          if (j : ℕ) = 0
          then (-zeta) * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i (Fin.mk (S.card - 1) (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨21, hu⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) - 1) (by
                  have := j.isLt; omega)) := by
  ext i j
  simp only [Matrix.of_apply, slaterMatTwist]
  rw [orderEmb_wrap21_index (supp x) hu hv h j]
  by_cases hj : (j : ℕ) = 0
  · rw [if_pos hj, if_pos hj]
    have hlast : ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have h1 : 0 < S.card := by
          rw [← h]; exact Finset.card_pos.mpr ⟨21, hu⟩
        omega)) : Slot) = 21 :=
      (orderEmbOfFin_max21 (supp x) hu h).1
    rw [hlast]
    exact psiTwist_shift_wrap (modeOf S i)
  · rw [if_neg hj, if_neg hj]

/-- Столбец циклического прыжка влево `0 ↦ 21` в твистованном базисе:
на последнем месте — столбец сайта `21`, равный `(−ζ)^{−1}·ω^{−k_i}·ψ̃_{k_i}(0)`
(`psiTwist_pred_wrap`), остальные столбцы сдвинуты влево. -/
theorem slaterMatTwist_wrap01_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hu : (0 : Slot) ∈ supp x)
    (hv : (21 : Slot) ∉ supp x) :
    (Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
        psiTwist (modeOf S i)
          (((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
            ((card_replace (supp x) 0 hu 21 hv).trans h) j))
      = Matrix.of fun (i : Fin S.card) (j : Fin S.card) =>
          if hj : (j : ℕ) = S.card - 1
          then (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i (Fin.mk 0 (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨0, hu⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) + 1) (by
                  have := j.isLt; omega)) := by
  ext i j
  simp only [Matrix.of_apply, slaterMatTwist]
  rw [orderEmb_wrap01_index (supp x) hu hv h j]
  by_cases hj : (j : ℕ) = S.card - 1
  · rw [dif_pos hj, dif_pos hj]
    have hzero : ((supp x).orderEmbOfFin h (Fin.mk 0 (by
        have h1 : 0 < S.card := by
          rw [← h]; exact Finset.card_pos.mpr ⟨0, hu⟩
        omega)) : Slot) = 0 :=
      (orderEmbOfFin_min0 (supp x) hu h).1
    rw [hzero]
    exact psiTwist_pred_wrap (modeOf S i)
  · rw [dif_neg hj, dif_neg hj]

/-- **Цель для чётных секторов (твист).** С твистованными модами
`ψ̃_k(u) = ζ^u·ψ_k(u)` (`ζ^{22} = −1`, антипериодическое условие) оператор
прыжков диагонален и в чётных секторах: знак `(−1)^{k−1}` границы
компенсируется фазой `ζ^{±1}`. -/
theorem slater_diag_even_twist (S : Finset Slot) (hEven : Even S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slaterTwist S y)
      = (∑ i : Fin S.card, (eps (modeOf S i) : ℂ)) • (fun y => slaterTwist S y) := by
  sorry

/-- **Цель: ортогональность Слейтера (Коши–Бине).** Для наборов мод
одинаковой мощности `⟨Ψ_S, Ψ_T⟩ = δ_{S,T}`: при `S = T` норма 1, при
`S ≠ T` — нуль. Сводится к Коши–Бине для прямоугольных матриц мод
(ортонормальность строк `ψ_k` — Ortho.lean); леммы Коши–Бине в mathlib
нет. -/
theorem slater_orth (S T : Finset Slot) (hST : S.card = T.card) :
    slaterIP (fun y => slater S y) (fun y => slater T y)
      = if S = T then 1 else 0 := by
  sorry

end Septinal
