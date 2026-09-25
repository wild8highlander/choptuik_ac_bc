#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ЗУМ-КАМПАНИЯ v6: КОЛЬЦЕВАЯ ЧЁТНОСТЬ + ЭХО-ОСОЗНАННЫЕ ФИТЫ -> ПРОЦЕНТНОЕ tau*
ZOOM CAMPAIGN v6: ANNULUS PARITY + ECHO-AWARE FITS -> PERCENT-LEVEL tau*
================================================================================

v6 = два слоя поверх v5 (Тейлор-патч, maшино-выведенная иерархия O1-O5):

  1. КОЛЬЦЕВАЯ ЧЁТНОСТЬ (solver._annulus_parity): парная проекция зеркальной
     чётности ВНЕ тейлор-зоны (G=t+s чётно, D=t-s нечётно, pq чётно, m нечётно)
     + гашение аномальных мод (C/xi в O, M1*xi в m). Лечит стену v5:
     зеркало-чётность сырого марша ломается снаружи зоны
     (m_mirror=-12.7 vs m_phys=+4.2 при |r|~100du).

  2. ЭХО-ОСОЗНАННЫЕ ФИТЫ (этот модуль, БЕЗ якорей):
     a) tau* — амплитуда CSS-неподвижной точки башни центра:
        z-редукция (center_modes.py) даёт T0 = t0*s, P2h = P2*s^2 и связь
        неподвижной точки P2h* = T0*/3 => s_est = t0/(3 P2) — ЧАСЫ коллапса
        из самой башни (без внешних нормировок);
        tau_row = (t0*s_est)^2 = t0^4/(9 P2^2);
        модель у глубоких строк:
          ln tau_row = ln tau* + A1 cos(2 pi z/Delta) + A2 sin(2 pi z/Delta)
                       + c e^{-lambda (z - z0)},
        (a0, A1, A2, c) линейны при заданных (Delta, lambda) — вложенное
        линейное МНК, сетка по (Delta, lambda); Delta и lambda СВОБОДНЫЕ
        (кросс-чек: Delta_fit vs 7*pi/30 спинорной лестницы, lambda_fit vs
        lambda+(tau*) башни).
     b) перекрёстные CSS-связи на тех же строках (не зависят от tau):
        W2/t0^2 -> 4/3,  M3/(R1 t0^2) -> 2/3 (Торн),  d0*s -> 0,
        калибровка (1-chi^2)R1^2 = A0 -> C0_gauge -> 0.
     c) gamma(M(eps)) с wiggle-фитом ДСС:
          ln M = gamma ln eps + b0 + B1 cos(2 pi ln eps/Delta) + B2 sin(...)
     d) гамма из башни: gamma_tower = Delta_fit / lambda+(tau*) — первые
        принципы (lambda+(tau) — точный корень характеристического многочлена
        замкнутой башни, center_modes.json gamma_curve).

Запуск:
    python3 grid_machine_v6.py                 # полная лестница eps
    python3 grid_machine_v6.py 1e-3,3e-4       # чанк (домер по предыдущему JSON)
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

from zoom_solver import (ZoomRunner, echo_peaks, echo_period_from_peaks,
                         RESULTS, V_P, SIGMA)

BASE = os.path.dirname(os.path.abspath(__file__))
A_STAR = 0.0805333
DELTA_SP = 7.0 * np.pi / 30.0          # спинорная лестница (7 квант pi/30)
GAMMA_LIT = 0.374
B_CH = 1.0 - np.cos(2.0 * np.pi / 7.0)
OUT_PATH = os.path.join(RESULTS, "grid_machine_v6.json")
EPS_DEFAULT = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
Z_WIN_ECHOES = 2.5                     # глубина окна фита tau* (в эхах)


# ==============================================================================
# 1. ИЗВЛЕЧЕНИЕ tau-СТРОК ИЗ ТЕЙЛОР-ГИСТОГРАММ
# ==============================================================================
def stage_z_map(stage_constraints):
    """z на стадии k (0 = базовая): z накапливается на зумах."""
    zs = {0: 0.0}
    for c in stage_constraints:
        zs[int(c["zoom"])] = float(c["z"])
    return zs


