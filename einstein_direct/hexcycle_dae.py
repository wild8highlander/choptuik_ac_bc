#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания [сессия 20 / v16]: HEXCYCLE-DAE — маршрут через цикл фигур
(пирамида -> конус -> усечённый конус -> параболический пивот -> чаша ->
лог-замыкание), встроенный в нелинейную DAE башни.

Исходная ситуация (вердикт v15, машинные теоремы): локальный марш DAE около
критической точки невозможен АЛГЕБРАИЧЕСКИ — единственное многообразие решений
через x* есть плоская линия равновесий; обещанные следующие шаги: глобальные
компоненты S вдали от x*. Предложение автора (сессия 20): использовать сам
динамический геометрический цикл (sympy_hexcycle.py, гексагон на циферблате
формы) как ГЛОБАЛЬНЫЙ предиктор — маршрут по фигурам конечной амплитуды.

Вложение (аксиомы, все помечены; входы — машинные результаты, без подгонки):
  E1. АМПЛИТУДНАЯ КНИГА двигает масштаб T0h: шаг стороны e^{STEPS[k]}, пары
      закрывают ветви: (3/2)^2 = tau3 = 9/4 (CORE, UV[xi^3]),
      (4/3)^2 = 1/tau5 = 16/9 (RING, Mdef[xi^5]); полный цикл tau3/tau5^2
      = 64/9, kappa_cyc = ln(64/9) — всё из center_o6_nsolve/hexcycle.json.
      Станция k: T0h_k = T0h* * exp(-+r_k), r_k = sum_{j<k} STEPS[j mod 6]
      (коллапс: минус; обдув: плюс). Станция 0 (пирамида) = критический
      масштаб; станция k носит имя k mod 6.
  E2. Линейка R1h = 1 зафиксирована в ЧИСТОМ чтении книги; компенсация
      линейкой тестируется отдельно (скан/посадки) — плоская линия v15
      гуляет именно по R1h.
  E3. Амплитуды — ТОЧНЫЕ chain-формы v15 (D0h = 0 тождественно,
      R3h = 2 R1h T0h^2/9, W2h = 4 T0h^2/3, P2h = T0h/3, R5h, M5h, P4h);
      гомотетическая кинематика: tau = T0h^2, dT0h/dtau = 1/(2 T0h),
      потоки/dd — точное цепное правило по формам.

Слои теста (обе точки kappa = 2 и 2 - pi^2/98; коллапс и обдув):
  [T1] СТАТИЧЕСКИЙ СЛОЙ:
    (a) невязка F(chain(T0h_k, 1), 0, 0) на станциях — дефект книги;
    (b) полюс P4h (T0h^2 = 45/8): жёсткий барьер или мягкая дегенерация
        (мультистарт lstsq-Ньютон по амплитудам, T0h приколот к полюсу);
    (c) СТАТИЧЕСКИЕ ПОСАДКИ на приколотых масштабах книги: существует ли
        статическое решение при T0h = T0h_k (компенсация линейкой R1h и
        прочих амплитуд) — глобальная стрельба по-book;
    (d) скан компенсации: min по R1h статической невязки на масштабах
        станций 1..3 (ветвь 4T0h^2-27 v14 против компенсации).
  [T2] КИНЕТИЧЕСКИЙ СЛОЙ: гомотетические (v, dd) — дефекты динамических ур.,
       пролонгация (должна быть точной по построению), совместимость
       замыкания r(x), сравнение замыкания u с кинематикой 3-го порядка.
  [T3] ПОСАДКИ (глобальная стрельба, обещанная v15):
    (L1) свободный joint-Ньютон [F; r] из гомотетических станций;
    (L2) lstsq-Ньютон [F; r] с приколотым T0h_k (книга держит масштаб) —
         нижний этаж невязки.
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings

import numpy as np
import sympy as sp

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)
RESULTS = os.path.join(BASE, "results")
T_START = time.time()

import dae_nonlinear_core as dnc
from dae_nonlinear_core import NonlinearDAE, log
import sympy_hexcycle as hx


# ------------------------------------------------------------------ якоря ---
def load_anchors() -> dict:
    with open(os.path.join(RESULTS, "hexcycle.json"), encoding="utf-8") as fh:
        hxc = json.load(fh)
    a = {
        "stations": hx.STATIONS,
        "steps": [float(s) for s in hx.STEPS],
        "tau3": hxc["anchors"]["tau3"],
        "tau5": hxc["anchors"]["tau5"],
        "kappa_cyc": hxc["closure"]["kappa_cyc"],
        "Delta_cyc": hxc["closure"]["Delta_cyc"],
    }
    assert abs(a["kappa_cyc"] - np.log(64 / 9)) < 1e-12
    return a


