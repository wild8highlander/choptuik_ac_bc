#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
СПИНОР-АНАЛИЗ DSS: ПОКАЗАТЕЛИ pi/15 И pi/30, СКЭЛЛИНГ ПАРАМЕТРОВ (v4)
SPINOR ANALYSIS OF DSS: THE pi/15 AND pi/30 EXPONENTS, PARAMETER SCALING
================================================================================

Фундаментальный уровень (указание автора монографии): весь путь цепочки эхо
проходят СПИНОРНЫЕ ФУНКЦИИ с показателями pi/15 и pi/30 со скэллингом
параметров. Взрывы (распады/сборки) обязаны происходить — это частные
(критические) случаи уравнений Эйнштейна; точные значения есть не у всех
решений. Процентная gamma грубым зумом без фундаментального замыкания НЕ
достигается — подтверждено стеной глубины z ~ 3-5 (диагноз v3, README §8-9).

ЧТО ДЕЛАЕТ МОДУЛЬ
-----------------
1. Формализует спинорную (Z2-зеркальную) структуру регулярного центра:
   зеркало (u,v)->(v,u): r -> -r, s <-> t, p <-> -q, c <-> d.
   Регулярное разложение = разложение по чётности относительно зеркала:
     E = (t+s)/2 — чётная ("скалярная") часть, E = t0 + E2 x^2 + ...
     O = (t-s)/2 — нечётная ("спинорная") часть, O = a x + O(x^3),
   связка наклонов s1 - t1 = -2a. Клэмп t=s (v2) насильно обнуляет
   спинорный сектор — причина стены глубины. Численная проверка парностей
   на слабопольном забеге входит в модуль (verify_mirror_parity).

2. Точные соотношения фреймворка (framework relations) и их расхождения
   с литературой — таблица в JSON:
     (R1) gamma = b_Ch = 1 - cos(2*pi/7) = 0.376510   [gamma_lit = 0.374]
     (R2) Delta = 7*pi/30              = 0.733038     [Delta_lit  = 0.737637]
     (R3) omega_wiggle = 4*pi/Delta = 120/7 = 17.142857 (рациональное!)
                                                       [4*pi/Delta_lit=17.0165]
     (R4) произведение gamma*Delta: 0.376510*0.733038 = 0.275993
          против gamma_lit*Delta_lit = 0.374*0.737637 = 0.275876 -> 0.04%
          (расхождения R1 и R2 почти компенсируются в произведении)
   Спинорные фазы на эхо: phi15 = pi*Delta/15, phi30 = pi*Delta/30.

3. Дельта-оценка из зум-забегов: пики кривизны Q(v) сходятся к точке
   накопления v* геометрически, v* - v_n ~ exp(-n*Delta); совместный фит
   (v*, Delta) по последовательности пиков (fit_delta_geometric).

4. Скэллинг параметров: рост амплитуд пиков ln Q_n ~ kappa * zeta_n
   (screaming-мода, литература kappa ~ 2.87) — оценка kappa из данных.

5. Честные пределы данных: частоты pi/15, pi/30 в log-переменной дзета
   дают модуляции с периодами 30 и 60 по дзета (~40-80 эхо). Наши данные
   покрывают z ~ 3-5 (2-7 эхо) — на 1.5 порядка меньше необходимого.
   Разрешение спинорной модуляции = цель v5 (цепочка z >= 30).

Запуск:  python3 spinor_analysis.py        # ~3-5 мин (2 зум-забега)
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from zoom_solver import ZoomRunner, echo_peaks, RESULTS, V_P, SIGMA

A_FIXED_GRID = 0.0805333
GAMMA_LIT = 0.374
DELTA_LIT = 0.737637          # Choptuik 1993; Gundlach 2007 (review)
KAPPA_LIT = 2.87              # растущая (screaming) мода возмущений
B_CH = 1.0 - np.cos(2.0 * np.pi / 7.0)
DELTA_SP = 7.0 * np.pi / 30.0
PI_15 = np.pi / 15.0
PI_30 = np.pi / 30.0

OUT_PATH = os.path.join(RESULTS, "spinor_analysis.json")


