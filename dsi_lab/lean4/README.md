# lean4/ — the Lean 4 formalization of the DSI theorem layer

Version 1.0.0 · Lean 4 + Mathlib · builds in CI (workflow `lean.yml`)

---

## What this is

A machine-checked formalization of the theorem layer of the seven
experiments, following the same conventions as the QHB package
(`QHB/monolith/lean/`). The layer is split in two honest strata:

**The exact stratum (proved here, `sorry`-free, no data axioms).**

| theorem | content |
|---------|---------|
| `census_valence_identity` | 7F = 3V = 2E = \|PSL(2,7)\| = 168 (the {7,3} census) |
| `census_euler` | V − E + F = 2 − 2·3 = −4 (genus 3) |
| `cf_9_224_divisions` | 224 = 24·9 + 8, 9 = 8·1 + 1 (CF division steps) |
| `cf_9_224_step`, `cf_8_9_step`, `cK3_eq_cf` | 9/224 = [0; 24, 1, 8] exactly |
| `eFree_lt_one` | 5/7 < 1 (the free-scalar floor) |
| `tree_e_le_two`, `tree_e_ge_one` | 1 ≤ 1 + 2/n ≤ 2 for n ≥ 2 (theorem B arithmetic) |
| `ladder_free_lt_tree` | the ladder ordering 5/7 < 1 + 2/n |
| `scaled_permutation_minimum` | 7·(4/7)² − 8·(4/7) + 3 = 5/7 (the trace-theorem equality case) |
| `weighted_tree_549_49` | F(k=3, c²=4/7) = (n−1)·2·(c²−1)² + n + 2 = 549/49 exactly |

**The axiom-anchored stratum (exact statements, numerically verified by
experiment 7).** Theorem A (threshold e ≥ 1 for partial isometries),
theorem B (coverage arithmetic F = n + 2·rank(I−P−Q)) and theorem C
(unitary pairs F = 2n) are declared as `axiom`s whose content is
machine-verified by `results/exp7_e1_threshold.json` (24 000 random
pairs, zero threshold violations, identity error 5.9e-16). The corollary
D (class closure: 5/7 is unreachable inside the partial-isometry class)
is **derived** from theorem A — a real proof, no `sorry`.

## Files

| file | contents |
|------|----------|
| `DSILab.lean` | the whole formalization (single module, Mathlib import) |
| `DSILab_AxiomAudit.lean` | `#print axioms` audit of every theorem |
| `lakefile.toml`, `lean-toolchain` | Mathlib build pin (toolchain v4.21.0, same as QHB) |

## Build

```bash
cd dsi_lab/lean4
lake update && lake exe cache get! && lake build
lake env lean DSILab_AxiomAudit.lean    # the axiom audit
```

The exact stratum uses only the standard logical axioms
(`propext`, `Classical.choice`, `Quot.sound`); the axiom-anchored
stratum additionally lists `DSILab.leavittF`, `DSILab.MatrixPosSub`,
`DSILab.rankM`, `DSILab.theorem_A_threshold`, `DSILab.theorem_B_coverage`,
`DSILab.theorem_C_unitary` — each documented with the numerical
experiment that anchors it.
