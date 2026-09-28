# termux/ — Running the Verification Suite on Android (Termux)

This folder contains the shell entry points that run the whole verification
pipeline of `einstein_direct/` on an Android phone via Termux, and the push
helpers used to publish commits from the phone.

## What is inside

| File | Role |
|---|---|
| `01_termux_install.sh` | one-shot environment setup: packages, Python, NumPy/SciPy/SymPy/matplotlib/pytest inside Termux |
| `02_termux_run.sh` | runs the full pipeline: pytest suite → fixed-grid campaign → zoom campaign → spinor analysis; writes JSONs into `einstein_direct/results/` |
| `03_push_to_github.sh` | interactive helper that commits and pushes the repository from the phone (asks for credentials; nothing is stored in the repo) |
| `choptuik_push.sh` | minimal commit-and-push helper (add/commit/push with status output) |
| `install_shortcut.sh` | installs a shell alias so the pipeline can be started with one word |

## How to use

```bash
# inside Termux, from a clone of this repository:
bash termux/01_termux_install.sh     # once per device
bash termux/02_termux_run.sh         # full run (~1 h on a phone)
bash termux/02_termux_run.sh --quick # reduced grids, ~15 min
```

`02_termux_run.sh` auto-locates the `einstein_direct/` folder next to itself
or inside a local clone; the `--quick` profile lowers the bisection grid
(N = 600) and keeps every other protocol unchanged, so the run stays a
faithful (if coarser) verification.

## Notes

- The scripts are idempotent and safe to re-run; they never modify results,
  they only append new JSONs.
- Credentials for `03_push_to_github.sh` are typed interactively or supplied
  via the standard git credential mechanisms; **no tokens are stored inside
  this repository**.
- The phone runs are single-threaded by design, matching the reproducibility
  discipline of the desktop machines.
