# Go — bridge.go

Collapse-Hawking Bridge v2.0.0 · multilang self-test twin

---

## Run

```bash
go run bridge.go
```

Toolchain: Go >= 1.19

## Status

PORTABLE SOURCE — not executed on the packaging machine (no Go toolchain at packaging time). Run once locally and diff against ../javascript/reference_output.txt before relying on it.

## What it computes

The same 12-item validation block as every other twin (see the parent
[README](../README.md) for the full table): the septinial constant
`b_Ch = 1 - cos(2*pi/7)`, the Page fraction `1 - 2^(-3/2)`, the anchor
product `Delta*gamma = 1.28656`, the CMB contact mass `4.5016e+22 kg`,
the thermodynamic quartet `T_H / S_BH / t_evap / P_H` at 1e12 kg, three
Page-curve samples (including the exact `S_rad/S0 = 0.5` at the Page
time), the critical amplitude ladder (honest F-1 drift 2.79e-3 per doubling — the stale 1.06e-6 claim is retracted) and the floor law `(13 ± 1)/N`.

## Reading notes

The Go twin is written as package main with table-driven tests
left out on purpose: one file, one function, one output block. It uses
only math/ and fmt/ from the standard library.

## Porting details

Go prints float64 via %e with (int) cast semantics identical to C printf; the captured-protocol diff applies unchanged.

## Cross-checks

* reference output (captured where verified): `n/a (portable source)`
* diff target for portable sources: `../javascript/reference_output.txt`
* acceptance: max relative deviation <= 1e-11 across the 28 numeric fields

## See also

* [Parent README](../README.md) — the language matrix and the protocol.
* [chbridge (Python reference)](../../chbridge/README.md)
