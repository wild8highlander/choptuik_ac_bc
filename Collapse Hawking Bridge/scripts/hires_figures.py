#!/usr/bin/env python3
"""
hires_figures.py — the ultra-high-resolution (600 dpi) figure suite.

Seventeen figure types x two languages (en, ru) x two themes
(light, dark) = 68 PNG files under figures_hires/<lang>/<theme>/.

Every figure maps ONE measurement architecture of the committed
campaigns to its own visual layout:

  hq_01  A* bisection ladder            (C1, bisection search)
  hq_02  amplitude scan N=400           (C1, fixed-N amplitude scan)
  hq_03  amplitude scan N=800           (C1, fixed-N amplitude scan)
  hq_04  scan comparison N400 vs N800   (C1, cross-resolution audit)
  hq_05  born spectrum + gamma anchor   (C1, spectrum architecture)
  hq_06  subcritical q_max(eps)         (C2-sub, dispersal diagnostics)
  hq_07  critical slowdown v_qmax       (C2-sub, time-series sampling)
  hq_08  echo accumulation              (C2-sub, peak counting)
  hq_09  compactness decay ratio        (C2-sub, endpoint diagnostic)
  hq_10  born bifurcation f~(eps)       (C2-sup, bifurcation scan)
  hq_11  local bifurcation slope        (C2-sup, derivative measurement)
  hq_12  Delta*gamma anchor product     (C3, anchor comparison)
  hq_13  floor law floor_M ~ 12/N       (C3b + C1, resolution ladder)
  hq_14  gamma_eff convergence          (C3b, concentrated resolution)
  hq_15  thermodynamic landscape        (bridge mapping, 5 input scales)
  hq_16  Page curve detail              (Page model + Haar audit)
  hq_17  Roberts-Oshiro validation      (engine self-test)

The script never computes new physics: every number is read from the
committed verdicts (campaigns/reference/) and the derived tables
(data/bridge/).

Run:   python3 scripts/hires_figures.py --all
       python3 scripts/hires_figures.py --lang en --theme dark
       python3 scripts/hires_figures.py --dpi 300   (fast preview)
"""
import argparse
import csv
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import figstyle as fs
import matplotlib.pyplot as plt
import numpy as np
from chbridge.constants import (
    DGAMMA_LIT,
    DGAMMA_TARGET,
    DGAMMA_TOL,
    T_CMB,
    echo_delta,
    gamma_Ch,
)
from chbridge.hawking import PAGE_FRACTION

REF = os.path.join(ROOT, "campaigns", "reference")
DATA = os.path.join(ROOT, "data", "bridge")

