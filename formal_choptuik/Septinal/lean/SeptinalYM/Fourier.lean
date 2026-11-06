/-
Copyright (c) 2025. All rights reserved.
-/
import SeptinalYM.JW

/-!
# Одночастичный слой Фурье-диагонализации (пункты 2–3 JW-программы)

Одночастичный оператор перескока `hop` (амплитуда 2 на каждом из 22 рёбер
цикла) диагонализуется векторами Фурье `fourierVec k j = ω^{k·j}`,
`ω = exp(2πi/22)`:

`(hop *ᵥ fourierVec k) j = (2·ω^k + 2·ω^{−k}) · fourierVec k j`.

СТАТУС: написано, НЕ прошло compile-проверку (окружение пало на середине
восстановления; модуль ещё не добавлен в корень `SeptinalYM.lean` — добавить
строку `import SeptinalYM.Fourier`). При первом запуске ожидается 0–3
тактических фикса (имена `Fin.val_add`/`Fin.val_inj`, форма `Finset.mem_filter`),
математика не меняется. Далее по программе: секторные оценки на
Слейтеровском базисе и числовая часть 2Σ_k|cos(2πk/22)| = 28.106697.
-/

namespace Septinal

open Complex

/-- Первообразный корень 22-й степени из единицы. -/
noncomputable def omega : ℂ := exp (2 * Real.pi * I / numSlots)

/-- `ω` имеет порядок 22. -/
theorem omega_pow_numSlots : omega ^ numSlots = 1 := by
  unfold omega
  have h : (numSlots : ℕ) • (2 * Real.pi * I / (numSlots : ℕ)) = 2 * Real.pi * I := by
    rw [Nat.smul_def, smul_eq_mul]
    field_simp
  rw [zpow_natCast, ← h, Complex.exp_nat_mul, Complex.exp_two_pi_mul_I]

theorem omega_pow_mod (a : ℕ) : omega ^ (a % numSlots) = omega ^ a := by
  have hd := Nat.div_add_mod a numSlots
  have h1 : omega ^ (numSlots * (a / numSlots) + a % numSlots)
      = omega ^ (numSlots * (a / numSlots)) * omega ^ (a % numSlots) := pow_add _ _ _
  have h2 : omega ^ (numSlots * (a / numSlots)) = (omega ^ numSlots) ^ (a / numSlots) :=
    pow_mul _ _ _
  rw [← h1, ← h2, omega_pow_numSlots, one_pow, one_mul, hd]

theorem omega_pow_congr {a b : ℕ} (h : a % numSlots = b % numSlots) :
    omega ^ a = omega ^ b := by
  rw [← omega_pow_mod a, ← omega_pow_mod b, h]

/-- Вектор Фурье с модой `k`: `(fourierVec k) j = ω^{k·j}`. -/
noncomputable def fourierVec (k : Slot) : Slot → ℂ :=
  fun j => omega ^ (((k : ℕ) * (j : ℕ)) % numSlots)

/-- Циклический предшественник: `(j − 1) = (j + 21) mod 22`. -/
theorem val_pred (j : Slot) :
    (((j - 1 : Slot) : ℕ)) = (((j : ℕ) + 21) % numSlots) := by
  fin_cases j <;> rfl

theorem val_suc (j : Slot) :
    (((j + 1 : Slot) : ℕ)) = (((j : ℕ) + 1) % numSlots) := Fin.val_add j 1

theorem pred_add_one (j : Slot) : (((j - 1 : Slot)) + 1 : Slot) = j := by
  fin_cases j <;> rfl

/-- Сумма по циклу с двумя выделенными точками (общая аддитивная форма). -/
theorem sum_univ_two_points_gen {M : Type} [AddCommMonoid M] {F : Slot → M} (s t : Slot)
    (hst : s ≠ t) (h : ∀ u : Slot, u ≠ s → u ≠ t → F u = 0) :
    (∑ u : Slot, F u) = F s + F t := by
  have h1 : ∑ u : Slot, F u = F s + ∑ u ∈ (Finset.univ.erase s), F u :=
    Finset.add_sum_erase Finset.univ F (Finset.mem_univ s)
  have htmem : t ∈ (Finset.univ.erase s : Finset Slot) :=
    Finset.mem_erase.2 ⟨Ne.symm hst, Finset.mem_univ t⟩
  have h3 : ∑ u ∈ (Finset.univ.erase s : Finset Slot), F u
      = F t + ∑ u ∈ ((Finset.univ.erase s).erase t), F u :=
    Finset.add_sum_erase (Finset.univ.erase s) F htmem
  have hEq : ∑ u ∈ ((Finset.univ.erase s).erase t : Finset Slot), F u = 0 := by
    refine Finset.sum_eq_zero fun u hu => ?_
    have hu1 : u ≠ s := by
      intro hc
      rw [hc] at hu
      simp at hu
    have hu2 : u ≠ t := by
      intro hc
      rw [hc] at hu
      simp at hu
    exact h u hu1 hu2
  rw [h1, h3, hEq, add_zero]

