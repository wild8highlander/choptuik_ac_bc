"""IVP02 — canonical job: a fresh interpreter recomputes the canonical
gap block from scratch and must match the committed verdict exactly."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, verdict, write_verdict

CODE = r"""
import sys, json, math
sys.path.insert(0, __ROOT__)
from qhb.gap import static_of_chain, floquet_gap
E0, E1, D0, s, h, L = static_of_chain()
g, _ = floquet_gap(D0, beta=0.2)
print(json.dumps({"Delta0": D0, "s": s, "gap_beta02": g}))
""".replace("__ROOT__", repr(ROOT))

r = subprocess.run([sys.executable, "-c", CODE], capture_output=True,
                   text=True, cwd=ROOT)
if r.returncode != 0:
    raise RuntimeError(r.stderr)
fresh = json.loads(r.stdout)
c1 = verdict("c1_verdict.json")
dev_d0 = abs(fresh["Delta0"] - c1["static"]["Delta0"])
dev_g = abs(fresh["gap_beta02"] - next(x["gap"] for x in c1["window"]["rows"]
                                       if abs(x["beta"] - 0.2) < 1e-9))
ok = dev_d0 == 0.0 and dev_g < 1e-9
write_verdict("IVP02.json", {"check": "canonical job (fresh interpreter)",
                             "verdict": "PASS" if ok else "FAIL",
                             "dev_Delta0": dev_d0, "dev_gap_beta02": dev_g})
print("IVP02:", "PASS" if ok else "FAIL")
