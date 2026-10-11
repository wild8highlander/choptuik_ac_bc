# CHANGES — главный README v2 + GitHub-фичи (choptuik_ac_bc)

Дата: 2026-10-11
База: origin/main @ 6bc1f734 («QHB») — проверено `git ls-remote`, локальная копия = GitHub main.

## Что внутри пакета

| Файл | Куда положить в репозитории | Что это |
|---|---|---|
| `README.md` | `/README.md` (заменить) | **Новый главный README** (RU): 181 КБ, 2111 строк (старый: 82.5 КБ, 1404 строки) |
| `README.en.md` | `/README.en.md` (новый) | Компактная английская витрина с переключателем языков |
| `SUPPORT.md` | `/SUPPORT.md` (новый) | Где получить помощь (GitHub показывает баннер) |
| `GOVERNANCE.md` | `/GOVERNANCE.md` (новый) | Модель управления «один автор — один мейнтейнер» |
| `CODEOWNERS` | `/.github/CODEOWNERS` (новый) | Авто-назначение ревью: `* @wild8highlander` |
| `release.yml` | `/.github/release.yml` (новый) | Авто-категории release notes (breaking / theorems / campaigns / docs / infra) |
| `assets_logo/` | `/assets/logo/` (новая папка) | Корневое лого dark+light (PNG 600×1900 px @150 dpi + SVG) + генератор `make_root_logo.py` |

## Куда скопировать (из корня распакованной папки)

```bash
cp README.md README.en.md SUPPORT.md GOVERNANCE.md  <repo>/
cp CODEOWNERS release.yml                           <repo>/.github/
cp -r assets_logo                                   <repo>/assets/logo
```

`make_root_logo.py` можно положить рядом: `<repo>/assets/logo/make_root_logo.py`
(скрипт детерминированный, matplotlib-only, перегенерирует оба PNG и SVG).

## Что изменилось в README (кратко)

1. **Новые программы, которых не было в старом README**: Collapse Hawking Bridge (v2.1.0)
   и QHB (v2.3.0) описаны полностью — кампании C1–C12, IVP-аудиты, Lean/Mathlib,
   X1–X13, Iron-QA, книги Excel, межъязыковые близнецы; QCD Bridge-артефакты (55 фигур,
   19 4D-анимаций), dsi_lab (7 экспериментов), docs/ и code/.
2. **Раздел «★ Три поправки и их универсальность»**: сектора π/2, π/3, π/7, формулы
   β(d)=d²/2, α(d)=d⁵/22, таблица переносимости (QHB +11.28%, иерархия 1865:1, b_Ch,
   QNM-фактор, Strong CP, Δ·γ), аналитические выкладки шаг за шагом, анимации к трём
   режимам, mermaid-диаграмма «как связаны три моста».
3. **Лого**: `<picture>` с автоматическим dark/light (файлы в assets/logo/).
4. **Формат**: Mermaid mindmap (карта репо) + timeline (хронология) + 6 flowchart;
   KaTeX-формулы; alerts [!NOTE]/[!TIP]/[!IMPORTANT]/[!WARNING]; 24 <details>-сворачивания;
   HTML-таблицы с анимациями; полное оглавление с якорями (все проверены — 248 ссылок OK, 0 битых).
5. **Новые разделы**: хронология 2024→2026, галерея фигур (8 сюжетов × все программы),
   архитектура 3 конвейеров, форматы отчётов, полное дерево проекта, межъязыковая
   матрица + 12 контрольных величин, FAQ (10 вопросов), глоссарий (21 термин),
   реестр всех 46 анимаций, карта 17 hi-res фигур CHB, 13 таблиц данных CHB,
   31 JSON QHB, листы книг, CHANGELOG CHB, карта машин ED, контракт новой кампании,
   задачи контрибьюторам, карта функций GitHub.
6. **Исправления старого README**: битые пути `einstein_direct/`, `interactive-viz/`,
   `qcd_bridge/` → реальные имена папок с пробелами (URL-encoded); бейджи тестов
   теперь по пакетам (ED 58+10 · CHB 63 · QHB 154); «58/58» больше не приписывается
   всему репозиторию; QNM-таблица помечена как гипотеза-модель; Strong CP — как
   гипотетическая рамка (⚠️-блок).
7. **GitHub-фичи добавлены (отсутствовали)**: CODEOWNERS, release.yml, SUPPORT.md,
   GOVERNANCE.md, README.en.md, корневое лого. Остальные (FUNDING, CITATION.cff,
   SECURITY, шаблоны, 11 workflows, dependabot, labeler, discussions) — уже были в репо;
   в README добавлена их карта («Функции GitHub этого репозитория»).

## Числа и честность

- Все числа взяты из committed-источников репо: `results/RESULTS.md` и
  `campaigns/reference/*.json` (CHB), `QHB/data/*.json` + `claims.json` (QHB),
  `Einstein Direct/results/*.json` (ED), `multilang/*/reference_output.txt` (близнецы).
- Версия CHB указана как в текущем main (2.1.0). Если применяется ранее подготовленный
  пакет v2.2.0 — обновите цифру «(v2.1.0)» в заголовке Программы IV и в таблице
  навигации по пакетам на «2.2.0» (2 упоминания в README.md, 1 в README.en.md).
- Сводные счётчики (1793 файла, 369 МБ, 274 py, 232 json, 513 png, 71 docx, 110 pdf,
  23 gif+23 mp4) посчитаны `git ls-files` по текущему main.

## После копирования (рекомендуемый порядок)

```bash
cd <repo>
git add README.md README.en.md SUPPORT.md GOVERNANCE.md .github/CODEOWNERS .github/release.yml assets/logo/
git commit -m "docs: new flagship README (RU) + EN mirror + governance/support + release config + repo logo"
# опционально: git tag v2.3.0 && git push origin main --tags
```

Проверка на GitHub после пуша: баннер лого в dark/light, mindmap и timeline рендерятся,
GIF-анимации проигрываются, сворачивания работают, кнопка «Cite this repository» читает CITATION.cff.
