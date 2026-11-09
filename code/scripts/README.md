# scripts/ — Repository-Level Utility Scripts

Utility scripts that operate on the whole repository rather than on the
`einstein_direct/` laboratory itself. The research machines live in
`einstein_direct/`; everything here is packaging, runners and checks.

## What is inside

| File | Role |
|---|---|
| `run_all.sh` | runs the full verification pipeline end-to-end (derivation, solver tests, campaigns) |
| `run_verify.sh` | runs only the verification/pytest layer |
| `run_viz.sh` | starts the interactive visualization app |
| `build_java.sh` | builds the Java web application |
| `brick_scan_tick.py`, `brick_scan_tick.json` | copy of the intermediate-bricks machine and its committed output (kept here for repository-level runners) |
| `global_static_search.py`, `global_static_search.json` | copy of the global static census machine and its committed output |
| `qcd_bridge/` | helper scripts of the QCD-bridge artifact folder |
| `scrub_readme_en.py` | one-shot maintenance script used to keep the documentation consistent |

## How to use

```bash
bash scripts/run_all.sh      # everything
bash scripts/run_verify.sh   # verification suite only
bash scripts/run_viz.sh      # interactive visualization
bash scripts/build_java.sh   # java-webapp build
```

## Notes

- The canonical copies of `brick_scan_tick.py` and `global_static_search.py`
  live in `einstein_direct/`; the copies here exist so that repository-level
  runners can execute them without changing directories. When editing the
  machines, edit the canonical copies in `einstein_direct/` first.
- All runner scripts are idempotent and never delete results.
