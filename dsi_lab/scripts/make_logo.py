#!/usr/bin/env python3
"""
make_logo.py — the official logo and avatars of the DSI laboratory.

"Ink & Gold" emblem drawn with the package's own mathematics:

  LEFT  — the Klein quartic emblem: a regular heptagon {7} with the
          triangular face lines of the {7,3} tiling (PSL(2,7) motif),
          the gold center marking the V=E=F meeting point;
  ARC   — the convergent ladder 1/24 -> 1/25 -> 9/224 rising to c_K3
          (the DSI-4 observation, gold);
  RIGHT — the e-ladder of the partial-isometry class: steps 5/7 (free),
          1 (theorem A) and 2 (theorem C) with the gold e* = 1 line.

Variants: light / dark (theme-aware), PNG @ 600 dpi + SVG (text as paths).
Avatars: square 1024 px emblems (light / dark) for repository avatars.
Deterministic; no external assets.

Run:  python3 scripts/make_logo.py
Out:  logo/dsilab_logo_{light,dark}.{png,svg}
      logo/dsilab_avatar_{light,dark}.png
"""

from __future__ import annotations

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _p in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
):
    try:
        fm.fontManager.addfont(_p)
    except Exception:  # noqa: BLE001 - font registration is best-effort
        pass

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, RegularPolygon

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "path"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "logo")

THEMES = {
    "light": {
        "ink": "#1A1A24",
        "gold": "#8C6D1F",
        "gold_soft": "#C9A84C",
        "muted": "#6B6455",
        "panel": "#F4EFE3",
    },
    "dark": {
        "ink": "#E8E2D0",
        "gold": "#C9A84C",
        "gold_soft": "#E3C878",
        "muted": "#9A9484",
        "panel": "#141420",
    },
}


def draw_heptagon(ax, cx, cy, r, t):
    """The {7} with {7,3} triangular-face hint and the gold center."""
    hept = RegularPolygon(
        (cx, cy),
        7,
        radius=r,
        orientation=np.pi / 7,
        facecolor="none",
        edgecolor=t["ink"],
        lw=3.2,
        zorder=4,
    )
    ax.add_patch(hept)
    # triangular tiling hint: chords from every second vertex
    ang0 = np.pi / 7
    verts = [
        (
            cx + r * np.sin(ang0 + 2 * np.pi * k / 7),
            cy + r * np.cos(ang0 + 2 * np.pi * k / 7),
        )
        for k in range(7)
    ]
    for i in range(7):
        j = (i + 2) % 7
        ax.plot(
            [verts[i][0], verts[j][0]],
            [verts[i][1], verts[j][1]],
            color=t["ink"],
            lw=1.1,
            alpha=0.45,
            zorder=3,
        )
    ax.add_patch(
        Circle((cx, cy), r * 0.16, facecolor=t["gold"], edgecolor="none", zorder=6)
    )
    for k in range(7):
        ax.plot(
            [verts[k][0]],
            [verts[k][1]],
            marker="o",
            ms=4.5,
            color=t["gold_soft"],
            zorder=5,
        )


def draw_convergent_arc(ax, t):
    """The convergent ladder 1/24 -> 1/25 -> 9/224 rising to c_K3."""
    xs = np.linspace(232.0, 470.0, 120)
    base, top = 210.0, 330.0
    ax.plot(
        xs,
        base + (top - base) * (xs - xs[0]) / (xs[-1] - xs[0]),
        color=t["ink"],
        lw=1.4,
        alpha=0.35,
        zorder=2,
    )
    ladder = [(250.0, 232.0, "1/24"), (330.0, 256.0, "1/25"), (428.0, 292.0, "9/224")]
    for x, y, lab in ladder:
        ax.plot([x], [y], marker="D", ms=8, color=t["gold"], zorder=6)
        ax.text(x, y - 26, lab, ha="center", fontsize=10.5, color=t["muted"], zorder=7)
    arrow = FancyArrowPatch(
        (444.0, 300.0),
        (500.0, 336.0),
        connectionstyle="arc3,rad=0.18",
        arrowstyle="-|>",
        mutation_scale=22,
        lw=3.0,
        color=t["gold"],
        zorder=7,
    )
    ax.add_patch(arrow)
    ax.text(
        472.0,
        352.0,
        "$c_{K3} = 9/224$",
        ha="center",
        fontsize=14,
        color=t["gold"],
        zorder=8,
    )
    ax.text(
        352.0,
        188.0,
        "convergents of the measured c_K3",
        ha="center",
        fontsize=9.5,
        color=t["muted"],
        zorder=8,
    )


