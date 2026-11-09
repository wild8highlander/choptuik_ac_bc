/-
Septinal YM · Этап 4d: сборка `slater_diag_odd`.

Схема: mulVec-расщепление суммы операторов; разбор рёбер `s` по типу
(заблокированное / succ-активное / pred-активное); вклад succ-ребра —
`2·D⁺(j_s)` (через `cofG_det_updateCol`), pred-ребра — `2·D⁻(j_{s+1})`;
«недостающие» члены занятых соседних пар обнуляются (два равных столбца);
свёртка `Σ_j Σ_i d_i·M_{ij}·C_{ij} = (Σ_i d_i)·det M`; связка с `eps`.
-/
import SeptinalYM.Stage4c

namespace Septinal
open Finset BigOperators Matrix

/-! ## 4d-0: mulVec-расщепление суммы -/

/-- Перестановка порядка суммирования для матричных двойных сумм. -/
theorem matrix_sum_comm {m n : Type*} [Fintype m] [Fintype n] {α : Type*}
    [AddCommMonoid α] (s : Finset n) (M : m → n → α) :
    (∑ j : m, ∑ i ∈ s, M j i) = ∑ i ∈ s, ∑ j : m, M j i :=
  Finset.sum_comm

/-- Расщепление mulVec по конечной сумме операторов. -/
theorem mulVec_sum {m n : Type*} [Fintype n] [DecidableEq n] {α : Type*}
    [NonUnitalNonAssocSemiring α] [Fintype m] {ι : Type*} [Fintype ι] (s : Finset ι)
    (M : ι → Matrix m n α) (v : n → α) :
    ((∑ i ∈ s, M i) *ᵥ v) = ∑ i ∈ s, (M i *ᵥ v) := by
  funext x
  have hl : ((∑ i ∈ s, M i) *ᵥ v) x = ∑ j, ∑ i ∈ s, M i x j * v j := by
    simp only [Matrix.mulVec, dotProduct, Matrix.sum_apply, Finset.sum_mul]
  have hr : (∑ i ∈ s, M i *ᵥ v) x = ∑ i ∈ s, ∑ j, M i x j * v j := by
    simp [Matrix.mulVec, dotProduct, Finset.sum_mul]
  rw [hl, hr]
  exact matrix_sum_comm s (fun j i => M i x j * v j)

/-! ## 4d-1: вклады рёбер в кофакторной форме -/

/-- Вклад succ-активного ребра (`x s = 1`, `x (s+1) = 0`, без цикла):
`2·Σ_i ω^{k_i}·M_{i,j₀}·C_{i,j₀}` — разложение по столбцу `j₀`. -/
theorem bondTerm_succ_Dplus (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h0 : x (s + 1) = 0) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i j₀ * cofG (slaterMat S x h) i j₀ := by
  have heq : (Matrix.of fun (i j : Fin S.card) =>
      if j = j₀ then omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀
      else slaterMat S x h i j)
      = (slaterMat S x h).updateCol j₀
          (fun i => omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀) := by
    ext i j
    by_cases hj : j = j₀
    · subst hj; simp [Matrix.updateCol_apply, Matrix.of_apply]
    · simp [Matrix.updateCol_apply, Matrix.of_apply, hj]
  rw [bondTerm_hop_succ S x h s h1 h0 hnb j₀ hj₀, heq, cofG_det_updateCol]

/-- Вклад pred-активного ребра (`x (s+1) = 1`, `x s = 0`, без цикла):
`2·Σ_i ω^{−k_i}·M_{i,j₁}·C_{i,j₁}` — разложение по столбцу `j₁`. -/
theorem bondTerm_pred_Dminus (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x (s + 1) = 1) (h0 : x s = 0) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₁ : Fin S.card) (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i j₁ * cofG (slaterMat S x h) i j₁ := by
  have heq : (Matrix.of fun (i j : Fin S.card) =>
      if j = j₁ then omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₁
      else slaterMat S x h i j)
      = (slaterMat S x h).updateCol j₁
          (fun i => omega ^ (numSlots - modeOf S i % numSlots) * slaterMat S x h i j₁) := by
    ext i j
    by_cases hj : j = j₁
    · subst hj; simp [Matrix.updateCol_apply, Matrix.of_apply]
    · simp [Matrix.updateCol_apply, Matrix.of_apply, hj]
  rw [bondTerm_hop_pred S x h s h1 h0 hnb j₁ hj₁, heq, cofG_det_updateCol]

/-! ## 4d-2: обнуление занятых пар -/

/-- `ω^{22−k} · ω^{k} = 1` в мостовой форме pred-вкладов (без внешнего `%`). -/
theorem omega_mul_inv_bridge (k : ℕ) :
    omega ^ (numSlots - k % numSlots) * omega ^ (k % numSlots) = 1 := by
  have h22 : numSlots = 22 := rfl
  have hlt : k % numSlots < numSlots := by
    rw [h22]; exact Nat.mod_lt k (by norm_num)
  rw [← pow_add]
  have hsum : (numSlots - k % numSlots) + k % numSlots = numSlots := by
    rw [h22]; omega
  rw [hsum, omega_pow_numSlots]

/-- Занятая succ-пара (`x s = 1`, `x (s+1) = 1`, без цикла): масштабированный
столбец `j₀` совпадает со столбцом `j₁` — `D⁺(j₀) = 0`. -/
theorem dplus_zero_of_pair (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h2 : x (s + 1) = 1) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (∑ i, omega ^ (modeOf S i % numSlots)
        * slaterMat S x h i j₀ * cofG (slaterMat S x h) i j₀) = 0 := by
  have hs : s ∈ supp x := by rw [← hj₀]; exact Finset.orderEmbOfFin_mem _ _ _
  have hs1 : (s + 1 : Slot) ∈ supp x := by
    rw [← hj₁]; exact Finset.orderEmbOfFin_mem _ _ _
  have hne : j₀ ≠ j₁ := by
    intro hc
    exfalso
    have h22 : numSlots = 22 := rfl
    have hlt : (s : ℕ) < 22 := by
      have := s.isLt
      omega
    have hmod : ((s : ℕ) + 1) % numSlots = ((s : ℕ) + 1) % 22 := by
      congr 1
    have hpos : (s : ℕ) ≠ ((s : ℕ) + 1) % numSlots := by
      have hlink : ((s : ℕ) + 1) % numSlots = ((s : ℕ) + 1) % 22 := hmod
      omega
    have hslot : ((supp x).orderEmbOfFin h j₀ : Slot)
        = ((supp x).orderEmbOfFin h j₁ : Slot) := by
      rw [hc]
    rw [hj₀, hj₁] at hslot
    have hcon : ((s : Slot) : ℕ) = ((s : ℕ) + 1) % numSlots :=
      (congrArg (fun u : Slot => (u : ℕ)) hslot).trans (val_suc s)
    exact hpos hcon
  rw [← cofG_det_updateCol]
  refine det_updateCol_eq_col_zero _ j₀ j₁ _ hne ?_
  intro i
  rw [slaterMat_cols_succ_prop S x h s (s + 1 : Slot) hs hs1 rfl j₀ j₁ hj₀ hj₁ i]

end Septinal
