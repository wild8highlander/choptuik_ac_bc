# -*- coding: utf-8 -*-
"""
make_animations.py — 3 launch animations x RU/EN (GIF + MP4).

  anim_01_gap   — the quadratic opening of the Floquet gap;
  anim_02_trap  — the trio: free escape vs the sealed trap;
  anim_03_wu    — the Wu door: asymmetric annihilation of pairs.

Reads committed data only (plus one live single-trial trio run for the
trajectory panel).  ffmpeg is used for MP4; GIF via PillowWriter.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

from figstyle import TOKENS, LANG, style

DATA = os.path.join(ROOT, "data", "qhb")
OUT = os.path.join(ROOT, "animations")
DPI = 90


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------
def anim_gap(lang, theme, path_base):
    tok = style(theme)
    L = LANG[lang]
    d = load("gap_scan_window.json")
    b = np.array(d["beta"])
    g = np.array(d["gap"])
    d0, B2 = g[0], d["B2"]
    wing_b = np.array(d["wing_betas"])
    wing_s = np.array(d["wing_shifts"])

    fig = plt.figure(figsize=(7.2, 4.6), constrained_layout=True)
    ax = fig.gca()
    bw = np.linspace(0, 0.8, 200)
    ax.plot(bw, d0 + B2 * bw ** 2, "-", lw=1.2, color=tok["grid"])
    ax.plot(wing_b, d0 + wing_s, "s", ms=3, color=tok["grid"])
    (pt,) = ax.plot([], [], "o", ms=9, color=tok["gold"])
    (law,) = ax.plot([], [], "-", lw=2.0, color=tok["ink"])
    txt = ax.text(0.03, 0.9, "", transform=ax.transAxes, fontsize=12,
                  color=tok["ink"])
    ax.set_xlim(0, 0.82)
    ax.set_ylim(d0 - 0.012, d0 + 0.006)
    ax.set_xlabel(L["gap_x"])
    ax.set_ylabel(L["gap_y"])
    ax.set_title(L["gap_title"], fontsize=12)
    frames = list(zip(b, g))

    def update(k):
        beta, gap = frames[k]
        kk = max(k, 1)
        law.set_data(b[:kk + 1], d0 + B2 * b[:kk + 1] ** 2)
        pt.set_data([beta], [gap])
        txt.set_text(f"$\\beta$ = {beta:.3f}   "
                     f"$\\Delta_F-\\Delta_0$ = {gap - d0:+.2e}")
        return pt, law, txt

    ani = FuncAnimation(fig, update, frames=len(frames), blit=False)
    save(ani, fig, path_base, len(frames), 12)
    plt.close(fig)


# ----------------------------------------------------------------------------
def anim_trap(lang, theme, path_base):
    tok = style(theme)
    L = LANG[lang]
    from engine.solver import make_ensemble, trio_run
    pos0, vel0, rej = make_ensemble(1, seed=20261010 + 7)
    r_free = trio_run(pos0, vel0, V0=0.0, record_every=25)
    r_trap = trio_run(pos0, vel0, V0=8.0, Omega=2.0, record_every=25)
    tf = r_free["traj"]
    tt = r_trap["traj"]

    fig = plt.figure(figsize=(9.6, 4.8), constrained_layout=True)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    for ax, ttl in ((ax1, L["trap_free"]), (ax2, "V$_0$ = 8, $\\Omega$ = 2")):
        ax.set_xlim(-12.5, 12.5)
        ax.set_ylim(-12.5, 12.5)
        ax.set_aspect("equal")
        ax.set_title(ttl, fontsize=10.5)
        ax.tick_params(labelsize=7)
        for rr in (8.0,):
            th = np.linspace(0, 2 * np.pi, 100)
            ax.plot(rr * np.cos(th), rr * np.sin(th), ls="--", lw=1,
                    color=tok["gold"], alpha=0.6)
    colors = (tok["gold"], tok["ink"], tok["muted"])
    lines = [ax1.plot([], [], "-", lw=0.8, alpha=0.7, color=c)[0]
             for c in colors]
    dots = [ax1.plot([], [], "o", ms=5, color=c)[0] for c in colors]
    lines2 = [ax2.plot([], [], "-", lw=0.8, alpha=0.7, color=c)[0]
              for c in colors]
    dots2 = [ax2.plot([], [], "o", ms=5, color=c)[0] for c in colors]

    def update(k):
        out = []
        for i in range(3):
            lines[i].set_data(tf[:k + 1, 0, i, 0], tf[:k + 1, 0, i, 1])
            dots[i].set_data([tf[k, 0, i, 0]], [tf[k, 0, i, 1]])
            lines2[i].set_data(tt[:k + 1, 0, i, 0], tt[:k + 1, 0, i, 1])
            dots2[i].set_data([tt[k, 0, i, 0]], [tt[k, 0, i, 1]])
        return out

    n = min(len(tf), len(tt))
    ani = FuncAnimation(fig, update, frames=n, blit=False)
    save(ani, fig, path_base, n, 20)
    plt.close(fig)


# ----------------------------------------------------------------------------
def anim_wu(lang, theme, path_base):
    tok = style(theme)
    L = LANG[lang]
    rng = np.random.default_rng(20261010)
    alpha = 0.9
    n = 400
    # particle fountain: species +/- as dots; asymmetric annihilation
    fig = plt.figure(figsize=(7.2, 4.6), constrained_layout=True)
    ax = fig.gca()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    title = ax.text(5, 5.6, L["wu_title"], ha="center", fontsize=12,
                    color=tok["ink"])
    plus = [[], []]
    minus = [[], []]

    def draw(frame):
        for c in list(ax.lines) + list(ax.collections):
            c.remove()
        alive_p = [[], []]
        alive_m = [[], []]
        for j in range(frame + 1):
            x0 = 5
            y0 = 0.4
            # born pair j
            t_age = frame - j
            # survival: species - annihilates faster (1+alpha)
            if rng.random() < math.exp(-0.010 * (1 - alpha) * t_age):
                alive_p[0].append(x0 + 0.4 + 0.02 * j)
                alive_p[1].append(y0 + min(4.5, 0.12 * t_age))
            if rng.random() < math.exp(-0.010 * (1 + alpha) * t_age):
                alive_m[0].append(x0 - 0.4 - 0.02 * j)
                alive_m[1].append(y0 + min(4.5, 0.12 * t_age))
        ax.scatter(alive_p[0], alive_p[1], s=26, color=tok["gold"],
                   marker="o", label="e$^+$ (matter)")
        ax.scatter(alive_m[0], alive_m[1], s=26, color=tok["ink"],
                   marker="s", label="e$^-$")
        np_, nm = len(alive_p[0]), len(alive_m[0])
        r = (np_ - nm) / max(np_ + nm, 1)
        ax.text(5, 5.05, f"$N_+$ = {np_}   $N_-$ = {nm}   "
                         f"$r$ = {r:+.3f}", ha="center", fontsize=11,
                color=tok["ink"])
        ax.legend(loc="upper left", fontsize=8, framealpha=0.0)
        return []

    ani = FuncAnimation(fig, draw, frames=60, blit=False)
    save(ani, fig, path_base, 60, 14)
    plt.close(fig)


# ----------------------------------------------------------------------------
def save(ani, fig, path_base, n_frames, fps):
    gif = path_base + ".gif"
    mp4 = path_base + ".mp4"
    try:
        ani.save(gif, writer=PillowWriter(fps=fps), dpi=DPI)
    except Exception as exc:
        print(f"GIF failed for {path_base}: {exc}")
    try:
        ani.save(mp4, writer=FFMpegWriter(fps=fps, bitrate=1800), dpi=DPI)
    except Exception as exc:
        print(f"MP4 failed for {path_base}: {exc}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    builders = {"anim_01_gap": anim_gap, "anim_02_trap": anim_trap,
                "anim_03_wu": anim_wu}
    only = args.only.split(",") if args.only else list(builders)
    for lang in ("en", "ru"):
        out_dir = os.path.join(OUT, lang)
        os.makedirs(out_dir, exist_ok=True)
        for name in only:
            builders[name](lang, "light", os.path.join(out_dir, name))
            print(f"built {lang}/{name} (gif+mp4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
