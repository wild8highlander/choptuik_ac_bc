# -*- coding: utf-8 -*-
import json
import math
import os
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)


def load_c2():
    with open(os.path.join(ROOT, "campaigns", "reference", "c2_verdict.json"),
              encoding="utf-8") as fh:
        return json.load(fh)


class TestEngine:
    def test_kepler(self):
        from engine.solver import kepler_period_check
        Tk, Tm, err = kepler_period_check()
        assert Tm is not None and err < 1e-6

    def test_ensemble_determinism(self):
        import numpy as np
        from engine.solver import make_ensemble
        p1, v1, r1 = make_ensemble(20)
        p2, v2, r2 = make_ensemble(20)
        assert r1 == r2
        assert np.array_equal(p1, p2) and np.array_equal(v1, v2)

    def test_energy_drift_free(self):
        import numpy as np
        from engine.solver import make_ensemble, trio_run
        pos, vel, _ = make_ensemble(60)
        r = trio_run(pos, vel, V0=0.0)
        assert r["E_drift_rel"] < 1e-3

    def test_trap_seals_single_cell(self):
        import numpy as np
        from engine.solver import make_ensemble, trio_run
        pos, vel, _ = make_ensemble(60)
        r = trio_run(pos, vel, V0=8.0, Omega=2.0)
        assert r["escaped"].mean() < 0.05


class TestValidate:
    def test_validate_all_pass(self):
        r = subprocess.run([sys.executable, "-m", "qhb.validate"],
                           cwd=ROOT, capture_output=True, text=True)
        assert "9/9 checks PASS" in r.stdout, r.stdout


class TestData:
    def test_rebuild_byte_deterministic(self, tmp_path):
        # the rebuild script writes into data/qhb; verify determinism by
        # checksumming twice
        script = os.path.join(ROOT, "scripts", "rebuild_data.py")
        import hashlib

        def digest():
            h = hashlib.sha256()
            for name in sorted(os.listdir(os.path.join(ROOT, "data", "qhb"))):
                with open(os.path.join(ROOT, "data", "qhb", name), "rb") as fh:
                    h.update(fh.read())
            return h.hexdigest()
        d1 = digest()
        subprocess.run([sys.executable, script], cwd=ROOT, check=True,
                       capture_output=True)
        d2 = digest()
        subprocess.run([sys.executable, script], cwd=ROOT, check=True,
                       capture_output=True)
        d3 = digest()
        assert d1 == d2 == d3


class TestTwins:
    def test_js_twin(self):
        out = os.path.join(ROOT, "multilang", "javascript",
                           "reference_output.txt")
        with open(out, encoding="utf-8") as fh:
            assert "14/14 checks PASS" in fh.read()

    def test_c_twin(self):
        out = os.path.join(ROOT, "multilang", "c", "reference_output.txt")
        with open(out, encoding="utf-8") as fh:
            assert "14/14 checks PASS" in fh.read()

    def test_cpp_twin(self):
        out = os.path.join(ROOT, "multilang", "cpp", "reference_output.txt")
        with open(out, encoding="utf-8") as fh:
            assert "14/14 checks PASS" in fh.read()