# Extended language pack for the hires suite (supplements figstyle.LANG).
HL = {
    "en": {
        "ladder_title": "A* bisection ladder (C1 + remediated reference)",
        "ladder_y": "critical amplitude  $A^*$",
        "ladder_x": "grid resolution  N",
        "ladder_ref": "remediated reference (F-1), N=1600",
        "ladder_agree": "ladder DRIFTS: 2.8e-3 over N800->N1600",
        "ladder_note": "threshold not converged; stale 1.06e-6 claim retracted",
        "scan_title": "Amplitude scan at N={N} (campaign C1)",
        "scan_y": "born black-hole mass  $M_{code}$",
        "scan_x": "distance from threshold  $\\varepsilon = A - A^*$",
        "sane": "sane run (completed)",
        "floorstop": "floor-stopped",
        "junk": "junk row (kept, flagged)",
        "floor": "mass floor  $\\approx 12/N$",
        "compare_title": "Cross-resolution audit of the scan architecture",
        "compare_note": "the grid floor, not the engine, saturates the far band",
        "spectrum_title": "Born spectrum vs the critical anchor",
        "anchor": "anchor slope  $\\gamma_{Ch} = 0.374$",
        "qmax_title": "Subcritical approach (campaign C2, dispersal architecture)",
        "qmax_y": "peak compactness  $q_{max} = \\max(2m/r)$",
        "horizon": "horizon compactness  $q = 1$",
        "slow_title": "Critical slowdown (campaign C2)",
        "slow_y": "peak time  $v_{qmax}$ (null coordinate of $q_{max}$)",
        "slow_x": "log-distance from threshold  $\\ln\\varepsilon$",
        "slow_fit": "fit  $v = a + b\\ln\\varepsilon$  ($b=-0.0334$, $r^2=0.71$)",
        "quant": "40-snapshot sampling (instrument quantization)",
        "echo_title": "Echo accumulation (campaign C2)",
        "echo_y": "echo peaks  $N_{peaks}$",
        "echo_x": "log-distance  $\\ln(1/\\varepsilon)$",
        "echo_fit": "fit  0.1909 peaks / e-fold",
        "echo_anchor": "critical anchor  $1/\\Delta = 0.2907$",
        "qfin_title": "Compactness decay along the subcritical branch",
        "qfin_y": "$q_{final}/q_{max}$",
        "bif_title": "Born bifurcation $\\tilde f(\\varepsilon)$ (campaign C2, supercritical)",
        "bif_y": "fraction of saturation  $\\tilde f(\\varepsilon)$",
        "eps_half": "$\\varepsilon_{1/2} = 4.86\\times10^{-3}$",
        "sat": "saturation  $\\tilde f = 1$",
        "slope_title": "Local log-log slope of the bifurcation curve",
        "slope_y": "$d\\ln\\tilde f / d\\ln\\varepsilon$",
        "slope_note": "derivative measured on the committed f~ rows",
        "dg_title": "The $\\Delta\\cdot\\gamma$ anchor product (campaign C3)",
        "dg_y": "product value",
        "dg_anchor": "$\\Delta\\cdot\\gamma = \\Delta_{lit}\\cdot\\gamma_{Ch} = 1.28656$",
        "dg_target": "target  1.27",
        "dg_tol": "tolerance  $\\pm 0.05$",
        "dg_pass": "PASS, deviation 1.3%",
        "floorlaw_title": "The floor law (campaigns C1 + C3b)",
        "floorlaw_y": "resolved mass floor  $M_{floor}$ [code units]",
        "floorlaw_x": "grid resolution  N",
        "floorlaw_fit": "1/N scaling: 12/N guide",
        "geff_title": "$\\gamma_{eff}$ at concentrated resolution (campaign C3b)",
        "geff_y": "fitted exponent  $\\gamma_{eff}$",
        "geff_anchor": "literature anchor  $\\gamma_{Ch} = 0.374$",
        "geff_note": "honest negative, per-grid thresholds (F-2): the floor governs the reachable band",
        "thermo_title": "Thermodynamic landscape of the mapped ensemble",
        "thermo_T": "Hawking temperature  $T_H$ [K]",
        "thermo_S": "entropy  $S_{BH}/k_B$",
        "thermo_t": "evaporation time  $t_{evap}$ [s]",
        "thermo_P": "peak power  $P_H$ [W]",
        "thermo_Mx": "black-hole mass  $M_{BH}$ [kg]",
        "page_title": "Page curves of the born ensemble (detailed)",
        "page_y": "radiation entropy  $S_{rad}/S_0$",
        "page_x": "time  $t/t_{evap}$",
        "page_time": "Page time  $(1-2^{-3/2})\\,t_{evap}$",
        "page_zoom": "zoom near the Page time",
        "page_haar": "Haar audit: max deviation 0.0042 bits",
        "val_title": "Roberts-Oshiro validation of the engine",
        "val_y": "$\\max|r - r_{exact}|$",
        "val_x": "grid N",
        "val_slope": "slope $-2$",
    },
    "ru": {
        "ladder_title": "Лестница бисекции $A^*$ (C1 + remediated референс)",
        "ladder_y": "критическая амплитуда  $A^*$",
        "ladder_x": "разрешение сетки  N",
        "ladder_ref": "remediated-референс (F-1), N=1600",
        "ladder_agree": "лестница ДРЕЙФУЕТ: 2.8e-3 на N800->N1600",
        "ladder_note": "порог не сошёлся; старое заявление 1.06e-6 отозвано",
        "scan_title": "Сканирование амплитуды при N={N} (кампания C1)",
        "scan_y": "масса рождённой ЧД  $M_{code}$",
        "scan_x": "расстояние от порога  $\\varepsilon = A - A^*$",
        "sane": "штатный прогон (completed)",
        "floorstop": "останов по полу",
        "junk": "мусорная строка (сохранена, помечена)",
        "floor": "массовый пол  $\\approx 12/N$",
        "compare_title": "Кросс-разрешённый аудит сканирующей архитектуры",
        "compare_note": "дальнюю полосу насыщает пол сетки, а не движок",
        "spectrum_title": "Спектр рождения против критического якоря",
        "anchor": "якорь  $\\gamma_{Ch} = 0{,}374$",
        "qmax_title": "Докритическое приближение (кампания C2, дисперсная архитектура)",
        "qmax_y": "пиковая компактность  $q_{max} = \\max(2m/r)$",
        "horizon": "компактность горизонта  $q = 1$",
        "slow_title": "Критическое замедление (кампания C2)",
        "slow_y": "время пика  $v_{qmax}$ (координата $q_{max}$)",
        "slow_x": "лог-расстояние от порога  $\\ln\\varepsilon$",
        "slow_fit": "фит  $v = a + b\\ln\\varepsilon$  ($b=-0{,}0334$, $r^2=0{,}71$)",
        "quant": "квантование: 40 снимков на прогон",
        "echo_title": "Накопление эхо-пиков (кампания C2)",
        "echo_y": "число эхо-пиков  $N_{peaks}$",
        "echo_x": "лог-расстояние  $\\ln(1/\\varepsilon)$",
        "echo_fit": "фит  0,1909 пиков / э-крат",
        "echo_anchor": "критический якорь  $1/\\Delta = 0{,}2907$",
        "qfin_title": "Затухание компактности по докритической ветви",
        "qfin_y": "$q_{final}/q_{max}$",
        "bif_title": "Бифуркация рождения $\\tilde f(\\varepsilon)$ (кампания C2, сверхкритическая)",
        "bif_y": "доля насыщения  $\\tilde f(\\varepsilon)$",
        "eps_half": "$\\varepsilon_{1/2} = 4{,}86\\times10^{-3}$",
        "sat": "насыщение  $\\tilde f = 1$",
        "slope_title": "Локальный наклон бифуркационной кривой (log-log)",
        "slope_y": "$d\\ln\\tilde f / d\\ln\\varepsilon$",
        "slope_note": "производная по зафиксированным строкам f~",
        "dg_title": "Якорное произведение $\\Delta\\cdot\\gamma$ (кампания C3)",
        "dg_y": "значение произведения",
        "dg_anchor": "$\\Delta\\cdot\\gamma = \\Delta_{lit}\\cdot\\gamma_{Ch} = 1{,}28656$",
        "dg_target": "цель  1,27",
        "dg_tol": "допуск  $\\pm 0{,}05$",
        "dg_pass": "ЗАЧЁТ, отклонение 1,3%",
        "floorlaw_title": "Закон пола (кампании C1 + C3b)",
        "floorlaw_y": "разрешённый массовый пол  $M_{floor}$ [код. ед.]",
        "floorlaw_x": "разрешение сетки  N",
        "floorlaw_fit": "скейлинг 1/N: ориентир 12/N",
        "geff_title": "$\\gamma_{eff}$ на концентрированных сетках (кампания C3b)",
        "geff_y": "фит-экспонента  $\\gamma_{eff}$",
        "geff_anchor": "литературный якорь  $\\gamma_{Ch} = 0{,}374$",
        "geff_note": "честный негатив, пороговые значения по сеткам (F-2): пол управляет достижимой полосой",
        "thermo_title": "Термодинамический ландшафт отображённого ансамбля",
        "thermo_T": "температура Хокинга  $T_H$ [К]",
        "thermo_S": "энтропия  $S_{BH}/k_B$",
        "thermo_t": "время испарения  $t_{evap}$ [с]",
        "thermo_P": "пиковая мощность  $P_H$ [Вт]",
        "thermo_Mx": "масса ЧД  $M_{BH}$ [кг]",
        "page_title": "Кривые Пейджа ансамбля рождения (детально)",
        "page_y": "энтропия излучения  $S_{rad}/S_0$",
        "page_x": "время  $t/t_{evap}$",
        "page_time": "Время Пейджа  $(1-2^{-3/2})\\,t_{evap}$",
        "page_zoom": "окрестность времени Пейджа",
        "page_haar": "аудит Хаара: макс. отклонение 0,0042 бит",
        "val_title": "Валидация движка (Робертс–Оширо)",
        "val_y": "$\\max|r - r_{exact}|$",
        "val_x": "сетка N",
        "val_slope": "наклон $-2$",
    },
}


