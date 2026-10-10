# -*- coding: utf-8 -*-
"""IVP07 — convergence orders: the committed p_eff ladders behave."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import verdict, write_verdict

c5 = verdict("c5_verdict.json")
ps = [p["p"] for p in c5["p_eff"]]
c1 = verdict("c1_verdict.json")
pM = c1["M_convergence"]["p_eff"]
ok = (ps[0] > 1.9 and ps[-1] < 2.0 and ps == sorted(ps)
      and all(1.5 < p < 2.5 for p in pM))
write_verdict("IVP07.json", {"check": "convergence orders",
                             "verdict": "PASS" if ok else "FAIL",
                             "drift_p_eff": ps, "floquet_M_p_eff": pM})
print("IVP07:", "PASS" if ok else "FAIL")
