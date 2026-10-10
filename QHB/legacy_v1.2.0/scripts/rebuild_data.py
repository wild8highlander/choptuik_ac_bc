# -*- coding: utf-8 -*-
"""
rebuild_data.py — regenerate every derived table in data/qhb/ from the
committed campaign verdicts (byte-deterministic, pinned by a test).

Chain of provenance (mirrors CHB):
    campaigns/reference/*.json  ->  data/qhb/*.csv|json  ->  figures
The script reads ONLY committed verdicts; no engine is invoked.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)

from qhb.bridge import master_table, write_outputs
from qhb.ladder import (density_ladder, temperature_ladder, gap_ladder,
                        constants_registry, write_outputs as write_ladders)
from qhb.constants import __version__

REF = os.path.join(ROOT, "campaigns", "reference")
OUT = os.path.join(ROOT, "data", "qhb")


def load(name):
    with open(os.path.join(REF, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    os.makedirs(OUT, exist_ok=True)
    c1 = load("c1_verdict.json")
    c2 = load("c2_verdict.json")
    c3 = load("c3_verdict.json")
    c4 = load("c4_verdict.json")
    c5 = load("c5_verdict.json")
    c6 = load("c6_verdict.json")
    c7 = load("c7_verdict.json")
    c8 = load("c8_verdict.json")
    c9 = load("c9_verdict.json")
    c10 = load("c10_verdict.json")
    c11 = load("c11_verdict.json")

    gap_values = {"gap_static": c1["static"]["Delta0"],
                  "gap_shift_beta05": c1["gap_shift_beta05"]}

    # --- master bridge table ---------------------------------------------------
    rows = master_table(gap_values)
    master_path = write_outputs(rows, OUT)

    # --- ladders -----------------------------------------------------------------
    write_ladders(density_ladder(), temperature_ladder(),
                  gap_ladder(c1["static"]["Delta0"]),
                  constants_registry(c1["static"]["Delta0"], c1["window"]["B2"]),
                  OUT)

    # --- campaign extracts ---------------------------------------------------------
    def dump(name, obj):
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
        return path

    dump("gap_scan_window.json",
         {"beta": [r["beta"] for r in c1["window"]["rows"]],
          "gap": [r["gap"] for r in c1["window"]["rows"]],
          "shift": [r["shift"] for r in c1["window"]["rows"]],
          "B2": c1["window"]["B2"], "r2": c1["window"]["r2"],
          "wing_betas": c1["wing"]["betas"],
          "wing_shifts": c1["wing"]["shifts"]})
    dump("gap_per_sector.json", c1["per_sector"])

    with open(os.path.join(OUT, "trap_grid.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("V0,Omega,P_esc,err,n_alive_end\n")
        for g in sorted(c2["grid"], key=lambda r: (r["Omega"], r["V0"])):
            fh.write(f'{g["V0"]:.4g},{g["Omega"]:.4g},{g["P_esc"]:.10e},'
                     f'{g["err"]:.10e},{g["n_alive_end"]}\n')
    dump("trap_lyapunov.json", c2["lyapunov"])
    dump("gascheau.json", c2["gascheau"])

    with open(os.path.join(OUT, "wu_residual_grid.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("alpha,x,r_exact,r_mc,dev\n")
        for r in c3["rows"]:
            fh.write(f'{r["alpha"]:.4g},{r["x"]:.4g},{r["r_exact"]:.10e},'
                     f'{r["r_mc"]:.10e},{r["dev"]:.10e}\n')
    dump("wu_anchor.json", c3["anchor"])
    dump("wu_eta_comparison.json", c3["eta_comparison"])

    with open(os.path.join(OUT, "floor_ladder.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("T_sim,N_samples,beats,resolution,gap_meas,err,resolved\n")
        for r in c4["rows"]:
            fh.write(f'{r["T_sim"]:.4g},{r["N_samples"]},'
                     f'{r["beats_in_window"]:.6f},{r["resolution"]:.6e},'
                     f'{r["gap_meas"] if r["gap_meas"] is not None else ""},'
                     f'{r["err"] if r["err"] is not None else ""},'
                     f'{int(r["resolved"])}\n')
    dump("floor_law.json", c4["floor_law"])

    with open(os.path.join(OUT, "drift_ladder.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("N,h,Delta_N\n")
        for r in c5["ladder"]:
            fh.write(f'{r["N"]},{r["h"]:.10e},{r["Delta_N"]:.12e}\n')
    dump("drift_law.json", {"p_eff": c5["p_eff"], "fit": c5["fit"],
                            "exact_channel": c5["exact_channel"]})

    # --- v1.1.0 campaign extracts (C6-C8) -----------------------------------------
    with open(os.path.join(OUT, "mapping_branches.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("branch,T_K,f_contact_Hz,M_contact_kg,f_gap_Hz,E_gap_MeV,"
                 "t_evap_s,rho_over_rhoP\n")
        for r in c6["branches"]:
            fh.write(f'{r["name"]},{r["T_K"]:.10e},{r["f_contact_Hz"]:.10e},'
                     f'{r["M_contact_kg"]:.10e},{r["f_gap_Hz"]:.10e},'
                     f'{r["E_gap_MeV"]:.10e},{r["t_evap_s"]:.10e},'
                     f'{r["rho_over_rhoP"]:.10e}\n')

    with open(os.path.join(OUT, "anharmonic_free.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("sigma,P_esc,err,n_alive_end,E_drift_surv\n")
        for r in c7["free_sigma_ladder"]:
            fh.write(f'{r["sigma"]:.6g},{r["P_esc"]:.10e},{r["err"]:.10e},'
                     f'{r["n_alive_end"]},{r["E_drift_surv"]:.10e}\n')

    with open(os.path.join(OUT, "anharmonic_grid.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("sigma,V0,Omega,P_esc,err,n_alive_end\n")
        for g in sorted(c7["grid"], key=lambda r: (r["Omega"], r["sigma"],
                                                   r["V0"])):
            fh.write(f'{g["sigma"]:.6g},{g["V0"]:.6g},{g["Omega"]:.6g},'
                     f'{g["P_esc"]:.10e},{g["err"]:.10e},'
                     f'{g["n_alive_end"]}\n')
    dump("anharmonic_boundary.json",
         {"L1": c7["L1_leakage_law"], "L2": c7["L2_boundary_collapse"],
          "L3": c7["L3_bound_chaos"],
          "regression_gate": c7["regression_gate"]})

    with open(os.path.join(OUT, "pairwise_residual.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("alpha,lambda,r_pair,r_linear_at_x_lambda\n")
        for r in c8["grid"]:
            fh.write(f'{r["alpha"]:.6g},{r["lambda"]:.6g},'
                     f'{r["r_pair"]:.10e},'
                     f'{r["r_linear_at_x=lambda"]:.10e}\n')
    dump("pairwise_checks.json",
         {"X1": c8["X1_no_door_exact"], "X2": c8["X2_monotone_imbalance"],
          "convergence": c8["convergence"], "mpmath": c8["mpmath_anchor"],
          "door_stays": c8["door_stays"], "shape_moves": c8["shape_moves"]})

    # --- v1.2.0 campaign extracts (C9-C11) -----------------------------------------
    with open(os.path.join(OUT, "phase_map.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("q_pk,beta,Delta_F,phase\n")
        for row in c9["map"]["rows"]:
            for cell in row["cells"]:
                fh.write(f'{row["q_pk"]:.6g},{cell["beta"]:.6g},'
                         f'{cell["Delta_F"]:.10e},{cell["phase"]}\n')

    with open(os.path.join(OUT, "phase_valley.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("q_pk,beta_star,Delta_F_min,above_floor\n")
        for v in c9["valley"]:
            fh.write(f'{v["q_pk"]:.6g},{v["beta_star"]:.10e},'
                     f'{v["Delta_F_min"]:.10e},{int(v["above_floor"])}\n')
    dump("phase_counterexample.json", c9["counterexample"])

    with open(os.path.join(OUT, "ablation.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("config,B2,max_abs_residual,b_flip_dev\n")
        for r in c10["ablation"]:
            fh.write(f'{r["config"]},{r["B2"]:.10e},'
                     f'{r["max_abs_residual"]:.10e},'
                     f'{r["b_flip_dev"]:.10e}\n')

    with open(os.path.join(OUT, "forecast.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("beta,true_shift,quadratic_forecast,error,error_share\n")
        for r in c10["forecast"]["rows"]:
            fh.write(f'{r["beta"]:.6g},{r["true_shift"]:.10e},'
                     f'{r["quadratic_forecast"]:.10e},{r["error"]:.10e},'
                     f'{r["error_share"]:.10e}\n')
    dump("ablation_additivity.json", {"shares": c10["causal_shares"],
                                      "rows": c10["additivity"]})

    with open(os.path.join(OUT, "barrier_cells.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("V0,Omega,P_esc,n_escaped,bound_violation_max,"
                 "bound_margin_min,exactly_impossible,E_drift_abs_max\n")
        for c in c11["blocks"]["B4_T13_barrier"]["cells"]:
            fh.write(f'{c["V0"]:.6g},{c["Omega"]:.6g},{c["P_esc"]:.10e},'
                     f'{c["n_escaped"]},{c["bound_violation_max"]:.10e},'
                     f'{c["bound_margin_min"]:.10e},'
                     f'{int(c["escape_exactly_impossible"])},'
                     f'{c["E_drift_abs_max"]:.10e}\n')
    dump("vortex_anchor.json", {
        "T11_spectrum": c11["blocks"]["B1_T11_exact"],
        "T11_rotation": c11["blocks"]["B2_T11_rotation"],
        "T12_manifold": c11["blocks"]["B3_T12_manifold"],
        "T13_V_star": c11["blocks"]["B4_T13_barrier"]["V_star"],
        "T13_oscillating_complement":
            c11["blocks"]["B4_T13_barrier"]["oscillating_complement"]})

    # --- the one summary json ---------------------------------------------------
    dump("qhb_summary.json", {
        "version": __version__,
        "gap_static": c1["static"]["Delta0"],
        "gap_B2": c1["window"]["B2"], "gap_B2_r2": c1["window"]["r2"],
        "B2_per_sector": [c1["per_sector"]["B2_A_pi2"],
                          c1["per_sector"]["B2_B_pi3"],
                          c1["per_sector"]["B2_C_pi7"]],
        "cross_share": c1["cross_share"],
        "P_esc_free": c2["T5_free_negative"]["P_esc_free"],
        "V0_star": c2["T6_trap"]["V0_star_per_Omega"],
        "lyapunov_free_median": c2["lyapunov"]["free"]["median"],
        "lyapunov_trap_median": c2["lyapunov"]["trap_V08_Om2"]["median"],
        "wu_r_anchor": c3["anchor"]["r_at_anchor"],
        "wu_max_dev": c3["max_dev_formula_vs_mc"],
        "floor_envelope_holds": c4["floor_law"]["envelope_holds_on_resolved"],
        "drift_p_eff": [p["p"] for p in c5["p_eff"]],
        "drift_C_measured": c5["fit"]["C_measured"],
        "drift_share_exact": c5["exact_channel"]["share_of_measured"],
        "map_E_gap_MeV_QCD": next(r["E_gap_MeV"] for r in c6["branches"]
                                  if r["name"] == "QCD_crossover"),
        "map_Lambda_over_Egap": c6["gates"]["G4_order_window"]
                                ["Lambda_over_E_gap_QCD"],
        "anh_P_esc_free": c7["regression_gate"]["P_esc_sigma0"],
        "anh_sigma_star": c7["L1_leakage_law"]["sigma_star_P05"],
        "anh_V0_star_shrink": c7["L2_boundary_collapse"]
                              ["shrink_factors_Om0_to_Om2"],
        "anh_lyapunov_median": c7["L3_bound_chaos"]["median"],
        "pair_r_zero_alpha": c8["X1_no_door_exact"]["r"],
        "pair_p_eff": c8["convergence"]["p_eff"],
        "pair_r_anchor": next(r["r_pair"] for r in c8["grid"]
                              if r["alpha"] == 0.9 and r["lambda"] == 1.0),
        "pair_full_imbalance": c8["shape_moves"]
                               ["r_pair_at_lambda_100_alpha_09"],
        "phase_map_min_gap": c9["gates"]["P1_no_closure"]["map_min_Delta_F"],
        "phase_valley_beta_q04": next(
            v["beta_star"] for v in c9["valley"]
            if abs(v["q_pk"] - 0.4) < 1e-9),
        "phase_counterexample_ratio": c9["counterexample"]["ratio_to_floor"],
        "compete_share_A": c10["causal_shares"]["A"],
        "compete_share_B": c10["causal_shares"]["B"],
        "compete_share_C": c10["causal_shares"]["C"],
        "compete_max_cross": c10["gates"]["Q3_additivity"]["max_cross_share"],
        "compete_residual_power": c10["forecast"]["effective_residual_power"],
        "vortex_omega_exact": c11["blocks"]["B1_T11_exact"]["omega_exact"],
        "vortex_omega_dev": c11["blocks"]["B2_T11_rotation"]["omega_dev"],
        "vortex_charpoly_dev": c11["blocks"]["B1_T11_exact"]
                               ["charpoly_identity_dev"],
        "aref_inv_drift": c11["blocks"]["B3_T12_manifold"]
                          ["invariants_drift_max"],
        "aref_r_max": c11["blocks"]["B3_T12_manifold"]["r_max"],
        "barrier_V_star": c11["blocks"]["B4_T13_barrier"]["V_star"],
        "barrier_median_wall_work": c11["blocks"]["B4_T13_barrier"]
                                   ["oscillating_complement"]
                                   ["median_abs_dE"],
    })
    print(f"data/qhb rebuilt from committed verdicts: {master_path} + ladders "
          f"+ campaign extracts + C6-C8 + C9-C11 tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
