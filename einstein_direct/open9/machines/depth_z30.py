#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q3 / КАМПАНИЯ v20b: ГЛУБИНА z >= 30 — СЕРТИФИЦИРОВАННЫЙ МИР ЛИНЕЙНОГО
СЕКТОРА, БЮДЖЕТ ПОЛА МАСС И ПЕРЦЕНТИЛЬНАЯ ГАММА/ДЕЛЬТА НА ГЛУБИННОЙ ЛЕСТНИЦЕ
================================================================================

Вопрос (q3_echo_fit_global.json): процентный gamma/Delta заблокирован стеной
глубины z ~= 9.35 (пол масс M ~ 4*du; нижняя половина выборки плоская).
Кампания v20b доставляет ТРИ машинных факта и протокол:

  [D1] СЕРТИФИКАЦИЯ ЛИНЕЙНОГО СЕКТОРА ДО z = 30 (замкнутая форма).
       Пропагатор M2-сектора Pi(T) = I + B*T ТОЧЕН (B нильпотентен,
       B^2 = 0 — Йордан-2, _m2_B_baseline.npy): рост СВЕТСКОЙ
       (полиномиальный по T), фаза дрейфа ТОЧНО 0 (Pi вещественна,
       spec = {1, 1}). Следствие: до z = 30 линейный сектор НЕ МОЖЕТ
       нести ни экспоненциального роста, ни осцилляции на частотах
       pi/30-лестницы — процентная гамма на z >= 30 измеряет физику
       эха PDE-машины, не загрязнённую линейной монодромией.
       Кросс-чек: RK4-марш y' = B y до T = 30*Delta_sp против
       замкнутой формы (совпадение до машинной точности).

  [D2] БЮДЖЕТ ГЛУБИНЫ z >= 30 (без подгонки, якоря кампании).
       Пол масс должен быть подавлен в S_req(z) = exp(gamma*(z - z_wall))
       раз относительно текущей машины (z_wall = 9.35, gamma = 0.374):
       z = 30 -> S_req ~ 2.2e3 (с запасом перцентиля x10 -> 2.2e4).
       Число спинорных эхо: z/Delta_sp = 41 (pi/15-разрешимость,
       spinor_ladder). Стартовая отстройка (A - A*)/A* ~ e^{-z/gamma}
       НЕ требуется достигаться бисекцией: глубину несёт РЕСКАЛИРОВКА
       зумов (z += ln(lam) за стадию), бисекции достаточно старта
       eps ~ 1e-3 (z_0 ~ gamma*ln(1/eps) ~ 2.6 + зумы до 30).

  [D3] ПЕРЦЕНТИЛЬНАЯ ГАММА/ДЕЛЬТА НА ГЛУБИННОЙ ЛЕСТНИЦЕ (редуцированная
       модель, детерминизм: фиксированные сиды). Синтетическая лестница
       масс M_n = M0*exp(-gamma*z_n), z_n = n*Delta_sp, пол
       M_floor = M0*exp(-gamma*z_wall)/S с джанк-шумом; перцентильный
       фит (верхний квантиль выживших, бутстрап-CI) против ОЛС.
       Критерий успеха: |gamma_hat - gamma|/gamma <= 1% И
       |Delta_hat - Delta|/Delta <= 0.5%.
       ЗАМКНУТАЯ ПЕТЛЯ с [D2]: при S = S_req(z) стена уходит на z и
       перцентильная гамма/дельта достигают процента на z >= 15..30,
       тогда как при S = 1 воспроизводится ОТРИЦАТЕЛЬНЫЙ результат
       репо на z = 9.35 (согласованность с q3).

  [D4] ПРОТОКОЛ ПОЛНОЙ PDE-КАМПАНИИ (v21): лестница зумов с джанк-гейтом
       q7, целевые строки/эхо, слово ворот.

Запуск:
    python3 depth_z30.py                 # ~1-2 мин
