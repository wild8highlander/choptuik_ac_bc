# monograph/ — the two-volume bilingual monograph set

Version 2.1.0 (IVP-15 alignment edition) · 8 documents · RU/EN × {appendix,
theorems} × {DOCX, PDF} + regenerable sources · all four DOCX pass
postcheck with 0 errors

---

## What this directory is

`monograph/` is the scholarly layer of the package: two reference
volumes, each shipped in Russian and English, each as an editable DOCX
and a print-ready PDF. Together they convert the package from a code
repository into a citable, quotable, self-contained research edition:

| volume | RU | EN | content |
|--------|----|----|---------|
| **Encyclopedic appendix** | `appendix_ru.docx` / `pdf` | `appendix_en.docx` / `pdf` | 13 parts: constants, engine, campaigns C1–C3b **and C6**, the bridge, theorems register, data dictionary, figure catalog, multilang matrix, reproduction runbook, roadmap + stage analysis, glossary, FAQ |
| **The theorems volume** | `theorems_ru.docx` / `pdf` | `theorems_en.docx` / `pdf` | 15 sections: **ten theorems T1–T10** with statements, proofs, verification and statuses; the verification matrix; the honesty register (eight items); references incl. the IVP-15 audit |

The two volumes cross-reference each other: the appendix's part VI is
the summary register of the theorems, and every theorem names its
campaign verdicts, figures and test pins. Page counts at packaging:
appendix ≈ 21–22 pages, theorems ≈ 16–17 pages (per language).

## What changed at v2.1.0 (the IVP-15 alignment)

The 2.0.0 volumes quoted the pre-audit numbers (the retracted
`1.06e-6` A*-agreement, the `gamma_eff ~ 0.12` artifact, the
`12/N ± 7%` floor wording). This edition quotes **only the
remediated, independently verified numbers**:

- the five-grid F-1 remediation ladder (`0.1051042795 … 0.0768211603`)
  with the honest drift `2.79e-3` per N800→N1600;
- the per-grid F-2 values: `gamma_eff = 0.041/0.060` (floor-dominated,
  r² 0.33/0.41) and floors `8.575e-3/4.245e-3` (law `(13 ± 1)/N`);
- the new **theorem T10** — the resolution-drift law
  (`A*_N − A*_cont = κ*·α²h²/(8s) > 0`): why one formula gives
  different values at scalar-scaled grids; two exact machine-verified
  lemmas (chord flattening `κh²/8`; chord-chain arc deficit), the C6
  calibration (`κ* = 2728.60`, `s = 413.8`), and the honest negatives
  (no `A*_inf`; the exact channel is sub-dominant, share
  `2.6e-3..9.1e-3`);
- a new part IV.5 (C6) in the appendix, a T10 row in both registers,
  an expanded honesty register (eight items), and the IVP-15 audit in
  the reference apparatus of both volumes;
- test/verification counts updated everywhere: **63 pytest** pins
  (incl. three C6 pins), 7/7 mpmath, twins `7.1e-13`.

## Design identity

Both volumes use the package's **Ink & Gold** identity: the R2
double-rule cover (ink `#1A1A1A`, gold `#C9A84C`), gold-ruled H1s,
gold-header zebra tables with the `#F5F2E8` surface, and figure
plates embedded from the light-theme figure catalogs. The same tokens
drive `../figures_hires/`, `../figures/logo/` and the web companion,
so a screenshot of any page is instantly recognizable as part of this
package.

Typography: Times New Roman throughout (all Unicode slots — Latin,
Cyrillic, math), 12 pt body, justified, 1.3 line spacing, three-zone
page numbering (cover unnumbered → front matter in Roman numerals →
body restarting at 1 in Arabic), running headers, TOC field with
placeholder entries and an explicit refresh hint.

## Document architecture (identical in all four DOCX)

1. **Cover section** — margin-0, exact-height wrapper, zero nested
   tables, `allNoBorders` (cross-engine safe: MS Office and WPS).