# ----------------------------------------------------------- цепочка (симв.) --
def parse_chain(sysd):
    """chain_symbolic -> лямбда-формы и производные по T0h (до 3-го порядка)
    и по R1h (1-й порядок). {имя: {ключ: callable}}."""
    T0h, R1h = sp.symbols("T0h R1h")
    loc = {"T0h": T0h, "R1h": R1h}
    out = {}
    for name, s in sysd["chain_symbolic"].items():
        e = sp.sympify(s, locals=loc)
        eT = sp.diff(e, T0h)
        eTT = sp.diff(eT, T0h)
        eTTT = sp.diff(eTT, T0h)
        eR = sp.diff(e, R1h)
        out[name] = {
            "amp": sp.lambdify((T0h, R1h), e, "numpy"),
            "aT": sp.lambdify((T0h, R1h), eT, "numpy"),
            "aR": sp.lambdify((T0h, R1h), eR, "numpy"),
            "aTT": sp.lambdify((T0h, R1h), eTT, "numpy"),
            "aTTT": sp.lambdify((T0h, R1h), eTTT, "numpy"),
        }
    return out


def chain_poles(sysd):
    """Особые точки цепочки по T0h (знаменатели) + проверка на устранимость."""
    T0h, R1h = sp.symbols("T0h R1h")
    loc = {"T0h": T0h, "R1h": R1h}
    poles = []
    seen = set()
    for name, s in sysd["chain_symbolic"].items():
        e = sp.sympify(s, locals=loc)
        e = sp.cancel(sp.together(e))
        den = sp.denom(e)
        if den == 1 or den.is_number:
            continue
        for root in sp.nroots(den, n=25, maxsteps=200):
            if abs(sp.im(root)) < 1e-18:
                r = float(sp.re(root))
                key = round(abs(r), 12)
                if key in seen:
                    continue
                seen.add(key)
                num_at = complex(sp.numer(sp.together(e))
                                 .subs(T0h, complex(root)))
                poles.append({"amp": name, "T0h": abs(r),
                              "tau": r * r,
                              "numer_vanishes": bool(abs(num_at) < 1e-30)})
    return poles


# --------------------------------------------------------- состояния цикла --
def station_scales(t0_star, n_sides, direction):
    """T0h на станциях k=0..n_sides; direction=-1 коллапс, +1 обдув."""
    sign = -1.0 if direction < 0 else 1.0
    r = 0.0
    out = []
    for k in range(n_sides + 1):
        if k > 0:
            r += hx.STEPS[(k - 1) % 6]
        out.append({"k": k, "station": k % 6, "r_book": r,
                    "T0h": t0_star * float(np.exp(sign * r)),
                    "tau": t0_star**2 * float(np.exp(2 * sign * r))})
    return out


def make_state(chain, T0h_val, r1h=1.0, kinetic=False):
    """20-мерное состояние: амплитуды по цепочке; kinetic=True добавляет
    гомотетические (v, dd) — точное цепное правило (tau = T0h^2):
    vT = 1/(2 T0h), dvT/dtau = -1/(4 T0h^3), d2vT/dtau2 = 3/(8 T0h^5)."""
    def val(name, key):
        try:
            v = float(chain[name][key](T0h_val, r1h))
        except ZeroDivisionError:
            return np.nan
        return v

    a = np.zeros(9)
    a[0] = T0h_val
    a[1] = val("P2h", "amp")
    a[2] = 0.0                                   # D0h = 0 (тоождественно)
    a[3] = r1h
    for idx, name in ((4, "W2h"), (5, "R3h"), (6, "P4h"), (7, "R5h"),
                      (8, "M5h")):
        a[idx] = val(name, "amp")
    x = np.zeros(20)
    x[:9] = a
    if not np.all(np.isfinite(a)):
        return x
    if not kinetic:
        return x
    vT = 1.0 / (2.0 * T0h_val)
    dvT = -1.0 / (4.0 * T0h_val**3)
    x[9 + 0] = vT                                # dT0
    x[9 + 1] = 0.0                               # dD0
    x[9 + 2] = val("P2h", "aT") * vT             # Qh  (поток P2h)
    x[9 + 3] = 0.0                               # dR1
    x[9 + 4] = val("W2h", "aT") * vT             # dW2
    x[9 + 5] = val("R3h", "aT") * vT             # dR3
    x[9 + 6] = val("P4h", "aT") * vT             # dP4
    x[9 + 7] = val("R5h", "aT") * vT             # dR5
    for j, name in ((0, "W2h"), (1, "R3h"), (2, "P4h")):
        x[17 + j] = (val(name, "aTT") * vT**2 + val(name, "aT") * dvT)
    return x


