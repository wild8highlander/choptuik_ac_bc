# C++17 — bridge.cpp

Collapse-Hawking Bridge v2.0.0 · multilang self-test twin

---

## Run

```bash
g++ -O2 -std=c++17 -o bridge bridge.cpp && ./bridge
```

Toolchain: any C++17 compiler (g++ / clang++ / MSVC 2019+)

## Status

VERIFIED — executed on the packaging machine; output captured in reference_output.txt and cross-checked against the C and JavaScript twins (max relative deviation 7.1e-13).

## What it computes

The same 12-item validation block as every other twin (see the parent
[README](../README.md) for the full table): the septinial constant
`b_Ch = 1 - cos(2*pi/7)`, the Page fraction `1 - 2^(-3/2)`, the anchor
product `Delta*gamma = 1.28656`, the CMB contact mass `4.5016e+22 kg`,
the thermodynamic quartet `T_H / S_BH / t_evap / P_H` at 1e12 kg, three
Page-curve samples (including the exact `S_rad/S0 = 0.5` at the Page
time), the critical amplitude ladder (honest F-1 drift 2.79e-3 per doubling — the stale 1.06e-6 claim is retracted) and the floor law `(13 ± 1)/N`.

## Reading notes

The C++ twin uses no headers beyond `<cmath>` and `<cstdio>`: no
classes, no templates, no iostream formatting surprises. printf keeps
the output byte-comparable with the C twin, which is the point — the
two differ by one letter in the filename and by the exponent operator.

## Porting details

M_PI is not standard C++; the file uses std::cos with 2.0 * M_PI via `<cmath>` on glibc. On MSVC add #define _USE_MATH_DEFINES before `<cmath>`.

## Cross-checks

* reference output (captured where verified): `cpp/reference_output.txt`
* diff target for portable sources: `../javascript/reference_output.txt`
* acceptance: max relative deviation <= 1e-11 across the 28 numeric fields

## See also

* [Parent README](../README.md) — the language matrix and the protocol.
* [chbridge (Python reference)](../../chbridge/README.md)
