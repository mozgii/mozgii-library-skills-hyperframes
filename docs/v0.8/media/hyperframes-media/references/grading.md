---
title: Grading footage with media-treatment
author: MOZGII, Inc.
lang: en
---

# Grading footage with media-treatment

Grading footage with `npx hyperframes media-treatment` fixes exposure, colour casts and saturation, and adds looks
such as grain, vignette or a LUT, in a way the renderer reproduces exactly. The result is a `data-color-grading`
attribute on the `<img>` or `<video>`.

## Grading families

Grading families are the groups of controls the command exposes; `--capabilities --json` prints them and
`--capability <id> --json` prints one family's controls and ranges.

| Family | Controls |
|---|---|
| `correction` | exposure, tonal balance, colour casts, saturation |
| `wheels` | shadow, midtone and highlight colour wheels |
| `curves` | master and per-channel curves as `[input, output]` points |
| `hue-curves` | hue-selective curves as `[hueDegrees, delta]` points |
| `secondary` | up to four HSL selections with bounded correction |
| `finishing` | vignette and deterministic film grain |
| `presets`, `palettes` | tested starting points and named palettes |
| `lut` | your own 3D `.cube` LUT |
| `animation` | custom properties a timeline may tween |
| `overlays` | registry blocks for HUDs, light leaks, flashes, freeze frames |

## The grading loop

The grading loop is measure, propose, compare, apply.

```bash
npx hyperframes media-treatment --selector '#hero' --analyze --json          # measured exposure and cast
npx hyperframes grade-compare --for frame.png --grades grades.json --out grades.png
npx hyperframes media-treatment --selector '#hero' --grading grade.json --dry-run --json
npx hyperframes media-treatment --selector '#hero' --grading grade.json --apply
```

`grades.json` is an array of labelled grading blocks, compared against a neutral baseline:

```json
[{ "label": "warm", "grading": { "adjust": { "temperature": 0.2, "contrast": 0.1 } } }]
```

Pick one intent per clip (fix it, or stylise it). Up to 16 candidates fit one comparison sheet.

## Animating a grade

A grade animates through its custom properties on the composition timeline. Write the starting value into the
element's inline `style`, then tween with finite `tl.to()` calls on properties such as `--hf-color-grading-intensity`,
`--hf-color-grading-blur` or `--hf-color-grading-exposure`. `--capability animation --json` lists the full set and
their ranges.

## Grading limits

Grading limits are worth knowing before promising a look. A treatment applies to the whole element in SDR, so it
cannot blur one region such as a face; mask a wrapper for that. HDR media keeps its range only when no SDR-only
treatment is applied. Generated `.cube` files that only encode exposure or white balance are unnecessary: use the
correction family.

## Looks and effects on footage

Looks and effects on footage live in the `effects` section of the same `data-color-grading` attribute, beside
`adjust` (corrections) and `details` (grain and vignette): blur, pixelate and bloom; scanlines, digital glitch, CRT
curvature, tape damage, channel separation and film artifacts; halftone, two-ink print, ordered dither and mono
screen; ASCII, engraving, crosshatch and Kuwahara paint. List the current set with `--capabilities --json` rather
than from memory. Pixelate a region (an email address in a screen recording) by stacking a second copy of the clip,
clipped to that region with `clip-path`, carrying `{"intensity":1,"effects":{"pixelate":0.5}}`.