2. **Front-matter section** — TOC title (not a heading), the
   `TableOfContents` field, the refresh-hint note, Roman page numbers.
3. **Body section** — Arabic numbering restarting at 1; H1/H2/H3 real
   heading styles (TOC-indexable, outline levels set); tables with
   `tableHeader` + `cantSplit` + `keepNext` titles; figures embedded
   with exact aspect ratios read from the PNG headers.

## Sources and regeneration

The single source of text is the generator pair under `src/`:

```
src/common.js          shared builder (cover R2, styles, tables, math, assembly)
src/theorems_ru.js     → theorems_ru.docx
src/theorems_en.js     → theorems_en.docx
src/appendix_ru.js     → appendix_ru.docx
src/appendix_en.js     → appendix_en.docx
src/postprocess_pagenum.py   footer format switches (WPS compatibility)
```

Regenerate everything:

```bash
cd monograph/src
node theorems_ru.js && node theorems_en.js
node appendix_ru.js && node appendix_en.js
cd ..
for f in theorems_ru theorems_en appendix_ru appendix_en; do
  python3 src/postprocess_pagenum.py $f.docx
done
soffice --headless --convert-to pdf --outdir pdf *.docx
```

The generators read every number from the committed verdicts and
tables (never hand-typed), embed figures by relative path from
`figures/`, `figures_hires/` and `results/scaling_drift/figures/`, and
are deterministic for a fixed package snapshot. Editing one table in
`data/bridge/` therefore propagates: rerun `rebuild_data.py`, then the
generators, then the conversion — the volumes cannot drift from the
data layer.

Post-generation checks (all four documents):

```bash
python3 $DOCX_SCRIPTS/add_toc_placeholders.py <file>.docx --auto   # exit 0
python3 $DOCX_SCRIPTS/postcheck.py <file>.docx                     # 0 errors
```

Packaging-time results at v2.1.0: postcheck reports **0 errors** on all
four (two benign warnings per volume: the section-separator page break
after the TOC, and mixed line spacing from table cells versus body
paragraphs — both by design).

## Theorem set (theorems volume, summary)

| № | theorem | status |
|---|---------|--------|
| T1 | Page fraction τ* = 1 − 2^(−3/2) = 0.6464466094… | exact |
| T2 | unique CMB contact mass 4.5016e22 kg | exact (Schwarzschild idealisation) |
| T3 | b_Ch = 2 sin²(π/7) = 0.37651019814126640; 0.67 % to γ_Ch | exact + comparison |
| T4 | engine convergence orders 2.031 / 2.093 ≈ 2 | numerically established |
| T5 | floor law floor_M ≈ (13 ± 1)/N (per-grid F-2 values) | numerically established |
| T6 | Δ·γ = 1.28656 inside 1.27 ± 0.05 (PASS 1.3 %); engine level negative | comparison |
| T7 | q_max strictly monotone; slowdown b = −0.0334, r² = 0.714 | numerically established |
| T8 | echo rate 0.1909 < 1/Δ = 0.2907 | numerically established |
| T9 | S_rad(τ*)/S0 = 1/2 exactly | exact (corollary of T1) |
| **T10** | **resolution drift: A*_N − A*_cont = κ*α²h²/(8s) > 0 (parabolic-tension sampling; κ* = 2728.60, s = 413.8; no A*_inf claimable)** | **analytically derived; measured** |

Status vocabulary is the package's honesty discipline: **exact** means
algebraically proved and committed as a closed form; **numerically
established** means measured on committed runs and pinned by tests;
**analytically derived** means proved for a committed model with
machine-verified lemmas and coefficients measured on committed
artifacts; **comparison** means related to literature anchors with no
derivation claim. The register repeats in every final document of the
package.

## Why DOCX and PDF from one source

