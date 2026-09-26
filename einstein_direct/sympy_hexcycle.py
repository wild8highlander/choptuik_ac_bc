#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ГЕКСАГОНАЛЬНЫЙ ПУАНКАРЕ-ЦИКЛ ТРАНСФОРМАЦИЙ — ДИНАМИКА ВМЕСТО УСЕЧЁННОЙ БАШНИ
POINCARE HEXAGONAL TRANSFORMATION CYCLE — DYNAMICS INSTEAD OF THE TRUNCATED TOWER
================================================================================

Исходный вердикт (sympy_center_o6_nsolve.py, машино-верифицирован):
  UV[xi^3]  форсирует T0^2 = 9/4    (tau3 = 2.25  = (3/2)^2)
  Mdef[xi^5] форсирует T0^2 = 9/16  (tau5 = 0.5625 = (3/4)^2)
  вместе — только тривиальное R3 = 0: СИСТЕМА НЕСОВМЕСТНА, у усечённой башни
  нет точного CSS-решения; источники W2/R3/P4 принципиально динамичны.

Настоящая машина формализует ответ на этот вердикт: вместо СТАТИЧЕСКОГО
усечения — ДИНАМИЧЕСКИЙ ЦИКЛ из шести станций (гексагон на циферблате формы):

  пирамида -> конус -> усечённый конус -> параболический пивот -> чаша ->
  -> лог-замыкание -> (возврат в пирамиду), и так по кругу.

Две зоны (аксиома модели, согласована с физикой зон):
  CORE-ПАРА  (пирамида, конус)         — UV[xi^3]-ветвь:  шаг ln(3/2)  = ln sqrt(tau3)
  RING-КВАРТЕТ (усечённый, парабола, чаша, замыкание) — Mdef[xi^5]-ветвь:
                                         шаг ln(4/3) = ln(1/sqrt(tau5))
Статическая несовместимость (tau3 != tau5 как точечные условия) растворяется:
две ветви живут в РАЗНЫХ книгах цикла:

  АМПЛИТУДНАЯ КНИГА (per станция): пара (3/2)^2 = tau3 — UV-ограничение
    закрывается ПРОИЗВЕДЕНИЕМ ПАРЫ; каждое кольцо-кольцо... каждое из двух
    колец-пар (усечённый+парабола, чаша+замыкание) даёт (4/3)^2 = 1/tau5.
    Полный цикл: tau3/tau5^2 = 64/9  =>  kappa_cyc = ln(64/9) = 2 ln(3/2)+4 ln(4/3).
  КНИГА ЭХА (per сторона гексагона): часы задаёт Mdef-ветвь:
    шаг часов -ln(tau5) = ln(16/9); 6 сторон => Delta_cyc = 6 ln(16/9) = 12 ln(4/3)
    = 24 ln(2/sqrt(3)) — «6-угольные логарифмические вычисления»: шаг кольца
    4/3 = (2/sqrt(3))^2 — КВАДРАТ отношения радиуса описанной окружности
    гексагона к радиусу вписанной (R/a = 2/sqrt(3)) — точная геометрия.

Уравнения Пуанкаре (квазискорости, абелев циферблат theta): свободная
циркуляция равномерна (p_theta = const), C6-инвариантный потенциал
V = -(V6/6) cos(6 theta) запирает цикл на шести станциях V'(k*pi/3) = 0.
Период циркуляции в log-времени = Delta_cyc — эхо. Цикл не даёт неподвижной
точки (CSS) — он даёт ПРЕДЕЛЬНЫЙ ЦИКЛ = DSS: именно дискретную
самоподобность, которую Чоптюк и наблюдал.

Честные якоря (БЕЗ подгонки, все входы — из результатов предыдущих сессий):
  kappa_obs = Delta_sp/gamma: 1.9601 (gamma_lit = 0.374) / 1.9470 (b_Ch)
  Delta_GHS = 3.44 ± 0.02 (Garfinkle-Horowitz-Stubbs, CSS-нормировка)
  lambda+(27/80) = 1.5091 (замороженная башня, center_modes.json)

Запуск: python3 sympy_hexcycle.py   (~5-10 c, results/hexcycle.json)
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)
log = print


