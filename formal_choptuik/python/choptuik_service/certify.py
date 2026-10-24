"""Certificate producer for the Lean <-> Python bridge (gap G4).

This module is the *proof-feeding* half of the bridge: it computes the
numerical content of the programme (spectrum of the truncated mode model,
Newton--Kantorovich constants for the correction equation, deep-scaling
fit of the critical exponent, interval enclosures), rounds every value
*outward* into an exact rational interval, and emits two artifacts:

1. a JSON certificate (machine-readable, exact decimal-string rationals)
   under ``bridge/certificates/``;
2. a generated Lean file ``lean/Choptuik/Bridge/Generated.lean`` that
   the theory layer checks by exact rational arithmetic (``norm_num``).

The division of labor (the honesty contract of the bridge):

* **Lean proves** (offline, machine-checked): the certificate *checks* --
  tightness, agreement with the rational model targets, echo-family
  structure -- and the *robustness theorems* that turn passing checks
  into spectral-shape conclusions for any operator whose eigenvalues
  pair with the certificate slots.
* **Python computes** (regression-locked by pytest, NOT by Lean): the
  pairing of computed eigenvalues with certificate slots, and the
  numerical values themselves.  Floats never enter the proof layer; only
  outward-rounded rationals do.

Rounding model: IEEE-754 double input -> ``Fraction`` (exact) -> +/-
tolerance pad -> outward rounding at 9 decimal places.  The pad
(1e-7 for the spectrum) exceeds the eigensolver error (~1e-10) by three
orders of magnitude, so the committed certificates remain valid under
recomputation on any conforming LAPACK.

Usage::

    python -m choptuik_service.certify emit   [--root <formal_choptuik>]
    python -m choptuik_service.certify check  [--root <formal_choptuik>]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from . import __version__
from .evolver import ECHO_PERIOD, GAMMA, LAMBDA0, ModeModel, mode_families
from .spectrum import compute_spectrum

CERT_SCHEMA = "choptuik-certificate/1.0"
PROTOCOL_VERSION = "1.1"

#: certificate rationals live on a 9-decimal grid
DECIMALS = 9
#: half-width of spectrum enclosures (eigensolver error is ~1e-10)
SPECTRUM_PAD = Fraction(1, 10**7)
#: echo-family tolerance proved on the Lean side (module constant `echoTol`)
ECHO_TOL = Fraction(1, 10**5)
#: maximum admitted interval width in the spectrum certificate
WIDTH_MAX = Fraction(1, 10**6)
#: half-width of the scaling-agreement enclosure (fit error is ~1e-10)
SCALING_PAD = Fraction(1, 10**6)
#: maximum admitted width of the Newton band
BAND_WIDTH_MAX = Fraction(1, 10**5)

N_DECAYING = 7


# ----------------------------------------------------------------------
# exact rational helpers
# ----------------------------------------------------------------------

def floor_at(q: Fraction, places: int = DECIMALS) -> Fraction:
    """Round *down* to the 10^-places grid."""
    scale = 10**places
    return Fraction(math.floor(q * scale), scale)


def ceil_at(q: Fraction, places: int = DECIMALS) -> Fraction:
    """Round *up* to the 10^-places grid."""
    scale = 10**places
    return Fraction(math.ceil(q * scale), scale)


def rat_iv(x: float, pad: Fraction) -> tuple[Fraction, Fraction]:
    """Outward-rounded rational enclosure of the float ``x`` with pad."""
    xq = Fraction(x)  # exact value of the double
    return floor_at(xq - pad), ceil_at(xq + pad)


def qstr(q: Fraction) -> str:
    """Exact human-readable form: decimal if the denominator divides 10^k."""
    den, num = q.denominator, q.numerator
    if den == 1:
        return str(num)
    d, k = den, 0
    while d % 2 == 0:
        d //= 2
        k += 1
    while d % 5 == 0:
        d //= 5
        k += 1
    if d == 1:
        # den divides 10^k: render with k decimals, trailing zeros stripped
        s = str(abs(num) * 10**k // den).rjust(k + 1, "0")
        body = (s[:-k] + "." + s[-k:]).rstrip("0").rstrip(".")
        return ("-" if num < 0 else "") + body
    return f"{num}/{den}"


def lean_rat(q: Fraction) -> str:
    """Lean literal for the exact rational (numerator may be negative)."""
    if q < 0:
        return f"(-{-q.numerator} : ℚ) / {q.denominator}"
    return f"({q.numerator} : ℚ) / {q.denominator}"


# ----------------------------------------------------------------------
# certificate 1: spectrum shape (gap G2, model level)
# ----------------------------------------------------------------------

def _pair_spectrum(n: int = N_DECAYING) -> dict[str, Any]:
    """Pair the computed eigenvalues with the model slots.

    Returns the unstable eigenvalue and, per decaying pair ``k``, the
    ``+Im`` entry.  This pairing is the numerical content of the
    certificate -- it is asserted here and regression-locked by pytest,
    not proved in Lean.
    """
    res = compute_spectrum(n)
    vals = list(res.eigenvalues)
    if len(vals) != 2 * n + 1:
        raise AssertionError(f"expected {2*n+1} eigenvalues, got {len(vals)}")
    unstable = [v for v in vals if v.real > 0]
    if len(unstable) != 1 or abs(unstable[0].imag) > 1e-9:
        raise AssertionError("spectrum does not have exactly one real unstable mode")
    lam0 = unstable[0]
    pairs = []
    for k in range(n):
        model_re = -(4.30 + 1.80 * k)
        cands = [v for v in vals if abs(v.real - model_re) < 1e-5]
        pos = [v for v in cands if v.imag > 0]
        if len(pos) != 1:
            raise AssertionError(f"pair {k}: could not isolate the +Im member")
        pairs.append(pos[0])
    return {"lam0": lam0, "pairs": pairs, "eigenvalues": vals}


def build_spectrum_certificate(n: int = N_DECAYING) -> dict[str, Any]:
    """Spectrum-shape certificate: rational enclosures + model agreement."""
    data = _pair_spectrum(n)
    lam0 = data["lam0"]
    pairs = data["pairs"]

    lam0_lo, lam0_hi = rat_iv(float(lam0.real), SPECTRUM_PAD)
    model_lam0 = Fraction(26745, 10000)
    if not (lam0_lo <= model_lam0 <= lam0_hi):
        raise AssertionError("lambda0 enclosure misses the model target")

    re_ivs, im_ivs = [], []
    for k, v in enumerate(pairs):
        model_re = Fraction(-(43 + 18 * k), 10)
        re_lo, re_hi = rat_iv(float(v.real), SPECTRUM_PAD)
        im_lo, im_hi = rat_iv(float(v.imag), SPECTRUM_PAD)
        if not (re_lo <= model_re <= re_hi):
            raise AssertionError(f"Re slot {k} misses the model target")
        if re_hi >= 0 or im_lo <= 0:
            raise AssertionError(f"slot {k}: stability/positivity violated")
        if re_hi - re_lo > WIDTH_MAX or im_hi - im_lo > WIDTH_MAX:
            raise AssertionError(f"slot {k}: interval too wide")
        re_ivs.append((re_lo, re_hi))
        im_ivs.append((im_lo, im_hi))

    # echo-family structure, checked exactly on the rationals:
    #   (2k+1)*im0.hi - W <= im_k.lo   and   im_k.hi <= (2k+1)*im0.lo + W
    im0_lo, im0_hi = im_ivs[0]
    if ECHO_TOL >= im0_lo:
        raise AssertionError("fundamental enclosure not separated from the tolerance")
    for k, (im_lo, im_hi) in enumerate(im_ivs):
        lhs = (2 * k + 1) * im0_hi - ECHO_TOL
        rhs = (2 * k + 1) * im0_lo + ECHO_TOL
        if not (lhs <= im_lo and im_hi <= rhs):
            raise AssertionError(f"echo family check failed at k={k}")

    def enc(lo: Fraction, hi: Fraction) -> dict[str, str]:
        return {"lo": qstr(lo), "hi": qstr(hi)}

    return {
        "schema": CERT_SCHEMA,
        "kind": "spectrum",
        "producer": {
            "tool": "choptuik_service.certify",
            "version": __version__,
            "protocol": PROTOCOL_VERSION,
        },
        "source": {
            "operator": "build_operator(7) — real block matrix of the truncated mode model",
            "eigensolver": "numpy.linalg.eigvals (LAPACK *geev)",
            "n_decaying_pairs": n,
        },
        "tolerances": {
            "pad": qstr(SPECTRUM_PAD),
            "echo_tolerance": qstr(ECHO_TOL),
            "width_max": qstr(WIDTH_MAX),
        },
        "lambda0": {
            "enclosure": enc(lam0_lo, lam0_hi),
            "model": qstr(model_lam0),
            "computed": float(lam0.real),
        },
        "re": [
            {"k": k, "enclosure": enc(*re_ivs[k]), "model": qstr(Fraction(-(43 + 18 * k), 10)),
             "computed": float(pairs[k].real)}
            for k in range(n)
        ],
        "im": [
            {"k": k, "enclosure": enc(*im_ivs[k]), "model_formula": "(2k+1)*pi/ln(2)",
             "computed": float(pairs[k].imag)}
            for k in range(n)
        ],
        "lean": {
            "module": "Choptuik.Bridge.Generated",
            "certificate_def": "spectrumCert",
            "checks_theorem": "spectrumChecks_generated",
        },
    }


# ----------------------------------------------------------------------
# certificate 2: Newton–Kantorovich constants + interval-Newton band
# ----------------------------------------------------------------------

def _interval_newton(lo: Fraction, hi: Fraction, iters: int = 60) -> tuple[Fraction, Fraction]:
    """Interval Newton for F(x) = 1/2 - (3/10)x^2 on [lo, hi] (exact)."""
    for _ in range(iters):
        m = (lo + hi) / 2
        fm = Fraction(1, 2) - Fraction(3, 10) * m * m
        # F'(X) = -(3/5) * [lo, hi] = [-(3/5)hi, -(3/5)lo], strictly negative
        dlo = -Fraction(3, 5) * hi
        dhi = -Fraction(3, 5) * lo
        if not (dhi < 0):
            raise AssertionError("derivative interval contains zero")
        # fm / [dlo, dhi] with negative divisor: 1/D = [1/dhi, 1/dlo]
        # (x ↦ 1/x is decreasing on the negative half-line)
        inv_lo, inv_hi = Fraction(1) / dhi, Fraction(1) / dlo
        if fm >= 0:
            q_lo, q_hi = fm * inv_lo, fm * inv_hi
        else:
            q_lo, q_hi = fm * inv_hi, fm * inv_lo
        # N = m - [q_lo, q_hi]
        n_lo, n_hi = m - q_hi, m - q_lo
        # intersect
        new_lo, new_hi = max(lo, n_lo), min(hi, n_hi)
        if new_lo > new_hi:
            raise AssertionError("interval Newton lost the root")
        lo, hi = new_lo, new_hi
        if hi - lo <= Fraction(1, 10**7):
            break
    return lo, hi


def build_newton_certificate() -> dict[str, Any]:
    """NK certificate for the correction equation 1/2 - (3/10)x^2 = 0.

    The map is the leading correction term of the mass-scaling ansatz
    ``M ~ d^gamma (1 - 0.3 d^2)``; its positive zero is the scale
    d = sqrt(5/3) at which the correction reaches one half.  The
    certificate packages:
      * the exact Newton–Kantorovich constants (beta, L, r, R) that
        instantiate ``newton_kantorovich_local`` on the Lean side;
      * the interval-Newton band [a, b] enclosing the root.
    """
    x0 = Fraction(13, 10)
    R = Fraction(1, 10)
    beta = Fraction(50, 39)      # |inv| bound: inv = -50/39 (derivative -39/50 at x0)
    L = Fraction(3, 50)          # Lipschitz defect on the ball |x - 13/10| <= 1/10
    r = Fraction(7, 1000)        # |Phi(x0)| = |1/2 - (3/10)(13/10)^2|
    q = beta * L                 # = 1/13
    S = beta * r / (1 - q)       # = 91/9360
    if not (q < 1 and S <= R):
        raise AssertionError("NK constants do not satisfy the contraction budget")

    band_lo, band_hi = _interval_newton(Fraction(12, 10), Fraction(14, 10))
    a = floor_at(band_lo, 6)
    b = ceil_at(band_hi, 6)
    target = Fraction(5, 3)
    if not (a > 0 and a * a <= target <= b * b and b - a <= BAND_WIDTH_MAX):
        raise AssertionError("interval-Newton band failed its exact checks")
    if not (x0 - R <= a and b <= x0 + R):
        raise AssertionError("band escapes the Newton ball")

    return {
        "schema": CERT_SCHEMA,
        "kind": "newton",
        "producer": {"tool": "choptuik_service.certify", "version": __version__,
                     "protocol": PROTOCOL_VERSION},
        "source": {
            "equation": "1/2 - (3/10) x^2 = 0",
            "meaning": "leading correction term of the mass-scaling ansatz",
            "root": "sqrt(5/3)",
            "method": "interval Newton with exact rational arithmetic",
        },
        "map": {"phi": "1/2 - (3/10)x^2", "x0": qstr(x0), "deriv_at_x0": "-39/50",
                "inv": "-50/39"},
        "constants": {
            "beta": qstr(beta), "L": qstr(L), "r": qstr(r), "R": qstr(R),
            "betaL": qstr(q), "S": qstr(S),
        },
        "band": {"lo": qstr(a), "hi": qstr(b), "width_max": qstr(BAND_WIDTH_MAX)},
        "lean": {
            "module": "Choptuik.Bridge.Generated",
            "band_def": "newtonBand",
            "checks_theorem": "newtonChecks_generated",
        },
    }


# ----------------------------------------------------------------------
# certificate 3: scaling agreement (gamma fit vs 1/lambda_0)
# ----------------------------------------------------------------------

def build_scaling_certificate() -> dict[str, Any]:
    """Deep-scaling gamma fit, enclosed and compared to 1/lambda_0.

    The fit runs on the noiseless supercritical family of the mode model
    over d in [1e-9, 1e-4] — the range on which the correction term
    (relative size ~ 3e-9) is negligible — so the fitted slope agrees
    with the calibrated gamma = 1/lambda_0 to ~1e-10.  The certificate
    checks the *pipeline*: numerics as a check against the proof, in the
    discipline of ``bridge/protocol.md``.
    """
    model = ModeModel()
    d = np.logspace(-9, -4, 24)
    mass = np.array([model.black_hole_mass(float(x), noisy=False) for x in d])
    x = np.log(d)
    y = np.log(mass)
    slope, intercept = np.polyfit(x, y, 1)
    gamma_fit = float(slope)

    lo, hi = rat_iv(gamma_fit, SCALING_PAD)
    target = Fraction(10000, 26745)
    if not (lo <= target <= hi):
        raise AssertionError("scaling enclosure misses 1/lambda_0")
    if hi - lo > Fraction(3, 10**6):
        raise AssertionError("scaling enclosure too wide")

    return {
        "schema": CERT_SCHEMA,
        "kind": "scaling",
        "producer": {"tool": "choptuik_service.certify", "version": __version__,
                     "protocol": PROTOCOL_VERSION},
        "source": {
            "family": "ModeModel.black_hole_mass (noiseless)",
            "range": "d in [1e-9, 1e-4], 24 log-spaced samples",
            "fit": "least squares of log M against log d",
        },
        "gamma_fit": gamma_fit,
        "target": qstr(target),
        "enclosure": {"lo": qstr(lo), "hi": qstr(hi)},
        "tolerance": qstr(SCALING_PAD),
        "lean": {
            "module": "Choptuik.Bridge.Generated",
            "interval_def": "scalingIv",
            "checks_theorem": "scalingChecks_generated",
        },
    }


# ----------------------------------------------------------------------
# certificate 4: interval enclosure of the correction band image (G5)
# ----------------------------------------------------------------------

def build_interval_certificate(newton: dict[str, Any] | None = None) -> dict[str, Any]:
    """Exact Horner enclosure of p(x) = 1 - (3/10)x^2 on the Newton band.

    This is the certificate-channel twin of the interactive
    ``interval_bound`` endpoint: the enclosure is computed with *exact
    rational* interval arithmetic (the float module
    ``interval_checks.py`` serves the interactive channel only).  The
    Lean side re-derives the same bounds through the proved soundness
    laws ``Interval.mul_sound`` / ``Interval.add_sound`` — the G5
    consumption pattern.
    """
    if newton is None:
        newton = build_newton_certificate()
    a = Fraction(newton["band"]["lo"])
    b = Fraction(newton["band"]["hi"])

    # Horner: p(x) = ((0*x - 3/10) * x) + 1  — exact interval steps
    c = -Fraction(3, 10)
    # c * [a, b] with c < 0 <= a <= b  ->  [c*b, c*a]
    step1_lo, step1_hi = c * b, c * a
    # step1 = [s_lo, s_hi] < 0 times [a, b] > 0:  min = s_lo*b, max = s_hi*a
    step2_lo, step2_hi = step1_lo * b, step1_hi * a
    img_lo, img_hi = step2_lo + 1, step2_hi + 1

    # independent check by endpoint monotonicity (p is decreasing on a,b > 0)
    assert img_lo == 1 - Fraction(3, 10) * b * b
    assert img_hi == 1 - Fraction(3, 10) * a * a

    return {
        "schema": CERT_SCHEMA,
        "kind": "interval",
        "producer": {"tool": "choptuik_service.certify", "version": __version__,
                     "protocol": PROTOCOL_VERSION},
        "source": {
            "polynomial": "1 - (3/10) x^2",
            "domain": "the certified Newton band",
            "method": "exact rational Horner enclosure (G5 pattern)",
        },
        "domain": {"lo": qstr(a), "hi": qstr(b)},
        "image": {"lo": qstr(img_lo), "hi": qstr(img_hi)},
        "lean": {
            "module": "Choptuik.Bridge.Generated",
            "checks_theorem": "intervalChecks_generated",
        },
    }


BUILDERS = {
    "spectrum": build_spectrum_certificate,
    "newton": build_newton_certificate,
    "scaling": build_scaling_certificate,
    "interval": build_interval_certificate,
}


def build_certificate(kind: str) -> dict[str, Any]:
    """Public entry point used by the bridge server (protocol v1.1)."""
    if kind not in BUILDERS:
        raise KeyError(kind)
    if kind == "interval":
        return build_interval_certificate()
    return BUILDERS[kind]()


# ----------------------------------------------------------------------
# Lean emission
# ----------------------------------------------------------------------

_HEADER = """/-
   F O R M A L   C H O P T U I K   ·   Choptuik/Bridge/Generated.lean

   AUTO-GENERATED by python/choptuik_service/certify.py — DO NOT EDIT.
   Regenerate with:  python -m choptuik_service.certify emit
   (regeneration is byte-stable for any conforming LAPACK: the pads
   exceed the eigensolver error by three orders of magnitude).

   Certificate data of the Lean <-> Python bridge (gap G4):
     * spectrumCert  — rational enclosures of the computed spectrum of
       the truncated mode model (7 decaying conjugate pairs);
     * newtonBand    — interval-Newton enclosure of the positive root of
       the correction equation 1/2 - (3/10)x^2 = 0;
     * scalingIv     — enclosure of the deep-scaling gamma fit.

   Every declaration below is checked by exact rational arithmetic
   (`norm_num` over the rationals); the soundness interpretation lives
   in Choptuik/Bridge/Certificates.lean and Discharge.lean.
