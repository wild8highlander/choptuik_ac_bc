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
