#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Рисунки гексагонального Пуанкаре-цикла: колесо станций, динамика/книга,
честное замыкание. Версии RU и EN, 300 dpi."""
import json
import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, RegularPolygon

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
FIG_RU = os.path.join(BASE, "figures", "fig_ru")
FIG_EN = os.path.join(BASE, "figures", "fig_en")
DL = "/home/z/my-project/download"
os.makedirs(FIG_RU, exist_ok=True)
os.makedirs(FIG_EN, exist_ok=True)
os.makedirs(DL, exist_ok=True)

with open(os.path.join(RESULTS, "hexcycle.json"), encoding="utf-8") as fh:
    HC = json.load(fh)
CL, NM = HC["closure"], HC["numeric"]

C_CORE = "#1e3a5f"      # UV-пара
C_RING = "#b45309"      # Mdef-кольцо
C_OK = "#0e7c66"
C_BAND = "#9fc5e8"

TAU3, TAU5 = 2.25, 0.5625
KAPPA = CL["kappa_cyc"]
DELTA = CL["Delta_cyc"]
D_GHS = 3.44


def station_shape(k, xi):
    ax = np.abs(xi)
    if k in (0, 1):
        return 1.0 - ax
    if k == 2:
        return np.maximum(0.25, 1.0 - ax)
    if k == 3:
        return 1.0 - xi**2
    if k == 4:
        return xi**2 - 1.0
    # k == 5: пирамида нового масштаба (лог-замыкание); форму рисуем схематично,
    # амплитудный множитель x exp(-Delta_cyc) = 0.032 указан в подписи панели
    return 1.0 - ax


L = {
    "ru": {
        "wheel_title": ("Гексагональный Пуанкаре-цикл трансформаций:\n"
                        "пирамида → конус → усечённый конус → парабола → чаша "
                        "→ лог-замыкание → пирамида\n"
                        "(в 1D-сечении пирамида и конус совпадают — различие "
                        "азимутальное: 4 грани против вращения)"),
        "center1": "ДВЕ КНИГИ ЦИКЛА\n\n"
                   "амплитудная (per станция):\n"
                   "CORE: ln(3/2), RING: ln(4/3)\n"
                   r"$\kappa_{cyc}=\ln(64/9)=%.4f$" % KAPPA + "\n\n"
                   "часы эха (per сторона):\n"
                   r"$-\ln\tau_5=\ln(16/9)$" + "\n"
                   r"$\Delta_{cyc}=6\ln(16/9)=%.4f$" % DELTA,
        "station_names": ["0. Пирамида", "1. Конус", "2. Усечённый конус",
                          "3. Параболический пивот", "4. Чаша",
                          "5. Лог-замыкание (×e$^{-Δ_cyc}$)"],
        "station_steps": [r"шаг $\ln(3/2)$", r"шаг $\ln(3/2)$",
                          r"шаг $\ln(4/3)$, кольцо 4:3",
                          r"мультипликатор 1 (пивот)",
                          r"мультипликатор $-1$ (переворот)",
                          r"$(2/\sqrt{3})^2=4/3$"],
        "zone_uv": "зона UV[ξ³]: τ₃ = (3/2)² = 9/4",
        "zone_mdef": "зона Mdef[ξ⁵]: τ₅ = (3/4)² = 9/16",
        "dyn_title": ("Уравнения Пуанкаре и книга цикла\n"
                      r"(a) C₆-потенциал V = −(V₆/6)cos 6θ: запирание станций "
                      "V'(kπ/3) = 0; (б) амплитудная книга vs часы эха"),
        "dyn_a": "потенциал циферблата (запертая циркуляция, V₆ = 0.05)",
        "dyn_a_y": "V(θ)",
        "dyn_a_x": "θ (циферблат формы)",
        "dyn_b": "книга: спуск κ_cyc за цикл, часы: Δ_cyc за цикл",
        "dyn_b_x": "часы z = ln(1/s) (log-время)",
        "dyn_b_y": "амплитудная книга −r",
        "dyn_slope": r"наклон $\kappa_{cyc}/\Delta_{cyc} = %.4f$" % (KAPPA / DELTA),
        "dyn_stations": "станции kπ/3 (заперты)",
        "dyn_saddle": "неустойчивые kπ/6",
        "dyn_free": r"свободная циркуляция: $p_\theta$ = const, период = Δ_cyc точно",
        "close_title": ("Честное замыкание цикла: якоря без подгонки\n"
                        "(все входы — машинные результаты сессий 7-8)"),
        "close_a": "правитель эха: Δ_cyc против коридора Чоптюка",
        "close_a_x": "Δ (CSS-нормировка, log-время)",
        "close_band": "Чоптюк 3.44 ± 0.02",
        "close_cyc": r"Δ_cyc = %.4f (в коридоре)" % DELTA,
        "close_tent": "5·ln2 = 3.4657 (+0.39%)",
        "close_b": "расхождения с якорями, %",
        "close_b_labels": ["κ_cyc vs κ_obs\n(γ_lit)\n+0.085%",
                           "γ_cyc vs γ_lit\n(0.374)\n−0.085%",
                           "γ_cyc vs b_Ch\n(1−cos 2π/7)\n−0.751%",
                           "Δ_cyc vs Choptuik\n(3.44)\n+0.354%",
                           "Δ_cyc vs 5·ln2\n(решётка пирамиды)\n−0.391%"],
        "close_c": "заполнение дефицита κ (динамика источников)",
        "close_c_bars": ["башня\nλ₊(27/80)\n= %.4f" % CL["lambda_plus_tower"],
                         "κ_obs\n(γ_lit)\n= %.4f" % CL["kappa_obs_gamma_lit"],
                         "κ_obs\n(b_Ch)\n= %.4f" % CL["kappa_obs_b_Ch"],
                         "цикл\nκ_cyc = ln(64/9)\n= %.4f" % KAPPA],
        "close_c_ann": ("дефицит башни +0.451 заполнен циклом\n"
                        "на %.1f%% (κ_cyc − λ₊ = +0.453)" % 100.4),
        "note_norm": ("Нормировки: Δ_cyc — CSS-книга (Чоптюк); спинор-фреймворк репо "
                      "использует Δ_sp = 7π/30 = 0.733 (R2) — другая книга; "
                      "отношение 4.71 ~ δ_F — не утверждается."),
        "files": ["fig_hexcycle.png", "fig_hexcycle_dynamics.png",
                  "fig_hexcycle_closure.png"],
    },
    "en": {
        "wheel_title": ("Poincare hexagonal transformation cycle:\n"
                        "pyramid -> cone -> truncated cone -> parabola -> bowl "
                        "-> log closure -> pyramid\n"
                        "(in the 1D cross-section pyramid and cone coincide — "
                        "the difference is azimuthal: 4 faces vs revolution)"),
        "center1": "TWO BOOKS OF THE CYCLE\n\n"
                   "amplitude (per station):\n"
                   "CORE: ln(3/2), RING: ln(4/3)\n"
                   r"$\kappa_{cyc}=\ln(64/9)=%.4f$" % KAPPA + "\n\n"
                   "echo clock (per side):\n"
                   r"$-\ln\tau_5=\ln(16/9)$" + "\n"
                   r"$\Delta_{cyc}=6\ln(16/9)=%.4f$" % DELTA,
        "station_names": ["0. Pyramid", "1. Cone", "2. Truncated cone",
                          "3. Parabolic pivot", "4. Bowl", "5. Log closure (×e$^{-Δ_cyc}$)"],
        "station_steps": [r"step $\ln(3/2)$", r"step $\ln(3/2)$",
                          r"step $\ln(4/3)$, ring 4:3",
                          r"multiplier 1 (pivot)",
                          r"multiplier $-1$ (flip)",
                          r"$(2/\sqrt{3})^2=4/3$"],
        "zone_uv": "UV[ξ³] zone: τ₃ = (3/2)² = 9/4",
        "zone_mdef": "Mdef[ξ⁵] zone: τ₅ = (3/4)² = 9/16",
        "dyn_title": ("Poincare equations and the cycle book\n"
                      r"(a) C6 potential V = −(V6/6)cos 6θ: station lock "
                      "V'(kπ/3) = 0; (b) amplitude book vs echo clock"),
        "dyn_a": "dial potential (locked circulation, V6 = 0.05)",
        "dyn_a_y": "V(θ)",
        "dyn_a_x": "θ (shape dial)",
        "dyn_b": "book: κ_cyc descent per cycle, clock: Δ_cyc per cycle",
        "dyn_b_x": "clock z = ln(1/s) (log-time)",
        "dyn_b_y": "amplitude book −r",
        "dyn_slope": r"slope $\kappa_{cyc}/\Delta_{cyc} = %.4f$" % (KAPPA / DELTA),
        "dyn_stations": "stations kπ/3 (locked)",
        "dyn_saddle": "unstable kπ/6",
        "dyn_free": r"free circulation: $p_\theta$ = const, period = Δ_cyc exactly",
        "close_title": ("Honest closure of the cycle: no-fitting anchors\n"
                        "(all inputs are machine results of sessions 7-8)"),
        "close_a": "echo ruler: Δ_cyc against the Choptuik band",
        "close_a_x": "Δ (CSS normalization, log-time)",
        "close_band": "Чоптюк 3.44 ± 0.02",
        "close_cyc": r"Δ_cyc = 6 ln(16/9) = %.4f (inside the band)" % DELTA,
        "close_tent": "5·ln2 = 3.4657 (+0.39%)",
        "close_b": "deviations from anchors, %",
        "close_b_labels": ["κ_cyc vs κ_obs\n(γ_lit)\n+0.085%",
                           "γ_cyc vs γ_lit\n(0.374)\n−0.085%",
                           "γ_cyc vs b_Ch\n(1−cos 2π/7)\n−0.751%",
                           "Δ_cyc vs Choptuik\n(3.44)\n+0.354%",
                           "Δ_cyc vs 5·ln2\n(pyramid lattice)\n−0.391%"],
        "close_c": "filling the κ deficit (source dynamics)",
        "close_c_bars": ["tower\nλ₊(27/80)\n= %.4f" % CL["lambda_plus_tower"],
                         "κ_obs\n(γ_lit)\n= %.4f" % CL["kappa_obs_gamma_lit"],
                         "κ_obs\n(b_Ch)\n= %.4f" % CL["kappa_obs_b_Ch"],
                         "cycle\nκ_cyc = ln(64/9)\n= %.4f" % KAPPA],
        "close_c_ann": ("tower deficit +0.451 filled by the cycle\n"
                        "to %.1f%% (κ_cyc − λ₊ = +0.453)" % 100.4),
        "note_norm": ("Normalizations: Δ_cyc is the CSS book (Choptuik); the repo "
                      "spinor framework uses Δ_sp = 7π/30 = 0.733 (R2) — another "
                      "book; the ratio 4.71 ~ δ_F is not claimed."),
        "files": ["fig_hexcycle.png", "fig_hexcycle_dynamics.png",
                  "fig_hexcycle_closure.png"],
    },
}


# ------------------------------------------------------------- 1. колесо ---
def fig_wheel(lang, path):
    d = L[lang]
    fig = plt.figure(figsize=(14.0, 13.6))
    ax = fig.add_axes([0.30, 0.27, 0.40, 0.40])
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.5, 0.995, d["wheel_title"], ha="center", va="top",
             fontsize=11.8)

    ang = [np.pi / 2 + k * np.pi / 3 for k in range(6)]
    vs = np.array([[np.cos(a), np.sin(a)] for a in ang])
    # зоны: CORE-пара (станции 0,1) vs RING-квартет (2..5)
    for k in range(6):
        c = C_CORE if k in (0, 1) else C_RING
        ax.add_patch(plt.Circle(vs[k], 0.13, color=c, zorder=5, alpha=0.92))
        ax.text(vs[k][0], vs[k][1], str(k), color="w", ha="center",
                va="center", fontsize=13, fontweight="bold", zorder=6)
    # стороны-стрелки (циркуляция по кругу)
    for k in range(6):
        p0, p1 = vs[k], vs[(k + 1) % 6]
        mid = 0.5 * (p0 + p1)
        arr = FancyArrowPatch(0.78 * p0 + 0.22 * p1, 0.22 * p0 + 0.78 * p1,
                              arrowstyle="-|>", mutation_scale=22,
                              lw=2.4, color="#555555", zorder=3)
        ax.add_patch(arr)
        nrm = np.array([-mid[1], mid[0]]) / np.linalg.norm(mid)
        lab = r"$-\ln\tau_5$" if lang == "ru" else r"$-\ln\tau_5$"
        ax.text(mid[0] * 1.16, mid[1] * 1.16, lab, ha="center", va="center",
                fontsize=10.5, color="#555555", rotation=0)
    # гексагон-подложка
    ax.add_patch(RegularPolygon((0, 0), 6, radius=1.0, orientation=np.pi / 2,
                                fill=False, lw=1.2, ls=":", color="#aaaaaa",
                                zorder=1))
    ax.text(0, 0.30, d["center1"], ha="center", va="center", fontsize=10.2,
            family="DejaVu Sans")
    ax.text(-1.42, -1.38, "• " + d["zone_uv"], color=C_CORE, fontsize=11)
    ax.text(-1.42, -1.50, "• " + d["zone_mdef"], color=C_RING, fontsize=11)

    # 6 панелей станций по вершинам
    xi = np.linspace(-1.12, 1.12, 400)
    for k in range(6):
        cx, cy = 0.50 + 0.335 * np.cos(ang[k]), 0.485 + 0.330 * np.sin(ang[k])
        sax = fig.add_axes([cx - 0.080, cy - 0.058, 0.160, 0.116])
        c = C_CORE if k in (0, 1) else C_RING
        sax.plot(xi, station_shape(k, xi), color=c, lw=2.0)
        sax.fill_between(xi, station_shape(k, xi), -1.25, color=c, alpha=0.10)
        sax.axhline(0, color="#cccccc", lw=0.6)
        sax.axvline(0, color="#cccccc", lw=0.6)
        sax.set_xlim(-1.18, 1.18)
        sax.set_ylim(-1.25, 1.3)
        sax.set_xticks([])
        sax.set_yticks([])
        for s in sax.spines.values():
            s.set_color(c)
        sax.set_title(d["station_names"][k] + "\n" + d["station_steps"][k],
                      fontsize=9.3, color=c)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------- 2. динамика ---
def fig_dynamics(lang, path):
    d = L[lang]
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(13.6, 5.6),
                                   constrained_layout=True)
    # (a) потенциал
    th = np.linspace(0, 2 * np.pi, 800)
    V6 = 0.05
    axa.plot(th, -(V6 / 6) * np.cos(6 * th), color=C_CORE, lw=2.2,
             label=d["dyn_a"])
    st = np.array([k * np.pi / 3 for k in range(6)])
    axa.plot(st, -(V6 / 6) * np.cos(6 * st), "o", color=C_OK, ms=9, zorder=5,
             label=d["dyn_stations"])
    sad = np.array([k * np.pi / 6 for k in range(1, 12, 2)])
    axa.plot(sad, -(V6 / 6) * np.cos(6 * sad), "x", color="#b3261e", ms=9,
             mew=2.2, zorder=5, label=d["dyn_saddle"])
    axa.set_xlabel(d["dyn_a_x"])
    axa.set_ylabel(d["dyn_a_y"])
    axa.set_ylim(-0.010, 0.0145)
    axa.set_title(d["dyn_title"], fontsize=11)
    axa.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=8.6,
               framealpha=0.9)
    axa.text(0.99, 0.03, d["dyn_free"], transform=axa.transAxes, ha="right",
             va="bottom", fontsize=8.6, color="#444444",
             bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cccccc",
                       alpha=0.92))
    # (б) книга vs часы (ступени по 6 станциям; сторона = ln(16/9) log-времени)
    steps = np.array([np.log(1.5), np.log(1.5)] + [np.log(4 / 3)] * 4)
    side = np.log(16 / 9)
    zs, rv = [0.0], [0.0]
    for cyc in range(3):
        for s in steps:
            zs.append(zs[-1] + side)
            rv.append(rv[-1] - s)
    zs = np.array(zs)
    rv = np.array(rv)
    # ступенчатая кривая
    zz, rr = [zs[0]], [rv[0]]
    for i in range(1, len(zs)):
        zz += [zs[i], zs[i]]
        rr += [rv[i - 1], rv[i]]
    axb.plot(zz, rr, color=C_RING, lw=2.0, label=d["dyn_b"])
    zlin = np.linspace(0, zs[-1], 50)
    axb.plot(zlin, -(KAPPA / DELTA) * zlin, "--", color="#555555", lw=1.4,
             label=d["dyn_slope"])
    for n in range(1, 4):
        axb.axvline(n * DELTA, color=C_CORE, lw=0.8, ls=":", alpha=0.7)
    axb.set_xlabel(d["dyn_b_x"])
    axb.set_ylabel(d["dyn_b_y"])
    axb.legend(loc="upper left", fontsize=8.8, framealpha=0.9)
    fig.savefig(path, dpi=300)
    plt.close(fig)


# --------------------------------------------------------- 3. замыкание ---
def fig_closure(lang, path):
    d = L[lang]
    fig, (axa, axb, axc) = plt.subplots(
        1, 3, figsize=(15.6, 5.4), constrained_layout=True,
        gridspec_kw={"width_ratios": [1.15, 1.0, 0.9]})
    # (a) правитель эха
    axa.axvspan(D_GHS - 0.02, D_GHS + 0.02, color=C_BAND, alpha=0.45,
                label=d["close_band"])
    axa.axvline(DELTA, color=C_OK, lw=2.6)
    axa.axvline(5 * np.log(2), color="#777777", lw=1.8, ls="--")
    ymax = 1.0
    axa.text(DELTA - 0.003, 0.96, d["close_cyc"], rotation=90, ha="right",
             va="top", fontsize=9.3, color=C_OK, clip_on=True)
    axa.text(5 * np.log(2) + 0.005, 0.96, d["close_tent"], rotation=90,
             ha="left", va="top", fontsize=8.6, color="#555555",
             clip_on=True)
    axa.set_xlim(3.33, 3.58)
    axa.set_ylim(0, ymax)
    axa.set_yticks([])
    axa.set_xlabel(d["close_a_x"])
    axa.set_title(d["close_a"], fontsize=11)
    axa.legend(loc="upper left", fontsize=9)
    # (б) расхождения
    devs = [CL["kappa_dev_vs_gamma_lit_pct"], CL["gamma_dev_vs_lit_pct"],
            CL["gamma_dev_vs_b_Ch_pct"], CL["Delta_dev_vs_GHS_pct"],
            CL["tent_lattice_dev_pct"]]
    cols = [C_OK if abs(v) < 0.5 else C_RING for v in devs]
    axb.bar(range(5), devs, color=cols, alpha=0.85)
    axb.axhline(0, color="#333333", lw=1.0)
    axb.set_xticks(range(5))
    axb.set_xticklabels(d["close_b_labels"], fontsize=7.6)
    axb.set_ylabel(d["close_b"])
    axb.set_title(d["close_b"], fontsize=11)
    axb.set_ylim(-1.05, 0.65)
    for i, v in enumerate(devs):
        axb.text(i, v + (0.05 if v >= 0 else -0.11), f"{v:+.3f}%",
                 ha="center", fontsize=8.2)
    # (в) дефицит
    vals = [CL["lambda_plus_tower"], CL["kappa_obs_gamma_lit"],
            CL["kappa_obs_b_Ch"], KAPPA]
    cols = ["#8a8a8a", C_CORE, C_CORE, C_OK]
    axc.bar(range(4), vals, color=cols, alpha=0.9, width=0.62)
    axc.set_xticks(range(4))
    axc.set_xticklabels(d["close_c_bars"], fontsize=8.0)
    axc.axhline(CL["kappa_obs_gamma_lit"], color=C_CORE, lw=1.0, ls=":")
    axc.set_ylim(0, 2.35)
    axc.text(0.02, 0.955, d["close_c_ann"], transform=axc.transAxes,
             fontsize=8.8, va="top",
             bbox=dict(boxstyle="round,pad=0.3", fc="#f0f5fa", ec=C_CORE))
    axc.set_title(d["close_c"], fontsize=11)
    fig.suptitle(d["close_title"], fontsize=12.5)
    fig.get_layout_engine().set(rect=[0.0, 0.05, 1.0, 0.95])
    fig.text(0.5, 0.012, d["note_norm"], ha="center", va="bottom",
             fontsize=8.6, color="#555555")
    fig.savefig(path, dpi=300)
    plt.close(fig)


def main():
    for lang, folder in (("ru", FIG_RU), ("en", FIG_EN)):
        fig_wheel(lang, os.path.join(folder, "fig_hexcycle.png"))
        fig_dynamics(lang, os.path.join(folder, "fig_hexcycle_dynamics.png"))
        fig_closure(lang, os.path.join(folder, "fig_hexcycle_closure.png"))
        for f in L[lang]["files"]:
            shutil.copy(os.path.join(folder, f), os.path.join(DL, f))
            shutil.copy(os.path.join(folder, f),
                        os.path.join(DL, f.replace(".png", f"_{lang}.png")))
        print(f"[{lang}] 3 рисунка -> {folder}")
    print("Копии ->", DL)


if __name__ == "__main__":
    main()
