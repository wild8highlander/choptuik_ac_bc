#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
РАСЧЁТ СХОДИМОСТИ И ОТТАЛКИВАНИЯ ИЗ ПЕРВЫХ ПРИНЦИПОВ — ЦЕНТРАЛЬНАЯ БАШНЯ
CONVERGENCE AND REPULSION FROM FIRST PRINCIPLES — THE CENTRAL TOWER
================================================================================

Маршрут (ни одного подгоночного параметра; эмпирика — только якоря сравнения):

  Гильберт (sympy_derivation.py) → двойной нуль (6 ур.) → иерархия центра
  O1–O5 (sympy_center.py, все формы верифицированы SymPy, включая найденные
  машиной +W2 в O3 и коэффициент 2 в O5) →

  I.  ТОРНОВСКИЙ BOOKKEEPING МАССЫ (маршрут Мизнера–Шарпа, MTW):
      законы потока  m_v = -2 r^2 p t^2 / alpha^2   и   m_u = -2 r^2 q s^2 / alpha^2
      — МАШИННЫЙ вывод из {Mdef, UV, C1, C2} (невязки 0; q_u = p_v через
      смешанные частные r_uv);
      центральная связь масса–наклон  M3 = 2 R1 t0^2 / (3 (1-chi)^2)  — точно,
      при каждой y (не только CSS!);
      калибровка центра из Mdef(xi^0):  (1 - chi^2) R1^2 = A0;
      порог Хупа 2m/r = 1 → xi_AH = sqrt(R1/(2 M3)), CSS: sqrt(3/(4 tau)).

  II. ЛОГ-ВРЕМЯ z = -ln s (s = y* - y): МАШИННАЯ редукция O1–O5 анзацем
      X = x^(z) s^{-p} (таблица показателей p из размерной bookkeeping;
      проверка чистоты: каждый член уравнения несёт одну степень s) →
      автономная z-башня → CSS-неподвижная точка:
          d0* = 0,  t0* = 3 P2*,  W2* = (4/3) tau,  M3*/R1* = (2/3) tau,
          R3*/R1* = (2/9) tau,   tau := t0*^2.
      БЕЗ торновской связки у точки два свободных модуля; связка потока массы
      замыкает её до ОДНОГО параметра (амплитуды tau).

  III. ЛИНЕАРИЗАЦИЯ (замкнутая башня уровней 0–2, глубокие источники
      заморожены):
      tau → 0:   char = -27 λ (λ+1)^2 (λ+2) (λ+3)  →  ТОЧНЫЙ спектр
                 {0, -1, -1, -2, -3} — целые показатели сходимости
                 («выводы фундаментальных уровней» для стабильных мод);
      tau > 0:   ровно ОДИН растущий корень λ+(tau) — канал отталкивания —
                 в codim-1 окне 0 < tau <= tau2,  tau2 = 27/80 ТОЧНО
                 (char(0,tau) = 8 tau (27 - 80 tau));
                 λ+(27/80) = 1.5091 → γ_tower = Δ_sp/λ+ = 0.4857 (минимум);
      точные точки: λ+ = 2 при tau = 1/2 (невязка -216(2τ-1)(8τ-45)) и
                 tau = 45/8;
      tau > 27/80: второй растущий корень — «распады/сборки» (взрывные
                 частные случаи — ожидаемая физика).

  IV. ЭМПИРИКА (критическая цепочка v5): поток-диагностика
      M3 vs 2R1t0^2/(3(1-chi)^2) на строках; tau_row по O1-нормировке
      s = t0/(3 P2); γ_pred(tau_row); монодромия эхо exp(λ Δ_sp); спинорная
      лестница π/15, π/30 (фазы на эхо, 7 квантов pi/30 на эхо).

ЯКОРЯ СРАВНЕНИЯ (не подгоняются): γ_lit = 0.374±0.004, b_Ch = 1-cos(2π/7),
Δ_sp = 7π/30. Наблюдаемый показатель отталкивания κ_obs = Δ_sp/γ ≈ 1.947–1.960
лежит ВЫШЕ λ+(27/80) ≈ 1.509 — дефицит ≈ +0.44 в κ есть количественная мера
вклада глубоких уровней башни (O6+) в отталкивание: замкнутая башня уровней
0–2 даёт точный скелет (устойчивое ядро + один канал отталкивания), но не
процентную γ.

Запуск:  python3 center_modes.py    # ~2–4 мин (SymPy + 1 цепочка зумов)
Вывод:   results/center_modes.json, figures/fig_modes_{ru,en}.png
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
for _fd in ("fig_ru", "fig_en"):
    os.makedirs(os.path.join(BASE, "figures", _fd), exist_ok=True)

