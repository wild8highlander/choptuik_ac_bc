# docs/REPRODUCE.md — the reproduction index

Every claim → the exact command → the committed artifact. The golden rule of
the parent programme applies: *machine-readable or it did not happen.*

## 0. Environment

| Component | Version | Note |
|---|---|---|
| Lean + elan | `leanprover/lean4:v4.21.0` | `lean/lean-toolchain` |
| mathlib | pinned `v4.21.0` | `lean/lakefile.toml` |
| Python | ≥ 3.10 | `numpy`, `matplotlib`, `sympy`, `mpmath`, `pillow` |

## 1. The Lean side

```bash
cd lean
lake exe cache get!                   # prebuilt mathlib artifacts for v4.21.0
lake build                            # checks every proof of both libraries
```

Expected: `Build completed successfully.` — exit 0, only linter notes.
The committed evidence: `logs/full_build5.log` (2 884 steps),
`logs/merged_build.log` (2 885), `logs/final_check.log` (2 894).

```bash
lake env lean AxiomAudit.lean         # the 33 Choptuik headline axioms
lake env lean Satellite/AxiomAudit.lean  # the 62 Satellite headline axioms
```

Expected: every line ends with
`depends on axioms: [propext, Classical.choice, Quot.sound]` (or `[propext]`
for the pure counting theorems) — never `sorryAx`.
Committed evidence: `logs/choptuik_audit.log` (`AUDIT_EXIT=0`),
`logs/sat_final.log`.

## 2. The Python side

Run from the package root. Every script is idempotent and byte-stable — run
twice, diff, expect no differences.

| Command | Recomputes | Writes |
|---|---|---|
| `python scripts/compute_all.py` | every constant record, the spectrum slots, the NK data, the inventory scan | `data/constants.json`, `data/records.csv`, `data/spectrum_certificate.csv`, `data/bridge_certificates.csv`, `data/echo_model_derived.csv`, `data/septinial_corrections.csv`, `data/berry_model.csv`, `data/theorem_inventory.csv`, `data/build_manifest.json` |
| `python scripts/certify.py emit` | the rational bridge certificates | `data/certificates.json` |
| `python scripts/certify.py check` | the emitted fractions **against the committed `Generated.lean`** | console: `bridge certificate channel: LIVE` |
| `python scripts/b1_berry_model.py` | the exact SymPy series, 50-digit bounds on 40 points | `data/berry_series.csv` |
| `python scripts/check_dial_22.py` | capacity / chirality / cascade brute force | `data/dial22_results.json` |
| `python scripts/klein_psl27.py` | the exhaustive PSL(2,7) + {7,3} enumeration (~6 s) | `data/klein_psl27_results.json` |
| `python scripts/generate_figures.py` | all 32 figures (dark·EN + dark·RU + light·EN + light·RU) | `figures/`, `figures/dark_ru/`, `figures/monograph_en/`, `figures/monograph_ru/` |
| `python scripts/generate_figures.py --theme dark --lang en` | one rendition only | `figures/*.png` |
| `python scripts/generate_animations.py` | all 10 GIFs (EN + RU), ~50 s | `animations/en/`, `animations/ru/` |
| `python scripts/generate_banners.py` | the SVG identity, EN + RU renditions | `assets/banners/`, `assets/logo/` |
| `python scripts/generate_docs.py` | the theorem atlas from the sources | `docs/THEOREMS.md` |
| `python3 scripts/septinal_verify.py --ci --preset quick --task all` | large-matrix re-derivation of every headline constant (7 tasks, two-pass, menu/CLI/CI) | `results/run_*/` |
| `python3 scripts/septinal_verify.py --self-test` | harness unit/props/contract layers | `results/selftest_*/SELFTEST.md` |
| `python3 scripts/septinal_verify.py --ladder all` | convergence ladder on tasks 2/3/6/7: observed order p vs the theoretical band | `results/ladder_*/` |
| `python3 scripts/septinal_verify.jl --ladder all` | the same ladder in the Julia twin | `results/ladder_*/` |
| `python3 scripts/septinal_verify.py --task 7 --top-only` | streaming extreme (power + Rayleigh only, no Krylov V) | `results/run_*/` |
| `python scripts/verify.py` | the pre-push gate: links, counts, artifacts | console: `VERIFY: ALL GREEN` |

> [!TIP]
> The harness twins accept `--size N` as a single master handle: any solver
> knob left at ≤ 0 (`m_lift`, `blocks`, `krylov`, `n_echo`, `lsq_n`, `m_big`)
> is derived from it. `--expr "k=v, …"` sets arbitrary fields, `--reorth
> none` trades the rigorous Ritz bound for O(1) Krylov memory (declared 3%
> window, logged loudly), `--ram-budget 8G` raises the V guard, and
> `--load-script FILE` registers custom tasks at runtime (both languages).

## 3. Claim → artifact index

| Claim (README) | Verified by | Artifact |
|---|---|---|
| \|γ − 0.374\| = 263/2674500 < 10⁻³ | Lean `Scaling.gamma_close_to_published` + re-assertion in `compute_all.py` | `data/records.csv` |
| \|Δ − 3.4453\| < 5·10⁻⁴ | Lean `echoingPeriod_gundlach1997` + `compute_all.py` | `data/records.csv` |
| wiggle period ∈ [4.60, 4.62] | Lean `wiggle_published_check` + `compute_all.py` | `data/echo_model_derived.csv` |
| λ₀ ∈ [2.6744999, 2.674500101] | `Generated.lean` (norm_num) vs `certify.py check` | `data/certificates.json` |
| ∃! root in [12/10, 14/10] | Lean `truncated_dss_solution_exists_unique` | `data/bridge_certificates.csv` |
| 24 − 2 = 22, 11 + 11, cascade survivors | Lean `Dial`/`Chiral`/`Cascade` + `check_dial_22.py` | `data/dial22_results.json` |
| 704 · 5 346 · 369 754 | Lean `denom_A/B/C` + `compute_all.py` | `data/septinial_corrections.csv` |
| 168 = 1+21+56+42+48; 179 subgroups; 14 S₄; 24/84/56; χ = −4; 8 triangles; 24 pairs, stab 7 | Lean `C5_Klein` + `klein_psl27.py` | `data/klein_psl27_results.json` |
| 0 < R(δ) ≤ δ⁴/4 | Lean `Berry.remainder_pos/le` + `b1_berry_model.py` | `data/berry_series.csv` |
| 0 sorry / 0 project axioms | the two audit files + the committed logs | `docs/AUDIT.md` |
| γ₃ = 0.373892…, β_C = π²/98, α_C = π⁵/369754 | Lean `Unlock.gamma_exact/quanta` + `compute_all.py` | `data/constants.json` |

## 4. Determinism checklist

1. `sha256sum data/*` before and after a full re-run — identical;
2. the only seeded random draw (`np.random.default_rng(1993)` — the scatter
   jitter of the scaling figure) is fixed by seed;
3. GIF/PNG renders are functions of the committed CSVs and the Lean-locked
   constants — no screenshot folklore anywhere.
