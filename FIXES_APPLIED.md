# FIXES_APPLIED — исправления в этом архиве (fix pack, 2026-09-22)

Этот ZIP — патч поверх клона репозитория `wild8highlander/choptuik_ac_bc`.
Распаковка с заменой файлов (`unzip -o ... -d .`) не трогает остальные файлы.
Список того, что именно чинится, — ниже.

## TL;DR (EN)

CLI entry points crashed with `EOFError` on non-TTY stdin and ignored the
`--config` / `--section` flags documented in the README; `audit_transfer`
hard-required `playwright`; the CI badge was red because the consistency
job referenced an outdated API (`delta_bC`/`aut_order`); the Lint badge was
red because `mypy` blocked on numpy's own stubs; the CI `paths` filter kept
badges stale. This pack fixes all of the above and adds `termux/` helper
scripts (one-tap push via PAT, optional `--force` only by explicit flag).

---

## 1. CLI падал при неинтерактивном запуске (главный баг «не запускается CL»)

**Симптом:** `python3 run.py` (и в `python/`, и в `code/python/`) падал с
`EOFError: EOF when reading a line`, если stdin не терминал: запуск из
Termux-виджета, из скрипта, через pipe (`echo | python run.py`), в CI.

**Файлы:**
- `code/python/run.py` — добавлен `safe_input()` (перехват `EOFError` и
  `KeyboardInterrupt`); меню теперь мягко завершается с кодом 0;
- `code/python/run.py` — если stdin не TTY, автоматически включается
  неинтерактивный режим (без вопросов, сразу верификация);
- `python/src/ui/interactive_menu.py` — та же защита `_safe_input()` в
  главном меню (10 опций);
- `python/run.py` — TTY-детект: при piped/закрытом stdin переходит в
  `--mode verify --non-interactive` вместо падения.

## 2. Команды из README Quick Start не работали

**Симптом:** `python3 run.py --config ../../qcd_bridge/configs/verify_all.json`
и `python3 run.py --section 3,6,8` (документированы в README) игнорировали
аргументы: режим оставался `interactive`, падали в меню, а без терминала —
крашились. (`--section` работал только как префикс argparse у `--sections`
и только вместе с явным `--mode verify_section`.)

**Файл:** `code/python/run.py`
- `--config` теперь сам переключает режим в `custom`;
- `--sections`/`--section` (добавлен алиас) — в `verify_section`;
- значения из JSON-конфига можно переопределить флагами CLI.

**Проверено:** обе команды отрабатывают с exit 0, отчёты создаются.

## 3. audit_transfer падал без playwright

**Симптом:** `run_all.py` выполнял все 3 задачи верификации и падал на
последнем шаге фигур: `ModuleNotFoundError: No module named 'playwright'`
(модуль тяжёлый, ставится отдельно и нигде не был объявлен).

**Файлы:** `audit_transfer/python/audit_transfer/figures.py`,
`audit_transfer/python/run_all.py`
- playwright теперь опционален: без него диаграмма `fig_transfer_map.png`
  пропускается с понятной подсказкой, HTML-заготовка сохраняется;
- блок фигур обёрнут в try/except — результаты задач 1–3 (`results/*.json`)
  больше не могут быть потеряны из-за графики;
- полный прогон завершается exit 0 (проверено, ~20 с).

## 4. Красный бейдж CI: consistency-джоб звал несуществующий API

**Симптом:** бейдж CI на GitHub показывал «failing». Джоб
«Cross-implementation consistency» обращался к атрибутам
`f.delta_bC`, `f.delta_Ch`, `f.b_Ch`, `c.aut_order`, которых у классов нет
(реальный API: `ChoptyukFormula().compute()` → поля `delta_bc`,
`delta_ch_full`, `b_ch`; `KleinCurve.psl_order`). Коммит ed3cbca выровнял
тесты с API, но пропустил этот джоб.

**Файл:** `.github/workflows/ci.yml` — джоб переписан под реальный API,
проверено локально: PASS.

## 5. Красный/устаревший бейдж Lint + несвежий CI

- `.github/workflows/lint.yml`: mypy сейчас ломается на собственных
  стабах numpy (PEP 695 `type`-стейтменты) — это не код проекта; шаг mypy
  переведён в advisory (`continue-on-error: true`), как уже было в ci.yml.
  Блокирующие проверки ruff и black оставлены строгими (код их проходит:
  26 файлов black — без изменений, ruff — чисто);
- `.github/workflows/lint.yml`: добавлен `workflow_dispatch` (кнопка
  ручного запуска в Actions — удобно, чтобы обновить бейдж);
- `.github/workflows/ci.yml`: убран `paths`-фильтр — теперь CI запускается
  на КАЖДЫЙ пуш в main и бейдж не «застаивается» со старым статусом.

## 6. Новое: termux/ — автоматическая публикация с телефона

- `termux/choptuik_push.sh` — скрипт автопубликации: находит клон,
  настраивает PAT-токен (спрашивает один раз, проверяет на сервере,
  хранит с правами 600), коммитит, пушит в `origin main` от имени
  `wild8highlander`. Форс — ТОЛЬКО по явному флагу `--force`;
  при отклонении push печатает оба варианта действий;
