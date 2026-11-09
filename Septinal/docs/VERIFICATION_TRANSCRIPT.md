# VERIFICATION TRANSCRIPT — septinal_verify harnesses (§22 Definition of Done)

Date: 2026-11-04. Ground truth: Septinal archive `data/constants.json`,
`data/records.csv`, `data/dial22_results.json`, `data/klein_psl27_results.json`.
Seed 1993, splitmix64 — identical stream in both language builds, so synthetic
data and golden scalars coincide across Python and Julia.

## Python build — `scripts/septinal_verify.py` (Python 3.12, stdlib only)

1. Menu (`python3 septinal_verify.py`, pty):
   ```
   ==============================================================================
   SEPTINAL VERIFICATION HARNESS
   ==============================================================================
   [Core]      s self-test   b bench   c config   g language (en)
   [Suite]     1 gamma-scaling  2 dial-spectrum  3 echo-spacing  4 berry-quantum
               5 psl27-lattice  6 cyclotomic-records  7 lanczos-guard
   [Actions]   a all   f quick check   h audit   p presets   r reload
   [Labs]      l labs   d3 3d-lab   ? keys   q quit
   ```
   `g` switches to «СЕПТИНАЛЬНЫЙ ВЕРИФИКАЦИОННЫЙ СТЕНД» (RU UI verified via pty).

2. `--ci --preset quick --task all` → exit 0:
   ```
   DONE: 7/7 tasks PASS -> results/run_20261104_192742
   task=01 gamma-scaling        PASS  (two-pass, 12.3 s)
   task=02 dial-spectrum        PASS  (13.9 s)
   task=03 echo-spacing         PASS  (11.8 s)
   task=04 berry-quantum        PASS  (12.0 s)
   task=05 psl27-lattice        PASS  (16.7 s)
   task=06 cyclotomic-records   PASS  (11.8 s)
   task=07 lanczos-guard        PASS  (19.2 s)
   ```
   Key verified numbers (task metrics, quick preset):
   - t1 slope = 0.373922944879, |slope − 0.373901663862| = 2.1e-05 < 1e-3 (bound);
     free-period fit P = 4.612296060 vs λ0·Δ/2 = 4.607431224575;
     rational identity 2000/5349, |γ − 0.374| = 263/2674500 exact.
   - t2 core spectrum error 3.7e-12 vs 2cos(πk/12)×2, zero multiplicity 2 (the
     antipodal gap {0,12}); lifted Ritz within its Krylov tolerance.
   - t3 L_est error 1.0e-04 (O(h²)), Richardson pass-2 error < 1e-7·L.
   - t4 two-level normal form exact (≤1e-9), remainder 0 ≤ R ≤ δ⁴/4 elementwise;
     Weyl bound |Δλ| ≤ 2c honoured on the coupled chain.
   - t5 total 179 = 1+21+28+35+28+8+21+14+8+14+1, s4_count 14, circulant
     spectrum vs closed form 7.8e-11.
   - t6 cos(2π/7) via deflated Lanczos → γ3 = 0.373892204263 (err < 1e-8);
     rational records 263/2674500 and 76201/500000000 re-derived exactly.
   - t7 RAM guard: n = 11·m², V-memory ≤ 384 MiB, loud downgrade wired.

3. Artifacts per run dir (verified listing):
   ```
   results/run_*/index.html  results.json  MANIFEST.toml  FINAL_REPORT/
   FINAL_REPORT/final_report.{md,html,pdf,docx}  full_run_log.txt
   FINAL_REPORT/computation_log_full.txt  results_verdicts.txt
   FINAL_REPORT/config_snapshot.txt  FINAL_REPORT/RTM.md
   task_*/report.{md,html,pdf,docx}  task_*/plots/*.png *.svg animation.gif
   logs/computation_log.txt  logs/stdout_capture.txt  logs/events.jsonl
   logs/monitor.csv
   ```

4. `--self-test --props --contract` → `SELFTEST: PASS (17/17)`, exit 0;
   SELFTEST.md + logs/selftest.jsonl written.  Covers: eigen pipeline vs
   QΛQᵗ, exact rational records, closed forms, font markup, PNG/GIF
   structure, SVG escaping, integration task1, golden scalars, determinism,
   no-NaN, dims, bounded memory, contract sanity (ERR_UNKNOWN_TASK raised,
   completions generated).

5. `--print-config` (fragment):
   ```
   # effective config (precedence: default < file < env < cli < menu)
   source               = 'septinal-archive'       [default]
   size                 = 48                       [default]
   seed                 = 1993                     [default]
   ```

6. `--generate-completions bash | head -5`:
   ```
   # bash completion for septinal_verify.py (generated, no external utils)
   _sept_complete() {
     local cur="${COMP_WORDS[COMP_CWORD]}"
     case "${cur}" in
   ```

