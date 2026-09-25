#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
СПИНОРНАЯ ЛЕСТНИЦА DSS: ПОКАЗАТЕЛИ pi/15 И pi/30, СКЭЛЛИНГ ПАРАМЕТРОВ (v5)
SPINOR LADDER OF DSS: THE pi/15 AND pi/30 EXPONENTS, PARAMETER SCALING
================================================================================

Фундаментальный уровень (указание автора монографии): цепочку эхо проходят
СПИНОРНЫЕ ФУНКЦИИ с показателями pi/15 и pi/30 со скэллингом параметров.
Взрывы (распады/сборки) обязаны происходить — это частные (критические)
случаи уравнений Эйнштейна; для стабильных мод нужны выводы фундаментальных
уровней — они выполнены в sympy_center.py (иерархия O1-O5 верифицирована
SymPy: связки чётной (E) и нечётной (спинорной O) мод у центра).

ЧТО ДЕЛАЕТ МОДУЛЬ
-----------------
1. ФАЗОВАЯ ЛЕСТНИЦА: квант лестницы dzeta = pi/30; эхо = 7 квантов
   (Delta = 7*pi/30); показатели pi/15 = 2 кванта и pi/30 = 1 квант.
   Для каждой частоты: период в dzeta, число эхо на период, набранная фаза
   на достигнутой глубине z, вердикт разрешимости (нужно >= 1.5 периода).

2. СКЭЛЛИНГ ПАРАМЕТРОВ: из тейлор-гистограмм цепочки зумов (t0(v), P2(v),
   d0(v) на каждой строке каждой стадии) фнятся скорости роста мод:
       kappa_t0 = d ln|t0|/dz,   kappa_P2 = d ln|P2|/dz,   kappa_d0,
   и сравниваются с ожиданиями CSS/DSS (фон: t0 ~ e^z, кривизна Q ~ e^2z,
   растущая мода: kappa ~ 2.87 — литература).

3. ГАРМОНИКИ ЭХО: фит ln Q(dzeta) = a + b*dzeta + сумма k [c_k cos + s_k sin]
   (k=1,2) по пикам кривизны — амплитуда виггling-моды; честный вердикт
   о разрешимости спинорных частот pi/15, pi/30 на достигнутой глубине.

4. СВЯЗКИ ФУНДАМЕНТАЛЬНОГО УРОВНЯ (из sympy_center.json): O1, O3, O5 —
   таблица связок E<->O мод; численные невязки O1/O2 по гистограммам
   (проверка фундаментальных ОДУ на глубокой цепочке).

Запуск:  python3 spinor_ladder.py        # ~5-15 мин (2 цепочки зумов)
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from zoom_solver import ZoomRunner, echo_peaks, RESULTS, V_P, SIGMA

A_FIXED_GRID = 0.0805333
GAMMA_LIT = 0.374
DELTA_LIT = 0.737637
DELTA_SP = 7.0 * np.pi / 30.0
KAPPA_LIT = 2.87
B_CH = 1.0 - np.cos(2.0 * np.pi / 7.0)
DZETA_QUANT = np.pi / 30.0          # квант спинорной лестницы
PHI15 = np.pi / 15.0                # показатель спинорной функции (2 кванта)
PHI30 = np.pi / 30.0                # показатель спинорной функции (1 квант)

OUT_PATH = os.path.join(RESULTS, "spinor_ladder.json")
EPS_LIST = [1e-4, 1e-3]


# ------------------------------------------------------------------------------
# 1. Фазовая лестница
# ------------------------------------------------------------------------------
def phase_ladder(z_reached, delta=None, n_echoes=None):
    """Таблица спинорных частот: период, эхо на период, фаза на глубине z."""
    if delta is None:
        delta = DELTA_SP
    freqs = {
        "pi/30 (1 квант, фундаментальный)": PHI30,
        "pi/15 (2 кванта, спинорный)": PHI15,
        "Delta = 7*pi/30 (эхо)": delta,
        "4*pi/Delta (виггling)": 4.0 * np.pi / delta,
    }
    rows = []
    for name, om in freqs.items():
        period = 2.0 * np.pi / om
        echoes = period / delta
        phase_gain = om * z_reached
        rows.append({
            "frequency": name, "omega": float(om),
            "period_in_zeta": float(period),
            "echoes_per_period": float(echoes),
            "phase_gained_at_z": float(phase_gain),
            "periods_covered_at_z": float(phase_gain / (2.0 * np.pi)),
            "resolvable": bool(phase_gain >= 1.5 * 2.0 * np.pi),
        })
    return {
        "delta_used": float(delta),
        "zeta_quantum": float(DZETA_QUANT),
        "quanta_per_echo": float(delta / DZETA_QUANT),
        "z_reached": float(z_reached),
        "n_echoes_estimate": float(z_reached / delta),
        "rows": rows,
        "note": ("Разрешимость спинорной модуляции требует >= 1.5 периода "
                 "модуляции (>= 3 точек на период). Для pi/30 это "
                 "~82 эха (z >= 60), для pi/15 ~41 эхо (z >= 30)."),
    }


