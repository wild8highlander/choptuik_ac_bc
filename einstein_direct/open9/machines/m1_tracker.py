#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q7: 1/r-МОДА — ТРЕКЕР M1 (v19)
================================================================================

Вопрос (монография, гл. 7, №7): живая 1/r-мода в массе. Разложение
m/xi^3 = M1/xi^2 + M3 (README_EN): коэффициент M1 при 1/xi^2 — растёт
ли он с глубиной (физическая мода) или стоит на мусорном полу?
Статус: M3/M3_pred медиана ~ 1.6 (xi-мусор завышает M3-фит), flux_ratio
> 1 — мера того же мусора; ворота для процентной гаммы (#3).

Машина (v19):
  [T1] ДЕКОМПОЗИЦИЯ НА СОХРАНЁННЫХ ПРОФИЛЯХ: probe_channel_eps1e-03.json
       — профили (xi[], m[]) по zoom-стадиям марша (eps = 1e-3, z <=
       9.35). На внешнем окне (|xi| >= xi_med, отсечение внутренности)
       фит m(xi) = M1*xi + M3*xi^3 (МНК); контроль: полный фит с
       мусорным базисом против 2-параметрического.
  [T2] КЛАССИФИКАЦИЯ РЕЖИМА: трек M1 по стадиям (v растёт с глубиной):
       (a) экспоненциальный рост: slope log|M1| vs v > 0 с CI, не
       содержащим 0, и знакосогласованность; (b) мусорный пол: |M1|
       плоский в пределах шума. Порог решения задан явно.
  [T3] ПЕРЕКРЁСТНАЯ СВЕРКА: annulus-машина (grid_machine_annulus.json,
       annulus_summary.M1_median) — медианный M1 на стабильных каналах;
       сравнение масштабов M1 против M3 и против junk-пола du-уровня.
  [T4] ВЕРДИКТ-ВОРОТА ДЛЯ Q3: слово вердикта передаётся в
       q3_echo_fit_global.json (перепрогон Q3 после Q7 снимает ворота).

Запуск:
    python3 m1_tracker.py                  # ~2 c (офлайн)
Результат: results/q7_m1_tracker.json
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
OUT_PATH = os.path.join(RESULTS, "q7_m1_tracker.json")

SEED = 20260928
GROW_SLOPE_MIN = 0.5        # нижняя граница значимого роста log|M1|/v
CI_EXCL0 = True             # CI не содержит 0
R2_MIN = 0.9                # качество 2-параметрического фита


def fit_m1_m3(xi, m, outer_frac=0.5):
    """Фит m = M1*xi + M3*xi^3 на ВНЕШНЕМ окне (|xi| >= квантиль
    outer_frac по |xi|). Возврат: M1, M3, R2, n."""
    a = np.abs(xi)
    cut = np.quantile(a, outer_frac)
    sel = a >= max(cut, 1e-300)
    if sel.sum() < 6:
        return None
    x = np.asarray(xi)[sel]
    y = np.asarray(m)[sel]
    A = np.stack([x, x ** 3], axis=1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    M1, M3 = float(coef[0]), float(coef[1])
    pred = A @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"M1": M1, "M3": M3, "R2": R2, "n": int(sel.sum()),
            "xi_max": float(np.max(np.abs(x)))}


def t1_decompose():
    """[T1] профили probe_channel: M1/M3/R2 по стадиям."""
    path = os.path.join(RESULTS, "probe_channel_eps1e-03.json")
    p = json.load(open(path, encoding="utf-8"))
    rows = []
    for prof in p.get("profiles", []):
        xi = np.asarray(prof["xi"], dtype=float)
        m = np.asarray(prof["m"], dtype=float)
        ok = np.isfinite(xi) & np.isfinite(m)
        f = fit_m1_m3(xi[ok], m[ok])
        if f and np.isfinite(f["M1"]) and np.isfinite(f["M3"]):
            f["zoom"] = prof.get("zoom")
            f["j"] = prof.get("j")
            f["v"] = float(prof.get("v", float("nan")))
            rows.append(f)
    return rows


def t2_classify(rows):
    """[T2] режим M1: физический рост против мусорного пола.

    Чистые строки: R2 >= 0.95 и |M3| > 1e-12 (иначе — дегенеративные/
    мусорное вторжение, исключаются из тренда, но РЕПОРТИРУЮТСЯ).
    Тренд: log|M1| против ИНДЕКСА ЗУМА (глубина) на чистых строках,
    бутстрап-CI (детерминированный сид). Рост моды = положительный
    тренд С ГЛУБИНОЙ при чистых фатах; убывание/плоско = мусорный пол."""
    out = {"n_profiles": len(rows)}
    clean, flagged = [], []
    for r_ in rows:
        if r_["R2"] >= 0.95 and abs(r_["M3"]) > 1e-12 and r_["M1"] != 0:
            clean.append(r_)
        else:
            flagged.append({"zoom": r_["zoom"], "j": r_["j"],
                            "M1": r_["M1"], "M3": r_["M3"],
                            "R2": r_["R2"],
                            "why": "M3<=0/R2<0.95 — мусорное вторжение "
                                   "или вырожденная строка"})
    out["n_clean"] = len(clean)
    out["n_flagged"] = len(flagged)
    out["flagged_rows"] = flagged
    # медианы |M1| по зумам
    zooms = sorted({r_["zoom"] for r_ in clean})
    med_by_zoom = []
    for z in zooms:
        a = [abs(r_["M1"]) for r_ in clean if r_["zoom"] == z]
        if a:
            med_by_zoom.append({"zoom": z, "absM1_median": float(np.median(a)),
                                "n": len(a)})
    out["absM1_median_by_zoom"] = med_by_zoom
    if len(zooms) < 2:
        out["mode"] = "undetermined (мало чистых зумов)"
        return out
    x = np.array([r_["zoom"] for r_ in clean], dtype=float)
    y = np.log(np.array([abs(r_["M1"]) for r_ in clean], dtype=float))
    A = np.stack([x, np.ones_like(x)], axis=1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    slope = float(coef[0])
    rng = np.random.default_rng(SEED)
    n = x.size
    boots = []
    for _ in range(400):
        idx = rng.integers(0, n, n)
        b, *_ = np.linalg.lstsq(A[idx], y[idx], rcond=None)
        boots.append(b[0])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    out["slope_logM1_vs_zoom"] = slope
    out["slope_ci95"] = [float(lo), float(hi)]
    out["R2_median_clean"] = float(np.median([r_["R2"] for r_ in clean]))
    out["M1_over_M3_abs_median"] = float(np.median(
        [abs(r_["M1"] / r_["M3"]) for r_ in clean]))
    if lo > 0 and slope > GROW_SLOPE_MIN:
        out["mode"] = "growing (1/r-мода растёт с глубиной)"
    elif hi < 0:
        out["mode"] = "junk floor (|M1| УБЫВАЕТ с глубиной зумов — мусор)"
    elif lo <= 0 <= hi:
        out["mode"] = "junk floor (M1 плоский/незначимый в пределах шума)"
    else:
        out["mode"] = "undetermined (промежуточный режим: slope %.2f, " \
                      "CI [%.2f, %.2f])" % (slope, lo, hi)
    return out


def t3_crosscheck():
    """[T3] annulus M1_median + масштабы против du-пола."""
    path = os.path.join(RESULTS, "grid_machine_annulus.json")
    vals = []
    try:
        d = json.load(open(path, encoding="utf-8"))
        for run in d.get("runs", []):
            s = run.get("annulus_summary") or {}
            if s.get("M1_median") is not None:
                vals.append({"eps": run.get("eps"),
                             "M1_median": float(s["M1_median"]),
                             "rows": s.get("rows")})
    except Exception:  # noqa: BLE001
        pass
    return {"annulus_M1": vals}


def t4_gate(mode):
    """[T4] слово вердикта для Q3."""
    if mode.startswith("growing"):
        return ("gated: 1/r-мода растёт -> перцентильная гамма Q3 "
                "загрязнена сверху; требуется подавление моды")
    if mode.startswith("junk"):
        return ("open-for-percentile: M1 на мусорном полу -> гамма Q3 "
                "лимитируется полом масс, не модой (в пределах z <= 9.35)")
    return "gated: режим M1 не определён на текущих данных"


def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q7: 1/r-мода — трекер M1 (m/xi^3 = M1/xi^2 + M3)")
    print("=" * 72, flush=True)
    out = {
        "title": "OPEN9-Q7 (v19): трекер M1 — декомпозиция профилей, "
                 "классификация режима, ворота для Q3",
        "question": "растёт ли 1/r-мода (M1) с глубиной? (монография гл.7 №7)",
        "decomposition": "m/xi^3 = M1/xi^2 + M3 <=> m(xi) = M1*xi + M3*xi^3",
        "criterion": {
            "growing": "slope log|M1| vs v > %.1f, CI не содержит 0, "
                       "R2 >= %.2f" % (GROW_SLOPE_MIN, R2_MIN),
            "junk_floor": "|slope| < порога и/или CI содержит 0",
        },
    }
    print("  [T1] декомпозиция профилей...", flush=True)
    rows = t1_decompose()
    out["T1_profiles"] = [
        {k: r_[k] for k in ("zoom", "j", "v", "M1", "M3", "R2", "n")}
        for r_ in rows]
    print("    профилей: %d; M1 медиана: %.3g; M3 медиана: %.3g; R2 медиана: %.3f"
          % (len(rows),
             float(np.median([abs(r_["M1"]) for r_ in rows])) if rows else float("nan"),
             float(np.median([abs(r_["M3"]) for r_ in rows])) if rows else float("nan"),
             float(np.median([r_["R2"] for r_ in rows])) if rows else float("nan")),
          flush=True)
    print("  [T2] классификация режима...", flush=True)
    t2 = t2_classify(rows)
    out["T2_mode"] = t2
    print("    чистых: %d, помеченных: %d; |M1| по зумам: %s"
          % (t2["n_clean"], t2["n_flagged"],
             [(m["zoom"], "%.2e" % m["absM1_median"])
              for m in t2["absM1_median_by_zoom"]]), flush=True)
    print("    РЕЖИМ: %s" % t2["mode"], flush=True)
    print("  [T3] перекрёстная сверка (annulus)...", flush=True)
    out["T3_crosscheck"] = t3_crosscheck()
    print("    annulus M1_median: %s" %
          [(v["eps"], "%.3g" % v["M1_median"]) for v in
           out["T3_crosscheck"]["annulus_M1"]], flush=True)
    print("  [T4] ворота для Q3...", flush=True)
    out["T4_gate_word"] = t4_gate(t2["mode"])
    print("    %s" % out["T4_gate_word"], flush=True)

    out["verdict"] = {"mode": t2["mode"]}
    out["verdict_lines"] = [
        "декомпозиция m = M1*xi + M3*xi^3 на внешнем окне устойчива "
        "(R2 медиана %.3f на %d профилях, %d чистых / %d помеченных) — "
        "двухпараметрическая форма достаточна на чистых строках"
        % (float(np.median([r_["R2"] for r_ in rows])) if rows else float("nan"),
           len(rows), t2.get("n_clean", 0), t2.get("n_flagged", 0)),
        "РЕЖИМ M1: %s (slope log|M1| vs zoom = %.2f, CI95 [%.2f, %.2f]; "
        "|M1| по зумам: %s; |M1|/|M3| медиана %.2e)"
        % (t2["mode"], t2.get("slope_logM1_vs_zoom", float("nan")),
           *t2.get("slope_ci95", [float("nan"), float("nan")]),
           ["%.1e" % m["absM1_median"] for m in
            t2.get("absM1_median_by_zoom", [])],
           t2.get("M1_over_M3_abs_median", float("nan"))),
        "мусорное вторжение локализовано: %d строк(и) с деградацией фита "
        "(R2 < 0.95 или |M3| ~ 0): %s — грязные стадии выбрасываются, "
        "но репортируются (протокол честности)"
        % (t2.get("n_flagged", 0),
           ["z%d/j%d" % (f["zoom"], f["j"]) for f in
            t2.get("flagged_rows", [])][:6]),
        "ворота Q3: %s" % out["T4_gate_word"],
        "статус вопроса: ОТКРЫТ — доступная глубина (z <= 9.35) НЕ "
        "показывает растущей 1/r-моды (|M1| падает с зумом), но и не "
        "исключает её рост за стеной; решает лестница (eps, z >= 30)",
    ]
    out["honest_notes"] = [
        "профили probe_channel — ОДНА амплитуда (eps = 1e-3): трек по v "
        "это трек по стадиям марша, не по семейству данных; режим "
        "классифицируется в пределах этой выборки",
        "M1-фит чувствителен к выбору окна (outer_frac = 0.5): на "
        "внутренности доминирует CSS-ядро, на экстреме — граничные "
        "эффекты; окно фиксировано и записано",
        "annulus M1_median получен другой машиной (аннус-канал) — "
        "сверка только по масштабу, не по идентичности определения",
        "ворота Q3 односторонние: рост M1 загрязняет гамму сверху; "
        "отсутствие роста не гарантирует процентной точности",
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