/-- `ω^{k·(j+1)} = ω^k · ω^{k·j}`. -/
theorem fourierVec_suc (k j : Slot) :
    fourierVec k (j + 1) = omega ^ ((k : ℕ)) * fourierVec k j := by
  have h22 : numSlots = 22 := rfl
  unfold fourierVec
  rw [val_suc]
  have e1 : omega ^ ((k : ℕ) * (((j : ℕ) + 1) % numSlots))
      = omega ^ ((k : ℕ) * ((j : ℕ) + 1)) :=
    omega_pow_congr (by rw [h22]; omega)
  have e2 : omega ^ ((k : ℕ) * ((j : ℕ) + 1))
      = omega ^ (((k : ℕ) * (j : ℕ)) % numSlots + (k : ℕ)) := by
    congr 1
    rw [h22]; omega
  rw [e1, e2, pow_add, mul_comm]

/-- `ω^{k·(j−1)} = ω^{−k} · ω^{k·j}`. -/
theorem fourierVec_pred (k j : Slot) :
    fourierVec k ((j - 1 : Slot)) = (omega ^ (k : ℕ))⁻¹ * fourierVec k j := by
  have h22 : numSlots = 22 := rfl
  have hpow : (omega ^ (k : ℕ)) * omega ^ (numSlots - (k : ℕ)) = 1 := by
    have hsum : ((k : ℕ)) + (numSlots - (k : ℕ)) = numSlots := by rw [h22]; omega
    rw [← pow_add, hsum, omega_pow_numSlots]
  unfold fourierVec
  rw [val_pred]
  have e1 : omega ^ ((k : ℕ) * (((j : ℕ) + 21) % numSlots))
      = omega ^ ((k : ℕ) * ((j : ℕ) + 21)) :=
    omega_pow_congr (by rw [h22]; omega)
  have e2 : omega ^ ((k : ℕ) * ((j : ℕ) + 21))
      = omega ^ (((k : ℕ) * (j : ℕ)) % numSlots + (numSlots - (k : ℕ)) * numSlots) := by
    congr 1
    rw [h22]; omega
  have e3 : omega ^ (((k : ℕ) * (j : ℕ)) % numSlots + (numSlots - (k : ℕ)) * numSlots)
      = omega ^ (((k : ℕ) * (j : ℕ)) % numSlots) * (omega ^ numSlots) ^ (numSlots - (k : ℕ)) := by
    rw [pow_add, pow_mul]
  rw [e1, e2, e3, omega_pow_numSlots, one_pow, one_mul, mul_comm (omega ^ (k : ℕ))⁻¹,
    ← hpow, one_mul]
  exact (omega_pow_mod _).symm

/-- Одночастичный оператор перескока по циклу 22: амплитуда 2 на каждом
из 22 рёбер `(j, j+1)`. -/
noncomputable def hop : Matrix Slot Slot ℂ :=
  Matrix.of fun j k => if ((k : Slot) = j + 1 ∨ (j : Slot) = k + 1) then (2 : ℂ) else 0

theorem mulVec_hop (f : Slot → ℂ) (j : Slot) :
    (hop *ᵥ f) j = (2 : ℂ) * f (j + 1) + (2 : ℂ) * f ((j - 1 : Slot)) := by
  rw [Matrix.mulVec, dotProduct]
  simp only [hop, Matrix.of_apply]
  have hne : (j + 1 : Slot) ≠ ((j - 1 : Slot)) := by
    intro hc
    fin_cases j <;> simp at hc
  have hout : ∀ u : Slot, u ≠ (j + 1 : Slot) → u ≠ ((j - 1 : Slot)) →
      ((if ((u : Slot) = j + 1 ∨ (j : Slot) = u + 1) then (2 : ℂ) * f u else 0 : ℂ)) = 0 := by
    intro u hu1 hu2
    have h2 : ¬((j : Slot) = u + 1) := by
      intro hc
      apply hu2
      apply Fin.ext
      rw [Fin.val_add] at hc
      rw [val_pred]
      have h22 : numSlots = 22 := rfl
      rw [h22] at hc ⊢
      have hu' := u.isLt
      have hj' := j.isLt
      omega
    rw [if_neg (not_or.mpr ⟨hu1, h2⟩)]
  rw [sum_univ_two_points_gen (j + 1 : Slot) ((j - 1 : Slot)) hne hout]
  have hFs : ((if ((j + 1 : Slot) = j + 1 ∨ (j : Slot) = (j + 1 : Slot) + 1)
        then (2 : ℂ) * f (j + 1) else 0 : ℂ)) = (2 : ℂ) * f (j + 1) :=
    if_pos (Or.inl rfl)
  have hFt : ((if (((j - 1 : Slot)) = j + 1 ∨ (j : Slot) = ((j - 1 : Slot)) + 1)
        then (2 : ℂ) * f ((j - 1 : Slot)) else 0 : ℂ)) = (2 : ℂ) * f ((j - 1 : Slot)) :=
    if_pos (Or.inr (pred_add_one j))
  rw [hFs, hFt]

/-- **Собственное уравнение одночастичного слоя**: мода Фурье `k` — собственный
вектор `hop` с собственным значением `2ω^k + 2ω^{−k}`. -/
theorem hop_fourier_eigen (k : Slot) :
    ∀ j : Slot, (hop *ᵥ fourierVec k) j
      = (2 * omega ^ (k : ℕ) + 2 * (omega ^ (k : ℕ))⁻¹) * fourierVec k j := by
  intro j
  rw [mulVec_hop, fourierVec_suc, fourierVec_pred]
  ring

end Septinal
