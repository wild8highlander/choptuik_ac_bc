#!/usr/bin/env python3
"""
make_figures.py — regenerate every figure of the project.

Seven figures x two languages (en, ru) x two themes (light, dark) = 28
PNG files under figures/<lang>/<theme>/.  All data come from the
committed verdicts (campaigns/reference/) and derived tables
(data/bridge/); the script never computes new physics, only visualises
committed results.

Run:   python3 scripts/make_figures.py --all
       python3 scripts/make_figures.py --lang en --theme dark
"""
import argparse
import csv
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import figstyle as fs
import matplotlib.pyplot as plt
from chbridge.constants import T_CMB, gamma_Ch
from chbridge.hawking import (
    PAGE_FRACTION,
    S_BH,
    T_H,
    k_B,
)

REF = os.path.join(ROOT, "campaigns", "reference")
DATA = os.path.join(ROOT, "data", "bridge")


def _load(name):
    with open(os.path.join(REF, name)) as f:
        return json.load(f)


def _load_c1():
    return _load("c1_verdict.json")


# ---------------------------------------------------------------------------
def fig_hawking(t, L, ax_t, ax_s):
    """T_H and S_BH vs mass with the CMB contact point."""
    M = np.logspace(10, 33, 400)
    T = np.array([T_H(m) for m in M])
    S = np.array([S_BH(m) for m in M]) / k_B
    ax_t.plot(M, T, color=t["ink"], lw=2)
    ax_t.set_xscale("log"); ax_t.set_yscale("log")
    ax_t.axhline(T_CMB, color=t["muted"], lw=1, ls="--")
    M_cmb = 4.50e22
    ax_t.plot([M_cmb], [T_CMB], "o", color=t["gold"], ms=8, zorder=5)
    ax_t.annotate(L["cmb_contact"], (M_cmb, T_CMB),
                  xytext=(M_cmb * 3e-3, T_CMB * 40),
                  color=t["gold"], fontsize=10)
    ax_t.axvline(M_cmb, color=t["gold_soft"], lw=1, ls=":")
    ax_t.set_xlabel(L["M"]); ax_t.set_ylabel(L["T_H"])
    ax_t.set_title(L["hawking_title"])
    ax_t.grid(True, which="both")

    ax_s.plot(M, S, color=t["ink"], lw=2)
    ax_s.set_xscale("log"); ax_s.set_yscale("log")
    ax_s.set_xlabel(L["M"]); ax_s.set_ylabel(L["S_BH"])
    ax_s.grid(True, which="both")


def fig_page(t, L, ax):
    """Radiation entropy curves of the three ensemble members."""
    path = os.path.join(DATA, "page_curve_grid.csv")
    with open(path) as f:
        rows = list(csv.DictReader(f))
    colors = {"near_floor": t["gold"], "mid": t["ink"], "saturated": t["muted"]}
    for member in ("saturated", "mid", "near_floor"):
        rr = [r for r in rows if r["member"] == member]
        tau = np.array([float(r["t_over_t_evap"]) for r in rr])
        S = np.array([float(r["S_rad_over_kB_norm"]) for r in rr])
        ax.plot(tau, S, color=colors[member], lw=2,
                label=f"f~ = {float(rr[0]['f_tilde']):.4f}")
    ax.axvline(PAGE_FRACTION, color=t["gold"], lw=1.4, ls="--")
    ax.annotate(L["page_time"], (PAGE_FRACTION, 0.72), xytext=(PAGE_FRACTION - 0.34, 0.72),
                color=t["gold"], fontsize=10,
                arrowprops=dict(arrowstyle="->", color=t["gold"]))
    ax.set_xlabel(L["page_x"]); ax.set_ylabel(L["page_y"])
    ax.set_title(L["page_title"])
    ax.legend(frameon=False)
    ax.grid(True)


