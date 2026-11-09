import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Complex.Norm
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.Data.Matrix.ConjTranspose
import Mathlib.Data.Finset.Max
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FieldSimp

import SeptinalYM.Basic

/-!
# Септинальная система: матричная часть

Пространство состояний `ℋ_Sept = ⊗_{s ∈ D\G} ℂ²` с битовым базисом
`Cfg = Fin 22 → Fin 2`:

* `H0site`, `H0` — диагональная часть `H₀ = Σ_s H_s`;
* `bondTerm`, `V` — связь `V = J·Σ_s (σx^{(s)}σx^{(s+1)} + σy^{(s)}σy^{(s+1)})`;
* `HSept` — полный гамильтониан `H₀ + V`;
* эрмитовость всей цепочки — **лемма 2 плана** (`HSept_isHermitian`);
* квадратичная форма `qform` и оценка `|⟨v|V|v⟩| ≤ 44|J|·‖v‖²`.

Определение `IsHermitian` (см. `SeptinalYM.Basic`) повторяет стандартное
`Matrix.IsHermitian` (`Mᴴ = M`); собственная копия позволяет не тянуть тяжёлый
модуль `Mathlib.LinearAlgebra.Matrix.Hermitian` (спектральная теория).
-/

open scoped Real
open scoped Matrix

namespace Septinal

/-! ## Конфигурационное пространство и нормы -/

/-- Конфигурация = битовая строка длины 22: базис `ℋ_Sept`. -/
abbrev Cfg : Type := Fin numSlots → Fin 2

/-- Вектор состояния как функция на битовом базисе. -/
abbrev Vec : Type := Cfg → ℂ

/-- Вакуумное состояние: все биты 0. -/
def vac : Cfg := fun _ => 0

/-- Квадрат евклидовой нормы: `‖v‖² = Σ_x |v_x|²`. -/
noncomputable def nrm2 (v : Vec) : ℝ := ∑ x, (‖v x‖ : ℝ) ^ 2

theorem nrm2_nonneg (v : Vec) : 0 ≤ nrm2 v :=
  Finset.sum_nonneg fun x _ => sq_nonneg _

/-- Разбиение суммы суммы по слагаемым (в mathlib v4.21.0 лемма
`Finset.sum_add_distrib` удалена — держим собственную копию). -/
theorem sum_add_distrib' {ι M : Type*} [AddCommMonoid M] (u : Finset ι) (f g : ι → M) :
    (∑ i ∈ u, (f i + g i)) = (∑ i ∈ u, f i) + (∑ i ∈ u, g i) := by
  classical
  induction u using Finset.induction_on with
  | empty => simp
  | insert a u ha ih => simp only [Finset.sum_insert ha, ih]; abel

/-! ## Биты и переключение битов -/

/-- `star` тривиален на вещественных скалярах в `ℂ`. -/
theorem star_ofReal' (r : ℝ) : star ((r : ℝ) : ℂ) = ((r : ℝ) : ℂ) :=
  Complex.conj_ofReal r

/-- Значение τ: `+1` для бита 0 (собственное значение σ_z), `−1` для бита 1. -/
def tau (b : Fin 2) : ℝ := if b = 0 then 1 else -1

theorem bit_cases (b : Fin 2) : b = 0 ∨ b = 1 := by fin_cases b <;> simp

theorem tau_cases (b : Fin 2) : tau b = 1 ∧ b = 0 ∨ tau b = -1 ∧ b = 1 := by
  fin_cases b <;> simp [tau]

/-- Инверсия бита в `Fin 2` — инволюция. -/
theorem fin2_sub_invol : ∀ b : Fin 2, (1 : Fin 2) - (1 - b) = b := by decide

theorem fin2_sub_ne : ∀ a b : Fin 2, ((1 : Fin 2) - a ≠ 1 - b) ↔ a ≠ b := by decide

/-- Переключение битов `s` и `t` конфигурации (инволюция на `Cfg`). -/
def flipTwo (s t : Slot) (x : Cfg) : Cfg := fun u =>
  if u = s ∨ u = t then (1 - x u : Fin 2) else x u

theorem flipTwo_invol (s t : Slot) (x : Cfg) : flipTwo s t (flipTwo s t x) = x := by
  funext u
  by_cases h : u = s ∨ u = t
  · simp only [flipTwo, if_pos h]
    rw [fin2_sub_invol]
  · simp only [flipTwo, if_neg h]

theorem flipTwo_bijective (s t : Slot) : Function.Bijective (flipTwo s t) := by
  constructor
  · intro a b hab
    have := congrArg (flipTwo s t) hab
    rwa [flipTwo_invol, flipTwo_invol] at this
  · intro b
    exact ⟨flipTwo s t b, flipTwo_invol s t b⟩

