# monolith/lean — Lean 4 formalization (v2.3.0)

| File | Content | Status |
|------|---------|--------|
| `QHB_Theorems.lean` | T1–T20 scaffold, 500 lines, **10 closed kernels** | compiles (Mathlib) |
| `QHB_T19_Mathlib.lean` | full T19 port: block charpolys via `Matrix.charpoly`, **8 closed kernels** | compiles (Mathlib) |
| `QHB_AxiomAudit.lean` | `#print axioms` for all **18 closed kernels** | CI fails on `sorryAx` |
| `lakefile.toml` | Mathlib dependency (rev pinned by CI at build time) | — |
| `lean-toolchain` | auto-synced with Mathlib in CI | — |

## Build

```bash
lake update && lake exe cache get! && lake build
lake env lean QHB_AxiomAudit.lean   # must print no sorryAx
```

The GitHub Actions workflow `.github/workflows/lean.yml` performs the same
build on every push/PR (toolchain synced with Mathlib, cache fetched).

Honesty pattern: `sorry`-marked statements are exact statements anchored to
machine JSON layers; closed kernels are `sorry`-free and audited.
v2.3.0 erratum: T20.stall sign fixed (tau_max strictly decreases in T).
