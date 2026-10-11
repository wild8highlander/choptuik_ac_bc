# chbridge — the Python core

![v2.1.0](https://img.shields.io/badge/version-2.1.0-8C6D1F) ![tests](https://img.shields.io/badge/pytest-63_passed-brightgreen) ![mpmath](https://img.shields.io/badge/validate-7%2F7_PASS-blue)

**TL;DR**

- `chbridge` is the importable core of the project: constants, closed-form
  black-hole thermodynamics, the bridge mapping `M_BH = M_in * f~(eps)`,
  Page-curve ensembles, scale ladders, and a 50-digit verification layer.
- Everything dimensionful flows from `constants.py` (Part A: CODATA 2018;
  Part B: engine anchors; Part C: committed campaign verdicts).
- Nothing here is fitted. Literature values are anchors; machine values
  point to the verdict files they came from.

**Contents**

- [Module map](#module-map)
- [constants.py — single source of truth](#constantspy--single-source-of-truth)
- [hawking.py — thermodynamic side](#hawkingpy--thermodynamic-side)
- [bridge.py — the mapping](#bridgepy--the-mapping)
- [page.py — Page curves](#pagepy--page-curves)
- [ladder.py — scale ladders](#ladderpy--scale-ladders)
- [validate.py — 50-digit layer](#validatepy--50-digit-layer)
- [Design decisions](#design-decisions)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)

---

## Module map

```
constants.py ──> hawking.py ──> bridge.py ──> data/bridge tables
     │               │              │
     │               └──> page.py   └──> figures (via scripts/)
     │                      │
     └──────────> ladder.py │
                    │       │
                    v       v
               validate.py (mpmath, 50 digits) — re-checks everything
```

Import surface:

```python
import chbridge
chbridge.__version__          # "2.1.0"
from chbridge.hawking import T_H, S_BH, t_evap, t_page, equal_CMB_mass
from chbridge.bridge import load_campaign, born_spectrum, master_table
```

## constants.py — single source of truth

Three parts, one rule: exact formulas or committed machine outputs,
nothing fitted.

| part | contents | examples |
|---|---|---|
| A | physical constants (CODATA 2018), cosmology (Planck 2018), Planck units, astronomical units | `G`, `c`, `hbar`, `k_B`, `T_CMB = 2.72548`, `l_P`, `m_P`, `M_sun` |
| B | engine anchors: septinial family (exact), clock theorems, QNM data, literature anchors | `delta_C = pi/7`, `b_Ch = 0.37651019814126640`, `gamma_Ch = 0.374` (anchor), `echo_delta = 3.44 +- 0.02` (anchor) |
| C | committed campaign verdicts + bridge input scales | `CAMPAIGN["a_star_N800"] = 0.08053436279296877`, `BRIDGE_SCALES` |

Also provided: `f_qnm_schwarzschild(M)` (l=2 ringdown frequency) and
`kretschmann_horizon(M)` / `kretschmann_planck()` (curvature scales).

The Delta*gamma invariant lives here as data:

```python
DGAMMA_TARGET = 1.27     # project hypothesis
DGAMMA_TOL    = 0.05     # acceptance tolerance
DGAMMA_LIT    = 1.28656  # anchor product 3.44 * 0.374
```

## hawking.py — thermodynamic side

Closed-form Schwarzschild thermodynamics. Every function is an exact
formula in CODATA constants — see the formula table in
[docs/theory.md](../docs/theory.md#1-the-two-pillars).

```python
from chbridge.hawking import *

M = 4.5016e22                 # kg — the CMB contact mass
T_H(M)                        # 2.7255 K  (= T_CMB by construction)
r_s(M)                        # 6.69e4 m
S_BH(M) / k_B                 # 5.37e61   (dimensionless)
t_evap(M)                     # 7.66e51 s
t_page(M)                     # 0.6464466 * t_evap(M)
equal_CMB_mass()              # 4.5016e22 kg
```

Conventions: `PAGE_FRACTION = 1 - 2**(-3/2) = 0.6464466094067262`; the
unitary entropy-flux kink meets at exactly `S0/2` (pinned by
`tests/test_page.py::test_curve_structure`). Formatters `fmt_len`,
`fmt_time`, `fmt_entropy` produce the human columns of
`data/bridge/bridge_master.csv`.

## bridge.py — the mapping

The bridge object is the dimensionless born spectrum measured by the
engine:

```
f~(eps) = M_code(eps) / M_code_sat ,    M_BH(eps; M_in) = M_in * f~(eps)
```

API:

| function | purpose |
|---|---|
| `load_campaign(path=None)` | load a verdict JSON (default: committed C1) |
| `born_spectrum(verdict)` | merge scans -> cleaned rows with `f~`, `(rows, M_sat)` |
| `ensemble_members(rows)` | `near_floor` / `mid` / `saturated` members |
| `master_table(verdict)` | 15 rows x 23 columns, SI units (5 scales x 3 members) |
| `write_outputs(verdict, out_dir)` | write `born_spectrum.csv`, `bridge_master.csv`, summary |

```python
from chbridge.bridge import load_campaign, master_table
v = load_campaign()                     # campaigns/reference/c1_verdict.json
master, members, M_sat = master_table(v)
row = next(r for r in master if r["input_scale"] == "CMB input"
                             and r["member"] == "saturated")
row["T_H_K"]                            # '2.726446e+00' — the contact point
```

Honesty rules encoded here: junk rows keep their flags; the near-critical
power law is an anchor comparison (`gamma_Ch`), never a fit of the
committed data; `gamma` is carried as honestly unmeasurable at fixed
grid.

## page.py — Page curves

Unitary entropy-flux model for the born ensemble:

```
S_BH(t)  = S0 (1 - t/t_evap)^{2/3}
S_rad(t) = S_BH(t)            t < t_Page      (young hole)
S_rad(t) = S0 - S_BH(t)       t > t_Page      (old hole)
```

plus the exact Haar-averaged Page formula (Page 1993 / Sen 1996) for
dimensions `m <= n`:

```
S(m, n) = ( sum_{k=n+1}^{mn} 1/k  -  (m-1)/(2n) ) / ln 2
```

| call | result |
|---|---|
| `curves(4.5e22)` | normalized tau, S_BH, S_rad, S0 grids (240 points) |
| `haar_avg_entropy(2, 2)` | 0.48016 bits (exact 1/3 nats) |
| `haar_avg_entropy(2, 4)` | 0.73511 bits |
| `write_outputs(dir)` | `page_curve_grid.csv` (720 rows), `page_members.csv` (15), `page_haar_check.csv` (18) |

The committed Monte-Carlo check (seeded, `default_rng(20260101)`)
agrees with the formula to **0.0042 bits** maximum over 18 partitions.

## ladder.py — scale ladders

Three comparison tables (accelerations, lengths, curvatures) mixing
cosmological scales (`c/H0`, `cH0/2pi`, MOND `a0`), horizon scales
(`kappa = c^4/4GM`, Kretschmann, `r_s/l_P`) and the Planck barrier
(`r_P ~ 1.9 l_P`). Plus `bridge_constants.csv`: the eight-row registry of
the project's dimensionless quantities (gamma anchor, `b_Ch`, the 0.67%
gap, `delta_C`, `Delta`, Page fraction, Delta*gamma target, A* agreement).

`write_outputs(dir)` writes all four CSVs. The ladders are comparisons:
no derivation of `a0` (or any cosmological quantity) from horizon physics
is claimed.

## validate.py — 50-digit layer

```python
python3 -m chbridge.validate
```

```
b_Ch identity + 0.67% gap  PASS    {'gap_pct': 0.666701}
PAGE_FRACTION              PASS    {'ref': 0.646447}
S~M^2, T~1/M, t~M^3        PASS    {}
CMB contact                PASS    {'M_CMB': 4.5015948405198975e+22}
Planck units               PASS    {}
Delta*gamma anchor arithmetic  PASS  {'product': 1.28656, 'dev': 0.01656}
Kretschmann scale law      PASS    {}
7/7 checks PASS (mpmath dps=50, chbridge v2.1.0)
```

Every closed-form constant is recomputed in 50-digit `mpmath`
arithmetic independently of the float values in `constants.py`;
`tests/test_ladder.py::test_validate_all_pass` requires `7/7`.

## Design decisions

1. **Flat package, no config files.** `import chbridge` works from a
   checkout without installation; `pyproject.toml` exists for
   `pip install -e .` convenience only.
2. **Verdicts over prints.** Functions that produce numbers write
   machine-readable files; console output is a courtesy, never the
   artifact.
3. **Anchors are data.** `gamma_Ch` and `echo_delta` sit in
   `constants.py` with the word *anchor* in their comments; no code
   path optimizes toward them.  The project's own `b_Ch` is a
   hypothesis constant, not an anchor: the former `b_Ch_lit` label
   (b_Ch rounded to 5 digits, once presented as a "literature
   anchor") was removed at v2.2.0 as self-referential.
4. **Relative imports inside, absolute honesty outside.** The package
   never mutates its inputs; `write_outputs` only ever writes into the
   directory you hand it.

## Honesty notes

- `constants.CAMPAIGN["gamma_campaign"]` is `None` on purpose: gamma is
  not percent-measurable at fixed grid (see
  [docs/methods.md](../docs/methods.md#5-measuring-gamma-protocol-and-floor)).
- The septinial coincidences (`b_Ch` vs `gamma_Ch`, 0.67%) are committed
  as comparisons; nothing in the package derives physics from them.
- Photon-only evaporation: committed lifetimes are idealisations
  (greybody factors out of scope).

## FAQ

**Q: Why does `master_table` return strings for numbers?**
A: The master table is a *rendering* of the mapping into CSV form; the
CSV writer needs stable column formatting. Parse with `float()` — the
underlying functions (`T_H`, `S_BH`, ...) return floats.

**Q: Can I plug in my own campaign verdict?**
A: Yes: `load_campaign("path/to/verdict.json")`, then
`write_outputs(v, "dir")`. The verdict must carry `scan_N400` /
`scan_N800` blocks in the C1 schema (see
[campaigns/README.md](../campaigns/README.md#verdict-schema)).

**Q: Where is the numerical engine?**
A: Deliberately not here. `chbridge` is the mapping layer; the
double-null engine lives in [engine/](../engine/README.md) and is used
by campaigns, not by the package.

**Q: Why does `equal_CMB_mass()` give 4.5016e22 and the master table
say 4.50e22?**
A: The input scale is the rounded anchor 4.50e22 kg; the exact inverse
formula gives 4.5016e22. Both appear on purpose — the rounded value is
the *scale*, the exact one the *prediction*.

**Q: Is `b_Ch = 0.37651` used anywhere as a physics input?**
A: No. It is exact framework data, committed and compared with
`gamma_Ch = 0.374` (0.67% gap). No derivation, no fit, no claim.

## See also

- [Root README](../README.md) — the project overview
- [docs/theory.md](../docs/theory.md) — the physics
- [docs/methods.md](../docs/methods.md) — the numerics
- [campaigns/](../campaigns/README.md) — how verdicts are produced
- [data/](../data/README.md) — where outputs land

---

## Краткое резюме (Russian)

`chbridge` — ядро проекта «Коллапс–Хокинг»: единый источник констант
(`constants.py`: CODATA-2018, септиниальное семейство `delta_C = pi/7`,
`b_Ch = 1 − cos(2π/7) = 0.37651019814126640`, вердикты кампаний),
замкнутые формулы термодинамики Шварцшильда (`hawking.py`), главный
мост `M_BH = M_in · f~(ε)` (`bridge.py`, таблица 15×23), ансамбль кривых
Пейджа с точной формулой усреднения Хаара (`page.py`, max 0.0042 бита),
лестницы масштабов (`ladder.py`) и 50-значный слой проверки на mpmath
(`validate.py`, 7/7 PASS). Ничего не подгоняется: литературные значения
— якоря для сравнения, машинные — ссылки на вердикты кампаний.
