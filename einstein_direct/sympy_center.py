#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
МАШИННЫЙ ВЫВОД ЦЕНТРАЛЬНОЙ (СПИНОРНОЙ) ИЕРАРХИИ — ТЕЙЛОР-ПАТЧ v5
MACHINE DERIVATION OF THE CENTRAL (SPINOR) HIERARCHY — TAYLOR PATCH v5
================================================================================

Фундаментальный уровень для стабильных мод (указание автора монографии):
регулярный центр разлагается на чётную (скалярную, E) и нечётную (спинорную,
O) части; уравнения Эйнштейна на каждом порядке по радиусу дают ОДУ и связи
между коэффициентами разложения — "выводы фундаментальных уровней". Часть
решений обязана взрываться (распады/сборки — частные случаи); стабильные моды
описываются выведенной здесь иерархией.

Координаты: x = (v-u)/2 (радиальное направление у центра), y = (u+v)/2
(время на мировой линии центра). Центр r = 0 — кривая x = xs(y); дрейф
центра по сетке: chi := dxs/dy. Радиальная переменная xi = x - xs(y).

Разложение (по чётности относительно зеркала (u,v)->(v,u), т.е. xi -> -xi):
    r    = R1(y) xi + R3(y) xi^3
    Phi  = P0(y) + P2(y) xi^2 + P4(y) xi^4          (чётное — скалярный сектор)
    omega= W0(y) + W2(y) xi^2                        (чётное)
    m    = M3(y) xi^3                                (нечётное, m ~ r^3)

Правила дифференцирования (цепное правило с дрейфом):
    d/du = (1/2) d/dy - ((1+chi)/2) d/dxi
    d/dv = (1/2) d/dy + ((1-chi)/2) d/dxi

Система (машинный вывод session 1, solver.py):
    (SC) s_v + (p t + q s)/r = 0
    (UV) p_v + alpha^2 m / (2 r^2) = 0
    (C2) q_v - 2 d q + (kappa/2) r t^2 = 0
    (TH) c_v - alpha^2 m / (2 r^3) + (kappa/2) s t = 0
    (C1) p_u - 2 c p + (kappa/2) r s^2 = 0
    (Mdef) m - (r/2)(1 + 4 p q / alpha^2) = 0

