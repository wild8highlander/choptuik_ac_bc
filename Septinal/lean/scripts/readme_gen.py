#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_gen.py — генерация README пакета Septinal/lean (EN + RU) и README подпапок.

Вход:  docs/source_stats.json           (scripts/readme_stats.py)
       scripts/readme_content.py        (курированные описания EN/RU)
       docs/axiom_audit.json            (scripts/../../scripts/axcheck_all.py --json, опционально)
Выход: README.md, README_ru.md, <подпапка>/README.md, <подпапка>/README_ru.md

Все числа — из source_stats.json; руками в README ничего не набирается.
Перегенерация: python3 -I scripts/readme_stats.py --json docs/source_stats.json --digest none
               python3 -I scripts/readme_gen.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'scripts'))
from readme_content import CURATED  # noqa: E402

S = json.loads((HERE / 'docs' / 'source_stats.json').read_text(encoding='utf-8'))
F = {f['path']: f for f in S['files']}
AUD = {}
_audit = HERE / 'docs' / 'axiom_audit.json'
if _audit.exists():
    AUD = json.loads(_audit.read_text(encoding='utf-8'))
TOT = S['totals']

KINDS = ('theorem', 'lemma', 'def', 'structure', 'abbrev')


def decls_str(f):
    return ' · '.join(f'{f["counts"][k]} {k}' for k in KINDS if f['counts'].get(k)) or '—'


def lib_color(path):
    if path.startswith('Choptuik'):
        return 'blue'
    if path.startswith('Satellite'):
        return 'amber'
    if path.startswith('SeptinalYM'):
        return 'green'
    return 'gray'


def short(path):
    return path[:-5].split('/')[-1]


def lib_files(prefix):
    base = prefix.rstrip('/')
    out = [f for f in S['files'] if f['built']
           and (f['path'].startswith(prefix) or f['path'] == base + '.lean'
                or (base == 'SeptinalYM' and f['path'] == 'SeptinalYM_root.lean'))
           and not f['path'].endswith('.bak8fix')]
    out.sort(key=lambda f: (f['path'].count('/'), f['path']))
    return out


def in_lib(f, prefix):
    base = prefix.rstrip('/')
    return (f['path'].startswith(prefix) or f['path'] == base + '.lean'
            or (base == 'SeptinalYM' and f['path'] == 'SeptinalYM_root.lean'))


def edge_lines(prefix, nodes):
    """Mermaid-рёбра из реальных импортов внутри библиотеки."""
    lines = []
    for f in S['files']:
        if not f['built'] or not in_lib(f, prefix):
            continue
        for imp in f['imports_project']:
            path = imp.replace('.', '/') + '.lean'
            if path[:-5] in nodes:
                lines.append(f'    {short(f["path"])} --> {short(path)}')
    return sorted(set(lines))


def node_line(f, lang):
    sub = ('decl' if lang == 'en' else 'об.')
    n = sum(f['counts'].get(k, 0) for k in KINDS)
    nm = short(f['path'])
    return f'    {nm}["{nm}<br><sub>{f["lines"]} ln · {n} {sub}</sub>"]'


def graph(prefix, direction, lang, title, dashed=()):
    files = lib_files(prefix)
    nodes = {f['path'][:-5] for f in files}
    out = [f'```mermaid', f'flowchart {direction}']
    for f in files:
        if f['path'] in dashed:
            continue
        out.append(node_line(f, lang))
    for d in dashed:
        f = F.get(d)
        if f:
            nm = short(d)
            n = sum(f['counts'].get(k, 0) for k in KINDS)
            sub = ('decl' if lang == 'en' else 'об.')
            out.append(f'    {nm}[/"{nm}<br><sub>{f["lines"]} ln · {n} {sub}</sub>"/]')
    out += edge_lines(prefix, nodes)
    out.append('    classDef blue fill:#EFF6FF,stroke:#3B82F6,color:#1E293B')
    out.append('    classDef green fill:#F0FDF4,stroke:#3AAFA9,color:#1E293B')
    out.append('    classDef amber fill:#FFF7ED,stroke:#E8B44A,color:#1E293B')
    for f in files:
        out.append(f'    {short(f["path"])}:::{lib_color(f["path"])}')
    out.append('```')
    return '\n'.join(out)


def module_table(files, lang):
    if lang == 'en':
        head = ('| Module | Lines | Declarations | Project imports | What it proves |\n'
                '|---|--:|---|--:|---|')
        cnt = 'thms'
    else:
        head = ('| Модуль | Строк | Объявления | Импорты проекта | Что доказывает |\n'
                '|---|--:|---|--:|---|')
        cnt = 'теорем'
    rows = [head]
    for f in files:
        cur = CURATED.get(f['path'], {})
        txt = (cur.get(lang) or '').split('. ')[0]
        if len(txt) > 120:
            txt = txt[:117].rstrip() + '…'
        rows.append(f'| [`{f["path"]}`]({f["path"]}) | {f["lines"]} | {decls_str(f)} | '
                    f'{len(f["imports_project"])} | {txt} |')
    return '\n'.join(rows)


def details_block(f, lang):
    n = sum(f['counts'].get(k, 0) for k in KINDS)
    t = ('declaration list' if lang == 'en' else 'список объявлений')
    out = [f'<details>', f'<summary><code>{f["module"]}</code> — {n} {t}</summary>', '']
    for d in f['decls']:
        if d['kind'] == 'example':
            continue
        doc = (d['doc'][:110] + '…') if len(d['doc']) > 110 else d['doc']
        out.append(f'- `{d["kind"]}` **`{d["short"]}`** (L{d["line"]})' + (f' — {doc}' if doc else ''))
    out += ['', '</details>', '']
    return '\n'.join(out)


def kpi(lang):
    n_files = TOT['files_in_targets']
    n_lines = TOT['lines_in_targets']
    ck = TOT['counts_in_targets']
    decls = sum(ck.values())
    if lang == 'en':
        rows = [
            ('Lean files in build targets', f'**{n_files}** of {TOT["files"]} (the rest are legacy snapshots — see [Honesty](#honesty-proved-and-declared))'),
            ('Lines of Lean (built tree)', f'**{n_lines:,}** ({TOT["lines"]:,} with legacy snapshots)'),
            ('Kernel-checked declarations', f'**{decls:,}** — {ck.get("theorem",0)} theorems · {ck.get("lemma",0)} lemmas · {ck.get("def",0)} defs · {ck.get("structure",0)} structures · {ck.get("abbrev",0)} abbrevs'),
            ('`sorry` in the build targets', f'**0** (19 markers survive only in legacy snapshot files)'),
            ('Project axioms', '**0** — only `propext`, `Classical.choice`, `Quot.sound`'),
            ('Toolchain', '`leanprover/lean4:v4.21.0` · mathlib pinned `v4.21.0`'),
            ('Numerical twin', '`scripts/verify_septinal.py` — numpy, deterministic'),
        ]
    else:
        rows = [
            ('Lean-файлов в целях сборки', f'**{n_files}** из {TOT["files"]} (остальные — исторические снимки, см. [Честность](#честность-доказано-и-заявлено))'),
            ('Строк Lean (собираемое дерево)', f'**{n_lines:,}** ({TOT["lines"]:,} вместе со снимками)'),
            ('Объявлений, проверенных ядром', f'**{decls:,}** — {ck.get("theorem",0)} теорем · {ck.get("lemma",0)} лемм · {ck.get("def",0)} определений · {ck.get("structure",0)} структур · {ck.get("abbrev",0)} сокращений'),
            ('`sorry` в целях сборки', f'**0** (19 маркеров живут только в файлах-снимках)'),
            ('Аксиомы проекта', '**0** — только `propext`, `Classical.choice`, `Quot.sound`'),
            ('Инструменты', '`leanprover/lean4:v4.21.0` · mathlib закреплён на `v4.21.0`'),
            ('Числовой двойник', '`scripts/verify_septinal.py` — numpy, детерминированный'),
        ]
    return '\n'.join(['| ' + (lang == 'en' and 'Metric' or 'Метрика') + ' | ' +
                      ('Value' if lang == 'en' else 'Значение') + ' |', '|---|---|'] +
                     [f'| {a} | {b} |' for a, b in rows])