def draw_e_ladder(ax, t):
    """The e-ladder: 5/7 (free), 1 (theorem A), 2 (theorem C)."""
    x0, w = 620.0, 46.0
    steps = (
        (0.0, 5.0 / 7.0, "5/7", t["muted"]),
        (1.0, 1.0, "1", t["ink"]),
        (2.0, 2.0, "2", t["ink"]),
    )
    scale = 52.0
    y_base = 200.0
    for dx, val, lab, col in steps:
        h = val * scale
        ax.add_patch(
            plt.Rectangle(
                (x0 + dx * (w + 14.0), y_base),
                w,
                h,
                facecolor=col,
                edgecolor="none",
                alpha=0.85,
                zorder=4,
            )
        )
        ax.text(
            x0 + dx * (w + 14.0) + w / 2,
            y_base + h + 13.0,
            lab,
            ha="center",
            fontsize=11,
            color=t["muted"],
            zorder=6,
        )
    ax.plot(
        [x0 - 10.0, x0 + 3 * (w + 14.0)],
        [y_base + scale, y_base + scale],
        color=t["gold"],
        lw=2.2,
        ls="--",
        zorder=5,
    )
    ax.text(
        x0 - 24.0,
        y_base + scale - 20.0,
        "$e^* = 1$",
        ha="right",
        fontsize=12.5,
        color=t["gold"],
        zorder=7,
    )
    ax.plot(
        [x0 - 12.0, x0 + 3 * (w + 14.0)],
        [y_base, y_base],
        color=t["ink"],
        lw=2.0,
        zorder=3,
    )
    ax.text(
        x0 + (w + 14.0),
        y_base - 26.0,
        "the e-ladder: 5/7 -> 1 -> 2",
        ha="center",
        fontsize=9.5,
        color=t["muted"],
        zorder=8,
    )


def draw_banner(theme: str):
    t = THEMES[theme]
    fig = plt.figure(figsize=(9.6, 4.6), dpi=600)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 960)
    ax.set_ylim(0, 460)
    ax.axis("off")

    draw_heptagon(ax, 128.0, 300.0, 88.0, t)
    draw_convergent_arc(ax, t)
    draw_e_ladder(ax, t)

    # ---------------- wordmark ----------------------------------------------
    ax.text(
        480.0,
        108.0,
        "DSI  LAB",
        ha="center",
        va="center",
        fontsize=34,
        color=t["ink"],
        fontweight="bold",
    )
    ax.plot([268.0, 448.0], [66.0, 66.0], color=t["gold"], lw=1.6, zorder=3)
    ax.plot([512.0, 692.0], [66.0, 66.0], color=t["gold"], lw=1.6, zorder=3)
    ax.plot([480.0], [66.0], marker="D", ms=7.5, color=t["gold"], zorder=4)
    ax.text(
        480.0,
        34.0,
        "dynamics of invariants \u00b7 seven experiments on the "
        "b\u2013C / a\u2013C framework",
        ha="center",
        fontsize=11.5,
        color=t["muted"],
    )
    return fig


def draw_avatar(theme: str):
    """Square 1024 px emblem: heptagon + convergent spike + DSI monogram."""
    t = THEMES[theme]
    fig = plt.figure(figsize=(10.24, 10.24), dpi=100)
    fig.patch.set_facecolor(t["panel"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1024)
    ax.set_ylim(0, 1024)
    ax.axis("off")

    # halo ring
    ax.add_patch(
        Circle(
            (512.0, 610.0),
            330.0,
            facecolor="none",
            edgecolor=t["gold"],
            lw=3.0,
            alpha=0.55,
            zorder=2,
        )
    )
    draw_heptagon(ax, 512.0, 610.0, 268.0, t)

    # convergent spike: three gold diamonds rising along the right edge
    for x, y, ms in ((690.0, 480.0, 9.0), (742.0, 566.0, 10.5), (800.0, 668.0, 12.0)):
        ax.plot([x], [y], marker="D", ms=ms, color=t["gold_soft"], zorder=6)

    ax.text(
        512.0,
        172.0,
        "DSI LAB",
        ha="center",
        va="center",
        fontsize=64,
        color=t["ink"],
        fontweight="bold",
    )
    ax.plot([352.0, 472.0], [108.0, 108.0], color=t["gold"], lw=2.2, zorder=3)
    ax.plot([552.0, 672.0], [108.0, 108.0], color=t["gold"], lw=2.2, zorder=3)
    ax.plot([512.0], [108.0], marker="D", ms=10.0, color=t["gold"], zorder=4)
    return fig


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for theme in ("light", "dark"):
        fig = draw_banner(theme)
        for ext in ("png", "svg"):
            path = os.path.join(OUT, f"dsilab_logo_{theme}.{ext}")
            fig.savefig(path, transparent=True)
            print("wrote", os.path.relpath(path, ROOT))
        plt.close(fig)
        fig = draw_avatar(theme)
        path = os.path.join(OUT, f"dsilab_avatar_{theme}.png")
        fig.savefig(path)
        plt.close(fig)
        print("wrote", os.path.relpath(path, ROOT))
    print("DONE: logo (light/dark, PNG 600dpi + SVG) + avatars 1024px")


if __name__ == "__main__":
    main()
