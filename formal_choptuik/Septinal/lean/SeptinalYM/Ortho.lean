/-
Copyright (c) 2025. All rights reserved.
-/
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Algebra.GeomSum
import SeptinalYM.Slater

/-!
# Ортогональность мод Фурье (первый лист фрагмента «Коши–Бине»)

Одночастичные моды `ψ_k(u) = ω^{k·u}/√22` ортогональны:

`Σ_u conj(ψ_k u)·ψ_l u = δ_{k = l}`  (`psi_inner`, `k, l < 22`).

Это диагональный лист матрицы Грама Слейтеровских определителей: Коши–Бине
сводит `⟨Ψ_S, Ψ_T⟩` к определителю матрицы `G_{kl} = ⟨ψ_k, ψ_l⟩`, и
ортогональность мод даёт ортонормированность определителей. Инструменты:

* `omega_eq_exp` — степень корня как экспонента;
* `star_two_pi_I_div` — сопряжение чисто мнимого показателя меняет знак;
* `conj_omega_pow_mul` — `conj(ω^a)·ω^b = ω^{22−a+b}` (периодичность `exp`
  через `exp(2πi) = 1`);
* `omega_ne_one_of_mod` — `ω^d ≠ 1` при `d ≢ 0 (mod 22)`: вещественная часть
  `cos(2πd/22) = 1` даёт `22 ∣ d` (`Real.cos_eq_one_iff`);
* `sum_omega_mul` — сумма корней по циклу: `Σ_u ω^{d·u} = 0` при `d ≢ 0` —
  геометрическая сумма `(q^{22}−1)/(q−1)` с `q = ω^d ≠ 1`, `q^{22} = 1`;
* `term_exponent` — мод-арифметика показателя произведения;
* `psi_inner` — диагональный случай почленно (`1/22` на слагаемое),
  недиагональный — геометрическая сумма нулевая.
-/

namespace Septinal

open Complex Real
open scoped Real

/-! ## Вспомогательные факты о сопряжении -/