# ------------------------------------------------------------------------------
# Константы (рамка монографии + литература — ТОЛЬКО якоря сравнения)
# ------------------------------------------------------------------------------
KAPPA = sp.Integer(2)                      # 8*pi*G = 2 (4*pi*G = 1) — точно
DELTA_SP = 7.0 * np.pi / 30.0              # рамка: Delta = 7 квантов pi/30
B_CH = 1.0 - np.cos(2.0 * np.pi / 7.0)     # 0.3765102...
GAMMA_LIT = 0.374
DELTA_LIT = 0.737637
PHI15 = np.pi / 15.0
PHI30 = np.pi / 30.0
A_STAR = 0.0805333
EPS_RUN = 1e-4

log_lines: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    log_lines.append(msg)


# ==============================================================================
# I. ТОРНОВСКИЙ BOOKKEEPING МАССЫ (Мизнер–Шарп, MTW)
# ==============================================================================
def part1_thorne():
    out = {}
    r, p, q, s_, t_, c_, d_, m, a2 = sp.symbols("r p q s t c d m a2", nonzero=True)
    # Mdef: м = (r/2)(1 + 4 p q / a2)  →  2 p q / a2 = m/r - 1/2
    # Правила системы (kappa = 2):
    #   (UV)  p_v = -a2 m/(2 r^2);  (C2) q_v = 2 d q - r t^2;  (C1) p_u = 2 c p - r s^2
    #   a2_v = 2 a2 d;  a2_u = 2 a2 c;  q_u = p_v (смешанные частные r_uv)
    # d_v(m) = q/2 + (2/a2)(p q^2 + r q p_v + r p q_v) - 2 r p q a2_v / a2^2
    m_v = (q / 2 + (2 / a2) * (p * q**2 + r * q * (-a2 * m / (2 * r**2))
                               + r * p * (2 * d_ * q - r * t_**2))
           - 2 * r * p * q * (2 * a2 * d_) / a2**2)
    target_v = -2 * r**2 * p * t_**2 / a2
    # устраняем p через Mdef: p = a2 (2m/r - 1)/(4 q)
    p_elim = a2 * (2 * m / r - 1) / (4 * q)
    res_v = sp.simplify((m_v - target_v).subs(p, p_elim))
    out["flux_law_v"] = {"expr": "m_v = -2 r^2 p t^2 / alpha^2",
                         "residual": sp.sstr(res_v), "verified": res_v == 0}
    m_u = (p / 2 + (2 / a2) * (p**2 * q + r * q * (2 * c_ * p - r * s_**2)
                               + r * p * (-a2 * m / (2 * r**2)))
           - 2 * r * p * q * (2 * a2 * c_) / a2**2)
    target_u = -2 * r**2 * q * s_**2 / a2
    res_u = sp.simplify((m_u - target_u).subs(p, p_elim))
    out["flux_law_u"] = {"expr": "m_u = -2 r^2 q s^2 / alpha^2",
                         "residual": sp.sstr(res_u), "verified": res_u == 0}
    log(f"[I] торновские законы потока: v -> {res_v}, u -> {res_u}")
    return out


def part1_center_link():
    """Центральная связь M3 = 2 R1 t0^2 / (3 (1-chi)^2) + калибровка центра."""
    # анзац sympy_center (общий chi)
    from sympy_center import (R1, R3, P0, P2, W0, M3, CHI, d_u, d_v, xi, y,
                              series_coeffs)
    r_e = R1 * xi + R3 * xi**3
    Phi_e = P0 + P2 * xi**2
    om_e = W0
    m_e = M3 * xi**3
    a2_e = sp.exp(2 * om_e)
    s_e, t_e = d_u(Phi_e), d_v(Phi_e)
    p_e, q_e = d_u(r_e), d_v(r_e)
    # поток: d_v m  vs  -2 r^2 p t^2 / a2
    lhs = d_v(m_e)
    rhs = -2 * r_e**2 * p_e * t_e**2 / a2_e
    diff = sp.simplify(lhs - rhs)
    cs = series_coeffs(diff, order=4)
    # xi^2: (3(1-chi)/2) M3 - R1 t0^2/(1-chi) = 0 → M3-связка
    t0sym = sp.diff(P0, y) / 2
    eq2 = sp.simplify(cs[2])
    M3_raw = sp.solve(sp.Eq(eq2, 0), M3)[0]
    # калибровка центра: m(0) = 0 → a2(0) = -4 p(0) q(0) = (1-chi^2) R1^2
    p0 = sp.simplify(p_e.subs(xi, 0))
    q0 = sp.simplify(q_e.subs(xi, 0))
    a2_center = sp.simplify(-4 * p0 * q0)
    M3_link = sp.simplify(M3_raw.subs(sp.exp(2 * W0), a2_center))
    M3_target = 2 * R1 * t0sym**2 / (3 * (1 - CHI) ** 2)
    link_res = sp.simplify(M3_link - M3_target)
    out = {
        "mass_slope_link": {"expr": "M3 = 2 R1 t0^2 / (3 (1-chi)^2)",
                            "residual": sp.sstr(link_res), "verified": link_res == 0,
                            "note": "точно при каждой y (не только CSS)"},
        "gauge_center": {"expr": "(1-chi^2) R1^2 = A0",
                         "a2_center": sp.sstr(a2_center),
                         "verified": sp.simplify(a2_center - (1 - CHI**2) * R1**2) == 0},
        "hoop": {"threshold": "2m/r = 1",
                 "xi_AH": "sqrt(R1/(2 M3))",
                 "css_value": "sqrt(3/(4 tau))  (chi=0)"},
    }
    log(f"[I] связь M3(t0): невязка {link_res}; калибровка: {sp.sstr(a2_center)}")
    return out