def kinematic_third_order(chain, T0h_val, r1h=1.0):
    """Кинематические значения величин замыкания u (9):
    (M5h', dT0', dD0', Q', dR1', dR5', dddW2, dddR3, dddP4)."""
    vT = 1.0 / (2.0 * T0h_val)
    dvT = -1.0 / (4.0 * T0h_val**3)
    d2vT = 3.0 / (8.0 * T0h_val**5)

    def val(name, key):
        return float(chain[name][key](T0h_val, r1h))

    def d2(name):
        return val(name, "aTT") * vT**2 + val(name, "aT") * dvT

    def d3(name):
        return (val(name, "aTTT") * vT**3 + 3.0 * val(name, "aTT") * vT * dvT
                + val(name, "aT") * d2vT)

    return np.array([
        val("M5h", "aT") * vT,      # M5h'
        dvT,                        # dT0'  = d2(T0h)
        0.0,                        # dD0'  (D0h = 0)
        d2("P2h"),                  # Q'
        0.0,                        # dR1'
        d2("R5h"),                  # dR5'
        d3("W2h"), d3("R3h"), d3("P4h"),
    ])


# ---------------------------------------------------------------- дефекты --
def defect_rows(dae, chain, scales, kinetic, label):
    rows = []
    for rec in scales:
        x = make_state(chain, rec["T0h"], kinetic=kinetic)
        if not np.all(np.isfinite(x)):
            rows.append({**rec, "finite": False, "label": label})
            continue
        Fv = dae.eval_F(x)
        rv, _ = dae.rvec(x)
        wi = int(np.argmax(np.abs(Fv[:12])))
        row = {**rec, "finite": True, "label": label,
               "F_max": float(np.max(np.abs(Fv))),
               "F_max_static": float(np.max(np.abs(Fv[:12]))),
               "F_max_prolong": float(np.max(np.abs(Fv[12:]))),
               "worst_live_eq": wi,
               "r_max": float(np.max(np.abs(rv))),
               "norm_x": float(np.linalg.norm(x))}
        if kinetic:
            try:
                V, dia = dae.closure(x)
                u = np.array([V[8]] + [V[9 + fi] for fi in dnc.NEW_FLOWS]
                             + [V[17 + k] for k in range(3)])
                uk = kinematic_third_order(chain, rec["T0h"])
                row["closure_vs_kin_max"] = float(np.max(np.abs(u - uk)))
                row["closure_solv_res"] = dia["solv_res"]
            except dnc.BreakdownError as ex:
                row["closure_breakdown"] = str(ex)
        rows.append(row)
    return rows


