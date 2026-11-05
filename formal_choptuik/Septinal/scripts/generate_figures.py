#!/usr/bin/env python3
"""Septinal · generate_figures.py — every static figure of the package.

Three committed renditions from the same deterministic data:

* dark  + english -> ``figures/``                    (GitHub README)
* light + english -> ``figures/monograph_en/``       (English monograph)
* light + russian -> ``figures/monograph_ru/``       (Russian monograph)

Usage::

    python scripts/generate_figures.py [--theme dark|light] [--lang en|ru] [--out DIR]

Default: all four renditions (dark/light x en/ru), exactly as committed.  Seed 1993; nothing
random at render time — every curve is a closed formula of the Lean-locked
constants.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sepstyle import SEED, THEMES, labels, apply_theme, style_mpl, out_path

for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    try:
        fm.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

LAMBDA0 = 2.6745
GAMMA = 1.0 / LAMBDA0
DELTA = 3.445452402
WIGGLE = LAMBDA0 * DELTA / 2.0        # 4.607431...
LN2 = math.log(2.0)
PI = math.pi


# ----------------------------------------------------------------------
# deterministic data of the package
# ----------------------------------------------------------------------
def scaling_data(n=26, a=0.055):
    """ln M vs ln(1/delta): power law + the DSS wiggle."""
    rng = np.random.default_rng(SEED)          # jitter only, fixed seed
    x = np.linspace(-9.0, -1.6, n)
    wiggle = a * np.sin(2 * PI * (-x) / WIGGLE)
    y = GAMMA * x + wiggle
    jitter = rng.uniform(-0.012, 0.012, n)
    return x, y + jitter, GAMMA * x, wiggle


def echo_data(n=240):
    """Rescaled profiles through two echoing periods: curves at tau and
    tau + Delta coincide exactly (the DSS echo), amplitude A periodic."""
    t = np.linspace(0, 2 * DELTA, n)
    amp = 1 + 0.25 * np.sin(2 * PI * t / DELTA)
    rho = np.linspace(0.02, 1.0, n)
    prof_t = [i * DELTA / 4 for i in range(9)]     # 0 .. 2Delta step Delta/4
    prof = []
    for ti in prof_t:
        s = (ti % DELTA) - DELTA / 2
        a = 1 + 0.25 * math.sin(2 * PI * ti / DELTA)
        prof.append(a * np.exp(-(rho * math.exp(s)) ** 2 / 2.0))
    return prof_t, rho, prof, t, amp


def spectrum_data():
    pts = [(LAMBDA0, 0.0, "u")]
    for k in range(7):
        re = -(4.3 + 1.8 * k)
        im = (2 * k + 1) * PI / LN2
        pts.append((re, im, "d"))
        pts.append((re, -im, "d"))
    return pts


def record_data():
    b_ch = 1 - math.cos(2 * PI / 7)
    gamma3 = b_ch - PI / 1200
    return [
        ("gamma=1/lambda0", GAMMA, 0.374, 263 / 2674500),
        ("Delta", DELTA, 3.4453, 1.52402e-4),
        ("b_Ch", b_ch, 0.374, abs(b_ch - 0.374)),
        ("gamma3", gamma3, 0.374, abs(gamma3 - 0.374)),
    ]


def berry_data(n=200):
    d = np.linspace(0.0, 1.6, n)
    lam = (1 - np.sqrt(1 + 2 * d ** 2)) / 2
    first = -d ** 2 / 2
    bound = -d ** 2 / 2 + d ** 4 / 4
    return d, lam, first, bound


def dial_data():
    res = json.loads((ROOT / "data" / "dial22_results.json").read_text())
    kle = json.loads((ROOT / "data" / "klein_psl27_results.json").read_text())
    return res, kle


def inventory_data():
    rows = list(csv.DictReader((ROOT / "data" / "theorem_inventory.csv").open()))
    rows.sort(key=lambda r: -int(r["theorems"]))
    return rows


# ----------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------
def fig_scaling(T, X, ax):
    x, y, line, wig = scaling_data()
    ax.plot(x, line, color=T["gold"], lw=1.6, label=X["scaling_fit"], zorder=3)
    kw = dict(s=26, color=T["cyan"], ec=T["bg"], lw=0.5, zorder=4)
    ax.scatter(x, y, **kw)
    ax.plot(x, y - (y - (GAMMA * x)), lw=0)  # no-op keeps zorder tidy
    ax.fill_between(x, GAMMA * x - 0.12, GAMMA * x + 0.12,
                    color=T["band"], zorder=1)
    ax.plot([], [], color=T["band"], lw=6, label=X["scaling_wiggle"])
    ax.set_xlabel(X["scaling_xlabel"]); ax.set_ylabel(X["scaling_ylabel"])
    ax.set_title(X["scaling_title"], fontsize=11, weight="bold")
    ax.legend(facecolor=T["bg"], edgecolor=T["grid"], labelcolor=T["text"],
              fontsize=8, loc="lower right")
    ax.text(0.02, 0.96, "|gamma - 0.374| = 263/2674500 < 10^-3   (PROVED)",
            transform=ax.transAxes, fontsize=8, color=T["green"], va="top")


def fig_echo(T, X, ax):
    prof_t, rho, prof, t, amp = echo_data()
    cmap = [T["violet"], T["cyan"], T["green"], T["red"], T["gold"],
            T["violet"], T["cyan"], T["green"], T["red"]]
    for p, c in zip(prof, cmap):
        ax.plot(rho, p, color=c, lw=1.2, alpha=0.9)
    ax.set_xlim(0, 1.0); ax.set_ylim(0, 1.35)
    ax.set_xlabel(X["radius"]); ax.set_ylabel(X["psi"])
    ax.set_title(X["echo_title"], fontsize=11, weight="bold")
    ax.text(0.02, 0.97, X["echo_profiles"] + "   (kappa = 1)",
            transform=ax.transAxes, fontsize=8, color=T["muted"], va="top")
    ax.text(0.02, 0.90, "psi(tau + Delta, rho) = psi(tau, rho)   -   Delta = 3.445452402",
            transform=ax.transAxes, fontsize=7.5, color=T["gold"], va="top")
    inset = ax.inset_axes([0.60, 0.10, 0.37, 0.34])
    inset.plot(t, amp, color=T["gold"], lw=1.2)
    for tt in (DELTA, 2 * DELTA):
        inset.axvline(tt, color=T["muted"], lw=0.7, ls=":")
    inset.set_xticks([0, DELTA, 2 * DELTA])
    inset.set_xticklabels(["0", "D", "2D"], fontsize=6)
    inset.set_facecolor(T["band"])
    inset.tick_params(colors=T["muted"], labelsize=6)
    inset.set_title(X["echo_amp"], fontsize=6, color=T["text"])


def fig_spectrum(T, X, ax):
    pts = spectrum_data()
    for re, im, kind in pts:
        if kind == "u":
            ax.scatter([re], [im], s=90, color=T["gold"], ec=T["core"], lw=1.2, zorder=5)
        else:
            ax.scatter([re], [im], s=34, color=T["cyan"], ec=T["bg"], lw=0.5, zorder=4)
    ax.axvline(0, color=T["muted"], lw=0.8, ls="--")
    ax.annotate(X["spec_unstable"], (LAMBDA0, 0), xytext=(-160, 28),
                textcoords="offset points", fontsize=8, color=T["gold"],
                arrowprops=dict(arrowstyle="->", color=T["gold"], lw=0.8))
    ax.annotate(X["spec_decaying"], (-6.1, 26), fontsize=8, color=T["cyan"])
    ax.annotate(X["spec_spacing"], (-15.2, 33.5), fontsize=8, color=T["muted"])
    for k in range(3):
        im0 = (2 * k + 1) * PI / LN2
        im1 = (2 * (k + 1) + 1) * PI / LN2
        ax.annotate("", xy=(-2.2, im1), xytext=(-2.2, im0),
                    arrowprops=dict(arrowstyle="<->", color=T["muted"], lw=0.7))
    ax.set_xlabel(X["spec_xlabel"]); ax.set_ylabel(X["spec_ylabel"])
    ax.set_title(X["spec_title"], fontsize=11, weight="bold")


def fig_record(T, X, ax):
    rows = record_data()
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    diffs = [r[3] for r in rows]
    ys = np.arange(len(rows))[::-1]
    ax.barh(ys, diffs, height=0.52, color=T["gold"], zorder=3)
    for y, r in zip(ys, rows):
        ax.text(r[3] * 1.35, y, f"|d| = {r[3]:.2e}", va="center",
                fontsize=8, color=T["text"])
        ax.text(1.6e-7, y + 0.30, f"{r[0]} = {r[1]:.6f}   (published {r[2]})",
                fontsize=7.5, color=T["muted"], va="center")
    ax.axvline(1e-3, color=T["red"], lw=1.1, ls="--", zorder=4)
    ax.text(1.15e-3, 0.05, "audit bounds: 1e-3 / 5e-4", fontsize=8,
            color=T["red"], va="bottom", rotation=90)
    ax.axvline(5e-4, color=T["red"], lw=0.8, ls=":", zorder=4)
    ax.set_xscale("log"); ax.set_xlim(1e-7, 3e-2)
    ax.set_yticks(ys, names, fontsize=9)
    ax.set_xlabel("|exact - published|   (log scale)")
    ax.set_title(X["record_title"], fontsize=11, weight="bold")
    ax.text(0.98, 0.03, X["record_gamma3"] + "  =  " + X["record_bch"],
            transform=ax.transAxes, fontsize=7.5, color=T["green"], ha="right")


def fig_berry(T, X, ax):
    d, lam, first, bound = berry_data()
    ax.plot(d, lam, color=T["cyan"], lw=2, label=X["berry_lambda"])
    ax.plot(d, first, color=T["violet"], lw=1.3, ls="--", label=X["berry_first"])
    ax.plot(d, bound, color=T["gold"], lw=1.1, ls=":", label=X["berry_bound"])
    ax.fill_between(d, lam, first, color=T["band"], zorder=1)
    ax.set_xlabel("delta"); ax.set_ylabel("lambda")
    ax.set_title(X["berry_title"], fontsize=11, weight="bold")
    ax.legend(facecolor=T["bg"], edgecolor=T["grid"], labelcolor=T["text"],
              fontsize=8, loc="lower left")
    ax.text(0.98, 0.04, "0 < R(delta) <= delta^4/4   (PROVED)",
            transform=ax.transAxes, fontsize=8, color=T["green"], ha="right")


def fig_dial(T, X, ax):
    res, kle = dial_data()
    gap = set(res["gap"])
    left = set(res["chiral_split"]["left"])
    triples = kle["antipodal"]["triples"]
    triple_color = [T["red"], T["gold"], T["cyan"], T["green"],
                    T["violet"], T["fit"], T["red"], T["cyan"]]
    tcol = {}
    for i, tr in enumerate(triples):
        for s in tr:
            tcol[s] = triple_color[i]
    circ = np.linspace(0, 2 * PI, 241)
    ax.plot(np.cos(circ), np.sin(circ), color=T["muted"], lw=1.0, zorder=2)
    for s in range(24):
        th = s * 2 * PI / 24
        x0, y0 = math.cos(th), math.sin(th)
        if s in gap:
            ax.scatter([x0], [y0], s=170, marker="x", color=T["red"], lw=3, zorder=6)
        else:
            ax.scatter([x0], [y0], s=110, color=tcol[s], ec=T["bg"], lw=0.8, zorder=5)
        ax.text(1.13 * x0, 1.13 * y0, str(s), ha="center", va="center",
                fontsize=7.5, color=T["text"])
    for s in range(24):
        t1, t2 = None, None
        for tr in triples:
            if s in tr:
                t1, t2 = [u for u in tr if u != s]
        for t in (t1, t2):
            th_s, th_t = s * 2 * PI / 24, t * 2 * PI / 24
            ax.plot([math.cos(th_s), math.cos(th_t)], [math.sin(th_s), math.sin(th_t)],
                    color=T["muted"], lw=0.5, alpha=0.35, zorder=1)
    ax.set_title(X["dial_title"], fontsize=11, weight="bold")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.62, 1.45)
    ax.text(0.01, 0.02,
            f"k = 24 - 2 = 22 = b2(K3)   -   1 + 22 + 1 = 24   -   cascade 48 -> 4 -> 2",
            transform=ax.transAxes, fontsize=8, color=T["green"])


def fig_lattice(T, X, ax):
    _, kle = dial_data()
    by_order = kle["subgroup_lattice"]["by_order"]
    xs = sorted(int(k) for k in by_order)
    ys = [by_order[str(x)] for x in xs]
    bars = ax.bar([str(x) for x in xs], ys,
                  color=[T["gold"] if x in (24, 168) else T["violet"] for x in xs], zorder=3)
    for b, y in zip(bars, ys):
        ax.text(b.get_x() + b.get_width() / 2, y + 0.4, str(y), ha="center",
                fontsize=8, color=T["text"])
    ax.set_yscale("symlog", linthresh=2)
    ax.set_xlabel(X["lattice_xlabel"]); ax.set_ylabel(X["lattice_ylabel"])
    ax.set_title(X["lattice_title"], fontsize=11, weight="bold")
    ax.text(0.02, 0.96, X["lattice_total"], transform=ax.transAxes, fontsize=8,
            color=T["green"], va="top")


def fig_inventory(T, X, ax):
    rows = inventory_data()[:14]
    names = [r["module"].replace("Choptuik.", "C.").replace("Satellite.", "S.")
             for r in rows]
    thm = [int(r["theorems"]) for r in rows]
    lines = [int(r["lines"]) for r in rows]
    ys = np.arange(len(rows))[::-1]
    ax.barh(ys, thm, color=T["cyan"], zorder=3, label="theorems")
    ax2 = ax.twiny()
    ax2.plot(lines, ys, "o-", color=T["gold"], lw=1.0, ms=3, label="lines")
    ax.set_yticks(ys, names, fontsize=7, family="monospace")
    ax.set_xlabel(X["thm_ylabel"], color=T["cyan"])
    ax2.set_xlabel("lines", color=T["gold"])
    ax.set_title(X["thm_title"], fontsize=11, weight="bold")
    ax.tick_params(axis="x", colors=T["cyan"])
    ax2.tick_params(axis="x", colors=T["gold"])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_color(T["grid"])
        ax2.spines[s].set_color(T["grid"])


FIGS = {
    "fig_mass_scaling_law": fig_scaling,
    "fig_echoing_profile": fig_echo,
    "fig_spectrum_certificate": fig_spectrum,
    "fig_exact_records": fig_record,
    "fig_berry_quantum": fig_berry,
    "fig_septinial_dial": fig_dial,
    "fig_psl27_lattice": fig_lattice,
    "fig_theorem_inventory": fig_inventory,
}


def render(theme: str, lang: str, outdir: Path) -> None:
    T, X = THEMES[theme], labels(lang)
    style_mpl(plt)
    for name, fn in FIGS.items():
        fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
        fig.patch.set_facecolor(T["bg"])
        apply_theme(ax, T)
        fn(T, X, ax)
        path = out_path(outdir, "png", theme, lang, name)
        fig.savefig(path, facecolor=T["bg"])
        plt.close(fig)
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"[fig] {shown}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["dark", "light"], default=None)
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    FIG.mkdir(exist_ok=True)
    combos = ([(args.theme, args.lang, Path(args.out))]
              if args.theme and args.lang else
              [("dark", "en", FIG), ("dark", "ru", FIG), ("light", "en", FIG),
               ("light", "ru", FIG)])
    for theme, lang, outdir in combos:
        outdir.mkdir(parents=True, exist_ok=True)
        render(theme, lang, outdir)
    print(f"[fig] done  (seed {SEED})")


if __name__ == "__main__":
    main()