def fig_ladder(t, L, ax):
    """Scale ladder (lengths) as a horizontal log bar chart."""
    path = os.path.join(DATA, "scale_ladder_length.csv")
    with open(path) as f:
        rows = list(csv.DictReader(f))
    names = [r["quantity"] for r in rows][::-1]
    vals = [float(r["value_m"]) for r in rows][::-1]
    ypos = np.arange(len(names))
    ax.barh(ypos, vals, color=t["gold_soft"], edgecolor=t["ink"], lw=0.5)
    ax.set_yticks(ypos); ax.set_yticklabels(names, fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("m")
    ax.set_title(L["ladder_title"])
    ax.grid(True, axis="x", which="both")


def fig_scaling(t, L, ax):
    """Born spectrum M(eps) with the gamma anchor and the floor."""
    c1 = _load_c1()
    rows = [r for r in c1["scan_N800"]["rows"] if r["sane"]]
    eps = np.array([r["eps"] for r in rows])
    M = np.array([r["M_code"] for r in rows])
    ax.scatter(eps[eps < 3e-2], M[eps < 3e-2], s=26, color=t["ink"],
               zorder=4, label="engine (N=800, sane)")
    ax.scatter(eps[eps >= 3e-2], M[eps >= 3e-2], s=26, facecolors="none",
               edgecolors=t["muted"], zorder=3, label="floor-saturated band")
    # anchor slope through the mid member
    eps_line = np.logspace(-3.5, -0.3, 50)
    C = math.log10(2.1e-2) - gamma_Ch * math.log10(1.3e-2)
    ax.plot(eps_line, 10 ** (C + gamma_Ch * np.log10(eps_line)),
            color=t["gold"], lw=1.6, ls="--", label=L["anchor"])
    ax.axhline(1.55e-2, color=t["muted"], lw=1.2, ls=":", label=L["floor"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["scaling_x"]); ax.set_ylabel(L["scaling_y"])
    ax.set_title(L["scaling_title"])
    ax.legend(frameon=False, fontsize=9)
    ax.grid(True, which="both")


def fig_validation(t, L, ax):
    """Roberts-Oshiro convergence: err vs N, slope -2."""
    c1 = _load_c1()
    val = c1["validation"]
    ns = np.array([v["n"] for v in val], dtype=float)
    err = np.array([v["err_r"] for v in val], dtype=float)
    ax.plot(ns, err, "o-", color=t["ink"], lw=2, ms=7)
    for v in val:
        if "convergence_order_r" in v:
            ax.annotate(f"order {v['convergence_order_r']:.2f}",
                        (v["n"], v["err_r"]), xytext=(v["n"] * 0.85, v["err_r"] * 1.6),
                        color=t["gold"], fontsize=10)
    ref = err[0] * (ns / ns[0]) ** (-2)
    ax.plot(ns, ref, ls="--", color=t["gold"], lw=1.4, label="slope -2")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["val_x"]); ax.set_ylabel(L["val_y"])
    ax.set_title(L["validation_title"])
    ax.legend(frameon=False)
    ax.grid(True, which="both")


def fig_map(t, L, ax):
    """The bridge map: engine -> f~ -> thermodynamics."""
    ax.axis("off")
    ax.set_title(L["map_title"], pad=18)

    def box(x, y, w, h, title, lines, face):
        r = plt.Rectangle((x, y), w, h, facecolor=face, edgecolor=t["ink"],
                          lw=1.2, zorder=2)
        ax.add_patch(r)
        ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top",
                fontsize=11, fontweight="bold", color=t["ink"], zorder=3)
        for i, s in enumerate(lines):
            ax.text(x + w / 2, y + h - 0.34 - i * 0.13, s, ha="center",
                    va="top", fontsize=9, color=t["ink"], zorder=3)

    box(0.02, 0.18, 0.40, 0.62,
        "CRITICAL COLLAPSE (engine)",
        ["double-null march, 4piG=1",
         "A* ladder: 0.10510 / 0.08820 / 0.080534",
         "ladder drifts to 0.077744 (N=1600, F-1)",
         "born spectrum f~(eps), floor kept"],
        t["panel"])
    box(0.58, 0.18, 0.40, 0.62,
        "BH THERMODYNAMICS",
        ["T_H ~ 1/M,  S_BH ~ M^2",
         "t_evap ~ M^3, t_Page = 0.6464 t_evap",
         "CMB contact at 4.50e22 kg",
         "Page curve + Haar check"],
        t["panel"])

    ax.annotate("", xy=(0.57, 0.55), xytext=(0.43, 0.55),
                arrowprops=dict(arrowstyle="-|>", lw=2.2, color=t["gold"]))
    ax.text(0.5, 0.60, "$M_{BH} = M_{in}\\cdot\\tilde f(\\varepsilon)$",
            ha="center", fontsize=11, color=t["gold"])
    ax.text(0.5, 0.47, "single input scale", ha="center", fontsize=9,
            color=t["muted"])
    ax.text(0.5, 0.06, "$\\Delta\\cdot\\gamma \\approx 1.27$ (C3)   |   "
            "$b_{Ch}=1-\\cos(2\\pi/7)=0.37651$ vs $\\gamma_{Ch}=0.374$ (0.67%)",
            ha="center", fontsize=9.5, color=t["ink"])