# ----------------------------------------------------------------- посадки --
def static_landing(dae, chain, T0h_pin, iters=80):
    """Минимальная статическая коррекция книги: min-norm Ньютон на
    F(a, 0, 0) = 0 из ЧИСТО книжного старта (цепочка, R1h = 1);
    T0h приколот, D0h = 0. Fallback-старты по R1h, если primary stalls.
    Дегенератный угол (R1h -> 0: R3h = R5h = M5h = 0, полубашня
    аннигилирует) отбраковывается: degenerate = True."""
    a_book = make_state(chain, T0h_pin, r1h=1.0, kinetic=False)[:9].copy()
    if not np.all(np.isfinite(a_book)):
        return {"converged": False, "reason": "chain NaN (полюс)"}
    ref = float(np.linalg.norm(a_book))
    seeds = [1.0, 0.5, 0.1, 2.0, 10.0]
    rng = np.random.default_rng(13)
    seeds += [float(np.exp(rng.uniform(-2, 2))) for _ in range(6)]
    best = {"F_max": np.inf, "R1h": None, "a": None, "converged": False}
    for si, r1_0 in enumerate(seeds):
        a = a_book.copy()
        if si > 0:
            a[3] = r1_0
            a[5] = 2 * r1_0 * a[0] ** 2 / 9            # R3h согласована
            a[7] = 2 * r1_0 * a[0] ** 2 * (3 * a[0] ** 2 - 5) / 45
            a[8] = 2 * r1_0 * a[0] ** 2 * (23 - 6 * a[0] ** 2) / 9
        F0 = float(np.max(np.abs(dae.eval_F(np.concatenate([a, np.zeros(11)])))))
        loc = {"F_max": np.inf, "R1h": None, "a": None, "F_start": F0}
        for _ in range(iters):
            x = np.concatenate([a, np.zeros(11)])
            Fv = dae.eval_F(x)
            m = float(np.max(np.abs(Fv)))
            if m < loc["F_max"]:
                loc = {"F_max": m, "R1h": float(a[3]), "a": a.copy(),
                       "F_start": F0}
            if m < max(1e-12, 1e-12 * F0):
                break
            Dm = dae.eval_DF(x)[:, :9]
            da_, *_ = np.linalg.lstsq(Dm, -Fv, rcond=None)
            nrm = float(np.linalg.norm(da_))
            cap = 0.5 * ref
            if nrm > cap:
                da_ *= cap / nrm
            a = a + da_
            if not np.all(np.isfinite(a)):
                break
        degenerate = (abs(loc["R1h"]) < 0.05
                      or (loc["a"] is not None
                          and float(np.linalg.norm(loc["a"])) > 50 * ref))
        better = (loc["F_max"] < best["F_max"])
        if si == 0 or (better and not degenerate) or \
           (better and best.get("degenerate") and not degenerate):
            loc["degenerate"] = degenerate
            best = loc
        if loc["F_max"] < max(1e-12, 1e-12 * F0) and not degenerate:
            best = loc
            best["degenerate"] = False
            best["converged"] = True
            break
    out = dict(best)
    out["a"] = [float(v) for v in best["a"]] if best["a"] is not None else None
    out["converged"] = bool(out.get("converged")
                            or best["F_max"] < max(1e-12, 1e-10))
    out["dist_from_book"] = (float(np.linalg.norm(np.array(best["a"]) - a_book))
                             if best["a"] is not None else None)
    out["near_degenerate"] = bool(abs(best["R1h"]) < 0.2) if best["R1h"] is not None else None
    if best["a"] is not None:
        a_ch = make_state(chain, T0h_pin, r1h=best["R1h"], kinetic=False)[:9]
        fin = np.isfinite(a_ch)
        out["chain_dev_max"] = float(np.max(
            np.abs(np.array(best["a"])[fin] - a_ch[fin])
            / np.maximum(np.abs(a_ch[fin]), 1e-12)))
        # посадка в S? (v = dd = 0 => rhs = 0 => r = 0 тривиально; проверяем)
        x_land = np.concatenate([np.array(best["a"], dtype=float),
                                 np.zeros(11)])
        rv, _ = dae.rvec(x_land)
        out["r_max_at_landing"] = float(np.max(np.abs(rv)))
        f_tol = max(1e-9, 1e-12 * (out.get("F_start") or 1.0))
        out["in_S"] = bool(out["r_max_at_landing"] < 1e-9
                           and best["F_max"] < f_tol)
        # локальная размерность статического множества (T0h приколот: 8 свободно)
        Dm = dae.eval_DF(x_land)[:, :9]
        sv = np.linalg.svd(Dm, compute_uv=False)
        rk = int(np.sum(sv > sv[0] * 1e-10))
        out["static_rank"] = rk
        out["static_dim_pinned"] = 8 - rk
    return out


def r1h_compensation_scan(dae, chain, T0h_pin, n=41):
    """min по R1h статической невязки при приколотом T0h (лог-сетка)."""
    grid = np.geomspace(1e-4, 1e2, n)
    vals = []
    for r1 in grid:
        x = make_state(chain, T0h_pin, r1h=float(r1), kinetic=False)
        if not np.all(np.isfinite(x)):
            vals.append(np.nan)
            continue
        vals.append(float(np.max(np.abs(dae.eval_F(x)))))
    vals = np.array(vals)
    im = int(np.nanargmin(vals))
    return {"T0h": T0h_pin, "R1h_grid": [float(g) for g in grid],
            "F_max_grid": [float(v) for v in vals],
            "min_F_max": float(vals[im]), "R1h_at_min": float(grid[im])}


def landing_free(dae, x0, iters=30, tol=1e-11):
    """L1: свободный joint-Ньютон [F; r] (dnc.joint_newton) + диагностика."""
    try:
        xl, gmax, used = dae.joint_newton(x0, iters=iters, tol=tol)
    except dnc.BreakdownError as ex:
        return {"converged": False, "breakdown": str(ex)}
    out = {"converged": bool(gmax < tol), "g_max": float(gmax),
           "iters": int(used), "dist_from_start": float(np.linalg.norm(xl - x0)),
           "dT0h": float(xl[0] - x0[0]), "T0h_land": float(xl[0])}
    try:
        V, dia = dae.closure(xl)
        Vn = float(np.linalg.norm(V))
        out["V_norm"] = Vn
        out["closure_solv_res"] = dia["solv_res"]
        if Vn > 1e-10:
            # v15 exit-тест: производная r-вектора вдоль потока
            h = 1e-7 * max(1.0, float(np.linalg.norm(xl)))
            rp, _ = dae.rvec(xl + h * V)
            rm, _ = dae.rvec(xl)
            out["exit_rate"] = float(np.linalg.norm(rp - rm) / h)
    except dnc.BreakdownError as ex:
        out["V_norm"] = None
        out["closure_breakdown"] = str(ex)
    return out


