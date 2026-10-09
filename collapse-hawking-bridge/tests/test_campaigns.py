# -*- coding: utf-8 -*-
"""Campaigns C2, C3b and C6: the committed verdicts, pinned.

The pins assert the *committed machine outputs* (campaigns/reference/).
If a campaign is re-run and a pin fails, the verdict genuinely changed —
treat it as a bug or a CHANGELOG event, never as a reason to edit the
test silently.

2.0.1 CHANGELOG event: C3b regenerated with per-grid thresholds (audit
finding F-2); the 2.0.0 gamma/floor pins were artifacts of the eps
mislabeled by +2.8e-3 and are replaced by the remediated values.

2.1.0 CHANGELOG event: campaign C6 added — the resolution-drift law
(theorem T10, parabolic-tension mechanism); verdict c6_drift_verdict.json
pinned (ladder facts, lemma precision, channel shares, honest negatives).
"""
import csv
import json
import math
import os

import chbridge.constants as K

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "campaigns", "reference")
DATA = os.path.join(ROOT, "data", "bridge")


def _verdict(name):
    with open(os.path.join(REF, name)) as f:
        return json.load(f)


def _c2():
    return _verdict("c2_verdict.json")


def _c3b():
    return _verdict("c3b_verdict.json")


def _c6():
    return _verdict("c6_drift_verdict.json")


# ---------------------------------------------------------------------------
# verdict envelopes
# ---------------------------------------------------------------------------
def test_c2_verdict_envelope():
    v = _c2()
    assert v["campaign"] == "chb_c2"
    assert v["project_version"] == "2.1.0"
    assert v["grid"]["N"] == 800
    assert isinstance(v["wall_total_s"], float) and v["wall_total_s"] > 0
    assert v["timestamp"]


def test_c3b_verdict_envelope():
    v = _c3b()
    assert v["campaign"] == "chb_c3b"
    assert v["project_version"] == "2.1.0"
    # F-2 remediation: per-grid thresholds committed with the verdict
    assert "a_star_per_grid" in v
    assert abs(v["a_star_per_grid"]["N1600"]["a_star"]
               - 0.0777443361282349) < 1e-12
    assert abs(v["a_star_per_grid"]["N3200"]["a_star"]
               - 0.07682177066802981) < 1e-12
    lad = v["gamma_ladder"]
    assert abs(lad["N1600"]["a_star_used"]
               - v["a_star_per_grid"]["N1600"]["a_star"]) < 1e-15
    assert isinstance(v["wall_total_s"], float) and v["wall_total_s"] > 0


def test_all_verdicts_carry_project_version():
    for name in ("c1_verdict.json", "c2_verdict.json",
                 "c3_verdict.json", "c3b_verdict.json",
                 "c6_drift_verdict.json"):
        assert _verdict(name)["project_version"] == "2.1.0", name


# ---------------------------------------------------------------------------
# C2 — subcritical branch
# ---------------------------------------------------------------------------
def test_c2_subcritical_rows():
    sub = _c2()["subcritical"]
    rows = sub["rows"]
    assert sub["n_runs"] == 13
    assert len(rows) == 13
    assert sub["flipped_runs"] == 0
    assert all(not r["flipped"] for r in rows)
    assert all(0.0 < r["q_max"] < 2.0 for r in rows)


def test_c2_compactness_approaches_threshold():
    """q_max grows monotonically as eps -> 0 (approach to the horizon)."""
    rows = sorted(_c2()["subcritical"]["rows"], key=lambda r: r["eps"])
    q = [r["q_max"] for r in rows]
    assert all(a > b for a, b in zip(q[:-1], q[1:]))   # q falls as eps grows
    assert q[0] < 1.0                       # still subcritical at the floor


def test_c2_slowdown_fit():
    fit = _c2()["subcritical"]["slowdown_fit"]
    assert fit["n_points"] == 13
    assert fit["slope_ln_eps"] < 0.0        # v_qmax grows as eps -> 0
    assert fit["r2"] > 0.5


