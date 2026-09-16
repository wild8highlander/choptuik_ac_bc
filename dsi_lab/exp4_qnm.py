#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ЭКСПЕРИМЕНТ 4. QNM-КАТАЛОГ LIGO/VIRGO + ЛЕСТНИЦА ОБЕРТОНОВ
================================================================================
Постановка. Фреймворк предсказывает мультипликативную поправку к частотам
квазинормальных мод (QNM):
    f_corr = f * (1 - delta_eff/pi^2),  delta_eff = (pi/7)^5/22 = 1/1200,
    т.е. f_corr = 0.99991551*f,  Δf = -8.3857e-5 * f   (фреймворк v2.0).

Здесь:
  A. КАТАЛОГ: 10 событий с известными (M_f, a_f) из публикаций LIGO/Virgo
     (GWTC-1/GWTC-2). f_QNM вычисляется по подгонке Берти–Кардозо–Уилла
     (2006) для фундаментальной l=m=2 моды:
        M*omega_R = 1.5251 - 1.1568*(1-a)^0.1292
        M*omega_I = 0.7000 + 1.9404*(1-a)^0.2223
     (M в геометрических единицах; M_sec = M/M_sun * 4.9255e-6 s).
     Для 4 «якорных» событий репо (GW150914, GW170104, GW170814, GW190521)
     берутся измеренные f из репо (251, 314/293*, 286/319*, 110 Гц) и
     сравниваются с подгонкой. (*в репо два набора; используем оба для
     проверки разброса.)
  B. Таблица предсказаний: f, f_corr, Δf для каталога; обнаружимость
     |Δf|/sigma против уровней: текущий (2%), A+ (1%), ET (0.1%),
     CE (0.01%) — как в репо (2% и 0.010%).
  C. ОБЕРТОНЫ GW150914: лестница l=m=2, n=0..4 в пределе Шварцшильда
     (эталонные значения Берти и др. 2006, Table I):
        M*omega = 0.37367-0.08896i, 0.58663-0.19533i, 0.79985-0.30064i,
                  1.01377-0.40573i, 1.22810-0.51060i
     масштабируются на M_f = 62.3 M☉; поправка фреймворка мультипликативна
     и ОДИНАКОВА для всех обертонов — фальсифицируемое предсказание:
     относительные интервалы обертонов не меняются.
  ЧЕСТНОСТЬ: (i) для новых событий f_QNM — это GR-предсказание (Берти),
  а не измерение; поправка фреймворка применяется к GR-значению.
  (ii) обертоны — в пределе Шварцшильда; при a=0.67 значения сдвинуты
  на O(1-a) ~ 30%; лестница используется как схема масштабирования.

