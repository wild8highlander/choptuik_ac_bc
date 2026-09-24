#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ЧИСЛЕННЫЙ СОЛВЕР: СФЕРИЧЕСКИЙ КОЛЛАПС БЕЗМАССОВОГО СКАЛЯРНОГО ПОЛЯ
NUMERICAL SOLVER: SPHERICAL COLLAPSE OF A MASSLESS SCALAR FIELD
================================================================================

Система уравнений (машинный вывод в sympy_derivation.py, верифицирован на
точном решении Робертса–Оширо с невязками ~1e-41):

    ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2,   omega := ln(alpha)

    (SC)  Phi_uv = -(r_u Phi_v + r_v Phi_u)/r
    (UV)  r_uv  = -(r_u r_v + alpha^2/4)/r  =  -alpha^2 m / (2 r^2)
    (C1)  r_uu  = 2 omega_u r_u - (kappa/2) r Phi_u^2
    (C2)  r_vv  = 2 omega_v r_v - (kappa/2) r Phi_v^2
    (TH)  omega_uv = alpha^2 m / (2 r^3) - (kappa/2) Phi_u Phi_v

где m(u,v) — масса Мизнера–Шарпа:

    1 - 2m/r = g^{ab} r_a r_b = -4 r_u r_v / alpha^2
    <=>  m = (r/2)(1 + 4 r_u r_v / alpha^2),   pq + alpha^2/4 = alpha^2 m/(2r)

Тождества, делающие систему регулярной (включая центр r = 0):
    (r^2)_{uv} = -alpha^2/2,        P := r r_u:  P_v = -alpha^2/4,
    m_u = -kappa r^2 Phi_u^2 r_v / alpha^2,
    m_v = -kappa r^2 Phi_v^2 r_u / alpha^2.

Метод: характеристический марш по строкам v (Goursat), RK2-Хойн (предиктор–
корректор на середине шага), векторизация по u (NumPy). Связи C1/C2 и
определение m контролируются на каждой строке. Горизонт/apparent horizon:
минимум q = r_v < 0 (захват), M_BH = m в точке q = 0 (там m = r/2).

Система единиц: 4 pi G = 1, т.е. kappa = 8 pi G = 2 (нормировка Burko 1996).

