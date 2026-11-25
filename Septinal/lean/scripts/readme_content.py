# -*- coding: utf-8 -*-
"""Курированные описания модулей для readme_gen.py (EN + RU).

Один модуль — один словарь: путь → {en, ru}. Кратко, по существу, без воды;
числа (строки, теоремы) подставляет readme_gen.py из source_stats.json.
"""

CURATED = {
    # ════════════════════════ Library I · Choptuik ════════════════════════
    'Choptuik.lean': {
        'en': 'Root module of Library I. Contains the hand-drawn namespace map and re-exports all 17 theory modules — the single import target of the axiom audit.',
        'ru': 'Корневой модуль библиотеки I. Содержит нарисованную от руки карту пространств имён и ре-экспортирует все 17 теоретических модулей — единственная точка импорта для аксиомного аудита.',
    },
    'Choptuik/Geometry/Basic.lean': {
        'en': 'The double-null arena `ds² = −e^{2f(u,v)} du dv + r(u,v)² dΩ²`: `DoubleNullData`, areal positivity, smoothness, spherical symmetry, `MassAspect` and the `BlackHoleFormed` predicate.',
        'ru': 'Арена дважды нулевых координат `ds² = −e^{2f(u,v)} du dv + r(u,v)² dΩ²`: `DoubleNullData`, положительность areal-радиуса, гладкость, сферическая симметрия, `MassAspect` и предикат `BlackHoleFormed`.',
    },
    'Choptuik/Geometry/Curvature.lean': {
        'en': 'Curvature bookkeeping and the isotropic (Weyl-finite) singularity — gap G3: `CurvatureProfile`, `StrongSingularity`, `IsotropicSingularity`, the repaired central claim and divergence invariance under homothetic rescaling.',
        'ru': 'Учёт кривизны и изотропная (конечная по Вейлю) сингулярность — разрыв G3: `CurvatureProfile`, `StrongSingularity`, `IsotropicSingularity`, восстановленное центральное утверждение и инвариантность расходимостей при омометрическом пересчёте.',
    },
    'Choptuik/Analysis/HyperbolicPDE.lean': {
        'en': 'The Einstein–scalar system `G_{μν} = 8π T_{μν}`, `□_g φ = 0` in spherical symmetry, reduced to first order for `(f, r, φ)`; `ClassicalSolution`, the constraint and wave operators, and `local_wellposedness` (shared with gap G1).',
        'ru': 'Система Эйнштейна–скаляра `G_{μν} = 8π T_{μν}`, `□_g φ = 0` в сферической симметрии, сведённая к системе первого порядка для `(f, r, φ)`; `ClassicalSolution`, операторы связи и волны, теорема `local_wellposedness` (общая с разрывом G1).',
    },
    'Choptuik/Analysis/FieldEquations.lean': {
        'en': 'The field equations through REAL derivatives (work-plan item 1): slice operators `du/dv/duu/dvv/duv` on `ℝ`, the five reduced equations `eqUU…eqWave`, `IsSolution` as a genuine PDE system; then two solved models — `Minkowski.minkowski_isSolution` and exterior `Schwarzschild.schwarzschild_isSolution` via the tortoise ODE `R′ = (R−2M)/R` — and four Hawking-mass monotonicity theorems. The largest module of the library (899 lines).',
        'ru': 'Полевые уравнения через НАСТОЯЩИЕ производные (пункт 1 рабочего плана): срезовые операторы `du/dv/duu/dvv/duv` на `ℝ`, пять редуцированных уравнений `eqUU…eqWave`, `IsSolution` как настоящая система ДУЧП; далее два решённых образца — `Minkowski.minkowski_isSolution` и внешний `Schwarzschild.schwarzschild_isSolution` через тортиозное ОДУ `R′ = (R−2M)/R` — и четыре теоремы монотонности массы Хокинга. Крупнейший модуль библиотеки (899 строк).',
    },
    'Choptuik/Analysis/Interval.lean': {
        'en': 'Verified interval arithmetic (gap G5, resolved in v0.4): the `Interval` type, exact `add`/`mul`, soundness theorems `add_sound`/`mul_sound` with their one-dimensional enclosures, and the `certificate_principle`.',
        'ru': 'Верифицированная интервальная арифметика (разрыв G5, закрыт в v0.4): тип `Interval`, точные `add`/`mul`, теоремы корректности `add_sound`/`mul_sound` с их одномерными ограничениями и `certificate_principle`.',
    },
    'Choptuik/Existence/DSS.lean': {
        'en': 'Discrete self-similarity and the central existence theorem: the echoing covariance `f(τ+Δ,ρ) = e^{κΔ}·f(τ, e^{−Δ}ρ)`, the `CriticalSolution` package, `critical_solution_exists`, determination by the fundamental domain, `critical_solution_unique` and reparametrization invariance.',
        'ru': 'Дискретная самоподобность и центральная теорема существования: ковариация эхо-отображения `f(τ+Δ,ρ) = e^{κΔ}·f(τ, e^{−Δ}ρ)`, пакет `CriticalSolution`, `critical_solution_exists`, определённость по фундаментальной полосе, `critical_solution_unique` и инвариантность к репараметризации.',
    },
    'Choptuik/Existence/ImplicitFunction.lean': {
        'en': 'The Banach IFT route to existence (the Reiterer–Trubowitz heart): abstract `C1MapAt`/`DerivIsomorphism`, `newton_map_contractive`, `existence_via_implicit_function`, uniqueness of the Newton zero and persistence under perturbation.',
        'ru': 'Маршрут существования через банахову теорему о неявной функции (ядро Рейтерера–Трубовица): абстрактные `C1MapAt`/`DerivIsomorphism`, `newton_map_contractive`, `existence_via_implicit_function`, единственность нуля Ньютона и устойчивость к возмущениям.',
    },
    'Choptuik/Existence/DSSBoundary.lean': {
        'en': 'Items 3–6 of the work plan: self-similarity in the `(u,v)` arena, `minkowski_dss`/`minkowski_css`, the non-vacuousness warning `existence_vacuous_without_nondegeneracy`, similarity variables `(T, x)` and the equivalences `dss_iff_periodic`, `css_iff_constant`, `dss_solution_iff_periodic_bvp` — DSS + field equations ⇔ periodic boundary value problem.',
        'ru': 'Пункты 3–6 рабочего плана: самоподобность в арене `(u,v)`, `minkowski_dss`/`minkowski_css`, предупреждение о непустоте `existence_vacuous_without_nondegeneracy`, переменные подобия `(T, x)` и эквивалентности `dss_iff_periodic`, `css_iff_constant`, `dss_solution_iff_periodic_bvp` — ДСС + полевые уравнения ⇔ периодическая краевая задача.',
    },
    'Choptuik/Existence/TruncatedDSS.lean': {
        'en': 'Items 9–10: Newton–Kantorovich applied to the truncated DSS residual with a fully rational certificate (`β = 50/39`, `L = 3/50`, `r = 7/1000`, base `13/10`) checked by `norm_num` — `truncated_dss_solution_exists_unique`, with the unique root `√(5/3)` in `[1.2, 1.4]`.',
        'ru': 'Пункты 9–10: ньютоновско-канторовичевский шаг на усечённом остатке ДСС с полностью рациональным сертификатом (`β = 50/39`, `L = 3/50`, `r = 7/1000`, база `13/10`), проверяемым `norm_num`, — `truncated_dss_solution_exists_unique` с единственным корнем `√(5/3)` в `[1.2, 1.4]`.',
    },
    'Choptuik/Stability/Linearization.lean': {
        'en': 'Perturbation theory of the critical solution: `PerturbationMode` with growth rate, the `Unstable` predicate (`Re rate > 0`) and the `LinearizedOperator` with its abstract spectrum.',
        'ru': 'Теория возмущений критического решения: `PerturbationMode` со скоростью роста, предикат `Unstable` (`Re rate > 0`) и `LinearizedOperator` с абстрактным спектром.',
    },
    'Choptuik/Stability/Spectrum.lean': {
        'en': 'The spectral core (gap G2): calibrated constants `lambda0 = 2.6745`, `gamma = 1/λ₀`, `echoingPeriod` pinned to the published 3.445452402, the `certifiedSpectrum` hypothesis parameter, then `unique_unstable_mode`, `echo_family_structure` (spacing `2π/Δ`) and the log-log `mass_scaling_law`.',
        'ru': 'Спектральное ядро (разрыв G2): калиброванные константы `lambda0 = 2.6745`, `gamma = 1/λ₀`, `echoingPeriod`, приколоченный к опубликованному 3.445452402, гипотеза-параметр `certifiedSpectrum`, далее `unique_unstable_mode`, `echo_family_structure` (шаг `2π/Δ`) и `mass_scaling_law` в log-log-форме.',
    },
    'Choptuik/Stability/Gershgorin.lean': {
        'en': 'The spectral part without circularity: `gershgorin_disc` proved from scratch by the max-component eigenvector argument (mathlib v4.21 has no `Matrix.eigenvalue_mem_ball` — verified), for rational Galerkin matrices with an explicit truncation-tail hypothesis.',
        'ru': 'Спектральная часть без порочного круга: `gershgorin_disc` доказан с нуля через аргумент максимальной компоненты собственного вектора (в mathlib v4.21 нет `Matrix.eigenvalue_mem_ball` — проверено), для рациональных галёркинских матриц с явной гипотезой о хвосте усечения.',
    },
    'Choptuik/Scaling.lean': {
        'en': 'The headline predictions: `gammaChoptuik = 2000/5349` with `|γ − 0.374| < 10⁻³` **proved** (`gamma_close_to_published`), `universality` (constants depend only on field content) and the echoing formula `M_BH = |p−p*|^γ·F(ln|p−p*|/λ₀)`.',
        'ru': 'Флагманские предсказания: `gammaChoptuik = 2000/5349` с доказанным `|γ − 0.374| < 10⁻³` (`gamma_close_to_published`), `universality` (константы зависят только от состава полей) и эхо-формула `M_BH = |p−p*|^γ·F(ln|p−p*|/λ₀)`.',
    },
    'Choptuik/ScalingDerivation.lean': {
        'en': 'Item 7 — the scaling law DERIVED, not assumed: the `EchoModel` Poincaré map of a half-echo (multiplier `μ = e^{λ₀Δ/2}`), exit time and exit mass, `wiggle_periodic`, `scaling_law_derived` producing BOTH exponents, and `wiggle_published_check` (`λ₀Δ/2 ∈ [4.60, 4.62]`).',
        'ru': 'Пункт 7 — закон масштабирования ВЫВЕДЕН, а не принят: пуанкарево отображение `EchoModel` полушага эха (множитель `μ = e^{λ₀Δ/2}`), время и масса выхода, `wiggle_periodic`, `scaling_law_derived`, дающая ОБА показателя, и `wiggle_published_check` (`λ₀Δ/2 ∈ [4.60, 4.62]`).',
    },
    'Choptuik/Bridge/Certificates.lean': {
        'en': 'The certificate currency of the bridge (gap G4): `RatIv` rational intervals with `width`, the shared tolerances, `SpectrumCert`/`SpectrumChecks`, and the interpretation theorems `certified_unstable_pos`, `im_odd_multiple`, `spectrum_shape_of_certificate`, `newton_kantorovich_local`.',
        'ru': 'Валюта сертификатов моста (разрыв G4): рациональные интервалы `RatIv` с шириной, общие допуски, `SpectrumCert`/`SpectrumChecks` и интерпретационные теоремы `certified_unstable_pos`, `im_odd_multiple`, `spectrum_shape_of_certificate`, `newton_kantorovich_local`.',
    },
    'Choptuik/Bridge/Generated.lean': {
        'en': '**AUTO-GENERATED — do not edit** (producer: `python -m choptuik_service.certify emit`). Exact rational data: `lam0Iv`, the 7 decaying pairs of `spectrumCert`, `newtonBand`, `scalingIv`, `bandImageIv`, and 16 `check_*`/`*_generated` theorems proved by `norm_num` over the rationals.',
        'ru': '**АВТОГЕНЕРИРУЕТСЯ — не править руками** (продюсер: `python -m choptuik_service.certify emit`). Точные рациональные данные: `lam0Iv`, 7 затухающих пар `spectrumCert`, `newtonBand`, `scalingIv`, `bandImageIv` и 16 теорем `check_*`/`*_generated`, доказанных `norm_num` над рациональными числами.',
    },
    'Choptuik/Bridge/Discharge.lean': {
        'en': 'Closes the G4 loop — the theory layer consumes the certificates: `bridge_unique_unstable_mode` (G2 consumption), the correction-equation machinery (`correction_root_exists`, root in band, band image sound) landing on `√(5/3)`, and `scaling_agreement`.',
        'ru': 'Замыкает петлю G4 — теоретический слой потребляет сертификаты: `bridge_unique_unstable_mode` (потребление G2), механика уравнения поправки (`correction_root_exists`, корень в полосе, корректность образа полосы) с выходом на `√(5/3)` и `scaling_agreement`.',
    },
    'AxiomAudit.lean': {
        'en': 'The axiom audit: 26 `#print axioms` over every headline theorem of Library I. Discipline: `sorryAx` must never appear; the admissible output is exactly `[propext, Classical.choice, Quot.sound]`. Run: `lake env lean AxiomAudit.lean`.',
        'ru': 'Аксиомный аудит: 26 команд `#print axioms` по всем флагманским теоремам библиотеки I. Дисциплина: `sorryAx` появляться не должен; допустимый вывод — ровно `[propext, Classical.choice, Quot.sound]`. Запуск: `lake env lean AxiomAudit.lean`.',
    },
    # ════════════════════════ Library II · SeptinalYM ════════════════════════
    'SeptinalYM/Basic.lean': {
        'en': 'Step 1 — the septinal data and the local Berry Hamiltonian: the 22-slot cycle `D \\ G`, the `A ⊔ B` split, the sector-C phase `δ_C = π/7`, `HLocal = (I − √(1+2δ²)·σz)/2` with its proved local gap, `berryGap`, and the combinatorial constant `cmin`.',
        'ru': 'Шаг 1 — септинальные данные и локальный бэрри-гамильтониан: 22-вершинный цикл `D \\ G`, разбиение `A ⊔ B`, фаза сектора C `δ_C = π/7`, `HLocal = (I − √(1+2δ²)·σz)/2` с доказанным локальным зазором, `berryGap` и комбинаторная константа `cmin`.',
    },
    'SeptinalYM/MatrixAux.lean': {
        'en': 'The matrix layer: state space `ℋ_Sept = ⊗_{s∈D\\G} ℂ²` with bit-string basis `Cfg = Fin 22 → Fin 2`, the vacuum, the diagonal `H₀`, hermiticity facts, the bond term `bondTerm s` and the connection `V = J·Σ_s bondTerm s` with the quadratic-form bound `qform_V_le`.',
        'ru': 'Матричный слой: пространство состояний `ℋ_Sept = ⊗_{s∈D\\G} ℂ²` с битовым базисом `Cfg = Fin 22 → Fin 2`, вакуум, диагональная часть `H₀`, факты эрмитовости, рёберный оператор `bondTerm s` и связь `V = J·Σ_s bondTerm s` с оценкой квадратичной формы `qform_V_le`.',
    },
    'SeptinalYM/JW.lean': {
        'en': 'The Jordan–Wigner layer (795 lines, 48 theorems): configuration weight and parity, the even/odd sector decomposition, majorana operators `majVia`/`majX`/`majY` with the anticommutation (CAR) algebra, `V_parity_commute`, and the edge-wrap `(21, 0)` case with the parity operator — the foundation of the `‖V‖ ≤ 28.1067·|J|` bound.',
        'ru': 'Слой Джордана–Вигнера (795 строк, 48 теорем): вес и чётность конфигурации, секторное разложение на чётные/нечётные, мажораны `majVia`/`majX`/`majY` с антикоммутационной алгеброй (CAR), `V_parity_commute` и ребро-обмотка `(21, 0)` с оператором чётности — фундамент оценки `‖V‖ ≤ 28.1067·|J|`.',
    },
    'SeptinalYM/Fourier.lean': {
        'en': 'The one-particle Fourier layer (JW items 2–3): the root of unity `ω = e^{2πi/22}`, Fourier modes `fourierVec k`, the hop operator `hop` and its diagonalisation `hop_fourier_eigen` — the single-particle spectrum of the 22-cycle.',
        'ru': 'Одночастичный слой Фурье (пункты 2–3 JW-программы): корень единицы `ω = e^{2πi/22}`, моды Фурье `fourierVec k`, оператор перескока `hop` и его диагонализация `hop_fourier_eigen` — одночастичный спектр 22-цикла.',
    },
    'SeptinalYM/Slater.lean': {
        'en': 'The multi-bit layer (JW item 3): the one-particle energies `ε_k` with `ε_{k+11} = ε_k` symmetry, positive/negative spectral parts, the maximum over occupied modes attained at `S = {k : ε_k > 0}`, the exact constant `cSept = 2·Σ_k|cos(2πk/22)| = 28.1067…`, and the Slater determinant skeleton `ψ_S`.',
        'ru': 'Многобитовый слой (пункт 3 JW-программы): одночастичные энергии `ε_k` с симметрией `ε_{k+11} = ε_k`, положительная и отрицательная части спектра, максимум по занятым модам на `S = {k : ε_k > 0}`, точная константа `cSept = 2·Σ_k|cos(2πk/22)| = 28.1067…` и каркас слейтеровских определителей `ψ_S`.',
    },
    'SeptinalYM/SlaterDiag.lean': {
        'en': 'Fragment 3, part 1 — cofactor mechanics for `A·Ψ_S` (1591 lines, 54 theorems): the Slater matrix `slaterMat`, scaled-column determinants, wrong-cofactor zeros, module shifts, sorted-carrier reindexing, the cyclic wraps `21 ↦ 0`/`0 ↦ 21` with permutation signs, and the twisted modes `ψ̃_k(u) = ζ^u·ψ_k(u)` that diagonalise the chain in ALL sectors.',
        'ru': 'Фрагмент 3, часть 1 — кофакторная механика для `A·Ψ_S` (1591 строка, 54 теоремы): слейтеровская матрица `slaterMat`, определители с масштабированными столбцами, нулевые «чужие» кофакторы, сдвиги мод, перкладка сортированных носителей, циклические прыжки `21 ↦ 0`/`0 ↦ 21` со знаками перестановок и твистованные моды `ψ̃_k(u) = ζ^u·ψ_k(u)`, делающие цепочку диагональной во ВСЕХ секторах.',
    },
    'SeptinalYM/Stage4c.lean': {
        'en': 'Stage 4c — cofactor bricks for the final assembly: `ω`-arithmetic for the wrap bridges (`ω^k·ω^{21k} = 1`), zero determinants for scaled columns of occupied pairs (two equal columns), and proportionality of occupied adjacent columns — including pairs through the cycle boundary (sites 21 and 0).',
        'ru': 'Этап 4c — кофакторные кирпичи финальной сборки: арифметика `ω` для мостов через границу (`ω^k·ω^{21k} = 1`), нулевые определители масштабированных столбцов занятых пар (два равных столбца) и пропорциональность занятых соседних столбцов — включая пары через границу цикла (сайты 21 и 0).',
    },
    'SeptinalYM/Stage4d.lean': {
        'en': 'Stage 4d — the assembly itself and the largest file of the package (2710 lines, 92 theorems): `mulVec` splitting of the operator sum, edge-by-edge case analysis (blocked / succ-active / pred-active), contributions `2·D⁺(j_s)` and `2·D⁻(j_{s+1})` via `cofG_det_updateCol`, zeroing of «missing» occupied-pair terms, the cofactor fold `Σ_j Σ_i d_i·M_{ij}·C_{ij} = (Σ_i d_i)·det M`, the headline `slater_diag_odd`, its twisted twin `slater_diag_even_twist`, and the Cauchy–Binet orthogonality block **O2–O5** ending in `slater_orth`.',
        'ru': 'Этап 4d — сама сборка и крупнейший файл пакета (2710 строк, 92 теоремы): `mulVec`-расщепление суммы операторов, разбор рёбер по типу (заблокированное / succ-активное / pred-активное), вклады `2·D⁺(j_s)` и `2·D⁻(j_{s+1})` через `cofG_det_updateCol`, обнуление «недостающих» членов занятых пар, свёртка кофакторов `Σ_j Σ_i d_i·M_{ij}·C_{ij} = (Σ_i d_i)·det M`, флагман `slater_diag_odd`, его твистованный двойник `slater_diag_even_twist` и блок ортогональности по Коши–Бине **O2–O5**, завершающийся `slater_orth`.',
    },
    'SeptinalYM/Sector.lean': {
        'en': 'The bridge to sector bounds (JW item 4): exact edge decomposition `qform_V_eq_sum`, the chain preserves particle number (weight), `septinal_gap_of_chain` and the sector-wise bounds `sector_pos_bound_of_chain`/`sector_neg_bound_of_chain`.',
        'ru': 'Мост к секторным оценкам (пункт 4 JW-программы): точное разложение по рёбрам `qform_V_eq_sum`, цепочка сохраняет число частиц (вес), `septinal_gap_of_chain` и секторные оценки `sector_pos_bound_of_chain`/`sector_neg_bound_of_chain`.',
    },
    'SeptinalYM/Ortho.lean': {
        'en': 'First sheet of the Cauchy–Binet fragment: orthogonality of the Fourier modes `Σ_u conj(ψ_k u)·ψ_l u = δ_{kl}` (`psi_inner`), with the conjugation lemmas for `ω` powers.',
        'ru': 'Первый лист фрагмента «Коши–Бине»: ортогональность мод Фурье `Σ_u conj(ψ_k u)·ψ_l u = δ_{kl}` (`psi_inner`) со вспомогательными леммами о сопряжении степеней `ω`.',
    },
    'SeptinalYM/Numeric.lean': {
        'en': 'The numeric sheet closing the JW chain: the exact constant `cSept = 2·Σ_k|cos(2πk/22)| = 28.1066967…` bounded by a chain of Taylor majorants on `[0, 2]` (MVT template, pairwise symmetry of the 22-mode sum, five decimal majorants) — `cSept ≤ 28.1067`.',
        'ru': 'Числовой лист, замыкающий JW-цепочку: точная константа `cSept = 2·Σ_k|cos(2πk/22)| = 28.1066967…` оценивается цепочкой тейлоровских мажорант на `[0, 2]` (шаблон MVT, попарная симметрия суммы по 22 модам, пять десятичных мажорант) — `cSept ≤ 28.1067`.',
    },
    'SeptinalYM/Gap.lean': {
        'en': 'The septinal gap — lemma 3 of the plan: the vacuum energy `Evac`, bit-combinatoric bounds on `H₀` (`qform_H0_ge` for `v ⊥ vac`), the generalized lemma with the constant `C` and `|J| < Δ₀/C`, and the three forms of the gap: `septinal_gap`, `septinal_gap_jw`, `septinal_gap_jw_via_sectors`.',
        'ru': 'Септинальный зазор — лемма 3 плана: энергия вакуума `Evac`, битово-комбинаторная оценка `H₀` (`qform_H0_ge` для `v ⊥ vac`), обобщённая лемма с константой `C` и `|J| < Δ₀/C` и три формы зазора: `septinal_gap`, `septinal_gap_jw`, `septinal_gap_jw_via_sectors`.',
    },
    'SeptinalYM/YMTarget.lean': {
        'en': 'The embedding into Yang–Mills state space: the `YM4` carrier, the canonical inclusion `Φ : ℋ_Sept → Y.Space` proved linear and isometric, `septinal_embeds_in_ym`, and `septinal_gap_transports` — the gap transfers along the embedding. The verifiable half of the physical hypothesis.',
        'ru': 'Вложение в пространство состояний Янга–Миллса: носитель `YM4`, каноническое включение `Φ : ℋ_Sept → Y.Space` с доказанной линейностью и изометричностью, `septinal_embeds_in_ym` и `septinal_gap_transports` — зазор переносится вдоль вложения. Проверяемая половина физической гипотезы.',
    },
    'SeptinalYM.lean': {
        'en': 'Root of Library II: imports `Basic`, `MatrixAux`, `Gap`, `JW`, `YMTarget` — the mass-gap core. The heavier diagonalisation chain (Slater → SlaterDiag → Stage4c → Stage4d) is reached via the explicit target `lake build SeptinalYM.Stage4d`.',
        'ru': 'Корень библиотеки II: импортирует `Basic`, `MatrixAux`, `Gap`, `JW`, `YMTarget` — ядро массового зазора. Более тяжёлая цепочка диагонализации (Slater → SlaterDiag → Stage4c → Stage4d) собирается явной целью `lake build SeptinalYM.Stage4d`.',
    },
    'SeptinalYM_root.lean': {
        'en': 'Alternative (wider) root: also imports `Fourier`, `Slater`, `SlaterDiag`, `Sector`, `Ortho` — one command to type-check the whole core plus the diagonalisation modules.',
        'ru': 'Альтернативный (широкий) корень: дополнительно импортирует `Fourier`, `Slater`, `SlaterDiag`, `Sector`, `Ortho` — одна команда для проверки всего ядра вместе с модулями диагонализации.',
    },
    # ════════════════════════ Library III · Satellite ════════════════════════
    'Satellite.lean': {
        'en': 'Root of Library III: imports the six satellite modules `B1 → B2 → B2b → C2 → C3 → C4`.',
        'ru': 'Корень библиотеки III: импортирует шесть модулей спутника `B1 → B2 → B2b → C2 → C3 → C4`.',
    },
    'Satellite/B1_BerryShift.lean': {
        'en': 'B1 — the Berry quantum in the canonical two-level normal form: lower level `λ₋(δ) = (1 − √(1+2δ²))/2 = −δ²/2 + R(δ)` with the explicit remainder `0 < R(δ) ≤ δ⁴/4` — closed forms, root identity, both remainder bounds. Twin: `scripts/b1_berry_model.py`.',
        'ru': 'B1 — бэрри-квант в канонической двухуровневой нормальной форме: нижний уровень `λ₋(δ) = (1 − √(1+2δ²))/2 = −δ²/2 + R(δ)` с явным остатком `0 < R(δ) ≤ δ⁴/4` — замкнутые формы, тождество корня, обе оценки остатка. Двойник: `scripts/b1_berry_model.py`.',
    },
    'Satellite/B2_Dial22.lean': {
        'en': 'B2 — the dial-22 postulate and the braking rule: P1 (a full turn carries 24 slots) and P2 (an unremovable structural gap of width 2) give the effective capacity `k = 22` and the structural pair `β(d) = d²/2`, `α(d) = d⁵/22` on the three septinial phases `π/2, π/3, π/7`. Twin: `scripts/check_dial_22.py`.',
        'ru': 'B2 — постулат циферблата-22 и правило торможения: P1 (полный оборот несёт 24 позиции) и P2 (неустранимый структурный зазор ширины 2) дают эффективную ёмкость `k = 22` и структурную пару `β(d) = d²/2`, `α(d) = d⁵/22` на трёх септинальных фазах `π/2, π/3, π/7`. Двойник: `scripts/check_dial_22.py`.',
    },
    'Satellite/B2b_Chirality.lean': {
        'en': 'B2b — the dial\'s chirality (P3): the oriented cycle, the split `22 = 11 + 11` with one blocked slot per half-turn arc `{0, 12}`, and the reflection `x ↦ 24 − x` — chirality is the choice of orientation, not of counting.',
        'ru': 'B2b — хиральность циферблата (P3): ориентированный цикл, расщепление `22 = 11 + 11` с одной заблокированной позицией на полудугу `{0, 12}` и отражение `x ↦ 24 − x` — хиральность есть выбор ориентации, а не способа счёта.',
    },
    'Satellite/C2_Corrections.lean': {
        'en': 'C2 — the three corrections of the septinial family: the structural divisor `k = 22 = b₂(K3)`, the integer skeletons of the quanta, the Choptuik constant `b_Ch = 1 − cos(2π/7)` with honest bracketing, and the three-term record `γ₃ = b_Ch − π/1200`.',
        'ru': 'C2 — три поправки септинального семейства: структурный делитель `k = 22 = b₂(K3)`, целочисленные каркасы квантов, константа Чоптуика `b_Ch = 1 − cos(2π/7)` с честным брэкетингом и трёхчленная запись `γ₃ = b_Ch − π/1200`.',
    },
    'Satellite/C3_Cascade.lean': {
        'en': 'C3 — the symmetry-breaking cascade (P4): among the 24 rotations exactly the two `{0, 12}` preserve the antipodal gap, among the 24 reflections exactly the same two; the four survivors close into the Klein four-group — the cascade `48 → 4 → 2`. Brute-force twin: `scripts/check_dial_22.py` (S6).',
        'ru': 'C3 — каскад нарушения симметрии (P4): из 24 поворотов зазор сохраняют ровно два `{0, 12}`, из 24 отражений — ровно те же два; четыре выживших замыкаются в четверичную группу Клейна — каскад `48 → 4 → 2`. Грубый двойник: `scripts/check_dial_22.py` (S6).',
    },
    'Satellite/C4_Unlock.lean': {
        'en': 'C4 — UNLOCK: the model\'s predictions as exact parameter-free theorems — `γ₃ = 1 − cos(2π/7) − π/1200` with proven analytic bounds, `k = 22` as a counting theorem of the antipodal cut, and the sector-C quanta `β_C = π²/98`, `α_C = π⁵/369754`. No free parameters anywhere.',
        'ru': 'C4 — UNLOCK: предсказания модели как точные безпараметрические теоремы — `γ₃ = 1 − cos(2π/7) − π/1200` с доказанными аналитическими границами, `k = 22` как счётная теорема антиподального среза и кванты сектора C `β_C = π²/98`, `α_C = π⁵/369754`. Ни одного свободного параметра.',
    },
    'Satellite/C5_Klein.lean': {
        'en': 'C5 — KLEIN: the integer skeleton of the exhaustive PSL(2,7)/Klein-quartic enumeration (computed by `scripts/klein_psl27.py`, full subgroup lattice + the {7,3} map, results in `../data/klein_psl27_results.json`), mirrored here as theorems. Present in the tree but not under the `Satellite.lean` root imports.',
        'ru': 'C5 — KLEIN: целочисленный каркас исчерпывающего перебора PSL(2,7)/квартики Клейна (считается `scripts/klein_psl27.py`, полная решётка подгрупп + карта {7,3}, результаты в `../data/klein_psl27_results.json`), продублированный здесь теоремами. Файл в дереве есть, но в импорты корня `Satellite.lean` не включён.',
    },
    'Satellite/AxiomAudit.lean': {
        'en': 'The satellite\'s axiom audit: mechanical proof that every headline theorem depends only on the three standard axioms. Run: `lake env lean Satellite/AxiomAudit.lean`.',
        'ru': 'Аксиомный аудит спутника: механическое доказательство того, что каждая флагманская теорема зависит только от трёх стандартных аксиом. Запуск: `lake env lean Satellite/AxiomAudit.lean`.',
    },
    # ════════════════════════ scripts/ ════════════════════════
    'scripts/verify_septinal.py': {
        'en': 'The numerical verification twin (numpy): checks `Δ_Berry(π/7) = √(1+2(π/7)²) = 1.184415888` (not the plan\'s 1.203), the Rayleigh threshold `‖V‖ < Δ`, the JW formula by dense diagonalisation at N = 4…10, the exact `‖V‖ = 0.592209·22|J|`-scale constant, and the vacuum-referenced gap statement.',
        'ru': 'Числовой двойник верификации (numpy): проверяет `Δ_Berry(π/7) = √(1+2(π/7)²) = 1.184415888` (а не 1.203 из плана), порог Рэлея `‖V‖ < Δ`, JW-формулу прямой диагонализацией при N = 4…10, точную константу `‖V‖ = 0.592209·22|J|`-масштаба и формулировку зазора от уровня вакуума.',
    },
    'scripts/readme_stats.py': {
        'en': 'Counts everything in this README from the sources: lines, bytes, declarations with namespaces, project imports, `/-!` sections, sorry markers, build-target membership (`--json docs/source_stats.json`).',
        'ru': 'Считает для этого README всё из исходников: строки, байты, объявления с пространствами имён, импорты проекта, секции `/-!`, маркеры sorry, принадлежность целям сборки (`--json docs/source_stats.json`).',
    },
    'scripts/readme_gen.py': {
        'en': 'Regenerates this README (EN + RU) and the subfolder READMEs from `source_stats.json` + the curated descriptions — numbers never typed by hand.',
        'ru': 'Перегенерирует этот README (EN + RU) и README подпапок из `source_stats.json` и курированных описаний — числа руками не набираются.',
    },
    'scripts/readme_charts.py': {
        'en': 'Draws the four charts of this README from `source_stats.json` (module sizes, declarations per library, the proof chain, the sorry map).',
        'ru': 'Рисует четыре графика этого README из `source_stats.json` (размеры модулей, объявления по библиотекам, цепочка доказательства, карта sorry).',
    },
    'scripts/readme_gif.py': {
        'en': 'Renders the terminal-style `lake build` GIF shown above.',
        'ru': 'Рисует показанную выше терминальную GIF-анимацию `lake build`.',
    },
}
