import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Real.Pi.Bounds
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Complex.Norm
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.ConjTranspose
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FieldSimp

/-!
# Септинальные данные и локальный бэрри-гамильтониан (Шаг 1)

Данные: `D \ G` — 22-вершинный цикл, разбиение `A ⊔ B`, фаза сектора `C`
`δ_C = π/7`. Привязка фаз к слотам фиксируется один раз, свободных параметров нет.

* `Slot`, `numSlots`, `deltaC` — септинальные данные;
* `berryGap δ = √(1 + 2δ²)` — локальный зазор Berry-модели;
* `HLocal` — локальный гамильтониан `H_s = ½(I − √(1+2δ_s²)·σ_z)`;
* `berry_local_gap` — лемма 1 плана;
* `cmin` — минимальный по слотам локальный зазор;
* `berryGap_septinal_approx` — вычислимая оценка зазора при `δ_C = π/7`:
  `Δ_Berry(π/7) = 1.184416 ± 10⁻⁶` (в плане стояло «≈ 1.203» —
  арифметическая неточность плана).
-/

open scoped Real

namespace Septinal

/-- Эрмитовость матрицы: `Mᴴ = M` (стандартное определение; собственная копия,
чтобы не тянуть спектральный модуль `Mathlib.LinearAlgebra.Matrix.Hermitian`). -/
def IsHermitian {n : Type} (M : Matrix n n ℂ) : Prop := M.conjTranspose = M

/-- Число слотов: `|D \ G| = 22` (abbrev — чтобы instance-поиск видел `22`). -/
abbrev numSlots : ℕ := 22

/-- Слоты — вершины 22-цикла `D \ G`. -/
abbrev Slot : Type := Fin numSlots

/-- Фаза сектора C: `δ_C = π/7`. -/
noncomputable def deltaC : ℝ := π / 7

/-- Локальный зазор Berry-модели: `Δ_Berry(δ) = √(1 + 2δ²)`. -/
noncomputable def berryGap (δ : ℝ) : ℝ := √(1 + 2 * δ ^ 2)

