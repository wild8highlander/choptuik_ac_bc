#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗАДАЧА ЧОПТЮКА: бисекция критической амплитуды A* и универсальный
массовый скейлинг M_BH = C (A - A*)^gamma.

Семейство начальных данных: гауссов импульс на входящей характеристике
    Phi(u0, v) = A exp(-(v - v_p)^2 / (2 sigma^2)),
(аналог семейства Чоптюка 1993). Критерий "сверхкритичности" — образование
разрешённого apparent горизонта (q = r_v < 0 при r > 8 du); масса Чёрной дыры
— масса Мизнера–Шарпа на горизонте.

Запуск:  python3 choptuik_scaling.py [--n 1600] [--decades 3.0]
Вывод:   results/choptuik_scaling.json
"""
import argparse
import json
import os
import time

import numpy as np

from solver import DoubleNullSolver, GaussianPulseData, SolverConfig

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

# Геометрия семейства (T = 1)
U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0


def run_amplitude(A, n=800, monitor_every=200):
    """Прогон одной амплитуды. Возвращает (supercritical, M_BH, diag, sol)."""
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=U0, v0=V0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(U0, U1), v_range=(V0, V1),
                       monitor_every=monitor_every)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    return diag.ah_found, diag.m_ah, diag, sol


def bisect_critical(lo, hi, n=800, tol=1e-6, max_iter=40, verbose=True):
    """Бисекция по амплитуде: lo — субкритическая, hi — сверхкритическая."""
    assert not run_amplitude(lo, n)[0], "lo должно быть субкритическим"
    assert run_amplitude(hi, n)[0], "hi должно быть сверхкритическим"
    hist = []
    for it in range(max_iter):
        mid = 0.5 * (lo + hi)
        if hi - lo < tol:
            break
        sup, m, diag, _ = run_amplitude(mid, n)
        hist.append({"iter": it, "A": mid, "supercritical": bool(sup), "M_AH": m})
        if verbose:
            print(f"  [{it:2d}] A = {mid:.8f} -> {'SUPER' if sup else 'sub'} "
                  f"(M = {m:.3e}), интервал [{lo:.6f}, {hi:.6f}]")
        if sup:
            hi = mid
        else:
            lo = mid
    a_star = 0.5 * (lo + hi)
    return a_star, hist


def mass_scaling(a_star, n=3000, decades=3.5, n_points=10, verbose=True):
    """Серия сверхкритических прогонов A = A* + eps и фит скейлинга.

    Учитывает смещение бисекции порогом нуклеации горизонта: фит
    M = C (eps + delta)^gamma (3 параметра, scipy.optimize.curve_fit).
    """
    from scipy.optimize import curve_fit
    eps_list = 10.0 ** (-np.linspace(1.0, 1.0 + decades, n_points))
    data = []
    for eps in eps_list:
        A = a_star + eps
        sup, m, diag, sol = run_amplitude(A, n)
        if not sup or m <= 0 or m > 0.05:
            if verbose:
                print(f"  A - A* = {eps:.2e}: не сверхкритическое / M вне диапазона — пропуск")
            continue
        data.append({"A": A, "eps": eps, "M": m, "v_ah": diag.v_ah,
                     "stop": diag.stopped_reason})
        if verbose:
            print(f"  A - A* = {eps:.3e}: M_BH = {m:.6e} ({diag.stopped_reason})")

    eps_a = np.array([d["eps"] for d in data])
    M_a = np.array([d["M"] for d in data])

    def model(e, C, gamma, delta):
        return C * (e + delta) ** gamma

    p0 = [0.05, 0.374, 1e-4]
    try:
        popt, pcov = curve_fit(model, eps_a, M_a, p0=p0, maxfev=20000)
        C_f, gamma_f, delta_f = popt
        perr = np.sqrt(np.diag(pcov))
        resid = M_a - model(eps_a, *popt)
        ss_res = float(resid @ resid)
        ss_tot = float(((M_a - M_a.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    except Exception as e:
        C_f, gamma_f, delta_f, perr, r2 = 0.0, float("nan"), 0.0, np.zeros(3), float("nan")

    return {
        "gamma": float(gamma_f), "gamma_err": float(perr[1]),
        "C": float(C_f), "delta": float(delta_f), "delta_err": float(perr[2]),
        "r2": float(r2),
        "a_star": a_star, "n": n, "decades": decades,
        "points": data,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-bisect", type=int, default=1600)
    ap.add_argument("--n-scale", type=int, default=3000)
    ap.add_argument("--decades", type=float, default=3.5)
    args = ap.parse_args()

    print("=" * 72)
    print("ЗАДАЧА ЧОПТЮКА: бисекция A* и скейлинг M ~ (A - A*)^gamma")
    print("=" * 72)
    t0 = time.time()

    # грубые границы (из зонда)
    lo, hi = 0.05, 0.15
    print(f"\n1) Бисекция критической амплитуды в [{lo}, {hi}], N = {args.n_bisect}:")
    a_star, hist = bisect_critical(lo, hi, n=args.n_bisect, tol=1e-7)
    print(f"   A* = {a_star:.8f}")

    print(f"\n2) Массовый скейлинг, N = {args.n_scale}, {args.decades} декады:")
    fit = mass_scaling(a_star, n=args.n_scale, decades=args.decades)
    print(f"\n   gamma = {fit['gamma']:.4f} +- {fit['gamma_err']:.4f}")
    print(f"   (Чоптюк 1993: gamma = 0.374 +- 0.004)")
    print(f"   b_Ch = 1 - cos(2*pi/7) = {1 - np.cos(2*np.pi/7):.5f}")

    b_ch = 1 - np.cos(2 * np.pi / 7)
    out = {
        "family": {"u0": U0, "v_p": V_P, "sigma": SIGMA, "A_range": [lo, hi]},
        "a_star": a_star,
        "bisect_history": hist,
        "scaling": fit,
        "references": {"gamma_choptuik": 0.374, "b_Ch": b_ch},
        "comparison": {
            "b_Ch": b_ch,
            "gamma_measured": fit["gamma"],
            "gamma_measured_err": fit["gamma_err"],
            "b_Ch_minus_gamma": b_ch - fit["gamma"],
            "gamma_choptuik": 0.374,
        },
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(RESULTS, "choptuik_scaling.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\n   Сохранено: results/choptuik_scaling.json ({out['runtime_s']} c)")


if __name__ == "__main__":
    main()
