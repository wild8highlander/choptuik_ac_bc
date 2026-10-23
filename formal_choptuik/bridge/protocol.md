# Bridge Protocol v1.0 — Lean ⇄ Python

> The contract that lets a proof assistant drive a numerical service.
> Lean 4 is the **client** (initiates every request); the Python service
> is the **server** (answers, never asks).  All payloads are UTF-8 JSON
> objects; all numbers are IEEE-754 doubles unless explicitly interval
> endpoints, which are always sent as `[lo, hi]` pairs.

## Transport

| Property | Value |
|---|---|
| Transport | ZeroMQ `REQ` / `REP` sockets |
| Default binding | `tcp://127.0.0.1:5557` |
| Framing | one JSON object per message (`sock.recv_json` / `send_json`) |
| Direction | Lean client → Python server → Lean client (strict lock-step) |
| Timeouts | recommended: 30 s client-side, fail closed |

## Envelope

**Request**

```json
{ "method": "<name>", ...parameters }
```

**Response (success)**

```json
{ "status": "ok", ...results }
```

**Response (failure)**

```json
{ "status": "error", "error": { "code": "<CODE>", "message": "..." } }
```

## Methods

### `ping`

Liveness + version + calibrated constants.

```json
→ { "method": "ping" }
← { "status": "ok", "service": "choptuik-service", "protocol": "1.0",
    "version": "0.3.0",
    "constants": { "lambda0": 2.6745, "gamma": 0.373902, "echo_period": 0.693147 } }
```

### `spectrum`

Diagonalize the linearized operator of the truncated mode model.

```json
→ { "method": "spectrum", "n_decaying": 7 }
← { "status": "ok",
    "eigenvalues": [ { "re": 2.6745, "im": 0.0 }, { "re": -4.3, "im": 4.5323 }, ... ],
    "single_unstable": true, "lambda0": 2.6745, "gamma": 0.373902,
    "echo_spacing_max_error": 2.0e-10 }
```

### `scaling_fit`

Least-squares fit of γ from a supercritical family.

```json
→ { "method": "scaling_fit", "delta_p": [1e-7, 1e-6, ...], "mass": [0.02, 0.04, ...] }
← { "status": "ok", "gamma_fit": 0.37388, "gamma_reference": 0.373902,
    "log_intercept": -0.22314, "rms_residual": 0.00213 }
```

### `echo_period`

Recover the echoing period Δ from an amplitude time series.

```json
→ { "method": "echo_period", "tau": [0.0, 0.01, ...], "amplitude": [1.0, 1.02, ...] }
← { "status": "ok", "delta_fit": 0.693147, "delta_reference": 0.693147,
    "abs_error": 1.2e-09 }
```

### `evolve`

Critical-evolution profiles at requested log-times.

```json
→ { "method": "evolve", "seed": 1993, "taus": [0.0, 0.5, 1.0] }
← { "status": "ok",
    "profiles": [ { "tau": 0.0, "r": [0.0, 0.0416, ...], "phi": [0.91, ...] }, ... ],
    "eigenvalues": [ [2.6745, 0.0], [-4.3, 4.5323], ... ] }
```

### `interval_bound`

Strict outward-rounded enclosure of a polynomial image (gap G5).

```json
→ { "method": "interval_bound", "coefficients": [1, -2, 1], "lo": 0.5, "hi": 1.5 }
← { "status": "ok", "domain": [0.5, 1.5], "image": [-1.25, 0.75], "width": 2.0 }
```

> Note: a Horner interval enclosure is *sound but may be wider* than the
> true image (dependency problem).  Soundness is the property the proof
> side relies on; tightness is the Python side's problem.

## Error codes

| Code | Meaning |
|---|---|
| `bad_request` | payload is not a JSON object |
| `unknown_method` | method name not in this table |
| `missing_field` | a required parameter is absent |
| `bad_input` | parameter present but invalid (shape, sign, size) |
| `no_echo` | the series does not exhibit a recoverable echo peak |

## Versioning & change discipline

* `protocol` field in every `ping` reply; breaking changes bump the
  major part and require a paired update of `bridge/protocol.md`,
  `python/choptuik_service/server.py` and the Lean client.
* Every protocol change must ship with a pytest in
  `python/tests/test_service.py` — the protocol is regression-locked.
* Numerical constants (`lambda0`, `gamma`, `echo_period`) are calibrated
  values; when Lean derives them formally (Phase 3), the Python values
  become *checks against the proof*, not sources of truth.
