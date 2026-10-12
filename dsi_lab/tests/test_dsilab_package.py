"""Unit tests for the dsilab package (fast, no experiment re-runs)."""

from fractions import Fraction

import numpy as np
import pytest

from dsilab.census import census_identity, genus_family_branches, gl3_f2
from dsilab.constants import (
    B_CH_SEVEN,
    C_K3_EXACT,
    E_FREE,
    PSL27_ORDER,
)
from dsilab.convergents import (
    continued_fraction,
    convergents_of,
    is_census_fraction,
)
from dsilab.leavitt import (
    G_projections,
    kunz_tree_trimmed,
    leavitt_F,
    scaled_permutation_defect,
    weighted_tree_F,
)


# -- constants ---------------------------------------------------------------
def test_c_k3_exact_value():
    assert C_K3_EXACT == Fraction(9, 224)
    assert abs(float(C_K3_EXACT) - 0.04017857142857143) < 1e-15


def test_b_ch_seven():
    assert abs(B_CH_SEVEN - 0.37651019814126640) < 1e-14


def test_psl27_order():
    assert PSL27_ORDER == 168


# -- leavitt: theorem A equality case (complementary projections) ------------
def test_theorem_A_equality_complementary():
    for n, p in ((4, 2), (6, 2), (6, 3), (8, 3), (10, 4)):
        q = n - p
        x1 = np.diag(np.r_[np.ones(p, dtype=complex), np.zeros(q)])
        x2 = np.diag(np.r_[np.zeros(p, dtype=complex), np.ones(q)])
        F = leavitt_F(x1, x2)
        assert abs(F - n) < 1e-10


def test_identity_F_equals_G_on_projections():
    rng = np.random.default_rng(7)
    for _ in range(20):
        n = int(rng.integers(2, 10))
        p = int(rng.integers(0, n + 1))
        a = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        u, _ = np.linalg.qr(a)
        p_mat = u @ np.diag(np.r_[np.ones(p), np.zeros(n - p)]) @ u.conj().T
        b = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        v, _ = np.linalg.qr(b)
        q_rank = int(rng.integers(0, n - p + 1))
        q_mat = (
            v
            @ np.diag(np.r_[np.zeros(p), np.ones(q_rank), np.zeros(n - p - q_rank)])
            @ v.conj().T
        )
        F = leavitt_F(p_mat, q_mat)
        G = G_projections(p_mat, q_mat, n)
        assert abs(F - G) < 1e-8 * max(1.0, F)


# -- theorem B: trimmed Kunz tree is exactly F = n + 2 ------------------------
@pytest.mark.parametrize("k", [2, 3, 4, 5, 6])
def test_theorem_B_tree_trim(k):
    n, F = kunz_tree_trimmed(k)
    assert n == 2 ** (k + 1) - 1
    assert abs(F - (n + 2)) < 1e-9


def test_weighted_tree_formula():
    # c^2 = 4/7 weighted tree: F = (n-1)*2*(4/7-1)^2 + n + 2 (exact formula)
    for k in (2, 3, 4):
        c = np.sqrt(4.0 / 7.0)
        n, _ = kunz_tree_trimmed(k)
        expected = (n - 1) * 2 * (4 / 7 - 1) ** 2 + n + 2
        got = weighted_tree_F(k, c, c)
        assert abs(got - expected) < 1e-9


def test_scaled_permutation_minimum_is_five_sevenths():
    t = Fraction(4, 7)
    assert scaled_permutation_defect(t) == E_FREE


def test_unitary_pairs_F_2n():
    rng = np.random.default_rng(11)
    for _ in range(10):
        n = int(rng.integers(1, 12))
        a = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        u1, _ = np.linalg.qr(a)
        b = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
        u2, _ = np.linalg.qr(b)
        assert abs(leavitt_F(u1, u2) - 2 * n) < 1e-9


# -- census: the {7,3} tiling of the Klein quartic ----------------------------
def test_gl3_f2_has_168_elements():
    assert len(gl3_f2()) == 168


def test_census_identity():
    c = census_identity()
    assert c["V"] == 56 and c["E"] == 84 and c["F"] == 24
    assert 7 * c["F"] == 3 * c["V"] == 2 * c["E"] == c["G_order"]
    assert c["chi"] == -4


def test_genus_branches_coincide_only_at_g3():
    br = genus_family_branches()
    for g in (3, 7, 14, 17):
        i_g = br["branch_I"][g]
        ii_g = br["branch_II"][g]
        if g == 3:
            assert abs(i_g - ii_g) < 1e-12
        else:
            assert abs(i_g - ii_g) > 1e-4  # g=7 already separates


# -- convergents: 9/224 is a convergent of the measured c_K3 ------------------
def test_cf_convergents_of_9_224():
    cf = [0, 24, 1, 8]
    convs = convergents_of(cf)
    assert convs[-1] == Fraction(9, 224)
    assert convs == [Fraction(0), Fraction(1, 24), Fraction(1, 25), Fraction(9, 224)]


def test_continued_fraction_deterministic():
    assert continued_fraction(0.5)[:3] == [0, 2]


def test_census_filter_accepts_9_224():
    assert is_census_fraction(Fraction(9, 224))
    assert not is_census_fraction(Fraction(1, 3 * 5))
    assert not is_census_fraction(Fraction(1, 2**7))
