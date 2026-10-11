# tables/ — the workbook layer

Version 2.2.0 · 1 XLSX · 14 sheets

---

## What this directory is

`tables/` holds **bridge_workbook.xlsx** — the entire committed data
layer of the package as a single portable spreadsheet. The CSV files
in `../data/bridge/` remain the machine source of truth
(byte-deterministic, test-pinned); the workbook is the human layer:
frozen headers, zebra rows, typed numbers, an Overview sheet with the
headline ledger, and one sheet per table with a descriptive title.

The workbook is generated, not hand-edited:

```bash
python3 scripts/build_workbook.py     # ~1 s, openpyxl only
```

Validation: `xlsx.py validate` → `status: passed, total_issues: 0`.

## Sheet inventory

| sheet | source | rows | content |
|-------|--------|------|---------|
| `Overview` | headline ledger + meta | 17 + 6 | package meta, 17 headline numbers with sources, sheet inventory |
| `bridge_constants` | `bridge_constants.csv` | 8 | Part A/B/C constants actually used by the bridge |
| `bridge_master` | `bridge_master.csv` | 15 | the full mapping: 5 input scales × 3 members × 23 columns |
| `born_spectrum` | `born_spectrum.csv` | 44 | born runs (26 @ N=400, 18 @ N=800) |
| `collapse_verdict_summary` | `collapse_verdict_summary.json` | 25 | flattened verdict summary (key/value) |
| `page_curve_grid` | `page_curve_grid.csv` | 720 | S_rad grid, 3 members × 240 points |
| `page_members` | `page_members.csv` | 3 | member definitions (f~) |
| `page_haar_check` | `page_haar_check.csv` | 18 | Haar formula vs Monte-Carlo, max dev 0.0042 bits |
| `scale_ladder_length` | `scale_ladder_length.csv` | 8 | lengths ladder |
| `scale_ladder_accel` | `scale_ladder_accel.csv` | 8 | accelerations ladder |
| `scale_ladder_curvature` | `scale_ladder_curvature.csv` | 5 | curvature ladder |
| `campaign_c2_subcritical` | `campaign_c2_subcritical.csv` | 13 | q_max / v_qmax / n_peaks / q_final per run |
| `campaign_c2_bifurcation` | `campaign_c2_bifurcation.csv` | 13 | f~ / M_code / sanity per run (junk kept) |
| `campaign_c3b_ladder` | `campaign_c3b_ladder.csv` | 12 | N=1600/3200 concentrated runs |

## Column semantics

The full 23-column dictionary of `bridge_master` lives in
`../data/README.md` (six groups: identity, geometry, thermodynamics,
radiation, curvature, comparison). The two campaign sheets are
verbatim copies of the committed verdict tables — the
`rebuild_data.py` stage [4/5] copies them without transformation, so
workbook cells equal verdict fields exactly. JSON-sourced sheets
(`collapse_verdict_summary`) are flattened one level with dotted keys
and are marked as key/value, not as a table.

## Design notes

* Numbers are typed where the source CSV carries clean numerics
  (`_numify`); identifiers, stop-reasons and flags stay text so that
  `True/False` semantics survive round-trips.
* Headers frozen at row 3 (`freeze_panes = A4`); column widths
  auto-fitted with a 42–64 char cap.
* No formulas, no macros, no charts inside the workbook by design:
  every derived view lives in the figure suites and the web app, and
  the workbook stays a faithful data mirror (the skill's live-formula
  guarantee does not apply to a conversion target).
* Generator: `../scripts/build_workbook.py` (openpyxl, no external
  deps); re-run any time — output is deterministic for a fixed
  `data/bridge/` snapshot.

## Honesty notes

1. The workbook is a *snapshot*: if a campaign verdict changes, the
   CSVs change (by rerunning the campaign) and the workbook must be
   rebuilt — a one-command step that CI can own.
2. Junk rows are present and flagged exactly as in the CSVs; nothing
   is filtered, rounded or "cleaned" on the way into the workbook.
3. The Overview headline values are copied from `../results/RESULTS.md`
   at v2.1.0 and each carries its source — the workbook adds no
   numbers of its own.

## FAQ

**Q: Why XLSX and not ODS?** XLSX is the lowest common denominator
across Office suites and pandas/openpyxl; ODS conversion is one
LibreOffice command away if needed.

**Q: Why 14 sheets and not one giant sheet?** The tables have
incompatible shapes (720-row grids vs 8-row ladders); a merged sheet
would need a union schema that serves nobody. One sheet per table
mirrors the CSV layout 1:1.

**Q: Can I diff the workbook against the CSVs?** Yes — regenerate it
and compare cell ranges; or simpler, diff the CSVs (the workbook adds
zero derived values).

**Q: Where are the campaign verdict JSONs?** In
`../campaigns/reference/`; the workbook mirrors only the flattened
summary — the full verdicts stay JSON because they carry nested
protocol metadata.

**Q: Is there a chart inside?** No — by design (see Design notes).
The visual layer is `../figures/`, `../figures_hires/`, `../animations/`
and the web companion.

## Краткое резюме (RU)

`tables/bridge_workbook.xlsx` — вся зафиксированная таблица данных
пакета в одном файле: 14 листов (обзор с 17 заголовочными числами и
источниками + 13 таблиц данных), зебра, закреплённые шапки, типизация
чисел. Рабочая книга — производный слой от байт-детерминированных CSV
`../data/bridge/`; генерируется `scripts/build_workbook.py` за секунду,
валидация xlsx.py: 0 замечаний. Ничего не фильтруется и не
пересчитывается; мусорные строки сохранены.