7. `--task-timeout 0.001 --task 1` → `FAIL REASON=TIMEOUT`, exit 1 (verified).
   `NO_COLOR=1 --lang ru --junit j.xml` → RU report + JUnit XML (verified).
   `/dev/null | python3 septinal_verify.py` → EOF-guard path, exits ≤ 50 empty
   reads with a default cheap run, exit 0 (verified).

## Julia build — `scripts/septinal_verify.jl` (Julia 1.10.4, stdlib only)

All contract surfaces verified in this environment:

1. Library mode: `julia -e 'include("septinal_verify.jl"); println("ok")'` —
   the `abspath(PROGRAM_FILE) == @__FILE__()` guard keeps the include silent
   (no exit, no side effects; `ok` prints).
2. `--help` / `--list-tasks` — registry and flag tables render.
3. `--ci --preset quick --task all` → exit 0:
   ```
   DONE: 7/7 tasks PASS -> results/run_20261104_202206
   PASS: 7 / 7
   ```
   Metrics are digit-identical to the Python build (shared splitmix64, seed
   1993): t1 slope 0.373922944879, |diff| 2.128e-05, free-period fit
   4.612296060; t2 core-spectrum error 3.711e-12 with zero multiplicity 2;
   t6 gamma3 0.373892204263 (err 7.7e-14).  results.json parses with a strict
   JSON reader; MANIFEST.toml carries the script sha256, per-task seeds and
   hashed artifacts.
4. Artifacts per run dir: `index.html`, `results.json`, `MANIFEST.toml`,
   `FINAL_REPORT/{final_report.md,html,pdf,docx,RTM.md,full_run_log.txt,
   computation_log_full.txt,results_verdicts.txt,config_snapshot.txt}`,
   per-task copies with `plots/*.png *.svg animation.gif`, and the five log
   streams under `logs/`.
5. `--self-test --props --contract` → `SELFTEST: PASS (15/15)`, exit 0 —
   includes the in-place LAPACK cross-check (`syev!`/`stev!`, the §23.7-8
   real-symmetric equivalents of hetrd!/dstev!) against the pure Sturm
   bisection, PNG/GIF structural checks and exact rational records.

Bugs found and fixed while bringing the Julia port to green (each verified by
an isolated repro kept under `scripts/parts/`): supersampled-canvas
`downsample` linear index (1-based row/col shift), `alphas`/`betas` slice
bounds in the Lanczos convergence check, `json_kv` key quoting + double
encoding of nested metrics, module-scope imports (`Printf`, `Zlib_jll`,
`Base64`), `@eval`-guarded module re-inclusion, `sytrd!`→`syev!` wrapper,
FINAL_REPORT per-task copy layout, and the greedy-macro parse of the §16
entry guard (`@__FILE__()`).

SKIPPED: none — all §22 demo items executed for both language builds.

## Addendum — the extended harness surfaces (verified in this environment)

Both twins gained a convergence ladder and a large-matrix mode set; the runs
below are committed verbatim outputs of this environment (quick preset unless
stated):

- `--ladder 3 --ladder-sizes 64,128,256,512` →
  `RESULT task=03 slug=ladder/3 verdict=PASS … observed_rate=1.99 expected_rate=2.00`
  (identical digits in Python and Julia — the ladder reuses the shared
  splitmix64 stream).
- `--task 2,5 --reorth none` → PASS in both builds. In this mode no Krylov V is
  stored (O(1) memory) and no rigorous Ritz bound exists, so the verdict uses a
  **declared 3% relative window**, logged loudly (`reorth=none: no rigorous
  Ritz bound - declared 3% window in force`). The full-reorth mode keeps the
  rigorous bounds and is the default.
- `--task 7 --top-only` → PASS in both builds: streaming power + Rayleigh only.
  The big-dial spectrum is symmetric (±λmax), so the probe runs on the
  spectrally shifted operator (shift 1.1·|λth| + 1); the observed Rayleigh
  quotient is 5.7661…/5.7692… against the theory constant.
- `--expr "size=16, krylov=24" --task 1 --no-two-pass --repeat 2` → PASS with
  `repeat_median_s` recorded.
- `--load-script my_task.py` / `my_task.jl` → a custom task registered as
  `my-experiment`/`my-task` (id 99) and executed: `verdict=PASS`.
  The Julia dispatch uses `Base.invokelatest`, so runtime-defined methods
  (world age) call cleanly.
- `--profile` writes `logs/profile.out` (cProfile stats / flat Julia profile).
- `--watch PATH` re-runs the suite on file changes; `--no-effects` (and
  `--ci`/`--plain`/non-TTY) disable the SEPTFX console effects (ASCII ocean,
  spinners, gradient banner, matrix rain, sparklines, wave progress bar).
