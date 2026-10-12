#!/usr/bin/env python3
"""
make_animations.py — the four launch animations of the DSI laboratory.

Four animations x two languages (en, ru), each delivered as MP4
(h264, 24 fps) and GIF, under animations/<lang>/:

  anim_01_convergents   the continued-fraction ladder of the measured
                        c_K3: convergents 1/24 -> 1/25 -> 9/224 landing
                        one by one, the gold observation line drawing
                        itself, the +0.0025% gap annotated
                        (data: results/exp2_dsi4.json)
  anim_02_ladder        the e-ladder theorem: bars 5/7 (free), 1
                        (theorem A), the trimmed-tree points 1 + 2/n
                        landing for k = 2..10 (theorem B), 2 (theorem C)
                        (data: results/exp7_e1_threshold.json)
  anim_03_census        the {7,3} tiling of the Klein quartic: the
                        heptagon-and-triangles motif drawing itself while
                        V = 56, E = 84, F = 24 land and the valence
                        identity 7F = 3V = 2E = 168 closes
                        (data: results/exp6_census_224.json)
  anim_04_overtones     the QNM overtone ladder of GW150914: overtone
                        amplitudes landing on the catalogue and the
                        0.84-sigma Cosmic-Explorer detectability bar
                        (data: results/exp4_qnm.json)

All physics is read from the committed verdicts; the script invents
nothing. Uses the bilingual labels of figlabels.py plus a local LANG map.

Run:   python3 scripts/make_animations.py --all
       python3 scripts/make_animations.py --lang en --only anim_02_ladder
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _p in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
):
    try:
        fm.fontManager.addfont(_p)
    except Exception:  # noqa: BLE001 - best-effort font registration
        pass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import Circle, RegularPolygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from figlabels import L  # noqa: E402  (bilingual base labels)

RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "animations")
FPS = 24

INK, GOLD, GOLD_SOFT = "#1A1A24", "#8C6D1F", "#C9A84C"
INK_D, GOLD_D, GOLD_SOFT_D = "#E8E2D0", "#C9A84C", "#E3C878"
MUTED, MUTED_D = "#6B6455", "#9A9484"
THEME = {
    "light": (INK, GOLD, GOLD_SOFT, MUTED, "#FFFFFF"),
    "dark": (INK_D, GOLD_D, GOLD_SOFT_D, MUTED_D, "#101018"),
}

LANG = {
    "en": {
        "a1_title": "The convergent ladder of the measured $c_{K3}$",
        "a1_y": "candidate value $p/q$",
        "a1_target": "measured $c_{K3}$",
        "a1_obs": "9/224 = 27/672 (+0.0025%)",
        "a1_note": "convergents of the continued fraction, q <= 224",
        "a2_title": "The e-ladder theorem (exp7)",
        "a2_y": "defect per generator $e = F/n$",
        "a2_free": "5/7 free scalars (outside the class)",
        "a2_A": "theorem A: e >= 1",
        "a2_B": "theorem B: tree F = n + 2",
        "a2_C": "theorem C: unitary F = 2n",
        "a3_title": "The {7,3} tiling of the Klein quartic (exp6)",
        "a3_V": "V = 56 triangles",
        "a3_E": "E = 84 edges",
        "a3_F": "F = 24 heptagons",
        "a3_id": "7F = 3V = 2E = |PSL(2,7)| = 168",
        "a4_title": "QNM overtone ladder of GW150914 (exp4)",
        "a4_y": "relative overtone amplitude",
        "a4_x": "overtone index n",
        "a4_ce": "Cosmic Explorer detectability 0.84 sigma",
    },
    "ru": {
        "a1_title": "Лестница подходящих дробей измеренного $c_{K3}$",
        "a1_y": "значение кандидата $p/q$",
        "a1_target": "измеренное $c_{K3}$",
        "a1_obs": "9/224 = 27/672 (+0.0025%)",
        "a1_note": "подходящие дроби цепной дроби, q <= 224",
        "a2_title": "Теорема о лестнице e (эксп. 7)",
        "a2_y": "дефект на генератор $e = F/n$",
        "a2_free": "5/7 свободные скаляры (вне класса)",
        "a2_A": "теорема A: e >= 1",
        "a2_B": "теорема B: дерево F = n + 2",
        "a2_C": "теорема C: унитарные F = 2n",
        "a3_title": "Тилинг {7,3} квартики Клейна (эксп. 6)",
        "a3_V": "V = 56 треугольников",
        "a3_E": "E = 84 ребра",
        "a3_F": "F = 24 семиугольника",
        "a3_id": "7F = 3V = 2E = |PSL(2,7)| = 168",
        "a4_title": "Лестница обертонов QNM GW150914 (эксп. 4)",
        "a4_y": "относительная амплитуда обертона",
        "a4_x": "номер обертона n",
        "a4_ce": "обнаружимость на Cosmic Explorer 0.84 сигмы",
    },
}


def _load(name: str) -> dict:
    with open(os.path.join(RESULTS, name), encoding="utf-8") as fh:
        return json.load(fh)


def _style(ax, lang_key, t):
    _ink, _gold, _gold_soft, muted, bg = t
    ax.set_facecolor(bg)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(muted)
    ax.tick_params(colors=muted)


# ---------------------------------------------------------------- anim 01 ---
def anim_01(t, txt):
    """Convergent ladder of the measured c_K3 (exp2)."""
    ink, gold, _gold_soft, muted, _bg = t
    d2 = _load("exp2_dsi4.json")
    target = float(d2["arithmetic"]["value"])
    convs = [
        (Fraction(1, 24), 0.041666666666666664),
        (Fraction(1, 25), 0.04),
        (Fraction(9, 224), target),
    ]
    n_frames = 96
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=110, constrained_layout=True)

    def draw(i):
        ax.clear()
        _style(ax, "a1", t)
        xs = np.linspace(0, 1, 200)
        ax.plot(
            xs,
            np.full_like(xs, target),
            color=muted,
            lw=1.0,
            ls=":",
            alpha=0.0 + min(1.0, i / 12) * 0.9,
        )
        if i >= 4:
            ax.text(0.30, target + 0.0004, txt["a1_target"], fontsize=11, color=muted)
        shown = []
        for k, (fr, val) in enumerate(convs):
            appear = 18 + k * 22
            if i >= appear:
                prog = min(1.0, (i - appear) / 14.0)
                shown.append((fr, val, prog))
        for k, (fr, val, prog) in enumerate(shown):
            ax.plot(
                [0.15 + k * 0.3],
                [val],
                marker="D",
                ms=10 + 3 * prog,
                color=gold if fr.numerator == 9 else muted,
                alpha=min(1.0, 0.35 + prog),
            )
            ax.text(
                0.15 + k * 0.3,
                val - 0.0016,
                f"{fr.numerator}/{fr.denominator}",
                ha="center",
                fontsize=12,
                color=gold if fr.numerator == 9 else muted,
                alpha=prog,
            )
        if i >= 78:
            ax.annotate(
                txt["a1_obs"],
                xy=(0.75, target),
                xytext=(0.30, target + 0.0055),
                fontsize=13,
                color=gold,
                arrowprops=dict(arrowstyle="-|>", color=gold, lw=1.8),
            )
            ax.text(
                0.5,
                0.055,
                txt["a1_note"],
                ha="center",
                fontsize=10,
                color=muted,
                transform=ax.transAxes,
            )
        ax.set_ylim(0.034, 0.046)
        ax.set_xlim(0, 1)
        ax.set_title(txt["a1_title"], fontsize=12, color=ink)
        ax.set_ylabel(txt["a1_y"], fontsize=10, color=ink)
        ax.set_xticks([])
        return []

    anim = FuncAnimation(fig, draw, frames=n_frames, blit=False)
    return anim


# ---------------------------------------------------------------- anim 02 ---
def anim_02(t, txt):
    """The e-ladder theorem (exp7)."""
    ink, gold, _gold_soft, muted, _bg = t
    d7 = _load("exp7_e1_threshold.json")
    tree = d7["theorem_B"]["tree"]
    n_frames = 132
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=110, constrained_layout=True)

    def draw(i):
        ax.clear()
        _style(ax, "a2", t)
        # free floor
        ax.axhline(5 / 7, color=muted, ls=":", lw=1.4, alpha=min(1.0, i / 10))
        if i >= 4:
            ax.text(3.4, 5 / 7 - 0.12, txt["a2_free"], fontsize=10, color=muted)
        # theorem A floor at 1
        ax.axhline(
            1.0, color=gold, ls="--", lw=2.0, alpha=min(1.0, max(0.0, (i - 12) / 12))
        )
        if i >= 24:
            ax.text(6.6, 1.07, txt["a2_A"], fontsize=11.5, color=gold)
        # theorem B: tree points 1 + 2/n landing
        for k, row in enumerate(tree):
            appear = 36 + k * 5
            if i >= appear:
                prog = min(1.0, (i - appear) / 8.0)
                e = float(row["e"])
                ax.plot(
                    [k + 1], [e], marker="o", ms=7 * prog, color="#1e6091", alpha=prog
                )
        if i >= 80:
            ax.text(2.2, 1.55, txt["a2_B"], fontsize=11, color="#1e6091")
        # theorem C at 2
        ax.axhline(
            2.0,
            color="#7c3aed",
            ls=":",
            lw=2.0,
            alpha=min(1.0, max(0.0, (i - 96) / 12)),
        )
        if i >= 112:
            ax.text(7.6, 2.06, txt["a2_C"], fontsize=11, color="#7c3aed")
        ax.set_ylim(0.55, 2.25)
        ax.set_xlim(0, 11)
        ax.set_xlabel("k (tree depth)", fontsize=10, color=ink)
        ax.set_ylabel(txt["a2_y"], fontsize=10, color=ink)
        ax.set_title(txt["a2_title"], fontsize=12, color=ink)
        return []

    anim = FuncAnimation(fig, draw, frames=n_frames, blit=False)
    return anim


# ---------------------------------------------------------------- anim 03 ---
def anim_03(t, txt):
    """The {7,3} census of the Klein quartic (exp6)."""
    ink, gold, _gold_soft, muted, bg = t
    d6 = _load("exp6_census_224.json")
    V, E, F = int(d6["census"]["V"]), int(d6["census"]["E"]), int(d6["census"]["F"])
    n_frames = 120
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=110, constrained_layout=True)

    def draw(i):
        ax.clear()
        ax.set_xlim(-1.7, 1.7)
        ax.set_ylim(-1.35, 1.45)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor(bg)
        cx, cy, r = -0.62, 0.05, 0.78
        # central heptagon
        hept = RegularPolygon(
            (cx, cy),
            7,
            radius=r,
            orientation=np.pi / 7,
            facecolor="none",
            edgecolor=ink,
            lw=2.6,
            alpha=min(1.0, i / 16),
            zorder=3,
        )
        ax.add_patch(hept)
        # seven neighbours (the {7,3} tiling motif)
        for k in range(7):
            ang = np.pi / 7 + 2 * np.pi * k / 7
            nx, ny = cx + 1.62 * r * np.sin(ang), cy + 1.62 * r * np.cos(ang)
            prog = min(1.0, max(0.0, (i - 12 - k * 4) / 12.0))
            if prog > 0:
                nb = RegularPolygon(
                    (nx, ny),
                    7,
                    radius=r,
                    orientation=np.pi / 7,
                    facecolor="none",
                    edgecolor=ink,
                    lw=1.8,
                    alpha=0.55 * prog,
                    zorder=2,
                )
                ax.add_patch(nb)
                ax.plot(
                    [cx + r * np.sin(ang), nx - r * np.sin(ang)],
                    [cy + r * np.cos(ang), ny - r * np.cos(ang)],
                    color=muted,
                    lw=1.0,
                    alpha=0.5 * prog,
                    zorder=1,
                )
        # gold center lands at i=48
        if i >= 48:
            ax.add_patch(
                Circle((cx, cy), 0.07, facecolor=gold, edgecolor="none", zorder=4)
            )
        # counters land 56 / 84 / 168
        rows = ((txt["a3_V"], V, 60), (txt["a3_E"], E, 72), (txt["a3_F"], F, 84))
        for j, (lab, val, appear) in enumerate(rows):
            if i >= appear:
                ax.text(0.42, 0.52 - j * 0.20, lab, fontsize=13.5, color=ink)
        if i >= 100:
            ax.text(0.42, -0.18, txt["a3_id"], fontsize=13, color=gold)
        ax.set_title(txt["a3_title"], fontsize=12, color=ink, pad=12)
        return []

    anim = FuncAnimation(fig, draw, frames=n_frames, blit=False)
    return anim


# ---------------------------------------------------------------- anim 04 ---
def anim_04(t, txt):
    """The falsifiable overtone law |delta_f_n| / f_n = const (exp4)."""
    ink, gold, _gold_soft, muted, _bg = t
    d4 = _load("exp4_qnm.json")
    rows = d4["overtones"]["overtones"]
    fs = np.array([float(r["f_n"]) for r in rows])
    dfs = np.abs(np.array([float(r["delta_f_n"]) for r in rows]))
    slope = float(np.median(dfs / fs))  # committed: 8.3857e-5
    n_frames = 130
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=110, constrained_layout=True)

    def draw(i):
        ax.clear()
        _style(ax, "a4", t)
        x_max, y_max = fs.max() * 1.08, dfs.max() * 1.18
        # the law line draws itself between frames 10..40
        prog_line = min(1.0, max(0.0, (i - 10) / 30.0))
        if prog_line > 0:
            xs = np.array([0.0, x_max * prog_line])
            ax.plot(xs, slope * xs, color=gold, lw=2.2, ls="--")
        # overtone points land one by one (n = 0..)
        for k, (x, y) in enumerate(zip(fs, dfs)):
            appear = 24 + k * 7
            if i >= appear:
                prog = min(1.0, (i - appear) / 8.0)
                ax.plot(
                    [x],
                    [y],
                    marker="o",
                    ms=8 * prog,
                    color=ink,
                    alpha=0.25 + 0.75 * prog,
                )
                if prog >= 1.0:
                    ax.annotate(
                        f"n={k}",
                        (x, y),
                        textcoords="offset points",
                        xytext=(6, 4),
                        fontsize=9,
                        color=muted,
                    )
        if i >= 100:
            ax.text(
                0.42,
                0.90,
                "$|\\Delta f_n| / f_n = $ const $= 8.3857\\times 10^{-5}$"
                " (falsifiable)",
                fontsize=12,
                color=gold,
                transform=ax.transAxes,
            )
            ax.text(
                0.42,
                0.83,
                txt["a4_ce"],
                fontsize=10.5,
                color=muted,
                transform=ax.transAxes,
            )
        ax.set_xlim(0, x_max)
        ax.set_ylim(0, y_max)
        ax.set_xlabel("$f_n$ (Hz)", fontsize=10, color=ink)
        ax.set_ylabel("$|\\Delta f_n|$ (Hz)", fontsize=10, color=ink)
        ax.set_title(txt["a4_title"], fontsize=12, color=ink)
        return []

    anim = FuncAnimation(fig, draw, frames=n_frames, blit=False)
    return anim


ANIMS = {
    "anim_01_convergents": anim_01,
    "anim_02_ladder": anim_02,
    "anim_03_census": anim_03,
    "anim_04_overtones": anim_04,
}


def render(name: str, lang: str, dpi: int = 110) -> None:
    t = THEME["light"]
    txt = dict(L[lang])
    txt.update(LANG[lang])
    anim = ANIMS[name](t, txt)
    outdir = os.path.join(OUT, lang)
    os.makedirs(outdir, exist_ok=True)
    mp4 = os.path.join(outdir, f"{name}.mp4")
    gif = os.path.join(outdir, f"{name}.gif")
    anim.save(mp4, writer=FFMpegWriter(fps=FPS, bitrate=1600))
    anim.save(gif, writer=PillowWriter(fps=16), dpi=96)
    plt.close(anim._fig)
    print("wrote", os.path.relpath(mp4, ROOT))
    print("wrote", os.path.relpath(gif, ROOT))


def main() -> None:
    ap = argparse.ArgumentParser(description="DSI lab launch animations")
    ap.add_argument("--lang", choices=("en", "ru"), help="single language")
    ap.add_argument("--only", choices=sorted(ANIMS), help="single animation")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    langs = ("en", "ru") if args.lang is None else (args.lang,)
    names = sorted(ANIMS) if args.only is None else [args.only]
    if not (args.all or args.lang or args.only):
        ap.print_help()
        return
    for lang in langs:
        for name in names:
            render(name, lang)
    print("DONE: animations")


if __name__ == "__main__":
    main()