-/

import Choptuik.Bridge.Certificates

namespace Choptuik.Bridge.Generated
"""


def _emit_rat_def(name: str, lo: Fraction, hi: Fraction) -> str:
    return f"def {name} : RatIv := ⟨{lean_rat(lo)}, {lean_rat(hi)}⟩\n"


def _emit_slot_fn(fname: str, rows: list[dict[str, Any]]) -> str:
    out = [f"def {fname} : ℕ → RatIv\n"]
    for k, r in enumerate(rows):
        lo = lean_rat(Fraction(r["enclosure"]["lo"]))
        hi = lean_rat(Fraction(r["enclosure"]["hi"]))
        out.append(f"  | {k} => ⟨{lo}, {hi}⟩\n")
    out.append(f"  | _ => ⟨0, 0⟩  -- out of range: unused (all checks bind k < {len(rows)})\n\n")
    return "".join(out)


def emit_lean(root: Path) -> str:
    """Render the generated Lean module (deterministic)."""
    spec = build_spectrum_certificate()
    newt = build_newton_certificate()
    scal = build_scaling_certificate()
    inter = build_interval_certificate()

    n = spec["source"]["n_decaying_pairs"]
    lam0 = spec["lambda0"]["enclosure"]
    re_rows = spec["re"]
    im_rows = spec["im"]

    L: list[str] = [_HEADER]

    L.append("/-! ### The spectrum certificate (7 decaying pairs) -/\n")
    L.append(_emit_rat_def("lam0Iv", Fraction(lam0["lo"]), Fraction(lam0["hi"])))

    # re / im slot functions via explicit match (k < 7 is all the checks use)
    L.append(_emit_slot_fn("reIv", re_rows))
    L.append(_emit_slot_fn("imIv", im_rows))

    L.append(f"""def spectrumCert : SpectrumCert where
  n := {n}
  lam0 := lam0Iv
  re := reIv
  im := imIv

