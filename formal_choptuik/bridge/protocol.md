# Bridge Protocol v1.1 — Lean ⇄ Python

> The contract that lets a proof assistant drive a numerical service.
> Lean 4 is the **client** (initiates every request); the Python service
> is the **server** (answers, never asks).  All payloads are UTF-8 JSON
> objects; all numbers are IEEE-754 doubles unless explicitly interval
> endpoints, which are always sent as `[lo, hi]` pairs — or **exact
> decimal rationals encoded as strings** on the certificate channel
> (v1.1), where nothing floating-point is allowed to cross.

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

### `certificate` (v1.1)

Proof-grade rational certificate bundle — the payload of the offline
> certificate channel (see *The certificate channel* below).

```json
→ { "method": "certificate", "kind": "spectrum" }
← { "status": "ok",
    "certificate": {
      "schema": "choptuik-certificate/1.0",
      "kind": "spectrum",
      "producer": { "tool": "choptuik_service.certify", "version": "0.4.1",
                    "protocol": "1.1" },
      "lambda0": { "enclosure": { "lo": "2.6744999", "hi": "2.674500101" },
                   "model": "2.6745", "computed": 2.6745 },
      ... } }
```

Kinds: `spectrum` (rational enclosures of the computed spectrum of the
truncated mode model), `newton` (Newton–Kantorovich constants + the
interval-Newton band of the correction equation), `scaling`
(deep-scaling γ-fit enclosure vs `1/λ₀`), `interval` (exact rational
Horner enclosure of the band image).  Unknown kinds are `bad_input`
errors.  Every rational is an **exact decimal string**; the response is
deterministic (regeneration is byte-stable).

## Error codes

| Code | Meaning |
|---|---|
| `bad_request` | payload is not a JSON object |
| `unknown_method` | method name not in this table |
| `missing_field` | a required parameter is absent |
| `bad_input` | parameter present but invalid (shape, sign, size) |
| `no_echo` | the series does not exhibit a recoverable echo peak |

## The certificate channel (v1.1, the proof-grade half of gap G4)

The interactive channel above is for exploration and calibration.  The
PROOF-FEEDING channel is offline and file-based — live floats never
enter the proof layer:

```
python/choptuik_service/certify.py
   │  compute (float64, LAPACK)
   │  + outward rounding to exact rationals (pads ≫ solver error)
   ├──▶ bridge/certificates/<kind>_certificate.json     (machine-readable)
   └──▶ lean/Choptuik/Bridge/Generated.lean             (Lean data + checks)
              │  norm_num over ℚ  (exact, machine-checked)
              ▼
        lean/Choptuik/Bridge/{Certificates,Discharge}.lean
           (robustness theorems turn checks into physics)
```

Division of labor (the honesty contract):

* **Lean proves**: the certificate checks (tightness, agreement with
  the rational model targets, echo structure) and the robustness
  theorems (`spectrum_shape_of_certificate`,
  `newton_kantorovich_local`, and the `Choptuik.Bridge.Discharge`
  headlines).
* **Python computes**: the numerical values and their PAIRING with the
  certificate slots — regression-locked by `tests/test_certify.py`,
  not by Lean.
* Regeneration is byte-stable for any conforming LAPACK (the pads
  exceed the eigensolver error by three orders of magnitude);
  `python -m choptuik_service.certify check` verifies the committed
  artifacts against a rebuild.

## Versioning & change discipline

* `protocol` field in every `ping` reply; breaking changes bump the
  major part and require a paired update of `bridge/protocol.md`,
  `python/choptuik_service/server.py` and the typed client
  (`python/choptuik_service/client.py`).
* v1.0 → v1.1 (this revision) is ADDITIVE: the new `certificate`
  method, the typed client codecs, and the offline certificate
  channel; all v1.0 methods keep their schemas (one latent v1.0 bug
  was fixed: `evolve` now emits `[re, im]` pairs as specified instead
  of non-serializable complex numbers).
* Every protocol change must ship with a pytest in
  `python/tests/` — the protocol is regression-locked.
* Numerical constants (`lambda0`, `gamma`, `echo_period`) are calibrated
  values; the certificate channel is the discipline through which they
  are CHECKED against the proof (`scaling_agreement`), not trusted.