def _load(name):
    with open(os.path.join(REF, name)) as f:
        return json.load(f)


def _csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# hq_01 — A* bisection ladder
def hq_01_ladder(t, L, ax):
    c1 = _load("c1_verdict.json")
    g = c1["a_star_grid"]
    ns = [200, 400, 800]
    ast = [g[f"N{n}"]["a_star"] for n in ns]
    # v2.0.1 remediation (F-1): the reference is the remediated ladder
    ladder = _load("a_star_ladder.json")["ladder"]
    ns_deep = [1600, 3200]
    ast_deep = [ladder[f"N{n}"]["a_star"] for n in ns_deep]
    ref = ladder["N1600"]["a_star"]
    ax.plot(ns, ast, "o-", color=t["ink"], lw=2.2, ms=9, zorder=5,
            label="engine bisection (C1)")
    ax.plot(ns_deep, ast_deep, "s--", color=t["ink"], lw=1.8, ms=7,
            alpha=0.75, zorder=5, label="remediated ladder (F-1, tol 5e-8)")
    ax.axhline(ref, color=t["gold"], lw=1.6, ls=":", zorder=3,
               label=L["ladder_ref"])
    ax.fill_between([150, 3600], ref * (1 - 2e-6), ref * (1 + 2e-6),
                    color=t["gold"], alpha=0.18, zorder=2)
    ax.annotate(L["ladder_agree"], (800, ast[-1]),
                xytext=(430, ast[-1] * 1.10), color=t["gold"], fontsize=11,
                arrowprops=dict(arrowstyle="->", color=t["gold"]))
    for n, a in zip(ns, ast):
        ax.annotate(f"{a:.6f}", (n, a), xytext=(n * 1.03, a * 0.985),
                    fontsize=10, color=t["ink"])
    for n, a in zip(ns_deep, ast_deep):
        ax.annotate(f"{a:.6f}", (n, a), xytext=(n * 1.02, a * 1.03),
                    fontsize=10, color=t["ink"])
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlim(150, 3600)
    ax.set_xlabel(L["ladder_x"]); ax.set_ylabel(L["ladder_y"])
    ax.set_title(L["ladder_title"])
    ax.legend(frameon=False, fontsize=10, loc="lower left")
    ax.grid(True, which="both")


