#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
NEAR-CRITICAL КАМПАНИЯ v8: ПРОВЕРКА ПРЕДСКАЗАНИЙ ГЕКСЦИКЛА
KAPPA = ln(64/9) И W2/t0^2 -> 4/3 НА ЛЕСТНИЦЕ EPS (TAU*-КАМПАНИЯ)
================================================================================

v8 = кампания поверх v6.1-машины (стабильные цепочки z~9.1-9.35) с ПОЛНОЙ
инструментацией измерений (solver._tay_diag_v8) и post-hoc анализом.

Что нового v8 (диагноз + механика):
  1. НАЙДЕН И ПОКАЗАН БАГ ЧАСОВ: tay["v_prev"] перезаписывался в chi-секции
     ДО вычисления dv_ode => dv_ode == 0 после первой строки стадии =>
     ОДУ O1/O3 мертвы (t0/d0 живут только через relax-каналы) =>
     замороженные tau-строки v6.1 (tau* = 3.3e-20, lambda_drift на краю
     сетки). Фикс — флаг tay_ode_fix (legacy не тронут).
  2. W2: сырой (d-c)-фит лежит под полом d-мусора на ~8 порядков
     (gates=cap на 100% строк). В динамике fix-режима — энфорсмент
     машино-верифицированного CSS-уравнения O3: W2* = kappa t0^2 - M3*/R1
     (chi=0: W2/t0^2 = 4/3 — кольцо гексцикла); отклонение измеряется
     каналами d0_field-дрейфа и dc-пары.
  3. LIVE-БАШНЯ (tay_ode_fix) — три механизма замыкания часов проверены
     и ОТКЛОНЕНЫ механически (разнос t0 за 1-2 стадии): слепой ОДУ с
     самореферентным P2; Риккати-часы s'=-1 в v стадии; часы ширины.
     Якорь E0_free отравлен перестройкой зоны (E_zone[0]=t0). Вывод:
     замыкание центра на этом усечении требует динамики P4 (O6+) —
     независимое подтверждение вердикта source-dynamics (O6-nsolve).

Проверяемые предсказания (hexcycle.json, без подгонки):
  kappa_cyc  = ln(64/9) = 1.9616585          (амплитудная книга цикла)
  W2/t0^2 -> 4/3 = 1/sqrt(tau5)              (кольцо гексагона)
  Delta_cyc  = 6 ln(16/9) = 3.4521849        (CSS-нормировка GHS 3.44±0.02)
  Delta_sp   = 7*pi/30   = 0.7330383         (нормировка кампании; отн. 4.7094)
  lambda+_tower(27/80) = 1.5090958           (замороженная башня — дефицит +0.45)

Каналы измерения (пост-хок, из СВЕЖИХ фитов каждой строки):
  tau_fresh = E0_free^4/(9 P2_fit^2) — та же книга, что в v6, но на свежих
  величинах (в v6 t0/P2 были замороженными реле). Часы:
  (a) z_cont_fresh = ln(1/s_est_fresh), s_est = |E0_free|/(3|P2_fit|);
  (b) z_fine — геометрические часы: лестница z_stage + внутри-стадийный
      лог-прогресс из уравнения часов CSS s' = -1 (s_stage = V_k/(1-e^-dz)):
      dz_within(x) = -ln(1 - x/C_k), x = v-прогресс по стадии.
  Фиты: модель A (a0 + A1 cos + A2 sin + c e^{-lam(z0-z)}) — цикл по
  аттрактору + транзиент; модель B (a0 + e^{+lam(z-z0)}(A1 cos + A2 sin)) —
  уход по неустойчивой моде (lambda+ => kappa). W2-каналы: raw/pair/d0-clock.

Запуск:
    python3 grid_machine_v8.py                # полная лестница eps
    python3 grid_machine_v8.py 1e-2,1e-3      # чанк
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

from zoom_solver import (ZoomRunner, echo_peaks, echo_period_from_peaks,
                         RESULTS, V_P, SIGMA)

BASE = os.path.dirname(os.path.abspath(__file__))
A_STAR = 0.0805333
DELTA_SP = 7.0 * np.pi / 30.0            # 0.7330383 (спинорная лестница)
GAMMA_LIT = 0.374
B_CH = 1.0 - np.cos(2.0 * np.pi / 7.0)
OUT_PATH = os.path.join(RESULTS, "grid_machine_v8.json")
EPS_DEFAULT = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
Z_WIN_ECHOES = 2.5

