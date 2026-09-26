#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
O6-ТОЧКА: ЧИСЛЕННЫЙ АНАЛИЗ (nsolve) — СВЯЗЫВАЕТ ЛИ РАСШИРЕННАЯ БАШНЯ tau?
O6 FIXED POINT: NUMERIC ANALYSIS (nsolve) — DOES THE EXTENDED TOWER PIN tau?
================================================================================

Урок первой попытки: z_tower решает N-уровни ДЕЛЕНИЕМ на dR1 (коэффициент при
dW2 в C2[xi^3] пропорционален dR1) — в неподвижной точке dR1 = 0 это полюса
(zoo). Корректная процедура: система точки строится из СЫРЫХ очищенных
z-коэффициентов ВСЕХ порядков (каждый коэффициент Тейлора остатка обязан
исчезать); потоки (dT0, dD0, ddQ, dR1, dW2, dR3, dP4, Q) = 0; уравнение =
числитель после cancel (защита от spurious-полюсов).

  1. Машинный вывод уровней O6+ (импорт sympy_center_o6).
  2. Сырые z-коэффициенты -> точка: ~13 уравнений на 10 неизвестных
     (T0, P2h, D0, R1h, W2h, R3h, P4h, R5h, M5h, M3h).
  3. nsolve из СЕМЕНИ АНАЛИТИКИ O1-O5 (без подгонки: D0*=0, P2h*=T0/3,
     W2h*=(4/3)tau, R3h*=(2/9)tau, M3h*=(2/3)tau, R1h*=1 — калибровка).
  4. Вердикт: связана ли T0 (tau* = T0*^2 из первых принципов).
  5. Если tau* найдена: lambda+(tau*) из точного char-полинома замкнутой
     башни (center_modes.json) -> gamma_tower = Delta/lambda+.

Запуск: python3 sympy_center_o6_nsolve.py   (~2-4 мин, results/center_o6_nsolve.json)
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy_center_o6 as o6  # noqa: E402

RESULTS = o6.RESULTS
log = print

ORDERS = {"SC": 5, "UV": 3, "C2": 3, "TH": 3, "C1": 3, "Mdef": 6}


def build_raw_fp_equations(coeffs, lv):
    """Сырые коэффициенты остатков -> z-форма -> уравнения точки.

    Каждый коэффициент Тейлора остатка обязан исчезать; на неподвижной точке
    все z-потоки нулевые. Уравнение = числитель после cancel (защита от
    ложных полюсов), знаменатель сохраняется как условие регулярности.
    """
    subs_lower = {
        o6.P0.diff(o6.y, 2): lv["O1"],
        o6.R1.diff(o6.y): lv["O2"],
        o6.W0.diff(o6.y, 2): lv["O3"],
        o6.P2.diff(o6.y, 2): lv["O5"],
        o6.M3: lv["O4"],
    }
    zero_flows = {o6.dT0: 0, o6.dD0: 0, o6.ddQ: 0, o6.dR1: 0,
                  o6.dW2: 0, o6.dR3: 0, o6.dP4: 0, o6.Q: 0}
    eqs, denom_conds = {}, {}
    for nm, need in ORDERS.items():
        for k in range(need + 1):
            co = coeffs[nm][k].subs(subs_lower)
            kk, ze = o6.purify(o6.to_z(co))
            if kk is None:
                continue                       # не очистилась — пропускаем честно
            ze = ze.subs(zero_flows)
            ze = sp.cancel(sp.together(sp.expand(ze)))
            num, den = sp.fraction(ze)
            num = sp.simplify(sp.expand(num))
            if num == 0:
                continue
            eqs[f"{nm}_xi{k}"] = num
            if den != 1:
                denom_conds[f"{nm}_xi{k}"] = sp.sstr(sp.simplify(den))
    return eqs, denom_conds


def nsolve_point(eq_list, unk, verbose=True):
    """nsolve из сетки сидов (аналитика O1-O5 + возмущения)."""
    n = len(unk)

    def seed_vec(t0v):
        t = t0v * t0v
        base = [t0v, t0v / 3.0, 0.0, 1.0, 4.0 * t / 3.0, 2.0 * t / 9.0,
                t0v * (27.0 + 16.0 * t) / 270.0, 0.0, 0.0, 2.0 * t / 3.0]
        return base[:n]

    res_funcs = []
    for e in eq_list:
        try:
            res_funcs.append(sp.lambdify(unk, e, "numpy"))
        except Exception:  # noqa: BLE001
            res_funcs.append(None)

    def resid(vec):
        vals = []
        for f in res_funcs:
            if f is None:
                continue
            try:
                v = float(f(*vec))
            except Exception:  # noqa: BLE001
                return float("inf")
            if not np.isfinite(v):
                return float("inf")
            vals.append(v)
        return float(np.max(np.abs(vals))) if vals else float("inf")

    sols, seen = [], []
    rng = np.random.default_rng(11)
    for t0s in (0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 0.1, 1.2):
        for trial in range(8):
            sv = np.array(seed_vec(t0s), dtype=float)
            if trial > 0:
                sv = sv * (1.0 + 0.3 * rng.standard_normal(n))
                sv[2] = 0.0                      # D0* = 0 (аналитика O1-O5)
                sv[3] = 1.0                      # калибровка R1h* = 1
                sv = np.abs(sv)                  # физическая ветка (s>0, R1>0)
            try:
                sol = sp.nsolve(eq_list, unk, list(sv), tol=1e-14,
                                maxsteps=150, prec=30)
            except Exception:  # noqa: BLE001
                continue
            vec = np.array([float(sol[i]) for i in range(n)], dtype=float)
            if not np.all(np.isfinite(vec)):
                continue
            r = resid(vec)
            if r > 1e-7:
                continue
            key = np.round(vec / max(abs(vec[3]), 1e-12), 6)
            if any(np.allclose(key / max(abs(k[3]), 1e-12), k0, rtol=1e-4)
                   for k0 in seen):
                continue
            seen.append(key)
            rec = {"seed_T0": t0s, "residual": r,
                   "values": {sp.sstr(u): float(vec[i])
                              for i, u in enumerate(unk)}}
            sols.append(rec)
            if verbose:
                log("    [nsolve] T0=%.6f P2h=%.5f D0=%.1e R1h=%.5f "
                    "W2h=%.5f R3h=%.6f P4h=%.6f R5h=%.3e M5h=%.3e "
                    "M3h=%.5f  res=%.1e" % (
                        vec[0], vec[1], vec[2], vec[3], vec[4], vec[5],
                        vec[6], vec[7], vec[8], vec[9], r))
            break
    return sols


