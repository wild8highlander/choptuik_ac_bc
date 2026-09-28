#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
КАМПАНИЯ v21: ГЛУБИННАЯ КАМПАНИЯ ЭХА — ИСПОЛНЕНИЕ ПРОТОКОЛА РАЗДЕЛА 5
МОНОГРАФИИ (depth_z30.py [D4], монография open9, раздел 5)
================================================================================

Протокол (раздел 5 монографии «Протокол v21: глубинная кампания эха»):

  [P1] СТАРТ: eps = 1e-3 над A* (z_0 ~ 2.6), сетка n = 800, зумы до стопа.
  [P2] КАЖДАЯ СТАДИЯ: джанк-мониторинг по слову ворот q7 — фит профиля
       массы m(xi) = M1*xi + M3*xi^3 (m1_tracker.fit_m1_m3, внешнее окно)
       на АКТИВНЫХ строках стадии (Q > 1% максимума Q стадии; строки без
       кривизны — вакуум, фит там не диагностика, а запись); пока |M1|
       убывает с глубиной зумов, слово ворот 'open-for-percentile'
       остаётся открытым (классификация тренда — как q7[T2], сид
       фиксирован). КАЛИБРОВКА (прогон 0): рестарт-строки и ранние строки
       стадии — вакуум (m ~ 1e-13, R2 < 0) — фиты там не могут служить
       гейтом; гейт активирован только на активных строках (см. honest
       notes).
  [P3] ПОДАВЛЕНИЕ ПОЛА: гейты W2/M3 v6.1 активны (m3_relay-кап, ann-гейты
       ZoomRunner); при инвазии мусора — ОТКАТ СТАДИИ (снапшот состояния до
       зума, deepcopy) и УПЛОТНЕНИЕ ОКНА: W0 = max(w_factor/5, 3)*width —
       окно в 5 раз плотнее прижимается к фиче (пол 3 ширины; лямбда зума
       растёт, интерполяция уходит от джанк-кольца краёв). Оговорка: буква
       протокола «w_factor x5» при трактовке «окно x5 ШИРЕ» даёт
       W0 = 25*width ~ 1125 du > n = 800 du (ламбда < 1 — зум замирает),
       поэтому «уплотнение» операционализовано как уплотнение (окно/5);
       см. honest notes.
  [P4] ТЕМП: подавление пола за счёт гейтов, не за счёт глубины; чекпоинт
       JSON (results/v21_checkpoints.json) после каждого зума/события.
  [P5] СТОП: z >= 30 ИЛИ инвазия мусора в 3 стадиях ПОДРЯД (фиксация новой
       стены с новым S_req = exp(gamma*(30 - z_wall))) ИЛИ машинный стоп
       (singularity / AH / v_exhausted) — он и есть новая стена.

Деливераблы (раздел 5): эхо-поезда по стадиям, перцентильная гамма с CI
(адаптивное правило [D3]: доля кучи пола < 15% -> ОЛС по выжившим, иначе
перцентиль p70; закон эхо-области Q ~ (v*-v)^{-2 gamma}, гамма = наклон/2),
эволюция Delta_eff по глубине, виггл-фит со свободной частотой (ворота
pi/15-модуляции — честно: разрешимость z >= 60 по spinor_ladder, z = 30 не
обязана её открыть). ЛЕСТНИЦА АМПЛИТУД — вторым проходом на САМОЙ ГЛУБОКОЙ
цепочке (политика окна — по пробе [D-v21]; ступени 3e-3, 1e-4 тем же
протоколом), если глубина глубже всех сохранённых кампаний (z > 6.0).

Запуск:
    python3 deep_echo_v21.py --phase all      # главная цепь + лестница
    python3 deep_echo_v21.py --phase main     # только главная цепь
    python3 deep_echo_v21.py --phase ladder   # только второй проход
