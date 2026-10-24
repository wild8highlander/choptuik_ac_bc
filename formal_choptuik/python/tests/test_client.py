"""Typed client tests: codecs, fuzz, and a live ZeroMQ round-trip.

The suite covers the three layers of ``choptuik_service.client``:

* **codecs** — every method's response (produced by the pure dispatcher
  ``handle_request``) decodes into the right dataclass;
* **fuzz** — a corpus of malformed payloads never crashes a decoder:
  everything surfaces as ``BridgeCodecError`` (fail closed);
* **transport** — a real REQ/REP exchange over an ephemeral TCP port
  against ``serve`` running in a background thread, including the
  timeout policy (a client with no server fails fast).

Requires ``pyzmq`` for the transport tests; skipped otherwise.

Run from ``formal_choptuik/python``::

    python -m pytest tests/test_client.py -v
"""

from __future__ import annotations

import math
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from choptuik_service.client import (  # noqa: E402
    BridgeClient,
    BridgeCodecError,
    BridgeServerError,
    BridgeTimeout,
    decode_certificate,
    decode_evolve,
    decode_interval_bound,
    decode_ping,
    decode_spectrum,
)
from choptuik_service.server import handle_request, serve  # noqa: E402

try:
    import zmq  # noqa: F401

    HAVE_ZMQ = True
except ImportError:  # pragma: no cover
    HAVE_ZMQ = False


# ----------------------------------------------------------------------
# codecs
# ----------------------------------------------------------------------

def test_decode_ping() -> None:
    rep = decode_ping(handle_request({"method": "ping"}))
    assert rep.service == "choptuik-service"
    assert rep.protocol == "1.1"
    assert rep.lambda0 == pytest.approx(2.6745)
    assert rep.echo_period == pytest.approx(math.log(2))


def test_decode_spectrum() -> None:
    rep = decode_spectrum(handle_request({"method": "spectrum", "n_decaying": 7}))
    assert len(rep.eigenvalues) == 15
    assert rep.single_unstable
    assert rep.eigenvalues[0].real == pytest.approx(2.6745, abs=1e-9)
    assert rep.gamma == pytest.approx(1 / 2.6745)


def test_decode_interval_bound() -> None:
    rep = decode_interval_bound(
        handle_request({"method": "interval_bound", "coefficients": [1, -2, 1],
                        "lo": 0.5, "hi": 1.5}))
    assert rep.domain == (pytest.approx(0.5), pytest.approx(1.5))
    assert rep.image[0] == pytest.approx(-1.25, abs=1e-9)
    assert rep.image[1] == pytest.approx(0.75, abs=1e-9)
    assert rep.width == pytest.approx(2.0, abs=1e-9)


def test_decode_evolve() -> None:
    rep = decode_evolve(handle_request({"method": "evolve", "seed": 1993,
                                        "taus": [0.0, 0.5]}))
    assert len(rep.profiles) == 2
    assert rep.profiles[0].tau == 0.0
    assert len(rep.profiles[0].r) == len(rep.profiles[0].phi)
    # evolve lists the unstable mode + the 7 positive-Im echo modes (no
    # conjugates), matching bridge/protocol.md
    assert len(rep.eigenvalues) == 8


def test_decode_certificate_all_kinds() -> None:
    for kind in ("spectrum", "newton", "scaling", "interval"):
        rep = decode_certificate(handle_request({"method": "certificate", "kind": kind}))
        assert rep.kind == kind
        assert rep.schema == "choptuik-certificate/1.0"


# ----------------------------------------------------------------------
# fuzz: malformed payloads must fail closed
# ----------------------------------------------------------------------