- `termux/install_shortcut.sh` — ставит ярлык пуша в «доверенную папку»
  Termux `~/.shortcuts` (Termux:Widget запускает такие скрипты одним
  тапом с рабочего стола, без подтверждений).

---

## РАУНД 2 (2026-09-22, после первого пуша fix pack'а): CI упал на 7 джоб

Первый пуш зафиксировал наши Python-фиксы, но у репозитория оставались
непочиненные CI-джобы, которые не трогал раунд 1 (Lint уже зелёный).
Итог прогона CI #79: Python 3.10/3.11/3.12 на windows-latest × 3,
Julia 1.10/1.11 × 2, Java 17/21 × 2 — все с «exit code 1». Всё починено
и проверено локально (Linux, Julia 1.10.12, Maven 3.9.9 + Temurin 21):

## 7. Julia CI падал на Pkg.instantiate: поддельные UUID пакетов

**Симптом:** обе джобы Julia 1.10/1.11 падали на шаге «Install Julia
dependencies» (3 попытки → exit 1). Воспроизведено локально:
`ERROR: expected package \`JSON [682c06d0]\` to be registered`.

**Причина:** в `julia/Project.toml` стояли выдуманные UUID:
- `Printf` → `de085821-7539-58de-a6c0-638f2599436f`
  (настоящий: `de0858da-6303-5e67-8744-51eddeeeb8d7`);
- `JSON` → `682c06d0-f43c-4c30-b111-5a9f5a44b905`
  (настоящий: `682c06a0-de6a-54ab-a142-c8b1cf79cde6`);
- `Plots` → `91a5bcdd-55d7-5caf-9e0b-520d859dae80`
  (настоящий: `91a5bcdd-55d7-5caf-9e0b-520d859cae80`).

Также в [deps] отсутствовал stdlib `Dates`, который код использует
(`julia/src/ChoptyukSpinor.jl:74`).

**Файлы:** `julia/Project.toml` — UUID исправлены на настоящие,
добавлен `Dates`.

## 8. Julia пакет не прекомпилировался: 3 ошибки в коде

По порядку появления (все воспроизведены и устранены локально):
1. `ERROR: Method overwriting is not permitted during Module
   precompilation` — `corrected_qnm_frequency` была определена ДВАЖДЫ
   (`choptyuk_formula.jl:246` и `qnm.jl:220`). Формулы идентичны —
   дубль удалён, оставлена версия из `qnm.jl` (у неё есть default
   `delta_C = π/7`);
2. `ParseError: visualization.jl:196:67` — лишняя закрывающая скобка в
   `annotate!(p3, [(masses[i], spins[i] + 0.02, text(name, 8)))])`;
3. `UndefVarError: SpinorPhases not defined` — блоки `export` стояли
   ПОСЛЕ include подмодулей; подмодуль Visualization делает
   `using ..ChoptyukSpinor` (подхватываются только уже экспортированные
   имена) → `export` перенесён ВЫШЕ include.

**Файлы:** `julia/src/choptyuk_formula.jl`, `julia/src/visualization.jl`,
`julia/src/ChoptyukSpinor.jl`.

**Проверено:** `julia --project=. -e 'using Pkg; Pkg.test()'` —
все 16 тестсетов PASS («Testing ChoptyukSpinor tests passed»),
пакет грузится, precompile чистый.

## 9. Julia-тесты звали несуществующие функции (та же болезнь, что у
## consistency-джобы в раунде 1)

**Симптом:** после починки загрузки пакета тесты падали бы: они вызывали
`genus(kc)`, `automorphism_order(kc)`, `scalar_curvature(kc)`,
`delta_a(sp)`, `trivial_eigenvalue(d)`, `delta_bc(cf)`,
`delta_ch_base(cf)`, `delta_ch_full(cf)`, `b_choptyuk(cf)` — таких
функций в API НЕТ.

**Файл:** `julia/test/runtests.jl` — первые 4 тестсета и «Deviations
Within Tolerance» переписаны под реальный API:
- `KleinCurve`: поля `kc.genus`, `kc.aut_order`, `kc.R` (+
  `is_hurwitz_curve(kc)`);
- `SpinorPhases`: поля `sp.delta_A/.delta_B/.delta_C`;
- `DiracOperator`: поле `d.lambda_D2_triv`;
- `ChoptyukFormula`: функции `bC_correction(cf)` → 3.438710,
  `aC_correction(cf)` → 3.437883, `choptyuk_constant(cf)` → 3.447040,
  поле `cf.b_Ch` → 0.376510 (все эталонные значения сошлись).

## 10. Java CI падал на несуществующей версии плагина

**Симптом:** обе джобы Java 17/21 падали на `mvn clean verify`.
Воспроизведено локально: `Could not find artifact
com.github.spotbugs:spotbugs-maven-plugin:jar:4.8.6 in central`.
У spotbugs-maven-plugin ЧЕТЫРЁХСЕГМЕНТНЫЕ версии: 4.8.6 НЕ существует
(есть 4.8.6.0…4.8.6.6) — проверено по API Maven Central.

