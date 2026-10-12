"""
bridge.py — THE BRIDGE: from engine code units to physical black holes.

The critical-collapse engine (engine/solver.py) works in geometric code
units (4 pi G = 1).  Its committed campaign (campaigns/reference/) yields
a DIMENSIONLESS born spectrum  M_code(eps),  eps = A - A*.

The bridge maps that spectrum onto physical black holes through a single
input scale M_in of the initial pulse:

    M_BH(eps; M_in) = M_in * f~(eps),     f~(eps) = M_code(eps)/M_code_sat

M_code_sat is the saturated (strongly supercritical) horizon mass —
physically the total mass of the pulse — so the dimensionless profile
f~(eps) is the universal object, and the scale is the ONLY input.

Honesty rules:
  * the fixed-grid mass floor is carried, not hidden: rows flagged
    junk/saturated keep their flags;
  * the near-critical power law M ~ eps^gamma is an ANCHOR comparison
    (gamma_Ch = 0.374), never a fit of the committed data;
  * gamma is honestly unmeasurable at committed resolution — the floor
    wins (campaign C3 quantifies this).

Outputs (via scripts/rebuild_data.py):
    data/bridge/born_spectrum.csv          dimensionless spectrum
    data/bridge/bridge_master.csv          the master mapping table
    data/bridge/collapse_verdict_summary.json
"""
import csv
import json
import math
import os

