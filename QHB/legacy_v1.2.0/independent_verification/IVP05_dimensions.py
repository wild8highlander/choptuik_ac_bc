"""IVP05 — dimensions audit: every physical column carries the right SI size."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, write_verdict

sys.path.insert(0, ROOT)
from qhb.bridge import S_BH, T_H, equal_cmb_mass, equal_qcd_mass, r_s, t_evap

checks = {
    "M_QCD_in_[1e10,1e12]_kg": 1e10 < equal_qcd_mass() < 1e12,
    "M_CMB_in_[1e21,1e24]_kg": 1e21 < equal_cmb_mass() < 1e24,
    "T_H(M_QCD)=T_QCD_order_1e12_K": 1e12 < T_H(equal_qcd_mass()) < 1e13,
    "r_s(M_CMB)_in_[1e-5,1e-3]_m": 1e-5 < r_s(equal_cmb_mass()) < 1e-3,
    "S_BH/kB(M_CMB)_in_[1e58,1e65]": 1e58 < S_BH(equal_cmb_mass())/1.380649e-23 < 1e65,
    "t_evap(M_CMB)_in_[1e48,1e56]_s": 1e48 < t_evap(equal_cmb_mass()) < 1e56,
}
ok = all(checks.values())
write_verdict("IVP05.json", {"check": "dimensions audit",
                             "verdict": "PASS" if ok else "FAIL",
                             "checks": checks})
print("IVP05:", "PASS" if ok else "FAIL")