def test_c2_echo_rate_below_anchor():
    """Echo accumulation rate: measured, compared with 1/Delta = 0.2907."""
    fit = _c2()["subcritical"]["echo_rate_fit"]
    assert 0.0 < fit["echoes_per_efold"] < 1.0 / K.echo_delta
    assert abs(fit["echoes_per_efold"] - 0.1908986733640667) < 1e-9


# ---------------------------------------------------------------------------
# C2 — supercritical bifurcation
# ---------------------------------------------------------------------------
def test_c2_bifurcation_summary():
    s = _c2()["bifurcation"]["summary"]
    assert 0.01 < s["M_sat_N800"] < 0.1
    assert 1e-4 < s["eps_half"] < 1e-1
    assert abs(s["eps_half"] - 0.004859801757908699) < 1e-12
    assert abs(s["M_sat_N800"] - 0.03518978551089466) < 1e-12


def test_c2_bifurcation_rows_keep_junk():
    rows = _c2()["bifurcation"]["rows"]
    assert len(rows) == 13
    junk = [r for r in rows if not r["sane"]]
    assert len(junk) >= 1                   # honest junk kept, never dropped
    sane_max = max(r["M_code"] for r in rows if r["sane"])
    f_sat = [r for r in rows if r["sane"] and r["M_code"] == sane_max][0]
    assert abs(f_sat["f_tilde"] - 1.0) < 1e-12   # M_sat normalises the scan


def test_c2_constants_mirror_verdict():
    """Part C of constants.py is a byte-faithful mirror of the verdicts."""
    c2 = _c2()
    Kv = K.CAMPAIGN
    assert Kv["eps_half_N800"] == c2["bifurcation"]["summary"]["eps_half"]
    assert Kv["mass_saturation_N800_c2"] == \
        c2["bifurcation"]["summary"]["M_sat_N800"]
    assert Kv["slowdown_slope_ln_eps"] == \
        c2["subcritical"]["slowdown_fit"]["slope_ln_eps"]
    assert Kv["echo_rate_per_efold"] == \
        c2["subcritical"]["echo_rate_fit"]["echoes_per_efold"]


# ---------------------------------------------------------------------------
# C3b — concentrated resolution
# ---------------------------------------------------------------------------
def test_c3b_floor_ladder_sinks():
    """The mass floor drops with resolution: 0.0155 (N=800) -> 8.6e-3 -> 4.2e-3.

    v2.0.1: floors from the per-grid-remediated scan (F-2).
    """
    lad = _c3b()["gamma_ladder"]
    f16 = lad["N1600"]["floor_M"]
    f32 = lad["N3200"]["floor_M"]
    assert 0.0155 > f16 > f32 > 0.0
    assert abs(f16 - 8.574765176255137e-03) < 1e-12
    assert abs(f32 - 4.244867407885677e-03) < 1e-12


def test_c3b_gamma_fit_floor_biased():
    """gamma_eff stays far below the anchor: the floor still governs the band.

    v2.0.1 (F-2): with per-grid thresholds the fits are floor-dominated
    (r2 < 0.5) and gamma_eff does NOT approach gamma_Ch = 0.374 — the C3
    honest negative stands; the 2.0.0 values (0.111/0.121, r2 0.82/0.96)
    were artifacts of the mislabeled eps axis.
    """
    lad = _c3b()["gamma_ladder"]
    g16, g32 = lad["N1600"], lad["N3200"]
    assert 0.0 < g16["gamma_eff"] < K.gamma_Ch
    assert 0.0 < g32["gamma_eff"] < K.gamma_Ch
    assert abs(g16["gamma_eff"] - 0.041024561830928216) < 1e-12
    assert abs(g32["gamma_eff"] - 0.06045204623387996) < 1e-12
    assert g16["r2"] < 0.5 and g32["r2"] < 0.5   # floor-dominated, honestly weak


def test_c3b_delta_honest_negative():
    """No run at any depth resolved >= 3 peaks: C3's negative stands."""
    v = _c3b()
    assert v["delta_eff"] is None
    assert v["products"]["P_engine_deep"] is None
    assert v["products"]["P_engine_deep_verdict"] is None
    for rows in v["delta_ladder"].values():
        for r in rows:
            assert r["n_peaks"] < 3


def test_c3b_anchor_product_passes():
    p = _c3b()["products"]
    assert abs(p["P_anchor"] - 1.28656) < 1e-9
    assert p["P_anchor_verdict"] == "PASS"