# --- предсказания гексцикла (results/hexcycle.json; БЕЗ подгонки) -----------
PRED = {
    "kappa_cyc": math.log(64.0 / 9.0),                     # 1.9616585
    "kappa_cyc_exact": "ln(64/9) = 2 ln(3/2) + 4 ln(4/3)",
    "W2_over_t02_target": 4.0 / 3.0,                       # кольцо = 1/sqrt(tau5)
    "Delta_cyc": 6.0 * math.log(16.0 / 9.0),               # 3.4521849 (CSS/GHS)
    "Delta_cyc_GHS_band": [3.42, 3.46],
    "delta_spinor": DELTA_SP,                              # 0.7330383
    "Delta_cyc_over_Delta_sp": 6.0 * math.log(16.0 / 9.0) / DELTA_SP,  # 4.7094
    "lambda_plus_tower_27_80": 1.5090958,                  # дефицит башни +0.45
    "gamma_cyc": DELTA_SP / math.log(64.0 / 9.0),          # 0.3736829
    "kappa_obs_gamma_lit": DELTA_SP / GAMMA_LIT,           # 1.9599954
    "kappa_obs_b_Ch": DELTA_SP / B_CH,                     # 1.9469281
    "note_clocks": ("Delta_cyc живёт в CSS-нормировке (GHS 3.44±0.02); "
                    "кампания измеряет Delta в своих часах (z_cont_fresh / "
                    "z_fine); отношение нормировок 4.7094 ~ delta_F — "
                    "книги, НЕ утверждается"),
}


# ==============================================================================
# 1. ИЗВЛЕЧЕНИЕ СТРОК (свежие фиты + диагностика v8)
# ==============================================================================
def stage_z_map(stage_constraints):
    zs = {0: 0.0}
    for c in stage_constraints:
        zs[int(c["zoom"])] = float(c["z"])
    return zs


def extract_rows_v8(tay_hist_all, zs, res_max=0.3):
    """Строки с диагностикой v8: свежие фиты + реле + часы + W2-каналы.

    Дедуп по (stage, v) — патч может писать несколько записей на строку.
    """
    rows = []
    seen = {}
    for rec in tay_hist_all:
        dg = rec.get("diag_v8")
        if dg is None:
            continue
        key = (int(rec.get("stage", 0)), round(float(rec["v"]), 12))
        # на строку может приходить несколько записей патча — держим
        # ПОСЛЕДНЮЮ (пост-перестройку; фиты свежее)
        seen[key] = rec
    for key, rec in seen.items():
        dg = rec["diag_v8"]
        t0 = rec.get("t0"); P2 = rec.get("P2")
        R1 = rec.get("R1"); d0 = rec.get("d0"); W2 = rec.get("W2")
        res_r = rec.get("res_r", float("nan"))
        res_E = rec.get("res_E", float("nan"))
        res_O = rec.get("res_O", float("nan"))
        if not all(np.isfinite(x) for x in (t0, P2, R1, d0, W2)):
            continue
        if not (np.isfinite(res_r) and res_r < res_max):
            continue
        if np.isfinite(resE := res_E) and resE >= res_max:
            continue
        if np.isfinite(resO := res_O) and resO >= res_max:
            continue
        E0 = rec.get("E0_free", float("nan"))
        if not np.isfinite(E0):
            continue
        p2_fresh = bool(np.isfinite(res_O))       # O-фит прошёл гейты
        e0_fresh = True                            # E-фит считается всегда
        stage = int(rec.get("stage", 0))
        rows.append({
            "v": float(rec["v"]), "stage": stage,
            "z_stage": float(zs.get(stage, 0.0)),
            "t0": float(t0), "P2": float(P2), "R1": float(R1),
            "d0": float(d0), "W2": float(W2),
            "E0_free": float(E0), "chi": float(rec.get("chi", 0.0)),
            "C0_gauge": float(rec.get("C0_gauge", float("nan"))),
            "res_r": float(res_r), "res_E": float(res_E), "res_O": float(res_O),
            "p2_fresh": p2_fresh,
            # свежие величины
            "s_est_fresh": abs(E0) / (3.0 * abs(P2)) if abs(P2) > 1e-300 else float("nan"),
            "W2_raw": float(dg["W2_raw"]), "W2_gate": dg["W2_gate"],
            "W2_cap": float(dg["W2_cap"]), "w_data": float(dg["w_data"]),
            "P2_raw": float(dg.get("P2_raw", float("nan"))),
            "d0_field": float(dg["d0_field"]),
            "dc_pair": [float(x) for x in dg["dc_pair"]],
            "xi_pair": [float(x) for x in dg["xi_pair"]],
            "t0_branch": dg["t0_branch"], "d0_branch": dg["d0_branch"],
            "dv_ode": float(dg["dv_ode"]),
            "M3_over_R1": float(dg["M3_over_R1"]),
            "W2_css": float(dg.get("W2_css", float("nan"))),
            "s_clock": float(dg.get("s_clock", float("nan"))),
        })
    return rows