def extract_tau_rows(tay_hist_all, zs, res_max=0.3):
    """Строки для фита tau*: s_est = t0/(3P2), tau_row = (t0 s_est)^2.

    Фильтры: фит-невязки E/O < res_max, конечность, s_est > 0 (ветка CSS).
    Возвращает список словарей (компактных).
    """
    rows = []
    for rec in tay_hist_all:
        t0 = rec.get("t0"); P2 = rec.get("P2")
        W2 = rec.get("W2"); M3 = rec.get("M3")
        R1 = rec.get("R1"); d0 = rec.get("d0")
        resE = rec.get("res_E", float("nan"))
        resO = rec.get("res_O", float("nan"))
        res_r = rec.get("res_r", float("nan"))
        if not all(np.isfinite(x) for x in (t0, P2, W2, M3, R1, d0)):
            continue
        # v6: основной фильтр качества — res_r (r-фит); res_E/O бывают nan
        # на строках с гейтованным O-фитом (это не брак строки, а гейт
        # ил-обусловленного базиса) — используем как мягкий фильтр
        if not (np.isfinite(res_r) and res_r < res_max):
            continue
        if np.isfinite(resE) and resE >= res_max:
            continue
        if np.isfinite(resO) and resO >= res_max:
            continue
        if abs(P2) < 1e-300 or abs(t0) < 1e-300:
            continue
        # v6: модульные значения — знак фита P2 (ил-обусловленный базис
        # с 1/xi) может флипаться относительно t0; CSS-связи придержим
        # по модулю, честно отмечено в honest_notes
        s_est = abs(t0) / (3.0 * abs(P2))
        if not (np.isfinite(s_est) and s_est > 0.0):
            continue
        tau_row = t0 ** 4 / (9.0 * P2 ** 2)
        if not np.isfinite(tau_row) or tau_row <= 0.0:
            continue
        z_cont = float(np.log(1.0 / s_est))
        stage = int(rec.get("stage", 0))
        rows.append({
            "v": float(rec["v"]), "stage": stage,
            "z_stage": float(zs.get(stage, 0.0)),
            "s_est": float(s_est), "z_cont": z_cont,
            "tau": float(tau_row), "t0": float(t0), "P2": float(P2),
            "r_W": float(W2 / t0 ** 2),            # -> 4/3
            "r_M": float(M3 / (R1 * t0 ** 2)),     # -> 2/3 (Торн, chi=0)
            "d0s": float(d0 * s_est),              # -> 0
            "g0": float(rec.get("C0_gauge", float("nan"))),  # -> 0
        })
    return rows


# ==============================================================================
# 2. ЭХО-ОСОЗНАННЫЙ ФИТ tau*
# ==============================================================================
def _wls_design(z, delta, lam, z0):
    """Матрица [1, cos, sin, exp(-lam (z-z0))] для линейных параметров."""
    x = 2.0 * np.pi * z / delta
    E = np.exp(-lam * (z - z0))
    return np.stack([np.ones_like(z), np.cos(x), np.sin(x), E], axis=1)


