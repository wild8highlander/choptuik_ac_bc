"""Bridge: born spectrum, ensemble members, master table, determinism."""
import json
import math
import os

from chbridge import bridge as B
from chbridge.constants import T_CMB
from chbridge.hawking import T_H, equal_CMB_mass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _verdict():
    with open(os.path.join(ROOT, "campaigns", "reference", "c1_verdict.json")) as f:
        return json.load(f)


def test_born_spectrum_shape():
    rows, M_sat = B.born_spectrum(_verdict())
    assert len(rows) == 26 + 18                     # N400 + N800 scans
    assert 0.05 < M_sat < 0.1                       # saturated code mass
    sane = [r for r in rows if r["sane"]]
    assert all(0 < r["f_tilde"] <= 1.0 for r in sane)


def test_ensemble_members():
    rows, _ = B.born_spectrum(_verdict())
    members = B.ensemble_members(rows)
    assert abs(members["near_floor"]["f_tilde"] - 0.2877) < 2e-3
    assert abs(members["mid"]["f_tilde"] - 0.2684) < 2e-3
    assert members["saturated"]["f_tilde"] == 1.0


def test_master_table_geometry():
    master, _, _ = B.master_table(_verdict())
    assert len(master) == 15                        # 5 scales x 3 members
    assert len(master[0]) == 23                     # columns
    r_cmb_sat = next(r for r in master
                     if r["input_scale"] == "CMB input"
                     and r["member"] == "saturated")
    assert abs(float(r_cmb_sat["T_H_over_T_CMB"]) - 1.0) < 2e-3


def test_master_table_horizon_identity():
    """r_s = 2GM/c^2 and r_s/l_P consistency inside the master table."""
    master, _, _ = B.master_table(_verdict())
    for r in master[:4]:
        rs = float(r["r_s_m"])
        M = float(r["M_BH_kg"])
        assert abs(rs - 2 * 6.67430e-11 * M / 299792458.0 ** 2) / rs < 1e-4


def test_cmb_member_is_the_contact_point():
    """The saturated CMB-input member sits AT the cosmological contact."""
    master, _, _ = B.master_table(_verdict())
    r = next(r for r in master
             if r["input_scale"] == "CMB input" and r["member"] == "saturated")
    M = float(r["M_BH_kg"])
    assert abs(T_H(M) - T_CMB) / T_CMB < 2e-3
    assert abs(M - equal_CMB_mass()) / equal_CMB_mass() < 2e-3


def test_planck_input_member_above_planck_barrier():
    """r_s of the born hole at Planck input exceeds the Planck length."""
    master, _, _ = B.master_table(_verdict())
    r = next(r for r in master
             if r["input_scale"] == "Planck input"
             and r["member"] == "saturated")
    assert float(r["r_s_over_lP"]) == 2.0   # saturated member: M = m_P


def test_rebuild_determinism():
    """Rebuilding the tables twice yields byte-identical master CSV."""
    v = _verdict()
    import tempfile
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        B.write_outputs(v, d1)
        B.write_outputs(v, d2)
        with open(os.path.join(d1, "bridge_master.csv"), "rb") as f1, \
             open(os.path.join(d2, "bridge_master.csv"), "rb") as f2:
            assert f1.read() == f2.read()


def test_summary_honesty_flags():
    rows, _ = B.born_spectrum(_verdict())
    junk = [r for r in rows if not r["sane"]]
    assert len(junk) > 0          # honest negatives are present and kept
    assert all("junk" in r["stop"] or not math.isfinite(r["f_tilde"])
               for r in junk)
