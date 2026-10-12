"""The Kunz (Leavitt) defect F and the partial-isometry class.

Everything in this module is exact or machine-precision linear algebra
extracted from experiments 1 and 7 so that the theorems have a single
verifiable implementation.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
from numpy.typing import NDArray

#: Weighted-tree formula tolerance (theorem F of exp1 / contrast of exp7).
F_WEIGHTED_FORMULA_TOL: float = 1e-9


def leavitt_F(x1: NDArray, x2: NDArray) -> float:
    """Kunz defect F(X1, X2) (Frobenius norms, complex-safe):

    F = ||X1*X1 − I||^2 + ||X2*X2 − I||^2 + ||X1*X2||^2
        + ||X1*X1* + X2*X2* − I||^2 .
    """
    eye = np.eye(x1.shape[0])
    return float(
        np.linalg.norm(x1.conj().T @ x1 - eye, "fro") ** 2
        + np.linalg.norm(x2.conj().T @ x2 - eye, "fro") ** 2
        + np.linalg.norm(x1.conj().T @ x2, "fro") ** 2
        + np.linalg.norm(x1 @ x1.conj().T + x2 @ x2.conj().T - eye, "fro") ** 2
    )


def G_projections(p: NDArray, q: NDArray, n: int) -> float:
    """G(P, Q) = 2trP² + 2trQ² + 3tr(PQ) − 4trP − 4trQ + 3n.

    For projections the identity F = G holds exactly (audited in exp7);
    on partial isometries it reduces to F = 3n − 2p − 2q + 3r.
    """
    trp = float(np.trace(p).real)
    trq = float(np.trace(q).real)
    trpq = float(np.trace(p @ q).real)
    trp2 = float(np.trace(p @ p).real)
    trq2 = float(np.trace(q @ q).real)
    return 2.0 * trp2 + 2.0 * trq2 + 3.0 * trpq - 4.0 * trp - 4.0 * trq + 3.0 * float(n)


def kunz_tree_operators(k: int) -> tuple[NDArray, NDArray]:
    """Truncated shifts (S1, S2) of the binary Kunz tree of depth k.

    Words of length < k; S_a maps a word to its extension by the letter a.
    The ranges of S1 and S2 split depth >= 1 without overlap, which is why
    the trimmed tree attains F = n + 2 exactly (theorem B).
    """
    words: list[str] = [""]
    level: list[str] = [""]
    for _ in range(k):
        level = [a + w for w in level for a in ("a", "b")]
        words.extend(level)
    idx = {w: i for i, w in enumerate(words)}
    n = len(words)
    s1 = np.zeros((n, n))
    s2 = np.zeros((n, n))
    for w in words:
        if len(w) < k:
            if ("a" + w) in idx:
                s1[idx["a" + w], idx[w]] = 1.0
            if ("b" + w) in idx:
                s2[idx["b" + w], idx[w]] = 1.0
    return s1, s2


def kunz_tree_trimmed(k: int) -> tuple[int, float]:
    """(n, F) for the depth-k trimmed tree: exact F = n + 2 (theorem B)."""
    s1, s2 = kunz_tree_operators(k)
    return s1.shape[0], leavitt_F(s1, s2)


def weighted_tree_F(k: int, c1: float, c2: float) -> float:
    """Exact weighted-tree defect F = (n−1)[(c1²−1)² + (c2²−1)²] + n + 2.

    The minimum over weights is c1 = c2 = 1 (the unweighted trimming);
    no weighting reaches 5/7 — the floor of the class is e = 1.
    """
    s1, s2 = kunz_tree_operators(k)
    n = s1.shape[0]
    formula = (n - 1) * ((c1 * c1 - 1.0) ** 2 + (c2 * c2 - 1.0) ** 2) + n + 2.0
    direct = leavitt_F(c1 * s1, c2 * s2)
    assert abs(direct - formula) < F_WEIGHTED_FORMULA_TOL
    return formula


def scaled_permutation_defect(t: Fraction | float) -> Fraction:
    """e(t) = F/n for X_i = sqrt(t)·P_i: 7t² − 8t + 3 (t = c²).

    Minimum at t = 4/7 equals exactly 5/7 — the equality case of the sharp
    trace theorem, attainable only OUTSIDE the partial-isometry class.
    """
    if isinstance(t, Fraction):
        return 7 * t * t - 8 * t + 3
    return Fraction(7 * t * t - 8 * t + 3).limit_denominator(10**12)