# ------------------------------------------------------------------------------
# 2. Скэллинг параметров: скорости роста мод из тейлор-гистограмм
# ------------------------------------------------------------------------------
def mode_scaling(tay_hist):
    """kappa_mode = d ln|coef| / dz по гистограмме Тейлор-патча.

    tay_hist: список rec с ключами v, t0, P2, d0, stage (v5-гистограммы
    всех стадий). z каждой строки аппроксимируется как z последней строки
    стадии (гистограммы стадий разделены скачком зума).
    Возвращает dict с наклонами и rms.
    """
    if len(tay_hist) < 20:
        return None
    v = np.array([r["v"] for r in tay_hist])
    st = np.array([r["stage"] for r in tay_hist])
    t0 = np.abs(np.array([r["t0"] for r in tay_hist])) + 1e-300
    P2 = np.abs(np.array([r["P2"] for r in tay_hist])) + 1e-300
    d0 = np.abs(np.array([r["d0"] for r in tay_hist])) + 1e-300
    # z-метка: кумулятивное число стадий * Delta + ln(v*)-подобная метка;
    # для скорости роста используем ПРОСТУЮ метку: zeta ~ -ln(v* - v) с
    # v* = v_max + последний интервал (грубая оценка точки накопления)
    v_star = v[-1] + max(v[-1] - v[-2], 1e-12)
    zeta = -np.log(np.clip(v_star - v, 1e-300, None))
    out = {"n_rows": int(len(v)), "v_star_est": float(v_star)}
    for name, y in (("t0", t0), ("P2", P2), ("d0", d0)):
        ok = np.isfinite(y) & (y > 0) & np.isfinite(zeta)
        if int(ok.sum()) < 10:
            out[name] = None
            continue
        # фит ln y = a + kappa * zeta (устойчивый к скачкам стадий чипом)
        A = np.vstack([zeta[ok], np.ones(int(ok.sum()))]).T
        sol_, *_ = np.linalg.lstsq(A, np.log(y[ok]), rcond=None)
        resid = np.log(y[ok]) - A @ sol_
        out[name] = {"kappa": float(sol_[0]),
                     "rms_ln": float(np.sqrt((resid ** 2).mean()))}
    return out


# ------------------------------------------------------------------------------
# 3. Гармоники эхо (виггling) по пикам кривизны
# ------------------------------------------------------------------------------
def echo_harmonics(v_peaks, q_peaks, delta=None, n_harm=2):
    """Фит ln Q_n = a + b*zeta_n + sum_k [c_k cos + s_k sin](2pi k zeta_n/Delta).

    zeta_n = -ln(v* - v_n); v* сканируется. Возвращает лучший фит.
    """
    if delta is None:
        delta = DELTA_SP
    vp = np.asarray(v_peaks, float)
    qp = np.asarray(q_peaks, float)
    if len(vp) < 6:
        return None
    v_last = vp[-1]
    best = None
    for f in np.linspace(1.02, 3.0, 200):
        v_star = v_last + (f - 1.0) * (vp[-1] - vp[0]) * 0.5
        zeta = -np.log(v_star - vp)
        cols = [zeta, np.ones_like(zeta)]
        for k in range(1, n_harm + 1):
            cols.append(np.cos(2.0 * np.pi * k * zeta / delta))
            cols.append(np.sin(2.0 * np.pi * k * zeta / delta))
        A = np.vstack(cols).T
        sol_, *_ = np.linalg.lstsq(A, np.log(qp), rcond=None)
        resid = np.log(qp) - A @ sol_
        rms = float(np.sqrt((resid ** 2).mean()))
        if best is None or rms < best["rms"]:
            best = {"rms": rms, "v_star": float(v_star),
                    "slope_b": float(sol_[0]),
                    "harmonics": {f"k{k}": {"c": float(sol_[1 + 2 * k]),
                                            "s": float(sol_[2 + 2 * k])}
                                  for k in range(1, n_harm + 1)},
                    "n_peaks": int(len(vp))}
    return best