/-- Локальный бэрри-гамильтониан слота: `H_s = ½(I − √(1+2δ_s²)·σ_z)`
как эрмитова 2×2-матрица (элементы вещественны). -/
noncomputable def HLocal (δ : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  Matrix.of
    ![![(((1 - √(1 + 2 * δ ^ 2)) / 2 : ℝ) : ℂ), ((0 : ℝ) : ℂ)],
      ![((0 : ℝ) : ℂ), (((1 + √(1 + 2 * δ ^ 2)) / 2 : ℝ) : ℂ)]]

/-- **Лемма 1 плана (`berry_local_gap`).** Локальный зазор строго положителен. -/
theorem berry_local_gap (δ : ℝ) : 0 < berryGap δ := by
  unfold berryGap
  have h1 : (1 : ℝ) ≤ 1 + 2 * δ ^ 2 := by nlinarith [sq_nonneg δ]
  calc (0 : ℝ) < 1 := zero_lt_one
    _ = √(1 : ℝ) := (Real.sqrt_one).symm
    _ ≤ √(1 + 2 * δ ^ 2) := Real.sqrt_le_sqrt h1

/-- Локальный гамильтониан самосопряжён. -/
theorem HLocal_isHermitian (δ : ℝ) : IsHermitian (HLocal δ) := by
  show (HLocal δ).conjTranspose = HLocal δ
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [HLocal, Matrix.conjTranspose_apply, Complex.star_def, Complex.conj_ofReal]

/-- Фаза сектора C положительна. -/
theorem deltaC_pos : 0 < deltaC := by
  unfold deltaC
  exact div_pos Real.pi_pos (by norm_num)

/-- Минимальный по слотам локальный зазор: `Δ₀ = min_s √(1 + 2δ_s²)`. -/
noncomputable def cmin (phase : Slot → ℝ) : ℝ :=
  (Finset.univ.image fun s : Slot => √(1 + 2 * phase s ^ 2)).min'
    ⟨√(1 + 2 * phase 0 ^ 2),
      Finset.mem_image.2 ⟨(0 : Slot), Finset.mem_univ 0, rfl⟩⟩

/-- Минимальный зазор мажорируется каждым локальным. -/
theorem cmin_le (phase : Slot → ℝ) (s : Slot) :
    cmin phase ≤ √(1 + 2 * phase s ^ 2) := by
  unfold cmin
  have hmem : √(1 + 2 * phase s ^ 2)
      ∈ Finset.univ.image fun s : Slot => √(1 + 2 * phase s ^ 2) :=
    Finset.mem_image.2 ⟨s, Finset.mem_univ s, rfl⟩
  exact (Finset.isLeast_min' _ _).2 (by simpa using hmem)

/-- Каждый локальный зазор ≥ 1, поэтому и минимум ≥ 1: зазор отделён от нуля
безо всяких гипотез на фазы. -/
theorem one_le_cmin (phase : Slot → ℝ) : 1 ≤ cmin phase := by
  unfold cmin
  rw [Finset.le_min'_iff]
  intro y hy
  obtain ⟨s, -, rfl⟩ := Finset.mem_image.1 hy
  have h1 : (1 : ℝ) ≤ 1 + 2 * phase s ^ 2 := by nlinarith [sq_nonneg (phase s)]
  calc (1 : ℝ) = √(1 : ℝ) := (Real.sqrt_one).symm
    _ ≤ √(1 + 2 * phase s ^ 2) := Real.sqrt_le_sqrt h1

/-- Числовая оценка: `Δ_Berry(π/7) = 1.184416 ± 10⁻⁶`.
(В плане стояло «≈ 1.203» — ошибка; точное значение 1.184415888…,
см. `scripts/verify_septinal.py`.) -/
theorem berryGap_septinal_approx : |berryGap deltaC - 1.184416| < 1e-6 := by
  have hpid1 : (3.141592 : ℝ) < π := Real.pi_gt_d6
  have hpid2 : π < (3.141593 : ℝ) := Real.pi_lt_d6
  have hlow : (3.141592 : ℝ) / 7 < π / 7 := by linarith
  have hhigh : π / 7 < (3.141593 : ℝ) / 7 := by linarith
  have hpos7 : (0 : ℝ) ≤ π / 7 := by positivity
  have hposd1 : (0 : ℝ) ≤ 3.141592 / 7 := by positivity
  have hposd2 : (0 : ℝ) ≤ 3.141593 / 7 := by positivity
  have hs1 : ((3.141592 : ℝ) / 7) ^ 2 < (π / 7) ^ 2 := by
    nlinarith [hlow, hpos7, hposd1]
  have hs2 : (π / 7) ^ 2 < ((3.141593 : ℝ) / 7) ^ 2 := by
    nlinarith [hhigh, hpos7, hposd2]
  have hlo : (1.184415 : ℝ) ^ 2 < 1 + 2 * (π / 7) ^ 2 := by linarith
  have hhi : 1 + 2 * (π / 7) ^ 2 < (1.184417 : ℝ) ^ 2 := by linarith
  have h0lo : (0 : ℝ) ≤ (1.184415 : ℝ) ^ 2 := by positivity
  have h0hi : (0 : ℝ) ≤ 1 + 2 * (π / 7) ^ 2 := by positivity
  rw [abs_lt]
  have hΔ : berryGap deltaC = √(1 + 2 * (π / 7) ^ 2) := rfl
  constructor
  · -- нижняя граница: Δ_Berry(π/7) > 1.184416 − 10⁻⁶ = 1.184415
    have h := Real.sqrt_lt_sqrt h0lo hlo
    rw [Real.sqrt_sq (show (0 : ℝ) ≤ 1.184415 by positivity)] at h
    linarith [h, hΔ]
  · -- верхняя граница: Δ_Berry(π/7) < 1.184416 + 10⁻⁶ = 1.184417
    have h := Real.sqrt_lt_sqrt h0hi hhi
    rw [Real.sqrt_sq (show (0 : ℝ) ≤ 1.184417 by positivity)] at h
    linarith [h, hΔ]

end Septinal