ВЫВОД: каждый остаток раскладывается по xi; коэффициенты xi^0..xi^3 дают
иерархию. Результат (chi = 0):
    (O1) t0' = 3 P2 - 2 (R1'/R1) t0,   t0 := P0'/2 = s(0) = t(0)
    (O2) R1' = 2 d0 R1,                d0 := W0'/2 = c(0) = d(0)
    (O3) d0' = M3/R1 + W2 - kappa t0^2   [+W2 — найдено машиной, не ручным выводом]
    (O4) M3 = (R1'^2 - 6 R1 R3)/(2 R1) + R1 W2   [из Mdef, калибровка R1^2=A0]
    (O5) P2'' = 20 P4 + 8 R3 P2/R1 - 2 (R1'/R1) P2' - 2 (R3'/R1) P0'
                + (R3 R1'/R1^2) P0'                 [связка спинор-моды с E]
плюс chi-поправки (дрейф центра) — все выведены и верифицированы SymPy.

Запуск:  python3 sympy_center.py          # ~10-20 c, results/center_hierarchy.json
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

KAPPA_S = sp.Integer(2)   # kappa = 8 pi G = 2 (точно, без float-загрязнения)

# ------------------------------------------------------------------------------
# 1. Ansatz и производные
# ------------------------------------------------------------------------------
y, xi = sp.symbols('y xi', real=True)
R1 = sp.Function('R1')(y)
R3 = sp.Function('R3')(y)
P0 = sp.Function('P0')(y)
P2 = sp.Function('P2')(y)
P4 = sp.Function('P4')(y)
W0 = sp.Function('W0')(y)
W2 = sp.Function('W2')(y)
M3 = sp.Function('M3')(y)
XS = sp.Function('xs')(y)          # x*(y) — положение центра
CHI = sp.diff(XS, y)               # chi = dx*/dy (дрейф центра)

r_e = R1 * xi + R3 * xi**3
Phi_e = P0 + P2 * xi**2 + P4 * xi**4
om_e = W0 + W2 * xi**2
m_e = M3 * xi**3
a2_e = sp.exp(2 * om_e)            # alpha^2 = exp(2 omega)


def d_u(f):
    """dF/du при фиксированном v: (1/2) f_y - ((1+chi)/2) f_xi."""
    return sp.Rational(1, 2) * sp.diff(f, y) - (1 + CHI) / 2 * sp.diff(f, xi)


def d_v(f):
    """dF/dv при фиксированном u: (1/2) f_y + ((1-chi)/2) f_xi."""
    return sp.Rational(1, 2) * sp.diff(f, y) + (1 - CHI) / 2 * sp.diff(f, xi)


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


def series_coeffs(expr, order=4):
    """Разложение по xi (chi, все функции — от y). Возвращает список
    коэффициентов [xi^0, xi^1, ...]. Остатки содержат r в знаменателе —
    обязаны проходить через sp.series (expand+coeff на рациональных
    функциях даёт неверные коэффициенты)."""
    ex = sp.together(sp.expand(expr))
    ser = sp.series(ex, xi, 0, order + 1).removeO()
    ser = sp.expand(ser)
    return [sp.simplify(ser.coeff(xi, k)) for k in range(order + 1)]


# ------------------------------------------------------------------------------
# 2. Извлечение иерархии (chi = 0 — стационарный центр)
# ------------------------------------------------------------------------------
def chi0(expr):
    return sp.simplify(expr.subs(CHI, 0))


def main():
    t0wall = time.time()
    out = {
        "config": {"kappa": int(KAPPA_S), "ansatz": {
            "r": "R1 xi + R3 xi^3", "Phi": "P0 + P2 xi^2 + P4 xi^4",
            "omega": "W0 + W2 xi^2", "m": "M3 xi^3",
            "xi": "x - xs(y)", "chi": "dxs/dy"}},
        "residual_orders": {}, "hierarchy": {}, "chi_corrections": {},
        "checks": {}, "honest_notes": [],
    }

    print("[1/4] Разложение остатков по xi (chi = 0)...")
    coeffs_chi0 = {}
    for name, res in RESIDUALS.items():
        cs = series_coeffs(chi0(res), order=4)
        coeffs_chi0[name] = cs
        nz = [k for k, c in enumerate(cs) if sp.simplify(c) != 0]
        out["residual_orders"][f"{name}_chi0_nonzero_orders"] = nz
        print(f"    {name}: ненулевые порядки xi: {nz}")

    # --- (O1): SC, порядок xi^0 -------------------------------------------
    # s_v|0 = t0'/2 - P2/2 (t0 = P0'/2); (pt+qs)/r|0 = -P2 + (R1'/R1) t0
    sc0 = sp.simplify(coeffs_chi0["SC"][0])
    t0sym = P0.diff(y) / 2
    O1_raw = sp.simplify(sp.solve(sp.Eq(sc0, 0), P0.diff(y, 2))[0])
    O1 = sp.simplify(O1_raw / 2)   # t0' = P0''/2
    out["hierarchy"]["O1_t0_prime_rhs"] = sp.sstr(O1)
    print(f"    O1: t0' = {sp.sstr(O1)}")
    # проверка формы 3 P2 - 2 (R1'/R1) t0:
    form_O1 = sp.simplify(O1 - (3 * P2 - 2 * R1.diff(y) / R1 * t0sym))
    out["checks"]["O1_form_3P2_minus_2(R1'/R1)t0"] = sp.sstr(form_O1)

    # --- (O2): C2, порядок xi^0 -------------------------------------------
    c20 = sp.simplify(coeffs_chi0["C2"][0])
    O2 = sp.simplify(sp.solve(sp.Eq(c20, 0), R1.diff(y))[0])
    out["hierarchy"]["O2_R1_prime_rhs"] = sp.sstr(O2)
    form_O2 = sp.simplify(O2 - 2 * (W0.diff(y) / 2) * R1)
    out["checks"]["O2_form_2d0R1"] = sp.sstr(form_O2)
    print(f"    O2: R1' = {sp.sstr(O2)}")

    # --- (O3): TH, порядок xi^0 -------------------------------------------
    # МАШИНА нашла член +W2 (нечётный наклон omega у центра), отсутствовавший
    # в ручном выводе: c_v(0) = d0'/2 - W2/2, а не d0'/2.
    th0 = sp.simplify(coeffs_chi0["TH"][0])
    # c_v|0 = d0'/2 - W2/2 (d0 = W0'/2); alpha^2 m/(2 r^3)|0 = A0 M3/(2 R1^3)
    O3_raw = sp.simplify(sp.solve(sp.Eq(th0, 0), W0.diff(y, 2))[0])
    O3 = sp.simplify(O3_raw / 2)   # d0' = W0''/2
    out["hierarchy"]["O3_d0_prime_rhs"] = sp.sstr(O3)
    print(f"    O3: d0' = {sp.sstr(O3)}")
    # при калибровке R1^2 = A0 = e^{2W0}: d0' = M3/R1 + W2 - kappa t0^2
    subs_gauge = {sp.exp(2 * W0): R1**2}
    O3_g = sp.simplify(O3.subs(subs_gauge))
    form_O3 = sp.simplify(O3_g - (M3 / R1 + W2 - KAPPA_S * t0sym**2))
    out["checks"]["O3_form_M3_over_R1_plus_W2_minus_kappa_t0sq (gauge R1^2=A0)"] = sp.sstr(form_O3)

    # --- (O4): Mdef: xi^1 — калибровка центра (R1^2 = A0), xi^3 — M3 ------
    md1 = sp.simplify(coeffs_chi0["Mdef"][1])
    out["hierarchy"]["Mdef_xi1_gauge_condition"] = sp.sstr(md1)
    md3 = sp.simplify(coeffs_chi0["Mdef"][3])
    O4 = sp.simplify(sp.solve(sp.Eq(md3, 0), M3)[0])
    out["hierarchy"]["O4_M3_series"] = sp.sstr(O4)
    print(f"    O4: M3 = {sp.sstr(O4)}")
    # форма (R1'^2 - 6 R1 R3)/(2 R1) + R1 W2 при калибровке
    # (заменяем ОБЕ экспоненты: exp(2W0) и exp(-2W0) -> R1^+-2)
    form_O4 = sp.simplify(
        O4.subs(sp.exp(-2 * W0), R1**-2).subs(sp.exp(2 * W0), R1**2)
        - ((R1.diff(y)**2 - 6 * R1 * R3) / (2 * R1) + R1 * W2))
    out["checks"]["O4_form_(R1'^2-6R1R3)/(2R1)+R1W2"] = sp.sstr(form_O4)

    # --- (O5): SC, порядок xi^2 — связка спинорной моды --------------------
    sc2 = sp.simplify(coeffs_chi0["SC"][2])
    P2pp = sp.simplify(sp.solve(sp.Eq(sc2, 0), P2.diff(y, 2))[0])
    out["hierarchy"]["O5_P2_prime_prime_rhs"] = sp.sstr(P2pp)
    print(f"    O5: P2'' = {sp.sstr(P2pp)}")
    form_O5 = sp.simplify(P2pp - (20 * P4 + 8 * R3 * P2 / R1
                                  - 2 * R1.diff(y) / R1 * P2.diff(y)
                                  - 2 * R3.diff(y) / R1 * P0.diff(y)
                                  + 2 * R3 * R1.diff(y) / R1**2 * P0.diff(y)))
    out["checks"]["O5_form_20P4+8R3P2/R1-..."] = sp.sstr(form_O5)

    # --- UV xi^0, xi^1: p_v(0) = 0 и связь R1'' с R3, M3 -------------------
    uv0 = sp.simplify(coeffs_chi0["UV"][0])
    uv1 = sp.simplify(coeffs_chi0["UV"][1])
    out["hierarchy"]["UV_xi0"] = sp.sstr(uv0)
    out["hierarchy"]["UV_xi1_R1pp_link"] = sp.sstr(uv1)
    print(f"    UV xi0: {sp.sstr(uv0)}")
    print(f"    UV xi1: {sp.sstr(uv1)}")

    # --- C1 xi^0, xi^1: согласование c(0), R1' -----------------------------
    c10 = sp.simplify(coeffs_chi0["C1"][0])
    c11 = sp.simplify(coeffs_chi0["C1"][1])
    out["hierarchy"]["C1_xi0"] = sp.sstr(c10)
    out["hierarchy"]["C1_xi1"] = sp.sstr(c11)
    print(f"    C1 xi0: {sp.sstr(c10)}")
    print(f"    C1 xi1: {sp.sstr(c11)}")

    # --- C2 xi^1 ------------------------------------------------------------
    c21 = sp.simplify(coeffs_chi0["C2"][1])
    out["hierarchy"]["C2_xi1"] = sp.sstr(c21)

    # ------------------------------------------------------------------------------
    # 3. chi-поправки (дрейф центра) — ключевые ODE с chi != 0
    # ------------------------------------------------------------------------------
    print("[2/4] chi-поправки (дрейф центра)...")
    for name in ("SC", "C2", "TH"):
        cs = series_coeffs(RESIDUALS[name], order=2)
        out["chi_corrections"][f"{name}_xi0"] = sp.sstr(sp.simplify(cs[0]))
        out["chi_corrections"][f"{name}_xi1"] = sp.sstr(sp.simplify(cs[1]))

    sc0c = sp.simplify(series_coeffs(RESIDUALS["SC"], order=2)[0])
    O1c = sp.simplify(sp.solve(sp.Eq(sc0c, 0), P0.diff(y, 2))[0] / 2)
    out["chi_corrections"]["O1_t0_prime_with_chi"] = sp.sstr(O1c)
    print(f"    O1(chi): t0' = {sp.sstr(O1c)}")

    c20c = sp.simplify(series_coeffs(RESIDUALS["C2"], order=2)[0])
    O2c = sp.simplify(sp.solve(sp.Eq(c20c, 0), R1.diff(y))[0])
    out["chi_corrections"]["O2_R1_prime_with_chi"] = sp.sstr(O2c)
    print(f"    O2(chi): R1' = {sp.sstr(O2c)}")

    # p(0), q(0) с chi: калибровка центра (Mdef xi^0)
    p0c = sp.simplify(p_e.subs(xi, 0))
    q0c = sp.simplify(q_e.subs(xi, 0))
    out["chi_corrections"]["p_center"] = sp.sstr(p0c)
    out["chi_corrections"]["q_center"] = sp.sstr(q0c)
    print(f"    p(0) = {sp.sstr(p0c)},  q(0) = {sp.sstr(q0c)}")

    # s, t с chi: нечётные наклоны
    s1c = sp.simplify(sp.expand(s_e).coeff(xi, 1))
    t1c = sp.simplify(sp.expand(t_e).coeff(xi, 1))
    out["chi_corrections"]["s_xi1"] = sp.sstr(s1c)
    out["chi_corrections"]["t_xi1"] = sp.sstr(t1c)

    # ------------------------------------------------------------------------------
    # 4. Проверки: плоское пространство и согласованность иерархии
    # ------------------------------------------------------------------------------
    print("[3/4] Проверки...")
    # Плоское пространство (БЕЗ поля): P0' = 0, P2 = 0, R1 = 1, R3 = 0,
    # W0 = const, W2 = 0, M3 = 0, chi = 0: все остатки = 0?
    flat_subs = {R1: 1, R3: 0, sp.diff(R1, y): 0, sp.diff(R1, y, 2): 0,
                 W0: 0, W2: 0, sp.diff(W0, y): 0, sp.diff(W0, y, 2): 0,
                 M3: 0, CHI: 0, P4: 0, P2: 0,
                 sp.diff(P0, y): 0, sp.diff(P0, y, 2): 0, R3.diff(y): 0}
    flat_ok = {}
    for name, res in RESIDUALS.items():
        val = sp.simplify(chi0(res).subs(flat_subs))
        flat_ok[name] = str(val)
    out["checks"]["flat_space_residuals"] = flat_ok
    print(f"    плоское пространство: {flat_ok}")

    # Неплоская согласованная волна у центра: плоская симметричная волна
    # Phi = P0(y), P0'' = 6 P2, R1 = 1, M3 = 0, W = 0: SC xi^0 выполнено?
    wave = sp.simplify(chi0(coeffs_chi0["SC"][0]).subs(
        {R1: 1, R3: 0, sp.diff(R1, y): 0, W0: 0, sp.diff(W0, y): 0,
         W2: 0, M3: 0, CHI: 0, P4: 0}))
    wave_ok = sp.simplify(wave.subs(P0.diff(y, 2), 6 * P2))
    out["checks"]["flat_symmetric_wave_SC_xi0"] = sp.sstr(wave_ok)
    print(f"    плоская симметричная волна (P0''=6P2): SC xi0 -> {wave_ok}")

    all_forms = {
        "O1": sp.simplify(form_O1) == 0,
        "O2": sp.simplify(form_O2) == 0,
        "O3": sp.simplify(form_O3) == 0,
        "O4": sp.simplify(form_O4) == 0,
        "O5": sp.simplify(form_O5) == 0,
        "wave": sp.simplify(wave_ok) == 0,
        "flat": all(v == "0" for v in flat_ok.values()),
        "C1_C2_consistency": sp.simplify(
            c10.subs(R1.diff(y), R1 * W0.diff(y))) == 0,
    }
    out["checks"]["hierarchy_forms_detail"] = {k: bool(v) for k, v in all_forms.items()}
    out["checks"]["hierarchy_forms_verified"] = bool(all(all_forms.values()))
    print(f"    формы O1-O5 + волна + плоское: {out['checks']['hierarchy_forms_detail']}")
    print(f"    ИТОГ верификации форм: {out['checks']['hierarchy_forms_verified']}")

    # ------------------------------------------------------------------------------
    # 5. Численная верификация на подкритическом забеге (A = 0.02, regular)
    # ------------------------------------------------------------------------------
    print("[4/4] Численная верификация измерительного конвейера (A=0.02, regular)...")
    num = numeric_center_check(A=0.02, n=800, closure="regular")
    out["numeric_subcritical"] = num
    sel = num["rows"][:3] + num["rows"][-2:]
    for row in sel:
        print(f"    v={row['v']:.3f}: R1={row['R1_fit']:.4f} (sqrt(a2)={row['sqrt_a2_center']:.4f}, "
              f"C0={row['C0_gauge_viol']:.1e}), P2={row['P2_fit']:.3e}, "
              f"t0_even={row['t0_even']:.3e}, M3rel={row.get('M3_rel_diff', float('nan')):.1e}")
    o1res = [r["O1_residual_rel"] for r in num["rows"][1:]
             if np.isfinite(r.get("O1_residual_rel", float("nan")))]
    o2res = [r["O2_residual_rel"] for r in num["rows"][1:]
             if np.isfinite(r.get("O2_residual_rel", float("nan")))]
    if o1res:
        print(f"    O1 Хойн-невязка/scale: max = {max(o1res):.3e}, median = {np.median(o1res):.3e}")
        print(f"    O2 Хойн-невязка/scale: max = {max(o2res):.3e}, median = {np.median(o2res):.3e}")

    out["runtime_s"] = round(time.time() - t0wall, 1)
    path = os.path.join(RESULTS, "center_hierarchy.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    print(f"Сохранено: {path}")
    return out


# ------------------------------------------------------------------------------
# Численная верификация: измерение коэффициентов на сетке + проверка O1/O2
# ------------------------------------------------------------------------------
def numeric_center_check(A=0.02, n=800, probe_vs=None, closure="regular"):
    """Измеряет R1, x*, P2, t0, d0, M3, W2 на строках забега и проверяет
    одношаговые ОДУ O1 (t0' = 3P2 - 4 d0 t0) и O2 (R1' = 2 d0 R1) схемой
    Хойна (усреднение правой части по концам шага — O(dv^3) невязка)."""
    if probe_vs is None:
        probe_vs = np.arange(0.50, 0.701, 0.01)
    from solver import DoubleNullSolver, GaussianPulseData, SolverConfig
    data = GaussianPulseData(A=A, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                       monitor_every=10**9)
    sol = DoubleNullSolver(cfg, data)
    sol.center_closure = closure
    sol.reg_m_rebuild = closure == "regular"
    sol.reg_pq_project = closure == "regular"
    sol.heal_enabled = closure != "regular"
    st = {k: getattr(sol, k).copy() for k in
          ("r", "Phi", "p", "q", "s", "t", "c", "m", "alpha2", "d", "w")}
    rows = []
    prev = None
    j = 1
    probe_pending = sorted(probe_vs)
    with np.errstate(all="ignore"):
        while j < n and probe_pending:
            st = sol._do_step(st, j)
            v_now = float(sol.v[j])
            if v_now >= probe_pending[0] - 1e-12:   # первая строка >= пробной v
                pv = probe_pending.pop(0)
                rec = measure_center_row(sol, st, v_now)
                if prev is not None:
                    dv = v_now - prev["v"]
                    # Хойн: правая часть ODE усредняется по концам шага
                    f1 = 3 * prev["P2_fit"] - 4 * prev["d0_center"] * prev["t0_even"]
                    f2 = 3 * rec["P2_fit"] - 4 * rec["d0_center"] * rec["t0_even"]
                    t0p = prev["t0_even"] + 0.5 * dv * (f1 + f2)
                    g1 = 2 * prev["d0_center"] * prev["R1_fit"]
                    g2 = 2 * rec["d0_center"] * rec["R1_fit"]
                    R1p = prev["R1_fit"] + 0.5 * dv * (g1 + g2)
                    sc_t = max(abs(prev["t0_even"]), abs(rec["t0_even"]), 1e-30)
                    sc_R = max(abs(prev["R1_fit"]), abs(rec["R1_fit"]), 1e-30)
                    rec["O1_residual_rel"] = float(abs(rec["t0_even"] - t0p) / sc_t)
                    rec["O2_residual_rel"] = float(abs(rec["R1_fit"] - R1p) / sc_R)
                    rec["t0_pred"] = float(t0p)
                    rec["R1_pred"] = float(R1p)
                else:
                    rec["O1_residual_rel"] = rec["O2_residual_rel"] = float("nan")
                rows.append(rec)
                prev = rec
            j += 1
    if len(rows) < 2:
        return {"A": A, "n": n, "rows": rows,
                "error": "менее 2 пробных строк — верификация O1/O2 невозможна"}
    return {"A": A, "n": n, "rows": rows,
            "note": ("Измерения: R1,x* — линейный фит r(x) на кольце; R3 — "
                     "кубический рефит; P2 — нечётный фит (t-s)/2; t0_even — "
                     "чётный фит (t+s)/2 с свободным E0; d0 — чётный фит "
                     "(c+d)/2; M3 — фит m/xi^3. O1/O2 — одношаговые невязки.")}


def measure_center_row(sol, st, v_now, ring_lo_du=8.0, ring_hi_du=32.0):
    """Измерение центральных коэффициентов на одной строке (чистый фит)."""
    r = st["r"]; s = st["s"]; t = st["t"]; c = st["c"]; d = st["d"]; m = st["m"]
    a2 = st["alpha2"]
    du = sol.du
    u = sol.u
    n = len(r)
    x = (v_now - u) / 2.0                      # радиальная координата сетки
    i0 = int(np.argmin(np.abs(r)))
    ring = (r > ring_lo_du * du) & (r < ring_hi_du * du) & (np.arange(n) <= i0)
    out = {"v": float(v_now), "i0": i0}

    if int(ring.sum()) < 6:
        out["fit_ok"] = False
        return out

    xr = x[ring]; rr = r[ring]
    # линейный фит r = R1 (x - x*)
    Amat = np.stack([xr, np.ones_like(xr)], axis=1)
    coef, *_ = np.linalg.lstsq(Amat, rr, rcond=None)
    R1_lin, b0 = float(coef[0]), float(coef[1])
    x_star = -b0 / R1_lin
    # кубический рефит
    xi_r = xr - x_star
    A2 = np.stack([xi_r, xi_r**3], axis=1)
    coef2, *_ = np.linalg.lstsq(A2, rr, rcond=None)
    R1, R3 = float(coef2[0]), float(coef2[1])
    resid = rr - A2 @ coef2
    rel = float(np.max(np.abs(resid)) / max(np.max(np.abs(rr)), 1e-30))
    out.update({"fit_ok": True, "R1_fit": R1, "R3_fit": R3, "x_star": float(x_star),
                "r_fit_relres": rel})

    # чётная/нечётная части (t, s) на кольце — фиты по xi
    xi_all = x - x_star
    E = 0.5 * (t + s)     # чётная часть
    O = 0.5 * (t - s)     # нечётная часть
    Er = E[ring]; Or = O[ring]; xir = xi_all[ring]
    # E = E0 + E2 xi^2 + E4 xi^4 (свободный E0)
    AE = np.stack([np.ones_like(xir), xir**2, xir**4], axis=1)
    cE, *_ = np.linalg.lstsq(AE, Er, rcond=None)
    out["t0_even"] = float(cE[0]); out["E2"] = float(cE[1]); out["E4"] = float(cE[2])
    # O = P2 xi + P4o xi^3 (+C/xi паразит)
    AO = np.stack([xir, xir**3, 1.0 / xir], axis=1)
    cO, *_ = np.linalg.lstsq(AO, Or, rcond=None)
    out["P2_fit"] = float(cO[0]); out["P4o_fit"] = float(cO[1])
    out["C_par"] = float(cO[2])
    # (c+d)/2 = d0 + e2 xi^2; (d-c)/2 = W2 xi
    cd = 0.5 * (c + d); dc = 0.5 * (d - c)
    Ac = np.stack([np.ones_like(xir), xir**2], axis=1)
    cC, *_ = np.linalg.lstsq(Ac, cd[ring], rcond=None)
    out["d0_center"] = float(cC[0]); out["e2_cd"] = float(cC[1])
    AW = np.stack([xir], axis=1)
    cW, *_ = np.linalg.lstsq(AW, dc[ring], rcond=None)
    out["W2_fit"] = float(cW[0])
    # M3: m/xi^3 = M3 + M5 xi^2
    mr = m[ring]
    okm = np.abs(xir) > 0
    AM = np.stack([np.ones_like(xir[okm]), xir[okm]**2], axis=1)
    cM, *_ = np.linalg.lstsq(AM, (mr / xir**3)[okm], rcond=None)
    out["M3_fit"] = float(cM[0])
    # калибровка C0: |R1^2 - alpha2(центр)|/alpha2 (парное среднее СОСЕДЕЙ)
    a2_c = float(0.5 * (a2[i0 - 1] + a2[i0 + 1])) if i0 >= 1 and i0 < n - 1 else float(a2[i0])
    out["sqrt_a2_center"] = float(np.sqrt(max(a2_c, 1e-300)))
    out["C0_gauge_viol"] = float(abs(R1**2 - a2_c) / max(a2_c, 1e-300))
    # M3_series (chi=0): (R1'^2 - 6 R1 R3)/(2 R1) + R1 W2, R1' = 2 d0 R1
    R1p = 2 * out["d0_center"] * R1
    out["M3_series"] = float((R1p**2 - 6 * R1 * R3) / (2 * R1) + R1 * out["W2_fit"])
    out["M3_rel_diff"] = float(abs(out["M3_fit"] - out["M3_series"]) /
                               max(abs(out["M3_fit"]), 1e-300))
    return out


if __name__ == "__main__":
    main()
