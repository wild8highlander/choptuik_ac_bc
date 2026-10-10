"""Evidence Engine, IVP-12 audit, data tables, twins, determinism."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def d(name):
    return json.loads((DATA / name).read_text())


def test_claims_registry_30():
    reg = json.loads((DATA / "claims.json").read_text())
    assert reg["summary"]["n_claims"] == 30
    st = reg["summary"]["by_status"]
    assert st["exact"] == 7
    assert st["measured-law"] == 12
    assert st["honest-negative"] == 9
    assert st["hypothesis"] == 1
    assert st["comparison"] == 1


def test_claims_have_falsifiers_and_budgets():
    reg = json.loads((DATA / "claims.json").read_text())["claims"]
    for c in reg:
        assert c["falsifier"] and len(c["budget"]) == 5
        assert c["status"] in {"exact", "measured-law", "honest-negative",
                              "hypothesis", "comparison"}
        assert c["ru"] and c["en"]


def test_ivp12_all_pass():
    a = d("audit_ivp12.json")
    assert a["n_ivp"] == 12 and a["all_pass"] and a["n_pass"] == 12


def test_ivp11_symbolic_poly():
    a = d("audit_ivp12.json")
    assert a["ivps"]["IVP-11"]["poly_ok"] is True
    assert "lam**2*(4*pi**2*lam**2 + 9)**2" in a["ivps"]["IVP-11"]["charpoly"]


def test_deep_checks_100d():
    dc = d("deep_checks.json")
    assert len(dc["omega_100d"].split(".")[-1]) >= 95
    assert dc["margin_100d"].startswith("148997540.98")
    assert dc["c9_jackknife_pass"] is True


def test_twin_check_51():
    tw = d("twins.json")
    assert tw["n_checks"] == 51 and tw["pairs"] == 14 and tw["sweeps"] == 3
    assert tw["all_pass"]


def test_determinism():
    rb = d("rebuild_hashes.json")
    assert rb["deterministic"] and rb["n_drift"] == 0 and rb["n_tables"] >= 30


@pytest.mark.parametrize("name", [
    "c1_gap_grid.json", "c2_sigma_scan.json", "c3_spin_constants.json",
    "c3_bridge_scan.json", "c4_tail_audit.json", "c5_free_three_body.json",
    "c6_y_spectrum.json", "c7_wkb_window.json", "c8_bootstrap.json",
    "c9_phase_grid.json", "c9_valley.json", "c9_naive_falsifier.json",
    "c10_shares.json", "c10_braking.json", "c10_out_of_window.json",
    "c11_rotation.json", "c11_aref_run.json", "c11_barrier_scan.json",
    "c11_escape_scan.json", "c11_spectrum.json", "c12_profiles.json",
    "c12_phase_grid.json", "c12_margin.json", "c12_fill_dynamics.json",
    "c12_nugget_bound.json", "c12_summary.json", "claims.json",
    "audit_ivp12.json", "deep_checks.json", "twins.json", "rebuild_hashes.json",
])
def test_json_valid(name):
    obj = json.loads((DATA / name).read_text())
    assert isinstance(obj, (dict, list))


def test_manifest_numbers():
    c9 = d("c9_phase_grid.json")
    assert c9["all_open"]
    v = d("c9_valley.json")
    assert v["beta_star"] == pytest.approx(3.3583, abs=1e-9)
    m = d("c12_margin.json")
    assert m["margin"] == pytest.approx(148997540.98, abs=1e4)
    e = d("c11_escape_scan.json")
    assert e["escapes"] == 0 and e["V_star"] == 0.9359375
