# dsi_lab — DSI Laboratory for the Choptuik–Isaev Framework

Self-contained package with **7 experiments** on the open problems of the
b-C/a-C spinor-correction framework (Klein quartic, genus 3, PSL(2,7)) and
the Choptuik critical-collapse problem. The package has **no dependency** on
the parent repository — everything reproduces with one command.

## Results at a glance

| # | File | Target | Key result |
|---|------|--------|------------|
| 1 | `exp1_sh3_bridge.py` | Open problem Sh.3(iii): trace bridge | Trace theorem confirmed (n=7..12, gap ≤ 5.9e-8); Cuntz tree F = n+2 exact; sofic √ε-law **refuted** by data |
| 2 | `exp2_dsi4.py` | DSI-4: c_K3 = 27/672 | 9/224 is a convergent of CF [0;24,1,8,…], rank #1 for q ≤ 2000, Gaussian mass 0.0499 |
| 3 | `exp3_hurwitz.py` | Hurwitz tower | **Finding D1**: repo row (g=14, n=11) is inconsistent (1092 not divisible by 11); correct is PSL(2,13); prediction Δ_Ch(π/13) = 3.3672 |
| 4 | `exp4_qnm.py` | QNM catalogue | 10 events; overtone detectability 0.84σ at Cosmic Explorer; falsifiable Δf_n/f_n = const = 8.3857e-5 |
| 5 | `exp5_qcd.py` | QCD bridge | **Finding E1**: tr(Q_K3⊕M_F)=32 requires centering ⟨λ⟩; afterwards slope −0.99 (~1/N); κT-sweep: BF(GUE) up to 1165 |
| 6 | `exp6_census_224.py` | Why denominator 224 = 4·56? | Explicit {7,3} census from GL(3,2): V=56, E=84, F=24, 7F=3V=2E=168; **uniqueness lemma**: 9/224 is unique within the rewrite budget; **degeneracy theorem**: branches c(g) coincide only at g=3 → discriminator (g−1)⁻¹ vs (g−1)⁻² |
| 7 | `exp7_e1_threshold.py` | Threshold e ≥ 1 | **Theorems A/B/C proven and verified** (identity 5.9e-16, 24000 pairs): ladder 5/7 → 1 → 2 is now a theorem; carrier-isometric constructions cannot realize the Sh.3(iii) bridge (η ≡ 1) |

Full reports: `reports/` (PDF + DOCX, RU/EN).

## Quick start

```bash
cd dsi_lab
python3 -m pip install -r requirements.txt
python3 -m pytest tests/ -q     # fast theorem checks (~2 min)
python3 run_all.py              # all 7 experiments (~5-15 min)
python3 run_all.py 2 6 7        # subset
```

Requirements: Python ≥ 3.9, numpy, scipy, matplotlib, pytest. No imports from
the parent repository. All experiments are deterministic (fixed seeds);
regenerated `results/*.json` should match the committed ones to ~1e-13.

Android/Termux instructions: see [README_TERMX.md](README_TERMX.md) (Russian;
the commands are copy-paste friendly).

## Layout

```
run_all.py         orchestrator (all experiments, subset selection, --list)
exp1..exp7*.py     experiments (deterministic)
fig_choptuik.py    summary Choptuik figure
figlabels.py       bilingual figure labels (ru/en)
results/           7 committed JSON results
fig_ru/, fig_en/   16 ready figures each
tests/             pytest suite: theorems A/B/C, {7,3} census, 9/224, Hurwitz
reports/           8 final documents (PDF/DOCX, RU/EN) + LaTeX sources
```
