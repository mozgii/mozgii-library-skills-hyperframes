---
title: Layout and safe areas for HyperFrames video
author: MOZGII, Inc.
lang: en
---

# Layout and safe areas for HyperFrames video

Layout for video differs from layout for the web: the frame is fixed, viewers cannot scroll or zoom, and phones show
the frame small. This page covers sizing, safe areas, frame composition and the layout audit's opt-out attributes.

## Video sizes are larger than web sizes

Video sizes for text and lines are two to three times their web values, because a 1080p frame is often watched on a
phone. Measured on a 1920×1080 canvas:

| Element | Web habit | Video |
|---|---|---|
| Headline | 32-48 px | 64-120 px (4-9% of frame height) |
| Body text | 14-16 px | 28-42 px |
| Data labels | 12 px | 18-24 px, never under 28 px if it must be read |
| Borders and rules | 1 px | 2-4 px |
| Padding | 16-32 px | 60-140 px |
| Decorative opacity | 3-8% | 12-25% |

`check` raises `text_below_floor` when text smaller than 2.6% of the frame's shorter edge (28 px at 1080) stays on
screen for 0.5 s or more.

## Safe areas

Safe areas keep content clear of the edges that platforms crop or cover. Keep all content inside the 90% action-safe
box and key text and captions inside the 80% title-safe box. Studio draws these guides; never add guide elements to
the composition. Vertical platforms also cover the bottom and right edge with buttons and captions: platform margins
are in `platform-formats`.

## Frame composition

Frame composition is how elements share the frame.

- Give the eye at least two focal points and a path between them.
- Anchor content to edges or a grid (left column, top bar, split frame) rather than floating it in the centre.
- Fill the frame: a hero line can take 60-80% of the width; quiet lines sit at 2.5-4% of frame height next to it.
- Tint neutrals toward the brand hue; a flat grey reads as unfinished.
- Avoid full-screen linear gradients on dark grounds: H.264 bands them. Use a radial glow or a solid with grain.

## Content containers that fit any canvas

A content container that fits any canvas fills its scene and uses padding to inset content, so the same scene works
at 1920×1080 and 1080×1920:

```css
.scene-content {
  display: flex; flex-direction: column; justify-content: center; gap: 24px;
  width: 100%; height: 100%; padding: 120px 160px; box-sizing: border-box;
}
```

Absolute positioning with fixed `top` and `left` on a content container overflows as soon as copy grows. Keep
`position: absolute` for decoration. For copy that varies (variables, translations), fit it:

```js
const { fontSize } = window.__hyperframes.fitTextFontSize(text, { fontFamily: "Inter", fontWeight: 800, maxWidth: 1600 });
```

## Layout audit opt-outs

An opt-out attribute tells `check` that an overflow or overlap is on purpose; `overflow: hidden` has no effect on the
audit. Pick the most specific attribute and put it on the smallest element that needs it:

| Attribute | Silences |
|---|---|
| `data-layout-allow-overflow` | overflow of this element and all of its descendants, text clipping included |
| `data-layout-bleed="true"` | a single, deliberate crop of primary text |
| `data-layout-allow-overlap` | layered text on this block alone; children do not inherit it |
| `data-layout-allow-occlusion` | an element that is supposed to cover text, a cutout of a person for instance |
| `data-layout-allow-caption-zone` | copy placed in the caption band on purpose |
| `data-layout-ignore` | decoration the audit should skip entirely |
| `data-hold` | deliberate stillness: `dead_stretch` does not count time while it is on screen |

Findings caught in one sample only, such as an element still entering, stay at info; findings that persist over
several samples count as errors.
