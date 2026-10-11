"""IVP11 — the vortex layer: the exact characteristic polynomial of the
corotating linearization derived symbolically (SymPy), the Aref
invariants at 50 digits (mpmath) and the neutral-stability eigenvalue
gate (numpy, own code path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, write_verdict

sys.path.insert(0, ROOT)

import math

import mpmath as mp
import sympy as sp

mp.mp.dps = 50

# --- 1. symbolic: the Kirchhoff Jacobian at the equilateral triangle --------
lam = sp.symbols("lambda")
a = sp.symbols("a", positive=True)
sqrt3 = sp.sqrt(3)
# unit equal circulations; side a; centroid at the origin
# (circumradius R = a/sqrt(3): vertices (R,0), (-R/2, +-R*sqrt(3)/2))
r = [sp.Matrix([a / sqrt3, sp.Integer(0)]),
     sp.Matrix([-a / (2 * sqrt3), a / 2]),
     sp.Matrix([-a / (2 * sqrt3), -a / 2])]
Gamma = [sp.Integer(1), sp.Integer(1), sp.Integer(1)]
omega = sp.Integer(3) / (2 * sp.pi * a ** 2)      # Gamma_tot/(2 pi a^2)

n = 3
J = sp.zeros(2 * n, 2 * n)
for k in range(n):
    for j in range(n):
        if j == k:
            continue
        d = r[k] - r[j]
        q = (d[0] ** 2 + d[1] ** 2)
        B = sp.Matrix([[2 * d[0] * d[1], d[1] ** 2 - d[0] ** 2],
                       [d[1] ** 2 - d[0] ** 2, -2 * d[0] * d[1]]])
        blk = -(Gamma[j] / (2 * sp.pi * q ** 2)) * B
        J[2 * k:2 * k + 2, 2 * j:2 * j + 2] += blk
        J[2 * k:2 * k + 2, 2 * k:2 * k + 2] -= blk
for k in range(n):
    J[2 * k, 2 * k + 1] += omega
    J[2 * k + 1, 2 * k] += -omega

char = sp.factor(sp.expand(J.charpoly(lam).as_expr()))
expected = sp.factor(lam ** 2 * (lam ** 2 + omega ** 2) ** 2)
sym_dev = sp.simplify(sp.expand(char - expected))
sym_ok = sym_dev == 0

# --- 2. mpmath 50 digits: the Aref launch invariants ------------------------
s2 = mp.sqrt(2)
pos = [(s2, mp.mpf(0)), (mp.mpf(0), s2), (s2, s2)]
gam = [mp.mpf(1), mp.mpf(1), mp.mpf(-1)]
I50 = sum(gam[k] * (pos[k][0] ** 2 + pos[k][1] ** 2) for k in range(3))
P50 = sum(gam[k] * pos[k][1] for k in range(3))
Q50 = sum(gam[k] * pos[k][0] for k in range(3))
H50 = -sum(gam[i] * gam[j] * mp.log(mp.hypot(pos[i][0] - pos[j][0],
                                             pos[i][1] - pos[j][1]))
           for i in range(3) for j in range(i + 1, 3)) / (2 * mp.pi)
max_inv = max(abs(v) for v in (I50, P50, Q50, H50))
mp_ok = max_inv < mp.mpf("1e-40")

# --- 3. numpy: the neutral-stability gate (own eigen path) ------------------
from qhb.vortex import linearize_triangle_exact

ev, om_num, _ = linearize_triangle_exact()
re_gate = max(abs(e.real) for e in ev if abs(e.imag) > 1e-6)
np_ok = re_gate < 1e-12 and abs(om_num - 3.0 / (2.0 * math.pi)) < 1e-15

ok = sym_ok and mp_ok and np_ok
write_verdict("IVP11.json", {"check": "vortex layer (SymPy charpoly + "
                             "mpmath Aref invariants + eigen gate)",
                             "verdict": "PASS" if ok else "FAIL",
                             "charpoly_symbolic": sp.srepr(expected)[:120],
                             "charpoly_dev": str(sym_dev),
                             "aref_invariants_max_50dig": float(max_inv),
                             "max_re_on_imag_pairs": float(re_gate),
                             "omega_numeric": om_num})
print("IVP11:", "PASS" if ok else "FAIL")
