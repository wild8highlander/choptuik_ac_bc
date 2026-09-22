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

## Полный список файлов в архиве

| Файл | Статус |
|---|---|
| `code/python/run.py` | исправлен (EOF, авто-режим, --section) |
| `python/run.py` | исправлен (TTY-детект) |
| `python/src/ui/interactive_menu.py` | исправлен (EOF, black-чистота) |
| `audit_transfer/python/run_all.py` | исправлен (фигуры не роняют прогон) |
| `audit_transfer/python/audit_transfer/figures.py` | исправлен (playwright опционален) |
| `.github/workflows/ci.yml` | исправлен (consistency-API, без paths-фильтра) |
| `.github/workflows/lint.yml` | исправлен (mypy advisory, workflow_dispatch) |
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
```
