# Contributing to formal_choptuik

> The house rules are short because they are strict.  The parent
> repository's discipline — *hypothesis → machine confirmation → honest
> caveats* — applies verbatim.

## Ground rules

1. **Every `sorry` is a ledger entry.**  A new `sorry` in
   `lean/Choptuik/**` must (a) carry a `G\d` gap-id comment, (b) exist in
   [`blueprint/gap_registry.csv`](blueprint/gap_registry.csv).  CI fails
   otherwise.
2. **No new axioms.**  Theory modules rest on `Classical.choice`,
   `propext`, `Quot.sound` only — see
   [`blueprint/axiomatic_base.md`](blueprint/axiomatic_base.md).
3. **Numerics never enter proofs raw.**  Floats cross the bridge as
   interval certificates; the proof layer consumes
   `interval_bound`-style enclosures only.
4. **Protocol changes are paired with tests.**  `bridge/protocol.md`
   changes require a same-commit pytest in
   [`python/tests/`](python/tests/).
5. **Regenerability.**  Touching `data/`, `figures/` or `assets/gifs/`
   means touching the generator scripts, never hand-editing outputs.

## Workflow

```bash
# theory changes
cd lean && lake exe cache get! && lake build

# service changes
cd python && python -m pytest tests/ -v

# asset/data changes
cd python && python scripts/generate_data.py \
  && python scripts/generate_figures.py \
  && python scripts/generate_animations.py
```

## Commit conventions

* `lean(G1): ...` — theory work tied to a gap id
* `python: ...` / `bridge: ...` / `docs: ...` — subsystem prefixes
* One logical change per commit; the milestone ledger
  (`roadmap/milestones.csv`) flips only with acceptance evidence.

## Where to discuss

Open a Discussion in the parent repository
(`wild8highlander/choptuik_ac_bc`) tagged `formal_choptuik`.  Gap-level
design debates should reference the registry id and cite the monograph
section that motivates the change.
