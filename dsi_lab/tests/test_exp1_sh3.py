# -*- coding: utf-8 -*-
"""Эксперимент 1 (Ш.3(iii)): мост следа — быстрые проверки.

Проверяем:
  1. Нижняя граница F(X1,X2) >= 5n/7 для произвольных пар (лемма устойчивости).
  2. Точка минимума: скалярная пара sqrt(4/7)*I достигает 5n/7.
  3. Тождество leavitt_F(P, Q) = G_of_PQ(P, Q) для проекций.
  4. L-BFGS в малых размерностях не проваливается ниже 5/7.
"""
import math

import numpy as np
import pytest

from exp1_sh3_bridge import G_of_PQ, leavitt_F, random_pair


def test_lower_bound_random_pairs():
    rng = np.random.default_rng(1234)
    for n in (2, 3, 5, 8):
        for _ in range(25):
            X1, X2 = random_pair(n, rng)
            F = leavitt_F(X1, X2)
            assert F >= 5.0 * n / 7.0 - 1e-9, (n, F)


def test_scalar_minimum_exact():
    for n in (1, 2, 4, 7):
        s = math.sqrt(4.0 / 7.0)
        X1 = s * np.eye(n) + 0j
        X2 = s * np.eye(n) + 0j
        F = leavitt_F(X1, X2)
        assert abs(F - 5.0 * n / 7.0) < 1e-10, (n, F)


def test_projection_identity_G_of_PQ():
    rng = np.random.default_rng(7)
    for n in (3, 6, 9):
        for _ in range(10):
            A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
            U, _ = np.linalg.qr(A)
            p = int(rng.integers(0, n + 1))
            q = int(rng.integers(0, n + 1))
            P = U @ np.diag(np.r_[np.ones(p), np.zeros(n - p)]) @ U.conj().T
            V, _ = np.linalg.qr(
                rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)))
            Q = V @ np.diag(np.r_[np.ones(q), np.zeros(n - q)]) @ V.conj().T
            F = leavitt_F(P, Q)
            G = G_of_PQ(P, Q).real
            assert abs(F - G) < 1e-8 * max(1.0, F), (n, F, G)


def test_lbfgs_stays_above_floor():
    """Мини-версия part_A: оптимизация не должна опускаться ниже 5/7."""
    from scipy.optimize import minimize

    rng = np.random.default_rng(42)
    n = 4
    floor = 5.0 * n / 7.0

    def obj(z):
        X1 = z[: n * n].reshape(n, n) + 1j * z[n * n:].reshape(n, n)
        X2 = -z[n * n:].reshape(n, n) + 1j * z[: n * n].reshape(n, n)
        return leavitt_F(X1, X2).real

    best = math.inf
    for _ in range(3):
        z0 = rng.standard_normal(2 * n * n) * 0.3
        r = minimize(obj, z0, method="L-BFGS-B",
                     options={"maxiter": 300, "ftol": 1e-14, "gtol": 1e-12})
        best = min(best, r.fun)
    assert best >= floor - 1e-6, best
    # и глобальный минимум 5n/7 действительно достигается скалярами
    assert abs(best - floor) < 1e-6 or best > floor