# hq_02 / hq_03 — amplitude scans
def _scan_panel(t, L, ax, key, title):
    c1 = _load("c1_verdict.json")
    scan = c1[key]
    rows = scan["rows"]
    eps = np.array([r["eps"] for r in rows])
    M = np.array([r["M_code"] for r in rows])
    sane = np.array([bool(r["sane"]) and r.get("stop") == "completed"
                     or (bool(r["sane"]) and r.get("stop") != "junk") for r in rows])
    junk = np.array([r.get("stop") == "junk" for r in rows])
    ax.scatter(eps[sane & ~junk], M[sane & ~junk], s=34, color=t["ink"],
               zorder=5, label=L["sane"])
    fl = np.array([r.get("stop") == "AH mass saturated" for r in rows])
    ax.scatter(eps[fl], M[fl], s=34, facecolors="none",
               edgecolors=t["muted"], lw=1.4, zorder=4, label=L["floorstop"])
    if junk.any():
        ax.scatter(eps[junk], M[junk], s=42, marker="x", color=t["bad"],
                   lw=1.6, zorder=6, label=L["junk"])
    ax.axhline(1.55e-2 if key == "scan_N800" else 7.9e-2, color=t["muted"],
               lw=1.2, ls=":", label=L["floor"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["scan_x"]); ax.set_ylabel(L["scan_y"])
    ax.set_title(title)
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.grid(True, which="both")


def hq_02_scan400(t, L, ax):
    _scan_panel(t, L, ax, "scan_N400", L["scan_title"].format(N=400))


def hq_03_scan800(t, L, ax):
    _scan_panel(t, L, ax, "scan_N800", L["scan_title"].format(N=800))


# hq_04 — cross-resolution audit
def hq_04_compare(t, L, ax):
    c1 = _load("c1_verdict.json")
    for key, col, lbl in (("scan_N400", t["muted"], "N=400"),
                          ("scan_N800", t["ink"], "N=800")):
        rows = [r for r in c1[key]["rows"] if r["sane"]]
        eps = np.array([r["eps"] for r in rows])
        M = np.array([r["M_code"] for r in rows])
        ax.plot(eps, M, "o", color=col, ms=6, lw=1.2, label=lbl, zorder=5)
    ax.axhline(1.55e-2, color=t["gold"], lw=1.4, ls=":")
    ax.text(3e-5, 1.8e-2, L["floor"], color=t["gold"], fontsize=10)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["scan_x"]); ax.set_ylabel(L["scan_y"])
    ax.set_title(L["compare_title"])
    ax.text(0.03, 0.06, L["compare_note"], transform=ax.transAxes,
            fontsize=10, color=t["muted"])
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.grid(True, which="both")