def add_z_fine(rows):
    """Геометрические тонкие часы: z_fine = z_stage + dz_within(v-прогресс).

    Уравнение часов CSS: s' = -1 (база) => s_stage = V_k/(1 - e^{-dz_k}),
    dz_within(x) = -ln(1 - x/C_k), C_k = 1/(1 - e^{-dz_k}), x — v-прогресс.
    На стадии 0 (без зумов) dz_within = 0. Честная оговорка: фазовая рябь
    DSS-профиля в ширине/прогрессе — O(1) систематика часов.
    """
    if not rows:
        return rows
    # z-приросты стадий
    zmax_by_stage = {}
    for r in rows:
        zmax_by_stage[r["stage"]] = max(zmax_by_stage.get(r["stage"], 0.0),
                                        r["z_stage"])
    stages = sorted(zmax_by_stage)
    zgain = {}
    prev = 0.0
    for st in stages:
        zgain[st] = max(zmax_by_stage[st] - prev, 0.0)
        prev = zmax_by_stage[st]
    # v-диапазоны стадий
    vr = {}
    for r in rows:
        lo, hi = vr.get(r["stage"], (float("inf"), float("-inf")))
        vr[r["stage"]] = (min(lo, r["v"]), max(hi, r["v"]))
    for r in rows:
        st = r["stage"]
        lo, hi = vr[st]
        V = hi - lo
        dz = zgain[st]
        if V <= 0 or dz <= 1e-9:
            r["z_fine"] = r["z_stage"]
            continue
        C = 1.0 / (1.0 - math.exp(-dz))
        x = (r["v"] - lo) / V
        x = min(max(x, 0.0), 1.0)
        r["z_fine"] = r["z_stage"] - math.log(max(1.0 - x / C, 1e-9))
    return rows


# ==============================================================================
# 2. ФИТЫ (модель A: аттрактор+транзиент; модель B: уход по lambda+)
# ==============================================================================
def _design_A(z, delta, lam, z0):
    x = 2.0 * np.pi * z / delta
    E = np.exp(-lam * (z0 - z))
    return np.stack([np.ones_like(z), np.cos(x), np.sin(x), E], axis=1)


def _design_B(z, delta, lam, z0):
    x = 2.0 * np.pi * z / delta
    g = np.exp(lam * (z - z0))
    return np.stack([np.ones_like(z), g * np.cos(x), g * np.sin(x)], axis=1)


def _nested_fit(z, y, design, d_grid, l_grid):
    best = None
    for dz in d_grid:
        for lz in l_grid:
            A = design(z, dz, lz, z.max())
            if np.linalg.matrix_rank(A) < A.shape[1]:
                continue
            sol, *_ = np.linalg.lstsq(A, y, rcond=None)
            r = y - A @ sol
            rss = float(r @ r)
            if best is None or rss < best[0]:
                best = (rss, dz, lz, sol)
    return best


def _mad_filter(y, k=4.0):
    """Отбраковка выбросов: |y - med| > k*1.4826*MAD (робастно)."""
    med = np.median(y)
    mad = np.median(np.abs(y - med)) * 1.4826
    if mad <= 0:
        return np.ones(len(y), dtype=bool)
    return np.abs(y - med) <= k * mad


