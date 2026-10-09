#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rebuild_data.py — derive every table in data/bridge/ from committed verdicts.

Provenance chain (single direction, no circularity):

    campaigns/run_c1.py  ->  campaigns/reference/c1_verdict.json
    campaigns/run_c2.py  ->  campaigns/reference/c2_verdict.json
    campaigns/run_c3.py  ->  campaigns/reference/c3_verdict.json
    campaigns/run_c3b.py ->  campaigns/reference/c3b_verdict.json
                                   |
                                   v  (this script, float-exact recomputation)
    chbridge.bridge/page/ladder  ->  data/bridge/*.csv + *_summary.json
                                   +  campaign_*.csv (verdict rows, verbatim)

Run after any committed-verdict update:  python3 scripts/rebuild_data.py
The script is deterministic; re-running it on the same verdicts must be
a no-op (verified by tests/test_bridge.py::test_rebuild_is_deterministic).
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from chbridge import bridge, page, ladder  # noqa: E402

OUT = os.path.join(ROOT, "data", "bridge")
REF = os.path.join(ROOT, "campaigns", "reference")


def _verdict(name):
    p = os.path.join(REF, name)
    if not os.path.exists(p):
        print(f"      (skipped: {name} not found — run its campaign first)")
        return None
    with open(p) as f:
        return json.load(f)


def _write_csv(path, cols, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def campaign_tables(outdir):
    """Verdict-to-table stage: campaign rows committed verbatim.

    No recomputation, no rounding, no reordering: the CSV cells are the
    JSON cells.  Campaigns that have not been run yet are skipped with
    a note, so `make data` works on partial checkouts."""
    written = []

    c2 = _verdict("c2_verdict.json")
    if c2 is not None:
        sub = c2["subcritical"]["rows"]
        _write_csv(os.path.join(outdir, "campaign_c2_subcritical.csv"),
                   ["eps", "A", "q_max", "v_qmax", "n_peaks",
                    "q_final_over_qmax", "flipped", "stop"], sub)
        bif = c2["bifurcation"]["rows"]
        _write_csv(os.path.join(outdir, "campaign_c2_bifurcation.csv"),
                   ["eps", "A", "M_code", "f_tilde", "stop", "sane"], bif)
        written += ["campaign_c2_subcritical.csv", "campaign_c2_bifurcation.csv"]

    c3b = _verdict("c3b_verdict.json")
    if c3b is not None:
        lad = []
        for grid, g in sorted(c3b["gamma_ladder"].items(),
                              key=lambda kv: int(kv[0][1:])):
            for r in g["rows"]:
                lad.append({"N": int(grid[1:]), **r})
        _write_csv(os.path.join(outdir, "campaign_c3b_ladder.csv"),
                   ["N", "eps", "A", "M_code", "stop", "sane"], lad)
        written.append("campaign_c3b_ladder.csv")

    return written


def main():
    verdict_path = os.path.join(ROOT, "campaigns", "reference", "c1_verdict.json")
    with open(verdict_path) as f:
        verdict = json.load(f)

    print("[1/5] bridge tables ...")
    summary = bridge.write_outputs(verdict, OUT)
    print(f"      born spectrum rows: {len(verdict['scan_rows_N400']) + len(verdict['scan_rows_N800'])}")
    print(f"      master table rows : 15 (5 input scales x 3 ensemble members)")
    print(f"      a* drift vs remediated reference (N=1600): "
          f"{summary['a_star_drift_N800_vs_reference']:.2e}")

    print("[2/5] page tables ...")
    pinfo = page.write_outputs(OUT)
    print(f"      grid points: {pinfo['grid_points']}, "
          f"haar partitions: {pinfo['haar_partitions']}, "
          f"max |S_formula - S_MC| = {pinfo['max_dev_bits']:.4f} bits")

    print("[3/5] ladder tables ...")
    linfo = ladder.write_outputs(OUT)
    print(f"      ladders: {linfo['accel_rows']} accel, "
          f"{linfo['length_rows']} length, {linfo['curvature_rows']} curvature")
    print(f"      a0 / (cH0/2pi) = {linfo['a0_over_cH0_2pi']:.4f}")
    print(f"      |gamma_Ch - b_Ch| / b_Ch = {linfo['gamma_vs_bch_pct']:.2f}%")

    print("[4/5] campaign tables (C2 branches, C3b resolution ladder) ...")
    written = campaign_tables(OUT)
    for name in written:
        print(f"      wrote {name}")

    print("[5/5] consistency spot-check ...")
    c2 = _verdict("c2_verdict.json")
    if c2 is not None:
        sub = c2["subcritical"]
        n_flipped = sub["flipped_runs"]
        print(f"      C2: {sub['n_runs']} subcritical runs "
              f"({n_flipped} flipped), "
              f"slowdown slope = {sub['slowdown_fit']['slope_ln_eps']:.4f}, "
              f"echo rate = {sub['echo_rate_fit']['echoes_per_efold']:.4f} /e-fold")
        print(f"      C2: M_sat(N=800) = {c2['bifurcation']['summary']['M_sat_N800']:.5f}, "
              f"eps_half = {c2['bifurcation']['summary']['eps_half']:.4e}")
    c3b = _verdict("c3b_verdict.json")
    if c3b is not None:
        for grid, g in sorted(c3b["gamma_ladder"].items(),
                              key=lambda kv: int(kv[0][1:])):
            print(f"      C3b {grid}: gamma_eff = {g['gamma_eff']:.4f} "
                  f"(floor_M = {g['floor_M']:.4e})")
        print(f"      C3b: P_anchor = {c3b['products']['P_anchor']:.5f} "
              f"-> {c3b['products']['P_anchor_verdict']}, "
              f"P_engine_deep = {c3b['products']['P_engine_deep']} "
              f"(honest negative kept)")

    print(f"\nall outputs -> {OUT}")


if __name__ == "__main__":
    main()
