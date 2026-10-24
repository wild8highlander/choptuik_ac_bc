"""Certificate channel flow diagram — formal_choptuik Volume III.

Ink & Gold light palette, consistent with python/scripts/generate_figures.py.
Deterministic: no random elements. Drawn with pure matplotlib primitives.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans"],
    "axes.unicode_minus": False,
    "savefig.dpi": 300,
})

# Ink & Gold light palette (matches the series figures)
BG, TEXT, MUTED = "#FAF8F4", "#2B2A28", "#6B6455"
GRID, BAND = "#DDD6C8", "#EFE9DC"
GOLD, VIOLET, CYAN = "#B08A3E", "#7A6BC0", "#3E93B5"
GREEN, RED, FIT = "#6E9481", "#B05252", "#8A6A24"

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/fig_cert_channel_{LANG}.png"

T = {
    "en": {
        "title": "The certificate channel: exact rationals end to end",
        "producer": "certify.py\n(LAPACK compute,\noutward rounding)",
        "json": "bridge/certificates/\n*.json\n(exact decimal rationals)",
        "gen": "Choptuik.Bridge.Generated\n(norm_num over \u211a,\nmachine-checked)",
        "checks": "check suites\nspectrum/newton/scaling/\ninterval *_generated",
        "disch": "Choptuik.Bridge.Discharge\nrobustness theorems",
        "heads": ("bridge_unique_unstable_mode \u00b7 correction_root_in_band\n"
                  "correction_band_image_sound \u00b7 scaling_agreement"),
        "lane1": "Python wing (producer)",
        "lane2": "committed artifacts",
        "lane3": "Lean 4 wing (consumer)",
        "note": "no float ever crosses this border",
    },
    "ru": {
        "title": "Канал сертификатов: точные рациональные от края до края",
        "producer": "certify.py\n(вычисление LAPACK,\nокругление наружу)",
        "json": "bridge/certificates/\n*.json\n(точные десятичные рациональные)",
        "gen": "Choptuik.Bridge.Generated\n(norm_num над \u211a,\nмашинно проверено)",
        "checks": "check-сьюты\nspectrum/newton/scaling/\ninterval *_generated",
        "disch": "Choptuik.Bridge.Discharge\nтеоремы робастности",
        "heads": ("bridge_unique_unstable_mode \u00b7 correction_root_in_band\n"
                  "correction_band_image_sound \u00b7 scaling_agreement"),
        "lane1": "Python-крыло (производитель)",
        "lane2": "коммитимые артефакты",
        "lane3": "Lean-крыло (потребитель)",
        "note": "ни одно float-число не пересекает эту границу",
    },
}[LANG]

fig, ax = plt.subplots(figsize=(10.4, 6.2), constrained_layout=True)
ax.set_xlim(0, 100)
ax.set_ylim(0, 62)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def box(x, y, w, h, text, fc, ec, fs=10.5, tc=TEXT, bold=False):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
        linewidth=1.4, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=tc, fontweight="bold" if bold else "normal")


def arrow(x0, y0, x1, y1, color, lw=2.0):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16,
        linewidth=lw, color=color, shrinkA=2, shrinkB=2))


ax.text(50, 59, T["title"], ha="center", va="center",
        fontsize=15, color=TEXT, fontweight="bold")

# lane labels
ax.text(16, 51.5, T["lane1"], ha="center", fontsize=10.5, color=MUTED, style="italic")
ax.text(50, 51.5, T["lane2"], ha="center", fontsize=10.5, color=MUTED, style="italic")
ax.text(84, 51.5, T["lane3"], ha="center", fontsize=10.5, color=MUTED, style="italic")
for x in (33, 67):
    ax.plot([x, x], [4, 50], color=GRID, lw=1.0, linestyle=(0, (4, 4)), zorder=0)

# producer
box(3, 38, 26, 10, T["producer"], BAND, GOLD, fs=10.5)
# JSON artifacts
box(37, 38, 26, 10, T["json"], "#F3EFE6", CYAN, fs=10)
# Generated.lean
box(71, 38, 26, 10, T["gen"], BAND, VIOLET, fs=10)
# check suites
box(71, 23, 26, 9, T["checks"], "#F3EFE6", VIOLET, fs=10)
# discharge
box(71, 10, 26, 9, T["disch"], BAND, GREEN, fs=10.5)
# headlines
box(14, 3.5, 83, 5.4, T["heads"], "#F6F2E8", FIT, fs=9.6)

arrow(29.5, 43, 36.4, 43, GOLD)
arrow(63.5, 43, 70.4, 43, CYAN)
arrow(84, 37.4, 84, 32.6, VIOLET)
arrow(84, 22.4, 84, 19.6, GREEN)
arrow(70.4, 14.5, 58, 9.6, GREEN)

# border note
ax.annotate("", xy=(66.6, 31), xytext=(66.6, 36.5),
            arrowprops=dict(arrowstyle="-", color=RED, lw=0))
ax.text(50, 33.4, "[ " + T["note"] + " ]", ha="center", fontsize=9.6,
        color=RED, style="italic",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#F7ECEC",
                  edgecolor=RED, linewidth=0.9))

fig.savefig(OUT, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
print("written", OUT)