def landing_pinned(dae, x0, iters=30):
    """L2: lstsq-Ньютон на [F; r] с приколотым T0h (книга держит масштаб)."""
    x = x0.copy()
    floor = np.inf
    for _ in range(iters):
        Fv = dae.eval_F(x)
        rv, _ = dae.rvec(x)
        G = np.concatenate([Fv, rv])
        floor = min(floor, float(np.max(np.abs(G))))
        if float(np.max(np.abs(G))) < 1e-12:
            break
        Dm = dae.eval_DF(x)
        Dr, _ = dae._r_jacobian(x)
        J = np.vstack([Dm, Dr])
        dx, *_ = np.linalg.lstsq(J, -G, rcond=None)
        dx[0] = 0.0                                 # T0h приколот книгой
        nrm = float(np.linalg.norm(dx))
        if nrm > 2.0 * dae.scale:
            dx *= 2.0 * dae.scale / nrm
        x = x + dx
        if not np.all(np.isfinite(x)):
            break
    Fv = dae.eval_F(x)
    rv, _ = dae.rvec(x)
    G = np.concatenate([Fv, rv])
    return {"floor_G_max": float(floor),
            "final_G_max": float(np.max(np.abs(G))),
            "final_F_max": float(np.max(np.abs(Fv))),
            "final_r_max": float(np.max(np.abs(rv))),
            "dist_from_start": float(np.linalg.norm(x - x0))}


def pole_barrier_test(sysd, dae, chain, T0h_pole, n_starts=8, iters=60):
    """Полюс цепочки: жёсткий барьер или мягкая дегенерация?

    Мультистарт lstsq-Ньютон по 9 амплитудам (v = dd = 0, T0h приколот к
    полюсу) на F(a, 0, 0) = 0. min невязка ~ 0 => мягкая (ветвь проходит);
    min невязка O(1) => жёсткий барьер книги.
    """
    rng = np.random.default_rng(11)
    starts = []
    for eps in (-1e-3, 1e-3):
        starts.append(make_state(chain, T0h_pole * (1.0 + eps),
                                 kinetic=False)[:9])
    for _ in range(n_starts):
        st = make_state(chain, T0h_pole * (1.0 + 1e-6), kinetic=False)[:9]
        st[1:] += 0.3 * rng.normal(size=8) * max(1.0, abs(T0h_pole))
        starts.append(st)
    best = np.inf
    for a0 in starts:
        a = a0.copy()
        for _ in range(iters):
            x = np.concatenate([a, np.zeros(11)])
            if not np.all(np.isfinite(x)):
                break
            Fv = dae.eval_F(x)
            m = float(np.max(np.abs(Fv)))
            best = min(best, m)
            if m < 1e-13:
                break
            Dm = dae.eval_DF(x)[:, :9]
            da_, *_ = np.linalg.lstsq(Dm, -Fv, rcond=None)
            nrm = float(np.linalg.norm(da_))
            if nrm > 2.0 * dae.scale:
                da_ *= 2.0 * dae.scale / nrm
            a = a + da_
    return {"min_F_max": float(best),
            "hard_barrier": bool(best > 1e-8)}


