# `Choptuik/`

[Septinal/lean](../README_ru.md) · 

Библиотека I — **критические явления**: арена дважды нулевых координат, полевые уравнения Эйнштейна–скаляра, существование и единственность ДСС, спектр и закон масштабирования, сертификатный мост. Корень: [`../Choptuik.lean`](../Choptuik.lean) · сборка: `lake build`.

## Файлы

| Модуль | Строк | Объявления |
|---|--:|---|
| [`FieldEquations.lean`](Analysis/FieldEquations.lean) | 899 | 56 (6 theorem · 32 lemma · 15 def · 3 structure) |
| [`HyperbolicPDE.lean`](Analysis/HyperbolicPDE.lean) | 101 | 5 (1 theorem · 3 def · 1 structure) |
| [`Interval.lean`](Analysis/Interval.lean) | 134 | 12 (7 theorem · 4 def · 1 structure) |
| [`Certificates.lean`](Bridge/Certificates.lean) | 473 | 15 (6 theorem · 6 def · 3 structure) |
| [`Discharge.lean`](Bridge/Discharge.lean) | 318 | 15 (12 theorem · 3 def) |
| [`Generated.lean`](Bridge/Generated.lean) | 130 | 23 (16 theorem · 7 def) |
| [`DSS.lean`](Existence/DSS.lean) | 325 | 7 (4 theorem · 2 def · 1 structure) |
| [`DSSBoundary.lean`](Existence/DSSBoundary.lean) | 322 | 20 (7 theorem · 2 lemma · 10 def · 1 structure) |
| [`ImplicitFunction.lean`](Existence/ImplicitFunction.lean) | 402 | 7 (5 theorem · 1 def · 1 structure) |
| [`TruncatedDSS.lean`](Existence/TruncatedDSS.lean) | 174 | 6 (2 theorem · 4 def) |
| [`Basic.lean`](Geometry/Basic.lean) | 82 | 6 (4 def · 2 structure) |
| [`Curvature.lean`](Geometry/Curvature.lean) | 129 | 6 (2 theorem · 3 def · 1 structure) |
| [`Scaling.lean`](Scaling.lean) | 212 | 5 (3 theorem · 2 def) |
| [`ScalingDerivation.lean`](ScalingDerivation.lean) | 239 | 16 (5 theorem · 5 lemma · 5 def · 1 structure) |
| [`Gershgorin.lean`](Stability/Gershgorin.lean) | 106 | 1 (1 theorem) |
| [`Linearization.lean`](Stability/Linearization.lean) | 52 | 4 (2 def · 2 structure) |
| [`Spectrum.lean`](Stability/Spectrum.lean) | 403 | 13 (9 theorem · 4 def) |

**Флагманские теоремы.**
- [`critical_solution_exists`](../Choptuik/Existence/DSS.lean)
- [`critical_solution_unique`](../Choptuik/Existence/DSS.lean)
- [`unique_unstable_mode`](../Choptuik/Stability/Spectrum.lean) — - The echoing period is positive.
- [`mass_scaling_law`](../Choptuik/Stability/Spectrum.lean)
- [`gamma_close_to_published`](../Choptuik/Scaling.lean)
- [`newton_kantorovich_local`](../Choptuik/Bridge/Certificates.lean)
- [`add_sound`](../Choptuik/Analysis/Interval.lean) — - Membership in an interval.
- [`mul_sound`](../Choptuik/Analysis/Interval.lean) — - For a fixed factor `x`, the products of `x` with the two bound points enclose `x * y` whenever `y` lies between them.
- [`certificate_principle`](../Choptuik/Analysis/Interval.lean)

## Сборка

```bash
`lake build`
```

---

Назад к пакету: [README Septinal/lean](../README_ru.md)