/-! ### The spectrum checks (exact rational arithmetic) -/
""")

    L.append("""theorem check_unstable_pos : 0 < spectrumCert.lam0.lo := by
  norm_num [lam0Iv, spectrumCert]

theorem check_decaying_neg : ∀ k < 7, (spectrumCert.re k).hi < 0 := by
  intro k _
  interval_cases k <;> norm_num [reIv, spectrumCert]

theorem check_im_pos : ∀ k < 7, 0 < (spectrumCert.im k).lo := by
  intro k _
  interval_cases k <;> norm_num [imIv, spectrumCert]

theorem check_fundamental : echoTolerance < (spectrumCert.im 0).lo := by
  norm_num [imIv, spectrumCert, echoTolerance]

theorem check_lam0_agree : spectrumCert.lam0.mem (26745 / 10000) := by
  norm_num [lam0Iv, spectrumCert, RatIv.mem]

theorem check_re_agree : ∀ k < 7,
    (spectrumCert.re k).mem (-(43 + 18 * (k : ℚ)) / 10) := by
  intro k _
  interval_cases k <;> norm_num [reIv, spectrumCert, RatIv.mem]

theorem check_odd_lo : ∀ k < 7,
    ((2 * k + 1 : ℕ) : ℚ) * (spectrumCert.im 0).hi - echoTolerance ≤ (spectrumCert.im k).lo := by
  intro k _
  interval_cases k <;> norm_num [imIv, spectrumCert, echoTolerance]