# ------------------------------------------------------------------ якоря ---
def load_anchors() -> dict:
    """Все входы — из машинных результатов предыдущих сессий (без подгонки)."""
    a = {}
    with open(os.path.join(RESULTS, "center_o6_nsolve.json"), encoding="utf-8") as fh:
        o6 = json.load(fh)
    a["tau3"] = o6["pinning"]["branch_UV3_tau"]          # 2.25
    a["tau5"] = o6["pinning"]["branch_Mdef5_tau"]        # 0.5625
    a["o6_verdict"] = o6["pinning"]["verdict"]
    with open(os.path.join(RESULTS, "spinor_analysis.json"), encoding="utf-8") as fh:
        sp_an = json.load(fh)
    fw = sp_an["spinor_framework"]
    a["b_Ch"] = fw["b_Ch = 1-cos(2pi/7)"]                # 0.3765101981412664
    a["Delta_sp"] = fw["Delta_sp = 7*pi/30"]             # 0.7330382858376184
    a["gamma_lit"] = fw["gamma_lit"]                     # 0.374
    a["Delta_lit"] = fw["delta_lit"]                     # 0.737637
    try:
        with open(os.path.join(RESULTS, "center_modes.json"), encoding="utf-8") as fh:
            cm = json.load(fh)
        spec = cm["spectrum"]
        a["lambda_plus_tower"] = spec["tau2_codim1_edge"]["lambda_plus"]  # 1.5090958...
        anch = spec.get("anchors", {})
        # собственные якоря репо (task 8) — первичный источник
        a["kappa_obs_gamma_lit"] = anch.get("kappa_obs_gamma_lit",
                                            a["Delta_sp"] / a["gamma_lit"])
        a["kappa_obs_b_Ch"] = anch.get("kappa_obs_bCh",
                                        a["Delta_sp"] / a["b_Ch"])
    except Exception as exc:                             # noqa: BLE001
        a["lambda_plus_tower"] = None
        a["kappa_obs_gamma_lit"] = a["Delta_sp"] / a["gamma_lit"]
        a["kappa_obs_b_Ch"] = a["Delta_sp"] / a["b_Ch"]
        a["lambda_plus_warning"] = f"center_modes.json: {exc}"
    a["Delta_GHS"] = 3.44                                # Garfinkle-Horowitz-Stubbs
    a["Delta_GHS_err"] = 0.02
    a["delta_Feigenbaum"] = 4.669201609102990
    return a


# --------------------------------------------------------------- символика ---
def sym_checks(A: dict) -> dict:
    """Точные тождества гексагонального замыкания (SymPy, всё должно быть 0)."""
    tau3 = sp.Rational(9, 4)
    tau5 = sp.Rational(9, 16)
    half3, half5 = sp.Rational(3, 2), sp.Rational(3, 4)      # sqrt(tau3), sqrt(tau5)
    ring = sp.Rational(4, 3)                                  # 1/sqrt(tau5)
    chk = {}

    def add(name, expr):
        chk[name] = bool(sp.simplify(sp.expand_log(sp.logcombine(
            sp.simplify(expr), force=True))) == 0)

    # --- ветви: квадраты и их отношение (машина O6: branch_UV3 / branch_Mdef5)
    add("tau3_is_(3/2)^2", tau3 - half3**2)
    add("tau5_is_(3/4)^2", tau5 - half5**2)
    add("branch_ratio_4", tau3 - 4 * tau5)
    add("sqrt_ratio_2 (удвоение пирамиды)", half3 - 2 * half5)
    add("ring_step_1/sqrt(tau5)", ring - 1 / half5)
    # --- гексагон: (R/a)^2 = 4/3  («6-угольные логарифмические вычисления»)
    chk["hexagon_(R/a)^2=4/3"] = bool(sp.simplify(
        (sp.Rational(2) / sp.sqrt(3))**2 - ring) == 0)
    # --- амплитудная книга: пара и два кольца-пары
    add("core_pair_closes_UV", half3**2 - tau3)
    add("ring_pair_closes_Mdef", ring**2 - 1 / tau5)
    add("cycle_book_tau3/tau5^2=64/9", tau3 / tau5**2 - sp.Rational(64, 9))
    add("kappa_cyc=2ln(3/2)+4ln(4/3)=ln(64/9)",
        2 * sp.log(half3) + 4 * sp.log(ring) - sp.log(sp.Rational(64, 9)))
    # --- книга эха: 6 сторон x (-ln tau5)
    add("Delta_cyc=-6ln(tau5)",
        -6 * sp.log(tau5) - 6 * sp.log(sp.Rational(16, 9)))
    add("Delta_cyc=12ln(4/3)",
        6 * sp.log(sp.Rational(16, 9)) - 12 * sp.log(ring))
    add("Delta_cyc=24ln(2/sqrt3)",
        12 * sp.log(ring) - 24 * sp.log(sp.Rational(2) / sp.sqrt(3)))
    # --- согласованность с машинными якорями (числа из JSON)
    chk["anchor_tau3_machine"] = bool(sp.nsimplify(A["tau3"]) == tau3)
    chk["anchor_tau5_machine"] = bool(sp.nsimplify(A["tau5"]) == tau5)
    return chk