theorem star_mul_self (c : ℂ) : star c * c = ((‖c‖ : ℝ) : ℂ) ^ 2 := by
  rw [Complex.star_def, mul_comm, Complex.mul_conj,
    ← Complex.norm_mul_self_eq_normSq, pow_two, Complex.ofReal_mul]

/-! ## H₀: диагональная часть -/

/-- Вклад слота `s` в `H₀`: диагональная матрица
`H_s = ½(I − √(1+2δ_s²)·σ_z^{(s)})`, встроенная в полное пространство. -/
noncomputable def H0site (phase : Slot → ℝ) (s : Slot) : Matrix Cfg Cfg ℂ :=
  Matrix.diagonal fun x =>
    (((1 - √(1 + 2 * phase s ^ 2) * tau (x s)) / 2 : ℝ) : ℂ)

/-- `H₀ = Σ_s H_s`. -/
noncomputable def H0 (phase : Slot → ℝ) : Matrix Cfg Cfg ℂ := ∑ s, H0site phase s

theorem H0site_isHermitian (phase : Slot → ℝ) (s : Slot) :
    IsHermitian (H0site phase s) := by
  show (H0site phase s).conjTranspose = H0site phase s
  ext x y
  simp only [H0site, Matrix.conjTranspose_apply, Matrix.diagonal_apply]
  by_cases h : x = y
  · subst h
    rw [if_pos rfl, star_ofReal']
  · have hyx : ¬(y = x) := fun hc => h hc.symm
    rw [if_neg hyx, if_neg h, star_zero]

theorem conjTranspose_sum {ι : Type*} [DecidableEq ι] (u : Finset ι)
    (A : ι → Matrix Cfg Cfg ℂ) :
    (∑ s ∈ u, A s).conjTranspose = ∑ s ∈ u, (A s).conjTranspose := by
  classical
  induction u using Finset.induction_on with
  | empty => simp
  | insert a u ha ih =>
      simp [Finset.sum_insert ha, ih, Matrix.conjTranspose_add]

theorem H0_isHermitian (phase : Slot → ℝ) : IsHermitian (H0 phase) := by
  show (∑ s, H0site phase s).conjTranspose = ∑ s, H0site phase s
  rw [conjTranspose_sum]
  exact Finset.sum_congr rfl fun s _ => H0site_isHermitian phase s

/-! ## V: связь по 22-циклу -/

/-- Элемент связи для ребра `(s, s+1)`: `σx^{(s)}σx^{(s+1)} + σy^{(s)}σy^{(s+1)}`
в матричной записи: переводит конфигурацию `x` в `flipTwo`-соседа с
амплитудой 2 при несовпадении битов, иначе 0. -/
noncomputable def bondTerm (s : Slot) : Matrix Cfg Cfg ℂ :=
  Matrix.of fun x y =>
    if y = flipTwo s (s + 1) x then
      (if x s ≠ x (s + 1) then ((2 : ℝ) : ℂ) else (0 : ℂ))
    else (0 : ℂ)

theorem bondTerm_symm (s : Slot) (x y : Cfg) :
    (y = flipTwo s (s + 1) x ∧ x s ≠ x (s + 1)) ↔
      (x = flipTwo s (s + 1) y ∧ y s ≠ y (s + 1)) := by
  constructor
  · rintro ⟨h1, h2⟩
    refine ⟨by rw [h1, flipTwo_invol], ?_⟩
    have hy1 : y s = (1 : Fin 2) - x s := by rw [h1]; simp [flipTwo]
    have hy2 : y (s + 1) = (1 : Fin 2) - x (s + 1) := by rw [h1]; simp [flipTwo]
    rw [hy1, hy2]
    exact (fin2_sub_ne _ _).2 h2
  · rintro ⟨h1, h2⟩
    refine ⟨by rw [h1, flipTwo_invol], ?_⟩
    have hx1 : x s = (1 : Fin 2) - y s := by rw [h1]; simp [flipTwo]
    have hx2 : x (s + 1) = (1 : Fin 2) - y (s + 1) := by rw [h1]; simp [flipTwo]
    rw [hx1, hx2]
    exact (fin2_sub_ne _ _).2 h2

theorem bondTerm_isHermitian (s : Slot) : IsHermitian (bondTerm s) := by
  show (bondTerm s).conjTranspose = bondTerm s
  ext x y
  simp only [Matrix.conjTranspose_apply, Matrix.of_apply, bondTerm]
  by_cases hxy : y = flipTwo s (s + 1) x
  · by_cases hbits : x s ≠ x (s + 1)
    · obtain ⟨h1, h2⟩ := (bondTerm_symm s x y).1 ⟨hxy, hbits⟩
      rw [if_pos hxy, if_pos hbits, if_pos h1, if_pos h2, star_ofReal']
    · push_neg at hbits
      have hbity : y s = y (s + 1) := by
        have hy1 : y s = (1 : Fin 2) - x s := by rw [hxy]; simp [flipTwo]
        have hy2 : y (s + 1) = (1 : Fin 2) - x (s + 1) := by rw [hxy]; simp [flipTwo]
        rw [hy1, hy2, hbits]
      have hfl : x = flipTwo s (s + 1) y := by rw [hxy, flipTwo_invol]
      rw [if_pos hxy, if_neg (not_not.mpr hbits), if_pos hfl,
        if_neg (not_not.mpr hbity), star_zero]
  · have hcontra : x = flipTwo s (s + 1) y → False := by
      intro hc
      refine hxy ?_
      rw [hc, flipTwo_invol]
    rw [if_neg hxy, if_neg hcontra, star_zero]

/-- `V = J·Σ_s bondTerm s` — связь по всем 22 рёбрам цикла. -/
noncomputable def V (J : ℝ) : Matrix Cfg Cfg ℂ := ((J : ℝ) : ℂ) • ∑ s, bondTerm s

theorem V_isHermitian (J : ℝ) : IsHermitian (V J) := by
  show (((J : ℝ) : ℂ) • ∑ s, bondTerm s).conjTranspose
      = ((J : ℝ) : ℂ) • ∑ s, bondTerm s
  rw [Matrix.conjTranspose_smul, star_ofReal', conjTranspose_sum]
  exact congrArg _ (Finset.sum_congr rfl fun s _ => bondTerm_isHermitian s)

/-! ## Квадратичная форма -/

/-- Квадратичная форма: `⟨v|M|v⟩ = Σ_x star (v x) · (M *ᵥ v) x`. -/
noncomputable def qform (M : Matrix Cfg Cfg ℂ) (v : Vec) : ℂ :=
  ∑ x, star (v x) * (M *ᵥ v) x

theorem qform_add (M N : Matrix Cfg Cfg ℂ) (v : Vec) :
    qform (M + N) v = qform M v + qform N v := by
  simp only [qform, Matrix.add_mulVec, Pi.add_apply, mul_add]
  rw [sum_add_distrib']

theorem qform_smul (c : ℂ) (M : Matrix Cfg Cfg ℂ) (v : Vec) :
    qform (c • M) v = c * qform M v := by
  simp only [qform, Matrix.smul_mulVec_assoc, Pi.smul_apply, smul_eq_mul, Finset.mul_sum]
  exact Finset.sum_congr rfl fun x _ => by ring

theorem qform_sum {ι : Type*} [DecidableEq ι] (u : Finset ι)
    (A : ι → Matrix Cfg Cfg ℂ) (v : Vec) :
    qform (∑ s ∈ u, A s) v = ∑ s ∈ u, qform (A s) v := by
  classical
  induction u using Finset.induction_on with
  | empty => simp [qform, star_zero]
  | insert a u ha ih =>
      simp only [Finset.sum_insert ha, qform_add, ih, Finset.sum_insert ha]

/-! ## Вещественность диагональной формы -/

/-- Сумма вещественных коэрций — коэрция суммы. -/
theorem sum_ofReal {ι : Type*} (u : Finset ι) (f : ι → ℝ) :
    (∑ s ∈ u, ((f s : ℝ) : ℂ)) = (((∑ s ∈ u, f s : ℝ) : ℝ) : ℂ) := by
  classical
  induction u using Finset.induction_on with
  | empty => simp
  | insert a u ha ih =>
      rw [Finset.sum_insert ha, ih, ← Complex.ofReal_add, Finset.sum_insert ha,
        add_comm (f a) (∑ s ∈ u, f s)]

/-- Квадратичная форма вещественной диагональной матрицы вещественна:
`⟨v|diag d|v⟩ = Σ_x d_x·|v_x|²`. -/
theorem qform_diagonal_ofReal (d : Cfg → ℝ) (v : Vec) :
    qform (Matrix.diagonal fun x => ((d x : ℝ) : ℂ)) v =
      ((∑ x, d x * (‖v x‖ : ℝ) ^ 2 : ℝ) : ℂ) := by
  unfold qform
  rw [← sum_ofReal]
  refine Finset.sum_congr rfl fun x _ => ?_
  have hzero : ∀ b ∈ Finset.univ, b ≠ x →
      (Matrix.diagonal fun x => ((d x : ℝ) : ℂ)) x b * v b = 0 := by
    intro b _ hb
    rw [Matrix.diagonal_apply, if_neg (Ne.symm hb), zero_mul]
  rw [Matrix.mulVec, dotProduct, Finset.sum_eq_single_of_mem x (Finset.mem_univ x) hzero,
    Matrix.diagonal_apply, if_pos rfl]
  have h1 : star (v x) * (((d x : ℝ) : ℂ) * v x)
      = ((d x : ℝ) : ℂ) * (star (v x) * v x) := by
    rw [← mul_assoc, mul_comm (star (v x)) ((d x : ℝ) : ℂ), mul_assoc]
  rw [h1, star_mul_self (v x), Complex.ofReal_mul, Complex.ofReal_pow]

/-- Сумма делений на 2 равна делению суммы на 2. -/
theorem sum_div_two {ι : Type*} [Fintype ι] (F : ι → ℝ) :
    (∑ i : ι, F i / 2) = (∑ i : ι, F i) * (2:ℝ)⁻¹ := by
  rw [Finset.sum_congr rfl fun i (_ : i ∈ Finset.univ) => div_eq_mul_inv _ _,
    ← Finset.sum_mul _ _ ((2 : ℝ)⁻¹)]

/-- Квадратичная форма `H₀` в явном вещественном виде. -/
theorem qform_H0_val (phase : Slot → ℝ) (v : Vec) :
    qform (H0 phase) v =
      ((∑ x : Cfg, ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)))) / 2 *
        (‖v x‖ : ℝ) ^ 2 : ℝ) : ℂ) := by
  show qform (∑ s : Slot, H0site phase s) v =
      ((∑ x : Cfg, ((∑ s : Slot, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)))) / 2 *
        (‖v x‖ : ℝ) ^ 2 : ℝ) : ℂ)
  rw [qform_sum]
  have hsite : ∀ s : Slot, qform (H0site phase s) v =
      ((∑ x : Cfg, (1 - √(1 + 2 * phase s ^ 2) * tau (x s)) / 2 *
        (‖v x‖ : ℝ) ^ 2 : ℝ) : ℂ) :=
    fun s => qform_diagonal_ofReal (fun x => (1 - √(1 + 2 * phase s ^ 2) * tau (x s)) / 2) v
  rw [Finset.sum_congr rfl fun s _ => hsite s, sum_ofReal, Finset.sum_comm (β := ℝ),
    ← sum_ofReal, ← sum_ofReal]
  refine Finset.sum_congr rfl fun x _ => ?_
  have hsumdiv : ∀ F : Slot → ℝ, (∑ i : Slot, F i / 2) = (∑ i : Slot, F i) / 2 := by
    intro F
    rw [Finset.sum_congr rfl fun i (_ : i ∈ Finset.univ) => div_eq_mul_inv _ _,
      ← Finset.sum_mul _ _ ((2 : ℝ)⁻¹), div_eq_mul_inv]
  rw [Complex.ofReal_inj, ← Finset.sum_mul _ _ ((‖v x‖ : ℝ) ^ 2),
    hsumdiv (fun i => (1 - √(1 + 2 * phase i ^ 2) * tau (x i)))]

