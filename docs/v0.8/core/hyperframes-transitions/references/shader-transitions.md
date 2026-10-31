---
title: HyperFrames shader transitions
author: MOZGII, Inc.
lang: en
---

# HyperFrames shader transitions

The `@hyperframes/shader-transitions` package (MIT, version 0.8.223) supplies HyperFrames' shader transitions. Its
`init()` samples each scene while it animates, blends the samples in a fragment shader on a WebGL canvas, and gives
back a GSAP timeline, so a scene keeps moving while it transitions. Where WebGL is missing, the timeline simply plays
without the shader.

## Contents

The sections of this page:

- Loading the package
- The shaders
- Init options
- Capture rules for shader films
- Choosing a shader
- Visual pattern warning

## Loading the package

Loading the package works from a CDN script (global `HyperShader`) or npm.

```html
<script src="https://cdn.jsdelivr.net/npm/@hyperframes/shader-transitions@0.8.223/dist/index.global.js"></script>
```

```bash
npm install @hyperframes/shader-transitions
```

```js
import { init, SHADER_NAMES } from "@hyperframes/shader-transitions";
```

Distribution files: `dist/index.js` (ESM), `dist/index.cjs` (CommonJS), `dist/index.global.js` (script tag).

## The shaders

The shaders available in the package, by name:

| Shader | Look |
|---|---|
| `domain-warp` | the image bends like liquid along a noise field, edge glowing |
| `ridged-burn` | the old scene burns away along ridges, throwing sparks and a hot glow |
| `whip-pan` | a sideways streak, as if the camera swung fast |
| `sdf-iris` | a circle opens onto the new scene, its rim lit |
| `ripple-waves` | rings spread out from the middle like a pond |
| `gravitational-lens` | space bends into a well, colours fringing at the edge |
| `cinematic-zoom` | a rush toward the centre with colour fringes on the blur |
| `chromatic-split` | red, green and blue drift apart outward from the middle |
| `glitch` | blocks jump out of place over scanlines |
| `swirl-vortex` | the frame twists into a spiral, roughened by noise |
| `thermal-distortion` | a heat haze climbs from the bottom edge |
| `flash-through-white` | the frame burns out to white and the next scene appears |
| `cross-warp-morph` | both scenes melt into each other through a noise pattern |
| `light-leak` | warm light floods in from the side with a lens flare |

`SHADER_NAMES` exports this list for validation.

## Init options

Init options configure scenes and transition times.

| Option | Required | Meaning |
|---|---|---|
| `bgColor` | yes | fallback background hex for capture; use the canvas background |
| `accentColor` | no | hex for shader glows |
| `scenes` | yes | the id of every scene element, in playing order |
| `transitions` | yes | `{ time, shader, duration = 0.7, ease = "power2.inOut" }` per seam |
| `timeline` | no | an existing GSAP timeline to add transitions to |
| `compositionId` | no | override the `data-composition-id` used for registration |
| `previewCaptureFps` | no | preview capture samples per transition second (default 30); renders composite per frame |

## Capture rules for shader films

Capture rules for shader films exist because scenes are captured to textures (natively with Chrome's HTML-in-canvas
when available, otherwise html2canvas), and canvas drawing does not match CSS exactly.

1. No `transparent` keyword in gradients; it interpolates through black. Write the colour at zero alpha:
   `rgba(200,117,51,0)`.
2. No gradient backgrounds on elements thinner than 4 px; use a solid colour on thin rules.
3. Prefer literal colours over `var()` on elements visible during capture.
4. Mark decorative elements that cannot follow these rules with `data-no-capture`; they stay live but are left out of
   the texture.
5. Keep gradient opacity at 0.15 or above.
6. Give every scene an explicit `background-color` and pass the same value as `bgColor`, or textures render black.
7. Use shader transitions for every seam in that composition; do not mix them with DOM-based CSS scene swaps.

## Choosing a shader

Choosing a shader follows the film's energy and how much attention the seam deserves. A shader film has a shader on
every seam, because `init()` throws unless `scenes.length === transitions.length + 1`, so the choice is which shader
goes where: keep the loud ones for the peaks, never two loud ones in a row, and give the seams between them a quiet
shader. When only one moment deserves a shader, build the rest in CSS and take that moment from the registry
(`npx hyperframes catalog --tag transition --json`).

| Shader | Energy | Duration | Use when | Avoid |
|---|---|---|---|---|
| `cinematic-zoom` | medium-high | 0.4 to 0.6 s | revealing the product or the hero number | fast-cut runs |
| `cross-warp-morph` | medium | 0.5 to 0.8 s | related scenes in dark, premium pieces | data-heavy pieces, light palettes |
| `domain-warp` | low-medium | 0.6 to 1 s | data flow, simulation, continuous change | corporate clean brands |
| `gravitational-lens` | medium-high | 0.6 to 1 s | dramatic, space or depth themes | casual tone |
| `flash-through-white` | high | 0.2 to 0.4 s | a beat drop, a reveal | calm pieces |
| `glitch`, `chromatic-split` | high | 0.15 to 0.4 s | tech, tension, error moments | luxury, wellness |
| `light-leak`, `thermal-distortion` | low-medium | 0.6 to 0.9 s | warm, nostalgic, premium | data and tech |
| `whip-pan` | medium-high | 0.3 to 0.5 s | editorial pace, sideways story moves | slow pieces |

## Visual pattern warning

The visual pattern warning: avoid transitions that show repeating geometry (tile grids, hexagon cells, even dot
arrays, evenly spaced circles). The eye reads the grid at once and it looks cheap. Organic noise (FBM, domain warping)
works because it is irregular.
