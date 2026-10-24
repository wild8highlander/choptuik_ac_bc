<p align="center">
  <img src="../assets/banners/divider_photon.svg" alt="" width="60%">
</p>

# bridge/ — Lean ⇄ Python, typed at the border

![protocol](https://img.shields.io/badge/protocol-v1.1-4CC9F0?style=flat-square)
![transport](https://img.shields.io/badge/ZeroMQ-REQ/REP-4CC9F0?logo=zmq&logoColor=white&style=flat-square)
![binding](https://img.shields.io/badge/tcp-127.0.0.1:5557-8A8272?style=flat-square)
![certificates](https://img.shields.io/badge/certificate_channel-live-43AA8B?style=flat-square)

The contract that lets the proof assistant *drive* the numerics without
ever trusting them.  Lean 4 initiates every request; the Python service
answers; raw floats never enter the proof layer — only exact rational
certificates do (the discipline of
[`blueprint/axiomatic_base.md`](../blueprint/axiomatic_base.md)).

## Two channels (v1.1)

```
INTERACTIVE (exploration, calibration)                PROOF-GRADE (offline, file-based)
─────────────────────────────────────                 ──────────────────────────────────
Lean 4 ──FFI (C ABI)──▶ ZeroMQ REQ ──tcp:5557──▶      certify.py: compute (LAPACK)
   ▲                choptuik-service (REP)             │ outward-round to exact rationals
   └────── typed replies (floats) ◀────                ├──▶ bridge/certificates/*.json
                                                       └──▶ lean/Choptuik/Bridge/Generated.lean
typed Python client: choptuik_service/client.py                │ norm_num over ℚ (machine-checked)
(schema-checked decoding, fail-closed timeouts)                ▼
                                                    Choptuik/Bridge/{Certificates,Discharge}.lean
                                                    (robustness theorems: checks ⇒ physics)
```

The proof-grade channel is the one the theory consumes: the pairing of
computed values with certificate slots is regression-locked by pytest,
everything below it is machine-checked in Lean — the honest boundary of
gap G4.

## Contents

| File | Purpose |
|---|---|
| [`protocol.md`](protocol.md) | **the spec of record**: envelope, 7 methods with schemas, error codes, the certificate channel, versioning discipline |
| [`certificates/`](certificates/) | committed certificate artifacts (exact decimal rationals, deterministic) |
| [`examples/LeanClient.lean`](examples/LeanClient.lean) | illustrative typed client; shows the FFI usage pattern (transport-level, no proof content) |

## Methods (v1.1)

| Endpoint | Returns | Feeds (Lean side) |
|---|---|---|
| `ping` | version + calibrated constants | session sanity |
| `spectrum` | eigenvalues, single-unstable flag | calibration target of G2 |
| `scaling_fit` | γ_fit, rms | check against `mass_scaling_law` |
| `echo_period` | Δ_fit | check against `echoingPeriod = ln 2` |
| `evolve` | profiles at requested log-times | numeric seed for G1 / IFT |
| `interval_bound` | sound enclosure `[lo, hi]` | strict bounds for the IFT route |
| `certificate` | **rational certificate bundle** (4 kinds) | `Choptuik.Bridge.Generated` (the proof-grade channel) |

## Certificate kinds

| Kind | Content | Lean consumer |
|---|---|---|
| `spectrum` | rational enclosures of the computed spectrum (7 decaying pairs) | `spectrumChecks_generated` → `bridge_unique_unstable_mode` |
| `newton` | NK constants (β, L, r, R) + interval-Newton band | `newtonChecks_generated` → `correction_root_in_band` |
| `scaling` | deep-scaling γ-fit enclosure vs `1/λ₀` | `scalingChecks_generated` → `scaling_agreement` |
| `interval` | exact Horner enclosure of the band image | `intervalChecks_generated` → `correction_band_image_sound` |

> [!TIP]
> Protocol changes are **regression-locked**: any change to
> `protocol.md` requires a paired pytest in
> [`python/tests/`](../python/tests/) in the same commit.  The bridge is
> part of the proof infrastructure — it follows the same change
> discipline as theorems.

## Working the certificate channel

```bash
# regenerate both artifacts (byte-stable; safe on any conforming LAPACK)
python -m choptuik_service.certify emit

# verify the committed artifacts against a rebuild
python -m choptuik_service.certify check

# rebuild the Lean side (checks + discharge)
cd ../lean && lake build
```

<p align="center">
  <img src="../assets/banners/divider_wave.svg" alt="" width="100%">
</p>
