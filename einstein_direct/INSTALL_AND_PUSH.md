# Installation and Running (einstein_direct)

This note describes how to install the dependencies and run the verification
laboratory of this folder — on a desktop and on an Android phone (Termux).
For the full documentation see [README.md](README.md) and the deep ledger
[README_EN.md](README_EN.md).

## 1. Requirements

- Python ≥ 3.9
- NumPy, SciPy, SymPy, matplotlib, pytest
- ~200 MB of free disk space for results and figures

```bash
python3 -m pip install numpy scipy sympy matplotlib pytest
```

No compiled extensions of this repository are required; everything is pure
Python on top of the scientific stack.

## 2. Desktop quick start

```bash
cd einstein_direct

# symbolic layer (machine-verified derivation)
python3 sympy_derivation.py            # residuals ~1e-41 vs Roberts–Oshiro
python3 roberts_test.py                # solver regression

# verification suite (fast, re-checks machine theorems from results/)
python3 -m pytest tests/ -q            # 21 passed

# numerical campaigns
python3 choptuik_scaling.py --n-bisect 1200
python3 zoom_campaign_regular.py       # ~5–8 min
python3 grid_machine_annulus.py        # full eps ladder

# figures
python3 figures.py && python3 spinor_figures.py
```

All machines set `OPENBLAS/OMP/MKL/NUMEXPR_NUM_THREADS = 1` internally;
do not override this — multithreaded LAPACK breaks near-critical
reproducibility.

## 3. Android (Termux)

```bash
bash termux/01_termux_install.sh       # once per device (from the repo root)
bash termux/02_termux_run.sh           # full pipeline (~1 h)
bash termux/02_termux_run.sh --quick   # ~15 min, coarser grids, same protocol
```

The Termux runner auto-locates `einstein_direct/`, runs the pytest suite, the
fixed-grid campaign, the zoom campaign and the spinor analysis, and writes
all JSONs into `einstein_direct/results/`.

## 4. Publishing results

Results are plain files inside the repository. To publish them from the
phone:

```bash
bash termux/03_push_to_github.sh       # interactive; credentials are asked,
                                       # nothing is stored in the repository
```

Standard git usage from a desktop clone works identically
(`git add … && git commit … && git push`). No personal access tokens are ever
written into the repository tree or into tracked configuration.
