#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""График спинор-анализа: парности центра (A/B замыканий) + соотношения
фреймворка R1-R4. Версии RU и EN, 300 dpi."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
FIG_RU = os.path.join(BASE, "figures", "fig_ru")
FIG_EN = os.path.join(BASE, "figures", "fig_en")
os.makedirs(FIG_RU, exist_ok=True)
os.makedirs(FIG_EN, exist_ok=True)

with open(os.path.join(RESULTS, "spinor_analysis.json"), encoding="utf-8") as fh:
    SP = json.load(fh)

B_CH = SP["spinor_framework"]["b_Ch = 1-cos(2pi/7)"]
D_SP = SP["spinor_framework"]["Delta_sp = 7*pi/30"]
G_LIT = SP["spinor_framework"]["gamma_lit"]
D_LIT = SP["spinor_framework"]["delta_lit"]
R3_SP = SP["spinor_framework"]["R3_omega_wiggle = 4*pi/Delta_sp = 120/7"]
R3_LIT = SP["spinor_framework"]["omega_wiggle_lit = 4*pi/Delta_lit"]
R4_SP = SP["spinor_framework"]["R4_product_gamma*Delta_spinor"]
R4_LIT = SP["spinor_framework"]["R4_product_gamma*Delta_lit"]

mp = SP["mirror_parity"]
pq_clamp = mp["clamp_v2"]["inner_ring"]["pq_even"]
pq_reg = mp["regular_v3"]["inner_ring"]["pq_even"]

L = {
    "ru": {
        "title1": "Спинорный сектор центра: чётная добавка (p+q)\n"
                  "внутреннее кольцо, v = 0.55, A = 0.075",
        "x1": ["клэмп v2\n(t=s, спинорный\nсектор убит)",
               "regular v3\n(связка наклонов\ns$_1$−t$_1$ = −2a)"],
        "y1": "нарушение чётности (p+q), отн. ед.",
        "title2": "Соотношения спинор-фреймворка:\nрасхождения с литературой",
        "labels2": ["R1: γ = b_Ch\n= 1−cos(2π/7)",
                    "R2: Δ = 7π/30",
                    "R3: ω = 4π/Δ\n= 120/7",
                    "R4: γ·Δ\n(произведение)"],
        "y2": "расхождение, %",
        "ann": "R1–R3: ~0.6–0.7%;\nв R4 расхождения\nкомпенсируются (0.04%)",
        "file": "fig_spinor.png",
    },
    "en": {
        "title1": "Spinor sector of the center: even part of (p+q)\n"
                  "inner ring, v = 0.55, A = 0.075",
        "x1": ["clamp v2\n(t=s, spinor\nsector killed)",
               "regular v3\n(slope link\ns$_1$−t$_1$ = −2a)"],
        "y1": "(p+q) even-parity violation, rel. units",
        "title2": "Spinor-framework relations:\ndeviations from literature",
        "labels2": ["R1: γ = b_Ch\n= 1−cos(2π/7)",
                    "R2: Δ = 7π/30",
                    "R3: ω = 4π/Δ\n= 120/7",
                    "R4: γ·Δ\n(product)"],
        "y2": "deviation, %",
        "ann": "R1–R3: ~0.6–0.7%;\nin R4 the deviations\ncancel (0.04%)",
        "file": "fig_spinor.png",
    },
}

for lang, T in L.items():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6),
                                   constrained_layout=True)
    # --- панель 1: парность p+q ------------------------------------------
    vals = [pq_clamp, pq_reg]
    bars = ax1.bar(T["x1"], vals, width=0.55,
                   color=["#c0504d", "#4f81bd"], edgecolor="black", lw=0.6)
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}",
                 ha="center", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, 1.18)
    ax1.set_ylabel(T["y1"], fontsize=11)
    ax1.set_title(T["title1"], fontsize=11)
    ax1.grid(axis="y", alpha=0.3)
    ax1.axhline(1.0, color="grey", ls=":", lw=0.8)
    # --- панель 2: R1-R4 ---------------------------------------------------
    devs = [abs(B_CH - G_LIT) / G_LIT * 100,
            abs(D_SP - D_LIT) / D_LIT * 100,
            abs(R3_SP - R3_LIT) / R3_LIT * 100,
            abs(R4_SP - R4_LIT) / R4_LIT * 100]
    colors = ["#4f81bd", "#4f81bd", "#4f81bd", "#9bbb59"]
    bars = ax2.bar(T["labels2"], devs, width=0.6, color=colors,
                   edgecolor="black", lw=0.6)
    for b, v in zip(bars, devs):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}%",
                 ha="center", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, max(devs) * 1.35)
    ax2.set_ylabel(T["y2"], fontsize=11)
    ax2.set_title(T["title2"], fontsize=11)
    ax2.grid(axis="y", alpha=0.3)
    ax2.text(0.98, 0.95, T["ann"], transform=ax2.transAxes, ha="right",
             va="top", fontsize=9.5,
             bbox=dict(boxstyle="round", fc="#f2f2f2", ec="grey"))
    out = FIG_RU if lang == "ru" else FIG_EN
    fig.savefig(os.path.join(out, T["file"]), dpi=300)
    plt.close(fig)
    print(f"saved: {os.path.join(out, T['file'])}")
