# animations/ — the four launch animations of the DSI laboratory

Four animations × two languages (en, ru), each delivered as **MP4**
(h264, 24 fps) and **GIF**, generated deterministically by
[`scripts/make_animations.py`](../scripts/make_animations.py) from the
committed verdicts in [`results/`](../results/) — the script invents
nothing.

## The four

| animation | what it shows | data source |
|-----------|---------------|-------------|
| `anim_01_convergents` | the continued-fraction ladder of the measured c_K3: convergents 1/24 → 1/25 → **9/224** landing on the observation line (+0.0025 %) | `results/exp2_dsi4.json` |
| `anim_02_ladder` | the e-ladder theorem: the 5/7 free-scalar floor, theorem A (e ≥ 1), the trimmed-tree points 1 + 2/n → 1 (theorem B), theorem C (F = 2n) | `results/exp7_e1_threshold.json` |
| `anim_03_census` | the {7,3} tiling of the Klein quartic drawing itself: V = 56 triangles, E = 84 edges, F = 24 heptagons, and the valence identity 7F = 3V = 2E = 168 | `results/exp6_census_224.json` |
| `anim_04_overtones` | the falsifiable overtone law \|Δf_n\|/f_n = const = 8.3857e-5 of the GW150914 QNM catalogue, with the 0.84σ Cosmic-Explorer detectability note | `results/exp4_qnm.json` |

## Layout

```text
animations/
  en/anim_01_convergents.mp4 + .gif   anim_02_ladder ... anim_04_overtones
  ru/anim_01_convergents.mp4 + .gif   ... (полный зеркальный набор)
```

## Regenerate

```bash
cd dsi_lab
python3 scripts/make_animations.py --all                  # en + ru
python3 scripts/make_animations.py --lang ru --only anim_03_census
```

Requires ffmpeg for the MP4s (the GIFs render with Pillow alone).
