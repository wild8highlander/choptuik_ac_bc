/-
Septinal YM · Этап 4c: кофакторные кирпичи сборки `slater_diag_odd`.

Свёртка вкладов рёбер: масштабированные столбцы занятых пар дают нулевые
определители (два равных столбца), суммы масштабированных кофакторных
вкладов сворачиваются в `(Σ_i d_i) · det M`, столбцы занятых соседних
сайтов пропорциональны (ψ-сдвиг), включая пары через границу цикла
(сайты 21 и 0).
-/
import SeptinalYM.SlaterDiag

namespace Septinal
open Finset BigOperators

/-! ## 4c-0: арифметика ω для мостов -/

/-- `ω ≠ 0` (из `ω^22 = 1`). -/
theorem omega_ne_zero : omega ≠ 0 := by
  intro hc
  have h : omega ^ numSlots = 1 := omega_pow_numSlots
  rw [hc, zero_pow (show (numSlots:ℕ) ≠ 0 by
    have h22 : numSlots = 22 := rfl
    omega)] at h
  exact zero_ne_one h

/-- `ω^{k} · ω^{21k} = 1` (мост wrap-членов: `21 ≡ −1 (mod 22)`). -/
theorem omega_pos_wrap (k : ℕ) :
    omega ^ (k % numSlots) * omega ^ ((k * 21) % numSlots) = 1 := by
  have h22 : numSlots = 22 := rfl
  rw [omega_pow_mod, omega_pow_mod, ← pow_add]
  have hnat : k + k * 21 = numSlots * k := by rw [h22]; ring
  rw [hnat, pow_mul, omega_pow_numSlots, one_pow]

/-- `ω^{−k} · ω^{k} = 1` (форма мостов pred-вкладов). -/
theorem omega_neg_wrap (k : ℕ) :
    omega ^ ((numSlots - k % numSlots) % numSlots) * omega ^ (k % numSlots) = 1 := by
  have h22 : numSlots = 22 := rfl
  have hlt : k % numSlots < numSlots := by
    rw [h22]; exact Nat.mod_lt k (by norm_num)
  rw [omega_pow_mod (numSlots - k % numSlots), ← pow_add]
  have hsum : (numSlots - k % numSlots) + k % numSlots = numSlots := by
    rw [h22]; omega
  rw [hsum, omega_pow_numSlots]

/-- `ω^{−k} = ω^{21k}` — pred-мостовая форма совпадает с wrap-формой. -/
theorem omega_neg_eq_21 (k : ℕ) :
    omega ^ ((numSlots - k % numSlots) % numSlots) = omega ^ ((k * 21) % numSlots) := by
  have h1 : omega ^ ((numSlots - k % numSlots) % numSlots) * omega ^ (k % numSlots) = 1 :=
    omega_neg_wrap k
  have h2 : omega ^ ((k * 21) % numSlots) * omega ^ (k % numSlots) = 1 := by
    rw [mul_comm]
    exact omega_pos_wrap k
  exact mul_right_cancel₀ (pow_ne_zero _ omega_ne_zero) (h1.trans h2.symm)

/-! ## 4c-A: обнуление масштабированных столбцов занятых пар -/