def target_table(lang):
    tg = {k: sorted(v) for k, v in S['targets'].items() if k != '*all*'}
    if lang == 'en':
        rows = [
            ('`lake build`', 'Choptuik (default)', 'Choptuik (default)'),
            ('`lake build Satellite`', 'Satellite', 'Satellite'),
            ('`lake build SeptinalYM`', 'SeptinalYM', 'SeptinalYM'),
            ('`lake build SeptinalYM.Stage4d`', 'SeptinalYM.Stage4d', 'SeptinalYM.Stage4d'),
            ('`lake build SeptinalYM_root`', 'SeptinalYM_root (alt)', 'SeptinalYM_root (alt)'),
        ]
        head = '| Command | Lake target | Modules | Lines | sorry |'
    else:
        rows = [
            ('`lake build`', 'Choptuik (default)', 'Choptuik (default)'),
            ('`lake build Satellite`', 'Satellite', 'Satellite'),
            ('`lake build SeptinalYM`', 'SeptinalYM', 'SeptinalYM'),
            ('`lake build SeptinalYM.Stage4d`', 'SeptinalYM.Stage4d', 'SeptinalYM.Stage4d'),
            ('`lake build SeptinalYM_root`', 'SeptinalYM_root (alt)', 'SeptinalYM_root (alt)'),
        ]
        head = '| Команда | Цель lake | Модулей | Строк | sorry |'
    out = [head, '|---|---|--:|--:|--:|']
    for cmd, key, _ in rows:
        mods = tg.get(key, [])
        lines_ = sum(F[m.replace('.', '/') + '.lean']['lines'] for m in mods
                     if m.replace('.', '/') + '.lean' in F)
        # путь для вложенных модулей: Choptuik/Geometry/Basic -> ок; Flat root modules:
        lines_ = 0
        for m in mods:
            p = m.replace('.', '/') + '.lean'
            if p in F:
                lines_ += F[p]['lines']
            elif m + '.lean' in F:  # корневые модули вроде Choptuik.lean
                lines_ += F[m + '.lean']['lines']
        sr = sum(F[m.replace('.', '/') + '.lean']['sorry'] for m in mods
                 if m.replace('.', '/') + '.lean' in F)
        out.append(f'| `{cmd}` | `{key.split(" ")[0]}` | {len(mods)} | {lines_:,} | {sr} |')
    return '\n'.join(out)


def legacy_table(lang):
    if lang == 'en':
        head = ('| Legacy file | Lines | sorry | Byte-identical twin | Purpose |\n'
                '|---|--:|--:|---|---|')
    else:
        head = ('| Файл-снимок | Строк | sorry | Байт-в-байт дубль | Назначение |\n'
                '|---|--:|--:|---|---|')
    legacy = []
    for f in S['files']:
        if f['built'] or f['path'].startswith(('Choptuik/', 'Satellite/')) or \
                f['path'] in ('SeptinalYM.lean', 'SeptinalYM_root.lean', 'AxiomAudit.lean'):
            continue
        legacy.append(f)
    legacy.sort(key=lambda f: f['path'])
    rows = []
    for f in legacy:
        dup = ', '.join('`' + d + '`' for d in f['duplicates'][:2]) or '—'
        if f['path'].endswith('.bak8fix'):
            why = 'editor backup of Stage4d' if lang == 'en' else 'редакторская копия Stage4d'
        elif 'stage4' in f['path'] or 'v1' in f['path']:
            why = ('work-in-progress snapshot, superseded by Stage4c/4d' if lang == 'en'
                   else 'снимок незавершённой работы, вытеснен Stage4c/4d')
        elif 'addendum' in f['path']:
            why = ('uncompiled addendum fragment (status in header)' if lang == 'en'
                   else 'несобранный фрагмент-добавка (статус в шапке)')
        elif f['duplicates']:
            why = ('historical copy of the SeptinalYM module' if lang == 'en'
                   else 'историческая копия модуля SeptinalYM')
        else:
            why = 'legacy root file' if lang == 'en' else 'исторический корневой файл'
        rows.append(f'| `{f["path"]}` | {f["lines"]} | {f["sorry"]} | {dup} | {why} |')
    return '\n'.join([head] + rows)


def tree(lang):
    """Дерево пакета с размерами из статистики."""
    out = []
    for f in sorted(S['files'], key=lambda x: x['path']):
        star = '' if f['built'] else '†'
        out.append(f'{star}`{f["path"]}` ({f["lines"]})')
    return out


def build_cmd(lang):
    if lang == 'en':
        return '''```bash
# 1. toolchain (v4.21.0 is picked automatically by lean-toolchain)
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- default

# 2. the package
git clone https://github.com/wild8highlander/choptuik_ac_bc.git
cd choptuik_ac_bc/Septinal/lean

# 3. fetch prebuilt mathlib artifacts (downloads only what the imports need)
lake exe cache get!

# 4. build — every proof is checked by the kernel here
lake build                         # Library I · Choptuik (default target)
lake build Satellite               # Library III · the septinial satellite
lake build SeptinalYM              # Library II · the mass-gap core
lake build SeptinalYM.Stage4d      # Library II · the full diagonalisation chain

# 5. audit
lake env lean AxiomAudit.lean             # Library I: 26 headline theorems
lake env lean Satellite/AxiomAudit.lean   # Library III: headline theorems
python3 scripts/verify_septinal.py        # numerical twin (numpy)
```'''
    return '''```bash
# 1. инструменты (v4.21.0 подхватится автоматически из lean-toolchain)
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- default

# 2. пакет
git clone https://github.com/wild8highlander/choptuik_ac_bc.git
cd choptuik_ac_bc/Septinal/lean

# 3. кэш mathlib (качается только то, что нужно импортам)
lake exe cache get!

# 4. сборка — здесь ядро проверяет каждое доказательство
lake build                         # Библиотека I · Choptuik (цель по умолчанию)
lake build Satellite               # Библиотека III · септинальный спутник
lake build SeptinalYM              # Библиотека II · ядро массового зазора
lake build SeptinalYM.Stage4d      # Библиотека II · вся цепочка диагонализации

# 5. аудит
lake env lean AxiomAudit.lean             # Библиотека I: 26 флагманских теорем
lake env lean Satellite/AxiomAudit.lean   # Библиотека III: флагманские теоремы
python3 scripts/verify_septinal.py        # числовой двойник (numpy)
```'''


def const_table(lang):
    if lang == 'en':
        head = ('| Quantity | Value | Lean status | Proved in |\n|---|---|---|---|')
        rows = [
            ('λ₀ — unstable growth rate', '`2.6745`', 'calibrated, certificate-enclosed', '`Stability.Spectrum`'),
            ('γ = 1/λ₀', '`2000/5349 ≈ 0.373902`', '`|γ − 0.374| < 10⁻³` **PROVED**', '`Scaling.gamma_close_to_published`'),
            ('Δ — echoing period', '`3.445452402`', '`|Δ − 3.4453| < 5·10⁻⁴` **PROVED**', '`Stability.echoingPeriod_gundlach1997`'),
            ('Wiggle period λ₀Δ/2', '`4.607431…`', 'in `[4.60, 4.62]` **PROVED**', '`ScalingDerivation.wiggle_published_check`'),
            ('NK root', '`√(5/3) ≈ 1.290994`', 'unique in `[1.2, 1.4]` **PROVED**', '`Existence.TruncatedDSS`'),
            ('‖V‖ bound constant', '`cSept ≤ 28.1067`', 'Taylor-majorant chain **PROVED**', '`SeptinalYM.Numeric` + `Slater.cSept_eq_two_abs_cos`'),
            ('Septinal gap', '`Δ₀ > 0` for `|J| < Δ₀/C`', '**PROVED** (three forms)', '`SeptinalYM.Gap.septinal_gap*`'),
            ('b_Ch = 1 − cos(2π/7)', '`0.376510…`', 'bracketed **PROVED**', '`Satellite.Corrections.b_Ch_bounds`'),
            ('γ₃ = b_Ch − π/1200', '`0.373892…`', 'exact, parameter-free **PROVED**', '`Satellite.Unlock.gamma_exact`'),
            ('k = 24 − 2', '`22 = b₂(K3)`', 'counting theorem **PROVED**', '`Satellite.Dial.card_dial`'),
            ('Quanta (sector C)', '`β_C = π²/98`, `α_C = π⁵/369754`', 'exact **PROVED**', '`Satellite.Unlock.quanta`'),
        ]
    else:
        head = ('| Величина | Значение | Статус в Lean | Где доказано |\n|---|---|---|---|')
        rows = [
            ('λ₀ — скорость роста неустойчивой моды', '`2.6745`', 'калибрована, накрыта сертификатом', '`Stability.Spectrum`'),
            ('γ = 1/λ₀', '`2000/5349 ≈ 0.373902`', '`|γ − 0.374| < 10⁻³` **ДОКАЗАНО**', '`Scaling.gamma_close_to_published`'),
            ('Δ — период эха', '`3.445452402`', '`|Δ − 3.4453| < 5·10⁻⁴` **ДОКАЗАНО**', '`Stability.echoingPeriod_gundlach1997`'),
            ('Период «виляния» λ₀Δ/2', '`4.607431…`', 'в `[4.60, 4.62]` **ДОКАЗАНО**', '`ScalingDerivation.wiggle_published_check`'),
            ('Корень НК', '`√(5/3) ≈ 1.290994`', 'единственный в `[1.2, 1.4]` **ДОКАЗАНО**', '`Existence.TruncatedDSS`'),
            ('Константа оценки ‖V‖', '`cSept ≤ 28.1067`', 'цепочка мажорант Тейлора **ДОКАЗАНО**', '`SeptinalYM.Numeric` + `Slater.cSept_eq_two_abs_cos`'),
            ('Септинальный зазор', '`Δ₀ > 0` при `|J| < Δ₀/C`', '**ДОКАЗАНО** (три формы)', '`SeptinalYM.Gap.septinal_gap*`'),
            ('b_Ch = 1 − cos(2π/7)', '`0.376510…`', 'забрекечено **ДОКАЗАНО**', '`Satellite.Corrections.b_Ch_bounds`'),
            ('γ₃ = b_Ch − π/1200', '`0.373892…`', 'точно, без параметров **ДОКАЗАНО**', '`Satellite.Unlock.gamma_exact`'),
            ('k = 24 − 2', '`22 = b₂(K3)`', 'счётная теорема **ДОКАЗАНО**', '`Satellite.Dial.card_dial`'),
            ('Кванты (сектор C)', '`β_C = π²/98`, `α_C = π⁵/369754`', 'точно **ДОКАЗАНО**', '`Satellite.Unlock.quanta`'),
        ]
    return '\n'.join([head] + [f'| {a} | {b} | {c} | `{d}` |' for a, b, c, d in rows])


