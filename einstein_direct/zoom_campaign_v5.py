#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗУМ-КАМПАНИЯ v5: центральный Тейлор-патч (машино-выведенная иерархия центра)
============================================================================
Отличия от v3.2-кампании:
  * зум-стадии работают с center_closure="taylor": коэффициенты регулярного
    разложения центра (t0, d0) эволюционируют по машино-выведенным ОДУ
    (sympy_center.py: O1 t0'=3P2-4d0t0, O3 d0'=M3/R1+W2-kappa*t0^2) как
    внутреннее ГУ (подход Чоптюка 1993);
  * чётная паразита (p+q) — источник взрыва E-моды — проектируется с учётом
    смещения центра x*; зона реконструкции покрывает ПОЛНЫЙ радиус
    (фактор 2 в клетках: xi = k*du/2);
  * масса Чёрной дыры для скейлинга: M(eps) = max по забегу массы на
    пересечении q=0 (m_ah_max), пост-обработка; фит gamma = d ln M/d ln eps;
  * ДСС-диагностика: пики кривизны Q(v), фит Delta.
Статус пишется ЧЕСТНО: что достигнуто, что нет.

Запуск:  python3 zoom_campaign_v5.py            # ~20-40 мин
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from zoom_solver import (ZoomRunner, echo_peaks, echo_period_from_peaks,
                         RESULTS, V_P, SIGMA)

A_FIXED_GRID = 0.0805333
GAMMA_LIT = 0.374
DELTA_LIT = 0.737637
B_CH = 1 - np.cos(2 * np.pi / 7)

OUT_PATH = os.path.join(RESULTS, "zoom_campaign_v5.json")

EPS_LIST = [3e-5, 1e-4, 3e-4, 1e-3, 1e-2]

if len(os.sys.argv) > 1:          # подмножество eps для чанкового запуска
    EPS_LIST = [float(x) for x in os.sys.argv[1].split(",")]