# ------------------------------------------------------------ кампания точки --
def campaign_point(kv, label):
    out = {"label": label, "kappa": float(sp.N(kv, 15))}
    log(f"\n================ {label}: kappa = {out['kappa']:.9f} ================")
    sysd = dnc.build_nonlinear_system(kv, validate=False)
    chain = parse_chain(sysd)
    dae = NonlinearDAE(sysd)
    t0s = float(sysd["x_star"][0])
    out["T0h_star"] = t0s
    out["tau_star"] = float(sysd["tau_star"])
    out["residual_at_point"] = sysd["residual_at_point"]
    log(f"  [N0] F(x*) = {sysd['residual_at_point']:.2e}; "
        f"T0h* = {t0s:.6f} (tau* = {out['tau_star']:.5f})")

    # --- якорь: станция 0 = x*
    x0 = make_state(chain, t0s, kinetic=False)
    out["station0_is_x_star"] = float(np.max(np.abs(x0[:9] - sysd["x_star"][:9])))
    F0 = float(np.max(np.abs(dae.eval_F(x0))))
    out["station0_F_max"] = F0
    log(f"  [V0] станция 0 == x*: разл. {out['station0_is_x_star']:.2e}, "
        f"F = {F0:.2e}")

    # --- [T1a] статический слой по циклу (коллапс 2 цикла, обдув 1 цикл)
    for tag, ndir, nsides in (("collapse", -1, 12), ("blowup", 1, 6)):
        scales = station_scales(t0s, nsides, ndir)
        rows = defect_rows(dae, chain, scales, kinetic=False,
                           label=f"static_{tag}")
        ok_rows = [r for r in rows if r.get("finite")]
        fmax = max(r["F_max"] for r in ok_rows)
        st0 = [r for r in ok_rows if r["k"] == 0][0]
        out[f"T1_static_{tag}"] = {"rows": rows, "F_max": fmax,
                                   "F_max_station0": st0["F_max"]}
        log(f"  [T1a] статический слой {tag}: {len(ok_rows)} станций, "
            f"F_max = {fmax:.3e} (станция 0: {st0['F_max']:.2e}); худшие ур.: "
            f"{sorted(set(r['worst_live_eq'] for r in ok_rows))}")

    # --- [T1b] полюса цепочки + барьер-тесты
    poles = chain_poles(sysd)
    out["chain_poles"] = poles
    for p in poles:
        log(f"  [T1b] полюс {p['amp']}: T0h = {p['T0h']:.6f} "
            f"(tau = {p['tau']:.5f}), числитель "
            f"{'нулев (устраним)' if p['numer_vanishes'] else 'НЕ нулевой'}")
    barriers = []
    for p in poles:
        if not p["numer_vanishes"] and 0.2 * t0s < p["T0h"] < 3.0 * t0s:
            bt = pole_barrier_test(sysd, dae, chain, p["T0h"])
            bt.update({"amp": p["amp"], "T0h": p["T0h"], "tau": p["tau"]})
            barriers.append(bt)
            log(f"  [T1b] барьер-тест на полюсе {p['amp']}: min F = "
                f"{bt['min_F_max']:.3e} -> "
                f"{'ЖЁСТКИЙ барьер' if bt['hard_barrier'] else 'мягкая дегенерация'}")
    out["pole_barriers"] = barriers

    # --- [T1c] статические посадки (минимальная коррекция книги) на каждой
    #     станции: кривая запертой линейки R1h(k); периодичность по циклам
    walks = {}
    for tag, ndir, nsides in (("collapse", -1, 12), ("blowup", 1, 6)):
        w = {}
        for rec in station_scales(t0s, nsides, ndir):
            if rec["k"] == 0:
                continue                       # станция 0 = x*
            sl = static_landing(dae, chain, rec["T0h"])
            sl["station"] = rec["station"]
            sl["T0h"] = rec["T0h"]
            w[f"k{rec['k']}"] = sl
        walks[tag] = w
        okk = [(kk, v) for kk, v in w.items()
               if v.get("converged") and not v.get("degenerate")]
        ruler = [round(v["R1h"], 4) for _, v in okk]
        nS = sum(1 for _, v in okk if v.get("in_S"))
        ndn = sum(1 for _, v in okk if v.get("near_degenerate"))
        log(f"  [T1c] {tag}: компенсированных станций {len(okk)}/{len(w)} "
            f"(дегенерат отбракован); R1h(k) = {ruler}; в S: {nS}, "
            f"близко-к-дегенерату: {ndn}")
        if okk:
            cd = [v.get("chain_dev_max") for _, v in okk
                  if v.get("chain_dev_max") is not None]
            if cd:
                log(f"        chain_dev_max = {max(cd):.3e}")
    # периодичность компенсированной книги: |R1h(k+6) - R1h(k)|
    wc = walks.get("collapse", {})
    per = []
    for k in range(1, 7):
        a_, b_ = wc.get(f"k{k}", {}), wc.get(f"k{k+6}", {})
        if a_.get("converged") and b_.get("converged") and \
           not a_.get("degenerate") and not b_.get("degenerate"):
            per.append(abs(b_["R1h"] - a_["R1h"]))
    if per:
        out["ruler_periodicity_max"] = float(max(per))
        log(f"  [T1c] периодичность линейки max|R1h(k+6)-R1h(k)| = "
            f"{max(per):.4f}")
    if wc.get("k6", {}).get("converged") and not wc["k6"].get("degenerate"):
        out["delta_R1h_one_cycle"] = abs(wc["k6"]["R1h"] - 1.0)
    out["T1c_ruler_walk"] = walks

    # --- [T1d] скан компенсации R1h на масштабах станций 1..3 (коллапс)
    comp = {}
    for rec in scales[1:4]:
        if any(abs(rec["T0h"] - p["T0h"]) < 1e-6 for p in poles):
            continue
        cs = r1h_compensation_scan(dae, chain, rec["T0h"])
        comp[f"k{rec['k']}"] = cs
        log(f"  [T1d] компенсация R1h при T0h = {rec['T0h']:.4f}: "
            f"min F = {cs['min_F_max']:.3e} при R1h = {cs['R1h_at_min']:.4g}")
    out["T1d_r1h_compensation"] = comp

    # --- [T2] кинетический слой (первый цикл, оба направления)
    kin = {}
    for tag, ndir, nsides in (("collapse", -1, 6), ("blowup", 1, 6)):
        scales_k = station_scales(t0s, nsides, ndir)
        rows = defect_rows(dae, chain, scales_k, kinetic=True,
                           label=f"kin_{tag}")
        ok_rows = [r for r in rows if r.get("finite")]
        kin[tag] = {"rows": rows}
        if ok_rows:
            kin[tag]["F_max"] = max(r["F_max"] for r in ok_rows)
            kin[tag]["r_max"] = max(r["r_max"] for r in ok_rows)
            kin[tag]["prolong_max"] = max(r["F_max_prolong"] for r in ok_rows)
            cvs = [r["closure_vs_kin_max"] for r in ok_rows
                   if "closure_vs_kin_max" in r]
            kin[tag]["closure_vs_kin_max"] = max(cvs) if cvs else None
            n_brk = sum(1 for r in ok_rows if "closure_breakdown" in r)
            kin[tag]["closure_breakdowns"] = n_brk
            log(f"  [T2] кинетический слой {tag}: F_max = "
                f"{kin[tag]['F_max']:.3e}, r_max = {kin[tag]['r_max']:.3e}, "
                f"пролонгация = {kin[tag]['prolong_max']:.3e}, "
                f"замыкание-vs-кинематика = "
                f"{kin[tag]['closure_vs_kin_max']}, срывов: {n_brk}")
    out["T2_kinetic"] = kin
    r_vals = [r["r_max"] for r in kin["collapse"]["rows"] if r.get("finite")]
    out["delta_kin_collapse_cycle"] = float(np.mean(r_vals)) if r_vals else None

    # --- [T3] посадки L1/L2 (первый цикл, оба направления)
    land = {}
    for tag, ndir, nsides in (("collapse", -1, 6), ("blowup", 1, 6)):
        scales_l = station_scales(t0s, nsides, ndir)
        l1, l2 = {}, {}
        for rec in scales_l[1:]:                 # станция 0 = x*
            xh = make_state(chain, rec["T0h"], kinetic=True)
            if not np.all(np.isfinite(xh)):
                continue
            l1[f"k{rec['k']}"] = landing_free(dae, xh)
            l2[f"k{rec['k']}"] = landing_pinned(dae, xh)
        land[tag] = {"L1_free": l1, "L2_pinned": l2}
        conv = [v for v in l1.values() if v.get("converged")]
        fl = max(v["floor_G_max"] for v in l2.values())
        log(f"  [T3] посадки {tag}: L1 сошлись {len(conv)}/{len(l1)}; "
            f"L2 нижний этаж max = {fl:.3e}")
        for kk_, v_ in l1.items():
            if v_.get("converged"):
                log(f"       L1 {kk_}: {v_['iters']} итер., |G| = "
                    f"{v_['g_max']:.2e}, dT0h = {v_['dT0h']:.4g}, "
                    f"|V| = {v_.get('V_norm')}, exit_rate = "
                    f"{v_.get('exit_rate')}")
    out["T3_landings"] = land
    return out