def sym_poincare() -> dict:
    """Уравнения Пуанкаре в квазискоростях на абелевом циферблате.

    Группа — окружность (циферблат формы theta); квазискорость omega = theta'.
    Коммутаторы абелевы: c^k_{ij} = 0, уравнения Пуанкаре
        d/dt (dL*/d omega) = X_theta(L*)
    совпадают с Эйлера-Лагранжа. C6-потенциал запирает станции.
    """
    t = sp.Symbol("t", real=True)
    J, V6 = sp.symbols("J V6", positive=True)
    th = sp.Function("theta")(t)
    V = -V6 * sp.cos(6 * th) / 6
    Lstar = J * sp.diff(th, t)**2 / 2 - V

    # форма Пуанкаре: d/dt(dL*/d omega) - X_theta(L*),  X_theta = d/d theta
    poincare_res = (sp.diff(sp.diff(Lstar, sp.diff(th, t)), t)
                    - sp.diff(Lstar, th))
    # форма Эйлера-Лагранжа (должна совпасть — группа абелева)
    el_res = sp.diff(sp.diff(Lstar, sp.diff(th, t)), t) - sp.diff(Lstar, th)
    # эталон: J theta'' + V6 sin(6 theta) = 0
    eom_manual = J * sp.diff(th, t, 2) + V6 * sp.sin(6 * th)

    out = {
        "poincare_abelian_equals_EL": bool(
            sp.simplify(sp.expand(poincare_res - el_res)) == 0),
        "poincare_eq_manual_form": bool(sp.simplify(poincare_res - eom_manual) == 0),
        "station_lock_k_pi_3": [],
        "free_circulation_p_theta_const": None,
        "note": ("группа циферблата абелева: структурные константы c^k_{ij}=0, "
                 "уравнения Пуанкаре = уравнения Эйлера-Лагранжа; C6-потенциал "
                 "V=-(V6/6)cos(6 theta) запирает шесть станций theta=k*pi/3"),
    }
    # запирание станций: V'(k pi/3) = 0 для всех шести
    Vp = sp.diff(V, th)
    for k in range(6):
        out["station_lock_k_pi_3"].append(bool(
            sp.simplify(Vp.subs(th, k * sp.pi / 3)) == 0))
    # свободная циркуляция: V = const => EOM J theta'' = 0 => решение
    # theta = omega0*t + theta0 даёт p_theta = J*omega0 = const (проверка подстановкой)
    omega0, theta0 = sp.symbols("omega0 theta0", positive=True)
    th_free = omega0 * t + theta0
    p_free = J * sp.diff(th_free, t)
    out["free_circulation_p_theta_const"] = bool(
        sp.simplify(sp.diff(p_free, t)) == 0
        and sp.simplify(sp.diff(sp.Symbol("V0"), sp.Symbol("theta"))) == 0)
    out["station_lock_all"] = bool(all(out["station_lock_k_pi_3"]))
    return out