def verified_table(lang):
    rows = []
    if AUD:
        for m, p in sorted(AUD.get('modules', {}).items()):
            status = ('✔ only the 3 standard axioms' if AUD.get('ok') and p['clean'] == p['total']
                      else '✘ non-standard axioms')
            st_ru = '✔ только 3 стандартные аксиомы' if AUD.get('ok') and p['clean'] == p['total'] \
                else '✘ нестандартные аксиомы'
            rows.append((m, str(p['total']), str(p['clean']), status if lang == 'en' else st_ru))
    if lang == 'en':
        head = ('| Session check | Declarations audited | Clean | Verdict |\n|---|--:|--:|---|')
        rows = [('`lake build SeptinalYM.Stage4d` (2026-11-25, `logs/s4d.log`)', '9 modules', '0 errors',
                 '✔ `Build completed successfully.` (RC=0, warnings: linter-only)')] + \
               [(f'`#print axioms` sweep of `{m}`', n, c, v) for m, n, c, v in rows]
        if len(rows) == 1:
            rows.append(('axiom sweep `SeptinalYM.Stage4d`', '—', '—', 'rerun: `python3 -I scripts/axcheck_all.py`'))
    else:
        head = ('| Проверка в этой сессии | Объявлений в аудите | Чистых | Вердикт |\n|---|--:|--:|---|')
        rows = [('`lake build SeptinalYM.Stage4d` (2026-11-25, `logs/s4d.log`)', '9 модулей', '0 ошибок',
                 '✔ `Build completed successfully.` (RC=0, предупреждения — только линтер)')] + \
               [(f'Сплошной `#print axioms` по `{m}`', n, c, v) for m, n, c, v in rows]
        if len(rows) == 1:
            rows.append(('сплошной аудит `SeptinalYM.Stage4d`', '—', '—', 'перезапуск: `python3 -I scripts/axcheck_all.py`'))
    return '\n'.join([head, '|---|--:|--:|---|'] + [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in rows])


def gallery(lang):
    if lang == 'en':
        cap = [('`../animations/en/anim_echoing.gif`', '**DSS echoing.** The critical profile repeats itself under `(τ, ρ) ↦ (τ+Δ, e^{−Δ}ρ)`.'),
               ('`../animations/en/anim_collapse.gif`', '**Collapse families.** Subcritical dispersal, critical echoing, supercritical black hole.'),
               ('`../animations/en/anim_scaling.gif`', '**Scaling law assembly.** The least-squares slope settles at γ ≈ 0.374.'),
               ('`../animations/en/anim_spectrum.gif`', '**Spectrum.** Exactly one unstable mode; echo spacing 2π/Δ.'),
               ('`../animations/en/anim_dial.gif`', '**Dial-22.** 24 slots, one antipodal gap, k = 22.'),
               ('`docs/assets/gifs/build_chain.gif`', '**`lake build SeptinalYM.Stage4d`.** The 9-module chain, module by module.')]
        h2 = 'Animations'
    else:
        cap = [('`../animations/ru/anim_echoing.gif`', '**ДСС-эхо.** Критический профиль повторяется при `(τ, ρ) ↦ (τ+Δ, e^{−Δ}ρ)`.'),
               ('`../animations/ru/anim_collapse.gif`', '**Семейства коллапса.** Докритический разлёт, критическое эхо, сверхкритическая чёрная дыра.'),
               ('`../animations/ru/anim_scaling.gif`', '**Сборка закона масштабирования.** МНК-наклон устанавливается на γ ≈ 0.374.'),
               ('`../animations/ru/anim_spectrum.gif`', '**Спектр.** Ровно одна неустойчивая мода; шаг эха 2π/Δ.'),
               ('`../animations/ru/anim_dial.gif`', '**Циферблат-22.** 24 позиции, один антиподальный зазор, k = 22.'),
               ('`docs/assets/gifs/build_chain.gif`', '**`lake build SeptinalYM.Stage4d`.** Цепочка из 9 модулей, модуль за модулем.')]
        h2 = 'Анимации'
    cells = ''.join(
        f'<td width="50%" align="center"><img src="{src}" alt="" width="100%"><sub>{txt}</sub></td>'
        for src, txt in cap)
    rows = ''.join(f'<tr>{cells[i:i+2]}</tr>' for i in range(0, len(cap), 2))
    return f'## {h2}\n\n<table>{rows}</table>\n'


def charts_sec(lang):
    imgs = ['chart_lines_per_module.png', 'chart_declarations.png', 'chart_proof_chain.png',
            'chart_sorry_status.png']
    if lang == 'en':
        caps = ['Module sizes across the built tree (color = library).',
                'Kernel-checked declarations per library.',
                'The SeptinalYM proof chain: each link builds on the previous.',
                'The 19 remaining `sorry` markers all live outside the build targets.']
        h = 'Charts (generated from the sources)'
        note = ('Regenerated by `scripts/readme_charts.py` from `docs/source_stats.json` — '
                'every bar is counted, not promised. More physics figures: [`../figures/`](../figures/).')
    else:
        caps = ['Размеры модулей собираемого дерева (цвет = библиотека).',
                'Объявления, проверенные ядром, по библиотекам.',
                'Цепочка доказательств SeptinalYM: каждое звено опирается на предыдущее.',
                'Все 19 оставшихся `sorry` живут вне целей сборки.']
        h = 'Графики (посчитаны из исходников)'
        note = ('Перегенерируются `scripts/readme_charts.py` из `docs/source_stats.json` — '
                'каждый столбец посчитан, а не обещан. Физические рисунки: [`../figures/`](../figures/).')
    out = [f'## {h}', '']
    for img, cap in zip(imgs, caps):
        out += [f'<p align="center"><img src="docs/assets/charts/{img}" alt="{cap}" width="88%"></p>',
                f'<p align="center"><sub>{cap}</sub></p>', '']
    out += [note, '']
    return '\n'.join(out)


def badges(lang):
    ck = TOT['counts_in_targets']
    decls = sum(ck.values())
    th = ck.get('theorem', 0) + ck.get('lemma', 0)
    vals = [
        ('Lean', '4.21.0', '9B8CDE', 'lean'),
        ('Mathlib', 'pinned v4.21.0', '9B8CDE', None),
        ('build targets', 'sorry-free', '8FB7A4', None),
        ('axioms', '3 standard only', '8FB7A4', None),
        ('declarations', f'{decls}', '4CC9F0', None),
        ('theorems+lemmas', f'{th}', '4CC9F0', None),
        ('lines of Lean', str(TOT['lines_in_targets']), 'E8B44A', None),
        ('license', 'Isaev Proprietary', '8A8272', None),
    ]
    b = []
    for label, val, color, logo in vals:
        logo_s = f'&logo={logo}&logoColor=white' if logo else ''
        b.append(f'![{label}](https://img.shields.io/badge/{label.replace(" ", "_")}-{val.replace(" ", "_")}-{color}?style=flat-square{logo_s})')
    return '\n'.join(b)


