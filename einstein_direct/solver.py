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
        # --- v3: регулярное замыкание центра ------------------------------
        # Регулярное разложение у центра (u=v, r~0):
        #   Phi = Phi0(y) + a(y) x^2 + ...,  x = (v-u)/2 ~ r,
        #   t = Phi_v = t0 + a x + O(x^3),  s = Phi_u = t0 - a x + O(x^3),
        #   т.е. чётная часть E = (t+s)/2 = t0 + O(x^2), нечётная O = (t-s)/2 = a x:
        #   СВЯЗКА НАКЛОНОВ s1 - t1 = -2a (клэмп t=s насильно ставит a=0 и
        #   при быстром сжатии взрывается: s_v = -(pt+qs)/r ~ 2 c' s / r).
        #   Паразитная однородная мода марша t: t_hom ~ C/r (1/r к центру) —
        #   отделяется от регулярной a*r двухпараметрическим фитом
        #   O(r) = a r + C/r на кольце и ОТБРАСЫВАЕТСЯ.
        self.center_closure = "clamp"   # "clamp" (v2) | "regular" (v3) | "taylor" (v5)
        self.reg_zone_du = 8.0          # радиус зоны реконструкции, клеток du
        self.reg_annulus = 4.0          # кольцо фита: [R_zone, reg_annulus*R_zone]
        self.reg_m_rebuild = False      # перестройка m ~ r^3 в зоне (зум-стадии)
        self.reg_pq_project = False     # проекция чётных частей (p+q), (c+d)
        # сеточный пол для r в знаменателях (защита от деления на r~0:
        # эволюционный m в центральной клетке не согласован с r ~ 1e-14,
        # что давало всплески w = a2 m / (2 r_safe^3) ~ 1e20 и взрыв d)
        self.r_floor = 0.5 * self.du
        # --- v5: центральный Тейлор-патч (closure="taylor") -----------------
        # Машино-выведенная иерархия центра (sympy_center.py, верифицирована):
        #   (O1) t0' = 3 P2 - 2 (R1'/R1) t0 = 3 P2 - 4 d0 t0
        #   (O2) R1' = 2 d0 R1
        #   (O3) d0' = M3/R1 + W2 - kappa t0^2
        #   калибровка регулярности: (1-chi^2) R1^2 = alpha2(0)
        # Коэффициенты (t0, R1, d0) ЭВОЛЮЦИОНИРУЮТ как внутреннее ГУ (Чоптюк
        # 1993), P2/E2/W2/M3/R3/x*/chi измеряются фитом на чистом кольце;
        # зона |r| <= R_zone пересобирается ИЗ РЯДА Тейлора (без клэмпа и
        # без чётного усреднения сырого центра).
        self._tay = None                # состояние патча (ленивая инициализация)
        self.tay_relax = 0.5            # релаксация t0/d0 к фит-значению
        self.tay_verbose = False
        # A/B-флаги блоков патча (бисекция C1-всплеска)
        self.tay_do_ts = True           # (a) пересборка t,s из E/O
        self.tay_do_m = True            # (b) пересборка m = M3 xi^3
        self.tay_do_pq = True           # (c) проекция чётной части (p+q)
        self.tay_do_pq_series = True    # (v6) серийная пересборка p,q, k=1..K
        #     (точная компенсация pt=-qs для перемарша t; i0 НЕ трогается —
        #     анти-петля v5: p(i0) через R1; урок про C1 относится к полной
        #     пересборке ВСЕЙ строки — здесь только зона с тейпером)
        # --- v6: кольцевая чётность (annulus parity projection) ------------
        # Проекция зеркальной чётности + гашение аномальных мод (C/xi в O,
        # M1*xi в m) ВНЕ тейлор-зоны. Стена v5 (диагностика кампании):
        # зеркало-чётность сырого марша ломается СНАРУЖИ зоны
        # (m_mirror=-12.7 vs m_phys=+4.2 при |r|~100du).
        self.annulus_parity = False     # включается зум-машиной v6
        self.ann_factor = 10.0          # R_ann = ann_factor * R_zone
        self.ann_do_pq = True           # проекция (p+q)/(p-q) в кольце
        self.ann_do_cd = True           # проекция (c+d)/(d-c) в кольце
        self.ann_do_cpar = True         # гашение C/xi-моды в O = (t-s)/2
        self.ann_do_m1 = True           # гашение 1/r-моды массы (M1*xi)
        # v6.1: гейт G/D-проекций кольца в единицах локального масштаба поля.
        # 0.5 (v6) — консервативно; трассировка eps=1e-3 показала: сырой марш
        # t дрейфует (t_out -> 0 при s_out ~ 1), чётный мусор D = t-s достигает
        # O(1) = локального масштаба, гейт 0.5 его НЕ пускает -> компаундинг ->
        # взрыв t_out (0.001 -> 3.18 -> 1.3e3) и смерть стадии на j=11-12.
        # 2.5 (агрессивный режим зум-машины) пускает O(1)-проекцию: t,s
        # переслаживаются к зеркально-согласованной паре на первой же строке,
        # дальше правки малы и гейт снова в консервативном диапазоне.
        self.ann_relax_gate = 0.5
        # v6.1: CROSS-режим кольца: t := mirror(s) — точное CSS-соотношение
        # t(xi) = s(-xi) (s не трогается — эволюционируемое поле, источник
        # истины). Устраняет БИТВУ марша (t сжимается к 0 снаружи зоны) и
        # проекции (тянет t к O(1)): обе правки действуют только на t,
        # G/D-чётности выполняются точно, C/xi-мода марша заменяется.
        self.ann_cross = False
        self._ann_hist = []             # диагностика кольца (cap 256)
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
            # v6: сглаживание краевой колонки r перед ВТОРОЙ производной.
            # Интерполяция даёт пилу d r ~ 0.3 du на границе домена ->
            # r_vv ~ +-2.7e3 (физически O(1-30)), а при шумном q0 ~ 0.003
            # d_edge взрывается как 6.6e5 (трассировка v6 — главный источник
            # c,d-каскада на рестарт-строках). Биномиальный фильтр 9 точек.
            r_col = np.asarray(self._edge_r_arr, dtype=float)
            kern = np.array([1., 8., 28., 56., 70., 56., 28., 8., 1.]) / 256.0
            pad = 4
            r_pad = np.concatenate([np.full(pad, r_col[0]), r_col,
                                    np.full(pad, r_col[-1])])
            r_sm = np.convolve(r_pad, kern, mode="same")[pad:-pad]
            r_vv = (r_sm[jr + 1] - 2.0 * r_sm[jr] + r_sm[jr - 1]) / self.dv ** 2
        elif hasattr(self.data, "edge_r_vv"):
            r_vv = float(self.data.edge_r_vv(self.u[0], np.array([v_new]))[0])
        else:
            r_vv = 0.0
        # v6: q0-guard — при пиле q0 ~ 0.003 делим на шум; берём локальную
        # медиану q по первым клеткам (краевое замыкание — численная гигиена)
        q_loc = float(np.median(np.abs(st["q"][0:5])))
        q_use = st["q"][0] if abs(st["q"][0]) > 0.2 * max(q_loc, 1e-12) \
            else (st["q"][1] if abs(st["q"][1]) > 1e-12 else q_loc)
        d_edge_raw = (r_vv + 0.5 * KAPPA * st["r"][0] * st["t"][0] ** 2) / (2.0 * q_use)
        # v6.1: ФИЗИЧЕСКИЙ КАП d_edge (канал j=19-20, трассировка eps=1e-3).
        # d_edge = omega_v на краю — вторая производная интерполированной
        # краевой колонки r(v): усиление шума ~ 1/dv^2 = 3e8 на глубокой
        # стадии. Мусор d_edge ~ -1e4..-1e6 действует на q[0] как q' = 2dq
        # (|2 dv d| > 1 уже при d ~ -6e3): q краевой колонки осциллирует
        # через ноль -> q_use -> 0 -> d_edge ещё больше — ПОЛОЖИТЕЛЬНАЯ
        # обратная связь (трассировка: q0: 0.53 -> 0.14 -> 0.0024 -> -0.23 ->
        # +2.68 при d_edge: -6e3 -> -9e5), d-колонка -2.3e5, alpha2_v = 2a2 d
        # флипает знак a2 за одну строку — смерть стадии на j=11.
        # Физический масштаб omega_v на краю O(1-30); кап 1e3 касается
        # только мусора и размыкает петлю.
        cap_edge = 1.0e3
        if np.isfinite(d_edge_raw) and abs(d_edge_raw) > cap_edge:
            self._d_edge_clipped = getattr(self, "_d_edge_clipped", 0) + 1
            d_edge_raw = float(np.sign(d_edge_raw)) * cap_edge
        return d_edge_raw

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

    def _center_regular(self, t_arr, s_arr, m_arr, r_arr,
                        p_arr=None, q_arr=None, c_arr=None, d_arr=None):
        """v3.1: регулярная реконструкция центральной зоны (каждая строка).

        Зона |r| <= R_zone, R_zone = max(reg_zone_du*du, 1.2*R_heal).
        Шаги:
          1. Чётная часть E(r_k) = 0.25[(t+s)(-r_k) + (t+s)(+r_k)] — парное
             усреднение ПОЛОВИННЫХ сумм (убивает нечётный мусор марша,
             включая 1/r-моду, и сохраняет вариацию E(r) ~ t0 + E2 r^2).
          2. Нечётная часть: фит O(r) = (t-s)/2 = a r + C/r по физической
             стороне (r > 0) на кольце [R_zone, reg_annulus*R_zone];
             регулярная часть a*r оставляется, паразитная C/r отбрасывается.
             (Гарантирует связку наклонов s1-t1 = -2a вместо a=0.)
          3. Пересборка зоны С ГЛАДКИМ ТЕЙПЕРОМ w(k) = (1-(k/K)^2)^2:
             y <- y + w * (y_reg - y) — нулевая производная на краю зоны,
             НЕТ разрыва y/y_reg (иначе край зоны сам становится источником
             мусора — так v3.0 дала цепочку КОРОЧЕ v2).
          4. Масса: m3 согласована С КРАЕМ зоны (m3 = <m/r^3> на k=K+1..K+3,
             вне родительской мусорной зоны) — непрерывность m на краю;
             кубический закон убивает постоянную добавку dm (именно она даёт
             2m/r ~ 2dm/r -> взрыв у центра).
        """
        R_zone = max(self.reg_zone_du * self.du,
                     1.2 * float(getattr(self, "R_heal", 0.0)))
        r_abs = np.abs(r_arr)
        i0 = int(np.argmin(r_abs))
        if r_abs[i0] > 3.0 * self.du:
            return  # центр вне окна
        n = len(r_arr)
        K = int(round(R_zone / self.du))
        K = min(K, i0 - 3, n - 4 - i0)   # кольцо m3: k = K+1..K+3 должно существовать
        if K < 1:
            return
        # --- (2) фит нечётной части на кольце (физическая сторона r>0) ---
        lo, hi = R_zone, self.reg_annulus * R_zone
        idx = np.where((r_arr > lo) & (r_arr <= hi) & (np.arange(n) <= i0))[0]
        a = 0.0
        if idx.size >= 4:
            rr = r_arr[idx]
            O = 0.5 * (t_arr[idx] - s_arr[idx])
            ok = np.isfinite(rr) & np.isfinite(O) & (rr > 0)
            if int(ok.sum()) >= 4:
                rr, O = rr[ok], O[ok]
                Amat = np.stack([rr, 1.0 / rr], axis=1)
                coef, *_ = np.linalg.lstsq(Amat, O, rcond=None)
                if np.isfinite(coef[0]) and np.isfinite(coef[1]):
                    a, C = float(coef[0]), float(coef[1])
                    # --- guards (v3.2): фит не должен впрыскивать мусор -----
                    resid = O - (a * rr + C / rr)
                    rel_res = float(np.max(np.abs(resid)) /
                                    max(float(np.max(np.abs(O))), 1e-30))
                    # (i) большие остатки -> кольцо не описывается a r + C/r
                    if rel_res > 0.30:
                        a = 0.0
                    # (ii) 1/r-мода доминирует на краю зоны -> a ненадёжен
                    elif abs(C) > abs(a) * R_zone**2:
                        a = 0.0
        # --- (1)+(3) пересборка зоны с тейпером (векторно, k = 0..K) ------
        ks = np.arange(0, K + 1)
        ip = i0 - ks          # физическая сторона (r > 0)
        im = i0 + ks          # зеркало (r < 0)
        Gp = t_arr[ip] + s_arr[ip]
        Gm = t_arr[im] + s_arr[im]
        fin_p, fin_m = np.isfinite(Gp), np.isfinite(Gm)
        E = np.where(fin_p & fin_m, 0.25 * (Gp + Gm),
                     np.where(fin_p, 0.5 * Gp,
                              np.where(fin_m, 0.5 * Gm, 0.0)))
        rp, rm = r_arr[ip], r_arr[im]
        tp_reg = E + a * rp
        sp_reg = E - a * rp
        tm_reg = E + a * rm
        sm_reg = E - a * rm
        w = (1.0 - (ks / float(K)) ** 2) ** 2   # тейпер: 1 в центре, 0 на краю
        t_arr[ip] += w * (tp_reg - t_arr[ip])
        s_arr[ip] += w * (sp_reg - s_arr[ip])
        t_arr[im] += w * (tm_reg - t_arr[im])
        s_arr[im] += w * (sm_reg - s_arr[im])
        # --- (4) масса: кубический закон, m3 согласован с краем зоны ------
        if self.reg_m_rebuild:
            km = np.arange(K + 1, K + 4)
            ipm, imm = i0 - km, i0 + km
            cand = np.concatenate([m_arr[ipm] / r_arr[ipm] ** 3,
                                   m_arr[imm] / r_arr[imm] ** 3])
            cand = cand[np.isfinite(cand)]
            if cand.size >= 2:
                m3 = float(np.median(cand))
                m_arr[ip] += w * (m3 * rp ** 3 - m_arr[ip])
                m_arr[im] += w * (m3 * rm ** 3 - m_arr[im])
        # --- (5) проекции чётных частей p+q и c+d (регулярность) ----------
        # Зеркальный анализ (u,v)->(v,u): r -> -r, p <-> -q, s <-> t, c <-> d:
        #   p+q НЕЧЁТЕН (регулярно O(x^3), (p+q)(0)=0), чётная добавка δ —
        #   паразит: даёт источник s_v ⊃ E·δ/r (1/r-связка, взрыв E в зоне);
        #   c+d ЧЁТЕН с (c+d)(0) = c(0)+d(0) = 0: убираем только центр. значение.
        if self.reg_pq_project:
            Sp = p_arr[ip] + q_arr[ip]
            Sm = p_arr[im] + q_arr[im]
            e_pq = 0.5 * (Sp + Sm)          # чётная часть (вся — паразитная)
            p_arr[ip] -= w * 0.5 * e_pq
            q_arr[ip] -= w * 0.5 * e_pq
            p_arr[im] -= w * 0.5 * e_pq
            q_arr[im] -= w * 0.5 * e_pq
            Sc = c_arr[ip] + d_arr[ip]
            Smc = c_arr[im] + d_arr[im]
            e_cd = 0.5 * (Sc + Smc)         # чётная часть c+d
            e0 = float(e_cd[0])             # (c+d)(0) — обязано быть 0
            c_arr[ip] -= w * 0.5 * e0
            d_arr[ip] -= w * 0.5 * e0
            c_arr[im] -= w * 0.5 * e0
            d_arr[im] -= w * 0.5 * e0

    # ------------------------------------------------------------------
    def _center_taylor(self, t_arr, st, v_new):
        """v5: ЦЕНТРАЛЬНЫЙ ТЕЙЛОР-ПАТЧ (подход Чоптюка 1993).

        Коэффициенты регулярного разложения у центра ЭВОЛЮЦИОНИРУЮТ по
        машино-выведенным ОДУ (sympy_center.py, все формы верифицированы):
            (O1) t0' = 3 P2 - 4 d0 t0          [SC, порядок xi^0]
            (O2) R1' = 2 d0 R1                 [C2/C1, порядок xi^0]
            (O3) d0' = M3/R1 + W2 - kappa t0^2 [TH, порядок xi^0]
        и служат ВНУТРЕННИМ ГУ; зона |r| <= R_zone пересобирается из ряда:
            E(xi) = t0 + E2 xi^2 + E4 xi^4        (чётная, скалярная часть)
            O(xi) = P2 xi + P4o xi^3              (нечётная, СПИНОРНАЯ часть)
            t = E + O,  s = E - O,  r = R1 xi + R3 xi^3,
            p = -(1+chi) R1/2 + (R1'/2) xi - (3(1+chi)/2) R3 xi^2,
            q = +(1-chi) R1/2 + (R1'/2) xi + (3(1-chi)/2) R3 xi^2,
            m = M3 xi^3,
        где xi = x - x*(v), x = (v-u)/2, chi = dx*/dy (дрейф центра).
        P2, E2, E4, W2, M3, R3, x* измеряются фитами на чистом кольце
        [R_zone, 4 R_zone] (как в v3.2), чётная паразита (p+q) в зоне
        уничтожается проекцией (источник взрыва E: E_v = -(p+q)E/r).

        Отличие от v3.2 "regular": E(0) = t0 — эволюционирующая величина,
        а не шумное парное среднее сырого центра; зона — точный ряд, а не
        тейперная смесь; (p+q) — точная проекция с учётом смещения x*.
        При отказе фит-ов — откат к v3.2 "regular" на этой строке.
        """
        du = self.du
        r_arr = st["r"]; s_arr = st["s"]; p_arr = st["p"]; q_arr = st["q"]
        m_arr = st["m"]; a2_arr = st["alpha2"]; c_arr = st["c"]; d_arr = st["d"]
        u = self.u
        n = len(r_arr)
        x = (v_new - u) / 2.0
        r_abs = np.abs(r_arr)
        i0 = int(np.argmin(r_abs))
        if r_abs[i0] > 3.0 * du:
            return
        ring_lo = max(self.reg_zone_du * du, 1.2 * float(getattr(self, "R_heal", 0.0)))
        ring_hi = self.reg_annulus * ring_lo
        # ЗОНА В КЛЕТКАХ: xi = k*du/2 (x меняется на du/2 за клетку), поэтому
        # |xi| <= ring_lo соответствует k <= 2*ring_lo/du (фактор 2!).
        K = int(round(2.0 * ring_lo / du))
        # запас под краевое кольцо m3 (k = K+1..K+3 с ОБЕИХ сторон)
        K = min(K, i0 - 4, n - 5 - i0)
        if K < 4:
            return
        if self._tay is None:
            self._tay = {"init": False, "t0": 0.0, "R1": 1.0, "d0": 0.0,
                         "P2": 0.0, "x_prev": None, "v_prev": None,
                         "xstar_prev": None, "hist": [], "fallbacks": 0, "rows": 0}
        tay = self._tay
        tay["rows"] += 1
        early = tay["rows"] <= 6     # v6: рестарт-строки — фиты грязны

        # --- 1. фит r на кольце (физическая сторона): R1, x*, R3 ----------
        # v6.1: кольцо ОБЕ стороны (|r|): односторонний фит (маска r > ring_lo,
        # i <= i0) смещал интерсепт x* кубической волной кольца на ~10 du
        # (профиль стадии смерти: x* - x[i0] = 10.5 du) — все пары/проекции/
        # cross строились вокруг НЕВЕРНОЙ оси зеркала и инжектировали O(1).
        # Двусторонний фит: r(xi) нечётен — интерсепт якорится симметрией.
        ringm = (np.abs(r_arr) > ring_lo) & (np.abs(r_arr) < ring_hi)
        nr = int(ringm.sum())
        ok = nr >= 6
        R1 = R3 = x_star = chi = 0.0
        res_r = float("nan")
        if ok:
            xr = x[ringm]; rr = r_arr[ringm]
            A1 = np.stack([xr, np.ones_like(xr)], axis=1)
            c1, *_ = np.linalg.lstsq(A1, rr, rcond=None)
            if np.isfinite(c1).all() and abs(c1[0]) > 1e-8:
                x_star = float(-c1[1] / c1[0])
                xi_r = xr - x_star
                A2m = np.stack([xi_r, xi_r**3], axis=1)
                c2, *_ = np.linalg.lstsq(A2m, rr, rcond=None)
                R1, R3 = float(c2[0]), float(c2[1])
                res_r = float(np.max(np.abs(rr - A2m @ c2)) / max(np.max(np.abs(rr)), 1e-30))
                ok = np.isfinite(R1) and np.isfinite(R3) and R1 > 0.2 and res_r < 0.3
        # v6.1: гейт сходимости оси: центр сетки (argmin|r|) обязан совпадать
        # с фитованным x* в ~2 du, иначе пары/проекции вокруг неверной оси
        if ok and abs(x[i0] - x_star) > 2.5 * du:
            ok = False
        if not ok:
            tay["fallbacks"] += 1
            self._center_regular(t_arr, s_arr, m_arr, r_arr,
                                 p_arr=p_arr, q_arr=q_arr,
                                 c_arr=c_arr, d_arr=d_arr)
            return

        # --- 2. дрейф центра chi ------------------------------------------
        if tay["xstar_prev"] is not None and tay["v_prev"] is not None:
            u_star = v_new - 2.0 * x_star
            u_prev = tay["v_prev"] - 2.0 * tay["xstar_prev"]
            dvv = v_new - tay["v_prev"]
            duo = u_star - u_prev
            den = dvv + duo
            if abs(den) > 1e-14:
                chi = (dvv - duo) / den
            chi = float(np.clip(chi, -0.45, 0.45))
        tay["xstar_prev"] = x_star
        tay["v_prev"] = v_new

        # --- 3. парные фиты в зоне (k = 1..K, обе стороны, точные xi) -----
        ks = np.arange(1, K + 1)
        ip = i0 - ks
        im = i0 + ks
        xi_p = x[ip] - x_star
        xi_m = x[im] - x_star
        G = t_arr + s_arr          # = 2E + нечётный мусор
        D = t_arr - s_arr          # = 2O + чётный мусор
        E_pair = 0.25 * (G[ip] + G[im])          # чётная часть E(xi)
        O_pair = 0.25 * (D[ip] - D[im])          # нечётная часть O(xi)
        fin = np.isfinite(E_pair) & np.isfinite(O_pair) \
            & np.isfinite(xi_p) & np.isfinite(xi_m)
        if int(fin.sum()) < K // 2:
            tay["fallbacks"] += 1
            self._center_regular(t_arr, s_arr, m_arr, r_arr,
                                 p_arr=p_arr, q_arr=q_arr,
                                 c_arr=c_arr, d_arr=d_arr)
            return
        # чётный фит E = E0 + E2 xi^2 + E4 xi^4 (обе стороны, точные xi)
        xe = np.concatenate([xi_p[fin], xi_m[fin]])
        ye = np.concatenate([E_pair[fin], E_pair[fin]])
        AE = np.stack([np.ones_like(xe), xe**2, xe**4], axis=1)
        cE, *_ = np.linalg.lstsq(AE, ye, rcond=None)
        E0_free, E2, E4 = (float(v) for v in cE)
        res_E = float(np.max(np.abs(ye - AE @ cE)) / max(np.max(np.abs(ye)), 1e-30))
        # НЕРАЗРЫВНОСТЬ/САНИТАРНОСТЬ фитов (защита от впрыска мусора):
        # модель не должна превышать данные и должна их описывать
        def fit_ok(coef, Amat, ydat, max_boost=50.0, max_res=0.30):
            model = Amat @ coef
            res = float(np.max(np.abs(ydat - model)) / max(np.max(np.abs(ydat)), 1e-30))
            boost = float(np.max(np.abs(model)) / max(np.max(np.abs(ydat)), 1e-30))
            return bool(np.all(np.isfinite(coef)) and res < max_res
                        and boost < max_boost), res, boost
        e_ok, res_E, boost_E = fit_ok(cE, AE, ye)
        # v6.1: диагностика гейтов E-фита (канал P2=0/tau-строк)
        dbg_e = (float(boost_E), float(res_E))
        # нечётный фит O = P2 xi + P4o xi^3 + C/xi (паразитная 1/xi-мода)
        xo = np.concatenate([xi_p[fin], xi_m[fin]])
        yo = np.concatenate([O_pair[fin], -O_pair[fin]])
        AO = np.stack([xo, xo**3, 1.0 / np.where(np.abs(xo) > 1e-14, xo, 1e-14)], axis=1)
        cO, *_ = np.linalg.lstsq(AO, yo, rcond=None)
        P2, P4o, C_par = (float(v) for v in cO)
        o_ok, res_O, boost_O = fit_ok(cO, AO, yo)
        dbg_o = (float(boost_O), float(res_O))
        # v6: буст-гейт В ТОЧКАХ ЗОНЫ. Базис [xi, xi^3, xi^5, 1/xi] ил-обусло-
        # влен: на данных кольца модель с канселем P2*xi - C/xi хороша, но
        # ВНУТРИ зоны P2*xi взрывается (трассировка v6: P2=1.4e9 при данных
        # O~O(1) -> max|t| зоны 1e6 -> перемарш 8e8 -> смерть строки 1).
        # Физический масштаб: |O(xi_min)| <= O(max|E| + |t0|) у центра.
        xi_min_z = 0.5 * du
        o_zone_val = abs(P2) * xi_min_z + abs(P4o) * xi_min_z ** 3
        o_zone_scale = max(float(np.max(np.abs(E_pair[fin])))
                           + abs(tay.get("t0", 0.0)), 1e-30)
        dbg_zone = (float(o_zone_val), float(o_zone_scale))
        if o_ok and o_zone_val > 50.0 * o_zone_scale:
            o_ok = False
            dbg_o = dbg_o + ("zone_boost",)
        if not (e_ok and o_ok):
            # фиты зоны не описывают данные (рестарт-строка/мусор):
            # НЕ пересобираем t,s из ряда — только точный центр t=s=t0;
            # P2 для ОДУ не обновляем мусором
            if not o_ok:
                P2 = tay.get("P2", 0.0)
                P4o = 0.0
                C_par = float("nan")
            E2 = E4 = 0.0
            res_E = res_O = float("nan")
        # (c+d): чётная часть -> d0; (d-c): нечётная -> W2
        cd = c_arr + d_arr
        dc = d_arr - c_arr
        yc = np.concatenate([cd[ip[fin]], cd[im[fin]]])
        AC = np.stack([np.ones_like(xe), xe, xe**2, xe**3], axis=1)
        cC, *_ = np.linalg.lstsq(AC, yc, rcond=None)
        d0_fit = float(0.5 * cC[0])
        yw = np.concatenate([dc[ip[fin]], -dc[im[fin]]])
        AW = np.stack([xo, xo**3], axis=1)
        cW, *_ = np.linalg.lstsq(AW, yw, rcond=None)
        W2 = float(cW[0])
        # v6: санитарность W2 (идёт в ОДУ O3 напрямую; мусорный W2 ~ 1e13
        # взрывает d0 и убивает строку — механика стены v5 на eps >= 1e-3):
        # (a) boost-гейт: модель W2*xi не должна превышать данные кольца;
        # (b) jump-гейт относительно предыдущего значения (естественный
        #     масштаб 1/ring_lo^2);
        W2_prev = tay.get("W2", 0.0)
        w_data = float(np.max(np.abs(yw))) if yw.size else 0.0
        W2_ok = np.isfinite(W2)
        if W2_ok and w_data > 0:
            W2_ok = abs(W2) * float(np.max(np.abs(xo))) <= 30.0 * w_data
        if W2_ok and np.isfinite(W2_prev) and abs(W2_prev) > 0:
            W2_ok = abs(W2) < 20.0 * max(
                abs(W2_prev), 1.0 / max(ring_lo, 1e-30) ** 2)
        if not W2_ok:
            W2 = W2_prev if np.isfinite(W2_prev) else 0.0
            tay["W2_gated"] = tay.get("W2_gated", 0) + 1
        # v6: башенный масштаб-гейт W2 (масштабно-свободная связь CSS:
        # W2/t0^2 -> 4/3; |W2| = O(10) t0^2 у CSS). ВАЖНО: БЕЗ d0 в cap —
        # петля самоподогрева W2-мусор -> d0 (ОДУ O3) -> свой cap (урок
        # трассировки v6). + O(1) пол: далёкие от CSS строки теряют член W2
        # в O3 — допустимо (d0' = M3/R1 - kappa t0^2 остаётся ограниченной).
        W2_cap = 10.0 * abs(tay.get("t0", 0.0)) ** 2 + 1.0
        if abs(W2) > W2_cap:
            W2 = W2_prev if np.isfinite(W2_prev) and abs(W2_prev) <= W2_cap else 0.0
            tay["W2_gated"] = tay.get("W2_gated", 0) + 1
        # M3: фит m/xi^3 = M3 + M5 xi^2 на кольце [ring_lo, 2 ring_lo]
        ring_m3 = (r_arr > ring_lo) & (r_arr < 2.0 * ring_lo) & (np.arange(n) <= i0)
        M3 = 0.0
        if int(ring_m3.sum()) >= 4:
            xm3 = x[ring_m3] - x_star
            ym3 = m_arr[ring_m3] / np.where(np.abs(xm3) > 1e-14, xm3, 1e-14)**3
            finm = np.isfinite(ym3) & (ym3 > -1e6) & (ym3 < 1e6)
            if int(finm.sum()) >= 4:
                AM3 = np.stack([np.ones_like(xm3[finm]), xm3[finm]**2], axis=1)
                cM, *_ = np.linalg.lstsq(AM3, ym3[finm], rcond=None)
                M3_cand = float(cM[0])
                # санитарность: m на краю зоны после пересборки не должна
                # превышать сырую массу кольца (иначе мусорный M3 ядовит)
                m_ring_max = float(np.max(np.abs(m_arr[ring_m3])))
                if (np.isfinite(M3_cand)
                        and abs(M3_cand) * ring_lo**3 < 10.0 * max(m_ring_max, 1e-30)):
                    # v6: ЧИСТО башенный гейт M3 — торновская связка
                    # M3 = 2 R1 t0^2 / (3 (1-chi)^2), машино-верифицирована
                    # как ТОЖДЕСТВО при каждой y (center_modes [I]);
                    # M3 ~ 1e16 при t0 ~ O(1) невозможна. Гейт 50x покрывает
                    # сеточную систематику фитов (ratio ~ 1.6 +- разброс).
                    M3_tower = 2.0 * abs(R1) * tay.get("t0", 0.0) ** 2 / 3.0
                    M3_prev = tay.get("M3_prev", 0.0)
                    if abs(M3_cand) <= 50.0 * max(M3_tower, 1e-300):
                        M3 = M3_cand
                        tay["M3_prev"] = M3_cand
                    elif (np.isfinite(M3_prev)
                          and abs(M3_prev) <= 50.0 * max(M3_tower, 1e-300)):
                        M3 = M3_prev          # держим предыдущее валидное
                        tay["M3_gated"] = tay.get("M3_gated", 0) + 1
                    else:
                        M3 = 0.0              # не rebuild'им m этим M3
                        tay["M3_gated"] = tay.get("M3_gated", 0) + 1

        # --- 4. эволюция коэффициентов (ОДУ O1-O3, релаксация) -------------
        # dv_ode считается ДО обновления v_prev (иначе всегда 0)
        dv_ode = (v_new - tay["v_prev"]) if (tay["v_prev"] is not None
                                             and tay["init"]) else self.dv
        # v6: ЭНФОРСМЕНТ торновской связки: M3 = 2 R1 t0^2 / (3(1-chi)^2) —
        # машино-верифицированная ТОЖДЕСТВЕННОСТЬ при каждой y (center_modes
        # [I]). Сырой m у центра junk-доминирован 1/r-модой (M1/xi^2 >> M3),
        # фит M3 невозможен -> используем связку КАК ЗНАЧЕНИЕ (первые
        # принципы, без подгонки: t0, R1, chi — измеренные величины).
        # Edge-медиана остаётся только диагностикой качества центра.
        M3_tower = 2.0 * R1 * (tay["t0"] ** 2) \
            / (3.0 * max(1.0 - chi * chi, 0.25))
        tay["M3tw"] = M3_tower
        tay["chi_fit"] = chi
        tay["M3_prev"] = M3_tower
        M3_fit_diag = M3
        M3 = M3_tower
        if not tay["init"]:
            tay["init"] = True
            scale_e0 = max(float(np.max(np.abs(E_pair))), 1e-30)
            tay["t0"] = E0_free if abs(E0_free) < 1e2 * scale_e0 else 0.0
            scale_cd0 = max(float(np.max(np.abs(yc))), 1e-30)
            tay["d0"] = d0_fit if abs(d0_fit) < 1e2 * scale_cd0 else 0.0
            tay["R1"] = R1
        else:
            # санитарные масштабы данных строки (абсолютная защита от скачков)
            scale_e = max(float(np.max(np.abs(E_pair[fin]))), 1e-30)
            scale_cd = max(float(np.max(np.abs(yc))), 1e-30)
            # O1: t0' = 3 P2_prev - 4 d0 t0 (предиктор) + релаксация к E0_free
            t0_pred = tay["t0"] + dv_ode * (3.0 * tay["P2"] - 4.0 * tay["d0"] * tay["t0"])
            jump = abs(E0_free - t0_pred)
            scale = max(abs(t0_pred), abs(E0_free), 1e-12)
            # v6: E(0) не может превышать данные кольца в ~5 раз (мягкая
            # экстраполяция xi->0); прежний гейт 100x пропускал E0_free=13.4
            # при данных 0.5 (трассировка v6) -> t0-junk -> q/r-каскад стадии 2
            e_sane = (abs(E0_free) < 5.0 * (scale_e + abs(tay["t0"]))) \
                and (abs(E0_free) < 1e2 * (abs(t0_pred) + scale_e))
            if np.isfinite(E0_free) and e_sane and jump < 0.75 * scale:
                t0_relax = t0_pred + self.tay_relax * (E0_free - t0_pred)
                # v6.1: темповой кап t0: у CSS t0 ~ e^z растает ~1.5%/строку
                # (z += 1 за ~эхо ~ 45 строк); удвоение за строку — мусор
                # (трассировка: t0 x2/строку через E0_free-релаксацию)
                t0_rate = 1.5 * abs(tay["t0"]) + 0.2 * scale_e + 1e-300
                if abs(t0_relax - tay["t0"]) > t0_rate:
                    t0_relax = tay["t0"] \
                        + np.sign(t0_relax - tay["t0"]) * t0_rate
                tay["t0"] = t0_relax
            elif (np.isfinite(t0_pred)
                  and abs(t0_pred - tay["t0"]) < 10.0 * (abs(tay["t0"]) + scale)):
                tay["t0"] = t0_pred
            # иначе: t0 заморожена (мусорная строка — не впрыскиваем предиктор)
            # O2: R1' = 2 d0 R1 — R1 хранится как ДИАГНОСТИКА (фит),
            # ОБРАТНОЙ ЗАПИСИ p(i0) через R1 НЕТ (петля обратной связи:
            # фит искажённого патчем r-профиля -> p(i0) -> новый перекос r)
            tay["R1"] = R1
            # O3: d0' = M3/R1 + W2 - kappa t0^2 (M3 — торновская связка)
            d0_pred = tay["d0"] + dv_ode * (M3 / R1 + W2 - KAPPA * tay["t0"] ** 2)
            # v6: башенный масштаб d0 (d0/t0 = D0/T0 -> 0 у CSS; d0 ~ O(t0)
            # вдали): предиктор выше 20*|t0|+1 — мусор ОДУ. БЕЗ |d0| в cap —
            # самоподогрев (урок трассировки v6)
            d0_cap = 20.0 * abs(tay["t0"]) + 1.0
            if abs(d0_pred) > d0_cap:
                d0_pred = np.sign(d0_pred) * d0_cap if np.isfinite(d0_pred) else 0.0
                tay["d0_capped"] = tay.get("d0_capped", 0) + 1
            jump_d = abs(d0_fit - d0_pred)
            scale_d = max(abs(d0_pred), abs(d0_fit), 1e-12)
            d_sane = abs(d0_fit) < 1e2 * (abs(d0_pred) + scale_cd)
            if np.isfinite(d0_fit) and d_sane and jump_d < 0.75 * scale_d:
                tay["d0"] = d0_pred + self.tay_relax * (d0_fit - d0_pred)
            elif (np.isfinite(d0_pred)
                  and abs(d0_pred - tay["d0"]) < 10.0 * (abs(tay["d0"]) + scale_d)):
                tay["d0"] = d0_pred
            # иначе: d0 заморожена (мусорная строка)
        tay["P2"] = P2 if (o_ok or not early) else tay["P2"]
        # v6.1: early-accept — успешный фит рестарт-строки (свежая
        # интерполяция, ЛУЧШИЕ данные стадии) раньше отбрасывался правилом
        # early (tay_rows <= 6) -> реле P2=0 самозапиралось: перестройка
        # зоны с P2=0 гасила нечётную структуру -> следующие фиты видели
        # плоскость (res_O ~ 1.0) -> P2=0 навсегда -> ноль tau-строк.
        # Теперь гейты (res/boost/zone-boost) сами решают годность фита.
        tay["W2"] = W2
        tay["v_prev"] = v_new
        tay["xstar_prev"] = x_star
        t0 = tay["t0"]
        d0 = tay["d0"]
        R1p = 2.0 * d0 * R1                       # O2: R1' = 2 d0 R1
        M3_series = (R1p ** 2 - 6.0 * R1 * R3) / (2.0 * R1) + R1 * W2

        # --- 5. пересборка зоны (v5-минимум, объём v3.2 + upgrades) --------
        # (a) t, s: чётная часть E — парные средние k=1..K (полная структура,
        #     без экстраполяционной ошибки фита -> C1 не ломается); в центре
        #     E(0) = t0 — ЭВОЛЮЦИОНИРУЮЩАЯ величина (ОДУ O1), а не шумное
        #     парное среднее сырого центра (главное отличие от v3.2);
        #     нечётная часть O = P2 xi + P4o xi^3 — точный ряд (C/xi-мода
        #     отделяется фитoм и ОТБРАСЫВАЕТСЯ);
        # (b) m = M3 xi^3, M3 — медиана m/xi^3 на краевом кольце (v3.2);
        # (c) чётная паразита (p+q) — источник взрыва E-моды — проекция с
        #     учётом смещения x* (иначе вбрасывается константа R1' * delta);
        # (d) p, q, r, a2 НЕ трогаются (кроме точки i0 для c, d) — сырой
        #     марш держит дискретную C1 (полная пересборка ряда p,q даёт
        #     C1 1e-8 -> 0.5 — проверено).
        do_m_row = True
        # v6.1: гейт ПЕРЕСТРОЙКИ — при отказе фитов (мусорные пары) зона
        # НЕ пересобирается из сырых парных средних (раньше E_zone считался
        # безусловно и инжектировал мусор в зону даже при проваленных
        # гейтах — канал смерти j=53-55, cross-пробник eps=1e-3). Зона
        # держит предыдущую серию, центр — t=s=t0. Плюс темповой гейт:
        # E0_free (экстраполяция данных зоны к xi=0) физически ~ t0;
        # рост E0_free вдвое за строку — петля положительной обратной
        # связи перестройки (t0: 0.065 -> 35 за 8 строк) — блокируется.
        scale_e_row = max(float(np.max(np.abs(E_pair[fin]))), 1e-30)
        do_ts_row = bool(
            e_ok and o_ok
            and abs(E0_free) < 3.0 * (abs(tay.get("t0", 0.0)) + scale_e_row))
        ks_all = np.arange(0, K + 1)
        ipa = i0 - ks_all
        ima = i0 + ks_all
        xia = x[ipa] - x_star
        xib = x[ima] - x_star
        gamma = (1.0 - (ks_all / float(K)) ** 2) ** 2   # гладкий тейпер v3.2:
        # нулевая производная на краю зоны; ступенчатый гамма-рамп (0.5/0)
        # даёт corr/du ~ O(0.1) в p_u -> всплеск C1 (проверено)
        O_of = lambda xq: P2 * xq + P4o * xq**3
        E_zone = 0.25 * ((t_arr[ipa] + s_arr[ipa]) + (t_arr[ima] + s_arr[ima]))
        E_zone[0] = t0                            # якорь ОДУ O1
        # v6: на ранних строках стадии пересборки t,s/p,q НЕ делаем (фиты
        # кольца на рестарт-строках грязны: P2-фит дал 1.4e9 на чистых
        # данных из-за канселя с 1/xi; вторая итерация корректора усиливает
        # свой же мусор). Центр держится t=s=t0, c=d=d0; P2 — из реле.
        if self.tay_do_ts and not early and do_ts_row:
            for idx, xq, Ez in ((ipa, xia, E_zone), (ima, xib, E_zone)):
                t_ser = Ez + O_of(xq)
                s_ser = Ez - O_of(xq)
                t_arr[idx] += gamma * (t_ser - t_arr[idx])
                s_arr[idx] += gamma * (s_ser - s_arr[idx])
        # (a2) v6: серийная пересборка p,q в зоне (k=1..K, тейпер gamma[1:],
        # точка i0 НЕ трогается). Анзац верифицирован sympy_center.py:
        #   p = -(1+chi)R1/2 + (R1'/2)xi - (3(1+chi)/2)R3 xi^2
        #   q = +(1-chi)R1/2 + (R1'/2)xi + (3(1-chi)/2)R3 xi^2
        # Это даёт точную компенсацию pt+qs -> O(xi) у центра (источник SC
        # регулярен), необходимую перемаршу t; C1 на краю зоны держится
        # тейпером (нулевой наклон на краю).
        if self.tay_do_pq_series and not early and do_ts_row:
            R1p_s = 2.0 * d0 * R1
            p_ser_a = (-(1.0 + chi) * 0.5 * R1 + 0.5 * R1p_s * xia
                       - 1.5 * (1.0 + chi) * R3 * xia ** 2)
            q_ser_a = ((1.0 - chi) * 0.5 * R1 + 0.5 * R1p_s * xia
                       + 1.5 * (1.0 - chi) * R3 * xia ** 2)
            p_ser_b = (-(1.0 + chi) * 0.5 * R1 + 0.5 * R1p_s * xib
                       - 1.5 * (1.0 + chi) * R3 * xib ** 2)
            q_ser_b = ((1.0 - chi) * 0.5 * R1 + 0.5 * R1p_s * xib
                       + 1.5 * (1.0 - chi) * R3 * xib ** 2)
            p_arr[ipa[1:]] += gamma[1:] * (p_ser_a[1:] - p_arr[ipa[1:]])
            q_arr[ipa[1:]] += gamma[1:] * (q_ser_a[1:] - q_arr[ipa[1:]])
            p_arr[ima[1:]] += gamma[1:] * (p_ser_b[1:] - p_arr[ima[1:]])
            q_arr[ima[1:]] += gamma[1:] * (q_ser_b[1:] - q_arr[ima[1:]])
        # (b) масса: m = M3 xi^3 (краевое кольцо), с тейпером
        ks_e = np.arange(K + 1, K + 4)
        ipm, imm = i0 - ks_e, i0 + ks_e
        cand = np.concatenate([m_arr[ipm] / np.where(np.abs(r_arr[ipm]) > 1e-14,
                                                     r_arr[ipm], 1e-14) ** 3,
                               m_arr[imm] / np.where(np.abs(r_arr[imm]) > 1e-14,
                                                     r_arr[imm], 1e-14) ** 3])
        cand = cand[np.isfinite(cand)]
        M3 = float(np.median(cand)) if cand.size >= 2 else M3
        # v6: ФИНАЛЬНЫЙ башенный гейт M3 — edge-медиана НЕ доверяет (урок
        # смоука: мусорная m на краевом кольце давала M3 ~ 1e16 ПОСЛЕ
        # гейтованного фита, и она шла в rebuild m и ОДУ O3 -> каскад
        # d0 -> omega -> a2 -> 1e300). Гейт: |M3| <= 50 x 2R1 t0^2/3.
        M3_tower = 2.0 * abs(R1) * t0 ** 2 / 3.0
        if abs(M3) > 50.0 * max(M3_tower, 1e-300):
            tay["M3_gated"] = tay.get("M3_gated", 0) + 1
            M3_prev_v = tay.get("M3_prev", 0.0)
            if not (np.isfinite(M3_prev_v)
                    and abs(M3_prev_v) <= 50.0 * max(M3_tower, 1e-300)):
                M3 = 0.0
                do_m_row = False
            else:
                M3 = M3_prev_v
        tay["M3_prev"] = M3 if M3 != 0.0 else tay.get("M3_prev", 0.0)
        if self.tay_do_m and do_m_row:
            m_ser = M3 * xia**3
            m_arr[ipa] += gamma * (m_ser - m_arr[ipa])
            m_arr[ima] += gamma * (M3 * xib**3 - m_arr[ima])
        # (c) проекция чётной части (p+q) в зоне (k=1..K): 4-параметровый фит
        # учитывает смещение x*; коррекция пополам на p и q, p-q сохраняется
        ks1 = np.arange(1, K + 1)
        ip1 = i0 - ks1
        im1 = i0 + ks1
        pq_even = np.zeros(2 * K)
        if self.tay_do_pq:
            pq = p_arr + q_arr
            xpq = np.concatenate([x[ip1] - x_star, x[im1] - x_star])
            ypq = np.concatenate([pq[ip1], pq[im1]])
            APQ = np.stack([np.ones_like(xpq), xpq, xpq**2, xpq**3], axis=1)
            cPQ, *_ = np.linalg.lstsq(APQ, ypq, rcond=None)
            pq_even = cPQ[0] + cPQ[2] * xpq**2        # чётная часть (паразита)
            corr = 0.5 * np.concatenate([gamma[1:], gamma[1:]]) * pq_even
            sum_pq = pq[ip1] - corr[:K]
            dif_pq = pq[ip1] - 2.0 * q_arr[ip1]       # p - q сохраняем
            p_arr[ip1] = 0.5 * (sum_pq + dif_pq)
            q_arr[ip1] = 0.5 * (sum_pq - dif_pq)
            sum_pq = pq[im1] - corr[K:]
            dif_pq = pq[im1] - 2.0 * q_arr[im1]
            p_arr[im1] = 0.5 * (sum_pq + dif_pq)
            q_arr[im1] = 0.5 * (sum_pq - dif_pq)
        # центральная точка: t = s = t0, c = d = d0 (только эти; p, q, r,
        # a2 в точке i0 НЕ трогаются — защита от петли обратной связи)
        t_arr[i0] = t0
        s_arr[i0] = t0
        c_arr[i0] = d0
        d_arr[i0] = d0

        # --- 6. диагностика -------------------------------------------------
        a2_c = 0.5 * (a2_arr[i0 - 1] + a2_arr[i0 + 1]) if i0 >= 1 and i0 < n - 1 \
            else float(a2_arr[i0])
        rec = {
            "v": float(v_new), "t0": float(t0), "R1": float(R1), "d0": float(d0),
            "P2": float(P2), "W2": float(W2), "M3": float(M3),
            "M3_fit": float(M3_fit_diag) if np.isfinite(M3_fit_diag) else 0.0,
            "M3_series": float(M3_series), "x_star": float(x_star), "chi": float(chi),
            "E0_free": float(E0_free), "C_par": float(C_par),
            "tay_rows": int(tay["rows"]),
            "C0_gauge": float(abs(R1**2 - a2_c) / max(a2_c, 1e-300)),
            "res_r": res_r, "res_E": res_E, "res_O": res_O,
            "dbg_E_boost_res": dbg_e, "dbg_O_boost_res": dbg_o,
            "dbg_zone": dbg_zone,
            "pq_even_max": float(np.max(np.abs(pq_even))) if pq_even.size else 0.0,
        }
        tay["hist"].append(rec)
        if len(tay["hist"]) > 512:
            tay["hist"].pop(0)

    def _annulus_parity(self, st, v_new):
        """v6: КОЛЬЦЕВАЯ ЧЁТНОСТЬ — проекция зеркальной чётности ВНЕ зоны.

        Точная зеркальная симметрия (u,v)->(v,u) критического решения даёт
        на каждой строке (y = const), как функции xi = x - x*:
            G := t+s = 2E(xi)   ЧЁТНО;    D := t-s = 2O(xi)   НЕЧЁТНО;
            pq := p+q ЧЁТНО;    pd := p-q НЕЧЁТНО;
            cd := c+d ЧЁТНО;    dc := d-c НЕЧЁТНО;
            m НЕЧЁТНО (m ~ M3 xi^3 + M5 xi^5, регулярность m(0)=0, m~r^3).
        Всё, что нарушает эти чётности вне зоны реконструкции, — чистый
        дискретизационный мусор сырого марша (стена v5), и он гасится
        парной проекцией с гладким тейпером. Однородная мода марша
        t_hom ~ C/xi и массовый мусор m_junk = M1*xi НЕЧЁТНЫ — чётностью
        не ловятся, гасятся отдельно фитом на кольце:
            O-пары: базис [xi, xi^3, xi^5, 1/xi] -> C_j гасится;
            m-пары: базис [xi, xi^3, xi^5]       -> M1 гасится.
        r, alpha2, Phi НЕ трогаются (урок v5: петля обратной связи C1).
        """
        du = self.du
        r_arr = st["r"]
        n = len(r_arr)
        u = self.u
        x = (v_new - u) / 2.0
        r_abs = np.abs(r_arr)
        i0 = int(np.argmin(r_abs))
        if r_abs[i0] > 3.0 * du:
            return
        # --- v6: поточечный башенный конверт cd (с ПЕРВОЙ строки стадии) ---
        # cd = c+d = omega_y = W0' + W2' xi^2 + ...; W0' = 2 d0 — машино-
        # выведенная связь (O2). Рестарт-транзиент d ~ 1e4 (трассировка v6:
        # первый mover каскада p,q -> t) физически невозможен и клипуется.
        # Не требует парности/свежести патча — работает на рестарт-строках.
        tay0 = getattr(self, "_tay", None)
        d0_ann = float(tay0.get("d0", 0.0)) if tay0 else 0.0
        t0_ann = float(tay0.get("t0", 0.0)) if tay0 else 0.0
        if np.isfinite(d0_ann) and np.isfinite(t0_ann):
            ring_lo0 = max(self.reg_zone_du * du,
                           1.2 * float(getattr(self, "R_heal", 0.0)))
            # конверт на ВСЮ строку: мусор d = d_edge + cumtrapz(w) размазывается
            # cumtrapz'ом ЗА пределы кольца (трассировка v6: maxc ~ 3e3 при
            # r >> 80du). Насыщение роста x20: физический omega_y = c+d вдали
            # от центра O(10-100), junk ~ 1e3-1e4 -> клипуется, физика нет.
            near = np.isfinite(st["r"])
            cd_all = st["c"] + st["d"]
            xi_near = x - float(x[i0])
            env = 25.0 * (abs(d0_ann) + abs(t0_ann)) * np.maximum(
                1.0, np.minimum(np.abs(xi_near) / max(ring_lo0, 1e-30),
                                20.0)) + 60.0
            dev = cd_all - 2.0 * d0_ann
            bad = near & (np.abs(dev) > env) & np.isfinite(dev)
            if bad.any():
                fix = np.where(bad, dev - np.sign(dev) * env, 0.0)
                cd_new = cd_all - fix
                st["c"][near] += 0.5 * (cd_new - cd_all)[near]
                st["d"][near] += 0.5 * (cd_new - cd_all)[near]
        # --- v6: ПЕРЕМАРШ t от края тейлор-зоны наружу (обе стороны) -------
        # Сырой марш в _do_step стартует с i0: источник SC ~ q*s/r ~ 1/r
        # требует компенсации pt = -qs с точностью ~1e-4; дисбаланс накапливает
        # t снаружи зоны (трассировка v6: рост 0.36 -> 8e3 за 10 строк).
        # Перемарш стартует от ЧИСТОГО серийного t(K_zone) (патч уже отработал
        # на этой строке) и заменяет t снаружи; мода C/r затухает наружу.
        # Работает С ПЕРВОЙ строки стадии (гейт tay_rows > 6 — только для
        # парных проекций ниже, перемаршу парность не нужна).
        ring_lo0 = max(self.reg_zone_du * du,
                       1.2 * float(getattr(self, "R_heal", 0.0)))
        K_zone0 = int(round(2.0 * ring_lo0 / du))
        with np.errstate(all="ignore"):
            Kzm = min(K_zone0, i0 - 2, n - 3 - i0)
            if Kzm >= 4 and tay0 and np.isfinite(tay0.get("t0", float("nan"))) \
                    and abs(tay0.get("t0", 0.0)) > 0:
                r_safe_m = np.where(np.abs(r_arr) < self.r_floor,
                                    self.r_floor, r_arr)
                pr_m = st["p"] / r_safe_m
                qsr_m = st["q"] * st["s"] / r_safe_m
                # fac <= 0.12: физический fac = 0.5 p du/r <= 0.5|p|/Kzm ~ 0.03
                # при k > Kzm; клип включает себя ТОЛЬКО на мусорном p —
                # иначе компаундинг (1.45/0.55)^600 (трассировка v6)
                fac_m = np.clip(0.5 * du * pr_m, -0.12, 0.12)
                tq = st["t"].copy()
                i_a = i0 - Kzm                    # (+r)-сторона
                t_next = tq[i_a]
                for i in range(i_a - 1, -1, -1):
                    t_next = (t_next * (1.0 + fac_m[i + 1])
                              + 0.5 * du * (qsr_m[i] + qsr_m[i + 1])) \
                        / (1.0 - fac_m[i])
                    tq[i] = t_next
                i_b = i0 + Kzm                    # зеркало
                t_next = tq[i_b]
                for i in range(i_b + 1, n):
                    t_next = (t_next * (1.0 - fac_m[i - 1])
                              - 0.5 * du * (qsr_m[i - 1] + qsr_m[i])) \
                        / (1.0 + fac_m[i])
                    tq[i] = t_next
                # T-cap вне зоны: физический |t| снаружи ~ O(max|s| строки)
                # (CSS-соотношение t(xi) = s(-xi) — зеркало ДОВЕРЕННОГО
                # эволюционируемого поля s, а не зоны: кап на t_zone_max
                # самоуничтожался при грязной зоне — канал j=54)
                s_row_max = float(np.nanmax(np.abs(st["s"][np.isfinite(st["s"])]))) \
                    if np.isfinite(st["s"]).any() else 0.0
                t_zone_max = float(np.nanmax(np.abs(tq[i_a:i_b + 1]))) \
                    if Kzm > 0 else 0.0
                cap_t = 20.0 * max(t_zone_max, s_row_max) \
                    + 20.0 * abs(tay0.get("t0", 0.0)) + 10.0
                tq[:i_a] = np.clip(tq[:i_a], -cap_t, cap_t)
                tq[i_b + 1:] = np.clip(tq[i_b + 1:], -cap_t, cap_t)
                tq = np.where(np.isfinite(tq), tq, st["t"])
                st["t"][:] = tq
        # x*: только СВЕЖЕЕ значение тейлор-патча этой строки; на рестарт-
        # строках (фит не сходился/нет записи) кольцо НЕ работает — на грязном
        # состоянии парная проекция вокруг смещённого центра впрыскивает
        # мусор вместо его гашения (урок первого смоука v6)
        x_star = None
        tay = getattr(self, "_tay", None)
        if tay and tay.get("hist"):
            last = tay["hist"][-1]
            res_r = last.get("res_r", float("nan"))
            if (abs(last.get("v", 1e18) - v_new) <= 1.5 * self.dv
                    and last.get("tay_rows", 0) > 6
                    and np.isfinite(last.get("x_star", float("nan")))
                    and np.isfinite(res_r) and res_r < 0.15
                    and abs(float(x[i0]) - float(last["x_star"])) <= 2.5 * du):
                x_star = float(last["x_star"])
        if x_star is None:
            return
        if r_abs[i0] > 1.5 * du:      # центр плохо локализован на этой строке
            return
        # (перемарш t выполняется ВЫШЕ — с первой строки стадии, без парности)
        ring_lo = max(self.reg_zone_du * du,
                      1.2 * float(getattr(self, "R_heal", 0.0)))
        K_zone = int(round(2.0 * ring_lo / du))
        k_lo = K_zone + 4                       # зазор за краевым кольцом m3
        K_A = int(round(2.0 * self.ann_factor * ring_lo / du))
        K_A = min(K_A, i0 - 3, n - 4 - i0)
        if K_A <= k_lo + 4:
            return
        ks = np.arange(k_lo, K_A + 1)
        ip = i0 - ks
        im = i0 + ks
        t_arr = st["t"]; s_arr = st["s"]
        p_arr = st["p"]; q_arr = st["q"]
        c_arr = st["c"]; d_arr = st["d"]; m_arr = st["m"]
        G = t_arr + s_arr
        D = t_arr - s_arr
        gated = []
        xi_p = x[ip] - x_star
        xi_m = x[im] - x_star
        with np.errstate(all="ignore"):
            fin = (np.isfinite(G[ip]) & np.isfinite(G[im])
                   & np.isfinite(D[ip]) & np.isfinite(D[im])
                   & np.isfinite(xi_p) & np.isfinite(xi_m)
                   & (np.abs(xi_p) > 1e-12) & (np.abs(xi_m) > 1e-12))
            if int(fin.sum()) < max(len(ks) // 2, 4):
                return
            # гладкий тейпер: 0 на обоих краях кольца, 1 в середине
            kk = (ks - k_lo) / float(max(K_A - k_lo, 1))
            w = np.minimum(1.0, np.minimum(4.0 * kk, 4.0 * (1.0 - kk))) ** 2
            w = np.where(fin, w, 0.0)
            xi_sp = np.where(np.abs(xi_p) > 1e-12, xi_p, 1e-12)
            xi_sm = np.where(np.abs(xi_m) > 1e-12, xi_m, 1e-12)
            C_j = float("nan"); M1 = float("nan")

            # --- (t,s): CROSS или парная проекция чётности -----------------
            G_odd = 0.5 * (G[ip] - G[im])       # нечётный мусор в G
            D_even = 0.5 * (D[ip] + D[im])      # чётный мусор в D
            dG_ip = -w * G_odd                  # на im — зеркально (+w G_odd)
            dD_ip = -w * D_even
            dD_im = -w * D_even
            if getattr(self, "ann_cross", False):
                # v6.1 CROSS: t(xi) := s(-xi) с тейпером w; s НЕ трогается.
                # Точное CSS-соотношение: на CSS-профиле h(xi) = g(-xi),
                # поэтому cross-assign удовлетворяет ОБЕИМ чётностям (G =
                # s+s_mirror чётно, D = s_mirror-s нечётно) и не воюет с
                # эволюцией s. Битва марша/проекции (канал j=19-20)
                # устранена: марш t нужен только ВНУТРИ зоны (внутреннее
                # ГУ t(i0)=s(i0)), снаружи t срежется к зеркалу s.
                s_ip = s_arr[ip]; s_im = s_arr[im]
                okc = np.isfinite(s_ip) & np.isfinite(s_im) & fin
                dG_ip = np.where(okc, w * (s_im - t_arr[ip]), 0.0)
                dG_im = np.where(okc, w * (s_ip - t_arr[im]), 0.0)
                t_arr[ip] += dG_ip
                t_arr[im] += dG_im
                dD_ip = dG_ip
                dD_im = dG_im
                scale_G = float(np.max(np.abs(G[ip][fin]))) + float(np.max(np.abs(G[im][fin])))
                scale_D = scale_G
            else:
                # v6-гейт: правка не должна превышать долю локального поля
                # (ann_relax_gate: 0.5 консервативно, 2.5 — агрессивный режим;
                # см. комментарий в __init__ — канал j=19-20)
                scale_G = float(np.max(np.abs(G[ip][fin]))) + float(np.max(np.abs(G[im][fin])))
                scale_D = float(np.max(np.abs(D[ip][fin]))) + float(np.max(np.abs(D[im][fin])))
                gate = float(getattr(self, "ann_relax_gate", 0.5))
                if scale_G > 0 and float(np.max(np.abs(dG_ip))) > gate * scale_G:
                    dG_ip = np.zeros_like(dG_ip); gated.append("G")
                if scale_D > 0 and float(np.max(np.abs(dD_ip))) > gate * scale_D:
                    dD_ip = np.zeros_like(dD_ip); dD_im = np.zeros_like(dD_im)
                    gated.append("D")
                t_arr[ip] += 0.5 * (dG_ip + dD_ip)
                s_arr[ip] += 0.5 * (dG_ip - dD_ip)
                dG_im = -dG_ip
                t_arr[im] += 0.5 * (dG_im + dD_im)
                s_arr[im] += 0.5 * (dG_im - dD_im)
            G_odd_max = float(np.max(np.abs(w * G_odd))) if scale_G > 0 else 0.0
            D_even_max = float(np.max(np.abs(w * D_even))) if scale_D > 0 else 0.0
            if self.ann_do_cpar and not getattr(self, "ann_cross", False):
                # однородная мода марша O_hom ~ C/xi (нечётная): фит на кольце
                # (в CROSS-режиме не нужна: t := mirror(s) заменяет C/xi)
                O_pair = 0.25 * (D[ip] - D[im])             # = O(xi_p)
                ok = fin & np.isfinite(O_pair)
                if int(ok.sum()) >= max(len(ks) // 2, 4):
                    AO = np.stack([xi_p, xi_p ** 3, xi_p ** 5,
                                   1.0 / xi_sp], axis=1)
                    cO, *_ = np.linalg.lstsq(AO[ok], O_pair[ok], rcond=None)
                    C_j = float(cO[3])
                    corr_c = w * 2.0 * C_j / xi_sp
                    if float(np.max(np.abs(corr_c))) <= gate * max(scale_D, 1e-300):
                        dD_ip = dD_ip - corr_c
                        dD_im = dD_im - w * 2.0 * C_j / xi_sm
                    else:
                        gated.append("C/xi")
            t_arr[ip] += 0.5 * (dG_ip + dD_ip)
            s_arr[ip] += 0.5 * (dG_ip - dD_ip)
            dG_im = -dG_ip
            t_arr[im] += 0.5 * (dG_im + dD_im)
            s_arr[im] += 0.5 * (dG_im - dD_im)

            # --- (p,q): pq чётно, pd нечётно --------------------------------
            if self.ann_do_pq:
                pq = p_arr + q_arr
                pd = p_arr - q_arr
                pq_odd = 0.5 * (pq[ip] - pq[im])
                pd_even = 0.5 * (pd[ip] + pd[im])
                dpq = -w * pq_odd
                dpd = -w * pd_even
                p_arr[ip] += 0.5 * (dpq + dpd)
                q_arr[ip] += 0.5 * (dpq - dpd)
                p_arr[im] += 0.5 * (-dpq + dpd)
                q_arr[im] += 0.5 * (-dpq - dpd)

            # --- (c,d): cd чётно, dc нечётно (конверт — поточечный, выше) ----
            if self.ann_do_cd:
                cd = c_arr + d_arr
                dc = d_arr - c_arr
                cd_odd = 0.5 * (cd[ip] - cd[im])
                dc_even = 0.5 * (dc[ip] + dc[im])
                dcd = -w * cd_odd
                ddc = -w * dc_even
                c_arr[ip] += 0.5 * (dcd - ddc)
                d_arr[ip] += 0.5 * (dcd + ddc)
                c_arr[im] += 0.5 * (-dcd - ddc)
                d_arr[im] += 0.5 * (-dcd + ddc)

            # --- m: башенный бленд m -> M3tw*xi^3 + M5*xi^5 (БЕЗ 1/r-моды) ---
            if self.ann_do_m1:
                M3tw = float(tay.get("M3tw", 0.0)) if tay else 0.0
                ym = m_arr[ip]
                okm = fin & np.isfinite(ym) & np.isfinite(M3tw) \
                    & (abs(M3tw) > 0)
                if int(okm.sum()) >= max(len(ks) // 2, 4):
                    Am = np.stack([xi_p, xi_p ** 3, xi_p ** 5], axis=1)
                    cm, *_ = np.linalg.lstsq(Am[okm], ym[okm], rcond=None)
                    M1 = float(cm[0])
                    M5f = float(cm[2])
                    # гейт M5: |M5| <= 10 |M3tw| / ring_lo^2 (масштаб 1/L^2)
                    if not np.isfinite(M5f) or \
                            abs(M5f) > 10.0 * abs(M3tw) / max(ring_lo, 1e-30) ** 2:
                        M5f = 0.0
                    # цель: торновская кубика + физическая xi^5-поправка фита;
                    # 1/r-мода (M1*xi) ВЫБРАСЫВАЕТСЯ (junk-доминировала сырое m)
                    mtg_p = M3tw * xi_p ** 3 + M5f * xi_p ** 5
                    mtg_m = -(M3tw * xi_p ** 3 + M5f * xi_p ** 5)
                    m_arr[ip] += np.where(okm, w * (mtg_p - m_arr[ip]), 0.0)
                    m_arr[im] += np.where(okm, w * (mtg_m - m_arr[im]), 0.0)

        self._ann_hist.append({
            "v": float(v_new), "K_zone": int(K_zone), "K_A": int(K_A),
            "corr_ts_max": float(np.max(np.abs(dG_ip))),
            "corr_D_max": float(np.max(np.abs(dD_ip))) if np.size(dD_ip) else 0.0,
            "G_odd_max": G_odd_max, "D_even_max": D_even_max,
            "corr_m_max": float(abs(M1) * float(np.max(np.abs(xi_p))))
                if np.isfinite(M1) else 0.0,
            "C_j": float(C_j), "M1": float(M1),
            "gated": ",".join(gated),
        })
        if len(self._ann_hist) > 256:
            self._ann_hist.pop(0)

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
            # ВНИМАНИЕ (фикс v3): усредняются ПОЛОВИННЫЕ суммы E=(t+s)/2:
            # y = 0.25[(t+s)(-r) + (t+s)(+r)] = E(r); прежние 0.5 давали y = 2E
            # (двойная чётная часть в зоне при E != 0).
            y = 0.25 * (A_plus + A_minus)
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
                # v6: CFL-страж марша: коэффициент 0.5*du*p/r физически
                # O(1e-2); мусорный p (рестарт-транзиент) даёт полюс
                # 1/(1-0.5du p/r) -> взрыв t за одну строку (трассировка v6).
                # Клип только и включает себя на мусорных p.
                fac = np.clip(0.5 * self.du * pr, -0.45, 0.45)
                t_new = np.empty_like(st_new["p"])
                t_new[i0c] = float(st_new["s"][i0c])
                # (+r)-сторона: r убывает с i, наружу = убывание i
                for i in range(i0c - 1, -1, -1):
                    t_new[i] = (t_new[i + 1] * (1.0 + fac[i + 1])
                                + 0.5 * self.du * (qsr[i] + qsr[i + 1])) \
                               / (1.0 - fac[i])
                # зеркало: наружу = рост i
                for i in range(i0c + 1, len(pr)):
                    t_new[i] = (t_new[i - 1] * (1.0 - fac[i - 1])
                                - 0.5 * self.du * (qsr[i - 1] + qsr[i])) \
                               / (1.0 + fac[i])
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
            # реконструкция центра (ОБА режима марша): v5 Тейлор-патч
            # (эволюция коэффициентов как внутреннего ГУ), v3 регулярное
            # замыкание (связка наклонов s1-t1) или v2 клэмп t=s
            if getattr(self, "center_closure", "clamp") == "taylor":
                self._center_taylor(t_new, st_new, v_new)
            elif getattr(self, "center_closure", "clamp") == "regular":
                self._center_regular(t_new, st_new["s"], st_new["m"], r_new,
                                     p_arr=st_new["p"], q_arr=st_new["q"],
                                     c_arr=st_new["c"], d_arr=st_new["d"])
            elif self.heal_enabled:
                self._center_heal(t_new, st_new["s"], st_new["m"], r_new)
            # v6.1: ПОРЯДОК ИСПРАВЛЕН (канал j=19-20, трассировка eps=1e-3).
            # Было: st_new["t"] алиасился с родительским массивом -> перемарш/
            # чётность мутировали РОДИТЕЛЬСКИЙ t, результат выбрасывался
            # (st_new["t"] = t_new), а Phi впитывал полувпрыск из мутированного
            # родителя — сэндвич t портился, наружный t не чистился никогда.
            # Теперь: t_new -> Phi (по чистому родителю) -> чётность/перемарш
            # на НОВОМ t -> согласование Phi с правкой (дискретный сэндвич
            # Phi_v = (t_old + t_new)/2 сохраняется точно).
            st_new["t"] = t_new
            st_new["Phi"] = st["Phi"] + 0.5 * dv * (st["t"] + t_new)
            st_new["Phi"][0] = float(self._edge_Phi(np.array([v_new]))[0])
            if getattr(self, "annulus_parity", False):
                t_pre = t_new.copy()
                self._annulus_parity(st_new, v_new)
                dT = st_new["t"] - t_pre
                if np.isfinite(dT).all() and np.any(dT != 0.0):
                    st_new["Phi"] += 0.5 * dv * dT
                    st_new["Phi"][0] = float(
                        self._edge_Phi(np.array([v_new]))[0])
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
        w = st["alpha2"] * st["m"] / (2.0 * r_safe**3) \
            - 0.5 * KAPPA * st["s"] * st["t"]
        # v6: башенный страж источника TH. Регулярное значение у центра:
        # a2 m/(2r^3)|0 = a2 M3/(2 R1^3) = O(t0^2) (после M3-гейта через
        # торновскую связку M3 = 2R1 t0^2/3), kappa/2 s t = O(t0^2).
        # Мусор интерполяции m на рестарт-строках давал w ~ 1e8 (трассировка
        # v6) -> каскад c,d -> p,q -> t. Клип 50*(t0^2+1) трогает только мусор.
        tay = getattr(self, "_tay", None)
        if self.center_closure == "taylor" and tay:
            t0c = abs(tay.get("t0", 0.0))
            if np.isfinite(t0c):
                wcap = 50.0 * (t0c * t0c + 1.0)
                w = np.nan_to_num(w, nan=0.0, posinf=wcap, neginf=-wcap)
                w = np.clip(w, -wcap, wcap)
            # v6: ранние строки стадии — источник w у центра = БАШЕННОЕ
            # значение TH: w(0) = a2 M3/(2 R1^3) - kappa/2 t0^2; при торновской
            # M3 = 2R1 t0^2/(3(1-chi)^2) и калибровке a2(0) = (1-chi^2) R1^2:
            #   w(0) = t0^2/(3(1-chi)^2) * (1-chi^2) - t0^2 = -(2/3) t0^2 (chi=0).
            # Мусор cumtrapz(w) через интерполяционный m/r^3 — главный источник
            # c,d-каскада на рестарт-строках (трассировка v6).
            tay_rows = tay.get("rows", 99)
            t0v = tay.get("t0", 0.0)
            if tay_rows <= 8 and np.isfinite(t0v):
                r_loc = np.abs(st["r"]) < 2.0 * self.reg_zone_du * self.du
                w = np.where(r_loc, -(2.0 / 3.0) * t0v * t0v, w)
        return w

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