def fit_tau_star(rows, z_window=None, delta_grid=None, lam_grid=None,
                 delta_fixed=None, n_boot=200, seed=7):
    """ln tau = a0 + A1 cos(2pi z/Delta) + A2 sin(2pi z/Delta) + c e^{-lam(z-z0)}.

    Линейные параметры (a0, A1, A2, c) при заданных (Delta, lambda);
    сеточный поиск по (Delta, lambda) с вложенным МНК. tau* = exp(a0).
    """
    z = np.array([r["z_cont"] for r in rows])
    y = np.log(np.array([r["tau"] for r in rows]))
    if len(z) == 0:
        return None
    if z_window is None:
        z_window = Z_WIN_ECHOES * DELTA_SP
    m = z >= z.max() - z_window
    z, y = z[m], y[m]
    if len(z) < 10:
        return None
    z0 = float(z.max())
    if delta_grid is None:
        delta_grid = np.linspace(0.55, 1.05, 21)
    if lam_grid is None:
        lam_grid = np.geomspace(0.3, 6.0, 25)
    if delta_fixed is not None:
        delta_grid = np.array([delta_fixed])

    def solve(dz, lz):
        A = _wls_design(z, dz, lz, z0)
        sol, *_ = np.linalg.lstsq(A, y, rcond=None)
        r = y - A @ sol
        return float(r @ r), sol

    best = None
    for dz in delta_grid:
        for lz in lam_grid:
            rss, sol = solve(dz, lz)
            if best is None or rss < best[0]:
                best = (rss, dz, lz, sol)
    rss, d_fit, l_fit, sol = best
    a0, A1, A2, c = (float(v) for v in sol)

    # bootstrap по строкам (устойчивые ошибки)
    rng = np.random.default_rng(seed)
    boots = []
    idx = np.arange(len(z))
    for _ in range(n_boot):
        sel = rng.choice(idx, size=len(idx), replace=True)
        Ab = _wls_design(z[sel], d_fit, l_fit, z0)
        yb = y[sel]
        if np.linalg.matrix_rank(Ab) < 4:
            continue
        sb, *_ = np.linalg.lstsq(Ab, yb, rcond=None)
        boots.append(sb[0])
    se_a0 = float(np.std(boots)) if len(boots) > 20 else float("nan")

    return {
        "tau_star": float(np.exp(a0)), "tau_star_err_rel": se_a0,
        "wiggle_amp": float(np.hypot(A1, A2)),
        "c_drift": c, "lambda_drift": float(l_fit),
        "delta_fit": float(d_fit), "n_rows": int(len(z)),
        "z_window": [float(z.min()), float(z.max())],
        "rss": rss,
        "a0": a0, "A1": A1, "A2": A2, "z0": z0,
    }


def css_cross_checks(rows, z_window=None):
    """Медианы CSS-связей на глубоком окне (не зависят от tau)."""
    if not rows:
        return None
    z = np.array([r["z_cont"] for r in rows])
    if z_window is None:
        z_window = Z_WIN_ECHOES * DELTA_SP
    m = z >= z.max() - z_window
    if m.sum() < 5:
        return None
    r_W = np.array([r["r_W"] for r in rows])[m]
    r_M = np.array([r["r_M"] for r in rows])[m]
    d0s = np.array([r["d0s"] for r in rows])[m]
    g0 = np.array([r["g0"] for r in rows])[m]
    g0 = g0[np.isfinite(g0)]
    return {
        "n_rows": int(m.sum()),
        "W2_over_t02": {"median": float(np.median(r_W)),
                        "p10": float(np.percentile(r_W, 10)),
                        "p90": float(np.percentile(r_W, 90)),
                        "target": 4.0 / 3.0},
        "M3_over_R1_t02": {"median": float(np.median(r_M)),
                           "p10": float(np.percentile(r_M, 10)),
                           "p90": float(np.percentile(r_M, 90)),
                           "target": 2.0 / 3.0},
        "d0_times_s": {"median": float(np.median(np.abs(d0s))),
                       "p90": float(np.percentile(np.abs(d0s), 90)),
                       "target": 0.0},
        "C0_gauge": {"median": float(np.median(g0)) if len(g0) else None,
                     "target": 0.0},
    }


