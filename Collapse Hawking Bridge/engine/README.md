# engine — the double-null characteristic engine

![v2.2.0](https://img.shields.io/badge/version-2.2.0-8C6D1F) ![validation](https://img.shields.io/badge/Roberts--Oshiro-orders_2.03%2F2.09-brightgreen) ![units](https://img.shields.io/badge/units-4piG%3D1_(kappa%3D2)-blue)

**TL;DR**

- `solver.py` is a self-contained (~2000 lines, NumPy-only) engine for
  the spherical collapse of a massless scalar field in double-null
  coordinates: characteristic (Goursat) march, RK2-Heun, constraint
  monitoring, apparent-horizon finder.
- Verified against the exact Roberts (1989) solution with clean
  second-order convergence (orders 2.03 / 2.09 at N=400/800).
- The engine speaks geometric code units (`4 pi G = 1`); it knows
  nothing about physical masses — the mapping lives in `chbridge`.

**Contents**

- [The system](#the-system)
- [The method](#the-method)
- [Diagnostics and horizon finding](#diagnostics-and-horizon-finding)
- [Public API](#public-api)
- [Quick start](#quick-start)
- [Validation](#validation)
- [Performance](#performance)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)

---

## The system

Spherical Einstein-scalar system, double-null form
`ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2`, `omega := ln(alpha)`:

```
(SC)  Phi_uv   = -(r_u Phi_v + r_v Phi_u) / r
(UV)  r_uv     = -(r_u r_v + alpha^2/4) / r
(C1)  r_uu     = 2 omega_u r_u - (kappa/2) r Phi_u^2
(C2)  r_vv     = 2 omega_v r_v - (kappa/2) r Phi_v^2
(TH)  omega_uv = alpha^2 m / (2 r^3) - (kappa/2) Phi_u Phi_v
```

with the Misner-Sharp mass

```
1 - 2m/r = g^{ab} r_a r_b  <=>  m = (r/2)(1 + 4 r_u r_v / alpha^2).
```

The formulation is closed by regularity identities that keep the march
well-defined down to the centre `r = 0`:

```
(r^2)_uv = -alpha^2/2 ,     P := r r_u :  P_v = -alpha^2/4 ,
m_u = -kappa r^2 Phi_u^2 r_v / alpha^2 ,
m_v = -kappa r^2 Phi_v^2 r_u / alpha^2 .
```

The equation system was obtained by symbolic derivation (sympy) and
verified against the exact Roberts-Oshiro solution to residuals
~1e-41.

**Units:** `4 pi G = 1`, i.e. `kappa = 8 pi G = 2` (Burko
normalisation). All campaign data stay in these code units by design.

## The method

- **March:** characteristic integration over `v`-rows (Goursat
  problem), vectorised over `u` with NumPy.
- **Scheme:** second-order Heun predictor-corrector with a half-step
  predictor; the midpoint state is advanced with the trapezoidal
  combination of slopes.
- **Constraints, every row:** Hamiltonian `c1`, momentum `c2`, and the
  mass-definition identity `mdef` are recomputed from the evolved
  fields; their running maxima are carried in the diagnostics of
  every run (see the committed values in
  [docs/validation.md](../docs/validation.md#1-engine-validation-roberts-oshiro-regression)).
- **Stopping:** runs stop on apparent-horizon capture, on AH mass
  saturation (beyond the pulse total — the honest stop), or on
  completing the domain; the stop reason is a first-class field of
  every scan row.

## Diagnostics and horizon finding

The compactness monitor is `q = r_v`: capture when `q` turns negative.
At the `q = 0` point `m = r/2`, which is the apparent-horizon mass.
Diagnostics returned by `run()`:

| field | meaning |
|---|---|
| `ah_found` | apparent horizon captured during the run |
| `m_ah` | AH mass (code units) |
| `r_ah`, `v_ah` | areal radius and null time of capture |
| `stopped_reason` | `completed` / `AH mass saturated` / capture string |
| `c1_max`, `c2_max`, `mdef_max` | running maxima of the constraints |

Snapshots (with `monitor_every`) carry per-row `v`, `r`,
`two_m_over_r` arrays — the raw material for the evolution figures and
for the C3 echo detector.

## Public API

```python
from solver import (DoubleNullSolver, SolverConfig,
                    GaussianPulseData, RobertsData)

# the collapse family: Gaussian pulse of amplitude A at v_p
data = GaussianPulseData(A=0.081, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
cfg  = SolverConfig(n_u=400, n_v=400,
                    u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                    monitor_every=100)
sol  = DoubleNullSolver(cfg, data)
diag = sol.run(verbose=False)
diag.ah_found, diag.m_ah, diag.stopped_reason

# the exact solution used for regression
rdata = RobertsData(sigma=0.1)
r_ex, Phi_ex, _, _, _, _ = rdata.fields(sol.u, np.full_like(sol.u, sol.v_final))
```

## Quick start

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "engine")
from solver import DoubleNullSolver, GaussianPulseData, SolverConfig

data = GaussianPulseData(A=0.09, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
cfg  = SolverConfig(n_u=200, n_v=200, u_range=(-1.0, 1.05),
                    v_range=(0.0, 1.0), monitor_every=50)
diag = DoubleNullSolver(cfg, data).run(verbose=False)
print(diag.ah_found, diag.m_ah, diag.stopped_reason)
# True 0.02315... AH mass saturated
PY
```

Subcritical/supercritical boundary for this family sits near
`A* ~ 0.0805` at N=800 (see the grid-honesty ladder in
[docs/methods.md §3](../docs/methods.md#3-critical-amplitude-bisection-and-the-grid-honesty-ladder)).

## Validation

Roberts-Oshiro exact solution, band `u in (-0.3, 0.7)`, `v in (1, 2)`:

| grid N | max err r | order |
|-------:|----------:|------:|
| 200 | 4.686e-05 | — |
| 400 | 1.146e-05 | 2.031 |
| 800 | 2.687e-06 | 2.093 |

Re-run on every `pytest` invocation at N=200
(`tests/test_engine.py`); the full three-grid ladder is produced by
campaign C1.

## Performance

| task | grid | wall |
|---|---|---:|
| single run | N=200 | ~0.1 s |
| single run | N=400 | ~0.35 s |
| single run | N=800 | ~1.5-2 s |
| bisection A* (16-20 iters) | N=800 | ~46 s |
| campaign C1 (45 runs) | mixed | ~48 s |
| campaign C3 (31 runs) | N=800 | ~14 s |

Reference hardware: 4-core sandbox CPU; the march is NumPy-vectorised
over `u`, so single-core performance dominates.

## Honesty notes

- The engine has **no** tuned parameters: `kappa = 2` is the unit
  convention, `monitor_every` is bookkeeping. Nothing anywhere is
  calibrated to the literature anchors.
- At fixed grid the mass spectrum has a resolution floor (committed:
  `1.55e-2` code units at N=800); the engine does not hide it, and the
  campaigns commit it as a first-class result.
- The engine does not perform its own DSS analysis; the echo detector
  of campaign C3 is an estimator with declared limitations (see
  [docs/methods.md](../docs/methods.md#6-measuring-delta-the-log-time-echo-detector)).

## FAQ

**Q: Why double-null and not a 3+1 code?**
A: Spherical scalar collapse is exactly a two-characteristic problem;
double-null resolution of the critical point is the cleanest and the
standard tool for it (Choptuik 1993 methodology).

**Q: Can I use another matter model?**
A: The `GaussianPulseData` / `RobertsData` classes define the scalar
field initial data and exact targets; adding a family means adding a
data class with the same interface — see CONTRIBUTING.md.

**Q: Why is the solver not part of the `chbridge` package?**
A: Separation of duties: the engine measures (code units), the package
maps (SI units). Campaigns import the engine directly from `engine/`.

**Q: What is "AH mass saturated"?**
A: A stop state, not an error: the apparent-horizon mass reached the
scale of the whole pulse and the run's purpose (measuring the birth
spectrum) is over. These rows are committed and flagged, never dropped.

**Q: Is the engine deterministic?**
A: Yes — pure NumPy float arithmetic, no RNG anywhere; the same inputs
give bit-identical outputs (the data-rebuild determinism test relies on
this).

## See also

- [campaigns/](../campaigns/README.md) — what the engine measures
- [docs/methods.md](../docs/methods.md) — discretisation details
- [docs/validation.md](../docs/validation.md) — the validation ledger
- [chbridge/](../chbridge/README.md) — the mapping layer

---

## Краткое резюме (Russian)

`engine/solver.py` — автономный (~2000 строк, только NumPy) движок
сферического коллапса безмассового скалярного поля в двойных нулевых
координатах: характеристический марш Гурса, схема Хойна 2-го порядка,
мониторинг связей Гамильтона/импульса/определения массы на каждой
строке, поиск видимого горизонта по смене знака `q = r_v`. Единицы
`4πG = 1` (κ=2). Верифицирован на точном решении Робертса–Оширо:
порядок сходимости 2.03/2.09 (N=400/800), невязки связей ~1e-6…1e-7.
Никаких подгоночных параметров; массовый пол фиксированной сетки
(1.55e-2 кодовых единиц при N=800) — честный первоклассный результат,
закоммиченный в вердиктах кампаний.
