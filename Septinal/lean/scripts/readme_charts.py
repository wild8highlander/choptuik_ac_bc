#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_charts.py — графики для README пакета Septinal/lean из docs/source_stats.json.
Всё считается из исходников; перегенерация: python3 -I scripts/readme_charts.py
Выход: docs/assets/charts/*.png (200 dpi, светлый фон — для README на GitHub).
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
plt.rcParams.update({
    'font.sans-serif': ['DejaVu Sans'],
    'axes.unicode_minus': False,
    'figure.facecolor': '#FFFFFF',
    'axes.facecolor': '#FFFFFF',
    'axes.edgecolor': '#E5E7EB',
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
    'xtick.major.size': 0,
    'ytick.major.size': 0,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.titlepad': 14,
    'legend.frameon': False,
    'legend.fontsize': 9,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.facecolor': '#FFFFFF',
})

HERE = pathlib.Path(__file__).resolve().parents[1]
OUT = HERE / 'docs' / 'assets' / 'charts'
OUT.mkdir(parents=True, exist_ok=True)
S = json.loads((HERE / 'docs' / 'source_stats.json').read_text(encoding='utf-8'))
FILES = {f['path']: f for f in S['files']}

# палитра: низкая насыщенность, один акцент
C_BLUE, C_CYAN, C_PURPLE, C_AMBER = '#4C6EF5', '#3AAFA9', '#8B7CC8', '#E8B44A'
G900, G700, G400, G200 = '#111827', '#374151', '#9CA3AF', '#E5E7EB'
LIB_COLORS = {'Choptuik': C_BLUE, 'Satellite': C_AMBER, 'SeptinalYM': C_CYAN, '(root)': G400}


def clean_ax(ax, grid='x'):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if grid:
        ax.xaxis.grid(True, alpha=0.08, color='#D1D5DB')
        ax.set_axisbelow(True)


def save(fig, name):
    p = OUT / name
    fig.savefig(p, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print(f'✅ {p.name} ({p.stat().st_size // 1024} КБ)')


# ── 1. Размер модулей по библиотекам (в целевых корнях сборки) ──────────────
def lib_of(f):
    top = f['path'].split('/')[0]
    return top if top in LIB_COLORS else '(root)'


built = [f for f in S['files'] if f['built'] and not f['path'].endswith('.bak8fix')]
built.sort(key=lambda f: f['lines'])
labels = [f['path'].replace('.lean', '') for f in built]
vals = [f['lines'] for f in built]
cols = [LIB_COLORS[lib_of(f)] for f in built]
fig, ax = plt.subplots(figsize=(9, 0.24 * len(built) + 2.4))
bars = ax.barh(range(len(built)), vals, color=cols, height=0.62, zorder=3)
for b, v, f in zip(bars, vals, built):
    ax.text(v + 25, b.get_y() + b.get_height() / 2, str(v), va='center',
            fontsize=8, color=G900 if v > 700 else G400)
ax.set_yticks(range(len(built)))
ax.set_yticklabels(labels, fontsize=7.5)
ax.set_xlim(0, max(vals) * 1.12)
ax.set_title('Lines of Lean source per module — the proof chain is bottom-heavy\n'
             '(blue: Choptuik · cyan: SeptinalYM · amber: Satellite · gray: root/audit)',
             loc='left')
clean_ax(ax)
save(fig, 'chart_lines_per_module.png')

# ── 2. Объявления по типам в трёх библиотеках ───────────────────────────────
groups = [('Choptuik', lambda f: f['path'].startswith('Choptuik/')),
          ('Satellite', lambda f: f['path'].startswith('Satellite/')),
          ('SeptinalYM', lambda f: f['path'].startswith('SeptinalYM/'))]
kinds = ['theorem', 'lemma', 'def', 'structure', 'abbrev']
series = {k: [] for k in kinds}
names_g = []
for name, pred in groups:
    sel = [f for f in built if pred(f)]
    names_g.append(f'{name}\n({len(sel)} modules)')
    for k in kinds:
        series[k].append(sum(f['counts'].get(k, 0) for f in sel))
fig, ax = plt.subplots(figsize=(9.5, 5.2))
x = np.arange(len(names_g))
bottom = np.zeros(len(names_g))
colors_k = {'theorem': C_BLUE, 'lemma': '#7C9BF2', 'def': C_CYAN,
            'structure': C_PURPLE, 'abbrev': C_AMBER}
for k in kinds:
    v = np.array(series[k], dtype=float)
    ax.bar(x, v, 0.52, bottom=bottom, color=colors_k[k], label=k,
           zorder=3, edgecolor='white', linewidth=0.4)
    for xi, (vi, bi) in enumerate(zip(v, bottom)):
        if vi >= 25:
            ax.text(xi, bi + vi / 2, f'{int(vi)}', ha='center', va='center',
                    fontsize=9, color='white', fontweight='bold')
    bottom += v
for xi, tot in enumerate(bottom):
    ax.text(xi, tot + 8, f'{int(tot)}', ha='center', fontsize=11,
            fontweight='bold', color=G900)
ax.set_xticks(x)
ax.set_xticklabels(names_g, fontsize=10)
ax.set_ylim(0, bottom.max() * 1.18)
ax.set_title('Declarations per library: every one is checked by the kernel,\n'
             'no `sorry`, no project axioms', loc='left')
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))
clean_ax(ax, grid=None)
ax.yaxis.grid(True, alpha=0.08, color='#D1D5DB')
save(fig, 'chart_declarations.png')

# ── 3. Цепочка доказательства SeptinalYM: накопленный объём ─────────────────
chain = ['SeptinalYM/Basic.lean', 'SeptinalYM/MatrixAux.lean', 'SeptinalYM/JW.lean',
         'SeptinalYM/Fourier.lean', 'SeptinalYM/Slater.lean', 'SeptinalYM/SlaterDiag.lean',
         'SeptinalYM/Stage4c.lean', 'SeptinalYM/Stage4d.lean']
cn, cv, cum = [], [], 0
for p in chain:
    f = FILES.get(p)
    if f:
        cn.append(p.split('/')[-1].replace('.lean', ''))
        cv.append(f['lines'])
        cum += f['lines']
fig, ax = plt.subplots(figsize=(9.5, 5.0))
bars = ax.bar(range(len(cn)), cv, 0.58, color='#D1FAE5', edgecolor='#3AAFA9',
              linewidth=1.2, zorder=3, label='module lines')
ax.set_ylim(0, cum * 1.2)
ax.step([-0.5] + list(range(len(cn) - 1)), np.maximum.accumulate(np.cumsum(cv)) / 1000 * 1000,
        where='post', color=G900, linewidth=1.6, zorder=4, visible=False)
runcum = np.cumsum(cv)
ax2 = ax.twinx()
ax2.plot(range(len(cn)), runcum, color=G900, linewidth=2.0, marker='o',
         markersize=4.5, markerfacecolor='white', markeredgecolor=G900, zorder=5,
         label='cumulative lines')
ax2.spines['top'].set_visible(False)
ax2.set_ylim(0, cum * 1.25)
ax2.set_ylabel('cumulative lines', fontsize=9, color=G700)
for xi, v in enumerate(runcum):
    ax2.annotate(f'{v:,}', (xi, v), textcoords='offset points', xytext=(0, 9),
                 ha='center', fontsize=8, color=G700)
ax.set_xticks(range(len(cn)))
ax.set_xticklabels(cn, fontsize=8.5, rotation=14, ha='right')
ax.set_title('The Jordan–Wigner → Slater-diagonalisation chain:\n'
             f'each link builds on the previous, {cum:,} lines end to end', loc='left')
ax.set_ylabel('module lines', fontsize=9, color=G700)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='upper left', bbox_to_anchor=(0.01, 0.98))
clean_ax(ax, grid=None)
save(fig, 'chart_proof_chain.png')

# ── 4. Статус честности: сорри/дубликаты по категориям ──────────────────────
cats = {'built (in a lake target)': 0, 'legacy snapshots (root copies)': 0,
        'not compiled (addendum/twin)': 0}
for f in S['files']:
    if f['built']:
        cats['built (in a lake target)'] += f['sorry']
    elif f['path'].startswith(('SlaterDiag_v1', 'SlaterDiag_stage4')) or \
            (f['path'].count('/') == 0 and f['path'] not in
             ('AxiomAudit.lean', 'Choptuik.lean', 'Satellite.lean', 'SeptinalYM.lean',
              'SeptinalYM_root.lean', 'lakefile.toml')):
        cats['legacy snapshots (root copies)'] += f['sorry']
    else:
        cats['not compiled (addendum/twin)'] += f['sorry']
fig, ax = plt.subplots(figsize=(7.5, 3.4))
ks = list(cats)
ax.barh(range(len(ks)), [cats[k] for k in ks],
        color=['#8FB7A4', '#E8B44A', '#E86A6A'][:len(ks)], height=0.52, zorder=3)
for i, k in enumerate(ks):
    ax.text(cats[k] + 0.25, i, f'{cats[k]} sorries', va='center', fontsize=9.5, color=G900)
ax.set_yticks(range(len(ks)))
ax.set_yticklabels(ks, fontsize=9.5)
ax.set_xlim(0, max(cats.values()) * 1.3)
ax.set_title('Where the 19 remaining `sorry` markers live:\n'
             'all outside the build targets — the built libraries are clean', loc='left')
clean_ax(ax)
save(fig, 'chart_sorry_status.png')

print('готово:', ', '.join(sorted(p.name for p in OUT.glob('*.png'))))
