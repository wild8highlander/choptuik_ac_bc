"""Typed client for the choptuik bridge service (protocol v1.1).

The Lean 4 side of the repository consumes the service through
CERTIFICATES (see :mod:`choptuik_service.certify`), not through live
floats.  This module is the typed client for the INTERACTIVE channel:
it decodes every response schema into frozen dataclasses, fails closed
on any malformed payload, and wraps the ZeroMQ REQ/REP exchange with a
timeout policy.  It is the Python twin of the illustrative
``bridge/examples/LeanClient.lean`` and the regression harness used by
the pytest suite (including the live round-trip test).

Design rules (mirroring ``bridge/protocol.md``):

* every decoder raises :class:`BridgeCodecError` — never a raw
  ``KeyError``/``TypeError`` — on malformed input (fuzz-safe);
* the socket exchange is strictly lock-step REQ/REP with a client-side
  timeout; a timeout raises :class:`BridgeTimeout` and the client
  closes the socket (fail closed, no retry by default: the caller
  decides whether a stale answer is still meaningful);
* all numbers are validated finite; NaN/Inf are rejected.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable

from . import __version__
from .certify import CERT_SCHEMA
from .server import PROTOCOL_VERSION

#: methods whose responses this client can decode
SUPPORTED_METHODS = (
    "ping",
    "spectrum",
    "scaling_fit",
    "echo_period",
    "evolve",
    "interval_bound",
    "certificate",
)

CERTIFICATE_KINDS = ("spectrum", "newton", "scaling", "interval")


class BridgeError(Exception):
    """Base class of client-side bridge failures."""


class BridgeCodecError(BridgeError):
    """A response payload did not match its schema."""


class BridgeTimeout(BridgeError):
    """The service did not answer within the timeout."""


class BridgeServerError(BridgeError):
    """The service answered with ``status: error``."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


# ----------------------------------------------------------------------
# validation helpers
# ----------------------------------------------------------------------