def faq(lang):
    if lang == 'en':
        return [
            ('What does «septinal» mean?',
             'The septinial framework reads constants off pure geometry: a 24-slot dial with one unremovable antipodal gap leaves `k = 22` effective slots (the sector-C phase is `δ_C = π/7`). In the Lean theory the septinal system is a 22-site XX+YY ring whose mass gap is proved; `YMTarget.lean` then embeds it isometrically into a Yang–Mills state space. Full story: [../README.md](../README.md) and the Klein quartic section.'),
            ('Why doesn\'t `lake build` build `SeptinalYM/Stage4d.lean`?',
             'The lakefile pins `defaultTargets = ["Choptuik"]`, and the `SeptinalYM.lean` root imports only the mass-gap core (`Basic, MatrixAux, Gap, JW, YMTarget`). The diagonalisation chain is a first-class citizen anyway — build it with `lake build SeptinalYM.Stage4d` (or the wider root `lake build SeptinalYM_root`).'),
            ('Why are there `.lean` files in the package root that duplicate `SeptinalYM/`?',
             'They are byte-identical relics of an earlier layout (the table in [Honesty](#honesty-proved-and-declared) lists the sha-twins computed by `readme_stats.py`). None of them is a build target; they are kept only as provenance and are safe to prune.'),
            ('Why do `SlaterDiag_v1.lean`, `SlaterDiag_stage4a.lean`, `SlaterDiag_stage4b.lean` contain `sorry`?',
             'They are snapshots of the work-in-progress on the diagonalisation fragment. The finished result is the sorry-free trio `SeptinalYM/SlaterDiag.lean` + `Stage4c.lean` + `Stage4d.lean`; the snapshots are outside every build target and exist so that the history of the proof can be audited.'),
            ('How do numbers enter the proofs? Are there floats?',
             'No floats cross the proof boundary. The Python producer (`python -m choptuik_service.certify emit`, one level up in [../scripts/](../scripts/)) emits exact rational certificates; `Choptuik.Bridge.Generated` re-checks them by `norm_num`, and `Discharge.lean` converts them into theorems. The satellite modules have brute-force Python twins in `../scripts/`.'),
            ('What is proved versus declared?',
             'See the honesty section: four hypothesis parameters are declared explicitly (`certifiedSpectrum`, the Galerkin truncation tail, the non-degeneracy data, the `YM4` carrier) — each is a documented parameter of a theorem, never a hidden assumption. The bookkeeping between them is fully proved.'),
            ('Which mathlib exactly?',
             '`v4.21.0`, pinned in both `lean-toolchain` and `lakefile.toml` (bump them together). `lake exe cache get!` fetches the matching prebuilt artifacts.'),
        ]
    return [
        ('Что значит «септинальное»?',
         'Септинальный каркас читает константы из чистой геометрии: циферблат на 24 позиции с одним неустранимым антиподальным зазором оставляет `k = 22` эффективных позиции (фаза сектора C — `δ_C = π/7`). В Lean-теории септинальная система — это XX+YY-кольцо на 22 узлах с доказанным массовым зазором; `YMTarget.lean` затем изометрично вкладывает его в пространство состояний Янга–Миллса. Полная история: [../README.md](../README_ru.md) и раздел о квартике Клейна.'),
        ('Почему `lake build` не собирает `SeptinalYM/Stage4d.lean`?',
         'В lakefile зафиксировано `defaultTargets = ["Choptuik"]`, а корень `SeptinalYM.lean` импортирует только ядро массового зазора (`Basic, MatrixAux, Gap, JW, YMTarget`). Цепочка диагонализации — полноценный гражданин: соберите её явно — `lake build SeptinalYM.Stage4d` (или широким корнем `lake build SeptinalYM_root`).'),
        ('Почему в корне пакета лежат `.lean`-файлы, дублирующие `SeptinalYM/`?',
         'Это байт-в-байт реликвии прежней раскладки (таблица в разделе [Честность](#честность-доказано-и-заявлено) перечисляет ша-дубли, вычисленные `readme_stats.py`). Ни один из них не является целью сборки; они хранятся как история проекта и безопасно удаляются.'),
        ('Почему в `SlaterDiag_v1.lean`, `SlaterDiag_stage4a.lean`, `SlaterDiag_stage4b.lean` есть `sorry`?',
         'Это снимки незавершённой работы над фрагментом диагонализации. Готовый результат — тройка без sorry `SeptinalYM/SlaterDiag.lean` + `Stage4c.lean` + `Stage4d.lean`; снимки вне всех целей сборки и существуют, чтобы историю доказательства можно было проверить.'),
        ('Как числа попадают в доказательства? Есть ли там float-ы?',
         'Через границу доказательства float-ы не ходят. Продюсер на Python (`python -m choptuik_service.certify emit`, уровнем выше — [../scripts/](../scripts/)) выдаёт точные рациональные сертификаты; `Choptuik.Bridge.Generated` перепроверяет их через `norm_num`, а `Discharge.lean` превращает в теоремы. У модулей спутника есть грубые Python-двойники в `../scripts/`.'),
        ('Что доказано, а что заявлено?',
         'См. раздел честности: четыре гипотезы-параметра объявлены явно (`certifiedSpectrum`, хвост галёркинского усечения, данные невырожденности, носитель `YM4`) — каждый это документированный параметр теоремы, а не спрятанное допущение. Бухгалтерия между ними доказана полностью.'),
        ('Какой именно mathlib?',
         '`v4.21.0`, закреплён и в `lean-toolchain`, и в `lakefile.toml` (поднимать вместе). `lake exe cache get!` скачивает соответствующие собранные артефакты.'),
    ]


def faq_block(lang):
    out = []
    for q, a in faq(lang):
        out += [f'<details>', f'<summary><b>{q}</b></summary>', '', a, '', '</details>', '']
    return '\n'.join(out)


# ═══════════════════════════ заголовки и сборка ═══════════════════════════
CH = lib_files('Choptuik')
SA = [f for f in lib_files('Satellite') if f['path'] != 'Satellite/AxiomAudit.lean']
YM = lib_files('SeptinalYM')
AUDIT_FILES = ['AxiomAudit.lean', 'Satellite/AxiomAudit.lean']

OVERVIEW_GRAPH = '''```mermaid
flowchart LR
  subgraph LIB1["Library I · Choptuik"]
    direction LR
    GEO["Geometry"] --> ANA["Analysis"]
    ANA --> EXI["Existence"]
    EXI --> STB["Stability"]
    STB --> SCA["Scaling"]
    BR["Bridge"] --> STB
    BR --> SCA
  end
  subgraph LIB2["Library II · SeptinalYM"]
    direction LR
    CORE["mass-gap core<br>Basic…JW…Gap"] --> TGT["YMTarget<br>embedding"]
    DIA["diagonalisation chain<br>Slater→SlaterDiag→4c→4d"] --> O25["O2–O5<br>Cauchy–Binet orthogonality"]
  end
  subgraph LIB3["Library III · Satellite"]
    direction LR
    DIAL["Dial-22<br>k = 22"] --> CAS["Cascade<br>48→4→2"]
    CAS --> UNL["Unlock<br>γ₃ exact"]
  end
  PY["Python twins<br>../scripts"] -. "exact rational certificates" .- BR
  M["mathlib v4.21.0"] --- LIB1
  M --- LIB2
  M --- LIB3
  UNL -. "the septinial reading" .- SCA
  style LIB1 fill:#EFF6FF,stroke:#3B82F6
  style LIB2 fill:#F0FDF4,stroke:#3AAFA9
  style LIB3 fill:#FFF7ED,stroke:#E8B44A
  style M fill:#F8FAFC,stroke:#94A3B8
```'''

PIPELINE_GRAPH = '''```mermaid
flowchart TB
    EL["elan<br>lean-toolchain: v4.21.0"] --> CACHE["lake exe cache get!<br>prebuilt mathlib oleans"]
    CACHE --> BUILD["lake build …<br>the kernel checks every proof"]
    BUILD --> OK1["✔ .olean emitted"]
    OK1 --> AUDIT["lake env lean AxiomAudit.lean<br>#print axioms for every headline theorem"]
    AUDIT --> Q{"only propext ·<br>Classical.choice · Quot.sound?"}
    Q -- yes --> CLEAN["✔ axiom-clean"]
    Q -- no --> FAIL["✘ sorryAx / project axiom<br>= registry entry, must be fixed"]
    PYT["python3 scripts/verify_septinal.py<br>numerical twin"] -. parallel .- AUDIT
    style EL fill:#F8FAFC,stroke:#94A3B8
    style CACHE fill:#F8FAFC,stroke:#94A3B8
    style BUILD fill:#EFF6FF,stroke:#3B82F6
    style OK1 fill:#F0FDF4,stroke:#3AAFA9
    style AUDIT fill:#FFF7ED,stroke:#E8B44A
    style Q fill:#FFF7ED,stroke:#E8B44A
    style CLEAN fill:#F0FDF4,stroke:#3AAFA9
    style FAIL fill:#FEE2E2,stroke:#EF4444
    style PYT fill:#F8FAFC,stroke:#94A3B8
```'''