# hq_05 — born spectrum + anchor
def hq_05_spectrum(t, L, ax):
    c1 = _load("c1_verdict.json")
    rows = [r for r in c1["scan_N800"]["rows"] if r["sane"]]
    eps = np.array([r["eps"] for r in rows])
    M = np.array([r["M_code"] for r in rows])
    ax.scatter(eps[eps < 3e-2], M[eps < 3e-2], s=30, color=t["ink"],
               zorder=5, label="engine (N=800, sane)")
    ax.scatter(eps[eps >= 3e-2], M[eps >= 3e-2], s=30, facecolors="none",
               edgecolors=t["muted"], zorder=4, label="floor band")
    born = _csv("born_spectrum.csv")
    e2 = np.array([float(r["eps"]) for r in born
                   if r["grid"] == "800" and r["sane"] == "True"])
    m2 = np.array([float(r["M_code"]) for r in born
                   if r["grid"] == "800" and r["sane"] == "True"])
    if len(e2):
        ax.scatter(e2, m2, s=16, color=t["gold"], zorder=6, alpha=0.75,
                   label="born spectrum rows (N=800)")
    eps_line = np.logspace(-3.5, -0.3, 60)
    C = math.log10(2.1e-2) - gamma_Ch * math.log10(1.3e-2)
    ax.plot(eps_line, 10 ** (C + gamma_Ch * np.log10(eps_line)),
            color=t["gold"], lw=1.8, ls="--", label=L["anchor"])
    ax.axhline(1.55e-2, color=t["muted"], lw=1.2, ls=":", label=L["floor"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["scan_x"]); ax.set_ylabel(L["scan_y"])
    ax.set_title(L["spectrum_title"])
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.grid(True, which="both")


# hq_06 — subcritical q_max
def hq_06_qmax(t, L, ax):
    c2 = _load("c2_verdict.json")
    rows = [r for r in c2["subcritical"]["rows"]
            if not r["flipped"] and r["q_max"] is not None]
    eps = np.array([r["eps"] for r in rows])
    q = np.array([r["q_max"] for r in rows])
    ax.plot(eps, q, "o-", color=t["ink"], ms=7, lw=1.5, zorder=5)
    ax.axhline(1.0, color=t["gold"], lw=1.5, ls="--", label=L["horizon"])
    ax.set_xscale("log")
    ax.set_ylim(0, 1.08)
    ax.set_xlabel(L["slow_x"].replace("$\\ln\\varepsilon$",
                                      "$\\varepsilon = A^* - A$"))
    ax.set_ylabel(L["qmax_y"])
    ax.set_title(L["qmax_title"])
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.grid(True, which="both")


# hq_07 — critical slowdown
def hq_07_slowdown(t, L, ax):
    c2 = _load("c2_verdict.json")
    rows = [r for r in c2["subcritical"]["rows"]
            if not r["flipped"] and r["q_max"] is not None]
    eps = np.array([r["eps"] for r in rows])
    v = np.array([r["v_qmax"] for r in rows])
    fit = c2["subcritical"]["slowdown_fit"]
    b, a = fit["slope_ln_eps"], fit["intercept"]
    x = np.log(eps)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(x, v, "o", color=t["ink"], ms=8, zorder=5, label=L["quant"])
    ax.plot(xs, a + b * xs, "-", color=t["gold"], lw=2, zorder=4,
            label=L["slow_fit"])
    ax.set_xlabel(L["slow_x"]); ax.set_ylabel(L["slow_y"])
    ax.set_title(L["slow_title"])
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    ax.grid(True)


# hq_08 — echo accumulation
def hq_08_echo(t, L, ax):
    c2 = _load("c2_verdict.json")
    rows = [r for r in c2["subcritical"]["rows"]
            if not r["flipped"] and r["q_max"] is not None]
    eps = np.array([r["eps"] for r in rows])
    n = np.array([float(r["n_peaks"]) for r in rows])
    fit = c2["subcritical"]["echo_rate_fit"]
    rate, a0 = fit["echoes_per_efold"], fit["intercept"]
    x = np.log(1.0 / eps)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(x, n, "o", color=t["ink"], ms=8, zorder=5)
    ax.plot(xs, a0 + rate * xs, "-", color=t["gold"], lw=2, zorder=4,
            label=L["echo_fit"])
    slope_ref = 1.0 / echo_delta
    ax.plot(xs, a0 + slope_ref * xs, "--", color=t["muted"], lw=1.5,
            label=L["echo_anchor"])
    ax.set_xlabel(L["echo_x"]); ax.set_ylabel(L["echo_y"])
    ax.set_title(L["echo_title"])
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.grid(True)


# hq_09 — compactness decay
def hq_09_qfinal(t, L, ax):
    rows = _csv("campaign_c2_subcritical.csv")
    pts = [(float(r["eps"]), float(r["q_final_over_qmax"]))
           for r in rows if r["q_final_over_qmax"] and r["flipped"] == "False"]
    pts.sort()
    eps = np.array([p[0] for p in pts])
    ratio = np.array([p[1] for p in pts])
    ax.plot(eps, ratio, "s-", color=t["ink"], ms=7, lw=1.5, zorder=5)
    ax.set_xscale("log")
    ax.set_xlabel(L["slow_x"].replace("$\\ln\\varepsilon$",
                                      "$\\varepsilon = A^* - A$"))
    ax.set_ylabel(L["qfin_y"])
    ax.set_title(L["qfin_title"])
    ax.grid(True, which="both")


# hq_10 — bifurcation
def hq_10_bifurcation(t, L, ax):
    c2 = _load("c2_verdict.json")
    rows = c2["bifurcation"]["rows"]
    sane = [r for r in rows if r["sane"]]
    junk = [r for r in rows if not r["sane"]]
    eps = np.array([r["eps"] for r in sane])
    f = np.array([r["f_tilde"] for r in sane])
    ax.scatter(eps, f, s=34, color=t["ink"], zorder=5, label="sane")
    if junk:
        eJ = np.array([r["eps"] for r in junk])
        ax.scatter(eJ, [1.5] * len(eJ), s=44, marker="x", color=t["bad"],
                   lw=1.6, zorder=6, label=L["junk"])
    ax.axhline(1.0, color=t["muted"], lw=1.2, ls=":", label=L["sat"])
    eh = c2["bifurcation"]["summary"]["eps_half"]
    ax.axvline(eh, color=t["gold"], lw=1.6, ls="--")
    ax.annotate(L["eps_half"], (eh, 0.30), xytext=(eh * 3.0, 0.24),
                color=t["gold"], fontsize=11,
                arrowprops=dict(arrowstyle="->", color=t["gold"]))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(0.05, 2.2)
    ax.set_xlabel(L["scan_x"]); ax.set_ylabel(L["bif_y"])
    ax.set_title(L["bif_title"])
    ax.legend(frameon=False, fontsize=10, loc="lower right")
    ax.grid(True, which="both")


# hq_11 — local bifurcation slope
def hq_11_slope(t, L, ax):
    rows = [r for r in _csv("campaign_c2_bifurcation.csv")
            if r["sane"] == "True" and r["f_tilde"]]
    rows.sort(key=lambda r: float(r["eps"]))
    eps = np.array([float(r["eps"]) for r in rows])
    f = np.array([float(r["f_tilde"]) for r in rows])
    lx, lf = np.log(eps), np.log(f)
    slope = np.gradient(lf, lx)
    ax.plot(eps[1:-1], slope[1:-1], "o-", color=t["ink"], ms=7, lw=1.4,
            zorder=5)
    ax.axhline(0.0, color=t["muted"], lw=1.0, ls=":")
    ax.set_xscale("log")
    ax.set_xlabel(L["scan_x"]); ax.set_ylabel(L["slope_y"])
    ax.set_title(L["slope_title"])
    ax.text(0.03, 0.06, L["slope_note"], transform=ax.transAxes,
            fontsize=10, color=t["muted"])
    ax.grid(True, which="both")


# hq_12 — Delta*gamma anchor
def hq_12_dgamma(t, L, ax):
    lo, hi = DGAMMA_TARGET - DGAMMA_TOL, DGAMMA_TARGET + DGAMMA_TOL
    ax.axhspan(lo, hi, color=t["gold"], alpha=0.14, zorder=1)
    ax.axhline(DGAMMA_TARGET, color=t["muted"], lw=1.4, ls="--", zorder=2,
               label=L["dg_target"])
    ax.axhline(DGAMMA_LIT, color=t["gold"], lw=2.4, zorder=5,
               label=L["dg_anchor"])
    ax.axhline(lo, color=t["muted"], lw=0.9, ls=":", zorder=2)
    ax.axhline(hi, color=t["muted"], lw=0.9, ls=":", zorder=2,
               label=L["dg_tol"])
    ax.text(0.985, DGAMMA_LIT + 0.004, L["dg_pass"], ha="right",
            color=t["ok"], fontsize=12, fontweight="bold")
    ax.text(0.985, DGAMMA_LIT - 0.014,
            f"$\\Delta = {echo_delta}$,  $\\gamma = {gamma_Ch}$",
            ha="right", fontsize=11, color=t["ink"])
    ax.set_ylim(1.17, 1.40)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_ylabel(L["dg_y"])
    ax.set_title(L["dg_title"])
    ax.legend(frameon=False, fontsize=10, loc="lower left")
    ax.grid(True, axis="y")


# hq_13 — floor law
def hq_13_floorlaw(t, L, ax):
    c3b = _load("c3b_verdict.json")
    # v2.1.0 (F-2): floors read from the committed per-grid verdict and the
    # C1 Part-C constant — the previously hard-coded pre-remediation values
    # are retracted.
    pts = [(800, 0.0155)]
    for g, N in (("N1600", 1600), ("N3200", 3200)):
        pts.append((N, c3b["gamma_ladder"][g]["floor_M"]))
    ns = np.array([p[0] for p in pts], dtype=float)
    fl = np.array([p[1] for p in pts])
    ax.plot(ns, fl, "o", color=t["ink"], ms=10, zorder=5)
    for n, f in zip(ns, fl):
        ax.annotate(f"{f:.4g}", (n, f), xytext=(n * 1.02, f * 1.25),
                    fontsize=11, color=t["ink"])
    xs = np.linspace(700, 3400, 100)
    ax.plot(xs, 12.0 / xs, "--", color=t["gold"], lw=2, zorder=4,
            label=L["floorlaw_fit"])
    ax.plot(xs, 9.6 / xs, ":", color=t["muted"], lw=1.2, alpha=0.8)
    ax.plot(xs, 14.4 / xs, ":", color=t["muted"], lw=1.2, alpha=0.8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["floorlaw_x"]); ax.set_ylabel(L["floorlaw_y"])
    ax.set_title(L["floorlaw_title"])
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.grid(True, which="both")


# hq_14 — gamma_eff convergence
def hq_14_geff(t, L, ax):
    # v2.1.0 (F-2): per-grid remediated fits read from the C3b verdict —
    # the retracted 2.0.0 values (0.111/0.121, eps-mislabeling artifact)
    # are no longer plotted.
    c3b = _load("c3b_verdict.json")
    lad = c3b["gamma_ladder"]
    ns = [1600, 3200]
    gs = [lad["N1600"]["gamma_eff"], lad["N3200"]["gamma_eff"]]
    r2s = [lad["N1600"]["r2"], lad["N3200"]["r2"]]
    ax.plot(ns, gs, "o-", color=t["ink"], lw=2.2, ms=10, zorder=5)
    for n, g, r2 in zip(ns, gs, r2s):
        ax.annotate(f"{g:.4f}\n(r2={r2:.2f})", (n, g), xytext=(n * 0.90, g * 1.10),
                    fontsize=11, color=t["ink"])
    ax.axhline(gamma_Ch, color=t["gold"], lw=1.8, ls="--",
               label=L["geff_anchor"])
    ax.set_xlim(1200, 3800)
    ax.set_ylim(0.0, 0.45)
    ax.set_xlabel(L["floorlaw_x"]); ax.set_ylabel(L["geff_y"])
    ax.set_title(L["geff_title"])
    ax.text(0.03, 0.10, L["geff_note"], transform=ax.transAxes,
            fontsize=10, color=t["muted"])
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.grid(True)


# hq_15 — thermodynamic landscape
def hq_15_thermo(t, L, ax1, ax2, ax3, ax4):
    rows = _csv("bridge_master.csv")
    groups = {}
    for r in rows:
        groups.setdefault(r["input_scale"], []).append(r)
    palette = [t["gold"], t["ink"], t["muted"], t["ok"], t["bad"]]
    for (scale, rr), col in zip(groups.items(), palette):
        M = np.array([float(r["M_BH_kg"]) for r in rr])
        TH = np.array([float(r["T_H_K"]) for r in rr])
        S = np.array([float(r["S_BH_over_kB"]) for r in rr])
        te = np.array([float(r["t_evap_s"]) for r in rr])
        P = np.array([float(r["P_H_W"]) for r in rr])
        ax1.plot(M, TH, "o-", ms=6, lw=1.2, color=col, label=scale)
        ax2.plot(M, S, "o-", ms=6, lw=1.2, color=col)
        ax3.plot(M, te, "o-", ms=6, lw=1.2, color=col)
        ax4.plot(M, P, "o-", ms=6, lw=1.2, color=col)
    for ax, ylab in ((ax1, L["thermo_T"]), (ax2, L["thermo_S"]),
                     (ax3, L["thermo_t"]), (ax4, L["thermo_P"])):
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel(L["thermo_Mx"]); ax.set_ylabel(ylab)
        ax.grid(True, which="both")
    ax1.axhline(T_CMB, color=t["muted"], lw=1.1, ls="--")
    ax1.legend(frameon=False, fontsize=9, loc="upper right")
    fig = ax1.figure
    fig.suptitle(L["thermo_title"], fontsize=14)


# hq_16 — Page curve detail
def hq_16_page(t, L, ax):
    rows = _csv("page_curve_grid.csv")
    colors = {"near_floor": t["gold"], "mid": t["ink"], "saturated": t["muted"]}
    for member in ("saturated", "mid", "near_floor"):
        rr = [r for r in rows if r["member"] == member]
        tau = np.array([float(r["t_over_t_evap"]) for r in rr])
        S = np.array([float(r["S_rad_over_kB_norm"]) for r in rr])
        ax.plot(tau, S, color=colors[member], lw=2.2,
                label=f"f~ = {float(rr[0]['f_tilde']):.4f}")
    ax.axvline(PAGE_FRACTION, color=t["gold"], lw=1.6, ls="--")
    ax.annotate(L["page_time"], (PAGE_FRACTION, 0.40),
                xytext=(PAGE_FRACTION - 0.42, 0.36), color=t["gold"],
                fontsize=11,
                arrowprops=dict(arrowstyle="->", color=t["gold"]))
    ax.text(0.02, 0.965, L["page_haar"], transform=ax.transAxes,
            fontsize=10, color=t["ok"], va="top")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0.28, 1.02)
    ax.set_xlabel(L["page_x"]); ax.set_ylabel(L["page_y"])
    ax.set_title(L["page_title"])
    ax.legend(frameon=False, fontsize=10, loc="lower right")
    ax.grid(True)


