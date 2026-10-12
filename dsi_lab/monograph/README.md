# monograph/ — the DSI laboratory monographs (EN + RU)

Version 2.0.0 · compiled with Tectonic (XeTeX engine) · sources in `tex/`

---

## What is here

| file | contents |
|------|----------|
| `dsilab_monograph_en.pdf` | **The DSI Laboratory: Dynamics of Invariants for the b–C/a–C Framework** — the full theorem layer, census attack, findings D1/E1, honesty discipline, Lean 4 layer (English) |
| `dsilab_monograph_ru.pdf` | the same monograph — Russian edition |
| `tex/dsilab_monograph_en.tex` | LaTeX source of the English edition |
| `tex/dsilab_monograph_ru.tex` | LaTeX source of the Russian edition |
| `tex/figures/` | the figures embedded by both editions (copied from `fig_en/`) |

The monographs are the citable, self-contained statement of the
package: the theorem layer with proofs (the sharp trace theorem,
theorems A/B/C + corollary D), the uniqueness lemma and the degeneracy
theorem for 9/224, the two corrections produced by the package
(findings D1 and E1), and the reproduction contract.

## Rebuild

```bash
cd dsi_lab/monograph/tex
tectonic dsilab_monograph_en.tex
tectonic dsilab_monograph_ru.tex
mv dsilab_monograph_*.pdf ..
```

Requirements: [Tectonic](https://tectonic-typesetting.github.io) with
network access on the first run (it fetches packages on demand). The
Russian edition needs the Liberation fonts (installed by default on
Linux; on other systems substitute any Cyrillic-capable serif).

## Relation to the reports

The compiled short reports (attack + open-problems, EN/RU, PDF + DOCX)
live in [`../reports/`](../reports/); the monograph is the long form
and supersedes the reports wherever they disagree.