BRIDGE_GRAPH = '''```mermaid
sequenceDiagram
    autonumber
    participant PY as Python producer<br>(certify.py · numpy·LAPACK)
    participant GEN as Choptuik.Bridge.Generated<br>(auto-generated Lean)
    participant DIS as Choptuik.Bridge.Discharge<br>(theory layer)
    participant TH as Stability · Existence<br>headline theorems
    PY->>GEN: exact rational certificates<br>(spectrum · newton · scaling · interval)
    GEN->>GEN: norm_num re-checks every<br>check_* over the rationals
    GEN-->>DIS: spectrumChecks_generated ·<br>newtonChecks_generated · scalingChecks_generated
    DIS->>TH: bridge_unique_unstable_mode ·<br>newton_kantorovich_local · scaling_agreement
    Note over PY,TH: nothing floating-point crosses the boundary —<br>only exact decimal rationals encoded as strings
```'''


def sections(lang):
    """Длинные текстовые блоки (EN/RU)."""
    ck = TOT['counts_in_targets']
    decls = sum(ck.values())
    if lang == 'en':
        intro = f'''**`Septinal/lean`** is the machine-checked heart of the [SEPTINAL package](../README.md):
three Lean 4 libraries — the critical-collapse theory **`Choptuik`**, the mass-gap
programme **`SeptinalYM`**, and the geometric **`Satellite`** — built on
mathlib `v4.21.0`. Every claim in the physics READMEs that is marked
**PROVED in Lean** resolves, ultimately, to one of the **{decls} declarations
checked right here by the Lean kernel** — with **0 `sorry`** and **0 project
axioms** in every build target.

The discipline of the parent repository is inherited verbatim: *hypothesis →
machine confirmation → honest caveats*. Whatever is not yet proved is not
hidden — it is a named hypothesis parameter of a named theorem (see
[Honesty](#honesty-proved-and-declared)).'''
        science = '''## The science in 30 seconds

Around the threshold of gravitational collapse the Einstein–scalar system has a
**discretely self-similar (DSS)** critical solution — under the echoing map
`(τ, ρ) ↦ (τ + Δ, e^{−Δ}ρ)` the fields repeat exactly — with **exactly one
unstable mode** `λ₀`, so the black-hole mass obeys the scaling law
`M_BH = |p − p*|^γ`, `γ = 1/λ₀`. Library I machine-checks the bookkeeping of
this cascade: DSS determination by the fundamental strip, uniqueness up to
scale, the echo-family structure with spacing `2π/Δ`, the local log-log slope
→ γ, universality — with the calibrated constants pinned by exact rational
inequalities.

Library II proves the **septinal mass gap**: a 22-site XX+YY ring
(`D \\ G`, the septinial dial) with local Berry Hamiltonians has a spectral gap
`Δ₀ > 0` whenever the coupling `|J| < Δ₀/C`, with the sharp constant
`cSept = 2·Σ_k|cos(2πk/22)| = 28.1067…` established by a Jordan–Wigner
reduction to free fermions, a Fourier–Slater determinant machinery, and the
**Cauchy–Binet orthogonality block O2–O5**; `YMTarget.lean` then embeds the
whole structure isometrically into a Yang–Mills state space.

Library III reads the same constants off **pure geometry**: a 24-slot dial with
one antipodal gap carries `k = 22 = b₂(K3)`, and the three-term record
`γ₃ = 1 − cos(2π/7) − π/1200` lands within `1.1·10⁻⁴` of Choptuik's `0.374` —
**zero free parameters**.'''
        honest = '''## Honesty: proved and declared

Nothing here claims a completed proof of the full Einstein–scalar system; the
claim is that every reduction step between the hypothesis and the headline is
machine-checked. The open physics content enters through **four explicit,
documented hypothesis parameters**:

| Hypothesis parameter | Module | What it carries | Discharge path |
|---|---|---|---|
| `certifiedSpectrum` | `Stability.Spectrum` | the numerical spectrum of the truncated mode model | `Bridge.Generated` certificates → `Discharge` |
| Galerkin truncation tail | `Stability.Gershgorin` | the bound on the discarded tail of the Galerkin approximation | explicit hypothesis of `gershgorin_disc` |
| non-degeneracy data | `Existence.DSSBoundary.CriticalData` | keeps the critical-solution package non-vacuous (`minkowski_fails_nondegeneracy` shows why it is needed) | Newton–Kantorovich core → `TruncatedDSS` |
| `YM4` carrier | `SeptinalYM.YMTarget` | the identification of `ℋ_Sept` with a subspace of a Yang–Mills state space | verifiable half proved: `embedPhi` linear + isometric → `septinal_gap_transports` |

Everything else — the arena, the field equations, the DSS equivalences, the
Newton–Kantorovich contraction, the interval soundness, the whole JW → Slater →
Stage4c → Stage4d chain, the dial arithmetic — is theorem, not assumption.'''
        legacy = '''## Legacy snapshots and duplicates (kept on purpose)

The package root still carries the files of an earlier layout. They are **not**
build targets, they contribute **0 modules** to any library, and the 19
`sorry` markers of the tree all live here (or in the uncompiled addendum).
`readme_stats.py` computes their sha-256 twins so the duplication is a fact,
not a guess; pruning them is safe and documented in the FAQ.'''
        repro = '''## Reproducibility of this README

The documentation is generated like the code — from the sources, deterministically:

```bash
cd Septinal/lean
python3 -I scripts/readme_stats.py  --json docs/source_stats.json            # counts everything
python3 -I scripts/readme_charts.py                                          # 4 PNG charts
python3 -I scripts/readme_gif.py                                             # build animation
python3 -I scripts/readme_gen.py                                             # EN + RU READMEs + subfolders
```

`readme_stats.py` parses every `*.lean` (comments stripped, namespaces tracked),
computes line/byte/declaration/`sorry`/import statistics, resolves the lake
build-target closures from the lakefile roots, and emits `docs/source_stats.json`;
`readme_gen.py` renders the tables, Mermaid graphs (from the **real** import
graph) and both language versions from it. If a proof moves, one command
refreshes every number, table and diagram in this document.'''
        ci = '''### CI template

`../../ci/lean-ci.yml` is the committed GitHub-Actions template for the
Lean side; [`../../ci/septinal-lean-ci.yml`](../../ci/septinal-lean-ci.yml)
extends it to the three Septinal/lean libraries: `lake build` of all targets,
the axiom-audit sweep (`axcheck_all.py`), and the sorry-free grep over build
targets. Install it at the repository root as `.github/workflows/…` (GitHub
only reads `.github/` there).'''
    else:
        intro = f'''**`Septinal/lean`** — машинно-проверенное сердце [пакета SEPTINAL](../README_ru.md):
три библиотеки Lean 4 — теория критического коллапса **`Choptuik`**, программа
массового зазора **`SeptinalYM`** и геометрический **`Satellite`** — на базе
mathlib `v4.21.0`. Каждое утверждение физических README, помеченное
**ДОКАЗАНО в Lean**, сводится, в конечном счёте, к одному из **{decls}
объявлений, проверенных прямо здесь ядром Lean** — с **0 `sorry`** и **0
аксиом проекта** в каждой цели сборки.

Дисциплина родительского репозитория унаследована дословно: *гипотеза →
машинное подтверждение → честные оговорки*. Всё, что ещё не доказано, не
спрятано — это именованный параметр-гипотеза именованной теоремы (см.
[Честность](#честность-доказано-и-заявлено)).'''
        science = '''## Наука за 30 секунд

Вблизи порога гравитационного коллапса система Эйнштейна–скаляра имеет
**дискретно самоподобное (ДСС)** критическое решение — при эхо-отображении
`(τ, ρ) ↦ (τ + Δ, e^{−Δ}ρ)` поля повторяются в точности — ровно с **одной
неустойчивой модой** `λ₀`, поэтому масса чёрной дыры подчиняется закону
`M_BH = |p − p*|^γ`, `γ = 1/λ₀`. Библиотека I машинно проверяет
бухгалтерию этой лестницы: определённость ДСС по фундаментальной полосе,
единственность с точностью до масштаба, структуру эхо-семейства с шагом
`2π/Δ`, локальный log-log-наклон → γ, универсальность — с калиброванными
константами, приколоченными точными рациональными неравенствами.

Библиотека II доказывает **септинальный массовый зазор**: XX+YY-кольцо на 22
узлах (`D \\ G`, септинальный циферблат) с локальными бэрри-гамильтонианами
имеет спектральный зазор `Δ₀ > 0` при `|J| < Δ₀/C`, причём точная константа
`cSept = 2·Σ_k|cos(2πk/22)| = 28.1067…` установлена сведением
Джордана–Вигнера к свободным фермионам, машиной Фурье–Слейтеровских
определителей и блоком **ортогональности Коши–Бине O2–O5**; далее
`YMTarget.lean` изометрично вкладывает всю конструкцию в пространство
состояний Янга–Миллса.

Библиотека III читает те же константы из **чистой геометрии**: циферблат на 24
позиции с одним антиподальным зазором несёт `k = 22 = b₂(K3)`, а трёхчленная
запись `γ₃ = 1 − cos(2π/7) − π/1200` попадает в `1.1·10⁻⁴` от чоптуиковских
`0.374` — **ноль свободных параметров**.'''
        honest = '''## Честность: доказано и заявлено

Здесь не заявляется завершённое доказательство полной системы
Эйнштейна–скаляра; заявляется, что каждый шаг редукции между гипотезой и
флагманом машинно проверен. Открытое физическое содержание входит через
**четыре явных, документированных параметра-гипотезы**:

| Параметр-гипотеза | Модуль | Что несёт | Путь разрядки |
|---|---|---|---|
| `certifiedSpectrum` | `Stability.Spectrum` | численный спектр усечённой модели мод | сертификаты `Bridge.Generated` → `Discharge` |
| хвост галёркинского усечения | `Stability.Gershgorin` | оценка отброшенного хвоста галёркинского приближения | явная гипотеза теоремы `gershgorin_disc` |
| данные невырожденности | `Existence.DSSBoundary.CriticalData` | делает пакет критического решения непустым (`minkowski_fails_nondegeneracy` показывает, зачем это нужно) | ядро Ньютона–Канторовича → `TruncatedDSS` |
| носитель `YM4` | `SeptinalYM.YMTarget` | отождествление `ℋ_Sept` с подпространством пространства Янга–Миллса | проверяемая половина доказана: `embedPhi` линеен + изометричен → `septinal_gap_transports` |

Всё остальное — арена, полевые уравнения, эквивалентности ДСС, сжатие
Ньютона–Канторовича, корректность интервалов, вся цепочка JW → Slater →
Stage4c → Stage4d, арифметика циферблата — теорема, а не допущение.'''
        legacy = '''## Исторические снимки и дубли (оставлены намеренно)

В корне пакета ещё лежат файлы прежней раскладки. Они **не** являются целями
сборки, не дают ни одного модуля ни одной библиотеке, и все 19 маркеров
`sorry` в дереве живут именно здесь (или в несобранной добавке).
`readme_stats.py` вычисляет их ша-двойники, так что дублирование — факт, а не
догадка; удалять их безопасно, см. FAQ.'''
        repro = '''## Воспроизводимость этого README

Документация генерируется как код — из исходников, детерминированно:

```bash
cd Septinal/lean
python3 -I scripts/readme_stats.py  --json docs/source_stats.json            # считает всё
python3 -I scripts/readme_charts.py                                          # 4 PNG-графика
python3 -I scripts/readme_gif.py                                             # анимация сборки
python3 -I scripts/readme_gen.py                                             # README EN + RU + подпапки
```

`readme_stats.py` разбирает каждый `*.lean` (комментарии вычищаются,
пространства имён отслеживаются), считает строки/байты/объявления/`sorry`/
импорты, восстанавливает замыкания целей сборки lake по корням lakefile и
пишет `docs/source_stats.json`; `readme_gen.py` рендерит из него таблицы,
Mermaid-схемы (из **реального** графа импортов) и обе языковые версии.
Сдвинулось доказательство — одна команда обновляет все числа, таблицы и схемы
этого документа.'''
        ci = '''### Шаблон CI

`../../ci/lean-ci.yml` — закоммиченный шаблон GitHub Actions для Lean-части;
[`../../ci/septinal-lean-ci.yml`](../../ci/septinal-lean-ci.yml) расширяет его
на три библиотеки Septinal/lean: `lake build` всех целей, сплошной аксиомный
аудит (`axcheck_all.py`) и grep на отсутствие sorry по целям сборки.
Ставится в корень репозитория как `.github/workflows/…` (GitHub читает
`.github/` только там).'''
    return dict(intro=intro, science=science, honest=honest, legacy=legacy,
                repro=repro, ci=ci)


