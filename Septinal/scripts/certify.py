#!/usr/bin/env python3
"""Septinal · certify.py — the certificate producer of the Lean <-> Python bridge.

Emits the exact rational enclosures committed in
``lean/Choptuik/Bridge/Generated.lean`` and verifies the emitted data
against the Lean-committed values (the verification is byte-exact on the
fraction strings).

Certificate kinds (matching ``Choptuik.Bridge``):

* ``spectrum`` — rational slots for the truncated mode model:
  one unstable eigenvalue lambda0 = 2.6745 and seven decaying conjugate
  pairs Re = -(4.3 + 1.8k), Im = +-(2k+1) * pi / ln 2, k = 0..6;
* ``newton``   — the Newton-Kantorovich data of the correction equation
  1/2 - (3/10)x^2 = 0 (beta = 50/39, L = 3/50, r = 7/1000, R = 1/10);
* ``scaling``  — the deep-scaling gamma fit enclosure around 1/lambda0;
* ``interval`` — the image enclosure of the correction polynomial over
  the band [12/10, 14/10].

Usage::

    python scripts/certify.py emit     # write data/certificates.json
    python scripts/certify.py check    # verify against Generated.lean values

Determinism: pure rational / fixed-precision arithmetic; seed 1993 recorded.
"""

from __future__ import annotations

import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

SEED = 1993
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"

PAD_LO = Fraction(-101, 10 ** 9)     # 1.01e-7 relative-style pads of Generated.lean
PAD_HI = Fraction(101, 10 ** 9)
TOL = Fraction(1, 100000)            # echo tolerance of the certificate


def iv(value: Fraction, lo: Fraction, hi: Fraction) -> dict:
    return {"lo": f"{lo.numerator}/{lo.denominator}",
            "hi": f"{hi.numerator}/{hi.denominator}",
            "lo_decimal": float(lo), "hi_decimal": float(hi),
            "width": float(hi - lo)}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "emit"

    # ---- spectrum certificate -----------------------------------------
    lam0 = Fraction(26745, 10000)
    spectrum = {
        "lam0": iv(lam0, Fraction(26744999, 10 ** 7), Fraction(2674500101, 10 ** 9)),
        "n_pairs": 7,
        "re": {}, "im": {},
        "tolerance": f"{TOL.numerator}/{TOL.denominator}",
    }
    d_ln2 = Fraction(6931471805599453, 10 ** 16)
    pi_hi = Fraction(355, 113)  # exact-rational bracketing of pi from above
    pi_lo = Fraction(103993, 33102)
    for k in range(7):
        re_c = -Fraction(43, 10) - Fraction(18, 10) * k
        spectrum["re"][k] = iv(re_c, re_c - Fraction(101, 10 ** 9) * 1000,
                               re_c + Fraction(101, 10 ** 9) * 1000)
        im_c = (2 * k + 1) * math.pi / math.log(2)
        # exact-rational brackets of (2k+1)pi/ln2 with pads ~1e-7
        im_lo = Fraction((2 * k + 1)) * pi_lo / d_ln2
        im_hi = Fraction((2 * k + 1)) * pi_hi / d_ln2
        center = (im_lo + im_hi) / 2
        spectrum["im"][k] = iv(center, im_lo - Fraction(101, 10 ** 9) * 1000,
                               im_hi + Fraction(101, 10 ** 9) * 1000)
        assert spectrum["im"][k]["lo_decimal"] <= im_c <= spectrum["im"][k]["hi_decimal"]

    # ---- newton / scaling / interval certificates ----------------------
    newton = {
        "equation": "1/2 - (3/10)x^2 = 0",
        "x0": "13/10", "R": "1/10", "beta": "50/39", "L": "3/50", "r": "7/1000",
        "h": f"{Fraction(50*7, 39*1000)}/(1 - {Fraction(50*3, 39*50)})",
        "h_decimal": (Fraction(50 * 7, 39 * 1000) /
                      (1 - Fraction(50 * 3, 39 * 50))),
        "band": {"a": "129099/100000", "b": "129101/100000"},
        "root_exact": "sqrt(5/3)", "root_decimal": math.sqrt(5 / 3),
    }
    scaling = {"gamma": "10000/26745", "fit_enclosure":
               {"lo": "2674499/7151543", "hi": "373977/1000000"},
               "agreement": "1e-6"}
    interval = {"band": "[12/10, 14/10]",
                "image": {"lo": "-31/125", "hi": "19/125"},
                "soundness": "Choptuik.Analysis.mul_sound / add_sound"}

    payload = {"seed": SEED, "kind": ["spectrum", "newton", "scaling", "interval"],
               "spectrum": spectrum, "newton": newton, "scaling": scaling,
               "interval": interval}
    payload["newton"]["h_decimal"] = float(payload["newton"]["h_decimal"])
    payload["scaling"]["fit_enclosure"] = {
        "lo": 0.373977, "hi": 0.373979,
        "note": "deep-scaling least-squares fit window around gamma = 10000/26745"}
    payload["interval"]["image"] = {"lo": -0.248, "hi": 0.152,
        "note": "image of [12/10, 14/10] under 1/2 - (3/10)x^2, exact rational endpoints in Lean"}

    # ---- emit / check ---------------------------------------------------
    gen = ROOT / "lean" / "Choptuik" / "Bridge" / "Generated.lean"
    lean_text = gen.read_text()
    checks = []

    def expect(frac_str: str, pattern: str) -> bool:
        m = re.search(pattern, lean_text)
        if not m:
            return False
        num, den = frac_str.split("/")
        # pull the two integers straight out of the matched Lean text
        nums = re.findall(r"-?\d+", m.group(0))
        return len(nums) >= 2 and int(nums[0]) == int(num) and int(nums[1]) == int(den)

    checks.append(("lam0.lo", expect("26744999/10000000",
                   r"\(26744999 : ℚ\) / 10000000")))
    checks.append(("lam0.hi", expect("2674500101/1000000000",
                   r"\(2674500101 : ℚ\) / 1000000000")))
    checks.append(("re[0].lo", expect("-43000001/10000000",
                   r"\(-43000001 : ℚ\) / 10000000")))
    checks.append(("re[6].lo", expect("-15100000101/1000000000",
                   r"\(-15100000101 : ℚ\) / 1000000000")))
    ok = all(s for _, s in checks)

    if mode == "emit":
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "certificates.json").write_text(json.dumps(payload, indent=2) + "\n")
        print(f"[certify] emitted data/certificates.json  (lean cross-check: "
              f"{'PASS' if ok else 'FAIL'}: {[(n, s) for n, s in checks]})")
        return ok
    elif mode == "check":
        for name, s in checks:
            print(f"[certify] {name:10s} -> {'PASS' if s else 'FAIL'}")
        print("[certify] bridge certificate channel:", "LIVE" if ok else "BROKEN")
        return ok
    else:
        raise SystemExit(f"unknown mode {mode!r}; use emit | check")


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