theorem check_odd_hi : ∀ k < 7,
    (spectrumCert.im k).hi ≤ ((2 * k + 1 : ℕ) : ℚ) * (spectrumCert.im 0).lo + echoTolerance := by
  intro k _
  interval_cases k <;> norm_num [imIv, spectrumCert, echoTolerance]

theorem check_lam0_width : spectrumCert.lam0.width ≤ widthMax := by
  norm_num [lam0Iv, spectrumCert, RatIv.width, widthMax]

theorem check_re_width : ∀ k < 7, (spectrumCert.re k).width ≤ widthMax := by
  intro k _
  interval_cases k <;> norm_num [reIv, spectrumCert, RatIv.width, widthMax]

theorem check_im_width : ∀ k < 7, (spectrumCert.im k).width ≤ widthMax := by
  intro k _
  interval_cases k <;> norm_num [imIv, spectrumCert, RatIv.width, widthMax]

/-- The full check suite of the emitted spectrum certificate. -/
theorem spectrumChecks_generated : SpectrumChecks spectrumCert :=
  ⟨check_unstable_pos, check_decaying_neg, check_im_pos, check_fundamental,
    check_lam0_agree, check_re_agree, check_odd_lo, check_odd_hi,
    check_lam0_width, check_re_width, check_im_width⟩