def main():
    t0 = time.time()
    out = {
        "config": {"n": 800, "max_zooms": 12, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA,
                   "center_closure": "taylor (v5: ODE-evolved t0/d0, "
                                     "offset-aware (p+q) projection, "
                                     "full-radius zone, m~M3*xi^3)",
                   "eps_list": EPS_LIST},
        "a_star_source": "fixed-grid N=1600 bisection (validated, session 1)",
        "a_star": A_FIXED_GRID,
        "gamma_lit": GAMMA_LIT, "delta_lit": DELTA_LIT, "b_Ch": B_CH,
        "delta_spinor": 7 * np.pi / 30,
        "runs": [],
    }

    # чанковые запуски: подхватываем предыдущие результаты (другие eps)
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, encoding="utf-8") as fh:
                prev = json.load(fh)
            keep = [r for r in prev.get("runs", [])
                    if r["eps"] not in EPS_LIST]
            if keep:
                out["runs"].extend(keep)
                print(f"(подхвачено {len(keep)} прогонов предыдущих чанков)")
        except Exception:
            pass

    print("=" * 72)
    print("ЗУМ-КАМПАНИЯ v5 (Тейлор-патч центра): A*_fg = %.7f" % A_FIXED_GRID)
    print("=" * 72, flush=True)

    for eps in EPS_LIST:
        A = A_FIXED_GRID + eps
        r = ZoomRunner(A=A, n=800, max_zooms=12, verbose=False)
        d = r.run()
        tr = r.track
        rec = {
            "eps": eps, "A": A,
            "stop": d.stopped,
            "M_AH_frozen": float(d.m_ah),
            "M_AH_max_seen": float(d.m_ah_max),
            "zooms": d.zooms, "z_reached": float(r._z_acc),
            "mx_max": float(np.nanmax(tr["mx"])),
            "runtime_s": round(d.runtime, 1),
            "stage_constraints": [
                {"zoom": c["zoom"], "lam": round(c["lam"], 3),
                 "z": round(c["z"], 4), "c1_max": c["c1_max"]}
                for c in d.stage_constraints],
        }
        # эхо: пики Q на всей пост-зумовой части
        vp, yp = echo_peaks(r.track, "Q")
        rec["Q_peaks_n"] = int(len(vp))
        if len(vp) >= 4:
            D, Derr, npk = echo_period_from_peaks(vp)
            rec["Delta_ln_intervals"] = {"Delta": float(D), "err": float(Derr),
                                         "n": int(npk)}
        rec["Q_peaks_v"] = [round(float(x), 6) for x in vp[:16]]
        # сводка тейлор-гистограмм по стадиям
        tay_summ = []
        sol_hist = getattr(r.sol, "_tay", None)
        if sol_hist and sol_hist.get("hist"):
            h = sol_hist["hist"]
            tay_summ.append({"stage": "last",
                             "rows": len(h),
                             "t0_last": h[-1]["t0"], "t0_max": max(abs(x["t0"]) for x in h),
                             "P2_last": h[-1]["P2"],
                             "C0_median": float(np.median([x["C0_gauge"] for x in h])),
                             "pq_even_median": float(np.median([x["pq_even_max"] for x in h])),
                             "fallbacks": sol_hist["fallbacks"]})
        rec["taylor_summary_last_stage"] = tay_summ
        out["runs"].append(rec)
        print(f"  eps={eps:.1e}: stop={d.stopped}, M_frozen={d.m_ah:.6f}, "
              f"M_max={d.m_ah_max:.6f}, zooms={d.zooms}, z={r._z_acc:.2f}, "
              f"Q-пиков={len(vp)}", flush=True)

    # --- скейлинг gamma: M(eps) = M_AH_max_seen ---------------------------
    ok = [(r_["eps"], r_["M_AH_max_seen"]) for r_ in out["runs"]
          if r_["M_AH_max_seen"] > 1e-8]
    out["gamma_fit"] = None
    if len(ok) >= 3:
        xs = np.log(np.array([e for e, _ in ok]))
        ys = np.log(np.array([m for _, m in ok]))
        Am = np.vstack([xs, np.ones_like(xs)]).T
        sol_, res, *_ = np.linalg.lstsq(Am, ys, rcond=None)
        gamma = float(sol_[0])
        yfit = Am @ sol_
        dof = max(len(xs) - 2, 1)
        s2 = float(((ys - yfit) ** 2).sum()) / dof
        cov = s2 * np.linalg.inv(Am.T @ Am)
        out["gamma_fit"] = {
            "method": "ln M vs ln eps, M = M_AH_max_seen (пост-обработка)",
            "gamma": gamma, "gamma_err": float(np.sqrt(max(cov[0, 0], 0.0))),
            "n_points": len(ok),
            "vs_gamma_lit_dev": abs(gamma - GAMMA_LIT) / GAMMA_LIT,
            "vs_b_Ch_dev": abs(gamma - B_CH) / B_CH,
            "points": [{"eps": e, "M": m} for e, m in ok],
        }

    z_max = max(r_["z_reached"] for r_ in out["runs"])
    n_ah = sum(1 for r_ in out["runs"] if r_["M_AH_frozen"] > 0)
    out["summary"] = {
        "z_max_reached": z_max,
        "runs_with_frozen_AH": n_ah,
        "delta_measured": None,
        "percent_level_achieved": bool(out["gamma_fit"]
                                       and out["gamma_fit"]["gamma_err"] < 0.02),
        "v5_achievements": [
            "машино-выведенная иерархия центра (sympy_center.py): O1-O5, "
            "все формы верифицированы SymPy; численная верификация O1/O2 "
            "на подкритическом забеге (O2: 1.1e-3, O1: 2.8e-2)",
            "центральный Тейлор-патч: t0/d0 эволюционируют как внутреннее ГУ",
            "глубина цепочки: z_max = %.2f (v3.2: 6.05)" % z_max,
        ],
        "v6_roadmap": [
            "устойчивый захват горизонта на глубоких стадиях "
            "(порог r > 8du и критерий устойчивости 6 строк)",
            "спинорная модуляция pi/15, pi/30 требует z >= 30",
        ],
    }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t0:.0f} c)")
    if out["gamma_fit"]:
        gf = out["gamma_fit"]
        print(f"gamma = {gf['gamma']:.4f} +- {gf['gamma_err']:.4f} "
              f"(lit {GAMMA_LIT}, dev {gf['vs_gamma_lit_dev']:.2%}; "
              f"b_Ch {B_CH:.6f}, dev {gf['vs_b_Ch_dev']:.2%})")


if __name__ == "__main__":
    main()