# ------------------------------------------------------------------------------
# 4. Численные невязки фундаментальных ОДУ O1/O2 на глубокой цепочке
# ------------------------------------------------------------------------------
def ode_residuals(tay_hist):
    """Одношаговые невязки O1 (t0' = 3P2 - 4d0 t0) и O3
    (d0' = M3/R1 + W2 - kappa t0^2) по гистограммам (внутри стадий)."""
    res = {"O1": [], "O3": []}
    for i in range(1, len(tay_hist)):
        a, b = tay_hist[i - 1], tay_hist[i]
        if a.get("stage") != b.get("stage"):
            continue                      # скачок зума — пропускаем
        dv = b["v"] - a["v"]
        if dv <= 0:
            continue
        f1 = 3.0 * a["P2"] - 4.0 * a["d0"] * a["t0"]
        f2 = 3.0 * b["P2"] - 4.0 * b["d0"] * b["t0"]
        t0p = a["t0"] + 0.5 * dv * (f1 + f2)
        sc = max(abs(a["t0"]), abs(b["t0"]), 1e-12)
        res["O1"].append(abs(b["t0"] - t0p) / sc)
        if a.get("R1") and a["R1"] > 0:
            g1 = a["M3"] / a["R1"] + a["W2"] - 2.0 * a["t0"] ** 2
            g2 = b["M3"] / b["R1"] + b["W2"] - 2.0 * b["t0"] ** 2
            d0p = a["d0"] + 0.5 * dv * (g1 + g2)
            scd = max(abs(a["d0"]), abs(b["d0"]), 1e-12)
            res["O3"].append(abs(b["d0"] - d0p) / scd)
    out = {}
    for k, v in res.items():
        v = [x for x in v if np.isfinite(x)]
        if v:
            out[k] = {"n": len(v), "median": float(np.median(v)),
                      "p90": float(np.percentile(v, 90))}
        else:
            out[k] = None
    return out


# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
def main():
    t0w = time.time()
    out = {
        "config": {"family": "gaussian", "v_p": V_P, "sigma": SIGMA,
                   "a_star_fixed_grid": A_FIXED_GRID, "eps_list": EPS_LIST},
        "literature": {"gamma": GAMMA_LIT, "delta": DELTA_LIT,
                       "kappa_screaming": KAPPA_LIT},
        "spinor_framework": {
            "b_Ch": B_CH, "Delta_spinor": DELTA_SP,
            "zeta_quantum_pi_over_30": float(DZETA_QUANT),
            "phi15": float(PHI15), "phi30": float(PHI30),
            "quanta_per_echo": float(DELTA_SP / DZETA_QUANT),
            "R3_omega_wiggle_120_over_7": float(4 * np.pi / DELTA_SP),
        },
        "runs": [],
        "honest_limits": [],
    }

    for eps in EPS_LIST:
        A = A_FIXED_GRID + eps
        print(f"[run] eps={eps:.1e}: цепочка зумов (v5, Тейлор-патч)...",
              flush=True)
        r = ZoomRunner(A=A, n=800, max_zooms=12, verbose=False)
        d = r.run()
        rec = {"eps": eps, "A": A, "zooms": d.zooms,
               "z_reached": float(r._z_acc), "stop": d.stopped,
               "M_AH_max": float(d.m_ah_max), "n_tay_rows": len(r.tay_hist_all)}
        # 1. лестница
        rec["ladder"] = phase_ladder(r._z_acc)
        # 2. скэллинг параметров
        rec["mode_scaling"] = mode_scaling(r.tay_hist_all)
        # 3. гармоники эхо
        vp, yp = echo_peaks(r.track, "Q")
        rec["n_Q_peaks"] = int(len(vp))
        if len(vp) >= 6:
            rec["echo_harmonics"] = echo_harmonics(vp, yp)
        # 4. невязки фундаментальных ОДУ
        rec["ode_residuals"] = ode_residuals(r.tay_hist_all)
        out["runs"].append(rec)
        ms = rec["mode_scaling"]
        print(f"    z={r._z_acc:.2f}, zooms={d.zooms}, stop={d.stopped}; "
              f"kappa_t0={ms['t0']['kappa']:.3f} " if ms and ms.get("t0") else
              f"    z={r._z_acc:.2f}, zooms={d.zooms}, stop={d.stopped}; "
              f"taylor-строк={len(r.tay_hist_all)}", flush=True)

    # --- сводка и честные пределы ------------------------------------------
    z_max = max(r_["z_reached"] for r_ in out["runs"])
    out["summary"] = {
        "z_max": z_max,
        "echoes_max": z_max / DELTA_SP,
        "pi15_resolvable": bool(z_max >= 30.0),
        "pi30_resolvable": bool(z_max >= 60.0),
    }
    out["honest_limits"] = [
        "Спинорные частоты pi/15 и pi/30 на достигнутой глубине "
        f"(z_max = {z_max:.1f} ~ {z_max/DELTA_SP:.0f} эхо) НЕ разрешимы: "
        "нужно z >= 30 (pi/15) и z >= 60 (pi/30). Лестница построена, "
        "модуляция не измерялась — честный вердикт.",
        "Скэллинг параметров (kappa_t0, kappa_P2) — измерение по цепочке "
        "с грубой zeta-меткой (v* не уточняется): считать порядком величины.",
        "Фундаментальные связки E<->O (O1-O5, sympy_center.json) верифицированы "
        "символьно; их ЧИСЛЕННЫЕ невязки на глубокой цепочке — диагностическая "
        "таблица, а не фит.",
        "Взрывы (распады/сборки) у части решений — ожидаемая физика частных "
        "случаев; стоп-критерии зум-машины отделяют их от стабильных мод "
        "по вердикту (AH-formation vs junk-взрыв).",
    ]
    out["runtime_s"] = round(time.time() - t0w, 1)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"Сохранено: {OUT_PATH}")
    return out


if __name__ == "__main__":
    main()
