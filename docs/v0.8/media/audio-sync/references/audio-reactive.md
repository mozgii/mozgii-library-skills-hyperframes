---
title: Audio-reactive motion in seek-rendered video
author: MOZGII, Inc.
lang: en
---

# Audio-reactive motion in seek-rendered video

Audio-reactive motion makes visuals respond to sound: a logo that pushes on the kick, a glow that brightens on
cymbals, captions that arrive heavier on loud phrases. In a seek-rendered video the audio cannot be analysed live,
because frames are not rendered in playback order. The sound is analysed once into per-frame data, and the timeline
reads that data as a function of time.

## Contents

The sections of this page:

- The band data
- Build-time shaping
- Per-frame reading in onUpdate: a logo that pulses with the bass
- Mapping bands to properties
- Limits that keep it tasteful
- What never to build

## The band data

The band data comes from `scripts/extract_audio_bands.py`: one entry per video frame with `rms` (overall loudness)
and `bands` (energy from bass to treble), each normalised 0 to 1 to that band's own 95th percentile. Embed it in the
composition (a `<script>` that assigns `const AUDIO = {...}`) or load it from `assets/` before building the timeline.

| Bands (8, 30 Hz to 16 kHz, log-spaced) | Roughly |
|---|---|
| 0 to 1 | kick, sub-bass, bass |
| 2 to 3 | bass notes, low mids, warmth |
| 4 to 5 | voice body, snares, guitars |
| 6 to 7 | presence, hi-hats, cymbals, air |

## Build-time shaping

Build-time shaping reads the data while building tweens: each group or element gets a stronger or softer version of a
normal tween. Nothing runs per frame, so it is the cheapest and safest approach.

```js
function peak(start, end, b0, b1) {
  let m = 0;
  for (let f = Math.floor(start * AUDIO.fps); f <= Math.min(AUDIO.totalFrames - 1, Math.floor(end * AUDIO.fps)); f++)
    for (let b = b0; b <= b1; b++) m = Math.max(m, AUDIO.frames[f].bands[b]);
  return m;
}
SECTIONS.forEach((s) => {
  const bass = peak(s.start, s.start + 0.4, 0, 1);
  tl.fromTo(`#${s.id}`, { scale: 0.92, opacity: 0 },
    { scale: 1 + bass * 0.05, opacity: 1, duration: 0.3, ease: "power3.out" }, s.start);
});
```

## Per-frame reading in onUpdate: a logo that pulses with the bass

Per-frame reading in `onUpdate` drives a property continuously, such as a logo that pulses with the bass of the
track. One linear tween spans the time range; its `onUpdate` turns the current time into a frame index and sets
properties from that frame. The result depends only on time, so any seek renders correctly.

```js
const clock = { t: 0 }, D = AUDIO.totalFrames / AUDIO.fps;
tl.to(clock, { t: D, duration: D, ease: "none", onUpdate: () => {
  const f = AUDIO.frames[Math.min(AUDIO.totalFrames - 1, Math.floor(clock.t * AUDIO.fps))];
  gsap.set("#logo", { scale: 1 + f.bands[0] * 0.04 });
  gsap.set("#glow", { opacity: 0.25 + f.bands[6] * 0.35 });
  gsap.set("#bg", { "--energy": f.rms.toFixed(3) });              // CSS reads var(--energy)
} }, 0);
```

Never animate the same property from this `onUpdate` and from another tween. Never build it as one `tl.call()` per
frame: seeking does not replay callbacks, so renders show stale values.

## Mapping bands to properties

Mapping bands to properties, with sensible ranges:

| Sound | Property | Range |
|---|---|---|
| Bass (bands 0 to 1) | scale of a logo or hero | +2 to +5% |
| Bass | background brightness or a radial glow | +10 to +30% |
| Mids (4 to 5) | blur or distortion on a backdrop | 0 to 4 px |
| Treble (6 to 7) | glow radius, sparkle opacity | 0 to 30% |
| RMS | camera shake amplitude, particle speed | small; seeded |

## Limits that keep it tasteful

Limits that keep audio-reactive motion tasteful:

- Text and logos: 5% scale or less and 30% glow or less, or reading suffers.
- Backgrounds can take 10 to 30%.
- Smooth the release, never the attack: hits must stay sharp (the extraction script does this).
- React to one band per element; several reacting to everything reads as jitter.

## What never to build

What never to build from audio data: equaliser bars, spectrum analysers and waveforms (unless the video is about
audio), strobing, and rainbow colour cycling. The audio supplies timing and intensity; the look still comes from the
brand.