Four independent authoring pipelines would guarantee drift between
languages and formats. Instead: one generator per volume per language
produces the DOCX (the editable master), and LibreOffice produces the
PDF from that exact master. Consequences: RU/EN stay structurally
aligned (same tables, same figures, same numbering), every PDF is a
faithful render of its DOCX, and any edit happens in exactly one place
— the generator — before both formats are rebuilt.

## Honesty notes

1. The volumes quote only committed numbers; the generators contain no
   constants of their own (spot-check: grep the `src/*.js` files —
   every numeric literal is either a label, a retraction note, or a
   layout size).
2. Figure plates embed from the light theme; the dark-theme variants
   exist in the catalogs but are not embedded (print optimisation).
   The T10 figure embeds from `results/scaling_drift/figures/`.
3. PDF page counts are produced by LibreOffice 25.2 and may shift by
   ±1 page across converters; the DOCX is the master.
4. The theorems volume deliberately includes the honest negatives
   (T6 engine level, the floor-dominated per-grid γ_eff, Δ unresolved,
   no A*_inf, the sub-dominant exact channel) with the same
   typographic weight as the positive results.
5. Both editions carry the full honesty register as a closing section
   — trimming it out of a translation is forbidden by `CONTRIBUTING.md`.
6. The 2.0.0 editions quoted the retracted `1.06e-6` agreement and the
   `γ_eff ~ 0.12` artifact; they are superseded by this v2.1.0
   alignment edition (see CHANGELOG and `independent_verification/`).

## FAQ

**Q: Which volume should I cite?** Cite the appendix for data,
protocols and reproduction; cite the theorems volume for statements
and proofs. Both carry the same version and date; the CITATION.cff at
the package root covers the package as a whole.

**Q: Why is the appendix ~21 pages and not 200?** Encyclopedic means
*complete and indexed*, not *padded*: every number of the ledger, every
protocol and every catalog entry is here; narrative repetition and
re-derived textbook material are not. The 600 dpi figure suite and the
data workbook carry the bulk that would otherwise bloat the pages.

**Q: Can I translate a third language?** Yes — copy one generator,
translate the content strings, keep the structure calls identical, and
add the language to this README. The shared `common.js` guarantees the
new edition lands on the same layout.

**Q: Why Times New Roman and not the package's display font?**
Print convention and metric safety across Word/WPS/LibreOffice; the
Ink & Gold identity lives in the palette and rules, which survive any
document font.

**Q: Do the PDFs contain selectable text?** Yes — LibreOffice
conversion is vector; text is selectable, searchable and copyable, and
both PDFs keep the document metadata (title, author, description).

## See also

* `../figures_hires/README.md` — the print-grade figure catalog.
* `../figures/logo/` — the package logo (light/dark, PNG + SVG).
* `../tables/README.md` — the Excel data layer.
* `../multilang/README.md` — the cross-language twins.
* `../results/ROADMAP.md` — where the research goes next.
* `../docs/scaling_law.md` — the T10 derivation the theorems volume summarises.
* `../docs/theory.md`, `../docs/methods.md` — the technical prose.

## Краткое резюме (RU)

`monograph/` — научный слой пакета: два тома на двух языках в двух
форматах (8 документов). Том 1 — энциклопедическое приложение (13
частей: константы, движок, кампании C1–C3b и C6, мост, реестр теорем,
словарь данных, каталог фигур, мультиязычная матрица, воспроизведение,
роадмап и анализ этапа, глоссарий, FAQ). Том 2 — **десять теорем
T1–T10** с формулировками, доказательствами, верификацией и статусами,
матрицей верификации и регистром честности из восьми пунктов. Издание
v2.1.0 согласовано с независимой верификацией IVP-15: цитируются только
исправленные числа (лестница F-1, пороговые значения F-2), добавлена
теорема T10 — закон дрейфа с разрешением. Единый источник текста —
генераторы `src/*.js`; DOCX — мастер, PDF — конвертация LibreOffice;
все четыре DOCX проходят postcheck с 0 ошибок. Фирменный стиль
Ink & Gold совпадает с фигурами, логотипом и веб-приложением.
