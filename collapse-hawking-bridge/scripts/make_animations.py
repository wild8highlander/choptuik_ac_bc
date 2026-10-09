#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_animations.py — the four launch animations of the bridge.

Four animations x two languages (en, ru), each delivered as MP4
(h264, 24 fps) and GIF, under animations/<lang>/:

  anim_01_evaporation   mass decay + Page curve with the travelling
                        entropy switch (uses chbridge.page curves and
                        the photon-only law M(t) = M0 (1 - t/tevap)^(1/3))
  anim_02_bifurcation   born bifurcation f~(eps) assembling point by
                        point, eps_half appearing at the end
  anim_03_slowdown      critical slowdown: v_qmax points landing, fit
                        line drawing, quantization note
  anim_04_floor_law     the floor law floor_M ~ 12/N with the three
                        committed floors landing one after another

All physics is read from the committed verdicts and the chbridge
package; the script invents nothing.

Run:   python3 scripts/make_animations.py --all
       python3 scripts/make_animations.py --lang en --only anim_02_bifurcation
"""
import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter  # noqa: E402

import figstyle as fs  # noqa: E402
from chbridge.hawking import PAGE_FRACTION  # noqa: E402

REF = os.path.join(ROOT, "campaigns", "reference")
DATA = os.path.join(ROOT, "data", "bridge")
OUT = os.path.join(ROOT, "animations")

FPS = 24

LANG = {
    "en": {
        "a1_title": "Evaporation and the Page transition",
        "a1_M": "black-hole mass  $M/M_0$",
        "a1_S": "radiation entropy  $S_{rad}/S_0$",
        "a1_t": "time  $t/t_{evap}$",
        "a1_page": "Page time  $0.6464\\,t_{evap}$",
        "a1_before": "hole dominates: information returns inward",
        "a1_after": "radiation dominates: entropy grows to $S_0$",
        "a2_title": "Born bifurcation $\\tilde f(\\varepsilon)$ (campaign C2)",
        "a2_y": "fraction of saturation  $\\tilde f(\\varepsilon)$",
        "a2_x": "distance from threshold  $\\varepsilon = A - A^*$",
        "a2_eps_half": "$\\varepsilon_{1/2} = 4.86\\times10^{-3}$",
        "a2_sat": "saturation  $\\tilde f = 1$",
        "a3_title": "Critical slowdown (campaign C2)",
        "a3_y": "peak time  $v_{qmax}$ (null coordinate of $q_{max}$)",
        "a3_x": "log-distance from threshold  $\\ln\\varepsilon$",
        "a3_fit": "fit $v = a + b\\ln\\varepsilon$,  $b=-0.0334$, $r^2=0.71$",
        "a3_quant": "40-snapshot sampling (instrument quantization)",
        "a4_title": "The floor law (campaigns C1 + C3b)",
        "a4_y": "resolved mass floor  $M_{floor}$ [code units]",
        "a4_x": "grid resolution  N",
        "a4_law": "1/N scaling: 12/N guide",
    },
    "ru": {
        "a1_title": "Испарение и переход Пейджа",
        "a1_M": "масса ЧД  $M/M_0$",
        "a1_S": "энтропия излучения  $S_{rad}/S_0$",
        "a1_t": "время  $t/t_{evap}$",
        "a1_page": "Время Пейджа  $0{,}6464\\,t_{evap}$",
        "a1_before": "доминирует дыра: информация возвращается внутрь",
        "a1_after": "доминирует излучение: энтропия растёт до $S_0$",
        "a2_title": "Бифуркация рождения $\\tilde f(\\varepsilon)$ (кампания C2)",
        "a2_y": "доля насыщения  $\\tilde f(\\varepsilon)$",
        "a2_x": "расстояние от порога  $\\varepsilon = A - A^*$",
        "a2_eps_half": "$\\varepsilon_{1/2} = 4{,}86\\times10^{-3}$",
        "a2_sat": "насыщение  $\\tilde f = 1$",
        "a3_title": "Критическое замедление (кампания C2)",
        "a3_y": "время пика  $v_{qmax}$ (координата $q_{max}$)",
        "a3_x": "лог-расстояние от порога  $\\ln\\varepsilon$",
        "a3_fit": "фит $v = a + b\\ln\\varepsilon$,  $b=-0{,}0334$, $r^2=0{,}71$",
        "a3_quant": "квантование: 40 снимков на прогон",
        "a4_title": "Закон пола (кампании C1 + C3b)",
        "a4_y": "разрешённый массовый пол  $M_{floor}$ [код. ед.]",
        "a4_x": "разрешение сетки  N",
        "a4_law": "скейлинг 1/N: ориентир 12/N",
    },
}


def _load(name):
    with open(os.path.join(REF, name)) as f:
        return json.load(f)


def _csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def _page_curve(member="mid"):
    rows = [r for r in _csv("page_curve_grid.csv") if r["member"] == member]
    tau = np.array([float(r["t_over_t_evap"]) for r in rows])
    S = np.array([float(r["S_rad_over_kB_norm"]) for r in rows])
    order = np.argsort(tau)
    return tau[order], S[order]


def _smooth(S, k=6):
    pad = np.r_[np.repeat(S[0], k), S, np.repeat(S[-1], k)]
    kern = np.hanning(2 * k + 1); kern /= kern.sum()
    return np.convolve(pad, kern, mode="same")[k:-k]


# ---------------------------------------------------------------------------
def anim_01(L, t):
    tau, S = _page_curve("mid")
    S = _smooth(S)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 6.0), dpi=110,
                                   constrained_layout=True,
                                   height_ratios=[1.0, 1.15])
    fig.patch.set_facecolor(t["bg"])
    for ax in (ax1, ax2):
        ax.set_facecolor(t["panel"])
        ax.grid(True, alpha=0.3, color=t["grid"])
        ax.tick_params(colors=t["ink"])
        for s in ax.spines.values():
            s.set_color(t["grid"])
    # panel 1: mass decay (photon-only law)
    ax1.plot(tau, (1 - tau) ** (1 / 3.0), color=t["muted"], lw=1.2, ls="--")
    (mline,) = ax1.plot([], [], color=t["ink"], lw=2.6)
    (mdot,) = ax1.plot([], [], "o", color=t["gold"], ms=11, zorder=6)
    ax1.set_xlim(0, 1); ax1.set_ylim(-0.04, 1.05)
    ax1.set_ylabel(L["a1_M"], color=t["ink"])
    ax1.set_title(L["a1_title"], color=t["ink"])
    # panel 2: radiation entropy
    ax2.plot(tau, S, color=t["muted"], lw=1.0, alpha=0.5)
    (sline,) = ax2.plot([], [], color=t["gold"], lw=2.8)
    ax2.axvline(PAGE_FRACTION, color=t["gold"], lw=1.4, ls="--", alpha=0.85)
    ax2.annotate(L["a1_page"], (PAGE_FRACTION, 0.34),
                 xytext=(PAGE_FRACTION - 0.52, 0.30), color=t["gold"],
                 fontsize=10,
                 arrowprops=dict(arrowstyle="->", color=t["gold"]))
    ax2.set_xlim(0, 1); ax2.set_ylim(0.28, 1.04)
    ax2.set_xlabel(L["a1_t"], color=t["ink"])
    ax2.set_ylabel(L["a1_S"], color=t["ink"])
    phase = ax2.text(0.03, 0.955, "", transform=ax2.transAxes,
                     fontsize=10, color=t["ink"], va="top")

    def draw(i):
        k = max(1, int(i / N_FRAMES * len(tau)))
        mline.set_data(tau[:k], (1 - tau[:k]) ** (1 / 3.0))
        mdot.set_data([tau[k - 1]], [(1 - tau[k - 1]) ** (1 / 3.0)])
        sline.set_data(tau[:k], S[:k])
        if tau[k - 1] < PAGE_FRACTION:
            phase.set_text(L["a1_before"])
        else:
            phase.set_text(L["a1_after"])
        return mline, mdot, sline, phase

    return fig, draw, len(tau) - 1


def anim_02(L, t):
    c2 = _load("c2_verdict.json")
    rows = sorted(c2["bifurcation"]["rows"], key=lambda r: -r["eps"])
    eps = np.array([r["eps"] for r in rows if r["sane"]])
    f = np.array([r["f_tilde"] for r in rows if r["sane"]])
    eh = c2["bifurcation"]["summary"]["eps_half"]
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=110,
                           constrained_layout=True)
    fig.patch.set_facecolor(t["bg"]); ax.set_facecolor(t["panel"])
    ax.grid(True, which="both", alpha=0.3, color=t["grid"])
    ax.tick_params(colors=t["ink"])
    for s in ax.spines.values():
        s.set_color(t["grid"])
    ax.axhline(1.0, color=t["muted"], lw=1.1, ls=":", alpha=0.9)
    ax.text(2.4e-4, 1.06, L["a2_sat"], fontsize=10, color=t["muted"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(7e-5, 0.6); ax.set_ylim(0.09, 1.8)
    ax.set_xlabel(L["a2_x"], color=t["ink"])
    ax.set_ylabel(L["a2_y"], color=t["ink"])
    ax.set_title(L["a2_title"], color=t["ink"])
    scat = ax.scatter([], [], s=52, color=t["ink"], zorder=5)
    vline = ax.axvline(eh, color=t["gold"], lw=1.7, ls="--", alpha=0.0)
    txt = ax.annotate("", (eh, 0.24), xytext=(eh * 3.2, 0.19), color=t["gold"],
                      fontsize=11,
                      arrowprops=dict(arrowstyle="->", color=t["gold"],
                                      alpha=0.0))
    ax.annotate(L["a2_eps_half"], (eh, 0.30), xytext=(eh * 3.2, 0.19),
                color=t["gold"], fontsize=11, alpha=0.0)
    label = ax.text(0.5, 0.955, "", transform=ax.transAxes, ha="center",
                    fontsize=12, color=t["gold"])

    def draw(i):
        n_pts = max(1, min(len(eps), int(i / (N_FRAMES * 0.75) * len(eps)) + 1))
        scat.set_offsets(np.c_[eps[:n_pts], f[:n_pts]])
        label.set_text(f"{n_pts} / {len(eps)} runs")
        if i / N_FRAMES > 0.78:
            vline.set_alpha(0.95)
            txt.set_alpha(1.0)
        return scat, vline, txt, label

    return fig, draw, 1


def anim_03(L, t):
    c2 = _load("c2_verdict.json")
    rows = [r for r in c2["subcritical"]["rows"]
            if not r["flipped"] and r["q_max"] is not None]
    rows = sorted(rows, key=lambda r: np.log(r["eps"]))
    x = np.array([np.log(r["eps"]) for r in rows])
    v = np.array([r["v_qmax"] for r in rows])
    fit = c2["subcritical"]["slowdown_fit"]
    b, a = fit["slope_ln_eps"], fit["intercept"]
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=110,
                           constrained_layout=True)
    fig.patch.set_facecolor(t["bg"]); ax.set_facecolor(t["panel"])
    ax.grid(True, alpha=0.3, color=t["grid"])
    ax.tick_params(colors=t["ink"])
    for s in ax.spines.values():
        s.set_color(t["grid"])
    ax.set_xlabel(L["a3_x"], color=t["ink"])
    ax.set_ylabel(L["a3_y"], color=t["ink"])
    ax.set_title(L["a3_title"], color=t["ink"])
    ax.set_xlim(x.min() - 0.3, x.max() + 0.3)
    ax.set_ylim(0.55, 0.67)
    (line,) = ax.plot([], [], "o", color=t["ink"], ms=9, zorder=5)
    (fitline,) = ax.plot([], [], color=t["gold"], lw=2.2, zorder=4)
    note = ax.text(0.03, 0.94, "", transform=ax.transAxes, fontsize=10,
                   color=t["muted"], va="top")
    xs = np.linspace(x.min(), x.max(), 120)

    def draw(i):
        k = max(1, int(i / (N_FRAMES * 0.6) * len(x)) + 1)
        k = min(k, len(x))
        line.set_data(x[:k], v[:k])
        note.set_text(L["a3_quant"] if k < len(x) else "")
        if i / N_FRAMES > 0.62:
            kk = int((i / N_FRAMES - 0.62) / 0.35 * 120) + 1
            fitline.set_data(xs[:min(kk, 120)], (a + b * xs[:min(kk, 120)]))
            note.set_text(L["a3_fit"])
        return line, fitline, note

    return fig, draw, 1


def anim_04(L, t):
    # v2.1.0 (F-2): the per-grid remediated floors — the previously
    # hard-coded pre-remediation values are retracted.
    pts = [(800, 0.0155), (1600, 8.574765e-03), (3200, 4.244867e-03)]
    ns = np.array([p[0] for p in pts], dtype=float)
    fl = np.array([p[1] for p in pts])
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=110,
                           constrained_layout=True)
    fig.patch.set_facecolor(t["bg"]); ax.set_facecolor(t["panel"])
    ax.grid(True, which="both", alpha=0.3, color=t["grid"])
    ax.tick_params(colors=t["ink"])
    for s in ax.spines.values():
        s.set_color(t["grid"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(650, 4200); ax.set_ylim(2.4e-3, 2.4e-2)
    ax.set_xlabel(L["a4_x"], color=t["ink"])
    ax.set_ylabel(L["a4_y"], color=t["ink"])
    ax.set_title(L["a4_title"], color=t["ink"])
    (pts_line,) = ax.plot([], [], "o", color=t["ink"], ms=11, zorder=6)
    (law,) = ax.plot([], [], "--", color=t["gold"], lw=2.2, zorder=4)
    labels = [ax.annotate("", (n, f), xytext=(n * 0.92, f * 1.22),
                          fontsize=11, color=t["ink"]) for n, f in pts]
    xs = np.linspace(650, 4200, 140)

    def draw(i):
        k = min(3, int(i / (N_FRAMES * 0.62) * 3) + 1)
        pts_line.set_data(ns[:k], fl[:k])
        for j in range(k):
            labels[j].set_text(f"{fl[j]:.4g}")
        if i / N_FRAMES > 0.64:
            kk = int((i / N_FRAMES - 0.64) / 0.33 * 140) + 1
            law.set_data(xs[:min(kk, 140)], 12.0 / xs[:min(kk, 140)])
        return pts_line, law

    return fig, draw, 1


ANIMS = {
    "anim_01_evaporation": anim_01,
    "anim_02_bifurcation": anim_02,
    "anim_03_slowdown": anim_03,
    "anim_04_floor_law": anim_04,
}

N_FRAMES = 96  # ~4 s at 24 fps


def render(name, lang, dpi=110):
    t = fs.style("light")
    L = LANG[lang]
    builder = ANIMS[name]
    fig, draw, frames = builder(L, t)
    total = N_FRAMES if frames == 1 else min(N_FRAMES, frames)
    anim = FuncAnimation(fig, draw, frames=total, blit=False)
    outdir = os.path.join(OUT, lang)
    os.makedirs(outdir, exist_ok=True)
    mp4 = os.path.join(outdir, name + ".mp4")
    gif = os.path.join(outdir, name + ".gif")
    anim.save(mp4, writer=FFMpegWriter(fps=FPS, bitrate=1600))
    anim.save(gif, writer=PillowWriter(fps=16), dpi=96)
    plt.close(fig)
    return mp4, gif


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--only", choices=sorted(ANIMS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    langs = ["en", "ru"] if args.all else [args.lang or "en"]
    names = [args.only] if args.only else sorted(ANIMS)
    n = 0
    for lang in langs:
        for name in names:
            mp4, gif = render(name, lang)
            print("wrote", os.path.relpath(mp4, ROOT))
            print("wrote", os.path.relpath(gif, ROOT))
            n += 1
    print(f"\n{n} animations rendered ({len(names)} x {len(langs)} lang, mp4+gif)")


if __name__ == "__main__":
    main()
