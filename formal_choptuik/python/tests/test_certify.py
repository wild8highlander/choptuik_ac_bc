"""Certificate producer tests (bridge G4, proof-grade channel).

Locks the honesty contract of the certificate flow:

* soundness — every emitted enclosure contains the model target it
  claims, with the advertised tightness;
* exactness — the arithmetic behind every certificate is exact
  (``fractions.Fraction``), including the interval-Newton band;
* determinism — rebuilding the certificates reproduces the committed
  JSON byte-for-byte, and regenerating the Lean module is byte-stable;
* coverage — the four certificate kinds round-trip through
  ``handle_request`` (protocol v1.1 ``certificate`` method).

Run from ``formal_choptuik/python``::

    python -m pytest tests/test_certify.py -v
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from choptuik_service.certify import (  # noqa: E402
    CERT_SCHEMA,
    build_certificate,
    build_interval_certificate,
    build_newton_certificate,
    build_scaling_certificate,
    build_spectrum_certificate,
    cmd_emit,
    emit_lean,
)
from choptuik_service.server import handle_request  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CERT_DIR = ROOT / "bridge" / "certificates"
GENERATED = ROOT / "lean" / "Choptuik" / "Bridge" / "Generated.lean"


# ----------------------------------------------------------------------
# spectrum certificate
# ----------------------------------------------------------------------

def test_spectrum_certificate_soundness() -> None:
    cert = build_spectrum_certificate()
    lam0 = Fraction(cert["lambda0"]["enclosure"]["lo"]), Fraction(cert["lambda0"]["enclosure"]["hi"])
    model = Fraction(cert["lambda0"]["model"])
    assert lam0[0] <= model <= lam0[1], "lambda0 enclosure must contain the model target"
    for k, row in enumerate(cert["re"]):
        lo, hi = Fraction(row["enclosure"]["lo"]), Fraction(row["enclosure"]["hi"])
        target = Fraction(-(43 + 18 * k), 10)
        assert lo <= target <= hi, f"Re slot {k} misses the model value"
        assert hi < 0, f"Re slot {k} must be strictly stable"
    for row in cert["im"]:
        assert Fraction(row["enclosure"]["lo"]) > 0, "echo slots must be positive"


def test_spectrum_certificate_tightness() -> None:
    cert = build_spectrum_certificate()
    pad = Fraction(cert["tolerances"]["pad"])
    width_max = Fraction(cert["tolerances"]["width_max"])
    lo, hi = Fraction(cert["lambda0"]["enclosure"]["lo"]), Fraction(cert["lambda0"]["enclosure"]["hi"])
    assert hi - lo <= width_max
    for section in ("re", "im"):
        for row in cert[section]:
            w = Fraction(row["enclosure"]["hi"]) - Fraction(row["enclosure"]["lo"])
            assert w <= width_max
    assert pad > 0 and pad < width_max  # pad is inside the width budget


def test_spectrum_echo_structure_exact() -> None:
    """The odd-multiple echo checks hold exactly on the rationals."""
    cert = build_spectrum_certificate()
    W = Fraction(cert["tolerances"]["echo_tolerance"])
    im = [(Fraction(r["enclosure"]["lo"]), Fraction(r["enclosure"]["hi"])) for r in cert["im"]]
    for k, (lo, hi) in enumerate(im):
        lhs = (2 * k + 1) * im[0][1] - W
        rhs = (2 * k + 1) * im[0][0] + W
        assert lhs <= lo, f"odd_lo fails at k={k}"
        assert hi <= rhs, f"odd_hi fails at k={k}"


# ----------------------------------------------------------------------
# newton certificate
# ----------------------------------------------------------------------

def test_newton_band_is_exact_and_squeezes_the_root() -> None:
    cert = build_newton_certificate()
    a = Fraction(cert["band"]["lo"])
    b = Fraction(cert["band"]["hi"])
    target = Fraction(5, 3)
    assert 0 < a <= b
    assert a * a <= target <= b * b
    assert b - a <= Fraction(cert["band"]["width_max"])
    # inside the Newton ball
    x0 = Fraction(cert["map"]["x0"])
    R = Fraction(cert["constants"]["R"])
    assert x0 - R <= a and b <= x0 + R


def test_newton_constants_satisfy_the_budget() -> None:
    cert = build_newton_certificate()
    beta = Fraction(cert["constants"]["beta"])
    L = Fraction(cert["constants"]["L"])
    r = Fraction(cert["constants"]["r"])
    R = Fraction(cert["constants"]["R"])
    assert beta * L < 1, "contraction budget"
    assert beta * r / (1 - beta * L) <= R, "displacement budget"
    # the documented exact values
    assert beta == Fraction(50, 39)
    assert L == Fraction(3, 50)
    assert r == Fraction(7, 1000)
    assert beta * L == Fraction(1, 13)
    assert beta * r / (1 - beta * L) == Fraction(7, 720)


# ----------------------------------------------------------------------
# scaling certificate
# ----------------------------------------------------------------------

def test_scaling_certificate_hits_the_theoretical_exponent() -> None:
    cert = build_scaling_certificate()
    lo = Fraction(cert["enclosure"]["lo"])
    hi = Fraction(cert["enclosure"]["hi"])
    target = Fraction(cert["target"])
    tol = Fraction(cert["tolerance"])
    assert lo <= target <= hi
    assert abs((lo + hi) / 2 - target) <= tol
    assert hi - lo <= Fraction(3, 10**6)


# ----------------------------------------------------------------------
# interval certificate
# ----------------------------------------------------------------------

def test_interval_certificate_matches_exact_horner() -> None:
    cert = build_interval_certificate()
    a = Fraction(cert["domain"]["lo"])
    b = Fraction(cert["domain"]["hi"])
    lo = Fraction(cert["image"]["lo"])
    hi = Fraction(cert["image"]["hi"])
    # p(x) = 1 - 3/10 x^2 is decreasing on a,b > 0
    assert lo == 1 - Fraction(3, 10) * b * b
    assert hi == 1 - Fraction(3, 10) * a * a
    # the half image contains the critical value 1/2 (root of p - 1/2 = 0)
    assert lo <= Fraction(1, 2) <= hi


# ----------------------------------------------------------------------
# determinism + committed artifacts
# ----------------------------------------------------------------------

def test_certificates_regenerate_deterministically() -> None:
    for kind in ("spectrum", "newton", "scaling", "interval"):
        first = build_certificate(kind)
        second = build_certificate(kind)
        assert first == second, f"{kind} certificate is not deterministic"
        assert json.dumps(first, indent=2) == json.dumps(second, indent=2)


def test_committed_certificates_match_rebuild() -> None:
    for kind in ("spectrum", "newton", "scaling", "interval"):
        committed = CERT_DIR / f"{kind}_certificate.json"
        assert committed.exists(), f"missing committed certificate {committed}"
        on_disk = json.loads(committed.read_text())
        assert on_disk == build_certificate(kind), (
            f"committed {kind} certificate diverged from the producer — "
            f"re-run `python -m choptuik_service.certify emit`"
        )


def test_generated_lean_module_is_byte_stable() -> None:
    assert GENERATED.exists(), "Generated.lean is missing"
    assert GENERATED.read_text() == emit_lean(ROOT), (
        "Generated.lean is not byte-stable under regeneration"
    )


def test_certificate_schema_fields() -> None:
    for kind in ("spectrum", "newton", "scaling", "interval"):
        cert = build_certificate(kind)
        assert cert["schema"] == CERT_SCHEMA
        assert cert["kind"] == kind
        producer = cert["producer"]
        assert producer["tool"] == "choptuik_service.certify"
        assert producer["protocol"] == "1.1"
        assert "version" in producer


# ----------------------------------------------------------------------
# protocol v1.1: the certificate method
# ----------------------------------------------------------------------

@pytest.mark.parametrize("kind", ["spectrum", "newton", "scaling", "interval"])
def test_certificate_method_roundtrip(kind: str) -> None:
    rep = handle_request({"method": "certificate", "kind": kind})
    assert rep["status"] == "ok"
    assert rep["certificate"]["kind"] == kind
    assert rep["certificate"] == build_certificate(kind)


def test_certificate_method_rejects_unknown_kind() -> None:
    rep = handle_request({"method": "certificate", "kind": "banana"})
    assert rep["status"] == "error"
    assert rep["error"]["code"] == "bad_input"


def test_certificate_method_default_kind() -> None:
    rep = handle_request({"method": "certificate"})
    assert rep["status"] == "ok"
    assert rep["certificate"]["kind"] == "spectrum"


def test_emit_cli_writes_all_artifacts(tmp_path: Path) -> None:
    # emit into a scratch root; must not touch the repository
    rc = cmd_emit(tmp_path)
    assert rc == 0
    for kind in ("spectrum", "newton", "scaling", "interval"):
        assert (tmp_path / "bridge" / "certificates" / f"{kind}_certificate.json").exists()
    gen = tmp_path / "lean" / "Choptuik" / "Bridge" / "Generated.lean"
    assert gen.exists()
    assert gen.read_text() == GENERATED.read_text(), "scratch emission differs from committed"
