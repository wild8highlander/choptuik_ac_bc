#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МНОГОСТАДИЙНЫЙ РЕГИДДИНГ (ZOOM) ДЛЯ ЗАДАЧИ ЧОПТЮКА
MULTI-STAGE REGRIDDING (ZOOM) FOR THE CHOPTUIK PROBLEM

Реализует адаптивное перерегриддинг в стиле Чоптюка (1993): когда активная
структура около центра сжимается до ~25 клеток, окно сетки переносится и
сжимается в λ ≈ 6 раз, поля интерполируются (кубически) из буфера строк,
эволюция продолжается на новой сетке. Уровень z = Σ ln(du_old/du_new) —
логарифмическая шкала масштабов; в этой шкале измеряется период эха Δ
дискретной самоподобности (DSS).

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
    m_ah: float = 0.0
    r_ah: float = 0.0
    zooms: int = 0
    z_final: float = 0.0
    stopped: str = "incomplete"
    runtime: float = 0.0


class ZoomRunner:
    """Многостадийный забег с перерегриддингом."""

    def __init__(self, A: float, n: int = 1200, max_zooms: int = 12,
                 w_trigger: float = 35.0, w_factor: float = 6.0,
                 max_2m_over_r: float = 2.0, verbose: bool = False):
        self.A = A
        self.n = n
        self.max_zooms = max_zooms
        self.w_trigger = w_trigger      # триггер: ширина структуры < w_trigger du
        self.w_factor = w_factor        # новое окно = w * w_factor
        self.max_2m_over_r = max_2m_over_r
        self.verbose = verbose
        self.diag = ZoomDiag()
        self.echo = []                  # (z, max 2m/r) — трек DSS
        self.m_ah_hist = []             # (v, m_ah) — рост массы горизонта
        self._new_stage(u_span=(U0, U1), v_span=(V0, V1))

    # ------------------------------------------------------------------
    def _new_stage(self, u_span, v_span, row=None, edge=None):
        cfg = SolverConfig(n_u=self.n, n_v=self.n, u_range=u_span, v_range=v_span,
                           monitor_every=10 ** 9, max_2m_over_r=self.max_2m_over_r)
        if row is None:
            data = GaussianPulseData(A=self.A, v_p=V_P, sigma=SIGMA, u0=u_span[0], v0=v_span[0])
            self.sol = DoubleNullSolver(cfg, data)
        else:
            self.sol = DoubleNullSolver.from_fields(cfg, u_span_u := np.linspace(*u_span, self.n),
                                                    np.linspace(*v_span, self.n),
                                                    row, edge["r"], edge["Phi"], edge["t"])
        self.u = self.sol.u
        self.v = self.sol.v
        self.du = self.sol.du
        self.dv = self.sol.dv
        self.st = {k: getattr(self.sol, k).copy() for k in FIELDS}
        self.j = 0
        self.buffer_v = [self.v[0]]
        self.buffer = [{k: self.st[k].copy() for k in FIELDS}]

    # ------------------------------------------------------------------
    def _row_diag(self, st, j):
        """Диагностика строки: max 2m/r, фокус, ширина активной зоны.

        Ширина измеряется по градиенту поля s = Phi_u (тонкая структура эха
        локализована в градиентах, а не в профиле массы).
        """
        r = st["r"]
        phys = r > 2.0 * self.du
        if not phys.any():
            return 0.0, 0.0, 0.0
        tmr = np.where(phys, 2.0 * st["m"] / np.where(phys, r, 1.0), 0.0)
        mx = float(tmr.max())
        # тонкая структура: |s| = |Phi_u|
        smag = np.abs(st["s"]) * (r > self.du)
        smax = float(smag.max())
        Phi_scale = float(np.max(np.abs(st["Phi"])[r > self.du])) or 1.0
        self.frac = smax * self.du / Phi_scale
        self.smax_loc = smax
        self.Phi_scale = Phi_scale
        # градиентный масштаб самой резкой фичи (в клетках)
        self.L_grad = (Phi_scale / smax) / self.du if smax > 0 else 1e9
        if smax <= 0:
            return mx, 0.0, float(self.u[np.argmax(tmr)])
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
        return mx, width, u_focus

    # ------------------------------------------------------------------
    def run(self):
        t0 = time.time()
        diag = self.diag
        stop_reason = None

        while True:
            sol = self.sol
            self.j += 1
            if self.j >= self.n:
                stop_reason = "v_exhausted"
                break
            st_new = sol._do_step(self.st, self.j)
            self.st = st_new
            v_now = self.v[self.j]
            self.buffer_v.append(v_now)
            self.buffer.append({k: st_new[k].copy() for k in FIELDS})
            if len(self.buffer_v) > self.n + 50:
                self.buffer_v.pop(0)
                self.buffer.pop(0)

            mx, width, u_focus = self._row_diag(st_new, self.j)
            self.echo.append((self._z_total(v_now), mx))

            # горизонт (разрешённый)
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
                if m_ah > diag.m_ah:
                    diag.m_ah = m_ah
                    diag.r_ah = r_ah
                self.m_ah_hist.append((v_now, m_ah))

            # сингулярность
            tmr_res = np.where(phys, 2.0 * st_new["m"] / np.where(phys, st_new["r"], 1.0), 0.0)
            if not np.isfinite(tmr_res).all() or tmr_res.max() > self.max_2m_over_r:
                diag.supercritical = True
                stop_reason = "singularity"
                break

            # триггер зума: градиентный масштаб < 50 клеток
            if (getattr(self, "L_grad", 1e9) < 50.0
                    and getattr(self, "smax_loc", 0.0) > 0.1 * getattr(self, "Phi_scale", 1.0)
                    and mx < 0.98 * self.max_2m_over_r
                    and 0 < width
                    and diag.zooms < self.max_zooms
                    and self._can_zoom(width, u_focus)):
                if self.verbose:
                    print(f"    [trigger] j={self.j} frac={self.frac:.2f} "
                          f"w/du={width/self.du:.0f} mx={mx:.3f}")
                self._zoom(width, u_focus, v_now)
                continue
        # конец while

        diag.stopped = stop_reason or "completed"
        diag.runtime = time.time() - t0
        # финальные поля в sol
        for k in FIELDS:
            setattr(self.sol, k, self.st[k])
        self.sol.v_final = self.v[min(self.j, self.n - 1)]
        return diag

    # ------------------------------------------------------------------
    def _z_base(self):
        """Базовый ln-масштаб: ln от ширины пульса к текущему окну (до зумов)."""
        return 0.0

    def _z_total(self, v_now):
        """Текущая лог-шкала: z накопленных зумов + ln(доля окна)."""
        # приближение: эхо-шкала ~ ln(окно/структура); используем только z зумов
        return self._z_acc

    _z_acc = 0.0

    def _can_zoom(self, width, u_focus):
        """Хватает ли буфера, u-домена и v-бюджета для зума."""
        W = max(self.w_factor * width, 40.0 * self.du)
        v_hi = min(self.v[self.j] + 1.5 * W, V1)
        v_lo = self.v[self.j] - 0.5 * (v_hi - self.v[self.j])
        if v_lo < self.buffer_v[0] - 1e-12:
            return False
        W_u = v_hi - v_lo
        u_lo, u_hi = u_focus - W_u / 2, u_focus + W_u / 2
        if u_lo <= self.u[0] + 1e-12 or u_hi >= self.u[-1] - 1e-12:
            return False
        return True

    def _zoom(self, width, u_focus, v_now):
        """Перерегриддинг: продолжить старый забег до v_hi, интерполировать окно."""
        W0 = max(self.w_factor * width, 40.0 * self.du)
        v_hi = min(v_now + 1.5 * W0, V1)
        v_lo = v_now - 0.5 * (v_hi - v_now)
        W = v_hi - v_lo                     # квадратные ячейки: W_u = W_v
        u_lo, u_hi = u_focus - W / 2, u_focus + W / 2

        # продолжаем старый марш, пока v не покроет v_hi
        sol = self.sol
        while self.v[min(self.j, self.n - 1)] < v_hi and self.j + 1 < self.n:
            self.j += 1
            st_new = sol._do_step(self.st, self.j)
            self.st = st_new
            self.buffer_v.append(self.v[self.j])
            self.buffer.append({k: st_new[k].copy() for k in FIELDS})

        # 2D-интерполяция полей из буфера на новую сетку
        vb = np.array(self.buffer_v)
        ub = self.u.copy()
        # срез буфера по v ∈ [v_lo, v_hi]
        mask = (vb >= v_lo - 1e-12) & (vb <= v_hi + 1e-12)
        vb_s = vb[mask]
        buf_s = [self.buffer[i] for i in np.where(mask)[0]]
        if len(vb_s) < 8:
            return False
        du_new = W / self.n
        u_new = np.linspace(u_lo, u_hi, self.n)
        v_new = np.linspace(v_lo, v_hi, self.n)
        Vg, Ug = np.meshgrid(vb_s, u_new, indexing="ij")

        CLIP = {"r": 1e3, "Phi": 50.0, "p": 1e3, "q": 1e3, "s": 1e6, "t": 1e6,
                "c": 1e6, "m": 1e3, "alpha2": 1e8, "d": 1e8, "w": 1e8}

        def sanitize(F):
            F = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)
            return F

        def interp_field(k, u_target=None):
            Fb = np.array([b[k] for b in buf_s])          # (n_v_buf, n_u)
            Fb = sanitize(Fb)
            Fb = np.clip(Fb, -CLIP[k], CLIP[k])
            itp = RegularGridInterpolator((vb_s, ub), Fb, method="cubic",
                                          bounds_error=False, fill_value=None)
            if u_target is None:
                return itp(np.stack([Vg, Ug], axis=-1))
            Vg2, Ug2 = np.meshgrid(vb_s, u_target, indexing="ij")
            return itp(np.stack([Vg2, Ug2], axis=-1))

        row = {k: interp_field(k)[0, :] for k in FIELDS}   # строка v = v_lo
        # колонки края u = u_lo (в одной 2D-интерполяции — срез[:, 0])
        edge_full = {k: interp_field(k) for k in FIELDS}
        edge = {k: edge_full[k][:, 0] for k in FIELDS}
        # r-колонка для omega_v на краю: на сетке нового v
        edge_r_col = edge["r"]
        # ВАЖНО: m не пересчитываем через определение (катастрофическое
        # сокращение near center) — m гладкая эволюционная переменная.
        # Только гарантируем alpha2 > 0 и конечность полей.
        for d_ in (row, edge):
            d_["alpha2"] = np.clip(np.nan_to_num(d_["alpha2"], nan=1.0,
                                                  posinf=1.0, neginf=1.0), 1e-6, 1e8)
            for k in FIELDS:
                d_[k] = np.nan_to_num(d_[k], nan=0.0, posinf=0.0, neginf=0.0)

        du_old = self.du
        self._new_stage((u_lo, u_hi), (v_lo, v_hi), row=row,
                        edge={"r": edge["r"], "Phi": edge["Phi"], "t": edge["t"]})
        lam = du_old / du_new
        self._z_acc += float(np.log(lam))
        self.diag.zooms += 1
        if self.verbose:
            print(f"    [zoom #{self.diag.zooms}] W = {W:.3e}, lambda = {lam:.2f}, "
                  f"z = {self._z_acc:.3f}, du = {du_new:.3e}")
        return True


# ------------------------------------------------------------------------------
def zoom_probe(A=0.0806, n=1200, verbose=True):
    """Тест: ближнекритический забег с зумами."""
    print(f"Zoom-проба: A = A* + 1e-4 = {A}, N = {n}")
    runner = ZoomRunner(A=A, n=n, verbose=verbose)
    diag = runner.run()
    print(f"  supercritical = {diag.supercritical}, M_AH = {diag.m_ah:.4e}, "
          f"r_AH = {diag.r_ah:.3e}, zooms = {diag.zooms}, z = {runner._z_acc:.2f}, "
          f"stop = {diag.stopped}, время {diag.runtime:.1f} c")
    return runner, diag


if __name__ == "__main__":
    zoom_probe()