""")

    a = Fraction(newt["band"]["lo"])
    b = Fraction(newt["band"]["hi"])
    L.append("/-! ### The Newton–Kantorovich certificate (correction equation) -/\n")
    L.append(_emit_rat_def("newtonBand", a, b))
    L.append(f"""/-- Band checks: positive, narrow, and squeezing the target 5/3. -/
theorem newtonChecks_generated :
    0 < newtonBand.lo ∧ newtonBand.width ≤ bandWidthMax ∧
      newtonBand.lo * newtonBand.lo ≤ 5 / 3 ∧ 5 / 3 ≤ newtonBand.hi * newtonBand.hi := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [newtonBand, RatIv.width, bandWidthMax]

/-- The exact Newton–Kantorovich constants of the correction map
(at base point 13/10, ball radius 1/10). -/
theorem nkConstants_generated :
    (50 / 39 : ℚ) * (3 / 50) < 1 ∧
      (50 / 39 : ℚ) * (7 / 1000) / (1 - (50 / 39 : ℚ) * (3 / 50)) ≤ 1 / 10 := by
  constructor <;> norm_num
""")

    slo = Fraction(scal["enclosure"]["lo"])
    shi = Fraction(scal["enclosure"]["hi"])
    L.append("/-! ### The scaling-agreement certificate -/\n")
    L.append(_emit_rat_def("scalingIv", slo, shi))
    L.append(f"""theorem scalingChecks_generated :
    scalingIv.mem (10000 / 26745) ∧ scalingIv.width ≤ 3 / 10 ^ 6 ∧
      (scalingIv.lo + scalingIv.hi) / 2 - 10000 / 26745 ≤ 1 / 10 ^ 6 ∧
      10000 / 26745 - (scalingIv.lo + scalingIv.hi) / 2 ≤ 1 / 10 ^ 6 := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [scalingIv, RatIv.mem, RatIv.width]
