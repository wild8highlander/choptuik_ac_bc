# python

The canonical Python implementation of the verification and simulation suite
for the spinor-correction framework (b-C and a-C corrections on the Klein
quartic curve). It is the reference stack of the repository: every claim of
the monograph is checked here by `src/verification/`, swept and plotted by
`src/simulation/` and `src/visualization/`, and written out in seven report
formats by `src/reporting/`. CI runs this package on Python 3.10/3.11/3.12
across Ubuntu, macOS and Windows.

## What is inside

| Path | Contents |
|------|----------|
| `run.py` | CLI entry point and interactive menu launcher |
| `pyproject.toml` | Packaging and tool configuration (setuptools, pytest, ruff, mypy, coverage) |
| `setup.py` / `requirements.txt` | Legacy install shim and pinned runtime dependencies |
| `src/core/` | Typed implementations of the mathematics: `klein_curve.py`, `spinor_phases.py`, `dirac_operator.py`, `choptyuk_formula.py`, `surfaces.py`, `hypothesis.py`, `qnm.py`, `enhanced_verification.py` |
| `src/verification/` | `verify_all.py` (full verification suite) and `verify_enhanced.py` (extended claims: 4D, K3, Tyukovsky, Einstein GR QNM results) |
| `src/simulation/` | `simulator.py` — parameter sweeps (`sweep_delta_C`, `sweep_lambda_1`) and convergence analysis |
| `src/visualization/` | `plots.py` — 600 DPI PNG and vector PDF figure generation |
| `src/reporting/` | `report_writer.py` — DOCX, PDF, TXT, MD, CSV, HTML, JSON reports with execution logs appended |
| `src/ui/` | `interactive_menu.py` — terminal menu (falls back to non-interactive mode without a TTY) |
| `tests/` | pytest suite: `test_choptyuk.py`, `test_simulation_qnm.py`, `test_reports_verify.py` |
| `config/` | `default_config.json` — default verification parameters |
| `presets/` | Named presets: `standard.json`, `high_precision.json`, `ligo_analysis.json` |

## How to run

```bash
cd python
python3 -m pip install -r requirements.txt

# interactive menu (default)
python run.py

# non-interactive verification (what CI and the Docker image run)
python run.py --mode verify --non-interactive --output-dir output

# simulation sweeps + plots + reports
python run.py --mode simulate --non-interactive

# with a config file or a named preset
python run.py --config config/default_config.json --non-interactive
python run.py --preset standard --non-interactive
python run.py --preset ligo_analysis --non-interactive
```

CLI flags accepted by `run.py`: `--mode {verify,simulate,interactive}`,
`--non-interactive`, `--output-dir DIR`, `--config FILE`,
`--preset {standard,high_precision,ligo_analysis}`,
`--log-level {DEBUG,INFO,WARNING,ERROR}`.

Tests and quality gates:

```bash
python -m pytest                      # full suite (testpaths = tests)
python -m pytest -m "not slow"        # skip slow verification tests
python -m ruff check src tests        # lint
python -m mypy src                    # static typing
```

## Verification content

- Klein curve invariants: genus 3, automorphism group PSL(2,7) of order 168,
  scalar curvature R = −2, Hurwitz identity checks.
- Spinor phases δ_A = π/2, δ_B = π/3, δ_C = π/7 and the enumeration of all
  64 spinor structures built from them.
- Dirac eigenvalue via the Lichnerowicz formula: λ₁(D²_σ₀) = λ₁(Δ) + R/4
  with the Bourque–Strohmaier Laplacian value λ₁ = 3.838.
- The unified formula (b-C Berry-phase correction and a-C braking term) and
  its deviations from the observed value, evaluated to the configured
  tolerance (default 0.0001 in the Java stack, configurable here via presets).
- LIGO/Virgo quasi-normal-mode predictions: the preset `ligo_analysis.json`
  reproduces the event-by-event comparison tables and plots.

## Notes

- Core dependencies are `numpy`, `scipy`, `matplotlib`, `mpmath`; the report
  writers additionally use `python-docx`, `reportlab`, `markdown`, `jinja2`.
  Extra groups in `pyproject.toml`: `reports`, `all`, `dev` (pytest, ruff,
  mypy).
- Without a TTY (piped/CI invocation) the interactive menu automatically
  switches to non-interactive verify mode instead of blocking.
- All artifacts are written under the chosen output directory:
  `output/plots/`, `output/reports/`, `output/logs/execution.log`.
- `pyproject.toml` enforces coverage ≥ 80% (`fail_under = 80`) and marks the
  interactive menu and plotting layers as excluded from unit coverage because
  they are exercised by integration runs.
- The Julia mirror of this stack lives in `../julia/`; cross-implementation
  agreement of the reference values (e.g. Δ_bC = 3.438710,
  Δ_Ch base = 3.437883, Δ_Ch full = 3.447040, b_Ch = 0.376510) is part of the
  verification design.
