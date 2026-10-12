# logs/ — logged verification runs

This directory keeps the logged verification runs of the package:
`bash scripts/run_logged.sh` runs `make verify` (test + validate + run)
and tees everything to `logs/run_<UTC timestamp>.log`, stamped with:

- the UTC start time, host and git SHA;
- the tool versions (python, numpy, scipy, matplotlib);
- the full output of the pytest suite, the committed-verdict audit and
  all seven experiments;
- the sha256 of every `results/*.json` **after** the run, so any future
  run can be compared byte-for-byte against the committed verdicts.

## Convention

Logs are append-only artifacts: a new run adds a new file and never
edits an old one. If a run disagrees with the committed verdicts beyond
the tolerance of [`../docs/methods.md`](../docs/methods.md), the log is
the evidence — keep it and add a row to the claim ledger.

## Files

| file | run |
|------|-----|
| `run_20261012T085952Z.log` | the v2.0.0 release verification: tests 51 passed · validate 13/13 · all 7 experiments (94.9 s total) · `git diff results/` empty — byte-identical determinism |