# ==============================================================================
# 3. WIGGLE-ФИТ gamma(M(eps)) — эхо-осознанный скейлинг
# ==============================================================================
def fit_gamma_wiggle(points, delta_grid=None, delta_fixed=None):
    """ln M = g ln eps + b0 + B1 cos(2 pi ln eps/Delta) + B2 sin(...).

    Линейные (g, b0, B1, B2) при заданном Delta; сетка по Delta.
    """
    xs = np.log(np.array([p[0] for p in points]))
    ys = np.log(np.array([p[1] for p in points]))
    if len(xs) < 5:
        return None
    if delta_grid is None:
        delta_grid = np.linspace(0.55, 1.05, 26)
    if delta_fixed is not None:
        delta_grid = np.array([delta_fixed])

    def solve(dz):
        x = 2.0 * np.pi * xs / dz
        A = np.stack([xs, np.ones_like(xs), np.cos(x), np.sin(x)], axis=1)
        sol, *_ = np.linalg.lstsq(A, ys, rcond=None)
        r = ys - A @ sol
        dof = max(len(xs) - 4, 1)
        return float(r @ r) / dof, sol

    best = None
    for dz in delta_grid:
        rss, sol = solve(dz)
        if best is None or rss < best[0]:
            best = (rss, dz, sol)
    rss, d_fit, sol = best
    g, b0, B1, B2 = (float(v) for v in sol)
    return {
        "gamma": g, "delta_fit": float(d_fit),
        "wiggle_amp": float(np.hypot(B1, B2)),
        "rss_dof": rss, "n_points": len(xs),
        "gamma_err": float(np.sqrt(max(rss, 0.0)
                                   * np.linalg.inv(np.stack(
                                       [xs, np.ones_like(xs), np.cos(
                                           2 * np.pi * xs / d_fit),
                                        np.sin(2 * np.pi * xs / d_fit)],
                                       axis=1).T
                                       @ np.stack(
                                           [xs, np.ones_like(xs),
                                            np.cos(2 * np.pi * xs / d_fit),
                                            np.sin(2 * np.pi * xs / d_fit)],
                                           axis=1))[0, 0])),
    }


# ==============================================================================
# 4. lambda+(tau) ИЗ БТАШНИ (center_modes.json, точный корень char-полинома)
# ==============================================================================
def lambda_plus_interp(tau, curve):
    """Интерполяция lambda+(tau) по сохранённой gamma_curve башни."""
    ts = np.array([c["tau"] for c in curve])
    ls = np.array([c["lambda_plus"] for c in curve])
    o = np.argsort(ts)
    return float(np.interp(np.log(max(tau, 1e-12)), np.log(ts[o]), ls[o]))