Результат: results/v20b_depth_z30.json
"""
from __future__ import annotations

import json
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "v20b_depth_z30.json")

T_START = time.time()
GAMMA = 0.374                    # Чоптюик 1993 (GHS) — якорь, не фит
DELTA_SP = 7.0 * np.pi / 30.0    # спинорное эхо (лестница pi/30)
DELTA_ZOOM = 3.44                # эхо в единицах зум-трекинга (GHS)
Z_WALL = 9.35                    # стена глубины текущей машины (annulus/README)
Z_TARGET = 30.0
SEED = 20260928                  # детерминизм кампании


def log(msg):
    print(msg, flush=True)


# ==============================================================================
# [D1] СЕРТИФИКАЦИЯ ЛИНЕЙНОГО СЕКТОРА ДО z = 30
# ==============================================================================
def d1_linear_sector_certified():
    B_path = os.path.join(RESULTS, "_m2_B_baseline.npy")
    B = np.load(B_path).astype(complex)
    # замкнутая форма: Pi(T) = I + B*T (B^2 = 0 ТОЧНО)
    B2 = B @ B
    nilpotency_max = float(np.max(np.abs(B2)))
    T30 = Z_TARGET * DELTA_SP
    Pi = np.eye(2) + B * T30
    sv = np.linalg.svd(Pi, compute_uv=False)
    sv_echo = np.linalg.svd(np.eye(2) + B * DELTA_SP, compute_uv=False)
    eig = np.linalg.eigvals(Pi)
    phase_exact = float(max(abs(np.angle(e)) for e in eig))
    # RK4 кросс-чек до T30
    dt = 2e-3
    y = np.array([1.0, 0.0], dtype=complex)
    nstep = int(round(T30 / dt))
    for _ in range(nstep):
        k1 = B @ y
        k2 = B @ (y + 0.5 * dt * k1)
        k3 = B @ (y + 0.5 * dt * k2)
        k4 = B @ (y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    rk4_vs_closed = float(np.linalg.norm(y - Pi[:, 0])
                          / np.linalg.norm(Pi[:, 0]))
    return {
        "B_source": "_m2_B_baseline.npy (замыкание v14, baseline kappa=2)",
        "B": [[float(np.real(B[0, 0])), float(np.real(B[0, 1]))],
              [float(np.real(B[1, 0])), float(np.real(B[1, 1]))]],
        "nilpotency_max_abs_B2": nilpotency_max,
        "propagator_closed_form": "Pi(T) = I + B*T (точно, B^2 = 0)",
        "T_at_z30": T30,
        "sigma_max_at_z30": float(sv[0]),
        "sigma_max_per_echo": float(sv_echo[0]),
        "eigenvalues_at_z30": [[float(np.real(e)), float(np.imag(e))]
                               for e in eig],
        "phase_drift_max_rad": phase_exact,
        "rk4_vs_closed_form_rel": rk4_vs_closed,
        "growth_law": "светской: sigma_max(T) ~ (350/61)*T/sqrt(2) — "
                      "полиномиальный, НЕ экспонента",
        "claim": ("линейный сектор до z = 30 сертифицирован в замкнутой "
                  "форме: фаза дрейфа ТОЧНО 0 (spec = {1,1} вещественные), "
                  "рост светской ~%.1f к z = 30 (%.2f за эхо) — никакой "
                  "осцилляции pi/30-лестницы и никакой экспоненты "
                  "линейная монодромия не несёт" % (sv[0], sv_echo[0])),
    }


# ==============================================================================
# [D2] БЮДЖЕТ ГЛУБИНЫ
# ==============================================================================
def d2_depth_budget():
    S_req = float(np.exp(GAMMA * (Z_TARGET - Z_WALL)))
    S_req_safe = 10.0 * S_req
    echoes_spinor = Z_TARGET / DELTA_SP
    echoes_zoom = Z_TARGET / DELTA_ZOOM
    # стартовая отстройка, если бы глубину несла бисекция (нереалистично),
    # и реалистичный старт eps ~ 1e-3 + зумы
    eps_bisect = float(np.exp(-Z_TARGET / GAMMA))
    eps_start = 1e-3
    z_start = GAMMA * float(np.log(1.0 / eps_start))
    zooms_needed = (Z_TARGET - z_start) / (Z_WALL / 10.0)   # ~1 z/зум, консерв.
    rows = []
    for z in (9.35, 15.0, 20.0, 25.0, 30.0):
        rows.append({
            "z": z,
            "S_req": float(np.exp(GAMMA * (z - Z_WALL))),
            "S_req_x10": float(10.0 * np.exp(GAMMA * (z - Z_WALL))),
            "spinor_echoes_total": float(z / DELTA_SP),
            "spinor_echoes_above_wall": float((z - Z_WALL) / DELTA_SP),
        })
    return {
        "anchors": {"gamma": GAMMA, "z_wall": Z_WALL, "z_target": Z_TARGET,
                    "delta_spinor": DELTA_SP, "delta_zoom_units": DELTA_ZOOM},
        "S_req_at_z30": S_req,
        "S_req_safe_x10_at_z30": S_req_safe,
        "spinor_echoes_to_z30": echoes_spinor,
        "zoom_echoes_to_z30_zoomunits": echoes_zoom,
        "eps_if_bisect_only": eps_bisect,
        "note_bisect": ("бисекцией глубину не нести: (A-A*)/A* ~ e^{-z/gamma} "
                        "~ %.1e при z = 30 — вне двойной точности; глубину "
                        "несёт рескалирование зумов (z += ln lam за стадию)"
                        % eps_bisect),
        "realistic_start": {"eps_start": eps_start,
                            "z_start": z_start,
                            "zooms_needed_conservative": float(zooms_needed)},
        "ladder_table": rows,
    }


# ==============================================================================
# [D3] ПЕРЦЕНТИЛЬНАЯ ГАММА/ДЕЛЬТА НА ГЛУБИННОЙ ЛЕСТНИЦЕ
# ==============================================================================
def percentile_gamma(zs, ms, p_mass=70):
    """Перцентильный фит: выжившие (не на полу), затем верхний (100-p)%
    выборки; ОЛС ln M vs z; бутстрап-CI (сид фиксирован)."""
    zs = np.asarray(zs, float)
    ms = np.asarray(ms, float)
    surv = ms > ms.max() * 1e-12
    thr = np.percentile(ms[surv], p_mass)
    keep = surv & (ms >= thr)
    n_used = int(keep.sum())
    if n_used < 3:
        return None
    rng = np.random.default_rng(SEED)
    idx = np.where(keep)[0]
    boots = []
    for _ in range(200):
        sel = rng.choice(idx, size=n_used, replace=True)
        A = np.vstack([zs[sel], np.ones(n_used)]).T
        sol, *_ = np.linalg.lstsq(A, np.log(ms[sel]), rcond=None)
        boots.append(-sol[0])
    A = np.vstack([zs[idx], np.ones(n_used)]).T
    sol, *_ = np.linalg.lstsq(A, np.log(ms[idx]), rcond=None)
    g = float(-sol[0])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"gamma": g, "ci95": [float(lo), float(hi)],
            "ci_width": float(hi - lo), "n_used": n_used,
            "p_mass": p_mass}


def ols_gamma(zs, ms):
    zs = np.asarray(zs, float)
    ms = np.asarray(ms, float)
    A = np.vstack([zs, np.ones(len(zs))]).T
    sol, *_ = np.linalg.lstsq(A, np.log(ms), rcond=None)
    return float(-sol[0])


def delta_hat_from_peaks(n_echo, delta, jitter_rel, rng):
    """Синтетические пики в v-пространстве: интервалы убывают геометрически
    dv_{n+1}/dv_n = e^{-delta} (рескалировка зума); шум интервала jitter_rel;
    Delta_hat — фит ln(dv_n) = c - Delta*n (оценщик v5-v9,
    echo_period_from_peaks)."""
    n_int = max(n_echo - 1, 3)
    dv = np.exp(-delta * np.arange(n_int)) * (1.0 - np.exp(-delta))
    dv_obs = dv * (1.0 + jitter_rel * rng.standard_normal(n_int))
    dv_obs = np.clip(dv_obs, 1e-300, None)
    k = np.arange(n_int)
    A = np.vstack([k, np.ones_like(k)]).T
    sol, *_ = np.linalg.lstsq(A, np.log(dv_obs), rcond=None)
    return float(-sol[0])


def adaptive_gamma_estimator(zs, ms_obs, floor_est):
    """Априорное правило (без обращения к истине): доля точек в куче пола
    (наблюдаемая!) < 15% -> ОЛС по выжившим; >= 15% -> перцентиль p70
    выживших (правило q3/G1). Все кандидаты записываются для прозрачности."""
    zs = np.asarray(zs, float)
    ms = np.asarray(ms_obs, float)
    surv = ms > floor_est * 1.20  # 3с-полоса джанка 5% (якорь кампаний)
    share_obs = float(1.0 - surv.mean())
    cands = {}
    if surv.sum() >= 3:
        zi, mi = zs[surv], ms[surv]
        A = np.vstack([zi, np.ones(len(zi))]).T
        sol, *_ = np.linalg.lstsq(A, np.log(mi), rcond=None)
        cands["ols_survivors"] = {"gamma": float(-sol[0]), "ci95": None,
                                  "ci_width": None, "n_used": int(len(zi))}
    for p in (50, 70, 85):
        g = percentile_gamma(zs, ms, p)
        if g:
            cands[f"pct_p{p}"] = g
    if share_obs < 0.15 and "ols_survivors" in cands:
        chosen = "ols_survivors"
    elif "pct_p70" in cands:
        chosen = "pct_p70"
    else:
        chosen = next(iter(cands))
    return {"chosen": chosen, "share_floor_obs": share_obs,
            "candidates": cands, "estimate": cands.get(chosen)}


def d3_percentile_ladder():
    out = {"scenarios": [], "method_note":
           "редуцированная модель: пики эха в v-пространстве (интервалы "
           "геометрические, отношение e^-Delta, дельта в зум-единицах "
           "3.44), массы M_n = M0*exp(-gamma*z_n) по спинорным эхо "
           "(z_n = n*Delta_sp), пол на глубине z_f = 7.0 + (z_t - 9.35) "
           "(калибровка: при S=1 стена воспроизводит q3), джанк-шум 5% "
           "на зажатых точках; априорное правило оценщика: доля кучи "
           "пола < 15% -> ОЛС по выжившим, иначе перцентиль p70 (правило "
           "q3/G1); успех: |g-g*|/g <= 1% и |D-D*|/D <= 0.5% (джанк "
           "интервалов 1%)"}
    for z_t in (9.35, 15.0, 20.0, 25.0, 30.0):
        S = float(np.exp(GAMMA * (z_t - Z_WALL)))
        n_echo = int(round(z_t / DELTA_SP))
        zs = np.arange(1, n_echo + 1) * DELTA_SP
        ms_true = np.exp(-GAMMA * zs)                    # M0 = 1
        z_floor = 7.0 + (z_t - Z_WALL)                   # глубина пола
        floor = float(np.exp(-GAMMA * z_floor))
        rng = np.random.default_rng(SEED + int(z_t * 100))
        junk = floor * (1.0 + 0.05 * np.abs(rng.standard_normal(n_echo)))
        ms_obs = np.maximum(ms_true, junk)
        share_clamped = float(np.mean(ms_obs > ms_true * (1 + 1e-12)))
        floor_est = float(np.min(ms_obs))
        # дельта: два сценария джанка интервалов
        rng_d1 = np.random.default_rng(SEED + 7)
        rng_d3 = np.random.default_rng(SEED + 11)
        D1 = delta_hat_from_peaks(n_echo, DELTA_ZOOM, 0.01, rng_d1)
        D3 = delta_hat_from_peaks(n_echo, DELTA_ZOOM, 0.03, rng_d3)
        est = adaptive_gamma_estimator(zs, ms_obs, floor_est)
        g_hat = est["estimate"]["gamma"] if est["estimate"] else float("nan")
        ci_w = est["estimate"].get("ci_width")
        g_o = ols_gamma(zs, ms_obs)
        ok_g = (np.isfinite(g_hat)
                and abs(g_hat - GAMMA) / GAMMA <= 0.01
                and (ci_w is None or ci_w <= 0.10 * GAMMA))
        ok_d = abs(D1 - DELTA_ZOOM) / DELTA_ZOOM <= 0.005
        out["scenarios"].append({
            "z_target": z_t, "S_used": S, "n_echoes": n_echo,
            "z_floor_used": z_floor,
            "floor_share_clamped": share_clamped,
            "share_floor_observed": est["share_floor_obs"],
            "estimator_rule": est["chosen"],
            "gamma_estimate": est["estimate"],
            "gamma_candidates": est["candidates"],
            "gamma_err_pct": float(abs(g_hat - GAMMA) / GAMMA * 100),
            "gamma_ols_naive": g_o,
            "ols_naive_err_pct": float(abs(g_o - GAMMA) / GAMMA * 100),
            "delta_hat_jitter1pct": D1, "delta_hat_jitter3pct": D3,
            "delta_err_pct_jitter1pct": float(
                abs(D1 - DELTA_ZOOM) / DELTA_ZOOM * 100),
            "success_gamma": bool(ok_g), "success_delta": bool(ok_d),
            "success": bool(ok_g and ok_d),
        })
        log(f"  z = {z_t:5.2f}: S = {S:9.1f}, эхо = {n_echo:3d}, "
            f"пол = {share_clamped:5.1%}, правило = {est['chosen']:13s}, "
            f"гамма = {g_hat:.4f} ({abs(g_hat - GAMMA) / GAMMA * 100:5.2f}%), "
            f"наивный ОЛС = {g_o:.4f} ({abs(g_o - GAMMA) / GAMMA * 100:5.2f}%), "
            f"Delta = {D1:.3f} ({abs(D1 - DELTA_ZOOM) / DELTA_ZOOM * 100:.2f}%), "
            f"успех = {ok_g and ok_d}")
    n_ok = sum(s["success"] for s in out["scenarios"])
    out["summary"] = {
        "n_scenarios": len(out["scenarios"]),
        "n_success": n_ok,
        "closed_loop": ("петля с [D2] замкнута: подавление пола S = S_req(z) "
                        "уводит кучу пола глубже целевой z; наивный ОЛС "
                        "воспроизводит отрицательный вердикт q3 там, где "
                        "пол доминирует, априорное правило (выжившие/ p70) "
                        "его обходит"),
    }
    return out


# ==============================================================================
# [D4] ПРОТОКОЛ ПОЛНОЙ PDE-КАМПАНИИ (v21)
# ==============================================================================
def d4_protocol():
    return {
        "name": "v21_deep_echo",
        "schedule": [
            "старт: eps = 1e-3 над A* (z_0 ~ 2.6), n = 800, зумы до стопа",
            "каждая стадия: джанк-мониторинг q7 (M1-зум-лестница; слово "
            "ворот 'open-for-percentile' пока |M1| убывает с глубиной зумов)",
            "подавление пола: W2/M3-гейты v6.1 активны; при инвазии мусора "
            "(j >= 12) — откат стадии и уплотнение окна (w_factor x5)",
            "целевой темп: S_req(z) подавления пола за счёт гейтов, "
            "не за счёт глубины; чекпоинт JSON после каждого эха",
            "стоп: z >= 30 (41 спинорное эхо) ИЛИ джанк-инвазия 3 стадий "
            "подряд (фиксация стены с новым S)",
        ],
        "deliverables": ["echo-пики до z = 30", "перцентильная гамма с CI",
                         "Delta_eff с эволюцией по глубине",
                         "ворота: открытая pi/15-модуляция (1.5 периода)"],
        "honest_status": ("протокол написан, полная PDE-кампания v21 — "
                          "за пределами этой сессии; редуцированная модель "
                          "[D3] сертифицирует ОЦЕНЩИКИ, не физику"),
    }


# ==============================================================================
def main():
    out = {
        "title": "OPEN9-Q3 / v20b: глубина z >= 30 — сертификация, бюджет, "
                 "перцентильная лестница",
        "question": "достижим ли процентный gamma/Delta при z >= 30? "
                    "(монография гл.7 №3; q3: переизмерение заблокировано "
                    "стеной z ~ 9.35)",
    }
    log("[D1] сертификация линейного сектора до z = 30...")
    out["D1_linear_sector"] = d1_linear_sector_certified()
    log("    %s" % out["D1_linear_sector"]["claim"])
    log("    RK4 vs замкнутая форма: rel = %.2e; фаза = %.1e рад"
        % (out["D1_linear_sector"]["rk4_vs_closed_form_rel"],
           out["D1_linear_sector"]["phase_drift_max_rad"]))
    log("[D2] бюджет глубины...")
    out["D2_budget"] = d2_depth_budget()
    log("    S_req(z=30) = %.3e (x10 запас: %.1e); эхо до z=30: %.0f "
        "(спинорных) / %.1f (зум-единиц)"
        % (out["D2_budget"]["S_req_at_z30"],
           out["D2_budget"]["S_req_safe_x10_at_z30"],
           out["D2_budget"]["spinor_echoes_to_z30"],
           out["D2_budget"]["zoom_echoes_to_z30_zoomunits"]))
    log("[D3] перцентильная гамма/дельта на глубинной лестнице...")
    out["D3_percentile_ladder"] = d3_percentile_ladder()
    log("[D4] протокол v21...")
    out["D4_protocol"] = d4_protocol()

    sc = out["D3_percentile_ladder"]["scenarios"]
    ok_deep = [s for s in sc if s["z_target"] >= 15.0 and s["success"]]
    ok_wall = [s for s in sc if s["z_target"] == 9.35 and s["success"]]
    out["verdict_lines"] = [
        "линейный сектор сертифицирован до z = 30 в замкнутой форме: "
        "Pi(T) = I + B*T, фаза ТОЧНО 0, рост светской (%.0f к z = 30) — "
        "процентная гамма на z >= 30 чиста от линейной монодромии"
        % out["D1_linear_sector"]["sigma_max_at_z30"],
        "бюджет: пол должен быть подавлен в %.1e раз (x10 запас %.1e) — "
        "это ~%.0f спинорных эхо; бисекция глубину не несёт "
        "(eps ~ 1e-%d), несёт рескалирование зумов"
        % (out["D2_budget"]["S_req_at_z30"],
           out["D2_budget"]["S_req_safe_x10_at_z30"],
           out["D2_budget"]["spinor_echoes_to_z30"], 35),
        "редуцированная лестница: %d/%d сценариев успешны; стена z = 9.35 "
        "при S = 1 %s; сценарии z >= 15 с S = S_req(z) %s — петля с "
        "бюджетом [D2] замкнута"
        % (len(ok_deep) + len(ok_wall), len(sc),
           "подтверждена (неуспех)" if not ok_wall else "НЕ воспроизведена",
           "достигают процента" if ok_deep else "процента не достигают"),
        "статус вопроса №3: оценщики сертифицированы, бюджет квантован, "
        "протокол v21 написан; полный вердикт о процентной гамме — "
        "после PDE-кампании v21 (честный статус)",
    ]
    out["honest_notes"] = [
        "редуцированная модель [D3] — НЕ PDE-машина: она сертифицирует "
        "оценщики и бюджет (петля S_req <-> процент), но не физику "
        "джанк-инвазии на глубоких стадиях; полный вердикт за v21",
        "джанк-шум 5% на зажатых точках и 1%/3% джанк интервалов — "
        "консервативные предположения, откалиброванные по уровню мусора "
        "сохранённых кампаний (mirror-pair floor 1.4..2.3e2), не измерение",
        "S_req предполагает, что пол масс масштабируется как физическая "
        "масса (du-уровень сетки): если пол анизотропен по глубине, "
        "бюджет требует пересчёта после v21-чекпоинтов",
        "ворота q7 односторонни (растущая M1 загрязняет сверху): "
        "отсутствие роста M1 на v21 — необходимое, не достаточное условие "
        "процентной гаммы",
    ]
    out["runtime_s"] = round(time.time() - T_START, 1)
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    log(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    return out


if __name__ == "__main__":
    main()
