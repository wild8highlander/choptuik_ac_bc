# dsi_lab

DSI Laboratory: a self-contained package of **seven experiments** on the open
problems of the b-C/a-C spinor-correction framework (Klein quartic, genus 3,
PSL(2,7)) and the Choptuik critical-collapse problem. The package has no
dependency on the parent repository — everything reproduces with one command,
with fixed seeds, so regenerated results match the committed JSON files to
about 1e-13.

## What is verified here

| # | File | Target | Key result |
|---|------|--------|------------|
| 1 | `exp1_sh3_bridge.py` | Open problem Sh.3(iii): trace bridge | Trace theorem confirmed (n = 7..12, gap ≤ 5.9e-8); Cuntz tree F = n+2 exact; the sofic √ε-law **refuted** by data |
| 2 | `exp2_dsi4.py` | DSI-4: c_K3 = 27/672 | 9/224 is a convergent of CF [0;24,1,8,…], rank #1 for q ≤ 2000; Gaussian mass 0.0499 |
| 3 | `exp3_hurwitz.py` | Hurwitz tower | **Finding D1**: the repository row (g=14, n=11) is inconsistent (1092 not divisible by 11); the correct group is PSL(2,13); prediction Δ_Ch(π/13) = 3.3672 |
| 4 | `exp4_qnm.py` | QNM catalogue | 10 events; overtone detectability 0.84σ at Cosmic Explorer; falsifiable Δf_n/f_n = const = 8.3857e-5 |
| 5 | `exp5_qcd.py` | QCD bridge | **Finding E1**: tr(Q_K3⊕M_F) = 32 requires centering ⟨λ⟩; afterwards slope −0.99 (~1/N); κT-sweep: BF(GUE) up to 1165 |
| 6 | `exp6_census_224.py` | Why the denominator 224 = 4·56? | Explicit {7,3} census from GL(3,2): V=56, E=84, F=24, 7F=3V=2E=168; **uniqueness lemma** for 9/224; **degeneracy theorem**: branches c(g) coincide only at g=3 |
| 7 | `exp7_e1_threshold.py` | Threshold e ≥ 1 | **Theorems A/B/C proven and verified** (identity 5.9e-16 over 24000 pairs); ladder 5/7 → 1 → 2 is a theorem; carrier-isometric constructions cannot realize the Sh.3(iii) bridge |

## What is inside

| Path | Contents |
|------|----------|
| `run_all.py` | Orchestrator: all experiments, subset selection, `--list` |
| `exp1…exp7*.py` | The seven deterministic experiments |
| `fig_choptuik.py` | Summary Choptuik figure |
| `figlabels.py` | Bilingual figure labels (en/ru) |
| `tests/` | pytest suite: theorems A/B/C, the {7,3} census, the 9/224 convergent, Hurwitz tower, smoke tests |
| `results/` | Seven committed JSON results, one per experiment |
| `fig_en/`, `fig_ru/` | 16 ready-made figures per language |
| `reports/` | Eight final documents (PDF + DOCX, EN/RU) with LaTeX sources in `tex/` and HTML covers |
| `Makefile` | Shortcut targets (see below) |
| `requirements.txt` | numpy, scipy, matplotlib, pytest |

## How to run

```bash
cd dsi_lab
python3 -m pip install -r requirements.txt

python3 -m pytest tests/ -q     # fast theorem checks (~2 min)
python3 run_all.py              # all 7 experiments (~5–15 min)
python3 run_all.py 2 6 7        # subset of experiments
python3 run_all.py --list       # list experiments
python3 fig_choptuik.py         # summary figure only
```

Makefile shortcuts (the same commands):

```bash
make test     # pytest suite (~1–2 min)
make run      # all 7 experiments + the summary figure (5–15 min)
make quick    # fastest subset: experiments 2, 6, 7
make fig      # summary Choptuik figure only
make verify   # test + run (full verification)
make clean    # remove __pycache__ and .pytest_cache
```

## Notes

- Requirements: Python ≥ 3.9 with numpy, scipy, matplotlib, pytest. No
  imports from the parent repository — the folder is intentionally
  standalone and can be copied out and run elsewhere.
- All experiments are deterministic (fixed seeds). A fresh run should
  reproduce the committed `results/*.json` to ~1e-13; larger deviations are
  a verification finding.
- On Android/Termux the commands are identical (`pkg install make` first);
  the former Termux-specific readme has been folded into this file — the
  targets above were chosen to be Termux-friendly.
- `reports/` contains its own README describing the compiled reports; the
  LaTeX sources in `reports/tex/` allow regeneration of the PDFs.
- Findings D1 (Hurwitz tower) and E1 (QCD trace centering) are corrections
  discovered *by* the experiments and are called out explicitly in the
  reports — the package practices the same honesty policy as the monographs:
  proved / verified numerically / refuted are always distinguished.
