---
name: video-design-system
description: Sets the visual identity of a programmatic video before any scene is built - reading or writing a design.md brand file, choosing light or dark ground, palette tokens, type pairing and video type sizes, a named visual style, textures and depth layers, and checking a composition against the brand afterwards. Use when starting a new HyperFrames video, when no brand file exists, when a video looks generic or off-brand, or when the person names a style or mood.
metadata:
  tags:
  - design-system
  - brand
  - palette
  - typography
  - design-md
  - visual-style
  - video
---

# Video design system

A video design system is the small set of decisions every scene shares: ground colour, ink, one accent, two type
voices, corner and spacing rules, a motion signature and a texture. Settle it first and write it down, usually in a
`design.md` at the project root, so every scene and every later edit uses the same values.

## When to use this skill

Use this skill at the start of a new video, when a project has no brand file, when the person names a mood or style,
when output looks generic, and after building, to check the composition against the brand.

## Step 0: read what the project already has

```bash
npx hyperframes --version
ls design.md DESIGN.md frame.md 2>/dev/null          # the brand file, either spelling
ls assets/fonts 2>/dev/null                          # the fonts actually on hand
```

An existing brand file wins over anything below.

## Pick the starting point

What you were handed decides where the identity comes from.

| You have | Start from | Why the others lose |
|---|---|---|
| A `design.md` or `DESIGN.md` | that file, with its exact values | it is the source of truth; anything else invents colours |
| A live website | a capture and its tokens (`website-to-hyperframes`) | real brand values beat a guess from a screenshot |
| Colours or fonts, and no system | those, plus a type pairing and roles | a named style would override what they gave you |
| A mood only | a named style (Step 4) | a tested set of tokens is quicker than one built from nothing |
| Nothing | three questions: mood, light or dark, brand colours or fonts | one question now saves a rebuilt film |

## Step 1: find the brand

Step 1 finds the brand before choosing anything.

1. Look for `design.md` or `DESIGN.md` at the project root (both spellings; they are different files on Linux).
   It is the source of truth: use its exact hex values, families and weights.
2. If it names fonts that are not bundled with HyperFrames and no files exist in `assets/fonts/`, say so before
   writing HTML: "design.md asks for Söhne, but there are no font files; add .woff2 files to assets/fonts/ or I will
   use the closest bundled family."
3. If there is a website, capture it (`website-to-hyperframes`) and derive the brand from its tokens.
4. Otherwise ask three things: the mood, light or dark, and any brand colours or fonts. Or offer a named style.

`design.md` defines the brand, not the frame: apply its colours at video scale (stronger borders, larger type,
visible accents), not at web-UI opacity.

## Step 2: palette

Step 2 picks the palette and names colours by role.

- Declare `--bg`, `--text-primary`, `--accent` (plus surfaces, borders, muted accent) before writing HTML; scenes use
  the variables, never raw hex.
- One accent hue; the same ground in every scene; tint neutrals toward the accent.
- No pure `#000` or `#fff`; no full-screen linear gradients on dark grounds (H.264 bands them).
- Dark ground for tech, cinema, finance and luxury; light for editorial, wellness, food and children.

Tokens, rules, OKLCH recipe and nine palette families: [references/palettes.md](references/palettes.md).

## Step 3: type

Step 3 picks two type voices and sets video sizes.

- Pair across categories (serif with sans, sans with mono); two similar sans faces look like a mistake.
- One expressive face per scene; the other recedes.
- Weight contrast must be visible in motion: 300 against 800 or 900, not 400 against 700.
- Sizes at 1080p: headlines 64 to 120 px, body 28 to 42 px, labels 18 to 24 px; never below 28 px for text that must
  be read on a phone.
- Track display sizes slightly tighter (−0.01 to −0.04 em); on dark grounds, drop body weight a step and open
  line-height by 0.05 to 0.1.

Font loading, bundled families, licences and OpenType features: `video-fonts`.

## Step 4: a named style, when one fits

A named style is a starter identity with tokens for colour, type, corners, spacing and motion. Eight are available:
Swiss Pulse (precise, data), Velvet Standard (premium), Deconstructed (raw), Maximalist Type (loud launches), Data
Drift (AI, immersive), Soft Signal (warm, human), Folk Frequency (vivid, consumer), Shadow Cut (dark, cinematic).
Token blocks and how to make your own: [references/visual-styles.md](references/visual-styles.md).

