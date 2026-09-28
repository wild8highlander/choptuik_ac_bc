# audit_transfer

Editorial-verification appendix to the framework monographs: a self-contained,
machine-checked audit of the monograph texts plus two follow-up results that
close open items of the programme. Everything in this folder is computed by
two independent engines (Python and Julia) with fixed seeds and zero fitted
parameters, so every number in the appendix PDFs is reproducible on demand.

## What is verified here

| # | Task | What the code establishes |
|---|------|---------------------------|
| 1 | **Monograph audit** | The b-C and a-C corrections are reproduced from first principles at machine precision (no fitting). A catalogue of seven typographical errors **E1–E7** in the LaTeX sources is derived and each entry is fixed numerically. |
| 2 | **DSI closure of c_K3 = 0.04018** | The last empirical input of the framework is derived at leading order from DSI with λ = 22 = b₂(K3): c_K3 = 1 − cos(2π/22) = 0.0405070 (+0.82%); the braking-coupled RG map gives 0.0403596 (+0.45%); the residual is the finite-window systematics, reproduced numerically. |
| 3 | **Stability lemma Sh.3** | The uniform trace theorem F ≥ 5n/7 is proved (identity F = G(P,Q) + convexity + Haar averaging); the √(4/7)·I sharpness construction is confirmed numerically to 10⁻¹⁴; the soficity→matrix bridge is stated as an exact analytic formulation (the single item that is posed, not computed). |

## What is inside

| Path | Contents |
|------|----------|
| `python/` | Canonical engine: package `audit_transfer/` (`monograph_audit.py`, `dsi_closure.py`, `stability_lemma.py`, `figures.py`), orchestrator `run_all.py`, `requirements.txt` |
| `julia/` | Independent Julia port of the verification core (`audit_transfer.jl`, `Project.toml`); standard library only (LinearAlgebra, Random, Statistics, Printf) |
| `appendix/` | Compiled appendix PDF `Audit_i_Perenos_Prilozhenie.pdf` plus LaTeX/HTML sources and figure sources |
| `lemma_article/` | The Sh.3 lemma as a standalone article: PDF + LaTeX source + cover |
| `figures/` | Four summary PNG figures (audit errors, DSI closure, stability lemma, transfer map) |
| `results/` | Committed JSON outputs: `monograph_audit.json`, `dsi_closure.json`, `stability_lemma.json`, `julia_results.json` |

## How to run

Python engine (Python ≥ 3.10 with NumPy, SciPy, Matplotlib):

```bash
# from the repository root
python3 audit_transfer/python/run_all.py

# or from this folder
cd audit_transfer/python
python3 -m pip install -r requirements.txt
python3 run_all.py
```

Julia engine (independent cross-check, no third-party packages):

```bash
cd audit_transfer/julia
julia audit_transfer.jl            # stdlib-only, project environment not required
julia --project=. audit_transfer.jl  # equivalent, with the project activated
```

The full Python run takes roughly 2–4 minutes (dominated by the numerical
minimisation of the Sh.3 lemma) and rewrites `results/*.json` and
`figures/*.png`. Committed results should match a fresh run to machine
precision because all seeds are fixed.

## Notes

- The two engines are written deliberately independently: agreement between
  `results/*.json` (Python) and `results/julia_results.json` (Julia) is itself
  part of the verification.
- `figures.py` uses Playwright for one structural diagram
  (`fig_transfer_map.png`) only. Without Playwright the run still succeeds and
  the remaining figures are produced; the JSON results are unaffected.
- The appendix states explicitly, throughout, what is *proved*, what is
  *verified numerically*, and what remains an *exact analytic formulation*
  (only the soficity bridge Sh.3(iii) is in the last category).
- The PDF write-ups are in Russian; the LaTeX sources in `appendix/source/`
  and `lemma_article/source/` allow regeneration and translation.
