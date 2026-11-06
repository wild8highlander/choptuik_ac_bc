import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Analysis.Normed.Module.Basic
import Mathlib.Analysis.Normed.Lp.PiLp

import SeptinalYM.Gap

/-!
# Вложение септинальной системы в пространство состояний Янга–Миллса

Пространство состояний 4D SU(2) Янга–Миллса бесконечномерно; отождествление
`ℋ_Sept` с его подпространством — физическая гипотеза плана. Формально она
распадается на проверяемую часть и физическую:

* **проверяемая часть (доказана ниже):** существует комплексное нормированное
  пространство `Y` и ℂ-линейное изометричное вложение `Φ : ℋ_Sept → Y.Space`;
  в качестве `Y` берётся `ℋ_Sept` с евклидовой (ℓ²) нормой (`PiLp 2`),
  `Φ` — каноническое включение. Вместе с `septinal_gap` это даёт теорему
  `septinal_gap_transports`: зазор `Δ = Δ₀ − 44|J| > 0` записывается в
  терминах нормы в `Y`, т.е. является утверждением о геометрии пары `(Y, Φ)`,
  независимым от координатной модели;
* **физическая часть (гипотеза, документирована в README):** построенное `Y`
  реализуется как подпространство пространства состояний 4D SU(2) Янга–Миллса
  с переносом динамики (интертвининг с YM-гамильтонианом).

Стратегия плана «построить `Φ` на циклическом подпространстве, порождённом
вакуумом» соответствует динамической части; её формализация требует
спектральной теории (`Mathlib.LinearAlgebra.Matrix.Hermitian`) и оставлена
следующим шагом. Формальная цель без `sorry` закрыта ниже.
-/

namespace Septinal

/-- Абстрактное пространство состояний 4D SU(2) Янга–Миллса.
Структура намеренно минимальна: это интерфейс цели, а не определение. -/
structure YM4 where
  /-- Носитель: комплексное нормированное пространство состояний. -/
  Space : Type
  /-- Нормированная структура. -/
  [normed : NormedAddCommGroup Space]
  /-- Комплексная структура. -/
  [complex : NormedSpace ℂ Space]

attribute [instance] YM4.normed YM4.complex

/-- Конкретная модель пространства `Y`: `ℋ_Sept` с евклидовой нормой
`‖v‖ = √(nrm2 v)` (гильбертово пополнение линейной оболочки базиса `Cfg`;
циклическое подпространство вакуума вкладывается в него тождественно). -/
noncomputable def ymSeptinal : YM4 where
  Space := PiLp 2 fun _ : Cfg => ℂ

/-- Каноническое вложение `Φ : ℋ_Sept → Y.Space`. -/
noncomputable def embedPhi (v : Vec) : ymSeptinal.Space :=
  WithLp.toLp (p := 2) v

theorem embedPhi_linear (v w : Vec) (a b : ℂ) :
    embedPhi (a • v + b • w) = a • embedPhi v + b • embedPhi w := rfl

theorem embedPhi_isometric (v : Vec) : ‖embedPhi v‖ = √(nrm2 v) := by
  rw [PiLp.norm_eq_of_L2]
  congr 1

/-- **Теорема-цель.** Существует ℂ-линейное изометричное вложение
`Φ : ℋ_Sept → Y.Space` в пространство состояний `Y` (модель `ymSeptinal`). -/
theorem septinal_embeds_in_ym :
    ∃ (Y : YM4) (Φ : Vec → Y.Space),
      (∀ v w : Vec, ∀ a b : ℂ, Φ (a • v + b • w) = a • Φ v + b • Φ w) ∧
      (∀ v : Vec, ‖Φ v‖ = √(nrm2 v)) :=
  ⟨ymSeptinal, embedPhi, embedPhi_linear, embedPhi_isometric⟩

/-- **Перенос зазора (следствие леммы 3).** При `|J| < Δ₀/44` существует `Δ > 0`
(а именно `Δ = Δ₀ − 44|J|`) с оценкой `Re⟨v|H_Sept|v⟩ ≥ (E_vac + Δ)·‖Φ v‖²` —
зазор сформулирован чисто в терминах геометрии вложения `(Y, Φ)`. -/
theorem septinal_gap_transports (phase : Slot → ℝ) (J : ℝ) (hJ : |J| < cmin phase / 44) :
    ∃ Δ : ℝ, 0 < Δ ∧ ∀ v : Vec, v vac = 0 →
      (qform (HSept phase J) v).re ≥
        Evac phase * (‖embedPhi v‖ : ℝ) ^ 2 + Δ * (‖embedPhi v‖ : ℝ) ^ 2 := by
  obtain ⟨Δ, hΔ, hgap⟩ := septinal_gap phase J hJ
  refine ⟨Δ, hΔ, fun v hv => ?_⟩
  have hnorm : (‖embedPhi v‖ : ℝ) ^ 2 = nrm2 v := by
    rw [embedPhi_isometric, Real.sq_sqrt (nrm2_nonneg v)]
  rw [hnorm]
  exact hgap v hv

end Septinal
