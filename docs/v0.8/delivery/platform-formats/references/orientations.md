---
title: Orientation layouts and type scales
author: MOZGII, Inc.
lang: en
---

# Orientation layouts and type scales

Orientation layouts and type scales give each canvas shape (9:16, 16:9, 4:5, 1:1, 21:9) its own safe areas, type sizes, layout philosophy and common patterns. Build for the primary orientation first, then rebuild layouts for the others rather than cropping.

## Contents

The sections of this page:

- Orientation quick reference
- Landscape HD 1920×1080 (16:9)
- Landscape SD 1280×720 (16:9)
- Portrait 1080×1920 (9:16)
- Portrait feed 1080×1350 (4:5)
- Square 1080×1080 (1:1)
- Widescreen 2560×1080 (21:9)
- Multi-format projects
- Choosing an orientation

## Orientation quick reference

The orientation quick reference lists each canvas with its ratio, platforms and scale factor against 1080p landscape.

| Format | Dimensions | Ratio | Platform | Scale factor |
|---|---|---|---|---|
| Landscape HD | 1920×1080 | 16:9 | YouTube, website hero, LinkedIn video, desktop | 1.0 (baseline) |
| Landscape SD | 1280×720 | 16:9 | Draft, preview, fast render | 0.67 |
| Portrait Shorts | 1080×1920 | 9:16 | TikTok, Instagram Reels, YouTube Shorts | 0.56 |
| Square | 1080×1080 | 1:1 | Instagram feed, Twitter/X, LinkedIn image | 0.56 |
| Portrait Feed | 1080×1350 | 4:5 | Instagram portrait feed | 0.56 |
| Widescreen | 2560×1080 | 21:9 | Cinematic, event screens, ultra-wide monitors | 1.33 |
| 4K | 3840×2160 | 16:9 | Premium delivery, broadcast | 2.0 |

HyperFrames composition dimensions are set via `data-width` and `data-height` on the root composition element.

## Landscape HD 1920×1080 (16:9)

Landscape HD at 1920×1080 is the default canvas.

**Use for:** YouTube, website hero, desktop software demos, LinkedIn, conference screens, broadcast.

### Dimensions
- Canvas: 1920 × 1080px
- Safe zone: 120px top/bottom · 160px left/right
- Content area: 1600 × 840px
- Center: 960, 540

### Typography Scale
| Role | Min | Typical | Max |
|---|---|---|---|
| Display | 100px | 140–200px | 280px |
| Headline | 60px | 80–120px | 160px |
| Subheading | 32px | 40–60px | 80px |
| Body | 24px | 28–36px | 48px |
| Caption | 18px | 20–24px | 28px |
| Data/Mono | 18px | 20–28px | 36px |
| Label/Tag | 16px | 18–20px | 24px |

### Layout Philosophy
- Horizontal space is your asset. Use wide-format splits: 60/40, 70/30, full-bleed left with content right.
- The safe zone (160px side) is minimum. Premium compositions use 200–280px padding for breathing room.
- Three-column grid works well: decoratives left, primary content center, supporting element right.
- Large negative space reads as confidence, not emptiness.

### Common Patterns
- **Cinematic thirds:** Subject occupies left or right third; typographic content fills opposite two-thirds
- **Hero center:** Large centered display text + full-bleed background image or video
- **Split screen:** Vertical rule at 50%, contrasting content each side
- **Lower third:** Content anchored to bottom 200px, rest is visual atmosphere
- **Data wall:** Grid of stats fills the 1600×840 content area, decoratives in safe zone

## Landscape SD 1280×720 (16:9)

Landscape SD at 1280×720 is for drafts and small embeds.

**Use for:** Draft renders, fast iteration, embed thumbnails. Identical layout to HD, just set `data-width="1280" data-height="720"`.

### Dimensions
- Canvas: 1280 × 720px
- Safe zone: 80px top/bottom · 100px left/right
- Scale factor: 0.67× vs HD baseline

### Typography Scale
Multiply HD scales by 0.67:
| Role | Min | Typical |
|---|---|---|
| Display | 67px | 94–134px |
| Headline | 40px | 54–80px |
| Body | 16px | 19–24px |

Use `--quality draft` when rendering at 720p for faster iteration cycles.

## Portrait 1080×1920 (9:16)

Portrait at 1080×1920 is the vertical canvas for short-form apps.

**Use for:** TikTok, Instagram Reels, YouTube Shorts, Snapchat. Mobile-first. Viewers hold their phone. Text competes with UI chrome at top and bottom.

### Dimensions
- Canvas: 1080 × 1920px
- Safe zone: 200px top (above platform UI) · 250px bottom (below platform UI/CTA) · 60px left/right
- Content area: 960 × 1470px
- Center: 540, 960

### Typography Scale
| Role | Min | Typical | Notes |
|---|---|---|---|
| Display | 80px | 100–160px | Often stacked vertically, one word per line |
| Headline | 56px | 72–100px | |
| Subheading | 32px | 40–56px | |
| Body | 28px | 32–40px | Larger than landscape, thumb viewing distance |
| Caption | 24px | 28–36px | Captions appear over video; must be readable |
| Label | 20px | 22–28px | |

**Large text shrinks and small text grows against landscape.** Display and headline sit at about 0.8 of landscape because the frame is only 1080 wide; body grows by about 1.15, and captions and labels by about 1.4, because the screen is small and held in the hand.

