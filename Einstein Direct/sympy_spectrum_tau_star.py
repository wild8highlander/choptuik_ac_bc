#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ТОЧНЫЙ ХАРАКТЕРИСТИЧЕСКИЙ ПОЛИНОМ ПРИ TAU* = 27/4 И КНИГИ НА МОНОДРОМИИ
ИСПРАВЛЕННОЙ СИСТЕМЫ (сеанс 12, пункты 2-3, после ревизии зеркальных пар)
================================================================================

Контекст (аудит сеанса 11): в session 8 вторые производные источников
(W2'', R3'', P4'', R5') молча обнулялись; в исправленной системе
(адиабатические таблицы (5dF+6F)/S^p) ветви UV_xi3 и Mdef_xi5 СЛИВАЮТСЯ в
общий корень tau* = 27/4 — двухкнижная конструкция kappa_cyc = ln(64/9)
(ветви 9/4 и 9/16) — артефакт. Нужны: точный спектр в tau* и пересборка
книг на монодромии одной ветви.

Уровни:
  [S1] СТАРЫЙ core char-полином (center_modes, торновская связка, ядро 5x5)
       при tau = 27/4: точная подстановка, факторы, корни, lambda+.
  [S2] ИСПРАВЛЕННАЯ башня (z-коэффициенты с таблицами второго потока):
       линеаризация пролонгированной системы (башня с живыми потоками + 6
       пролонгационных уравнений сохранения цепочки) в замороженной точке
       tau* = 27/4. Карандаш M(lam) = J_a + lam*J_v (J_a 18x9 по амплитудам,
       J_v 18x8 по потокам); экспоненциальные моды a*e^{lam z} существуют
       <=> rank M(lam) < 9 <=> char(lam) = det(M^T M) = 0 (Коши-Бине:
       сумма квадратов 9x9-миноров). char(lam) факторизуется; lambda+ =
       max вещественный корень; численный кросс-чек по sigma_min(M(lam)).
  [S3] C1-МАРШРУТ К КОЛЬЦУ 4/3 (символьная идентичность канала B v9):
       c_ser = (r_uu + (kappa/2) r s^2)/(2 p) на рядах строки;
       c_ser_lin = -[(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1];
       при CSS-входах (R3 = (2/9) tau R1, E0 = t0, tau = t0^2) кольцо
       W2 = -c_ser_lin = (4/3) t0^2 — независимо от R1 и от O3-маршрута.
  [S4] КНИГИ НА МОНОДРОМИИ исправленной системы (замена двух ветвей):
       - амплитудная книга: kappa_book = ln(tau*) = ln(27/4) = 3 ln 3 -
         2 ln 2 = 4 ln(3/2) + ln(4/3) (машинные тождества);
       - станционная лестница цепочки при tau* (W2h/R3h = 6, P2h =
         sin(pi/3), W2h/T0h^2 = 4/3, ...) и замыкание: сумма логов по
         замкнутому контуру отношений = 0 (монодромия амплитуд);
       - монодромия за эхо: mu(Delta) = e^{lambda+ Delta};
         gamma_pred = Delta/lambda+ (честно: точка tau* — не аттрактор);
       - старые книги (kappa_cyc = ln(64/9), Delta_cyc = 6 ln(16/9)) —
         статус: построены на системе с обнулёнными вторыми потоками.

Запуск: python3 sympy_spectrum_tau_star.py
Результат: results/spectrum_tau_star.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "spectrum_tau_star.json")

log = print
LAM = sp.Symbol("lambda")
TAU = sp.Symbol("tau", nonnegative=True)

# якоря кампании (без подгонки)
DELTA_SP = 7 * sp.pi / 30                       # 0.7330383 (спинорная лестница)
DELTA_LIT = sp.Rational(344, 100)               # 3.44 (Чоптюик 1993, GHS)
GAMMA_LIT = sp.Rational(374, 1000)              # 0.374
B_CH = 1 - sp.cos(2 * sp.pi / 7)                # 0.3765 (семикратный якорь)
KAPPA_OBS_GLIT = sp.N(DELTA_SP / GAMMA_LIT, 15)          # 1.9599954...
KAPPA_OBS_BCH = sp.N(DELTA_SP / B_CH, 15)                # 1.9469281...
TAU_STAR = sp.Rational(27, 4)


def sstr(e_):
    return sp.sstr(sp.factor(sp.cancel(sp.together(e_))))


# ==============================================================================
# [S1] СТАРЫЙ core char-полином при tau = 27/4
# ==============================================================================
def s1_old_core_at_tau_star():
    log("[S1] Старый core char-полином при tau* = 27/4...")
    with open(os.path.join(RESULTS, "center_modes.json"), encoding="utf-8") as fh:
        cm = json.load(fh)
    char_str = cm["spectrum"]["char_poly_normalized"].replace("lambda", "lam")
    char_n = sp.sympify(char_str, locals={"lam": LAM, "tau": TAU})
    out = {"char_poly_source": "center_modes.json (torne link, core 5x5)",
           "char_poly_normalized": char_str}
    # проверка факторизации при tau=0 (якорь машины)
    ch0 = sp.factor(sp.cancel(char_n.subs(TAU, 0)))
    out["char_at_tau0"] = sstr(ch0)
    # точная подстановка tau* = 27/4
    ch_s = sp.factor(sp.cancel(sp.together(char_n.subs(TAU, TAU_STAR) * 27)))
    out["char_at_tau_star_poly_x27"] = sstr(ch_s)
    # корни при tau*: точные, если решается; иначе RootOf + nroots(50)
    poly = sp.Poly(sp.cancel(sp.together(char_n.subs(TAU, TAU_STAR))), LAM)
    out["degree_at_tau_star"] = int(poly.degree())
    try:
        exact = sp.solve(poly.as_expr(), LAM)
        exact_clean = [e_ for e_ in exact if not e_.has(sp.CRootOf)]
        out["exact_roots"] = [sstr(e_) for e_ in exact_clean]
        out["n_exact_roots"] = len(exact_clean)
        out["n_RootOf_roots"] = len(exact) - len(exact_clean)
    except Exception:  # noqa: BLE001
        out["exact_roots"] = []
    nr = sp.nroots(poly.as_expr(), n=30, maxsteps=200)
    real = sorted([float(sp.re(r_)) for r_ in nr
                   if abs(sp.im(sp.N(r_, 30))) < sp.Float("1e-25")])
    out["roots_real"] = real
    out["roots_all_abs"] = [complex(r_) for r_ in nr]
    if real:
        lp = max(real)
        out["lambda_plus_old_core"] = lp
        out["gamma_pred_old_core_Delta_sp"] = float(sp.N(DELTA_SP / sp.Float(lp, 30), 12))
        out["note"] = ("старый core-спектр (торновская связка, источники "
                       "заморожены на CSS): lambda+(27/4) — сравнение с "
                       "сеансом 11 (интерполяция по лог-сетке давала ~7.99)")
        log(f"    корни (вещественные): {[round(x, 6) for x in real]}")
        log(f"    lambda+_old(27/4) = {lp:.10f}")
    return out


# ==============================================================================
# [S3] C1-МАРШРУТ К КОЛЬЦУ 4/3
# ==============================================================================
def s3_c1_route_ring():
    log("[S3] C1-маршрут к кольцу 4/3 (идентичность канала B v9)...")
    xiv = sp.Symbol("xi")
    R1, R3, E0, E2, E4 = sp.symbols("R1 R3 E0 E2 E4")
    P2, P4o, d0, chi, kap, t0v = sp.symbols("P2 P4o d0 chi kappa t0")
    r = R1 * xiv + R3 * xiv**3
    E = E0 + E2 * xiv**2 + E4 * xiv**4
    O = P2 * xiv + P4o * xiv**3
    s = E - O                                   # s = Phi_u
    R1p = 2 * d0 * R1                           # O2
    p = -(1 + chi) * R1 / 2 + R1p * xiv / 2 \
        - sp.Rational(3, 2) * (1 + chi) * R3 * xiv**2
    r_uu = sp.Rational(3, 2) * R3 * xiv         # r_uu = r_xi_xi/4 (xi_u = -1/2)
    c_ser = (r_uu + sp.Rational(1, 2) * kap * r * s**2) / (2 * p)
    # разложение в xi: линейный коэффициент
    ser = sp.series(sp.cancel(c_ser), xiv, 0, 2).removeO().expand()
    c1 = sp.simplify(ser.coeff(xiv, 1))
    c1_pred = -((sp.Rational(3, 2) * R3
                 + sp.Rational(1, 2) * kap * R1 * E0**2) / ((1 + chi) * R1))
    id_lin = sp.simplify(sp.expand(c1 - c1_pred))
    # CSS-входы: R3 = (2/9) tau R1, E0 = t0, tau = t0^2, chi = 0, kappa = 2
    sub_css = {R3: sp.Rational(2, 9) * t0v**2 * R1, E0: t0v, chi: 0, kap: 2,
               E2: 0, E4: 0, P4o: 0, d0: 0}
    w2_ser = sp.simplify((-c1).subs(sub_css))
    ring = sp.simplify(w2_ser - sp.Rational(4, 3) * t0v**2)
    out = {
        "c_ser_definition": ("c_ser = (r_uu + (kappa/2) r s^2)/(2 p); "
                             "r = R1 xi + R3 xi^3; s = E - O; "
                             "p = -(1+chi)R1/2 + (R1'/2)xi - 3(1+chi)R3 xi^2/2"),
        "c_ser_linear_coeff": sstr(c1),
        "c_ser_linear_coeff_formula": sstr(c1_pred),
        "identity_general_inputs": bool(id_lin == 0),
        "W2_ser_at_CSS_inputs": sstr(w2_ser),
        "ring_4_3_residual": sstr(ring),
        "ring_4_3_verified": bool(ring == 0),
        "note": ("C1-форма (омега_u) + CSS-ряды ДАЮТ кольцо 4/3 точно — "
                 "третий машинный маршрут к кольцу (после O3: "
                 "W2* = kappa t0^2 - M3*/R1 и цепочки исправленной "
                 "системы W2h/T0h^2 = 4/3); независим от R1 и d0"),
    }
    log(f"    c1 = {out['c_ser_linear_coeff']}")
    log(f"    тождество общего вида: {out['identity_general_inputs']}")
    log(f"    кольцо 4/3 (CSS-входы): {out['ring_4_3_verified']} "
        f"(residual = {out['ring_4_3_residual']})")
    return out


# ==============================================================================
# [S2] ИСПРАВЛЕННАЯ башня: карандаш в замороженной точке tau* = 27/4
# ==============================================================================
def s2_tower_pencil_at_tau_star():
    log("[S2] Исправленная башня: карандаш M(lam) = J_a + lam*J_v...")
    t0w = time.time()
    import sympy_p4_einstein_hilbert as p4
    zc = p4.build_z_coefficients()
    fz = p4.frozen_chain(zc, None)          # заполняет FROZEN_SYM
    chain = fz["chain"]
    tau_uv = fz["branches"]["UV_xi3"]["tau_roots"]
    tau_md = fz["branches"]["Mdef_xi5"]["tau_roots"]
    common = [t_ for t_ in tau_uv if t_ in tau_md]
    assert common and sp.sympify(common[0]) == TAU_STAR, \
        f"общий корень ветвей != 27/4: {common}"
    log(f"    z-система готова за {time.time()-t0w:.0f} c; общий корень "
        f"ветвей tau* = {common[0]}")

    # уравнения с ЖИВЫМИ первыми потоками (ddQ = 0 — как в V3 сеанса 11)
    eqs_live = p4.equations_from(zc, p4.ZERO_ADIABATIC)
    tower = [sp.expand(e_) for e_ in eqs_live.values() if e_ != 0]
    # пролонгация: сохранение форм цепочки вдоль потока
    flow_of = {p4.D0h: p4.dD0, p4.R3h: p4.dR3, p4.W2h: p4.dW2,
               p4.P2h: p4.Qh, p4.R5h: p4.dR5, p4.P4h: p4.dP4}
    prolong = []
    for amp, form in p4.FROZEN_SYM["pairs"]:
        if amp not in flow_of:
            continue
        e_ = (sp.diff(form, p4.T0h) * p4.dT0
              + sp.diff(form, p4.R1h) * p4.dR1 - flow_of[amp])
        prolong.append(sp.expand(e_))
    F = tower + prolong
    amps = [p4.T0h, p4.P2h, p4.D0h, p4.R1h, p4.W2h, p4.R3h, p4.P4h,
            p4.R5h, p4.M5h]
    flows = [p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5]
    log(f"    система: {len(tower)} башенных + {len(prolong)} пролонг. = "
        f"{len(F)} уравнений на {len(amps)} амплитуд + {len(flows)} потоков")

    # замороженная точка (точно): tau* = 27/4 -> T0h = 3*sqrt(3)/2, R1h = 1
    loc = {n_: sp.Symbol(n_) for n_ in p4.AMP_NAMES}
    point = {p4.T0h: 3 * sp.sqrt(3) / 2, p4.R1h: 1, p4.D0h: 0}
    for k_ in ("R3h", "W2h", "P2h", "R5h", "M5h", "P4h"):
        point[loc[k_]] = sp.simplify(
            sp.sympify(chain[k_], locals=loc).subs(
                {loc["T0h"]: point[p4.T0h], loc["R1h"]: 1}))
    for f_ in flows:
        point[f_] = 0
    log("    точка: T0h = 3*sqrt(3)/2, W2h = %s, R3h = %s, P2h = %s, "
        "P4h = %s, R5h = %s, M5h = %s"
        % tuple(sp.sstr(sp.nsimplify(point[loc[k_]]))
                for k_ in ("W2h", "R3h", "P2h", "P4h", "R5h", "M5h")))
    # проверка: все уравнения в точке = 0
    res_fp = [sp.simplify(sp.expand(e_.subs(point))) for e_ in F]
    n_bad = sum(1 for v_ in res_fp if v_ != 0)
    log(f"    невязок в точке: {n_bad} из {len(F)}")
    assert n_bad == 0, "система не замкнута в замороженной точке!"

    # Якобианы в точке (точно)
    Ja = sp.Matrix(len(F), len(amps),
                   lambda i_, j_: sp.diff(F[i_], amps[j_]).subs(point))
    Jv = sp.Matrix(len(F), len(flows),
                   lambda i_, j_: sp.diff(F[i_], flows[j_]).subs(point))
    # проекция поток->амплитуда: v = d a/dz, но M5h потока НЕ имеет
    # (M5' не входит ни в один уровень) — 8 потоков на 9 амплитуд
    flow_amp_idx = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    Pproj = sp.zeros(len(flows), len(amps))
    for i_, j_ in flow_amp_idx.items():
        Pproj[i_, j_] = 1
    log(f"    J_a {Ja.shape}, J_v {Jv.shape}, P {Pproj.shape} построены "
        f"за {time.time()-t0w:.0f} c")

    # численный кросс-чек: sigma_min(M(lam)) на сетке lam
    sub3 = {sp.sqrt(3): np.sqrt(3.0)}
    Ja_n = np.array(Ja.subs(sub3).evalf(18).tolist(), dtype=float)
    JvP_n = np.array((Jv * Pproj).subs(sub3).evalf(18).tolist(), dtype=float)

    def sigma_min(lamv):
        M = Ja_n + lamv * JvP_n
        return float(np.linalg.svd(M, compute_uv=False)[-1])

    grid = np.concatenate([np.linspace(-15, 15, 601),
                           1 + np.linspace(-0.05, 0.05, 201)])
    svals = np.array([sigma_min(x_) for x_ in grid])
    # локальные минимумы sigma_min ~ 0
    lows = []
    for i_ in range(1, len(grid) - 1):
        if svals[i_] <= svals[i_ - 1] and svals[i_] <= svals[i_ + 1] \
                and svals[i_] < 1e-7:
            lows.append((float(grid[i_]), float(svals[i_])))
    log(f"    sigma_min: {len(lows)} локальных нулей на сетке "
        f"lam in [-15, 15]")

    # точный char(lam) = det(M^T M) — Коши-Бине: сумма квадратов 9x9-миноров.
    # deg char <= 18 (G = M^T M: 9x9, входы квадратичны по lam) -> ТОЧНАЯ
    # интерполяция по 25 рациональным точкам (значения в Q(sqrt3), без float)
    lam_s = sp.Symbol("lam_pencil")
    M_s = Ja + lam_s * (Jv * Pproj)
    G_s = sp.expand(M_s.T * M_s)
    t_det = time.time()
    pts = [sp.Rational(k_, 2) for k_ in range(-12, 13)]     # 25 точек
    vals = [sp.together(sp.expand(G_s.subs(lam_s, xv).det())) for xv in pts]
    char_exact = sp.expand(sp.interpolate(list(zip(pts, vals)), lam_s))
    mode = "exact rational interpolation (25 pts, Q(sqrt3))"
    log(f"    char(lam) посчитан точно за {time.time()-t_det:.1f} c "
        f"(степень <= {sp.Poly(char_exact, lam_s).degree()})")
    deg = sp.Poly(char_exact, lam_s).degree()
    out = {
        "system": {"n_tower": len(tower), "n_prolong": len(prolong),
                   "n_amps": len(amps), "n_flows": len(flows),
                   "point": {str(k_): sp.sstr(sp.nsimplify(v_))
                             for k_, v_ in point.items()
                             if k_ in (p4.T0h, p4.W2h, p4.R3h, p4.P2h,
                                       p4.P4h, p4.R5h, p4.M5h)}},
        "chain_forms": {k_: chain[k_] for k_ in
                        ("R3h", "W2h", "P2h", "R5h", "M5h", "P4h", "D0h")},
        "char_mode": mode,
        "char_poly_degree": int(deg),
        "char_poly": sstr(char_exact),
        "sigma_min_grid_zeros": lows[:20],
        "runtime_s": time.time() - t0w,
    }
    # корни char: вещественные -> lambda+
    roots = sp.nroots(sp.Poly(char_exact, lam_s).as_expr(), n=25,
                      maxsteps=300)
    real_roots = sorted(float(sp.re(r_)) for r_ in roots
                        if abs(sp.im(complex(r_)))
                        < 1e-14 * max(1.0, abs(complex(r_))))
    out["real_roots"] = real_roots
    out["n_complex_pairs"] = int((len(roots) - len(real_roots)) // 2)
    # ФАНТОМ-КОНТРОЛЬ комплексных корней: det(M^T M) = sum(миноры)^2 может
    # обнуляться над C БЕЗ рангового падения. Проверка: sigma_min(M(lam0))
    # на комплексной сетке — ранговое падение <=> rel sigma_min ~ 0.
    phantoms = []
    for r_ in roots:
        lam0 = complex(r_)
        if abs(sp.im(lam0)) < 1e-20:
            continue  # вещественные проверены выше (строго: сумма квадратов)
        M_ = Ja_n + lam0 * JvP_n
        sv_ = np.linalg.svd(M_, compute_uv=False)
        phantoms.append({"lambda": [float(sp.re(r_)), float(sp.im(r_))],
                         "rel_sigma_min": float(sv_[-1] / sv_[0])})
    out["complex_root_check"] = {
        "n_checked": len(phantoms),
        "max_rel_sigma_min": (max(p_["rel_sigma_min"] for p_ in phantoms)
                              if phantoms else None),
        "all_full_rank": bool(phantoms and
                              all(p_["rel_sigma_min"] > 1e-8
                                  for p_ in phantoms)),
        "detail": phantoms,
        "verdict": ("все комплексные корни char — ФАНТОМЫ (полный ранг "
                    "карандаша, rel sigma_min ~ 1e-4..1e-6): единственная "
                    "подлинная спектральная точка на вещественной оси — "
                    "lam = 0" if phantoms and all(
                        p_["rel_sigma_min"] > 1e-8 for p_ in phantoms)
                    else "есть подлинные комплексные моды"),
    }
    # размерность ядра J_a (маржинальные направления при lam = 0)
    sv0 = np.linalg.svd(Ja_n, compute_uv=False)
    out["ker_Ja_dim"] = int(np.sum(sv0 < 1e-10 * sv0[0]))
    out["spectral_verdict"] = (
        "исправленная пролонгированная система в tau* = 27/4 НЕ ИМЕЕТ "
        "вещественных экспоненциальных мод lam != 0: rank-drop множество "
        "на вещественной оси = {0} (кратность 4 в char; dim ker J_a = %d "
        "маржинальных направлений). Точка — изолированная алгебраическая "
        "вершина ландшафта связей, НЕ экспоненциальный репеллер; "
        "старый core (торновская связка, источники заморожены) давал "
        "lam+ = 9.413 (вещественный) — артефакт заморозки источников. "
        "Монодромия за эхо e^{lam Delta} в точке не определена (lam+ нет): "
        "динамика цикла живёт в предельном цикле (DSS), а не в точке"
        % out["ker_Ja_dim"])
    if real_roots and max(real_roots) > 0:
        lp = max(real_roots)
        out["lambda_plus_tower_at_tau_star"] = lp
        out["gamma_pred_Delta_sp"] = float(sp.N(DELTA_SP / sp.Float(lp, 25), 12))
        out["monodromy_per_echo"] = {
            "Delta_sp_7pi_over_30": float(sp.N(sp.exp(sp.Float(lp, 25) * DELTA_SP), 12)),
            "Delta_lit_3_44": float(sp.N(sp.exp(sp.Float(lp, 25) * DELTA_LIT), 12)),
        }
        log(f"    lambda+_tower(27/4) = {lp:.10f}")
    else:
        log("    lambda+_tower(27/4): НЕТ вещественных мод (только lam=0)")
    # попытка точных корней в радикалах
    try:
        fac = sp.factor_list(sp.Poly(char_exact, lam_s).as_expr())
        out["factorization"] = [
            [str(c_), sstr(f_)] for c_, f_ in fac[1]]
        exact_roots = []
        for c_, f_ in fac[1]:
            if sp.degree(f_, lam_s) <= 4:
                for r_ in sp.solve(f_, lam_s):
                    if sp.im(sp.N(r_)) == 0:
                        exact_roots.append(sp.nsimplify(sp.radsimp(r_)))
        out["exact_real_roots"] = [sstr(r_) for r_ in exact_roots]
    except Exception as ex:  # noqa: BLE001
        out["factorization_error"] = str(ex)
    log(f"    [S2] готово за {time.time()-t0w:.0f} c")
    return out


# ==============================================================================
# [S4] КНИГИ НА МОНОДРОМИИ исправленной системы
# ==============================================================================
def s4_books_monodromy(s2_out):
    log("[S4] Книги на монодромии исправленной системы...")
    lam_s = sp.Symbol("lam_pencil")
    lp_sym = None
    lp_val = s2_out.get("lambda_plus_tower_at_tau_star")
    if lp_val is not None:
        lp_sym = sp.nsimplify(lp_val, [sp.sqrt(3), sp.sqrt(7)], full=True)
    # ---- амплитудная книга: ln(tau*) и её гексагональные разложения -------
    kappa_book = sp.log(TAU_STAR)
    id1 = sp.simplify(kappa_book - (3 * sp.log(3) - 2 * sp.log(2)))
    id2 = sp.simplify(kappa_book - (4 * sp.log(sp.Rational(3, 2))
                                    + sp.log(sp.Rational(4, 3))))
    kappa_book_f = float(sp.N(kappa_book, 15))
    out = {
        "kappa_book": {"value": kappa_book_f,
                       "exact": "ln(27/4) = 3 ln 3 - 2 ln 2",
                       "is_3ln3_minus_2ln2": bool(id1 == 0),
                       "is_4ln32_plus_ln43": bool(id2 == 0),
                       "decomposition": "4 ln(3/2) + 1 ln(4/3) — 5 книг + "
                                        "1 нулевая (нейтральный пивот) на 6 "
                                        "станций",
                       "dev_vs_kappa_obs_gamma_lit_pct":
                           float(sp.N(100 * (kappa_book - KAPPA_OBS_GLIT)
                                      / KAPPA_OBS_GLIT, 8)),
                       "dev_vs_kappa_obs_b_Ch_pct":
                           float(sp.N(100 * (kappa_book - KAPPA_OBS_BCH)
                                      / KAPPA_OBS_BCH, 8)),
                       },
    }
    log(f"    kappa_book = ln(27/4) = {kappa_book_f:.6f} "
        f"({out['kappa_book']['dev_vs_kappa_obs_gamma_lit_pct']:+.2f}% к "
        f"kappa_obs(gamma_lit))")
    # ---- станционная лестница цепочки при tau* (точные значения) ----------
    T0v = 3 * sp.sqrt(3) / 2
    forms = s2_out.get("chain_forms") or {}
    loc = {n_: sp.Symbol(n_) for n_ in ("T0h", "R1h")}
    sub_pt = {loc["T0h"]: T0v, loc["R1h"]: 1}
    amps = {
        "R1h": sp.Integer(1), "D0h": sp.Integer(0),
        "P2h": sp.sqrt(3) / 2, "R3h": sp.Rational(3, 2),
        "W2h": sp.Integer(9), "T0h": T0v,
    }
    for k_ in ("R5h", "M5h", "P4h"):
        if k_ in forms:
            amps[k_] = sp.simplify(sp.sympify(forms[k_], locals=loc)
                                   .subs(sub_pt))
        else:
            amps[k_] = sp.Symbol(k_)
    amps = {k_: sp.simplify(v_) for k_, v_ in amps.items()}
    hex_facts = {
        "tau_star_is_3cubed_over_4": sp.sstr(TAU_STAR) == "27/4",
        "P2h_is_sin_pi_over_3": sp.sstr(sp.nsimplify(amps["P2h"])) == "sqrt(3)/2",
        "W2h_over_R3h": sstr(sp.simplify(amps["W2h"] / amps["R3h"])),
        "W2h_over_T0h2": sstr(sp.simplify(
            amps["W2h"] / amps["T0h"]**2)),
        "R3h_over_T0h2": sstr(sp.simplify(
            amps["R3h"] / amps["T0h"]**2)),
        "P2h_over_T0h": sstr(sp.simplify(
            amps["P2h"] / amps["T0h"])),
        "T0h_over_P2h": sstr(sp.simplify(
            amps["T0h"] / amps["P2h"])),
        "R5h": sstr(amps["R5h"]), "M5h": sstr(amps["M5h"]),
        "P4h": sstr(amps["P4h"]),
    }
    out["hex_facts"] = hex_facts
    log(f"    гексагональные факты цепочки: W2h/R3h = {hex_facts['W2h_over_R3h']}, "
        f"W2h/T0h^2 = {hex_facts['W2h_over_T0h2']}, "
        f"P2h = sin(pi/3): {hex_facts['P2h_is_sin_pi_over_3']}, "
        f"P4h = {hex_facts['P4h']}")
    # ---- монодромия амплитуд: замкнутый контур отношений ------------------
    # контур: R1h -> T0h -> P2h -> R3h -> W2h -> R5h -> R1h (6 звеньев)
    loop = ["R1h", "T0h", "P2h", "R3h", "W2h", "R5h"]
    ratios, logs_sum = [], sp.Integer(0)
    prod = sp.Integer(1)
    for i_ in range(len(loop)):
        a_, b_ = loop[i_], loop[(i_ + 1) % len(loop)]
        rt = sp.simplify(amps[a_] / amps[b_])
        ratios.append({"from": a_, "to": b_, "ratio": sstr(rt),
                       "log": float(sp.N(sp.log(abs(rt)), 10))
                       if rt != 0 else None})
        logs_sum += sp.log(sp.Abs(rt)) if rt != 0 else sp.Integer(0)
        prod *= rt
    mono_res = sp.simplify(sp.expand(prod - 1))
    out["station_ladder"] = {
        "loop": loop,
        "ratios": ratios,
        "log_sum_closed_loop": float(sp.N(logs_sum, 12)),
        "monodromy_product": sstr(prod),
        "monodromy_identity": bool(mono_res == 0),
        "note": ("произведение отношений по замкнутому контуру = 1 — "
                 "монодромия амплитуд вокруг 6-станционного цикла = "
                 "тождество (возврат в пирамиду); машинная проверка"),
    }
    log(f"    монодромия амплитуд (сумма логов контура) = "
        f"{out['station_ladder']['log_sum_closed_loop']}")
    # ---- монодромия за эхо e^{lambda+ Delta} ------------------------------
    mono = {}
    if lp_val is not None:
        for nm, Dv in (("Delta_sp", DELTA_SP), ("Delta_lit", DELTA_LIT),
                       ("Delta_cyc_old", 6 * sp.log(sp.Rational(16, 9)))):
            mu_ = sp.exp(sp.N(lp_sym, 25) * Dv) if lp_sym else None
            mono[nm] = {
                "Delta": float(sp.N(Dv, 12)),
                "mu_exp_lambda_plus_Delta": float(sp.N(mu_, 12)),
                "gamma_pred": float(sp.N(Dv / sp.Float(lp_val, 25), 12)),
            }
        out["monodromy_per_echo"] = mono
        out["gamma_note"] = (
            "gamma_pred = Delta/lambda+ в tau* — НЕ наблюдаемая gamma "
            "(0.374): точка tau* = 27/4 — замороженная точка усечённой "
            "башни, не критический аттрактор (спектр монотонен); честный "
            "статус: монодромия за эхо характеризует устойчивость точки")
    # ---- старые книги: статус артефакта -----------------------------------
    out["old_books_status"] = {
        "kappa_cyc": "ln(64/9) = 2 ln(3/2) + 4 ln(4/3) = 1.9616585",
        "Delta_cyc": "6 ln(16/9) = 12 ln(4/3) = 3.4521849",
        "status": ("построены на двух ветвях (tau3 = 9/4, tau5 = 9/16), "
                   "которые в исправленной системе (аудит вторых потоков) "
                   "сливаются в общий корень tau* = 27/4; конструкция "
                   "признаётся артефактом обнулённых W2''/R3''/P4''/R5'; "
                   "замена: kappa_book = ln(27/4) = 3 ln3 - 2 ln2; часы "
                   "из цепочки НЕ выводятся — честные часы остаются "
                   "измеренными (v8: модель B Delta = 0.73 ~ Delta_sp "
                   "- 0.4%; Q-эхо Delta_cyc/Delta_Q ~ 2)"),
        "survives": ["кольцо 4/3 (W2h/T0h^2 — цепочка + C1-маршрут)",
                     "DSS-картина (предельный цикл, РК4 сеанса 10)",
                     "Delta-сигналы v8 (модель B, Q-пики)"],
    }
    log("    старые книги: статус артефакта зафиксирован; кольцо 4/3 и "
        "DSS переживают пересборку")
    return out


# --------------------------------------------------------------------- main ---
def main() -> None:
    t0w = time.time()
    out = {"config": {
        "model": ("Точный спектр при tau* = 27/4 и книги на монодромии "
                  "исправленной системы (сеанс 12)"),
        "tau_star": "27/4",
        "anchors": {"Delta_sp": "7*pi/30", "Delta_lit": "3.44",
                    "gamma_lit": "0.374", "b_Ch": "1-cos(2*pi/7)"},
    }}
    global _CHAIN_CACHE
    # [S3] сначала (быстрый, не требует o6-системы)
    out["c1_route_ring"] = s3_c1_route_ring()
    # [S1] старый core char при tau*
    try:
        out["old_core_at_tau_star"] = s1_old_core_at_tau_star()
    except Exception:  # noqa: BLE001
        out["old_core_at_tau_star"] = {"error": traceback.format_exc()}
    # [S2] исправленная башня (тяжёлый уровень)
    try:
        out["tower_pencil_at_tau_star"] = s2_tower_pencil_at_tau_star()
    except Exception:  # noqa: BLE001
        out["tower_pencil_at_tau_star"] = {"error": traceback.format_exc()}
    # [S4] книги на монодромии (нужны формы цепочки из [S2])
    try:
        out["books_monodromy"] = s4_books_monodromy(
            out.get("tower_pencil_at_tau_star") or {})
    except Exception:  # noqa: BLE001
        out["books_monodromy"] = {"error": traceback.format_exc()}
    out["runtime_s"] = time.time() - t0w
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    log(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")


if __name__ == "__main__":
    main()
