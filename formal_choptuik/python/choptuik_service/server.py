"""JSON-over-ZMQ bridge service for the Lean 4 proof assistant.

Implements the server half of the ``formal_choptuik`` bridge protocol
(see ``bridge/protocol.md``).  The request dispatcher :func:`handle_request`
is a *pure function* on dictionaries so that the pytest suite can verify
the protocol without opening any socket; :func:`serve` merely wraps it in
a ZeroMQ REP loop.

Endpoints
---------
ping            -> liveness + version
spectrum        -> eigenvalue table of the linearized operator
scaling_fit     -> fit gamma from (delta_p, mass) samples
echo_period     -> recover the echoing period from an amplitude series
evolve          -> critical-evolution profiles at requested log-times
interval_bound  -> strict enclosure of a polynomial image (gap G5)
certificate     -> proof-grade rational certificate bundle (v1.1, gap G4)
"""

from __future__ import annotations

import importlib
from typing import Any

import numpy as np

from . import __version__
from .certify import build_certificate
from .evolver import (
    ECHO_PERIOD,
    GAMMA,
    LAMBDA0,
    ModeModel,
    echo_period_from_profile,
    fit_scaling_exponent,
)
from .interval_checks import Interval, _down, _up
from .spectrum import compute_spectrum

PROTOCOL_VERSION = "1.1"

CERTIFICATE_KINDS = ("spectrum", "newton", "scaling", "interval")


def _err(code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "error": {"code": code, "message": message}}


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Pure dispatcher: request dict in, response dict out."""
    if not isinstance(payload, dict):
        return _err("bad_request", "payload must be a JSON object")
    method = payload.get("method")

    if method == "ping":
        return {
            "status": "ok",
            "service": "choptuik-service",
            "protocol": PROTOCOL_VERSION,
            "version": __version__,
            "constants": {
                "lambda0": LAMBDA0,
                "gamma": GAMMA,
                "echo_period": ECHO_PERIOD,
            },
        }

    if method == "spectrum":
        n = int(payload.get("n_decaying", 7))
        res = compute_spectrum(n)
        return {
            "status": "ok",
            "eigenvalues": [
                {"re": float(v.real), "im": float(v.imag)} for v in res.eigenvalues
            ],
            "single_unstable": bool(res.single_unstable),
            "lambda0": res.lambda0,
            "gamma": 1.0 / res.lambda0,
            "echo_spacing_max_error": res.echo_spacing_max_error,
        }

    if method == "scaling_fit":
        try:
            dp = np.asarray(payload["delta_p"], dtype=float)
            mass = np.asarray(payload["mass"], dtype=float)
        except KeyError as exc:
            return _err("missing_field", f"missing field: {exc}")
        if dp.shape != mass.shape or dp.size < 3:
            return _err("bad_input", "delta_p and mass must be equal-length arrays of size >= 3")
        if np.any(dp <= 0) or np.any(mass <= 0):
            return _err("bad_input", "delta_p and mass must be strictly positive")
        gamma, intercept, rms = fit_scaling_exponent(dp, mass)
        return {
            "status": "ok",
            "gamma_fit": gamma,
            "gamma_reference": GAMMA,
            "log_intercept": intercept,
            "rms_residual": rms,
        }

    if method == "echo_period":
        try:
            tau = np.asarray(payload["tau"], dtype=float)
            amp = np.asarray(payload["amplitude"], dtype=float)
        except KeyError as exc:
            return _err("missing_field", f"missing field: {exc}")
        if tau.shape != amp.shape or tau.size < 16:
            return _err("bad_input", "need equal-length tau/amplitude arrays of size >= 16")
        try:
            delta = echo_period_from_profile(tau, amp)
        except RuntimeError as exc:
            return _err("no_echo", str(exc))
        return {
            "status": "ok",
            "delta_fit": delta,
            "delta_reference": ECHO_PERIOD,
            "abs_error": abs(delta - ECHO_PERIOD),
        }

    if method == "evolve":
        model = ModeModel(seed=int(payload.get("seed", 1993)))
        taus = payload.get("taus", [0.0, 0.25, 0.5])
        profiles = []
        for t in taus:
            p = model.profile(float(t))
            profiles.append({"tau": float(t), "r": model.grid.tolist(), "phi": p.tolist()})
        # v0.4.1 fix: complex values are not JSON-serializable — emit [re, im]
        # pairs exactly as bridge/protocol.md specifies (v0.3 sent raw complex)
        evs = [[float(v.real), float(v.imag)] for v in model.eigenvalues]
        return {"status": "ok", "profiles": profiles, "eigenvalues": evs}

    if method == "interval_bound":
        try:
            coeffs = [float(c) for c in payload["coefficients"]]
            lo = float(payload["lo"])
            hi = float(payload["hi"])
        except KeyError as exc:
            return _err("missing_field", f"missing field: {exc}")
        dom = Interval(_down(min(lo, hi)), _up(max(lo, hi)))
        enc = Interval.point(0.0).enclose_polynomial(coeffs, dom)
        return {
            "status": "ok",
            "domain": [dom.lo, dom.hi],
            "image": [enc.lo, enc.hi],
            "width": enc.width(),
        }

    if method == "certificate":
        kind = payload.get("kind", "spectrum")
        if kind not in CERTIFICATE_KINDS:
            return _err("bad_input", f"unknown certificate kind: {kind!r}")
        return {"status": "ok", "certificate": build_certificate(kind)}

    return _err("unknown_method", f"unknown method: {method!r}")


def serve(bind: str = "tcp://127.0.0.1:5557") -> None:  # pragma: no cover
    """Blocking REP loop. Requires the optional ``pyzmq`` extra."""
    zmq = importlib.import_module("zmq")
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REP)
    sock.bind(bind)
    print(f"[choptuik-service] listening on {bind} (protocol {PROTOCOL_VERSION})")
    try:
        while True:
            message = sock.recv_json()
            sock.send_json(handle_request(message))
    finally:
        sock.close(0)
        ctx.term()


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        demo = {"method": "ping"}
        print(json.dumps(handle_request(demo), indent=2))
    else:
        serve()
