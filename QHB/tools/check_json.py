#!/usr/bin/env python3
"""Iron-QA: every JSON artifact in the release must parse and carry its layer meta."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def main() -> int:
    bad, n = [], 0
    for p in sorted(ROOT.rglob("*.json")):
        rel = p.relative_to(ROOT)
        if any(s in str(rel) for s in (".git", "node_modules")):
            continue
        n += 1
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            bad.append(f"{rel}: {e}")
    print(f"[check_json] parsed {n} JSON files, {len(bad)} broken")
    for b in bad:
        print("  BROKEN:", b)
    # layer meta spot checks
    must = {
        "monolith/extra_research/extra_research_results.json",
        "monolith/roadmap_research/roadmap_results.json",
        "monolith/analytic_layer/v220_t19.json",
        "monolith/analytic_layer/v220_cosmo.json",
        "monolith/analytic_layer/v220_ladders.json",
    }
    missing = [m for m in must if not (ROOT / m).exists()]
    if missing:
        print("  MISSING LAYER FILES:", missing)
        return 1
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
