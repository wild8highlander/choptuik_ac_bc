# logo/ — the DSI laboratory identity

Everything here is generated deterministically by
[`scripts/make_logo.py`](../scripts/make_logo.py) — no external assets, no
fonts embedded by hand, the emblem is drawn with the package's own
mathematics (the {7} heptagon and its {7,3} face chords, the convergent
ladder 1/24 → 1/25 → 9/224, and the e-ladder 5/7 → 1 → 2).

## Files

| file | purpose |
|------|---------|
| `dsilab_logo_light.png` / `.svg` | banner logo for light theme (README, monographs) |
| `dsilab_logo_dark.png` / `.svg` | banner logo for dark theme |
| `dsilab_avatar_light.png` | square 1024 px repository avatar, light |
| `dsilab_avatar_dark.png` | square 1024 px repository avatar, dark |

The banner PNGs are rendered at 600 dpi (5760 × 2760) with transparent
background; the SVGs carry text as paths so they render identically
anywhere. The README displays them theme-aware:

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="logo/dsilab_logo_dark.png">
  <img src="logo/dsilab_logo_light.png" alt="DSI Lab — logo" width="100%">
</picture>
```

## Regenerate

```bash
cd dsi_lab
python3 scripts/make_logo.py
```