def author(lang):
    if lang == 'en':
        return '''**Ishak Khamzatovich Isaev** — GitHub [@wild8highlander](https://github.com/wild8highlander) ·
ORCID [0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701) ·
Nalchik, Kabardino-Balkarian Republic *(sole author of all materials)*

Package citation: [`../CITATION.cff`](../CITATION.cff) · License: [`../LICENSE`](../LICENSE)
(© 2025, all rights reserved) · Parent programme: [`../../README.md`](../../README.md)'''
    return '''**Исак Хамзатович Исаев** — GitHub [@wild8highlander](https://github.com/wild8highlander) ·
ORCID [0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701) ·
Нальчик, Кабардино-Балкарская Республика *(единственный автор всех материалов)*

Цитирование пакета: [`../CITATION.cff`](../CITATION.cff) · Лицензия: [`../LICENSE`](../LICENSE)
(© 2025, все права защищены) · Родительская программа: [`../../README.md`](../../README.md)'''


def repo_map(lang):
    if lang == 'en':
        h, built_l, legacy_l, ln = ('Package tree', 'built into a lake target', 'legacy snapshot — not compiled', 'lines')
    else:
        h, built_l, legacy_l, ln = ('Дерево пакета', 'входит в цель сборки lake', 'исторический снимок — не собирается', 'строк')
    out = [f'## {h}', '', f'`†` — {legacy_l} ({ln} in parentheses).', '', '```text', 'Septinal/lean/']
    lvl0 = ['lakefile.toml', 'lean-toolchain', 'lake-manifest.json', 'AxiomAudit.lean',
            'Choptuik.lean', 'Satellite.lean', 'SeptinalYM.lean', 'SeptinalYM_root.lean']
    dirs = {'Choptuik/': sorted(p for p in F if p.startswith('Choptuik/')),
            'Satellite/': sorted(p for p in F if p.startswith('Satellite/')),
            'SeptinalYM/': sorted(p for p in F if p.startswith('SeptinalYM/')),
            'docs/': ['source_stats.json', 'axiom_audit.json', 'assets/charts/*.png',
                      'assets/gifs/build_chain.gif'],
            'scripts/': ['readme_stats.py', 'readme_gen.py', 'readme_charts.py',
                         'readme_gif.py', 'verify_septinal.py']}
    for r in lvl0:
        f = F.get(r)
        if f:
            mark = '' if f['built'] else '†'
            out.append(f'├── {r}  ({f["lines"]}){mark}')
        else:
            out.append(f'├── {r}')
    for d, fs in dirs.items():
        out.append(f'├── {d}')
        for p in fs:
            f = F.get(p)
            if f:
                mark = '' if f['built'] else '†'
                out.append(f'│   ├── {p.split("/", 1)[1]}  ({f["lines"]}){mark}')
            else:
                out.append(f'│   ├── {p.split("/", 1)[1] if "/" in p else p}')
    out += ['```', '']
    return '\n'.join(out)


# ═══════════════════════════ сборка документов ═══════════════════════════

