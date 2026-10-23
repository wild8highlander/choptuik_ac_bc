<p align="center">
  <img src="../assets/banners/divider_photon.svg" alt="" width="60%">
</p>

# bridge/ — Lean ⇄ Python, typed at the border

![protocol](https://img.shields.io/badge/protocol-v1.0-4CC9F0?style=flat-square)
![transport](https://img.shields.io/badge/ZeroMQ-REQ/REP-4CC9F0?logo=zmq&logoColor=white&style=flat-square)
![binding](https://img.shields.io/badge/tcp-127.0.0.1:5557-8A8272?style=flat-square)
![client](https://img.shields.io/badge/Lean_FFI-C_ABI-9B8CDE?logo=lean&logoColor=white&style=flat-square)

The contract that lets the proof assistant *drive* the numerics without
ever trusting them.  Lean 4 initiates every request; the Python service
answers; raw floats never enter the proof layer — only interval
certificates do (the discipline of
[`blueprint/axiomatic_base.md`](../blueprint/axiomatic_base.md)).

```
Lean 4  ──FFI (C ABI)──▶  ZeroMQ REQ  ──tcp:5557──▶  choptuik-service (REP)
   ▲                                                     │
   └──────────────  interval certificates  ◀──────────────┘
```

## Contents

| File | Purpose |
|---|---|
| [`protocol.md`](protocol.md) | **the spec of record**: envelope, 6 methods with schemas, error codes, versioning discipline |
| [`examples/LeanClient.lean`](examples/LeanClient.lean) | illustrative typed client; shows the Phase-2 usage — `evolve` output feeds `existence_via_implicit_function` |

## Methods (v1.0)

| Endpoint | Returns | Feeds (Lean side) |
|---|---|---|
| `ping` | version + calibrated constants | session sanity |
| `spectrum` | eigenvalues, single-unstable flag | calibration target of G2 |
| `scaling_fit` | γ_fit, rms | check against `mass_scaling_law` |
| `echo_period` | Δ_fit | check against `echoingPeriod = ln 2` |
| `evolve` | profiles at requested log-times | numeric seed for G1 / IFT |
| `interval_bound` | sound enclosure `[lo, hi]` | strict bounds for the IFT route |

> [!TIP]
> Protocol changes are **regression-locked**: any change to
> `protocol.md` requires a paired pytest in
> [`python/tests/test_service.py`](../python/tests/test_service.py)
> in the same commit.  The bridge is part of the proof infrastructure —
> it follows the same change discipline as theorems.

## Production hardening (Phase 1, task P1.5)

The example client is deliberately illustrative.  Hardening lands as:
typed JSON codecs for each response schema, timeout + retry policy,
mutual authentication over `ipc://` for local setups, and a fuzz test
against malformed payloads — all behind the same `exchange` signature.

<p align="center">
  <img src="../assets/banners/divider_wave.svg" alt="" width="100%">
</p>