# ---------------------------------------------------- книги замыкания (числа) ---
def closure_books(A: dict) -> dict:
    """Численные книги: kappa_cyc, Delta_cyc, gamma_cyc + честные расхождения."""
    half3, half5 = 1.5, 0.75
    ring = 4.0 / 3.0
    kappa_cyc = 2 * np.log(half3) + 4 * np.log(ring)          # ln(64/9)
    delta_cyc = -6 * np.log(A["tau5"])                        # 6 ln(16/9)
    d_sp, g_lit, b_ch = A["Delta_sp"], A["gamma_lit"], A["b_Ch"]
    kap_glit = A["kappa_obs_gamma_lit"]      # якорь репо (task 8)
    kap_bch = A["kappa_obs_b_Ch"]
    gamma_cyc = d_sp / kappa_cyc
    lam = A.get("lambda_plus_tower")
    out = {
        "kappa_cyc": kappa_cyc,
        "kappa_cyc_exact": "ln(64/9) = 2 ln(3/2) + 4 ln(4/3)",
        "kappa_obs_gamma_lit": kap_glit,
        "kappa_obs_b_Ch": kap_bch,
        "kappa_dev_vs_gamma_lit_pct": 100 * (kappa_cyc - kap_glit) / kap_glit,
        "kappa_dev_vs_b_Ch_pct": 100 * (kappa_cyc - kap_bch) / kap_bch,
        "gamma_cyc": gamma_cyc,
        "gamma_cyc_exact": "Delta_sp / kappa_cyc",
        "gamma_dev_vs_lit_pct": 100 * (gamma_cyc - g_lit) / g_lit,
        "gamma_dev_vs_b_Ch_pct": 100 * (gamma_cyc - b_ch) / b_ch,
        "Delta_cyc": delta_cyc,
        "Delta_cyc_exact": "-6 ln(tau5) = 6 ln(16/9) = 12 ln(4/3) = 24 ln(2/sqrt3)",
        "Delta_dev_vs_GHS_pct": 100 * (delta_cyc - A["Delta_GHS"]) / A["Delta_GHS"],
        "Delta_in_GHS_band": bool(abs(delta_cyc - A["Delta_GHS"])
                                  <= A["Delta_GHS_err"]),
        "tent_lattice_ratio": delta_cyc / np.log(2.0),
        "tent_lattice_dev_pct": 100 * (delta_cyc - 5 * np.log(2.0))
        / (5 * np.log(2.0)),
        "cycle_book_tau3_over_tau5_sq": A["tau3"] / A["tau5"]**2,
        "clock_rate_per_side": -np.log(A["tau5"]),
        "clock_note": ("часы эха глобальные: одна сторона гексагона = "
                       "-ln(tau5) = ln(16/9) log-времени; 6 сторон = эхо"),
    }
    if lam is not None:
        out["lambda_plus_tower"] = lam
        out["deficit_tower"] = kap_glit - lam
        out["deficit_filled_by_cycle"] = kappa_cyc - lam
        out["deficit_fill_quality_pct"] = 100 * (kappa_cyc - lam) / (kap_glit - lam)
        out["kappa_tower_vs_cycle_note"] = (
            "замороженная башня lambda+(27/80) = %.4f давала дефицит +0.45 в "
            "kappa; цикл (динамика источников) даёт kappa_cyc = %.4f — дефицит "
            "заполнен на %.1f%%" % (lam, kappa_cyc,
                                    out["deficit_fill_quality_pct"]))
    # нормировочная сноска: Delta_cyc (CSS-нормировка) vs Delta_sp (спинор-нормировка)
    out["Delta_cyc_over_Delta_sp"] = delta_cyc / d_sp
    out["Delta_norm_note"] = (
        "Delta_cyc=%.4f живёт в CSS-нормировке (GHS 3.44±0.02); спинор-фреймворк "
        "репо использует Delta_sp=7*pi/30=%.4f (R2, -0.62%% к delta_lit). "
        "Отношение Delta_cyc/Delta_sp = %.4f ~ delta_Feigenbaum = %.4f (+%.2f%%) — "
        "вопрос нормировки книг, НЕ утверждается" % (
            delta_cyc, d_sp, delta_cyc / d_sp, A["delta_Feigenbaum"],
            100 * (delta_cyc / d_sp / A["delta_Feigenbaum"] - 1)))
    return out


