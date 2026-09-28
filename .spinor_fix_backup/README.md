# .spinor_fix_backup

Backup snapshot taken immediately before applying the spinor-verification
fix campaign: corrected enhanced-verification code, regenerated monograph
renderings, and the updated census experiment. The folder preserves the
*pre-fix* state of each affected file so that the changes can be audited by
direct comparison with the live copies.

## What is inside

| Path (inside this backup) | Live counterpart | Contents of the backup copy |
|---------------------------|------------------|------------------------------|
| `python/src/core/enhanced_verification.py` | `python/src/core/enhanced_verification.py` | Pre-fix numerical verification of the enhanced claims (4D, Kähler, Tyukovsky, Einstein GR results) |
| `python/src/verification/verify_enhanced.py` | `python/src/verification/verify_enhanced.py` | Pre-fix extended verification suite |
| `python/src/visualization/plots.py` | `python/src/visualization/plots.py` | Pre-fix plotting layer |
| `python/tests/test_choptyuk.py` | `python/tests/test_choptyuk.py` | Pre-fix test suite |
| `interactive-viz/src/lib/compute.ts` | `interactive-viz/src/lib/compute.ts` | Pre-fix client-side computation module |
| `interactive-viz/src/app/enhanced/page.tsx` | `interactive-viz/src/app/enhanced/page.tsx` | Pre-fix enhanced dashboard page |
| `dsi_lab/exp6_census_224.py` | `dsi_lab/exp6_census_224.py` | Pre-fix census experiment (denominator 224) |
| `dsi_lab/results/exp6_census_224.json` | `dsi_lab/results/exp6_census_224.json` | Pre-fix committed experiment result |
| `docs/monograph/` (9 files) | `docs/monograph/` | Pre-fix enhanced monograph renderings: DOCX + PDF (EN/RU), LaTeX sources (EN/RU), `verification_results_enhanced.json` |

### Full backup file list

```
docs/monograph/Choptyuk_Braking_Monograph_EN_Enhanced.docx
docs/monograph/Choptyuk_Braking_Monograph_EN_Enhanced.pdf
docs/monograph/Choptyuk_Braking_Monograph_RU_Enhanced.docx
docs/monograph/Choptyuk_Braking_Monograph_RU_Enhanced.pdf
docs/monograph/monograph_enhanced_en.tex
docs/monograph/monograph_enhanced_ru.tex
docs/monograph/verification_results_enhanced.json
dsi_lab/exp6_census_224.py
dsi_lab/results/exp6_census_224.json
interactive-viz/src/app/enhanced/page.tsx
interactive-viz/src/lib/compute.ts
python/src/core/enhanced_verification.py
python/src/verification/verify_enhanced.py
python/src/visualization/plots.py
python/tests/test_choptyuk.py
```

## How to use

Nothing here is executed or imported — it is a frozen snapshot for auditing:

```bash
# compare a backed-up file against the fixed live copy
diff .spinor_fix_backup/python/src/verification/verify_enhanced.py \
     python/src/verification/verify_enhanced.py

# see everything that changed in the campaign
git diff --no-index .spinor_fix_backup/python python/src
```

The authoritative verification always runs from the live trees:

```bash
cd python && python run.py --mode verify --non-interactive
cd dsi_lab && python3 run_all.py 6
```

## Notes

- This folder is kept for provenance only: do not add it to `PYTHONPATH`,
  do not import from it, and do not run its copies — they represent the
  state *before* the spinor corrections and contain the known discrepancies
  that were subsequently fixed.
- The backup mirrors the original directory layout (`python/…`,
  `interactive-viz/…`, `dsi_lab/…`, `docs/monograph/…`) so file-by-file
  diffs apply cleanly.
- If the fix campaign is ever re-examined, start from the JSON results here
  versus the current results — that comparison documents exactly which
  numbers moved and by how much.