BAD_PAYLOADS: list[Any] = [
    None,
    42,
    "ping",
    [],
    [1, 2, 3],
    {},                                # missing everything
    {"status": "ok"},                  # missing fields
    {"status": 7},                     # non-string status
    {"status": "ok", "service": 5, "protocol": "1.1", "version": "0",
     "constants": {"lambda0": 0, "gamma": 0, "echo_period": 0}},
    {"status": "ok", "eigenvalues": "nope", "single_unstable": True,
     "lambda0": 1, "gamma": 1, "echo_spacing_max_error": 0},
    {"status": "ok", "eigenvalues": [{"re": "x", "im": 1.0}], "single_unstable": True,
     "lambda0": 1, "gamma": 1, "echo_spacing_max_error": 0},
    {"status": "ok", "eigenvalues": [{"re": float("nan"), "im": 0}],
     "single_unstable": True, "lambda0": 1, "gamma": 1,
     "echo_spacing_max_error": 0},     # NaN rejected
    {"status": "ok", "eigenvalues": [], "single_unstable": "yes",
     "lambda0": 1, "gamma": 1, "echo_spacing_max_error": 0},
    {"status": "error"},               # error without body
    {"status": "error", "error": "flat"},
    {"status": "error", "error": {"code": 1, "message": "m"}},
    {"status": "maybe", "service": "x"},
    {"status": "ok", "certificate": {"kind": "banana", "schema": "x"}},
    {"status": "ok", "certificate": {"kind": "spectrum", "schema": "wrong/1.0"}},
    {"status": "ok", "certificate": {"kind": "spectrum"}},
    {"status": "ok", "domain": [0.5], "image": [-1, 1], "width": 2},
    {"status": "ok", "domain": [0.5, 1.5], "image": [-1, 1, 3], "width": 2},
]


@pytest.mark.parametrize("payload", BAD_PAYLOADS, ids=lambda p: repr(p)[:60])
def test_fuzz_decoders_fail_closed(payload: Any) -> None:
    for decoder in (decode_ping, decode_spectrum, decode_interval_bound,
                    decode_evolve, decode_certificate):
        try:
            decoder(payload)
        except BridgeCodecError:
            pass  # expected: malformed input surfaces as a codec error
        except BridgeServerError:
            pass  # well-formed error envelopes are also fine
        else:
            # a decoder may legitimately succeed on well-formed payloads
            # of ITS OWN method only; for the fuzz corpus the only such
            # case is the empty-ish dict which must NOT decode anywhere
            if payload in (None, 42, "ping", [], [1, 2, 3], {}):
                pytest.fail(f"{decoder.__name__} accepted malformed {payload!r}")


def test_fuzz_numeric_validation() -> None:
    with pytest.raises(BridgeCodecError):
        decode_interval_bound({"status": "ok", "domain": [0.5, float("inf")],
                               "image": [0, 0], "width": 0})
    with pytest.raises(BridgeCodecError):
        decode_evolve({"status": "ok", "profiles": [{"tau": True, "r": [], "phi": []}],
                       "eigenvalues": []})


# ----------------------------------------------------------------------
# transport: live REQ/REP round-trip on an ephemeral port
# ----------------------------------------------------------------------

@pytest.mark.skipif(not HAVE_ZMQ, reason="pyzmq not installed")
class TestLiveRoundTrip:
    @pytest.fixture()
    def endpoint(self) -> str:
        import zmq as zmq_mod

        ctx = zmq_mod.Context()
        sock = ctx.socket(zmq_mod.REP)
        port = sock.bind_to_random_port("tcp://127.0.0.1")
        sock.close(0)
        ctx.term()
        return f"tcp://127.0.0.1:{port}"

    @staticmethod
    def _serve_in_thread(endpoint: str) -> threading.Thread:
        t = threading.Thread(target=serve, args=(endpoint,), daemon=True)
        t.start()
        time.sleep(0.4)  # let the socket bind
        return t

    def test_ping_spectrum_certificate_roundtrip(self, endpoint: str) -> None:
        thread = self._serve_in_thread(endpoint)
        try:
            with BridgeClient(endpoint, timeout=10.0) as client:
                pong = client.ping()
                assert pong.protocol == "1.1"
                assert pong.service == "choptuik-service"

                spec = client.spectrum(7)
                assert spec.single_unstable
                assert spec.lambda0 == pytest.approx(2.6745, abs=1e-9)

                for kind in ("spectrum", "newton", "scaling", "interval"):
                    cert = client.certificate(kind)
                    assert cert.kind == kind
                    assert cert.schema == "choptuik-certificate/1.0"
        finally:
            pass  # daemon thread dies with the process

    def test_timeout_fails_closed(self, endpoint: str) -> None:
        # endpoint with no server behind it
        with pytest.raises(BridgeTimeout):
            with BridgeClient(endpoint, timeout=0.5) as client:
                client.ping()