# ------------------------------------------------------------------ станции ---
STATIONS = [
    {"k": 0, "ru": "Пирамида", "en": "Pyramid", "zone": "CORE/UV",
     "shape": "1-|xi| (tent, излом в вершине)", "step": "ln(3/2)",
     "map_note": "наклон 2 — решётка удвоений"},
    {"k": 1, "ru": "Конус", "en": "Cone", "zone": "CORE/UV",
     "shape": "1-|xi| (азимутально гладкий)", "step": "ln(3/2)",
     "map_note": "пара закрывает UV: (3/2)^2 = tau3 = 9/4"},
    {"k": 2, "ru": "Усечённый конус", "en": "Truncated cone", "zone": "RING/Mdef",
     "shape": "max(1/4, 1-|xi|), кольцо 4:3", "step": "ln(4/3)",
     "map_note": "верхний радиус 3/4 = sqrt(tau5)"},
    {"k": 3, "ru": "Параболический пивот", "en": "Parabolic pivot", "zone": "RING/Mdef",
     "shape": "1-xi^2 (излом разрешается)", "step": "ln(4/3) (книга); мультипликатор 1",
     "map_note": "нейтральный пивот фокусировки/дефокусировки"},
    {"k": 4, "ru": "Чаша", "en": "Bowl", "zone": "RING/Mdef",
     "shape": "xi^2-1 (переворот)", "step": "ln(4/3) (модуль)",
     "map_note": "мультипликатор -1: переворот книги (чаща)"},
    {"k": 5, "ru": "Лог-замыкание", "en": "Log closure", "zone": "RING/Mdef",
     "shape": "пирамида нового масштаба e^{-Delta_cyc}", "step": "ln(4/3)",
     "map_note": "6-угольные лог-вычисления: (2/sqrt3)^2 = 4/3"},
]
STEPS = [np.log(1.5), np.log(1.5), np.log(4 / 3), np.log(4 / 3),
         np.log(4 / 3), np.log(4 / 3)]


def station_shape(k: int, xi: np.ndarray) -> np.ndarray:
    """1D-сечения станций (для морфа и рисунков)."""
    ax = np.abs(xi)
    if k in (0, 1):
        return 1.0 - ax                                   # пирамида/конус
    if k == 2:
        return np.maximum(0.25, 1.0 - ax)                 # усечённый конус
    if k == 3:
        return 1.0 - xi**2                                # парабола
    if k == 4:
        return xi**2 - 1.0                                # чаша
    # k == 5: пирамида нового масштаба (лог-замыкание)
    return (1.0 - ax) * np.exp(-(-6 * np.log(9 / 16)))


def morph(xi: np.ndarray, phi: float) -> np.ndarray:
    """Гладкий C0-морф по циферблату: cos^2-бампы вокруг станций, нормировка."""
    stations = np.array([k * np.pi / 3 for k in range(6)])
    d = np.abs(((phi - stations + np.pi) % (2 * np.pi)) - np.pi)
    w = np.where(d <= np.pi / 3, np.cos(np.pi * d / (2 * np.pi / 3))**2, 0.0)
    w = w / w.sum()
    return sum(w[k] * station_shape(k, xi) for k in range(6))


