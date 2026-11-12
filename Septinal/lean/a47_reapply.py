#!/usr/bin/env python3
# Re-apply all a47 edits + insert the final O2-O5 block into Stage4d.lean
import io

P = '/home/z/my-project/leanwork/choptuik_ac_bc/formal_choptuik/Septinal/lean/SeptinalYM/Stage4d.lean'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(old, new, tag):
    global s
    assert old in s, f'MISSING: {tag}'
    assert s.count(old) == 1, f'NOT UNIQUE: {tag} ({s.count(old)})'
    s = s.replace(old, new, 1)
    print(f'ok: {tag}')

# E1: succ Fix 1 (wrap 21+1=0 via h2)
rep("""          (show (0 : Slot) ∈ supp x from
            supp_mem_of_one x (0 : Slot) (by rw [← hemb21]; exact h2))
""","""          (show (0 : Slot) ∈ supp x from
            supp_mem_of_one x (0 : Slot)
              (by
                rw [hemb21, show ((21 : Slot) + 1 : Slot) = (0 : Slot) from rfl] at h2
                exact h2))
""","E1 succ-wrap")

# E2: succ Fix 2 (hnb 21-val)
rep("""      · have hnb : (((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) ≠ 0 := by
          intro hc
          have hval : ((supp x).orderEmbOfFin h j : ℕ) = 0 := by
            have := val_suc (supp x).orderEmbOfFin h j
            have h22 : numSlots = 22 := rfl
            simp only [h22] at this
            rw [hc] at this
            omega
          exact hemb21 (Fin.ext hval).symm
""","""      · have hnb : ((((supp x).orderEmbOfFin h j : Slot) + 1 : Slot) : ℕ) ≠ 0 := by
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
""","E2 succ-hnb")

# E3: pred P0+P1 (drop hs0, wrap-argument via h1)
rep("""      have hs0 : ((supp x).orderEmbOfFin h j : Slot) + 21
          = ((supp x).orderEmbOfFin h j : Slot) := by
        refine Fin.ext ?_
        have hlt : ((supp x).orderEmbOfFin h j : ℕ) < 22 := by
          have := (supp x).orderEmbOfFin h j |>.isLt
          have h22 : numSlots = 22 := rfl
          simp only [h22] at this
          exact this
        rw [Fin.val_add, val_suc]
        simp only [Nat.mod_eq_of_lt hlt]
        omega
      by_cases hz0 : ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot)
      · rw [dminus_zero_wrap_twist S x h
          (show (21 : Slot) ∈ supp x from
            supp_mem_of_one x (21 : Slot) (by rw [← hz0]; exact h1))
""","""      by_cases hz0 : ((supp x).orderEmbOfFin h j : Slot) = (0 : Slot)
      · rw [dminus_zero_wrap_twist S x h
          (show (21 : Slot) ∈ supp x from
            supp_mem_of_one x (21 : Slot)
              (by
                rw [hz0, show ((0 : Slot) + 21 : Slot) = (21 : Slot) from rfl] at h1
                exact h1))
""","E3 pred-wrap")

# E4: pred P2/P3 (hnb over +21+1, arg order)
rep("""      · have hnb : ((supp x).orderEmbOfFin h j : ℕ) ≠ 0 := by
          intro hc
          exact hz0 (Fin.ext hc).symm
        exact dminus_zero_of_pair_twist S x h ((supp x).orderEmbOfFin h j + 21 : Slot)
          h1 (by rw [slot_pred_suc_eq _]; exact hs1) hnb j
          (embInv S x h hz ((supp x).orderEmbOfFin h j + 21 : Slot))
          (show ((supp x).orderEmbOfFin h j : Slot)
              = (supp x).orderEmbOfFin h j + 21 + 1 from
            (slot_pred_suc_eq ((supp x).orderEmbOfFin h j)).symm)
          (embInv_spec S x h hz _ (supp_mem_of_one x _ h1))
""","""      · -- внутренняя занятая pred-пара
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
""","E4 pred-hnb")

# E5: bondTerm sum_erase_add #1
rep("""  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot) (21 : Slot)
    (Finset.mem_univ _) (fun s => (bondTerm s *ᵥ (fun y => slaterTwist S y)) x)]
  rw [Finset.sum_congr rfl
""","""  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
    (fun s => (bondTerm s *ᵥ (fun y => slaterTwist S y)) x) (Finset.mem_univ (21 : Slot))]
  rw [Finset.sum_congr rfl
""","E5 erase-1")

# E6: bondTerm sum_erase_add #2
rep("""  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot) (21 : Slot)
      (Finset.mem_univ _)
      (fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
""","""  rw [← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 1 ∧ x (s + 1 : Slot) = 0 then
""","E6 erase-2a")
rep("""      else 0)),
    ← Finset.sum_erase_add (Finset.univ : Finset Slot) (21 : Slot)
      (Finset.mem_univ _)
      (fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
""","""      else 0)) (Finset.mem_univ (21 : Slot)),
    ← Finset.sum_erase_add (Finset.univ : Finset Slot)
      (fun s => (if x s = 0 ∧ x (s + 1 : Slot) = 1 then
""","E6 erase-2b")
rep("""      else 0))]
  rw [mul_add, mul_add]
  ring
""","""      else 0)) (Finset.mem_univ (21 : Slot))]
  rw [mul_add, mul_add]
  ring
""","E6 erase-2c")