/-- Сопряжение частного. -/
theorem star_div' (x y : ℂ) : star (x / y) = star x / star y := by
  rw [div_eq_mul_inv, div_eq_mul_inv, star_mul', star_inv₀]

/-- Показатель `2πi/22` чисто мнимый с мнимой частью `2π/22`. -/
theorem two_pi_I_div_re_im :
    (2 * π * I / (numSlots : ℂ)).re = 0
      ∧ (2 * π * I / (numSlots : ℂ)).im = 2 * π / numSlots := by
  constructor
  · norm_num [Complex.div_re, Complex.mul_re, Complex.I_re, Complex.I_im,
      Complex.ofReal_re, Complex.ofReal_im, numSlots]
  · norm_num [Complex.div_im, Complex.mul_im, Complex.I_re, Complex.I_im,
      Complex.ofReal_re, Complex.ofReal_im, numSlots]

/-- Сопряжение чисто мнимого показателя меняет знак. -/
theorem star_two_pi_I_div :
    star (2 * π * I / (numSlots : ℂ)) = -(2 * π * I / (numSlots : ℂ)) := by
  obtain ⟨hre, him⟩ := two_pi_I_div_re_im
  rw [Complex.star_def, Complex.ext_iff]
  simp only [Complex.conj_re, Complex.conj_im, Complex.neg_re, Complex.neg_im,
    hre, him]
  simp

/-- Степень корня как экспонента: `ω^n = exp(n·2πi/22)`. -/
theorem omega_eq_exp (n : ℕ) :
    omega ^ n = Complex.exp (((n : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))) := by
  rw [omega, ← Complex.exp_nat_mul]

/-- Сопряжение степени корня: `conj(ω^a)·ω^b = ω^{22−a+b}` при `a < 22`. -/
theorem conj_omega_pow_mul (a b : ℕ) (ha : a < numSlots) :
    star (omega ^ a) * omega ^ b = omega ^ (numSlots - a + b) := by
  have hz : ∀ n : ℕ, omega ^ n = Complex.exp (((n : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))) :=
    omega_eq_exp
  have hstara : star (omega ^ a)
      = Complex.exp (-(((a : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))) := by
    rw [hz a, Complex.star_def, ← Complex.exp_conj, ← Complex.star_def]
    congr 1
    rw [star_mul', star_natCast, star_two_pi_I_div]
    ring
  have htar : omega ^ (numSlots - a + b)
      = Complex.exp (-(((a : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))))
        * Complex.exp (((b : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))) := by
    rw [hz (numSlots - a + b)]
    have hle : a ≤ numSlots := Nat.le_of_lt ha
    have hsplit : (((numSlots - a + b : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))
        = (2 * π * I) + (-(((a : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))
          + ((b : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))) := by
      rw [Nat.cast_add, Nat.cast_sub hle]
      field_simp [show ((numSlots : ℕ) : ℂ) ≠ 0 from by norm_num [numSlots]]
      ring
    rw [hsplit]
    rw [Complex.exp_add (2 * π * I)
      (-(((a : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))
        + ((b : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))]
    rw [Complex.exp_two_pi_mul_I, one_mul]
    rw [Complex.exp_add (-(((a : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))))
      (((b : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ)))]
  rw [hstara, htar, hz b]

/-! ## Суммы корней по циклу -/

/-- `ω^d ≠ 1` при `d ≢ 0 (mod 22)`: сводим к `d' = d % 22 ∈ (0, 22)`, тогда
аргумент `2πd'/22 ∈ (0, 2π)` и `cos = 1` даёт `d' = 0` — противоречие
(`Real.cos_eq_one_iff_of_lt_of_lt`). -/
theorem omega_ne_one_of_mod (d : ℕ) (hd : d % numSlots ≠ 0) : omega ^ d ≠ 1 := by
  intro h1
  have hd'lt : d % numSlots < numSlots := Nat.mod_lt _ (by norm_num [numSlots])
  have hd'ne : d % numSlots ≠ 0 := hd
  have h1' : omega ^ (d % numSlots) = 1 := by rw [omega_pow_mod]; exact h1
  have hexp := omega_eq_exp (d % numSlots)
  obtain ⟨hre0, him0⟩ := two_pi_I_div_re_im
  have hzre : (((d % numSlots : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))).re = 0 := by
    have hcd : ((d % numSlots : ℕ) : ℂ) = ((d % numSlots : ℝ) : ℂ) :=
      (Complex.ofReal_natCast _).symm
    rw [hcd, Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im, hre0, him0]
    ring
  have him : (((d % numSlots : ℕ) : ℂ) * (2 * π * I / (numSlots : ℂ))).im
      = 2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ) := by
    have hcd : ((d % numSlots : ℕ) : ℂ) = ((d % numSlots : ℝ) : ℂ) :=
      (Complex.ofReal_natCast _).symm
    rw [hcd, Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im, hre0, him0]
    field_simp
    ring
  have h1re : Real.cos (2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ)) = 1 := by
    have h0 : (omega ^ (d % numSlots)).re = 1 := by rw [h1']; simp
    rw [hexp, Complex.exp_re, hzre, Real.exp_zero, him] at h0
    simpa using h0
  have hd'pos : (0 : ℝ) < ((d % numSlots : ℕ) : ℝ) := by
    exact Nat.cast_pos.2 (Nat.pos_of_ne_zero hd'ne)
  have hpos : (0 : ℝ) < 2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ) := by
    positivity
  have hlt : 2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ) < 2 * π := by
    have hmul : (2 : ℝ) * π * ((d % numSlots : ℕ) : ℝ)
        < (2 : ℝ) * π * (numSlots : ℝ) := by
      refine mul_lt_mul_of_pos_left ?_ (by positivity : (0 : ℝ) < 2 * π)
      exact_mod_cast hd'lt
    rw [div_lt_iff₀ (by positivity : (0 : ℝ) < (numSlots : ℝ))]
    linarith [hmul]
  have hx1 : -(2 * π) < 2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ) := by
    linarith
  have hnez : ¬(2 * π * ((d % numSlots : ℕ) : ℝ) / (numSlots : ℝ) = 0) := fun hc => by
    rw [hc] at hpos
    exact lt_irrefl 0 hpos
  have hzero := (Real.cos_eq_one_iff_of_lt_of_lt hx1 hlt).1 h1re
  exact absurd hzero hnez

/-- Геометрическая сумма корней: `Σ_u ω^{d·u} = 0` при `d ≢ 0 (mod 22)`. -/
theorem sum_omega_mul (d : ℕ) (hd : d % numSlots ≠ 0) :
    ∑ u : Slot, omega ^ ((d * (u : ℕ)) % numSlots) = 0 := by
  rw [Fin.sum_univ_eq_sum_range (fun i : ℕ => omega ^ ((d * i) % numSlots))]
  have hpow : ∀ i ∈ Finset.range numSlots,
      omega ^ ((d * i) % numSlots) = (omega ^ d) ^ i := by
    intro i _
    rw [omega_pow_mod, ← pow_mul]
  rw [Finset.sum_congr rfl hpow, geom_sum_eq (omega_ne_one_of_mod d hd) numSlots]
  have hp22 : (omega ^ d) ^ numSlots = 1 := by
    rw [← pow_mul, mul_comm d numSlots, pow_mul, omega_pow_numSlots, one_pow]
  rw [hp22]
  norm_num

/-- Мод-арифметика показателя: показатель произведения сопряжённой и прямой
степени равен показателю разностной моды `(l + 22 − k)·u`. -/
theorem term_exponent (k l n : ℕ) (hk : k < numSlots) :
    ((numSlots - (k * n) % numSlots) + (l * n) % numSlots) % numSlots
      = ((l + numSlots - k) * n) % numSlots := by
  have hmod : (k * n) % numSlots ≤ numSlots :=
    Nat.le_of_lt (Nat.mod_lt _ (by norm_num [numSlots]))
  have hA : ((numSlots - (k * n) % numSlots) + (l * n) % numSlots) + (k * n) % numSlots
      = numSlots + (l * n) % numSlots := by
    have h1 : (k * n) % numSlots + (numSlots - (k * n) % numSlots) = numSlots :=
      Nat.add_sub_cancel' hmod
    omega
  have hE : ((numSlots - (k * n) % numSlots) + (l * n) % numSlots) + k * n
      ≡ l * n [MOD numSlots] := by
    calc ((numSlots - (k * n) % numSlots) + (l * n) % numSlots) + k * n
        ≡ ((numSlots - (k * n) % numSlots) + (l * n) % numSlots)
            + (k * n) % numSlots [MOD numSlots] :=
          Nat.ModEq.add_left _ (Nat.mod_modEq (k * n) numSlots).symm
      _ = numSlots + (l * n) % numSlots := hA
      _ ≡ 0 + (l * n) % numSlots [MOD numSlots] :=
          Nat.ModEq.add_right _ (show numSlots ≡ 0 [MOD numSlots] from rfl)
      _ = (l * n) % numSlots := Nat.zero_add _
      _ ≡ l * n [MOD numSlots] := Nat.mod_modEq _ _
  have hD : ((l + numSlots - k) * n) + k * n ≡ l * n [MOD numSlots] := by
    have hdk : (l + numSlots - k) + k = l + numSlots := by omega
    have hmul : ((l + numSlots - k) * n) + k * n = (l + numSlots) * n := by
      rw [← Nat.add_mul, hdk]
    calc ((l + numSlots - k) * n) + k * n
        = (l + numSlots) * n := hmul
      _ = l * n + numSlots * n := Nat.add_mul l numSlots n
      _ ≡ l * n + 0 * n [MOD numSlots] :=
          Nat.ModEq.add_left _ (Nat.ModEq.mul_right n
            (show numSlots ≡ 0 [MOD numSlots] from rfl))
      _ = l * n := by ring
  exact Nat.ModEq.add_right_cancel' (k * n) (hE.trans hD.symm)

/-! ## Ортогональность мод -/

/-- **Ортогональность мод Фурье**: `Σ_u conj(ψ_k u)·ψ_l u = δ_{k=l}` для
`k, l < 22` — одночастичная версия листа «Коши–Бине». -/
theorem psi_inner (k l : ℕ) (hk : k < numSlots) (hl : l < numSlots) :
    ∑ u : Slot, star (psi k u) * psi l u = if k = l then 1 else 0 := by
  have h22 : numSlots = 22 := rfl
  have hc : ((Real.sqrt 22 : ℝ) : ℂ) * ((Real.sqrt 22 : ℝ) : ℂ) = ((22 : ℝ) : ℂ) := by
    rw [← Complex.ofReal_mul, Real.mul_self_sqrt (by norm_num : (0 : ℝ) ≤ 22)]
  have hsc : star (((Real.sqrt 22 : ℝ) : ℂ)) = ((Real.sqrt 22 : ℝ) : ℂ) :=
    star_ofReal' _
  set d : ℕ := l + numSlots - k with hdef
  have hterm : ∀ u : Slot, star (psi k u) * psi l u
      = omega ^ ((d * (u : ℕ)) % numSlots) / ((22 : ℝ) : ℂ) := by
    intro u
    have hau : ((k * (u : ℕ)) % numSlots) < numSlots :=
      Nat.mod_lt _ (by norm_num [numSlots])
    unfold psi
    rw [star_div', div_mul_div_comm, hsc, hc]
    rw [conj_omega_pow_mul _ _ hau]
    rw [omega_pow_congr (term_exponent k l (u : ℕ) hk), omega_pow_mod]
  have hsumdiv : ∑ u : Slot, (omega ^ ((d * (u : ℕ)) % numSlots) / ((22 : ℝ) : ℂ))
      = (∑ u : Slot, omega ^ ((d * (u : ℕ)) % numSlots)) / ((22 : ℝ) : ℂ) := by
    rw [Finset.sum_congr rfl fun u _ => div_eq_mul_inv _ _, ← Finset.sum_mul, div_eq_mul_inv]
  rw [Finset.sum_congr rfl (fun u _ => hterm u), hsumdiv]
  by_cases hkl : k = l
  · subst hkl
    have hd0 : d = numSlots := by rw [hdef]; omega
    have hver : ∀ u : Slot, omega ^ ((d * (u : ℕ)) % numSlots) = (1 : ℂ) := by
      intro u
      rw [hd0]
      have hmod0 : (numSlots * (u : ℕ)) % numSlots = 0 :=
        Nat.mod_eq_zero_of_dvd (dvd_mul_of_dvd_left (dvd_refl numSlots) _)
      rw [hmod0, pow_zero]
    rw [Finset.sum_congr rfl (fun u _ => hver u), Finset.sum_const,
      Finset.card_univ, Fintype.card_fin, h22]
    rw [if_pos rfl]
    norm_num
  · rw [if_neg hkl]
    have hdne : d % numSlots ≠ 0 := by
      intro hc
      have hpos : 0 < l + numSlots - k := by omega
      have hlt : l + numSlots - k < 2 * numSlots := by omega
      obtain ⟨m, hm⟩ := Nat.dvd_iff_mod_eq_zero.mpr hc
      rw [hdef] at hm
      rw [hm] at hpos hlt
      rw [Nat.mul_comm 2 numSlots] at hlt
      have hm1 : m = 1 := by
        rcases Nat.lt_or_ge m 2 with h | h
        · have hm0 : m ≠ 0 := by
            intro h0
            rw [h0] at hpos
            simp at hpos
          omega
        · exfalso
          have h2le : 2 * numSlots ≤ m * numSlots := Nat.mul_le_mul_right numSlots h
          rw [Nat.mul_comm numSlots m, Nat.mul_comm numSlots 2] at hlt
          omega
      rw [hm1] at hm
      omega
    rw [sum_omega_mul d hdne, zero_div]

end Septinal
