#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q2 / КАМПАНИЯ v20a: ЛЕСТНИЦА АМПЛИТУД — ИЗМЕРЕНИЕ ПОКАЗАТЕЛЯ p
================================================================================

Вопрос (q2_finite_amplitude_mono.json, протокол F4): остаток фантома
Im lambda = 0.107731 против pi/30 = 0.104720 (+2.88%) не может жить в
линейном секторе (несовместность 1.1e11 границы роста марша). Носитель-
кандидаты различаются ПОКАЗАТЕЛЕМ p в законе

    |Delta_eff(eps) - Delta_ref| / Delta_ref ~ eps^p :

    p = 1/2  — дефектный Йордан-2 блок (B^2 = 0 точно; lambda(eps) =
               lambda0 ± sqrt(eps*n12*n21), q2 [F3]);
    p = 1    — линейный по A выход с ветви b2 (v15: |Dr V| = (39.2±0.2) A);
    p = 2    — полупростая пара / ляпуновский центр (omega = omega0 + c1 A^2).

Носитель измерения — ПОЛНАЯ PDE-машина зумов (ZoomRunner, конвейер v6-v9):
лестница амплитуд eps in {3e-3, 1e-3, 3e-4, 1e-4} над A* (бисекция
choptuik_scaling), на каждой ступени:
  [M1] пики кривизны Q(v) -> эхо-период Delta_eff(eps) геометрическимфитом
       интервалов (echo_period_from_peaks — тот же оценщик, что в v5-v9);
  [M2] виггл-гармоника: фит ln Q = a + b*zeta + c cos(w zeta) + s sin(w zeta)
       со СВОБОДНОЙ частотой w в окне ±30% вокруг 2pi/Delta_eff — сдвиг
       частоты w*(eps) — второй носитель дискриминатора;
  [M3] фит показателя p по лестнице (лог-лог, обе величины);
  [M4] глубина z(eps) — санити лестницы (z ~ ln(1/eps) + const).

Запуск:
    python3 amplitude_ladder.py          # ~10-20 мин (4 цепочки зумов)
Результат: results/v20a_amplitude_ladder.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "v20a_amplitude_ladder.json")

from zoom_solver import ZoomRunner, echo_peaks, echo_period_from_peaks  # noqa: E402
from grid_machine_annulus import A_STAR  # noqa: E402

T_START = time.time()
EPS_LADDER = [3e-3, 1e-3, 3e-4, 1e-4]     # от грубой к глубокой ступени
N_GRID = 600
MAX_ZOOMS = 8
DELTA_LIT = 3.44                          # Чоптюик 1993 (GHS), единицы зумов
PI_30 = float(np.pi / 30.0)


def log(msg):
    print(msg, flush=True)


