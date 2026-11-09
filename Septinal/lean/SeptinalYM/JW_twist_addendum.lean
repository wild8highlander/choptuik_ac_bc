/-! ## Ребро-обмотка (21, 0): мажораны с оператором чётности (пункт JW-программы 1)
    ДОБАВКА к JW.lean перед `end Septinal`. СТАТУС: написано, НЕ прошло compile-проверку
    (окружение пало на середине восстановления). При первом запуске ожидается
    0–2 тактических фикса, математика не меняется. -/

/-- Вес `x` распадается на строку последнего слота и его бит. -/
theorem weight_eq_wBelow_add_last (x : Cfg) :
    weight x = wBelow 21 x + (if x 21 = 1 then 1 else 0) := by
  unfold weight wBelow
  have hcompl : (Finset.univ.filter fun u : Slot => (u : ℕ) < (21 : ℕ))ᶜ
      = {(21 : Slot)} := by
    ext u
    simp only [Finset.mem_compl, Finset.mem_filter, Finset.mem_univ,
      Finset.mem_singleton, true_and]
    constructor
    · intro h
      have h22 : numSlots = 22 := rfl
      have h1 := u.isLt
      omega
    · intro h hc
      rw [hc] at h
      simp at h
  rw [Finset.sum_add_sum_compl
    (Finset.univ.filter fun u : Slot => (u : ℕ) < (21 : ℕ))
    (fun u : Slot => (if x u = 1 then 1 else 0)), hcompl, Finset.sum_singleton]
  ring

/-- Для последнего слота `(−1)^{строка} · чётность = (−1)^{бит}`:
промежуточные биты сокращаются. -/
theorem powBelow_mul_par_last (x : Cfg) :
    ((-1 : ℂ) ^ wBelow 21 x) * par x = (-1 : ℂ) ^ (if x 21 = 1 then 1 else 0) := by
  have hw := weight_eq_wBelow_add_last x
  unfold par at *
  have e1 : ((-1 : ℂ) ^ wBelow 21 x) * ((-1 : ℂ) ^ weight x)
      = ((-1 : ℂ) ^ (wBelow 21 x + weight x)) := (pow_add _ _ _).symm
  rw [e1, hw]
  have h2 : wBelow 21 x + (wBelow 21 x + (if x 21 = 1 then 1 else 0))
      = (2 * wBelow 21 x) + (if x 21 = 1 then 1 else 0) := by ring
  rw [h2, pow_add, negOne_pow_two_mul, one_mul]
  rcases bit_cases (x 21) with hb | hb <;> rw [hb] <;> simp

/-- Скрученная мажорана слота 0: строка Джордана–Вигнера замыкается через
оператор чётности `P = (−1)^N`, т.е. `γ_{2·22+a} = P·γ_a`. -/
def majTw (a : Bool) (v : Vec) : Vec := fun x =>
  par x * lsig a (x 0) * v (flipOne 0 x)

/-- **Ребро-обмотка (21, 0)**: с учётом замыкания строки через чётность,
`bondTerm 21 = i(γ_{42}·(Pγ_1) − γ_{43}·(Pγ_0))`. -/
theorem bondTerm_last_mulVec_eq (v : Vec) (x : Cfg) :
    (bondTerm 21 *ᵥ v) x
      = Complex.I * ((majX 21 (majTw true v)) x - (majY 21 (majTw false v)) x) := by
  rw [mulVec_bondTerm 21 v x]
  have hz0 : (flipOne 21 x) 0 = x 0 := by
    simp [flipOne, flipTwo]
    decide
  have hX : (majX 21 (majTw true v)) x
      = ((-1 : ℂ) ^ (if x 21 = 1 then 1 else 0)) * (-1 : ℂ)
        * (lsig true (x 0) * v (flipOne 0 (flipOne 21 x))) := by
    simp only [majX, majVia, majTw, lsig]
    rw [hz0, par_flipOne, mul_neg, ← powBelow_mul_par_last]
  have hY : (majY 21 (majTw false v)) x
      = ((-1 : ℂ) ^ (if x 21 = 1 then 1 else 0)) * (-1 : ℂ)
        * (lsig true (x 21) * v (flipOne 0 (flipOne 21 x))) := by
    simp only [majY, majVia, majTw, lsig]
    rw [hz0, par_flipOne, mul_neg, ← powBelow_mul_par_last]
  rw [hX, hY, flipOne_pair 21 0 (Ne.symm (suc_ne_all 21)) x]
  rcases bit_cases (x 21) with hb | hb <;>
    rcases bit_cases (x 0) with hb2 | hb2 <;>
    rw [hb, hb2] <;> simp [lsig] <;> ring
