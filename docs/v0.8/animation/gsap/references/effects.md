---
title: GSAP effects for video
author: MOZGII, Inc.
lang: en
---

# GSAP effects for video

GSAP effects for video are small, deterministic patterns that recur in explainers and promos: a typewriter with a
cursor, a count-up number, a rotating word, a highlight sweep and a progress bar. Each one is built only from tweens
and `tl.set` calls at times, so it seeks correctly.

## Contents

The sections of this page:

- Typewriter with a cursor
- Count-up numbers
- Rotating word
- Highlight sweep across wrapped lines
- Progress bar
- Seeded decoding text

## Typewriter with a cursor

A typewriter with a cursor types text with TextPlugin and blinks the cursor with finite, timeline-driven steps instead
of an infinite CSS animation.

```html
<span id="typed"></span><span id="caret">|</span>
```

```js
gsap.registerPlugin(TextPlugin);
const text = "Ship the video, not the setup.";
const t0 = 1.0, cps = 12, typeEnd = t0 + text.length / cps, holdEnd = typeEnd + 1.6;
tl.set("#caret", { opacity: 1 }, t0);
tl.to("#typed", { text: { value: text }, duration: text.length / cps, ease: "none" }, t0);
for (let t = typeEnd, on = false; t < holdEnd; t += 0.4, on = !on) tl.set("#caret", { opacity: on ? 1 : 0 }, t);
```

Keep the text and caret elements flush in the HTML (no whitespace between them), or a gap appears.

## Count-up numbers

Count-up numbers tween a plain object and write the formatted value on update.

```js
const n = { v: 0 };
tl.to(n, { v: 1284000, duration: 1.4, ease: "power2.out",
  onUpdate: () => { el.textContent = "$" + Math.round(n.v).toLocaleString("en-US"); } }, 2.0);
```

Set `font-variant-numeric: tabular-nums` so digits do not jitter, and run the count for 1.2 to 1.6 s, then hold.

## Rotating word

A rotating word swaps one word of a sentence through a list of options, slot-machine style, spending about 0.1 s on
each before it settles on the last.

```html
<h2>Built for <span id="slot" style="display:inline-block;overflow:hidden;height:1.1em;vertical-align:bottom">
  <span id="slot-reel" style="display:block">
    <span style="display:block">teams</span><span style="display:block">agents</span>
    <span style="display:block">studios</span><span style="display:block">you</span>
  </span></span></h2>
```

```js
const steps = 3;   // three rolls to the fourth word
for (let i = 1; i <= steps; i++)
  tl.to("#slot-reel", { yPercent: -(100 / (steps + 1)) * i, duration: 0.1, ease: "power2.inOut" }, 2 + i * 0.12);
```

## Highlight sweep across wrapped lines

A highlight sweep across wrapped lines tweens a custom property that sizes a background band, with
`box-decoration-break: clone` so each line gets its own band.

```css
.mark { --sweep: 0%; background: linear-gradient(#ffd23f, #ffd23f) 0 88% / var(--sweep) 38% no-repeat;
        -webkit-box-decoration-break: clone; box-decoration-break: clone; }
```

```js
tl.fromTo(".mark", { "--sweep": "0%" }, { "--sweep": "100%", duration: 0.5, ease: "power2.out" }, 3);
```

More marker styles (circle, burst, scribble, strike): the `vfx` skill's text emphasis reference.

## Progress bar

A progress bar scales a filled bar from its left edge while a label counts.

```js
tl.fromTo("#bar-fill", { scaleX: 0 }, { scaleX: 0.72, transformOrigin: "0% 50%", duration: 1.2, ease: "power3.out" }, 4);
const p = { v: 0 };
tl.to(p, { v: 72, duration: 1.2, ease: "power3.out", onUpdate: () => { label.textContent = Math.round(p.v) + "%"; } }, 4);
```

## Seeded decoding text

Seeded decoding text replaces ScrambleText when frames must be identical between renders.

```js
function seededRandom(seed) { let count = seed | 0; return () => { count = count + 0x2AC5E3B1 | 0;
  const spread = Math.imul(count, 0x4F2B71A3), mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
  return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296; }; }
const target = "ACCESS GRANTED", glyphs = "01#%&*";
const s = { p: 0 };
el.textContent = target;                                  // the rest state, whatever the HTML holds
tl.to(s, { p: 1, duration: 1.2, ease: "none", onUpdate: () => {
  if (s.p === 0) { el.textContent = target; return; }     // a back-seek lands here: no glyphs before the tween
  const rand = seededRandom(Math.floor(s.p * 60));          // seed from progress: same frame, same glyphs
  const shown = Math.floor(s.p * target.length);
  el.textContent = target.split("").map((c, i) => i < shown || c === " " ? c : glyphs[Math.floor(rand() * glyphs.length)]).join("");
} }, 2);
```
