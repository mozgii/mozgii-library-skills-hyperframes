---
title: Website capture and brand notes
author: MOZGII, Inc.
lang: en
---

# Website capture and brand notes

Website capture with `npx hyperframes capture` loads a live page, scrolls it, and writes screenshots, downloaded
assets and extracted design data into a normal HyperFrames project. Brand notes (`DESIGN.md`) condense that data into
a cheat sheet for the rest of the work.

## Contents

The sections of this page:

- Capture flags
- Capture output files
- Reading order and working notes
- Rich captures with many images
- DESIGN.md template
- Overview
- Colors
- Typography
- Elevation
- Components
- Do's and Don'ts
- Brand token rules

## Capture flags

Capture flags bound time and choose what is fetched.

```bash
npx hyperframes capture https://example.com -o product-video/capture --json
npx hyperframes capture https://example.com --skip-assets          # no image or SVG download
npx hyperframes capture https://example.com --skip-vision          # no optional AI image captions
npx hyperframes capture https://example.com --max-screenshots 12
npx hyperframes capture https://example.com --timeout 60000        # navigation only, ms
npx hyperframes capture https://example.com --capture-budget 90000 # work after navigation (default 120000 ms)
npx hyperframes capture --video product-video/capture --list       # list the page's videos; then --index N
HYPERFRAMES_CAPTURE_PROXY=http://127.0.0.1:3128 npx hyperframes capture https://example.com
```

Vision captions in `asset-descriptions.md` appear only when a vision API key (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`
or `GOOGLE_API_KEY`) is set. Videos on the page are not downloaded by default.

## Capture output files

Capture output files and what to take from each:

| File | Holds | Take |
|---|---|---|
| `screenshots/scroll-NNN.png` | viewport captures down the page, about 30% overlap | mood, layout, light or dark ground |
| `screenshots/full-page.png` | one 1x plate of the whole page after the scroll pass, sticky elements made static | camera moves down the page (skipped above 16384 px tall) |
| `extracted/tokens.json` | colours, font families and weights, section, heading and CTA counts | the palette and type |
| `extracted/visible-text.txt` | text lines tagged `[h1]`, `[p]`, `[a]` | key messages and exact numbers |
| `extracted/asset-descriptions.md` | one line per downloaded asset | the menu of visuals |
| `extracted/animations.json` | scroll triggers, marquees, canvas or WebGL, named CSS animations | motion the brand already uses |
| `extracted/lottie-manifest.json`, `video-manifest.json` | embedded animations and videos with previews | reusable motion and footage |
| `extracted/shaders.json` | the page's GLSL | gradient colours and noise to echo |
| `extracted/page.html` | the page, with every `@font-face` rule kept | font files and their `unicode-range` subsets |

A push-in that goes beyond 1:1 on the full-page plate needs a separate 2x capture of just that region.

## Reading order and working notes

Reading order and working notes keep context small: read a file, write one or two sentences about it, move on. The
notes are the working memory once the raw file content leaves context. Read the hero screenshot first, then the rest
of the scroll set, then tokens, visible text and asset descriptions, then the optional manifests. Open individual
assets only when building the beat that uses them.

## Rich captures with many images

Rich captures with 30 or more images are catalogued once: view every image and SVG and write one line each (file name,
what it shows, dominant colours, approximate size), then use that catalog for the rest of the work. A sub-agent can do
this pass in parallel.

## DESIGN.md template

The DESIGN.md template has six sections and stays under 100 lines.

```markdown
# Design System

## Overview
Three or four factual sentences: layout patterns, colour strategy, type tone, overall feel.

## Colors
- **Surface**: `#0B0D12` deep ink background
- **Content**: `#F4F1EA` warm white text
- **Accent**: `#FF5A36` coral for calls to action and highlights
- **Quiet border**: `#2A2E37` dividers and card edges

## Typography
- **Display**: Playfair Display, italic, for headline statements
- **Sans**: Inter 400/600/800 for body and UI
- **Mono**: JetBrains Mono for labels, uppercase, tracking 0.12em

## Elevation
One paragraph: borders, shadows, glass or flat colour shifts, with exact values.

## Components
- **Bento grid**: cards with 24 px radius, 1 px borders at 8% white
- **Logo marquee**: slow horizontal ticker of monochrome logos

## Do's and Don'ts
### Do's
- Separate sections with thin borders rather than colour blocks
### Don'ts
- Do not use bright solid backgrounds
- Do not use standard drop shadows; use soft radial glows
```

Leave out a style prompt, an assets list and a motion section: the storyboard covers those.

## Brand token rules

Brand token rules stop common misreadings of `tokens.json`:

- Use exact hex values from the tokens; never approximate.
- For the accent, choose the captured colour that appears in the most roles; default link blue `#0000EE` and status
  reds or greens never qualify.
- A monospace face found in the capture fills the mono role. Icon fonts never set text.
- Copy font files along with their `@font-face` rules (`unicode-range` included) and name each file by family, weight
  and style; otherwise an upright "Regular" and an italic "Regular" overwrite each other.
- For a dark brand on a template with a light ground, swap ground and ink.