from .constants import (
    BRIDGE_SCALES,
    CAMPAIGN,
    T_CMB,
    b_Ch,
    f_qnm_schwarzschild,
    gamma_Ch,
    k_B,
    kretschmann_horizon,
    kretschmann_planck,
    l_P,
    qnm_rel_shift,
)
from .hawking import (
    P_H,
    S_BH,
    T_H,
    equal_CMB_mass,
    fmt_time,
    r_s,
    rho_mean,
    surface_gravity,
    t_evap,
    t_page,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERDICT_DEFAULT = os.path.join(ROOT, "campaigns", "reference", "c1_verdict.json")


def load_campaign(path=None):
    """Load a campaign verdict JSON (default: the committed C1 verdict)."""
    with open(path or VERDICT_DEFAULT) as f:
        return json.load(f)


def born_spectrum(verdict):
    """Merge the scans of a verdict into one cleaned dimensionless spectrum."""
    rows = []
    for tag in ("scan_N400", "scan_N800"):
        for r in verdict.get(tag, {"rows": []})["rows"]:
            rows.append({
                "grid": verdict[tag]["N"],
                "A": r["A"], "eps": r["eps"], "M_code": r["M_code"],
                "stop": r["stop"], "sane": r.get("sane", False),
            })
    M_sat = max(r["M_code"] for r in rows
                if r["sane"] and math.isfinite(r["M_code"]))
    for r in rows:
        r["f_tilde"] = (r["M_code"] / M_sat
                        if (r["sane"] and math.isfinite(r["M_code"]))
                        else float("nan"))
    return rows, M_sat


def ensemble_members(rows):
    """near_floor / mid / saturated members of the born ensemble (N=800)."""
    sane800 = sorted([r for r in rows if r["grid"] == 800 and r["sane"]],
                     key=lambda r: r["eps"])
    return {
        "near_floor": sane800[0],                       # smallest resolved
        "mid": next(r for r in sane800 if r["eps"] > 1e-2),
        "saturated": max((r for r in rows if r["sane"] and r["grid"] == 400),
                         key=lambda r: r["M_code"]),
    }


def master_table(verdict):
    """Build the master mapping table (list of dicts, SI units)."""
    rows, M_sat = born_spectrum(verdict)
    members = ensemble_members(rows)

    master = []
    for scale_name, M_in in BRIDGE_SCALES:
        for tag, r in members.items():
            M_BH = M_in * r["f_tilde"]
            master.append({
                "input_scale": scale_name,
                "M_in_kg": f"{M_in:.6e}",
                "member": tag,
                "eps": f"{r['eps']:.6g}",
                "f_tilde": f"{r['f_tilde']:.6g}",
                "M_BH_kg": f"{M_BH:.6e}",
                "M_BH_over_M_in": f"{r['f_tilde']:.6g}",
                "r_s_m": f"{r_s(M_BH):.6e}",
                "r_s_over_lP": f"{r_s(M_BH)/l_P:.6e}",
                "T_H_K": f"{T_H(M_BH):.6e}",
                "S_BH_over_kB": f"{S_BH(M_BH)/k_B:.6e}",
                "P_H_W": f"{P_H(M_BH):.6e}",
                "t_evap_s": f"{t_evap(M_BH):.6e}",
                "t_evap_human": fmt_time(t_evap(M_BH)),
                "t_Page_s": f"{t_page(M_BH):.6e}",
                "t_Page_human": fmt_time(t_page(M_BH)),
                "rho_mean_kg_m3": f"{rho_mean(M_BH):.6e}",
                "surface_grav_m_s2": f"{surface_gravity(M_BH):.6e}",
                "f_QNM_l2_Hz": f"{f_qnm_schwarzschild(M_BH):.6e}",
                "f_QNM_corr_Hz": f"{f_qnm_schwarzschild(M_BH)*(1-qnm_rel_shift):.6e}",
                "K_horizon_m4": f"{kretschmann_horizon(M_BH):.6e}",
                "K_horizon_over_KP": f"{kretschmann_horizon(M_BH)/kretschmann_planck():.6e}",
                "T_H_over_T_CMB": f"{T_H(M_BH)/T_CMB:.6e}",
            })
    return master, members, M_sat


def write_outputs(verdict, out_dir):
    """Write born_spectrum.csv, bridge_master.csv and the verdict summary."""
    os.makedirs(out_dir, exist_ok=True)
    rows, M_sat = born_spectrum(verdict)
    members = ensemble_members(rows)

    with open(os.path.join(out_dir, "born_spectrum.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["grid", "A", "eps", "M_code",
                                          "f_tilde", "stop", "sane"])
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.8g}" if isinstance(r[k], float) else r[k])
                        for k in w.fieldnames})

    master, _, _ = master_table(verdict)
    fields = list(master[0].keys())
    with open(os.path.join(out_dir, "bridge_master.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(master)

    sane800 = sorted([r for r in rows if r["grid"] == 800 and r["sane"]],
                     key=lambda r: r["eps"])
    # v2.0.1 remediation (F-1): the reference is the remediated ladder
    # (campaigns/reference/a_star_ladder.json); the threshold drifts with
    # resolution — honesty over agreement claims.
    a_star_ref_1600 = CAMPAIGN["a_star_reference_N1600"]
    summary = {
        "campaign": "C1",
        "a_star_grid": {k: v["a_star"] for k, v in verdict["a_star_grid"].items()},
        "a_star_reference_N1600": a_star_ref_1600,
        "a_star_drift_N800_vs_reference": abs(
            verdict["a_star_grid"]["N800"]["a_star"] - a_star_ref_1600),
        "roberts_convergence_orders": [v.get("convergence_order_r")
                                       for v in verdict["validation"][1:]],
        "M_code_sat": M_sat,
        "mass_floor_N800_code": sane800[0]["M_code"],
        "f_tilde_range_resolved": [sane800[0]["f_tilde"], 1.0],
        "gamma_campaign": "honestly unmeasurable: fixed-grid floor dominates " +
                          "(C3 floor-biased gamma_eff = 0.005 +- 0.035 at " +
                          "N=800; C3b per-grid remediation concurs: 0.041 / " +
                          "0.060 at N=1600/3200, floor-dominated)",
        "gamma_Ch_anchor": gamma_Ch,
        # v2.2.0: the former "b_Ch_lit" key (b_Ch rounded to 5 digits, once
        # labeled a "literature anchor") is removed — a hypothesis constant
        # must not travel under a literature label.  The 0.67% comparison is
        # |gamma_Ch - b_Ch| / b_Ch and lives in the docs, not in this table.
        "b_Ch": b_Ch,
        "junk_rows": verdict["honest_notes"]["junk_rows_total"],
        "M_CMB_kg": equal_CMB_mass(),
        "members": {k: {"eps": v["eps"], "f_tilde": v["f_tilde"],
                        "M_code": v["M_code"]} for k, v in members.items()},
    }
    with open(os.path.join(out_dir, "collapse_verdict_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary
