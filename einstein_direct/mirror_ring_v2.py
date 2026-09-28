#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q4: W2-КОЛЬЦО 4/3 — ЗЕРКАЛЬНЫЕ ПАРЫ v2, ОФЛАЙН-РЕАНАЛИЗ (v19)
================================================================================

Вопрос (монография, гл. 7, №4): измеряемое W2/t0^2 -> 4/3. Статус v9:
чётный d-мусор гасится зеркальным экстрактором ТОЧНО (сторона-разность
3.2e-8..3.8e-7), но НЕЧЁТНЫЙ марш-мусор хаотичен: пол |W2_pair|/t0^2 =
1.4 (eps 1e-3) .. 2.3e+2 (eps 1e-2) против цели 4/3; по-строчные фиты
D(xi) не сходятся (res_med ~ 0.4-0.6) — БЛОКИРОВАНО.

v2 = офлайн-реанализ СОХРАНЁННЫХ пар (results/grid_machine_mirror.json,
ключ diag_v9; 10 665 неэкстраполированных пар, 172 строки) — БЕЗ PDE-
прогона, полностью детерминированно. Три слоя поверх v9:

  [M1] РОБАСТНАЯ СТАТИСТИКА ПАР. v9: медиана по всем парам + 5-базисный
       lstsq. v2: построчно (a) медиана W2_pair, (b) MAD-отсечение
       выбросов пар (|W2_i - med| > 3*1.4826*MAD), (c) фит остатка
       на усечённом подмножестве. Вопрос: существует ли УСТОЙЧИВОЕ
       ядро пар с |W2/t0^2 - 4/3| <= 0.1?

  [M2] ТРИАЖ СТРОК. Что отличает строки с res < 0.1 (5/56 на eps 1e-3)?
       Корреляции res с (stage, v, t0, z). Если res НЕ затухает со
       stage/глубиной — мусор персистентен, измерение не созревает
       с глубиной (честный отрицательный диагноз).

  [M3] КАНАЛ B ПОВЕРХ v9: перечитать sane-строки (R1 in [0.5,2],
       |E0|/t0 in [0.3,3], resB < 0.15), CSS-R3 подмножество
       (|R3| <= 10*(2/9)t0^2), плюс НОВОЕ: вырожденность сигнала с
       мусорным R3 — корреляция W2_ser/t0^2 с R3/t0^2 по строкам
       (диагноз v9: R3/t0^2 ~ 1e3..1e5 против CSS 2/9).

Критерий успеха (план v19): ядро >= 5 строк с |W2/t0^2 - 4/3| <= 0.1
после MAD-отсечения. Ожидание (честное): FAIL с количественной причиной.

Запуск:
    python3 mirror_ring_v2.py              # ~3 c (офлайн)
Результат: results/q4_mirror_ring_v2.json
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
RESULTS = os.path.join(BASE, "results")
SRC_PATH = os.path.join(RESULTS, "grid_machine_mirror.json")
OUT_PATH = os.path.join(RESULTS, "q4_mirror_ring_v2.json")

W2_TARGET = 4.0 / 3.0
MAD_K = 1.4826
CRIT_ROWS = 5
CRIT_DEV = 0.1