# ==============================================================================
# 5. КАМПАНИЯ
# ==============================================================================
def run_chunk(eps_list, n=800, max_zooms=14, annulus=True, ann_factor=10.0,
              march_center=True, r_ah_du=8.0, verbose=False):
    """Прогнать eps-чанк, влить в OUT_PATH, пересчитать фиты, сохранить."""
    t_start = time.time()
    out = {
        "config": {"n": n, "max_zooms": max_zooms, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA,
                   "annulus": annulus, "ann_factor": ann_factor,
                   "march_center": march_center, "r_ah_du": r_ah_du,
                   "closure": "taylor (v5 patch) + annulus parity (v6)",
                   "eps_list_run": eps_list},
        "a_star": A_STAR,
        "a_star_source": "fixed-grid N=1600 bisection (validated, session 1)",
        "gamma_lit": GAMMA_LIT, "b_Ch": B_CH,
        "delta_spinor": DELTA_SP,
        "runs": [],
    }
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, encoding="utf-8") as fh:
                prev = json.load(fh)
            keep = [r for r in prev.get("runs", [])
                    if r["eps"] not in eps_list]
            if keep:
                out["runs"].extend(keep)
                print(f"(подхвачено {len(keep)} прогонов предыдущих чанков)",
                      flush=True)
        except Exception:
            pass

    print("=" * 72)
    print("ЗУМ-КАМПАНИЯ v6 (кольцевая чётность + эхо-фиты): A* = %.7f" % A_STAR)
    print("=" * 72, flush=True)

    for eps in sorted(eps_list):
        A = A_STAR + eps
        t0 = time.time()
        r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose,
                       annulus=annulus, ann_factor=ann_factor,
                       march_center=march_center, r_ah_du=r_ah_du)
        d = r.run()
        zs = stage_z_map(d.stage_constraints)
        tau_rows = extract_tau_rows(r.tay_hist_all, zs)
        tr = r.track
        vp, yp = echo_peaks(r.track, "Q")
        rec = {
            "eps": eps, "A": A,
            "stop": d.stopped,
            "M_AH_frozen": float(d.m_ah),
            "M_AH_max_seen": float(d.m_ah_max),
            "zooms": d.zooms, "z_reached": float(r._z_acc),
            "mx_max": float(np.nanmax(tr["mx"])),
            "runtime_s": round(time.time() - t0, 1),
            "stage_constraints": [
                {"zoom": c["zoom"], "lam": round(c["lam"], 3),
                 "z": round(c["z"], 4), "c1_max": c["c1_max"]}
                for c in d.stage_constraints],
            "Q_peaks_n": int(len(vp)),
        }
        if len(vp) >= 4:
            D, Derr, npk = echo_period_from_peaks(vp)
            rec["Delta_ln_intervals"] = {"Delta": float(D),
                                         "err": float(Derr), "n": int(npk)}
        # эхо-осознанный фит tau* по ЭТОМУ забегу
        tf = fit_tau_star(tau_rows)
        rec["tau_fit"] = {k: v for k, v in tf.items()
                          if k not in ("a0", "A1", "A2", "z0")} if tf else None
        rec["tau_css_checks"] = css_cross_checks(tau_rows)
        # компактная выборка tau-строк (глубокое окно + прореживание)
        if tau_rows:
            zc = np.array([x["z_cont"] for x in tau_rows])
            deep = zc >= zc.max() - 4.0 * DELTA_SP
            sel = [x for i, x in enumerate(tau_rows)
                   if deep[i] or i % 4 == 0]
            rec["tau_rows_kept"] = len(sel)
        else:
            sel = []
        rec["tau_rows_sample"] = sel[:2500]
        ann = getattr(r.sol, "_ann_hist", [])
        if ann:
            cj = [abs(x["C_j"]) for x in ann if np.isfinite(x["C_j"])]
            m1 = [abs(x["M1"]) for x in ann if np.isfinite(x["M1"])]
            rec["annulus_summary"] = {
                "rows": len(ann),
                "C_j_median": float(np.median(cj)) if cj else None,
                "M1_median": float(np.median(m1)) if m1 else None,
            }
        out["runs"].append(rec)
        tfit = rec["tau_fit"]
        print(f"  eps={eps:.1e}: stop={d.stopped}, M_frozen={d.m_ah:.6f}, "
              f"M_max={d.m_ah_max:.6f}, zooms={d.zooms}, z={r._z_acc:.2f}, "
              f"tau_rows={len(tau_rows)}"
              + (f", tau*={tfit['tau_star']:.4f}+-{tfit['tau_star_err_rel']:.4f}"
                 f" (D_fit={tfit['delta_fit']:.3f}, lam={tfit['lambda_drift']:.2f})"
                 if tfit else ", tau_fit=n/a")
              + f" [{time.time()-t0:.0f}s]", flush=True)

    analyze_and_save(out)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t_start:.0f} c)")
    return out