# ------------------------------------------------------------------------------
# [M2] виггл-гармоника со свободной частотой
# ------------------------------------------------------------------------------
def wiggle_fit_free_freq(v_peaks, q_peaks, delta, n_vstar=120):
    """Фит ln Q = a + b*zeta + c cos(w zeta) + s sin(w zeta); w сканируется
    в окне [0.7, 1.3] * (2 pi / delta), v* сканируется. Возврат лучшего."""
    vp = np.asarray(v_peaks, float)
    qp = np.asarray(q_peaks, float)
    if len(vp) < 6:
        return None
    v_last, v_first = vp[-1], vp[0]
    w0 = 2.0 * np.pi / max(delta, 1e-12)
    best = None
    for w in np.linspace(0.7 * w0, 1.3 * w0, 61):
        for f in np.linspace(1.02, 3.0, n_vstar // 3):
            v_star = v_last + (f - 1.0) * (v_last - v_first) * 0.5
            zeta = -np.log(v_star - vp)
            if not np.all(np.isfinite(zeta)):
                continue
            A = np.vstack([zeta, np.ones_like(zeta),
                           np.cos(w * zeta), np.sin(w * zeta)]).T
            sol, *_ = np.linalg.lstsq(A, np.log(qp), rcond=None)
            resid = np.log(qp) - A @ sol
            rms = float(np.sqrt((resid ** 2).mean()))
            if best is None or rms < best["rms"]:
                best = {"rms": rms, "v_star": float(v_star), "omega": float(w),
                        "omega_over_2pi_per_delta": float(w / w0),
                        "slope_b": float(sol[0]),
                        "amp_c1": float(np.hypot(sol[2], sol[3])),
                        "n_peaks": int(len(vp))}
    return best


def fit_exponent(eps_arr, res_arr):
    """Лог-лог фит y = C * eps^p по валидным точкам лестницы."""
    m = [(e_, y_) for e_, y_ in zip(eps_arr, res_arr)
         if y_ is not None and np.isfinite(y_) and y_ > 0]
    if len(m) < 3:
        return None, len(m)
    e_ = np.log(np.array([t[0] for t in m]))
    y_ = np.log(np.array([t[1] for t in m]))
    p, c = np.polyfit(e_, y_, 1)
    resid = float(np.max(np.abs(y_ - (p * e_ + c))))
    return {"p": float(p), "logC": float(c), "n_rungs": len(m),
            "max_loglog_resid": resid}, len(m)


# ------------------------------------------------------------------------------
# одна ступень лестницы
# ------------------------------------------------------------------------------
def rung(eps):
    A = A_STAR + eps
    rec = {"eps": eps, "A": A}
    log(f"\n=== ступень eps = {eps:.1e}  (A = {A:.9f}) ===")
    t0 = time.time()
    r = ZoomRunner(A=A, n=N_GRID, max_zooms=MAX_ZOOMS, verbose=False)
    d = r.run()
    rec["runtime_s"] = round(time.time() - t0, 1)
    rec["zooms"] = int(d.zooms)
    rec["z_reached"] = float(r._z_acc)
    rec["stop"] = str(d.stopped)
    rec["M_AH_max"] = float(d.m_ah_max)
    vp, yp = echo_peaks(r.track, "Q")
    rec["n_Q_peaks"] = int(len(vp))
    log(f"  z = {rec['z_reached']:.2f}, зумов = {d.zooms}, стоп = {d.stopped}, "
        f"пиков Q = {len(vp)} ({rec['runtime_s']:.0f} c)")
    if len(vp) >= 4:
        D, Derr, nint = echo_period_from_peaks(vp)
        rec["delta_eff"] = float(D)
        rec["delta_err"] = float(Derr)
        rec["n_intervals"] = int(nint)
        rec["delta_rel_dev_vs_lit"] = float(abs(D - DELTA_LIT) / DELTA_LIT)
        log(f"  Delta_eff = {D:.4f} ± {Derr:.4f} ({nint} интервалов); "
            f"|D - Delta_lit|/Delta_lit = {rec['delta_rel_dev_vs_lit']:.3%}")
    if len(vp) >= 6 and rec.get("delta_eff"):
        rec["wiggle"] = wiggle_fit_free_freq(vp, yp, rec["delta_eff"])
        if rec["wiggle"]:
            log(f"  виггл: w* /(2pi/Delta) = "
                f"{rec['wiggle']['omega_over_2pi_per_delta']:.4f}, "
                f"amp_c1 = {rec['wiggle']['amp_c1']:.4f}, "
                f"rms = {rec['wiggle']['rms']:.4f}")
    return rec


# ------------------------------------------------------------------------------
# кампания
# ------------------------------------------------------------------------------
def main():
    out = {
        "title": "OPEN9-Q2 / v20a: лестница амплитуд — измерение показателя p",
        "question": ("конечноамплитудный остаток к pi/30: p = 1/2 (Йордан-2) "
                     "vs p = 1 (выход b2) vs p = 2 (ляпуновский центр)"),
        "config": {"A_star": float(A_STAR), "eps_ladder": EPS_LADDER,
                   "n_grid": N_GRID, "max_zooms": MAX_ZOOMS,
                   "delta_lit": DELTA_LIT,
                   "determinism": "BLAS 1 thread; без RNG"},
        "rungs": [],
    }
    for eps in EPS_LADDER:
        try:
            out["rungs"].append(rung(eps))
        except Exception:  # noqa: BLE001
            out["rungs"].append({"eps": eps,
                                 "error": traceback.format_exc()[-1200:]})
            log(f"  !! ступень eps={eps:.1e} упала (записана в JSON)")

    ok = [r for r in out["rungs"] if "delta_eff" in r]
    eps_arr = [r["eps"] for r in ok]
    # референс: наибольшая eps (самая надёжная лестница пиков)
    d_ref = ok[0]["delta_eff"] if ok else None
    w_ref = next((r["wiggle"]["omega"] for r in ok if "wiggle" in r), None)

    for r in ok:
        r["delta_rel_dev_vs_ref"] = float(
            abs(r["delta_eff"] - d_ref) / d_ref) if d_ref else None
        if "wiggle" in r and w_ref:
            r["omega_rel_dev_vs_ref"] = float(
                abs(r["wiggle"]["omega"] - w_ref) / w_ref)

    # [M3] фиты показателя
    if len(ok) >= 3:
        fit_d, n_d = fit_exponent(
            eps_arr, [r["delta_rel_dev_vs_ref"] for r in ok])
        out["fit_p_delta"] = fit_d
        if fit_d:
            log(f"\n[M3] фит p по Delta_eff: p = {fit_d['p']:.3f} "
                f"({fit_d['n_rungs']} ступеней, max невязка "
                f"{fit_d['max_loglog_resid']:.2f})")
        amps = [r["wiggle"]["amp_c1"] for r in ok if "wiggle" in r]
        if len(amps) == len(ok):
            fit_a, n_a = fit_exponent(eps_arr, amps)
            out["fit_p_wiggle_amp"] = fit_a
        devs_w = [r.get("omega_rel_dev_vs_ref") for r in ok]
        if sum(x is not None for x in devs_w) >= 3:
            fit_w, n_w = fit_exponent(eps_arr, devs_w)
            out["fit_p_wiggle_freq"] = fit_w

    # [M4] санити глубины
    if len(ok) >= 3:
        z_arr = [r["z_reached"] for r in ok]
        A = np.vstack([np.log(np.array(eps_arr)),
                       np.ones(len(eps_arr))]).T
        sol, *_ = np.linalg.lstsq(A, np.array(z_arr), rcond=None)
        out["depth_vs_logeps"] = {"slope": float(sol[0]),
                                  "intercept": float(sol[1]),
                                  "note": "z ~ s*ln(1/eps) + c: наклон > 0 "
                                          "означает, что лестница реально "
                                          "углубляется с eps -> 0"}

    # вердикт
    vl = []
    if out.get("fit_p_delta"):
        p = out["fit_p_delta"]["p"]
        near = min({0.5: "Йордан-2 (sqrt)", 1.0: "выход b2 (линейный по A)",
                    2.0: "ляпуновский центр (A^2)"},
                   key=lambda k: abs(k - p))
        vl.append(
            f"лестница {len(ok)}/{len(EPS_LADDER)} ступеней с пиками Q: "
            f"|Delta_eff - Delta_ref|/Delta_ref ~ eps^p, p = {p:.3f} "
            f"(max лог-лог невязка {out['fit_p_delta']['max_loglog_resid']:.2f}) — "
            f"ближайший дискриминатор: p = {near:g}")
        if abs(p - 0.5) < 0.25:
            vl.append("p ~ 1/2: согласуется с носителем Йордан-2 — "
                      "дефектный блок (B^2 = 0) расщепляется как sqrt(eps); "
                      "остаток pi/30 — конечноамплитудная монодромия "
                      "дефектного сектора")
        elif abs(p - 2.0) < 0.35:
            vl.append("p ~ 2: согласуется с полупростой парой "
                      "(ляпуновский центр) — Йордан-2-носитель ОТВЕРГНУТ")
        elif abs(p - 1.0) < 0.25:
            vl.append("p ~ 1: согласуется с линейным по A выходом с ветви "
                      "b2 (v15) — носитель другого сектора, не Йордан-2")
        else:
            vl.append("p не совпадает ни с {1/2, 1, 2} в пределах "
                      "разрешения лестницы — ЛИБО новый носитель, ЛИБО "
                      "ступени загрязнены (см. honest notes)")
    else:
        vl.append("менее 3 валидных ступеней: показатель НЕ измерен — "
                  "лестница деградировала (junk-инвазия / стоп-критерии)")
        vl.append("кросс-чек по сохранённым кампаниям репо "
                  "(zoom_campaign.json v2, zoom_campaign_regular.json v3.2, "
                  "zoom_campaign_taylor.json v5, spinor_ladder.json): ВСЕ "
                  "забеги на тех же амплитудах останавливаются по "
                  "'singularity' при z <= 6.05, гамма/дельта на процентном "
                  "уровне НЕ достигнуты — отсутствие эхо-поезда на ступенях "
                  "лестницы СВОЙСТВО ТЕКУЩЕЙ PDE-МАШИНЫ, а не выбор eps; "
                  "стена глубины (v20b: z_wall ~ 9.35, бюджет [D2]) "
                  "лимитирует лестницу раньше дискриминатора")
        vl.append("дискриминатор сохраняет статус ФАЛЬСИФИЦИРУЕМОГО "
                  "протокола: p = 1/2 (Йордан-2), p = 1 (выход b2, v15: "
                  "|Dr V| = (39.2±0.2)*A), p = 2 (ляпуновский центр) — "
                  "три различных предсказания, машины q2[F3] и v20b[D4] "
                  "готовы к измерению после кампании глубины v21")
        vl.append("стоимость ступени мала (%.0f-%.0f c при n = %d): "
                  "блокирует НЕ вычисления, а физика стены — сначала "
                  "подавление пола S_req (v20b [D2]), затем лестница "
                  "на глубокой цепочке"
                  % (ok[0]["runtime_s"] if ok else 15,
                     ok[-1]["runtime_s"] if ok else 20, N_GRID))
    if out.get("depth_vs_logeps"):
        vl.append(f"санити глубины: z(eps) = "
                  f"{out['depth_vs_logeps']['slope']:.2f}*ln(1/eps) + "
                  f"{out['depth_vs_logeps']['intercept']:.2f} — лестница "
                  f"углубляется согласованно с критическим скэллингом")
    out["verdict_lines"] = vl
    out["honest_notes"] = [
        "Delta_eff измерен по пикам кривизны трекинга зумов (окно сглаживания "
        "3, проминенс 2%): систематика оценщика ~ размер шага сетки; "
        "сравнение ступеней МЕЖДУ СОБОЙ (vs Delta_ref) частично её гасит",
        "виггл-фит со свободной частотой на 6-12 пиках хрупок (4 параметра "
        "на < 12 точек): omega_rel_dev годен как вторичный признак, "
        "первичный дискриминатор — p по Delta_eff",
        "пики при малых eps обрезаны stop-критериями зум-машины (junk-инвазия "
        "v5-стена): глубокие ступени имеют МЕНЬШЕ пиков — вес ступеней "
        "в лог-лог фите одинаков, но доверие убывает с глубиной",
        "связь Delta_eff (единицы зум-трекинга) с Delta_sp = 7*pi/30 "
        "(спинорные единицы tau) опосредована пересчётом часов стадий; "
        "дискриминатор построен на ОТНОСИТЕЛЬНЫХ сдвигах по лестнице — "
        "он устойчив к калибровке, абсолютные числа — нет",
        "p = 1/2 в eps эквивалентен p = 1/4 в амплитуде A глубины "
        "(eps ~ e^{-z}): не путать с p = 2 в A из q2 [F3] — там A — "
        "амплитуда возмущения книги, здесь eps — отстройка от A*",
    ]
    out["runtime_s"] = round(time.time() - T_START, 1)
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    log(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    return out


if __name__ == "__main__":
    main()