def _require_mapping(payload: Any, what: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BridgeCodecError(f"{what}: expected a JSON object, got {type(payload).__name__}")
    return payload


def _require(mapping: dict[str, Any], key: str, what: str) -> Any:
    if key not in mapping:
        raise BridgeCodecError(f"{what}: missing field {key!r}")
    return mapping[key]


def _number(x: Any, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise BridgeCodecError(f"{what}: expected a number, got {x!r}")
    v = float(x)
    if not math.isfinite(v):
        raise BridgeCodecError(f"{what}: non-finite number {v!r}")
    return v


def _integer(x: Any, what: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise BridgeCodecError(f"{what}: expected an integer, got {x!r}")
    return x


def _string(x: Any, what: str) -> str:
    if not isinstance(x, str):
        raise BridgeCodecError(f"{what}: expected a string, got {x!r}")
    return x


def _boolean(x: Any, what: str) -> bool:
    if not isinstance(x, bool):
        raise BridgeCodecError(f"{what}: expected a boolean, got {x!r}")
    return x


def _list(x: Any, what: str) -> list[Any]:
    if not isinstance(x, list):
        raise BridgeCodecError(f"{what}: expected an array, got {type(x).__name__}")
    return x


# ----------------------------------------------------------------------
# typed response schemas
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class PingReply:
    service: str
    protocol: str
    version: str
    lambda0: float
    gamma: float
    echo_period: float


@dataclass(frozen=True)
class SpectrumReply:
    eigenvalues: list[complex]
    single_unstable: bool
    lambda0: float
    gamma: float
    echo_spacing_max_error: float


@dataclass(frozen=True)
class ScalingFitReply:
    gamma_fit: float
    gamma_reference: float
    log_intercept: float
    rms_residual: float


@dataclass(frozen=True)
class EchoPeriodReply:
    delta_fit: float
    delta_reference: float
    abs_error: float


@dataclass(frozen=True)
class EvolveProfile:
    tau: float
    r: list[float]
    phi: list[float]


@dataclass(frozen=True)
class EvolveReply:
    profiles: list[EvolveProfile]
    eigenvalues: list[complex]


@dataclass(frozen=True)
class IntervalBoundReply:
    domain: tuple[float, float]
    image: tuple[float, float]
    width: float


@dataclass(frozen=True)
class CertificateReply:
    kind: str
    schema: str
    certificate: dict[str, Any] = field(repr=False)


# ----------------------------------------------------------------------
# decoders (one per method; all raise BridgeCodecError on bad input)
# ----------------------------------------------------------------------

def decode_ping(rep: Any) -> PingReply:
    m = _require_mapping(rep, "ping")
    c = _require_mapping(_require(m, "constants", "ping"), "ping.constants")
    return PingReply(
        service=_string(_require(m, "service", "ping"), "ping.service"),
        protocol=_string(_require(m, "protocol", "ping"), "ping.protocol"),
        version=_string(_require(m, "version", "ping"), "ping.version"),
        lambda0=_number(_require(c, "lambda0", "ping.constants"), "ping.constants.lambda0"),
        gamma=_number(_require(c, "gamma", "ping.constants"), "ping.constants.gamma"),
        echo_period=_number(_require(c, "echo_period", "ping.constants"),
                            "ping.constants.echo_period"),
    )


def decode_spectrum(rep: Any) -> SpectrumReply:
    m = _require_mapping(rep, "spectrum")
    evs = _list(_require(m, "eigenvalues", "spectrum"), "spectrum.eigenvalues")
    out: list[complex] = []
    for i, e in enumerate(evs):
        em = _require_mapping(e, f"spectrum.eigenvalues[{i}]")
        out.append(complex(
            _number(_require(em, "re", f"spectrum.eigenvalues[{i}]"),
                    f"spectrum.eigenvalues[{i}].re"),
            _number(_require(em, "im", f"spectrum.eigenvalues[{i}]"),
                    f"spectrum.eigenvalues[{i}].im"),
        ))
    return SpectrumReply(
        eigenvalues=out,
        single_unstable=_boolean(_require(m, "single_unstable", "spectrum"),
                                 "spectrum.single_unstable"),
        lambda0=_number(_require(m, "lambda0", "spectrum"), "spectrum.lambda0"),
        gamma=_number(_require(m, "gamma", "spectrum"), "spectrum.gamma"),
        echo_spacing_max_error=_number(
            _require(m, "echo_spacing_max_error", "spectrum"),
            "spectrum.echo_spacing_max_error"),
    )


def decode_scaling_fit(rep: Any) -> ScalingFitReply:
    m = _require_mapping(rep, "scaling_fit")
    return ScalingFitReply(
        gamma_fit=_number(_require(m, "gamma_fit", "scaling_fit"), "scaling_fit.gamma_fit"),
        gamma_reference=_number(_require(m, "gamma_reference", "scaling_fit"),
                                "scaling_fit.gamma_reference"),
        log_intercept=_number(_require(m, "log_intercept", "scaling_fit"),
                              "scaling_fit.log_intercept"),
        rms_residual=_number(_require(m, "rms_residual", "scaling_fit"),
                             "scaling_fit.rms_residual"),
    )


def decode_echo_period(rep: Any) -> EchoPeriodReply:
    m = _require_mapping(rep, "echo_period")
    return EchoPeriodReply(
        delta_fit=_number(_require(m, "delta_fit", "echo_period"), "echo_period.delta_fit"),
        delta_reference=_number(_require(m, "delta_reference", "echo_period"),
                                "echo_period.delta_reference"),
        abs_error=_number(_require(m, "abs_error", "echo_period"), "echo_period.abs_error"),
    )


def decode_evolve(rep: Any) -> EvolveReply:
    m = _require_mapping(rep, "evolve")
    profs = _list(_require(m, "profiles", "evolve"), "evolve.profiles")
    out: list[EvolveProfile] = []
    for i, p in enumerate(profs):
        pm = _require_mapping(p, f"evolve.profiles[{i}]")
        out.append(EvolveProfile(
            tau=_number(_require(pm, "tau", f"evolve.profiles[{i}]"),
                        f"evolve.profiles[{i}].tau"),
            r=[_number(v, f"evolve.profiles[{i}].r") for v in
               _list(_require(pm, "r", f"evolve.profiles[{i}]"), f"evolve.profiles[{i}].r")],
            phi=[_number(v, f"evolve.profiles[{i}].phi") for v in
                 _list(_require(pm, "phi", f"evolve.profiles[{i}]"), f"evolve.profiles[{i}].phi")],
        ))
    evs = _list(_require(m, "eigenvalues", "evolve"), "evolve.eigenvalues")
    zs: list[complex] = []
    for i, e in enumerate(evs):
        pair = _list(e, f"evolve.eigenvalues[{i}]")
        if len(pair) != 2:
            raise BridgeCodecError(f"evolve.eigenvalues[{i}]: expected [re, im]")
        zs.append(complex(_number(pair[0], f"evolve.eigenvalues[{i}].re"),
                          _number(pair[1], f"evolve.eigenvalues[{i}].im")))
    return EvolveReply(profiles=out, eigenvalues=zs)


def decode_interval_bound(rep: Any) -> IntervalBoundReply:
    m = _require_mapping(rep, "interval_bound")
    dom = _list(_require(m, "domain", "interval_bound"), "interval_bound.domain")
    img = _list(_require(m, "image", "interval_bound"), "interval_bound.image")
    if len(dom) != 2 or len(img) != 2:
        raise BridgeCodecError("interval_bound: domain/image must be [lo, hi]")
    return IntervalBoundReply(
        domain=(_number(dom[0], "interval_bound.domain.lo"),
                _number(dom[1], "interval_bound.domain.hi")),
        image=(_number(img[0], "interval_bound.image.lo"),
               _number(img[1], "interval_bound.image.hi")),
        width=_number(_require(m, "width", "interval_bound"), "interval_bound.width"),
    )


def decode_certificate(rep: Any) -> CertificateReply:
    m = _require_mapping(rep, "certificate")
    cert = _require_mapping(_require(m, "certificate", "certificate"), "certificate.payload")
    kind = _string(_require(cert, "kind", "certificate.payload"), "certificate.payload.kind")
    schema = _string(_require(cert, "schema", "certificate.payload"),
                     "certificate.payload.schema")
    if kind not in CERTIFICATE_KINDS:
        raise BridgeCodecError(f"certificate.payload.kind: unknown kind {kind!r}")
    if schema != CERT_SCHEMA:
        raise BridgeCodecError(f"certificate.payload.schema: expected {CERT_SCHEMA!r}, "
                               f"got {schema!r}")
    # spot-check the kind-specific mandatory structure
    if kind == "spectrum":
        for key in ("lambda0", "re", "im"):
            _require(cert, key, "certificate.payload")
    elif kind == "newton":
        for key in ("constants", "band"):
            _require(cert, key, "certificate.payload")
    elif kind == "scaling":
        for key in ("enclosure", "target"):
            _require(cert, key, "certificate.payload")
    else:
        for key in ("domain", "image"):
            _require(cert, key, "certificate.payload")
    return CertificateReply(kind=kind, schema=schema, certificate=cert)


#: method name -> decoder
DECODERS: dict[str, Callable[[Any], Any]] = {
    "ping": decode_ping,
    "spectrum": decode_spectrum,
    "scaling_fit": decode_scaling_fit,
    "echo_period": decode_echo_period,
    "evolve": decode_evolve,
    "interval_bound": decode_interval_bound,
    "certificate": decode_certificate,
}


# ----------------------------------------------------------------------
# the client (REQ/REP over ZeroMQ, fail closed)
# ----------------------------------------------------------------------

class BridgeClient:
    """Lock-step REQ client with typed decoding and a timeout policy.

    Parameters
    ----------
    endpoint:
        ZMQ endpoint of the service (default ``tcp://127.0.0.1:5557``).
    timeout:
        Client-side timeout in seconds (fail closed: a timeout raises
        :class:`BridgeTimeout` and the socket is closed).
    """

    def __init__(self, endpoint: str = "tcp://127.0.0.1:5557", timeout: float = 30.0) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._ctx = None
        self._sock = None

    # -- lifecycle ------------------------------------------------------
    def connect(self) -> None:
        zmq = self._zmq()
        self._ctx = zmq.Context()
        self._sock = self._ctx.socket(zmq.REQ)
        self._sock.setsockopt(zmq.LINGER, 0)
        self._sock.setsockopt(zmq.RCVTIMEO, int(self.timeout * 1000))
        self._sock.setsockopt(zmq.SNDTIMEO, int(self.timeout * 1000))
        self._sock.connect(self.endpoint)

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close(0)
            self._sock = None
        if self._ctx is not None:
            self._ctx.term()
            self._ctx = None

    def __enter__(self) -> "BridgeClient":
        self.connect()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    @staticmethod
    def _zmq() -> Any:
        try:
            import zmq  # optional extra
        except ImportError as exc:  # pragma: no cover
            raise BridgeError("pyzmq is not installed") from exc
        return zmq

    # -- the exchange ----------------------------------------------------
    def call(self, method: str, **params: Any) -> Any:
        """One lock-step exchange; returns the DECODED reply."""
        if method not in SUPPORTED_METHODS:
            raise BridgeCodecError(f"unsupported method: {method!r}")
        if self._sock is None:
            self.connect()
        assert self._sock is not None
        request: dict[str, Any] = {"method": method, **params}
        try:
            self._sock.send_json(request)
            raw = self._sock.recv_json()
        except Exception as exc:  # timeout or closed socket: fail closed
            self.close()
            raise BridgeTimeout(f"{method}: no answer within {self.timeout}s "
                                f"({type(exc).__name__})") from exc
        rep = _require_mapping(raw, method)
        status = _require(rep, "status", method)
        if status == "error":
            err = _require_mapping(_require(rep, "error", method), f"{method}.error")
            raise BridgeServerError(
                _string(_require(err, "code", f"{method}.error"), f"{method}.error.code"),
                _string(_require(err, "message", f"{method}.error"), f"{method}.error.message"),
            )
        if status != "ok":
            raise BridgeCodecError(f"{method}: unexpected status {status!r}")
        return DECODERS[method](rep)

    # -- typed convenience wrappers --------------------------------------
    def ping(self) -> PingReply:
        return self.call("ping")

    def spectrum(self, n_decaying: int = 7) -> SpectrumReply:
        return self.call("spectrum", n_decaying=int(n_decaying))

    def certificate(self, kind: str = "spectrum") -> CertificateReply:
        return self.call("certificate", kind=kind)


__all__ = [
    "BridgeClient",
    "BridgeCodecError",
    "BridgeError",
    "BridgeServerError",
    "BridgeTimeout",
    "CERTIFICATE_KINDS",
    "DECODERS",
    "SUPPORTED_METHODS",
    "CertificateReply",
    "EchoPeriodReply",
    "EvolveProfile",
    "EvolveReply",
    "IntervalBoundReply",
    "PingReply",
    "ScalingFitReply",
    "SpectrumReply",
    "decode_certificate",
    "decode_echo_period",
    "decode_evolve",
    "decode_interval_bound",
    "decode_ping",
    "decode_scaling_fit",
    "decode_spectrum",
]
