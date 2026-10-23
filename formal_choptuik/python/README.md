<p align="center">
  <img src="../assets/banners/banner_data.svg" alt="data and figures" width="100%">
</p>

# python/ — the numerical wing

![Python](https://img.shields.io/badge/Python-3.10+-4CC9F0?logo=python&logoColor=white&style=flat-square)
![numpy](https://img.shields.io/badge/numpy-deterministic-4CC9F0?logo=numpy&logoColor=white&style=flat-square)
![tests](https://img.shields.io/badge/pytest-14/14_passing-8FB7A4?style=flat-square)
![seed](https://img.shields.io/badge/seed-1993-E8B44A?style=flat-square)
![pyzmq](https://img.shields.io/badge/pyzmq-optional_extra-9B8CDE?style=flat-square)

The computational service the Lean side drives: a calibrated linear-mode
model of the DSS critical solution, a genuine eigensolve of the
linearized operator, directed-rounding interval arithmetic, and a
JSON-over-ZMQ server implementing [`bridge/protocol.md`](../bridge/protocol.md).

> [!IMPORTANT]
> **Honest caveat.**  The mode model is *calibrated* to the published
> Choptuik constants (λ₀ = 2.6745, γ = 1/λ₀, Δ = ln 2) — it is a
> laboratory for the verification workflow and the source of the
> committed datasets, **not** a solver of the full Einstein–scalar
> system.  The full system is precisely what the Lean roadmap formalizes.

## Layout

```
python/
├── choptuik_service/            the service package
│   ├── evolver.py               mode model, scaling fit, echo recovery
│   ├── spectrum.py              block-matrix operator + eigensolve
│   ├── interval_checks.py       outward-rounded Interval (gap G5)
│   └── server.py                pure dispatcher + ZMQ REP loop
├── scripts/
│   ├── generate_data.py         -> data/*.csv
│   ├── generate_figures.py      -> figures/*.png (dark/light × en/ru)
│   ├── generate_animations.py   -> assets/gifs/*.gif
│   └── generate_architecture.py -> fig_architecture.png
├── tests/test_service.py        14 regression-locked tests
└── requirements.txt
```

## Quickstart

```bash
pip install -r requirements.txt     # pyzmq commented: enable for the bridge
python -m pytest tests/ -v          # protocol + physics regressions
python scripts/generate_data.py     # byte-identical CSVs on a given numpy
python choptuik_service/server.py   # serve tcp://127.0.0.1:5557
python choptuik_service/server.py --selftest   # one ping, no socket
```

## What the service guarantees

| Guarantee | Mechanism |
|---|---|
| single unstable eigenvalue, echo spacing `2π/Δ` | `spectrum.compute_spectrum` — a real 15×15 eigensolve, not a lookup |
| γ_fit = 0.37388 vs γ_ref = 0.37390 | `fit_scaling_exponent` on the seeded supercritical family |
| Δ recovered from a raw amplitude series | autocorrelation peak, `echo_period_from_profile` |
| strict enclosures | `Interval` with `math.nextafter` outward rounding |
| protocol cannot silently drift | `tests/test_service.py` locks every endpoint |

## Verified numbers (this build)

| Quantity | Value |
|---|---|
| λ₀ | 2.6745 (single unstable mode ✓) |
| γ = 1/λ₀ | 0.373902 (fit: 0.37388, rms 2.1·10⁻³) |
| Δ | 0.693147 = ln 2 (recovered: 0.693147) |
| echo spacing error | 2.0·10⁻¹⁰ |

<p align="center">
  <img src="../assets/banners/divider_photon.svg" alt="" width="100%">
</p>
