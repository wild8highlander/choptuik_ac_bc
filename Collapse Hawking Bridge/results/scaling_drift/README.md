# results/scaling_drift — the resolution-drift law (campaign C6)

![campaign](https://img.shields.io/badge/campaign-C6_drift-8C6D1F)
![theorem](https://img.shields.io/badge/theorem-T10_parabolic--tension-1A1A24)
![status](https://img.shields.io/badge/lemmas-machine--verified-brightgreen)
![negatives](https://img.shields.io/badge/A*_inf-not_claimable-8C3A2F)

The results folder of **campaign C6** — the package's answer to the
question *why one formula gives different values when the scale is
rescaled*. The classification formula ("supercritical iff an apparent
horizon forms") necessarily returns different thresholds at different
grid resolutions, because grid-sampled **parabolic structures stretch
and compress under the curvature of their tension**: sampling flattens
the compaction peak by exactly `kappa h^2/8` and shortens the chord
chain against the continuum arc.

## Contents

- **[REPORT.md](REPORT.md)** — the verification report: the two exact
  lemmas, the measured `p_eff` trajectory, the channel decomposition,
  and the two honest negatives (no `A*_inf`; the exact channel is
  sub-dominant). English body, Russian summary at the end.
- **figures/** — eight PNG (two types × `en/ru` × `light/dark`,
  300 dpi), regenerable by `scripts/make_c6_figures.py`:
  - `drift_ladder_*` — observed per-doubling drift vs the T10 exact
    channel vs the rejected two-term fit, with `1/N` and `1/N^2` guides;
  - `parabola_tension_*` — the worst-alignment chord family on a
    parabola and the exact chord sag `kappa h^2/8`.

## Where the law lives

| artifact | role |
|---|---|
| `campaigns/reference/c6_drift_verdict.json` | the machine verdict — the law |
| `campaigns/reference/c6_drift_channels.csv` | per-grid channel decomposition |
| `campaigns/reference/c6_parabola_check.csv` | machine-precision lemma checks |
| `docs/scaling_law.md` | the full derivation of theorem T10 |
| `tests/test_campaigns.py` (C6 block) | pytest pins of the verdict |

The inputs of C6 are committed artifacts only (`a_star_ladder.csv`,
`profiles_sub_supercritical.json`, `subcritical_scan.csv`); the run is
deterministic and needs no engine march (~2 s):

```bash
python3 campaigns/run_c6_drift.py
python3 scripts/make_c6_figures.py
```

## Status vocabulary

- the two lemmas are **exact** (closed-form statements, machine-verified
  to `1.9e-16` / `2.0e-9` relative);
- the threshold-shift corollary (T10) is **analytically derived** with
  **measured** coefficients (`kappa* = 2728.60`, `s = 413.8`);
- the dominant-channel attribution (march-error amplification under
  near-critical lingering) is a **labeled hypothesis** — it shapes the
  AMR engine-upgrade target on the roadmap, and nothing in the package
  depends on it as a fact.

## See also

- [docs/scaling_law.md](../../docs/scaling_law.md) — the theory.
- [results/RESULTS.md](../RESULTS.md) — the headline ledger (row 18).
- [independent_verification/RESULTS.md](../../independent_verification/RESULTS.md)
  — the audit findings (F-1) that motivated the question.

## Краткое резюме (Russian)

Папка результатов кампании C6 — закона дрейфа порога с разрешением.
Теорема T10: одна и та же формула классификации обязана давать разные
значения на разных сетках, потому что дискретизованные параболические
структуры растягиваются и сжимаются под действием кривизны своего
натяжения (пик занижен ровно на `kappa h^2/8`, ломаная короче дуги).
Здесь: отчёт REPORT.md (EN + краткое резюме RU) и восемь фигур
(2 типа × en/ru × light/dark). Закон живёт в
`campaigns/reference/c6_drift_verdict.json`; теория — в
`docs/scaling_law.md`; тесты — в блоке C6 файла `tests/test_campaigns.py`.
