"""
make_logo.py — the package logo: a gold ring bearing the quark trio
(three gold dots on the septinial 2*pi/7 lattice of the Klein quartic
motif), light/dark, PNG (600 dpi) + SVG.
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import style
from matplotlib.patches import Circle

OUT = os.path.join(ROOT, "figures", "logo")


def build_logo(theme):
    tok = style(theme)
    fig = plt.figure(figsize=(8, 2.4), constrained_layout=True)
    fig.patch.set_facecolor(tok["bg"])
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    cx, cy, R = 1.5, 1.5, 1.15
    # the ring
    ring = Circle((cx, cy), R, fill=False, ec=tok["gold"], lw=3.2)
    ax.add_patch(ring)
    # the quark trio on the septinial angles
    for k, ang in enumerate((2 * math.pi / 7, 2 * math.pi / 3, math.pi)):
        x = cx + 0.62 * R * math.cos(ang)
        y = cy + 0.62 * R * math.sin(ang)
        ax.add_patch(Circle((x, y), 0.13, fc=tok["gold"], ec="none"))
        ax.add_patch(Circle((cx - 0.62 * R * math.cos(ang),
                             cy - 0.62 * R * math.sin(ang)),
                            0.075, fc=tok["gold_soft"], ec="none"))
    ax.text(cx, cy - R - 0.28, "$\\pi/2\\ \\pi/3\\ \\pi/7$",
            ha="center", fontsize=8, color=tok["muted"])
    ax.text(3.3, 1.78, "QUARK–HAWKING BRIDGE" if theme == "light"
            else "QUARK–HAWKING BRIDGE",
            fontsize=21, color=tok["ink"], fontweight="bold", va="center")
    ax.text(3.32, 1.12,
            "три поправки · зазор · дверь Ву · трио-ловушка"
            if False else
            "three corrections · the gap · the Wu door · the trio trap",
            fontsize=9.5, color=tok["muted"], va="center")
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ru-subtitle", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for theme in ("light", "dark"):
        fig = build_logo(theme)
        fig.savefig(os.path.join(OUT, f"qhb_logo_{theme}.png"), dpi=600)
        fig.savefig(os.path.join(OUT, f"qhb_logo_{theme}.svg"))
        plt.close(fig)
        print(f"logo {theme}: PNG(600dpi) + SVG")
    return 0


if __name__ == "__main__":
    sys.exit(main())
