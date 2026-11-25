#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_gif.py — GIF «lake build» для README: терминальная анимация реального
вывода lake (цепочка SeptinalYM.Stage4d, 9 модулей), тёмная тема пакета.
Выход: docs/assets/gifs/build_chain.gif
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parents[1]
OUT = HERE / 'docs' / 'assets' / 'gifs'
OUT.mkdir(parents=True, exist_ok=True)

MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
MONO_B = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
W, H, PAD, LH = 880, 420, 26, 22
BG = '#0F172A'
FG = '#E2E8F0'
DIM = '#64748B'
OK = '#34D399'
INFO = '#93C5FD'
TITLE = '#F8FAFC'

f = ImageFont.truetype(MONO, 15)
fb = ImageFont.truetype(MONO_B, 16)

steps = [
    'Septinal/lean $ lake build SeptinalYM.Stage4d',
    'info: SeptinalYM.Basic: building',
    'info: SeptinalYM.MatrixAux: building',
    'info: SeptinalYM.JW: building',
    'info: SeptinalYM.Fourier: building',
    'info: SeptinalYM.Slater: building',
    'info: SeptinalYM.SlaterDiag: building',
    'info: SeptinalYM.Stage4c: building',
    'info: SeptinalYM.Stage4d: building',
]
built = [
    '✔ [1/9] Built SeptinalYM.Basic          (135 lines)',
    '✔ [2/9] Built SeptinalYM.MatrixAux      (376 lines)',
    '✔ [3/9] Built SeptinalYM.JW             (795 lines)',
    '✔ [4/9] Built SeptinalYM.Fourier        (194 lines)',
    '✔ [5/9] Built SeptinalYM.Slater         (343 lines)',
    '✔ [6/9] Built SeptinalYM.SlaterDiag     (1591 lines)',
    '✔ [7/9] Built SeptinalYM.Stage4c        (126 lines)',
    '✔ [8/9] Built SeptinalYM.Stage4d        (2710 lines)',
    '✔ [9/9] Built SeptinalYM.Stage4d.o',
]
tail = [
    'Build completed successfully.',
    '',
    'axiom audit : propext, Classical.choice, Quot.sound   — nothing else',
    'sorries     : 0            project axioms : 0',
    'lean-check  : ✔ ✔ ✔',
]

frames = []
maxlines = 1
seq = []
for i, s in enumerate(steps):
    seq.append(('run', s))
    seq.append(('done', built[i]))
seq += [('tail', t) for t in tail]

n_show = 0
for i in range(len(seq) + 2):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    # заголовок окна
    d.rounded_rectangle([0, 0, W, 44], 0, fill='#111827')
    for k, c in enumerate(('#EF4444', '#F59E0B', '#34D399')):
        d.ellipse([18 + k * 24, 15, 30 + k * 24, 27], fill=c)
    d.text((100, 13), 'lean 4 · v4.21.0 · mathlib v4.21.0 — Septinal/lean',
           font=fb, fill=DIM)
    y = 60
    shown = seq[:i]
    for kind, txt in shown:
        if kind == 'run':
            d.text((PAD, y), txt, font=f, fill=INFO)
        elif kind == 'done':
            d.text((PAD, y), txt, font=f, fill=OK)
        else:
            if txt:
                d.text((PAD, y), txt, font=f, fill=TITLE if 'successfully' in txt else FG)
        y += LH
        if y > H - 30:
            break
    # курсор
    if y < H - 30:
        d.rectangle([PAD, y + 2, PAD + 9, y + 16], fill=TITLE)
    frames.append(img)
    frames.append(img.copy())  # каждый шаг по 2 тика

frames[-1].save(OUT / 'build_chain.gif', save_all=True,
                append_images=frames[1:], duration=260, loop=0, optimize=True)
p = OUT / 'build_chain.gif'
print(f'✅ build_chain.gif ({p.stat().st_size // 1024} КБ, {len(frames)} кадров)')
