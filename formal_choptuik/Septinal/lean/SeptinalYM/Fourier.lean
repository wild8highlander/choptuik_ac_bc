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
-/

namespace Septinal

open Complex
open scoped Matrix

/-- Первообразный корень 22-й степени из единицы. -/
noncomputable def omega : ℂ := exp (2 * Real.pi * I / numSlots)

/-- `ω` имеет порядок 22. -/
theorem omega_pow_numSlots : omega ^ numSlots = 1 := by
  unfold omega
  rw [← Complex.exp_nat_mul]
  have hns : ((numSlots : ℕ) : ℂ) ≠ 0 := by norm_num [numSlots]
  have heq : ((numSlots : ℕ) : ℂ) * (2 * Real.pi * I / (numSlots : ℕ))
      = 2 * Real.pi * I := by
    field_simp
  rw [heq, Complex.exp_two_pi_mul_I]

theorem omega_pow_mod (a : ℕ) : omega ^ (a % numSlots) = omega ^ a := by
  have hd := Nat.div_add_mod a numSlots
  have h1 : omega ^ (numSlots * (a / numSlots) + a % numSlots)
      = omega ^ (numSlots * (a / numSlots)) * omega ^ (a % numSlots) := pow_add _ _ _
  have h2 : omega ^ (numSlots * (a / numSlots)) = (omega ^ numSlots) ^ (a / numSlots) :=
    pow_mul _ _ _
  have h3 : omega ^ a = omega ^ (numSlots * (a / numSlots) + a % numSlots) := by
    rw [hd]
  rw [h3, h1, h2, omega_pow_numSlots, one_pow, one_mul]

theorem omega_pow_congr {a b : ℕ} (h : a % numSlots = b % numSlots) :
    omega ^ a = omega ^ b := by
  rw [← omega_pow_mod a, ← omega_pow_mod b, h]

/-- Вектор Фурье с модой `k`: `(fourierVec k) j = ω^{k·j}`. -/
noncomputable def fourierVec (k : Slot) : Slot → ℂ :=
  fun j => omega ^ ((Fin.val k * Fin.val j) % numSlots)

/-- Циклический предшественник: `(j − 1) = (j + 21) mod 22`. -/
theorem val_pred (j : Slot) :
    (Fin.val (j - 1 : Slot)) = ((Fin.val j + 21) % numSlots) := by
  fin_cases j <;> rfl

theorem val_suc (j : Slot) :
    (Fin.val (j + 1 : Slot)) = ((Fin.val j + 1) % numSlots) := Fin.val_add j 1

theorem pred_add_one (j : Slot) : (((j - 1 : Slot)) + 1 : Slot) = j := by
  fin_cases j <;> rfl

/-- Арифметика мод для соседа: `k·(j+1) ≡ k·j + k (mod 22)`. -/
theorem nat_mod_suc (k j : Slot) :
    (Fin.val k * (Fin.val j + 1)) % numSlots
      = ((Fin.val k * Fin.val j) % numSlots + Fin.val k) % numSlots := by
  show (Fin.val k * (Fin.val j + 1)) % 22
      = ((Fin.val k * Fin.val j) % 22 + Fin.val k) % 22
  fin_cases k <;> fin_cases j <;> decide

/-- Арифметика мод для предшественника: `k·(j+21) ≡ k·j − k (mod 22)`. -/
theorem nat_mod_pred (k j : Slot) :
    (Fin.val k * (Fin.val j + 21)) % numSlots
      = ((Fin.val k * Fin.val j) % numSlots + (numSlots - Fin.val k)) % numSlots := by
  show (Fin.val k * (Fin.val j + 21)) % 22
      = ((Fin.val k * Fin.val j) % 22 + (22 - Fin.val k)) % 22
  fin_cases k <;> fin_cases j <;> decide

/-- Сокращение по модулю: множитель на `(m % n)` можно заменить на `m`. -/
theorem omega_pow_mul_mod (k m : ℕ) :
    omega ^ ((k * (m % numSlots)) % numSlots) = omega ^ ((k * m) % numSlots) := by
  rw [omega_pow_mod (k * (m % numSlots)), omega_pow_mod (k * m)]
  exact omega_pow_congr (Nat.ModEq.mul_left k (Nat.mod_modEq m numSlots))

/-- Сумма по циклу с двумя выделенными точками (общая аддитивная форма). -/
theorem sum_univ_two_points_gen {M : Type} [AddCommMonoid M] {F : Slot → M} (s t : Slot)
    (hst : s ≠ t) (h : ∀ u : Slot, u ≠ s → u ≠ t → F u = 0) :
    (∑ u : Slot, F u) = F s + F t := by
  have h1 : ∑ u : Slot, F u = F s + ∑ u ∈ (Finset.univ.erase s), F u :=
    (Finset.add_sum_erase Finset.univ F (Finset.mem_univ s)).symm
  have htmem : t ∈ (Finset.univ.erase s : Finset Slot) :=
    Finset.mem_erase.2 ⟨Ne.symm hst, Finset.mem_univ t⟩
  have h3 : ∑ u ∈ (Finset.univ.erase s : Finset Slot), F u
      = F t + ∑ u ∈ ((Finset.univ.erase s).erase t), F u :=
    (Finset.add_sum_erase (Finset.univ.erase s) F htmem).symm
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
    fourierVec k (j + 1) = omega ^ (Fin.val k) * fourierVec k j := by
  unfold fourierVec
  show omega ^ ((Fin.val k * Fin.val (j + 1)) % numSlots)
      = omega ^ (Fin.val k) * omega ^ ((Fin.val k * Fin.val j) % numSlots)
  rw [val_suc, omega_pow_mul_mod, omega_pow_mod, omega_pow_congr (nat_mod_suc k j),
    pow_add, mul_comm]