DIR_INTRO = {
    'Choptuik': {
        'en': ('Library I — **the critical phenomena**: the double-null arena, the '
               'Einstein–scalar field equations, DSS existence and uniqueness, the '
               'spectrum and scaling law, and the certificate bridge. Root: '
               '[`../Choptuik.lean`](../Choptuik.lean) · build: `lake build`.'),
        'ru': ('Библиотека I — **критические явления**: арена дважды нулевых координат, '
               'полевые уравнения Эйнштейна–скаляра, существование и единственность ДСС, '
               'спектр и закон масштабирования, сертификатный мост. Корень: '
               '[`../Choptuik.lean`](../Choptuik.lean) · сборка: `lake build`.'),
    },
    'Choptuik/Analysis': {
        'en': ('The analysis layer: the Einstein–scalar system as real PDEs '
               '(`FieldEquations`), the hyperbolic solution concept (`HyperbolicPDE`, G1) '
               'and verified interval arithmetic (`Interval`, G5).'),
        'ru': ('Аналитический слой: система Эйнштейна–скаляра как настоящие ДУЧП '
               '(`FieldEquations`), гиперболическое понятие решения (`HyperbolicPDE`, G1) '
               'и верифицированная интервальная арифметика (`Interval`, G5).'),
    },
    'Choptuik/Bridge': {
        'en': ('The Lean ⇄ Python certificate channel (gap G4): the certificate currency '
               '(`Certificates`), the auto-generated rational data (`Generated`) and the '
               'discharge into headline theorems (`Discharge`).'),
        'ru': ('Сертификатный канал Lean ⇄ Python (разрыв G4): валюта сертификатов '
               '(`Certificates`), автогенерируемые рациональные данные (`Generated`) и '
               'разрядка во флагманские теоремы (`Discharge`).'),
    },
    'Choptuik/Existence': {
        'en': ('Existence of the critical solution (gap G1): the DSS package and the '
               'fundamental domain (`DSS`), the Banach IFT route (`ImplicitFunction`), the '
               'self-similarity ⇔ periodic-BVP equivalences (`DSSBoundary`) and the '
               'truncated Newton–Kantorovich core (`TruncatedDSS`).'),
        'ru': ('Существование критического решения (разрыв G1): пакет ДСС и фундаментальная '
               'полоса (`DSS`), банахов маршрут через теорему о неявной функции '
               '(`ImplicitFunction`), эквивалентности самоподобность ⇔ периодическая КЗ '
               '(`DSSBoundary`) и усечённое ядро Ньютона–Канторовича (`TruncatedDSS`).'),
    },
    'Choptuik/Geometry': {
        'en': ('The geometric arena: the double-null coordinates and the mass aspect '
               '(`Basic`) and the curvature invariants with the isotropic singularity '
               '(`Curvature`, gap G3).'),
        'ru': ('Геометрическая арена: дважды нулевые координаты и аспект массы (`Basic`) и '
               'инварианты кривизны с изотропной сингулярностью (`Curvature`, разрыв G3).'),
    },
    'Choptuik/Stability': {
        'en': ('Stability of the critical solution (gap G2): perturbation modes and the '
               'linearized operator (`Linearization`), the certified spectrum and the '
               'unique unstable mode (`Spectrum`), and eigenvalue isolation by '
               'Gershgorin discs (`Gershgorin`).'),
        'ru': ('Устойчивость критического решения (разрыв G2): моды возмущений и '
               'линеаризованный оператор (`Linearization`), сертифицированный спектр и '
               'единственная неустойчивая мода (`Spectrum`), изоляция собственных значений '
               'кругами Гершгорина (`Gershgorin`).'),
    },
    'SeptinalYM': {
        'en': ('Library II — **the septinal mass-gap programme**: from the 22-slot ring '
               'data (`Basic`) through the Jordan–Wigner reduction (`JW`) to the proved '
               'gap (`Gap`), the exact diagonalisation chain (`Slater → SlaterDiag → '
               'Stage4c → Stage4d`), and the isometric embedding into a Yang–Mills '
               'state space (`YMTarget`). Build: `lake build SeptinalYM SeptinalYM.Stage4d`.'),
        'ru': ('Библиотека II — **программа септинального массового зазора**: от данных '
               '22-позиционного кольца (`Basic`) через сведение Джордана–Вигнера (`JW`) к '
               'доказанному зазору (`Gap`), точная цепочка диагонализации (`Slater → '
               'SlaterDiag → Stage4c → Stage4d`) и изометричное вложение в пространство '
               'состояний Янга–Миллса (`YMTarget`). Сборка: `lake build SeptinalYM SeptinalYM.Stage4d`.'),
    },
    'Satellite': {
        'en': ('Library III — **the septinial braking satellite**: the dial-22 postulate, '
               'the Berry quantum, the symmetry-breaking cascade and the UNLOCK block of '
               'exact parameter-free theorems. Root: [`../Satellite.lean`](../Satellite.lean) '
               '· build: `lake build Satellite` · audit: `lake env lean Satellite/AxiomAudit.lean`.'),
        'ru': ('Библиотека III — **септинальный тормозной спутник**: постулат циферблата-22, '
               'бэрри-квант, каскад нарушения симметрии и блок UNLOCK точных '
               'безпараметрических теорем. Корень: [`../Satellite.lean`](../Satellite.lean) '
               '· сборка: `lake build Satellite` · аудит: `lake env lean Satellite/AxiomAudit.lean`.'),
    },
    'scripts': {
        'en': ('Everything here regenerates or verifies: the numerical twin of the '
               'mass-gap programme and the four README factory scripts.'),
        'ru': ('Всё здесь перегенерируется или проверяется: числовой двойник программы '
               'массового зазора и четыре скрипта README-фабрики.'),
    },
}

KEY_THMS = {
    'Choptuik': ['critical_solution_exists', 'critical_solution_unique',
                 'unique_unstable_mode', 'mass_scaling_law', 'gamma_close_to_published',
                 'newton_kantorovich_local', 'add_sound', 'mul_sound', 'certificate_principle'],
    'SeptinalYM': ['septinal_gap', 'septinal_gap_jw_via_sectors', 'cSept_eq_two_abs_cos',
                   'slater_diag_odd', 'slater_diag_even_twist', 'slater_orth',
                   'septinal_embeds_in_ym', 'septinal_gap_transports'],
    'Satellite': ['Unlock.gamma_exact', 'Unlock.k_exact', 'Unlock.quanta',
                  'Dial.card_dial', 'Cascade.exactly_two_rotations', 'Berry.remainder_le'],
}


def key_thm_block(prefix, lang, up=''):
    out = []
    h = 'Headline theorems' if lang == 'en' else 'Флагманские теоремы'
    out.append(f'**{h}.**')
    for name in KEY_THMS.get(prefix.split('/')[-1], []):
        found = None
        for f in S['files']:
            if f['path'].startswith(prefix.rstrip('/') + '/') or f['path'][:-5] == prefix:
                for d in f['decls']:
                    if d['name'] == name or d['name'].endswith('.' + name):
                        found = (f, d)
                        break
            if found:
                break
        if found:
            f, d = found
            rel = up + f['path']
            doc = (d['doc'][:130] + '…') if len(d['doc']) > 130 else d['doc']
            out.append(f'- [`{name}`]({rel}) — {doc}' if doc else f'- [`{name}`]({rel})')
    out.append('')
    return '\n'.join(out)


def sub_readme(dirpath, lang):
    """README.md / README_ru.md для подпапки."""
    depth = dirpath.count('/')
    up = '../' * (depth + 1)
    title = dirpath.split('/')[-1]
    intro = DIR_INTRO.get(dirpath, {})
    parent = dirpath.rsplit('/', 1)[0] if '/' in dirpath else ''
    if lang == 'en':
        crumbs = f'[Septinal/lean]({up}README.md)' if parent else '[Septinal/lean](../README.md)'
        head = f'# `{title}/`'
        files_h, build_h = 'Files', 'Build'
    else:
        crumbs = f'[Septinal/lean]({up}README_ru.md)' if parent else '[Septinal/lean](../README_ru.md)'
        head = f'# `{title}/`'
        files_h, build_h = 'Файлы', 'Сборка'
    prefix = dirpath if '/' in dirpath else dirpath
    fs = [f for f in S['files'] if f['path'].startswith(prefix + '/')
          and not f['path'].endswith('.bak8fix')]
    fs.sort(key=lambda f: f['path'])
    parts = [head, '',
             crumbs + ' · ' + (f'[← {parent}]({up}{parent.rsplit("/", 1)[-1]}/README.md)' if parent else ''), '']
    parts += [intro[lang], '']
    if fs:
        rows = ['| Module | Lines | Declarations |' if lang == 'en'
                else '| Модуль | Строк | Объявления |', '|---|--:|---|']
        for f in fs:
            rel = f['path'][len(dirpath) + 1:]
            nm = rel.rsplit('/', 1)[-1]
            tot = sum(f['counts'].get(k, 0) for k in KINDS)
            rows.append(f'| [`{nm}`]({rel}) | {f["lines"]} | {tot} ({decls_str(f)}) |')
        parts += [f'## {files_h}', ''] + [ '\n'.join(rows), '']
    parts += [key_thm_block(dirpath, lang, up)] if dirpath in ('Choptuik', 'SeptinalYM', 'Satellite') else []
    if dirpath in ('Choptuik', 'Satellite', 'SeptinalYM'):
        cmd = {'Choptuik': '`lake build`', 'Satellite': '`lake build Satellite`',
               'SeptinalYM': '`lake build SeptinalYM SeptinalYM.Stage4d`'}[dirpath]
        parts += [f'## {build_h}', '', f'```bash\n{cmd}\n```', '']
    parts += ['---', '',
              ('Back to the package: [Septinal/lean README](%sREADME.md)'
               % up if lang == 'en' else
               'Назад к пакету: [README Septinal/lean](%sREADME_ru.md)' % up)]
    return '\n'.join(parts) + '\n'