def fit_echo(rows, zkey="z_fine", model="A", win_echoes=Z_WIN_ECHOES,
             mid_offset=None, n_boot=200, seed=11):
    """Фит ln tau по выбранному окну и модели; возвращает tau*, Delta, lambda.

    tau_fresh — СЫРЫЕ фиты (E0_free, P2_raw до гейтов); гейты не режут строки
    (на глубоких строках метрика max-res гейта задавлена краем зоны),
    вместо этого — MAD-отбраковка выбросов внутри окна.
    """
    ok = [r for r in rows
          if np.isfinite(r.get("tau_fresh", float("nan")))
          and r["tau_fresh"] > 0 and np.isfinite(r.get(zkey, float("nan")))]
    if len(ok) < 12:
        return None
    zall = np.array([r[zkey] for r in ok])
    yall = np.log(np.array([r["tau_fresh"] for r in ok]))
    zmax = zall.max()
    if model == "A" and mid_offset is not None:
        m = (zall >= zmax - mid_offset - Z_WIN_ECHOES * DELTA_SP) & \
            (zall <= zmax - mid_offset)
    else:
        m = zall >= zmax - win_echoes * DELTA_SP
    z, y = zall[m], yall[m]
    mm = _mad_filter(y)
    z, y = z[mm], y[mm]
    if len(z) < 12:
        return None
    d_grid = np.linspace(0.45, 1.35, 46)
    if model == "A":
        l_grid = np.geomspace(0.05, 8.0, 40)
        design = _design_A
    else:
        l_grid = np.geomspace(0.3, 6.0, 40)
        design = _design_B
    best = _nested_fit(z, y, design, d_grid, l_grid)
    if best is None:
        return None
    rss, d_fit, l_fit, sol = best
    # bootstrap (полный вложенный поиск на прореженной сетке)
    rng = np.random.default_rng(seed)
    d_g2 = d_grid[::3]
    l_g2 = l_grid[::3]
    bs = []
    idx = np.arange(len(z))
    for _ in range(n_boot):
        sel = rng.choice(idx, size=len(idx), replace=True)
        b = _nested_fit(z[sel], y[sel], design, d_g2, l_g2)
        if b is not None:
            bs.append((b[1], b[2], b[3][0]))
    if bs:
        arr = np.array(bs)
        se_d = float(np.std(arr[:, 0]))
        se_l = float(np.std(arr[:, 1]))
        se_a0 = float(np.std(arr[:, 2]))
    else:
        se_d = se_l = se_a0 = float("nan")
    return {
        "model": model, "z_clock": zkey,
        "tau_star": float(np.exp(sol[0])),
        "tau_star_err_rel": se_a0,
        "Delta_fit": float(d_fit), "Delta_err": se_d,
        "lambda_fit": float(l_fit), "lambda_err": se_l,
        "wiggle_amp": float(np.hypot(sol[1], sol[2])),
        "n_rows": int(len(z)),
        "z_window": [float(z.min()), float(z.max())],
        "rss": rss,
    }


# ==============================================================================
# 3. W2-КАНАЛЫ (цель 4/3)
# ==============================================================================
def w2_channels(rows, zkey="z_fine", win_echoes=Z_WIN_ECHOES):
    if not rows:
        return None
    z = np.array([r.get(zkey, float("nan")) for r in rows])
    fin = np.isfinite(z)
    zmax = np.nanmax(z[fin]) if fin.any() else float("nan")
    m = fin & (z >= zmax - win_echoes * DELTA_SP)
    sel = [r for r, mm in zip(rows, m) if mm]
    if len(sel) < 5:
        return None
    out = {"n_rows": int(len(sel)), "target": 4.0 / 3.0}
    # ch1: сырой фит (до гейтов)
    v1 = np.array([r["W2_raw"] / r["t0"] ** 2 for r in sel
                   if abs(r["t0"]) > 1e-300])
    # ch2: dc-пара (нечётная часть внутренней пары)
    v2 = []
    for r in sel:
        (dc1, dc2), (x1, x2) = r["dc_pair"], r["xi_pair"]
        if abs(x1 - x2) > 1e-14 and all(np.isfinite([dc1, dc2, x1, x2])):
            v2.append(((dc1 - dc2) / (x1 - x2)) / r["t0"] ** 2)
    v2 = np.array(v2)
    # ch3: d0-clock (O3-согласованность по полю): W2 = dd0/dv - M3/R1 + 2 t0^2
    v3 = []
    for i in range(1, len(sel)):
        a, b = sel[i - 1], sel[i]
        if a["stage"] != b["stage"]:
            continue
        dv = b["v"] - a["v"]
        if dv <= 0:
            continue
        dd0 = b["d0_field"] - a["d0_field"]
        t0m = 0.5 * (abs(a["t0"]) + abs(b["t0"]))
        m3r = 0.5 * (a["M3_over_R1"] + b["M3_over_R1"])
        if t0m > 1e-300:
            v3.append((dd0 / dv - m3r + 2.0 * t0m ** 2) / t0m ** 2)
    v3 = np.array(v3)
    # ch4: реле (гейтованный фит — как в v6)
    v4 = np.array([r["W2"] / r["t0"] ** 2 for r in sel
                   if abs(r["t0"]) > 1e-300])

    def stat(arr):
        if arr.size == 0:
            return {"n": 0, "median": None, "p10": None, "p90": None}
        return {"n": int(arr.size),
                "median": float(np.median(arr)),
                "p10": float(np.percentile(arr, 10)),
                "p90": float(np.percentile(arr, 90))}

    out["ch_raw_fit"] = stat(v1)
    out["ch_dc_pair"] = stat(v2)
    out["ch_d0_clock"] = stat(v3)
    out["ch_relay_gated"] = stat(v4)
    # доля строк, где сырой фит прошёл башенный кап (живой сигнал)
    out["raw_pass_cap_frac"] = float(np.mean([
        1.0 if r["W2_gate"] == "" else 0.0 for r in sel]))
    return out


