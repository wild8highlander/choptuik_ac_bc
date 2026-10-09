# Docs — reading order and map

Five documents, one reading order.  Total ~35 minutes; each stands
alone if you already know what it covers.

| order | file | what it is | read it when |
|---:|---|---|---|
| 1 | [theory.md](theory.md) | the physics: pillars, bridge object `f~(eps)`, CMB contact, septinial family (hypothesis), Delta*gamma invariant | you want to know WHAT is claimed and what is honestly not |
| 2 | [methods.md](methods.md) | the numerics: double-null engine, bisection, scans, floor, echo detector, Haar MC, determinism | you want to know HOW every number is produced |
| 3 | [validation.md](validation.md) | the ledger: every check with its number and verdict file | you want to VERIFY instead of trusting |
| 4 | [scaling_law.md](scaling_law.md) | theorem T10: why one formula gives different values at different scales — the two exact lemmas and the drift law | you want the resolution-drift derivation (v2.1.0) |
| 5 | ../results/RESULTS.md | the one-page result register + roadmap | you want the headlines |

## Conventions used across the docs

- **anchor** — a literature or engine value used for comparison only;
  never a fit target.
- **honest negative** — a committed non-result (mass floor, flat fit,
  unresolved echoes) with its diagnostic trail.
- **verdict** — a machine-readable JSON in `campaigns/reference/`;
  prose pages cite it, never replace it.
- code units are `4 pi G = 1` (`kappa = 2`) unless SI is explicit.

## Relationship to the code

`docs/` claims <-> `chbridge/` implements <-> `campaigns/` measures <->
`data/bridge/` stores <-> `tests/` pins <-> `docs/validation.md`
audits.  A doc statement that no test or verdict supports is a bug;
report it as such.
