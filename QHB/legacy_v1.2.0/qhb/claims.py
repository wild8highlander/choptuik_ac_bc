"""
claims.py — the Evidence Engine validator (v1.2.0).

Every load-bearing statement of the package lives in
results/claims_registry.json with:

  * a STATUS from the closed enum
        exact | measured-law | honest-negative | hypothesis | comparison
  * a VERDICT ADDRESS (the file that carries the number),
  * an UNCERTAINTY BUDGET with the five committed fields
        statistical / discretization / solver / parameter / model
    (a value or explicit null — a null is a claim that the component
    is absent, never that it is unknown),
  * a PRE-COMMITTED FALSIFICATION CRITERION.

The validator checks the schema, the status enum, the existence of every
verdict file and the registry self-consistency.  Run:

    python3 -m qhb.claims        # validate + print the registry table

The registry is pinned by tests/test_claims.py: a registry that does not
validate breaks the build.
"""
import json
import os
import sys

STATUSES = ("exact", "measured-law", "honest-negative", "hypothesis",
            "comparison")
UNCERTAINTY_FIELDS = ("statistical", "discretization", "solver",
                      "parameter", "model")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REGISTRY = os.path.join(ROOT, "results", "claims_registry.json")


def load_registry(path=REGISTRY):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate(reg=None, root=ROOT):
    """Validate the registry; returns (ok, errors list, claims list)."""
    if reg is None:
        reg = load_registry()
    errors = []
    if reg.get("schema") != "qhb.claims/1.0":
        errors.append("schema marker missing or unknown")
    claims = reg.get("claims", [])
    if not claims:
        errors.append("registry carries no claims")
    seen = set()
    status_counts = {}
    for c in claims:
        cid = c.get("id", "<missing>")
        if cid in seen:
            errors.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c.get("status") not in STATUSES:
            errors.append(f"{cid}: bad status {c.get('status')!r}")
        status_counts[c.get("status")] = \
            status_counts.get(c.get("status"), 0) + 1
        unc = c.get("uncertainty")
        if not isinstance(unc, dict) or \
                set(unc.keys()) != set(UNCERTAINTY_FIELDS):
            errors.append(f"{cid}: uncertainty budget must carry exactly "
                          f"{UNCERTAINTY_FIELDS}")
        if not c.get("statement") or len(c["statement"]) < 20:
            errors.append(f"{cid}: statement missing or too short")
        if not c.get("falsification") or len(c["falsification"]) < 20:
            errors.append(f"{cid}: falsification criterion missing")
        if not c.get("verdict"):
            errors.append(f"{cid}: verdict address missing")
        else:
            vpath = os.path.join(root, c["verdict"])
            if not os.path.exists(vpath):
                errors.append(f"{cid}: verdict file not found: "
                              f"{c['verdict']}")
    return (len(errors) == 0), errors, claims


def main():
    ok, errors, claims = validate()
    counts = {}
    for c in claims:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print(f"claims registry: {len(claims)} claims")
    for st in STATUSES:
        print(f"  {st:17s} {counts.get(st, 0)}")
    if ok:
        print("validation: PASS (schema, statuses, verdict addresses, " +
              "uncertainty budgets, falsification criteria)")
        return 0
    print("validation: FAIL")
    for e in errors:
        print("  -", e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
