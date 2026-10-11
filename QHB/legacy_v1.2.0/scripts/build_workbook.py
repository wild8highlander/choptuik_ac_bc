"""
build_workbook.py — tables/qhb_workbook.xlsx: the offline book of the
package (14 sheets), rebuilt byte-deterministically from data/qhb and
the committed verdicts.  Ink & Gold header styling (workbook_style).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from workbook_style import PAL, header_fill, header_font, thin_border, zebra_fill

DATA = os.path.join(ROOT, "data", "qhb")
OUT = os.path.join(ROOT, "tables", "qhb_workbook.xlsx")


def load_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")
    header = lines[0].split(",")
    rows = []
    for ln in lines[1:]:
        vals = ln.split(",")
        row = {}
        for c, v in zip(header, vals):
            try:
                row[c] = float(v) if v and not v.startswith(("Planck", "QCD",
                        "Asteroid", "CMB", "Solar", "near", "mid", "sat",
                        "Lambda", "T_QCD", "gap", '"')) else v
            except ValueError:
                row[c] = v
        rows.append(row)
    return header, rows


def load_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def sheet(wb, title, header, rows, widths=None):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border
    for i, r in enumerate(rows):
        ws.append([r.get(c, "") for c in header])
        for c in ws[i + 2]:
            c.fill = zebra_fill(i)
            c.border = thin_border
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A2"
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # 1. README sheet
    ws = wb.create_sheet("README")
    readme = [
        ["Quark-Hawking Bridge — offline workbook", ""],
        ["version", "1.1.0"],
        ["source", "data/qhb/* (rebuilt from campaigns/reference)"],
        ["", ""],
        ["sheet", "content"],
        ["constants", "the dimensionless registry (exact + anchors)"],
        ["master_table", "15 rows x 23 columns of the bridge"],
        ["gap_scan", "the C1 gap law window + wing"],
        ["gap_per_sector", "B2 of the three septinial sectors"],
        ["trap_grid", "the C2 escape map (V0 x Omega)"],
        ["lyapunov", "bound chaos: free vs trapped exponents"],
        ["wu_grid", "the C3 residual map (alpha x x)"],
        ["floor_ladder", "the C4 spectral floor ladder"],
        ["drift_ladder", "the C5 gap-drift ladder"],
        ["drift_law", "C5 fit + exact channel share"],
        ["mapping_branches", "the C6 three-branch physical mapping"],
        ["anharmonic_free", "the C7 free sigma-ladder (the flux tube seals)"],
        ["anharmonic_grid", "the C7 sealing grid (sigma x V0 x Omega)"],
        ["pairwise", "the C8 pairwise door vs the linear door"],
        ["honest_negatives", "the carried negatives of the package"],
    ]
    for r in readme:
        ws.append(r)
    ws["A1"].font = Font(bold=True, size=14, color=PAL["accent"])
    for row in ws.iter_rows(min_row=5, max_row=5):
        for c in row:
            c.font = header_font
            c.fill = header_fill
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 70

    # 2. constants registry
    hdr, rows = load_csv("qhb_constants.csv")
    sheet(wb, "constants", hdr, rows, [20, 34, 26, 30])

    # 3. master table
    hdr, rows = load_csv("bridge_master.csv")
    sheet(wb, "master_table", hdr, rows,
          [24] + [15] * (len(hdr) - 1))

    # 4. gap scan
    d = load_json("gap_scan_window.json")
    rows = [{"beta": b, "gap": g, "shift": s}
            for b, g, s in zip(d["beta"], d["gap"], d["shift"])]
    for b, s in zip(d["wing_betas"], d["wing_shifts"]):
        rows.append({"beta": b, "gap": "", "shift": s})
    sheet(wb, "gap_scan", ["beta", "gap", "shift"], rows, [12, 18, 18])

    # 5. per-sector
    d = load_json("gap_per_sector.json")
    sheet(wb, "gap_per_sector", ["sector", "B2"],
          [{"sector": k, "B2": v} for k, v in d.items()], [16, 20])

    # 6. trap grid
    hdr, rows = load_csv("trap_grid.csv")
    sheet(wb, "trap_grid", hdr, rows, [10, 10, 14, 14, 12])

    # 7. lyapunov
    d = load_json("trap_lyapunov.json")
    sheet(wb, "lyapunov", ["ensemble", "median", "mean"],
          [{"ensemble": "free (V0=0)", "median": d["free"]["median"],
            "mean": d["free"]["mean"]},
           {"ensemble": "trap (V0=8, Omega=2)",
            "median": d["trap_V08_Om2"]["median"],
            "mean": d["trap_V08_Om2"]["mean"]}], [22, 14, 14])

    # 8. wu grid
    hdr, rows = load_csv("wu_residual_grid.csv")
    sheet(wb, "wu_grid", hdr, rows, [10, 10, 14, 14, 14])

    # 9. floor ladder
    hdr, rows = load_csv("floor_ladder.csv")
    sheet(wb, "floor_ladder", hdr, rows, [10, 12, 12, 14, 14, 14, 10])

    # 10. drift ladder
    hdr, rows = load_csv("drift_ladder.csv")
    sheet(wb, "drift_ladder", hdr, rows, [8, 16, 18])

    # 11. drift law
    d = load_json("drift_law.json")
    rows = [{"quantity": "p_eff", "value": ", ".join(
        f'{p["pair"]}: {p["p"]:.4f}' for p in d["p_eff"])},
        {"quantity": "Delta_cont_fit (NOT claimed)",
         "value": d["fit"]["Delta_cont_fit"]},
        {"quantity": "C_measured", "value": d["fit"]["C_measured"]},
        {"quantity": "C_exact = s*kappa/8",
         "value": d["exact_channel"]["C_exact_s_kappa_over_8"]},
        {"quantity": "exact-channel share",
         "value": d["exact_channel"]["share_of_measured"]}]
    sheet(wb, "drift_law", ["quantity", "value"], rows, [34, 60])

    # 11b. mapping branches (C6)
    hdr, rows = load_csv("mapping_branches.csv")
    sheet(wb, "mapping_branches", hdr, rows,
          [18] + [15] * (len(hdr) - 1))

    # 11c. anharmonic trio (C7): the free sigma-ladder and the grid
    hdr_f, rows_f = load_csv("anharmonic_free.csv")
    sheet(wb, "anharmonic_free", hdr_f, rows_f, [12, 14, 12, 12, 14])
    hdr_g, rows_g = load_csv("anharmonic_grid.csv")
    sheet(wb, "anharmonic_grid", hdr_g, rows_g, [12, 10, 10, 14, 12, 12])

    # 12. pairwise door (C8)
    hdr_p, rows_p = load_csv("pairwise_residual.csv")
    sheet(wb, "pairwise", hdr_p, rows_p, [10, 12, 16, 20])

    # 13. the phase map (C9): valley + counterexample
    hdr_v, rows_v = load_csv("phase_valley.csv")
    sheet(wb, "phase_valley", hdr_v, rows_v, [10, 14, 14, 12])
    ce = load_json("phase_counterexample.json")
    sheet(wb, "phase_counterexample",
          ["quantity", "value"],
          [{"quantity": "B2 (committed window)", "value": ce["B2_committed"]},
           {"quantity": "beta_c (naive closure forecast)",
            "value": ce["beta_c_quadratic_forecast"]},
           {"quantity": "Delta_F measured at beta_c",
            "value": ce["Delta_F_measured_at_beta_c"]},
           {"quantity": "ratio to the detector floor",
            "value": ce["ratio_to_floor"]}],
          [40, 20])

    # 14. the causal map (C10): ablation + forecast
    hdr_a, rows_a = load_csv("ablation.csv")
    sheet(wb, "ablation", hdr_a, rows_a, [12, 16, 16, 16])
    hdr_fc, rows_fc = load_csv("forecast.csv")
    sheet(wb, "forecast", hdr_fc, rows_fc, [10, 16, 18, 14, 14])

    # 15. the vortex anchor and the static barrier (C11)
    hdr_b, rows_b = load_csv("barrier_cells.csv")
    sheet(wb, "barrier_cells", hdr_b, rows_b,
          [8, 8, 12, 12, 18, 16, 14, 16])
    va = load_json("vortex_anchor.json")
    rows_t11 = [{"quantity": k, "value": v} for k, v in [
        ("omega_exact (3/(2pi))", va["T11_spectrum"]["omega_exact"]),
        ("max |Re| on the imaginary pairs",
         va["T11_spectrum"]["max_re_on_imag_pairs"]),
        ("charpoly identity dev",
         va["T11_spectrum"]["charpoly_identity_dev"]),
        ("rotation omega dev", va["T11_rotation"]["omega_dev"]),
        ("rigidity (shape err max)", va["T11_rotation"]["shape_err_max"]),
        ("T12 Aref invariants drift",
         va["T12_manifold"]["invariants_drift_max"]),
        ("T12 r_max (bound, no wall)", va["T12_manifold"]["r_max"]),
        ("T13 V* (exact impossibility threshold)", va["T13_V_star"]),
        ("T13 median wall work |dE|",
         va["T13_oscillating_complement"]["median_abs_dE"]),
    ]]
    sheet(wb, "vortex_anchor", ["quantity", "value"], rows_t11, [44, 20])

    # 16. the claims registry (Evidence Engine)
    import json as _json
    reg_path = os.path.join(ROOT, "results", "claims_registry.json")
    with open(reg_path, encoding="utf-8") as fh:
        reg = _json.load(fh)
    rows_c = [{"id": c["id"], "status": c["status"], "campaign":
               c.get("campaign") or "-", "statement": c["statement"],
               "verdict": c["verdict"]} for c in reg["claims"]]
    sheet(wb, "claims_registry", ["id", "status", "campaign", "statement",
                                  "verdict"],
          rows_c, [10, 16, 10, 72, 40])

    # 17. honest negatives
    s = load_json("qhb_summary.json")
    rows = [
        {"negative": "P_esc(V0=0) > 0 — static gravity does not confine",
         "value": s["P_esc_free"]},
        {"negative": "the a-channel alone opens nothing (all-order zero)",
         "value": 0.0},
        {"negative": "T=20 window: beats < 3 — gap unresolved", "value": 1.53},
        {"negative": "Delta_cont NOT claimed (two-term fit)",
         "value": ""},
        {"negative": "the Wu door does not reproduce eta alone",
         "value": 6.1e-10},
        {"negative": "Gascheau: equal-mass equilateral is unstable",
         "value": 1.0 / 27.0},
        {"negative": "T7 closed form does not extend to pairwise kinetics",
         "value": ""},
        {"negative": "the pairwise door leaves the linear alpha-limit "
                     "toward the FULL imbalance (toy)",
         "value": s["pair_full_imbalance"]},
        {"negative": "the Lambda_QCD branch is a renormalisation scale, "
                     "not a temperature", "value": ""},
        {"negative": "the electroweak branch is a VEV, not a bath "
                     "temperature (the least honest branch)", "value": ""},
        {"negative": "no gap closure on the whole searched phase map "
                     "(finite-range statement)",
         "value": s["phase_map_min_gap"]},
        {"negative": "the naive quadratic window extrapolation is "
                     "falsified at its own forecast closure point "
                     "(6.3x floor)",
         "value": s["phase_counterexample_ratio"]},
        {"negative": "the out-of-window quadratic forecast fails; the "
                     "wing is quartic (residual power 4.07)",
         "value": s["compete_residual_power"]},
        {"negative": "at Omega > 0 the wall pumps energy — the C2/C7 "
                     "sealing is finite-time (the static seal is exact)",
         "value": s["barrier_median_wall_work"]},
    ]
    sheet(wb, "honest_negatives", ["negative", "value"], rows, [56, 16])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print(f"workbook written: {OUT} ({len(wb.sheetnames)} sheets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
