# engine — the numeric engine (trio + Wu MC)

![v1.0.0](https://img.shields.io/badge/version-1.0.0-8C6D1F) ![validation](https://img.shields.io/badge/Kepler_e%3D0.5-rel_err_1.3e--9-brightgreen)

**TL;DR**

- `solver.py` is a self-contained NumPy engine: vectorised RK4 three-body
  with an oscillating geometric wall, early-escape freezing, Benettin
  Lyapunov exponents, the Poisson realisation of the Wu door, and the
  Kepler validation anchor.
- Determinism: the only RNG is `default_rng(20261010)`.

Committed engine parameters: softening `eps^2 = 1e-2` (documented toy
regularisation), `dt = 2e-3`, `t_end = 12`, `R_esc = 12`, ensemble
300 trials in the band `E in [-0.6, -0.05)`.

Validation: two-body ellipse `e = 0.5, a = 1, mu = 2` — measured period
4.442883 vs Kepler 4.442883, relative error **1.3e-9** (clean RK4
order; pinned by `tests/test_engine.py::test_kepler`).

Honesty notes: for `V0 > 0` the wall does physical work — the
energy-drift metric is reported only on `V0 = 0` runs; escape
statistics, not micro-dynamics, are the observable under softening.


## v1.1.0 — the confining core (C7)

`trio_accel`, `total_energy`, `trio_run` and `lyapunov` accept
`sigma = 0.0` (the default).  With `sigma > 0` every pair carries the
Cornell-like linear term `U_conf(r) = sigma * r_soft` (constant-
magnitude attraction; analytic Benettin Jacobian included).  At
`sigma = 0` the code path is byte-identical to v1.0.0: the campaign C7
regression gate re-measures the committed C2 free-trio escape count
with dev 0.0 exactly.  Honest scope: the Kepler anchor validates the
Newton law (sigma = 0) only; the sigma > 0 runs are an engine-level
hypothesis with no validation anchor beyond the regression gate and
the energy-drift report.