def fig_branches(t, L, ax_s, ax_x):
    """The two branches of campaign C2: approach (sub) and f~ (super)."""
    c2 = _load("c2_verdict.json")
    sub = c2["subcritical"]
    rows = [r for r in sub["rows"]
            if not r["flipped"] and r["q_max"] is not None]
    eps = np.array([r["eps"] for r in rows])
    q_max = np.array([r["q_max"] for r in rows])
    ax_s.plot(eps, q_max, "o-", color=t["ink"], ms=6, lw=1.4, zorder=4)
    ax_s.axhline(1.0, color=t["gold"], lw=1.4, ls="--", label=L["branch_horizon"])
    ax_s.set_xscale("log")
    ax_s.set_ylim(0.0, 1.08)
    ax_s.set_xlabel(L["branch_sub_x"])
    ax_s.set_ylabel(L["branch_sub_y"])
    ax_s.set_title(L["branch_sub_title"])
    ax_s.legend(frameon=False, fontsize=9, loc="upper right")
    ax_s.grid(True, which="both")

    bif = [r for r in c2["bifurcation"]["rows"] if r["sane"]]
    eps = np.array([r["eps"] for r in bif])
    ftl = np.array([r["f_tilde"] for r in bif])
    ax_x.scatter(eps, ftl, s=26, color=t["ink"], zorder=4)
    eps_half = c2["bifurcation"]["summary"]["eps_half"]
    ax_x.axhline(1.0, color=t["muted"], lw=1.1, ls=":", label=L["branch_sat"])
    ax_x.axvline(eps_half, color=t["gold"], lw=1.4, ls="--")
    ax_x.annotate(L["branch_eps_half"], (eps_half, 0.30),
                  xytext=(eps_half * 3.5, 0.26), color=t["gold"], fontsize=10,
                  arrowprops=dict(arrowstyle="->", color=t["gold"]))
    ax_x.set_xscale("log"); ax_x.set_yscale("log")
    ax_x.set_xlabel(L["branch_bif_x"])
    ax_x.set_ylabel(L["branch_bif_y"])
    ax_x.set_title(L["branch_bif_title"])
    ax_x.legend(frameon=False, fontsize=9, loc="lower right")
    ax_x.grid(True, which="both")


FIGS = {
    "fig_hawking": (fig_hawking, True),   # True = two panels
    "fig_page": (fig_page, False),
    "fig_ladder": (fig_ladder, False),
    "fig_scaling": (fig_scaling, False),
    "fig_validation": (fig_validation, False),
    "fig_map": (fig_map, False),
    "fig_branches": (fig_branches, True),  # True = two panels
}


def make_one(name, lang, theme, dpi=300):
    t = fs.style(theme)
    L = fs.LANG[lang]
    fn, two = FIGS[name]
    if two:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0),
                                 constrained_layout=True)
        fn(t, L, axes[0], axes[1])
    else:
        fig = fs.new_fig()
        ax = fig.add_subplot(111)
        fn(t, L, ax)
    outdir = os.path.join(ROOT, "figures", lang, theme)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, name + ".png")
    fs.finish(fig, out, dpi=dpi)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--theme", choices=["light", "dark"], default=None)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    langs = ["en", "ru"] if args.all else [args.lang or "en"]
    themes = ["light", "dark"] if args.all else [args.theme or "light"]
    n = 0
    for lang in langs:
        for theme in themes:
            for name in FIGS:
                p = make_one(name, lang, theme, args.dpi)
                print("wrote", os.path.relpath(p, ROOT))
                n += 1
    print(f"\n{n} figures written ({len(FIGS)} x {len(langs)} lang x {len(themes)} theme)")


if __name__ == "__main__":
    main()