## Step 5: texture and depth

Step 5 adds the background layer that keeps frames from feeling empty: a radial glow, ghost type, a grid or rules, a
vignette, a grain layer. Two to five background elements per scene, each moving slowly or not at all. Code:
[references/textures-and-depth.md](references/textures-and-depth.md).

## The design.md file

The `design.md` file records the decisions in a form people and agents both read: optional YAML tokens on top, then
`## Overview`, `## Colors`, `## Typography`, `## Elevation`, `## Components` and `## Do's and Don'ts`. Keep it under
about 100 lines. A minimal one:

```markdown
---
colors: { bg: "#0b0d12", ink: "#f4f1ea", accent: "#ff5a36", border: "#2a2e37" }
typography: { display: "Playfair Display 400 italic", sans: "Inter 400/800", mono: "JetBrains Mono 500" }
rounded: { card: 24px }
motion: { entry: "expo.out", exit: "power3.in", transition: "blur swap" }
---
## Overview
Quiet, editorial, dark. One coral accent carries meaning; everything else is ink on near-black.
## Do's and Don'ts
- Do: thin 2 px rules to structure frames. - Don't: gradients across the whole frame, drop shadows, neon.
```

## Lazy defaults to question

Lazy defaults to question are the choices generated designs reach for first. Each can be right on purpose; none
should appear by default:

- gradient text (`background-clip: text`), purple-to-blue gradients, cyan-on-dark neon;
- left-edge accent stripes on cards; identical card grids;
- pure black or white grounds;
- everything centred with equal weight;
- the most overused families for the register (Inter or Roboto everywhere, Playfair Display for anything premium)
  without a reason;
- emoji standing in for icons.

## Checking a composition against the brand

Checking a composition against the brand happens after building, from the HTML:

1. Every hex in the composition appears in the palette; flag invented colours.
2. Families and weights match the type spec; no substitutions.
3. Corner radii, padding and gaps follow the declared values.
4. Shadows follow the declared depth (flat, subtle or layered).
5. Nothing on the Don'ts list appears.
6. Without a brand file: the same ground, ink and accent in every scene, and no lazy default left unexamined.

Report violations as a list and fix each before showing the preview.

## Verify the brand in the composition

```bash
grep -ohE '#[0-9a-fA-F]{6}\b' index.html compositions/*.html | sort | uniq -c | sort -rn   # each hex is in the palette
npx hyperframes check --json | grep -c font_family_without_font_face                       # expect 0
npx hyperframes snapshot --review                                                          # one ground across the beat sheet
```

A hex that appears once is usually an invented colour.

## Checklist

- [ ] Brand found or chosen and written to `design.md`.
- [ ] Palette declared as role tokens; one accent; tinted neutrals.
- [ ] Two type voices crossing categories; video sizes; visible weight contrast.
- [ ] Background layer in every scene.
- [ ] Composition checked against the brand; contrast passes `check`.

## Gotchas

- **Symptom:** Brand colours look weak on video. **Cause:** Web opacities (5 to 8%) vanish after compression. **Fix:**
  use 12 to 25% for atmosphere and full saturation for focal elements.
- **Symptom:** A brand font is silently replaced. **Cause:** A non-bundled family without `@font-face` falls back.
  **Fix:** add the rule and the file; lint fails `font_family_without_font_face` until then.
- **Symptom:** Every scene looks like a different film. **Cause:** Colour invented per scene. **Fix:** keep one
  ground.

## Anti-patterns

| Do not | Do instead |
|---|---|
| raw hex in scenes | role tokens: `--bg`, `--text-primary`, `--accent` |
| two similar sans faces | pair across categories |
| 400 against 700 for contrast | 300 against 800 or 900, which reads in motion |
| a full-screen linear gradient on a dark ground | a radial glow plus grain; H.264 bands the gradient |

## References

- [references/palettes.md](references/palettes.md): role tokens, video colour rules, OKLCH palettes, nine palette families.
- [references/visual-styles.md](references/visual-styles.md): eight named styles with token blocks.
- [references/textures-and-depth.md](references/textures-and-depth.md): depth layers, grain, glows, ghost type, grids, vignettes, particles, glass.

## See also

`video-fonts`, `motion-design`, `design-to-hyperframes`, `video-thumbnails`, `video-review`.