def analyze_and_save(out):
    """Сводный анализ: tau* (по всем забегам), wiggle-gamma, gamma из башни."""
    runs = out["runs"]
    # --- объединённый фит tau* по всем глуб строкам всех забегов -----------
    all_rows = []
    for r_ in runs:
        all_rows.extend(r_.get("tau_rows_sample", []))
    out["tau_star_global"] = None
    if len(all_rows) >= 20:
        tf = fit_tau_star(all_rows)
        if tf:
            tf = {k: v for k, v in tf.items()
                  if k not in ("a0", "A1", "A2", "z0")}
            out["tau_star_global"] = tf
    # CSS-связи на объединённом глубоком окне
    out["css_checks_global"] = css_cross_checks(all_rows)

    # --- wiggle-gamma -------------------------------------------------------
    pts = [(r_["eps"], r_["M_AH_max_seen"]) for r_ in runs
           if r_.get("M_AH_max_seen", 0) > 1e-8]
    out["gamma_wiggle"] = fit_gamma_wiggle(pts) if len(pts) >= 5 else None
    out["gamma_wiggle_dsp"] = (fit_gamma_wiggle(pts, delta_fixed=DELTA_SP)
                               if len(pts) >= 5 else None)

    # --- gamma из башни: gamma = Delta_fit / lambda+(tau*) ------------------
    out["gamma_tower"] = None
    try:
        with open(os.path.join(RESULTS, "center_modes.json"),
                  encoding="utf-8") as fh:
            cm = json.load(fh)
        curve = cm["part3"]["gamma_curve"]
        src = None
        if out["tau_star_global"]:
            src = ("global", out["tau_star_global"])
        else:
            cands = [(r_["eps"], r_["tau_fit"]) for r_ in runs
                     if r_.get("tau_fit")]
            if cands:
                src = (cands[-1][0], cands[-1][1])
        if src is not None:
            eps_src, tf = src
            tau_s = tf["tau_star"]
            lam_tower = lambda_plus_interp(tau_s, curve)
            d_use = tf.get("delta_fit", DELTA_SP)
            out["gamma_tower"] = {
                "tau_star_source": f"eps={eps_src:.1e}",
                "tau_star": tau_s,
                "lambda_plus_tower": lam_tower,
                "delta_used": d_use,
                "gamma_tower": float(d_use / lam_tower),
                "vs_b_Ch_dev": abs(d_use / lam_tower - B_CH) / B_CH,
                "vs_gamma_lit_dev": abs(d_use / lam_tower - GAMMA_LIT) / GAMMA_LIT,
                "note": ("lambda+(tau) — точный корень характеристического "
                         "многочлена замкнутой башни (center_modes.py); "
                         "вне codim-1 окна 0<tau<=27/80 формально "
                         "(усечение уровней 0-2), см. honest_notes"),
            }
    except Exception as e:  # noqa: BLE001
        out["gamma_tower_error"] = str(e)

    # --- сводка --------------------------------------------------------------
    z_max = max((r_["z_reached"] for r_ in runs), default=0.0)
    tsg = out["tau_star_global"]
    gw = out["gamma_wiggle"]
    out["summary"] = {
        "z_max_reached": z_max,
        "tau_star_global": tsg["tau_star"] if tsg else None,
        "tau_star_err_rel": tsg["tau_star_err_rel"] if tsg else None,
        "delta_fit_global": tsg["delta_fit"] if tsg else None,
        "lambda_drift_global": tsg["lambda_drift"] if tsg else None,
        "gamma_wiggle": gw["gamma"] if gw else None,
        "gamma_tower": (out["gamma_tower"] or {}).get("gamma_tower"),
        "percent_level_tau": bool(tsg and tsg["tau_star_err_rel"] < 0.02),
        "v6_achievements": [],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    # печатная сводка
    if tsg:
        print(f"\n[tau*] global: {tsg['tau_star']:.5f} "
              f"+- {tsg['tau_star_err_rel']:.2%} "
              f"(Delta_fit={tsg['delta_fit']:.4f} vs 7pi/30={DELTA_SP:.4f}; "
              f"lambda_drift={tsg['lambda_drift']:.3f})")
    if out["css_checks_global"]:
        cc = out["css_checks_global"]
        print(f"[CSS] W2/t0^2 = {cc['W2_over_t02']['median']:.4f} (цель 4/3), "
              f"M3/(R1 t0^2) = {cc['M3_over_R1_t02']['median']:.4f} (цель 2/3), "
              f"|d0*s| = {cc['d0_times_s']['median']:.2e}")
    if gw:
        print(f"[gamma] wiggle: {gw['gamma']:.4f} (Delta_fit={gw['delta_fit']:.4f}); "
              f"lit {GAMMA_LIT}, b_Ch {B_CH:.6f}")
    if out["gamma_tower"]:
        gt = out["gamma_tower"]
        print(f"[gamma] tower: Delta_fit/lambda+(tau*) = {gt['gamma_tower']:.4f} "
              f"(lambda+ = {gt['lambda_plus_tower']:.4f}; "
              f"dev b_Ch {gt['vs_b_Ch_dev']:.2%})")


def main():
    eps_list = EPS_DEFAULT
    if len(sys.argv) > 1:
        eps_list = [float(x) for x in sys.argv[1].split(",")]
    run_chunk(eps_list)


if __name__ == "__main__":
    main()
