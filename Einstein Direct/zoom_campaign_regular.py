#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗУМ-КАМПАНИЯ (ПРОТОКОЛ): РЕГУЛЯРНОЕ ЗАМЫКАНИЕ ЦЕНТРА
=====================================================
Отличия от базовой кампании (zoom_campaign.py):
  * зум-стадии работают с center_closure="regular" (связка наклонов
    s1-t1 = -2a вместо клэмпа a=0), кубическая масса в зоне, проекция
    чётных частей (p+q) и (c+d), тейперная реконструкция;
  * протоколируются СПИНОРНЫЕ диагностики стены: max|E| (чётная мода),
    max|O| (нечётная/спинорная мода) в зоне и на кольце в момент стопа;
  * max_zooms=4.
Статус: честный протокол. Чистые сверхкритические вердикты и Delta на
процентном уровне НЕ достигнуты (стена z ~ 3.6-5.9); см. README §13-14.

Запуск:  python3 zoom_campaign_regular.py       # ~5-8 мин
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from zoom_solver import (ZoomRunner, echo_peaks, RESULTS, V_P, SIGMA)

A_FIXED_GRID = 0.0805333
GAMMA_LIT = 0.374
DELTA_LIT = 0.737637
B_CH = 1 - np.cos(2 * np.pi / 7)

OUT_PATH = os.path.join(RESULTS, "zoom_campaign_regular.json")


def junk_diag(runner):
    """Спинорные диагностики стены на финальной строке."""
    sol = runner.sol
    r = sol.r; t = getattr(sol, "t", None); s = getattr(sol, "s", None)
    du = runner.du
    if t is None or s is None:
        return {}
    ra = np.abs(r)
    i0 = int(np.argmin(ra))
    R_heal = float(getattr(sol, "R_heal", 0.0))
    R_zone = max(sol.reg_zone_du * du, 1.2 * R_heal)
    zone = ra <= R_zone
    ring = (r > R_zone) & (r <= 4 * R_zone)
    G = t + s
    K = int(min(R_zone / du, i0, len(r) - 1 - i0))
    E_max = O_max = float("nan")
    if K >= 1:
        ks = np.arange(0, K + 1)
        E = 0.25 * (G[i0 - ks] + G[i0 + ks])
        O = 0.5 * (t[i0 - ks] - s[i0 - ks])
        E_max = float(np.nanmax(np.abs(E)))
        O_max = float(np.nanmax(np.abs(O)))
    return {
        "R_zone_over_du": float(R_zone / du),
        "max_abs_t_zone": float(np.nanmax(np.abs(t[zone]))) if zone.any() else None,
        "max_abs_t_ring": float(np.nanmax(np.abs(t[ring]))) if ring.any() else None,
        "E_max_zone": E_max,
        "O_max_zone": O_max,
    }


def main():
    t0 = time.time()
    out = {
        "config": {"n": 800, "max_zooms": 4, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA,
                   "center_closure": "regular (s1-t1 link, m~r^3, "
                                     "pq/cd parity projection, taper)"},
        "a_star_source": "fixed-grid N=1600 bisection (validated, session 1)",
        "a_star": A_FIXED_GRID,
        "gamma_lit": GAMMA_LIT, "delta_lit": DELTA_LIT, "b_Ch": B_CH,
        "delta_spinor": 7 * np.pi / 30,
        "status": ("PROTOCOL: center junk suppressed (mass junk "
                   "3.56 -> 6.6e-5), depth wall persists (z ~ 3.6-5.9); "
                   "gamma/delta at percent level NOT achieved; spinor "
                   "diagnostics recorded (see README sec. 13-14)"),
    }

    print("=" * 72)
    print("ЗУМ-КАМПАНИЯ (регулярное замыкание): A*_fg = %.7f" % A_FIXED_GRID)
    print("=" * 72, flush=True)

    eps_list = [3e-5, 1e-4, 1e-3, 1e-2]
    runs = []
    for eps in eps_list:
        A = A_FIXED_GRID + eps
        r = ZoomRunner(A=A, n=800, max_zooms=4, verbose=False)
        d = r.run()
        tr = r.track
        rec = {
            "eps": eps, "A": A,
            "stop": d.stopped,
            "M_AH_frozen": float(d.m_ah),
            "M_AH_max_seen": float(d.m_ah_max),
            "zooms": d.zooms, "z_reached": float(r._z_acc),
            "mx_max": float(np.nanmax(tr["mx"])),
            "v_last": float(tr["v"][-1]) if tr["v"] else None,
            "runtime_s": round(d.runtime, 1),
            "junk_diag_at_stop": junk_diag(r),
        }
        vp, yp = echo_peaks(r.track, "Q")
        rec["Q_peaks_n"] = int(len(vp))
        rec["Q_peaks_v"] = [round(float(x), 5) for x in vp[:12]]
        runs.append(rec)
        print(f"  eps={eps:.1e}: stop={d.stopped}, M_frozen={d.m_ah:.6f}, "
              f"zooms={d.zooms}, z={r._z_acc:.2f}, "
              f"Q-пиков={len(vp)}", flush=True)
    out["runs"] = runs

    z_max = max(r_["z_reached"] for r_ in runs)
    n_ah = sum(1 for r_ in runs if r_["M_AH_frozen"] > 0)
    out["summary"] = {
        "z_max_reached": z_max,
        "runs_with_frozen_AH": n_ah,
        "gamma_measured": None,
        "delta_measured": None,
        "percent_level_achieved": False,
        "achievements": [
            "массовый мусор у центра подавлен (max M_AH junk 3.56 -> 6.6e-5)",
            "кольцо [R_zone, 4R_zone] стабильно до самого стопа",
            "механизм стены уточнён: чётная мода E у центра + 1/r-связка "
            "через чётную добавку (p+q); сырое марширование вне зоны несёт "
            "O(1)-нарушение спинорных парностей (см. spinor_analysis.json)",
            "глубина: z до 5.85 (4 зума, eps=1e-4)",
        ],
        "roadmap": [
            "центральный Тейлор-патч (Чоптюк 1993): эволюция коэффициентов "
            "регулярного разложения (t0, a, ...) как внутреннего ГУ",
            "спинорная модуляция pi/15, pi/30 требует z >= 30 (>= 40 эхо)",
        ],
    }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t0:.0f} c)")


if __name__ == "__main__":
    main()
