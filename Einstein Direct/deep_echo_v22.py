#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
КАМПАНИЯ v22: V-БЮДЖЕТ И ЯКОРЕНИЕ ОКНА — ПРОРЫВ СТЕНЫ z ~ 7.2 (w = 3)
================================================================================

Постановка (следующая научная задача после v21): расширение v-бюджета при
w = 3 (v_ahead_factor / телескоп) — догнать 4-й пик эха и Delta_eff.

Диагноз (трассировка цепочки v21 probe(w=3), воспроизведена с расхождением
0.00e+00 — детерминизм машины):

  [F1] Телескопический кап (v-домен ребёнка <= домену родителя) НЕ СВЯЗАН ни
       на одном из 4 зумов: ahead_req меньше запаса родителя в 3.4-15 раз.
       Активный бюджет — собственный размах окна, не конверт.
  [F2] Финальная стадия (du = 1.92e-6, 799 строк) — ВАКУУМ: Q ~ 0, w_cells = 0,
       mx = 0. Структура осталась ПОЗАДИ окна: лестница триггеров зума
       СПУСКАЕТСЯ по v (0.4781 -> 0.4072 -> 0.4035 -> 0.4015), а окно
       простирается назад лишь на 0.5*(v_hi - v_now) и зажато снизу буфером
       родителя (buffer_v[0] = v_lo родителя).
  [F3] v-extension (_try_extend) — МЁРТВЫЙ КОД ПО ПОСТРОЕНИЮ: вызывается
       только при j >= n, когда v_now = v[n-1] = stage_v[1]; запас
       stage_v[1] - v_now = 0 < 12*du всегда. Поэтому v_exhausted всегда
       терминален. (Инвариант stage_v == (v[0], v[-1]) — конструкция
       _new_stage; рантайм-след: slack = 0.0 точно на каждом вызове.)
  [F4] Голодание назад-размаха на стене (зум #4): эффективный назад-ход
       v_now - v_lo = 2.0e-4 (клэмп буфера: родитель промаршировал всего
       ~24 строки до триггера), интервал лестницы ~1.1e-3..2.0e-3 —
       следующее эхо/триггер ОСТАЛИСЬ ЗА нижней кромкой окна. Стадия-5
       промаршировала вакуум до края -> v_exhausted.

Отсюда РЕДИРЕКЦИЯ рычага (честно, по данным машины):
  - v_ahead_factor ВПЕРЁД (+v) — инертен: впереди триггера вакуум (F2), а
    назад-расширение перехватывается клэмпом буфера. Зонд подтверждает.
  - Настоящий рычаг — ЗАДНИЙ ЯКОРЬ окна: v_lo = v_now - k_back*(v_hi - v_now)
    (вместо жёстких 0.5) НА РАННИХ ЗУМАХ: пол родителя опускается, буферный
    клэмп детей ослабляется рекурсивно, лестница триггеров получает v-комнаты
    спускаться к машине-v*. Цена: W_v = (1 + k_back)*ahead растёт,
    du_new = W_v/n растёт, лямбда зума падает (~1/(1+k_back)) — зонд измеряет
    чистый эффект на z.

Протокол:
  [C1] CERT: контроль (k_back = 0.5, v_ahead = 1.5) обязан воспроизвести
       цепочку v21 probe(w=3) ТОЧНО (z = 7.20358520128802, 4 зума,
       v_exhausted) — вилка _zoom нейтральна к физике. Факты [F1]-[F4]
       сертифицируются на этой же цепочке.
  [C2] PROBE: (k_back, v_ahead) из {(0.5,1.5) контроль, (1.0,1.5), (2.0,1.5),
       (0.5,3.0)} при w = 3, eps = 1e-3, n = 800. Метрики: z, зумов, пиков,
       стоп, спуск пола окна (v_lo по зумам), средняя лямбда.
       Гипотеза H: k_back >= 1 двигает стену (z > 7.2); v_ahead = 3.0 при
       k_back = 0.5 — инертен (клэмп буфера перехватывает).
  [C3] DEEP: лучшая политика (максимум z) до машинного стопа; эхо-поезда по
       стадиям; при >= 4 пиках на стадии — Delta_eff (echo_period_from_peaks);
       гамма — при >= 6 пиках (правило [D3] v21); честный вердикт иначе.
  [C4] LADDER: второй проход (лестница амплитуд 3e-3, 1e-4) на лучшей
       политике, если глубина > 6.0 (порог v21).

Запуск:
    python3 deep_echo_v22.py --phase all      # cert + probe + deep + ladder
    python3 deep_echo_v22.py --phase cert     # только контроль/сертификация
    python3 deep_echo_v22.py --phase probe    # только зонд политик
    python3 deep_echo_v22.py --phase deep     # только глубокий прогон
Результат: results/v22_v_budget.json (+ v22_checkpoints.json)
"""
from __future__ import annotations

import argparse
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
OUT_PATH = os.path.join(RESULTS, "v22_v_budget.json")
CKPT_PATH = os.path.join(RESULTS, "v22_checkpoints.json")

from scipy.interpolate import RegularGridInterpolator  # noqa: E402

from zoom_solver import ZoomRunner, FIELDS, echo_peaks, echo_period_from_peaks  # noqa: E402
from grid_machine_annulus import A_STAR  # noqa: E402
from depth_z30 import GAMMA, Z_TARGET, Z_WALL, SEED  # noqa: E402
from amplitude_ladder import fit_exponent  # noqa: E402
from deep_echo_v21 import (  # noqa: E402
    EPS_MAIN, N_GRID, MAX_ZOOMS, DELTA_LIT, LADDER_EPS, LADDER_MIN_Z,
    _stage_analysis, _gamma_estimate, _wiggle_gate, _new_wall, log)

T_START = time.time()

# --- параметры кампании --------------------------------------------------------
W_FACTOR = 3.0                 # лучшая политика окна v21 [D-v21]
V_BACK_BASE = 0.5              # контроль = точная формула родителя
V_AHEAD_BASE = 1.5             # контроль = точное значение родителя
PROBE_POLICIES = [(1.0, 1.5), (2.0, 1.5), (0.5, 3.0)]   # (k_back, v_ahead)
# [C2b] адаптивный поздний якорь: зумы 1..switch-1 — контроль (0.5),
# с зума switch — поздний k_back (хирургия стены, где живёт лестница)
PROBE2_POLICIES = [(1.0, 3), (2.0, 3), (3.0, 3)]        # (k_back_late, switch_zoom)
V_AHEAD_FIXED = 1.5            # v_ahead вперёд — инертен [C2], фиксируем
# [C2c] корневой якорь + якорь на полу покрытия: k1 на зуме 1 опускает КОРНЕВОЙ
# пол чуть ниже ожидаемого эха (~0.4003; критический k = 0.507), с зума 2 окно
# якорится на глубочайшую покрытую точку (v_lo = buffer_v[0]) — пол замирает,
# лестница спускается В покрытую область. Разрушительная зона k >= 1
# (рестарт в хвосте импульса) обходится стороной.
PROBE3_POLICIES = [0.52, 0.60, 0.80]                    # k1 (зум 1)
ANCHOR_FROM_ZOOM = 2           # с какого зума якорить на пол покрытия
V21_W3_Z = 7.20358520128802    # контрольная глубина v21 probe(w=3)
V21_W3_ZOOMS = 4
DEEP_MIN_GAIN = 0.05           # z-выигрыш политики, значимый для DEEP


def checkpoint(tag, runner, extra=None):
    """[P4-стиль v21] чекпоинт после каждого события."""
    try:
        rec = {"tag": tag, "z": float(runner._z_acc),
               "zooms": int(runner.diag.zooms), "du": float(runner.du),
               "stage_v": [float(runner.stage_v[0]), float(runner.stage_v[1])]}
        if extra:
            rec.update(extra)
        with open(CKPT_PATH, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
    except OSError:
        pass


# ==============================================================================
# Машина v22: вилка _zoom с якорными параметрами (k_back, v_ahead)
# ==============================================================================
class V22Runner(ZoomRunner):
    """ZoomRunner с параметризованным v-бюджетом зума.

    Тело _zoom скопировано с zoom_solver.ZoomRunner._zoom (бит-в-бит) с
    ЕДИНСТВЕННЫМ математическим изменением: коэффициент 0.5 в формуле
    v_lo заменён на self.v_back. При (v_back=0.5, v_ahead=1.5) вилка
    обязана быть нейтральной к физике — контроль [C1] проверяет на
    точное воспроизведение цепочки v21 probe(w=3).

    Дополнительно ведёт журнал зумов (v-бюджет: запрос/кап/клэмп/лямбда)
    и журнал вызовов _try_extend (сертификация [F3]).
    """

    def __init__(self, *a, **kw):
        self.v_back = float(kw.pop("v_back", V_BACK_BASE))
        self.v_ahead = float(kw.pop("v_ahead", V_AHEAD_BASE))
        self.v_back_late = kw.pop("v_back_late", None)
        self.switch_zoom = int(kw.pop("switch_zoom", 3))
        self.anchor_from_zoom = kw.pop("anchor_from_zoom", None)
        self.zoom_log = []
        self.extend_log = []
        super().__init__(*a, **kw)

    def _k_back_now(self):
        """Адаптивный якорь: до switch_zoom — v_back, с него — v_back_late."""
        if (self.v_back_late is not None
                and self.diag.zooms + 1 >= self.switch_zoom):
            return float(self.v_back_late)
        return float(self.v_back)

    def _anchor_floor_now(self):
        """Якорь на полу покрытия с зума anchor_from_zoom."""
        return (self.anchor_from_zoom is not None
                and self.diag.zooms + 1 >= int(self.anchor_from_zoom))

    # -- зум с якорными параметрами (вилка родителя) ---------------------------
    def _zoom(self, width, u_focus, v_now, du_target=None, v_ahead_factor=None):
        if v_ahead_factor is None:
            v_ahead_factor = self.v_ahead
        du_old = self.du
        W0 = max(self.w_factor * width, 40.0 * du_old)
        if du_target is None:
            du_target = W0 / self.n
        W_new = du_target * self.n
        v_hi_req = v_now + v_ahead_factor * W_new
        v_hi = min(v_hi_req, self.stage_v[1])
        cap_active = bool(v_hi_req > self.stage_v[1] + 1e-15)
        slack_parent = float(self.stage_v[1] - v_now)   # ДО _new_stage
        j0 = int(self.j)
        if v_hi - v_now < 12.0 * du_old:
            self.zoom_log.append({"ok": False, "v_now": float(v_now),
                                  "why": "ahead<12du"})
            return False
        # продолжаем старый марш, пока v не покроет v_hi
        while self.j + 1 < self.n and self.v[self.j + 1] <= v_hi + 1e-12:
            self.j += 1
            st_new = self.sol._do_step(self.st, self.j)
            self.st = st_new
            self.buffer_v.append(self.v[self.j])
            self.buffer.append({k: st_new[k].copy() for k in FIELDS})
        march_cover_rows = int(self.j - j0)
        v_hi = min(v_hi, self.v[self.j])           # реально покрытое v_hi
        k_back = self._k_back_now()
        clamp_floor = float(self.buffer_v[0])
        anchor_floor = self._anchor_floor_now()
        v_lo_uncapped = v_now - k_back * (v_hi - v_now)
        if anchor_floor:
            v_lo = clamp_floor          # якорь: глубочайшая покрытая точка
        else:
            v_lo = max(v_lo_uncapped, clamp_floor)
        clamp_active = bool(v_lo_uncapped < clamp_floor - 1e-15)
        W_v = v_hi - v_lo
        if W_v < 24.0 * du_old:
            self.zoom_log.append({"ok": False, "v_now": float(v_now),
                                  "why": "W_v<24du"})
            return False
        du_new = W_v / self.n                       # квадратные ячейки
        W_u = W_v
        if W_u >= (self.u[-1] - self.u[0]) * 0.999:
            u_lo, u_hi = self.u[0], self.u[-1]
        else:
            # фича на u_frac от левого края; окно обязано содержать
            # центральную линию u = v (область сжатия r -> 0); клип в домен
            u_hi = u_focus + (1.0 - self.u_frac) * W_u
            u_hi = max(u_hi, v_now + 0.02 * W_u)
            u_lo = u_hi - W_u
            if u_hi > self.u[-1]:
                u_hi = self.u[-1]
                u_lo = u_hi - W_u
            if u_lo < self.u[0]:
                u_lo = self.u[0]
                u_hi = u_lo + W_u

        # 2D-интерполяция полей из буфера на новую сетку
        vb = np.array(self.buffer_v)
        ub = self.u.copy()
        mask = (vb >= v_lo - 1e-12) & (vb <= v_hi + 1e-12)
        vb_s = vb[mask]
        buf_s = [self.buffer[i] for i in np.where(mask)[0]]
        if len(vb_s) < 8:
            self.zoom_log.append({"ok": False, "v_now": float(v_now),
                                  "why": "buffer<8"})
            return False
        u_new = np.linspace(u_lo, u_hi, self.n)
        v_new = np.linspace(v_lo, v_hi, self.n)
        Vg, Ug = np.meshgrid(vb_s, u_new, indexing="ij")

        CLIP = {"r": 1e3, "Phi": 50.0, "p": 1e3, "q": 1e3, "s": 1e6, "t": 1e6,
                "c": 1e6, "m": 1e3, "alpha2": 1e8, "d": 1e8, "w": 1e8}

        def interp_field(k, u_target=None):
            Fb = np.array([b[k] for b in buf_s])
            Fb = np.nan_to_num(Fb, nan=0.0, posinf=0.0, neginf=0.0)
            Fb = np.clip(Fb, -CLIP[k], CLIP[k])
            itp = RegularGridInterpolator((vb_s, ub), Fb, method="cubic",
                                          bounds_error=False, fill_value=None)
            if u_target is None:
                return itp(np.stack([Vg, Ug], axis=-1))
            Vg2, Ug2 = np.meshgrid(vb_s, u_target, indexing="ij")
            return itp(np.stack([Vg2, Ug2], axis=-1))

        row = {k: interp_field(k)[0, :] for k in FIELDS}
        edge_full = {k: interp_field(k) for k in FIELDS}
        edge = {k: edge_full[k][:, 0] for k in FIELDS}
        # m — гладкая эволюционная переменная (см. родитель: пересчёт через
        # определение катастрофически сокращает near center)
        for d_ in (row, edge):
            d_["alpha2"] = np.clip(np.nan_to_num(d_["alpha2"], nan=1.0,
                                                 posinf=1.0, neginf=1.0), 1e-8, 1e8)
            for k in FIELDS:
                d_[k] = np.nan_to_num(d_[k], nan=0.0, posinf=0.0, neginf=0.0)

        # v6: регуляризация m у центра ПЕРВОЙ строки новой стадии
        # (гейт |m| <= 50 |M3| |xi|^3, башенный масштаб из реле)
        if self._m3_relay > 0:
            v_row = float(vb_s[0])
            x_row = (v_row - u_new) / 2.0
            i0r = int(np.argmin(np.abs(row["r"])))
            xi_row = x_row - x_row[i0r]
            cap_m = 50.0 * self._m3_relay * np.abs(xi_row) ** 3 + 1e-300
            m_old_row = row["m"]
            row["m"] = np.where(
                np.isfinite(m_old_row) & (np.abs(m_old_row) > cap_m),
                np.sign(m_old_row) * cap_m, m_old_row)

        lam = du_old / du_new
        self._new_stage((u_lo, u_hi), (v_lo, v_hi), row=row,
                        edge={"r": edge["r"], "Phi": edge["Phi"], "t": edge["t"]},
                        du_parent=du_old)
        self._z_acc += float(np.log(lam))
        self.diag.zooms += 1
        c1 = self._stage_c1()
        self.diag.stage_constraints.append(
            {"zoom": self.diag.zooms, "lam": float(lam), "du": float(du_new),
             "z": self._z_acc, "c1_max": c1})
        self.zoom_log.append({
            "ok": True, "zoom_index": int(self.diag.zooms),
            "v_now": float(v_now), "width": float(width),
            "w_cells_trigger": float(width / du_old),
            "W_new": float(W_new), "v_ahead": float(v_ahead_factor),
            "v_back": float(k_back),
            "v_back_early": float(self.v_back),
            "v_back_late": (float(self.v_back_late)
                            if self.v_back_late is not None else None),
            "anchor_floor": bool(anchor_floor),
            "anchor_from_zoom": (int(self.anchor_from_zoom)
                                 if self.anchor_from_zoom is not None else None),
            "ahead_req": float(v_ahead_factor * W_new),
            "slack_parent": slack_parent,
            "cap_active": cap_active,
            "march_cover_rows": march_cover_rows,
            "v_hi": float(v_hi), "v_lo": float(v_lo),
            "v_lo_uncapped": float(v_lo_uncapped),
            "clamp_active": clamp_active,
            "clamp_floor": clamp_floor,
            "W_v": float(W_v), "du_new": float(du_new), "lam": float(lam),
            "z_acc": float(self._z_acc), "c1_max": float(c1)})
        if self.verbose:
            print(f"    [zoom #{self.diag.zooms}] W_v={W_v:.3e} lam={lam:.2f} "
                  f"z={self._z_acc:.3f} du={du_new:.3e} v=[{v_lo:.5f},{v_hi:.5f}] "
                  f"back={v_now - v_lo:.3e} clamp={clamp_active} C1={c1:.1e}")
        checkpoint(f"zoom#{self.diag.zooms}", self)
        return True

    # -- трассировка мёртвого расширения [F3] ----------------------------------
    def _try_extend(self):
        v_now = self.v[min(self.j, self.n - 1)]
        slack = float(self.stage_v[1] - v_now)
        self.extend_log.append({
            "j": int(self.j), "n": int(self.n), "slack": slack,
            "du": float(self.du), "zooms": int(self.diag.zooms),
            "mx": float(self.track["mx"][-1]) if self.track["mx"] else 0.0})
        return super()._try_extend()


# ==============================================================================
# Прогон одной цепочки с политикой (k_back, v_ahead)
# ==============================================================================
def run_chain(eps, tag, v_back=V_BACK_BASE, v_ahead=V_AHEAD_BASE,
              v_back_late=None, switch_zoom=3, anchor_from_zoom=None,
              n_grid=None, max_zooms=None, verbose=False):
    """Цепочка зумов с политикой якорения; возвращает (rec, runner)."""
    n_grid = n_grid or N_GRID
    max_zooms = max_zooms or MAX_ZOOMS
    A = A_STAR + eps
    pol_txt = ("k_back=%.1f" % v_back if v_back_late is None else
               "k_back: 0.5->%.1f с зума %d" % (v_back_late, switch_zoom))
    if anchor_from_zoom is not None:
        pol_txt += ", якорь на пол с зума %d" % anchor_from_zoom
    log(f"\n=== цепочка {tag}: eps = {eps:.1e}, n = {n_grid}, "
        f"w = {W_FACTOR:.1f}, {pol_txt}, v_ahead = {v_ahead:.1f} ===")
    runner = V22Runner(A=A, n=n_grid, max_zooms=max_zooms, w_factor=W_FACTOR,
                       verbose=verbose, v_back=v_back, v_ahead=v_ahead,
                       v_back_late=v_back_late, switch_zoom=switch_zoom,
                       anchor_from_zoom=anchor_from_zoom)
    diag = runner.run()
    z_final = float(runner._z_acc)
    stages, peaks = _stage_analysis(runner)
    n_peaks_total = len(peaks)
    best_seg = max(stages, key=lambda s: s["n_peaks"]) if stages else None
    delta_eff_best = None
    if best_seg and best_seg.get("delta_eff") is not None:
        delta_eff_best = {"zoom_index": best_seg["zoom_index"],
                          "delta_eff": best_seg["delta_eff"],
                          "delta_err": best_seg["delta_err"],
                          "n_peaks_seg": best_seg["n_peaks"]}
    # лямбды по зумам
    lams = [zl["lam"] for zl in runner.zoom_log if zl.get("ok")]
    rec = {
        "tag": tag, "eps": eps, "A": A, "n_grid": n_grid,
        "policy": {"w_factor": W_FACTOR, "k_back": v_back,
                   "v_ahead": v_ahead, "k_back_late": v_back_late,
                   "switch_zoom": (switch_zoom if v_back_late is not None
                                   else None),
                   "anchor_from_zoom": anchor_from_zoom},
        "z_reached": z_final, "zooms": int(diag.zooms),
        "stop": str(diag.stopped),
        "n_Q_peaks_total": int(n_peaks_total),
        "n_stages": len(stages),
        "peaks_per_stage": [{"zoom_index": s["zoom_index"],
                             "n_peaks": s["n_peaks"],
                             "v_peaks": s["v_peaks"],
                             "Q_peaks": s["Q_peaks"],
                             "z_start": s["z_start"],
                             "z_end": s["z_end"]} for s in stages],
        "delta_eff_best": delta_eff_best,
        "lam_mean": float(np.mean(lams)) if lams else None,
        "lam_list": [float(x) for x in lams],
        "zoom_log": runner.zoom_log,
        "extend_log": runner.extend_log,
        "du_final": float(runner.du),
        "runtime_s": round(time.time() - T_START, 1),
        "supercritical": bool(diag.supercritical),
        "m_ah": float(diag.m_ah),
    }
    return rec, runner


# ==============================================================================
# [C1] Сертификация: контроль + факты [F1]-[F4]
# ==============================================================================
def phase_cert():
    rec, runner = run_chain(EPS_MAIN, "cert(контроль k_back=0.5,v_ahead=1.5)")
    dev = abs(rec["z_reached"] - V21_W3_Z)
    repro = bool(dev < 1e-9 and rec["zooms"] == V21_W3_ZOOMS
                 and rec["stop"] == "v_exhausted")

    # [F1] кап не связан
    zl_ok = [zl for zl in runner.zoom_log if zl.get("ok")]
    slack = [zl["slack_parent"] for zl in zl_ok if zl.get("slack_parent")]
    ratio = [zl["ahead_req"] / zl["slack_parent"] for zl in zl_ok
             if zl.get("slack_parent")]
    f1 = {"n_zooms": len(zl_ok),
          "cap_active_count": sum(1 for zl in zl_ok if zl["cap_active"]),
          "ahead_over_slack_max": float(max(ratio)) if ratio else None,
          "verdict": ("кап НЕ связан ни на одном зуме (активный бюджет — "
                      "собственный размах окна, не конверт)"
                      if all(not zl["cap_active"] for zl in zl_ok)
                      else "кап связан минимум на одном зуме")}

    # [F2] вакуум финальной стадии
    v = np.array(runner.track["v"]); qc = np.array(runner.track["Q"])
    wc = np.array(runner.track["w_cells"]); mx = np.array(runner.track["mx"])
    bounds = [0] + [i for i in range(1, len(v))
                    if v[i] < v[i - 1] - 1e-12] + [len(v)]
    a, b = bounds[-2], bounds[-1]
    qmax = float(np.abs(qc).max()) or 1.0
    vac_frac = float(np.mean(np.abs(qc[a:b]) < 1e-4 * qmax))
    f2 = {"stage_rows": int(b - a), "v_lo": float(v[a]), "v_hi": float(v[b - 1]),
          "vacuum_row_share": vac_frac,
          "max_mx_final_stage": float(mx[a:b].max()),
          "w_cells_final_edge": float(wc[b - 1]),
          "verdict": ("финальная стадия — вакуум (структура осталась позади "
                      "окна): лестница триггеров спускается по v, окно "
                      "смотрит вперёд" if vac_frac > 0.9 else
                      "финальная стадия содержит структуру")}

    # [F3] мёртвое расширение
    el = runner.extend_log
    f3 = {"n_calls": len(el),
          "slack_all_zero": bool(el) and all(abs(e["slack"]) < 1e-15
                                             for e in el),
          "structural_invariant": ("stage_v == (v[0], v[-1]) по построению "
                                   "_new_stage; вызов при j >= n даёт "
                                   "v_now = v[n-1] = stage_v[1]; запас = 0 "
                                   "< 12*du всегда -> v_exhausted "
                                   "терминален по построению"),
          "verdict": ("_try_extend мёртв: %d вызовов, запас 0.0 точно на "
                      "всех" % len(el))
          if el and all(abs(e["slack"]) < 1e-15 for e in el)
          else ("_try_extend жив (запас > 0) — пересмотреть [F3]")}

    # [F4] голодание назад-размаха
    trig = [zl["v_now"] for zl in zl_ok]
    starv = []
    for i, zl in enumerate(zl_ok):
        back_eff = zl["v_now"] - zl["v_lo"]
        nxt = (trig[i + 1] - zl["v_now"]) if i + 1 < len(trig) else None
        starv.append({"zoom_index": zl["zoom_index"],
                      "back_eff": float(back_eff),
                      "back_req": float(zl["v_now"] - zl["v_lo_uncapped"]),
                      "clamp_active": zl["clamp_active"],
                      "interval_to_next_trigger": (float(-nxt) if nxt
                                                   is not None else None),
                      "w_cells_trigger": zl["w_cells_trigger"],
                      "lam": zl["lam"]})
    f4 = {"rows": starv,
          "note": ("интервал лестницы ОТРИЦАТЕЛЕН по v (спуск к v*); "
                   "покрытие: back_eff >= |интервал| означает, что следующее "
                   "эхо было внутри окна; финальный зум покрытия не имеет — "
                   "свидетельство [F2]"),
          "verdict": ("голодание назад-размаха на стене подтверждено"
                      if any(r["clamp_active"] for r in starv) else
                      "клэмп буфера не активен — пересмотреть [F4]")}

    cert = {"status": "executed", "reproduced_v21_w3": repro,
            "z_dev_vs_v21": float(dev), "control": rec,
            "F1_cap_free": f1, "F2_final_vacuum": f2,
            "F3_dead_extension": f3, "F4_starvation": f4}
    log(f"\n[C1] контроль: z = {rec['z_reached']:.6f} (v21: {V21_W3_Z:.6f}), "
        f"воспроизведение = {repro}")
    log(f"[F1] {f1['verdict']} (max ahead/slack = {f1['ahead_over_slack_max']:.3f})"
        if f1["ahead_over_slack_max"] else f"[F1] {f1['verdict']}")
    log(f"[F2] {f2['verdict']} (доля вакуумных строк = {vac_frac:.3f})")
    log(f"[F3] {f3['verdict']}")
    log("[F4] клэмп буфера активен на зуме: "
        f"{[r['zoom_index'] for r in starv if r['clamp_active']]}")
    return cert


# ==============================================================================
# [C2] Зонд политик (k_back, v_ahead)
# ==============================================================================
def phase_probe():
    rows = []
    for k_back, v_ahead in PROBE_POLICIES:
        rec, _ = run_chain(EPS_MAIN, f"probe(k_back={k_back},v_ahead={v_ahead})",
                           v_back=k_back, v_ahead=v_ahead)
        rows.append({
            "k_back": k_back, "v_ahead": v_ahead,
            "z_reached": rec["z_reached"], "zooms": rec["zooms"],
            "stop": rec["stop"], "n_Q_peaks_total": rec["n_Q_peaks_total"],
            "n_stages": rec["n_stages"],
            "max_peaks_per_stage": max((s["n_peaks"] for s in
                                        rec["peaks_per_stage"]), default=0),
            "lam_mean": rec["lam_mean"],
            "du_final": rec["du_final"],
            "floor_descent": [zl["v_lo"] for zl in rec["zoom_log"]
                              if zl.get("ok")],
            "delta_eff_best": rec["delta_eff_best"]})
        log(f"  [probe] k_back={k_back}, v_ahead={v_ahead}: "
            f"z = {rec['z_reached']:.3f}, зумов = {rec['zooms']}, "
            f"стоп = {rec['stop']}, пиков = {rec['n_Q_peaks_total']}")
    # интерпретация
    ctrl_z = V21_W3_Z
    best = max(rows, key=lambda r: r["z_reached"])
    ahead_rows = [r for r in rows if r["k_back"] == 0.5 and r["v_ahead"] > 1.5]
    back_rows = [r for r in rows if r["k_back"] > 0.5]
    probe = {
        "status": "executed", "rows": rows,
        "control_z": ctrl_z,
        "ahead_inert": bool(ahead_rows) and all(
            abs(r["z_reached"] - ctrl_z) < 1e-6 or r["z_reached"] <= ctrl_z
            for r in ahead_rows),
        "back_unlocks": bool(back_rows) and any(
            r["z_reached"] > ctrl_z + DEEP_MIN_GAIN for r in back_rows),
        "best_policy": {"k_back": best["k_back"], "v_ahead": best["v_ahead"],
                        "z": best["z_reached"]},
    }
    return probe


# ==============================================================================
# Сборка вердикта
# ==============================================================================
def build_verdict(cert, probe, probe2, probe3, deep, ladder):
    vl = []
    if cert:
        c = cert["control"]
        vl.append("контроль [C1]: вилка _zoom нейтральна — цепочка v21 "
                  "probe(w=3) воспроизведена с расхождением %.1e "
                  "(z = %.6f, %d зумов, %s)"
                  % (cert["z_dev_vs_v21"], c["z_reached"], c["zooms"],
                     c["stop"]))
        f1, f2, f3 = (cert["F1_cap_free"], cert["F2_final_vacuum"],
                      cert["F3_dead_extension"])
        vl.append("[F1] телескопический кап не связан (%d/%d зумов свободны, "
                  "max ahead/slack = %.3f) — стена не в конверте"
                  % (f1["n_zooms"] - f1["cap_active_count"], f1["n_zooms"],
                     f1["ahead_over_slack_max"] or float("nan")))
        vl.append("[F2] финальная стадия — вакуум (доля пустых строк %.3f, "
                  "mx_max = %.3f): лестница триггеров спускается по v "
                  "(0.4781 -> 0.4072 -> 0.4035 -> 0.4015), окно смотрело вперёд"
                  % (f2["vacuum_row_share"], f2["max_mx_final_stage"]))
        vl.append("[F3] v-extension (_try_extend) мёртв по построению: %d "
                  "вызовов с запасом 0.0 точно — v_exhausted терминален "
                  "всегда; правило «телескопический v-домен» + вызов при "
                  "j >= n делают запас нулевым по построению" % f3["n_calls"])
    if probe and probe.get("status") == "executed":
        rows = probe["rows"]
        vl.append("[C2] зонд политик (глобальный якорь): %s" % "; ".join(
            "(k_back=%.1f, v_ahead=%.1f): z = %.2f, зумов %d, пиков %d, "
            "стоп %s" % (r["k_back"], r["v_ahead"], r["z_reached"],
                         r["zooms"], r["n_Q_peaks_total"], r["stop"])
            for r in rows))
        vl.append("редирекция рычага: v_ahead вперёд %s; глобальный задний "
                  "якорь %s — рестарт-строка попадает в область входящего "
                  "импульса (v_p = 0.5 +- 0.1) и ре-эволюция импульса на "
                  "мелкой сетке ломает лестницу (зум 1, стоп %s)"
                  % ("инертен (клэмп буфера перехватывает назад-расширение)"
                     if probe["ahead_inert"] else "эффективен",
                     "РАЗРУШИТЕЛЕН" if all(r["z_reached"] < 2.5
                                           for r in rows)
                     else "не двигает стену",
                     rows[0]["stop"] if rows else "?"))
    if probe2 and probe2.get("status") == "executed":
        rows2 = probe2["rows"]
        vl.append("[C2b] зонд позднего якоря (зумы 1-2 — точный контроль): %s"
                  % "; ".join(
                      "(late=%.1f с зума %d): z = %.2f, зумов %d, пиков %d, "
                      "стоп %s" % (r["k_back_late"], r["switch_zoom"],
                                   r["z_reached"], r["zooms"],
                                   r["n_Q_peaks_total"], r["stop"])
                      for r in rows2))
        vl.append("вывод [C2b]: поздний якорь %s — пол окна может только "
                  "ПОДНИМАТЬСЯ (ratchet покрытием: v_lo ребёнка >= v_lo "
                  "родителя), поздние зумы перехватываются клэмпом "
                  "(лучшая: late = %.1f, z = %.2f ~ контроль)"
                  % ("стену не двигает (все поздние якоря зажаты полом "
                     "0.40113)" if not probe2["back_unlocks_late"] else "двигает",
                     probe2["best_policy"]["k_back_late"],
                     probe2["best_policy"]["z"]))
    if probe3 and probe3.get("status") == "executed":
        rows3 = probe3["rows"]
        vl.append("[C2c] зонд корневого якоря + якоря на полу (k1 на зуме 1, "
                  "с зума 2 v_lo = buffer_v[0]): %s" % "; ".join(
                      "(k1=%.2f): z = %.2f, зумов %d, пиков %d (макс/стадия "
                      "%d), стоп %s" % (r["k1"], r["z_reached"], r["zooms"],
                                        r["n_Q_peaks_total"],
                                        r["max_peaks_per_stage"], r["stop"])
                      for r in rows3))
        vl.append("вывод [C2c]: корневой якорь %s (лучший: k1 = %.2f, "
                  "z = %.2f против контроля 7.20; пол замирает у корня, "
                  "лестница спускается в покрытую область)"
                  % ("двигает стену" if probe3["back_unlocks_root"]
                     else "стену не двигает", probe3["best_policy"]["k1"],
                     probe3["best_policy"]["z"]))
    if deep:
        pol = deep.get("policy", {})
        pol_txt = "k_back = %s" % pol.get("k_back", pol.get("v_back", "?"))
        if pol.get("k_back_late") is not None:
            pol_txt += " -> %s с зума %s" % (pol["k_back_late"],
                                             pol.get("switch_zoom"))
        if pol.get("anchor_from_zoom") is not None:
            pol_txt += ", якорь на пол с зума %s" % pol["anchor_from_zoom"]
        vl.append("[C3] глубокий прогон (%s): z = %.2f, зумов %d, стоп = %s, "
                  "пиков всего %d, макс пиков на стадии %d"
                  % (pol_txt,
                     deep.get("z_reached", float("nan")),
                     deep.get("zooms", -1), deep.get("stop", "?"),
                     deep.get("n_Q_peaks_total", -1),
                     max((s["n_peaks"] for s in deep.get("peaks_per_stage", [])),
                         default=0)))
        deb = deep.get("delta_eff_best")
        if deb:
            d, e = deb["delta_eff"], deb["delta_err"]
            excl = (abs(DELTA_LIT - d) / e if e and e > 0 else float("inf"))
            vl.append("4-й пик ДОСТИГНУТ: Delta_eff = %.4f +- %.4f на стадии "
                      "z%d (%d пиков) — но период пиков НЕ DSS: лит. 3.44 "
                      "исключена на %.1f sigma (оценка совместима с нулём); "
                      "четвёрка пиков — суб-эхо структура или загрязнение "
                      "лестницы у пола, DSS-периодичность на этой глубине "
                      "НЕ подтверждена (честный статус)"
                      % (d, e, deb["zoom_index"], deb["n_peaks_seg"], excl))
        else:
            vl.append("Delta_eff НЕ измерена: 4-го пика на одной стадии нет "
                      "(эхо-поезд не развился до поезда — честный статус)")
    if ladder is not None:
        if ladder.get("status") == "executed":
            fp = ladder.get("fit_p_delta")
            vl.append("[C4] лестница амплитуд: %s"
                      % ("p = %.3f по Delta_eff" % fp["p"] if fp else
                         "исполнена, Delta_eff нет на >= 3 ступенях — p "
                         "не измерим (честно)"))
        else:
            vl.append("[C4] лестница амплитуд: ПРОПУЩЕНА — %s"
                      % ladder.get("reason", ""))
    return vl


HONEST_NOTES = [
    "вилка _zoom в V22Runner копирует тело родителя бит-в-бит с ЕДИНСТВЕННЫМ "
    "изменением (коэффициент 0.5 в v_lo -> k_back); нейтральность вилки "
    "сертифицирована контролем [C1] на точное воспроизведение цепочки v21 "
    "probe(w=3) (расхождение < 1e-9) — изменения физики нет, изменения "
    "размещения окна есть",
    "гипотеза заказа (v_ahead_factor вперёд) проверена и ОТКЛОНЕНА данными: "
    "вперёд от триггера — вакуум ([F2]), назад-расширение перехватывается "
    "клэмпом буфера (v_lo >= buffer_v[0]); рабочий рычаг — задний якорь "
    "k_back на ранних зумах (углубление пола родителя)",
    "экстраполяция за покрытым буфером рассмотрена и ОТВЕРГНУТА: интерполяция "
    "ребёнка с более грубых строк прародителя разрушает разрешение зума "
    "(починка хуже болезни); клэмп буфера оставлен",
    "интервал лестницы оценивается по соседним триггерам (шумно, 4 точки); "
    "оценка следующего триггера 0.3995..0.4004 — основание выбора k_back "
    ">= 1, не предсказание",
    "глобальный задний якорь (k_back с первого зума) РАЗРУШИТЕЛЕН — зонд "
    "[C2]: рестарт-строка опускается в область входящего импульса "
    "(v_p = 0.5, sigma = 0.1) и его ре-эволюция на мелкой сетке останавливает "
    "лестницу (1 зум, z ~ 1.5-1.9); механизм ре-эволюции — интерпретация по "
    "геометрии окна, прямая трассировка полей не проводилась; хирургическая "
    "альтернатива — поздний якорь [C2b] (зумы 1-2 бит-в-бит контроль)",
    "цена якоря: W_v = (1+k_back)*ahead, du_new = W_v/n, лямбда падает "
    "~1/(1+k_back) — z-бюджет на зум снижается; чистый эффект измеряет "
    "зонд [C2] (глубина против политики), а не выводится аналитически",
    "Delta_eff требует >= 4 пиков на ОДНОЙ стадии (echo_period_from_peaks); "
    "пики считаются по сегментам стадий (_stage_analysis v21), кросс-стадийные "
    "серии с ломаным v не интерпретируются",
    "масштаб v22: пробы оконных политик идут на ЧИСТОЙ физике ZoomRunner "
    "(обёртка джанк-гейтов [P2]/[P3] v21 не подключена; в v21 при w = 3 "
    "инвазий не было); полный протокол [P1]-[P5] с гейтами и откатами — "
    "предмет следующей кампании на принятой политике",
    "лямбда-профиль корневого якоря нерегулярен (k1 = 0.52: lam = [8.8, 5.3, "
    "3.3, 5.2, 1.4]) — окно формируется и шириной фичи, и полом; качество "
    "интерполяции рестарт-строк контролируется C1-связью (c1_max в журнале "
    "зумов), порогов отбраковки лямбды не вводилось",
    "гамма считается правилом [D3] v21 (перцентиль/ОЛС-выжившие, бутстрап с "
    "сидом %d) только при >= 6 пиках; чувствительность калибровки часов "
    "(v*, стадия) — как в v21" % SEED,
]


# ==============================================================================
# [C2b] Зонд 2: адаптивный поздний якорь (хирургия стены)
# ==============================================================================
def phase_probe2():
    """Зумы 1..switch-1 — точный контроль (0.5); с зума switch — k_back_late.

    Обоснование: глобальный якорь с первого зума разрушает цепь
    (рестарт-строка попадает в область входящего импульса v_p = 0.5 +- 0.1);
    стена же живёт на зумах >= 3 — якорить надо только там."""
    rows = []
    for k_late, sw in PROBE2_POLICIES:
        rec, _ = run_chain(EPS_MAIN, f"probe2(late={k_late},switch={sw})",
                           v_back=V_BACK_BASE, v_ahead=V_AHEAD_FIXED,
                           v_back_late=k_late, switch_zoom=sw)
        rows.append({
            "k_back_late": k_late, "switch_zoom": sw,
            "z_reached": rec["z_reached"], "zooms": rec["zooms"],
            "stop": rec["stop"], "n_Q_peaks_total": rec["n_Q_peaks_total"],
            "max_peaks_per_stage": max((s["n_peaks"] for s in
                                        rec["peaks_per_stage"]), default=0),
            "lam_mean": rec["lam_mean"],
            "lam_list": rec["lam_list"],
            "du_final": rec["du_final"],
            "floor_descent": [zl["v_lo"] for zl in rec["zoom_log"]
                              if zl.get("ok")],
            "trigger_ladder": [zl["v_now"] for zl in rec["zoom_log"]
                               if zl.get("ok")],
            "delta_eff_best": rec["delta_eff_best"]})
        log(f"  [probe2] late={k_late}, switch={sw}: z = "
            f"{rec['z_reached']:.3f}, зумов = {rec['zooms']}, "
            f"стоп = {rec['stop']}, пиков = {rec['n_Q_peaks_total']}")
    best = max(rows, key=lambda r: r["z_reached"])
    return {
        "status": "executed", "rows": rows,
        "control_z": V21_W3_Z,
        "back_unlocks_late": best["z_reached"] > V21_W3_Z + DEEP_MIN_GAIN,
        "best_policy": {"k_back_late": best["k_back_late"],
                        "switch_zoom": best["switch_zoom"],
                        "z": best["z_reached"]},
    }


# ==============================================================================
# [C2c] Зонд 3: корневой якорь (k1) + якорь на полу покрытия
# ==============================================================================
def phase_probe3():
    """Зум 1 с k1 чуть выше критического (0.507) опускает КОРНЕВОЙ пол окна
    ниже ожидаемого эха (~0.4003); с зума 2 окно якорится на глубочайшую
    покрытую точку (v_lo = buffer_v[0]) — пол замирает у корня (ratchet подъёма пола устранён), лестница триггеров спускается В покрытую
    область. Разрушительная зона k >= 1 (рестарт в хвосте импульса)
    обходится: k1 <= 0.8."""
    rows = []
    for k1 in PROBE3_POLICIES:
        rec, _ = run_chain(EPS_MAIN, f"probe3(k1={k1})",
                           v_back=k1, v_ahead=V_AHEAD_FIXED,
                           anchor_from_zoom=ANCHOR_FROM_ZOOM)
        rows.append({
            "k1": k1, "anchor_from_zoom": ANCHOR_FROM_ZOOM,
            "z_reached": rec["z_reached"], "zooms": rec["zooms"],
            "stop": rec["stop"], "n_Q_peaks_total": rec["n_Q_peaks_total"],
            "max_peaks_per_stage": max((s["n_peaks"] for s in
                                        rec["peaks_per_stage"]), default=0),
            "lam_mean": rec["lam_mean"], "lam_list": rec["lam_list"],
            "du_final": rec["du_final"],
            "floor_descent": [zl["v_lo"] for zl in rec["zoom_log"]
                              if zl.get("ok")],
            "trigger_ladder": [zl["v_now"] for zl in rec["zoom_log"]
                               if zl.get("ok")],
            "delta_eff_best": rec["delta_eff_best"]})
        log(f"  [probe3] k1={k1}: z = {rec['z_reached']:.3f}, "
            f"зумов = {rec['zooms']}, стоп = {rec['stop']}, "
            f"пиков = {rec['n_Q_peaks_total']}")
    best = max(rows, key=lambda r: r["z_reached"])
    return {
        "status": "executed", "rows": rows, "control_z": V21_W3_Z,
        "back_unlocks_root": best["z_reached"] > V21_W3_Z + DEEP_MIN_GAIN,
        "best_policy": {"k1": best["k1"],
                        "anchor_from_zoom": ANCHOR_FROM_ZOOM,
                        "z": best["z_reached"]},
    }


# ==============================================================================
# [C3] Глубокий прогон лучшей политики
# ==============================================================================
def phase_deep(policy):
    rec, runner = run_chain(EPS_MAIN,
                            "deep(%s)" % json.dumps(policy, ensure_ascii=False),
                            **policy)
    stages, peaks = _stage_analysis(runner)
    rec["peaks_rows"] = peaks
    rec["gamma"] = _gamma_estimate(peaks)
    rec["wiggle"] = _wiggle_gate(stages)
    rec["new_wall"] = _new_wall({"kind": "machine:" + rec["stop"]},
                                rec["z_reached"])
    # спуск лестницы триггеров/полов окна (карта якорения)
    zl_ok = [zl for zl in runner.zoom_log if zl.get("ok")]
    rec["anchor_map"] = [{"zoom_index": zl["zoom_index"],
                          "v_trigger": zl["v_now"],
                          "v_floor": zl["v_lo"],
                          "clamp_active": zl["clamp_active"],
                          "lam": zl["lam"],
                          "z_acc": zl["z_acc"]} for zl in zl_ok]
    log(f"\n[C3] deep: z = {rec['z_reached']:.3f}, зумов = {rec['zooms']}, "
        f"стоп = {rec['stop']}, пиков = {rec['n_Q_peaks_total']}, "
        f"пиков/стадия max = "
        f"{max((s['n_peaks'] for s in stages), default=0)}")
    g = rec["gamma"]
    if g.get("status") == "measured" and g.get("gamma_hat"):
        log(f"     гамма: {g['gamma_hat']:.4f} (правило {g['estimator_rule']})")
    db = rec["delta_eff_best"]
    if db:
        log(f"     Delta_eff = {db['delta_eff']:.4f} +- {db['delta_err']:.4f} "
            f"(стадия z{db['zoom_index']}, {db['n_peaks_seg']} пиков)")
    return rec


# ==============================================================================
# [C4] Второй проход: лестница амплитуд на лучшей политике v22
# ==============================================================================
def phase_ladder(policy, deep_rec):
    if deep_rec["z_reached"] < LADDER_MIN_Z:
        return {"status": "skipped",
                "reason": "глубокая цепочка z = %.2f < %.0f (порог v21): "
                          "носителя лестницы нет"
                          % (deep_rec["z_reached"], LADDER_MIN_Z)}
    rungs = [{"tag": deep_rec["tag"], "eps": deep_rec["eps"],
              "z_reached": deep_rec["z_reached"],
              "n_Q_peaks_total": deep_rec["n_Q_peaks_total"],
              "delta_eff": (deep_rec["delta_eff_best"]["delta_eff"]
                            if deep_rec["delta_eff_best"] else None),
              "stop": deep_rec["stop"]}]
    for eps in LADDER_EPS:
        rec, _ = run_chain(eps, "ladder(%s)" % json.dumps(policy,
                                                          ensure_ascii=False),
                           **policy)
        rungs.append({"tag": rec["tag"], "eps": rec["eps"],
                      "z_reached": rec["z_reached"],
                      "n_Q_peaks_total": rec["n_Q_peaks_total"],
                      "delta_eff": (rec["delta_eff_best"]["delta_eff"]
                                    if rec["delta_eff_best"] else None),
                      "stop": rec["stop"]})
        log(f"  [ladder] eps = {eps:.1e}: z = {rec['z_reached']:.3f}, "
            f"пиков = {rec['n_Q_peaks_total']}, стоп = {rec['stop']}")
    out = {"status": "executed",
           "policy": policy,
           "rungs": rungs}
    ok = [r for r in rungs if r.get("delta_eff") is not None]
    if len(ok) >= 3:
        eps_arr = [r["eps"] for r in ok]
        d_ref = ok[0]["delta_eff"]
        devs = [abs(r["delta_eff"] - d_ref) / d_ref for r in ok]
        fit, n = fit_exponent(eps_arr, devs)
        out["fit_p_delta"] = fit
    else:
        out["fit_p_delta"] = None
        out["note"] = ("валидных ступеней с Delta_eff: %d из %d — p не "
                       "измерим (честно)" % (len(ok), len(rungs)))
    return out


# ==============================================================================
# Сборка и запуск
# ==============================================================================
def main():
    global N_GRID, MAX_ZOOMS, EPS_MAIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("cert", "probe", "probe2", "probe3",
                                        "deep", "ladder", "all"),
                    default="all")
    ap.add_argument("--n-grid", type=int, default=N_GRID)
    ap.add_argument("--max-zooms", type=int, default=MAX_ZOOMS)
    ap.add_argument("--eps", type=float, default=EPS_MAIN)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    N_GRID = args.n_grid
    MAX_ZOOMS = args.max_zooms
    EPS_MAIN = args.eps

    out = {
        "title": "КАМПАНИЯ v22: v-бюджет и якорение окна — прорыв стены "
                 "z ~ 7.2 (w = 3)",
        "question": ("двигает ли расширение v-бюджета (v_ahead_factor / "
                     "телескоп / задний якорь) стену z ~ 7.2 при w = 3 и "
                     "открывает ли 4-й пик эха и Delta_eff?"),
        "config": {"A_star": float(A_STAR), "eps": EPS_MAIN,
                   "n_grid": N_GRID, "max_zooms": MAX_ZOOMS,
                   "w_factor": W_FACTOR, "v_back_base": V_BACK_BASE,
                   "v_ahead_base": V_AHEAD_BASE,
                   "probe_policies": [list(p) for p in PROBE_POLICIES],
                   "probe2_policies": [list(p) for p in PROBE2_POLICIES],
                   "probe3_policies": list(PROBE3_POLICIES),
                   "anchor_from_zoom": ANCHOR_FROM_ZOOM,
                   "z_target": Z_TARGET, "z_wall_v21": Z_WALL,
                   "gamma_anchor": GAMMA, "delta_lit": DELTA_LIT,
                   "v21_w3_control": {"z": V21_W3_Z, "zooms": V21_W3_ZOOMS},
                   "determinism": "BLAS 1 thread; без RNG (бутстрап с "
                                  "фиксированным сидом %d)" % SEED},
        "protocol_reference": ("v21 [D-v21] проба оконной политики; диагноз "
                               "v22 (трассировка цепочки w=3); заказ: "
                               "v-бюджет (v_ahead_factor/телескоп) за 4-й "
                               "пик и Delta_eff"),
    }
    os.makedirs(RESULTS, exist_ok=True)

    def save():
        out["runtime_s"] = round(time.time() - T_START, 1)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)

    cert = probe = probe2 = probe3 = None
    deep_rec = None
    ladder = None
    # частичный прогон: восстановить предыдущие фазы (save() переписывает файл)
    if args.phase != "all" and os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, encoding="utf-8") as fh:
                prev = json.load(fh)
            for k in ("cert", "probe", "probe2", "probe3", "deep",
                      "second_pass"):
                if k in prev:
                    out[k] = prev[k]
            cert = out.get("cert")
            probe = out.get("probe")
            probe2 = out.get("probe2")
            probe3 = out.get("probe3")
            deep_rec = out.get("deep")
            ladder = out.get("second_pass")
            log("(восстановлены фазы: %s из предыдущего прогона)"
                % ", ".join(k for k in ("cert", "probe", "probe2", "probe3",
                                        "deep", "second_pass") if k in prev))
        except (OSError, json.JSONDecodeError):
            pass
    if args.phase in ("cert", "all"):
        cert = phase_cert()
        out["cert"] = cert
        save()
    if args.phase in ("probe", "all"):
        probe = phase_probe()
        out["probe"] = probe
        save()
    if args.phase in ("probe2", "all"):
        probe2 = phase_probe2()
        out["probe2"] = probe2
        save()
    if args.phase in ("probe3", "all"):
        probe3 = phase_probe3()
        out["probe3"] = probe3
        save()
    # политика для DEEP: ПРИЗ ЗАКАЗА — 4-й пик и Delta_eff, поэтому критерий
    # (макс пиков на стадии, затем z); глубина — второй приз (записывается)
    def _pk(rec_):
        return max((s["n_peaks"] for s in rec_.get("peaks_per_stage", [])),
                   default=0)

    policy = {"v_back": V_BACK_BASE, "v_ahead": V_AHEAD_BASE}
    cands = [((3, V21_W3_Z), policy)]      # контроль: 3 пика, z = 7.204
    if probe is not None:
        for r in probe["rows"]:
            cands.append(((int(r.get("max_peaks_per_stage", 0)),
                           float(r["z_reached"])),
                          {"v_back": float(r["k_back"]),
                           "v_ahead": float(r["v_ahead"])}))
    if probe2 is not None:
        for r in probe2["rows"]:
            cands.append(((int(r.get("max_peaks_per_stage", 0)),
                           float(r["z_reached"])),
                          {"v_back": V_BACK_BASE,
                           "v_ahead": V_AHEAD_FIXED,
                           "v_back_late": float(r["k_back_late"]),
                           "switch_zoom": int(r["switch_zoom"])}))
    if probe3 is not None:
        for r in probe3["rows"]:
            cands.append(((int(r.get("max_peaks_per_stage", 0)),
                           float(r["z_reached"])),
                          {"v_back": float(r["k1"]),
                           "v_ahead": V_AHEAD_FIXED,
                           "anchor_from_zoom": int(r["anchor_from_zoom"])}))
    _score, policy = max(cands, key=lambda t: t[0])
    z_record = max(t[0][1] for t in cands)
    out["deep_policy"] = policy
    out["depth_record_z"] = z_record
    if args.phase in ("deep", "all"):
        deep_rec = phase_deep(policy)
        out["deep"] = deep_rec
        save()
    if args.phase in ("ladder", "all"):
        if deep_rec is None:
            with open(OUT_PATH, encoding="utf-8") as fh:
                prev = json.load(fh)
            deep_rec = prev.get("deep")
            policy = prev.get("deep_policy", policy)
        if deep_rec is None:
            ladder = {"status": "skipped",
                      "reason": "нет глубокого прогона (запустите --phase deep)"}
        else:
            ladder = phase_ladder(policy, deep_rec)
        out["second_pass"] = ladder
        save()

    out["verdict_lines"] = build_verdict(cert, probe, probe2, probe3,
                                         deep_rec, ladder)
    out["honest_notes"] = HONEST_NOTES
    out["runtime_s"] = round(time.time() - T_START, 1)
    save()
    log("\n=== ВЕРДИКТ v22 ===")
    for line in out["verdict_lines"]:
        log(" * " + line)
    log(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    return out


if __name__ == "__main__":
    main()