# ==============================================================================
# 4. КАМПАНИЯ
# ==============================================================================
def run_chunk(eps_list, n=800, max_zooms=14, annulus=True, ann_factor=10.0,
              march_center=True, r_ah_du=8.0, ann_relax_gate=0.5,
              ann_cross=True, live_probe=True, verbose=False):
    t_start = time.time()
    out = {
        "config": {"n": n, "max_zooms": max_zooms, "family": "gaussian",
                   "v_p": V_P, "sigma": SIGMA,
                   "annulus": annulus, "ann_factor": ann_factor,
                   "march_center": march_center, "r_ah_du": r_ah_du,
                   "ann_relax_gate": ann_relax_gate, "ann_cross": ann_cross,
                   "closure": "taylor (v5 patch) + annulus parity cross (v6.1); "
                              "динамика LEGACY (v6.1) + инструментация v8",
                   "eps_list_run": eps_list,
                   "live_probe": live_probe},
        "a_star": A_STAR,
        "a_star_source": "fixed-grid N=1600 bisection (validated, session 1)",
        "gamma_lit": GAMMA_LIT, "b_Ch": B_CH,
        "delta_spinor": DELTA_SP,
        "predictions": PRED,
        "runs": [],
    }

    print("=" * 72)
    print("КАМПАНИЯ v8 (tau*-проверка гексцикла): A* = %.7f" % A_STAR)
    print("  предсказания: kappa = ln(64/9) = %.6f | W2/t0^2 -> 4/3 | "
          "Delta_cyc = 6 ln(16/9) = %.4f" % (PRED["kappa_cyc"],
                                             PRED["Delta_cyc"]))
    print("=" * 72, flush=True)

    for eps in sorted(eps_list):
        A = A_STAR + eps
        t0 = time.time()
        r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose,
                       annulus=annulus, ann_factor=ann_factor,
                       march_center=march_center, r_ah_du=r_ah_du,
                       ann_relax_gate=ann_relax_gate, ann_cross=ann_cross,
                       tay_ode_fix=False, tay_diag_v8=True)
        d = r.run()
        rec = _summarize_run(r, d, eps, A, time.time() - t0)
        out["runs"].append(rec)
        print(f"  eps={eps:.1e}: stop={d.stopped}, zooms={d.zooms}, "
              f"z={r._z_acc:.2f}, rows={rec['n_rows']}, "
              f"tau_rows={rec['n_tau_fresh']}"
              f" [{time.time()-t0:.0f}s]", flush=True)

    # live-проба (задокументированный отказ live-башни)
    if live_probe:
        eps = 1e-2
        A = A_STAR + eps
        t0 = time.time()
        r = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose,
                       annulus=annulus, ann_factor=ann_factor,
                       march_center=march_center, r_ah_du=r_ah_du,
                       ann_relax_gate=ann_relax_gate, ann_cross=ann_cross,
                       tay_ode_fix=True, tay_diag_v8=True)
        d = r.run()
        lv = _summarize_run(r, d, eps, A, time.time() - t0)
        lv["leg"] = "live_tower (tay_ode_fix: dv-часы + W2_css + CSS-часы)"
        lv["verdict"] = (
            "live-башня заблокирована на этом усечении: три механизма "
            "замыкания часов (слепой ОДУ с самореферентным P2; Риккати "
            "s'=-1; часы ширины) дают разнос t0 за 1-2 стадии; якорь "
            "E0_free отравлен перестройкой зоны (E_zone[0]=t0). Требуется "
            "динамика P4 (O6+) — согласуется с вердиктом source-dynamics.")
        out["live_tower"] = lv
        print(f"  live-probe eps={eps:.1e}: stop={d.stopped}, "
              f"z={r._z_acc:.2f} (документированный отказ live-башни) "
              f"[{time.time()-t0:.0f}s]", flush=True)

    analyze_and_save(out)
    print(f"\nСохранено: {OUT_PATH} ({time.time()-t_start:.0f} c)")
    return out


