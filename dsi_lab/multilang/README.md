# multilang/ — the DSI core in six languages

Version 1.0.0 · standalone · drop-in folder · no build system required

---

## What this directory is

`multilang/` carries the exact core of the DSI laboratory — the {7,3}
census arithmetic and the theorem-A/B/C block of the Kunz defect —
rewritten in several programming languages so the package can be
*touched* by readers of any background. Every program in here is a
**self-test**, not a library: it recomputes the same ten numbers, prints
them, self-checks, and exits. Nothing is downloaded, nothing is fitted,
nothing is hidden.

The validation block each twin prints covers:

| # | quantity | formula | reference value |
|---|----------|---------|-----------------|
| 1 | septinial constant | `b_Ch = 1 - cos(2*pi/7)` | 0.3765101981412664 |
| 2 | convergent identities | `9*24+8 = 224`, `8*1+1 = 9` | 1/24, 1/25, 9/224 |
| 3 | DSI-4 observation | `c_K3 = 9/224` | 0.0401785714285714 |
| 4 | {7,3} census | `7F = 3V = 2E = 168`, `V-E+F = -4` | V=56 E=84 F=24 |
| 5 | theorem C | `F(perm pair, n=7) = 2n` | 14 |
| 6 | theorem A | `F(complementary, n=8) = n` | 8 |
| 7 | theorem B | trimmed tree k=2: `F = n+2` | n=7, F=9 |
| 8 | weighted tree | `(n-1)*2*(c^2-1)^2 + n + 2`, c^2=4/7, k=3 | 549/49 = 11.20408… |
| 9 | the e-ladder | `5/7` and `1 + 2/7` | 0.7142857… / 1.2857142… |
| 10 | scaled-permutation minimum | `7t^2-8t+3` at `t = 4/7` | 5/7 exactly |

Every quantity is exact integer arithmetic or fixed-order IEEE-754
double arithmetic, so **every compiled twin prints byte-identical
output** — the committed `reference_output.txt` files prove it.

## Language matrix

| folder | language | verified at packaging | entry point | toolchain |
|--------|----------|----------------------|-------------|-----------|
| [`c/`](c/) | C | **yes** — gcc, output committed | `dsi_core.c` | any C99 |
| [`cpp/`](cpp/) | C++ | **yes** — g++, output identical to C | `dsi_core.cpp` | any C++11 |
| [`javascript/`](javascript/) | JavaScript | **yes** — node, output identical | `dsi_core.mjs` | Node 14+ |
| [`rust/`](rust/) | Rust | source (compile locally) | `dsi_core.rs` | rustc 1.60+ |
| [`go/`](go/) | Go | source (compile locally) | `dsi_core.go` | Go 1.19+ |
| [`julia/`](julia/) | Julia | source (run locally) | `dsi_core.jl` | Julia 1.8+ |

Byte-identical output was verified for C (gcc), C++ (g++) and JavaScript
(node) at packaging time; the Rust, Go and Julia sources mirror the same
ten checks and the same print format, and are committed without a
reference output because the packaging environment does not carry their
toolchains — the same convention as the parent `Collapse Hawking Bridge`
multilang/ folder.

## Reproduce the verification

```bash
cd dsi_lab/multilang
gcc  -O2 -ffp-contract=off -o /tmp/dsi_core c/dsi_core.c -lm     && /tmp/dsi_core
g++  -O2 -ffp-contract=off -o /tmp/dsi_core cpp/dsi_core.cpp     && /tmp/dsi_core
node javascript/dsi_core.mjs
diff <(/tmp/dsi_core) c/reference_output.txt     # byte-identical
```

Each twin exits 0 on 10/10 PASS and 1 otherwise, so the folder is
CI-friendly.
