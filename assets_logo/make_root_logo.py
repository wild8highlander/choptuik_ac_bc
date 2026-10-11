#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Root repository logo generator — choptuik_ac_bc.
Style: "Ink & Gold" (same family as Collapse Hawking Bridge logo).
Output: assets/logo/choptyuk_logo_{dark,light}.png (+ .svg)
Provenance: pure matplotlib geometry, no RNG, deterministic.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, Circle
import numpy as np
import os

OUT = "/home/z/my-project/repo_choptuik/assets/logo"
os.makedirs(OUT, exist_ok=True)

THEMES = {
    "dark": dict(bg="#0d0b08", ink="#f2ead8", gold="#d4af37", gold2="#9a7b1e",
                 grey="#8a8578", deep="#1a1712"),
    "light": dict(bg="#faf6ec", ink="#1c1a15", gold="#a8811c", gold2="#6e5510",
                  grey="#6e6a5e", deep="#e7dfc9"),
}

PHASES = [("/2", np.pi / 2), ("/3", np.pi / 3), ("/7", np.pi / 7)]


def draw_logo(theme: str):
    T = THEMES[theme]
    fig = plt.figure(figsize=(20, 6.25), dpi=150)
    fig.patch.set_facecolor(T["bg"])

    # ---------- left panel: three spinor sectors ----------
    ax = fig.add_axes([0.005, 0.02, 0.22, 0.96])
    ax.set_facecolor(T["bg"])
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.35, 1.55)
    ax.axis("off")
    radii = [1.18, 0.86, 0.54]
    cols = [T["gold"], T["gold2"], T["grey"]]
    for (lbl, ph), r, c in zip(PHASES, radii, cols):
        ax.add_patch(Circle((0, 0), r, fill=False, lw=1.1, ec=c, alpha=0.35))
        ax.add_patch(Arc((0, 0), 2 * r, 2 * r, theta1=-90.0,
                         theta2=-90.0 + np.degrees(ph), lw=4.2, ec=c))
        ax.plot([0, r * np.cos(np.radians(-90 + np.degrees(ph)))],
                [0, r * np.sin(np.radians(-90 + np.degrees(ph)))],
                lw=1.4, c=c, alpha=0.9)
        ax.text(r * 0.72 * np.cos(np.radians(-90 + np.degrees(ph) / 2)) + 0.10,
                r * 0.72 * np.sin(np.radians(-90 + np.degrees(ph) / 2)),
                rf"$\pi{lbl}$", color=c, fontsize=15, ha="left", va="center")
    ax.text(0, 1.44, "septinial family", color=T["ink"], fontsize=13.5,
            ha="center", style="italic")
    ax.plot([0], [0], marker="o", ms=6, color=T["gold"], zorder=5)

    # ---------- right panel: collapse -> black hole bridge ----------
    ax2 = fig.add_axes([0.775, 0.02, 0.22, 0.96])
    ax2.set_facecolor(T["bg"])
    ax2.set_xlim(-1.5, 1.9)
    ax2.set_ylim(-1.35, 1.55)
    ax2.axis("off")
    x = np.linspace(-1.35, 0.75, 240)
    for amp, c, a in [(0.92, T["grey"], 0.8), (1.10, T["gold2"], 0.9), (1.26, T["gold"], 1.0)]:
        y = amp * np.exp(-((x + 0.3) ** 2) / 0.16)
        y = -0.28 + y * 0.72
        ax2.plot(x, y, lw=2.0, color=c, alpha=a)
    arrow = FancyArrowPatch((0.52, 0.12), (1.02, 0.42), arrowstyle="-|>",
                            mutation_scale=26, lw=2.6, color=T["gold"])
    ax2.add_patch(arrow)
    ax2.add_patch(Circle((1.34, 0.52), 0.30, fill=True, fc=T["bg"], ec=T["gold"], lw=2.6))
    hole_fc = "#000000" if theme == "dark" else "#d9d0b8"
    ax2.add_patch(Circle((1.34, 0.52), 0.22, fill=True, fc=hole_fc,
                         ec=T["gold2"], lw=1.0))
    for ang in range(0, 360, 30):
        r1, r2 = 0.36, 0.50
        ax2.plot([1.34 + r1 * np.cos(np.radians(ang)), 1.34 + r2 * np.cos(np.radians(ang))],
                 [0.52 + r1 * np.sin(np.radians(ang)), 0.52 + r2 * np.sin(np.radians(ang))],
                 lw=1.6, color=T["gold"], alpha=0.85)
    ax2.text(1.34, -0.08, r"$T_H\propto 1/M$", color=T["ink"], fontsize=12.5, ha="center")
    ax2.text(1.34, -0.34, r"$S_{BH}\propto M^2$", color=T["ink"], fontsize=12.5, ha="center")
    ax2.text(-0.31, 1.38, r"$M_{BH}(\varepsilon)=M_{in}\cdot\tilde f(\varepsilon)$",
             color=T["gold"], fontsize=15, ha="center")
    ax2.text(-0.31, 1.13, "critical collapse", color=T["grey"], fontsize=11.5,
             ha="center", style="italic")

    # ---------- center: title block ----------
    axc = fig.add_axes([0.225, 0.02, 0.55, 0.96])
    axc.set_facecolor(T["bg"])
    axc.set_xlim(0, 1)
    axc.set_ylim(0, 1)
    axc.axis("off")
    axc.text(0.5, 0.66, "CHOPTUIK  AC–BC", color=T["ink"], fontsize=47,
             ha="center", va="center", fontweight="bold",
             fontfamily="DejaVu Sans")
    axc.plot([0.30, 0.46], [0.545, 0.545], lw=2.0, color=T["gold"])
    axc.plot([0.54, 0.70], [0.545, 0.545], lw=2.0, color=T["gold"])
    axc.plot([0.50], [0.545], marker="D", ms=9, color=T["gold"])
    axc.text(0.5, 0.40, "Spinor corrections b-C & a-C  ·  the Choptyuk problem\n"
                       "Direct Einstein programme  ·  machine-verified",
             color=T["gold"], fontsize=17.5, ha="center", va="center", linespacing=1.7)
    axc.text(0.5, 0.16, r"$\delta_A=\pi/2\ \ \delta_B=\pi/3\ \ \delta_C=\pi/7$"
             r"$\ \ \cdot\ \ b_{Ch}=1-\cos(2\pi/7)\ \ \cdot\ \ \Delta\cdot\gamma\approx 1.27$",
             color=T["grey"], fontsize=14.5, ha="center", va="center")

    for ext in ("png", "svg"):
        path = os.path.join(OUT, f"choptyuk_logo_{theme}.{ext}")
        fig.savefig(path, facecolor=T["bg"])
        print("saved", path)
    plt.close(fig)


if __name__ == "__main__":
    for th in ("dark", "light"):
        draw_logo(th)