/-- `ω^{k·(j−1)} = ω^{−k} · ω^{k·j}`. -/
theorem fourierVec_pred (k j : Slot) :
    fourierVec k (j - 1) = (omega ^ (Fin.val k))⁻¹ * fourierVec k j := by
  have hpow : (omega ^ (Fin.val k)) * omega ^ (numSlots - Fin.val k) = 1 := by
    have hsum : Fin.val k + (numSlots - Fin.val k) = numSlots := by
      have h22 : numSlots = 22 := rfl
      omega
    rw [← pow_add, hsum, omega_pow_numSlots]
  have hk0 : omega ^ (Fin.val k) ≠ 0 := by
    intro hc
    rw [hc, zero_mul] at hpow
    exact zero_ne_one hpow
  have hinv : (omega ^ (Fin.val k))⁻¹ = omega ^ (numSlots - Fin.val k) := by
    calc (omega ^ (Fin.val k))⁻¹
        = (omega ^ (Fin.val k))⁻¹
            * (omega ^ (Fin.val k) * omega ^ (numSlots - Fin.val k)) := by
          rw [hpow, mul_one]
      _ = ((omega ^ (Fin.val k))⁻¹ * omega ^ (Fin.val k))
            * omega ^ (numSlots - Fin.val k) := (mul_assoc _ _ _).symm
      _ = omega ^ (numSlots - Fin.val k) := by
          rw [inv_mul_cancel₀ hk0, one_mul]
  unfold fourierVec
  show omega ^ ((Fin.val k * Fin.val (j - 1)) % numSlots)
      = (omega ^ (Fin.val k))⁻¹ * omega ^ ((Fin.val k * Fin.val j) % numSlots)
  rw [val_pred, omega_pow_mul_mod, omega_pow_mod, omega_pow_congr (nat_mod_pred k j),
    hinv, ← pow_add, add_comm (numSlots - Fin.val k) ((Fin.val k * Fin.val j) % numSlots)]

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
    fin_cases j <;> exact absurd hc (by decide)
  have hout : ∀ u : Slot, u ≠ (j + 1 : Slot) → u ≠ ((j - 1 : Slot)) →
      (((if ((u : Slot) = j + 1 ∨ (j : Slot) = u + 1) then (2 : ℂ) else 0) * f u) : ℂ) = 0 := by
    intro u hu1 hu2
    have h2 : ¬((j : Slot) = u + 1) := by
      intro hc
      apply hu2
      have hc2 : (Fin.val (u + 1 : Slot)) = (Fin.val j) :=
        congrArg Fin.val hc.symm
      have hc3 : ((Fin.val u + 1) % 22) = (Fin.val j) := by
        rw [← hc2]
        exact (val_suc u).symm
      refine Fin.val_inj.mp ?_
      rw [val_pred]
      show (Fin.val u) = ((Fin.val j + 21) % 22)
      have h22 : numSlots = 22 := rfl
      have hu2 : Fin.val u < 22 := by omega
      have hj2 : Fin.val j < 22 := by omega
      omega
    rw [if_neg (not_or.mpr ⟨hu1, h2⟩), zero_mul]
  rw [sum_univ_two_points_gen (j + 1 : Slot) ((j - 1 : Slot)) hne hout]
  have hFs : (((if ((j + 1 : Slot) = j + 1 ∨ (j : Slot) = (j + 1 : Slot) + 1)
        then (2 : ℂ) else 0) * f (j + 1) : ℂ)) = (2 : ℂ) * f (j + 1) := by
    rw [if_pos (Or.inl rfl)]
  have hFt : (((if (((j - 1 : Slot)) = j + 1 ∨ (j : Slot) = ((j - 1 : Slot)) + 1)
        then (2 : ℂ) else 0) * f ((j - 1 : Slot)) : ℂ)) = (2 : ℂ) * f ((j - 1 : Slot)) := by
    rw [if_pos (Or.inr (pred_add_one j).symm)]
  rw [hFs, hFt]

/-- **Собственное уравнение одночастичного слоя**: мода Фурье `k` — собственный
вектор `hop` с собственным значением `2ω^k + 2ω^{−k}`. -/
theorem hop_fourier_eigen (k : Slot) :
    ∀ j : Slot, (hop *ᵥ fourierVec k) j
      = (2 * omega ^ (Fin.val k) + 2 * (omega ^ (Fin.val k))⁻¹) * fourierVec k j := by
  intro j
  rw [mulVec_hop, fourierVec_suc, fourierVec_pred]
  ring

end Septinal
