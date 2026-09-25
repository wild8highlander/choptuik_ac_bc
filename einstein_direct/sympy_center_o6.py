#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
УРОВЕНЬ O6+: ДИНАМИКА ИСТОЧНИКОВ БАШНИ ЦЕНТРА (МАШИННЫЙ ВЫВОД)
TOWER LEVEL O6+: SOURCE DYNAMICS OF THE CENTER HIERARCHY (MACHINE DERIVATION)
================================================================================

Продолжение sympy_center.py (O1-O5 верифицированы) на СЛЕДУЮЩИЕ уровни башни.

Идея: иерархия O1-O5 использует не все коэффициенты разложения остатков по xi.
Неиспользованные коэффициенты — либо ЗАВИСИМЫЕ (обращаются в 0 после
подстановки нижних уровней), либо дают ДИНАМИКУ ИСТОЧНИКОВ: W2', P4', R3'
(в z-редукции center_modes.py они замораживались: dW2h=dR3h=dP4h=0 —
"стандартная линеаризация замкнутой башни", см. honest_notes части [III]).
Уровень O6+ размораживает источники.

Процедура башни (строгая):
  1. Расширенный анзац (chi = 0):
     r   = R1 xi + R3 xi^3 + R5 xi^5
     Phi = P0 + P2 xi^2 + P4 xi^4
     om  = W0 + W2 xi^2
     m   = M3 xi^3 + M5 xi^5
  2. Остатки SC/UV/C2/TH/C1/Mdef -> series по xi (sp.series — expand+coeff
     на рациональных функциях НЕВЕРЕН, урок sympy_center.py).
  3. Нижние уровни O1 (SC[0]), O2 (C2[0]), O3 (TH[0]), O4 (Mdef[3]),
     O5 (SC[2]) подставляются ВЫШЕ (каждый уровень использует все предыдущие).
  4. Оставшиеся ненулевые коэффициенты машина пытается решить относительно
     {W2', P4', P4'', R3', M5, R5} — найденные пары (коэффициент, цель)
     и есть уровни O6, O7, ... Каждая форма верифицируется обратной
     подстановкой (невязка = 0 тождественно).
  5. z-редукция (X = xhat(s) s^{-p}, ds/dy = -1) — таблица center_modes.py,
     размороженная: dR3h, dW2h, dP4h.
  6. Расширенная z-система -> CSS-неподвижная точка -> СВЯЗЫВАЕТ ЛИ ОНА tau?
     -> линеаризация -> спектр сходимости/отталкивания.

Запуск:  python3 sympy_center_o6.py        # ~1-3 мин, results/center_o6.json
"""
from __future__ import annotations

import json
import os
import time
import traceback

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

KAPPA_S = sp.Integer(2)
y, xi = sp.symbols('y xi', real=True)

# --- расширенный анзац (chi = 0) -------------------------------------------
R1 = sp.Function('R1')(y)
R3 = sp.Function('R3')(y)
R5 = sp.Function('R5')(y)
P0 = sp.Function('P0')(y)
P2 = sp.Function('P2')(y)
P4 = sp.Function('P4')(y)
W0 = sp.Function('W0')(y)
W2 = sp.Function('W2')(y)
M3 = sp.Function('M3')(y)
M5 = sp.Function('M5')(y)

r_e = R1 * xi + R3 * xi**3 + R5 * xi**5
Phi_e = P0 + P2 * xi**2 + P4 * xi**4
om_e = W0 + W2 * xi**2
m_e = M3 * xi**3 + M5 * xi**5
a2_e = sp.exp(2 * om_e)


def d_u(f):   # chi = 0
    return sp.Rational(1, 2) * sp.diff(f, y) - sp.Rational(1, 2) * sp.diff(f, xi)


def d_v(f):   # chi = 0
    return sp.Rational(1, 2) * sp.diff(f, y) + sp.Rational(1, 2) * sp.diff(f, xi)


s_e, t_e = d_u(Phi_e), d_v(Phi_e)
p_e, q_e = d_u(r_e), d_v(r_e)
c_e, d_e = d_u(om_e), d_v(om_e)

RESIDUALS = {
    "SC": sp.simplify(d_v(s_e) + (p_e * t_e + q_e * s_e) / r_e),
    "UV": sp.simplify(d_v(p_e) + a2_e * m_e / (2 * r_e**2)),
    "C2": sp.simplify(d_v(q_e) - 2 * d_e * q_e + sp.Rational(1, 2) * KAPPA_S * r_e * t_e**2),
    "TH": sp.simplify(d_v(c_e) - a2_e * m_e / (2 * r_e**3) + sp.Rational(1, 2) * KAPPA_S * s_e * t_e),
    "C1": sp.simplify(d_u(p_e) - 2 * c_e * p_e + sp.Rational(1, 2) * KAPPA_S * r_e * s_e**2),
    "Mdef": sp.simplify(m_e - (r_e / 2) * (1 + 4 * p_e * q_e / a2_e)),
}


def series_coeffs(expr, order):
    ex = sp.together(sp.expand(expr))
    ser = sp.series(ex, xi, 0, order + 1).removeO()
    ser = sp.expand(ser)
    return [sp.simplify(ser.coeff(xi, k)) for k in range(order + 1)]


def log(msg):
    print(msg, flush=True)


# ==============================================================================
# 1. НИЖНИЕ УРОВНИ O1-O5 (те же формы, что в sympy_center.main — перепроверка)
# ==============================================================================
def lower_levels(coeffs):
    t0sym = P0.diff(y) / 2
    d0sym = W0.diff(y) / 2
    lv = {}
    lv["O1"] = sp.simplify(sp.solve(sp.Eq(coeffs["SC"][0], 0),
                                    P0.diff(y, 2))[0])          # P0''
    lv["O2"] = sp.simplify(sp.solve(sp.Eq(coeffs["C2"][0], 0),
                                    R1.diff(y))[0])             # R1'
    lv["O3"] = sp.simplify(sp.solve(sp.Eq(coeffs["TH"][0], 0),
                                    W0.diff(y, 2))[0])          # W0''
    lv["O4"] = sp.simplify(sp.solve(sp.Eq(coeffs["Mdef"][3], 0), M3)[0])
    lv["O5"] = sp.simplify(sp.solve(sp.Eq(coeffs["SC"][2], 0),
                                    P2.diff(y, 2))[0])          # P2''
    # контроль форм (уроки sympy_center: +W2 в O3, коэффициент 2 в O5)
    ok = {}
    ok["O1_form"] = sp.simplify(lv["O1"] / 2
                                - (3 * P2 - 2 * R1.diff(y) / R1 * t0sym))
    ok["O2_form"] = sp.simplify(lv["O2"] - 2 * d0sym * R1)
    ok["O3_form_gauge"] = sp.simplify(
        lv["O3"].subs(sp.exp(2 * W0), R1**2) / 2
        - (M3 / R1 + W2 - KAPPA_S * t0sym**2))
    ok["O5_form"] = sp.simplify(
        lv["O5"] - (20 * P4 + 8 * R3 * P2 / R1
                    - 2 * R1.diff(y) / R1 * P2.diff(y)
                    - 2 * R3.diff(y) / R1 * P0.diff(y)
                    + 2 * R3 * R1.diff(y) / R1**2 * P0.diff(y)))
    return lv, ok


# ==============================================================================
# 2. ПОИСК СЛЕДУЮЩИХ УРОВНЕЙ (динамика источников)
# ==============================================================================
TARGETS = {
    "W2'": sp.diff(W2, y),
    "P4'": sp.diff(P4, y),
    "P4''": sp.diff(P4, y, 2),
    "R3'": sp.diff(R3, y),
    "R5": R5,
    "M5": M5,
}


def find_next_levels(coeffs, lv):
    """Сканируем неиспользованные коэффициенты: подставляем нижние уровни,
    решаем относительно целей. Возвращаем {(name, order): (target, form)}."""
    subs_lower = {
        P0.diff(y, 2): lv["O1"],
        R1.diff(y): lv["O2"],
        W0.diff(y, 2): lv["O3"],
        P2.diff(y, 2): lv["O5"],
        M3: lv["O4"],
    }
    used = {("SC", 0), ("C2", 0), ("TH", 0), ("Mdef", 3), ("SC", 2)}
    found = {}
    dep = []
    order_need = {"SC": 5, "UV": 3, "C2": 3, "TH": 3, "C1": 3, "Mdef": 6}
    for nm, need in order_need.items():
        for k in range(need + 1):
            if (nm, k) in used:
                continue
            try:
                co = sp.simplify(sp.expand(
                    coeffs[nm][k].subs(subs_lower)))
            except Exception:  # noqa: BLE001
                co = coeffs[nm][k]
            co = sp.simplify(co)
            if co == 0:
                dep.append((nm, k))
                continue
            hit = None
            for tname, tgt in TARGETS.items():
                if not co.has(tgt):
                    continue
                try:
                    sol = sp.solve(sp.Eq(co, 0), tgt)
                except Exception:  # noqa: BLE001
                    continue
                if sol:
                    form = sp.simplify(sol[0])
                    # форма обязана содержать другие функции (не тривиальная)
                    syms = form.free_symbols & {R1, R3, R5, P0, P2, P4,
                                                W0, W2, M3, M5}
                    derivs = [s for s in form.atoms(sp.Derivative)]
                    if syms or derivs:
                        hit = (tname, form)
                        break
            if hit:
                found[(nm, k)] = hit
                log(f"    уровень {nm}[xi^{k}] -> {hit[0]}")
            else:
                log(f"    {nm}[xi^{k}]: ненулевой, цели не решается "
                    f"(сохранён как consistency)")
    return found, dep


def verify_levels(coeffs, found, lv):
    """Верификация: подстановка формы обратно в коэффициент даёт 0."""
    subs_lower = {
        P0.diff(y, 2): lv["O1"],
        R1.diff(y): lv["O2"],
        W0.diff(y, 2): lv["O3"],
        P2.diff(y, 2): lv["O5"],
        M3: lv["O4"],
    }
    ver = {}
    for (nm, k), (tname, form) in found.items():
        tgt = TARGETS[tname]
        co = sp.simplify(sp.expand(coeffs[nm][k].subs(subs_lower)))
        res = sp.simplify(co.subs(tgt, form))
        ver[f"{nm}_xi{k}_{tname}"] = sp.sstr(res)
        log(f"    verify {nm}[xi^{k}] -> {tname}: residual = {res}")
    return ver


# ==============================================================================
# 3. z-РЕДУКЦИЯ (размороженные источники)
# ==============================================================================
S = sp.Symbol("s_collapse", positive=True)
T0, P2h, Q, D0, R1h, W2h, R3h, P4h, R5h, M3h, M5h = sp.symbols(
    "T0h P2h Qh D0h R1h W2h R3h P4h R5h M3h M5h")
dT0, dD0, ddQ, dR1, dW2, dR3, dP4 = sp.symbols(
    "dT0h dD0h ddQh dR1h dW2h dR3h dP4h")

# таблица: f = fhat s^{-p}; f' = (dfhat + p fhat) s^{-(p+1)}  (ds/dy = -1)
TBL_D = {
    sp.diff(P0, y, 2): 2 * (dT0 + T0) / S**2,
    sp.diff(P0, y): 2 * T0 / S,
    sp.diff(R1, y): dR1 / S,
    sp.diff(P2, y, 2): (ddQ + 5 * Q + 6 * P2h) / S**4,
    sp.diff(P2, y): (Q + 2 * P2h) / S**3,
    sp.diff(P4, y): (dP4 + 4 * P4h) / S**5,
    sp.diff(R3, y): (dR3 + 2 * R3h) / S**3,
    sp.diff(W0, y, 2): 2 * (dD0 + D0) / S**2,
    sp.diff(W0, y): 2 * D0 / S,
    sp.diff(W2, y): (dW2 + 2 * W2h) / S**3,
}
TBL_F = {
    R1: R1h, R3: R3h / S**2, R5: R5h / S**4,
    P2: P2h / S**2, P4: P4h / S**4,
    W2: W2h / S**2, M3: M3h / S**2, M5: M5h / S**4,
    sp.exp(2 * W0): R1h**2, sp.exp(-2 * W0): 1 / R1h**2,
}


def to_z(expr):
    for k_, v_ in TBL_D.items():
        expr = expr.subs(k_, v_)
    for k_, v_ in TBL_F.items():
        expr = expr.subs(k_, v_)
    return sp.expand(expr)


def purify(ze):
    for k in range(0, 9):
        cand = sp.simplify(sp.expand(ze * S**k))
        if not cand.has(S):
            return k, cand
    return None, ze


def z_tower(coeffs, found_verified):
    """z-формы из НЕЯВНЫХ коэффициентов (содержат старшие производные)."""
    out = {}
    impl = {
        "F1_dT0": (coeffs["SC"][0], dT0),
        "F4_dD0": (coeffs["TH"][0], dD0),
        "F3_ddQ": (coeffs["SC"][2], ddQ),
        "O4_M3_link": (coeffs["Mdef"][3], M3h),
    }
    for key, (co, tgt) in impl.items():
        k, ze = purify(to_z(co))
        out[key] = sp.solve(sp.Eq(ze, 0), tgt)[0]
        out[key + "_purity"] = k
    out["F5_dR1"] = "2 D0h R1h"
    dsym = {"W2'": dW2, "R3'": dR3, "P4'": dP4}
    for (nm, kord), (tname, form) in found_verified.items():
        if tname not in dsym:
            continue
        k, ze = purify(to_z(coeffs[nm][kord]))
        key = f"N_{tname.strip(chr(39))}_{nm}{kord}"
        try:
            out[key] = sp.solve(sp.Eq(ze, 0), dsym[tname])[0]
            out[key + "_purity"] = k
        except Exception:  # noqa: BLE001
            out[key] = "solve_failed"
    return out


# ==============================================================================
# 4. CSS-НЕПОДВИЖНАЯ ТОЧКА: СВЯЗЫВАЕТ ЛИ ОНА tau?
# ==============================================================================
def fixed_point(zsys):
    """F=0 на неподвижной точке: все z-производные = 0."""
    zero = {dT0: 0, dD0: 0, ddQ: 0, dR1: 0, dW2: 0, dR3: 0, dP4: 0, Q: 0}
    eqs = {}
    for k_, v_ in zsys.items():
        if k_.endswith("_purity") or k_ in ("F5_dR1", "O4_M3_link"):
            continue
        eqs[k_] = sp.simplify(sp.expand(v_.subs(zero)))
    # подстановка M3-связки и алгебраических связок R5/M5
    subs_link = {}
    if "O4_M3_link" in zsys:
        subs_link[M3h] = zsys["O4_M3_link"]
    for k_ in list(eqs):
        if k_.startswith("N_R5") or k_.startswith("N_M5"):
            continue
    for k_ in list(eqs):
        eqs[k_] = sp.simplify(sp.expand(eqs[k_].subs(subs_link)))
    return eqs


def main():
    t_wall = time.time()
    out = {
        "config": {"kappa": int(KAPPA_S), "ansatz_extended": {
            "r": "R1 xi + R3 xi^3 + R5 xi^5", "Phi": "P0+P2 xi^2+P4 xi^4",
            "omega": "W0 + W2 xi^2", "m": "M3 xi^3 + M5 xi^5",
            "chi": 0}},
        "levels": {}, "verify": {}, "z_system": {}, "fixed_point": {},
        "honest_notes": [],
    }
    log("[1/5] Остатки расширенного анзаца, series по xi...")
    ORDERS = {"SC": 5, "UV": 3, "C2": 3, "TH": 3, "C1": 3, "Mdef": 6}
    coeffs = {}
    for nm, res in RESIDUALS.items():
        coeffs[nm] = series_coeffs(res, ORDERS[nm])
        nz = [k for k, c in enumerate(coeffs[nm]) if c != 0]
        log(f"    {nm}: ненулевые xi-порядки {nz}")

    log("[2/5] Нижние уровни O1-O5 (перепроверка форм)...")
    lv, ok = lower_levels(coeffs)
    for k_, v_ in ok.items():
        log(f"    {k_}: {sp.sstr(v_)}")
        out["verify"][k_] = sp.sstr(v_)

    log("[3/5] Поиск уровней O6+ (динамика источников)...")
    found, dep = find_next_levels(coeffs, lv)
    out["levels"]["found"] = {f"{nm}_xi{k}": {"target": t, "form": sp.sstr(f)}
                              for (nm, k), (t, f) in found.items()}
    out["levels"]["dependent_zero_after_lower"] = [f"{nm}_xi{k}"
                                                   for (nm, k) in dep]
    ver = verify_levels(coeffs, found, lv)
    out["verify"].update(ver)

    log("[4/5] z-редукция (размороженные W2h, R3h, P4h)...")
    # только уровни с нулевой верификацией
    found_ver = {}
    for (nm, kord), (tname, form) in found.items():
        vkey = f"{nm}_xi{kord}_{tname}"
        if str(ver.get(vkey, "x")) == "0":
            found_ver[(nm, kord)] = (tname, form)
    zsys = z_tower(coeffs, found_ver)
    out["z_system"] = {k_: (sp.sstr(v_) if not k_.endswith("_purity")
                            else v_) for k_, v_ in zsys.items()}

    log("[5/5] CSS-неподвижная точка расширенной башни...")
    try:
        eqs = fixed_point(zsys)
        # неизвестные точки: T0*, P2h*, D0*, R1h*, W2h*, R3h*, P4h*, R5h*, M5h*
        unk = [T0, P2h, D0, R1h, W2h, R3h, P4h, R5h, M5h]
        eq_list = []
        names = []
        for k_, e in eqs.items():
            e2 = sp.simplify(e)
            if e2 == 0:
                continue
            eq_list.append(e2)
            names.append(k_)
        log(f"    нетривиальных уравнений на точку: {len(eq_list)} {names}")
        sols = sp.solve(eq_list, unk, dict=True)
        out["fixed_point"]["n_equations"] = len(eq_list)
        out["fixed_point"]["names"] = names
        out["fixed_point"]["solutions"] = [
            {sp.sstr(k_): sp.sstr(v_) for k_, v_ in s.items()} for s in sols]
        tau_pinned = False
        for s in sols:
            if T0 in s and sp.simplify(s[T0]).free_symbols <= set():
                tau_pinned = True
        out["fixed_point"]["tau_pinned"] = bool(tau_pinned)
        log(f"    решений: {len(sols)}; tau связан: {tau_pinned}")
        if not sols:
            # линеаризационный анализ невозможен без точки — сохранить
            out["honest_notes"].append(
                "sp.solve не замкнул точку в замкнутой форме — требуется "
                "численный анализ системы (следующий шаг)")
    except Exception:  # noqa: BLE001
        out["fixed_point"]["error"] = traceback.format_exc()
        log("    fixed_point: ошибка (сохранена)")

    out["runtime_s"] = round(time.time() - t_wall, 1)
    with open(os.path.join(RESULTS, "center_o6.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    log(f"Сохранено: results/center_o6.json ({out['runtime_s']} c)")


if __name__ == "__main__":
    main()
