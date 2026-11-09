#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Численная верификация утверждений плана "Шаг к гипотезе Янга-Миллса"
(септинальная система: D\\G — 22-вершинный цикл, дельта_C = pi/7).

Проверяется:
  1. Delta_Berry(pi/7) = sqrt(1 + 2*(pi/7)^2)  — и сравнение со значением из плана.
  2. Порог строгой положительности зазора: ||V|| < Delta/2 (консервативная форма
     плана) и ||V|| < Delta (точная форма из принципа Рэлея).
  3. ||V|| для 22-вершинного цикла с V = J * sum_<s,s'> (sx sx + sy sy):
       - грубая оценка треугольником: ||V|| <= 2|J|*|E| = 44|J|;
       - точное значение через Джордана-Вигнера (свободные фермионы, две границы).
     Формула JW верифицируется прямой диагонализацией при N = 4, 6, 8, 10.
  4. Требуемые пороги на |J|.
  5. Локальный гамильтониан H_s = (I - sqrt(1+2 delta^2) sz)/2: спектр и зазор.
  6. E_vac — показывает, что зазор нужно отсчитывать ОТ уровня вакуума.
"""
import numpy as np
import math

N_SITES = 22          # |D \ G|
DELTA_C = math.pi / 7  # фаза сектора C

sx = np.array([[0, 1], [1, 0]], dtype=complex)
sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
sz = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def kron_chain(ops, N):
    """Оператор на N кубитах: ops[i] действует на i-м, на остальных identity."""
    out = np.array([[1.0 + 0j]])
    for i in range(N):
        out = np.kron(out, ops.get(i, I2))
    return out


def V_ring(N, J=1.0):
    """V = J * sum по рёбрам цикла (sx_i sx_{i+1} + sy_i sy_{i+1}), полная матрица 2^N."""
    dim = 2 ** N
    V = np.zeros((dim, dim), dtype=complex)
    for s in range(N):
        t = s + 1 if s + 1 < N else 0  # цикл: ребро (s, s+1 mod N)
        V += kron_chain({s: sx, t: sx}, N) + kron_chain({s: sy, t: sy}, N)
    return J * V


def jw_norm(N, J=1.0):
    """Точная норма V через Джордана-Вигнера.
    V = J * sum (sx sx + sy sy) = 2J * sum (s+ s- + h.c.)  =>  одночастичные
    энергии  eps_k(phi) = 4J cos((2 pi k + phi)/N);  чётность числа фермионов
    задаёт граничную фазу phi из {0, pi}.  Максимум энергии в секторе с данным
    phi равен сумме положительных eps = (1/2) sum |eps| (спектр симметричен).
    ||V|| = max по phi."""
    best = 0.0
    for phi in (0.0, math.pi):
        ks = np.arange(N)
        eps = 4.0 * J * np.cos((2.0 * math.pi * ks + phi) / N)
        best = max(best, 0.5 * np.sum(np.abs(eps)))
    return best


print("=" * 72)
print("1) Delta_Berry(pi/7) = sqrt(1 + 2*(pi/7)^2)")
d = DELTA_C
Delta = math.sqrt(1 + 2 * d * d)
print(f"   delta_C        = pi/7 = {d:.15f}")
print(f"   Delta_Berry    = {Delta:.15f}")
print(f"   план утверждал ~1.203  ->  расхождение: {1.203 - Delta:+.6f}")
print(f"   (вероятная причина: sqrt(1+2*(pi/7)^2) посчитан с неточным pi)")

print("=" * 72)
print("2) Пороги строгой положительности зазора")
print(f"   консервативная форма плана:  ||V|| < Delta/2 = {Delta / 2:.9f}")
print(f"   точная форма (Рэлей):        ||V|| < Delta   = {Delta:.9f}")
print(f"   план утверждал порог 0.601 (соответствует Delta=1.203/2=0.6015)")

print("=" * 72)
print("3) ||V|| для XX+YY-цикла, V = J * sum_edges (sx sx + sy sy)")
print("   Верификация JW-формулы прямой диагонализацией:")
for N in (4, 6, 8, 10):
    Vd = V_ring(N, J=1.0)
    norm_dense = np.linalg.norm(np.linalg.eigvalsh(Vd), ord=np.inf)
    norm_jw = jw_norm(N, J=1.0)
    ok = "OK " if abs(norm_dense - norm_jw) < 1e-9 else "FAIL"
    print(f"   N={N:2d}: dense={norm_dense:.12f}  JW={norm_jw:.12f}  [{ok}]")

norm_jw_22 = jw_norm(N_SITES, J=1.0)
crude_22 = 2.0 * N_SITES  # 2|J| на ребро * 22 ребра = 44|J|
print(f"   N=22: грубая оценка (треугольник): ||V|| <= 44|J|  (коэф. {crude_22})")
print(f"   N=22: точное значение (JW):        ||V||  = {norm_jw_22:.9f}|J|  (коэф. {norm_jw_22:.6f})")

print("=" * 72)
print("4) Требуемые пороги на |J| для положительности зазора")
print(f"   по грубой оценке (44|J| < Delta):        |J| < {Delta / crude_22:.9f}")
print(f"   по точной оценке ({norm_jw_22:.3f}|J| < Delta):      |J| < {Delta / norm_jw_22:.9f}")
print(f"   консервативная форма плана (44|J| < Delta/2): |J| < {Delta / 2 / crude_22:.9f}")

print("=" * 72)
print("5) Локальный гамильтониан H_s = (I - sqrt(1+2 delta^2) sz)/2, delta = pi/7")
c = math.sqrt(1 + 2 * d * d)
Hloc = 0.5 * (I2 - c * sz)
ev = np.linalg.eigvalsh(Hloc)
print(f"   собственные значения: {ev[0]:.12f}, {ev[1]:.12f}")
print(f"   локальный зазор: {ev[1] - ev[0]:.12f}  (должно быть Delta_Berry = {Delta:.12f})")

print("=" * 72)
print("6) Уровень вакуума E_vac (все спины вниз по энергии):")
print(f"   E_vac = N/2 * (1 - sqrt(1+2d^2)) при равномерной привязке = {N_SITES * 0.5 * (1 - c):.9f}")
print("   -> E_vac < 0, поэтому утверждение зазора формулируется ОТНОСИТЕЛЬНО E_vac:")
print("      <v|H|v> >= E_vac + Delta для v, ортогональных вакууму (формальная часть в Lean).")
print("=" * 72)
print("ВЕРДИКТ: Delta_Berry(pi/7) = 1.184415888 (не 1.203); порог ||V|| < 0.592209 (не 0.601).")