### Layout Philosophy
- Vertical momentum is your axis. Think scroll, swipe, fall.
- Top-to-bottom narrative: hook at top, body in middle, call-to-action at bottom.
- Full-bleed backgrounds are standard. Content floats over them.
- Text-forward compositions: a single stat or quote filling 60%+ of the frame reads powerfully.
- Left-align body text, centered text in portrait formats reads as decoration, not content.
- Avoid splitting the frame horizontally (left/right halves), the aspect ratio makes them feel narrow.

### Common Patterns
- **Vertical stack:** Display headline (top third) → body (middle) → CTA/badge (bottom)
- **Quote card:** Single quote filling 70% of frame, name/attribution at bottom
- **Countdown/stat:** Huge number centered, supporting context below
- **Before/after:** Two stacked half-frames with a rule between them

### Platform UI Awareness
| Platform | Top chrome | Bottom chrome | Total protected |
|---|---|---|---|
| TikTok | ~80px | ~280px | 360px |
| Instagram Reels | ~100px | ~200px | 300px |
| YouTube Shorts | ~90px | ~200px | 290px |

Use 200px top + 250px bottom safe zone to clear all platforms. Test at 1080×1920.

## Square 1080×1080 (1:1)

Square at 1080×1080 suits feeds and thumbnails.

**Use for:** Instagram feed posts, Twitter/X, LinkedIn image posts, product thumbnails.

### Dimensions
- Canvas: 1080 × 1080px
- Safe zone: 80px all sides
- Content area: 920 × 920px
- Center: 540, 540

### Typography Scale
| Role | Min | Typical |
|---|---|---|
| Display | 80px | 100–160px |
| Headline | 56px | 72–100px |
| Body | 24px | 28–36px |
| Caption | 18px | 20–24px |

### Layout Philosophy
- The square is the most democratic format, no dominant axis.
- Center-heavy compositions work well: radially symmetrical layouts, single hero element.
- Four-quadrant layouts (2×2 grid) are effective for comparisons or feature sets.
- Avoid horizontal thirds (they imply landscape) and vertical thirds (they imply portrait).
- Strong diagonal motion (top-left → bottom-right) creates energy in a static format.

## Portrait feed 1080×1350 (4:5)

Portrait feed at 1080×1350 is the tallest shape most feeds show uncropped.

**Use for:** Instagram portrait feed, the largest format shown natively in the feed without cropping. Fills more screen than square.

### Dimensions
- Canvas: 1080 × 1350px
- Safe zone: 80px top/bottom · 60px left/right
- Content area: 960 × 1190px
- Center: 540, 675

### Layout Philosophy
- More vertical than square, less extreme than 9:16. Generous text space.
- Portrait photography + title card overlays work exceptionally well.
- Three horizontal zones: atmosphere (top 350px), primary content (650px), grounding element (350px).

## Widescreen 2560×1080 (21:9)

Widescreen at 2560×1080 is for cinematic films and stage screens.

**Use for:** Cinematic productions, event stage screens, ultra-wide monitor applications, premium brand films.

### Dimensions
- Canvas: 2560 × 1080px
- Safe zone: 120px top/bottom · 240px left/right
- Content area: 2080 × 840px
- Center: 1280, 540

### Typography Scale (same vertical as 1920×1080)
| Role | Min | Typical | Notes |
|---|---|---|---|
| Display | 100px | 140–200px | Same as HD, extra horizontal space is atmosphere |
| Headline | 60px | 80–120px | |
| Body | 24px | 28–36px | |

### Layout Philosophy
- Extreme horizontal space. Content in center 1280×840 feels natural; side zones are purely atmospheric.
- Do NOT stretch layouts across full 2560px, it creates empty, disconnected compositions.
- Parallax depth layers: background fills full width, content anchors to center 1/3.
- Cinematic letterbox effect (add black bars at top/bottom) can simulate 2.39:1 for dramatic films.

## Multi-format projects

Multi-format projects render one piece to several orientations:

1. **Author for the primary orientation first** (usually 1920×1080).
2. **Use percentage-based layout** (flexbox, `padding: 6%`) not hardcoded pixel positions.
3. **Create separate sub-compositions per orientation** in `compositions/`: each optimizes its layout.
4. **Typography scale tokens** defined once in CSS variables, adjusted per orientation via a wrapper class.

```css
/* In index.html root CSS. The sizes sit on the same rule that the overrides match: a calc() with var() is
   resolved where it is declared, so sizes declared on :root would ignore a scale changed on a child. */
[data-width] {
  --display-scale: 1;
  --body-scale: 1;
  --display-size: calc(140px * var(--display-scale));
  --body-size: calc(28px * var(--body-scale));
}

/* Per-orientation overrides */
[data-width="1080"][data-height="1920"] { --display-scale: 0.8; --body-scale: 1.15; }
[data-width="1080"][data-height="1080"] { --display-scale: 0.8; --body-scale: 1; }
```

## Choosing an orientation

Choosing an orientation follows the words in the request.

| Signal in request | Orientation |
|---|---|
| "YouTube video", "website hero", "desktop", no format mentioned | 1920×1080 |
| "TikTok", "Reel", "Shorts", "vertical", "phone" | 1080×1920 |
| "Instagram post", "square", "feed" | 1080×1080 |
| "Instagram portrait", "4:5" | 1080×1350 |
| "cinematic", "widescreen", "ultra-wide", "event screen" | 2560×1080 |
| "4K", "broadcast", "premium delivery" | 3840×2160 |
| Multiple mentioned, or "all formats" | Author 1920×1080 first, create variants |

If the orientation is ambiguous and matters for layout: ask before writing HTML.
