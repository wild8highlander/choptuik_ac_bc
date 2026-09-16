#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИГУРА «Задача Чоптюка»: универсальный массовый скейлинг (иллюстрация) и
сравнение измеренного критического показателя с кандидатом фреймворка.

Панель (a): схематический лог-лог скейлинг M_BH ∝ (p − p*)^γ для двух
различных семейств начальных данных — универсальность (синтетические данные,
чистая иллюстрация к постановке Чоптюка 1993).

Панель (b): измеренное γ ≈ 0.374 (Чоптюк 1993; одна неустойчивая мода,
λ₀ ≈ 2.674 ⇒ γ = 1/λ₀) против кандидата фреймворка b_Ch = 1 − cos(2π/7)
≈ 0.3765 — зазор +0.67%.

Запуск: python3 fig_choptuik.py   →  fig_ru/fig_choptuik.png, fig_en/...
"""
import math
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from figlabels import L

GAMMA = 0.374          # Чоптюк 1993 (универсальный показатель)
B_CH = 1 - math.cos(2 * math.pi / 7)   # ≈ 0.37651


def main():
    for lang in ("ru", "en"):
        t = L[lang]
        lang_dir = os.path.join(BASE, f"fig_{lang}")
        os.makedirs(lang_dir, exist_ok=True)

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.font_manager as fm
        for fp in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            if os.path.exists(fp):
                fm.fontManager.addfont(fp)
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
        plt.rcParams["axes.unicode_minus"] = False

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.9),
                                       constrained_layout=True)
        # (a) универсальный скейлинг (синтетика)
        rng = np.random.default_rng(11)
        eps = np.linspace(-6.5, -0.3, 220)          # ln(p − p*)
        for off, name, col in ((0.00, t["ch_fam1"], "#1e6091"),
                               (0.35, t["ch_fam2"], "#b45309")):
            y = GAMMA * eps + off + 0.02 * np.sin(3.4 * eps) \
                + 0.012 * rng.standard_normal(eps.size)
            ax1.plot(eps, y, ".", color=col, ms=3.2, alpha=0.75, label=name)
            ax1.plot(eps, GAMMA * eps + off, "-", color=col, lw=1.6, alpha=0.9)
        ax1.text(-6.1, GAMMA * (-6.1) + 1.15, t["ch_slope"], fontsize=11,
                 color="#333333", rotation=0)
        ax1.set_xlabel(t["ch_xlabel"])
        ax1.set_ylabel(t["ch_ylabel"])
        ax1.set_title(t["ch_title"], fontsize=10.5)
        ax1.legend(loc="upper left", fontsize=9)
        # (b) константы
        vals = [GAMMA, B_CH, 1 / 2.674]
        names = [t["ch_gamma"], t["ch_bch"], t["ch_inv"]]
        cols = ["#0e7c66", "#b45309", "#1e6091"]
        bars = ax2.barh(names, vals, color=cols, alpha=0.85, height=0.5)
        for b, v in zip(bars, vals):
            ax2.text(v + 0.004, b.get_y() + b.get_height() / 2, f"{v:.4f}",
                     va="center", fontsize=10)
        ax2.axvline(GAMMA, color="#0e7c66", ls="--", lw=1.3)
        ax2.set_xlim(0, 0.46)
        ax2.set_xlabel("γ")
        ax2.set_title(t["ch_const_title"], fontsize=10.5)
        ax2.invert_yaxis()
        fig.savefig(os.path.join(lang_dir, "fig_choptuik.png"), dpi=300)
        plt.close(fig)
        print(f"[OK] {lang_dir}/fig_choptuik.png")


if __name__ == "__main__":
    main()