/-! ## Оценка нормы связи -/

theorem two_mul_le_sq_add (a b : ℝ) : 2 * a * b ≤ a ^ 2 + b ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

theorem norm_star_eq (z : ℂ) : ‖star z‖ = ‖z‖ := by
  rw [Complex.star_def]
  exact Complex.norm_conj z

/-- Действие `bondTerm s` на вектор. -/
theorem mulVec_bondTerm (s : Slot) (v : Vec) (x : Cfg) :
    (bondTerm s *ᵥ v) x =
      (if x s ≠ x (s + 1) then ((2 : ℝ) : ℂ) * v (flipTwo s (s + 1) x) else (0 : ℂ)) := by
  rw [Matrix.mulVec, dotProduct]
  by_cases hP : x s ≠ x (s + 1)
  · simp [bondTerm, Matrix.of_apply, hP]
  · push_neg at hP
    simp [bondTerm, Matrix.of_apply, hP]

/-- Действие вещественной диагональной матрицы на вектор. -/
theorem mulVec_diagonal (d : Cfg → ℝ) (v : Vec) (x : Cfg) :
    ((Matrix.diagonal fun x => ((d x : ℝ) : ℂ)) *ᵥ v) x = ((d x : ℝ) : ℂ) * v x := by
  rw [Matrix.mulVec, dotProduct]
  simp [Matrix.diagonal_apply]

