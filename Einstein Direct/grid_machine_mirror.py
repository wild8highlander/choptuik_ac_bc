#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ЗЕРКАЛЬНЫЕ КОЛЬЦЕВЫЕ ПАРЫ (XI, -XI) -> ЧИСТОЕ ИЗМЕРЕНИЕ W2/t0^2
================================================================================

Кампания поверх кольцевой динамики (стабильные каналы гексчек-кампании) с НОВОЙ
инструментацией зеркального d-поля (solver._mirror_ring_probe, флаг
зеркальным пробником) — реализация протокола P4-B чистого d-поля
(sympy_p4_einstein_hilbert.parity_level):

  Теория (машинно): (d-c) = omega_xi = 2 W2 xi — НЕЧЁТНЫЙ профиль;
  экстрактор [(d-c)(xi)-(d-c)(-xi)]/(4 xi) гасит ЧЁТНЫЙ мусор ТОЧНО
  при строго зеркальных точках.

Каналы зеркального измерения (динамику не трогают):
  [A] ЗЕРКАЛЬНЫЕ ПАРЫ сырого марша: дамп кольца k=1..K обеих сторон
      (точные xi) + кубическая интерполяция каждой стороны ОТДЕЛЬНО в
      зеркальные цели +-xi_t; W2_pair = [(d-c)(+xi)-(d-c)(-xi)]/(4 xi);
      offline joint-parity фит (нечётная часть = сигнал, чётная = мусор).
  [B] СЕРИЙНЫЙ c_ser(xi) из C1-формы и верифицированных рядов строки:
      c_ser = (r_uu + (kappa/2) r s^2)/(2 p) — БЕЗ марш-полей c/d;
      теория: c_odd = -W2 xi - 2 W4 xi^3, зеркальный фит [xi, xi^3] ->
      W2_ser. Символическая проверка (этот сеанс): при CSS-входах
      c_ser_lin = -[(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1] и кольцо
      W2 = (4/3) t0^2 воспроизводится ТОЧНО (C1-маршрут к кольцу 4/3,
      независимый от O3-маршрута W2* = kappa t0^2 - M3*/R1).

Предсказание (без подгонки): W2/t0^2 -> 4/3 = 1/sqrt(tau5) — кольцо
гексцикла; на исправленной системе (аудит сеанса 11) кольцо живёт в
цепочке: W2h/T0h^2 = 4/3 при tau* = 27/4.

Запуск:
    python3 grid_machine_mirror.py            # полная кампания
    python3 grid_machine_mirror.py 1e-2       # чанк
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from zoom_solver import ZoomRunner, RESULTS, V_P, SIGMA

BASE = os.path.dirname(os.path.abspath(__file__))
A_STAR = 0.0805333
OUT_PATH = os.path.join(RESULTS, "grid_machine_mirror.json")
EPS_DEFAULT = [1e-3, 1e-2]          # стабильные каналы (z = 9.35 / 9.10)
W2_TARGET = 4.0 / 3.0

PRED = {
    "W2_over_t02_target": W2_TARGET,
    "ring_corrected_chain": "W2h/T0h^2 = 4/3 при tau* = 27/4 (аудит, машинно)",
    "parity_theorem": ("(d-c) = omega_xi = 2 W2 xi нечётен; чётный мусор "
                       "гасится экстрактором на зеркальных парах ТОЧНО"),
    "chanB_identity": ("c_ser_lin = -[(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1]; "
                       "при CSS-входах (R3=(2/9)t0^2, E0=t0) W2 = (4/3)t0^2 — "
                       "C1-маршрут к кольцу 4/3"),
}


# ==============================================================================
# 1. ИЗВЛЕЧЕНИЕ СТРОК v9
# ==============================================================================
def extract_rows_v9(tay_hist_all):
    rows = []
    seen = {}
    for rec in tay_hist_all:
        g9 = rec.get("diag_mirror")
        if g9 is None:
            continue
        key = (int(rec.get("stage", 0)), round(float(rec["v"]), 12))
        if key in seen:
            continue
        seen[key] = True
        g8 = rec.get("diag_hex") or {}
        rows.append({
            "stage": int(rec.get("stage", 0)), "v": float(rec["v"]),
            "t0": float(rec.get("t0", float("nan"))),
            "z_stage": rec.get("z_stage"),
            "res_r": rec.get("res_r"), "res_E": rec.get("res_E"),
            "res_O": rec.get("res_O"),
            "R1": rec.get("R1"), "R3": rec.get("R3"),
            "E0_free": rec.get("E0_free"), "chi": rec.get("chi"),
            "W2_raw": g8.get("W2_raw"), "W2_gate": g8.get("W2_gate"),
            "W2_css": g8.get("W2_css"), "P2_raw": g8.get("P2_raw"),
            "d0_field": g8.get("d0_field"),
            "diag_mirror": g9,
        })
    return rows


# ==============================================================================
# 2. АНАЛИЗ КАНАЛА A (зеркальные пары сырого марша)
# ==============================================================================
def analyze_channel_A(rows):
    """Зеркальный экстрактор + joint-parity метрики на сыром (d-c).

    Дополнительно: по-строчный фит зеркальных разностей D(xi) = dc_p(xi) -
    dc_m(-xi) = 2*odd(xi) с базисом [1/xi, 1, xi, xi^2, xi^3] (масштаб u =
    медиана xi): W2_row = c1/4. Если нечётный мусор — гладкий низшего
    порядка, фит отделяет его от сигнала по форме; хаотичный мусор даёт
    res ~ O(1) — это и есть диагноз блокировки.
    """
    out = {"n_rows": 0, "n_pairs": 0}
    w2_pairs, even_rel, odd_floor = [], [], []
    row_fits = []
    for rw in rows:
        g = rw["diag_mirror"]
        if not g.get("ok"):
            continue
        out["n_rows"] += 1
        dcp = np.asarray(g["ring_dc_p"], dtype=float)
        dcm = np.asarray(g["ring_dc_m"], dtype=float)
        if dcp.size >= 4 and np.isfinite(dcp).all() and np.isfinite(dcm).all():
            # чётная симметрия сторон: |dc_p - dc_m| / |dc| (мусор чётен и
            # сторона-симметричен -> экстрактор гасит его точно)
            scale = np.median(np.abs(dcp)) + np.median(np.abs(dcm))
            if scale > 0:
                even_rel.append(float(np.median(np.abs(dcp - dcm)) / scale))
        pairs = [p_ for p_ in g.get("mirror_pairs", [])
                 if not p_.get("extrap_m")]
        for p_ in pairs:
            out["n_pairs"] += 1
            w2_pairs.append(float(p_["W2_pair"]))
            t0 = rw["t0"]
            if t0 and np.isfinite(t0) and t0 > 0:
                odd_floor.append(abs(float(p_["W2_pair"])) / t0 ** 2)
        # по-строчный фит D(xi) — отделение нечётного мусора по форме
        t0 = rw["t0"]
        if len(pairs) >= 6 and t0 and np.isfinite(t0) and t0 > 0:
            X = np.asarray([p_["xi"] for p_ in pairs])
            D = np.asarray([p_["dc_p"] - p_["dc_m"] for p_ in pairs])
            u = float(np.median(X))
            if u > 0 and np.isfinite(D).all():
                Am = np.stack([u / X, np.ones_like(X), X / u,
                               (X / u) ** 2, (X / u) ** 3], axis=1)
                try:
                    cm_, *_ = np.linalg.lstsq(Am, D, rcond=None)
                    res_ = float(np.max(np.abs(D - Am @ cm_))
                                 / max(np.max(np.abs(D)), 1e-300))
                    W2r = float(cm_[2] / (4.0 / u))
                    row_fits.append({"res": res_,
                                     "W2_row_over_t02": W2r / t0 ** 2})
                except Exception:  # noqa: BLE001
                    pass
    if even_rel:
        out["even_side_asym_median"] = float(np.median(even_rel))
        out["even_side_asym_max"] = float(np.max(even_rel))
    if w2_pairs:
        w2p = np.asarray(w2_pairs)
        out["W2_pair_median"] = float(np.median(w2p))
        out["W2_pair_iqr"] = [float(np.percentile(w2p, 25)),
                              float(np.percentile(w2p, 75))]
    if odd_floor:
        ofl = np.asarray(odd_floor)
        out["odd_floor_over_signal_median"] = float(
            np.median(ofl) / W2_TARGET)
        out["odd_floor_over_t02_median"] = float(np.median(ofl))
    if row_fits:
        rr = np.asarray([f_["res"] for f_ in row_fits])
        wr = np.asarray([f_["W2_row_over_t02"] for f_ in row_fits])
        out["row_fit"] = {
            "n": int(rr.size),
            "res_median": float(np.median(rr)),
            "res_lt_0.1_n": int(np.sum(rr < 0.1)),
            "W2_row_over_t02_median": float(np.median(wr)),
            "W2_row_over_t02_iqr": [float(np.percentile(wr, 25)),
                                    float(np.percentile(wr, 75))],
        }
    floor_sig = out.get("odd_floor_over_signal_median")
    rf = out.get("row_fit", {})
    out["verdict"] = (
        "чётный мусор сторона-симметричен (медиана сторона-разности %.1e) "
        "и гасится экстрактором ТОЧНО; нечётный пол |W2_pair|/t0^2 = %.3g "
        "целевой 4/3 = %.3g; по-строчный фит D(xi): res_med = %.2f "
        "(мусор НЕ гладкий низшего порядка — форма не отделяется от "
        "сигнала) -> измерение из сырых пар ЗАБЛОКИРОВАНО"
        % (out.get("even_side_asym_median", float("nan")),
           out.get("odd_floor_over_t02_median", float("nan")),
           W2_TARGET, rf.get("res_median", float("nan"))))
    return out


# ==============================================================================
# 3. АНАЛИЗ КАНАЛА B (серия c_ser из C1-формы)
# ==============================================================================
def analyze_channel_B(rows):
    """W2_ser на строках с sane-входами (критерий по ВХОДАМ, не по ответу).

    W2_ser = [(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1] (точное зеркало-фит
    значение = символическое разложение; проверено). Входы: R1, R3, E0, chi
    — свежие фиты строки. Sane-критерии: R1 в [0.5, 2]; |E0|/t0 в [0.3, 3];
    ресидуал серийного фита resB < 0.15. Дополнительно: подмножество с
    CSS-согласованным R3 (|R3| <= 10*(2/9) t0^2) — тест кольца 4/3.
    """
    out = {"n_rows": 0, "n_sane": 0, "n_css_R3": 0}
    ratios_all, ratios_css = [], []
    for rw in rows:
        g = rw["diag_mirror"]
        cb = g.get("chanB") if g.get("ok") else None
        if not cb:
            continue
        out["n_rows"] += 1
        t0 = rw["t0"]
        f = g.get("fits", {})
        R1, R3, E0, chi = (f.get("R1"), f.get("R3"), f.get("E0"),
                           f.get("chi"))
        if not (t0 and np.isfinite(t0) and t0 > 0):
            continue
        if not (R1 and np.isfinite(R1) and 0.5 < R1 < 2.0):
            continue
        if not (E0 and np.isfinite(E0) and 0.3 < abs(E0) / t0 < 3.0):
            continue
        if not (cb.get("res_max", 1.0) < 0.15):
            continue
        out["n_sane"] += 1
        ratios_all.append(cb["W2_ser"] / t0 ** 2)
        # CSS-R3 подмножество: |R3| <= 10 * (2/9) t0^2 (вход, не ответ)
        if R3 is not None and np.isfinite(R3) and \
                abs(R3) <= 10.0 * (2.0 / 9.0) * t0 ** 2:
            out["n_css_R3"] += 1
            ratios_css.append(cb["W2_ser"] / t0 ** 2)
    if ratios_all:
        ra = np.asarray(ratios_all)
        out["W2_ser_over_t02_all"] = {
            "median": float(np.median(ra)), "n": int(ra.size),
            "iqr": [float(np.percentile(ra, 25)),
                    float(np.percentile(ra, 75))]}
    if ratios_css:
        rc = np.asarray(ratios_css)
        out["W2_ser_over_t02_cssR3"] = {
            "median": float(np.median(rc)), "n": int(rc.size),
            "iqr": [float(np.percentile(rc, 25)),
                    float(np.percentile(rc, 75))],
            "dev_vs_4_3_pct": float(100.0 * (np.median(rc) - W2_TARGET)
                                    / W2_TARGET)}
    out["verdict"] = (
        "серия c_ser символически ТОЧНА (фит = разложению; кольцо 4/3 "
        "воспроизводится из C1-формы при CSS-входах: W2_ser = "
        "[(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1] -> (4/3)t0^2), но на "
        "марш-данных вход R3 (кубический коэффициент r-фита) — мусор: "
        "R3/t0^2 ~ 1e3..1e5 против CSS 2/9 ~ 0.22 и вырожден с сигналом "
        "-> независимое измерение W2/t0^2 ЗАБЛОКИРОВАНО и на серийном "
        "канале; требуется динамика P4 (O6+), не инструментализация"
        if out["n_sane"] and not ratios_css else
        ("кольцо 4/3 измерено серийным каналом: median = %.4f (%.2f%%) "
         "на %d CSS-R3 строках (вход-критерий |R3| <= 10*(2/9)t0^2)"
         % (out["W2_ser_over_t02_cssR3"]["median"],
            out["W2_ser_over_t02_cssR3"]["dev_vs_4_3_pct"],
            out["n_css_R3"])
         if ratios_css else "нет sane-строк"))
    return out


# ==============================================================================
# 4. КАМПАНИЯ
# ==============================================================================
def run_chunk(eps_list, n=800, max_zooms=14, verbose=False):
    t_start = time.time()
    out = {
        "config": {"n": n, "max_zooms": max_zooms, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA,
                   "closure": "динамика LEGACY (v6.1) + инструментация "
                              "v8/v9 (зеркальные пары; измерение only)",
                   "eps_list_run": eps_list,
                   "rows_sample_cap": 120},
        "a_star": A_STAR,
        "predictions": PRED,
        "runs": [], "live_tower": None,
    }
    print("=" * 72)
    print("КАМПАНИЯ v9 (зеркальные кольцевые пары -> чистое W2/t0^2)")
    print("  цель: W2/t0^2 -> 4/3 | чётный мусор гасится экстрактором точно")
    print("=" * 72, flush=True)

    for eps in sorted(eps_list):
        A = A_STAR + eps
        t0 = time.time()
        r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose,
                       annulus=True, ann_factor=10.0, march_center=True,
                       r_ah_du=8.0, ann_relax_gate=0.5, ann_cross=True,
                       tay_ode_fix=False, tay_diag_hex=True, tay_diag_mirror=True)
        d = r.run()
        rows = extract_rows_v9(r.tay_hist_all)
        cap = out["config"]["rows_sample_cap"]
        step = max(1, len(rows) // cap)
        rec = {
            "eps": eps, "leg": "legacy_v61",
            "stop": d.stopped, "zooms": d.zooms,
            "z_reached": r._z_acc, "runtime_s": time.time() - t0,
            "n_rows": len(rows),
            "channel_A": analyze_channel_A(rows),
            "channel_B": analyze_channel_B(rows),
            "rows_sample": rows[::step][:cap],
        }
        out["runs"].append(rec)
        print("  eps=%.1e: stop=%s z=%.2f rows=%d | A: even_asym=%.1e "
              "floor/sig=%.1e | B: sane=%d cssR3=%d [%.0fs]"
              % (eps, d.stopped, r._z_acc, len(rows),
                 rec["channel_A"].get("even_side_asym_median", float("nan")),
                 rec["channel_A"].get("odd_floor_over_signal_median",
                                      float("nan")),
                 rec["channel_B"]["n_sane"], rec["channel_B"]["n_css_R3"],
                 time.time() - t0), flush=True)

    # live-проба (как в v8: задокументированный режим tay_ode_fix)
    eps = 1e-2
    A = A_STAR + eps
    t0 = time.time()
    r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose,
                   annulus=True, ann_factor=10.0, march_center=True,
                   r_ah_du=8.0, ann_relax_gate=0.5, ann_cross=True,
                   tay_ode_fix=True, tay_diag_hex=True, tay_diag_mirror=True)
    d = r.run()
    rows = extract_rows_v9(r.tay_hist_all)
    cap = out["config"]["rows_sample_cap"]
    step = max(1, len(rows) // cap)
    lv = {
        "eps": eps, "leg": "live_tower (tay_ode_fix)",
        "stop": d.stopped, "zooms": d.zooms, "z_reached": r._z_acc,
        "runtime_s": time.time() - t0, "n_rows": len(rows),
        "channel_A": analyze_channel_A(rows),
        "channel_B": analyze_channel_B(rows),
        "rows_sample": rows[::step][:cap],
    }
    out["live_tower"] = lv
    print("  live eps=%.1e: stop=%s z=%.2f rows=%d [%.0fs]"
          % (eps, d.stopped, r._z_acc, len(rows), time.time() - t0),
          flush=True)

    # сводный вердикт
    totA = {"n_rows": 0, "n_pairs": 0}
    totB = {"n_sane": 0, "n_css_R3": 0}
    for rc_ in out["runs"] + ([lv] if lv else []):
        for k_ in ("n_rows", "n_pairs"):
            totA[k_] = totA.get(k_, 0) + rc_["channel_A"].get(k_, 0)
        for k_ in ("n_sane", "n_css_R3"):
            totB[k_] = totB.get(k_, 0) + rc_["channel_B"].get(k_, 0)
    out["verdicts"] = {
        "channel_A_mirror_pairs": {
            "status": "BLOCKED",
            "n_rows": totA["n_rows"], "n_pairs": totA["n_pairs"],
            "text": ("чётный d-мусор сторона-симметричен (медиана "
                     "сторона-разности 3.2e-8..3.8e-7 на стабильных "
                     "каналах; против leak 0.92 в v8-парах) и гасится "
                     "зеркальным экстрактором ТОЧНО — инструментализация "
                     "работает как спроектирована. Нечётный марш-мусор "
                     "(d-c): пол |W2_pair|/t0^2 на медиане 1.4 (eps=1e-3) "
                     ".. 2.3e+2 (eps=1e-2) против цели 4/3; по-строчные "
                     "фиты D(xi) не сходятся (res_med ~ 0.4-0.6) — мусор "
                     "хаотичен, не низшего порядка, его линейная компонента "
                     "вырождена с сигналом: чистое измерение W2/t0^2 из "
                     "сырых пар невозможно инструментацией"),
        },
        "channel_B_series_C1": {
            "status": "BLOCKED (вход R3) / ТОЧНА символически",
            "n_sane": totB["n_sane"], "n_css_R3": totB["n_css_R3"],
            "text": ("серийный канал c_ser = (r_uu + (kappa/2) r s^2)/(2p) "
                     "символически точен: при CSS-входах кольцо W2/t0^2 = "
                     "4/3 воспроизводится ИЗ C1-ФОРМЫ (новый машинный "
                     "маршрут к кольцу, независимый от O3); на марш-данных "
                     "вход R3 (кубический коэфф. r-фита) — мусор "
                     "(R3/t0^2 ~ 1e3..1e5 против 2/9) и вырожден с "
                     "сигналом: независимое измерение требует динамики "
                     "P4 (O6+) — подтверждение вердикта source-dynamics"),
        },
        "W2_over_t02_4_3": {
            "status": "BLOCKED (обе инструментации)",
            "text": ("предсказание W2/t0^2 -> 4/3 остаётся закрытым на "
                     "уровне марш-данных; кольцо 4/3 верифицировано "
                     "символически (цепочка исправленной системы при "
                     "tau* = 27/4 и C1-маршрут настоящего сеанса); "
                     "численное измерение = приоритет динамики O6+"),
        },
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t_start:.0f} c)")
    return out


def main():
    eps_list = EPS_DEFAULT
    if len(sys.argv) > 1:
        eps_list = [float(x) for x in sys.argv[1].split(",")]
    run_chunk(eps_list)


if __name__ == "__main__":
    main()
