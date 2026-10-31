---
title: Caption animation styles
author: MOZGII, Inc.
lang: en
---

# Caption animation styles

Caption animation styles are the entrances, highlights and exits that give captions energy without hurting reading.
All of them are plain GSAP tweens placed at transcript times, so they seek and render exactly.

## Contents

The sections of this page:

- Styles by energy
- Karaoke highlight
- Emphasis words
- Clip-path wipe entrance
- Slam word
- Scatter and drop exits
- Audio-reactive caption intensity
- Marker highlights on captions

## Styles by energy

Styles by energy pick a highlight and an exit from the transcript's pace.

| Energy | Highlight | Exit | Variation |
|---|---|---|---|
| High | karaoke with accent colour, glow and a 15% scale pop | scatter or drop | change highlight style every 2 groups |
| Medium-high | karaoke with a colour pop | scatter or collapse | every 3 groups |
| Medium | karaoke, white only | fade and slide | every 3 groups |
| Medium-low | karaoke, 3% scale | fade | one style, vary the ease |
| Low | karaoke, warm tones, slower | collapse | every 4 groups |

Never stack two competing animations on one word at one time.

## Karaoke highlight

A karaoke highlight lights each word at its own start time while the group stays on screen.

```js
g.words.forEach((w, wi) => {
  const sel = `#cap-${gi}-${wi}`;
  tl.fromTo(sel, { color: "rgba(255,255,255,.55)", scale: 1 },
    { color: "#ffffff", scale: 1.06, duration: 0.08, ease: "power2.out" }, w.start);
  tl.to(sel, { scale: 1, duration: 0.12, ease: "power2.inOut" }, w.end);
});
```

Each word span needs `display: inline-block` for the scale to apply.

## Emphasis words

Emphasis words break the group's pattern: brand names, numbers, ALL-CAPS words, emotional keywords and calls to
action get a larger scale, the accent colour or an overshoot ease.

```js
const EMPHASIS = /^(free|now|never|\d[\d,.%]*)$/i;
if (EMPHASIS.test(w.text.replace(/[^\w%.,]/g, ""))) {
  tl.fromTo(sel, { scale: 0.8, color: "#ffffff" },
    { scale: 1.18, color: "#ff5a36", duration: 0.22, ease: "back.out(2)" }, w.start);
}
```

## Clip-path wipe entrance

A clip-path wipe entrance reveals the group left to right, like a marker sweep.

```js
tl.fromTo(el, { clipPath: "inset(0 100% 0 0)", opacity: 1 },
  { clipPath: "inset(0 0% 0 0)", duration: 0.22, ease: "power3.out" }, start);
```

## Slam word

A slam word lands a single word large and fast, with a short shake of its container.

```js
tl.fromTo(sel, { scale: 2.4, opacity: 0, filter: "blur(6px)" },
  { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.in" }, w.start);
tl.fromTo(el, { x: 0 }, { x: 6, duration: 0.03, repeat: 3, yoyo: true, ease: "none" }, w.start + 0.16);
```

The shake uses a finite `repeat`, as every repeat in HyperFrames must.

## Scatter and drop exits

Scatter and drop exits leave with energy instead of a plain fade. Offsets come from a seeded PRNG so every render is
the same.

```js
function seededRandom(seed) { let count = seed | 0; return () => { count = count + 0x2AC5E3B1 | 0;
  const spread = Math.imul(count, 0x4F2B71A3), mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
  return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296; }; }
const rand = seededRandom(gi + 1);
g.words.forEach((w, wi) => tl.to(`#cap-${gi}-${wi}`, {
  x: (rand() - 0.5) * 120, y: -40 - rand() * 60, rotation: (rand() - 0.5) * 30, opacity: 0,
  duration: 0.2, ease: "power2.in" }, g.end - 0.2));
tl.set(el, { opacity: 0, visibility: "hidden" }, g.end);
```

A drop exit is the same with `y: 80` and `ease: "power3.in"`.

## Audio-reactive caption intensity

Audio-reactive caption intensity scales each group's entrance by the music's energy in that group's time range. The
values are read when the timeline is built, not per frame, so nothing depends on playback.

```js
// AUDIO = { fps, frames: [{ rms, bands: [...] }] } from the audio-sync skill's extraction script
const f0 = Math.floor(g.start * AUDIO.fps), f1 = Math.min(Math.floor(g.end * AUDIO.fps), AUDIO.frames.length - 1);
let bass = 0;
for (let f = f0; f <= f1; f++) bass = Math.max(bass, AUDIO.frames[f].bands[0], AUDIO.frames[f].bands[1]);
tl.fromTo(el, { scale: 0.96 }, { scale: 1 + bass * 0.06, duration: 0.3, ease: "power2.out" }, start);
tl.set(el, { scale: 1 }, g.end - 0.15);
```

Keep the variation to 3 to 6% scale and a soft glow; heavy pulsing makes text unreadable.

## Marker highlights on captions

Marker highlights on captions draw a sweep, circle, burst or scribble on one emphasis word on top of the karaoke pass.
The code for each mode is in the `vfx` skill's text emphasis reference. Use them on one word per few groups at most.