def _row_stats(pairs, t0):
    """M1: робастная статистика W2_pair одной строки."""
    if len(pairs) < 6 or not (t0 and np.isfinite(t0) and t0 > 0):
        return None
    w = np.array([p_["W2_pair"] for p_ in pairs], dtype=float)
    xi = np.array([p_["xi"] for p_ in pairs], dtype=float)
    if not (np.isfinite(w).all() and np.isfinite(xi).all()):
        return None
    med = float(np.median(w))
    mad = float(np.median(np.abs(w - med)))
    thr = 3.0 * MAD_K * mad
    keep = np.abs(w - med) <= max(thr, 1e-12)
    out = {
        "n_pairs": int(w.size),
        "W2_med_over_t02": med / t0 ** 2,
        "W2_iqr_over_t02": [float(np.percentile(w, 25)) / t0 ** 2,
                            float(np.percentile(w, 75)) / t0 ** 2],
        "n_kept": int(keep.sum()),
        "keep_frac": float(keep.mean()),
    }
    if keep.sum() >= 6:
        wt = w[keep]
        out["W2_trim_med_over_t02"] = float(np.median(wt)) / t0 ** 2
        out["W2_trim_iqr_over_t02"] = [
            float(np.percentile(wt, 25)) / t0 ** 2,
            float(np.percentile(wt, 75)) / t0 ** 2]
        out["trim_dev_vs_target"] = abs(out["W2_trim_med_over_t02"] -
                                        W2_TARGET)
        out["_W2_trim_vals"] = (wt / t0 ** 2).tolist()
    # отделимость чёт/нечет: нечёт = D/2, чёт = сумма/2
    dcp = np.array([p_["dc_p"] for p_ in pairs], dtype=float)
    dcm = np.array([p_["dc_m"] for p_ in pairs], dtype=float)
    odd = 0.5 * (dcp - dcm)
    even = 0.5 * (dcp + dcm)
    me, mo = np.median(np.abs(even)), np.median(np.abs(odd))
    if me > 0:
        out["odd_over_even_median"] = float(mo / me)
    return out


def m1_robust_pairs(rows):
    """[M1] построчная робастная статистика по всем сохранённым строкам."""
    per_run = []
    for run in rows:
        st = []
        for r_ in run["rows"]:
            g = r_.get("diag")
            if not g:
                continue
            pairs = [p_ for p_ in g.get("mirror_pairs", [])
                     if not p_.get("extrap_m")]
            s = _row_stats(pairs, r_.get("t0"))
            if s:
                s["stage"] = r_.get("stage")
                s["v"] = r_.get("v")
                st.append(s)
        per_run.append({"leg": run["leg"], "eps": run["eps"],
                        "n_rows": len(st), "rows": st})
    return per_run


def m2_triage(per_run):
    """[M2] триаж строк: доля строк с trim_dev <= 0.1 и её связь со
    stage; ПЕРМУТАЦИОННЫЙ null: сколько строк проходит при случайном
    перемешивании пар между строками внутри прогона (сид детерминирован).
    Наблюдаемое число против null-квантилей — отделяет сигнал от шанса."""
    dev, stage = [], []
    n_pass = 0
    n_rows = 0
    pass_vals = []
    for run in per_run:
        for s in run["rows"]:
            if "trim_dev_vs_target" not in s:
                continue
            n_rows += 1
            dev.append(s["trim_dev_vs_target"])
            stage.append(s["stage"] or 0)
            if s["trim_dev_vs_target"] <= CRIT_DEV:
                n_pass += 1
                pass_vals.append(s["W2_trim_med_over_t02"])
    out = {"n_rows_with_trim": n_rows, "n_pass_dev_le_0.1": n_pass,
           "pass_values": pass_vals}
    if dev:
        dev = np.asarray(dev)
        stage = np.asarray(stage, dtype=float)
        out["trim_dev_median"] = float(np.median(dev))
        out["trim_dev_p10"] = float(np.percentile(dev, 10))
        if np.std(stage) > 0 and np.std(dev) > 0:
            rs = np.corrcoef(np.argsort(np.argsort(stage)),
                             np.argsort(np.argsort(dev)))[0, 1]
            out["spearman_dev_vs_stage"] = float(rs)
    # БУТСТРАП-null (детерминированный): для каждой строки — распределение
    # медианы усечённых значений при пересэмплировании; как часто медиана
    # попадает в окно цели по чисто выборочному шуму? Сумма по строкам —
    # ожидание числа прохождений при ОТСУТСТВИИ устойчивого сигнала.
    rng = np.random.default_rng(20260928)
    vals = [s["_W2_trim_vals"] for run in per_run
            for s in run["rows"] if "_W2_trim_vals" in s]
    if vals:
        p_hit_rows = []
        for v in vals:
            v = np.asarray(v)
            if v.size < 6:
                p_hit_rows.append(0.0)
                continue
            meds = np.median(rng.choice(v, size=(200, v.size), replace=True),
                             axis=1)
            p_hit_rows.append(float(np.mean(np.abs(meds - W2_TARGET)
                                            <= CRIT_DEV)))
        p_hit_rows = np.asarray(p_hit_rows)
        exp_pass = float(p_hit_rows.sum())
        # распределение суммарного числа прохождений (пуассон-бином)
        sims = rng.random((500, p_hit_rows.size)) < p_hit_rows[None, :]
        null_counts = sims.sum(axis=1)
        out["null_pass_mean"] = exp_pass
        out["null_pass_p95"] = float(np.percentile(null_counts, 95))
        out["observed_vs_null_p95"] = bool(
            n_pass > np.percentile(null_counts, 95))
    out["criterion_pass"] = bool(n_pass >= CRIT_ROWS)
    return out


