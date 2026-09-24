#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
МНОГОСТАДИЙНЫЙ РЕГИДДИНГ (ZOOM) ДЛЯ ЗАДАЧИ ЧОПТЮКА — v2 (стабильная цепочка)
MULTI-STAGE REGRIDDING (ZOOM) FOR THE CHOPTUIK PROBLEM — v2 (stable chain)
================================================================================

Адаптивное перерегрирование в стиле Чоптюка (1993): активная структура около
центра сжимается; когда градиентный масштаб L_grad = (max|Phi|/max|s|)/du
падает ниже w_trigger клеток, окно сетки переносится и сжимается так, чтобы
du_new = du_old/lam; поля интерполируются кубически из буфера строк, эволюция
продолжается на новой сетке. Уровень z = sum ln(du_old/du_new) — лог-шкала
масштабов; в ней измеряется период эха ДСС (DSS) delta ~ 0.737.

Ключевые исправления v2 (по результатам отладки v1):
  1. Окно зума размещается с учётом дрейфа структуры (+u): фича помещается на
     35% от левого края окна; окно клипуется в родительский u-домен.
  2. Телескопический v-бюджет: v-домен новой стадии <= v-домена родителя
     (в v1 окно могло выйти за покрытые буфером строки -> экстраполяция).
  3. v-extension: если марш дошёл до правого края v-сетки без триггера,
     выполняется трансляция окна (lam = 1) вперёд по v.
  4. Масса Чёрной дыры фиксируется при ПЕРВОМ устойчивом горизонте
     (>=6 строк подряд с пересечением q=0), а не max по времени.
  5. Полный трекинг DSS-обсерваблов по строкам: v, mx = max 2m/r,
     Q = max 2m/r^2 (кривизна), L_grad, ширина, u_focus, du, z.
  6. Ранний останов после образования горизонта (mx > 1.02) — экономия.

Запуск:  python3 zoom_solver.py            # тест ближнекритического забега
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from solver import (DoubleNullSolver, GaussianPulseData, SolverConfig, KAPPA)

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0

FIELDS = ("r", "Phi", "p", "q", "s", "t", "c", "m", "alpha2", "d", "w")


@dataclass
class ZoomDiag:
    supercritical: bool = False
    m_ah: float = 0.0          # масса ПЕРВОГО устойчивого горизонта (основная)
    m_ah_max: float = 0.0      # max массы горизонта по времени (диагностика)
    r_ah: float = 0.0
    v_ah: float = float("nan")
    zooms: int = 0
    z_final: float = 0.0
    stopped: str = "incomplete"
    runtime: float = 0.0
    stage_constraints: list = field(default_factory=list)  # C1/C2/mdef по стадиям