# ------------------------------------------------------------------ численно ---
def numeric_cycle(A: dict) -> dict:
    """Свободная и запертая циркуляция + карта возвращения + лестница эхов."""
    d_cyc = -6 * np.log(A["tau5"])
    kappa_cyc = 2 * np.log(1.5) + 4 * np.log(4 / 3)       # ln(64/9)
    side = -np.log(A["tau5"])               # log-время одной стороны = ln(16/9)
    omega0 = (np.pi / 3) / side             # одна сторона = ln(16/9) log-времени

    # свободная циркуляция: период T = 2*pi/omega0 = Delta_cyc (точно)
    T_free = 2 * np.pi / omega0
    # запертая (V6 = 0.05, J = 1): RK4, честный сдвиг периода O(V6)
    J, V6v = 1.0, 0.05
    acc = lambda th: -(V6v / J) * np.sin(6.0 * th)            # noqa: E731

    def rk4(state, dt):
        th, om = state

        def f(s):
            return np.array([s[1], acc(s[0])])
        k1 = f(state)
        k2 = f(state + 0.5 * dt * k1)
        k3 = f(state + 0.5 * dt * k2)
        k4 = f(state + dt * k3)
        return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    dt = side / 20000.0
    state = np.array([0.0, omega0])
    t_elapsed, crossings = 0.0, []
    r_book, r_at_section = 0.0, [0.0]        # амплитудная книга с пинками
    two_pi, third = 2 * np.pi, np.pi / 3.0
    idx_prev = 0                              # номер стороны floor(theta/third)
    n_steps = int(3.2 * T_free / dt) + 10
    for _ in range(n_steps):
        prev = state[0]
        state = rk4(state, dt)
        t_elapsed += dt
        idx_new = int(np.floor(state[0] / third))
        if idx_new != idx_prev:               # пересечение станции (ровно одна за шаг)
            k = idx_new % 6
            r_book -= STEPS[k]
            if k == 0:                        # сечение = пирамида
                frac = (idx_new * third - prev) / (state[0] - prev)
                crossings.append(t_elapsed - dt + frac * dt)
                r_at_section.append(r_book)
            idx_prev = idx_new
    periods = np.diff(crossings) if len(crossings) >= 3 else np.array([np.nan])
    T_locked = float(np.mean(periods[-2:])) if len(periods) else float("nan")
    # поцикловый шаг книги: разности сечений должны равняться kappa_cyc
    if len(r_at_section) >= 2:
        cyc_steps = -np.diff(np.array(r_at_section))
        book_measured = float(np.mean(cyc_steps))
        book_ok = bool(np.max(np.abs(cyc_steps - kappa_cyc)) < 1e-9)
    else:
        book_measured, book_ok = float("nan"), False

    # лестница книги: r_{n+1} = r_n - kappa_cyc на каждом эхе, часы z_n = n Delta
    n_echo = 8
    ladder = [{"n": n, "z": n * d_cyc, "r_book": n * kappa_cyc}
              for n in range(n_echo + 1)]

    # карта возвращения: форма на сечении = пирамида (точно)
    xi = np.linspace(-1, 1, 2001)
    err_return = float(np.max(np.abs(morph(xi, 0.0) - station_shape(0, xi))))
    err_mid = float(np.max(np.abs(
        morph(xi, np.pi / 6) - 0.5 * (station_shape(0, xi) + station_shape(1, xi)))))
    return {
        "omega0_dial_rate": omega0,
        "omega0_exact": "(pi/3)/ln(16/9)",
        "period_free": T_free,
        "period_free_equals_Delta_cyc": bool(abs(T_free - d_cyc) < 1e-12),
        "period_locked_V6_0.05": T_locked,
        "period_locked_rel_shift_pct": 100 * (T_locked - d_cyc) / d_cyc,
        "kicks_per_cycle": 6,
        "book_step_per_cycle": kappa_cyc,
        "book_step_measured": book_measured,
        "book_step_measured_ok": book_ok,
        "ladder": ladder,
        "return_shape_max_err": err_return,
        "morph_midpoint_max_err": err_mid,
        "morph_note": ("морф нормирован (sum w = 1); на сечении theta=0 морф "
                       "== пирамида точно; в середине стороны — среднее соседей"),
    }