Запуск как модуля:  from solver import DoubleNullSolver, GaussianPulseData
================================================================================
"""
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field

import numpy as np

KAPPA = 2.0  # kappa = 8 pi G = 2 (4 pi G = 1)


# ------------------------------------------------------------------------------
# Начальные данные
# ------------------------------------------------------------------------------
@dataclass
class GaussianPulseData:
    """Семейство начальных данных Чоптюка: гауссов импульс на входящей
    характеристике u = u0; на строке v = v0 — плоское пространство.

    Phi(u0, v) = A exp(-(v - v_p)^2 / (2 sigma^2))
    """

    A: float
    v_p: float
    sigma: float
    u0: float
    v0: float = 0.0

    def edge_phi(self, v: np.ndarray) -> np.ndarray:
        return self.A * np.exp(-((v - self.v_p) ** 2) / (2 * self.sigma**2))

    def edge_phi_v(self, v: np.ndarray) -> np.ndarray:
        return -self.A * (v - self.v_p) / self.sigma**2 * np.exp(
            -((v - self.v_p) ** 2) / (2 * self.sigma**2)
        )

    def edge_r(self, v: np.ndarray) -> np.ndarray:
        return (v - self.u0) / 2.0

    def edge_r_v(self, v: np.ndarray) -> np.ndarray:
        return np.full_like(v, 0.5)

    def edge_r_vv(self, u_edge: float, v: np.ndarray) -> np.ndarray:
        return np.zeros_like(np.asarray(v, dtype=float))


@dataclass
class RobertsData:
    """Точное решение Робертса–Оширо (Burko 1996, (15)-(16)) как начальные
    данные на строке и характеристике (для валидации солвера).

    r^2 = 1/4 [(1-4s^2) v^2 - 2 u v + u^2],
    Phi = 1/2 ln |(1-2s-u/v)/(1+2s-u/v)|,   alpha = 1.
    """

    sigma: float

    def fields(self, u: np.ndarray, v: np.ndarray):
        """Возвращает (r, Phi, r_u, r_v, Phi_u, Phi_v) на сетке (u,v)."""
        s = self.sigma
        r2 = 0.25 * ((1 - 4 * s**2) * v**2 - 2 * u * v + u**2)
        r = np.sqrt(np.maximum(r2, 1e-300))
        # r_u = (r2)_u/(2r), r_v = (r2)_v/(2r)
        r2_u = 0.25 * (-2 * v + 2 * u)
        r2_v = 0.25 * (2 * (1 - 4 * s**2) * v - 2 * u)
        r_u = r2_u / (2 * r)
        r_v = r2_v / (2 * r)
        a = 1 - 2 * s - u / v
        b = 1 + 2 * s - u / v
        Phi = 0.5 * np.log(np.abs(a / b))
        # dPhi/du = 1/2 * (-1/v) * (1/a - 1/b)
        Phi_u = 0.5 * (-1.0 / v) * (1.0 / a - 1.0 / b)
        # dPhi/dv = 1/2 * (u/v^2) * (1/a - 1/b)
        Phi_v = 0.5 * (u / v**2) * (1.0 / a - 1.0 / b)
        return r, Phi, r_u, r_v, Phi_u, Phi_v

    def edge_r_vv(self, u_edge: float, v: np.ndarray) -> np.ndarray:
        """r_vv на характеристике u = u_edge: (r^2)_vv = (1-4s^2)/2 (константа)."""
        s = self.sigma
        r2_vv = (1 - 4 * s**2) / 2.0
        # r_vv = (r^2)_vv/(2r) - (r_v)^2/r   (в точке u = u_edge)
        u_arr = np.full_like(np.asarray(v, dtype=float), u_edge)
        r, _, _, r_v, _, _ = self.fields(u_arr, np.asarray(v, dtype=float))
        return r2_vv / (2 * r) - r_v**2 / r


# ------------------------------------------------------------------------------
# Солвер
# ------------------------------------------------------------------------------
@dataclass
class SolverConfig:
    n_u: int = 800                 # число точек по u (включая границы)
    n_v: int = 800                 # число точек по v
    u_range: tuple = (-1.0, 1.1)   # [u0, u1]
    v_range: tuple = (0.0, 1.0)    # [v0, v1]
    monitor_every: int = 25        # частота контроля связей
    max_2m_over_r: float = 2.0     # стоп-критерий (сингулярность)


@dataclass
class Diagnostics:
    """Результаты мониторинга."""

    c1_max: float = 0.0            # |C1-связь| max
    c2_max: float = 0.0            # |C2-связь| max
    mdef_max: float = 0.0          # |m - m_определение| max
    sandwich_q_max: float = 0.0    # |q_RK - q_sandwich| max
    sandwich_t_max: float = 0.0
    history: list = field(default_factory=list)   # строки-диагностики
    ah_found: bool = False
    m_ah: float = 0.0              # масса на горизонте (max по строкам)
    r_ah: float = 0.0
    v_ah: float = float("nan")
    stopped_reason: str = "completed"


class DoubleNullSolver:
    """Двунулевой характеристический солвер Эйнштейн–скаляр (сферическая симметрия)."""

    def __init__(self, cfg: SolverConfig, data):
        self.cfg = cfg
        self.data = data
        self.u = np.linspace(cfg.u_range[0], cfg.u_range[1], cfg.n_u)
        self.v = np.linspace(cfg.v_range[0], cfg.v_range[1], cfg.n_v)
        self.du = self.u[1] - self.u[0]
        self.dv = self.v[1] - self.v[0]
        self.diag = Diagnostics()
        self.R_heal = 0.0   # радиус унаследованной битой центральной зоны (зум)
        # марш t ОТ центра наружу (зум-стадии): мода 1/r затухает, центр —
        # внутреннее граничное условие t(i0) = s(i0); краевые данные не нужны
        self.march_from_center = False
        self.heal_enabled = True   # рутина лечения центра (отключается зум-машиной)
        # сеточный пол для r в знаменателях (защита от деления на r~0:
        # эволюционный m в центральной клетке не согласован с r ~ 1e-14,
        # что давало всплески w = a2 m / (2 r_safe^3) ~ 1e20 и взрыв d)
        self.r_floor = 0.5 * self.du
        self._init_fields()

    # ------------------------------------------------------------------ init
    def _init_fields(self):
        u, v0 = self.u, self.v[0]
        n = self.cfg.n_u
        if self.data is None:
            zz = np.zeros(n)
            self.r = zz.copy(); self.Phi = zz.copy()
            self.p = zz.copy(); self.q = zz.copy()
            self.s = zz.copy(); self.t = zz.copy()
            self.m = zz.copy(); self.c = zz.copy()
            self.alpha2 = np.ones(n)
            self.d = zz.copy(); self.w = zz.copy()
            self._edge_r_arr = np.zeros(self.cfg.n_v)
            self._edge_Phi_arr = np.zeros(self.cfg.n_v)
            self._edge_t_arr = np.zeros(self.cfg.n_v)
            return
        if isinstance(self.data, GaussianPulseData):
            # Плоская строка: r = (v0 - u)/2, Phi = 0
            self.r = (v0 - u) / 2.0
            self.Phi = np.zeros(n)
            self.p = np.full(n, -0.5)   # r_u
            self.q = np.full(n, 0.5)    # r_v
            self.s = np.zeros(n)        # Phi_u
            self.t = np.zeros(n)        # Phi_v
            alpha2 = np.ones(n)
        elif isinstance(self.data, RobertsData):
            r, Phi, r_u, r_v, Phi_u, Phi_v = self.data.fields(u, np.full_like(u, v0))
            self.r, self.Phi = r.copy(), Phi.copy()
            self.p, self.q = r_u.copy(), r_v.copy()
            self.s, self.t = Phi_u.copy(), Phi_v.copy()
            alpha2 = np.ones(n)
        else:
            raise TypeError(type(self.data))
        # Масса Мизнера–Шарпа из определения
        self.m = (self.r / 2.0) * (1.0 + 4.0 * self.p * self.q / alpha2)
        # omega_u (C1): r_uu = 2 omega_u r_u - (kappa/2) r s^2
        p_uu = self._d_dx(self.p)
        self.c = (p_uu + 0.5 * KAPPA * self.r * self.s**2) / (2.0 * self.p)
        self.alpha2 = alpha2
        # omega_v: на строке v0 — из плоскости/Робертса; для импульса d = 0
        self.d = np.zeros(n)
        # omega_uv (TH): alpha^2 m/(2 r^3) - (kappa/2) s t  (≈0 для обоих типов данных)
        self.w = self.alpha2 * self.m / (2.0 * self.r**3) - 0.5 * KAPPA * self.s * self.t
        # edge-гейдж: интеграл omega_v по краю (накапливается в run)
        self._edge_omega_acc = 0.0

    def _d_dx(self, f):
        """Вторая производная по u центральными разностями (2-й порядок)."""
        d = np.zeros_like(f)
        d[1:-1] = (f[2:] - f[:-2]) / (2.0 * self.du)
        d[0] = (-3 * f[0] + 4 * f[1] - f[2]) / (2.0 * self.du)
        d[-1] = (3 * f[-1] - 4 * f[-2] + f[-3]) / (2.0 * self.du)
        return d

    def _d2_dx2(self, f):
        d2 = np.zeros_like(f)
        d2[1:-1] = (f[2:] - 2 * f[1:-1] + f[:-2]) / self.du**2
        return d2

    # ------------------------------------------------------- slopes (RK2)
    def _slopes(self, st):
        """Скорости по v для всех полей. st — dict текущих полей."""
        r, Phi, p, q, s, t, c, m, a2, d, w = (
            st["r"], st["Phi"], st["p"], st["q"], st["s"], st["t"],
            st["c"], st["m"], st["alpha2"], st["d"], st["w"],
        )
        r_safe = np.where(np.abs(r) < self.r_floor, self.r_floor, r)
        m_safe = m
        slopes = {}
        slopes["r"] = q
        slopes["Phi"] = t
        # (UV): r_uv = -alpha^2 m / (2 r^2)   — p_v
        slopes["p"] = -a2 * m_safe / (2.0 * r_safe**2)
        # (C2): q_v = 2 d q - (kappa/2) r t^2
        slopes["q"] = 2.0 * d * q - 0.5 * KAPPA * r * t**2
        # (SC): s_v = -(p t + q s)/r
        slopes["s"] = -(p * t + q * s) / r_safe
        # (TH): c_v = alpha^2 m/(2 r^3) - (kappa/2) s t
        slopes["c"] = a2 * m_safe / (2.0 * r_safe**3) - 0.5 * KAPPA * s * t
        # m_v = -kappa r^2 t^2 p / alpha^2
        slopes["m"] = -KAPPA * r**2 * t**2 * p / a2
        # alpha2_v = 2 alpha2 d
        slopes["alpha2"] = 2.0 * a2 * d
        # t_v: BDF2 по истории (только для середины шага)
        slopes["t"] = None  # заполняется вызывающим кодом
        return slopes

    # ------------------------------------------------------- edge column
    def _edge_overwrite(self, st, v_new):
        """Точные данные на входящей характеристике u = u0 (колонка i = 0)."""
        if self.data is None:
            return st
        if isinstance(self.data, GaussianPulseData):
            st["r"][0] = float(self.data.edge_r(np.array([v_new]))[0])
            st["Phi"][0] = float(self.data.edge_phi(np.array([v_new]))[0])
            st["t"][0] = float(self.data.edge_phi_v(np.array([v_new]))[0])
            st["q"][0] = float(self.data.edge_r_v(np.array([v_new]))[0])
        elif isinstance(self.data, RobertsData):
            r, Phi, r_u, r_v, Phi_u, Phi_v = self.data.fields(
                np.array([self.u[0]]), np.array([v_new])
            )
            st["r"][0] = float(r[0])
            st["Phi"][0] = float(Phi[0])
            st["p"][0] = float(r_u[0])
            st["q"][0] = float(r_v[0])
            st["s"][0] = float(Phi_u[0])
            st["t"][0] = float(Phi_v[0])
        return st

    def _edge_omega_v(self, st, v_new=None):
        """omega_v на краю из C2: d_edge = (r_vv + (kappa/2) r t^2) / (2 q),
        где r_vv берётся из данных (у импульса r_vv = 0, у Робертса — нет)."""
        if v_new is None:
            v_new = self.v[-1]
        if self.data is None:
            j = int(np.searchsorted(self.v, float(np.asarray(v_new).reshape(-1)[0])))
            jr = min(max(j, 1), len(self._edge_r_arr) - 2)
            r_vv = (self._edge_r_arr[jr + 1] - 2.0 * self._edge_r_arr[jr]
                    + self._edge_r_arr[jr - 1]) / self.dv ** 2
        elif hasattr(self.data, "edge_r_vv"):
            r_vv = float(self.data.edge_r_vv(self.u[0], np.array([v_new]))[0])
        else:
            r_vv = 0.0
        return (r_vv + 0.5 * KAPPA * st["r"][0] * st["t"][0] ** 2) / (2.0 * st["q"][0])

    # ------------------------------------------------------- main march
    @classmethod
    def from_fields(cls, cfg, u, v, row, edge_r, edge_Phi, edge_t):
        """Солвер из готовых полей (после перерегриддинга); data = None.

        row — dict полей на строке v[0]; edge_* — колонки на u[0] (сетка v).
        """
        obj = cls(cfg, data=None)
        obj.u = np.asarray(u, dtype=float)
        obj.v = np.asarray(v, dtype=float)
        obj.du = obj.u[1] - obj.u[0]
        obj.dv = obj.v[1] - obj.v[0]
        for k, arr in row.items():
            setattr(obj, k, np.asarray(arr, dtype=float).copy())
        obj._edge_r_arr = np.asarray(edge_r, dtype=float)
        obj._edge_Phi_arr = np.asarray(edge_Phi, dtype=float)
        obj._edge_t_arr = np.asarray(edge_t, dtype=float)
        return obj

    def _center_heal(self, t_arr, s_arr, m_arr, r_arr, deep=False):
        """Регулярная реконструкция центральной зоны.

        Routine (deep=False, каждая строка): зона |r| <= max(2 du, R_heal),
        ДВУСТОРОННЕЕ парное чётное усреднение: y[k] = 0.5[(t+s)_{-k} + (t+s)_{+k}]
        (через тождество зеркала s(-r)=t(+r) сумма (t+s) чётна; усреднение
        убывает антисимметричный мусор — моду 1/r и расстройку маршей —
        и СОХРАНЯЕТ физическую вариацию по r, в отличие от константы).

        Deep (deep=True, ОДИН раз на рестарт-строке после зума): зона
        |r| <= R_zone, R_zone = max(2 du, R_heal) — константа y0 = чётный
        предел (t+s)/2 из аннулуса [1.15, 2.6] R_zone (аннулус вне
        унаследованной биты зоны), m ~ r^3 по аннулусу. Убивает
        унаследованный мусор родителя на самой рестарт-строке.
        """
        R_zone = max(2.0 * self.du, float(getattr(self, "R_heal", 0.0)))
        r_abs = np.abs(r_arr)
        i0 = int(np.argmin(r_abs))
        if r_abs[i0] > 3.0 * self.du:
            return  # центр вне окна
        n = len(r_arr)
        if not deep:
            # двухстороннее парное чётное усреднение (вариация сохраняется);
            # dr ~ 0.5 du на клетку (p ~ -1/2), так что клеток 2*R_zone/du
            K = int(np.ceil(2.0 * R_zone / self.du))
            K = min(K, i0, n - 1 - i0)
            if K < 1:
                y0 = 0.5 * (t_arr[i0] + s_arr[i0])
                t_arr[i0] = y0
                s_arr[i0] = y0
                return
            A_plus = (t_arr[i0 - K:i0 + 1] + s_arr[i0 - K:i0 + 1])[::-1]  # k=0..K
            A_minus = t_arr[i0:i0 + K + 1] + s_arr[i0:i0 + K + 1]       # k=0..K
            y = 0.5 * (A_plus + A_minus)
            t_arr[i0 - K:i0 + 1] = y[::-1]
            s_arr[i0 - K:i0 + 1] = y[::-1]
            t_arr[i0:i0 + K + 1] = y
            s_arr[i0:i0 + K + 1] = y
            return
        # аннулус в ФИЗИЧЕСКИХ r-единицах: dr/du = p ~ -1/2, ищем по массиву r
        rev = r_abs[:i0 + 1][::-1]          # возрастающий |r| от центра
        j_near = int(np.searchsorted(rev, 1.15 * R_zone))
        j_far = int(np.searchsorted(rev, 2.60 * R_zone))
        if j_far - j_near < 2 or j_near < 1 or i0 - j_far < 0:
            lo, hi = max(i0 - 6, 0), min(i0 + 7, n)
            y0 = 0.5 * (t_arr[i0] + s_arr[i0])
            t_arr[lo:hi] = y0
            s_arr[lo:hi] = y0
            return
        i_near = i0 - j_near
        i_far = i0 - j_far
        r_near = float(r_arr[i_near]); r_far = float(r_arr[i_far])
        y_near = float(0.5 * (t_arr[i_near] + s_arr[i_near]))
        y_far = float(0.5 * (t_arr[i_far] + s_arr[i_far]))
        if not (np.isfinite(y_near) and np.isfinite(y_far)):
            y0 = 0.5 * (t_arr[i0] + s_arr[i0])
            if not np.isfinite(y0):
                return
        else:
            den = r_far * r_far - r_near * r_near
            if den <= 0:
                y0 = y_near
            else:
                y0 = y_near - (y_near - y_far) * r_near * r_near / den
            lo_b = min(y_near, y_far) - 2.0 * abs(y_far - y_near)
            hi_b = max(y_near, y_far) + 2.0 * abs(y_far - y_near)
            y0 = float(np.clip(y0, lo_b, hi_b))
        lo = max(i0 - j_near, 0)
        hi = min(i0 + j_near + 1, n)
        t_arr[lo:hi] = y0
        s_arr[lo:hi] = y0
        # масса: регулярный закон m ~ r^3 (нечётное продолжение в зеркало)
        m_near = float(m_arr[i_near])
        if np.isfinite(m_near) and r_near > 0:
            m_arr[lo:hi] = m_near * (r_arr[lo:hi] / r_near) ** 3

    def _do_step(self, st, j):
        """Один шаг характеристического марша: строка j-1 -> строка j."""
        v_new = self.v[j]
        dv = self.dv
        EVOLVED = ("r", "p", "q", "s", "c", "m", "alpha2")

        # --- скорости на текущей строке (предиктор) --------------------
        sl = self._slopes(st)

        # --- предиктор: середина шага ----------------------------------
        st_m = {k: st[k] + 0.5 * dv * sl[k] for k in EVOLVED}
        st_m["Phi"], st_m["t"] = st["Phi"], st["t"]
        st_m["d"], st_m["w"] = st["d"], st["w"]
        st_m["w"] = self._th_form(st_m)
        d_edge_m = self._edge_omega_v(st_m, v_new - 0.5 * dv)
        st_m["d"] = d_edge_m + self._cumtrapz_u(st_m["w"])

        # --- корректор с итерацией (t на середине уточняется) ----------
        t_guess = st["t"]
        for _it in range(2):
            st_m["t"] = 0.5 * (st["t"] + t_guess)
            st_m["Phi"] = st["Phi"] + 0.25 * dv * (st["t"] + t_guess)
            st_m["w"] = self._th_form(st_m)
            st_m["d"] = d_edge_m + self._cumtrapz_u(st_m["w"])
            sl_m = self._slopes(st_m)

            st_new = {k: st[k] + dv * sl_m[k] for k in EVOLVED}
            st_new["Phi"], st_new["t"] = st["Phi"], st["t"]
            st_new["d"], st_new["w"] = st["d"], st["w"]
            st_new = self._edge_overwrite(st_new, v_new)
            st_new["w"] = self._th_form(st_new)
            d_edge_new = self._edge_omega_v(st_new, v_new)
            st_new["d"] = d_edge_new + self._cumtrapz_u(st_new["w"])

            # (Phi, t): ОДУ t_u = SC. Два режима:
            #   march_from_center (зум-стадии): марш ОТ центра наружу,
            #     внутреннее ГУ t(i0)=s(i0); мода 1/r затухает наружу.
            #   иначе (базовая стадия): марш с края (данные Goursat),
            #     клэмп t=s в зоне |r|<=5du, зеркало — явный марш.
            r_new = st_new["r"]
            r_safe = np.where(np.abs(r_new) < self.r_floor, self.r_floor, r_new)
            pr = st_new["p"] / r_safe
            qsr = st_new["q"] * st_new["s"] / r_safe
            r_reg = 5.0 * self.du
            if self.march_from_center:
                i0c = int(np.argmin(np.abs(r_new)))
                t_new = np.empty_like(st_new["p"])
                t_new[i0c] = float(st_new["s"][i0c])
                # (+r)-сторона: r убывает с i, наружу = убывание i
                for i in range(i0c - 1, -1, -1):
                    t_new[i] = (t_new[i + 1] * (1.0 + 0.5 * self.du * pr[i + 1])
                                + 0.5 * self.du * (qsr[i] + qsr[i + 1])) \
                               / (1.0 - 0.5 * self.du * pr[i])
                # зеркало: наружу = рост i
                for i in range(i0c + 1, len(pr)):
                    t_new[i] = (t_new[i - 1] * (1.0 - 0.5 * self.du * pr[i - 1])
                                - 0.5 * self.du * (qsr[i - 1] + qsr[i])) \
                               / (1.0 + 0.5 * self.du * pr[i])
            else:
                below = r_new <= r_reg
                i_cross = int(np.argmax(below)) if below.any() else len(pr)
                t_new = np.empty_like(st_new["p"])
                t_new[0] = float(self._edge_t(np.array([v_new]))[0])
                # неявный марш по точкам 1..i_cross-1 (все с r > r_reg)
                n_imp = max(i_cross - 1, 0)
                if n_imp >= 1:
                    A = 1.0 - 0.5 * self.du * pr[:n_imp]
                    D = 1.0 + 0.5 * self.du * pr[1:n_imp + 1]
                    B = -0.5 * self.du * (qsr[1:n_imp + 1] + qsr[:n_imp])
                    C = A / D
                    E = B / D
                    LCp = np.concatenate(([0.0], np.cumsum(np.log(C))))
                    Ep = np.concatenate(([0.0], E))
                    Sv = np.cumsum(Ep * np.exp(-LCp))
                    t_new[1:n_imp + 1] = np.exp(LCp[1:]) * (t_new[0] + Sv[1:])
                # центральная зона: регулярность t = s
                below_m = r_new < -r_reg
                i_mirror = int(np.argmax(below_m)) if below_m.any() else len(pr)
                i_end_cross = max(i_mirror, i_cross)
                t_new[i_cross:i_end_cross] = st_new["s"][i_cross:i_end_cross]
                # зеркало: явный марш
                for i in range(i_end_cross, len(pr)):
                    SC_im1 = -(st_new["p"][i - 1] * t_new[i - 1]
                               + st_new["q"][i - 1] * st_new["s"][i - 1]) / r_safe[i - 1]
                    t_new[i] = t_new[i - 1] + self.du * SC_im1
                # чётная реконструкция центра (чистит расстройку маршей)
                if self.heal_enabled:
                    self._center_heal(t_new, st_new["s"], st_new["m"], r_new)
            st_new["t"] = t_new
            st_new["Phi"] = st["Phi"] + 0.5 * dv * (st["t"] + t_new)
            st_new["Phi"][0] = float(self._edge_Phi(np.array([v_new]))[0])
            # ВАЖНО: w/d НЕ пересчитываем после марша t — иначе свежий мусор
            # марша через w ~ s*t и cumtrapz расползается в d по всему зеркалу
            # (w/d от предыдущей итерации — валидированное поведение).
            t_guess = t_new
        return st_new

    def run(self, verbose=True):
        cfg = self.cfg
        n_u, n_v = cfg.n_u, cfg.n_v
        t_start = time.time()
        self.snapshots = []

        st = {
            "r": self.r, "Phi": self.Phi, "p": self.p, "q": self.q,
            "s": self.s, "t": self.t, "c": self.c, "m": self.m,
            "alpha2": self.alpha2, "d": self.d, "w": self.w,
        }

        v_new = self.v[0]
        self._rows_since_ah_growth = 0
        for j in range(1, n_v):
            st_new = self._do_step(st, j)
            # Маскируем NaN (сингулярность внутри захваченной области не
            # загрязняет внешнюю область из-за характеристической структуры)
            for k in st_new:
                st_new[k] = np.nan_to_num(st_new[k], nan=0.0,
                                          posinf=0.0, neginf=0.0)
            v_new = self.v[j]

            # --- мониторинг связей ------------------------------------------
            if j % cfg.monitor_every == 0 or j == n_v - 1:
                self._monitor(st, st_new, j)

            # --- snapshots ---------------------------------------------------
            if j % max(1, n_v // 40) == 0:
                self.snapshots.append({
                    "v": v_new,
                    "r": st_new["r"].copy(),
                    "Phi": st_new["Phi"].copy(),
                    "m": st_new["m"].copy(),
                    "alpha2": st_new["alpha2"].copy(),
                    "two_m_over_r": 2.0 * st_new["m"] / np.where(
                        np.abs(st_new["r"]) > 1e-14, st_new["r"], 1e-14),
                })

            # --- горизонт (только разрешённые горизонты: r > 8 du) ----------
            r_thresh = 8.0 * self.du
            phys = st_new["r"] > r_thresh
            q_phys = np.where(phys, st_new["q"], 1.0)
            if q_phys.min() < 0.0:
                if not self.diag.ah_found:
                    self.diag.ah_found = True
                    self.diag.v_ah = v_new
                m_ah, r_ah = self._ah_mass(st_new, r_thresh)
                # санитарность: масса горизонта не может превышать полную массу
                # (m на ВНЕШНЕМ крае физической области) и радиус должен быть > 0
                phys_idx = np.where(phys)[0]
                m_out = float(st_new["m"][phys_idx[-1]]) if phys_idx.size else 0.0
                sane = (np.isfinite(m_ah) and 0 < m_ah < 1.2 * max(m_out, 1e-12)
                        and r_ah > 0)
                if sane and m_ah > self.diag.m_ah * 1.005:
                    self.diag.m_ah = m_ah
                    self.diag.r_ah = r_ah
                    self._rows_since_ah_growth = 0
                else:
                    self._rows_since_ah_growth += 1

            # --- стоп-критерий: насыщение массы горизонта или сингулярность --
            # стоп: валидная (конечная) часть строки съедена сингулярностью
            n_finite = int(np.isfinite(st_new["m"]).sum())
            if n_finite < 0.5 * n_u:
                self.diag.stopped_reason = "singularity (valid region < 50%)"
                st = st_new
                break
            if (self.diag.ah_found and self._rows_since_ah_growth > 0.25 * n_v
                    and self.diag.m_ah > 0):
                self.diag.stopped_reason = "AH mass saturated"
                st = st_new
                break

            # --- сдвиг строки ---------------------------------------------------
            st = st_new

        # финальные поля
        self.r, self.Phi = st["r"], st["Phi"]
        self.p, self.q, self.s, self.t = st["p"], st["q"], st["s"], st["t"]
        self.c, self.m, self.alpha2, self.d, self.w = \
            st["c"], st["m"], st["alpha2"], st["d"], st["w"]
        self.v_final = v_new
        self.runtime = time.time() - t_start
        if verbose:
            self.print_summary()
        return self.diag

    # ------------------------------------------------------------ helpers
    def _edge_t(self, v):
        """Точное Phi_v на входящей характеристике u = u0."""
        if self.data is None:
            j = int(np.searchsorted(self.v, float(np.asarray(v).reshape(-1)[0])))
            return np.array([self._edge_t_arr[min(j, len(self._edge_t_arr) - 1)]])
        if isinstance(self.data, GaussianPulseData):
            return self.data.edge_phi_v(np.asarray(v, dtype=float))
        if isinstance(self.data, RobertsData):
            return self.data.fields(np.full_like(np.asarray(v, dtype=float), self.u[0]), np.asarray(v, dtype=float))[5]
        raise TypeError(type(self.data))

    def _edge_Phi(self, v):
        """Точное Phi на входящей характеристике u = u0."""
        if self.data is None:
            j = int(np.searchsorted(self.v, float(np.asarray(v).reshape(-1)[0])))
            return np.array([self._edge_Phi_arr[min(j, len(self._edge_Phi_arr) - 1)]])
        if isinstance(self.data, GaussianPulseData):
            return self.data.edge_phi(np.asarray(v, dtype=float))
        if isinstance(self.data, RobertsData):
            return self.data.fields(np.full_like(np.asarray(v, dtype=float), self.u[0]), np.asarray(v, dtype=float))[1]
        raise TypeError(type(self.data))

    def _th_form(self, st):
        """(TH): omega_uv = alpha^2 m / (2 r^3) - (kappa/2) s t."""
        r_safe = np.where(np.abs(st["r"]) < self.r_floor, self.r_floor, st["r"])
        return st["alpha2"] * st["m"] / (2.0 * r_safe**3) - 0.5 * KAPPA * st["s"] * st["t"]

    def _cumtrapz_u(self, f):
        """Накопленный интеграл по u от левого края (трапеции)."""
        out = np.zeros_like(f)
        out[1:] = np.cumsum(0.5 * (f[1:] + f[:-1])) * self.du
        return out

    def _ah_mass(self, st, r_thresh=0.0):
        """Масса и радиус на apparent horizon (q = 0, переход + → −, r > r_thresh)."""
        q = st["q"]
        m_ah, r_ah = 0.0, 0.0
        valid = st["r"] > r_thresh
        qs = np.where(valid, q, 1.0)
        idx = np.where((qs[:-1] > 0) & (qs[1:] <= 0))[0]
        if idx.size:
            i = idx[-1]  # внешняя точка перехода
            # линейная интерполяция q -> 0
            q0, q1 = qs[i], qs[i + 1]
            f = q0 / (q0 - q1) if (q0 - q1) != 0 else 0.0
            r_ah = st["r"][i] * (1 - f) + st["r"][i + 1] * f
            m_ah = st["m"][i] * (1 - f) + st["m"][i + 1] * f
        return m_ah, r_ah

    def _monitor(self, st, st_new, j):
        """Контроль связей C1, C2, определения m и сэндвич-согласованности."""
        dv = self.dv
        # C1: c_vs = (r_uu + (kappa/2) r s^2) / (2 r_u)
        p_uu = self._d_dx(st_new["p"])
        c_vs = (p_uu + 0.5 * KAPPA * st_new["r"] * st_new["s"] ** 2) / (2.0 * st_new["p"])
        c1_res = np.abs(st_new["c"] - c_vs)
        # C2 (сэндвич): q_sandwich = 2(r_new - r)/dv - q
        q_sw = 2.0 * (st_new["r"] - st["r"]) / dv - st["q"]
        c2_res = np.abs(st_new["q"] - q_sw)
        # определение m: m_def = (r/2)(1 + 4 p q / alpha^2)
        m_def = 0.5 * st_new["r"] * (1.0 + 4.0 * st_new["p"] * st_new["q"] / st_new["alpha2"])
        m_res = np.abs(st_new["m"] - m_def)
        # сэндвич t
        t_sw = 2.0 * (st_new["Phi"] - st["Phi"]) / dv - st["t"]
        t_res = np.abs(st_new["t"] - t_sw)
        # запись максимума (вне центра, где |r| > 5 du)
        mask = np.abs(st_new["r"]) > 5.0 * self.du
        if mask.any():
            self.diag.c1_max = max(self.diag.c1_max, float(c1_res[mask].max()))
            self.diag.c2_max = max(self.diag.c2_max, float(c2_res[mask].max()))
            self.diag.mdef_max = max(self.diag.mdef_max, float(m_res[mask].max()))
            self.diag.sandwich_q_max = max(self.diag.sandwich_q_max, float(c2_res[mask].max()))
            self.diag.sandwich_t_max = max(self.diag.sandwich_t_max, float(t_res[mask].max()))
        self.diag.history.append({
            "j": j, "v": float(self.v[j]),
            "c1": float(c1_res[mask].max()) if mask.any() else 0.0,
            "c2": float(c2_res[mask].max()) if mask.any() else 0.0,
            "mdef": float(m_res[mask].max()) if mask.any() else 0.0,
            "phi_max": float(np.abs(st_new["Phi"]).max()),
            "r_min": float(st_new["r"].min()),
        })

    def print_summary(self):
        d = self.diag
        print(f"  [solver] v_final = {self.v_final:.4f}, время {self.runtime:.1f} c, "
              f"остановка: {d.stopped_reason}")
        print(f"  [solver] AH: {'найден' if d.ah_found else 'нет'}, "
              f"M_AH = {d.m_ah:.6e}, r_AH = {d.r_ah:.6e}")
        print(f"  [solver] связи: C1 max = {d.c1_max:.2e}, C2 max = {d.c2_max:.2e}, "
              f"|m - m_def| max = {d.mdef_max:.2e}")


# ------------------------------------------------------------------------------
# Самопроверка: эволюция плоского пространства должна оставаться плоским
# ------------------------------------------------------------------------------
def flat_space_test(n=200, verbose=True):
    """Тест 1: без импульса эволюция должна оставаться плоской (Minkowski)."""
    data = GaussianPulseData(A=0.0, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(-1.0, 1.05), v_range=(0.0, 1.0))
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    err_r = np.max(np.abs(sol.r - (sol.v_final - sol.u) / 2.0))
    err_Phi = np.max(np.abs(sol.Phi))
    err_a2 = np.max(np.abs(sol.alpha2 - 1.0))
    if verbose:
        print(f"[flat test] N = {n}: max|r - r_flat| = {err_r:.2e}, "
              f"max|Phi| = {err_Phi:.2e}, max|alpha^2 - 1| = {err_a2:.2e}")
    return err_r, err_Phi, err_a2


if __name__ == "__main__":
    print("=" * 70)
    print("САМОПРОВЕРКА СОЛВЕРА: плоское пространство (A = 0)")
    print("=" * 70)
    for n in (200, 400):
        flat_space_test(n)
