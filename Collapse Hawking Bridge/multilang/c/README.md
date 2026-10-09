# C99 — bridge.c

Collapse-Hawking Bridge v2.0.0 · multilang self-test twin

---

## Run

```bash
gcc -O2 -std=c99 -o bridge bridge.c -lm && ./bridge
```

Toolchain: any C99 compiler

## Status

VERIFIED — executed on the packaging machine; output captured in reference_output.txt and cross-checked against the C++ and JavaScript twins (max relative deviation 7.1e-13).

## What it computes

The same 12-item validation block as every other twin (see the parent
[README](../README.md) for the full table): the septinial constant
`b_Ch = 1 - cos(2*pi/7)`, the Page fraction `1 - 2^(-3/2)`, the anchor
product `Delta*gamma = 1.28656`, the CMB contact mass `4.5016e+22 kg`,
the thermodynamic quartet `T_H / S_BH / t_evap / P_H` at 1e12 kg, three
Page-curve samples (including the exact `S_rad/S0 = 0.5` at the Page
time), the critical amplitude ladder (honest F-1 drift 2.79e-3 per doubling — the stale 1.06e-6 claim is retracted) and the floor law `(13 ± 1)/N`.

## Reading notes

The C twin is the shortest complete program in the package and the
recommended starting point for teaching: 70 lines from CODATA constants
to the floor law, no abstractions between the reader and the physics.

## Porting details

M_PI is POSIX, not C99 — the file #defines PI itself, so it compiles with -std=c99 -lm on any conforming libc.

## Cross-checks

* reference output (captured where verified): `c/reference_output.txt`
* diff target for portable sources: `../javascript/reference_output.txt`
* acceptance: max relative deviation <= 1e-11 across the 28 numeric fields

## See also

* [Parent README](../README.md) — the language matrix and the protocol.
* [chbridge (Python reference)](../../chbridge/README.md)
