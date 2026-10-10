# data/ — derived tables (byte-deterministic)

Rebuilt from the committed verdicts by `scripts/rebuild_data.py`
(pinned byte-identical by a test).  Nothing here is hand-edited.

| file | source | content |
|---|---|---|
| `bridge_master.csv` | `qhb.bridge` | 15 rows x 23 columns (3 members x 5 scales) |
| `scale_ladder_density.csv` | `qhb.ladder` | the binding-furnace column (rho/rho_P) |
| `scale_ladder_temperature.csv` | `qhb.ladder` | T_H vs both contact temperatures |
| `scale_ladder_gaps.csv` | `qhb.ladder` | frequency anchors (Lambda_QCD, T_QCD, CMB, Planck) |
| `qhb_constants.csv` | `qhb.ladder` | the dimensionless registry |
| `gap_scan_window.json` | C1 | the committed window + the wing |
| `gap_per_sector.json` | C1 | B2 of the three septinial sectors |
| `trap_grid.csv` / `trap_lyapunov.json` / `gascheau.json` | C2 | the escape map, bound chaos, T4 |
| `wu_residual_grid.csv` / `wu_anchor.json` / `wu_eta_comparison.json` | C3 | the door map |
| `floor_ladder.csv` / `floor_law.json` | C4 | the detector ladder |
| `drift_ladder.csv` / `drift_law.json` | C5 | the drift ladder + channel share |
| `qhb_summary.json` | all | the one-page machine summary |


## v1.1.0 tables

- `mapping_branches.csv` — the C6 three-branch table (per-branch
  honesty tags live in the verdict);
- `anharmonic_free.csv`, `anharmonic_grid.csv`,
  `anharmonic_boundary.json` — the C7 sigma-ladder, the sealing grid
  and the V0* boundary block;
- `pairwise_residual.csv`, `pairwise_checks.json` — the C8 pairwise
  grid (with the linear-model comparison column) and the machine
  checks (X1/X2, RK4 ladder, mpmath).
