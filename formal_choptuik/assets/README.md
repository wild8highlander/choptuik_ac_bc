<p align="center">
  <img src="../assets/banners/banner_data.svg" alt="assets" width="100%">
</p>

# assets/ — the identity of formal_choptuik

![svg](https://img.shields.io/badge/SVG-animated·SMIL-9B8CDE?style=flat-square)
![gif](https://img.shields.io/badge/GIF-4_animations-E8B44A?style=flat-square)
![palette](https://img.shields.io/badge/palette-deep_space·gold·violet·cyan-4CC9F0?style=flat-square)
![deps](https://img.shields.io/badge/dependencies-zero-8FB7A4?style=flat-square)

Logos, banners and motion assets.  All SVGs animate via SMIL — no
JavaScript, no external fetches, GitHub-safe.  The GIFs regenerate from
seed 1993 via [`python/scripts/generate_animations.py`](../python/scripts/generate_animations.py).

## Logos — `logos/`

| File | Use |
|---|---|
| [`logo_formal_choptuik.svg`](logos/logo_formal_choptuik.svg) | horizontal logo: rotating accretion disk, λ on the horizon, orbiting photon |
| [`avatar_formal_choptuik.svg`](logos/avatar_formal_choptuik.svg) | 512×512 square — repository/social avatar |

## Banners — `banners/`

| File | Use |
|---|---|
| [`banner_header.svg`](banners/banner_header.svg) | hero banner: starfield, infalling waveform, black hole, title |
| [`banner_roadmap.svg`](banners/banner_roadmap.svg) | three phase chips with sweeping scanline |
| [`banner_gaps.svg`](banners/banner_gaps.svg) | severity chips (Blocker → Low) with staggered pulse |
| [`banner_lean.svg`](banners/banner_lean.svg) | namespace banner with λ/∀ watermarks and typing caret |
| [`banner_monographs.svg`](banners/banner_monographs.svg) | floating volumes I & II |
| [`banner_data.svg`](banners/banner_data.svg) | self-drawing scaling curve, γ = 1/λ₀ |
| [`divider_photon.svg`](banners/divider_photon.svg) | thin divider, photons both ways |
| [`divider_wave.svg`](banners/divider_wave.svg) | breathing sine divider |

## Animations — `gifs/`

| File | Frames | Shows |
|---|---|---|
| [`collapse_animation.gif`](gifs/collapse_animation.gif) | 48 | three families around the threshold; horizon forms in the supercritical panel |
| [`echoing_animation.gif`](gifs/echoing_animation.gif) | 72 | profile drift by Δ per period + echo-phase dial |
| [`scaling_animation.gif`](gifs/scaling_animation.gif) | 24 | the scaling law assembled run by run, γ settling to 0.3739 |
| [`attractor_animation.gif`](gifs/attractor_animation.gif) | 64 | trajectories peel off the codimension-one attractor; black hole at the end |

Palette (dark cosmic): background `#0F172A`, gold `#E8B44A`, violet
`#9B8CDE`, cyan `#4CC9F0` — a continuation of the parent repository's
"Ink & Gold" identity into deep space.

> [!NOTE]
> Frame counts are as stored in the committed GIFs (verified by
> regeneration, md5-identical to the committed files): Pillow merges the
> ten trailing hold frames of `scaling_animation.gif` into a single
> longer final frame (600 ms), so the generator's 24 data frames + 10
> hold frames are stored as 24 frames.

<p align="center">
  <img src="banners/divider_photon.svg" alt="" width="100%">
</p>
