# tests

The pytest suite of the **Collapse-Hawking Bridge** — 60 tests in 7 files that
pin every committed number of the project to its defining formula, its campaign
verdict, or its committed data table. Tests pin numbers, not types.

![v1.1.0](https://img.shields.io/badge/version-1.1.0-gold)
![tests](https://img.shields.io/badge/tests-60_passed-brightgreen)
![runtime](https://img.shields.io/badge/wall_time-~1_s-gold)
![network](https://img.shields.io/badge/network-none-brightgreen)

**TL;DR**

- 60 tests in 7 files; the full suite passes in under a second (0.82 s measured).
- `test_campaigns.py` (17 tests) pins the committed machine verdicts of
  campaigns C2 and C3b: envelope, both C2 branches, the C3b floor ladder,
  the anchor product, and the derived CSV tables.
- Constants, closed-form thermodynamics, the Page model, the bridge tables,
  the scale ladders — and the double-null engine itself — are all pinned.
- `test_rebuild_determinism` asserts byte-identical CSV output across rebuilds;
  `test_validate_all_pass` runs the 50-digit `mpmath` layer (7/7) inside pytest.
- The campaign tests read committed JSON and CSV files only — no engine runs.
- No network, no fixtures beyond `tmp_path`, no skipped or xfail tests.

---

## Table of contents

- [Philosophy](#philosophy)
- [Inventory](#inventory)
- [How to run](#how-to-run)
- [Runtime budget](#runtime-budget)
- [How to add a test](#how-to-add-a-test)
- [Honesty notes](#honesty-notes)
- [FAQ](#faq)
- [See also](#see-also)
- [Краткое резюме (Russian)](#краткое-резюме-russian)

## Philosophy

Every committed number that can regress has a test. The suite is therefore a
contract in executable form:

- **Constants are pinned twice** — once to their exact defining identity
  (e.g. b_Ch = 1 − cos(2π/7)) and once to their committed decimal value
  (0.37651019814126640).
- **Physics closures are pinned to book-level reference values** — a solar
  black hole has r_s = 2954 m, T_H ≈ 6.17e-8 K, S_BH/k_B ≈ 1.0494e77.
- **Campaign outputs are pinned to their committed verdicts** — the A* ladder,
  the ensemble members, the junk-row flags, and the C2 and C3b machine
  verdicts as committed. If a campaign is re-run and a pin fails,
  the verdict genuinely changed — treat it as a bug or a CHANGELOG event,
  never as a reason to edit the test silently.
- **Determinism is a test, not a promise** — rebuilding the data tables twice
  must produce byte-identical files.
- The engine is tested by regression against the exact Roberts–Oshiro
  solution, at production solver settings, not against a mock.

`conftest.py` is two lines of substance: it puts the repository root on
`sys.path` so `chbridge` and `engine/` import without installation.

## Inventory

60 tests total. Per file:

| File | Tests | Subject |
|---|---:|---|
| `test_constants.py` | 10 | exact identities and committed campaign values |
| `test_hawking.py` | 9 | closed-form Schwarzschild thermodynamics |
| `test_page.py` | 7 | Page curves and the Haar-averaging check |
| `test_bridge.py` | 8 | born spectrum, members, master table, determinism |
| `test_ladder.py` | 7 | scale ladders plus the 50-digit validation layer |
| `test_engine.py` | 2 | double-null engine regression against exact solution |
| `test_campaigns.py` | 17 | the committed verdicts of campaigns C2 and C3b |

### `test_constants.py`

| Test | Purpose |
|---|---|
| `test_b_ch_exact_identity` | b_Ch = 1 − cos(2π/7) = 2 sin²(π/7) holds to 1e-15 |
| `test_b_ch_reference_value` | pins the 16-digit reference value 0.37651019814126640 |
| `test_b_ch_framework_gap` | b_Ch sits 0.67% from the literature anchor γ_Ch = 0.374 |
| `test_septinial_phase` | δ_C = π/7 exactly (to 1e-15) |
| `test_page_fraction` | PAGE_FRACTION = 1 − 2^(−3/2) = 0.6464466094067262 |
| `test_dgamma_anchor_product` | 3.44 × 0.374 = 1.28656, within tolerance of the 1.27 target |
| `test_qnm_relative_shift` | qnm_rel_shift = 1/(1200π²) = 8.44343e-5 |
| `test_clock_theorems_exact` | τ*(0) = 6.75; τ*(1 brick) = 1323/(196 − π²); berry_kappa = 2 − π²/98 |
| `test_campaign_astar_ladder` | committed A* ladder decreases with N; N=800 matches the N=1600 reference to 1.1e-6 |
| `test_planck_units_cross` | m_P ≈ 2.176434e-8 kg, l_P ≈ 1.616255e-35 m, t_P = l_P/c |

### `test_hawking.py`

| Test | Purpose |
|---|---|
| `test_schwarzschild_radius_solar` | r_s(M_sun) = 2954 m |
| `test_hawking_temperature_solar` | T_H(M_sun) ≈ 6.17e-8 K |
| `test_entropy_solar` | S_BH(M_sun)/k_B ≈ 1.0494e77, cross-checked against the master table's saturated solar row |
| `test_power_laws` | T ~ 1/M, S ~ M², t_evap ~ M³, P ~ 1/M², κ ~ 1/M across 10¹²…10¹⁸ kg |
| `test_page_fraction_exact` | t_Page/t_evap equals PAGE_FRACTION to 1e-15 |
| `test_cmb_contact` | T_H(M_CMB) = T_CMB at M_CMB ≈ 4.50e22 kg ≈ 0.61 lunar masses |
| `test_mean_density_scaling` | mean interior density scales as M⁻² |
| `test_human_formatting` | `fmt_time`/`fmt_len` render human strings (`yr`, `2953 m`, `2 mm`) |
| `test_page_continuity_at_kink` | at t_Page both entropy-flux branches meet at S_0/2 |

### `test_page.py`

| Test | Purpose |
|---|---|
| `test_member_profile_values` | member profile f̃ = 0.287708 / 0.268393 / 1.0 |
| `test_curve_structure` | S_rad = S_BH for young holes, S_rad = S_0 − S_BH for old, kink at S_0/2 |
| `test_haar_formula_known_case` | 2×2 Haar average = 1/3 nats = 0.48016 bits |
| `test_haar_known_case_2x4` | 2×4 case = 0.509524 nats = 0.735105 bits |
| `test_haar_requires_m_le_n` | the (lo, hi) factor ordering mirrors the project convention |
| `test_haar_monotonic_in_partition` | smaller-factor entropy is maximal at the balanced cut |
| `test_haar_mc_small_deviation` | seeded Haar Monte-Carlo agrees with the formula to < 0.02 bits (N ≤ 5) |

### `test_bridge.py`

| Test | Purpose |
|---|---|
| `test_born_spectrum_shape` | 44 scan rows (26 + 18); saturated mass in (0.05, 0.1); sane f̃ in (0, 1] |
| `test_ensemble_members` | near_floor / mid / saturated f̃ = 0.2877 / 0.2684 / 1.0 |
| `test_master_table_geometry` | 15 rows × 23 columns; saturated CMB member at T_H/T_CMB ≈ 1 |
| `test_master_table_horizon_identity` | r_s = 2GM/c² holds row-by-row inside the master table |
| `test_cmb_member_is_the_contact_point` | the saturated CMB-input member sits at the cosmological contact |
| `test_planck_input_member_above_planck_barrier` | r_s/l_P = 2.0 for the saturated Planck member |
| `test_rebuild_determinism` | two rebuilds produce a byte-identical `bridge_master.csv` |
| `test_summary_honesty_flags` | junk rows exist, are kept, and are labeled as such |

### `test_ladder.py`

| Test | Purpose |
|---|---|
| `test_a0_mond_coincidence` | a0/(cH0/2π) ∈ (1.10, 1.20) — a comparison, never a derivation |
| `test_gamma_vs_bch_gap` | |γ_Ch − b_Ch|/b_Ch = 0.67% |
| `test_surface_gravity_ordering` | κ decreases with mass along the ladder |
| `test_kretschmann_scale_law` | K(M)·M⁴ = 3c⁸/(4G⁴) is constant |
| `test_kretschmann_planck_value` | 1/l_P⁴ = c⁶/(ħ²G²) to 1e-12 relative |
| `test_ladder_writer_runs` | writer emits 7 + 8 + 5 + 8 rows into `tmp_path` |
| `test_validate_all_pass` | all 7 mpmath 50-digit checks pass |

### `test_engine.py`

| Test | Purpose |
|---|---|
| `test_roberts_regression_n200` | N=200 double-null march reproduces the exact Roberts–Oshiro solution: err_r < 1e-4, α² → 1, constraints c1 < 0.01, c2 < 1e-4, mdef < 1e-3 |
| `test_engine_units_and_config` | the engine declares κ = 2 (4πG = 1 units) |

### `test_campaigns.py`

The pins assert the committed machine outputs in `campaigns/reference/` —
the verdict JSONs and the derived CSVs of [data/bridge](../data/README.md).

| Test | Purpose |
|---|---|
| `test_c2_verdict_envelope` | C2 verdict: campaign id `chb_c2`, project_version 1.1.0, grid N=800, positive wall time, timestamp |
| `test_c3b_verdict_envelope` | C3b verdict: campaign id `chb_c3b`, project_version 1.1.0, positive wall time |
| `test_all_verdicts_carry_project_version` | all four verdict files (c1, c2, c3, c3b) carry project_version "1.1.0" |
| `test_c2_subcritical_rows` | subcritical branch: 13 rows, 0 flipped, every q_max in (0, 2) |
| `test_c2_compactness_approaches_threshold` | q_max strictly monotone as eps → 0 (approach to the horizon); still < 1 at the eps floor |
| `test_c2_slowdown_fit` | 13 fit points; slowdown slope_ln_eps < 0; r² > 0.5 |
| `test_c2_echo_rate_below_anchor` | echo rate pinned to 0.1908986733640667 (±1e-9) and below the 1/Δ anchor 1/3.44 ≈ 0.2907 |
| `test_c2_bifurcation_summary` | M_sat_N800 = 0.03518978551089466 and eps_half = 0.004859801757908699 pinned to 1e-12 |
| `test_c2_bifurcation_rows_keep_junk` | 13 rows; honest junk kept (sane=False present); the largest sane mass carries f̃ = 1.0 |
| `test_c2_constants_mirror_verdict` | `constants.py` Part C (the CAMPAIGN dict) mirrors the C2 verdict exactly: eps_half, M_sat, slope, echo rate |
| `test_c3b_floor_ladder_sinks` | the floor sinks: 0.0155 > 8.574765e-03 > 4.244867e-03 > 0, each floor pinned to 1e-12 (per-grid F-2 values) |
| `test_c3b_gamma_fit_floor_biased` | gamma_eff < γ_Ch at both depths; per-grid F-2 values pinned (0.0410 / 0.0605, r² 0.33/0.41 — floor-dominated) |
| `test_c3b_delta_honest_negative` | delta_eff and P_engine_deep are None; every delta-ladder run resolves < 3 peaks — C3's negative stands |
| `test_c3b_anchor_product_passes` | P_anchor = 1.28656 with verdict PASS |
| `test_c3b_constants_mirror_verdict` | CAMPAIGN gamma_eff entries (N=1600, N=3200) mirror the C3b verdict |
| `test_campaign_tables_exist_and_match` | derived CSVs: 13 + 13 + 12 rows; junk kept in the bifurcation CSV; N ∈ {1600, 3200} |
| `test_c3b_gamma_ladder_csv_sane_counts` | 7 rows at N=1600 + 5 at N=3200; the `sane` column is strictly True/False |

## How to run

Everything from the repository root:

```console
$ make test                              # = python3 -m pytest tests/ -q
............................................................             [100%]
```

`pyproject.toml` sets `addopts = "-q"`, so the extra `-q` in the Makefile makes
the run doubly quiet and suppresses the count line. Run without it to see the
tally:

```console
$ python3 -m pytest tests/
............................................................             [100%]
63 passed in 0.8s
```

Single file:

```console
$ python3 -m pytest tests/test_campaigns.py
.................                                                        [100%]
17 passed in 0.08s
```

Selection by keyword:

```console
$ python3 -m pytest tests/ -k echo       # the C2 echo-rate pin
.                                                                        [100%]
1 passed, 59 deselected in 0.54s
$ python3 -m pytest tests/ -k haar       # 5 Haar-check tests
5 passed, 55 deselected in 0.63s
$ python3 -m pytest tests/ -k cmb        # 2 CMB-contact tests
2 passed, 58 deselected in 0.63s
```

Verbose, with names (pytest 9 prints one progress line per file):

```console
$ python3 -m pytest tests/test_campaigns.py -v
tests/test_campaigns.py .................                                [100%]
============================== 17 passed in 0.10s ==============================
```

Skipping the engine march during development:

```console
$ python3 -m pytest tests/ --deselect tests/test_engine.py::test_roberts_regression_n200
59 passed, 1 deselected in 0.68s
```

The validation layer can also be run standalone:

```console
$ python3 -m chbridge.validate
check                      status  detail
-----------------------------------------------------------------------
b_Ch identity + 0.67% gap  PASS    {'b_Ch_ref': mpf('0.37651019814126646947499511599576018936772526910359737'), 'gap_pct': 0.666701}
PAGE_FRACTION              PASS    {'ref': 0.646447}
S~M^2, T~1/M, t~M^3        PASS    {}
CMB contact                PASS    {'M_CMB': 4.5015948405198975e+22}
Planck units               PASS    {}
Delta*gamma anchor         PASS    {'product': 1.28656, 'dev': 0.01656}
Kretschmann scale law      PASS    {}

7/7 checks PASS (mpmath dps=50, chbridge v1.1.0)
```

## Runtime budget

Measured on the reference workstation (Python 3.12.14, pytest 9.0.2):

| Item | Measured time |
|---|---|
| full suite (`python3 -m pytest tests/`) | 0.82 s (0.8–1.1 s across runs) |
| heaviest single test: `test_roberts_regression_n200` | 0.22 s (call phase) |
| second heaviest: `test_haar_mc_small_deviation` | 0.11 s |
| `test_campaigns.py`, all 17 tests | 0.08 s whole file |
| everything else | ≤ 0.05 s per test |

Per-file wall times (each run pays interpreter start and imports once, which
is why the parts sum to more than the whole): `test_constants.py` 0.07 s,
`test_hawking.py` 0.26 s, `test_page.py` 0.36 s, `test_bridge.py` 0.08 s,
`test_ladder.py` 0.24 s, `test_engine.py` 0.40 s, `test_campaigns.py` 0.08 s.

The engine regression's docstring budgets ~1 s for the N=200 march on slower
hardware; even there the whole suite stays well inside a one-minute envelope.
The campaign tests are cheap by construction: they parse committed JSON and
CSV files and compare numbers — no engine marches, no figure rendering, no
network. There are no sleeps, no retries — if the suite is slow, something is
wrong locally.

## How to add a test

Rules, in priority order:

1. **Pin a committed number.** A test exists because a value can regress.
   State the value and its source (constant, verdict, table) in the docstring.
2. **No network.** Ever. If a test needs the outside world, it does not belong here.
3. **Seeded RNG only.** Use `np.random.default_rng(seed)` with a fixed seed;
   committed artifacts use seed 20260101, in-test randomness may use any fixed seed.
4. **File IO only under `tmp_path`** — with one deliberate exception: the
   campaign tests read the committed verdict JSONs and `data/bridge/` CSVs
   read-only, because pinning the committed bytes is their whole job.
5. **Keep it fast.** Target well under 1 s per test; if a test must be slow,
   say so in its docstring, as the engine regression does.
6. **Name it `test_*.py` / `test_*`.** `conftest.py` already handles `sys.path`;
   do not add path hacks or site-specific fixtures.

Place value-pinning tests for constants in `test_constants.py`, closed-form
thermodynamics in `test_hawking.py`, verdict pins for campaigns C2/C3b in
`test_campaigns.py`, and so on — the file layout mirrors the package and
campaign layout.

## Honesty notes

- The suite pins numbers; it does not certify physical truth. A passing suite
  means the code reproduces its own committed claims.
- The campaign tests pin *committed machine outputs*, not physical truth: they
  read the verdict JSONs and the derived CSVs verbatim and never run the
  engine. A re-run that moves a pin is a bug or a CHANGELOG event — the tests
  must not be edited silently to match.
- The bridge tests recompute from the verdict JSON rather than reading the
  committed CSVs; the committed artifacts are covered by the byte-identity
  test and by the no-op `make data` check.
- Figures are not pixel-tested. Their correctness is pinned indirectly: the
  tables they read are tested, and regeneration is deterministic.
- The authoritative test count is whatever `pytest --collect-only` prints on
  your checkout (60 here: 10 + 9 + 7 + 8 + 7 + 2 + 17); prose documents never
  override that count.

## FAQ

**How many tests are there, exactly?**
Whatever `python3 -m pytest tests/ --co -q` prints on your checkout — here 60,
split 10 constants + 9 hawking + 7 page + 8 bridge + 7 ladder + 2 engine +
17 campaigns. Prose counts (including this README) are secondary to the
collector; if they disagree, trust pytest and fix the prose.

**Why is `test_engine.py` slow?**
It is the only test that runs the real double-null characteristic march, on a
200×200 grid, and compares against the exact Roberts–Oshiro solution. It is
the integration test of the engine; 0.22 s measured, ~1 s budgeted. Everything
else is closed-form or file parsing.

**Why assert on CSV bytes?**
Byte identity is the determinism contract between the verdicts and the data
tables. Float-formatting drift, locale effects or a reordered column would all
break it — exactly the regressions worth catching before a figure does. The
campaign-table pins extend the same idea: the CSVs must equal the verdict rows
cell-for-cell.

**Why do the bridge tests recompute instead of reading the CSVs?**
Two ends, two tests: the verdict→table mapping is pinned by recomputation,
the committed artifact is pinned by `test_rebuild_determinism` and by the
no-op guarantee of `make data`. The campaign tests cover the second end for
the C2/C3b tables directly.

**What is the difference between the tests and `python3 -m chbridge.validate`?**
The validator re-derives 7 headline identities at 50 decimal digits with
mpmath. `test_validate_all_pass` runs it inside pytest so the two layers can
never drift apart.

## See also

- [test_campaigns.py](../tests/test_campaigns.py) — the C2/C3b/C6 verdict pins
- [validate.py](../chbridge/validate.py) — the 50-digit validation layer
- [conftest.py](../tests/conftest.py) — the two-line bootstrap
- [data/README.md](../data/README.md) — what the byte tests protect
- [docs/validation.md](../docs/validation.md) — the validation narrative
- [CONTRIBUTING.md](../CONTRIBUTING.md) — how changes are accepted
- [Makefile](../Makefile) — `make test`, `make validate`, `make all`

### The C6 block (3 tests, v2.1.0)

`test_c6_ladder_facts` pins the measured ladder signature committed by
the drift campaign: every per-doubling drift positive (approach from
above), `p_eff` strictly climbing (1.140 / 1.459 / 1.596), decay faster
than 1/N, and the two deep-grid drift values pinned to 1e-9.
`test_c6_lemmas_machine_precision` pins the two exact lemmas of theorem
T10: worst-alignment chord flattening == κh²/8 (to 1e-7 relative), the
alignment-averaged deficit == κh²/24 and the chord-chain closed form
(both to 1e-12), plus the compression inequality `L_chord < L_arc` on
all five grids. `test_c6_honest_negatives_and_channel` pins the
negatives themselves: the two-term extrapolation verdict is REJECTED
(despite R² = 0.999), the exact channel is positive but sub-dominant
(share < 0.05 everywhere), and the calibration constants match the
Part-C mirrors (κ* and s) to 1e-9. Together the block guarantees that
the package cannot silently "fix" the drift or overstate the channel —
the two temptations the audit discipline exists to block.

## Краткое резюме (Russian)

Тестовый набор проекта — 63 теста в семи файлах, все проходят примерно за
0,8 секунды. Философия проста: тесты закрепляют числа, а не типы. Каждая
константа проверена дважды — точным тождеством и зафиксированным десятичным
значением; термодинамика — по справочным значениям (r_s Солнца 2954 м,
T_H ≈ 6,17e-8 K); таблицы — по вердиктам кампаний; движок — регрессией на
точном решении Робертса–Оширо при N=200. Новый файл test_campaigns.py (20
тестов) закрепляет машинные вердикты кампаний C2, C3b и C6: обе ветви порога,
лестницу массового пола по сеткам (0.0155 > 8.57e-3 > 4.24e-3), скорость эха 0.1909 на
e-фолд, якорное произведение 1.28656 PASS, факты дрейфа лестницы A* и машинную
точность лемм T10, честные негативы C6 и производные CSV-таблицы; кампании
при этом не запускаются — тесты читают только зафиксированные JSON и CSV.
Отдельные тесты гарантируют побайтную идентичность таблиц при пересборке и
запускают 50-значную mpmath-валидацию (7/7) внутри pytest. Правила новых
тестов: без сети, генератор только с фиксированным зерном, ввод-вывод через
tmp_path; авторитетное число тестов — то, что печатает `pytest --collect-only`.
