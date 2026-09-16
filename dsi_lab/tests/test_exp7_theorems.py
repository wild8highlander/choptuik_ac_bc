# -*- coding: utf-8 -*-
"""Эксперимент 7: теоремы A/B/C — порог e >= 1 для частичных изометрий.

ТЕОРЕМА A: для частичных изометрий X1, X2 в C^n
           F = 3n - 2p - 2q + 3r >= n  (e = F/n >= 1),
           равенство <=> PQ = 0 и p + q = n.
ТЕОРЕМА B: при P + Q <= I точно F = n + 2*rank(I - P - Q);
           обрезка дерева Кунца даёт F = n + 2 (rank R = 1).
ТЕОРЕМА C: для унитарных пар (и перестановок) F = 2n точно.
"""
import numpy as np

from exp7_e1_threshold import (leavitt_F, random_partial_isometry,
                               random_projections_disjoint)


def _partial_isometry_pair(n, r1, r2, rng):
    X1 = random_partial_isometry(n, r1, rng)
    X2 = random_partial_isometry(n, r2, rng)
    return X1, X2


def test_theorem_A_identity_and_threshold():
    rng = np.random.default_rng(2024)
    for n in (2, 4, 6):
        for _ in range(120):
            r1 = int(rng.integers(0, n + 1))
            r2 = int(rng.integers(0, n + 1))
            X1, X2 = _partial_isometry_pair(n, r1, r2, rng)
            assert np.linalg.norm(X1 @ X1.conj().T @ X1 - X1) < 1e-11
            P, Q = X1 @ X1.conj().T, X2 @ X2.conj().T
            p = int(np.round(np.trace(P).real))
            q = int(np.round(np.trace(Q).real))
            r = np.trace(P @ Q).real
            F = leavitt_F(X1, X2)
            assert abs(F - (3 * n - 2 * p - 2 * q + 3 * r)) < 1e-8 * max(1, F)
            assert F >= n - 1e-9, (n, p, q, F)  # порог e >= 1


def test_theorem_A_equality_case():
    """Комплементарные ортогональные проекции: PQ = 0, p+q=n => F = n."""
    for n, p in ((4, 2), (6, 2), (6, 3), (8, 3)):
        q = n - p
        X1 = np.diag(np.r_[np.ones(p, dtype=complex), np.zeros(q)])
        X2 = np.diag(np.r_[np.zeros(p, dtype=complex), np.ones(q)])
        F = leavitt_F(X1, X2)
        assert abs(F - n) < 1e-10, (n, p, F)


def test_theorem_B_projection_covering():
    rng = np.random.default_rng(99)
    for _ in range(60):
        n = int(rng.integers(2, 13))
        p = int(rng.integers(0, n))
        q = int(rng.integers(0, n - p + 1))
        P, Q = random_projections_disjoint(n, p, q, rng)
        assert np.linalg.norm(P + Q - (P + Q).conj().T) < 1e-10
        R = np.eye(n) - P - Q
        rankR = int(np.linalg.matrix_rank(R, tol=1e-9))
        F = leavitt_F(P.copy(), Q.copy())
        assert abs(F - (n + 2 * rankR)) < 1e-8 * max(1, F), (n, p, q, F)


def test_theorem_B_tree_truncation_F_equals_n_plus_2():
    """Обрезка двоичного дерева глубины k: n = 2^(k+1) - 1, F = n + 2."""
    for k in (2, 3, 4):
        words = [""]
        level = [""]
        for _ in range(k):
            level = [a + w for w in level for a in ("a", "b")]
            words += level
        n = len(words)
        idx = {w: i for i, w in enumerate(words)}
        S1 = np.zeros((n, n))
        S2 = np.zeros((n, n))
        for w in words:
            if len(w) < k:
                if ("a" + w) in idx:
                    S1[idx["a" + w], idx[w]] = 1.0
                if ("b" + w) in idx:
                    S2[idx["b" + w], idx[w]] = 1.0
        F = leavitt_F(S1, S2)
        assert n == 2 ** (k + 1) - 1
        assert abs(F - (n + 2)) < 1e-8, (k, n, F)


def test_theorem_C_unitary_pairs():
    rng = np.random.default_rng(11)
    for n in (3, 5, 8):
        for _ in range(5):
            A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
            B = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
            U, _ = np.linalg.qr(A)
            V, _ = np.linalg.qr(B)
            F = leavitt_F(U, V)
            assert abs(F - 2 * n) < 1e-8, (n, F)


def test_trace_bounds_trPQ():
    """max(0, p+q-n) <= tr(PQ) <= min(p, q) — опорные оценки теоремы A."""
    rng = np.random.default_rng(5)
    for _ in range(80):
        n = int(rng.integers(2, 13))
        p = int(rng.integers(0, n + 1))
        q = int(rng.integers(0, n + 1))
        A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        U, _ = np.linalg.qr(A)
        P = U @ np.diag(np.r_[np.ones(p), np.zeros(n - p)]) @ U.conj().T
        B = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        V, _ = np.linalg.qr(B)
        Q = V @ np.diag(np.r_[np.ones(q), np.zeros(n - q)]) @ V.conj().T
        tr = np.trace(P @ Q).real
        assert max(0, p + q - n) - 1e-9 <= tr <= min(p, q) + 1e-9, (n, p, q, tr)