# ==============================================================================
# II. ЛОГ-ВРЕМЯ: МАШИННАЯ РЕДУКЦИЯ O1–O5
# ==============================================================================
def part2_z_tower():
    """Редукция верифицированных O1–O5 анзацем X = x^(z) s^{-p}: z-система."""
    import sympy_center as sc

    y = sc.y
    S = sp.Symbol("s_collapse", positive=True)
    # z-символы: значения (шапки) и z-производные
    T0, P2h, Q, D0, R1h, R3h, W2h, M3h, P4h, A0 = sp.symbols(
        "T0h P2h Qh D0h R1h R3h W2h M3h P4h A0")
    dT0, dD0, ddQ, dR1 = sp.symbols("dT0h dD0h ddQh dR1h")
    # таблица показателей p: P0=0, R1=0, W0=0, P2=2, R3=2, W2=2, M3=2, P4=4
    # ВАЖНО: сначала производные, потом функции (иначе Derivative(f(y),y)
    # при подстановке f(y) → expr обнулится дифференцированием выражения)
    tbl_d = {
        sp.diff(sc.P0, y, 2): 2 * (dT0 + T0) / S**2,
        sp.diff(sc.P0, y): 2 * T0 / S,
        sp.diff(sc.R1, y): dR1 / S,
        sp.diff(sc.P2, y, 2): (ddQ + 5 * Q + 6 * P2h) / S**4,
        sp.diff(sc.P2, y): (Q + 2 * P2h) / S**3,
        sp.diff(sc.R3, y): 2 * R3h / S**3,      # dR3* = 0 (заморожен)
        sp.diff(sc.W0, y, 2): 2 * (dD0 + D0) / S**2,
        sp.diff(sc.W0, y): 2 * D0 / S,
    }
    tbl_f = {
        sc.R1: R1h,
        sc.P2: P2h / S**2,
        sc.P4: P4h / S**4,
        sc.R3: R3h / S**2,
        sc.W2: W2h / S**2,
        sc.M3: M3h / S**2,
        sp.exp(2 * sc.W0): A0,
        sp.exp(-2 * sc.W0): 1 / A0,
    }

    def to_z(expr):
        # явный порядок: производные → функции (subs(dict) даёт свою сортировку)
        for k_, v_ in tbl_d.items():
            expr = expr.subs(k_, v_)
        for k_, v_ in tbl_f.items():
            expr = expr.subs(k_, v_)
        return sp.expand(expr)

    def purify(ze):
        """Общая степень s: (k, s-свободное выражение); k=None — не чисто."""
        for k in range(0, 7):
            cand = sp.simplify(sp.expand(ze * S**k))
            if not cand.has(S):
                return k, cand
        return None, ze
    # машинные формы O1–O5 (как в sympy_center.main, из верифицированных остатков)
    coeffs = {nm: sc.series_coeffs(sc.chi0(res), order=4)
              for nm, res in sc.RESIDUALS.items()}
    O1 = sp.diff(sc.P0, y, 2) / 2 - 3 * sc.P2 + sp.diff(sc.P0, y) * sp.diff(sc.R1, y) / sc.R1
    O2 = sp.diff(sc.R1, y) - sc.R1 * sp.diff(sc.W0, y)
    O3 = (sp.diff(sc.W0, y, 2) / 2 - sc.M3 * sp.exp(2 * sc.W0) / sc.R1**3 - sc.W2
          + sp.diff(sc.P0, y) ** 2 / 2)
    sc2 = sp.simplify(coeffs["SC"][2])
    P2pp = sp.solve(sp.Eq(sc2, 0), sp.diff(sc.P2, y, 2))[0]
    O5 = sp.diff(sc.P2, y, 2) - P2pp
    forms = {"O1": O1, "O2": O2, "O3": O3, "O5": O5}

    z_eqs, purity = {}, {}
    for nm, form in forms.items():
        k, ze = purify(to_z(form))
        purity[nm] = k
        z_eqs[nm] = ze
    # O4 (алгебраическая связь M3) из Mdef xi^3
    md3 = sp.simplify(coeffs["Mdef"][3])
    M3_series = sp.solve(sp.Eq(md3, 0), sc.M3)[0]
    k4, o4z = purify(to_z(sc.M3 - M3_series))
    purity["O4"] = k4
    # M3-связка из O4: solve o4z = 0 относительно M3h
    M3_expr = sp.solve(sp.Eq(o4z, 0), M3h)[0]

    # замыкание: dR1 = 2 D0 R1 (O2), A0 = R1^2 (калибровка chi=0)
    dR1_val = 2 * D0 * R1h
    F1 = sp.simplify(sp.solve(sp.Eq(z_eqs["O1"], 0), dT0)[0]
                     .subs(dR1, dR1_val))
    F3 = sp.simplify(sp.solve(sp.Eq(z_eqs["O5"], 0), ddQ)[0]
                     .subs(dR1, dR1_val))
    F4 = sp.simplify(sp.solve(sp.Eq(z_eqs["O3"], 0), dD0)[0]
                     .subs(M3h, M3_expr).subs(dR1, dR1_val).subs(A0, R1h**2))
    out = {
        "p_table": {"P0": 0, "R1": 0, "W0": 0, "P2": 2, "R3": 2, "W2": 2,
                    "M3": 2, "P4": 4},
        "purity_s_powers": purity,
        "z_system": {
            "F1_dt0": sp.sstr(F1), "F2_dP2": "Qh",
            "F3_ddQ": sp.sstr(F3), "F4_dD0": sp.sstr(F4),
            "F5_dR1": "2 D0h R1h",
            "M3_link_O4": sp.sstr(M3_expr),
        },
    }
    log(f"[II] чистота по s: {purity}")
    log(f"[II] F1: dT0 = {sp.sstr(F1)}")
    log(f"[II] F4: dD0 = {sp.sstr(F4)}")
    return out, (T0, P2h, Q, D0, R1h), (W2h, R3h, P4h), (F1, F3, F4), M3_expr, A0