# ------------------------------------------------------------------------------
# 1. Численная проверка спинорных (зеркальных) парностей регулярного центра
# ------------------------------------------------------------------------------
def verify_mirror_parity(A=0.075, n=500, v_probe=0.55, closure="clamp"):
    """Проверка Z2-парностей на сильном подкритическом забеге (сжатие).

    Проба ВО ВРЕМЯ прохождения импульса через центр (v ~ 0.55), кольцо
    k = 1..16 клеток. Зеркало (u,v)->(v,u): s(-r)=t(+r), t(-r)=s(+r)
    (скалярное поле чётно по x=(v-u)/2); p(-r)=-q(+r); (p+q) нечётно;
    m нечётно (m~r^3). closure="clamp" (v2) или "regular" (v3) — A/B
    сравнение действия замыканий центра на спинорный сектор.
    """
    from solver import DoubleNullSolver, GaussianPulseData, SolverConfig
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                       monitor_every=10 ** 9)
    sol = DoubleNullSolver(cfg, data)
    sol.center_closure = closure
    sol.reg_m_rebuild = closure == "regular"
    sol.reg_pq_project = closure == "regular"
    sol.heal_enabled = closure != "regular"
    st = {k: getattr(sol, k).copy() for k in
          ("r", "Phi", "p", "q", "s", "t", "c", "m", "alpha2", "d", "w")}
    j = 1
    with np.errstate(all="ignore"):
        while sol.v[j] < v_probe and j < n - 1:
            j += 1
            st = sol._do_step(st, j)
    r, s, t, p, q, m = (st["r"], st["s"], st["t"], st["p"], st["q"], st["m"])
    du = sol.du
    i0 = int(np.argmin(np.abs(r)))

    def ring_viol(k_lo, k_hi):
        ks = np.arange(k_lo, k_hi + 1)
        ip, im = i0 - ks, i0 + ks
        ts_scale = max(float(np.max(np.abs(t[ip]) + np.abs(s[ip]))), 1e-300)
        pq_scale = max(float(np.max(np.abs(p[ip]) + np.abs(q[ip]))), 1e-300)
        m_scale = max(float(np.max(np.abs(m[ip]))), 1e-300)
        st_v = float(np.max(np.abs(s[im] - t[ip]))) / ts_scale
        Sp, Sm = p[ip] + q[ip], p[im] + q[im]
        pq_even = float(np.max(np.abs(0.5 * (Sp + Sm)))) / max(
            float(np.max(np.abs(Sp))), 1e-300)
        m_v = float(np.max(np.abs(m[im] + m[ip]))) / m_scale
        return {"s_t": st_v, "pq_even": pq_even, "m_odd": m_v,
                "abs_scale_t_s": ts_scale, "abs_scale_m": m_scale}

    Kmax = min(16, i0, len(r) - 1 - i0)
    K_in = min(6, Kmax)
    inner = ring_viol(1, K_in) if K_in >= 1 else None
    outer = ring_viol(K_in + 2, Kmax) if Kmax >= K_in + 3 else None
    return {
        "closure": closure,
        "A": A, "n": n, "v_probe": float(sol.v[j]),
        "du": float(du), "cells_inner": int(K_in), "cells_outer": int(Kmax),
        "inner_ring": inner,
        "outer_ring": outer,
        "note": ("Z2-зеркальные парности: inner_ring (k<=6, зона "
                 "реконструкции) и outer_ring (сырой марш). Спинорный "
                 "сектор = нечётная часть (t-s)/2 и нечётность (p+q), m; "
                 "чётная добавка p+q даёт источник s_v = E*(p+q)/r — "
                 "механизм взрыва при сжатии"),
    }