def test_c3b_constants_mirror_verdict():
    Kv = K.CAMPAIGN
    lad = _c3b()["gamma_ladder"]
    assert Kv["gamma_eff_N1600_c3b"] == lad["N1600"]["gamma_eff"]
    assert Kv["gamma_eff_N3200_c3b"] == lad["N3200"]["gamma_eff"]


# ---------------------------------------------------------------------------
# derived campaign tables
# ---------------------------------------------------------------------------
def test_campaign_tables_exist_and_match():
    with open(os.path.join(DATA, "campaign_c2_subcritical.csv")) as f:
        sub = list(csv.DictReader(f))
    assert len(sub) == 13
    assert float(sub[0]["q_max"]) > 0

    with open(os.path.join(DATA, "campaign_c2_bifurcation.csv")) as f:
        bif = list(csv.DictReader(f))
    assert len(bif) == 13
    assert any(r["sane"] == "False" for r in bif)   # junk kept in the table too

    with open(os.path.join(DATA, "campaign_c3b_ladder.csv")) as f:
        lad = list(csv.DictReader(f))
    assert len(lad) == 12                    # 7 rows at N=1600 + 5 rows at N=3200
    assert {r["N"] for r in lad} == {"1600", "3200"}


def test_c3b_gamma_ladder_csv_sane_counts():
    with open(os.path.join(DATA, "campaign_c3b_ladder.csv")) as f:
        lad = list(csv.DictReader(f))
    n1600 = [r for r in lad if r["N"] == "1600"]
    n3200 = [r for r in lad if r["N"] == "3200"]
    assert len(n1600) == 7 and len(n3200) == 5
    assert all(r["sane"] in ("True", "False") for r in lad)


# ---------------------------------------------------------------------------
# C6 — the resolution-drift law (theorem T10)
# ---------------------------------------------------------------------------
def test_c6_ladder_facts():
    """The committed ladder drifts from above, faster than 1/N, p_eff climbing."""
    v = _c6()
    la = v["ladder_analysis"]
    assert la["monotone_from_above"] is True
    assert la["p_eff_strictly_climbing"] is True
    assert la["faster_than_1_over_N"] is True
    assert abs(la["drift_N800_to_N1600"] - 2.7895164e-3) < 1e-9
    assert abs(la["drift_N1600_to_N3200"] - 9.225655e-4) < 1e-9
    assert len(la["ladder"]) == 5 and len(la["per_doubling_drifts"]) == 4
    # measured p_eff trajectory committed in constants as well
    for got, want in zip(la["p_eff_measured"],
                         (1.140, 1.459, 1.596)):
        assert abs(got - want) < 5e-3


def test_c6_lemmas_machine_precision():
    """Lemma A (flattening) and Lemma B (tension/arc) verified exactly."""
    v = _c6()
    checks = v["parabola_checks"]
    assert len(checks) == 5
    assert max(c["worst_relerr"] for c in checks) < 1e-7
    assert max(c["mean_relerr"] for c in checks) < 1e-12
    assert max(c["chord_sum_closed_form_relerr"] for c in checks) < 1e-12
    # every chord chain must be SHORTER than the arc (compression under tension)
    assert all(c["arc_rel_deficit"] > 0 for c in checks)


def test_c6_honest_negatives_and_channel():
    """No A_inf claim; the exact channel is real, positive and sub-dominant."""
    v = _c6()
    st = v["extrapolation_stress_test"]
    assert st["trajectory_incompatible"] is True
    assert "REJECTED" in st["verdict"]
    assert st["r2"] > 0.999                      # descriptive fit is good...
    chan = v["channel_decomposition"]
    assert all(c["flattening_channel_dA"] > 0 for c in chan)
    assert all(c["share"] < 0.05 for c in chan)  # ...but sub-dominant
    assert abs(v["tension_calibration"]["kappa_code"]
               - K.CAMPAIGN["drift_kappa_star"]) < 1e-9
    assert abs(v["sensitivity_calibration"]["sensitivity_s_per_code_unit"]
               - K.CAMPAIGN["drift_sensitivity_s"]) < 1e-6