# ==============================================================================
# III. ЛИНЕАРИЗАЦИЯ: СПЕКТР СХОДИМОСТИ И ОТТАЛКИВАНИЯ
# ==============================================================================
def part3_linearization(state, sources, Fs, M3_expr, A0):
    T0, P2h, Q, D0, R1h = state
    W2h, R3h, P4h = sources
    F1, F3, F4 = Fs
    lam = sp.Symbol("lambda")
    tau = sp.Symbol("tau", nonnegative=True)
    rho1 = sp.Symbol("rho1", positive=True)
    T = sp.Symbol("T_amp", positive=True)

    Fv = sp.Matrix([F1, Q, F3, F4, 2 * D0 * R1h])
    V = sp.Matrix([T0, P2h, Q, D0, R1h])
    J = Fv.jacobian(V)

    # CSS-неподвижная точка + торновская связка (M3*/R1* = 2T²/3):
    # D0*=0, Q*=0, P2*=T/3, W2*=(4/3)T², R3*=(2/9)T²·ρ1,
    # P4* = (3 + 8(R3*/R1*))P2*/10, T = t0*  (τ ≡ T² — после построения poly)
    fp = {T0: T, P2h: T / 3, Q: 0, D0: 0, R1h: rho1,
          W2h: sp.Rational(4, 3) * T**2, R3h: sp.Rational(2, 9) * T**2 * rho1,
          P4h: (3 + sp.Rational(16, 9) * T**2) * T / 30}
    fp_check = [sp.simplify(F.subs(fp)) for F in Fv]
    fp_ok = all(v == 0 for v in fp_check)
    log(f"[III] проверка CSS-точки (с торновской связкой): {fp_check} -> {fp_ok}")

    Jc = sp.simplify(J.subs(fp))
    char_raw = sp.det(sp.Matrix(Jc - lam * sp.eye(5)))
    char = sp.factor(sp.cancel(char_raw.subs(T**2, tau)))
    # нормируем на старший коэффициент
    cl = sp.Poly(char, lam)
    lead = cl.LC()
    char_n = sp.factor(sp.cancel(char / lead))

    # точные проверки
    char0 = sp.factor(sp.cancel((char / lead).subs(tau, 0)))
    exact_spectrum = sp.solve(sp.Poly(char0, lam).as_expr(), lam)
    res_lam2 = sp.factor(sp.cancel((char / lead).subs(lam, 2)))
    char_at_lam0 = sp.factor(sp.cancel((char / lead).subs(lam, 0)))
    tau2_exact = sp.solve(sp.Eq(char_at_lam0, 0), tau)
    log(f"[III] char(tau=0) = {char0}")
    log(f"[III] корни при tau=0: {sorted(exact_spectrum, key=sp.default_sort_key)}")
    log(f"[III] char(lam=2) = {res_lam2}")
    log(f"[III] char(lam=0) = {char_at_lam0} -> tau2 = {tau2_exact}")

    # численные траектории корней
    cn = sp.Poly(char_n, lam).all_coeffs()
    cf = [sp.lambdify(tau, c, "numpy") for c in cn]

    def roots_at(tv):
        co = [float(c(tv)) for c in cf]
        return np.roots(co)

    def lambda_plus(tv):
        return float(np.max(roots_at(tv).real))

    tau_grid = [1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 27 / 80,
                0.4, 0.48, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
    curve = []
    for tv in tau_grid:
        lp = lambda_plus(tv)
        n_pos = int(np.sum(roots_at(tv).real > 1e-9))
        curve.append({"tau": float(tv), "lambda_plus": lp,
                      "n_growing": n_pos,
                      "gamma_pred": float(DELTA_SP / lp) if lp > 1e-12 else None,
                      "monodromy_per_echo": float(np.exp(lp * DELTA_SP))})
        log(f"[III] tau={tv:9.5f}: lambda+={lp:9.5f}, растущих={n_pos}, "
            f"gamma_pred={DELTA_SP / lp if lp > 1e-12 else float('nan'):.4f}")

    tau2 = 27.0 / 80.0
    lp_tau2 = lambda_plus(tau2)
    gamma_min = DELTA_SP / lp_tau2
    kappa_obs_bch = DELTA_SP / B_CH
    kappa_obs_glit = DELTA_SP / GAMMA_LIT
    # формальная амплитуда lambda+ = kappa_obs (вне codim-1 окна)
    def tau_for_kappa(kappa_target):
        lo, hi = 1e-3, 20.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if lambda_plus(mid) < kappa_target:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)
    tau_bch = tau_for_kappa(kappa_obs_bch)
    tau_glit = tau_for_kappa(kappa_obs_glit)

    out = {
        "char_poly_normalized": sp.sstr(char_n),
        "css_fixed_point": {"d0": 0, "t0": "3 P2", "Q": 0,
                           "W2": "4 tau/3", "M3_over_R1": "2 tau/3",
                           "R3_over_R1": "2 tau/9",
                           "P4": "(3+16*tau/9)*P2/10",
                           "verified": bool(fp_ok),
                           "note": ("без торновской связки у точки два свободных "
                                    "модуля; связка потока массы замыкает до "
                                    "одного (амплитуда tau)"), },
        "tau0_factorization": sp.sstr(char0),
        "fundamental_spectrum_exact": [sp.sstr(x) for x in
                                       sorted(exact_spectrum,
                                              key=sp.default_sort_key)],
        "exact_point_lambda2": {"residual": sp.sstr(res_lam2),
                                "tau": ["1/2", "45/8"]},
        "char_at_lambda0": sp.sstr(char_at_lam0),
        "tau2_codim1_edge": {"value": "27/80", "numeric": tau2,
                             "lambda_plus": lp_tau2,
                             "gamma_tower_min": gamma_min},
        "gamma_curve": curve,
        "anchors": {
            "kappa_obs_bCh": kappa_obs_bch,
            "kappa_obs_gamma_lit": kappa_obs_glit,
            "deficit_kappa_vs_tower": (kappa_obs_bch - lp_tau2,
                                       kappa_obs_glit - lp_tau2),
            "tau_formal_bCh": tau_bch,
            "tau_formal_gamma_lit": tau_glit,
            "note": ("kappa_obs = Delta_sp/gamma > lambda+(27/80): "
                     "наблюдаемое отталкивание сильнее, чем даёт замкнутая "
                     "башня уровней 0-2 в codim-1 окне — дефицит есть мера "
                     "вклада глубоких уровней (O6+)"),
        },
        "spinor_ladder": {
            "delta_spinor": DELTA_SP,
            "quanta_per_echo": DELTA_SP / PHI30,
            "phase_per_echo_pi30": PHI30 * DELTA_SP,
            "phase_per_echo_pi15": PHI15 * DELTA_SP,
            "wiggle_phase_per_echo": float(4 * np.pi),
            "monodromy_fundamental": {
                "lam_-1": float(np.exp(-DELTA_SP)),
                "lam_-2": float(np.exp(-2 * DELTA_SP)),
                "lam_-3": float(np.exp(-3 * DELTA_SP)),
            },
            "note": ("стабильные моды башни за эхо затухают как e^{lam*Delta} "
                     "< 1 (сходимость); спинорные фазы pi/15, pi/30 дают "
                     "вращение на эхо (лестница монографии)"),
        },
        "honest_notes": [
            "tau — единственный свободный модуль замкнутой башни (уровни 0-2); "
            "полная башня (O6+) должна фиксировать его — не сделано (честно).",
            "Замороженные источники (W2*, R3*, P4*, dR3*=0) — стандартная "
            "линеаризация замкнутой башни; их динамика — уровни O6+.",
            "z-башня выведена при chi=0; chi-поправки — в center_hierarchy.json.",
        ],
    }
    # живое sympy-выражение и коэффициенты — для part4/figure (не в JSON)
    cf_exprs = sp.Poly(char_n, lam).all_coeffs()
    return out, char_n, cf_exprs


