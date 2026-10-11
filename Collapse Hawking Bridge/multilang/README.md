# multilang/ — the bridge in seven languages

Version 2.0.0 · standalone · drop-in folder · no build system required

---

## What this directory is

`multilang/` carries the closed-form core of the Collapse–Hawking
Bridge, rewritten in several programming languages so that the package
can be *touched* by readers of any background. Every program in here is
a **self-test**, not a library: it recomputes the same small block of
numbers from the CODATA constants, prints them, and exits. Nothing is
downloaded, nothing is fitted, nothing is hidden.

The validation block each twin prints covers:

| # | quantity | formula | reference value |
|---|----------|---------|-----------------|
| 1 | septinial phase | `delta_C = pi/7` | 0.448798950513 |
| 2 | septinial constant | `b_Ch = 1 - cos(2*pi/7)` | 0.37651019814126640 |
| 3 | Page fraction | `1 - 2^(-3/2)` | 0.6464466094067262 |
| 4 | anchor product (arithmetic) | `Delta*gamma = 3.44 * 0.374` | 1.28656 (target 1.27 ± 0.05; ANCHOR_ARITHMETIC, not a measurement) |
| 5 | CMB contact mass | `hbar*c^3/(8*pi*G*kB*T_CMB)` | 4.501595e+22 kg |
| 6 | Hawking temperature | `T_H(1e12 kg)` | 1.226901e+11 K |
| 7 | BH entropy | `S_BH(1e12)/kB` | 2.652887e+40 |
| 8 | lifetime | `t_evap(1e12)` | 8.411478e+19 s ≈ 2665 Gyr |
| 9 | peak power | `P_H(1e12)` | 3.561622e+8 W |
| 10 | Page curve samples | `S_rad/S0` at τ = 0.5, τ*, 0.8 | 0.62996… / **0.5 exactly** / 0.65800… |
| 11 | critical amplitude | `A*(N=800)` vs remediation ladder N=1600 | 0.08053436, honest drift 2.79e-3 (F-1; the stale 1.06e-6 claim is retracted) |
| 12 | floor law | `floor_M(N)` vs `12/N` | 0.0155 / 8.575e-3 / 4.245e-3 (per-grid F-2 values) |

Item 10 hides a small exact theorem: at the Page time itself,
`S_rad/S0 = (1 - tau*)^{2/3} = (2^{-3/2})^{2/3} = 2^{-1} = 0.5`
— the entropy crossover happens exactly at one half. Every twin
reproduces it to machine precision.

## Language matrix

| folder | language | status at packaging | entry point | toolchain |
|--------|----------|---------------------|-------------|-----------|
| `../chbridge/` | **Python 3** | **reference implementation** (full package) | `python3 -m chbridge.validate` | numpy, mpmath |
| `javascript/` | JavaScript (ES2022) | **verified**: executed, cross-checked | `node bridge.mjs` | node ≥ 16 |
| `cpp/` | C++17 | **verified**: executed, cross-checked | `g++ -O2 -std=c++17 -o bridge bridge.cpp && ./bridge` | g++ / clang++ |
| `c/` | C99 | **verified**: executed, cross-checked | `gcc -O2 -std=c99 -o bridge bridge.c -lm && ./bridge` | gcc / clang |
| `julia/` | Julia | portable source (see honesty note) | `julia bridge.jl` | Julia ≥ 1.6 |
| `rust/` | Rust | portable source (see honesty note) | `rustc -O bridge.rs && ./bridge` | rustc ≥ 1.60 |
| `go/` | Go | portable source (see honesty note) | `go run bridge.go` | Go ≥ 1.19 |

The three **verified** twins were executed on the packaging machine and
mutually cross-checked line by line: the worst relative disagreement
across all 28 numeric fields is **7.1e-13** — consistent with printf
rounding alone. Their captured outputs live next to the sources as
`reference_output.txt`.

## Honesty note on the portable sources

`julia/`, `rust/` and `go/` are written against exactly the same closed
forms and mirror the verified twins line by line, but **no Julia, Rust
or Go toolchain existed on the packaging machine**, so these three were
*not executed here*. Their READMEs say so explicitly. If you run one of
them, diff its output against `javascript/reference_output.txt` (the
JS twin is the closest dialect to all three) and, if you wish, promote
it to "verified" in its README with a one-line commit note. This is the
same honesty discipline the rest of the package applies to campaigns:
status is claimed only for what was actually run.

## Why the block is small on purpose

