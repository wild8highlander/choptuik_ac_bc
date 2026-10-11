"""summarize.py — the one-page IVP summary (results/SUMMARY.md)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
npass = 0
for i in range(1, 12):
    p = os.path.join(HERE, "results", f"IVP{i:02d}.json")
    with open(p, encoding="utf-8") as fh:
        v = json.load(fh)
    rows.append((f"IVP{i:02d}", v["check"], v["verdict"]))
    npass += v["verdict"] == "PASS"
lines = ["# IVP-11 summary", "",
         f"Verdict: **{npass}/11 PASS**", "",
         "| IVP | check | verdict |", "|---|---|---|"]
for name, check, verdict in rows:
    lines.append(f"| {name} | {check} | **{verdict}** |")
with open(os.path.join(HERE, "results", "SUMMARY.md"), "w",
          encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
