import math
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from qhb.bridge import T_H, equal_cmb_mass, equal_qcd_mass, master_table
from qhb.constants import A_WU_ANCHOR, T_CMB, T_QCD_K
from qhb.ladder import constants_registry
from qhb.trio import (
    GASCHEAU_THRESHOLD,
    gascheau_verdict,
    growth_rate_equal_masses,
    wall_U,
)
from qhb.wu import required_x_for_eta, residual


class TestTrio:
    def test_gascheau_equal_masses(self):
        v = gascheau_verdict()
        assert v["nu"] == pytest.approx(1.0 / 3.0)
        assert v["verdict"] == "UNSTABLE"

    def test_threshold(self):
        assert GASCHEAU_THRESHOLD == pytest.approx(1.0 / 27.0)

    def test_growth(self):
        assert growth_rate_equal_masses() == pytest.approx(
            math.sqrt(1.5), rel=1e-15)

    def test_wall_shape(self):
        assert wall_U(7.0, 8.0, 2.0, 0.0) == 0.0           # inside
        assert wall_U(9.0, 8.0, 2.0, 0.0) == pytest.approx(16.0)  # 2*V0*s^2
        assert wall_U(9.0, 8.0, 2.0, math.pi / 2) == pytest.approx(0.0)


class TestWu:
    def test_limits(self):
        assert residual(0.0, 100.0) == 0.0
        assert residual(0.9, 1e8) == pytest.approx(0.9, abs=1e-7)
        assert residual(0.9, 1e-8) < 1e-7

    def test_anchor(self):
        assert residual(A_WU_ANCHOR, 100.0) == pytest.approx(0.899995686821,
                                                             abs=1e-9)

    def test_eta_scope(self):
        assert 1e-10 < required_x_for_eta(0.9) < 1e-6


class TestBridge:
    def test_qcd_contact(self):
        M = equal_qcd_mass()
        assert M == pytest.approx(6.814006e10, rel=1e-5)
        assert T_H(M) == pytest.approx(T_QCD_K, rel=1e-9)

    def test_cmb_contact(self):
        M = equal_cmb_mass()
        assert M == pytest.approx(4.5015948405e22, rel=1e-6)
        assert T_H(M) == pytest.approx(T_CMB, rel=1e-9)

    def test_master_table_shape(self):
        rows = master_table()
        assert len(rows) == 15
        assert len(rows[0]) == 23

    def test_registry(self):
        reg = constants_registry(0.523, -0.055)
        assert len(reg) == 21
        names = {r[0] for r in reg}
        assert {"bA_berry", "bB_berry", "bC_berry", "aA_braking",
                "M_QCD_kg", "M_CMB_kg"} <= names