/-- Если заменённый масштабированный столбец `j` совпадает со столбцом `j'`
(`j ≠ j'`), определитель нулевой (два равных столбца, транспонирование). -/
theorem det_updateCol_eq_col_zero {k : ℕ} (M : Matrix (Fin k) (Fin k) ℂ) (j j' : Fin k)
    (d : Fin k → ℂ) (hj : j ≠ j') (h : ∀ i, d i * M i j = M i j') :
    (M.updateCol j fun i => d i * M i j).det = 0 := by
  have hzero : (M.updateCol j (fun i => d i * M i j)).transpose.det = 0 := by
    refine Matrix.det_zero_of_row_eq hj ?_
    funext t
    show M.updateCol j (fun i => d i * M i j) t j
        = M.updateCol j (fun i => d i * M i j) t j'
    rw [Matrix.updateCol_apply, Matrix.updateCol_apply, if_pos rfl,
      if_neg (Ne.symm hj), h t]
  rwa [Matrix.det_transpose] at hzero

/-- Универсальная форма обнуления: мостовая матрица вклада ребра
(`of`-`if` с масштабированным столбцом `j`, совпадающим со столбцом `j'`)
имеет нулевой определитель. -/
theorem det_scaled_zero_of_eq {k : ℕ} (M : Matrix (Fin k) (Fin k) ℂ) (j j' : Fin k)
    (d : Fin k → ℂ) (hj : j ≠ j') (h : ∀ i, d i * M i j = M i j') :
    (Matrix.of fun i t => if t = j then d i * M i j else M i t).det = 0 := by
  have heq : (Matrix.of fun i t => if t = j then d i * M i j else M i t)
      = M.updateCol j (fun i => d i * M i j) := by
    ext i t
    by_cases ht : t = j
    · subst ht; simp [Matrix.updateCol_apply, Matrix.of_apply]
    · simp [Matrix.updateCol_apply, Matrix.of_apply, ht]
  rw [heq]
  exact det_updateCol_eq_col_zero M j j' d hj h

/-! ## 4c-B: пропорциональность занятых столбцов -/

/-- Столбцы Слейтеровской матрицы, отвечающие занятым соседним сайтам
`u₀ ↦ u₀+1`, поточечно пропорциональны: `M_{·,j₁} = ω^{k_i}·M_{·,j₀}`
(`ψ_k(u+1) = ω^{k mod 22}·ψ_k(u)`). -/
theorem slaterMat_cols_succ_prop (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u₀ u₁ : Slot) (hu₀ : u₀ ∈ supp x) (hu₁ : u₁ ∈ supp x) (hadj : u₁ = u₀ + 1)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = u₁) (i : Fin S.card) :
    slaterMat S x h i j₁
      = omega ^ (modeOf S i % numSlots) * slaterMat S x h i j₀ := by
  rw [slaterMat_entry_emb S x h i j₁, slaterMat_entry_emb S x h i j₀, hj₁, hadj,
    hj₀, psi_shift]

/-- Столбцы занятых сайтов `0` и `21` (соседи через границу цикла)
пропорциональны: `M_{·,j₀} = ω^{k_i}·M_{·,j₂₁}` (`21 ≡ −1 (mod 22)`). -/
theorem slaterMat_cols_wrap_prop (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hu0 : (0 : Slot) ∈ supp x) (hu21 : (21 : Slot) ∈ supp x)
    (j0 j21 : Fin S.card) (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0)
    (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21) (i : Fin S.card) :
    slaterMat S x h i j0
      = omega ^ (modeOf S i % numSlots) * slaterMat S x h i j21 := by
  rw [slaterMat_entry_emb S x h i j0, slaterMat_entry_emb S x h i j21, hj0, hj21]
  unfold psi
  have h0 : (((0 : Slot) : ℕ)) = 0 := rfl
  have h21 : (((21 : Slot) : ℕ)) = 21 := rfl
  rw [h0, h21, mul_zero, Nat.zero_mod, pow_zero, mul_div_assoc', omega_pos_wrap]

/-! ## 4c-A': свёртка сумм с общим масштабом -/

/-- Свёртка: `Σ_j Σ_i d_i·M_{ij}·C_{ij} = (Σ_i d_i)·det M`. -/
theorem sum_scaled_row {k : ℕ} (M : Matrix (Fin k) (Fin k) ℂ) (d : Fin k → ℂ) :
    (∑ j, ∑ i, d i * M i j * cofG M i j) = (∑ i, d i) * M.det := by
  rw [Finset.sum_comm, Finset.sum_mul]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [← cofG_sum_row M i, Finset.mul_sum]
  refine Finset.sum_congr rfl fun j _ => ?_
  ring

end Septinal