def _summarize_run(r, d, eps, A, dt):
    zs = stage_z_map(d.stage_constraints)
    rows = extract_rows_v8(r.tay_hist_all, zs)
    rows = add_z_fine(rows)
    for row in rows:
        P2r = row["P2_raw"]
        ae, ap = abs(row["E0_free"]), abs(P2r) \
            if np.isfinite(P2r) else float("nan")
        if (np.isfinite(ae) and np.isfinite(ap)
                and 1e-300 < ae < 1e100 and ap > 1e-300):
            try:   # лог-пространство: E0^4 переполняет float на мусорных строках
                row["tau_fresh"] = math.exp(4.0 * math.log(ae)
                                            - 2.0 * math.log(ap)
                                            - math.log(9.0))
            except OverflowError:
                row["tau_fresh"] = float("nan")
        else:
            row["tau_fresh"] = float("nan")
        row["s_est_fresh"] = ae / (3.0 * ap) \
            if (np.isfinite(ap) and ap > 1e-300) else float("nan")
        row["z_cont_fresh"] = math.log(3.0 * ap / ae) if (
            np.isfinite(ae) and np.isfinite(ap)
            and 1e-300 < ae < 1e100 and ap > 1e-300) else float("nan")
    tr = r.track
    vp, yp = echo_peaks(r.track, "Q")
    rec = {
        "leg": "legacy+diag (v6.1 динамика)",
        "eps": eps, "A": A,
        "stop": d.stopped,
        "M_AH_frozen": float(d.m_ah),
        "M_AH_max_seen": float(d.m_ah_max),
        "zooms": d.zooms, "z_reached": float(r._z_acc),
        "mx_max": float(np.nanmax(tr["mx"])) if len(tr["mx"]) else 0.0,
        "runtime_s": round(dt, 1),
        "stage_constraints": [
            {"zoom": c["zoom"], "lam": round(c["lam"], 3),
             "z": round(c["z"], 4), "c1_max": c["c1_max"]}
            for c in d.stage_constraints],
        "Q_peaks_n": int(len(vp)),
        "n_rows": len(rows),
        "n_tau_fresh": int(sum(1 for x in rows
                               if np.isfinite(x.get("tau_fresh", float("nan"))))),
    }
    if len(vp) >= 4:
        D, Derr, npk = echo_period_from_peaks(vp)
        rec["Delta_ln_intervals"] = {"Delta": float(D), "err": float(Derr),
                                     "n": int(npk)}
    # часы: согласованность z_cont_fresh vs z_fine
    zf = np.array([x["z_fine"] for x in rows]) if rows else np.array([])
    zc = np.array([x["z_cont_fresh"] for x in rows]) if rows else np.array([])
    okc = np.isfinite(zf) & np.isfinite(zc)
    if okc.sum() >= 10:
        A1 = np.stack([zc[okc], np.ones_like(zc[okc])], axis=1)
        (sl, ic), *_ = np.linalg.lstsq(A1, zf[okc], rcond=None)
        rec["clock_check"] = {
            "z_fine_vs_z_cont_fresh": {"slope": float(sl),
                                       "intercept": float(ic)},
            "n": int(okc.sum())}
    # фиты эха
    fits = {}
    for zkey in ("z_cont_fresh", "z_fine"):
        for mdl, off in (("A", None), ("A", 1.0), ("B", None)):
            f = fit_echo(rows, zkey=zkey, model=mdl, mid_offset=off)
            if f:
                fits[f"{mdl}@{zkey}" + ("_mid" if off else "_deep")] = f
    rec["echo_fits"] = fits
    rec["w2_channels"] = w2_channels(rows, zkey="z_fine")
    if w2c := w2_channels(rows, zkey="z_cont_fresh"):
        rec["w2_channels_zcont"] = w2c
    # компактная выборка строк (глубокое окно + прореживание)
    if rows:
        zc2 = np.array([x["z_fine"] for x in rows])
        deep = zc2 >= np.nanmax(zc2) - 4.0 * DELTA_SP
        sel = [x for i, x in enumerate(rows) if deep[i] or i % 4 == 0]
        rec["rows_sample"] = sel[:2500]
        rec["rows_kept"] = len(sel)
    # ветки эволюции (диагностика часов)
    if rows:
        tb, db, gv = {}, {}, []
        for x in rows:
            tb[x["t0_branch"]] = tb.get(x["t0_branch"], 0) + 1
            db[x["d0_branch"]] = db.get(x["d0_branch"], 0) + 1
            gv.append(abs(x["dv_ode"]))
        rec["branch_stats"] = {"t0": tb, "d0": db,
                               "dv_ode_nonzero_frac":
                                   float(np.mean([1.0 if g > 1e-14 else 0.0
                                                  for g in gv]))}
    return rec


