#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Графики для прямого решения задачи Чоптюка (RU + EN, стиль dsi_lab)."""
import json
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
RESULTS = os.path.join(BASE, "results")

TITLES = {
    "ru": {
        "conv_title": "Валидация: решение Робертса–Оширо",
        "conv_ylabel": "макс. ошибка",
        "conv_xlabel": "число узлов N",
        "conv_slope2": "наклон 2 (2-й порядок)",
        "scal_title": "Задача Чоптюка: массовый скейлинг",
        "scal_ylabel": "M_BH (масса горизонта)",
        "scal_xlabel": "A − A*",
        "scal_floor": "пол разрешения фиксированной сетки",
        "scal_gamma": "универсальный закон (γ = 0.374)",
        "evol_title_a": "субкритический (дисперсия)",
        "evol_title_b": "сверхкритический (горизонт)",
        "evol_ylabel": "2m/r",
        "evol_xlabel": "r",
        "evol_legend_m": "масса Мизнера–Шарпа (2m/r)",
        "lang_file": "рис",
    },
    "en": {
        "conv_title": "Validation: Roberts–Oshiro solution",
        "conv_ylabel": "max error",
        "conv_xlabel": "number of nodes N",
        "conv_slope2": "slope 2 (second order)",
        "scal_title": "Choptuik problem: mass scaling",
        "scal_ylabel": "M_BH (apparent horizon mass)",
        "scal_xlabel": "A − A*",
        "scal_floor": "fixed-grid resolution floor",
        "scal_gamma": "universal law (γ = 0.374)",
        "evol_title_a": "subcritical (dispersal)",
        "evol_title_b": "supercritical (black hole)",
        "evol_ylabel": "2m/r",
        "evol_xlabel": "r",
        "evol_legend_m": "Misner–Sharp mass (2m/r)",
        "lang_file": "fig",
    },
}


def main():
    import warnings
    warnings.filterwarnings("ignore")
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

    # --- данные ---------------------------------------------------------------
    rob = json.load(open(os.path.join(RESULTS, "roberts_test.json")))
    scal = json.load(open(os.path.join(RESULTS, "choptuik_scaling.json")))
    pts = [(p["eps"], p["M"]) for p in scal["scaling"]["points"] if 0 < p["M"] < 0.05]
    b_ch = scal["references"]["b_Ch"]

    # недостающие данные эволюции: два быстрых забега со снимками
    from solver import DoubleNullSolver, GaussianPulseData, SolverConfig
    snaps = {}
    for tag, A in (("sub", 0.05), ("super", 0.25)):
        data = GaussianPulseData(A=A, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
        cfg = SolverConfig(n_u=1200, n_v=1200, u_range=(-1.0, 1.05),
                           v_range=(0.0, 1.0), monitor_every=10 ** 9)
        sol = DoubleNullSolver(cfg, data)
        keep = []
        orig = sol._do_step
        def step(st, j, keep=keep, orig=orig, sol=sol):
            stn = orig(st, j)
            if j % 240 == 0:
                r = stn["r"]
                phys = r > 2 * sol.du
                tmr = np.where(phys, 2 * stn["m"] / np.where(phys, r, 1), 0.0)
                keep.append((r.copy(), tmr.copy(), float(sol.v[j])))
            return stn
        sol._do_step = step
        sol.run(verbose=False)
        snaps[tag] = keep

    for lang in ("ru", "en"):
        t = TITLES[lang]
        d_out = os.path.join(BASE, "figures", f"fig_{lang}")
        os.makedirs(d_out, exist_ok=True)

        # --- 1. Сходимость Робертса -------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6),
                                       constrained_layout=True)
        ns = [r["n_u"] for r in rob]
        er = [r["err_r"] for r in rob]
        eP = [r["err_Phi"] for r in rob]
        ax1.loglog(ns, er, "o-", color="#1e6091", lw=1.8, label="r")
        ax1.loglog(ns, eP, "s-", color="#b45309", lw=1.8, label=r"$\Phi$")
        ref = er[0] * (ns[0] / np.array(ns)) ** 2
        ax1.loglog(ns, ref, "--", color="#888888", lw=1.4, label=t["conv_slope2"])
        ax1.set_xlabel(t["conv_xlabel"])
        ax1.set_ylabel(t["conv_ylabel"])
        ax1.set_title(t["conv_title"], fontsize=11)
        ax1.legend(fontsize=9)
        ax1.grid(alpha=0.3, which="both")

        ax2.plot(ns, [r["c1_max"] for r in rob], "o-", color="#0e7c66",
                 lw=1.8, label="C1")
        ax2.set_xlabel(t["conv_xlabel"])
        ax2.set_ylabel("max |C1|")
        ax2.set_yscale("log")
        ax2.grid(alpha=0.3)
        ax2.set_title("Контроль связи C1 / constraint C1", fontsize=11)
        fig.savefig(os.path.join(d_out, "fig_validation.png"), dpi=300)
        plt.close(fig)

        # --- 2. Скейлинг -------------------------------------------------------
        fig, ax = plt.subplots(figsize=(7.4, 5.2), constrained_layout=True)
        e = np.array([p[0] for p in pts])
        M = np.array([p[1] for p in pts])
        ax.loglog(e, M, "o", color="#1e6091", ms=7, label="эксперимент / experiment")
        # универсальный закон, нормированный на первую точку
        gg = 0.374
        ref = M[0] * (e / e[0]) ** gg
        ax.loglog(e[e > 3e-3], ref[e > 3e-3], "--", color="#0e7c66", lw=1.6,
                  label=t["scal_gamma"])
        floor = np.full_like(e, np.median(M[e < 1e-2]))
        ax.loglog(e, floor, ":", color="#b45309", lw=1.8, label=t["scal_floor"])
        ax.axhline(b_ch * 0.014, color="#888888", lw=0.8, alpha=0.5)
        ax.set_xlabel(t["scal_xlabel"])
        ax.set_ylabel(t["scal_ylabel"])
        ax.set_title(f"{t['scal_title']},  A* = {scal['a_star']:.6f}",
                     fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3, which="both")
        fig.savefig(os.path.join(d_out, "fig_scaling.png"), dpi=300)
        plt.close(fig)

        # --- 3. Эволюция: суб- и сверхкритическая ------------------------------
        fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6),
                                 constrained_layout=True, sharey=True)
        for ax, tag, ttl in ((axes[0], "sub", t["evol_title_a"]),
                             (axes[1], "super", t["evol_title_b"])):
            for k, (r, tmr, v) in enumerate(snaps[tag]):
                ax.plot(r, tmr, lw=1.4, alpha=0.85,
                        color=plt.cm.viridis(k / max(len(snaps[tag]) - 1, 1)),
                        label=f"v = {v:.2f}" if k % 2 == 0 else None)
            ax.axhline(1.0, color="#b45309", ls="--", lw=1.2)
            ax.set_xlabel(t["evol_xlabel"])
            ax.set_title(ttl, fontsize=11)
            ax.set_xlim(0, 0.9)
            ax.set_ylim(0, 1.6)
            ax.grid(alpha=0.3)
        axes[0].set_ylabel(t["evol_ylabel"])
        axes[0].legend(fontsize=8, loc="upper right")
        fig.savefig(os.path.join(d_out, "fig_evolution.png"), dpi=300)
        plt.close(fig)

        print(f"[OK] {d_out}: fig_validation, fig_scaling, fig_evolution")


if __name__ == "__main__":
    main()