/-- Оценка квадратичной формы одного ребра: `|⟨v|bondTerm s|v⟩| ≤ 2‖v‖²`. -/
theorem qform_bond_le (s : Slot) (v : Vec) :
    ‖qform (bondTerm s) v‖ ≤ 2 * nrm2 v := by
  have hstep : ∀ x : Cfg,
      ‖star (v x) * (bondTerm s *ᵥ v) x‖ ≤
        (‖v x‖ : ℝ) ^ 2 + (‖v (flipTwo s (s + 1) x)‖ : ℝ) ^ 2 := by
    intro x
    rw [mulVec_bondTerm]
    by_cases hP : x s ≠ x (s + 1)
    · have h2 : ‖((2 : ℝ) : ℂ)‖ = 2 := by
        rw [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (by norm_num)]
      rw [if_pos hP, norm_mul, norm_mul, norm_star_eq, h2]
      linarith [two_mul_le_sq_add (‖v x‖ : ℝ) (‖v (flipTwo s (s + 1) x)‖ : ℝ)]
    · rw [if_neg hP, mul_zero, norm_zero]
      positivity
  calc ‖qform (bondTerm s) v‖
      = ‖∑ x, star (v x) * (bondTerm s *ᵥ v) x‖ := rfl
    _ ≤ ∑ x, ((‖v x‖ : ℝ) ^ 2 + (‖v (flipTwo s (s + 1) x)‖ : ℝ) ^ 2) := by
        exact le_trans (norm_sum_le _ _) (Finset.sum_le_sum fun x _ => hstep x)
    _ = ∑ x, (‖v x‖ : ℝ) ^ 2 + ∑ x, (‖v (flipTwo s (s + 1) x)‖ : ℝ) ^ 2 :=
        sum_add_distrib' Finset.univ _ _
    _ = ∑ x, (‖v x‖ : ℝ) ^ 2 + ∑ x, (‖v x‖ : ℝ) ^ 2 :=
        congrArg₂ (· + ·) rfl
          ((flipTwo_bijective s (s + 1)).sum_comp fun x => (‖v x‖ : ℝ) ^ 2)
    _ = 2 * nrm2 v := by
        rw [two_mul]
        rfl

