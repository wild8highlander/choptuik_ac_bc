#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_c6_figures.py — report figures for campaign C6 (the resolution-drift law).

Two figures x two languages (en/ru), light theme, 300 dpi, written to
results/scaling_drift/figures/:

  drift_ladder_XX.png     observed per-doubling drift of the committed
                          A* ladder vs the T10 exact parabolic-tension
                          channel and the REJECTED two-term fit;
  parabola_tension_XX.png the two exact lemmas in one picture: chord
                          flattening (kappa h^2/8 sag) and the
                          chord-chain arc deficit.

Deterministic: reads only committed artifacts (c6_drift_verdict.json).
Run:  python3 scripts/make_c6_figures.py
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.path.join(ROOT, "results", "scaling_drift", "figures")
REF = os.path.join(ROOT, "campaigns", "reference")

L = {
    "en": {
        "ladder_title": "Resolution drift of the threshold: observed vs exact channel",
        "ladder_y": "per-doubling drift  $A^*_N - A^*_{2N}$",
        "ladder_x": "grid resolution  N",
        "observed": "observed drift (committed ladder)",
        "exact": "T10 exact channel  $\\kappa^* h^2/(8s)$",
        "rejected": "two-term fit $a/N + b/N^2$ (REJECTED)",
        "guide1": "slope $-1/N$ guide",
        "guide2": "slope $-1/N^2$ guide",
        "para_title": "The two exact lemmas on a sampled parabola",
        "peak_note_short": "sampled peak is lower by $\\kappa h^2/8$ (worst alignment)",
        "zoom_title": "zoom: the chord sag at the peak",
        "para_y": "profile  $q(x)$",
        "para_x": "local coordinate  $x$",
        "continuum": "continuum parabola (tension $\\kappa$)",
        "chords": "sampled chord family",
        "sag": "chord sag $= \\kappa h^2/8$",
        "arc_note": "chord chain is shorter than the arc:\nthe sampled structure is compressed",
        "peak_note": "sampled peak is lower by $\\kappa h^2/8$\n(worst alignment)",
        "caption_ladder": ("Observed per-doubling drift of the committed remediation ladder "
                           "against the T10 exact parabolic-tension channel (calibrated on "
                           "committed artifacts) and the rejected two-term power-law fit."),
        "caption_para": ("Lemma A (chord flattening): the sampled peak sags by exactly kappa*h^2/8. "
                         "Lemma B (tension): the chord chain through the samples is shorter than the "
                         "continuum arc — the structure compresses under its tension at fixed grid."),
    },
    "ru": {
        "ladder_title": "Дрейф порога с разрешением: наблюдение и точный канал",
        "ladder_y": "дрейф за удвоение  $A^*_N - A^*_{2N}$",
        "ladder_x": "разрешение сетки  N",
        "observed": "наблюдаемый дрейф (зафиксированная лестница)",
        "exact": "точный канал Т10:  $\\kappa^* h^2/(8s)$",
        "rejected": "двухчленная аппроксимация $a/N + b/N^2$ (ОТВЕРГНУТА)",
        "guide1": "наклон $-1/N$",
        "guide2": "наклон $-1/N^2$",
        "para_title": "Две точные леммы на параболе при дискретизации",
        "peak_note_short": "пик занижен на $\\kappa h^2/8$ (худшее выравнивание)",
        "zoom_title": "масштаб: провис хорды у пика",
        "para_y": "профиль  $q(x)$",
        "para_x": "локальная координата  $x$",
        "continuum": "непрерывная парабола (натяжение $\\kappa$)",
        "chords": "дискретизованное семейство хорд",
        "sag": "провис хорды $= \\kappa h^2/8$",
        "arc_note": "ломаная короче дуги:\nдискретизованная структура сжата",
        "peak_note": "пик занижен на $\\kappa h^2/8$\n(худшее выравнивание)",
        "caption_ladder": ("Наблюдаемый дрейф порога за удвоение разрешения против точного "
                           "канала Т10 (параболическое натяжение, калибровка на зафиксированных "
                           "артефактах) и отвергнутой двухчленной аппроксимации."),
        "caption_para": ("Лемма А (сплющивание): пик при дискретизации занижен ровно на kappa*h^2/8. "
                         "Лемма B (натяжение): ломаная по узлам короче непрерывной дуги — структура "
                         "сжата под действием своего натяжения при фиксированной сетке."),
    },
}