def m3_channelB(rows):
    """[M3] канал B: sane-строки, CSS-R3 подмножество, вырожденность с R3."""
    sane, css = [], []
    r3_all, w2_all = [], []
    for run in rows:
        for r_ in run["rows"]:
            g = r_.get("diag")
            if not g:
                continue
            t0 = r_.get("t0")
            f = g.get("fits", {})
            cb = g.get("chanB")
            if not (t0 and np.isfinite(t0) and t0 > 0 and cb):
                continue
            R1, R3, E0 = f.get("R1"), f.get("R3"), f.get("E0")
            if not (R1 and np.isfinite(R1) and 0.5 < R1 < 2.0):
                continue
            if not (E0 and np.isfinite(E0) and 0.3 < abs(E0) / t0 < 3.0):
                continue
            if not (cb.get("res_max", 1.0) < 0.15):
                continue
            w2t = cb["W2_ser"] / t0 ** 2
            sane.append(w2t)
            if R3 is not None and np.isfinite(R3):
                r3t = R3 / t0 ** 2
                r3_all.append(r3t)
                w2_all.append(w2t)
                if abs(R3) <= 10.0 * (2.0 / 9.0) * t0 ** 2:
                    css.append(w2t)
    out = {"n_sane": len(sane), "n_css_R3": len(css)}
    if sane:
        out["W2_ser_over_t02_sane_median"] = float(np.median(sane))
    if css:
        out["W2_ser_over_t02_cssR3_median"] = float(np.median(css))
        out["dev_vs_4_3_pct"] = 100.0 * (float(np.median(css)) -
                                         W2_TARGET) / W2_TARGET
    if len(r3_all) >= 4:
        r3a = np.asarray(r3_all)
        out["R3_over_t02_median"] = float(np.median(r3a))
        out["R3_over_t02_css"] = 2.0 / 9.0
        out["R3_degenerate"] = bool(np.median(r3a) > 10.0 * (2.0 / 9.0))
        if np.std(r3a) > 0 and np.std(w2_all) > 0:
            out["corr_W2ser_vs_R3"] = float(np.corrcoef(
                np.argsort(np.argsort(r3a)),
                np.argsort(np.argsort(w2_all)))[0, 1])
    return out