/-- Оценка связи: `|⟨v|V|v⟩| ≤ 44·|J|·‖v‖²` (22 ребра × норма 2).
Грубая оценка треугольником; точная JW-норма `28.1067|J|` считается численно
в `scripts/verify_septinal.py`. -/
theorem qform_V_le (J : ℝ) (v : Vec) :
    ‖qform (V J) v‖ ≤ 44 * |J| * nrm2 v := by
  rw [V, qform_smul, qform_sum, norm_mul, Complex.norm_real, Real.norm_eq_abs]
  have h1 : |J| * ‖∑ s, qform (bondTerm s) v‖ ≤ |J| * ∑ s, ‖qform (bondTerm s) v‖ :=
    mul_le_mul_of_nonneg_left (norm_sum_le _ _) (abs_nonneg J)
  have h2 : |J| * ∑ s, ‖qform (bondTerm s) v‖ ≤ |J| * ∑ s : Slot, (2 * nrm2 v) :=
    mul_le_mul_of_nonneg_left
      (Finset.sum_le_sum fun s _ => qform_bond_le s v) (abs_nonneg J)
  refine le_trans (le_trans h1 h2) ?_
  have hsum22 : ∑ s : Slot, (2 * nrm2 v) = 44 * nrm2 v := by
    simp [numSlots]; ring
  rw [hsum22]
  exact le_of_eq (by ring)

/-! ## Полный гамильтониан -/

/-- **Септинальный гамильтониан** `H_Sept = H₀ + V` (Шаг 2 плана).
Без свободных параметров: фазы заданы на слотах, `J` — единственная
константа связи с порогом `|J| < Δ₀/44`. -/
noncomputable def HSept (phase : Slot → ℝ) (J : ℝ) : Matrix Cfg Cfg ℂ :=
  H0 phase + V J

/-- **Лемма 2 плана (`septinal_hamiltonian_hermitian`).**
Полный септинальный гамильтониан самосопряжён. -/
theorem HSept_isHermitian (phase : Slot → ℝ) (J : ℝ) :
    IsHermitian (HSept phase J) := by
  show (H0 phase + V J).conjTranspose = H0 phase + V J
  rw [Matrix.conjTranspose_add]
  exact congrArg₂ (· + ·) (H0_isHermitian phase) (V_isHermitian J)


end Septinal
