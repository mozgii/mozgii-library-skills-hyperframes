---
title: Website video storyboard and build loop
author: MOZGII, Inc.
lang: en
---

# Website video storyboard and build loop

The website video storyboard is `STORYBOARD.md`: global direction, an asset audit, then one block per beat. The build
loop turns each beat into a scene file and checks it before moving on.

## Contents

The sections of this page:

- Global direction block
- Asset audit table
- Per-beat block format
- Per-scene build loop
- Showing screenshots and images
- Audio wiring in the root

## Global direction block

The global direction block opens the storyboard and fixes what every beat shares.

```markdown
**Format:** 1920×1080, 30 fps
**Audio:** voiceover, low music bed, a few sound effects on visible actions
**VO direction:** calm, confident, short sentences; silence between sentences is a feature
**Style basis:** DESIGN.md (colours, fonts, components from the captured site)
**Music:** warm sustained pad from frame 0, swells under the feature run, drops for the comparison, resolves on the logo
```

## Asset audit table

The asset audit table lists every useful captured asset and assigns it to a beat or skips it with a reason.

| Asset | Type | Beat | Role |
|---|---|---|---|
| `hero-wave.png` | hero image | 1 | full-bleed background with a slow push |
| `dashboard.png` | product screenshot | 3 | floating card in perspective |
| `logo.svg` | SVG | 1, 5 | opener and closer |
| `icon-3.svg` | icon | SKIP | too small to read on video |

Use assets generously: screenshots as floating cards, logos as structure, photos behind numbers.

## Per-beat block format

The per-beat block format gives the builder everything for one scene.

```markdown
### BEAT 2 — THE PROBLEM (3.21–7.80 s)
**VO cue:** "Every week, teams lose hours to manual reports."
**Visual:** a wall of spreadsheet rows slides up and blurs; the number "11 h" lands large in the accent colour.
**Assets:** `spreadsheet.png` (captured), the brand mono font for the label
**Motion:** rows drift up 40 px over the beat; the number blurs in (0.18 s, expo.out) on "hours"
**Transition out:** the number scales into the next beat's card (object becomes the world)
**Depth:** blurred rows (back), number (mid), mono label and a thin rule (front)
**Sound:** soft whoosh on the transition, a low hit when the number lands
```

Times start as estimates and are replaced by transcript times in step 5.

## Per-scene build loop

The per-scene build loop is the same for every beat.

1. Read the beat's block.
2. Build the static hero frame (every element at its most visible moment) in `compositions/<beat>.html`.
3. Snapshot it (`npx hyperframes snapshot --composition <beat> --frames 3`) and fix overlap and overflow.
4. Add entrances with `fromTo`, timed to the words of the VO cue.
5. Add mid-scene activity so nothing sits frozen after the first quarter of the scene.
6. Add the transition into the next beat.
7. Cross-check assets: search the HTML for every file the beat was assigned; references point into the project, not
   inlined `data:` URIs.
8. Cross-check fonts: captured fonts load through `@font-face` from project files.
9. Run `npx hyperframes check --json` and look at the snapshots again.

## Showing screenshots and images

Showing screenshots and images on video needs a treatment, never a flat image pasted in:

- **Perspective card:** `gsap.set(el, { transformPerspective: 1200, rotationY: -8 })` plus a soft shadow. Set the
  perspective through GSAP, not CSS `transform`, which GSAP would overwrite.
- **Slow push:** `scale` 1 to 1.04 over the beat on a wrapper.
- **Device frame:** wrap the screenshot in a laptop or phone shape made with border radius and shadow.
- **Lifted element:** crop one UI element out of the screenshot and move it at a different depth for parallax.
- **Window scroll:** clip the full-page plate to a viewport and animate its `y`.

Centre with flexbox or grid, never with `transform: translate(-50%, -50%)`: GSAP owns `transform` and overwrites it.

## Audio wiring in the root

Audio wiring in the root `index.html` keeps each sound on its own element.

```html
<audio id="narration" class="clip" src="assets/narration.wav" data-start="0" data-track-index="6" data-volume="1"></audio>
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="28" data-track-index="7"
       data-volume="0.15" data-fade-in="0.4" data-fade-out="1.5" data-timeline-role="music"></audio>
<audio id="sfx-whoosh-1" class="clip" src="assets/sfx/whoosh.mp3" data-start="7.7" data-track-index="8" data-volume="0.6"></audio>
```

Add captions only when asked; they go in one captions scene (`hyperframes-captions`).
