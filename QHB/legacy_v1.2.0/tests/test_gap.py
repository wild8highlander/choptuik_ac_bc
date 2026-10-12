import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from qhb.gap import KAPPA, Q_PK, floquet_gap, lemma_a_worst, static_of_chain


class TestGap:
    def test_static_block(self):
        _E0, _E1, D0, s, _h, _L = static_of_chain()
        assert D0 == pytest.approx(0.523004556028, abs=1e-11)
        assert s == pytest.approx(-1.00398294, abs=1e-6)

    def test_floquet_identity_b0(self):
        _E0, _E1, D0, _s, _h, _L = static_of_chain()
        g, _ = floquet_gap(D0, beta=0.0)
        assert abs(g - D0) < 1e-12

    def test_quadratic_window(self):
        _E0, _E1, D0, _s, _h, _L = static_of_chain()
        g1, _ = floquet_gap(D0, beta=0.05)
        g2, _ = floquet_gap(D0, beta=0.1)
        # pure quadratic on the window: shift(0.1) = 4 * shift(0.05)
        assert abs((g1 - D0) / (g2 - D0) - 0.25) < 0.02

    def test_evenness_b_flip(self):
        from qhb.constants import BERRY_TRIO, BRAKING_TRIO
        _E0, _E1, D0, *_ = static_of_chain()
        b = tuple(0.3 * v for v in BERRY_TRIO)
        a = tuple(0.3 * v for v in BRAKING_TRIO)
        g1, _ = floquet_gap(D0, b=b, a=a)
        g2, _ = floquet_gap(D0, b=tuple(-v for v in b), a=a)
        assert abs(g1 - g2) < 1e-12

    def test_a_only_all_order_zero(self):
        from qhb.constants import BRAKING_TRIO
        _E0, _E1, D0, *_ = static_of_chain()
        g, _ = floquet_gap(D0, b=(0, 0, 0),
                           a=tuple(0.5 * v for v in BRAKING_TRIO))
        assert abs(g - D0) < 1e-12

    def test_lemma_a(self):
        # the committed centred chain for even N IS the worst alignment
        _, q, h, _L = __import__("qhb.gap", fromlist=["parabolic_profile"]) \
            .parabolic_profile(64, KAPPA, Q_PK)
        assert abs(-q.min() - (Q_PK - lemma_a_worst(KAPPA, h))) < 1e-14