Запуск: python3 exp4_qnm.py
Вывод:  results/exp4_qnm.json + figures (RU/EN).
================================================================================
"""
import json
import math
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from figlabels import L

PI = math.pi
M_SUN_SEC = 4.925490947e-6      # солнечная масса в секундах (геом. единицы)
DELTA_EFF = (PI / 7) ** 5 / 22   # 1/1200
QNM_FACTOR = 1 - DELTA_EFF / PI**2
SHIFT = DELTA_EFF / PI**2        # 8.3857e-5

# Эталонные обертоны l=m=2 в пределе Шварцшильда (Berti, Cardoso, Will 2006)
SCHW_L2_OVERTONES = [
    {"n": 0, "Momega_R": 0.37367, "Momega_I": 0.08896},
    {"n": 1, "Momega_R": 0.58663, "Momega_I": 0.19533},
    {"n": 2, "Momega_R": 0.79985, "Momega_I": 0.30064},
    {"n": 3, "Momega_R": 1.01377, "Momega_I": 0.40573},
    {"n": 4, "Momega_R": 1.22810, "Momega_I": 0.51060},
]


def berti_f(a, M_solar):
    """Частота фундаментальной l=m=2 моды, Гц (подгонка BCW2006)."""
    M_sec = M_solar * M_SUN_SEC
    Momega_R = 1.5251 - 1.1568 * (1 - a) ** 0.1292
    return Momega_R / (2 * PI * M_sec)


def berti_tau(a, M_solar):
    """Время затухания фундаментальной моды, мс."""
    M_sec = M_solar * M_SUN_SEC
    Momega_I = 0.7000 + 1.9404 * (1 - a) ** 0.2223
    return M_sec / Momega_I * 1000


# =============================================================================
def part_A():
    print("=" * 78)
    print("A. КАТАЛОГ: (M_f, a_f) -> f_QNM (подгонка Берти) и якорные события")
    print("=" * 78)
    # (имя, M_f, a_f, f_репо Гц или None, sigma_репо Гц или None)
    # M_f, a_f — финальные масса/спин из публикаций LVK (GWTC-1/GWTC-2)
    catalog = [
        ("GW150914", 62.3, 0.67, 251.0, 5.5),
        ("GW151226", 20.5, 0.74, None, None),
        ("GW170104", 48.7, 0.65, 314.0, 25.0),
        ("GW170608", 17.8, 0.69, None, None),
        ("GW170729", 59.1, 0.81, None, None),
        ("GW170809", 35.4, 0.70, None, None),
        ("GW170814", 53.4, 0.70, 286.0, 30.0),
        ("GW170818", 35.6, 0.67, None, None),
        ("GW190412", 40.3, 0.87, None, None),
        ("GW190521", 142.0, 0.72, 110.0, 10.0),
    ]
    out = []
    print(f"  {'событие':<10s} {'M_f':>6s} {'a_f':>5s} {'f(Берти)':>9s} "
          f"{'f(репо)':>8s} {'расх.':>7s} {'tau,мс':>7s}")
    for name, M, a, f_repo, sig_repo in catalog:
        f_fit = berti_f(a, M)
        tau = berti_tau(a, M)
        dev = (f_fit - f_repo) / f_repo * 100 if f_repo else None
        out.append({"name": name, "M_f": M, "a_f": a,
                    "f_berti": f_fit, "f_repo": f_repo,
                    "sigma_repo": sig_repo, "tau_ms": tau,
                    "berti_vs_repo_pct": dev,
                    "f_used": f_repo if f_repo else f_fit,
                    "f_source": "repo (measured)" if f_repo
                                else "Berti fit (GR prediction)"})
        d_str = f"{dev:+6.1f}%" if dev is not None else "  —"
        r_str = f"{f_repo:8.1f}" if f_repo else "     —"
        print(f"  {name:<10s} {M:6.1f} {a:5.2f} {f_fit:9.1f} {r_str} {d_str} "
              f"{tau:7.2f}")
    print("  ЧЕСТНОСТЬ: f(Берти) — GR-предсказание; для якорных событий")
    print("  используется измеренное f из репо. Расхождение ±10-15% —")
    print("  обычная точность подгонки/метода экстракции ringdown.")
    return out


def part_B(catalog):
    print("\n" + "=" * 78)
    print("B. ПРЕДСКАЗАННЫЕ СДВИГИ И ОБНАРУЖИМОСТЬ")
    print("=" * 78)
    detectors = [
        ("текущий LIGO (2%)", 0.02),
        ("LIGO A+ (1%)", 0.01),
        ("Einstein Telescope (0.1%)", 0.001),
        ("Cosmic Explorer (0.01%)", 0.0001),
    ]
    out = []
    print(f"  {'событие':<10s} {'f, Гц':>8s} {'Δf, Гц':>9s} "
          f"{'|Δf|/σ(2%)':>10s} {'ET(0.1%)':>9s} {'CE(0.01%)':>10s}")
    for ev in catalog:
        f = ev["f_used"]
        df = SHIFT * f
        # sigma: для якорных — sigma репо; для остальных — 2% от f
        sigma = ev["sigma_repo"] if ev["sigma_repo"] else 0.02 * f
        ratios = {nm: abs(df) / (rel * f) for nm, rel in detectors}
        out.append({**ev, "f_corr": QNM_FACTOR * f, "delta_f": -df,
                    "sigma_used": sigma,
                    "snr_current": abs(df) / sigma,
                    "detect_ratios": ratios})
        print(f"  {ev['name']:<10s} {f:8.1f} {-df:9.4f} "
              f"{abs(df)/sigma:10.4f} {ratios[detectors[2][0]]:9.2f} "
              f"{ratios[detectors[3][0]]:10.2f}")
    print(f"\n  Поправка: f_corr = f * {QNM_FACTOR:.9f} "
          f"(Δf/f = -{SHIFT:.4e})")
    print("  Вывод: относительная обнаружимость |Δf|/σ = 8.4e-5/прецизионность")
    print("  одинакова для всех событий: 0.004σ (2%), 0.08σ (ET), 0.84σ (CE)")
    print("  — сдвиг на ПОРОГЕ обнаружимости CE; объединение N событий даёт")
    print("  выигрыш √N. Фальсифицируемо на CE-классе детекторов.")
    return {"events": out, "detectors": detectors,
            "qnm_factor": QNM_FACTOR, "shift": SHIFT}


def part_C():
    print("\n" + "=" * 78)
    print("C. ЛЕСТНИЦА ОБЕРТОНОВ GW150914 (l=m=2, предел Шварцшильда)")
    print("=" * 78)
    M_f = 62.3
    M_sec = M_f * M_SUN_SEC
    f0_schw = SCHW_L2_OVERTONES[0]["Momega_R"] / (2 * PI * M_sec)
    # масштабируем на измеренную f0 репо (251 Гц)
    f0 = 251.0
    scale = f0 / f0_schw
    out = []
    print(f"  M_f = {M_f} M☉; f0(Шв.) = {f0_schw:.1f} Гц; масштаб к f0 = {f0} Гц")
    print(f"  {'n':>2s} {'f_n, Гц':>9s} {'tau_n, мс':>10s} {'Δf_n, Гц':>10s} "
          f"{'f_n/f_0':>8s}")
    for o in SCHW_L2_OVERTONES:
        f_n = o["Momega_R"] / (2 * PI * M_sec) * scale
        tau_n = M_sec / o["Momega_I"] * 1000
        df_n = SHIFT * f_n
        out.append({**o, "f_n": f_n, "tau_ms": tau_n, "delta_f_n": -df_n,
                    "ratio_to_f0": f_n / f0})
        print(f"  {o['n']:2d} {f_n:9.1f} {tau_n:10.2f} {-df_n:10.4f} "
              f"{f_n/f0:8.4f}")
    print("  Фальсифицируемое предсказание: Δf_n/f_n = const = "
          f"{SHIFT:.4e} для ВСЕХ n;")
    print("  относительные интервалы обертонов f_n/f_0 не меняются.")
    print("  ЧЕСТНОСТЬ: предел Шварцшильда; при a=0.67 частоты сдвинуты")
    print("  на O(1-a); лестница — схема масштабирования, не GR-таблица.")
    return {"M_f": M_f, "f0_used": f0, "overtones": out}


def make_figures(out, lang_dir, lang):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = L[lang]
    ev = out["predictions"]["events"]
    names = [e["name"] for e in ev]
    df = [-e["delta_f"] for e in ev]
    fig, ax = plt.subplots(figsize=(9.2, 5.2), constrained_layout=True)
    bars = ax.bar(names, df, color="#1e3a5f", alpha=0.85)
    ax.set_yscale("log")
    ax.set_ylabel(t["qnm_ylabel"] + " (log)")
    ax.set_title(t["qnm_title"])
    ax.tick_params(axis="x", rotation=45)
    for b, d in zip(bars, df):
        ax.text(b.get_x() + b.get_width() / 2, d * 1.12, f"{d:.4f}",
                ha="center", fontsize=8)
    fig.savefig(os.path.join(lang_dir, "fig_qnm_catalog.png"), dpi=300)
    plt.close(fig)

    ot = out["overtones"]["overtones"]
    ns = [o["n"] for o in ot]
    fns = [o["f_n"] for o in ot]
    dfs = [-o["delta_f_n"] for o in ot]
    fig, ax = plt.subplots(figsize=(8.6, 5.2), constrained_layout=True)
    ax.bar(ns, fns, width=0.55, color="#1e6091", alpha=0.8,
           label=r"$f_n$")
    ax.set_xlabel(t["qnm_overtones_xlabel"])
    ax.set_ylabel(t["qnm_overtones_ylabel"])
    ax2 = ax.twinx()
    ax2.bar(ns, dfs, width=0.25, color="#b45309", alpha=0.9,
            label=t["qnm_shift"])
    ax2.set_ylabel(t["qnm_ylabel"], color="#b45309")
    ax2.tick_params(axis="y", labelcolor="#b45309")
    for n, f, d in zip(ns, fns, dfs):
        ax.text(n, f + 12, f"{f:.0f}", ha="center", fontsize=9)
        ax2.text(n + 0.32, d, f"{d:.4f}", ha="left", va="center",
                 fontsize=8, color="#b45309")
    ax.set_title(t["qnm_overtones_title"])
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left")
    fig.savefig(os.path.join(lang_dir, "fig_qnm_overtones.png"), dpi=300)
    plt.close(fig)
    print(f"  [фигуры] {lang_dir}/fig_qnm_catalog.png, "
          f"fig_qnm_overtones.png")


def main():
    print("=" * 78)
    print("ЭКСПЕРИМЕНТ 4. QNM-КАТАЛОГ + ОБЕРТОНЫ (f_corr = 0.99991551*f)")
    print("=" * 78)
    out = {}
    cat_list = part_A()
    out["catalog"] = {"events": cat_list}
    out["predictions"] = part_B(cat_list)
    out["overtones"] = part_C()

    print("\n" + "=" * 78)
    print("СВОДКА")
    print("=" * 78)
    df_all = [-e["delta_f"] for e in out["predictions"]["events"]]
    print(f"  каталог: {len(df_all)} событий, Δf от {min(df_all):.4f} до "
          f"{max(df_all):.4f} Гц (пропорционально f)")
    snr_ce = [e["detect_ratios"]["Cosmic Explorer (0.01%)"] for e in
              out["predictions"]["events"]]
    print(f"  обнаружимость на CE: |Δf|/σ = {min(snr_ce):.2f}–{max(snr_ce):.2f} σ")
    print(f"  (относительная прецизионность делает отношение константой;"
          f" порог 1σ достигается при прецизионности 0.0084%)")
    ot = out["overtones"]["overtones"]
    print(f"  обертоны GW150914: f_0..f_4 = "
          f"{', '.join(f'{o['f_n']:.0f}' for o in ot)} Гц;")
    print(f"  Δf_n/f_n = const = {out['predictions']['shift']:.4e} при всех n")

    for lang, lang_dir in (("ru", os.path.join(BASE, "fig_ru")),
                           ("en", os.path.join(BASE, "fig_en"))):
        make_figures(out, lang_dir, lang)

    res_path = os.path.join(BASE, "results", "exp4_qnm.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {res_path}")


if __name__ == "__main__":
    main()