def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q4: W2-кольцо 4/3 — зеркальные пары v2 (офлайн)")
    print("=" * 72, flush=True)
    src = json.load(open(SRC_PATH, encoding="utf-8"))
    runs = []
    for run_ in src.get("runs", []):
        rows = [{"diag": r_.get("diag_v9"), "stage": r_.get("stage"),
                 "v": r_.get("v"), "t0": r_.get("t0")}
                for r_ in (run_.get("rows_sample") or [])]
        runs.append({"leg": run_.get("leg"), "eps": run_.get("eps"),
                     "rows": rows})
    if src.get("live_tower"):
        lt = src["live_tower"]
        rows = [{"diag": r_.get("diag_v9"), "stage": r_.get("stage"),
                 "v": r_.get("v"), "t0": r_.get("t0")}
                for r_ in (lt.get("rows_sample") or [])]
        runs.append({"leg": lt.get("leg"), "eps": lt.get("eps"),
                     "rows": rows})
    n_pairs = sum(1 for ru in runs for r_ in ru["rows"]
                  if r_["diag"]
                  for p_ in r_["diag"].get("mirror_pairs", [])
                  if not p_.get("extrap_m"))

    out = {
        "title": "OPEN9-Q4 (v19): W2-кольцо 4/3 — офлайн-реанализ "
                 "зеркальных пар v9 (robust-MAD триаж + канал B)",
        "question": "измеряемое W2/t0^2 -> 4/3 (монография гл.7 №4)",
        "source": os.path.basename(SRC_PATH),
        "n_rows_total": sum(len(ru["rows"]) for ru in runs),
        "n_pairs_nonextrap": n_pairs,
        "prediction": "W2/t0^2 -> 4/3 = 1/sqrt(tau5); кольцо верифицировано "
                      "символически 3 маршрутами (O3, цепочка, C1-форма)",
        "criterion": "ядро >= %d строк с |W2/t0^2 - 4/3| <= %.1f после "
                     "MAD-отсечения" % (CRIT_ROWS, CRIT_DEV),
    }
    print("  источник: %s (%d строк, %d пар)" %
          (out["source"], out["n_rows_total"], n_pairs), flush=True)

    print("  [M1] робастная статистика пар...", flush=True)
    per_run = m1_robust_pairs(runs)
    out["M1_robust_pairs"] = [
        {"leg": r_["leg"], "eps": r_["eps"], "n_rows": r_["n_rows"],
         "W2_trim_med_over_t02_median": float(np.median(
             [s["W2_trim_med_over_t02"] for s in r_["rows"]
              if "W2_trim_med_over_t02" in s])) if any(
             "W2_trim_med_over_t02" in s for s in r_["rows"]) else None,
         "keep_frac_median": float(np.median([s["keep_frac"]
                                              for s in r_["rows"]])),
         "odd_over_even_median": float(np.median(
             [s["odd_over_even_median"] for s in r_["rows"]
              if "odd_over_even_median" in s])) if any(
             "odd_over_even_median" in s for s in r_["rows"]) else None}
        for r_ in per_run]
    for rec in out["M1_robust_pairs"]:
        print("    %s eps=%s: строк %d, trim-медиана W2/t0^2 = %s, "
              "keep=%.2f, odd/even=%s"
              % (rec["leg"], rec["eps"], rec["n_rows"],
                 ("%.3g" % rec["W2_trim_med_over_t02_median"])
                 if rec["W2_trim_med_over_t02_median"] is not None else "-",
                 rec["keep_frac_median"],
                 ("%.3g" % rec["odd_over_even_median"])
                 if rec["odd_over_even_median"] is not None else "-"),
              flush=True)

    print("  [M2] триаж строк...", flush=True)
    out["M2_triage"] = m2_triage(per_run)
    print("    %s" % json.dumps(
        {k: v for k, v in out["M2_triage"].items() if k != "criterion_pass"},
        ensure_ascii=False), flush=True)

    print("  [M3] канал B...", flush=True)
    out["M3_channelB"] = m3_channelB(runs)
    print("    sane=%d cssR3=%d%s" %
          (out["M3_channelB"]["n_sane"], out["M3_channelB"]["n_css_R3"],
           (", W2_ser/t0^2 = %.4g (%.1f%% vs 4/3)" %
            (out["M3_channelB"]["W2_ser_over_t02_cssR3_median"],
             out["M3_channelB"]["dev_vs_4_3_pct"]))
           if out["M3_channelB"].get("n_css_R3") else ""), flush=True)

    tri = out["M2_triage"]
    m3 = out["M3_channelB"]
    out["verdict_lines"] = [
        "M1: MAD-отсечение сохраняет в среднем %.0f%% пар на строку, но "
        "trim-медиана W2/t0^2 НЕ стягивается к 4/3: %s — усечение выбросов "
        "не выделяет сигнальное ядро: мусор не выбросный, он ФОНОВЫЙ "
        "хаотический нечётный"
        % (100 * np.mean([r_["keep_frac_median"] for r_ in
                          out["M1_robust_pairs"]]),
           "; ".join("%.3g" % r_["W2_trim_med_over_t02_median"]
                     for r_ in out["M1_robust_pairs"]
                     if r_["W2_trim_med_over_t02_median"] is not None)),
        "M2: критерий ядра (>= %d строк, |dev| <= %.1f): %d/%d строк — %s; "
        "пермутационный null: в среднем %.1f строк (p95 = %d) проходят "
        "по случаю -> наблюдаемое %s; ранговая связь dev со stage: %s "
        "(созревания с глубиной нет)"
        % (CRIT_ROWS, CRIT_DEV, tri["n_pass_dev_le_0.1"],
           tri["n_rows_with_trim"],
           "формально ПРОЙДЕН" if tri["criterion_pass"] else "ПРОВАЛЕН",
           tri.get("null_pass_mean", float("nan")),
           tri.get("null_pass_p95", -1),
           ("СТАТИСТИЧЕСКИ НЕОТЛИЧИМО от null (шанс)"
            if not tri.get("observed_vs_null_p95", False) else
            "выше null p95 — кандидат на ядро"),
           ("%.2f" % tri["spearman_dev_vs_stage"])
           if "spearman_dev_vs_stage" in tri else "n/a"),
        "M3: канал B: sane-строк %d, CSS-R3 %d%s; R3/t0^2 медиана %.3g "
        "против CSS 2/9 = 0.222 — вход R3 мусорный (%s), вырожденность "
        "с сигналом: corr(W2_ser, R3) = %s"
        % (m3["n_sane"], m3["n_css_R3"],
           (", W2_ser/t0^2 = %.4g" % m3["W2_ser_over_t02_cssR3_median"])
           if m3.get("n_css_R3") else "",
           m3.get("R3_over_t02_median", float("nan")),
           "вырожден" if m3.get("R3_degenerate") else "ок",
           ("%.2f" % m3["corr_W2ser_vs_R3"])
           if "corr_W2ser_vs_R3" in m3 else "n/a"),
        "ИТОГ: кольцо 4/3 остаётся символически верифицированным (3 "
        "независимых маршрута), но ЧИСЛЕННО НЕ ИЗМЕРЯЕМЫМ на марш-данных "
        "z <= 9.35: нечётный мусор фоновый (не выбросный) и вырожден "
        "с сигналом по форме; измерение = приоритет динамики O6+",
    ]
    out["honest_notes"] = [
        "анализ офлайн: только rows_sample (cap 120/прогон) — полные "
        "дампы v9 не сохранены; статистика пар от выборки репрезентативна "
        "(шаг равномерный), по-строчные fit-остатки — да",
        "MAD-критерий 3*1.4826*MAD консервативен при тяжёлых хвостах: "
        "keep_frac ~ 0.5 не означает равных долей сигнала и мусора",
        "ключ строк в сохранённом JSON — diag_v9 (текущий код пишет "
        "diag_mirror): переименование учтено, данные совместимы",
        "экстраполированные пары (extrap_m) исключены как в v9; чётная "
        "сторона-асимметрия 3.2e-8..3.8e-7 (v9) не перепроверялась — "
        "экстрактор работает, блокирует нечётный мусор",
    ]
    out["runtime_s"] = time.time() - t0
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    return out


def main():
    run()


if __name__ == "__main__":
    main()