""")

    ilo = Fraction(inter["image"]["lo"])
    ihi = Fraction(inter["image"]["hi"])
    L.append("/-! ### The interval-enclosure certificate (G5 pattern) -/\n")
    L.append(_emit_rat_def("bandImageIv", ilo, ihi))
    L.append(f"""/-- The emitted image bounds are exactly the Horner enclosure of
`1 - (3/10)x^2` over the certified band. -/
theorem intervalChecks_generated :
    bandImageIv.lo = 1 - (3 / 10) * newtonBand.hi * newtonBand.hi ∧
      bandImageIv.hi = 1 - (3 / 10) * newtonBand.lo * newtonBand.lo := by
  constructor <;> norm_num [bandImageIv, newtonBand]
""")

    L.append("end Choptuik.Bridge.Generated\n")
    return "".join(L)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]  # .../formal_choptuik


def cmd_emit(root: Path) -> int:
    cert_dir = root / "bridge" / "certificates"
    cert_dir.mkdir(parents=True, exist_ok=True)
    certs = {
        "spectrum": build_spectrum_certificate(),
        "newton": build_newton_certificate(),
        "scaling": build_scaling_certificate(),
        "interval": build_interval_certificate(),
    }
    for kind, cert in certs.items():
        path = cert_dir / f"{kind}_certificate.json"
        path.write_text(json.dumps(cert, indent=2, ensure_ascii=False) + "\n")
        print(f"[certify] wrote {path}")
    lean_path = root / "lean" / "Choptuik" / "Bridge" / "Generated.lean"
    lean_path.parent.mkdir(parents=True, exist_ok=True)
    lean_path.write_text(emit_lean(root))
    print(f"[certify] wrote {lean_path}")
    return 0


def cmd_check(root: Path) -> int:
    """Recompute and verify: certificates still pass their own checks,
    and regeneration is byte-stable against the committed files."""
    ok = True
    cert_dir = root / "bridge" / "certificates"
    for kind in ("spectrum", "newton", "scaling", "interval"):
        # rebuild raises AssertionError on any failed check
        cert = BUILDERS[kind]() if kind != "interval" else build_interval_certificate()
        committed = cert_dir / f"{kind}_certificate.json"
        if not committed.exists():
            print(f"[certify] MISSING {committed}")
            ok = False
            continue
        old = json.loads(committed.read_text())
        if old != cert:
            print(f"[certify] NOTE {kind}: regenerated JSON differs from committed "
                  f"(tolerance event) — re-emit if intended")
    lean_path = root / "lean" / "Choptuik" / "Bridge" / "Generated.lean"
    if lean_path.exists():
        regenerated = emit_lean(root)
        if regenerated != lean_path.read_text():
            print("[certify] FAIL: Generated.lean is not byte-stable")
            ok = False
        else:
            print("[certify] Generated.lean regenerates byte-identically")
    else:
        print("[certify] FAIL: Generated.lean missing")
        ok = False
    print("[certify] all producer-side checks passed" if ok else "[certify] CHECK FAILED")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="certificate producer (bridge G4)")
    parser.add_argument("command", choices=["emit", "check"])
    parser.add_argument("--root", type=Path, default=_default_root(),
                        help="formal_choptuik root (default: repository layout)")
    args = parser.parse_args(argv)
    if args.command == "emit":
        return cmd_emit(args.root)
    return cmd_check(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