def draw_drift_ladder(verdict, lang, theme):
    t = figstyle.TOKENS[theme]
    tr = L[lang]
    fig, ax = plt.subplots(figsize=(8.6, 5.4), dpi=300, constrained_layout=True)
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["panel"])

    Ns = np.array([pt["N"] for pt in verdict["ladder_analysis"]["ladder"]], float)
    drifts = np.array(verdict["ladder_analysis"]["per_doubling_drifts"])
    Nmid = (Ns[:-1] + Ns[1:]) / 2.0

    ax.loglog(Nmid, drifts, "o", color=t["ink"], ms=9, lw=0,
              label=tr["observed"], zorder=5)

    chan = verdict["channel_decomposition"]
    chN = np.array([c["N"] for c in chan], float) * 2.0   # drift measured to 2N
    chA = np.array([c["flattening_channel_dA"] for c in chan], float)
    ax.loglog(chN, chA, "s--", color=t["gold"], lw=2.0, ms=7,
              label=tr["exact"], zorder=4)

    st = verdict["extrapolation_stress_test"]
    Ainf, a, b = st["A_inf_fit"], st["a_fit"], st["b_fit"]
    law = [(Ainf + a / n + b / n**2) - (Ainf + a / (2*n) + b / (4*n**2))
           for n in Nmid]
    ax.loglog(Nmid, law, ":", color=t["bad"], lw=2.2,
              label=tr["rejected"], zorder=3)

    # power-law guides anchored at the first observed point
    for p, lbl in ((1.0, tr["guide1"]), (2.0, tr["guide2"])):
        g = drifts[0] * (Nmid[0] / Nmid) ** p
        ax.loglog(Nmid, g, "-", color=t["grid"], lw=1.4, alpha=0.9)
        ax.annotate(lbl, (Nmid[-1], g[-1]), xytext=(-2, -14),
                    textcoords="offset points", ha="right", va="top",
                    fontsize=10, color=t["muted"])

    ax.set_xlabel(tr["ladder_x"], fontsize=12, color=t["ink"])
    ax.set_ylabel(tr["ladder_y"], fontsize=12, color=t["ink"])
    ax.set_title(tr["ladder_title"], fontsize=14, color=t["ink"], pad=12)
    ax.grid(True, which="both", alpha=0.35, color=t["grid"], lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["muted"])
    ax.tick_params(colors=t["ink"], labelsize=10)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.04),
                    fontsize=10, frameon=True, facecolor=t["panel"],
                    edgecolor=t["grid"], labelcolor=t["ink"])
    leg.get_frame().set_alpha(0.95)
    return fig


