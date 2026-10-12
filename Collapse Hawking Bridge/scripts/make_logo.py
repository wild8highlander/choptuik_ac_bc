#!/usr/bin/env python3
"""
make_logo.py — the official logo of the Collapse-Hawking Bridge.

"Ink & Gold" emblem: the two worlds the package bridges, drawn with the
package's own mathematics.

  LEFT  — critical collapse: three nested self-similar parabolas
          (the echoing profile near the threshold, the A* ladder) with
          the gold accumulation point;
  ARC   — the bridge itself: M_BH = M_in * f~(eps);
  RIGHT — the born black hole: Schwarzschild horizon disk, photon ring,
          Hawking quanta leaving it (thermodynamics side).

Variants: light / dark (theme-aware), PNG @ 600 dpi + SVG (text as
paths, portable). Deterministic; no external assets.

Run:  python3 scripts/make_logo.py
Out:  figures/logo/chb_logo_{light,dark}.{png,svg}
"""
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import contextlib

for _p in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    with contextlib.suppress(Exception):
        fm.fontManager.addfont(_p)

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "path"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures", "logo")

THEMES = {
    "light": {"bg": "none", "ink": "#1A1A24", "gold": "#8C6D1F",
              "gold_soft": "#C9A84C", "muted": "#6B6455", "hole": "#10101A",
              "hole_edge": "#C9A84C"},
    "dark": {"bg": "none", "ink": "#E8E2D0", "gold": "#C9A84C",
             "gold_soft": "#E3C878", "muted": "#9A9484", "hole": "#05050C",
             "hole_edge": "#E3C878"},
}


