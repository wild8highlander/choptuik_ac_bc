#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВАЛИДАЦИЯ 1: эволюция точного решения Робертса–Оширо.

Решение Робертса–Оширо (исправленная форма, Burko gr-qc/9608061) — точное
решение полной системы Эйнштейн–скаляр в двунулевых координатах (alpha = 1).
Солвер инициализируется на решении и должен его воспроизводить; рост ошибки
измеряет точность схемы.

Запуск:  python3 roberts_test.py
Вывод:   results/roberts_test.json
"""
import json
import os

import numpy as np

from solver import DoubleNullSolver, RobertsData, SolverConfig

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)


def roberts_error(n_u, n_v, sigma=0.1, u_range=(-0.3, 0.7), v_range=(1.0, 2.0)):
    """Эволюция на решении Робертса и максимальная ошибка в конце.

    Домен — полоса, где решение гладкое: сингулярности Робертса лежат на
    u = v(1 - 2*sigma) и u = v(1 + 2*sigma); при sigma = 0.1 это u = 0.8v:
    требуется u_max < 0.8 * v_min (для v_min = 1: u_max = 0.7 < 0.8 OK).
    """
    data = RobertsData(sigma=sigma)
    cfg = SolverConfig(n_u=n_u, n_v=n_v, u_range=u_range, v_range=v_range,
                       monitor_every=max(1, n_v // 8))
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)

    v_f = sol.v_final
    r_ex, Phi_ex, _, _, _, _ = data.fields(sol.u, np.full_like(sol.u, v_f))
    err_r = float(np.max(np.abs(sol.r - r_ex)))
    err_Phi = float(np.max(np.abs(sol.Phi - Phi_ex)))
    err_a2 = float(np.max(np.abs(sol.alpha2 - 1.0)))
    # относительная ошибка (характерная амплитуда r ~ 1, Phi ~ O(sigma))
    scale_Phi = float(np.max(np.abs(Phi_ex))) or 1.0
    return {
        "n_u": n_u, "n_v": n_v, "sigma": sigma,
        "v_final": float(v_f),
        "err_r": err_r,
        "err_Phi": err_Phi,
        "err_Phi_rel": err_Phi / scale_Phi,
        "err_alpha2": err_a2,
        "c1_max": diag.c1_max,
        "c2_max": diag.c2_max,
        "mdef_max": diag.mdef_max,
        "runtime_s": sol.runtime,
    }


def main():
    print("=" * 72)
    print("ТЕСТ РОБЕРТСА: эволюция точного решения Робертса–Оширо (sigma = 0.1)")
    print("=" * 72)
    results = []
    for n in (200, 400, 800):
        res = roberts_error(n, n)
        results.append(res)
        print(f"  N = {n:5d}: err_r = {res['err_r']:.3e}, "
              f"err_Phi = {res['err_Phi']:.3e} (отн. {res['err_Phi_rel']:.3e}), "
              f"err_alpha^2 = {res['err_alpha2']:.3e}, "
              f"C1 = {res['c1_max']:.1e}, время {res['runtime_s']:.1f} c")
    # порядок сходимости
    if len(results) >= 2:
        print("\n  Порядок сходимости (err_{N/2}/err_N):")
        for i in range(1, len(results)):
            o_r = np.log2(results[i - 1]["err_r"] / results[i]["err_r"]) if results[i]["err_r"] > 0 else float("nan")
            o_P = np.log2(results[i - 1]["err_Phi"] / results[i]["err_Phi"]) if results[i]["err_Phi"] > 0 else float("nan")
            print(f"    N {results[i-1]['n_u']} -> {results[i]['n_u']}: "
                  f"p_r = {o_r:.2f}, p_Phi = {o_P:.2f}")
    with open(os.path.join(RESULTS, "roberts_test.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\n  Сохранено: results/roberts_test.json")


if __name__ == "__main__":
    main()
