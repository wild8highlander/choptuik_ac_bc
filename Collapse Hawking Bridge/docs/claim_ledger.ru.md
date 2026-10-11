# Реестр соответствия — каждое заявление пакета сопоставлено с артефактом

**Назначение.** Самая дешёвая и самая защитимая проверка внешнего аудита —
таблица соответствия: *имеет ли каждое заявление пакета о самом себе
машиночитаемый адрес внутри пакета?* Этот файл — именно эта проверка,
закоммиченная. Правило пакета: **машиночитаемо или этого не было** —
заявление без адреса артефакта ниже — это баг; сообщите о нём.

**Сопутствующие документы:** [PREREGISTRATION.ru.md](../PREREGISTRATION.ru.md)
(замороженные критерии опровержения), [RESULTS.md](../results/RESULTS.md)
(реестр-проза), [validation.md](validation.md) (числа по каждой проверке).

## 1. Бейджи (шапка README.md / README.ru.md)

| заявление | артефакт, делающий его истинным | пин-тест |
|---|---|---|
| версия 2.2.0 | `VERSION`, `chbridge/constants.py::__version__`, `pyproject.toml` | `tests/test_constants.py::test_package_version_pin` |
| pytest 69 passed | `tests/` (сам набор); число зафиксировано в `tests/README.md` | прогон набора |
| validate 7/7 PASS | вывод `chbridge/validate.py::run_all` | `tests/test_ladder.py::test_validate_all_pass` |
| аудит IVP-15 remediated + aligned | `independent_verification/results/*.json`, `independent_verification/RESULTS.md` | `tests/test_preregistration.py` (дисциплина токенов) |
| теорема T10 (закон дрейфа) | `campaigns/reference/c6_drift_verdict.json`, `docs/scaling_law.md` | `tests/test_campaigns.py::test_c6_*` (3 пина) |
| figures_hires 68 @600dpi | `figures_hires/` — 68 PNG (17 архитектур × RU/EN × светлая/тёмная) | `scripts/hires_figures.py --all` |
| multilang 7 | Python + `multilang/{javascript,c,cpp,julia,rust,go}` | матрица `multilang/README.md` |

## 2. Заголовочные строки результатов (README §Headline ↔ RESULTS.md)

| # | заявление | адрес вердикта | пин |
|---|---|---|---|
| 1–2 | A*_N800 = 0.0805332422; лестница пяти сеток | `campaigns/reference/a_star_ladder.{json,csv}` | пины порядка `test_ladder.py` |
| 3–4 | дрейф N800→N1600 = 2.79e-3; p_eff 1.140/1.459/1.596 | `campaigns/reference/c6_drift_verdict.json` | `test_c6_ladder_facts` |
| 5 | порядки сходимости Робертса–Оширо 2.03/2.09 | `c1_verdict.json` | `test_constants.py::test_campaign_astar_ladder` + движковая регрессия |
| 6 | члены ансамбля f~ 0.2877/0.2684/1.0 | `data/bridge/collapse_verdict_summary.json` | `test_bridge.py` |
| 7–9 | CMB-контакт 4.5016e22 кг; доля Пейджа; Хаар 0.0042 бит | `chbridge/hawking.py`, `data/bridge/page_haar_check.csv` | `test_hawking.py`, `test_page.py` |
| 10–11 | b_Ch точно; зазор \|γ_Ch − b_Ch\|/b_Ch = 0.67% (γ_Ch — ЛИТЕРАТУРНАЯ сторона; b_Ch — собственная константа проекта; прежний ярлык «b_Ch_lit» снят на v2.2.0) | `chbridge/validate.py::check_b_Ch` | `test_constants.py::test_b_ch_*` |
| 12 | якорное произведение Δ·γ 1.28656 vs 1.27 — **ANCHOR_ARITHMETIC** (не измерение; движковый уровень INCONCLUSIVE) | `c3_verdict.json::products` | `test_campaigns.py::test_c3_verdict_semantics`, `test_preregistration.py` |
| 13–16 | ветви C2 (компактность, замедление, скорость эха, ε½) | `c2_verdict.json` | `test_campaigns.py::test_c2_*` |
| 17–18 | закон пола (13±1)/N; γ, Δ честно неизмеримы до N=3200 | `c3b_verdict.json` | `test_c3b_floor_ladder_sinks`, `test_c3b_gamma_fit_floor_biased`, `test_c3b_delta_honest_negative` |
| 19–20 | канал T10 κ*=2728.60, s=413.8, суб-доминантен; НИКАКОГО A*_inf | `c6_drift_verdict.json` | `test_c6_honest_negatives_and_channel` |
| 21 | 50-значный слой 7/7 | `chbridge.validate` | `test_validate_all_pass` |

## 3. Структурные заявления

| заявление | адрес | проверяется |
|---|---|---|
| bridge_master.csv = 15 строк × 23 столбца | `data/bridge/bridge_master.csv` | геометрические пины `test_bridge.py` |
| 13 байт-детерминистских таблиц | `data/bridge/` (13 файлов) | `test_rebuild_is_deterministic` |
| 28 рисунков @300dpi; 68 @600dpi; 16 анимационных файлов (4 × RU/EN × MP4/GIF); книга 14 листов | `figures/`, `figures_hires/`, `animations/`, `tables/bridge_workbook.xlsx` | скрипты пересборки |
| монография: 2 тома × RU/EN × DOCX+PDF, T1–T10 | `monograph/` | runbook монографии |

## 4. Заявления, которых этот пакет НЕ делает

Аудит сверял README родительского репозитория с содержимым этого пакета.
Для протокола: пакет Collapse–Hawking Bridge **не** заявляет ничего из
следующего (такое живёт, если вообще живёт, в других проектах
родительского репозитория и ничем здесь не подкреплено):

- «решение проблемы Чоптика» — пакет измеряет фиксированно-сеточные
  наблюдаемые и честно не достигает континуального порога;
- «решение сильной CP-проблемы»;
- QNM-предсказания для GW150914 / GW170104 / GW170814 / GW190521 — пакет
  несёт формулу рингдауна Шварцшильда l=2 и помеченную как гипотезу
  септиниальную *поправку* (относительный сдвиг 8.44e-5, кампания C4 —
  будущая работа), а не предсказания для событий;
- «машинная верификация на 1e-41» — машинный слой здесь — это
  байт-детерминизм, 50-значные mpmath-проверки и сходимость движка
  второго порядка; ничто из этого не есть утверждение уровня 1e-41;
- счётчик «58/58 тестов» — счётчик, закреплённый собственным README
  пакета, — это общее число pytest в `tests/` (см. бейдж; проверяется
  прогоном набора).

Русское зеркало английского оригинала: [claim_ledger.md](claim_ledger.md).
