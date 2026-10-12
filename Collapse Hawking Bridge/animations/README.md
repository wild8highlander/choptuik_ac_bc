# animations/ — the four launch animations

Version 2.0.0 · 4 animations × 2 languages · MP4 (h264, 24 fps) + GIF

---

## Purpose

Static curves answer "what is the value"; animations answer "how does
the measurement unfold". Each of the four animations stages one
central dynamical statement of the bridge, using only committed data
and the closed forms of `../chbridge/`. They are sized for talks and
for the web companion (7.6 × 5.2–6.0 in at 110 dpi base, GIF at 96
dpi), and they deliberately avoid cinematic effects: every moving
element is a number landing on an axis.

## Catalog

| file (per language) | statement staged | frames | data source |
|---------------------|------------------|--------|-------------|
| `anim_01_evaporation` | The Page transition: mass decays along the photon-only law M(t) = M₀(1−t/t_evap)^(1/3) while the radiation entropy follows the unitary flux model — descending before the Page time, rising after; the phase caption flips exactly at τ* = 1 − 2^(−3/2) = 0.6464466 | 96 | `chbridge.page.curves()` (mid member), `chbridge.hawking` |
| `anim_02_bifurcation` | The born bifurcation assembles run by run: f~(ε) points land from large ε to small (13 committed runs), then the half-width line ε½ = 4.86e-3 fades in with the counter of runs | 96 | `c2_verdict.json` → bifurcation.rows |
| `anim_03_slowdown` | Critical slowdown: v_qmax points land along ln ε (13 runs), then the fit line v = a + b ln ε draws itself, b = −0.0334, r² = 0.71, and the 40-snapshot quantization note appears | 96 | `c2_verdict.json` → subcritical.rows + slowdown_fit |
| `anim_04_floor_law` | The floor law: three committed per-grid floors (0.0155 at N=800, 8.575e-3 at N=1600, 4.245e-3 at N=3200) land one after another, then the 12/N guide line sweeps the axis | 96 | c1/c3b verdicts (F-2 values), constants.py Part C |

## Layout

```text
animations/
├── en/
│   ├── anim_01_evaporation.mp4   anim_01_evaporation.gif
│   ├── anim_02_bifurcation.mp4   anim_02_bifurcation.gif
│   ├── anim_03_slowdown.mp4      anim_03_slowdown.gif
│   └── anim_04_floor_law.mp4     anim_04_floor_law.gif
├── ru/   (same eight files, Russian labels)
└── README.md
```

## Rendering facts

* MP4: h264 (ffmpeg 7.1), 24 fps, bitrate 1600 kbps — plays natively
  in every browser and in LibreOffice/PowerPoint.
* GIF: 16 fps, 96 dpi — no codec needed, slightly quantized color;
  intended as the universal fallback, not the master.
* Duration ≈ 4 s each; the GIF runtime is ~6 s due to the 16 fps
  mapping of the same 96-frame timeline.
* Total size ≈ 1.8 MB for all eight pairs — small enough to live
  inside the package ZIP and inside talk decks without conversion.

## Physics honesty

1. `anim_01` visualises the **model** of `../chbridge/page.py` (the
   piecewise unitary flux model with the Haar-verified crossover), not
   a dynamical simulation of evaporation. The photon-only law and its
   idealisation status are documented in `../docs/methods.md`.
2. `anim_02` and `anim_03` stage *committed rows only* — the points
   you see land are the rows of the verdict files, junk rows excluded
   from the frame exactly as they are excluded from the fits (but kept
   in the verdicts).
3. `anim_04` overlays the 12/N guide as a summary of three measured
   floors; it is a fit of the committed ladder, not a theoretical
   derivation (see theorem T5 status in `../monograph/`).

## Regeneration

```bash
python3 scripts/make_animations.py --all           # 8 pairs, ~90 s
python3 scripts/make_animations.py --lang en --only anim_02_bifurcation
```

Requires ffmpeg on PATH for MP4 (GIFs render via Pillow regardless).
Output console tail: `8 animations rendered (4 x 2 lang, mp4+gif)`.

## FAQ

**Q: Why 96 frames?** Long enough for the eye to follow each point
landing, short enough for a 4-second slot in a talk; 96 = 4 s × 24 fps
exactly.

**Q: Why is the GIF slower than the MP4?** PillowWriter caps the
frame rate at 16 fps to keep GIF size and palette sane; the timeline
is identical, only the wall-clock pacing differs.

**Q: Can I get webm/HEVC?** The web companion serves the MP4s
directly; conversion is one ffmpeg command away
(`ffmpeg -i a.mp4 -c:v libvpx-vp9 a.webm`).

**Q: Why does anim_01 show the same curve for every ensemble member?**
It stages the **mid** member; the other two members differ only in
normalisation (f~), which would clutter the frame. The full three-
member comparison is figure `hq_16` in `../figures_hires/`.

**Q: Are the animations deterministic?** Yes — `FuncAnimation` over
fixed committed arrays, no RNG anywhere in the pipeline.

## See also

* `../figures_hires/README.md` — the 600 dpi still catalog.
* `../chbridge/page.py` — the model behind anim_01.
* `../docs/methods.md` — sampling and idealisation notes.
* `../results/RESULTS.md` — the ledger every frame is built from.

## Краткое резюме (RU)

Четыре запускные анимации в двух языках (MP4 h264 + GIF): испарение с
переходом Пейджа, сборка бифуркации рождения по committed-строкам,
критическое замедление с прорисовкой фита и закон пола (13±1)/N. Только
зафиксированные данные, без RNG, полная детерминированность; суммарно
1.8 МБ. Регенерация одной командой; физические допущения (фотонная
идеализация, модель потока энтропии) помечены и задокументированы.