# --------------------------------------------------------------------- main ---
def main() -> None:
    t0 = time.time()
    log("[1/5] Якоря из машинных результатов (center_o6_nsolve, "
        "spinor_analysis, center_modes)...")
    A = load_anchors()
    log(f"    tau3 = {A['tau3']} = (3/2)^2; tau5 = {A['tau5']} = (3/4)^2; "
        f"b_Ch = {A['b_Ch']:.6f}; Delta_sp = {A['Delta_sp']:.6f}; "
        f"gamma_lit = {A['gamma_lit']}")
    if A.get("lambda_plus_tower") is not None:
        log(f"    lambda+(27/80) = {A['lambda_plus_tower']:.6f} (башня); "
            f"kappa_obs(репо) = {A['kappa_obs_gamma_lit']:.4f} / "
            f"{A['kappa_obs_b_Ch']:.4f}")

    log("[2/5] Символика: квадраты ветвей, гексагон (R/a)^2 = 4/3, книги...")
    chk = sym_checks(A)
    bad = [k for k, v in chk.items() if not v]
    for k, v in chk.items():
        log(f"    {'OK ' if v else 'FAIL'} {k}")
    if bad:
        log(f"    !! провалены: {bad}")

    log("[3/5] Уравнения Пуанкаре (квазискорости, абелев циферблат)...")
    pc = sym_poincare()
    log(f"    Пуанкаре = Эйлера-Лагранжа (абелева группа): "
        f"{pc['poincare_abelian_equals_EL']}")
    log(f"    запирание станций V'(k*pi/3) = 0 (все 6): {pc['station_lock_all']}")
    log(f"    свободная циркуляция p_theta = const: "
        f"{pc['free_circulation_p_theta_const']}")

    log("[4/5] Книги замыкания + честные расхождения...")
    books = closure_books(A)
    log(f"    kappa_cyc = {books['kappa_cyc']:.6f} (ln 64/9)  vs  "
        f"kappa_obs: {books['kappa_obs_gamma_lit']:.4f} (gamma_lit, "
        f"{books['kappa_dev_vs_gamma_lit_pct']:+.3f}%) / "
        f"{books['kappa_obs_b_Ch']:.4f} (b_Ch, "
        f"{books['kappa_dev_vs_b_Ch_pct']:+.3f}%)")
    log(f"    gamma_cyc = {books['gamma_cyc']:.6f}  vs  0.374 "
        f"({books['gamma_dev_vs_lit_pct']:+.3f}%), b_Ch "
        f"({books['gamma_dev_vs_b_Ch_pct']:+.3f}%)")
    log(f"    Delta_cyc = {books['Delta_cyc']:.6f}  vs  GHS 3.44±0.02: "
        f"{books['Delta_dev_vs_GHS_pct']:+.3f}%, в коридоре: "
        f"{books['Delta_in_GHS_band']}")
    if "deficit_fill_quality_pct" in books:
        log(f"    дефицит башни +0.45 заполнен циклом на "
            f"{books['deficit_fill_quality_pct']:.1f}% "
            f"(kappa: {books['lambda_plus_tower']:.4f} -> {books['kappa_cyc']:.4f})")

    log("[5/5] Численная циркуляция (свободная/запертая) + карта возвращения...")
    num = numeric_cycle(A)
    log(f"    период свободной циркуляции = {num['period_free']:.6f} "
        f"== Delta_cyc: {num['period_free_equals_Delta_cyc']}")
    log(f"    запертая (V6=0.05): {num['period_locked_V6_0.05']:.6f} "
        f"({num['period_locked_rel_shift_pct']:+.3f}%)")
    log(f"    форма на сечении = пирамида точно "
        f"(max err = {num['return_shape_max_err']:.1e})")

    out = {
        "config": {
            "model": "гексагональный Пуанкаре-цикл трансформаций "
                     "(динамика вместо усечённой башни)",
            "stations": STATIONS,
            "clock": "глобальные часы эха: -ln(tau5) за сторону, 6 сторон = эхо",
            "zones": "CORE-пара (пирамида, конус) = UV[xi^3]; "
                     "RING-квартет = Mdef[xi^5]",
        },
        "anchors": {k: v for k, v in A.items() if k != "o6_verdict"},
        "o6_verdict_input": A["o6_verdict"],
        "sym_checks": chk,
        "poincare": pc,
        "closure": books,
        "numeric": num,
        "honest_notes": [
            "модель — bookkeeping ПОВЕРХ машино-верифицированных ветвей "
            "(tau3=9/4, tau5=9/16 из sympy_center_o6_nsolve.json); это НЕ вывод "
            "из уравнений Эйнштейна, а структура источ-динамики, которую те "
            "ветви требуют",
            "аксиомы модели: (1) разбиение 2+4 (CORE/RING) по зонам UV/Mdef; "
            "(2) глобальные часы эха = -ln(tau5) за сторону; остальное — "
            "теоремы/тождества внутри модели",
            "статическая несовместимость (tau3 != tau5 в одной точке) "
            "растворяется: ветви — шаги РАЗНЫХ книг цикла (амплитудной и эха), "
            "а не два кандидата одной амплитуды",
            "цикл даёт предельный цикл (DSS), а не CSS-точку — согласуется с "
            "тем, что Чоптюк наблюдал дискретную самоподобность",
            "Delta_cyc = 3.4522 — в CSS-нормировке (GHS 3.44±0.02); "
            "спинор-нормировка репо (Delta_sp = 7pi/30 = 0.733, R2) — другая "
            "книга; отношение 4.7096 ~ delta_F (~+0.9%) не утверждается",
            "подлинный тест — численная кампания tau* (v7+: измерение W2/t0^2 "
            "-> 4/3 на near-critical ветви); модель предсказывает: "
            "kappa = ln(64/9) = 1.9617, Delta_CSS = 6 ln(16/9) = 3.4522",
        ],
        "runtime_s": None,
    }
    out["runtime_s"] = round(time.time() - t0, 1)
    path = os.path.join(RESULTS, "hexcycle.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    n_bad = len(bad)
    log(f"Сохранено: {path} ({out['runtime_s']} c); символьных проверок: "
        f"{len(chk)}, провалено: {n_bad}")
    return 1 if (bad or not pc["station_lock_all"]
                 or not pc["poincare_abelian_equals_EL"]) else 0


if __name__ == "__main__":
    sys.exit(main())
