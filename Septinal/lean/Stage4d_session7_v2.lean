/-
Septinal YM · Этап 4d: сборка `slater_diag_odd`.

Схема: mulVec-расщепление суммы операторов; разбор рёбер `s` по типу
(заблокированное / succ-активное / pred-активное); вклад succ-ребра —
`2·D⁺(j_s)` (через `cofG_det_updateCol`), pred-ребра — `2·D⁻(j_{s+1})`;
«недостающие» члены занятых соседних пар обнуляются (два равных столбца);
свёртка `Σ_j Σ_i d_i·M_{ij}·C_{ij} = (Σ_i d_i)·det M`; связка с `eps`.
-/
import Mathlib.Data.Finset.SDiff
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

/-! ## 4d-3: разбор вклада внутреннего ребра -/

/-- Биты конфигурации: `x s ∈ {0, 1}`. -/
theorem cfg_bit (x : Cfg) (s : Slot) : x s = 0 ∨ x s = 1 := by
  have hval : (x s : ℕ) = 0 ∨ (x s : ℕ) = 1 := by
    have hlt : (x s : ℕ) < 2 := (x s).isLt
    omega
  rcases hval with h | h
  · exact Or.inl (Fin.val_injective h)
  · exact Or.inr (Fin.val_injective h)

/-! ## 4d-4: вклад внутреннего ребра в if-форме -/