# ------------------------------------------------------------------------------
# 2. Дельта: совместный фит (v*, Delta) по геометрической сходимости пиков
# ------------------------------------------------------------------------------
def fit_delta_geometric(v_peaks, v_star_scan=None):
    """v_n -> v*: v* - v_n ~ exp(-n*Delta). Минимизируем по v* скалярно,
    при фиксированном v* фит линеен: ln(v*-v_n) = c - n*Delta.

    Возвращает dict(Delta, Delta_err, v_star, n_peaks, rms) или None.
    """
    vp = np.asarray(sorted(v_peaks), dtype=float)
    if len(vp) < 4:
        return None
    dv = np.diff(vp)
    if np.any(dv <= 0):
        return None
    # геометрическая состоятельность: интервалы поезда должны УБЫВАТЬ
    # в среднем (сходимость к v*); растущие интервалы — не поезд эхо
    if not (dv[-1] < dv[0]):
        return None
    v_last = vp[-1]
    if v_star_scan is None:
        # v* выше последнего пика; шаг = последний интервал
        v_star_scan = np.linspace(v_last + 0.05 * dv[-1],
                                  v_last + 20 * dv[-1], 400)
    n = np.arange(len(vp))
    best = None
    for vs in v_star_scan:
        y = np.log(vs - vp)
        Amat = np.vstack([n, np.ones_like(n)]).T
        sol, *_ = np.linalg.lstsq(Amat, y, rcond=None)
        resid = y - Amat @ sol
        rms = float(np.sqrt((resid ** 2).mean()))
        if best is None or rms < best["rms"]:
            best = {"rms": rms, "Delta": float(-sol[0]),
                    "v_star": float(vs), "c": float(sol[1])}
    if best is None or not np.isfinite(best["Delta"]):
        return None
    # stderr наклона
    y = np.log(best["v_star"] - vp)
    Amat = np.vstack([n, np.ones_like(n)]).T
    resid = y - Amat @ np.array([best["Delta"] * -1, best["c"]])
    dof = max(len(vp) - 2, 1)
    s2 = float((resid ** 2).sum()) / dof
    cov = s2 * np.linalg.inv(Amat.T @ Amat)
    best["Delta_err"] = float(np.sqrt(max(cov[0, 0], 0.0)))
    best["n_peaks"] = int(len(vp))
    return best


def kappa_from_peaks(v_peaks, q_peaks, v_star):
    """Скэллинг амплитуд: ln Q_n = c + kappa*zeta_n, zeta_n = -ln(v*-v_n).

    Возвращает (kappa, kappa_err, n) или None.
    """
    vp = np.asarray(v_peaks, float)
    qp = np.asarray(q_peaks, float)
    ok = np.isfinite(qp) & (qp > 0) & (vp < v_star)
    if int(ok.sum()) < 3:
        return None
    vp, qp = vp[ok], qp[ok]
    zeta = -np.log(v_star - vp)
    Amat = np.vstack([zeta, np.ones_like(zeta)]).T
    sol, *_ = np.linalg.lstsq(Amat, np.log(qp), rcond=None)
    resid = np.log(qp) - Amat @ sol
    dof = max(len(zeta) - 2, 1)
    s2 = float((resid ** 2).sum()) / dof
    cov = s2 * np.linalg.inv(Amat.T @ Amat)
    return float(sol[0]), float(np.sqrt(max(cov[0, 0], 0.0))), int(len(zeta))


# ------------------------------------------------------------------------------
# 3. Извлечение пиков последней стадии (чистая зона данных)
# ------------------------------------------------------------------------------
def late_stage_peaks(runner, min_z_frac=0.0, key="Q"):
    """Пики Q(v) на строках с накопленным зумом z >= z_final*min_z_frac.

    Возвращает (v_peaks, Q_peaks)."""
    tr = runner.track
    v = np.array(tr["v"]); z = np.array(tr["z"]); y = np.array(tr[key], float)
    zf = z[-1] if len(z) else 0.0
    sel = z >= zf * min_z_frac - 1e-12
    if sel.sum() < 12:
        return np.array([]), np.array([])
    sub = {"v": v[sel], key: y[sel]}
    vp, yp = echo_peaks(sub, key)
    return vp, yp


# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
def main():
    t0 = time.time()
    out = {
        "config": {"family": "gaussian", "v_p": V_P, "sigma": SIGMA,
                   "a_star_fixed_grid": A_FIXED_GRID},
        "literature": {"gamma": GAMMA_LIT, "delta": DELTA_LIT,
                       "kappa_screaming": KAPPA_LIT},
        "spinor_framework": {},
        "mirror_parity": {},
        "runs": [],
        "delta_measurements": [],
        "kappa_measurements": [],
        "honest_limits": [],
    }

    # --- 2. точные соотношения фреймворка -----------------------------------
    gamma_lit_d = abs(B_CH - GAMMA_LIT) / GAMMA_LIT
    delta_lit_d = abs(DELTA_SP - DELTA_LIT) / DELTA_LIT
    prod_sp = B_CH * DELTA_SP
    prod_lit = GAMMA_LIT * DELTA_LIT
    out["spinor_framework"] = {
        "b_Ch = 1-cos(2pi/7)": B_CH,
        "gamma_lit": GAMMA_LIT,
        "R1_gamma_vs_lit_deviation": gamma_lit_d,
        "Delta_sp = 7*pi/30": DELTA_SP,
        "delta_lit": DELTA_LIT,
        "R2_delta_vs_lit_deviation": delta_lit_d,
        "R3_omega_wiggle = 4*pi/Delta_sp = 120/7": 4 * np.pi / DELTA_SP,
        "omega_wiggle_lit = 4*pi/Delta_lit": 4 * np.pi / DELTA_LIT,
        "R4_product_gamma*Delta_spinor": prod_sp,
        "R4_product_gamma*Delta_lit": prod_lit,
        "R4_product_deviation": abs(prod_sp - prod_lit) / prod_lit,
        "phase_per_echo_pi/15": PI_15 * DELTA_SP,
        "phase_per_echo_pi/30": PI_30 * DELTA_SP,
        "echoes_per_2pi_of_pi/15_phase": 2 * np.pi / (PI_15 * DELTA_SP),
        "echoes_per_2pi_of_pi/30_phase": 2 * np.pi / (PI_30 * DELTA_SP),
        "interpretation": (
            "Зеркало (u,v)->(v,u) — Z2-поворот спинорного типа; регулярный "
            "центр разлагается на скалярную (чётную E) и спинорную (нечётную "
            "O=a*r) части. Показатели pi/15 и pi/30 задают фазовую лестницу "
            "спинорных функций в log-переменной; Delta = 7*pi/30 — 7 "
            "квантов pi/30 на эхо. Расхождения с литературой у R1 (0.67%) и "
            "R2 (0.62%) почти компенсируются в произведении gamma*Delta "
            "(R4: 0.04%) — согласуется с идеей единой спинор-нормировки."),
    }

    # --- 1. зеркальные парности: A/B clamp (v2) vs regular (v3) -------------
    print("[1/3] Проверка зеркальных парностей центра (A/B: clamp vs regular)...")
    mp_clamp = verify_mirror_parity(closure="clamp")
    mp_reg = verify_mirror_parity(closure="regular")
    out["mirror_parity"] = {"clamp_v2": mp_clamp, "regular_v3": mp_reg}
    for tag, mp in (("clamp  v2", mp_clamp), ("regular v3", mp_reg)):
        ci, co = mp["inner_ring"], mp["outer_ring"]
        print(f"    {tag}: inner s_t={ci['s_t']:.2e} pq_even={ci['pq_even']:.2e} "
              f"m_odd={ci['m_odd']:.2e} | outer s_t={co['s_t']:.2e} "
              f"pq_even={co['pq_even']:.2e} m_odd={co['m_odd']:.2e}")

    # --- 3/4. дельта и каппа из зум-забегов ----------------------------------
    print("[2/3] Зум-забеги (v3.2, регулярное замыкание центра)...")
    for eps in (3e-5, 1e-4, 1e-3):
        A = A_FIXED_GRID + eps
        r = ZoomRunner(A=A, n=800, max_zooms=4, verbose=False)
        d = r.run()
        rec = {"eps": eps, "A": A, "zooms": d.zooms,
               "z_reached": float(r._z_acc), "stop": d.stopped,
               "M_AH_frozen": float(d.m_ah)}
        # пики: вся пост-зумовая часть (z>0) и последняя стадия
        for tag, frac in (("post_zoom", 0.0), ("last_stage", 1.0)):
            vp, yp = late_stage_peaks(r, min_z_frac=frac)
            fit = fit_delta_geometric(vp) if len(vp) >= 5 else None
            key = f"delta_{tag}"
            if fit:
                fit.update({"Q_peaks_v": [round(float(x), 6) for x in vp],
                            "Q_peaks_Q": [float(x) for x in yp]})
                kp = kappa_from_peaks(vp, yp, fit["v_star"])
                if kp:
                    fit["kappa"] = kp[0]; fit["kappa_err"] = kp[1]
                rec[key] = fit
                if tag == "post_zoom":
                    out["delta_measurements"].append(
                        {"eps": eps, "Delta": fit["Delta"],
                         "Delta_err": fit["Delta_err"], "n_peaks": fit["n_peaks"],
                         "v_star": fit["v_star"], "rms": fit["rms"]})
                    if "kappa" in fit:
                        out["kappa_measurements"].append(
                            {"eps": eps, "kappa": fit["kappa"],
                             "kappa_err": fit["kappa_err"]})
            else:
                rec[key] = None
        out["runs"].append(rec)
        d1 = rec.get("delta_post_zoom")
        print(f"    eps={eps:.0e}: zooms={d.zooms}, z={r._z_acc:.2f}, "
              f"stop={d.stopped}, "
              f"Delta={'%.4f±%.4f' % (d1['Delta'], d1['Delta_err']) if d1 else 'n/a'}")

    # --- сводные сравнения ----------------------------------------------------
    ds = [m["Delta"] for m in out["delta_measurements"]
          if np.isfinite(m["Delta"]) and m["Delta"] > 0.2 and m["Delta"] < 2.0]
    if ds:
        out["delta_summary"] = {
            "n_valid": len(ds),
            "Delta_median": float(np.median(ds)),
            "Delta_spread": float(np.std(ds)),
            "vs_Delta_lit_deviation": float(abs(np.median(ds) - DELTA_LIT) / DELTA_LIT),
            "vs_Delta_spinor_deviation": float(abs(np.median(ds) - DELTA_SP) / DELTA_SP),
        }
    ks = [m["kappa"] for m in out["kappa_measurements"] if np.isfinite(m["kappa"])]
    if ks:
        out["kappa_summary"] = {
            "n_valid": len(ks), "kappa_median": float(np.median(ks)),
            "vs_kappa_lit_deviation": float(abs(np.median(ks) - KAPPA_LIT) / KAPPA_LIT),
        }

    out["honest_limits"] = [
        "Стена глубины зум-цепочки: z ~ 3-5 (2-4 зума) — даже с v3-замыканием "
        "центра (связка наклонов s1-t1 = -2a, кубическая масса, проекция "
        "чётных частей p+q и c+d, тейпер) чётная мода E у центра выходит на "
        "взрыв за 2-3 рестарта. Полный фикс — центральный Тейлор-патч "
        "(подход Чоптюка 1993) — план v5.",
        "Delta-оценка по 4-7 пикам с rms-ошибкой 10-30% — ПРОТОТИП, не "
        "измерение; для процентной Delta нужно >= 6-8 чистых эхо (z >= 10).",
        "Спинорная модуляция с частотами pi/15, pi/30 имеет периоды 30 и 60 "
        "по дзета (~40-80 эхо) — на наших данных (2-7 эхо) НЕ разрешима; "
        "проверка возможна только при z >= 30.",
        "kappa-оценка по амплитудам Q-пиков загрязняется рестартами сетки; "
        "считать порядком величины.",
    ]
    out["runtime_s"] = round(time.time() - t0, 1)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"[3/3] Сохранено: {OUT_PATH}")

    # --- консольная сводка фреймворка ----------------------------------------
    sf = out["spinor_framework"]
    print("\n--- СПИНОР-ФРЕЙМВОРК: точные соотношения ---")
    print(f"  R1: gamma = b_Ch = 1-cos(2pi/7) = {sf['b_Ch = 1-cos(2pi/7)']:.6f}"
          f"  (lit {GAMMA_LIT}, dev {gamma_lit_d:.2%})")
    print(f"  R2: Delta = 7*pi/30 = {DELTA_SP:.6f}"
          f"  (lit {DELTA_LIT}, dev {delta_lit_d:.2%})")
    print(f"  R3: omega = 4*pi/Delta = 120/7 = {4*np.pi/DELTA_SP:.6f}"
          f"  (lit {4*np.pi/DELTA_LIT:.6f})")
    print(f"  R4: gamma*Delta: {prod_sp:.6f} vs {prod_lit:.6f}"
          f"  (dev {sf['R4_product_deviation']:.3%})")
    if "delta_summary" in out:
        dsm = out["delta_summary"]
        print(f"  Данные: Delta_median = {dsm['Delta_median']:.4f} "
              f"± {dsm['Delta_spread']:.4f} (n={dsm['n_valid']}), "
              f"dev lit {dsm['vs_Delta_lit_deviation']:.1%}, "
              f"dev спинор {dsm['vs_Delta_spinor_deviation']:.1%}")
    return out


if __name__ == "__main__":
    main()