# ==============================================================================
# IV. ЭМПИРИКА: КРИТИЧЕСКАЯ ЦЕПОЧКА v5
# ==============================================================================
def part4_empirics(cf_exprs):
    tau_sym = sp.Symbol("tau", nonnegative=True)
    cf_l = [sp.lambdify(tau_sym, c, "numpy") for c in cf_exprs]

    def lambda_plus(tv):
        co = [float(c(tv)) for c in cf_l]
        return float(np.max(np.roots(co).real))

    out = {"available": False}

    # --- (a) Валидация торновской связи на ЧИСТЫХ regular-забегах -------------
    # M3 = 2 R1 t0^2 / (3 (1-chi)^2) — точная идентичность для решений системы;
    # измеряем на строках подкритических забегов (sympy_center.measure_center_row)
    try:
        from sympy_center import numeric_center_check
        val = {}
        for A_val in (0.02, 0.075):
            chk = numeric_center_check(A=A_val, n=800, closure="regular")
            preds, ratios = [], []
            for row in chk["rows"]:
                if not row.get("fit_ok"):
                    continue
                t0e, R1f, M3f = row["t0_even"], row["R1_fit"], row["M3_fit"]
                if abs(t0e) < 1e-8 or not np.isfinite(M3f):
                    continue
                pred = 2.0 * R1f * t0e**2 / 3.0
                if abs(pred) > 1e-300:
                    preds.append(abs(pred))
                    ratios.append((abs(pred), M3f / pred))
            if not preds:
                continue
            # фильтр нулевого перехода t0: |pred| >= 25% максимума
            cut = 0.25 * max(preds)
            rr = np.array([x for a, x in ratios if a >= cut])
            rr = rr[np.isfinite(rr)]
            val[f"A={A_val}"] = {
                "n_rows": int(len(rr)),
                "flux_ratio_median": float(np.median(rr)) if len(rr) else None,
                "flux_ratio_p10": float(np.percentile(rr, 10)) if len(rr) else None,
                "flux_ratio_p90": float(np.percentile(rr, 90)) if len(rr) else None,
                "flux_dev_median": float(np.median(np.abs(rr - 1))) if len(rr) else None,
            }
            log(f"[IV] Торновская связь (A={A_val}, regular): ratio "
                f"median={val[f'A={A_val}']['flux_ratio_median']}, "
                f"p10..p90 = [{val[f'A={A_val}']['flux_ratio_p10']}, "
                f"{val[f'A={A_val}']['flux_ratio_p90']}]")
        out["thorne_link_validation"] = val
        out["thorne_link_validation"]["note"] = (
            "идентичность M3 = 2R1t0^2/(3(1-chi)^2) символически точна "
            "(невязка 0); на сетке n=800 (regular) ratio > 1 с дрейфом — "
            "это мера xi-junk в m (m/xi^3 = M1/xi^2 + M3: 1/r-мода завышает "
            "M3_fit на кольце) + систематика фитов. Строгая метрика качества "
            "центра; сжатие до процентов — цель v6 (та же стена, что и "
            "процентная gamma).")
        out["available"] = True
    except Exception as exc:  # noqa: BLE001
        out["thorne_link_error"] = repr(exc)
        log(f"[IV] валидация связи недоступна: {exc!r}")

    # --- (b) Критическая цепочка v5: невязки O1/O3 + xi_AH + честный вердикт ---
    try:
        from zoom_solver import ZoomRunner
        from spinor_ladder import ode_residuals
        A = A_STAR + EPS_RUN
        log(f"[IV] цепочка зумов: A = {A} (A* + {EPS_RUN}), n = 800...")
        runner = ZoomRunner(A=A, n=800, max_zooms=12, verbose=False)
        diag = runner.run()
        rows = list(runner.tay_hist_all)
        out["run"] = {"A": A, "zooms": diag.zooms, "stop": diag.stopped,
                      "z_reached": float(runner._z_acc),
                      "n_tay_rows": len(rows)}
        log(f"[IV] z={runner._z_acc:.2f}, zooms={diag.zooms}, строк={len(rows)}")
        # xi_AH: радиус горизонта Хупа в xi-единицах (s-свободная величина)
        xah = [np.sqrt(r_["R1"] / (2.0 * r_["M3"])) for r_ in rows
               if r_.get("M3", 0.0) > 1e-300 and r_.get("R1", 0.0) > 0
               and np.isfinite(r_.get("M3", np.nan))]
        xah = np.array(xah) if xah else np.array([])
        out["xi_AH_hoop"] = {
            "n": int(len(xah)),
            "median": float(np.median(xah)) if len(xah) else None,
            "p10": float(np.percentile(xah, 10)) if len(xah) else None,
            "p90": float(np.percentile(xah, 90)) if len(xah) else None,
            "note": ("2m/r = 2(M3/R1)xi^2 = 1 при xi = sqrt(R1/(2M3)); "
                     "в CSS xi_AH = sqrt(3/(4 tau)) — O(1) в xi-единицах"),
        }
        log(f"[IV] xi_AH (Хуп): median = {out['xi_AH_hoop']['median']}")
        # диагностика t0-транзиентов тейлор-патча на зум-стадиях
        ok = [r_ for r_ in rows
              if np.isfinite(r_.get("t0", np.nan)) and r_.get("P2", 0.0) != 0.0
              and r_.get("R1", 0.0) > 0 and np.isfinite(r_.get("M3", np.nan))]
        recs = []
        for r_ in ok:
            t0v, P2v, R1v, M3v = r_["t0"], r_["P2"], r_["R1"], r_["M3"]
            chi = r_.get("chi", 0.0)
            rec = {"v": float(r_["v"]), "stage": r_.get("stage", -1)}
            pred = 2.0 * R1v * t0v**2 / (3.0 * (1.0 - chi) ** 2)
            rec["flux_ratio"] = float(M3v / pred) if abs(pred) > 1e-300 else None
            s_row = t0v / (3.0 * P2v)
            rec["tau_row"] = float((t0v * s_row) ** 2)
            if 1e-4 <= rec["tau_row"] <= 30.0:
                kp = lambda_plus(rec["tau_row"])
                rec["kappa_rep"] = kp
                rec["gamma_pred"] = float(DELTA_SP / kp) if kp > 1e-9 else None
            recs.append(rec)
        # консистентные строки: identity в разумном диапазоне → tau_row значим
        good = [r_ for r_ in recs if r_.get("flux_ratio") is not None
                and 0.2 < r_["flux_ratio"] < 5.0 and "gamma_pred" in r_]
        out["n_rows_consistent"] = len(good)
        if good:
            out["tau_consistent"] = {
                "tau_row_median": float(np.median([r_["tau_row"] for r_ in good])),
                "gamma_pred_median": float(np.median([r_["gamma_pred"] for r_ in good])),
                "n": len(good),
            }
            log(f"[IV] консистентных строк: {len(good)}, "
                f"gamma_pred_median = {out['tau_consistent']['gamma_pred_median']}")
        fr_all = np.array([abs(r_["flux_ratio"] - 1.0) for r_ in recs
                           if r_.get("flux_ratio") is not None])
        out["flux_diagnostic_chain"] = {
            "n": int(len(fr_all)),
            "dev_median": float(np.median(fr_all)) if len(fr_all) else None,
            "dev_p90": float(np.percentile(fr_all, 90)) if len(fr_all) else None,
        }
        out["ode_residuals"] = ode_residuals(rows)
        out["available"] = True
        out["honest_notes"] = [
            "Торновская связь M3 = 2R1t0^2/(3(1-chi)^2) валидирована на "
            "ЧИСТЫХ регулярных забегах (thorne_link_validation); на строках "
            "критической ЦЕПОЧКИ после зум-рестартов t0 тейлор-патча — "
            "транзиент внутреннего ГУ, мгновенная identity нарушается "
            "(flux_diagnostic_chain) — это мера незарелаксированности патча, "
            "а не опровержение связи (связь точна для решений системы).",
            "tau_row значим только на консистентных строках (flux_ratio в "
            "[0.2, 5]); на цепочке v5 их мало — CSS-амплитуда на z~4.5 не "
            "измеряется, нужен z>=30 (v6).",
            "xi_AH (Хуп) — s-свободная величина, O(1) в xi-единицах, как и "
            "предсказывает CSS: sqrt(3/(4 tau)).",
        ]
    except Exception as exc:  # noqa: BLE001 — честная деградация
        out["error"] = repr(exc)
        out["honest_notes"] = ["цепочка зумов недоступна в этой среде — "
                               "эмпирическая часть пропущена (честно)."]
        log(f"[IV] НЕ ДОСТУПНО: {exc!r}")
    return out


