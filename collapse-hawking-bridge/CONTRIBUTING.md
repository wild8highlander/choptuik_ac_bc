# Contributing to the Collapse-Hawking Bridge

Thank you for considering a contribution. This repository is a research
package with a strict epistemic discipline; contributions are accepted
when they strengthen that discipline, not only when they add code.

## The discipline (read first)

1. **Anchors, never fits.** Literature values (`gamma_Ch = 0.374`,
   `Delta = 3.44 +- 0.02`) are comparison anchors. Nothing in the
   pipeline is tuned to reproduce them. If your change introduces a
   fitted quantity, it must be labeled as such in the verdict JSON.
2. **Machine-readable or it did not happen.** Every numerical claim of
   the project must trace to a committed JSON/CSV under
   `campaigns/reference/` or `data/bridge/`. Print statements are not
   results.
3. **Honest negatives are results.** Mass floors, junk rows, NOT-DSS
   verdicts, unmeasurable exponents — they are committed and flagged,
   never hidden or silently dropped.
4. **Reproducibility over cleverness.** A slower deterministic run that
   anyone can repeat beats a faster one nobody can.

## Development setup

```bash
python3 -m pip install -e ".[dev]"
make test        # pytest suite
make validate    # 50-digit mpmath checks
make data        # rebuild derived tables from committed verdicts
```

## What a good contribution looks like

- a new test that pins a previously unpinned number;
- a documentation fix that removes an ambiguity;
- a new campaign (`campaigns/run_cN.py`) that follows the C1/C2
  template: argparse knobs, JSON verdict, honest notes section,
  wall-time recorded;
- a figure improvement that keeps the Ink-Gold style tokens of
  `scripts/figstyle.py` and both languages (RU/EN) and themes
  (light/dark) working.

## Adding a campaign

Copy the structure of `run_c2.py`: a `VERDICT` dict with campaign tag,
engine string, project version, units, per-step rows, an `honest_notes`
block, and a final JSON dump into `campaigns/reference/`. Campaigns must
stay in engine code units; any physical mapping belongs to `chbridge`.

## Style

- Python >= 3.9, no new heavy dependencies without discussion.
- Docstrings state WHAT is computed and WHAT it is compared against.
- Comments explain why, not what.

## License

By contributing, you agree that your contributions are licensed under
the project license (see LICENSE) and that the Author retains all
rights under that license.
