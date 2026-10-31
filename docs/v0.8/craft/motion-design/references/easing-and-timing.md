---
title: Easing and timing maths for video
author: MOZGII, Inc.
lang: en
---

# Easing and timing maths for video

Easing and timing maths for video covers converting between frames and seconds, the shape of each common ease and its
CSS equivalent, springs as a function of time, and beat grids that do not drift.

## Contents

The sections of this page:

- Frames and seconds
- Frame rates in practice
- Ease curves and CSS equivalents
- Closed-form springs
- Beat grids that do not drift
- Reading time for on-screen text

## Frames and seconds

Frames and seconds convert with one multiplication: `seconds = frame / fps` and `frame = round(seconds * fps)`.
HyperFrames works in seconds; one frame at 30 fps is 0.0333 s, at 60 fps 0.0167 s, at 24 fps 0.0417 s. A clip shows
over `[start, start + duration)`, so an end state that must be seen has to land at least one frame before the end:
`end - 1 / fps`.

## Frame rates in practice

Frame rates in practice:

| fps | Use |
|---|---|
| 24 | film look, cinematic promos |
| 25 | PAL broadcast regions |
| 29.97 (`30000/1001`) | NTSC broadcast and some camera footage |
| 30 | the default for social and web video |
| 60 | screen recordings, fast UI motion, sports; doubles render time |

Match the frame rate of footage you cut into the film, or motion stutters (`--fps 30000/1001` renders NTSC rates).
Cloud targets accept only 24, 25, 30 and 60.

## Ease curves and CSS equivalents

Ease curves and CSS equivalents let the same feel carry across GSAP, WAAPI and CSS animations. The cubic-bezier
values are close fits, not exact.

| GSAP | Character | CSS `cubic-bezier` |
|---|---|---|
| `power1.out` (quad) | gentle | `(.25, .46, .45, .94)` |
| `power2.out` (cubic) | standard | `(.215, .61, .355, 1)` |
| `power3.out` (quart) | confident | `(.165, .84, .44, 1)` |
| `power4.out` (quint) | strong arrival | `(.23, 1, .32, 1)` |
| `expo.out` | long tail, premium | `(.16, 1, .3, 1)` |
| `power2.inOut` | camera move | `(.645, .045, .355, 1)` |
| `sine.inOut` | drift, calm | `(.445, .05, .55, .95)` |
| `power3.in` | exit, zoom through | `(.895, .03, .685, .22)` |
| `back.out(1.7)` | overshoot | `(.175, .885, .32, 1.275)` |

Durations by weight: 0.15 to 0.3 s energetic, 0.3 to 0.5 s standard, 0.5 to 0.8 s heavy or luxurious, 0.8 to 2 s
cinematic. The slowest scene in a film should be about three times slower than the fastest.

## Closed-form springs

A closed-form spring gives the position as a function of time and nothing else, which lets any single frame render in isolation. For a spring from 0 to
1 with stiffness `k`, damping `c` and mass `m`:

```js
function spring(t, { k = 170, c = 26, m = 1 } = {}) {
  const w0 = Math.sqrt(k / m), zeta = c / (2 * Math.sqrt(k * m));
  if (zeta < 1) {
    const wd = w0 * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + (zeta * w0 / wd) * Math.sin(wd * t));
  }
  return 1 - (1 + w0 * t) * Math.exp(-w0 * t);     // critically damped
}
// drive it from a linear tween on the timeline
const s = { t: 0 };
tl.to(s, { t: 1, duration: 1, ease: "none", onUpdate: () => gsap.set("#card", { y: 120 * (1 - spring(s.t)) }) }, 2);
```

The damping ratio `zeta` names the feel: 1 no bounce, 0.7 to 0.85 premium, 0.4 to 0.6 playful, under 0.3 cartoon.
CSS can approximate a spring with `linear()` sampled from the same function.

## Beat grids that do not drift

Beat grids that do not drift compute every beat from its index. Frames per beat is `fps * 60 / BPM`. Rounding one beat
and adding it repeatedly drifts: at 128 BPM and 30 fps, a beat is 14.0625 frames, and adding 14 each time is 2 frames
late after 32 beats.

```js
const bpm = 128, fps = 30, offset = 0.12;            // offset: time of beat 0 in the track
const beatTime = (i) => offset + (i * 60) / bpm;     // exact seconds
const beatFrame = (i) => Math.round(beatTime(i) * fps);
```

Cuts fall on beats; layout changes fall on bars (every 4 beats in 4/4). A move meant to arrive on a hit begins 40 to
190 ms ahead of it; a reaction starts 0 to 45 ms after; the hit itself is an instant `tl.set`. Real beat times come from
`npx hyperframes beats --json` (see `audio-sync`).

## Reading time for on-screen text

Reading time sets how long text holds: 0.5 s plus 0.3 s per word (1.4 s for 3 words, 2.3 s for 6), at least
2 s for the film's last line, and 0.4 s for a one- or two-word chapter line. HyperFrames' `check` warns `line_unread`
using a similar floor.