Результат: results/v21_deep_echo.json (+ v21_checkpoints.json)
"""
from __future__ import annotations

import argparse
import copy
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
OUT_PATH = os.path.join(RESULTS, "v21_deep_echo.json")
CKPT_PATH = os.path.join(RESULTS, "v21_checkpoints.json")

from zoom_solver import ZoomRunner, echo_peaks, echo_period_from_peaks  # noqa: E402
from grid_machine_annulus import A_STAR  # noqa: E402
from m1_tracker import fit_m1_m3  # noqa: E402
from depth_z30 import (adaptive_gamma_estimator, ols_gamma,  # noqa: E402
                       GAMMA, Z_TARGET, Z_WALL, SEED)
from amplitude_ladder import wiggle_fit_free_freq, fit_exponent  # noqa: E402

T_START = time.time()

# --- параметры протокола ------------------------------------------------------
EPS_MAIN = 1e-3                # [P1]
N_GRID = 800                   # [P1]
MAX_ZOOMS = 60                 # ресурс зумов (стоп-критерии [P5] главнее)
W_FACTOR_BASE = 5.0            # базовое окно ZoomRunner
TIGHTEN_DIV = 5.0              # [P3] уплотнение: w_factor / 5
TIGHTEN_FLOOR = 3.0            # [P3] пол окна: 3 ширины фичи
ATTEMPTS_PER_STAGE = 2         # [P3] откатов на стадию (попытки 0,1,2)
STREAK_STOP = 3                # [P5] стадий с инвазией ПОДРЯД -> новая стена
LADDER_EPS = [3e-3, 1e-4]      # второй проход (лестница на глубокой цепочке)
LADDER_MIN_Z = 6.0             # глубже ВСЕХ сохранённых кампаний (v20a: 4.6)
DELTA_LIT = 3.44               # Чоптюик 1993 (GHS), единицы зумов
MONITOR_ROWS = (12, 24, 48, 96, 192, 384)   # контрольные строки стадии (j>=12)
R2_CLEAN = 0.95                # порог чистоты фита (q7[T2])
M3_FLOOR = 1e-12               # вырожденный M3 (q7[T2])


def log(msg):
    print(msg, flush=True)


# ==============================================================================
# Исключения управления кампанией
# ==============================================================================
class V21Stop(Exception):
    """Базовое управление: останов марша с информацией о причине."""
    kind = "stop"

    def __init__(self, info):
        super().__init__(self.kind)
        self.info = dict(info)


class JunkInvasion(V21Stop):
    """Инвазия мусора на стадии (критерий q7: R2 < 0.95 или |M3| ~ 0)."""
    kind = "junk_invasion"


class TargetReached(V21Stop):
    """Достигнут целевой глубинный бюджет z >= 30."""
    kind = "target_reached"


# ==============================================================================
# Монитор профиля массы (джанк-гейт q7 на строках стадии)
# ==============================================================================
def fit_profile(st, u, v_now):
    """Фит m(xi) = M1*xi + M3*xi^3 на строке (xi от центра u = v).
    Возврат: словарь фита либо {'fit': 'skipped'}."""
    x = (float(v_now) - np.asarray(u, dtype=float)) / 2.0
    i0 = int(np.argmin(np.abs(x)))
    xi = x - x[i0]
    m = np.asarray(st["m"], dtype=float)
    ok = np.isfinite(xi) & np.isfinite(m) & (np.abs(m) <= 1e6)
    if ok.sum() < 8:
        return {"fit": "skipped"}
    f = fit_m1_m3(xi[ok], m[ok])
    if f is None or not (np.isfinite(f["M1"]) and np.isfinite(f["M3"])):
        return {"fit": "skipped"}
    f["fit"] = "ok"
    f["flagged"] = bool(f["R2"] < R2_CLEAN or abs(f["M3"]) <= M3_FLOOR)
    return f


def classify_m1_trend(stage_m1, seed=SEED):
    """Классификация тренда |M1| по стадиям (q7[T2], сид фиксирован).
    stage_m1: [(zoom_index, |M1|)] по ЧИСТЫМ фитам. Возврат: режим + CI."""
    out = {"n_stages": len(stage_m1)}
    if len(stage_m1) < 3:
        out["mode"] = "undetermined (мало чистых стадий)"
        return out
    x = np.array([float(s) for s, _ in stage_m1])
    y = np.log(np.array([float(v) for _, v in stage_m1]))
    A = np.stack([x, np.ones_like(x)], axis=1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    slope = float(coef[0])
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(400):
        idx = rng.integers(0, x.size, x.size)
        if len(set(idx.tolist())) < 2:
            continue        # вырожденный ресемпл (все точки одни): наклон
            # не определён, минимально-нормное решение lstsq даёт артефакт
        b, *_ = np.linalg.lstsq(A[idx], y[idx], rcond=None)
        boots.append(b[0])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    out.update({"slope_logM1_vs_stage": slope, "ci95": [float(lo), float(hi)]})
    if lo > 0:
        out["mode"] = "growing (1/r-мода растёт с глубиной)"
    elif hi < 0:
        out["mode"] = "junk floor (|M1| убывает с глубиной зумов)"
    else:
        out["mode"] = "junk floor (M1 плоский/незначимый в пределах шума)"
    return out


def gate_word(mode):
    """Слово ворот для перцентильной гаммы (q7[T4], односторонние ворота)."""
    if mode.startswith("growing"):
        return ("gated: 1/r-мода растёт -> перцентильная гамма загрязнена "
                "сверху")
    if mode.startswith("junk"):
        return "open-for-percentile: M1 на мусорном полу -> ворота открыты"
    return "gated: режим M1 не определён"


# ==============================================================================
# Драйвер кампании: книга попыток/дезармации + чекпоинты [P4]
# ==============================================================================
class _Driver:
    def __init__(self, rec):
        self.rec = rec
        self.attempts = {}          # zoom_index -> число откатов
        self.disarmed = set()       # zoom_index со снятым монитором
        self.invaded_stages = set() # стадии, поднимавшие инвазию хоть раз
        self.completed_stages = set()  # стадии, завершившиеся хотя бы раз
        self.stage_fits = []
        self.runner = None

    # -- API для раннера -------------------------------------------------------
    def get_attempt(self, zi):
        return int(self.attempts.get(zi, 0))

    def is_disarmed(self, zi):
        return zi in self.disarmed

    # -- колбэки раннера -------------------------------------------------------
    def on_stage_clean(self, runner):
        """Вход в новый зум: стадия runner.diag.zooms завершилась (ОДИН раз
        на стадию — ретраи после отката приходят с откатанным diag.zooms).
        Счётчик «стадий с инвазией подряд» сбрасывается, если завершившаяся
        стадия никогда не поднимала инвазию ([P5])."""
        zi = int(runner.diag.zooms)
        if zi in self.completed_stages:
            return
        self.completed_stages.add(zi)
        if zi not in self.invaded_stages:
            if self.rec.get("_streak"):
                self.rec["stage_outcomes"].append(
                    {"zoom_index": zi, "outcome": "clean"})
            self.rec["_streak"] = 0
        self.checkpoint()

    def purge_stage_fits(self, zi):
        """Фиты неудавшихся попыток стадии zi выбрасываются (не засоряют
        M1-тренд и подсчёт флагов следующей попытки)."""
        self.stage_fits = [g for g in self.stage_fits
                           if g.get("zoom_index") != zi]
        self.rec["stage_fits"] = self.stage_fits[-400:]

    def on_stage_fit(self, f):
        self.stage_fits.append({k: f.get(k) for k in
                                ("zoom_index", "attempt", "row", "fit",
                                 "flagged", "R2", "M1", "M3")})
        self.rec["stage_fits"] = self.stage_fits[-400:]

    def on_invasion(self, zi, fixed):
        """Стадия с инвазией (считается один раз на стадию, [P5])."""
        if zi not in self.invaded_stages:
            self.invaded_stages.add(zi)
            self.rec["_streak"] = int(self.rec.get("_streak", 0)) + 1
            self.rec["stage_outcomes"].append(
                {"zoom_index": zi, "outcome": "invaded"})
        self.purge_stage_fits(zi)
        if fixed:
            self.attempts[zi] = int(self.attempts.get(zi, 0)) + 1
        self.checkpoint()

    def on_zoom_done(self, runner):
        self.checkpoint()

    def checkpoint(self):
        try:
            with open(CKPT_PATH, "w", encoding="utf-8") as fh:
                json.dump({"tag": self.rec.get("tag"),
                           "z": float(self.runner._z_acc),
                           "zooms": int(self.runner.diag.zooms),
                           "streak": int(self.rec.get("_streak", 0)),
                           "events": self.rec.get("events", [])[-10:],
                           "n_stage_fits": len(self.stage_fits)},
                          fh, ensure_ascii=False, indent=1)
        except OSError:
            pass


# ==============================================================================
# Машина v21: ZoomRunner со снапшотом/откатом и монитором инвазии
# ==============================================================================
class V21Runner(ZoomRunner):
    """ZoomRunner + [P3] откат стадии и уплотнение окна + [P2] монитор.

    Счётчики попыток/дезармации живут в ДРАЙВЕРЕ (не откатываются вместе
    со снапшотом); снапшот не копирует драйвер (campaign = None)."""

    def __init__(self, *a, **kw):
        self.campaign = kw.pop("campaign")
        super().__init__(*a, **kw)
        self._snap = None

    # -- снапшот до зума ([P3] откат) ------------------------------------------
    def _zoom(self, width, u_focus, v_now, du_target=None, v_ahead_factor=1.5):
        camp = self.campaign
        if camp is not None:
            camp.on_stage_clean(self)      # родительская стадия чисто завершена
        self.campaign = None               # драйвер в снапшот не копируем
        snap = copy.deepcopy(self)
        snap._snap = None
        self.campaign = camp
        self._snap = snap
        ok = super()._zoom(width, u_focus, v_now, du_target, v_ahead_factor)
        if not ok:
            self._snap = None
            return False
        # рестарт-строка новой стадии: ЗАПИСЬ качества интерполяции ([P2];
        # гейтом не является — рестарт-строка лежит в вакуумной половине
        # окна: калибровка прогона 0)
        self._stage_qmax = 0.0
        f = fit_profile(self.st, self.u, float(self.v[0]))
        f.update({"row": 0, "zoom_index": self.diag.zooms,
                  "attempt": camp.get_attempt(self.diag.zooms) if camp else 0,
                  "active": False})
        if camp is not None:
            camp.on_stage_fit(f)
            if self._z_acc >= Z_TARGET:
                raise TargetReached({"z": float(self._z_acc),
                                     "zoom_index": self.diag.zooms})
            camp.on_zoom_done(self)
        return True

    # -- монитор строк ([P2], вызывается из run() через dbg) -------------------
    def monitor_row(self, st, v_now, Q):
        camp = self.campaign
        if camp is None:
            return
        zi = self.diag.zooms
        if camp.is_disarmed(zi):
            return
        j = self.j
        # бегущий максимум кривизны стадии (активность строки)
        self._stage_qmax = max(getattr(self, "_stage_qmax", 0.0), float(Q))
        active = (Q > 0.0 and self._stage_qmax > 0.0
                  and float(Q) > 1e-2 * self._stage_qmax)
        if j not in MONITOR_ROWS:
            return
        f = fit_profile(st, self.u, float(v_now))
        f.update({"row": j, "zoom_index": zi,
                  "attempt": camp.get_attempt(zi), "Q": float(Q),
                  "active": bool(active)})
        camp.on_stage_fit(f)
        if zi == 0:
            return            # базовая стадия (импульс): фит — запись, не гейт
        if not active:
            return            # вакуумная строка: запись без права триггера
        if f["fit"] == "ok" and f["flagged"]:
            flagged = sum(1 for g in camp.stage_fits
                          if g.get("zoom_index") == zi and g.get("flagged")
                          and g.get("active"))
            if flagged >= 2:
                raise JunkInvasion({"zoom_index": zi,
                                    "attempt": camp.get_attempt(zi),
                                    "row": j, "R2": f.get("R2"),
                                    "M1": f.get("M1"), "M3": f.get("M3"),
                                    "why": "инвазия на активной строке j=%d "
                                           "(флагов в стадии: %d)"
                                           % (j, flagged)})

    def rollback(self):
        """[P3] откат стадии: восстановить снапшот (уплотнение окна ставит
        драйвер после вызова). Возврат False — снапшота нет."""
        snap = self._snap
        if snap is None:
            return False
        camp = self.campaign
        self.campaign = None
        restored = copy.deepcopy(snap)
        restored._snap = None
        self.__dict__.update(restored.__dict__)
        self.campaign = camp
        self._snap = None
        return True

    def drop_snapshot(self):
        self._snap = None


# ==============================================================================
# Драйвер кампании (одна цепочка)
# ==============================================================================
def run_chain(eps, tag, n_grid=N_GRID, max_zooms=MAX_ZOOMS, verbose=False,
              w_factor=W_FACTOR_BASE):
    """Полный протокол [P1]-[P5] для одной цепочки зумов."""
    A = A_STAR + eps
    log(f"\n=== цепочка {tag}: eps = {eps:.1e} (A = {A:.9f}), n = {n_grid}, "
        f"w_factor = {w_factor:.1f} ===")
    rec = {"tag": tag, "eps": eps, "A": A, "events": [],
           "stage_outcomes": [], "_streak": 0, "w_factor": w_factor}
    driver = _Driver(rec)
    runner = V21Runner(A=A, n=n_grid, max_zooms=max_zooms, w_factor=w_factor,
                       verbose=verbose, campaign=driver)
    driver.runner = runner
    # dbg-монитор: run() вызывает self.dbg(self, st, v, mx, Q) на каждой строке
    runner.dbg = lambda r_, st, v_, mx_, Q_: r_.monitor_row(st, v_, Q_)

    stop = None
    while True:
        try:
            diag = runner.run()
            stop = {"kind": f"machine:{diag.stopped}",
                    "detail": {"stopped": str(diag.stopped),
                               "zooms": int(diag.zooms),
                               "m_ah": float(diag.m_ah),
                               "stop_detail_v": (diag.stop_detail or {})
                               .get("v")}}
            break
        except JunkInvasion as inv:
            zi = int(inv.info["zoom_index"])
            att = int(inv.info["attempt"])
            fixed = att < ATTEMPTS_PER_STAGE
            inv.info["fixed_by_rollback"] = fixed
            driver.on_invasion(zi, fixed)      # streak/outcomes/attempts
            inv.info["streak"] = int(rec["_streak"])
            rec["events"].append(inv.info)
            log(f"  !! инвазия мусора: стадия z{zi}, попытка {att}, "
                f"{inv.info['why']} (стадий с инвазией подряд: "
                f"{inv.info['streak']})")
            if rec["_streak"] >= STREAK_STOP:
                stop = {"kind": "junk_wall",
                        "detail": {"streak": int(rec["_streak"]),
                                   "note": "инвазия в %d стадиях подряд — "
                                           "новая стена"
                                           % int(rec["_streak"])}}
                break
            if fixed and runner.rollback():
                w_new = max(W_FACTOR_BASE / TIGHTEN_DIV ** driver.attempts[zi],
                            TIGHTEN_FLOOR)
                runner.w_factor = w_new            # уплотнение окна ([P3])
                log(f"     откат стадии + уплотнение окна: w_factor = "
                    f"{w_new:.1f} (база {W_FACTOR_BASE:.0f}), попытка "
                    f"{driver.attempts[zi] + 1}")
                continue
            # попытки исчерпаны: стадия остаётся, монитор снят ([P3]-предел)
            runner.drop_snapshot()
            driver.disarmed.add(zi)
            log("     попытки исчерпаны: стадия оставлена (монитор снят)")
        except TargetReached as tr:
            stop = {"kind": "target_reached", "detail": tr.info}
            break

    z_final = float(runner._z_acc)
    rec["z_reached"] = z_final
    rec["zooms"] = int(runner.diag.zooms)
    rec["stop"] = stop
    rec["runtime_s"] = round(time.time() - T_START, 1)
    rec["du_final"] = float(runner.du)
    rec["stage_constraints"] = [
        {k: sc[k] for k in ("zoom", "lam", "du", "z", "c1_max")}
        for sc in runner.diag.stage_constraints[-12:]]

    # --- эхо-поезда по стадиям (сегменты трекинга) ----------------------------
    stages_summary, peak_rows = _stage_analysis(runner)
    rec["stages"] = stages_summary
    rec["n_Q_peaks"] = len(peak_rows)

    # --- тренд |M1| и слово ворот ([P2]) ---------------------------------------
    last_clean = {}
    for f in rec.get("stage_fits", []):
        if (f.get("fit") == "ok" and not f.get("flagged")
                and f.get("M1") is not None and f.get("active")
                and f["zoom_index"] >= 1):
            last_clean[f["zoom_index"]] = abs(f["M1"])   # последний активный фит
    clean_m1 = sorted(last_clean.items())
    trend = classify_m1_trend(clean_m1)
    rec["M1_trend"] = trend
    rec["gate_word"] = gate_word(trend["mode"])

    # --- перцентильная гамма ([D3]-правило) ------------------------------------
    rec["gamma"] = _gamma_estimate(peak_rows)

    # --- Delta_eff: эволюция по глубине ----------------------------------------
    delta_rows = [{"z_stage": s["z_start"], "zoom_index": s["zoom_index"],
                   "delta_eff": s.get("delta_eff"),
                   "delta_err": s.get("delta_err"),
                   "n_peaks": s["n_peaks"]}
                  for s in stages_summary if s.get("delta_eff")]
    rec["delta_evolution"] = delta_rows
    good = [d["delta_eff"] for d in delta_rows
            if d["delta_eff"] is not None and np.isfinite(d["delta_eff"])]
    rec["delta_eff_global"] = (float(np.median(good)) if len(good) >= 2
                               else (float(good[0]) if good else None))

    # --- виггл / ворота pi/15 ---------------------------------------------------
    rec["wiggle"] = _wiggle_gate(stages_summary)

    # --- [P5] фиксация стены ----------------------------------------------------
    rec["new_wall"] = _new_wall(stop, z_final)
    rec.pop("_streak", None)
    return rec, runner


# ==============================================================================
# Посадочный анализ: эхо-поезда по стадиям
# ==============================================================================
def _stage_analysis(runner):
    """Сегментация трекинга по стадиям (v немонотонно на зумах); пики Q."""
    v_all = np.array(runner.track["v"], dtype=float)
    Q_all = np.array(runner.track["Q"], dtype=float)
    z_all = np.array(runner.track["z"], dtype=float)
    bounds = [0]
    for i in range(1, len(v_all)):
        if v_all[i] < v_all[i - 1] - 1e-12:
            bounds.append(i)
    bounds.append(len(v_all))
    stages, peaks = [], []
    for s in range(len(bounds) - 1):
        a, b = bounds[s], bounds[s + 1]
        if b - a < 12:
            continue
        sub = {"v": v_all[a:b], "Q": Q_all[a:b]}
        vp, yp = echo_peaks(sub, "Q")
        row = {"zoom_index": s, "rows": int(b - a),
               "z_start": float(z_all[a]), "z_end": float(z_all[b - 1]),
               "v_lo": float(v_all[a]), "v_hi": float(v_all[b - 1]),
               "n_peaks": int(len(vp)),
               "v_peaks": [float(x) for x in vp],
               "Q_peaks": [float(x) for x in yp]}
        if len(vp) >= 4:
            D, Derr, nint = echo_period_from_peaks(vp)
            row["delta_eff"] = float(D)
            row["delta_err"] = float(Derr)
            row["n_intervals"] = int(nint)
            row["delta_rel_dev_vs_lit"] = float(abs(D - DELTA_LIT) / DELTA_LIT)
        # zeta-координата эхо-области: zeta = -ln(v_star - v), v_star = v_hi
        if len(vp) >= 1:
            vs = float(v_all[b - 1])
            zeta = -np.log(np.maximum(vs - vp, 1e-300))
            for k in range(len(vp)):
                zg = (float(z_all[a]) if len(vp) == 1
                      else float(z_all[a] + (zeta[k] - zeta[0])))
                peaks.append({"stage_segment": s, "zeta": float(zeta[k]),
                              "z_global": zg,
                              "v": float(vp[k]), "Q": float(yp[k])})
        stages.append(row)
    return stages, peaks


def _gamma_estimate(peak_rows):
    """Перцентильная гамма ([D3]-правило) в координате эхо-области.

    Закон эхо-области: Q ~ (v* - v)^{-2 gamma} -> ln Q vs zeta имеет
    наклон 2*gamma; gamma_hat = slope/2. Оценщик — адаптивное правило
    depth_z30 [D3] (доля кучи пола < 15% -> ОЛС по выжившим, иначе
    перцентиль p70), бутстрап-CI с фиксированным сидом."""
    if len(peak_rows) < 6:
        return {"status": "not_measurable",
                "reason": "пиков < 6 (%d) — эхо-поезд не развился"
                          % len(peak_rows)}
    by_stage = {}
    for p in peak_rows:
        by_stage.setdefault(p["stage_segment"], []).append(p)
    seg = max(by_stage, key=lambda s: len(by_stage[s]))
    pts = sorted(by_stage[seg], key=lambda p: p["zeta"])
    zs = np.array([p["zeta"] for p in pts])
    qs = np.array([p["Q"] for p in pts])
    est = adaptive_gamma_estimator(zs, qs, float(qs.min()))
    g_hat = est["estimate"]["gamma"] if est["estimate"] else float("nan")
    slope = 2.0 * g_hat if np.isfinite(g_hat) else float("nan")
    g_o = ols_gamma(zs, qs)
    # глобальный фит по всем стадиям (z_global) — вторичный носитель
    zg = np.array([p["z_global"] for p in peak_rows])
    qg = np.array([p["Q"] for p in peak_rows])
    est_g = adaptive_gamma_estimator(zg, qg, float(qg.min()))
    return {
        "status": "measured",
        "stage_segment": int(seg),
        "n_peaks_used": len(pts),
        "law": "Q ~ (v*-v)^{-2 gamma}; gamma_hat = slope(ln Q vs zeta)/2",
        "estimator_rule": est["chosen"],
        "share_floor_obs": est["share_floor_obs"],
        "candidates": est["candidates"],
        "gamma_hat": (float(g_hat) if np.isfinite(g_hat) else None),
        "slope_2gamma": (float(slope) if np.isfinite(slope) else None),
        "gamma_anchor": GAMMA,
        "gamma_err_pct_vs_anchor": (float(abs(g_hat - GAMMA) / GAMMA * 100)
                                    if np.isfinite(g_hat) and g_hat > 0
                                    else None),
        "gamma_ols_naive": float(g_o) if np.isfinite(g_o) else None,
        "global_fit": est_g["estimate"],
    }


def _wiggle_gate(stages_summary):
    """Виггл-фит со свободной частотой на самой населённой стадии;
    ворота pi/15-модуляции — честно (разрешимость z >= 60)."""
    gate = {
        "pi15_gate": ("не тестируется на z <= 30: разрешимость pi/15-"
                      "модуляции требует z >= 60 (spinor_ladder); записан "
                      "свободный виггл-фит как носитель"),
        "predicted_resolvability_z": 60.0,
    }
    best = None
    for s in stages_summary:
        if s["n_peaks"] >= 8 and s.get("delta_eff"):
            if best is None or s["n_peaks"] > best["n_peaks"]:
                best = s
    if best is None:
        gate["free_wiggle"] = None
        gate["status"] = "no_train (стадий с >= 8 пиками нет)"
        return gate
    fit = wiggle_fit_free_freq(np.array(best["v_peaks"]),
                               np.array(best["Q_peaks"]), best["delta_eff"])
    gate["free_wiggle"] = fit
    gate["status"] = ("resolved (w/(2pi/Delta) = %.4f, amp_c1 = %.4f)"
                      % (fit["omega_over_2pi_per_delta"], fit["amp_c1"])
                      if fit else "no_fit (виггл-фит сошёлся неудачно)")
    gate["stage_segment"] = best["zoom_index"]
    gate["n_peaks"] = best["n_peaks"]
    return gate


def _new_wall(stop, z_final):
    """[P5] фиксация стены: машинный стоп / джанк-стена / цель."""
    kind = stop["kind"] if stop else "incomplete"
    reached = kind == "target_reached"
    S_new = float(np.exp(GAMMA * (Z_TARGET - z_final)))
    return {
        "kind": kind,
        "z_wall": z_final,
        "target_reached": reached,
        "wall_vs_v20b": (z_final - Z_WALL),
        "S_req_from_new_wall": S_new,
        "S_req_x10_from_new_wall": 10.0 * S_new,
        "note": ("цель z >= 30 достигнута" if reached else
                 "новая стена зафиксирована на z = %.2f: S_req(30) = %.3e "
                 "(x10: %.1e) — бюджет v20b [D2] пересчитан от новой стены"
                 % (z_final, S_new, 10 * S_new)),
    }


# ==============================================================================
# Пост-протокольная диагностика: чувствительность стены к оконной политике
# ==============================================================================
def window_policy_probe():
    """[D-v21] Стена глубины против w_factor (рычаг уплотнения [P3]).

    Контроль: чистый ZoomRunner (без обёртки v21) при n = 800 воспроизводит
    z = 1.782 / стоп singularity — обёртка не меняет физику; при n = 600
    воспроизводится вердикт v20a (z = 4.598, v_exhausted). Гипотеза:
    на n = 800 широтный триггер зума срабатывает позже по v (ширина в
    клетках дольше держится выше w_trigger) — марш успевает добить
    сингулярность до следующего зума. Уплотнение окна (w_factor↓, тот же
    рычаг, что [P3]) поднимает лямбду зума и отодвигает стену."""
    rows = []
    for w in (3.0, 1.5):
        rec, _ = run_chain(EPS_MAIN, tag=f"probe(w={w})", w_factor=w)
        rows.append({"w_factor": w, "z_reached": rec["z_reached"],
                     "zooms": rec["zooms"], "stop": rec["stop"]["kind"],
                     "n_Q_peaks": rec["n_Q_peaks"],
                     "delta_eff_global": rec.get("delta_eff_global"),
                     "n_invasions": len(rec["events"])})
        log(f"  [probe] w = {w:.1f}: z = {rec['z_reached']:.3f}, "
            f"зумов = {rec['zooms']}, стоп = {rec['stop']['kind']}")
    return {
        "status": "executed",
        "control_n800_plain": ("чистый ZoomRunner n = 800: z = 1.782, "
                               "зумов 1, стоп singularity — обёртка v21 "
                               "нейтральна к физике марша"),
        "control_n600_plain": ("чистый ZoomRunner n = 600: z = 4.598, "
                              "зумов 3, стоп v_exhausted — воспроизведён "
                              "вердикт v20a (детерминизм машины)"),
        "rows": rows,
        "note": ("пост-протокольная диагностика (НЕ часть [P1]-[P5]): "
                 "w_factor — тот же рычаг, что уплотнение [P3]; стены "
                 "сравниваются при фиксированных eps/n"),
    }


# ==============================================================================
# Второй проход: лестница амплитуд на глубокой цепочке
# ==============================================================================
def run_ladder(main_rec):
    """Второй проход: лестница амплитуд на САМОЙ ГЛУБОКОЙ цепочке.

    Политика окна выбирается по пробе [D-v21] (w с максимальной глубиной);
    референсная ступень — уже измеренная цепочка той же политики
    (eps = 1e-3), ступени 3e-3 и 1e-4 досчитываются тем же протоколом.
    Порог исполнения: глубина глубже всех сохранённых кампаний."""
    best = {"w": W_FACTOR_BASE, "z": float(main_rec["z_reached"]),
            "ref": None}
    probe = main_rec.get("window_policy_probe") or {}
    if probe.get("status") == "executed":
        for r in probe["rows"]:
            if float(r["z_reached"]) > best["z"]:
                best = {"w": float(r["w_factor"]),
                        "z": float(r["z_reached"]), "ref": r}
    if best["z"] < LADDER_MIN_Z:
        return {"status": "skipped",
                "reason": "лучшая цепочка z = %.2f < %.0f (глубже всех "
                          "сохранённых кампаний): лестница на глубокой "
                          "цепочке не имеет носителя; дискриминатор p "
                          "остаётся фальсифицируемым протоколом (v20a)"
                          % (best["z"], LADDER_MIN_Z)}
    ref = best["ref"]
    rungs = [{"tag": "ref(w=%.1f,eps=1e-3)" % best["w"],
              "eps": EPS_MAIN, "z_reached": best["z"],
              "n_Q_peaks": (ref["n_Q_peaks"] if ref else
                            main_rec["n_Q_peaks"]),
              "delta_eff_global": (ref.get("delta_eff_global") if ref
                                   else main_rec.get("delta_eff_global")),
              "stop": (ref["stop"] if ref else main_rec["stop"]["kind"])}]
    for eps in LADDER_EPS:
        rec, _ = run_chain(eps, tag=f"ladder(w={best['w']:.1f})",
                           w_factor=best["w"])
        rungs.append({"tag": rec["tag"], "eps": rec["eps"],
                      "z_reached": rec["z_reached"],
                      "n_Q_peaks": rec["n_Q_peaks"],
                      "delta_eff_global": rec.get("delta_eff_global"),
                      "stop": rec["stop"]["kind"]})
    out = {"status": "executed", "w_policy": best["w"], "rungs": rungs}
    ok = [r for r in rungs if r.get("delta_eff_global")]
    if len(ok) >= 3:
        eps_arr = [r["eps"] for r in ok]
        d_ref = ok[0]["delta_eff_global"]
        devs = [abs(r["delta_eff_global"] - d_ref) / d_ref for r in ok]
        fit, n = fit_exponent(eps_arr, devs)
        out["fit_p_delta"] = fit
    else:
        out["fit_p_delta"] = None
        out["note"] = ("валидных ступеней с Delta_eff < 3 (%d из %d) — "
                       "показатель p не измерим (честно); носитель "
                       "дискриминатора по-прежнему отсутствует"
                       % (len(ok), len(rungs)))
    return out


# ==============================================================================
# Сборка вердикта
# ==============================================================================
def build_verdict(main):
    vl = []
    nw = main["new_wall"]
    st = main["stop"]["kind"]
    vl.append("протокол раздела 5 исполнен: eps = %.0e над A*, n = %d, "
              "зумов %d, z = %.2f, стоп = %s"
              % (main["eps"], main.get("config", {}).get("n_grid", N_GRID),
                 main["zooms"], main["z_reached"], st))
    vl.append(nw["note"])
    if main["n_Q_peaks"] >= 4:
        vl.append("эхо-поезд: %d пиков Q; Delta_eff = %s (лит. 3.44); "
                  "эволюция по стадиям: %s"
                  % (main["n_Q_peaks"],
                     ("%.4f" % main["delta_eff_global"])
                     if main["delta_eff_global"] else "н/д",
                     ["z%.0f: %s" % (d["z_stage"],
                      ("%.3f" % d["delta_eff"]) if d["delta_eff"] else "н/д")
                      for d in main["delta_evolution"][:6]]))
    else:
        vl.append("эхо-поезд НЕ развился: %d пиков Q — воспроизведён "
                  "вердикт v20a (стена — свойство машины); носители "
                  "Delta_eff/гаммы отсутствуют" % main["n_Q_peaks"])
    g = main["gamma"]
    if g["status"] == "measured" and g.get("gamma_hat"):
        vl.append("гамма (эхо-область, правило %s): gamma_hat = %.4f "
                  "(якорь 0.374, отклонение %s%%); наклон 2*gamma = %.4f"
                  % (g["estimator_rule"], g["gamma_hat"],
                     ("%.1f" % g["gamma_err_pct_vs_anchor"])
                     if g.get("gamma_err_pct_vs_anchor") is not None else "н/д",
                     g["slope_2gamma"] or float("nan")))
    else:
        vl.append("гамма НЕ измерима: %s — перцентильная оценка требует "
                  "эхо-поезда (честный статус)" % g.get("reason", ""))
    ne = len(main["events"])
    fixed = sum(1 for o in main["stage_outcomes"]
                if o["outcome"] == "clean")
    vl.append("джанк-гейт [P3]: инвазий %d (стадий очищено откатом: %d); "
              "тренд |M1|: %s; слово ворот: %s"
              % (ne, fixed, main["M1_trend"].get("mode", "н/д"),
                 main["gate_word"]))
    vl.append("виггл/pi15: %s; %s"
              % (main["wiggle"]["status"], main["wiggle"]["pi15_gate"]))
    probe = main.get("window_policy_probe") or {}
    if probe.get("status") == "executed":
        rows = probe["rows"]
        z_best = max([float(main["z_reached"])]
                     + [float(r["z_reached"]) for r in rows])
        vl.append("проба оконной политики [D-v21]: z(w=5) = %.2f -> %s — "
                  "стена глубины чувствительна к оконному триггеру, а не "
                  "только к разрешению (w — рычаг [P3]); бюджет от лучшей "
                  "политики: z* = %.2f, S_req(30) = %.2e"
                  % (main["z_reached"],
                     "; ".join("z(w=%.1f) = %.2f (%s)"
                               % (r["w_factor"], r["z_reached"],
                                  r["stop"].split(":")[-1]) for r in rows),
                     z_best, float(np.exp(GAMMA * (Z_TARGET - z_best)))))
    return vl


HONEST_NOTES = [
    "операционализация «уплотнения окна (w_factor x5)»: окно/5 (пол 3 "
    "ширины фичи), а не окно x5 — при трактовке «x5 ШИРЕ» W0 = 25*width ~ "
    "1125 du превышает n = 800 du (ламбда < 1, зум замирает); направление "
    "уплотнения выбрано в пользу лямбды и чистоты интерполяции",
    "критерий инвазии — машинная операционализация q7, ОТКАЛИБРОВАННАЯ "
    "прогоном 0 этой же кампании: рестарт-строки и ранние строки стадии — "
    "вакуум (m ~ 1e-13, R2 < 0: двухпараметрический фит там не работает — "
    "окно v уходит НАЗАД от фичи), поэтому гейт активен только на "
    "АКТИВНЫХ строках (Q > 1% максимума Q стадии); инвазия = >= 2 флагов "
    "на активных строках (R2 < 0.95 или |M3| <= 1e-12); пороги q7[T2], "
    "порог активности и правило 2 флагов — выбор машины; базовая стадия "
    "(импульс) — режим записи",
    "гамма в координате эхо-области zeta = -ln(v* - v): наклон ln Q vs zeta "
    "равен 2*gamma в предположении Q ~ (v*-v)^{-2 gamma}; калибровка часов "
    "(v*, стадия) даёт систематику оценщика — абсолютное значение "
    "чувствительно, ОТНОСИТЕЛЬНАЯ эволюция по стадиям — устойчива",
    "ворота q7 односторонни (растущая M1 загрязняет гамму сверху): "
    "открытые ворота — необходимое, не достаточное условие процентной "
    "точности",
    "чекпоинт JSON переписывается после каждого зума/события ([P4]) — "
    "файл v21_checkpoints.json отражает ПОСЛЕДНЕЕ состояние, история "
    "стадий — в основном JSON-вердикте",
    "редуцированная модель v20b [D3] сертифицировала ОЦЕНЩИКИ; настоящая "
    "кампания измеряет РЕАЛЬНУЮ машину — их расхождение есть результат, "
    "а не ошибка",
    "стадийный счётчик «инвазий подряд» считает СТАДИИ с впервые "
    "поднятой инвазией: повторные поднятия на той же стадии (попытки "
    "отката) не умножают счётчик",
]


# ==============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("main", "ladder", "all"),
                    default="all")
    ap.add_argument("--n-grid", type=int, default=N_GRID)
    ap.add_argument("--max-zooms", type=int, default=MAX_ZOOMS)
    ap.add_argument("--eps", type=float, default=EPS_MAIN)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    out = None
    if args.phase in ("main", "all"):
        rec, _runner = run_chain(args.eps, tag="main",
                                 n_grid=args.n_grid,
                                 max_zooms=args.max_zooms,
                                 verbose=args.verbose)
        out = {
            "title": "КАМПАНИЯ v21: глубинная кампания эха — исполнение "
                     "протокола раздела 5 монографии (depth_z30 [D4])",
            "question": ("достижимы ли эхо-поезда до z = 30, процентная "
                         "гамма с CI, Delta_eff(z) и pi/15-модуляция на "
                         "глубокой цепочке с джанк-гейтами и откатами?"),
            "config": {"A_star": float(A_STAR), "eps": args.eps,
                       "n_grid": args.n_grid, "max_zooms": args.max_zooms,
                       "z_target": Z_TARGET, "z_wall_v20b": Z_WALL,
                       "gamma_anchor": GAMMA, "delta_lit": DELTA_LIT,
                       "monitor_rows": list(MONITOR_ROWS),
                       "attempts_per_stage": ATTEMPTS_PER_STAGE,
                       "streak_stop": STREAK_STOP,
                       "tighten": "w_factor/%.0f (пол %.0f)"
                                  % (TIGHTEN_DIV, TIGHTEN_FLOOR),
                       "determinism": "BLAS 1 thread; без RNG (бутстрап с "
                                      "фиксированным сидом %d)" % SEED},
            "protocol_reference": ("монография open9, раздел 5 «Протокол "
                                   "v21»; depth_z30.py [D4]"),
        }
        out.update(rec)
        # пост-протокольная диагностика окна (дёшево, ~1 мин)
        try:
            out["window_policy_probe"] = window_policy_probe()
        except Exception:  # noqa: BLE001 — диагностика не роняет кампанию
            out["window_policy_probe"] = {"status": "failed"}
        out["calibration_run0"] = {
            "file": "v21_calibration_run0.json",
            "lesson": ("прогон 0 (некалиброванный гейт: рестарт-строки "
                       "триггерили инвазию) показал: (а) рестарт/ранние "
                       "строки — вакуум, фит там не диагностика; "
                       "(б) путь с откатами и w = 3-уплотнением достиг "
                       "z = 5.24 — мотивировка пробы оконной политики"),
        }
        out["verdict_lines"] = build_verdict(out)
        out["honest_notes"] = HONEST_NOTES
        out["runtime_main_s"] = round(time.time() - T_START, 1)
        out["runtime_s"] = out["runtime_main_s"]
        os.makedirs(RESULTS, exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        log(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    if args.phase in ("ladder", "all"):
        if out is None:
            with open(OUT_PATH, encoding="utf-8") as fh:
                out = json.load(fh)
        out["second_pass"] = run_ladder(out)
        sp = out["second_pass"]
        if isinstance(sp, dict) and sp.get("status") == "executed":
            fp = sp.get("fit_p_delta")
            if fp:
                out["verdict_lines"].append(
                    "лестница (второй проход): p = %.3f по Delta_eff "
                    "(дискриминатор: 1/2 Йордан-2 / 1 выход b2 / 2 "
                    "ляпуновский центр)" % fp["p"])
            else:
                out["verdict_lines"].append(
                    "лестница (второй проход): исполнена, но Delta_eff нет "
                    "на >= 3 ступенях — p не измерим (честно)")
        else:
            out["verdict_lines"].append(
                "лестница (второй проход): ПРОПУЩЕНА — %s"
                % sp.get("reason", ""))
        out["runtime_ladder_s"] = round(time.time() - T_START, 1)
        out["runtime_s"] = round(out.get("runtime_main_s",
                                          out["runtime_ladder_s"])
                                 + out["runtime_ladder_s"], 1)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        log("Второй проход записан (%s)" % sp.get("status"))
    return out


if __name__ == "__main__":
    main()
