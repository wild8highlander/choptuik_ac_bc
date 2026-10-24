"""Protocol regression tests for the choptuik numerical service.

The suite exercises the pure dispatcher (no sockets) and the calibrated
physics constants.  Run from ``formal_choptuik/python``::

    python -m pytest tests/ -v
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from choptuik_service import __version__  # noqa: E402
from choptuik_service.evolver import (  # noqa: E402
    ECHO_PERIOD,
    GAMMA,
    ModeModel,
    echo_period_from_profile,
    fit_scaling_exponent,
)
from choptuik_service.interval_checks import Interval  # noqa: E402
from choptuik_service.server import handle_request  # noqa: E402
from choptuik_service.spectrum import compute_spectrum  # noqa: E402


# ----------------------------------------------------------------------
# spectrum structure (gap G2, model level)
# ----------------------------------------------------------------------
def test_spectrum_has_single_unstable_mode() -> None:
    res = compute_spectrum()
    assert res.single_unstable, "exactly one unstable mode expected"
    assert res.lambda0 == pytest.approx(2.6745, abs=1e-3)


def test_spectrum_decaying_modes_left_halfplane() -> None:
    res = compute_spectrum()
    assert np.all(np.real(res.decaying) < 0), "all decaying modes left of the axis"


def test_spectrum_echo_spacing_matches_2pi_over_delta() -> None:
    res = compute_spectrum()
    assert res.echo_spacing_max_error < 1e-6, "Im spacing must equal 2*pi/Delta"


# ----------------------------------------------------------------------
# scaling law (gap G1 corollary)
# ----------------------------------------------------------------------
def test_scaling_fit_recovers_gamma() -> None:
    model = ModeModel()
    d = np.logspace(-7, -1.5, 24)
    m = np.array([model.black_hole_mass(x) for x in d])
    gamma, _, rms = fit_scaling_exponent(d, m)
    assert gamma == pytest.approx(GAMMA, abs=5e-3)
    assert rms < 0.01


def test_black_hole_mass_vanishes_at_threshold() -> None:
    model = ModeModel()
    assert model.black_hole_mass(1e-9) < model.black_hole_mass(1e-3)


# ----------------------------------------------------------------------
# echoing period (DSS signature)
# ----------------------------------------------------------------------
def test_echo_period_recovered_from_series() -> None:
    tau = np.linspace(0.0, 4.0, 400)
    amp = np.exp(0.55 * tau) * (1.0 + 0.35 * np.sin(2 * math.pi * tau / ECHO_PERIOD))
    delta = echo_period_from_profile(tau, amp)
    assert delta == pytest.approx(ECHO_PERIOD, abs=0.02)


def test_echo_constant_is_ln2() -> None:
    assert ECHO_PERIOD == pytest.approx(math.log(2.0), abs=1e-12)


# ----------------------------------------------------------------------
# interval arithmetic (gap G5)
# ----------------------------------------------------------------------
def test_interval_add_mul_outward_rounding() -> None:
    a = Interval.point(0.1) + Interval.point(0.2)
    assert a.lo <= 0.1 + 0.2 <= a.hi
    p = Interval.point(1.0 / 3.0) * Interval.point(3.0)
    assert p.lo <= 1.0 <= p.hi


def test_interval_polynomial_enclosure() -> None:
    # (x-1)^2 on [0.5, 1.5]: true image is [0, 0.25].  A Horner interval
    # evaluation is a *sound enclosure*: it must contain the true image,
    # but may be wider (the classic dependency problem of interval
    # arithmetic) — exactly what strict error bounds require.
    x = Interval(0.5, 1.5)
    enc = Interval.point(0.0).enclose_polynomial([1.0, -2.0, 1.0], x)
    assert enc.lo <= 0.0 <= enc.hi          # true minimum enclosed
    assert enc.contains(0.25)               # true maximum enclosed
    assert enc.width() < 4.0                # not degenerate


# ----------------------------------------------------------------------
# protocol dispatcher (bridge contract)
# ----------------------------------------------------------------------
def test_ping_roundtrip() -> None:
    reply = handle_request({"method": "ping"})
    assert reply["status"] == "ok"
    assert reply["version"] == __version__
    assert reply["constants"]["gamma"] == pytest.approx(0.374, abs=1e-3)


def test_unknown_method_is_an_error() -> None:
    reply = handle_request({"method": "nope"})
    assert reply["status"] == "error"
    assert reply["error"]["code"] == "unknown_method"


def test_scaling_fit_endpoint() -> None:
    model = ModeModel()
    d = np.logspace(-6, -2, 12)
    m = [model.black_hole_mass(x) for x in d]
    reply = handle_request(
        {"method": "scaling_fit", "delta_p": d.tolist(), "mass": m}
    )
    assert reply["status"] == "ok"
    assert abs(reply["gamma_fit"] - reply["gamma_reference"]) < 5e-3


def test_echo_endpoint() -> None:
    tau = np.linspace(0, 3, 300)
    amp = np.exp(0.5 * tau) * (1 + 0.3 * np.sin(2 * math.pi * tau / ECHO_PERIOD))
    reply = handle_request(
        {"method": "echo_period", "tau": tau.tolist(), "amplitude": amp.tolist()}
    )
    assert reply["status"] == "ok"
    assert abs(reply["delta_fit"] - reply["delta_reference"]) < 0.02


def test_interval_endpoint() -> None:
    reply = handle_request(
        {"method": "interval_bound", "coefficients": [1, -2, 1], "lo": 0.5, "hi": 1.5}
    )
    assert reply["status"] == "ok"
    lo, hi = reply["image"]
    assert lo <= 0.0 <= hi                  # sound enclosure of the minimum
    assert lo <= 0.25 <= hi                 # sound enclosure of the maximum


# ----------------------------------------------------------------------
# protocol v1.1: the certificate method (gap G4)
# ----------------------------------------------------------------------
def test_ping_reports_protocol_v1_1() -> None:
    reply = handle_request({"method": "ping"})
    assert reply["protocol"] == "1.1"


def test_certificate_endpoint_spectrum() -> None:
    reply = handle_request({"method": "certificate", "kind": "spectrum"})
    assert reply["status"] == "ok"
    cert = reply["certificate"]
    assert cert["kind"] == "spectrum"
    assert cert["schema"] == "choptuik-certificate/1.0"
    assert cert["source"]["n_decaying_pairs"] == 7
    assert len(cert["re"]) == 7 and len(cert["im"]) == 7


def test_certificate_endpoint_rejects_bad_kind() -> None:
    reply = handle_request({"method": "certificate", "kind": 42})
    assert reply["status"] == "error"
    assert reply["error"]["code"] == "bad_input"