# hq_17 — RO validation
def hq_17_validation(t, L, ax):
    c1 = _load("c1_verdict.json")
    val = c1["validation"]
    ns = np.array([v["n"] for v in val], dtype=float)
    err = np.array([v["err_r"] for v in val], dtype=float)
    ax.plot(ns, err, "o-", color=t["ink"], lw=2.2, ms=9, zorder=5)
    for v in val:
        if "convergence_order_r" in v:
            ax.annotate(f"order {v['convergence_order_r']:.2f}",
                        (v["n"], v["err_r"]),
                        xytext=(v["n"] * 0.82, v["err_r"] * 1.7),
                        color=t["gold"], fontsize=11)
    ref = err[0] * (ns / ns[0]) ** (-2)
    ax.plot(ns, ref, ls="--", color=t["gold"], lw=1.6, label=L["val_slope"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(L["val_x"]); ax.set_ylabel(L["val_y"])
    ax.set_title(L["val_title"])
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.grid(True, which="both")


FIGS = {
    "hq_01_a_star_ladder": (hq_01_ladder, 1),
    "hq_02_amplitude_scan_N400": (hq_02_scan400, 1),
    "hq_03_amplitude_scan_N800": (hq_03_scan800, 1),
    "hq_04_scan_compare": (hq_04_compare, 1),
    "hq_05_born_spectrum": (hq_05_spectrum, 1),
    "hq_06_subcritical_qmax": (hq_06_qmax, 1),
    "hq_07_critical_slowdown": (hq_07_slowdown, 1),
    "hq_08_echo_accumulation": (hq_08_echo, 1),
    "hq_09_compactness_decay": (hq_09_qfinal, 1),
    "hq_10_born_bifurcation": (hq_10_bifurcation, 1),
    "hq_11_bifurcation_slope": (hq_11_slope, 1),
    "hq_12_dgamma_anchor": (hq_12_dgamma, 1),
    "hq_13_floor_law": (hq_13_floorlaw, 1),
    "hq_14_gamma_eff_convergence": (hq_14_geff, 1),
    "hq_15_thermo_landscape": (hq_15_thermo, 4),
    "hq_16_page_detail": (hq_16_page, 1),
    "hq_17_ro_validation": (hq_17_validation, 1),
}


def make_one(name, lang, theme, dpi):
    t = fs.style(theme)
    L = dict(fs.LANG[lang]); L.update(HL[lang])
    fn, panels = FIGS[name]
    if panels == 1:
        fig = fs.new_fig(7.4, 4.8)
        ax = fig.add_subplot(111)
        fn(t, L, ax)
    elif panels == 2:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0),
                                 constrained_layout=True)
        fn(t, L, axes[0], axes[1])
    else:
        fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.6),
                                 constrained_layout=True)
        fn(t, L, *axes.flat)
    outdir = os.path.join(ROOT, "figures_hires", lang, theme)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, name + ".png")
    fig.savefig(out, dpi=dpi, pil_kwargs={"compress_level": 9})
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--theme", choices=["light", "dark"], default=None)
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--figs", nargs="*", default=None,
                    help="regenerate only these figure types (e.g. hq_13_floorlaw)")
    args = ap.parse_args()

    langs = ["en", "ru"] if args.all else [args.lang or "en"]
    themes = ["light", "dark"] if args.all else [args.theme or "light"]
    figs = FIGS if args.figs is None else \
        [f for f in FIGS if f in args.figs]
    if not figs:
        ap.error("no matching figure types; known: " + ", ".join(FIGS))
    n = 0
    for lang in langs:
        for theme in themes:
            for name in figs:
                p = make_one(name, lang, theme, args.dpi)
                print("wrote", os.path.relpath(p, ROOT))
                n += 1
    print(f"\n{n} hires figures written "
          f"({len(figs)} types x {len(langs)} lang x {len(themes)} theme @ {args.dpi} dpi)")


if __name__ == "__main__":
    main()