class ZoomRunner:
    """Многостадийный забег с перерегрированием (v2)."""

    def __init__(self, A: float, n: int = 800, max_zooms: int = 12,
                 w_trigger: float = 45.0, w_factor: float = 5.0,
                 u_frac: float = 0.30, max_2m_over_r: float = 2.0,
                 verbose: bool = False):
        self.A = A
        self.n = n
        self.max_zooms = max_zooms
        self.w_trigger = w_trigger      # триггер: ширина < w_trigger клеток
        self.w_factor = w_factor        # новое окно >= w_factor * width
        self.u_frac = u_frac            # фича на u_frac от левого края окна
        self.max_2m_over_r = max_2m_over_r
        self.verbose = verbose
        self.dbg = None                 # опциональный колбэк диагностики строк
        self.diag = ZoomDiag()
        self._z_acc = 0.0
        # трекинг DSS
        self.track = {"v": [], "mx": [], "Q": [], "L": [], "width": [],
                      "u_focus": [], "du": [], "z": [], "w_cells": []}
        self.m_ah_hist = []             # (v, m_ah) — масса пересечения по строкам
        self._ah_rows = 0               # счётчик строк с устойчивым пересечением
        self._m_ah_frozen = 0.0
        self._new_stage(u_span=(U0, U1), v_span=(V0, V1))

    # ------------------------------------------------------------------
    def _new_stage(self, u_span, v_span, row=None, edge=None, du_parent=None):
        cfg = SolverConfig(n_u=self.n, n_v=self.n, u_range=u_span, v_range=v_span,
                           monitor_every=10 ** 9, max_2m_over_r=self.max_2m_over_r)
        if row is None:
            data = GaussianPulseData(A=self.A, v_p=V_P, sigma=SIGMA,
                                     u0=u_span[0], v0=v_span[0])
            self.sol = DoubleNullSolver(cfg, data)
        else:
            self.sol = DoubleNullSolver.from_fields(
                cfg, np.linspace(*u_span, self.n), np.linspace(*v_span, self.n),
                row, edge["r"], edge["Phi"], edge["t"])
            # --- v3: регулярное замыкание центра на зум-стадиях ------------
            # Связка наклонов s1-t1 = -2a (вместо клэмпа a=0), отброс
            # паразитной 1/r-моды фитом O = a r + C/r, масса m ~ r^3 в зоне.
            # R_heal = 5 du_parent — унаследованная клэмп-зона родителя:
            # зона реконструкции R_zone = max(8 du_new, 1.2 R_heal) покрывает
            # интерполяционный мусор рестарт-строки.
            self.sol.center_closure = "regular"
            self.sol.reg_m_rebuild = True
            self.sol.reg_pq_project = True
            if du_parent is not None:
                self.sol.R_heal = 5.0 * du_parent
        self.u = self.sol.u
        self.v = self.sol.v
        self.du = self.sol.du
        self.dv = self.sol.dv
        self.stage_v = (self.v[0], self.v[-1])   # телескопический v-бюджет
        self.st = {k: getattr(self.sol, k).copy() for k in FIELDS}
        # v2-лечение центра на зум-стадиях отключено: при closure="regular"
        # диспатчер в _do_step и так уходит в v3; строка ниже держит clamp-ветку
        # базовой стадии в v2-поведении (heal только на базовой стадии)
        if row is None:
            self.sol.heal_enabled = True
        else:
            self.sol.heal_enabled = False
        self._du_parent = du_parent if du_parent is not None else self.du
        self.j = 0
        self.wh = []                    # история ширины (клетки) ТЕКУЩЕЙ стадии
        self.buffer_v = [self.v[0]]
        self.buffer = [{k: self.st[k].copy() for k in FIELDS}]

    # ------------------------------------------------------------------
    def _row_diag(self, st):
        """Диагностика строки: mx = max 2m/r, Q = max 2m/r^2, масштабы."""
        r = st["r"]
        phys = r > 2.0 * self.du
        if not phys.any():
            return 0.0, 0.0, 0.0, 0.0
        rr = np.where(phys, r, 1.0)
        tmr = np.where(phys, 2.0 * st["m"] / rr, 0.0)
        mx = float(tmr.max())
        r4 = r > 4.0 * self.du
        Q = float((2.0 * st["m"] / np.where(r4, r**2, 1.0))[r4].max()) if r4.any() else 0.0
        # тонкая структура: |s| = |Phi_u|; маска r > 12 du исключает
        # артефакт клэмпа регулярности (слой 1/r при r ~ 5 du)
        smag = np.abs(st["s"]) * (r > 12.0 * self.du)
        smax = float(smag.max())
        Phi_scale = float(np.max(np.abs(st["Phi"])[r > self.du])) or 1.0
        self.smax_loc = smax
        self.Phi_scale = Phi_scale
        self.L_grad = (Phi_scale / smax) / self.du if smax > 0 else 1e9
        if smax <= 0:
            return mx, Q, 0.0, float(self.u[np.argmax(tmr)])
        im = int(np.argmax(smag))
        thr = 0.15 * smax
        i_lo = im
        while i_lo > 0 and smag[i_lo - 1] > thr:
            i_lo -= 1
        i_hi = im
        while i_hi < len(smag) - 1 and smag[i_hi + 1] > thr:
            i_hi += 1
        width = float(self.u[i_hi] - self.u[i_lo])
        u_focus = float(self.u[im])
        return mx, Q, width, u_focus

    # ------------------------------------------------------------------
    def run(self):
        t0 = time.time()
        diag = self.diag
        stop_reason = None
        with np.errstate(all="ignore"):
            while True:
                self.j += 1
                if self.j >= self.n:
                    # v-сетка стадии исчерпана: пробуем трансляцию окна вперёд
                    if self._try_extend():
                        continue
                    stop_reason = "v_exhausted"
                    break
                st_new = self.sol._do_step(self.st, self.j)
                self.st = st_new
                v_now = self.v[self.j]
                self.buffer_v.append(v_now)
                self.buffer.append({k: st_new[k].copy() for k in FIELDS})
                if len(self.buffer_v) > self.n + 60:
                    self.buffer_v.pop(0)
                    self.buffer.pop(0)

                mx, Q, width, u_focus = self._row_diag(st_new)
                if self.dbg is not None:
                    self.dbg(self, st_new, v_now, mx, Q)
                tr = self.track
                tr["v"].append(v_now); tr["mx"].append(mx); tr["Q"].append(Q)
                tr["L"].append(self.L_grad * self.du)
                tr["width"].append(width)
                tr["u_focus"].append(u_focus)
                tr["du"].append(self.du); tr["z"].append(self._z_acc)
                tr["w_cells"].append(width / self.du)
                w_cells = width / self.du
                self.wh.append(w_cells)
                # условие сжатия ВНУТРИ стадии: ширина меньше, чем 20 строк
                # назад (история стадии сбрасывается после каждого зума).
                # Отсекает артефакт 1/r у центра: его ширина в клетках
                # постоянна (задаётся маской, а не физическим сжатием).
                shrinking = len(self.wh) > 20 and w_cells < 0.85 * self.wh[-20]

                # --- горизонт (разрешённый: r > 8 du) ----------------------
                r_thresh = 8.0 * self.du
                phys = st_new["r"] > r_thresh
                qs = np.where(phys, st_new["q"], 1.0)
                idx = np.where((qs[:-1] > 0) & (qs[1:] <= 0))[0]
                if idx.size:
                    i = idx[-1]
                    q0, q1 = qs[i], qs[i + 1]
                    f = q0 / (q0 - q1) if q0 != q1 else 0.0
                    m_ah = st_new["m"][i] * (1 - f) + st_new["m"][i + 1] * f
                    r_ah = st_new["r"][i] * (1 - f) + st_new["r"][i + 1] * f
                    self.m_ah_hist.append((v_now, m_ah))
                    if m_ah > diag.m_ah_max and np.isfinite(m_ah):
                        diag.m_ah_max = m_ah
                    if m_ah > 0.2 * diag.m_ah_max and np.isfinite(m_ah):
                        self._ah_rows += 1
                    else:
                        self._ah_rows = 0
                    # первый устойчивый горизонт -> замораживаем массу
                    if self._m_ah_frozen == 0.0 and self._ah_rows >= 6:
                        self._m_ah_frozen = m_ah
                        diag.m_ah = m_ah
                        diag.r_ah = r_ah
                        diag.v_ah = v_now
                        diag.supercritical = True
                elif self._m_ah_frozen == 0.0:
                    self._ah_rows = 0

                # --- сингулярность -----------------------------------------
                tmr_res = np.where(phys, 2.0 * st_new["m"] /
                                   np.where(phys, st_new["r"], 1.0), 0.0)
                if not np.isfinite(tmr_res).all() or tmr_res.max() > self.max_2m_over_r:
                    stop_reason = "singularity"
                    break

                # --- ранний останов: горизонт образовался и удерживается ----
                if self._m_ah_frozen > 0.0 and mx > 1.02:
                    stop_reason = "AH formed"
                    break

                # --- триггер зума: ширина < порога И активно сжимается ------
                if (w_cells < self.w_trigger
                        and shrinking
                        and mx < 1.2
                        and width > 0
                        and diag.zooms < self.max_zooms
                        and self._m_ah_frozen == 0.0):
                    ok = self._zoom(width, u_focus, v_now)
                    if ok:
                        continue
                if self.verbose and self.j % 50 == 0:
                    print(f"    j={self.j} v={v_now:.4f} mx={mx:.3f} Q={Q:.2f} "
                          f"L={self.L_grad:.0f} w={w_cells:.0f} "
                          f"u_f={u_focus:+.3f} z={self._z_acc:.2f} du={self.du:.2e}")

        diag.stopped = stop_reason or "completed"
        diag.runtime = time.time() - t0
        diag.z_final = self._z_acc
        for k in FIELDS:
            setattr(self.sol, k, self.st[k])
        self.sol.v_final = self.v[min(self.j, self.n - 1)]
        if self.verbose:
            print(f"    [stop] {diag.stopped}: M={diag.m_ah:.5f} zooms={diag.zooms} "
                  f"z={self._z_acc:.2f} t={diag.runtime:.0f}s")
        return diag

    # ------------------------------------------------------------------
    def _try_extend(self):
        """Трансляция окна вперёд по v (du сохраняется), если есть v-бюджет."""
        if self.diag.zooms >= self.max_zooms + 6:
            return False
        v_now = self.v[min(self.j, self.n - 1)]
        if self.stage_v[1] - v_now < 12 * self.du:
            return False
        mx = self.track["mx"][-1] if self.track["mx"] else 0.0
        if mx > 1.2:
            return False
        u_focus = self.track["u_focus"][-1] if self.track["u_focus"] else 0.0
        return self._zoom(self.w_trigger * self.du, u_focus, v_now,
                          du_target=self.du, v_ahead_factor=0.65)

    # ------------------------------------------------------------------
    def _zoom(self, width, u_focus, v_now, du_target=None, v_ahead_factor=1.5):
        """Перерегрирование: продолжить марш до v_hi, интерполировать окно.

        du_target=None — авто: окно W0 = max(w_factor*width, 40 du) на n клеток
        (du_new = W0/n, лямбда = du_old/du_new ~ n/(w_factor*45)).
        du_target=du_old — трансляция окна (extension, лямбда = 1).
        """
        du_old = self.du
        W0 = max(self.w_factor * width, 40.0 * du_old)
        if du_target is None:
            du_target = W0 / self.n
        W_new = du_target * self.n
        # v-бюджет: телескопический (<= родительский домен)
        v_hi = min(v_now + v_ahead_factor * W_new, self.stage_v[1])
        if v_hi - v_now < 12.0 * du_old:
            return False
        # продолжаем старый марш, пока v не покроет v_hi
        while self.j + 1 < self.n and self.v[self.j + 1] <= v_hi + 1e-12:
            self.j += 1
            st_new = self.sol._do_step(self.st, self.j)
            self.st = st_new
            self.buffer_v.append(self.v[self.j])
            self.buffer.append({k: st_new[k].copy() for k in FIELDS})
        v_hi = min(v_hi, self.v[self.j])           # реально покрытое v_hi
        v_lo = max(v_now - 0.5 * (v_hi - v_now), self.buffer_v[0])
        W_v = v_hi - v_lo
        if W_v < 24.0 * du_old:
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
            return False
        du_new = W_v / self.n
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
        # m — гладкая эволюционная переменная: не пересчитываем через
        # определение (катастрофическое сокращение near center).
        for d_ in (row, edge):
            d_["alpha2"] = np.clip(np.nan_to_num(d_["alpha2"], nan=1.0,
                                                 posinf=1.0, neginf=1.0), 1e-8, 1e8)
            for k in FIELDS:
                d_[k] = np.nan_to_num(d_[k], nan=0.0, posinf=0.0, neginf=0.0)

        lam = du_old / du_new
        self._new_stage((u_lo, u_hi), (v_lo, v_hi), row=row,
                        edge={"r": edge["r"], "Phi": edge["Phi"], "t": edge["t"]},
                        du_parent=du_old)
        self._z_acc += float(np.log(lam))
        self.diag.zooms += 1
        # контроль связей сразу после рестарта (качество интерполяции)
        c1 = self._stage_c1()
        self.diag.stage_constraints.append(
            {"zoom": self.diag.zooms, "lam": float(lam), "du": float(du_new),
             "z": self._z_acc, "c1_max": c1})
        if self.verbose:
            print(f"    [zoom #{self.diag.zooms}] W_v={W_v:.3e} lam={lam:.2f} "
                  f"z={self._z_acc:.3f} du={du_new:.3e} u=[{u_lo:.3f},{u_hi:.3f}] "
                  f"v=[{v_lo:.3f},{v_hi:.3f}] C1={c1:.1e}")
        return True

    def _stage_c1(self):
        """Максимум |C1|-связи на текущей строке (вне центра)."""
        st = self.st
        p_uu = self.sol._d_dx(st["p"])
        c_vs = (p_uu + 0.5 * KAPPA * st["r"] * st["s"] ** 2) / (2.0 * st["p"])
        mask = np.abs(st["r"]) > 5.0 * self.du
        if not mask.any():
            return 0.0
        return float(np.abs(st["c"] - c_vs)[mask].max())


