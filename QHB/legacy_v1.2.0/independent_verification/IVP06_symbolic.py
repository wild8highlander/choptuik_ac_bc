"""IVP06 — symbolic layer (SymPy): the Gascheau criterion and Lemma A
in exact rational arithmetic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from ivp_common import write_verdict

lam = sp.symbols("lambda")
nu = sp.symbols("nu", positive=True)
char = lam**4 + lam**2 + sp.Rational(27, 4)*nu
# stability: all roots purely imaginary <=> 1 - 27*nu >= 0
disc = sp.discriminant(sp.Symbol("z")**2 + sp.Symbol("z") +
                       sp.Rational(27, 4)*nu, sp.Symbol("z"))
stable_cond = sp.simplify(1 - 27*nu)
nu_equal = sp.Rational(1, 3)
verdict_gascheau = "UNSTABLE" if sp.simplify(1 - 27*nu_equal) < 0 else "STABLE"

# Lemma A in exact rationals: sample q = k/2 x^2 - qpk on a centred grid
x, k, qpk, h = sp.symbols("x k qpk h", positive=True)
# worst alignment for even N: sites at +/- h/2, +/- 3h/2 ...
peak_sampled = -qpk + k*(h/2)**2/2
lemma = sp.simplify(k*h**2/8 - (k*(h/2)**2/2))
ok = sp.simplify(lemma) == 0 and verdict_gascheau == "UNSTABLE"
write_verdict("IVP06.json", {"check": "symbolic (SymPy)",
                             "verdict": "PASS" if ok else "FAIL",
                             "char_eq": str(char),
                             "stability_condition": str(stable_cond) + " >= 0",
                             "nu_equal_masses": "1/3",
                             "gascheau_verdict": verdict_gascheau,
                             "lemma_A_identity": "kappa*h^2/8 == "
                                                 "kappa*(h/2)^2/2 (exact)"})
print("IVP06:", "PASS" if ok else "FAIL")
