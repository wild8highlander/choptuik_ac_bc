"""Validate the committed results/*.json of the seven experiments.

Re-derives every committed verdict from the JSON payloads alone (no
recomputation) and checks it against the thresholds in dsilab.constants.
Used by `make validate`, the logged verification run and CI.

Exit code 0 = all verdicts hold; 1 = at least one failed (a finding).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dsilab.constants import (
    CENSUS_E,
    CENSUS_F,
    CENSUS_V,
    IDENTITY_ERR_A_MAX,
    PSL27_ORDER,
    THEOREM_B_ABS_TOL,
    THEOREM_C_ABS_TOL,
)

#: exp1: the sharp-trace-theorem minimization gap bound. The committed
#: maximum is 5.920e-8 (the README prose rounds it to "5.9e-8"); the check
#: uses the honest next-decimal ceiling so the verdict is stable.
TRACE_GAP_MAX: float = 6.0e-8

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def _load(name: str) -> dict:
    with (RESULTS_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate() -> list[tuple[str, bool, str]]:
    """Return (check, ok, detail) rows for every committed verdict."""
    rows: list[tuple[str, bool, str]] = []

    # -- exp1: sharp trace theorem at n = 7..12 -----------------------------
    exp1 = _load("exp1_sh3.json")
    minim = exp1["theorem_big_n"]["minimization"]
    gap_max = max(float(row["gap"]) for row in minim)
    rows.append(
        (
            "exp1 sharp trace theorem: max gap <= 5.9e-8",
            gap_max <= TRACE_GAP_MAX,
            f"max gap = {gap_max:.3e}",
        )
    )
    trunc = exp1["tree"]["truncation"]
    t_err = max(abs(float(row["F"]) - float(row["n+2"])) for row in trunc)
    rows.append(
        (
            "exp1 Kunz-tree trim: F = n + 2 exactly",
            t_err < 1e-9,
            f"max err = {t_err:.3e}",
        )
    )

    # -- exp2: the 9/224 observation ----------------------------------------
    exp2 = _load("exp2_dsi4.json")
    dev = float(exp2["arithmetic"]["dev_pct"])
    rows.append(
        (
            "exp2 DSI-4: |9/224 − measured| within +0.01%",
            dev < 0.01,
            f"deviation = {dev:.5f}%",
        )
    )

    # -- exp3: Hurwitz tower audit (finding D1) -----------------------------
    exp3 = _load("exp3_hurwitz.json")
    bad_rows = [r for r in exp3["repo_audit"] if not r["consistent"]]
    rows.append(
        (
            "exp3 finding D1: repo row (g=14, n=11) flagged",
            len(bad_rows) == 1 and bad_rows[0]["name"] == "Hurwitz_3",
            "corrected group PSL(2,13), (2,3,13)",
        )
    )
    tower_ok = all(r.get("all_ok", False) for r in exp3["tower"])
    rows.append(
        (
            "exp3 corrected tower: all checks hold",
            tower_ok,
            f"{len(exp3['tower'])} surfaces",
        )
    )

    # -- exp5: QCD bridge (finding E1) ---------------------------------------
    exp5 = _load("exp5_qcd.json")
    trace_core = float(exp5["nscaling"]["trace_core"])
    rows.append(
        (
            "exp5 finding E1: tr(Q_K3 (+) M_F) = 32 (centered)",
            abs(trace_core - 32.0) < 1e-9,
            f"trace_core = {trace_core:.12f}",
        )
    )

    # -- exp6: the {7,3} census ----------------------------------------------
    exp6 = _load("exp6_census_224.json")
    census = exp6["census"]
    rows.append(
        (
            "exp6 census: V = 56, E = 84, F = 24",
            int(census["V"]) == CENSUS_V
            and int(census["E"]) == CENSUS_E
            and int(census["F"]) == CENSUS_F,
            f"V={census['V']} E={census['E']} F={census['F']}",
        )
    )
    rows.append(
        (
            "exp6 census: |GL(3,2)| = 168",
            int(census["group_order"]) == PSL27_ORDER,
            f"order = {census['group_order']}",
        )
    )
    rows.append(
        (
            "exp6 census: Euler chi = V − E + F = −4",
            int(census["euler"]) == CENSUS_V - CENSUS_E + CENSUS_F,
            f"chi = {census['euler']}",
        )
    )

    # -- exp7: theorems A / B / C --------------------------------------------
    exp7 = _load("exp7_e1_threshold.json")
    a = exp7["theorem_A"]
    rows.append(
        (
            "exp7 A: zero threshold violations (e >= 1)",
            int(a["threshold_violations"]) == 0,
            f"{a['threshold_violations']} / {a['pairs']} pairs",
        )
    )
    rows.append(
        (
            "exp7 A: identity err <= 5.9e-16 (x10 slack)",
            float(a["identity_err"]) <= IDENTITY_ERR_A_MAX * 10,
            f"identity_err = {float(a['identity_err']):.3e}",
        )
    )
    b_err = max(float(d["err"]) for d in exp7["theorem_B"]["tree"])
    rows.append(
        (
            "exp7 B: tree F = n + 2·rank exactly",
            b_err < THEOREM_B_ABS_TOL,
            f"max err = {b_err:.3e}",
        )
    )
    c_err = max(
        float(exp7["theorem_C"]["unitary_max_err"]),
        float(exp7["theorem_C"]["perm_max_err"]),
    )
    rows.append(
        (
            "exp7 C: unitary pairs F = 2n exactly",
            c_err < THEOREM_C_ABS_TOL,
            f"max err = {c_err:.3e}",
        )
    )
    return rows


def main() -> int:
    rows = validate()
    print("=" * 78)
    print("dsilab.validate — committed-verdict audit")
    print("=" * 78)
    bad = 0
    for name, ok, detail in rows:
        mark = "PASS" if ok else "FAIL"
        bad += 0 if ok else 1
        print(f"  [{mark}] {name}: {detail}")
    print(f"  verdict: {len(rows) - bad}/{len(rows)} checks hold")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