def draw(theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(9.6, 4.6), dpi=600)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 960)
    ax.set_ylim(0, 460)
    ax.axis("off")

    # ---------------- left: nested self-similar parabolas -------------------
    cx0, rim = 152.0, 352.0
    a0 = 78.0          # depth of the outermost parabola
    for i, frac in enumerate((1.00, 0.60, 0.32)):
        w = 96.0 * frac
        depth = a0 * frac
        x = np.linspace(-w, w, 300)
        y = rim - depth * (1.0 - (x / w) ** 2)
        ax.plot(cx0 + x, y, color=t["ink"], lw=3.4 - 0.7 * i,
                alpha=1.0 - 0.30 * i, solid_capstyle="round", zorder=3)
        # gold tip: the local accumulation point of each echo
        ax.plot([cx0 + x[0]], [y[0]], marker="o", ms=5 - i,
                color=t["gold_soft"], alpha=0.9, zorder=4)
    # gold focus at the deepest accumulation point
    tip_y = rim - a0 * 0.32
    ax.plot([cx0], [tip_y], marker="o", ms=8, color=t["gold"], zorder=6)
    # distance-to-threshold arrows (eps -> 0, the ladder drift)
    ax.annotate("", xy=(cx0 + 14, tip_y + 6), xytext=(cx0 + 86, rim + 16),
                arrowprops={"arrowstyle": "-|>", "color": t["muted"], "lw": 1.4,
                                "alpha": 0.9, "connectionstyle": "arc3,rad=-0.25"})
    ax.annotate("", xy=(cx0 + 8, tip_y - 2), xytext=(cx0 + 116, rim + 30),
                arrowprops={"arrowstyle": "-|>", "color": t["muted"], "lw": 1.2,
                                "alpha": 0.65, "connectionstyle": "arc3,rad=-0.22"})
    ax.text(cx0 + 96, rim + 52, "$\\varepsilon = A - A^*$",
            fontsize=11, color=t["muted"], ha="center")

    # ---------------- right: the born black hole ----------------------------
    hx, hy, r_h = 712.0, 292.0, 56.0
    ax.add_patch(Circle((hx, hy), r_h, facecolor=t["hole"],
                        edgecolor=t["hole_edge"], lw=1.2, zorder=5))
    ax.add_patch(Circle((hx, hy), r_h + 8.5, facecolor="none",
                        edgecolor=t["gold"], lw=2.2, zorder=6))     # photon ring
    # Hawking quanta: rays leaving the hole (deterministic pattern)
    ang0 = 0.10
    for k in range(18):
        ang = ang0 + k * (2 * np.pi / 18) + 0.09 * np.sin(3.1 * k)
        if 0.55 * np.pi < ang < 0.95 * np.pi:
            continue                    # keep the label zone clean
        r1 = r_h + 16 + 5 * np.cos(2.3 * k)
        r2 = r1 + 15 + 11 * np.sin(1.7 * k + 1.0)
        x1, y1 = hx + r1 * np.cos(ang), hy + r1 * np.sin(ang)
        x2, y2 = hx + r2 * np.cos(ang), hy + r2 * np.sin(ang)
        ax.plot([x1, x2], [y1, y2], color=t["gold_soft"], lw=1.7,
                alpha=0.9, solid_capstyle="round", zorder=4)
        dx, dy = 3.2 * np.cos(ang), 3.2 * np.sin(ang)
        ax.plot([x2, x2 + dx], [y2, y2 + dy], color=t["gold_soft"], lw=1.3,
                alpha=0.7, solid_capstyle="round", zorder=4)
    ax.text(hx, hy + r_h + 30, "$T_H\\propto 1/M$", ha="center",
            fontsize=11, color=t["muted"], zorder=8)
    ax.text(hx, hy - r_h - 34, "$S_{BH}\\propto M^2$",
            ha="center", fontsize=11, color=t["muted"], zorder=8)

    # ---------------- the bridge arc ----------------------------------------
    arrow = FancyArrowPatch((cx0 + 122, rim - 96), (hx - r_h - 30, hy + 40),
                            connectionstyle="arc3,rad=-0.30",
                            arrowstyle="-|>", mutation_scale=24,
                            lw=3.4, color=t["gold"], zorder=7)
    ax.add_patch(arrow)
    ax.text(434, 396,
            "$M_{BH}(\\varepsilon; M_{in}) = M_{in}\\cdot\\tilde f(\\varepsilon)$",
            ha="center", fontsize=15, color=t["gold"], zorder=8)
    ax.text(434, 366, "one dimensionless birth profile  \u00b7  one input scale",
            ha="center", fontsize=10, color=t["muted"], zorder=8)

    # ---------------- wordmark ----------------------------------------------
    ax.text(480, 150, "COLLAPSE \u2013 HAWKING  BRIDGE",
            ha="center", va="center", fontsize=33, color=t["ink"],
            fontweight="bold")
    ax.plot([268, 448], [108, 108], color=t["gold"], lw=1.6, zorder=3)
    ax.plot([512, 692], [108, 108], color=t["gold"], lw=1.6, zorder=3)
    ax.plot([480], [108], marker="D", ms=7.5, color=t["gold"], zorder=4)
    ax.text(480, 74,
            "from the threshold of black-hole birth to black-hole thermodynamics",
            ha="center", fontsize=12, color=t["muted"])
    ax.text(480, 40,
            "A* ladder honest  \u00b7  \u0394\u00b7\u03b3 \u2248 1.27  \u00b7  "
            "floor law 12/N  \u00b7  IVP-15 verified",
            ha="center", fontsize=9.5, color=t["muted"], alpha=0.95)
    return fig


def main():
    os.makedirs(OUT, exist_ok=True)
    for theme in ("light", "dark"):
        fig = draw(theme)
        png = os.path.join(OUT, f"chb_logo_{theme}.png")
        svg = os.path.join(OUT, f"chb_logo_{theme}.svg")
        fig.savefig(png, transparent=True)
        fig.savefig(svg, transparent=True)
        plt.close(fig)
        print("wrote", os.path.relpath(png, ROOT))
        print("wrote", os.path.relpath(svg, ROOT))
    print("DONE: logo variants (light/dark, PNG 600dpi + SVG)")


if __name__ == "__main__":
    main()
