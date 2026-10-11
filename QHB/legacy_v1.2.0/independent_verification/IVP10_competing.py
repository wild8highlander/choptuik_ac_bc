"""IVP10 — the competing-model gates: a fresh interpreter re-derives the
ablation extremes (the exact zero of the braking-only configuration and
the spectator magnitude of the septinial C sector) at doubled Floquet
resolution, plus the evenness of every transverse configuration."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, write_verdict

sys.path.insert(0, ROOT)

from qhb.constants import BERRY_TRIO, BRAKING_TRIO
from qhb.gap import KAPPA, floquet_gap, static_gap

_, _, D0 = static_gap(64, KAPPA, 0.4)
M = 3840                                # doubled resolution

# 1. braking-only (none): B2 must vanish (all-order zero)
def shift(beta, bmask, amask):
    b = tuple(beta * BERRY_TRIO[k] if k in bmask else 0.0 for k in range(3))
    a = tuple(beta * BRAKING_TRIO[k] if k in amask else 0.0 for k in range(3))
    g, _ = floquet_gap(D0, b=b, a=a, M=M)
    return g - D0

b2_none = sum(shift(b, (), (0, 1, 2)) * b ** 2 for b in
              (0.05, 0.1, 0.15, 0.2)) / sum(b ** 4 for b in
                                            (0.05, 0.1, 0.15, 0.2))
ok_none = abs(b2_none) < 1e-12

# 2. the C sector is a spectator: |B2_C| < 1e-4 at doubled resolution
num = sum(shift(b, (2,), (2,)) * b ** 2 for b in (0.05, 0.1, 0.15, 0.2))
b2_C = abs(num / sum(b ** 4 for b in (0.05, 0.1, 0.15, 0.2)))
ok_C = b2_C < 1e-4

# 3. evenness at doubled resolution for A, B, C, ABC
even_devs = {}
for name, bm in (("A", (0,)), ("B", (1,)), ("C", (2,)), ("ABC", (0, 1, 2))):
    bp = tuple(BERRY_TRIO[k] if k in bm else 0.0 for k in range(3))
    ap = tuple(BRAKING_TRIO[k] if k in bm else 0.0 for k in range(3))
    g0, _ = floquet_gap(D0, b=bp, a=ap, M=M)
    g1, _ = floquet_gap(D0, b=tuple(-v for v in bp), a=ap, M=M)
    even_devs[name] = abs(g1 - g0)
ok_even = all(v < 1e-12 for v in even_devs.values())

ok = ok_none and ok_C and ok_even
write_verdict("IVP10.json", {"check": "competing-model gates (doubled "
                             "resolution)",
                             "verdict": "PASS" if ok else "FAIL",
                             "B2_none_at_M3840": b2_none,
                             "abs_B2_C_at_M3840": b2_C,
                             "evenness_devs_M3840": even_devs})
print("IVP10:", "PASS" if ok else "FAIL")
