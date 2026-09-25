#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
КАМПАНИЯ ЧОПТЮКА С ЗУМАМИ (v2, честный прототип)
=================================================
Статус: машина мульти-зумов v2 — ПРОТОТИП. Цепочка достигает z ~ 2-5
(1-3 зума), для сверхкритических амплитуд рестарт после зума #1-2 ещё
загрязняется (см. zoom_wall_diagnosis ниже). Поэтому:

  * бисекция A* берётся ВАЛИДИРОВАННАЯ (фиксированная сетка N=1600,
    прошлая сессия, choptuik_scaling.json);
  * эта кампания = протокольный прогон семейства зум-забегов: для сетки
    eps замеряется достигнутая глубина z, вердикт sub/super, масса
    горизонта (если горизонт заморожен ДО мусорного взрыва), точки
    отказа. Результат — документация стены глубины, а не измерение
    gamma/delta на уровне процента.

Запуск:  python3 zoom_campaign.py            # ~10-15 мин
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from zoom_solver import (ZoomRunner, echo_peaks, echo_period_from_peaks,
                         RESULTS, V_P, SIGMA)

A_FIXED_GRID = 0.0805333   # валидированная бисекция N=1600 (сессия 1)
GAMMA_LIT = 0.374
DELTA_LIT = 0.737
B_CH = 1 - np.cos(2 * np.pi / 7)   # 0.3765 (гипотеза монографии)

OUT_PATH = os.path.join(RESULTS, "zoom_campaign.json")


def run_zoom(A, n=800, max_zooms=3):
    r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=False)
    d = r.run()
    return r, d


def classify(r, d):
    """Честная классификация исхода забега."""
    tr = r.track
    mx = np.array(tr["mx"])
    if d.m_ah > 0 and mx.max() < 1.5:
        return "supercritical (AH frozen, clean)"
    if d.supercritical or d.m_ah_max > 0:
        return "contaminated (junk 2m/r explosion before/without clean AH)"
    if d.stopped in ("completed", "v_exhausted") and mx.max() < 0.9:
        return "subcritical (dispersal)"
    return "ambiguous"


def main():
    t0 = time.time()
    out = {
        "config": {"n": 800, "max_zooms": 3, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA},
        "a_star_source": "fixed-grid N=1600 bisection (validated, session 1)",
        "a_star": A_FIXED_GRID,
        "gamma_lit": GAMMA_LIT, "delta_lit": DELTA_LIT, "b_Ch": B_CH,
        "status": "PROTOTYPE: zoom chain reaches z~2-5; gamma/delta at "
                  "percent level NOT achieved; wall diagnosed (see "
                  "zoom_wall_diagnosis)",
    }

    print("=" * 72)
    print("ЗУМ-КАМПАНИЯ v2 (честный прототип): A*_fg = %.7f" % A_FIXED_GRID)
    print("=" * 72, flush=True)

    # --- серия зум-забегов по eps ----------------------------------------
    eps_list = [3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]
    runs = []
    for eps in eps_list:
        A = A_FIXED_GRID + eps
        r, d = run_zoom(A)
        cls = classify(r, d)
        tr = r.track
        rec = {
            "eps": eps, "A": A,
            "verdict": cls,
            "stop": d.stopped,
            "M_AH_frozen": float(d.m_ah),
            "M_AH_max_seen": float(d.m_ah_max),
            "zooms": d.zooms, "z_reached": float(r._z_acc),
            "mx_max": float(np.nanmax(tr["mx"])),
            "v_last": float(tr["v"][-1]) if tr["v"] else None,
            "runtime_s": round(d.runtime, 1),
        }
        # пики Q (для будущей дельты)
        vp, yp = echo_peaks(r.track, "Q")
        rec["Q_peaks_n"] = int(len(vp))
        rec["Q_peaks_v"] = [round(float(x), 5) for x in vp[:10]]
        runs.append(rec)
        print(f"  eps={eps:.1e}: {cls}")
        print(f"    stop={d.stopped}, M_frozen={d.m_ah:.5f}, "
              f"M_max={d.m_ah_max:.5f}, zooms={d.zooms}, z={r._z_acc:.2f}, "
              f"mx_max={rec['mx_max']:.3g}, Q-пиков={len(vp)}", flush=True)
    out["runs"] = runs

    # --- сводка ------------------------------------------------------------
    z_max = max(r_["z_reached"] for r_ in runs)
    n_clean_super = sum(1 for r_ in runs if r_["verdict"].startswith("supercritical"))
    n_sub = sum(1 for r_ in runs if r_["verdict"].startswith("subcritical"))
    out["summary"] = {
        "z_max_reached": z_max,
        "clean_supercritical_runs": n_clean_super,
        "clean_subcritical_runs": n_sub,
        "contaminated_runs": len(runs) - n_clean_super - n_sub,
        "gamma_measured": None,
        "delta_measured": None,
        "percent_level_achieved": False,
    }
    out["zoom_wall_diagnosis"] = {
        "symptom": ("после рестарта на зуме #1-2 для сверхкритических A "
                    "поля t,s взрываются у центра (2m/r ~ 60-5e10) до "
                    "настоящего горизонта; бисекция зум-забегами смещается"),
        "root_cause_1": ("клэмп t=s в зоне |r|<=5du навязывает неполное "
                         "регулярное условие: точная регулярность требует "
                         "pt+qs = O(r) и нетривиальной связки наклонов "
                         "(s1-t1); при t=s возникает член s_v = (p+q)s/r ~ "
                         "2c's, взрывающийся при быстром сжатии (c' ~ 1/ell)"),
        "root_cause_2": ("паразитная однородная мода ODE t_u = -(pt+qs)/r "
                         "растёт как 1/r к центру; фильтрация неудовлетвори -"
                         "тельна, т.к. физическая сходящаяся волна тоже "
                         "усиливается ~ 1/r и не отделяется локально"),
        "root_cause_3": ("интерполяционный рестарт переносит границу "
                         "клэмп-зоны родителя (5 du_parent = 5 lambda du_new "
                         "клеток) в область, которую лTreatment не покрывает"),
        "fix_roadmap": ("центральное ОДУ (подход Чоптюка 1993): интегрировать "
                        "регулярное разложение у центра (Phi0, s0=t0, "
                        "вторые производные) как внутреннее ГУ и маршировать "
                        "t наружу; тогда рестарты чисты и цепочка z>=10 "
                        "(5-7 зумов) даёт gamma на уровне процента и delta"),
        "z_needed_for_percent_gamma": "z ~ 10-12 (eps_rel до 1e-5, 6-8 эхо)",
    }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t0:.0f} c)")


if __name__ == "__main__":
    main()
