# -*- coding: utf-8 -*-
"""Unit pins of the classical vortex layer (qhb.vortex) and the Evidence
Engine registry (results/claims_registry.json)."""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qhb.vortex import (lagrange_omega, relative_equilibrium_omega,
                        circumradius, equilateral_positions, aref_launch,
                        invariants_of, kirchhoff_run, linearize_triangle_exact,
                        triangle_shape_error)
from qhb.claims import load_registry, validate, STATUSES


class TestVortexExact:
    def test_omega_exact(self):
        assert lagrange_omega(1.0, 1.0) == pytest.approx(3.0 / (2.0 * math.pi),
                                                         rel=1e-15)
        assert relative_equilibrium_omega((1.0, 1.0, 1.0)) \
            == pytest.approx(3.0 / (2.0 * math.pi), rel=1e-15)

    def test_circumradius(self):
        assert circumradius(1.0) == pytest.approx(1.0 / math.sqrt(3.0))

    def test_equilateral_separations(self):
        p = equilateral_positions()
        for i, j in ((0, 1), (1, 2), (2, 0)):
            assert np.hypot(*(p[i] - p[j])) == pytest.approx(1.0, abs=1e-12)

    def test_aref_invariants_machine_zero(self):
        pos, g = aref_launch()
        inv = invariants_of(pos, g)
        assert max(abs(v) for v in inv.values()) < 1e-15

    def test_exact_linearization_spectrum(self):
        ev, omega, _ = linearize_triangle_exact()
        imag = [e for e in ev if abs(e.imag) > 1e-6]
        zero = [e for e in ev if abs(e.imag) <= 1e-6]
        assert len(imag) == 4 and len(zero) == 2
        assert max(abs(e.real) for e in imag) < 1e-12
        for e in imag:
            assert abs(abs(e.imag) - omega) < 1e-9
        assert max(abs(e) for e in zero) < 1e-6


class TestVortexMeasured:
    def test_short_run_invariants(self):
        pos, g = aref_launch()
        res = kirchhoff_run(pos, g, dt=1e-3, steps=1000)
        inv0 = invariants_of(pos, g)
        inv1 = invariants_of(res["pos"], g)
        assert max(abs(inv1[k] - inv0[k]) for k in inv0) < 1e-12

    def test_triangle_rigidity_short(self):
        res = kirchhoff_run(equilateral_positions(), np.array([1.0, 1.0, 1.0]),
                            dt=1e-3, steps=2000)
        assert triangle_shape_error(res["pos"], 1.0) < 1e-10


class TestClaimsRegistry:
    @pytest.fixture(scope="class")
    def reg(self):
        return load_registry()

    def test_schema(self, reg):
        assert reg["schema"] == "qhb.claims/1.0"
        assert reg["project_version"] == "1.2.0"

    def test_validation_passes(self, reg):
        ok, errors, claims = validate(reg)
        assert ok, errors
        assert len(claims) >= 25

    def test_statuses_covered(self, reg):
        statuses = {c["status"] for c in reg["claims"]}
        assert statuses == set(STATUSES)

    def test_hypothesis_marker_present(self, reg):
        hyp = [c for c in reg["claims"] if c["status"] == "hypothesis"]
        assert len(hyp) == 1
        assert "MARKED HYPOTHESIS" in hyp[0]["statement"]

    def test_negatives_in_registry(self, reg):
        neg = [c for c in reg["claims"]
               if c["status"] == "honest-negative"]
        assert len(neg) >= 5
        ids = {c["id"] for c in neg}
        assert {"CLM-06", "CLM-09", "CLM-13", "CLM-19"} <= ids

    def test_uncertainty_budget_complete(self, reg):
        fields = {"statistical", "discretization", "solver", "parameter",
                  "model"}
        for c in reg["claims"]:
            assert set(c["uncertainty"].keys()) == fields