# ------------------------------------------------------------------------------
# Анализ трекинга: пики кривизны -> период эха ДСС
# ------------------------------------------------------------------------------
def echo_peaks(track, key="Q", min_rel_prom=0.02):
    """Локальные максимумы Q(v): возвращает (v_peaks, val_peaks).

    Пик = точка, где y=v[key] больше соседей в окне +-3 строк и выше
    локального минимума + порог. Используется грубое сглаживание (окно 3).
    """
    v = np.array(track["v"])
    y = np.array(track[key], dtype=float)
    if len(y) < 9:
        return np.array([]), np.array([])
    ys = np.copy(y)
    ys[1:-1] = 0.25 * y[:-2] + 0.5 * y[1:-1] + 0.25 * y[2:]
    peaks = []
    for i in range(3, len(y) - 3):
        if ys[i] >= ys[i - 1] and ys[i] >= ys[i + 1] and ys[i] > ys[i - 3] and ys[i] > ys[i + 3]:
            peaks.append(i)
    # фильтр значимости: пик выше окружающих минимумов
    sig = []
    for i in peaks:
        lo = max(0, i - 40)
        hi = min(len(ys), i + 40)
        prom = ys[i] - min(ys[lo:i].min(initial=ys[i]), ys[i + 1:hi].min(initial=ys[i]))
        # (фикс v4): убран безусловный "or prom > 0" — он пропускал шумовые
        # максимумы, что давало фальшивые поезда пиков и фальшивую Delta ~ 0.01
        if prom > min_rel_prom * max(abs(ys).max(), 1e-12):
            sig.append(i)
    if not sig:
        return np.array([]), np.array([])
    # параболическое уточнение
    vp, yp = [], []
    for i in sig:
        if 0 < i < len(y) - 1:
            den = (y[i - 1] - 2 * y[i] + y[i + 1])
            d = 0.5 * (y[i - 1] - y[i + 1]) / den if abs(den) > 1e-30 else 0.0
            d = float(np.clip(d, -1, 1))
            vp.append(v[i] + d * (v[1] - v[0]))
            yp.append(y[i])
    return np.array(vp), np.array(yp)


