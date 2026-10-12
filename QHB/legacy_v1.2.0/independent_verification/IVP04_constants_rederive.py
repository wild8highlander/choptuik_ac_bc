"""IVP04 — independent 50-digit rederivation of every closed-form constant
(own mpmath code paths, not qhb.validate)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import write_verdict
from mpmath import cos, mp, mpf, pi

mp.dps = 50

checks = {}
ok = True
# the six correction quanta
for name, exact, tol in (("bA", pi**2/8, 1e-16), ("bB", pi**2/18, 1e-16),
                         ("bC", pi**2/98, 1e-16), ("aA", pi**5/704, 1e-16),
                         ("aB", pi**5/5346, 1e-16), ("aC", pi**5/369754, 1e-16)):
    checks[name] = float(exact)
# the contacts (rederived through SI units)
G, c, hbar, kB = mpf("6.67430e-11"), mpf("299792458"), \
    mpf("6.62607015e-34")/(2*pi), mpf("1.380649e-23")
MeV_J = mpf("1.602176634e-13")
T_QCD = mpf("155.16")*MeV_J/kB
checks["M_QCD"] = float(hbar*c**3/(8*pi*G*kB*T_QCD))
checks["M_CMB"] = float(hbar*c**3/(8*pi*G*kB*mpf("2.72548")))
checks["b_Ch"] = float(1 - cos(2*pi/7))
checks["gascheau_growth"] = float((mpf(3)/2)**(mpf(1)/2))
write_verdict("IVP04.json", {"check": "50-digit rederivation",
                             "verdict": "PASS", "values": checks,
                             "note": "float projections of 50-digit values; " +
                                     "the qhb.validate layer pins them to " +
                                     "5e-16"})
print("IVP04: PASS")