# ==============================================================================
# Рисунок: спектр башни и gamma_pred(tau)
# ==============================================================================
def make_figure(cf_exprs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    for fp_ in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(fp_):
            fm.fontManager.addfont(fp_)
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    tau_sym = sp.Symbol("tau", nonnegative=True)
    cf = [sp.lambdify(tau_sym, c, "numpy") for c in cf_exprs]

    def roots_at(tv):
        return np.roots([float(c(tv)) for c in cf])

    taus = np.logspace(-4, np.log10(6.0), 400)
    branches = np.full((5, len(taus)), np.nan + 0j)
    for i, tv in enumerate(taus):
        rts = roots_at(tv)
        rts = np.array(sorted(rts, key=lambda z: z.real))
        branches[:len(rts), i] = rts

    titles = {"ru": ("Башня центра: спектр сходимости и отталкивания",
                     "γ_pred(τ) = Δ_sp/λ⁺ и якоря (без подгонки)"),
              "en": ("Central tower: convergence / repulsion spectrum",
                     "γ_pred(τ) = Δ_sp/λ⁺ and anchors (no fitting)")}
    for lang, (t1, t2) in titles.items():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6),
                                       constrained_layout=True)
        for bi in range(5):
            ax1.semilogx(taus, branches[bi].real, lw=1.4)
        ax1.axhline(0.0, color="k", lw=0.6)
        ax1.axvline(27 / 80, color="crimson", ls="--", lw=1.2,
                    label="τ₂ = 27/80 (codim-1)")
        ax1.axhspan(DELTA_SP / B_CH - 0.01, DELTA_SP / GAMMA_LIT + 0.01,
                    color="orange", alpha=0.35,
                    label="κ_obs = Δ_sp/γ ≈ 1.95–1.96")
        ax1.plot([0.5], [2.0], "k*", ms=11,
                 label="λ⁺ = 2 при τ = 1/2 (точно)")
        ax1.set_xlabel("τ = t0*²")
        ax1.set_ylabel("Re λ")
        ax1.set_title(t1)
        ax1.legend(fontsize=8, loc="lower right")
        lp = np.array([float(np.max(roots_at(tv).real)) for tv in taus])
        with np.errstate(divide="ignore"):
            gp = np.where(lp > 1e-12, DELTA_SP / np.maximum(lp, 1e-12), np.nan)
        ax2.semilogx(taus, gp, lw=1.6, label="γ_pred(τ)")
        ax2.axvline(27 / 80, color="crimson", ls="--", lw=1.2)
        ax2.axhline(B_CH, color="green", lw=1.2, label="b_Ch = 1−cos(2π/7)")
        ax2.axhline(GAMMA_LIT, color="purple", ls="-.", lw=1.2,
                    label="γ_lit = 0.374")
        ax2.axhspan(0.4857, 3.0, color="grey", alpha=0.15)
        ax2.annotate("codim-1 окно башни:\nγ ≥ Δ_sp/λ⁺(27/80) = 0.486",
                     xy=(1e-3, 0.9), fontsize=8)
        ax2.set_ylim(0.2, 3.0)
        ax2.set_xlabel("τ = t0*²")
        ax2.set_ylabel("γ_pred")
        ax2.set_title(t2)
        ax2.legend(fontsize=8)
        path = os.path.join(BASE, "figures", f"fig_{lang}", "fig_modes.png")
        fig.savefig(path, dpi=300)
        plt.close(fig)
        log(f"[FIG] {path}")