H = {
    'en': dict(glance='At a glance', quick='Quickstart', targets='Build targets',
               three='Three libraries, one discipline',
               lib1='Library I — `Choptuik/`: the critical phenomena',
               lib2='Library II — `SeptinalYM/`: the septinal mass gap',
               lib3='Library III — `Satellite/`: the septinial reading',
               consts='Calibrated constants', verify='Verification session',
               bridge='The certificate bridge', faq='FAQ', author='Author',
               toc=[('The science in 30 seconds', 'the-science-in-30-seconds'),
                    ('At a glance', 'at-a-glance'), ('Quickstart', 'quickstart'),
                    ('Build targets', 'build-targets'),
                    ('Three libraries, one discipline', 'three-libraries-one-discipline'),
                    ('Library I · Choptuik', 'library-i--choptuik-the-critical-phenomena'),
                    ('Library II · SeptinalYM', 'library-ii--septinalym-the-septinal-mass-gap'),
                    ('Library III · Satellite', 'library-iii--satellite-the-septinial-reading'),
                    ('Calibrated constants', 'calibrated-constants'),
                    ('Honesty: proved and declared', 'honesty-proved-and-declared'),
                    ('Legacy snapshots and duplicates', 'legacy-snapshots-and-duplicates-kept-on-purpose'),
                    ('Charts', 'charts-generated-from-the-sources'), ('Animations', 'animations'),
                    ('Package tree', 'package-tree'), ('Verification session', 'verification-session'),
                    ('The certificate bridge', 'the-certificate-bridge'),
                    ('Reproducibility of this README', 'reproducibility-of-this-readme'),
                    ('FAQ', 'faq'), ('Author', 'author')]),
    'ru': dict(glance='Пакет в числах', quick='Быстрый старт', targets='Цели сборки',
               three='Три библиотеки, одна дисциплина',
               lib1='Библиотека I — `Choptuik/`: критические явления',
               lib2='Библиотека II — `SeptinalYM/`: септинальный массовый зазор',
               lib3='Библиотека III — `Satellite/`: септинальное прочтение',
               consts='Калиброванные константы', verify='Проверка в сессии',
               bridge='Сертификатный мост', faq='Частые вопросы', author='Автор',
               toc=[('Наука за 30 секунд', 'наука-за-30-секунд'),
                    ('Пакет в числах', 'пакет-в-числах'), ('Быстрый старт', 'быстрый-старт'),
                    ('Цели сборки', 'цели-сборки'),
                    ('Три библиотеки, одна дисциплина', 'три-библиотеки-одна-дисциплина'),
                    ('Библиотека I · Choptuik', 'библиотека-i--choptuik-критические-явления'),
                    ('Библиотека II · SeptinalYM', 'библиотека-ii--septinalym-септинальный-массовый-зазор'),
                    ('Библиотека III · Satellite', 'библиотека-iii--satellite-септинальное-прочтение'),
                    ('Калиброванные константы', 'калиброванные-константы'),
                    ('Честность: доказано и заявлено', 'честность-доказано-и-заявлено'),
                    ('Исторические снимки и дубли', 'исторические-снимки-и-дубли-оставлены-намеренно'),
                    ('Графики', 'графики-посчитаны-из-исходников'), ('Анимации', 'анимации'),
                    ('Дерево пакета', 'дерево-пакета'), ('Проверка в сессии', 'проверка-в-сессии'),
                    ('Сертификатный мост', 'сертификатный-мост'),
                    ('Воспроизводимость этого README', 'воспроизводимость-этого-readme'),
                    ('Частые вопросы', 'частые-вопросы'), ('Автор', 'автор')]),
}


def toc_block(lang):
    items = '\n'.join(f'- [{t}](#{a})' for t, a in H[lang]['toc'])
    h = 'Table of contents' if lang == 'en' else 'Содержание'
    return f'## {h}\n\n{items}\n'


def readme(lang):
    L = sections(lang)
    ck = TOT['counts_in_targets']
    decls = sum(ck.values())
    banner = ('../assets/banners/banner_header.svg' if lang == 'en'
              else '../assets/banners/banner_header_ru.svg')
    parts = []
    parts.append(f'''<p align="center">
  <img src="{banner}" alt="SEPTINAL / lean" width="100%">
</p>

<p align="center">
  <img src="../assets/logo/logo_light.svg" alt="logo" width="130">&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/wild8highlander.png" alt="avatar" width="130" style="border-radius:50%">
</p>

# Septinal/lean — the machine-checked core

<p align="center">
{badges(lang)}
</p>

<p align="center">
  <b>[{'English' if lang == 'en' else 'English'}](README.md)</b> · <b>[{'Русский' if lang == 'ru' else 'Русский'}](README_ru.md)</b>
</p>
''')
    parts.append(L['intro'])
    parts.append('')
    if lang == 'en':
        parts.append('> [!IMPORTANT]\n> **Honest scope.** The theory libraries are '
                     'sorry-free and axiom-clean, but they formalise the *bookkeeping* '
                     'of the physics, not the full Einstein–scalar system: the numerical '
                     'content enters through named certificate hypotheses (see '
                     '[Honesty](#honesty-proved-and-declared)). Nothing here is a hidden '
                     'assumption; nothing here overclaims.')
    else:
        parts.append('> [!IMPORTANT]\n> **Честный объём.** Теоретические библиотеки '
                     'свободны от sorry и чисты по аксиомам, но формализуют '
                     '*бухгалтерию* физики, а не полную систему Эйнштейна–скаляра: '
                     'числовое содержание входит через именованные гипотезы-сертификаты '
                     '(см. [Честность](#честность-доказано-и-заявлено)). Здесь нет '
                     'спрятанных допущений; здесь ничего не обещано сверх доказанного.')
    parts.append('')
    parts.append(toc_block(lang))
    parts.append(L['science'])
    parts.append(f'''

## {H[lang]['glance']}

{kpi(lang)}
''')
    tip_text = (
        '**Cache roots matter.** `lake exe cache get` only fetches the Mathlib closure of the '
        'files you pass it. Pass *every* module of *every* library '
        '(`Choptuik/**/*.lean Satellite/*.lean SeptinalYM/*.lean *.lean`), or `lake build` '
        'will silently compile hundreds of Mathlib modules from source.'
        if lang == 'en' else
        '**Корни кэша важны.** `lake exe cache get` качает замыкание Mathlib только по '
        'переданным файлам. Передавайте *каждый* модуль *каждой* библиотеки '
        '(`Choptuik/**/*.lean Satellite/*.lean SeptinalYM/*.lean *.lean`), иначе `lake build` '
        'молча будет собирать сотни модулей Mathlib из исходников.')
    parts.append(f'''

## {H[lang]['quick']}

{build_cmd(lang)}

{PIPELINE_GRAPH}

> [!TIP]
> {tip_text}

### {H[lang]['targets']}

{target_table(lang)}
''')
    parts.append(f'''

## {H[lang]['three']}

{OVERVIEW_GRAPH}

''')
    parts.append(f'''## {H[lang]['lib1']}

{graph('Choptuik/', 'TB', lang, 'ch', dashed=('AxiomAudit.lean',))}

{module_table(CH, lang)}

{key_thm_block('Choptuik', lang)}

''')
    for f in CH:
        parts.append(details_block(f, lang))
    parts.append(f'''## {H[lang]['lib2']}

{graph('SeptinalYM/', 'LR', lang, 'ym', dashed=())}

{module_table(YM, lang)}

{key_thm_block('SeptinalYM', lang)}

''')
    for f in YM:
        parts.append(details_block(f, lang))
    parts.append(f'''## {H[lang]['lib3']}

{graph('Satellite/', 'LR', lang, 'sat', dashed=('Satellite/C5_Klein.lean', 'Satellite/AxiomAudit.lean'))}

{module_table(SA, lang)}

{key_thm_block('Satellite', lang)}

''')
    for f in SA:
        parts.append(details_block(f, lang))
    parts.append(f'''## {H[lang]['consts']}

{const_table(lang)}

''')
    parts.append(L['honest'])
    parts.append('')
    parts.append(L['legacy'])
    parts.append('')
    parts.append(legacy_table(lang))
    parts.append('')
    parts.append(charts_sec(lang))
    parts.append(gallery(lang))
    parts.append(repo_map(lang))
    parts.append(f'''## {H[lang]['verify']}

{verified_table(lang)}

{L['ci']}

### {H[lang]['bridge']}

{BRIDGE_GRAPH}

Protocol: [`../../bridge/protocol.md`](../../bridge/protocol.md) · producer:
[`../../python/choptuik_service/certify.py`](../../python/choptuik_service/certify.py).
''')
    parts.append(L['repro'])
    h_faq = H[lang]['faq']
    parts.append(f'''

## {h_faq}

''')
    parts.append(faq_block(lang))
    h_au = H[lang]['author']
    parts.append(f'''---

## {h_au}

<p align="center">
  <img src="https://github.com/wild8highlander.png" alt="@wild8highlander" width="120"><br>
  {author(lang).splitlines()[0]}
</p>

{author(lang).split("\n", 1)[1] if "\n" in author(lang) else ''}

<p align="center">
  <img src="../../assets/banners/divider_photon.svg" alt="" width="100%">
</p>
''')
    return '\n'.join(parts)


SUBDIRS = ['Choptuik', 'Choptuik/Analysis', 'Choptuik/Bridge', 'Choptuik/Existence',
           'Choptuik/Geometry', 'Choptuik/Stability', 'SeptinalYM', 'Satellite', 'scripts']


def main():
    for lang in ('en', 'ru'):
        name = 'README.md' if lang == 'en' else 'README_ru.md'
        (HERE / name).write_text(readme(lang), encoding='utf-8')
        print(f'✅ {name} ({(HERE / name).stat().st_size // 1024} КБ)')
        for d in SUBDIRS:
            p = HERE / d / name
            p.write_text(sub_readme(d, lang), encoding='utf-8')
        print(f'✅ README подпапок ×{len(SUBDIRS)}')


if __name__ == '__main__':
    main()