# ==============================================================================
# 5. СВОДНЫЙ АНАЛИЗ + ВЕРДИКТЫ
# ==============================================================================
def analyze_and_save(out):
    runs = [r for r in out["runs"] if r.get("rows_sample")]
    out["verdicts"] = {}

    # --- объединённый фит (все забеги, z_fine) -------------------------------
    all_rows = []
    for r_ in runs:
        all_rows.extend(r_.get("rows_sample", []))
    fB = fit_echo(all_rows, zkey="z_fine", model="B")
    fA = fit_echo(all_rows, zkey="z_fine", model="A")
    fAm = fit_echo(all_rows, zkey="z_fine", model="A", mid_offset=1.0)
    out["tau_star_global"] = {"model_B_deep_zfine": fB, "model_A_deep_zfine": fA,
                              "model_A_mid_zfine": fAm}

    # --- вердикт kappa -------------------------------------------------------
    def kappa_from(fit):
        if not fit:
            return None
        d, l = fit["Delta_fit"], fit["lambda_fit"]
        if not (np.isfinite(d) and np.isfinite(l)) or d <= 0 or l <= 0:
            return None
        kappa = DELTA_SP * l / d
        return {
            "lambda_fit": l, "lambda_err": fit.get("lambda_err"),
            "Delta_fit": d, "Delta_err": fit.get("Delta_err"),
            "kappa_meas": kappa,
            "kappa_target_ln64_9": PRED["kappa_cyc"],
            "dev_pct": 100.0 * (kappa - PRED["kappa_cyc"]) / PRED["kappa_cyc"],
            "lambda_vs_tower_1p5091_pct":
                100.0 * (l - PRED["lambda_plus_tower_27_80"])
                / PRED["lambda_plus_tower_27_80"],
        }
    out["verdicts"]["kappa_ln64_9"] = {
        "source": "модель B (уход по неустойчивой моде), часы z_fine",
        "measured": kappa_from(fB),
        "status": "blocked",
        "status_note": ("lambda_fit на нижнем крае сетки (0.3): уход по "
                        "неустойчивой моде в глубоком окне НЕ растёт "
                        "(решение сидит на предельном цикле DSS; разрул "
                        "— в самом конце цепочки, где данные уже мусор). "
                        "kappa_meas = 0.32 — НЕ измерение, а верхний/нижний "
                        "артефакт сетки. Канал требует P4-динамики (O6+) "
                        "и/или надёжного M(eps) (AH-захват)."),
    }
    # --- вердикт Delta -------------------------------------------------------
    dA = (fA or {}).get("Delta_fit")
    dB = (fB or {}).get("Delta_fit")
    d_ind = None
    devs = []
    for dv_ in (dA, dB):
        if dv_ and np.isfinite(dv_):
            devs.append(100.0 * (dv_ - DELTA_SP) / DELTA_SP)
    if devs:
        d_ind = {
            "Delta_fits_z_fine": [dA, dB],
            "dev_vs_Delta_sp_pct": devs,
            "status": "indicative",
            "status_note": ("Delta_fit ~ 0.67-0.77 vs Delta_sp = 0.733 "
                            "(-9...+5%), но книга tau_fresh шумна "
                            "(amp ~ 2.5-3.5 в ln tau; E0_free-экстраполяция "
                            "отравлена рядом зоны) — индикатор, не измерение"),
        }
    # геометрический канал: Q-пики (точные интервалы лестницы зумов)
    dq = None
    for r_ in runs:
        di = r_.get("Delta_ln_intervals")
        if di and di.get("n", 0) >= 3:
            dq = {"eps": r_["eps"], **di,
                  "ratio_to_Delta_cyc": di["Delta"] / PRED["Delta_cyc"],
                  "note": ("часы лестницы зумов; отношение к Delta_cyc "
                           "(CSS-нормировка) ~ 2 — удвоение пирамиды в "
                           "книге гексцикла, индикативно (ошибка 26%)")}
    out["verdicts"]["Delta_clock"] = {
        "delta_spinor_target": DELTA_SP,
        "delta_cyc_css_norm": PRED["Delta_cyc"],
        "measured_deep_A": dA,
        "measured_mid_A": (fAm or {}).get("Delta_fit"),
        "measured_B": dB,
        "indicative": d_ind,
        "Delta_Qpeaks_geometric": dq,
        "note": ("сравнение с Delta_sp требует ОДНОЙ нормировки часов; "
                 "фазовая рябь + нормировка книг — систематика"),
    }
    # --- вердикт W2 ----------------------------------------------------------
    w2g = None
    for r_ in runs:
        w = r_.get("w2_channels")
        if w and w["n_rows"] >= 5:
            w2g = w
    out["verdicts"]["W2_over_t02_4_3"] = {
        "target": 4.0 / 3.0,
        "channels_deep_window": w2g,
        "status": ("measured" if w2g and w2g["ch_dc_pair"]["n"] >= 5
                   and w2g["raw_pass_cap_frac"] > 0.5 else
                   "blocked — (d-c)-сигнал под полом d-мусора; "
                   "см. honest_notes"),
    }
    # --- лестница eps --------------------------------------------------------
    out["eps_ladder"] = [
        {"eps": r_["eps"], "z_reached": r_["z_reached"],
         "zooms": r_["zooms"], "stop": r_["stop"],
         "n_tau_fresh": r_.get("n_tau_fresh", 0),
         "Delta_Qpeaks": r_.get("Delta_ln_intervals")}
        for r_ in out["runs"]]
    # --- honest notes ---------------------------------------------------------
    out["honest_notes"] = [
        "Динамика кампании — LEGACY v6.1 (замороженные часы): стабильно, "
        "z~9.1; live-башня (dv-фикс + CSS-энфорсмент) — задокументированный "
        "отказ (самореферентность зоны, три механизма замыкания часов).",
        "НАЙДЕН БАГ ЧАСОВ v5-v6.1: tay[v_prev] перезаписывался до dv_ode => "
        "ОДУ O1/O3 мертвы после первой строки стадии (фикс — флаг "
        "tay_ode_fix; legacy воспроизведён: z=9.10, 5 зумов).",
        "Механика заморозки книги: гейты E/O-фитов падают на глубоких "
        "строках по max-res (динамический диапазон края зоны ~1000) => "
        "P2/W2 реле замораживаются с первой стадии; tau-книга v6.1 — "
        "замороженный артефакт (tau* = 3.3e-20).",
        "tau_fresh v8 — на сырых фатах (E0_free, P2_raw до гейтов): строки "
        "живые, но шумные (E0_free отравлен рядом зоны: значения до -1.2 "
        "при физическом t0 ~ 1e-3) — центральная книга на этой сетке "
        "всегда серия-опосредована (стена v5, переоткрыта на уровне P4).",
        "W2: сырой (d-c)-фит под полом d-мусора (~1e13 t0^2; gates=cap "
        "100% строк); каналы dc-пара/d0-clock — тот же пол. В динамике "
        "live-башни W2 энфорсится CSS-уравнением (W2* = kappa t0^2 - M3*/R1; "
        "chi=0: 4/3 — кольцо гексцикла), отклонение не разрешимо.",
        "M3/(R1 t0^2) в v6+ энфорсится торновской связкой — тавтология.",
        "M_AH не ловится (M_frozen=0) => gamma-wiggle по M(eps) недоступен.",
        "часы z_fine: уравнение часов CSS s'=-1 + телескопирование зумов; "
        "фазовая рябь DSS — O(1) систематика (slope z_fine/z_cont_fresh "
        "~ 0.71 — рассогласование нормировок часов видно в данных).",
    ]
    # --- печать ---------------------------------------------------------------
    print("\n===== СВОДКА v8 =====")
    zmax = max((r_["z_reached"] for r_ in out["runs"]), default=0.0)
    print(f"z_max = {zmax:.2f}; строк с tau_fresh: "
          f"{sum(r_.get('n_tau_fresh', 0) for r_ in out['runs'])}")
    kk = out["verdicts"]["kappa_ln64_9"]["measured"]
    print(f"[kappa] status: {out['verdicts']['kappa_ln64_9']['status']}")
    if kk:
        print(f"  lambda={kk['lambda_fit']:.4f}, Delta={kk['Delta_fit']:.4f} "
              f"(край сетки — уход не разрешён; kappa_meas={kk['kappa_meas']:.3f} "
              "— артефакт, не измерение)")
    dc = out["verdicts"]["Delta_clock"].get("indicative")
    if dc:
        print(f"[Delta] indicative: {dc['Delta_fits_z_fine']} vs Delta_sp="
              f"{DELTA_SP:.4f} (dev {['%+.1f%%' % x for x in dc['dev_vs_Delta_sp_pct']]})")
    dq = out["verdicts"]["Delta_clock"].get("Delta_Qpeaks_geometric")
    if dq:
        print(f"[Delta/Q-пики] геометрические часы: {dq['Delta']:.3f}+-"
              f"{dq['err']:.3f} (n={dq['n']}), /Delta_cyc = "
              f"{dq['ratio_to_Delta_cyc']:.2f}")
    if w2g:
        for ch in ("ch_raw_fit", "ch_dc_pair", "ch_d0_clock", "ch_relay_gated"):
            s = w2g.get(ch)
            if s and s["n"]:
                print(f"[W2/{ch}] med={s['median']:.4g} "
                      f"[{s['p10']:.3g}; {s['p90']:.3g}] (n={s['n']}, "
                      f"цель 4/3=1.333)")

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    return out


def main():
    eps_list = EPS_DEFAULT
    if len(sys.argv) > 1:
        eps_list = [float(x) for x in sys.argv[1].split(",")]
    run_chunk(eps_list)


if __name__ == "__main__":
    main()
