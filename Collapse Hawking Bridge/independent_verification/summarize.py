#!/usr/bin/env python3
"""
summarize.py — aggregate results/*.json into the IVP-15 verdict table
(markdown + console).  Re-runnable at any time after the IVP scripts.
"""
import json
import os
import sys

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(IVP_DIR, "results")

TITLES = {
    "IVP01": "Release identity & archive integrity",
    "IVP02": "Clean-room installation (multi-interpreter)",
    "IVP03": "Dependency & provenance audit",
    "IVP04": "Independent re-derivation of constants",
    "IVP05": "Dimensional-analysis audit",
    "IVP06": "Roberts symbolic residual test (SymPy)",
    "IVP07": "Method-of-convergence test (order of solver)",
    "IVP08": "Constraint-propagation audit",
    "IVP09": "Blind remeasurement of A*",
    "IVP10": "Threshold robustness / perturbation",
    "IVP11": "Blind mass-scaling (gamma) measurement",
    "IVP12": "Resolution-floor law (multi-resolution fit)",
    "IVP13": "Blind echo detector (Delta)",
    "IVP14": "Delta*gamma falsification",
    "IVP15": "Cross-language agreement (multilang twins)",
}

STATUS_MARK = {"PASS": "PASS", "PARTIAL": "PART", "INCONCLUSIVE": "INCON",
               "FAIL": "FAIL"}


def main():
    rows = []
    for ivp in TITLES:
        path = os.path.join(RESULTS, f"{ivp}.json")
        if os.path.exists(path):
            with open(path) as f:
                d = json.load(f)
            rows.append((ivp, d.get("status", "?"), TITLES[ivp]))
        else:
            rows.append((ivp, "NOT RUN", TITLES[ivp]))

    lines = ["| IVP | Check | Verdict |", "| :-- | :--- | :------ |"]
    for ivp, status, title in rows:
        lines.append(f"| {ivp} | {title} | **{STATUS_MARK.get(status, status)}** |")

    table = "\n".join(lines)
    print(table)
    counts = {}
    for _, s, _ in rows:
        counts[s] = counts.get(s, 0) + 1
    print("\nSummary: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))

    out = os.path.join(RESULTS, "SUMMARY.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(table + "\n")
    print(f"-> {os.path.relpath(out, os.path.dirname(IVP_DIR))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