**Файл:** `java-webapp/pom.xml` — версия плагина 4.8.6 → 4.8.6.6
(в `<build>` и в `<reporting>`).

**Проверено:** `mvn clean verify` → BUILD SUCCESS (Temurin 21,
Maven 3.9.9; в java-webapp нет junit-тестов — surefire «No tests to
run», чекстайл/spotbugs — report-only).

## 11. Python CI на Windows: pwsh ломал обратные слеши

**Симптом:** все 3 джобы Python на windows-latest падали с exit 1,
хотя ubuntu/macos — зелёные, а тесты платформо-независимы.

**Причина:** шаг «Run tests with coverage» использует переносы строк
`\` (bash-синтаксис), а Windows-раннеры по умолчанию исполняют `run:`
через pwsh, где `\` — НЕ символ продолжения: следующая строка
(`--cov=src \`) исполняется как отдельная «команда», pwsh завершается с
ошибкой. Дополнительно проверено симуляцией cp1251-кодировки по
умолчанию (типичная причина падений на Windows) — 78/78 тестов
проходят и с ней.

**Файл:** `.github/workflows/ci.yml` — для джобы python-ci добавлен
`defaults: run: shell: bash` (bash есть и на Windows-раннерах),
поведение на ubuntu/macos не меняется.

## 12. «Verify Audit & Transfer» падал на кросс-проверке артефактов

**Симптом:** джобы «Python · три задачи + фигуры» и «Julia ·
независимое подтверждение» — зелёные, а «Кросс-проверка Python ↔
Julia» падала с exit 1 за 4 секунды.

**Причина:** `actions/upload-artifact@v4` кладёт файлы внутрь
артефакта относительно ОБЩЕГО ПРЕДКА путей (`audit_transfer/`), то
есть файл оказывается в артефакте как `results/stability_lemma.json`,
а скрипт кросс-проверки искал его в корне артефакта
(`artifacts/python-verification-results/stability_lemma.json`) →
«артефакты не найдены» → exit 1.

**Файл:** `.github/workflows/verify-audit-transfer.yml` — поиск
переведён на рекурсивный glob
(`artifacts/…/**/stability_lemma.json`, `recursive=True`), устойчивый
к любому раскладу. Сами значения сходятся: пол 5/7 =
0.7142857142857143 (Python) vs 0.714285714286 (Julia), расхождение
1.4e-13 < 1e-9 — кросс-проверка пройдёт.

---

## Полный список файлов в архиве

| Файл | Статус |
|---|---|
| `code/python/run.py` | исправлен (EOF, авто-режим, --section) |
| `python/run.py` | исправлен (TTY-детект) |
| `python/src/ui/interactive_menu.py` | исправлен (EOF, black-чистота) |
| `audit_transfer/python/run_all.py` | исправлен (фигуры не роняют прогон) |
| `audit_transfer/python/audit_transfer/figures.py` | исправлен (playwright опционален) |
| `.github/workflows/ci.yml` | исправлен (consistency-API, без paths-фильтра, bash на Windows) |
| `.github/workflows/lint.yml` | исправлен (mypy advisory, workflow_dispatch) |
| `.github/workflows/verify-audit-transfer.yml` | исправлен (рекурсивный поиск артефактов в кросс-проверке) |
| `julia/Project.toml` | исправлен (настоящие UUID Printf/JSON/Plots, добавлен Dates) |
| `julia/src/ChoptyukSpinor.jl` | исправлен (export до include подмодулей) |
| `julia/src/choptyuk_formula.jl` | исправлен (убран дубль corrected_qnm_frequency) |
| `julia/src/visualization.jl` | исправлен (ParseError: лишняя скобка) |
| `julia/test/runtests.jl` | исправлен (тесты выровнены с реальным API) |
| `java-webapp/pom.xml` | исправлен (spotbugs-maven-plugin 4.8.6 → 4.8.6.6) |
| `termux/choptuik_push.sh` | новый |
| `termux/install_shortcut.sh` | новый |
| `FIXES_APPLIED.md` | новый (этот файл) |
| `ИНСТРУКЦИЯ_ДЛЯ_ЧАЙНИКОВ.md` / `.pdf` | новый (пошаговый гайд по публикации) |

## Как проверить исправления локально

```bash
# 1) CLI больше не падает без терминала (раньше — EOFError):
cd code/python && echo | python3 run.py --lang en            # exit 0
python3 run.py --section 3,6,8                               # из README

# 2) Команды из README:
python3 run.py --config ../../qcd_bridge/configs/verify_section_3_8.json

# 3) audit_transfer завершается без playwright:
python3 audit_transfer/python/run_all.py                     # exit 0

# 4) Тесты и линтеры (скоуп Lint-бейджа):
cd python && python -m pytest tests/ -q && ruff check src/ tests/ && black --check src/ tests/

# 5) Julia-тесты (раунд 2; Julia >= 1.9):
cd julia && julia --project=. -e 'using Pkg; Pkg.test()'

# 6) Java-сборка (раунд 2; нужен JDK 17+ и Maven):
cd java-webapp && mvn -B clean verify        # → BUILD SUCCESS
```