def draw_parabola(lang, theme):
    t = figstyle.TOKENS[theme]
    tr = L[lang]
    fig, (ax, axi) = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=300,
                                  constrained_layout=True,
                                  gridspec_kw={"width_ratios": [1.25, 1.0]})
    for a in (ax, axi):
        fig.patch.set_facecolor(t["bg"])
        a.set_facecolor(t["panel"])

    kappa, h, half = 2.0, 0.25, 1.0

    # --- panel 1: continuum parabola vs sampled chord family -------------
    xs = np.linspace(-half, half, 800)
    ax.plot(xs, 1.0 - kappa * xs**2 / 2.0, color=t["gold"], lw=3.0,
            label=tr["continuum"], zorder=4)
    # worst alignment: the peak sits at a CELL CENTRE (offset by h/2)
    nodes = np.arange(-half + h / 2.0, half + 1e-9, h)
    qn = 1.0 - kappa * nodes**2 / 2.0
    ax.plot(nodes, qn, "-", color=t["ink"], lw=1.6, marker="o", ms=5,
            mfc=t["panel"], mec=t["ink"], label=tr["chords"], zorder=5)
    # shaded arc-vs-chord deficit on both flanks (full cells only)
    for lo in (nodes[:-1], ):
        pass
    xf = np.concatenate([np.linspace(n0, n1, 60) for n0, n1 in zip(nodes[:-1], nodes[1:])])
    ax.fill_between(xf, 1.0 - kappa * xf**2 / 2.0, np.interp(xf, nodes, qn),
                    color=t["gold"], alpha=0.18, lw=0)
    ax.text(0.0, 0.40, tr["arc_note"], fontsize=10.5, color=t["muted"],
            ha="center")
    ax.text(0.0, 0.275, tr["peak_note_short"], fontsize=10.5, color=t["muted"],
            ha="center")
    ax.set_xlabel(tr["para_x"], fontsize=12, color=t["ink"])
    ax.set_ylabel(tr["para_y"], fontsize=12, color=t["ink"])
    ax.set_title(tr["para_title"], fontsize=13.5, color=t["ink"], pad=10)
    ax.grid(True, alpha=0.35, color=t["grid"], lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["muted"])
    ax.tick_params(colors=t["ink"], labelsize=10)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.04),
                    fontsize=10, frameon=True, facecolor=t["panel"],
                    edgecolor=t["grid"], labelcolor=t["ink"])
    leg.get_frame().set_alpha(0.95)

    # --- panel 2: zoom on the peak, worst alignment ----------------------
    chord_mid = 1.0 - kappa * (h / 2.0) ** 2 / 2.0        # = 1 - kappa h^2/8
    sag = kappa * h**2 / 8.0
    z = np.linspace(-0.26, 0.26, 400)
    axi.plot(z, 1.0 - kappa * z**2 / 2.0, color=t["gold"], lw=3.0)
    zn = nodes[(nodes > -0.28) & (nodes < 0.28)]
    axi.plot(zn, 1.0 - kappa * zn**2 / 2.0, "-", color=t["ink"], lw=1.6,
             marker="o", ms=6, mfc=t["panel"], mec=t["ink"])
    axi.annotate("", xy=(0.0, 1.0), xytext=(0.0, chord_mid),
                 arrowprops=dict(arrowstyle="<->", color=t["bad"], lw=2.0))
    axi.text(0.035, 1.0 - sag / 2.0, tr["sag"], fontsize=12, color=t["bad"],
             va="center")
    axi.set_xlim(-0.27, 0.40)
    axi.set_ylim(chord_mid - 0.012, 1.010)
    axi.set_xlabel(tr["para_x"], fontsize=11, color=t["ink"])
    axi.set_title(tr["zoom_title"], fontsize=12, color=t["ink"], pad=8)
    axi.grid(True, alpha=0.3, color=t["grid"], lw=0.5)
    for s in ("top", "right"):
        axi.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        axi.spines[s].set_color(t["muted"])
    axi.tick_params(colors=t["ink"], labelsize=9)
    return fig


def main():
    with open(os.path.join(REF, "c6_drift_verdict.json")) as f:
        verdict = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    for lang in ("en", "ru"):
        for theme in ("light", "dark"):
            tag = f"{lang}_{theme}"
            fig = draw_drift_ladder(verdict, lang, theme)
            p = os.path.join(OUT, f"drift_ladder_{tag}.png")
            fig.savefig(p, facecolor=fig.get_facecolor())
            plt.close(fig)
            print("wrote", os.path.relpath(p, ROOT))
            fig = draw_parabola(lang, theme)
            p = os.path.join(OUT, f"parabola_tension_{tag}.png")
            fig.savefig(p, facecolor=fig.get_facecolor())
            plt.close(fig)
            print("wrote", os.path.relpath(p, ROOT))
    print("DONE: 8 figures (2 types x en/ru x light/dark)")


if __name__ == "__main__":
    main()