/-- Для внутреннего ребра `s` (без цикла) вклад равен `2·D⁺(j_s)`, если
`s` занят и `s+1` свободен; `2·D⁻(j_{s+1})`, если `s` свободен и `s+1`
занят; нулю в противном случае. -/
theorem bondTerm_inner_if (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (hs21 : ((s : ℕ) + 1 < numSlots))
    (j_s j_n : Fin S.card) (hj_s : ((supp x).orderEmbOfFin h j_s : Slot) = s)
    (hj_n : ((supp x).orderEmbOfFin h j_n : Slot) = (s + 1 : Slot)) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (if x s = 1 ∧ x (s + 1 : Slot) = 0
          then ∑ i, omega ^ (modeOf S i % numSlots)
              * slaterMat S x h i j_s * cofG (slaterMat S x h) i j_s
          else 0)
        + ((2 : ℝ) : ℂ) * (if x s = 0 ∧ x (s + 1 : Slot) = 1
          then ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
              * slaterMat S x h i j_n * cofG (slaterMat S x h) i j_n
          else 0) := by
  have hnb : ((s + 1 : Slot) : ℕ) ≠ 0 := by
    have hlt := s.isLt
    have hv := val_suc s
    rcases Nat.lt_or_ge ((s : ℕ) + 1) 22 with h1 | h2
    · have hmod : ((s : ℕ) + 1) % numSlots = (s : ℕ) + 1 :=
        Nat.mod_eq_of_lt (by
          have h22 : numSlots = 22 := rfl
          omega)
      omega
    · have h22 : numSlots = 22 := rfl
      omega
  by_cases hs1 : x s = 1
  · by_cases hs2 : x (s + 1 : Slot) = 0
    · rw [bondTerm_succ_Dplus S x h s hs1 hs2 hnb j_s hj_s,
        if_pos (⟨hs1, hs2⟩ : x s = 1 ∧ x (s + 1 : Slot) = 0),
        if_neg (fun hc : x s = 0 ∧ x (s + 1 : Slot) = 1 => zero_ne_one (hs1.symm.trans hc.1).symm)]
      simp
    · have hs2' : x (s + 1 : Slot) = 1 := by
        rcases cfg_bit x (s + 1 : Slot) with h0 | h1
        · exact absurd h0 hs2
        · exact h1
      rw [bondTerm_blocked s (fun y => slater S y) x (by rw [hs1, hs2']),
        if_neg (fun hc : x s = 1 ∧ x (s + 1 : Slot) = 0 => zero_ne_one (hs2'.symm.trans hc.2).symm),
        if_neg (fun hc : x s = 0 ∧ x (s + 1 : Slot) = 1 => zero_ne_one (hs1.symm.trans hc.1).symm)]
      ring
  · have hs0 : x s = 0 := by
      rcases cfg_bit x s with h0 | h1
      · exact h0
      · exact absurd h1 hs1
    by_cases hs2 : x (s + 1 : Slot) = 1
    · rw [bondTerm_pred_Dminus S x h s hs2 hs0 hnb j_n hj_n,
        if_neg (fun hc : x s = 1 ∧ x (s + 1 : Slot) = 0 => hs1 hc.1),
        if_pos (⟨hs0, hs2⟩ : x s = 0 ∧ x (s + 1 : Slot) = 1)]
      simp
    · have hs2' : x (s + 1 : Slot) = 0 := by
        rcases cfg_bit x (s + 1 : Slot) with h0 | h1
        · exact h0
        · exact absurd h1 hs2
      rw [bondTerm_blocked s (fun y => slater S y) x (by rw [hs0, hs2']),
        if_neg (fun hc : x s = 1 ∧ x (s + 1 : Slot) = 0 => hs1 hc.1),
        if_neg (fun hc : x s = 0 ∧ x (s + 1 : Slot) = 1 => hs2 hc.2)]
      ring

/-! ## 4d-5: обнуление wrap-пары (21, 0) -/

/-- Занятая wrap-пара (сайты 21 и 0 оба заняты): `D⁺(j₂₁) = 0`. -/
theorem dplus_zero_wrap (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, omega ^ (modeOf S i % numSlots)
        * slaterMat S x h i j21 * cofG (slaterMat S x h) i j21) = 0 := by
  rw [← cofG_det_updateCol]
  have hne : j21 ≠ j0 := by
    intro hc
    have h1 : ((21 : Slot) : ℕ) = ((0 : Slot) : ℕ) := by
      rw [← hj21, ← hj0, hc]
    norm_num at h1
  refine det_updateCol_eq_col_zero _ j21 j0 _ hne ?_
  intro i
  rw [slaterMat_cols_wrap_prop S x h h0 h21 j0 j21 hj0 hj21 i]

/-- Занятая wrap-пара (сайты 21 и 0 оба заняты): `D⁻(j₀) = 0`. -/
theorem dminus_zero_wrap (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, omega ^ (numSlots - modeOf S i % numSlots)
        * slaterMat S x h i j0 * cofG (slaterMat S x h) i j0) = 0 := by
  rw [← cofG_det_updateCol]
  have hne : j0 ≠ j21 := by
    intro hc
    have h1 : ((21 : Slot) : ℕ) = ((0 : Slot) : ℕ) := by
      rw [← hj21, ← hj0, ← hc]
    norm_num at h1
  refine det_updateCol_eq_col_zero _ j0 j21 _ hne ?_
  intro i
  rw [slaterMat_cols_wrap_prop S x h h0 h21 j0 j21 hj0 hj21 i]
  rw [← mul_assoc, omega_mul_inv_bridge, one_mul]

/-! ## 4d-6: сумма по носителю через столбцы -/

/-- Сюръективность перечисления носителя: каждый занятый сайт отвечает
некоторому столбцу Слейтеровской матрицы. -/
theorem pos_surj (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u : Slot) (hu : u ∈ supp x) :
    ∃ j : Fin S.card, ((supp x).orderEmbOfFin h j : Slot) = u := by
  have hmem : u ∈ (supp x).sort (· ≤ ·) := by
    rw [Finset.mem_sort]; exact hu
  have hlen : ((supp x).sort (· ≤ ·)).length = S.card := by
    rw [Finset.length_sort]; exact h
  obtain ⟨n, hn⟩ := List.mem_iff_get.mp hmem
  refine ⟨Fin.cast hlen n, ?_⟩
  have hidx : Fin.cast (h.symm.trans (Finset.length_sort (· ≤ ·)).symm)
      (Fin.cast hlen n) = n := Fin.ext (by simp)
  have hget := sort_get_eq_orderEmbOfFin (supp x) h (Fin.cast hlen n)
  rw [hidx] at hget
  rw [← hget, hn]

/-- Сумма по занятым сайтам равна сумме по столбцам (перечисление
`orderEmbOfFin` — биекция столбцов и носителя). -/
theorem sum_supp_emb (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (F : Slot → ℂ) :
    (∑ u ∈ supp x, F u) = ∑ j : Fin S.card, F ((supp x).orderEmbOfFin h j) := by
  set fcols : Fin S.card → ↥(supp x) := fun j =>
    ⟨(supp x).orderEmbOfFin h j, Finset.orderEmbOfFin_mem _ _ _⟩ with hfcols
  have hinj : Function.Injective fcols := by
    intro a b hab
    exact StrictMono.injective ((supp x).orderEmbOfFin h).strictMono
      (congrArg Subtype.val hab)
  have hsurj : Function.Surjective fcols := by
    intro b
    obtain ⟨u, hu⟩ := b
    obtain ⟨j, hj⟩ := pos_surj S x h u hu
    exact ⟨j, Subtype.ext hj⟩
  have hmem : ∀ (j : Fin S.card), j ∈ (Finset.univ : Finset (Fin S.card)) ↔
      fcols j ∈ (Finset.univ : Finset ↥(supp x)) := by
    intro j
    exact ⟨fun _ => Finset.mem_univ _, fun _ => Finset.mem_univ _⟩
  have hval : ∀ j ∈ (Finset.univ : Finset (Fin S.card)),
      F ((supp x).orderEmbOfFin h j) = (fun b : ↥(supp x) => F b.val) (fcols j) :=
    fun j _ => rfl
  rw [Finset.sum_bijective fcols ⟨hinj, hsurj⟩ hmem hval
    (s := Finset.univ) (t := Finset.univ)
    (f := fun j => F ((supp x).orderEmbOfFin h j))
    (g := fun b : ↥(supp x) => F b.val)]
  exact (Finset.sum_attach (supp x) F).symm

/-! ## 4d-7: связка eps и омег -/

/-- Энергия моды через омегу: `ε_k = 2·(ω^{k mod 22} + ω^{22 − k mod 22})`
(мост между спектром `4·cos` и свёрткой кофакторов). -/
theorem eps_omega (k : ℕ) :
    (eps k : ℂ) = 2 * (omega ^ (k % numSlots) + omega ^ (numSlots - k % numSlots)) := by
  have h22 : numSlots = 22 := rfl
  have hm : k % numSlots < numSlots := Nat.mod_lt _ (by rw [h22]; norm_num)
  rw [h22] at hm
  have hk0 : 22 * (k / 22) + k % 22 = k := Nat.div_add_mod k 22
  have hk : ((k : ℝ)) = (22 : ℝ) * ((k / 22 : ℕ) : ℝ) + ((k % 22 : ℕ) : ℝ) := by
    have hk0' : (((22 * (k / 22) + k % 22 : ℕ)) : ℝ) = ((k : ℕ) : ℝ) := by rw [hk0]
    push_cast at hk0'
    linarith
  -- Периодичность косинуса: cos(2πk/22) = cos(2π(k mod 22)/22)
  have hsplit : (2 : ℝ) * Real.pi * (k : ℝ) / numSlots
      = 2 * Real.pi * (((k % numSlots : ℕ) : ℝ) / numSlots)
        + 2 * Real.pi * ((k / numSlots : ℕ) : ℝ) := by
    rw [h22, hk]
    ring
  have hsin0 : Real.sin (((k / numSlots : ℕ) : ℝ) * (2 * Real.pi)) = 0 := by
    have h := Real.sin_nat_mul_two_pi_sub 0 ((k / numSlots : ℕ) : ℕ)
    rw [sub_zero, Real.sin_zero, neg_zero] at h
    exact h
  have hper : Real.cos (2 * Real.pi * (k : ℝ) / numSlots)
      = Real.cos (2 * Real.pi * (((k % numSlots : ℕ) : ℝ) / numSlots)) := by
    rw [hsplit, Real.cos_add, mul_comm (2 * Real.pi) ((k / numSlots : ℕ) : ℝ),
      Real.cos_nat_mul_two_pi, hsin0]
    ring
  -- Омега через экспоненту (в форме, совместимой с разложением cos)
  have hdef : (omega : ℂ) = Complex.exp ((2 : ℝ) * Real.pi * Complex.I / numSlots) := rfl
  have hwR : (omega ^ (k % numSlots) : ℂ)
      = Complex.exp
          ((2 : ℝ) * Real.pi * (((k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I) := by
    have h1 : (omega ^ (k % numSlots) : ℂ)
        = Complex.exp
            (((k % numSlots : ℕ) : ℂ) * ((2 : ℝ) * Real.pi * Complex.I / numSlots)) := by
      rw [hdef, ← Complex.exp_nat_mul]
    rw [h1]
    congr 1
    push_cast
    ring
  have hwL : (omega ^ (numSlots - k % numSlots) : ℂ)
      = Complex.exp
          ((2 : ℝ) * Real.pi
            * (((numSlots - k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I) := by
    have h1 : (omega ^ (numSlots - k % numSlots) : ℂ)
        = Complex.exp
            (((numSlots - k % numSlots : ℕ) : ℂ)
              * ((2 : ℝ) * Real.pi * Complex.I / numSlots)) := by
      rw [hdef, ← Complex.exp_nat_mul]
    rw [h1]
    congr 1
    push_cast
    ring
  -- Склейка: 4·cos θ = 2·(exp(iθ) + exp(−iθ))
  have hexp2pi : Complex.exp ((2 : ℝ) * Real.pi * Complex.I) = 1 := by
    have hkey : ((2 : ℝ) * Real.pi * Complex.I)
        = ((numSlots : ℕ) : ℂ) * ((2 : ℝ) * Real.pi * Complex.I / numSlots) := by
      rw [h22]
      ring
    have hform : Complex.exp ((2 : ℝ) * Real.pi * Complex.I)
        = (omega : ℂ) ^ numSlots := by
      rw [hkey, Complex.exp_nat_mul, ← hdef, omega_pow_numSlots]
    rw [hform, omega_pow_numSlots]
  -- Правый член: exp(2πi·(22−m)/22) = exp(−2πi·m/22) через exp(2πi) = 1
  have hright : Complex.exp ((2 : ℝ) * Real.pi
        * (((numSlots - k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I)
      = Complex.exp (-((2 : ℝ) * Real.pi
        * (((k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I)) := by
    have h2 : Complex.exp ((2 : ℝ) * Real.pi
          * (((numSlots - k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I)
        = Complex.exp (((numSlots - k % numSlots : ℕ) : ℂ)
          * ((2 : ℝ) * Real.pi * Complex.I / numSlots)) := by
      congr 1
      push_cast
      ring
    have h3 : Complex.exp (-((2 : ℝ) * Real.pi
          * (((k % numSlots : ℕ) : ℝ) / numSlots) * Complex.I))
        = Complex.exp ((-((k % numSlots : ℕ) : ℂ))
          * ((2 : ℝ) * Real.pi * Complex.I / numSlots)) := by
      congr 1
      push_cast
      ring
    have hs2 : ((numSlots - k % numSlots : ℕ) : ℂ)
        * ((2 : ℝ) * Real.pi * Complex.I / numSlots)
        = ((numSlots : ℕ) : ℂ) * ((2 : ℝ) * Real.pi * Complex.I / numSlots)
          + (-((k % numSlots : ℕ) : ℂ)
            * ((2 : ℝ) * Real.pi * Complex.I / numSlots)) := by
      rw [h22]
      have hrel : k % 22 ≤ 22 := by omega
      rw [Nat.cast_sub hrel]
      push_cast
      ring
    have hsum : Complex.exp (((numSlots : ℕ) : ℂ)
          * ((2 : ℝ) * Real.pi * Complex.I / numSlots))
        = 1 := by
      rw [← hexp2pi]
      have hz : ((numSlots : ℕ) : ℂ) * ((2 : ℝ) * Real.pi * Complex.I / numSlots)
          = (2 : ℝ) * Real.pi * Complex.I := by
        rw [h22]
        push_cast
        ring
      rw [hz]
    rw [h2, hs2, Complex.exp_add, hsum, one_mul, ← h3]

  -- Склейка: 4·cos θ = 2·(exp(iθ) + exp(−iθ))
  unfold eps
  rw [hper, hwR, hwL, hright]
  push_cast
  unfold Complex.cos
  ring


/-! ## 4d-8: различие столбцов и pred-обнуление занятых пар -/

/-- Различие слотов в цикле: `s ≠ s+1`. -/
theorem slot_ne_suc (s : Slot) : (s : Slot) ≠ (s + 1 : Slot) := by
  intro hc
  have hval : ((s : Slot) : ℕ) = ((s + 1 : Slot) : ℕ) :=
    congrArg (fun u : Slot => (u : ℕ)) hc
  rw [val_suc s] at hval
  have h22 : numSlots = 22 := rfl
  have hlt : (s : ℕ) < 22 := by
    have := s.isLt
    omega
  have hlink : ((s : ℕ) + 1) % numSlots = ((s : ℕ) + 1) % 22 := by
    congr 1
  omega

/-- Разные занятые сайты — разные столбцы (инъективность перечисления). -/
theorem pos_ne_of_ne (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    {s t : Slot} (hst : s ≠ t)
    {j₀ j₁ : Fin S.card} (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = t) : j₀ ≠ j₁ := by
  intro hc
  have hslot : ((supp x).orderEmbOfFin h j₀ : Slot)
      = ((supp x).orderEmbOfFin h j₁ : Slot) := by rw [hc]
  rw [hj₀, hj₁] at hslot
  exact hst hslot

/-- Занятая succ-пара (`x s = 1`, `x (s+1) = 1`, без цикла): pred-
масштабированный столбец `j₁` совпадает со столбцом `j₀` — `D⁻(j₁) = 0`. -/
theorem dminus_zero_of_pair (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h2 : x (s + 1 : Slot) = 1) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (∑ i, omega ^ (numSlots - modeOf S i % numSlots)
        * slaterMat S x h i j₁ * cofG (slaterMat S x h) i j₁) = 0 := by
  have hs : s ∈ supp x := by rw [← hj₀]; exact Finset.orderEmbOfFin_mem _ _ _
  have hs1 : (s + 1 : Slot) ∈ supp x := by
    rw [← hj₁]; exact Finset.orderEmbOfFin_mem _ _ _
  rw [← cofG_det_updateCol]
  refine det_updateCol_eq_col_zero _ j₁ j₀ _
    (pos_ne_of_ne S x h (slot_ne_suc s).symm hj₁ hj₀) ?_
  intro i
  rw [slaterMat_cols_succ_prop S x h s (s + 1 : Slot) hs hs1 rfl j₀ j₁ hj₀ hj₁ i]
  rw [← mul_assoc, omega_mul_inv_bridge, one_mul]

/-! ## 4d-9: позиция сайта 21 — крайний столбец -/

/-- При занятом сайте 21 его позиция в сортировке носителя — последний
столбец (21 — максимальный слот). -/
theorem pos_last_max (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hu21 : (21 : Slot) ∈ supp x)
    (j21 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = (21 : Slot)) :
    ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨21, hu21⟩
        omega)) : Slot) = (21 : Slot) := by
  have hle1 : ((supp x).orderEmbOfFin h j21 : Slot)
      ≤ ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨21, hu21⟩
        omega)) : Slot) :=
    ((supp x).orderEmbOfFin h).monotone (by
      have hval := j21.isLt
      show (j21 : ℕ) ≤ S.card - 1
      omega)
  have hmem : ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨21, hu21⟩
        omega)) : Slot)
      ∈ supp x := Finset.orderEmbOfFin_mem _ _ _
  have hle2 : ((supp x).orderEmbOfFin h (Fin.mk (S.card - 1) (by
        have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨21, hu21⟩
        omega)) : Slot)
      ≤ (21 : Slot) := Fin.le_last _
  rw [hj21] at hle1
  exact le_antisymm hle2 hle1

/-! ## 4d-10: вклад wrap-ребра 21 в кофакторной форме -/

/-- Столбцы Слейтеровской матрицы с одинаковыми позициями совпадают
(поточечно). -/
theorem slaterMat_col_congr (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    {j j' : Fin S.card}
    (hj : ((supp x).orderEmbOfFin h j : Slot)
        = ((supp x).orderEmbOfFin h j' : Slot))
    (i : Fin S.card) :
    slaterMat S x h i j = slaterMat S x h i j' := by
  rw [slaterMat_entry_emb, slaterMat_entry_emb, hj]

/-- Вклад wrap-ребра `21` при `x 21 = 1`, `x 0 = 0` (циклический сдвиг
вправо): `(−1)^{k−1}·D⁺(j₂₁)` в столбце `j₂₁`. -/
theorem bondTerm_21_right (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (h1 : x (21 : Slot) = 1) (h0 : x (0 : Slot) = 0)
    (j21 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = (21 : Slot)) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (((-1 : ℂ) ^ (S.card - 1))
          * ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i j21 * cofG (slaterMat S x h) i j21) := by
  have hu21 : (21 : Slot) ∈ supp x := by
    unfold supp; simpa [h1] using Finset.mem_univ (21 : Slot)
  have hpos0 : 0 < S.card := by
    rw [← h]
    exact Finset.card_pos.mpr ⟨(21 : Slot), hu21⟩
  have hje : j21 = Fin.mk (S.card - 1) (by
      have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨(21 : Slot), hu21⟩
      omega) := by
    refine ((supp x).orderEmbOfFin h).injective ?_
    rw [hj21, pos_last_max S x h hu21 j21 hj21]
  rw [hje, bondTerm_hop_wrap_right S x h h1 h0,
    cofG_det_cyclic_right (slaterMat S x h) hpos0
      (fun i => omega ^ (modeOf S i % numSlots))]

/-! ## 4d-2в: сборка slater_diag_odd — переносные леммы -/

/-- Занятый сайт лежит в носителе. -/
theorem supp_mem_of_one (x : Cfg) (u : Slot) (h : x u = 1) : u ∈ supp x := by
  unfold supp; simp [h]

/-- Свободный сайт не лежит в носителе. -/
theorem supp_not_mem_of_zero (x : Cfg) (u : Slot) (h : x u = 0) : u ∉ supp x := by
  unfold supp; simp [h]

/-- Вклад wrap-ребра `21` при `x 0 = 1`, `x 21 = 0` (циклический сдвиг
влево): `(−1)^{k−1}·D⁻(j₀)` в столбце `j₀`. -/
theorem bondTerm_21_pred_left (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (h1 : x (0 : Slot) = 1) (h0 : x (21 : Slot) = 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = (0 : Slot)) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (((-1 : ℂ) ^ (S.card - 1))
          * ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i j₀ * cofG (slaterMat S x h) i j₀) := by
  have hu0 : (0 : Slot) ∈ supp x := supp_mem_of_one x (0 : Slot) h1
  have hpos0 : 0 < S.card := by
    rw [← h]; exact Finset.card_pos.mpr ⟨(0 : Slot), hu0⟩
  have hje : j₀ = Fin.mk 0 (by
      have hp : 0 < S.card := by omega
      omega) := by
    refine ((supp x).orderEmbOfFin h).injective ?_
    rw [hj₀, ((orderEmbOfFin_min0 (supp x) hu0 h).1).symm]
  rw [hje, bondTerm_hop_wrap_left S x h h1 h0,
    cofG_det_cyclic_left (slaterMat S x h) hpos0
      (fun i => omega ^ (numSlots - modeOf S i % numSlots))]

/-! ## 4d-2г: инфраструктура пере-индексации -/

/-- Обратное соответствие «позиция ↦ столбец»: занятый сайт `s`
получает свой столбец через сюръективность `pos_surj`. -/
noncomputable def embInv (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (s : Slot) : Fin S.card :=
  if hs : s ∈ supp x then (pos_surj S x h s hs).choose
  else Fin.mk 0 (by omega)

/-- Столбец, выбранный для занятого сайта, имеет эту позицию. -/
theorem embInv_spec (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (s : Slot) (hs : s ∈ supp x) :
    ((supp x).orderEmbOfFin h (embInv S x h hz s) : Slot) = s := by
  rw [embInv, dif_pos hs]
  exact (pos_surj S x h s hs).choose_spec

/-- Обратное к перечислению: `embInv (emb j) = j`. -/
theorem embInv_emb (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (j : Fin S.card) :
    embInv S x h hz ((supp x).orderEmbOfFin h j) = j :=
  ((supp x).orderEmbOfFin h).injective
    (by rw [embInv_spec S x h hz _ (Finset.orderEmbOfFin_mem _ _ _)])

/-- `s + 21 + 1 = s` в `Slot` (предшественник). -/
theorem slot_pred_suc_eq (s : Slot) : ((s + 21 : Slot) + 1 : Slot) = s := by
  refine Fin.ext ?_
  have h22 : numSlots = 22 := rfl
  rw [Fin.val_add, Fin.val_add]
  have hv : ((s : Slot) : ℕ) < numSlots := s.isLt
  simp only [h22] at hv ⊢
  rw [Nat.mod_add_mod]
  show (↑s + 22) % 22 = ↑s
  rw [Nat.add_mod_right, Nat.mod_eq_of_lt hv]

/-- Фильтр-перенос: сумма по всем слотам с условием «в носителе и `Q`»
равна сумме по столбцам с условием `Q` на позициях. -/
theorem sum_supp_filter (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (Q : Slot → Prop) [DecidablePred Q] (F : Slot → ℂ) :
    (∑ s : Slot, if s ∈ supp x ∧ Q s then F s else 0)
      = ∑ j : Fin S.card,
        (if Q ((supp x).orderEmbOfFin h j) then
          F ((supp x).orderEmbOfFin h j) else 0) := by
  have hzero : ∀ s ∈ (supp x)ᶜ, (if s ∈ supp x ∧ Q s then F s else 0) = 0 := by
    intro s hsc
    have hs : s ∉ supp x := Finset.mem_compl.mp hsc
    rw [if_neg (fun hc => hs hc.1)]
  have hsplit : (∑ s : Slot, if s ∈ supp x ∧ Q s then F s else 0)
      = ∑ s ∈ supp x, (if Q s then F s else 0) := by
    rw [← Finset.sum_add_sum_compl (s := supp x)
      (f := fun s => if s ∈ supp x ∧ Q s then F s else 0),
      Finset.sum_eq_zero hzero, add_zero]
    refine Finset.sum_congr rfl fun s hs => ?_
    by_cases hQ : Q s
    · rw [if_pos (⟨hs, hQ⟩ : s ∈ supp x ∧ Q s), if_pos hQ]
    · rw [if_neg (fun hc => hQ hc.2), if_neg hQ]
  rw [hsplit]
  exact sum_supp_emb S x h (fun u => if Q u then F u else 0)

/-- Пере-индексация succ-части: сумма по рёбрам переходит в сумму по
столбцам; столбец `j` срабатывает, когда его succ-сосед `emb j + 1`
свободен. -/
theorem succ_sum_reindex (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (F : Slot → ℂ) :
    (∑ s : Slot, if x s = 1 ∧ x (s + 1) = 0 then F s else 0)
      = ∑ j : Fin S.card,
        (if x ((supp x).orderEmbOfFin h j + 1) = 0 then
          F ((supp x).orderEmbOfFin h j) else 0) := by
  have hstep : (∑ s : Slot, if x s = 1 ∧ x (s + 1) = 0 then F s else 0)
      = ∑ s : Slot, if s ∈ supp x ∧ x (s + 1) = 0 then F s else 0 := by
    refine Finset.sum_congr rfl fun s _ => ?_
    by_cases hs : s ∈ supp x
    · by_cases hQ : x (s + 1) = 0
      · rw [if_pos (⟨mem_supp x s hs, hQ⟩ : x s = 1 ∧ x (s + 1) = 0),
          if_pos (⟨hs, hQ⟩ : s ∈ supp x ∧ x (s + 1) = 0)]
      · rw [if_neg (fun hc => hQ hc.2), if_neg (fun hc => hQ hc.2)]
    · rw [if_neg (fun hc => hs (supp_mem_of_one x s hc.1)),
        if_neg (fun hc => hs hc.1)]
  rw [hstep, sum_supp_filter S x h (fun s => x (s + 1) = 0)]

/-- Пере-индексация pred-части: сумма по рёбрам `s` переходит в сумму по
столбцам-целям `emb j`; аргумент `F` остаётся ребром-предшественником
`emb j + 21`. -/
theorem pred_sum_reindex (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (F : Slot → ℂ) :
    (∑ s : Slot, if x s = 0 ∧ x (s + 1) = 1 then F s else 0)
      = ∑ j : Fin S.card,
        (if x ((supp x).orderEmbOfFin h j + 21) = 0 then
          F ((supp x).orderEmbOfFin h j + 21) else 0) := by
  have hshift : (∑ s : Slot, if x s = 0 ∧ x (s + 1) = 1 then F s else 0)
      = ∑ u : Slot,
        (if x (u + 21) = 0 ∧ x u = 1 then F (u + 21) else 0) := by
    have hsucc : Function.Bijective (fun s : Slot => s + 1) := by
      constructor
      · intro a b hab
        refine Fin.ext ?_
        have hab2 : ((a + 1 : Slot) : ℕ) = ((b + 1 : Slot) : ℕ) :=
          congrArg Fin.val hab
        have h1 : ((a + 1 : Slot) : ℕ) = ((a : ℕ) + 1) % numSlots := val_suc a
        have h2 : ((b + 1 : Slot) : ℕ) = ((b : ℕ) + 1) % numSlots := val_suc b
        rw [h1, h2] at hab2
        have hlt1 : (a : ℕ) < numSlots := a.isLt
        have hlt2 : (b : ℕ) < numSlots := b.isLt
        have h22 : numSlots = 22 := rfl
        simp only [h22] at hlt1 hlt2
        have h22 : numSlots = 22 := rfl
        simp only [h22] at hab2
        omega
      · intro u
        exact ⟨u + 21, slot_pred_suc_eq u⟩
    have hmem : ∀ s : Slot, s ∈ (Finset.univ : Finset Slot) ↔
        (s + 1 : Slot) ∈ (Finset.univ : Finset Slot) := fun s =>
      ⟨fun _ => Finset.mem_univ _, fun _ => Finset.mem_univ _⟩
    have hval : ∀ s ∈ (Finset.univ : Finset Slot),
        (if x s = 0 ∧ x (s + 1) = 1 then F s else 0)
          = (fun u : Slot =>
              if x (u + 21) = 0 ∧ x u = 1 then F (u + 21) else 0) (s + 1) := by
      intro s _
      show (if x s = 0 ∧ x (s + 1) = 1 then F s else 0)
          = if x ((s + 1 : Slot) + 21) = 0 ∧ x (s + 1) = 1
            then F ((s + 1 : Slot) + 21) else 0
      have hsf : ((s + 1 : Slot) + 21 : Slot) = s := by
        fin_cases s <;> decide
      rw [hsf]
    rw [Finset.sum_bijective (fun s : Slot => s + 1) hsucc hmem hval
      (g := fun u => if x (u + 21) = 0 ∧ x u = 1 then F (u + 21) else 0)]
  have hsplit : (∑ u : Slot,
        if x (u + 21) = 0 ∧ x u = 1 then F (u + 21) else 0)
      = ∑ u : Slot,
        (if u ∈ supp x ∧ x (u + 21) = 0 then F (u + 21) else 0) := by
    refine Finset.sum_congr rfl fun u _ => ?_
    by_cases hs : u ∈ supp x
    · by_cases hQ : x (u + 21) = 0 <;> simp [hs, hQ, mem_supp x u hs]
    · have hx0 : x u = 0 := by
        rcases cfg_bit x u with h0 | h1
        · exact h0
        · exact absurd (supp_mem_of_one x u h1) hs
      by_cases hQ : x (u + 21) = 0 <;> simp [hs, hQ, hx0]
  rw [hshift, hsplit, sum_supp_filter S x h (fun s => x (s + 21) = 0)]


/-! ## 4d-3: сборка slater_diag_odd -/

/-- `s ∪ {a} = insert a s` (локальная версия: в mathlib v4.21.0
`Finset.union_singleton` отсутствует). -/
theorem finset_union_singleton_eq_insert {α : Type*} [DecidableEq α]
    (s : Finset α) (a : α) : s ∪ {a} = insert a s := by
  ext u
  simp only [Finset.mem_union, Finset.mem_singleton, Finset.mem_insert] <;> tauto

/-- `s \ {a} = s.erase a` (мост между sdiff-синглтоном и erase). -/
theorem finset_sdiff_singleton_eq_erase {α : Type*} [DecidableEq α]
    (s : Finset α) (a : α) : s \ {a} = s.erase a := by
  ext u
  by_cases h : u = a <;> simp [h]

/-- Мощность носителя сохраняется при активном прыжке `s ↦ s+1`
(частица перемещается, число занятых сайтов не меняется). -/
theorem supp_card_flipTwo_suc (x : Cfg) (s : Slot) (hP : x s ≠ x (s + 1 : Slot)) :
    (supp (flipTwo s (s + 1 : Slot) x)).card = (supp x).card := by
  rcases cfg_bit x s with hs0 | hs1
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · exact absurd (hs0.trans ht0.symm) hP
    · -- (0, 1): прыжок `s+1 ↦ s`
      rw [flipTwo_comm, supp_flipTwo_swap (s + 1 : Slot) s (slot_ne_suc s).symm x ht1 hs0,
        finset_sdiff_singleton_eq_erase _ _,
        finset_union_singleton_eq_insert _ _,
        Finset.card_insert_of_notMem (by
          refine fun hc => ?_
          rcases Finset.mem_erase.mp hc with ⟨h0, h1⟩
          exact supp_not_mem_of_zero x s hs0 (by simp [h0, h1])),
        Finset.card_erase_of_mem (supp_mem_of_one x (s + 1 : Slot) ht1)]
      have hmem1 : (s + 1 : Slot) ∈ supp x :=
        supp_mem_of_one x (s + 1 : Slot) ht1
      have hp1 : 1 ≤ (supp x).card := by
        have hp := Finset.card_pos.mpr ⟨_, hmem1⟩
        omega
      omega
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · -- (1, 0): прыжок `s ↦ s+1`
      rw [supp_flipTwo_swap s (s + 1 : Slot) (slot_ne_suc s) x hs1 ht0,
        finset_sdiff_singleton_eq_erase _ _,
        finset_union_singleton_eq_insert _ _,
        Finset.card_insert_of_notMem (by
          refine fun hc => ?_
          rcases Finset.mem_erase.mp hc with ⟨h0, h1⟩
          exact supp_not_mem_of_zero x (s + 1 : Slot) ht0 (by simp [h0, h1])),
        Finset.card_erase_of_mem (supp_mem_of_one x s hs1)]
      have hmem1 : s ∈ supp x := supp_mem_of_one x s hs1
      have hp1 : 1 ≤ (supp x).card := by
        have hp := Finset.card_pos.mpr ⟨_, hmem1⟩
        omega
      omega
    · exact absurd (hs1.trans ht1.symm) hP

/-- При несовпадающей мощности носителя вклад каждого ребра нулевой:
прыжок сохраняет мощность, а Ψ на чужих секторах равна нулю. -/
theorem bondTerm_mulVec_zero_hcard (S : Finset Slot) (x : Cfg)
    (hxz : (supp x).card ≠ S.card) (s : Slot) :
    (bondTerm s *ᵥ (fun y => slater S y)) x = 0 := by
  rw [mulVec_bondTerm]
  by_cases hP : x s ≠ x (s + 1 : Slot)
  · rw [if_pos hP, slater]
    split
    · next hc =>
        exact absurd ((supp_card_flipTwo_suc x s hP).symm.trans hc) hxz
    · rw [mul_zero]
  · rw [if_neg hP]

/-- Знак циклической перестановки столбцов при нечётной мощности:
`(-1)^(k-1) = 1`. -/
theorem neg_one_pow_pred_even {k : ℕ} (hOdd : Odd k) : ((-1 : ℂ) ^ (k - 1)) = 1 := by
  obtain ⟨m, rfl⟩ := hOdd
  rw [Nat.add_sub_cancel, pow_mul, pow_two, neg_mul, one_mul, neg_neg, one_pow]

/-- Вклад внутреннего ребра (без цикла) в if-форме через `embInv`. -/
theorem bondTerm_edge_if (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (s : Slot) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0) :
    (bondTerm s *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
          ∑ i, omega ^ (modeOf S i % numSlots)
            * slaterMat S x h i (embInv S x h hz s)
            * cofG (slaterMat S x h) i (embInv S x h hz s)
        else 0)
        + ((2 : ℝ) : ℂ) * (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
          ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
            * slaterMat S x h i (embInv S x h hz (s + 1 : Slot))
            * cofG (slaterMat S x h) i (embInv S x h hz (s + 1 : Slot))
        else 0) := by
  rcases cfg_bit x s with hs0 | hs1
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · -- (0, 0)
      rw [bondTerm_blocked s _ x (show x s = x (s + 1 : Slot) from hs0.trans ht0.symm),
        if_neg (fun hc => absurd (hc.1.symm.trans hs0) (by decide)),
        if_neg (fun hc => absurd (hc.2.symm.trans ht0) (by decide))]
      norm_num
    · -- (0, 1): pred-активное ребро
      rw [if_neg (fun hc => absurd (hc.1.symm.trans hs0) (by decide)),
        if_pos (⟨hs0, ht1⟩ : x s = 0 ∧ x (s + 1 : Slot) = 1)]
      rw [bondTerm_pred_Dminus S x h s ht1 hs0 hnb (embInv S x h hz (s + 1 : Slot))
        (embInv_spec S x h hz (s + 1 : Slot) (supp_mem_of_one x (s + 1 : Slot) ht1))]
      rw [mul_zero, zero_add]
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · -- (1, 0): succ-активное ребро
      rw [if_pos (⟨hs1, ht0⟩ : x s = 1 ∧ x (s + 1 : Slot) = 0),
        if_neg (fun hc => absurd (hc.1.symm.trans hs1) (by decide))]
      rw [bondTerm_succ_Dplus S x h s hs1 ht0 hnb (embInv S x h hz s)
        (embInv_spec S x h hz s (supp_mem_of_one x s hs1))]
      rw [mul_zero, add_zero]
    · -- (1, 1)
      rw [bondTerm_blocked s _ x (show x s = x (s + 1 : Slot) from hs1.trans ht1.symm),
        if_neg (fun hc => absurd (hc.2.symm.trans ht1) (by decide)),
        if_neg (fun hc => absurd (hc.1.symm.trans hs1) (by decide))]
      norm_num

/-- Вклад wrap-ребра `21` в if-форме (знак `(−1)^(k−1) = 1` при нечётной
мощности; сосед `21 + 1 = 0`). -/
theorem bondTerm_wrap_if (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (hOdd : Odd S.card) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slater S y)) x
      = ((2 : ℝ) : ℂ) * (if x (21 : Slot) = 1 ∧ x ((21 : Slot) + 1 : Slot) = 0 then
          ∑ i, omega ^ (modeOf S i % numSlots)
            * slaterMat S x h i (embInv S x h hz (21 : Slot))
            * cofG (slaterMat S x h) i (embInv S x h hz (21 : Slot))
        else 0)
        + ((2 : ℝ) : ℂ) * (if x (21 : Slot) = 0 ∧ x ((21 : Slot) + 1 : Slot) = 1 then
          ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
            * slaterMat S x h i (embInv S x h hz ((21 : Slot) + 1 : Slot))
            * cofG (slaterMat S x h) i (embInv S x h hz ((21 : Slot) + 1 : Slot))
        else 0) := by
  rcases cfg_bit x (21 : Slot) with hs0 | hs1
  · rcases cfg_bit x (0 : Slot) with ht0 | ht1
    · -- (0, 0)
      rw [bondTerm_blocked (21 : Slot) _ x
        (show x (21 : Slot) = x ((21 : Slot) + 1 : Slot) from hs0.trans ht0.symm),
        if_neg (fun hc => absurd (hc.1.symm.trans hs0) (by decide)),
        if_neg (fun hc => absurd (hc.2.symm.trans ht0) (by decide))]
      norm_num
    · -- (0, 1): wrap-прыжок влево `0 ↦ 21`
      rw [if_neg (fun hc => absurd (hc.1.symm.trans hs0) (by decide)),
        if_pos (⟨hs0, ht1⟩ : x (21 : Slot) = 0 ∧ x ((21 : Slot) + 1 : Slot) = 1)]
      rw [bondTerm_21_pred_left S x h ht1 hs0
        (embInv S x h hz ((21 : Slot) + 1 : Slot))
        (show ((supp x).orderEmbOfFin h
            (embInv S x h hz ((21 : Slot) + 1 : Slot)) : Slot) = (0 : Slot) from
          embInv_spec S x h hz ((21 : Slot) + 1 : Slot)
            (show ((21 : Slot) + 1 : Slot) ∈ supp x from
              supp_mem_of_one x (0 : Slot) ht1)),
        neg_one_pow_pred_even hOdd, one_mul]
      rw [mul_zero, zero_add]
  · rcases cfg_bit x (0 : Slot) with ht0 | ht1
    · -- (1, 0): wrap-прыжок вправо `21 ↦ 0`
      rw [if_pos (⟨hs1, ht0⟩ : x (21 : Slot) = 1 ∧ x ((21 : Slot) + 1 : Slot) = 0),
        if_neg (fun hc => absurd (hc.1.symm.trans hs1) (by decide))]
      rw [bondTerm_21_right S x h hs1 ht0 (embInv S x h hz (21 : Slot))
        (embInv_spec S x h hz (21 : Slot) (supp_mem_of_one x (21 : Slot) hs1)),
        neg_one_pow_pred_even hOdd, one_mul]
      rw [mul_zero, add_zero]
    · -- (1, 1)
      rw [bondTerm_blocked (21 : Slot) _ x
        (show x (21 : Slot) = x ((21 : Slot) + 1 : Slot) from hs1.trans ht1.symm),
        if_neg (fun hc => absurd (hc.2.symm.trans ht1) (by decide)),
        if_neg (fun hc => absurd (hc.1.symm.trans hs1) (by decide))]
      norm_num


/-- Succ-сумма сворачивается в `ω^{k}`-скалированный определитель:
сумма по столбцам с условием «succ-сосед свободен» дополняется нулями
занятых пар (внутренних и wrap) до полной суммы, затем `sum_scaled_row`. -/
theorem succ_part_scaled (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) :
    (∑ s : Slot, (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz s)
          * cofG (slaterMat S x h) i (embInv S x h hz s)
      else 0))
      = (∑ i, omega ^ (modeOf S i % numSlots)) * (slaterMat S x h).det := by
  rw [succ_sum_reindex S x h hz]
  have hFull : (∑ j : Fin S.card,
      (if x ((supp x).orderEmbOfFin h j + 1 : Slot) = 0 then
        ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz ((supp x).orderEmbOfFin h j : Slot))
          * cofG (slaterMat S x h) i
            (embInv S x h hz ((supp x).orderEmbOfFin h j : Slot))
      else 0))
      = ∑ j : Fin S.card,
        ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i j * cofG (slaterMat S x h) i j := by
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [embInv_emb S x h hz j]
    by_cases hQ : x ((supp x).orderEmbOfFin h j + 1 : Slot) = 0
    · rw [if_pos hQ]
    · rw [if_neg hQ]
      symm
      have h1 : x ((supp x).orderEmbOfFin h j : Slot) = 1 :=
        mem_supp x _ (Finset.orderEmbOfFin_mem _ _ _)
      have h2 : x ((supp x).orderEmbOfFin h j + 1 : Slot) = 1 := by
        rcases cfg_bit x _ with hb | hb
        · exact absurd hb hQ
        · exact hb
      by_cases hemb21 : ((supp x).orderEmbOfFin h j : Slot) = (21 : Slot)
      · -- wrap-пара (21, 0)
        rw [dplus_zero_wrap S x h
          (show (21 : Slot) ∈ supp x by
            rw [← hemb21]; exact Finset.orderEmbOfFin_mem _ _ _)
          (show (0 : Slot) ∈ supp x from
            supp_mem_of_one x (0 : Slot)
              (by
                rw [hemb21, show ((21 : Slot) + 1 : Slot) = (0 : Slot) from rfl] at h2
                exact h2))
          j (embInv S x h hz ((supp x).orderEmbOfFin h j + 1 : Slot))
          (show ((supp x).orderEmbOfFin h j : Slot) = (21 : Slot) from hemb21)
          (by
            rw [hemb21]
            exact embInv_spec S x h hz ((21 : Slot) + 1 : Slot)
              (supp_mem_of_one x (0 : Slot)
                (show x ((21 : Slot) + 1 : Slot) = 1 by rw [← hemb21]; exact h2)))]
      · -- внутренняя занятая пара
        have hnb : ((((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) : ℕ) ≠ 0 := by
          intro hc
          apply hemb21
          have hval : ((supp x).orderEmbOfFin h j : ℕ) = 21 := by
            have hv0 : ((supp x).orderEmbOfFin h j : ℕ) < 22 :=
              (supp x).orderEmbOfFin h j |>.isLt
            have h22 : numSlots = 22 := rfl
            have hv2 : ((((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) : ℕ)
                = (((supp x).orderEmbOfFin h j : ℕ) + 1) % numSlots :=
              val_suc ((supp x).orderEmbOfFin h j)
            rw [hc] at hv2
            simp only [h22] at hv2
            omega
          exact Fin.ext hval
        exact dplus_zero_of_pair S x h _ h1 h2 hnb j
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 1 : Slot))
          rfl
          (embInv_spec S x h hz _ (supp_mem_of_one x _ h2))
  rw [hFull]
  exact sum_scaled_row (slaterMat S x h) (fun i => omega ^ (modeOf S i % numSlots))

/-- Pred-сумма сворачивается в `ω^{−k}`-скалированный определитель. -/
theorem pred_part_scaled (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) :
    (∑ s : Slot, (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMat S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0))
      = (∑ i, omega ^ (numSlots - modeOf S i % numSlots)) * (slaterMat S x h).det := by
  rw [pred_sum_reindex S x h hz]
  have hFull : (∑ j : Fin S.card,
      (if x ((supp x).orderEmbOfFin h j + 21 : Slot) = 0 then
        ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i
            (embInv S x h hz (((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot))
          * cofG (slaterMat S x h) i
            (embInv S x h hz (((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot))
      else 0))
      = ∑ j : Fin S.card,
        ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i j * cofG (slaterMat S x h) i j := by
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [slot_pred_suc_eq ((supp x).orderEmbOfFin h j), embInv_emb S x h hz j]
    by_cases hQ : x ((supp x).orderEmbOfFin h j + 21 : Slot) = 0
    · rw [if_pos hQ]
    · rw [if_neg hQ]
      symm
      have hs1 : x ((supp x).orderEmbOfFin h j : Slot) = 1 :=
        mem_supp x _ (Finset.orderEmbOfFin_mem _ _ _)
      have h1 : x ((supp x).orderEmbOfFin h j + 21 : Slot) = 1 := by
        rcases cfg_bit x _ with hb | hb
        · exact absurd hb hQ
        · exact hb
      by_cases hz0 : ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot)
      · -- wrap-пара (21, 0)
        rw [dminus_zero_wrap S x h
          (show (21 : Slot) ∈ supp x from
            supp_mem_of_one x (21 : Slot)
              (by
                rw [hz0, show ((0 : Slot) + 21 : Slot) = (21 : Slot) from rfl] at h1
                exact h1))
          (show (0 : Slot) ∈ supp x by
            rw [← hz0]; exact Finset.orderEmbOfFin_mem _ _ _)
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 21 : Slot)) j
          (by
            rw [hz0]
            exact embInv_spec S x h hz ((0 : Slot) + 21 : Slot)
              (supp_mem_of_one x (21 : Slot)
                (show x ((0 : Slot) + 21 : Slot) = 1 by rw [← hz0]; exact h1)))
          (show ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot) from hz0)]
      · -- внутренняя занятая pred-пара
        have hnb : ((((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot) : ℕ) ≠ 0 := by
          intro hc
          rw [slot_pred_suc_eq ((supp x).orderEmbOfFin h j)] at hc
          exact hz0 (Fin.ext hc)
        exact dminus_zero_of_pair S x h ((supp x).orderEmbOfFin h j + 21 : Slot)
          h1 (by rw [slot_pred_suc_eq _]; exact hs1) hnb
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 21 : Slot)) j
          (embInv_spec S x h hz _ (supp_mem_of_one x _ h1))
          (show ((supp x).orderEmbOfFin h j : Slot)
              = (supp x).orderEmbOfFin h j + 21 + 1 from
            (slot_pred_suc_eq ((supp x).orderEmbOfFin h j)).symm)
  rw [hFull]
  exact sum_scaled_row (slaterMat S x h)
    (fun i => omega ^ (numSlots - modeOf S i % numSlots))


/-- У не-21 ребра прыжок не обёрнут. -/
theorem hnb_of_ne21 (s : Slot) (hs : s ≠ (21 : Slot)) :
    ((s + 1 : Slot) : ℕ) ≠ 0 := by
  intro hc
  have hlt : (s : ℕ) < 22 := by
    have := s.isLt
    have h22 : numSlots = 22 := rfl
    simp only [h22] at this
    exact this
  have hv : ((s + 1 : Slot) : ℕ) = ((s : ℕ) + 1) % numSlots := val_suc s
  have h22 : numSlots = 22 := rfl
  simp only [h22] at hv
  rw [hc] at hv
  have hsn : (s : ℕ) ≠ 21 := fun hq => hs (Fin.ext hq)
  omega

/-- Сумма вкладов всех рёбер через if-формы succ/pred-частей
(wrap-ребро 21 включено; знак `(−1)^(k−1) = 1` при нечётной мощности). -/
theorem bondTerm_sum_if (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hz : 0 < S.card) (hOdd : Odd S.card) :
    (∑ s : Slot, (bondTerm s *ᵥ (fun y => slater S y)) x)
      = ((2 : ℝ) : ℂ) * ∑ s : Slot,
          (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
            ∑ i, omega ^ (modeOf S i % numSlots)
              * slaterMat S x h i (embInv S x h hz s)
              * cofG (slaterMat S x h) i (embInv S x h hz s)
          else 0)
        + ((2 : ℝ) : ℂ) * ∑ s : Slot,
          (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
            ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
              * slaterMat S x h i (embInv S x h hz (s + 1 : Slot))
              * cofG (slaterMat S x h) i (embInv S x h hz (s + 1 : Slot))
          else 0) := by
  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
    (fun s => (bondTerm s *ᵥ (fun y => slater S y)) x) (Finset.mem_univ (21 : Slot))]
  rw [Finset.sum_congr rfl
    (fun s hs => bondTerm_edge_if S x h hz s (hnb_of_ne21 s (Finset.ne_of_mem_erase hs))),
    bondTerm_wrap_if S x h hz hOdd]
  rw [sum_add_distrib' (Finset.univ.erase (21 : Slot))]
  rw [← Finset.mul_sum (s := Finset.univ.erase (21 : Slot))
      (f := fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz s)
          * cofG (slaterMat S x h) i (embInv S x h hz s)
      else 0)),
    ← Finset.mul_sum (s := Finset.univ.erase (21 : Slot))
      (f := fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMat S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0))]
  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, omega ^ (modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz s)
          * cofG (slaterMat S x h) i (embInv S x h hz s)
      else 0)) (Finset.mem_univ (21 : Slot)),
    ← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, omega ^ (numSlots - modeOf S i % numSlots)
          * slaterMat S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMat S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0)) (Finset.mem_univ (21 : Slot))]
  rw [mul_add, mul_add]
  ring

/-- **Этап 4d, главный случай: диагонализация на нечётном секторе.** -/
theorem slater_diag_sector (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (hOdd : Odd S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slater S y) x
      = (∑ i : Fin S.card, (eps (modeOf S i) : ℂ)) * slater S x := by
  have hz : 0 < S.card := by
    obtain ⟨m, hm⟩ := hOdd
    omega
  rw [mulVec_sum, Finset.sum_apply, bondTerm_sum_if S x h hz hOdd,
    succ_part_scaled S x h hz, pred_part_scaled S x h hz]
  rw [slater_eq_det S x h, Finset.sum_mul]
  have e1 : ((2 : ℝ) : ℂ) * ∑ i, omega ^ (modeOf S i % numSlots) * (slaterMat S x h).det
      = ∑ i, ((2 : ℝ) : ℂ) * omega ^ (modeOf S i % numSlots) * (slaterMat S x h).det := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  have e2 : ((2 : ℝ) : ℂ) * ((∑ i, omega ^ (numSlots - modeOf S i % numSlots)) * (slaterMat S x h).det)
      = ∑ i, ((2 : ℝ) : ℂ) * omega ^ (numSlots - modeOf S i % numSlots) * (slaterMat S x h).det := by
    rw [← mul_assoc, Finset.mul_sum, Finset.sum_mul]
  have hsum : ∑ i : Fin S.card,
      (((2 : ℝ) : ℂ) * omega ^ (modeOf S i % numSlots) * (slaterMat S x h).det +
        ((2 : ℝ) : ℂ) * omega ^ (numSlots - modeOf S i % numSlots) * (slaterMat S x h).det)
    = ∑ i : Fin S.card, ((2 : ℝ) : ℂ) * omega ^ (modeOf S i % numSlots) * (slaterMat S x h).det
      + ∑ i : Fin S.card, ((2 : ℝ) : ℂ) * omega ^ (numSlots - modeOf S i % numSlots) * (slaterMat S x h).det :=
    sum_add_distrib' Finset.univ
      (fun i : Fin S.card => ((2 : ℝ) : ℂ) * omega ^ (modeOf S i % numSlots) * (slaterMat S x h).det)
      (fun i : Fin S.card => ((2 : ℝ) : ℂ) * omega ^ (numSlots - modeOf S i % numSlots) * (slaterMat S x h).det)
  rw [e1, e2, ← hsum, Finset.sum_mul]
  refine Finset.sum_congr (M := ℂ) rfl (fun i _ => ?_)
  have he := eps_omega (modeOf S i)
  rw [he]
  push_cast
  ring

/-- **Цель Stage 4 (гипотеза Odd): диагонализация.** Оператор прыжков
`A = Σ_s bondTerm s` диагонализуется слейтеровскими определителями при
нечётном `|S|`: `A·Ψ_S = (Σ_{k∈S} ε_k)·Ψ_S` на всех конфигурациях.
Основной случай — `slater_diag_sector`, чужой сектор — обнуление
(`bondTerm_mulVec_zero_hcard`). -/
theorem slater_diag_odd (S : Finset Slot) (hOdd : Odd S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slater S y)
      = (∑ i : Fin S.card, (eps (modeOf S i) : ℂ)) • (fun y => slater S y) := by
  funext x
  by_cases hxz : (supp x).card = S.card
  · exact slater_diag_sector S x hxz hOdd
  · rw [mulVec_sum, Finset.sum_apply,
      Finset.sum_eq_zero (fun s _ => bondTerm_mulVec_zero_hcard S x hxz s)]
    simp [Pi.smul_apply, slater, dif_neg hxz]

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

/-- Общая форма разложения Лапласа по столбцу (произвольный новый
столбец `v`). -/
theorem det_updateCol_laplace {k : ℕ} (M : Matrix (Fin k) (Fin k) ℂ) (j₀ : Fin k)
    (v : Fin k → ℂ) :
    (M.updateCol j₀ v).det = ∑ i, v i * cofG M i j₀ := by
  rw [← Matrix.det_transpose, ← Matrix.updateRow_transpose, cofG_det_updateRow]
  refine Finset.sum_congr rfl fun b _ => ?_
  have hcof : cofG Mᵀ j₀ b = cofG M b j₀ := by
    rw [cofG_eq_adjugate, cofG_eq_adjugate, ← Matrix.adjugate_transpose,
      Matrix.transpose_apply]
  rw [hcof]

/-- Линейность определителя по заменяемому столбцу. -/
theorem det_updateCol_smul_gen {k : ℕ} (M : Matrix (Fin k) (Fin k) ℂ) (j₀ : Fin k)
    (v : Fin k → ℂ) (c : ℂ) :
    (M.updateCol j₀ (fun i => c * v i)).det
      = c * (M.updateCol j₀ v).det := by
  rw [det_updateCol_laplace, det_updateCol_laplace, Finset.mul_sum]
  exact Finset.sum_congr rfl fun i _ => mul_assoc c (v i) (cofG M i j₀)

/-- Фаза моды `ζ` отлична от нуля. -/
theorem zeta_ne_zero : zeta ≠ 0 := by
  unfold zeta
  exact Complex.exp_ne_zero _

/-- Произведение `ζ·ω^{k}` отлично от нуля. -/
theorem zeta_omega_ne_zero (k : ℕ) : zeta * omega ^ (k % numSlots) ≠ 0 := by
  refine mul_ne_zero zeta_ne_zero ?_
  exact pow_ne_zero _ omega_ne_zero

/-- У внутреннего прыжка (не wrap) исходный сайт не равен 21, значит
`↑u₀ + 1 < 22` и `psiTwist_shift` применим. -/
theorem hu_of_hnb (u₀ : Slot) (hnb : ((u₀ + 1 : Slot) : ℕ) ≠ 0) :
    (u₀ : ℕ) + 1 < numSlots := by
  have hlt : (u₀ : ℕ) < 22 := by
    have := u₀.isLt
    have h22 : numSlots = 22 := rfl
    simp only [h22] at this
    exact this
  have hv : ((u₀ + 1 : Slot) : ℕ) = ((u₀ : ℕ) + 1) % numSlots := val_suc u₀
  have h22 : numSlots = 22 := rfl
  simp only [h22] at hv ⊢
  omega

/-- Столбцы занятых соседей `u₀, u₀+1` твистованной матрицы пропорциональны
с фазой `ζ·ω^{k_i}` (`psiTwist_shift`). -/
theorem slaterMatTwist_cols_succ_prop (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (u₀ u₁ : Slot) (hu₀ : u₀ ∈ supp x) (hu₁ : u₁ ∈ supp x) (hadj : u₁ = u₀ + 1)
    (hu : (u₀ : ℕ) + 1 < numSlots)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = u₁) (i : Fin S.card) :
    slaterMatTwist S x h i j₁
      = zeta * omega ^ (modeOf S i % numSlots) * slaterMatTwist S x h i j₀ := by
  show psiTwist (modeOf S i) (((supp x).orderEmbOfFin h j₁ : Slot))
      = zeta * omega ^ (modeOf S i % numSlots)
        * psiTwist (modeOf S i) ((supp x).orderEmbOfFin h j₀)
  rw [hj₁, hadj, hj₀, psiTwist_shift (modeOf S i) u₀ hu]

/-- Столбцы занятых сайтов `0` и `21` твистованной матрицы пропорциональны
с фазой `−ζ·ω^{k_i}` (антипериодичность, `psiTwist_shift_wrap`). -/
theorem slaterMatTwist_cols_wrap_prop (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hu0 : (0 : Slot) ∈ supp x) (hu21 : (21 : Slot) ∈ supp x)
    (j0 j21 : Fin S.card) (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0)
    (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21) (i : Fin S.card) :
    slaterMatTwist S x h i j0
      = -zeta * omega ^ (modeOf S i % numSlots) * slaterMatTwist S x h i j21 := by
  show psiTwist (modeOf S i) ((supp x).orderEmbOfFin h j0)
      = -zeta * omega ^ (modeOf S i % numSlots)
        * psiTwist (modeOf S i) ((supp x).orderEmbOfFin h j21)
  rw [hj0, hj21, show ((0 : Slot) : Slot) = ((21 : Slot) + 1 : Slot) from rfl]
  exact psiTwist_shift_wrap (modeOf S i)

/-- Сдвиг твистованной моды влево `u ↦ u−1`: фаза `(ζ·ω^{k})⁻¹`. -/
theorem psiTwist_pred_shift (k : ℕ) (u : Slot) (hu0 : (u : ℕ) ≠ 0) :
    psiTwist k (u - 1)
      = (zeta * omega ^ (k % numSlots))⁻¹ * psiTwist k u := by
  have hz : zeta * omega ^ (k % numSlots) ≠ 0 := zeta_omega_ne_zero k
  have hval : (((u - 1 : Slot) + 1 : Slot) : ℕ) = ((u : Slot) : ℕ) := by
    rw [pred_add_one u]
  have hup : ((u - 1 : Slot) : ℕ) + 1 < numSlots := by
    have hu : ((u : Slot) : ℕ) < numSlots := u.isLt
    have hup1 : ((u - 1 : Slot) : ℕ) < numSlots := (u - 1).isLt
    have h22 : numSlots = 22 := rfl
    have hv2 : (((u - 1 : Slot) + 1 : Slot) : ℕ)
        = (((u - 1 : Slot) : ℕ) + 1) % numSlots := val_suc (u - 1)
    rw [pred_add_one u] at hv2
    simp only [h22] at hv2 ⊢
    omega
  have h1 := psiTwist_shift k (u - 1) hup
  rw [pred_add_one u] at h1
  rw [h1, ← mul_assoc, inv_mul_cancel₀ hz, one_mul]

/-- Замена столбца сайта `v = u₀+1` в твистованной матрице: фаза `ζ·ω^{k_i}`. -/
theorem slaterMatTwist_replace_succ_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀mem : u₀ ∈ supp x) (v : Slot) (hvnot : v ∉ supp x)
    (hadj : v = u₀ + 1) (hnb : (v : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    (Matrix.of fun i j =>
        psiTwist (modeOf S i)
          (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀mem v hvnot).trans h) j))
      = Matrix.of fun i j =>
          if j = j₀ then zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j := by
  ext i j
  simp only [Matrix.of_apply, slaterMatTwist]
  by_cases hj : j = j₀
  · rw [hj, if_pos rfl,
      orderEmb_replace_succ_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j₀,
      if_pos rfl, hadj, psiTwist_shift (modeOf S i) u₀
        (hu_of_hnb u₀ (by rw [← hadj]; exact hnb)), hj₀]
  · rw [if_neg hj,
      orderEmb_replace_succ_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j,
      if_neg hj]

/-- Замена столбца сайта `v = u₀−1` в твистованной матрице: фаза
`(ζ·ω^{k_i})⁻¹`. -/
theorem slaterMatTwist_replace_pred_matrix (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀mem : u₀ ∈ supp x) (v : Slot) (hvnot : v ∉ supp x)
    (hadj : v = u₀ - 1) (hnb : (u₀ : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    (Matrix.of fun i j =>
        psiTwist (modeOf S i)
          (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
            ((card_replace (supp x) u₀ hU₀mem v hvnot).trans h) j))
      = Matrix.of fun i j =>
          if j = j₀ then (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j := by
  ext i j
  simp only [Matrix.of_apply, slaterMatTwist]
  by_cases hj : j = j₀
  · rw [hj, if_pos rfl,
      orderEmb_replace_pred_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j₀,
      if_pos rfl, hadj, psiTwist_pred_shift (modeOf S i) u₀ hnb, hj₀]
  · rw [if_neg hj,
      orderEmb_replace_pred_index (supp x) u₀ hU₀mem v hvnot hadj hnb h j₀ hj₀ j,
      if_neg hj]

/-- Значение Ψ̃_S на конфигурации с перескоком вправо (без цикла):
определитель матрицы со столбцом `j₀`, скалированным фазой `ζ·ω^{k_i}`. -/
theorem slaterTwist_hop_succ (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀ : u₀ ∈ supp x) (v : Slot) (hv : v ∉ supp x) (hadj : v = u₀ + 1)
    (hnb : (v : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    slaterTwist S (flipTwo u₀ v x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j).det := by
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
  have hmat' : slaterMatTwist S (flipTwo u₀ v x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMatTwist]
    rw [hproj j]
  calc slaterTwist S (flipTwo u₀ v x)
      = (slaterMatTwist S (flipTwo u₀ v x) hc).det := slaterTwist_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j).det :=
        congrArg Matrix.det
          (slaterMatTwist_replace_succ_matrix S x h u₀ hU₀ v hv hadj hnb j₀ hj₀)

/-- Значение Ψ̃_S на конфигурации с перескоком влево (без цикла):
определитель матрицы со столбцом `j₀`, скалированным фазой `(ζ·ω^{k_i})⁻¹`. -/
theorem slaterTwist_hop_pred (S : Finset Slot) (x : Cfg) (h : (supp x).card = S.card)
    (u₀ : Slot) (hU₀ : u₀ ∈ supp x) (v : Slot) (hv : v ∉ supp x) (hadj : v = u₀ - 1)
    (hnb : (u₀ : ℕ) ≠ 0) (j₀ : Fin S.card)
    (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = u₀) :
    slaterTwist S (flipTwo u₀ v x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j).det := by
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
  have hmat' : slaterMatTwist S (flipTwo u₀ v x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMatTwist]
    rw [hproj j]
  calc slaterTwist S (flipTwo u₀ v x)
      = (slaterMatTwist S (flipTwo u₀ v x) hc).det := slaterTwist_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {u₀} : Finset Slot) ∪ {v}).orderEmbOfFin
              ((card_replace (supp x) u₀ hU₀ v hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j).det :=
        congrArg Matrix.det
          (slaterMatTwist_replace_pred_matrix S x h u₀ hU₀ v hv hadj hnb j₀ hj₀)

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

/-- Вклад ребра `s` (перескок вправо, без цикла) в твистованном секторе. -/
theorem bondTerm_hop_succ_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h0 : x (s + 1 : Slot) = 0)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if j = j₀ then zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i j₀
          else slaterMatTwist S x h i j).det := by
  rw [mulVec_bondTerm,
    if_pos (show x s ≠ x (s + 1) from by rw [h1, h0]; exact one_ne_zero),
    slaterTwist_hop_succ S x h s
      (by unfold supp; simpa [h1] using Finset.mem_univ s)
      (s + 1 : Slot)
      (by intro hc
          have hmem := mem_supp _ _ hc
          rw [h0] at hmem
          exact zero_ne_one hmem)
      rfl hnb j₀ hj₀]

/-- Вклад succ-активного ребра в твистованном секторе:
`2·Σ_i ζ·ω^{k_i}·M̃_{i,j₀}·C̃_{i,j₀}`. -/
theorem bondTerm_succ_Dplus_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h0 : x (s + 1 : Slot) = 0)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i j₀ * cofG (slaterMatTwist S x h) i j₀ := by
  have heq : (Matrix.of fun (i j : Fin S.card) =>
      if j = j₀ then zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i j₀
      else slaterMatTwist S x h i j)
      = (slaterMatTwist S x h).updateCol j₀
          (fun i => zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i j₀) := by
    ext i j
    by_cases hj : j = j₀
    · subst hj; simp [Matrix.updateCol_apply, Matrix.of_apply]
    · simp [Matrix.updateCol_apply, Matrix.of_apply, hj]
  rw [bondTerm_hop_succ_twist S x h s h1 h0 hnb j₀ hj₀, heq, cofG_det_updateCol]

/-- Вклад ребра `s` (перескок влево, без цикла) в твистованном секторе. -/
theorem bondTerm_hop_pred_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x (s + 1 : Slot) = 1) (h0 : x s = 0)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₁ : Fin S.card) (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if j = j₁ then (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i j₁
          else slaterMatTwist S x h i j).det := by
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
    slaterTwist_hop_pred S x h (s + 1 : Slot)
      (by unfold supp; simpa [h1] using Finset.mem_univ (s + 1 : Slot))
      s
      (by intro hc
          have hmem := mem_supp _ _ hc
          rw [h0] at hmem
          exact zero_ne_one hmem)
      (slot_pred_suc s hs21).symm hnb j₁ hj₁]

/-- Вклад pred-активного ребра в твистованном секторе:
`2·Σ_i (ζ·ω^{k_i})⁻¹·M̃_{i,j₁}·C̃_{i,j₁}`. -/
theorem bondTerm_pred_Dminus_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x (s + 1 : Slot) = 1) (h0 : x s = 0)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₁ : Fin S.card) (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i j₁ * cofG (slaterMatTwist S x h) i j₁ := by
  have heq : (Matrix.of fun (i j : Fin S.card) =>
      if j = j₁ then (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i j₁
      else slaterMatTwist S x h i j)
      = (slaterMatTwist S x h).updateCol j₁
          (fun i => (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i j₁) := by
    ext i j
    by_cases hj : j = j₁
    · subst hj; simp [Matrix.updateCol_apply, Matrix.of_apply]
    · simp [Matrix.updateCol_apply, Matrix.of_apply, hj]
  rw [bondTerm_hop_pred_twist S x h s h1 h0 hnb j₁ hj₁, heq, cofG_det_updateCol]

/-- Значение Ψ̃_S на конфигурации с циклическим перескоком вправо
`21 ↦ 0`: определитель циклически сдвинутой твистованной матрицы. -/
theorem slaterTwist_hop_wrap_right (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hU₀ : (21 : Slot) ∈ supp x) (hv : (0 : Slot) ∉ supp x) :
    slaterTwist S (flipTwo (21 : Slot) (0 : Slot) x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if (j : ℕ) = 0
          then (-zeta) * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i (Fin.mk (S.card - 1) (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨21, hU₀⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) - 1) (by
                  have := j.isLt; omega))).det := by
  have hsupp : supp (flipTwo (21 : Slot) (0 : Slot) x)
      = ((supp x \ {21} : Finset Slot) ∪ {0}) :=
    supp_flipTwo_swap (21 : Slot) (0 : Slot) (by intro hc; exact hv (hc ▸ hU₀)) x
      (mem_supp _ _ hU₀) (not_mem_supp _ _ hv)
  have hc : (supp (flipTwo (21 : Slot) (0 : Slot) x)).card = S.card := by
    rw [hsupp]
    exact (card_replace (supp x) 21 hU₀ 0 hv).trans h
  have hproj : ∀ j : Fin S.card,
      ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc j : Slot)
        = (((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
            ((card_replace (supp x) 21 hU₀ 0 hv).trans h) j : Slot) := by
    intro j
    have hf : (fun j' : Fin S.card =>
          ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc j' : Slot))
        = ((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
            ((card_replace (supp x) 21 hU₀ 0 hv).trans h) := by
      refine Finset.orderEmbOfFin_unique
        ((card_replace (supp x) 21 hU₀ 0 hv).trans h) ?_ ?_
      · intro j'
        rw [← hsupp]
        exact Finset.orderEmbOfFin_mem _ _ _
      · intro a b hab
        exact ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc).strictMono hab
    exact congrFun hf j
  have hmat' : slaterMatTwist S (flipTwo (21 : Slot) (0 : Slot) x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
              ((card_replace (supp x) 21 hU₀ 0 hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMatTwist]
    rw [hproj j]
  calc slaterTwist S (flipTwo (21 : Slot) (0 : Slot) x)
      = (slaterMatTwist S (flipTwo (21 : Slot) (0 : Slot) x) hc).det :=
        slaterTwist_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {21} : Finset Slot) ∪ {0}).orderEmbOfFin
              ((card_replace (supp x) 21 hU₀ 0 hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if (j : ℕ) = 0
          then (-zeta) * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i (Fin.mk (S.card - 1) (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨21, hU₀⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) - 1) (by
                  have := j.isLt; omega))).det :=
        congrArg Matrix.det (slaterMatTwist_wrap21_matrix S x h hU₀ hv)

/-- Вклад wrap-ребра `21` (прыжок вправо) в твистованном секторе. -/
theorem bondTerm_hop_wrap_right_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (h1 : x (21 : Slot) = 1) (h0 : x (0 : Slot) = 0) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if (j : ℕ) = 0
          then (-zeta) * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i (Fin.mk (S.card - 1) (by
                  have h1' : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨21, by
                      unfold supp; simpa [h1] using Finset.mem_univ (21 : Slot)⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) - 1) (by
                  have := j.isLt; omega))).det := by
  have hu : (21 : Slot) ∈ supp x := by
    unfold supp; simpa [h1] using Finset.mem_univ (21 : Slot)
  have hv : (0 : Slot) ∉ supp x := by
    intro hc
    have hmem := mem_supp _ _ hc
    rw [h0] at hmem
    exact zero_ne_one hmem
  rw [mulVec_bondTerm,
    if_pos (show x (21 : Slot) ≠ x ((21 : Slot) + 1) from by
      intro hc
      rw [show ((21 : Slot) + 1) = (0 : Slot) from rfl, h1, h0] at hc
      exact one_ne_zero hc),
    show ((21 : Slot) + 1) = (0 : Slot) from rfl,
    slaterTwist_hop_wrap_right S x h hu hv]

/-- Значение Ψ̃_S на конфигурации с циклическим перескоком влево
`0 ↦ 21`. -/
theorem slaterTwist_hop_wrap_left (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hU₀ : (0 : Slot) ∈ supp x) (hv : (21 : Slot) ∉ supp x) :
    slaterTwist S (flipTwo (21 : Slot) (0 : Slot) x)
      = (Matrix.of fun (i j : Fin S.card) =>
          if hj : (j : ℕ) = S.card - 1
          then (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i (Fin.mk 0 (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨0, hU₀⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) + 1) (by
                  have := j.isLt; omega))).det := by
  have hsupp : supp (flipTwo (21 : Slot) (0 : Slot) x)
      = ((supp x \ {0} : Finset Slot) ∪ {21}) :=
    supp_flipTwo_swap (0 : Slot) (21 : Slot) (by intro hc; exact hv (hc ▸ hU₀)) x
      (mem_supp _ _ hU₀) (not_mem_supp _ _ hv)
  have hc : (supp (flipTwo (21 : Slot) (0 : Slot) x)).card = S.card := by
    rw [hsupp]
    exact (card_replace (supp x) 0 hU₀ 21 hv).trans h
  have hproj : ∀ j : Fin S.card,
      ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc j : Slot)
        = (((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
            ((card_replace (supp x) 0 hU₀ 21 hv).trans h) j : Slot) := by
    intro j
    have hf : (fun j' : Fin S.card =>
          ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc j' : Slot))
        = ((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
            ((card_replace (supp x) 0 hU₀ 21 hv).trans h) := by
      refine Finset.orderEmbOfFin_unique
        ((card_replace (supp x) 0 hU₀ 21 hv).trans h) ?_ ?_
      · intro j'
        rw [← hsupp]
        exact Finset.orderEmbOfFin_mem _ _ _
      · intro a b hab
        exact ((supp (flipTwo (21 : Slot) (0 : Slot) x)).orderEmbOfFin hc).strictMono hab
    exact congrFun hf j
  have hmat' : slaterMatTwist S (flipTwo (21 : Slot) (0 : Slot) x) hc
      = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
              ((card_replace (supp x) 0 hU₀ 21 hv).trans h) j)) := by
    ext i j
    simp only [Matrix.of_apply, slaterMatTwist]
    rw [hproj j]
  calc slaterTwist S (flipTwo (21 : Slot) (0 : Slot) x)
      = (slaterMatTwist S (flipTwo (21 : Slot) (0 : Slot) x) hc).det :=
        slaterTwist_eq_det S _ hc
    _ = (Matrix.of fun (i j : Fin S.card) =>
          psiTwist (modeOf S i)
            (((supp x \ {0} : Finset Slot) ∪ {21}).orderEmbOfFin
              ((card_replace (supp x) 0 hU₀ 21 hv).trans h) j)).det := by
        rw [hmat']
    _ = (Matrix.of fun (i j : Fin S.card) =>
          if hj : (j : ℕ) = S.card - 1
          then (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i (Fin.mk 0 (by
                  have h1 : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨0, hU₀⟩
                  omega))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) + 1) (by
                  have := j.isLt; omega))).det :=
        congrArg Matrix.det (slaterMatTwist_wrap01_matrix S x h hU₀ hv)

/-- Вклад wrap-ребра `21` (прыжок влево) в твистованном секторе. -/
theorem bondTerm_hop_wrap_left_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (h1 : x (0 : Slot) = 1) (h0 : x (21 : Slot) = 0) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (Matrix.of fun (i j : Fin S.card) =>
          if hj : (j : ℕ) = S.card - 1
          then (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i (Fin.mk 0 (by
                  have h1' : 0 < S.card := by
                    rw [← h]; exact Finset.card_pos.mpr ⟨0, by
                      unfold supp; simpa [h1] using Finset.mem_univ (0 : Slot)⟩
                  exact h1'))
          else slaterMatTwist S x h i (Fin.mk ((j : ℕ) + 1) (by
                  have := j.isLt; omega))).det := by
  have hu : (0 : Slot) ∈ supp x := by
    unfold supp; simpa [h1] using Finset.mem_univ (0 : Slot)
  have hv : (21 : Slot) ∉ supp x := by
    intro hc
    have hmem := mem_supp _ _ hc
    rw [h0] at hmem
    exact zero_ne_one hmem
  rw [mulVec_bondTerm,
    if_pos (show x (21 : Slot) ≠ x ((21 : Slot) + 1) from by
      intro hc
      rw [show ((21 : Slot) + 1) = (0 : Slot) from rfl, h0, h1] at hc
      exact zero_ne_one hc),
    show ((21 : Slot) + 1) = (0 : Slot) from rfl,
    slaterTwist_hop_wrap_left S x h hu hv]

/-- Занятая succ-пара в твистованном секторе: `D⁺(j₀) = 0`. -/
theorem dplus_zero_of_pair_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h2 : x (s + 1 : Slot) = 1)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (∑ i, zeta * omega ^ (modeOf S i % numSlots)
        * slaterMatTwist S x h i j₀ * cofG (slaterMatTwist S x h) i j₀) = 0 := by
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
    have hpos : (s : ℕ) ≠ ((s : ℕ) + 1) % numSlots := by
      have hlink : ((s : ℕ) + 1) % numSlots = ((s : ℕ) + 1) % 22 := by congr 1
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
  rw [slaterMatTwist_cols_succ_prop S x h s (s + 1 : Slot) hs hs1 rfl
    (hu_of_hnb s hnb) j₀ j₁ hj₀ hj₁ i]

/-- Занятая succ-пара в твистованном секторе: `D⁻(j₁) = 0`. -/
theorem dminus_zero_of_pair_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (s : Slot) (h1 : x s = 1) (h2 : x (s + 1 : Slot) = 1)
    (hnb : ((s + 1 : Slot) : ℕ) ≠ 0)
    (j₀ j₁ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = s)
    (hj₁ : ((supp x).orderEmbOfFin h j₁ : Slot) = s + 1) :
    (∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
        * slaterMatTwist S x h i j₁ * cofG (slaterMatTwist S x h) i j₁) = 0 := by
  have hs : s ∈ supp x := by rw [← hj₀]; exact Finset.orderEmbOfFin_mem _ _ _
  have hs1 : (s + 1 : Slot) ∈ supp x := by
    rw [← hj₁]; exact Finset.orderEmbOfFin_mem _ _ _
  rw [← cofG_det_updateCol]
  refine det_updateCol_eq_col_zero _ j₁ j₀ _
    (pos_ne_of_ne S x h (slot_ne_suc s).symm hj₁ hj₀) ?_
  intro i
  rw [slaterMatTwist_cols_succ_prop S x h s (s + 1 : Slot) hs hs1 rfl
    (hu_of_hnb s hnb) j₀ j₁ hj₀ hj₁ i]
  rw [← mul_assoc, inv_mul_cancel₀ (zeta_omega_ne_zero (modeOf S i)), one_mul]

/-- Собственная копия (в mathlib 308445d `Finset.sum_neg_distrib` удалена):
сумма противоположных равна противоположному суммы. -/
theorem sum_neg_distrib' {ι M : Type*} [AddCommGroup M] (u : Finset ι) (f : ι → M) :
    ∑ i ∈ u, (-f i) = -∑ i ∈ u, f i := by
  simpa using (map_sum (AddMonoidHom.neg : M →+ M) u f).symm

/-- Wrap-пара в твистованном секторе, `(−ζ)`-форма: `D⁺(j₂₁) = 0`. -/
theorem dplus_zero_wrap_twist_neg (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, -zeta * omega ^ (modeOf S i % numSlots)
        * slaterMatTwist S x h i j21 * cofG (slaterMatTwist S x h) i j21) = 0 := by
  rw [← cofG_det_updateCol]
  have hne : j21 ≠ j0 := by
    intro hc
    have h1 : ((21 : Slot) : ℕ) = ((0 : Slot) : ℕ) := by
      rw [← hj21, ← hj0, hc]
    norm_num at h1
  refine det_updateCol_eq_col_zero _ j21 j0 _ hne ?_
  intro i
  rw [slaterMatTwist_cols_wrap_prop S x h h0 h21 j0 j21 hj0 hj21 i]

/-- Wrap-пара в твистованном секторе: `D⁺(j₂₁) = 0` (знак через neg-мост). -/
theorem dplus_zero_wrap_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, zeta * omega ^ (modeOf S i % numSlots)
        * slaterMatTwist S x h i j21 * cofG (slaterMatTwist S x h) i j21) = 0 := by
  have h := dplus_zero_wrap_twist_neg S x h h21 h0 j21 j0 hj21 hj0
  simp only [neg_mul] at h
  rw [← neg_eq_zero, ← sum_neg_distrib' Finset.univ]
  exact h

/-- Wrap-пара в твистованном секторе, `(−ζ)`-форма: `D⁻(j₀) = 0`. -/
theorem dminus_zero_wrap_twist_neg (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
        * slaterMatTwist S x h i j0 * cofG (slaterMatTwist S x h) i j0) = 0 := by
  rw [← cofG_det_updateCol]
  have hne : j0 ≠ j21 := by
    intro hc
    have h1 : ((21 : Slot) : ℕ) = ((0 : Slot) : ℕ) := by
      rw [← hj21, ← hj0, ← hc]
    norm_num at h1
  refine det_updateCol_eq_col_zero _ j0 j21 _ hne ?_
  intro i
  simp only [slaterMatTwist, Matrix.of_apply, hj0, hj21]
  exact (psiTwist_pred_wrap (modeOf S i)).symm

/-- Wrap-пара в твистованном секторе: `D⁻(j₀) = 0` (знак через neg-мост). -/
theorem dminus_zero_wrap_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h21 : (21 : Slot) ∈ supp x) (h0 : (0 : Slot) ∈ supp x)
    (j21 j0 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = 21)
    (hj0 : ((supp x).orderEmbOfFin h j0 : Slot) = 0) :
    (∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
        * slaterMatTwist S x h i j0 * cofG (slaterMatTwist S x h) i j0) = 0 := by
  have h := dminus_zero_wrap_twist_neg S x h h21 h0 j21 j0 hj21 hj0
  simp only [inv_neg, mul_inv, neg_mul] at h
  rw [← neg_eq_zero, ← sum_neg_distrib' Finset.univ]
  simp only [mul_inv]
  exact h

/-- Вклад wrap-ребра `21` (прыжок вправо) в твистованном секторе:
`2·(−1)^{k−1}·Σ_i (−ζ)·ω^{k_i}·M̃_{i,j₂₁}·C̃_{i,j₂₁}`. -/
theorem bondTerm_21_right_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h1 : x (21 : Slot) = 1) (h0 : x (0 : Slot) = 0)
    (j21 : Fin S.card) (hj21 : ((supp x).orderEmbOfFin h j21 : Slot) = (21 : Slot)) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (((-1 : ℂ) ^ (S.card - 1))
          * ∑ i, -zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i j21 * cofG (slaterMatTwist S x h) i j21) := by
  have hu21 : (21 : Slot) ∈ supp x := by
    unfold supp; simpa [h1] using Finset.mem_univ (21 : Slot)
  have hpos0 : 0 < S.card := by
    rw [← h]
    exact Finset.card_pos.mpr ⟨(21 : Slot), hu21⟩
  have hje : j21 = Fin.mk (S.card - 1) (by
      have hp : 0 < #(supp x) := Finset.card_pos.mpr ⟨(21 : Slot), hu21⟩
      omega) := by
    refine ((supp x).orderEmbOfFin h).injective ?_
    rw [hj21, pos_last_max S x h hu21 j21 hj21]
  rw [hje, bondTerm_hop_wrap_right_twist S x h h1 h0,
    cofG_det_cyclic_right (slaterMatTwist S x h) hpos0
      (fun i => -zeta * omega ^ (modeOf S i % numSlots))]

/-- Вклад wrap-ребра `21` (прыжок влево) в твистованном секторе:
`2·(−1)^{k−1}·Σ_i (−ζ)⁻¹·(ω^{k_i})⁻¹·M̃_{i,j₀}·C̃_{i,j₀}`. -/
theorem bondTerm_21_pred_left_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (h1 : x (0 : Slot) = 1) (h0 : x (21 : Slot) = 0)
    (j₀ : Fin S.card) (hj₀ : ((supp x).orderEmbOfFin h j₀ : Slot) = (0 : Slot)) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (((-1 : ℂ) ^ (S.card - 1))
          * ∑ i, (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i j₀ * cofG (slaterMatTwist S x h) i j₀) := by
  have hu0 : (0 : Slot) ∈ supp x := supp_mem_of_one x (0 : Slot) h1
  have hpos0 : 0 < S.card := by
    rw [← h]; exact Finset.card_pos.mpr ⟨(0 : Slot), hu0⟩
  have hje : j₀ = Fin.mk 0 (by
      have hp : 0 < S.card := by omega
      omega) := by
    refine ((supp x).orderEmbOfFin h).injective ?_
    rw [hj₀, ((orderEmbOfFin_min0 (supp x) hu0 h).1).symm]
  rw [hje, bondTerm_hop_wrap_left_twist S x h h1 h0,
    cofG_det_cyclic_left (slaterMatTwist S x h) hpos0
      (fun i => (-zeta)⁻¹ * (omega ^ (modeOf S i % numSlots))⁻¹)]

/-- Спектр кольца в **чётных** секторах (граничные условия Либа–Шульца–Маттиса):
твистованная мода `ψ̃_k(u) = ζ^u·ω^{ku}` — собственная функция прыжкового
оператора с собственным значением `2(ζω^k + ζ^{−1}ω^{−k})
= 4·cos(π(2k+1)/22)`, а не `eps k = 4·cos(2πk/22)`. Численная проверка
(полный перебор N = 4, 6, 8; выборка N = 22; scripts/verify_eps_twist.py):
с `epsTwist` нарушений нет, с `eps` — есть. -/
noncomputable def epsTwist (k : ℕ) : ℂ :=
  2 * (zeta * omega ^ (k % numSlots) + (zeta * omega ^ (k % numSlots))⁻¹)

/-- Знак циклической перестановки при чётной ненулевой мощности:
`(-1)^(k-1) = −1`. -/
theorem neg_one_pow_pred_odd {k : ℕ} (hEven : Even k) (hk : 0 < k) :
    ((-1 : ℂ) ^ (k - 1)) = -1 := by
  obtain ⟨m, rfl⟩ := hEven
  have hm : 1 ≤ m := by omega
  rw [show m + m - 1 = 2 * (m - 1) + 1 from by omega, pow_add, pow_mul, pow_two,
    neg_mul, one_mul, neg_neg, one_pow, one_mul, pow_one]

/-- Вклад внутреннего ребра (без цикла) в твистованном секторе, if-форма. -/
theorem bondTerm_edge_if_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hz : 0 < S.card) (s : Slot) (hnb : ((s + 1 : Slot) : ℕ) ≠ 0) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
          ∑ i, zeta * omega ^ (modeOf S i % numSlots)
            * slaterMatTwist S x h i (embInv S x h hz s)
            * cofG (slaterMatTwist S x h) i (embInv S x h hz s)
        else 0)
        + ((2 : ℝ) : ℂ) * (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
          ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
            * slaterMatTwist S x h i (embInv S x h hz (s + 1 : Slot))
            * cofG (slaterMatTwist S x h) i (embInv S x h hz (s + 1 : Slot))
        else 0) := by
  rcases cfg_bit x s with hs0 | hs1
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · rw [bondTerm_blocked s _ x (show x s = x (s + 1 : Slot) from hs0.trans ht0.symm),
        if_neg (fun hc => zero_ne_one (hs0.symm.trans hc.1)),
        if_neg (fun hc => zero_ne_one (ht0.symm.trans hc.2))]
      norm_num
    · rw [if_neg (fun hc => zero_ne_one (hs0.symm.trans hc.1)),
        if_pos (⟨hs0, ht1⟩ : x s = 0 ∧ x (s + 1 : Slot) = 1)]
      rw [bondTerm_pred_Dminus_twist S x h s ht1 hs0 hnb
        (embInv S x h hz (s + 1 : Slot))
        (embInv_spec S x h hz (s + 1 : Slot) (supp_mem_of_one x (s + 1 : Slot) ht1))]
      rw [mul_zero, zero_add]
  · rcases cfg_bit x (s + 1 : Slot) with ht0 | ht1
    · rw [if_pos (⟨hs1, ht0⟩ : x s = 1 ∧ x (s + 1 : Slot) = 0),
        if_neg (fun hc => one_ne_zero (hs1.symm.trans hc.1))]
      rw [bondTerm_succ_Dplus_twist S x h s hs1 ht0 hnb (embInv S x h hz s)
        (embInv_spec S x h hz s (supp_mem_of_one x s hs1))]
      rw [mul_zero, add_zero]
    · rw [bondTerm_blocked s _ x (show x s = x (s + 1 : Slot) from hs1.trans ht1.symm),
        if_neg (fun hc => zero_ne_one (ht1.symm.trans hc.2).symm),
        if_neg (fun hc => zero_ne_one (hs1.symm.trans hc.1).symm)]
      norm_num

/-- Вклад wrap-ребра `21` в твистованном секторе, if-форма (знак
`(-1)^(k−1) = −1` при чётной ненулевой мощности компенсирует лишний минус
границы). -/
theorem bondTerm_wrap_if_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card)
    (hz : 0 < S.card) (hEven : Even S.card) :
    (bondTerm (21 : Slot) *ᵥ (fun y => slaterTwist S y)) x
      = ((2 : ℝ) : ℂ) * (if x (21 : Slot) = 1 ∧ x ((21 : Slot) + 1 : Slot) = 0 then
          ∑ i, zeta * omega ^ (modeOf S i % numSlots)
            * slaterMatTwist S x h i (embInv S x h hz (21 : Slot))
            * cofG (slaterMatTwist S x h) i (embInv S x h hz (21 : Slot))
        else 0)
        + ((2 : ℝ) : ℂ) * (if x (21 : Slot) = 0 ∧ x ((21 : Slot) + 1 : Slot) = 1 then
          ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
            * slaterMatTwist S x h i (embInv S x h hz ((21 : Slot) + 1 : Slot))
            * cofG (slaterMatTwist S x h) i (embInv S x h hz ((21 : Slot) + 1 : Slot))
        else 0) := by
  rcases cfg_bit x (21 : Slot) with hs0 | hs1
  · rcases cfg_bit x (0 : Slot) with ht0 | ht1
    · rw [bondTerm_blocked (21 : Slot) _ x
        (show x (21 : Slot) = x ((21 : Slot) + 1 : Slot) from hs0.trans ht0.symm),
        if_neg (fun hc => zero_ne_one (hs0.symm.trans hc.1)),
        if_neg (fun hc => zero_ne_one (ht0.symm.trans hc.2))]
      norm_num
    · rw [if_neg (fun hc => zero_ne_one (hs0.symm.trans hc.1)),
        if_pos (⟨hs0, ht1⟩ : x (21 : Slot) = 0 ∧ x ((21 : Slot) + 1 : Slot) = 1)]
      rw [bondTerm_21_pred_left_twist S x h ht1 hs0
        (embInv S x h hz ((21 : Slot) + 1 : Slot))
        (show ((supp x).orderEmbOfFin h
            (embInv S x h hz ((21 : Slot) + 1 : Slot)) : Slot) = (0 : Slot) from
          embInv_spec S x h hz ((21 : Slot) + 1 : Slot)
            (show ((21 : Slot) + 1 : Slot) ∈ supp x from
              supp_mem_of_one x (0 : Slot) ht1)),
        neg_one_pow_pred_odd hEven hz, neg_mul, one_mul, ← sum_neg_distrib' Finset.univ]
      simp only [inv_neg, neg_mul, neg_neg, mul_inv, mul_assoc]
      rw [mul_zero, zero_add]
  · rcases cfg_bit x (0 : Slot) with ht0 | ht1
    · rw [if_pos (⟨hs1, ht0⟩ : x (21 : Slot) = 1 ∧ x ((21 : Slot) + 1 : Slot) = 0),
        if_neg (fun hc => one_ne_zero (hs1.symm.trans hc.1))]
      rw [bondTerm_21_right_twist S x h hs1 ht0 (embInv S x h hz (21 : Slot))
        (embInv_spec S x h hz (21 : Slot) (supp_mem_of_one x (21 : Slot) hs1)),
        neg_one_pow_pred_odd hEven hz, neg_mul, one_mul, ← sum_neg_distrib' Finset.univ]
      simp only [neg_mul, neg_neg]
      rw [mul_zero, add_zero]
    · rw [bondTerm_blocked (21 : Slot) _ x
        (show x (21 : Slot) = x ((21 : Slot) + 1 : Slot) from hs1.trans ht1.symm),
        if_neg (fun hc => zero_ne_one (ht1.symm.trans hc.2).symm),
        if_neg (fun hc => zero_ne_one (hs1.symm.trans hc.1).symm)]
      norm_num

/-- Succ-сумма твистованного сектора сворачивается в `ζ·ω^{k}`-скалированный
определитель. -/
theorem succ_part_scaled_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hz : 0 < S.card) :
    (∑ s : Slot, (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i (embInv S x h hz s)
          * cofG (slaterMatTwist S x h) i (embInv S x h hz s)
      else 0))
      = (∑ i, zeta * omega ^ (modeOf S i % numSlots))
          * (slaterMatTwist S x h).det := by
  rw [succ_sum_reindex S x h hz (fun u => ∑ i, zeta * omega ^ (modeOf S i % numSlots)
      * slaterMatTwist S x h i (embInv S x h hz u)
      * cofG (slaterMatTwist S x h) i (embInv S x h hz u))]
  have hFull : (∑ j : Fin S.card,
      (if x ((supp x).orderEmbOfFin h j + 1 : Slot) = 0 then
        ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i
            (embInv S x h hz ((supp x).orderEmbOfFin h j : Slot))
          * cofG (slaterMatTwist S x h) i
            (embInv S x h hz ((supp x).orderEmbOfFin h j : Slot))
      else 0))
      = ∑ j : Fin S.card,
        ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i j * cofG (slaterMatTwist S x h) i j := by
    refine Finset.sum_congr (M := ℂ) rfl fun j _ => ?_
    rw [embInv_emb S x h hz j]
    by_cases hQ : x ((supp x).orderEmbOfFin h j + 1 : Slot) = 0
    · rw [if_pos hQ]
    · rw [if_neg hQ]
      symm
      have h1 : x ((supp x).orderEmbOfFin h j : Slot) = 1 :=
        mem_supp x _ (Finset.orderEmbOfFin_mem _ _ _)
      have h2 : x ((supp x).orderEmbOfFin h j + 1 : Slot) = 1 := by
        rcases cfg_bit x _ with hb | hb
        · exact absurd hb hQ
        · exact hb
      by_cases hemb21 : ((supp x).orderEmbOfFin h j : Slot) = (21 : Slot)
      · rw [dplus_zero_wrap_twist S x h
          (show (21 : Slot) ∈ supp x by
            rw [← hemb21]; exact Finset.orderEmbOfFin_mem _ _ _)
          (show (0 : Slot) ∈ supp x from
            supp_mem_of_one x (0 : Slot)
              (by
                rw [hemb21, show ((21 : Slot) + 1 : Slot) = (0 : Slot) from rfl] at h2
                exact h2))
          j (embInv S x h hz ((supp x).orderEmbOfFin h j + 1 : Slot))
          (show ((supp x).orderEmbOfFin h j : Slot) = (21 : Slot) from hemb21)
          (by
            rw [hemb21]
            exact embInv_spec S x h hz ((21 : Slot) + 1 : Slot)
              (supp_mem_of_one x (0 : Slot)
                (show x ((21 : Slot) + 1 : Slot) = 1 by rw [← hemb21]; exact h2)))]
      · have hnb : ((((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) : ℕ) ≠ 0 := by
          intro hc
          apply hemb21
          have hval : ((supp x).orderEmbOfFin h j : ℕ) = 21 := by
            have hv0 : ((supp x).orderEmbOfFin h j : ℕ) < 22 :=
              (supp x).orderEmbOfFin h j |>.isLt
            have h22 : numSlots = 22 := rfl
            have hv2 : ((((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) : ℕ)
                = (((supp x).orderEmbOfFin h j : ℕ) + 1) % numSlots :=
              val_suc ((supp x).orderEmbOfFin h j)
            rw [hc] at hv2
            simp only [h22] at hv2
            omega
          exact Fin.ext hval
        exact dplus_zero_of_pair_twist S x h _ h1 h2 hnb j
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 1 : Slot))
          rfl
          (embInv_spec S x h hz _ (supp_mem_of_one x _ h2))
  rw [hFull]
  exact sum_scaled_row (slaterMatTwist S x h)
    (fun i => zeta * omega ^ (modeOf S i % numSlots))

/-- Pred-сумма твистованного сектора сворачивается в `(ζ·ω^{k})⁻¹`-скалированный
определитель. -/
theorem pred_part_scaled_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hz : 0 < S.card) :
    (∑ s : Slot, (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMatTwist S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0))
      = (∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹)
          * (slaterMatTwist S x h).det := by
  rw [pred_sum_reindex S x h hz (fun u => ∑ i,
      (zeta * omega ^ (modeOf S i % numSlots))⁻¹
      * slaterMatTwist S x h i (embInv S x h hz (u + 1 : Slot))
      * cofG (slaterMatTwist S x h) i (embInv S x h hz (u + 1 : Slot)))]
  have hFull : (∑ j : Fin S.card,
      (if x ((supp x).orderEmbOfFin h j + 21 : Slot) = 0 then
        ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i
            (embInv S x h hz (((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot))
          * cofG (slaterMatTwist S x h) i
            (embInv S x h hz (((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot))
      else 0))
      = ∑ j : Fin S.card,
        ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i j * cofG (slaterMatTwist S x h) i j := by
    refine Finset.sum_congr (M := ℂ) rfl fun j _ => ?_
    rw [slot_pred_suc_eq ((supp x).orderEmbOfFin h j), embInv_emb S x h hz j]
    by_cases hQ : x ((supp x).orderEmbOfFin h j + 21 : Slot) = 0
    · rw [if_pos hQ]
    · rw [if_neg hQ]
      symm
      have hs1 : x ((supp x).orderEmbOfFin h j : Slot) = 1 :=
        mem_supp x _ (Finset.orderEmbOfFin_mem _ _ _)
      have h1 : x ((supp x).orderEmbOfFin h j + 21 : Slot) = 1 := by
        rcases cfg_bit x _ with hb | hb
        · exact absurd hb hQ
        · exact hb
      by_cases hz0 : ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot)
      · rw [dminus_zero_wrap_twist S x h
          (show (21 : Slot) ∈ supp x from
            supp_mem_of_one x (21 : Slot)
              (by
                rw [hz0, show ((0 : Slot) + 21 : Slot) = (21 : Slot) from rfl] at h1
                exact h1))
          (show (0 : Slot) ∈ supp x by
            rw [← hz0]; exact Finset.orderEmbOfFin_mem _ _ _)
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 21 : Slot)) j
          (by
            rw [hz0]
            exact embInv_spec S x h hz ((0 : Slot) + 21 : Slot)
              (supp_mem_of_one x (21 : Slot)
                (show x ((0 : Slot) + 21 : Slot) = 1 by rw [← hz0]; exact h1)))
          (show ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot) from hz0)]
      · -- внутренняя занятая pred-пара
        have hnb : ((((supp x).orderEmbOfFin h j + 21 : Slot) + 1 : Slot) : ℕ) ≠ 0 := by
          intro hc
          rw [slot_pred_suc_eq ((supp x).orderEmbOfFin h j)] at hc
          exact hz0 (Fin.ext hc)
        exact dminus_zero_of_pair_twist S x h ((supp x).orderEmbOfFin h j + 21 : Slot)
          h1 (by rw [slot_pred_suc_eq _]; exact hs1) hnb
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 21 : Slot)) j
          (embInv_spec S x h hz _ (supp_mem_of_one x _ h1))
          (show ((supp x).orderEmbOfFin h j : Slot)
              = (supp x).orderEmbOfFin h j + 21 + 1 from
            (slot_pred_suc_eq ((supp x).orderEmbOfFin h j)).symm)
  rw [hFull]
  exact sum_scaled_row (slaterMatTwist S x h)
    (fun i => (zeta * omega ^ (modeOf S i % numSlots))⁻¹)

/-- Сумма вкладов всех рёбер в твистованном секторе через if-формы. -/
theorem bondTerm_sum_if_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hz : 0 < S.card) (hEven : Even S.card) :
    (∑ s : Slot, (bondTerm s *ᵥ (fun y => slaterTwist S y)) x)
      = ((2 : ℝ) : ℂ) * ∑ s : Slot,
          (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
            ∑ i, zeta * omega ^ (modeOf S i % numSlots)
              * slaterMatTwist S x h i (embInv S x h hz s)
              * cofG (slaterMatTwist S x h) i (embInv S x h hz s)
          else 0)
        + ((2 : ℝ) : ℂ) * ∑ s : Slot,
          (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
            ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
              * slaterMatTwist S x h i (embInv S x h hz (s + 1 : Slot))
              * cofG (slaterMatTwist S x h) i (embInv S x h hz (s + 1 : Slot))
          else 0) := by
  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
    (fun s => (bondTerm s *ᵥ (fun y => slaterTwist S y)) x) (Finset.mem_univ (21 : Slot))]
  rw [Finset.sum_congr rfl
    (fun s hs => bondTerm_edge_if_twist S x h hz s (hnb_of_ne21 s (Finset.ne_of_mem_erase hs))),
    bondTerm_wrap_if_twist S x h hz hEven]
  rw [sum_add_distrib' (Finset.univ.erase (21 : Slot))]
  rw [← Finset.mul_sum (s := Finset.univ.erase (21 : Slot))
      (f := fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i (embInv S x h hz s)
          * cofG (slaterMatTwist S x h) i (embInv S x h hz s)
      else 0)),
    ← Finset.mul_sum (s := Finset.univ.erase (21 : Slot))
      (f := fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMatTwist S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0))]
  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
        ∑ i, zeta * omega ^ (modeOf S i % numSlots)
          * slaterMatTwist S x h i (embInv S x h hz s)
          * cofG (slaterMatTwist S x h) i (embInv S x h hz s)
      else 0)) (Finset.mem_univ (21 : Slot)),
    ← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
        ∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹
          * slaterMatTwist S x h i (embInv S x h hz (s + 1 : Slot))
          * cofG (slaterMatTwist S x h) i (embInv S x h hz (s + 1 : Slot))
      else 0)) (Finset.mem_univ (21 : Slot))]
  rw [mul_add, mul_add]
  ring

/-- **Этап 4d, главный случай: диагонализация на чётном твистованном секторе.** -/
theorem slater_diag_sector_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hEven : Even S.card) (hpos : 0 < S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slaterTwist S y) x
      = (∑ i : Fin S.card, epsTwist (modeOf S i)) * slaterTwist S x := by
  rw [mulVec_sum, Finset.sum_apply, bondTerm_sum_if_twist S x h hpos hEven,
    succ_part_scaled_twist S x h hpos, pred_part_scaled_twist S x h hpos]
  rw [slaterTwist_eq_det S x h]
  have e1 : ((2 : ℝ) : ℂ) * ((∑ i, zeta * omega ^ (modeOf S i % numSlots))
      * (slaterMatTwist S x h).det)
      = ∑ i, ((2 : ℝ) : ℂ) * zeta * omega ^ (modeOf S i % numSlots)
        * (slaterMatTwist S x h).det := by
    rw [Finset.sum_mul, Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  have e2 : ((2 : ℝ) : ℂ) * ((∑ i, (zeta * omega ^ (modeOf S i % numSlots))⁻¹)
      * (slaterMatTwist S x h).det)
      = ∑ i, ((2 : ℝ) : ℂ) * (zeta * omega ^ (modeOf S i % numSlots))⁻¹
        * (slaterMatTwist S x h).det := by
    rw [Finset.sum_mul, Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  rw [e1, e2, Finset.sum_mul]
  simp only [epsTwist, add_mul, mul_add]
  rw [sum_add_distrib']
  have h1 : ∑ i, ((2 : ℝ) : ℂ) * zeta * omega ^ (modeOf S i % numSlots)
      * (slaterMatTwist S x h).det
      = ∑ i, 2 * (zeta * omega ^ (modeOf S i % numSlots))
        * (slaterMatTwist S x h).det := by
    refine Finset.sum_congr rfl fun i _ => ?_
    push_cast
    ring
  have h2 : ∑ i, ((2 : ℝ) : ℂ) * (zeta * omega ^ (modeOf S i % numSlots))⁻¹
      * (slaterMatTwist S x h).det
      = ∑ i, 2 * (zeta * omega ^ (modeOf S i % numSlots))⁻¹
        * (slaterMatTwist S x h).det := by
    refine Finset.sum_congr rfl fun i _ => ?_
    push_cast
    ring
  rw [h1, h2]

/-- При несовпадающей мощности носителя вклад каждого ребра нулевой
и в твистованном секторе. -/
theorem bondTerm_mulVec_zero_hcard_twist (S : Finset Slot) (x : Cfg)
    (hxz : (supp x).card ≠ S.card) (s : Slot) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x = 0 := by
  rw [mulVec_bondTerm]
  by_cases hP : x s ≠ x (s + 1 : Slot)
  · rw [if_pos hP, slaterTwist]
    split
    · next hc =>
        exact absurd ((supp_card_flipTwo_suc x s hP).symm.trans hc) hxz
    · rw [mul_zero]
  · rw [if_neg hP]

/-- **Цель для чётных секторов (твист).** С твистованными модами
`ψ̃_k(u) = ζ^u·ψ_k(u)` (`ζ^{22} = −1`, антипериодическое условие) оператор
прыжков диагонален и в чётных секторах: знак `(−1)^{k−1}` границы
компенсируется фазой `ζ^{±1}`, а спектр задаёт `epsTwist` (эффект
Либа–Шульца–Маттиса). Гипотеза `hS` — сектор непуст (как `hOdd` в
нечётном случае; пустой сектор физически не возникает). -/
theorem slater_diag_even_twist (S : Finset Slot) (hS : 0 < S.card) (hEven : Even S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slaterTwist S y)
      = (∑ i : Fin S.card, (epsTwist (modeOf S i))) • (fun y => slaterTwist S y) := by
  funext x
  by_cases hxz : (supp x).card = S.card
  · exact slater_diag_sector_twist S x hxz hEven hS
  · rw [mulVec_sum, Finset.sum_apply,
      Finset.sum_eq_zero (fun s _ => bondTerm_mulVec_zero_hcard_twist S x hxz s)]
    simp [Pi.smul_apply, slaterTwist, dif_neg hxz]

/-- Развёртка произведения сумм по всем функциям: `∏_i Σ_u f(i,u) =
Σ_{g : Fin k → Fin n} ∏_i f(i, g(i))`. -/
theorem prod_univ_sum' {k n : ℕ} (f : Fin k → Fin n → ℂ) :
    (∏ i, ∑ u, f i u) = ∑ g : Fin k → Fin n, ∏ i, f i (g i) := by
  rw [Finset.prod_univ_sum, Fintype.piFinset_univ]

/-- **Форма Мура для определителя произведения**: `det (A·Bᵀ) =
Σ_{f : Fin k → Fin n} (∏_i A_{i,f(i)})·det(B_{·,f})`. При не-инъективном `f`
второй множитель нулевой автоматически (два равных столбца в `B_{·,f}`);
при инъективном — это Коши–Бине до группировки по образам `f`. -/
theorem det_mul_transpose_sum {k n : ℕ} (A B : Matrix (Fin k) (Fin n) ℂ) :
    (A * Bᵀ).det = ∑ f : Fin k → Fin n, (∏ i, A i (f i)) * (B.submatrix id f).det := by
  rw [← Matrix.det_transpose, Matrix.transpose_mul, Matrix.transpose_transpose,
    Matrix.det_apply']
  simp only [Matrix.mul_apply, Matrix.transpose_apply, dotProduct]
  have hexpand : ∀ σ : Equiv.Perm (Fin k),
      Equiv.Perm.sign σ * ∏ i, ∑ u, B (σ i) u * A i u
        = ∑ g : Fin k → Fin n,
          Equiv.Perm.sign σ * ∏ i, B (σ i) (g i) * A i (g i) := by
    intro σ
    rw [prod_univ_sum' (f := fun (i : Fin k) (u : Fin n) => B (σ i) u * A i u),
      Finset.mul_sum]
  rw [Finset.sum_congr rfl (fun σ (_ : σ ∈ Finset.univ) => hexpand σ), Finset.sum_comm]
  refine Finset.sum_congr rfl fun f _ => ?_
  rw [Matrix.det_apply' (B.submatrix id f)]
  simp only [Matrix.submatrix_apply, id_eq]
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun σ _ => ?_
  rw [Finset.prod_mul_distrib]
  ring

/-! ### Ортогональность Слейтера (Коши–Бине): О2–О5 -/

/-- Вспомогательное: определитель почленно-сопряжённой матрицы —
сопряжение определителя. -/
theorem det_map_star {m : ℕ} (M : Matrix (Fin m) (Fin m) ℂ) :
    (M.map star).det = star M.det := by
  have h : M.map star = M.map (starRingEnd ℂ) := by
    ext i j; simp
  rw [h]
  show ((starRingEnd ℂ).mapMatrix M).det = star M.det
  rw [← RingHom.map_det]
  rfl

/-- О2: определитель подматрицы по не-инъективному набору столбцов равен
нулю (два совпадающих столбца). -/
theorem det_submatrix_noninj_zero {k n : ℕ} (B : Matrix (Fin k) (Fin n) ℂ)
    {f : Fin k → Fin n} (hf : ¬Function.Injective f) : (B.submatrix id f).det = 0 := by
  rw [Function.not_injective_iff] at hf
  obtain ⟨i, j, hfeq, hij⟩ := hf
  refine Matrix.det_zero_of_column_eq hij (fun x => ?_)
  simp only [Matrix.submatrix_apply, id]
  rw [hfeq]

/-- Конфигурация ≃ конечное множество слотов: конфигурация — индикатор
своего носителя (`x = 1_{supp x}`). -/
def cfgEquivSet : Finset Slot ≃ Cfg where
  toFun U := fun u => if u ∈ U then 1 else 0
  invFun x := supp x
  left_inv U := by
    ext u
    by_cases h : u ∈ U <;> simp [supp, Finset.mem_filter, h]
  right_inv x := by
    funext u
    rcases cfg_bit x u with hb | hb
    · have h0 : u ∉ supp x := by
        intro hc
        simp only [supp, Finset.mem_filter, Finset.mem_univ, true_and] at hc
        rw [hc] at hb
        simp at hb
      simp [supp, Finset.mem_filter, hb, h0]
    · have h1 : u ∈ supp x := supp_mem_of_one x u hb
      simp [supp, Finset.mem_filter, hb, h1]

theorem supp_cfgEquivSet (U : Finset Slot) : supp (cfgEquivSet U) = U :=
  Equiv.injective cfgEquivSet (cfgEquivSet.right_inv (cfgEquivSet U))

/-- О3: скалярное произведение пере-индексируется по носителям
(конфигурации с данным носителем отвечают взаимно однозначно). -/
theorem slaterIP_reindex (S T : Finset Slot) :
    slaterIP (fun y => slater S y) (fun y => slater T y)
      = ∑ U : Finset Slot, star (slater S (cfgEquivSet U))
          * slater T (cfgEquivSet U) := by
  rw [slaterIP]
  exact Fintype.sum_equiv cfgEquivSet.symm
    (fun x => star (slater S x) * slater T x)
    (fun U => star (slater S (cfgEquivSet U)) * slater T (cfgEquivSet U))
    (fun x => (congrArg (fun u => star (slater S u) * slater T u)
      (cfgEquivSet.right_inv x)).symm)

/-- Определители матриц с совпадающими поэлементно записями (при
перенумерации `Fin m ≃ Fin n`) равны. -/
theorem det_congr_entries {m n : ℕ} (hmn : m = n) {M : Matrix (Fin m) (Fin m) ℂ}
    {N : Matrix (Fin n) (Fin n) ℂ}
    (hEnt : ∀ (i j : Fin m), M i j = N (Fin.cast hmn i) (Fin.cast hmn j)) :
    M.det = N.det := by
  cases hmn
  exact congrArg Matrix.det (Matrix.ext fun i j => by simpa using hEnt i j)

/-- Матрица мод `S`: строка `i` — мода `S_i` (в порядке возрастания),
столбцы — все слоты. -/
noncomputable def psiMat (S : Finset Slot) : Matrix (Fin S.card) (Fin numSlots) ℂ :=
  Matrix.of fun i u => psi (((S.sort (· ≤ ·)).get
    (Fin.cast (Finset.length_sort (· ≤ ·)).symm i))).toNat u

/-- О3.5: slater на индикаторе носителя — определитель подматрицы
матрицы мод по столбцам-элементам `U` (в порядке возрастания). -/
theorem slater_cfgEquivSet (S U : Finset Slot) (hU : U.card = S.card) :
    slater S (cfgEquivSet U) = ((psiMat S).submatrix id (U.orderEmbOfFin hU)).det := by
  have hsup : (supp (cfgEquivSet U)).card = S.card := by
    rw [supp_cfgEquivSet]; exact hU
  have hlist : ((supp (cfgEquivSet U)).sort (· ≤ ·)) = (U.sort (· ≤ ·)) :=
    congrArg (fun l => l.sort (· ≤ ·)) (supp_cfgEquivSet U)
  unfold slater
  rw [dif_pos hsup]
  refine det_congr_entries rfl (fun i j => ?_)
  simp [Matrix.of_apply, Matrix.submatrix_apply, hlist,
    Finset.orderEmbOfFin_apply]

/-- О4: подмножественная форма Коши–Бине: сумма по всем наборам столбцов
совпадает с суммой по `k`-элементным подмножествам (не-инъективные наборы
дают нуль, инъективные группируются по образу с учётом знака). -/
theorem cauchy_binet_subset {k n : ℕ} (A B : Matrix (Fin k) (Fin n) ℂ) :
    (∑ f : Fin k → Fin n, (∏ i, A i (f i)) * (B.submatrix id f).det)
      = (∑ U : Finset (Fin n), if hU : U.card = k then
            (A.submatrix id (U.orderEmbOfFin hU)).det
              * (B.submatrix id (U.orderEmbOfFin hU)).det
          else 0) := by
  have hzero : ∀ f : Fin k → Fin n, ¬Function.Injective f →
      (∏ i, A i (f i)) * (B.submatrix id f).det = 0 := fun f hf => by
    rw [det_submatrix_noninj_zero B hf, mul_zero]
  -- Шаг 1: не-инъективные наборы дают нуль.
  have h1 : ∑ f ∈ (Finset.univ : Finset (Fin k → Fin n)).filter
        (fun f => Function.Injective f),
      ((∏ i, A i (f i)) * (B.submatrix id f).det)
      = ∑ f : Fin k → Fin n, (∏ i, A i (f i)) * (B.submatrix id f).det := by
    refine Finset.sum_subset (Finset.filter_subset _ _) (fun f _ hf => ?_)
    rw [Finset.mem_filter] at hf
    exact hzero f (fun hc => hf ⟨Finset.mem_univ f, hc⟩)
  rw [← h1]
  -- Шаг 2: группировка по образу.
  rw [← Finset.sum_fiberwise ((Finset.univ : Finset (Fin k → Fin n)).filter
    (fun f => Function.Injective f)) (fun f => Finset.image f Finset.univ)
    (fun f => (∏ i, A i (f i)) * (B.submatrix id f).det)]
  -- Шаг 3: образы инъективных наборов — в точности k-элементные подмножества.
  have himage : ((Finset.univ : Finset (Fin k → Fin n)).filter
        (fun f => Function.Injective f)).image
      (fun f => Finset.image f Finset.univ)
      = (Finset.univ (α := Finset (Fin n))).filter
          (fun U : Finset (Fin n) => U.card = k) := by
    ext U
    simp only [Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨f, -, hinj, himg⟩
      rw [← himg, Finset.card_image_of_injective Finset.univ hinj]
      rfl
    · intro hcard
      refine ⟨U.orderEmbOfFin hcard, ?_, ?_⟩
      · simp [Finset.mem_filter]
      · ext u
        simp only [Finset.mem_image, Finset.mem_univ, true_and]
        constructor
        · rintro ⟨a, -, ha⟩
          exact ha ▸ Finset.orderEmbOfFin_mem _ _ _
        · intro hu
          exact ⟨(U.orderIsoOfFin hcard).symm ⟨u, hu⟩, by simp⟩
  simp only [himage]
  -- Шаг 4: справа dite по U — сводим к сумме по фильтру.
  have hrhs : (∑ U : Finset (Fin n), if hU : U.card = k then
        (A.submatrix id (U.orderEmbOfFin hU)).det
          * (B.submatrix id (U.orderEmbOfFin hU)).det
      else 0)
      = ∑ U ∈ (Finset.univ (α := Finset (Fin n))).filter
          (fun U : Finset (Fin n) => U.card = k),
        if hU : U.card = k then
          (A.submatrix id (U.orderEmbOfFin hU)).det
            * (B.submatrix id (U.orderEmbOfFin hU)).det
        else 0 := by
    refine (Finset.sum_subset (Finset.filter_subset _ _) (fun U _ hU => ?_)).symm
    rw [dif_neg (by simpa only [Finset.mem_filter, Finset.mem_univ, true_and, not_and,
      not_not] using hU)]
  rw [hrhs, Finset.sum_congr rfl (fun U hU => ?_)]
  · intro U hU
    rw [dif_pos (Finset.mem_filter.mp hU).2]
    -- фибра {f | инъективно, образ = U} пере-индексируется по Perm (Fin k)
    have hfib : ∑ f ∈ ((Finset.univ : Finset (Fin k → Fin n)).filter
          (fun f => Function.Injective f)).filter
          (fun f => Finset.image f Finset.univ = U),
        ((∏ i, A i (f i)) * (B.submatrix id f).det)
        = (A.submatrix id (U.orderEmbOfFin (Finset.mem_filter.mp hU).2)).det
            * (B.submatrix id (U.orderEmbOfFin (Finset.mem_filter.mp hU).2)).det := by
      set e := U.orderEmbOfFin (Finset.mem_filter.mp hU).2 with he
      have hperm : ∀ σ : Equiv.Perm (Fin k),
          (B.submatrix id (fun i => e (σ i))).det
            = Equiv.Perm.sign σ * (B.submatrix id e).det := by
        intro σ
        rw [← Matrix.submatrix_submatrix, Matrix.det_permute']
      have hAdet : ∑ σ : Equiv.Perm (Fin k),
          Equiv.Perm.sign σ * ∏ i, A i (e (σ i)) = (A.submatrix id e).det := by
        rw [← Matrix.det_transpose, Matrix.det_apply']
        simp only [Matrix.transpose_apply, Matrix.submatrix_apply]
      have hmapimg : ∀ σ : Equiv.Perm (Fin k),
          Finset.image (fun i => e (σ i)) Finset.univ = U := by
        intro σ
        ext u
        simp only [Finset.mem_image, Finset.mem_univ, true_and]
        constructor
        · rintro ⟨a, -, ha⟩
          exact ha ▸ Finset.orderEmbOfFin_mem _ _ _
        · intro hu
          exact ⟨σ.symm ((U.orderIsoOfFin (Finset.mem_filter.mp hU).2).symm ⟨u, hu⟩),
            by simp⟩
      have hsurj : ∀ f : {f : Fin k → Fin n // Function.Injective f ∧
          Finset.image f Finset.univ = U},
          ∃ σ : Equiv.Perm (Fin k),
            (fun σ => ⟨fun i => e (σ i), σ.injective.comp e.injective, hmapimg σ⟩) σ = f := by
        rintro ⟨f, hprop⟩
        obtain ⟨hinj, himg⟩ := hprop
        have hmem : ∀ i, f i ∈ U := fun i => by
          rw [← himg]; exact Finset.mem_image_of_mem _ (Finset.mem_univ i)
        refine ⟨fun i => (U.orderIsoOfFin (Finset.mem_filter.mp hU).2).symm ⟨f i, hmem i⟩, ?_⟩
        have hv : (fun i => e ((U.orderIsoOfFin (Finset.mem_filter.mp hU).2).symm
            ⟨f i, hmem i⟩)) = f := by
          funext i; simp
        simp [hv, hinj, himg]
      have hequiv := Equiv.ofBijective (fun σ : Equiv.Perm (Fin k) =>
        ⟨fun i => e (σ i), σ.injective.comp e.injective, hmapimg σ⟩)
        ⟨fun σ σ' h => Subtype.ext (funext fun i =>
          e.injective (congrFun (congrArg Subtype.val h) i)), hsurj⟩
      rw [Finset.sum_coe_sort, Fintype.sum_equiv hequiv
        (fun f : {f : Fin k → Fin n // Function.Injective f ∧
            Finset.image f Finset.univ = U} =>
          (∏ i, A i (f i)) * (B.submatrix id f).det)
        (fun σ : Equiv.Perm (Fin k) =>
          (∏ i, A i (e (σ i))) * (B.submatrix id (fun i => e (σ i))).det)
        (fun σ => rfl)]
      calc ∑ σ : Equiv.Perm (Fin k),
            (∏ i, A i (e (σ i))) * (B.submatrix id (fun i => e (σ i))).det
          = ∑ σ : Equiv.Perm (Fin k),
              Equiv.Perm.sign σ * ∏ i, A i (e (σ i)) * (B.submatrix id e).det := by
            refine Finset.sum_congr rfl fun σ _ => ?_
            rw [hperm σ, ← mul_assoc]
            ring
        _ = (A.submatrix id e).det * (B.submatrix id e).det := by
            rw [← Finset.sum_mul, hAdet, mul_comm]
    exact hfib U

/-- **О5: ортогональность Слейтера через Коши–Бине**: скалярное произведение —
определитель грам-матрицы, элементы которой даёт `psi_inner`; грам-матрица —
«матрица частичного тождественного соответствия» между отсортированными
наборами мод, её определитель равен `δ_{S,T}`. -/
theorem slater_orth (S T : Finset Slot) (hST : S.card = T.card) :
    slaterIP (fun y => slater S y) (fun y => slater T y)
      = if S = T then 1 else 0 := by
  rw [slaterIP_reindex S T]
  have hmods : ∀ (R : Finset Slot) (a : Fin R.card),
      (((R.sort (· ≤ ·)).get (Fin.cast (Finset.length_sort (· ≤ ·)).symm a) : Slot)).toNat
        < numSlots := by
    intro R a
    have := ((R.sort (· ≤ ·)).get
      (Fin.cast (Finset.length_sort (· ≤ ·)).symm a) : Slot).isLt
    simpa using this
  -- матрица мод T, строки перенумерованы в Fin S.card (мощности равны)
  set BTM : Matrix (Fin S.card) (Fin numSlots) ℂ :=
    Matrix.of fun i u => psi (((T.sort (· ≤ ·)).get
      (Fin.cast (hST.trans (Finset.length_sort (· ≤ ·)).symm) i))).toNat u
    with hBTMdef
  -- перенос определителя T-матрицы на перенумерованные строки
  have hBTM : ∀ (U : Finset Slot) (hUT : U.card = T.card) (hU : U.card = S.card),
      ((psiMat T).submatrix id (U.orderEmbOfFin hUT)).det
        = (BTM.submatrix id (U.orderEmbOfFin hU)).det := by
    intro U hUT hU
    refine det_congr_entries hST.symm (fun i j => ?_)
    simp [psiMat, Matrix.of_apply, Matrix.submatrix_apply, Finset.orderEmbOfFin_apply,
      hBTMdef]
  have hUpos : ∀ (U : Finset Slot) (hU : U.card = S.card),
      star (slater S (cfgEquivSet U)) * slater T (cfgEquivSet U)
        = ((psiMat S).map star).submatrix id (U.orderEmbOfFin hU) |>.det
          * (BTM.submatrix id (U.orderEmbOfFin hU)).det := by
    intro U hU
    have hUT : U.card = T.card := hU.trans hST
    have hswap : ((psiMat S).submatrix id (U.orderEmbOfFin hU)).map star
        = ((psiMat S).map star).submatrix id (U.orderEmbOfFin hU) := by
      ext a b; simp [Matrix.map_apply]
    rw [slater_cfgEquivSet S U hU, slater_cfgEquivSet T U hUT, det_map_star, hswap,
      hBTM U hUT hU]
  have hUneg : ∀ (U : Finset Slot) (hU : U.card ≠ S.card),
      star (slater S (cfgEquivSet U)) * slater T (cfgEquivSet U) = 0 := by
    intro U hU
    have hUT : U.card ≠ T.card := fun hc => hU (hc.trans hST.symm)
    rw [slater, dif_neg (by rw [supp_cfgEquivSet]; exact hU), star_zero, zero_mul,
      slater, dif_neg (by rw [supp_cfgEquivSet]; exact hUT)]
  rw [Finset.sum_congr rfl (fun U (_ : U ∈ Finset.univ) => ?_),
    ← cauchy_binet_subset (A := (psiMat S).map star) (B := BTM),
    ← det_mul_transpose_sum (A := (psiMat S).map star) (B := BTM)]
  · intro U
    by_cases hU : U.card = S.card
    · exact Eq.trans (hUpos U hU) (dif_pos hU).symm
    · exact Eq.trans (hUneg U hU) (dif_neg hU).symm
  -- грам-элементы: psi_inner
  have hlt : ∀ s : Slot, s.toNat < numSlots := fun s => s.isLt
  have hgram : ∀ a b : Fin S.card,
      (((psiMat S).map star) * BTMᵀ) a b
        = if ((S.sort (· ≤ ·)).get
              (Fin.cast (Finset.length_sort (· ≤ ·)).symm a) : Slot).toNat
            = ((T.sort (· ≤ ·)).get
              (Fin.cast (hST.trans (Finset.length_sort (· ≤ ·)).symm b))).toNat
          then 1 else 0 := by
    intro a b
    rw [Matrix.mul_apply, Matrix.transpose_apply, Matrix.map_apply]
    rw [psi_inner _ _ (hlt _) (hlt _)]
  by_cases hSET : S = T
  · subst hSET
    have hdiag : (((psiMat S).map star) * BTMᵀ)
        = Matrix.diagonal (fun _ : Fin S.card => (1 : ℂ)) := by
      have hemb : ∀ b : Fin S.card, ((S.sort (· ≤ ·)).get
          (Fin.cast (hST.trans (Finset.length_sort (· ≤ ·)).symm) b) : Slot)
          = (S.orderEmbOfFin rfl) b := by
        intro b
        rw [Finset.orderEmbOfFin_apply]
        simp
      have hinj : Function.Injective fun b : Fin S.card =>
          ((S.sort (· ≤ ·)).get
            (Fin.cast (hST.trans (Finset.length_sort (· ≤ ·)).symm) b) : Slot) := by
        intro b b' hbb
        simp only [hemb] at hbb
        exact (S.orderEmbOfFin rfl).injective hbb
      ext i j
      rw [hgram i j]
      by_cases h : i = j
      · subst h; simp
      · rw [if_neg (fun hc => h (hinj (by simpa using hc)))]
        simp
  · rw [if_neg hSET]
    -- S ≠ T при равных мощностях ⇒ есть мода в S \ T ⇒ нулевая строка грама
    have hsne : S \ T ≠ ∅ := by
      intro hc
      rw [Finset.sdiff_eq_empty_iff_subset] at hc
      exact hSET (Finset.eq_of_subset_of_card_le hc (le_of_eq hST.symm))
    obtain ⟨k₀, hk₀⟩ := Finset.exists_mem_of_ne_empty hsne
    have hk₀T : k₀ ∉ T := Finset.mem_sdiff.not.mp hk₀ |>.2
    obtain ⟨a₀, ha₀⟩ : ∃ a₀ : Fin S.card, ((S.sort (· ≤ ·)).get
        (Fin.cast (Finset.length_sort (· ≤ ·)).symm a₀) : Slot) = k₀ :=
      ⟨(S.orderIsoOfFin rfl).symm ⟨k₀, hk₀.1⟩, by
        simp [Finset.orderIsoOfFin_apply, Finset.orderEmbOfFin_apply]⟩
    have hrow : ∀ b : Fin S.card,
        (((psiMat S).map star) * BTMᵀ) a₀ b = 0 := by
      intro b
      rw [hgram a₀ b, ha₀]
      have hmem : ((T.sort (· ≤ ·)).get
          (Fin.cast (hST.trans (Finset.length_sort (· ≤ ·)).symm b)) : Slot) ∈ T := by
        simp
      exact if_neg (fun hc => hk₀T (Fin.ext (by simpa using hc)))
    rw [← Matrix.det_transpose, Matrix.det_zero_of_column_eq
      (i := a₀) (j := a₀) rfl (fun x => by rw [Matrix.transpose_apply, hrow x])]

end Septinal