def echo_period_from_peaks(v_peaks):
    """Дельта из отношения соседних интервалов: Delta = <ln(dv_n/dv_{n+1})>.

    Возия: интервалы между пиками убывают геометрически ~ e^{-n Delta}.
    Возвращяет (Delta, Delta_err, n_intervals).
    """
    if len(v_peaks) < 4:
        return float("nan"), float("nan"), 0
    dv = np.diff(v_peaks)
    dv = dv[dv > 0]
    if len(dv) < 3:
        return float("nan"), float("nan"), 0
    # fit ln(dv_n) = c - Delta*n (устойчивее, чем попарные отношения)
    n = np.arange(len(dv))
    A = np.vstack([n, np.ones_like(n)]).T
    y = np.log(dv)
    sol, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    Delta = -sol[0]
    yfit = A @ sol
    ss_res = float(((y - yfit) ** 2).sum())
    dof = max(len(y) - 2, 1)
    stderr = float(np.sqrt(ss_res / dof / max(len(y), 1))) if len(y) > 2 else float("nan")
    return float(Delta), stderr, len(dv)


# ------------------------------------------------------------------------------
def zoom_probe(A=0.0806, n=800, verbose=True, max_zooms=12):
    """Тест: ближнекритический забег с зумами (v2)."""
    print(f"Zoom-проба v2: A = {A}, N = {n}")
    runner = ZoomRunner(A=A, n=n, max_zooms=max_zooms, verbose=verbose)
    diag = runner.run()
    print(f"  supercritical = {diag.supercritical}, M_AH = {diag.m_ah:.6f} "
          f"(max {diag.m_ah_max:.6f}), zooms = {diag.zooms}, z = {runner._z_acc:.2f}, "
          f"stop = {diag.stopped}, время {diag.runtime:.1f} c")
    vp, yp = echo_peaks(runner.track, "Q")
    if len(vp) >= 4:
        D, Derr, npk = echo_period_from_peaks(vp)
        print(f"  пики Q: {len(vp)}, v = {np.round(vp, 4)}")
        print(f"  Delta (ln-интервалы) = {D:.4f} +- {Derr:.4f} (лит. 0.737)")
    return runner, diag


if __name__ == "__main__":
    zoom_probe(A=0.0805333 + 3e-5)