def main():
    t_wall = time.time()
    out = {"config": {"method": "raw-coefficient fixed point + nsolve multi-seed",
                      "kappa": int(o6.KAPPA_S),
                      "zero_flows": ["dT0", "dD0", "ddQ", "dR1", "dW2",
                                     "dR3", "dP4", "Q"]},
            "honest_notes": []}
    try:
        log("[1/4] Остатки -> series -> уровни O1-O5 + O6+...")
        coeffs = {nm: o6.series_coeffs(res, ORDERS[nm])
                  for nm, res in o6.RESIDUALS.items()}
        lv, ok = o6.lower_levels(coeffs)
        for k_, v_ in ok.items():
            out.setdefault("verify", {})[k_] = sp.sstr(v_)
            assert sp.sstr(v_) == "0", f"форма {k_} не верифицирована"
        found, dep = o6.find_next_levels(coeffs, lv)
        ver = o6.verify_levels(coeffs, found, lv)
        out["levels_found"] = {f"{nm}_xi{k}": {"target": t, "verify": sp.sstr(ver.get(f"{nm}_xi{k}_{t}", "?"))}
                               for (nm, k), (t, f) in found.items()}

        log("[2/4] Сырые z-коэффициенты -> система точки...")
        eqs, denoms = build_raw_fp_equations(coeffs, lv)
        out["n_equations"] = len(eqs)
        out["equations"] = {k_: sp.sstr(v_) for k_, v_ in eqs.items()}
        out["denominator_conditions"] = denoms
        log(f"    нетривиальных уравнений: {len(eqs)}: {list(eqs.keys())}")

        log("[3/4] nsolve из сетки сидов...")
        unk = [o6.T0, o6.P2h, o6.D0, o6.R1h, o6.W2h, o6.R3h, o6.P4h,
               o6.R5h, o6.M5h, o6.M3h]
        eq_list = [sp.sympify(e) for e in eqs.values()]
        sols = nsolve_point(eq_list, unk)
        out["solutions"] = sols
        if not sols:
            out["pinning"] = {"tau_pinned": None,
                              "note": "решений не найдено (система, "
                                      "возможно, переопределена несовместно)"}
            out["honest_notes"].append(
                "nsolve не нашёл точку: сырая система может быть "
                "несовместной — это означало бы, что CSS-анзац уровня O6+ "
                "не имеет точного решения (усечение противоречиво)")
        else:
            t0s = sorted({round(s["values"]["T0h"], 8) for s in sols})
            pinned = len(t0s) == 1
            out["pinning"] = {
                "t0_solutions": t0s, "n_distinct_T0": len(t0s),
                "tau_pinned": bool(pinned),
                "tau_star": (t0s[0] * t0s[0]) if pinned else None,
                "codim1_window_0_tau_27_80": bool(
                    pinned and 0.0 < t0s[0] * t0s[0] <= 27.0 / 80.0),
                "note": ("единственная T0* при R1h*=1: башня СВЯЗЫВАЕТ "
                         "амплитуду из первых принципов" if pinned else
                         "T0 не связана: семейство точек — амплитуда "
                         "остаётся свободной на уровне O6+"),
            }
            log(f"    вердикт: {out['pinning']['note']} "
                f"(T0 = {t0s}, tau* = {out['pinning']['tau_star']})")

            if pinned:
                tau_s = t0s[0] * t0s[0]
                try:
                    with open(os.path.join(RESULTS, "center_modes.json"),
                              encoding="utf-8") as fh:
                        cm = json.load(fh)
                    curve = cm["part3"]["gamma_curve"]
                    ts = np.array([c["tau"] for c in curve])
                    ls = np.array([c["lambda_plus"] for c in curve])
                    o_ = np.argsort(ts)
                    lam_p = float(np.interp(np.log(max(tau_s, 1e-12)),
                                            np.log(ts[o_]), ls[o_]))
                    out["gamma_tower"] = {
                        "tau_star": tau_s,
                        "lambda_plus_tower": lam_p,
                        "note": ("lambda+(tau) — точный корень "
                                 "характеристического многочлена замкнутой "
                                 "башни O1-O5 (center_modes.py)"),
                    }
                    log(f"    lambda+(tau*) = {lam_p:.5f}")
                except Exception as e:  # noqa: BLE001
                    out["gamma_tower_error"] = str(e)
    except Exception:  # noqa: BLE001
        out["error"] = traceback.format_exc()
        log(out["error"][-800:])

    out["runtime_s"] = round(time.time() - t_wall, 1)
    with open(os.path.join(RESULTS, "center_o6_nsolve.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    log(f"Сохранено: results/center_o6_nsolve.json ({out['runtime_s']} c)")


if __name__ == "__main__":
    main()
