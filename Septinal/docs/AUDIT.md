<p align="center">
  <img src="../assets/banners/banner_theorems.svg" alt="audit" width="100%">
</p>

# docs/AUDIT.md — the verification dossier

![sorry](https://img.shields.io/badge/sorry-0-8FB7A4.svg)
![axioms](https://img.shields.io/badge/project_axioms-0-8FB7A4.svg)
![audit](https://img.shields.io/badge/headline_declarations-95-brightgreen.svg)
![exit](https://img.shields.io/badge/AUDIT_EXIT-0-success.svg)

> [!IMPORTANT]
> Every line of this dossier is traceable: the log file, the step count and
> the exit code are all committed. Re-run the two `lake env lean` audits and
> `diff` the output against `logs/` — the audit is the proof.

This dossier records, from the **committed build logs**, what the Lean kernel
actually checked. Nothing here is a promise: every line quoted below exists in
`logs/`.

## 1. The builds

| Log | Scope | Steps | Outcome |
|---|---|---|---|
| `logs/cache.log` | mathlib `v4.21.0` fetch, prebuilt artifacts replayed | — | dependencies pinned and cached |
| `logs/full_build5.log` | full `Choptuik` library rebuild | 2 884 | `Build completed successfully.` |
| `logs/merged_build.log` | merged rebuild, both libraries | 2 885 | `Build completed successfully.` |
| `logs/final_check.log` | final verification rebuild | 2 894 | `Build completed successfully.` |
| `logs/sat_build2.log` · `logs/sat_build4.log` | `Satellite` library rebuilds | — | clean |
| `logs/sat_final.log` | `Satellite` + its axiom audit | — | `Build completed successfully.` |
| `logs/choptuik_audit.log` | the `Choptuik` axiom audit | — | `AUDIT_EXIT=0` |

Warnings committed in the logs are **linter notes only** (`unused variable`,
`unused section variable`) — no errors, no sorry warnings, no unsolved goals.

## 2. The axiom audit — the three-axiom policy

Both audit files mechanically print `#print axioms` for every headline theorem.
The full statement lists are mirrored in
[`THEOREMS.md`](THEOREMS.md#the-audited-headline-declarations).

| Audit | Declarations | Permitted axioms found |
|---|---|---|
| `lean/AxiomAudit.lean` | **33** | `propext`, `Classical.choice`, `Quot.sound` — nothing else |
| `lean/Satellite/AxiomAudit.lean` | **62** | `propext` (the counting theorems), plus `Classical.choice`, `Quot.sound` where mathlib analysis enters — nothing else |

Representative lines from `logs/choptuik_audit.log`:

```text
'Choptuik.Existence.critical_solution_exists' depends on axioms: [propext, Classical.choice, Quot.sound]
'Choptuik.Stability.unique_unstable_mode' depends on axioms: [propext, Classical.choice, Quot.sound]
'Choptuik.Scaling.gamma_close_to_published' depends on axioms: [propext, Classical.choice, Quot.sound]
'Choptuik.Bridge.Discharge.correction_root_in_band' depends on axioms: [propext, Classical.choice, Quot.sound]
```

and from `logs/sat_final.log`:

```text
'Satellite.Dial.card_dial' depends on axioms: [propext]
'Satellite.Unlock.unlock' depends on axioms: [propext, Classical.choice, Quot.sound]
'Satellite.Klein.k3_bridge' depends on axioms: [propext]
```

**`sorryAx` appears nowhere.** The string `sorry` occurs in the sources only
inside doc comments of the form “Zero sorry” — a claim the kernel itself
verifies every rebuild.

## 3. The Python-side checks (cross-language twins)

| Script | Checks | Verdict |
|---|---|---|
| `scripts/certify.py check` | the emitted rational certificates against the committed `Generated.lean` fractions | `bridge certificate channel: LIVE` |
| `scripts/b1_berry_model.py` | the exact SymPy series; `0 < R(δ) ≤ δ⁴/4` on 40 points, 50 digits | `ALL BOUNDS PASS` |
| `scripts/check_dial_22.py` | capacity 22, chirality 11 + 11, survivors {x, x+12, −x, 12−x}, closure V₄ | `ALL BRUTE-FORCE CHECKS PASS` |
| `scripts/klein_psl27.py` | 168 element orders, 179 subgroups, 14 × S₄, the {7,3} map 24/84/56, χ = −4, 8 antipodal triangles, 24 privileged pairs with stabilizer 7 | `ALL EXHAUSTIVE CHECKS PASS` |
| `scripts/compute_all.py` | every README number recomputed from the Lean-locked constants; the proved inequalities re-asserted | `wrote 7 files` |

The two sides meet in the middle: Lean verifies the rational skeletons,
Python re-derives them from independent code paths, and both agree to the
last fraction.

## 4. Determinism

* seed **1993** recorded in `data/*.json` and `animations/manifest.json`;
* no `random` call anywhere in `scripts/` at render time (the one seeded
  generator — the log-log jitter of the scaling scatter — uses
  `np.random.default_rng(1993)`);
* re-running any script twice produces byte-identical outputs.