The bridge has two halves. The **engine half** (critical collapse,
`engine/solver.py`, campaigns C1–C3b) is a research instrument: it
needs Python, numpy and ~200 s of wall time, and it is covered by the
60-test pytest suite in `../tests/`. The **thermodynamic half**
(Hawking, Page, evaporation, contact with the CMB) is a set of exact
closed forms of three elementary functions — `T_H(M)`, `S_BH(M)`,
`t_evap(M)` — plus the two exact constants `PAGE_FRACTION` and `b_Ch`.
That half *should* be reproducible in any language in under a minute,
and `multilang/` proves it. The split is deliberate:

* if a twin disagrees with Python, the bug is in the twin (closed
  forms are closed forms);
* if a twin agrees, the reader has a portable seed for their own
  notebooks, apps or CI — without installing the engine.

## What is NOT in this directory

* No solver. The double-null engine lives in `../engine/` and is
  Python-only by design (see `../engine/README.md` for the reasons).
* No campaign runners. `../campaigns/` owns the measurement protocols.
* No plotting. `../scripts/` and `../figures_hires/` own visuals.
* No build files, manifests or lock files. Each program is a single
  self-contained source file on purpose — a bridge seed, not a project.

## Reproduction in 60 seconds

```bash
cd multilang
node javascript/bridge.mjs                    # 1) JS twin
g++ -O2 -std=c++17 -o /tmp/b1 cpp/bridge.cpp  # 2) C++ twin
/tmp/b1
gcc -O2 -std=c99 -o /tmp/b2 c/bridge.c -lm    # 3) C twin
/tmp/b2
python3 - <<'PY'                              # 4) Python reference check
from chbridge.hawking import T_H, S_BH, k_B, t_evap
print(f"{T_H(1e12):.6e}", f"{S_BH(1e12)/k_B:.6e}", f"{t_evap(1e12):.6e}")
PY
diff <(grep -o '[-0-9.e+]*' javascript/reference_output.txt) \
     <(grep -o '[-0-9.e+]*' cpp/reference_output.txt)   # 5) optional: byte diff
```

(Step 4 assumes the package root is on `PYTHONPATH`; step 5 will show
only formatting noise, never physics.)

## Cross-language agreement protocol

1. Each verified twin prints 28 numeric fields in a fixed order.
2. Fields are compared pairwise by relative difference.
3. Acceptance: max relative deviation ≤ 1e-11 (printf rounding budget).
4. Measured on the packaging machine: **7.08e-13**. Verdict: PASS.
5. The protocol is re-runnable in one line per twin — see above.

## FAQ

**Q: Why no Java?** The packaging machine had a JRE without `javac`;
shipping an unverifiable .java file alongside verified twins would
break the honesty line drawn above. A Java twin is a 20-minute port of
`c/bridge.c` — PRs are welcome under the same protocol.

**Q: Why does every twin print the same sentences?** So that outputs
are diffable across languages, not only across runs.

**Q: Where are the *hard* numbers (A\*, f~, floors)?** They are
*campaign verdicts*, not closed forms: they come from the engine runs
committed under `../campaigns/reference/`. The twins mirror them as
constants and print them for context — recomputing them would require
the engine, which is exactly the half that *must not* be duplicated
lightly.

**Q: Can I use these files in a course?** Yes — they were written to be
read top to bottom in one sitting. The C file is the shortest; the JS
file is the easiest to run (node is everywhere); the C++ file shows
the same physics with RAII-free, header-free minimalism.

**Q: Numeric types?** All twins use IEEE-754 binary64 ("double").
No extended precision is needed for this block; the mpmath dps=50
checks live in Python (`python3 -m chbridge.validate`, 7/7 PASS).

## See also

* `../chbridge/README.md` — the reference Python implementation.
* `../docs/theory.md` — why these closed forms and no others.
* `../results/RESULTS.md` — the campaign ledger behind items 11–12.
* `../figures_hires/README.md` — 600 dpi visual catalog of the same numbers.
* `../animations/README.md` — the four launch animations.

## Краткое резюме (RU)

Каталог `multilang/` содержит ядро моста в семи языках: Python
(эталон, весь пакет) и шесть автономных самотестов — JavaScript, C++,
C (все три исполнены и взаимно сверены, максимум расхождений 7.1e-13),
а также Julia, Rust, Go (портативные исходники, честно помечены как
не исполненные на машине упаковки). Каждый самотест пересчитывает
12 контрольных величин — от б_Ч = 1−cos(2π/7) до закона пола
M_floor ≈ (13 ± 1)/N — и печатает одинаковый блок, пригодный для diff.
Ни один файл не требует сборочной системы: один файл — одна программа.