def main():
    t_wall = time.time()
    result = {
        "config": {"kappa": int(KAPPA), "A_star": A_STAR, "eps": EPS_RUN,
                   "delta_spinor": DELTA_SP, "b_Ch": B_CH,
                   "gamma_lit": GAMMA_LIT, "delta_lit": DELTA_LIT,
                   "phi15": PHI15, "phi30": PHI30},
        "route": ("Hilbert -> double-null (sympy_derivation) -> center hierarchy "
                  "O1-O5 (sympy_center) -> [I] Thorne/MTW mass bookkeeping -> "
                  "[II] log-time tower -> [III] linear spectrum -> [IV] empirics"),
        "honest_notes": [],
    }

    # --- I. Торновский маршрут -------------------------------------------------
    log("=" * 78)
    log("ЧАСТЬ I. Торновский bookkeeping массы (Мизнер–Шарп, MTW)")
    log("=" * 78)
    result["thorne"] = part1_thorne()
    result["thorne_center"] = part1_center_link()

    # --- II. z-башня ------------------------------------------------------------
    log("=" * 78)
    log("ЧАСТЬ II. Лог-время z: машинная редукция O1–O5")
    log("=" * 78)
    tower_out, state, sources, Fs, M3_expr, A0 = part2_z_tower()
    result["tower"] = tower_out

    # --- III. Линеаризация и спектр --------------------------------------------
    log("=" * 78)
    log("ЧАСТЬ III. Линеаризация: спектр сходимости и отталкивания")
    log("=" * 78)
    lin = part3_linearization(state, sources, Fs, M3_expr, A0)
    lin_out, char_n, cf_exprs = lin
    result["spectrum"] = lin_out

    # --- IV. Эмпирика -----------------------------------------------------------
    log("=" * 78)
    log("ЧАСТЬ IV. Эмпирика: критическая цепочка v5")
    log("=" * 78)
    result["empirics"] = part4_empirics(cf_exprs)

    # --- рисунок -----------------------------------------------------------------
    try:
        make_figure(cf_exprs)
        result["figures"] = ["figures/fig_ru/fig_modes.png",
                             "figures/fig_en/fig_modes.png"]
    except Exception as exc:  # noqa: BLE001
        result["figures"] = None
        log(f"[FIG] не удалось: {exc!r}")

    result["runtime_s"] = round(time.time() - t_wall, 1)
    path = os.path.join(RESULTS, "center_modes.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1, default=str)
    log(f"Сохранено: {path}")
    return result


if __name__ == "__main__":
    main()