# E7: sector_twist big block (final a47 form)
rep("""/-- **Этап 4d, главный случай: диагонализация на чётном твистованном секторе.** -/
theorem slater_diag_sector_twist (S : Finset Slot) (x : Cfg)
    (h : (supp x).card = S.card) (hEven : Even S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slaterTwist S y) x
      = (∑ i : Fin S.card, epsTwist (modeOf S i)) * slaterTwist S x := by
  have hz : 0 < S.card := by
    obtain ⟨m, rfl⟩ := hEven
    omega
  rw [mulVec_sum, Finset.sum_apply, bondTerm_sum_if_twist S x h hz hEven,
    succ_part_scaled_twist S x h hz, pred_part_scaled_twist S x h hz]
  rw [Pi.smul_apply, smul_eq_mul, slaterTwist_eq_det S x h]
  rw [← Finset.mul_sum, sum_add_distrib' Finset.univ, mul_add]
  simp only [epsTwist]
  ring
""","""/-- **Этап 4d, главный случай: диагонализация на чётном твистованном секторе.** -/
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
""","E7 sector_twist")

# E7b: even_twist with hS + zero_hcard moved before it
rep("""/-- **Цель для чётных секторов (твист).** С твистованными модами
`ψ̃_k(u) = ζ^u·ψ_k(u)` (`ζ^{22} = −1`, антипериодическое условие) оператор
прыжков диагонален и в чётных секторах: знак `(−1)^{k−1}` границы
компенсируется фазой `ζ^{±1}`, а спектр задаёт `epsTwist` (эффект
Либа–Шульца–Маттиса). -/
theorem slater_diag_even_twist (S : Finset Slot) (hEven : Even S.card) :
    (∑ s : Slot, bondTerm s).mulVec (fun y => slaterTwist S y)
      = (∑ i : Fin S.card, (epsTwist (modeOf S i))) • (fun y => slaterTwist S y) := by
  funext x
  by_cases hxz : (supp x).card = S.card
  · exact slater_diag_sector_twist S x hxz hEven
  · rw [mulVec_sum, Finset.sum_apply,
      Finset.sum_eq_zero (fun s _ => bondTerm_mulVec_zero_hcard_twist S x hxz s)]
    simp [Pi.smul_apply, slaterTwist, dif_neg hxz]

/-- При несовпадающей мощности носителя вклад каждого ребра нулевой
и в твистованном секторе. -/
theorem bondTerm_mulVec_zero_hcard_twist (S : Finset Slot) (x : Cfg)
    (hxz : (supp x).card ≠ S.card) (s : Slot) :
    (bondTerm s *ᵥ (fun y => slaterTwist S y)) x = 0 := by
  rw [mulVec_bondTerm]
  by_cases hP : x s ≠ x (s + 1 : Slot)
  · rw [if_pos hP, slaterTwist,
      dif_neg (fun hc => hxz ((supp_card_flipTwo_suc x s hP).trans hc)), mul_zero]
  · rw [if_neg hP]
""","""/-- При несовпадающей мощности носителя вклад каждого ребра нулевой
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
""","E7b even_twist")

# E8: prod_univ_sum' + det_mul_transpose_sum (final forms)
rep("""theorem prod_univ_sum' {k n : ℕ} (f : Fin k → Fin n → ℂ) :
    (∏ i, ∑ u, f i u) = ∑ g : Fin k → Fin n, ∏ i, f i (g i) := by
  rw [Finset.prod_univ_sum]
  congr 1
  ext g
  simp [Finset.piFinset]
""","""theorem prod_univ_sum' {k n : ℕ} (f : Fin k → Fin n → ℂ) :
    (∏ i, ∑ u, f i u) = ∑ g : Fin k → Fin n, ∏ i, f i (g i) := by
  rw [Finset.prod_univ_sum, Fintype.piFinset_univ]
""","E8 prod_univ")
rep("""theorem det_mul_transpose_sum {k n : ℕ} (A B : Matrix (Fin k) (Fin n) ℂ) :
    (A * Bᵀ).det = ∑ f : Fin k → Fin n, (∏ i, A i (f i)) * (B.submatrix id f).det := by
  rw [Matrix.det_transpose, Matrix.det_apply']
  simp only [Matrix.transpose_apply, Matrix.mul_apply, Matrix.dotProduct]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun f _ => ?_
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun σ _ => ?_
  rw [Finset.prod_mul_distrib, mul_comm (∏ i, A i (f i)) _,
    Finset.mul_sum, ← Finset.prod_mul_distrib]
  congr 1
  rw [← Matrix.det_apply' (B.submatrix id f)]
  refine Finset.sum_congr rfl fun σ _ => ?_
  simp only [Matrix.submatrix_apply]
""","""theorem det_mul_transpose_sum {k n : ℕ} (A B : Matrix (Fin k) (Fin n) ℂ) :
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
""","E8 det_mul")

# E9: replace slater_orth + sorry with the final O2-O5 block
frag = io.open('/home/z/my-project/scripts/o2o5_block.lean.frag', encoding='utf-8').read()
old_block = """/-- **Цель: ортогональность Слейтера (Коши–Бине).** Для наборов мод
одинаковой мощности `⟨Ψ_S, Ψ_T⟩ = δ_{S,T}`: при `S = T` норма 1, при
`S ≠ T` — нуль. Сводится к Коши–Бине для прямоугольных матриц мод
(ортонормальность строк `ψ_k` — Ortho.lean); леммы Коши–Бине в mathlib
нет. -/
theorem slater_orth (S T : Finset Slot) (hST : S.card = T.card) :
    slaterIP (fun y => slater S y) (fun y => slater T y)
      = if S = T then 1 else 0 := by
  sorry"""
rep(old_block, frag.rstrip('\n'), "E9 O2-O5 block")

io.open(P, 'w', encoding='utf-8').write(s)
print(f'DONE: {n0} -> {len(s)} bytes')