# --------------------------------------------------------------------- main --
def main() -> None:
    log("[1/3] Якоря гексцикла (hexcycle.json: tau3, tau5, STEPS, книги)...")
    A = load_anchors()
    log(f"    станции: {[s['en'] for s in A['stations']]}; "
        f"kappa_cyc = {A['kappa_cyc']:.6f}, Delta_cyc = {A['Delta_cyc']:.4f}")

    log("[2/3] Кампания в двух точках (kappa = 2; 2 - pi^2/98)...")
    points = {
        "baseline_kappa2": campaign_point(sp.Integer(2), "baseline_kappa2"),
        "one_brick_2-bC": campaign_point(
            sp.Integer(2) - sp.pi**2 / sp.Integer(98), "one_brick_2-bC"),
    }

    log("[3/3] Вердикт...")
    v = []
    st = max(p["T1_static_" + t]["F_max"]
             for p in points.values() for t in ("collapse", "blowup"))
    st0 = max(p["T1_static_" + t]["F_max_station0"]
              for p in points.values() for t in ("collapse", "blowup"))
    v.append(f"статический слой: F_max по циклу = {st:.3e} "
             f"(станция 0 = x*: {st0:.2e}) — амплитудная книга НЕ точна "
             f"статически вне критического масштаба"
             if st > 1e-9 else
             f"статический слой точен: F_max = {st:.2e}")
    hard = [b for p in points.values() for b in p.get("pole_barriers", [])
            if b["hard_barrier"]]
    v.append(f"полюс P4h (T0h^2 = 45/8, tau = 5.625): "
             f"{'ЖЁСТКИЙ барьер' if hard else 'мягкая дегенерация — ветвь проходит'}")
    for p in points.values():
        for tag, w in p["T1c_ruler_walk"].items():
            okk = [x_ for x_ in w.values()
                   if x_.get("converged") and not x_.get("degenerate")]
            v.append(f"компенсированная книга ({tag}): "
                     f"{len(okk)}/{len(w)} станций (мин. коррекция, "
                     f"дегенерат отбракован), R1h: "
                     f"{[round(x_['R1h'], 3) for x_ in okk]}")
    nS = sum(1 for p in points.values() for t in ("collapse", "blowup")
             for x_ in p["T1c_ruler_walk"][t].values()
             if x_.get("in_S") and not x_.get("degenerate"))
    dims = [x_["static_dim_pinned"] for p in points.values()
            for t in ("collapse", "blowup")
            for x_ in p["T1c_ruler_walk"][t].values()
            if x_.get("in_S")]
    if nS:
        v.append(f"компенсированные состояния лежат в S (F = r = 0): "
                 f"{nS} точек — ГЛОБАЛЬНЫЕ СТАТИЧЕСКИЕ КОМПОНЕНТЫ S найдены "
                 f"(ответ на оговорку v15); dim стат. множества при "
                 f"приколотом T0h = {sorted(set(dims))}")
    d1 = [p.get("delta_R1h_one_cycle") for p in points.values()
          if p.get("delta_R1h_one_cycle") is not None]
    per = [p.get("ruler_periodicity_max") for p in points.values()
           if p.get("ruler_periodicity_max") is not None]
    if d1:
        v.append(f"дефект возврата линейки: delta_R1h = {d1[0]:.4f} (1 цикл)"
                 + (f"; периодичность max|R1h(k+6)-R1h(k)| = {per[0]:.4f}"
                    if per else ""))
    exits = [x_.get("exit_rate") for p in points.values()
             for t in ("collapse", "blowup")
             for x_ in p["T3_landings"][t]["L1_free"].values()
             if x_.get("exit_rate") is not None]
    if exits:
        v.append(f"L1-посадки с |V| != 0: exit_rate = "
                 f"{min(exits):.3e}..{max(exits):.3e} — поток покидает S "
                 f"(v15-вердикт глобально)")
    kk = max(p["T2_kinetic"][t].get("r_max", 0.0)
             for p in points.values() for t in ("collapse", "blowup"))
    v.append(f"кинетический слой: r_max = {kk:.3e} — замыкание несовместимо "
             f"с гомотетической ходьбой" if kk > 1e-8 else
             f"кинетический слой: r_max = {kk:.3e} (совместимо!)")
    conv = sum(1 for p in points.values() for t in ("collapse", "blowup")
               for x_ in p["T3_landings"][t]["L1_free"].values()
               if x_.get("converged"))
    tot = sum(1 for p in points.values() for t in ("collapse", "blowup")
              for x_ in p["T3_landings"][t]["L1_free"].values())
    v.append(f"посадки L1 (глобальная стрельба): {conv}/{tot} сошлись")
    for line in v:
        log(f"    - {line}")

    out = {
        "title": "HEXCYCLE-DAE v16: цикл фигур (пирамида->конус->чаша) как "
                 "глобальный предиктор нелинейной DAE башни",
        "question": ("v15: локальный марш невозможен, S через x* = плоская "
                     "линия; сессия 20: несёт ли цикл фигур глобальные "
                     "компоненты S (стрельба по станциям конечной амплитуды)"),
        "embedding_axioms": [
            "E1: T0h_k = T0h* exp(-+r_k), r_k = sum STEPS; пары (3/2)^2 = tau3, "
            "(4/3)^2 = 1/tau5; станция 0 (пирамида) = критический масштаб",
            "E2: чистое чтение — R1h = 1; компенсация линейкой тестируется "
            "отдельно (T1c/T1d)",
            "E3: амплитуды = точные chain-формы v15 (D0h = 0); гомотетическая "
            "кинематика vT = 1/(2 T0h) — пролонгация по построению",
        ],
        "anchors": {k: A[k] for k in ("tau3", "tau5", "kappa_cyc", "Delta_cyc")},
        "points": points,
        "verdict_lines": v,
        "honest_notes": [
            "цикл входит через свои КНИГИ (шаги/зоны/станции — машинные "
            "якоря tau3, tau5); профили фигур (тент/парабола/чаша) остаются "
            "слоем-визуализацией модели",
            "E1-E3 — аксиомы вложения; альтернативные прочтения книги "
            "(неэкспоненциальный шаг, гуляющая R1h как часть книги) "
            "тестируются только сканом/посадками",
            "посадки — локальный анализ Ньютоном; глобальные компоненты S "
            "вдали от всех стартов не исключаются",
            "полюс P4h — свойство РЕШЁННОЙ ветви цепочки; прыжок ветви "
            "(Пюизо-тип) не исключён, барьер-тест мультистартовый",
            "жёсткость — свойство усечённой башни; PDE-машина v6-v9 остаётся "
            "носителем физики эха",
        ],
        "runtime_s": None,
    }
    out["runtime_s"] = round(time.time() - T_START, 1)
    path = os.path.join(RESULTS, "hexcycle_dae.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    log(f"Сохранено: {path} ({out['runtime_s']} c)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
