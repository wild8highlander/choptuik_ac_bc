# CHANGES — formal_choptuik/README.md update

Base: `formal_choptuik/README.md` @ commit `394abc` (2026-10-24, "Choptuik AC-BC").
Method: full clone + audited inventory (files counted, tests collected with
`pytest --collect-only`, theorems/axioms/sorries grepped, PDF pages read with
`pdfinfo`, CSV rows summed, figure DPI and GIF frames read with Pillow).

All 41 changed lines below are backed by a verifiable fact from the tree.

---

## 1. Corrections of stale numbers (README contradicted the tree)

| # | Location (old) | Was | Now | Evidence |
|---|---|---|---|---|
| 1 | Status badge | `status-v0.4·0_obligations·axiom_clean` | `status-v0.4.1·sorry_free·axiom_clean` | `lean/Choptuik.lean` header: "status : v0.4.1"; gap registry statuses say "partial-v04.1" |
| 2 | Status badge link | broken anchor `#-status` (no such section) | `#results-at-a-glance-v041` (new section) | — |
| 3 | Tests badge | `pytest-14/14_passing` | `pytest-65/65_passing` | `pytest --collect-only` → **65 tests collected**; `python/README.md` badge already says 65/65 |
| 4 | Python service block comment | `# 14 protocol/physics tests` | `# 65 tests: 17 service + 18 certify + 30 client` | collection per file: `test_service.py` 17, `test_certify.py` 18, `test_client.py` 30 |
| 5 | Reproducibility table | `pytest tests/ — 14 green` | `65 collected (30 client + 18 certificate + 17 service)` | same collection run |
| 6 | Monographs section | "Each volume: 20–30 pages" | "Each volume: 16–20 pages" | `pdfinfo`: Roadmap EN 18 p., Roadmap RU 20 p., Gaps EN 16 p., Gaps RU 17 p. |
| 7 | Protocol endpoints list | 6 methods (`ping`…`interval_bound`) | 7 methods — added **`certificate`** | `bridge/protocol.md` v1.1 and `bridge/README.md` "Methods (v1.1)" table: 7 endpoints incl. `certificate` |
| 8 | Lean namespace tree | ends at `Scaling`, no `Bridge/` | added `Bridge` branch: `Certificates · Generated · Discharge` | `lean/Choptuik.lean` imports all three; files exist under `lean/Choptuik/Bridge/` |
| 9 | Folder map, `data/` row | "deterministic CSVs behind every figure" | "7 deterministic CSVs (~12.9k rows)" | 7 CSV files; summed rows = 12,890 (data/README badge "~13.8k" is itself inaccurate) |

## 2. New content (what the folder actually contains, previously unreflected)

| # | Addition | Content |
|---|---|---|
| 10 | **New section "Results at a glance (v0.4.1)"** (+ TOC entry) | audited inventory table: Lean 12 modules + AxiomAudit, 0 sorry / 0 project axioms, 33 audited headline theorems (21 theory + 12 bridge — exactly the 33 `#print axioms` entries of `lean/AxiomAudit.lean`); bridge v1.1 with live certificate channel (4 kinds); 65 pytests; 7 CSVs / 12,890 rows; 8 figures @ 300 dpi + 4 GIFs (24–72 frames); 8 monograph renditions, 16–20 pages; governance row |
| 11 | Calibrated-constants table in the same section | λ₀ = 2.6745, γ = 1/λ₀ = 0.373902 (fit 0.373880, rms 2.1·10⁻³), Δ = 0.693147 = ln 2 (recovered, err 2.0·10⁻¹⁰), 2π/Δ = 9.064720 — values verified against `python/README.md` and `data/README.md` |
| 12 | **Status column in the gap-registry table** | G1–G3 🟠 partial, G4 🟢 live (v0.4.1), G5 ✅ resolved (v0.4), G6 ✅ resolved (v0.4) — taken verbatim from the `status` column of `blueprint/gap_registry.csv` |
| 13 | Roadmap section: task & milestone facts | "17 tasks: P1.1–P1.6 · P2.1–P2.6 · P3.1–P3.5" (counted in `roadmap/phase*.md`); link + summary of `roadmap/milestones.csv` (9 entries; M1.1 done, M1.2 delivered v0.4, M1.3 live v0.4.1) |
| 14 | Python service: certificate channel commands | `python -m choptuik_service.certify emit / check` — the proof-grade G4 workflow (paths verified in `certify.py`: writes `bridge/certificates/*.json` + `lean/Choptuik/Bridge/Generated.lean`) |
| 15 | Folder map enrichments | `bridge/`: "7 methods + 4 committed certificate JSONs"; `assets/`: "2 logos + 8 animated SVG banners"; `docs/`: "references (10 sources), glossary (17 terms)"; `ci/`: "axiom audit + pytest + byte-identical data regen" (3 jobs per `ci/README.md`); `roadmap/`: "17 tasks, milestone ledger" |
| 16 | Root-files note under Folder map | `CITATION.cff`, `CONTRIBUTING.md` with the four house rules (existed in the folder, never mentioned) |
| 17 | Reproducibility table: new rows | `certificates` row (byte-stable `certify emit`); stack row now mentions pytest and optional pyzmq (matches `requirements.txt`) |
| 18 | Lean build block | toolchain note: `leanprover/lean4:v4.21.0`, mathlib pinned `v4.21.0` (from `lean-toolchain` / `lakefile.toml`) |

## 3. Verified as correct and deliberately kept unchanged

- "65 pytests" in the Folder map (the only correct test count in the old README).
- "0 `sorry`, 0 project axioms, 33 headline theorems (21 theory + 12 bridge)" —
  verified: grep finds no `sorry` outside one comment in `AxiomAudit.lean`,
  no `axiom` declarations at all; `AxiomAudit.lean` lists exactly 33 entries.
- 8 figures @ 300 dpi (7 PNGs carry a 299.9994 dpi tag; `fig_architecture.png`
  has no dpi tag but is 2360×1632).
- 4 GIFs, seed 1993, 2 monographs × {RU, EN} × {DOCX, PDF}, 3-phase roadmap
  table, G1–G6 severities, CITATION/author blocks, animations HTML table.

---

## 4. Stale claims found in OTHER files (not touched — recommend fixing too)

| File | Stale claim | Actual |
|---|---|---|
| `ci/README.md` | badge `pytest-14_tests`; "14/14 green" | 65 tests |
| `lean/README.md` | badge "sorry ledger — 14 obligations" | v0.4.1 tree is sorry-free (its own table says "Proved (v0.4.1): everything") |
| `roadmap/README.md` | "M1.1 already done, the rest open" | `milestones.csv` also records M1.2 deliverable "done (v0.4)" and M1.3 partial-live (v0.4.1) |
| `data/README.md` | badge "rows ~13.8k total" | summed rows = 12,890 |
| `assets/README.md` | `scaling_animation.gif` "34 frames" | 24 frames (Pillow count) |
| `figures/README.md` | Gantt caption "14 tasks" | 17 tasks in `roadmap/phase*.md` |
| `lean/lakefile.toml` | `version = "0.3.0"` | tree is v0.4.1 |
| `CITATION.cff` | `version: 0.3.0` | tree is v0.4.1 |

## How to apply

Replace `formal_choptuik/README.md` in the repository with the `README.md`
shipped next to this file (byte-for-byte drop-in: same style, banners, links
and tone; only facts corrected and the two new blocks added).
