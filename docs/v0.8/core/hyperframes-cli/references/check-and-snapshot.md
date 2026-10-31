---
title: HyperFrames check, motion sidecars and snapshots
author: MOZGII, Inc.
lang: en
---

# HyperFrames check, motion sidecars and snapshots

HyperFrames check is the gate before preview and render: `npx hyperframes check` runs the linter, then boots Chrome
once and sweeps a grid of seek times, running every audit at each sample. Snapshots are the stills you read to see the
video. This page covers both, plus motion sidecars that state motion intent as assertions.

## Contents

The sections of this page:

- Check flags
- What check audits
- Severity and persistence
- Motion sidecars
- Snapshot modes
- Review sheets for a whole film
- Keyframes and motion paths

## Check flags

Check flags tune the sweep:

```bash
npx hyperframes check --json             # {ok, browserSkipped, lint, runtime, layout, motion, contrast, craft, hdr, snapshots}
npx hyperframes check --snapshots        # also write annotated overview frames and a crop per finding
npx hyperframes check --samples 15       # denser sweep (default 9)
npx hyperframes check --at 1.5,4,7.25    # hero-frame instants
npx hyperframes check --at-transitions   # also sample every tween start and end
npx hyperframes check --tolerance 4      # overflow pixels allowed before reporting (default 2)
npx hyperframes check --timeout 30000    # render-ready and navigation minimum, ms
npx hyperframes check --no-contrast      # skip WCAG while iterating
npx hyperframes check --strict           # warnings fail too
npx hyperframes check --caption-zone "x0=0;y0=.82;x1=1;y1=1;severity=error"   # reserve a caption band
npx hyperframes check --frame-check      # images, svg, video, canvas out of frame
```

Do not run a separate `lint` right before `check`; `check` already lints.

## What check audits

Check audits five areas in one browser session.

- **Runtime:** console errors, unhandled exceptions, failed requests, HTTP 4xx and 5xx.
- **Layout:** text spilling out of its box or the canvas, clipped text, overlaps and occlusion that persist, an opaque
  element hiding the whole canvas (`canvas_covered`), and children breaking out of containers that clip. Where text
  sits beneath a transparent `<video>`, coverage is worked out word by word from the alpha of that frame.
- **Motion:** assertions from `*.motion.json` sidecars.
- **Contrast:** visible text is held to WCAG AA, sampled at 5 grid points: a ratio of at least 4.5:1 for body text and
  3:1 for large text (24 px, or 19 px bold).
  Each failure carries the sampled colours and a `suggestedColor` in the same palette direction.
- **Craft (warnings only):** `line_unread`, `dead_stretch`, `text_below_floor`, `first_frame_empty`, `film_silent`.

Every finding has a selector, the element's `data-*` identity, the source file, a bounding box and the sample time.

## Severity and persistence

How severe a finding is depends on how long it lasts. A problem caught in a single sample, such as an element midway
through its entrance, is reported as info only. A problem that persists over several samples affects the exit code,
so an overlap that stays (`content_overlap`) counts as an error. When a composition runs 3 s or longer and none of
its frames ever differ, it fails `sweep_static`: a frozen timeline tells check that seeking has no effect on the page.
A card that is still by design carries `data-no-timeline` on its root.

A frequent false alarm comes from a reveal that is done early and then sits still: each sample sees the finished frame, so check
reports no movement. The fix is to stretch the reveal or follow the hold with something that actually happens next.
Adding a slow drift or a blinking caret only to quiet the warning makes the film worse.

## Motion sidecars

A motion sidecar is a `<name>.motion.json` file next to a composition that states what the motion must do. `check`
finds it automatically and reports failures as errors.

```json
{
  "duration": 12,
  "assertions": [
    { "kind": "before", "a": "#price-old", "b": "#price-new" },
    { "kind": "appearsBy", "selector": "#price-new", "bySec": 3.2 },
    { "kind": "keepsMoving", "withinSelector": "#pricing", "maxStaticSec": 2.5 },
    { "kind": "staysInFrame", "selector": ".plan-tile" }
  ]
}
```

| Assertion | Fails with |
|---|---|
| `appearsBy` | `motion_appears_late`: not at opacity 0.5 or more by `bySec` |
| `before` | `motion_out_of_order`: `a` does not appear strictly before `b` |
| `staysInFrame` | `motion_off_frame`: once visible, the box leaves the canvas |
| `keepsMoving` | `motion_frozen`: a static window longer than `maxStaticSec` (default 2 s); the last 3 s never count |

A selector that matches nothing fails `motion_selector_missing`, so a typo fails loudly.

## Snapshot modes

Snapshot modes choose which instants become PNGs. One of `--at`, `--range START,END` or `--composition <id>`;
`--frames` defaults to 5. Output goes to `.hyperframes/artifacts/snapshots/<id>/` unless `--output` is set.

```bash
npx hyperframes snapshot --at 0,2.5,5 --no-end
npx hyperframes snapshot --range 3,5 --frames 8
npx hyperframes snapshot --composition intro --frames 6
npx hyperframes snapshot --zoom "#cta" --zoom-scale 3
npx hyperframes snapshot --zoom "100,50,400,300"
npx hyperframes snapshot --angle iso                 # depth and overlap in 3D layouts
npx hyperframes snapshot --at 1,3,5 --against ref.mp4  # side by side with a reference video
```

`--zoom` raises the device scale factor instead of resizing the viewport, so layout is untouched. Managed snapshot
storage keeps the newest 10 runs and anything under 24 hours old; copy before and after evidence elsewhere.

## Review sheets for a whole film

Review sheets show a whole film over time in a few images. `npx hyperframes snapshot --review` writes:

- `review-beats.jpg`: every scene 0.3 s after it opens and again at its midpoint, plus each element marked
  `data-beat="name"`;
- `review-seam-NN.jpg`: five frames per cut, 0.2 s and 0.1 s before it, on it, and 0.1 s and 0.2 s after;
- `review-phone.jpg`: the same beat frames scaled to 360 px across, for judging whether text survives a phone.

`--json` returns paths and times. Judge the sheets with the `video-review` skill.

## Keyframes and motion paths

Keyframes and motion paths show one element's motion without a render.

```bash
npx hyperframes keyframes --json --selector '#card' --runtime all      # property, time, value, ease (GSAP, CSS, anime.js)
npx hyperframes keyframes --shot motion.png --selector '#card'         # samples drawn over time with the path
npx hyperframes keyframes --shot motion.png --selector '#card' --layout strip --from 2 --to 4
```
