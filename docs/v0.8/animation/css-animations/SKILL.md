---
name: css-animations
description: Writes native browser animation that HyperFrames seeks deterministically - CSS @keyframes with finite iteration counts and fill-mode both, and the Web Animations API (element.animate, KeyframeEffect) with delays standing in for clip starts - plus staggers with custom properties, linear() springs, and which effects (grain, shimmer, glow, masks, loops) suit native animation rather than GSAP. Use when a composition uses CSS keyframes, animation properties or element.animate, when adding a decorative loop without a library, or when native animation freezes, flickers or snaps back in a render.
metadata:
  tags:
  - css
  - keyframes
  - waapi
  - web-animations
  - element.animate
  - animation
  - hyperframes
  - loops
---

# CSS and Web Animations API motion for video

Native browser animation comes in two forms, and HyperFrames seeks both. CSS animations (`@keyframes` with the
`animation-*` properties) are found by the CSS adapter; Web Animations API animations (`element.animate()`,
`new Animation(new KeyframeEffect(...))`) are found by the WAAPI adapter, which reads `document.getAnimations()` and
also catches animations created later through `element.animate`. Each frame, both set every animation's
`currentTime` to the frame's time and pause it. Use them for decoration with a fixed length and for light motion
generated from data; scene choreography with many coordinated tweens reads better in GSAP (see `gsap`).

## When to use this skill

Use this skill when a composition uses `@keyframes` or `element.animate()`, when adding a repeating motif (grain,
shimmer, glow) without loading a library, when porting native web animation into a video, or when such motion
freezes, flickers, snaps back or starts at the wrong time in a render.

## Step 0: read the runtime that will seek the animation

```bash
npx hyperframes --version       # the CSS and WAAPI adapters ship with it
npx hyperframes browser path    # the pinned Chrome: `linear()` and WAAPI run in this build
grep -rnE 'infinite|Infinity' --include='*.html' --include='*.css' . | head   # loops to fix first
```

Native animation has no library version to pin; the Chrome the CLI pins decides what the CSS can do.

## Pick CSS keyframes or WAAPI

The choice between CSS keyframes and WAAPI depends on where the values come from.

| When | Use | Because |
|---|---|---|
| A fixed motif on one element (grain, shimmer, pulse) | CSS `@keyframes` | lives in the stylesheet; no script |
| Keyframes or delays computed from data (a list, a chart, tokens) | WAAPI `element.animate` | values are JavaScript |
| Many coordinated tweens, labels, plugins, non-CSS values | GSAP | a timeline is easier to read and edit |

All three can share a composition, as long as no two of them animate the same property of the same element.

## The seek contract for native animation

The seek contract for CSS and WAAPI animation has six rules.

1. Create everything at init: the element is in the DOM and `element.animate()` runs synchronously when the page
   loads, not from a timer or a promise.
2. Iteration counts are finite: `animation-iteration-count: 3`, `iterations: 3`, never `infinite` or `Infinity`.
   Compute the count from the clip's length.
3. Fill both ways: `animation-fill-mode: both` or `fill: "both"`, so a seek before the start or after the end shows
   the held state instead of the unanimated element.
4. Clip start: a CSS animation on a `.clip` with `data-start` runs in that clip's time. A WAAPI animation created at
   init runs in composition time, so a clip that starts at 4 s needs `delay: 4000`.
5. Never call `play()`, never set `animation-play-state: paused` by hand, and never change the DOM from a `finished`
   promise or an `animationend` event.
6. Nothing from hover, focus, scroll, class toggles on events, or the clock.

## CSS keyframes pattern

The CSS keyframes pattern is a timed element with a finite animation that fills both ways.

```html
<div id="pulse-ring" class="clip pulse-ring" data-start="0" data-duration="4" data-track-index="2"></div>
<style>
  .pulse-ring {
    width: 280px; height: 280px; border: 4px solid rgba(255,255,255,.7); border-radius: 50%;
    animation: pulse-ring 1200ms cubic-bezier(.2,0,0,1) 3 both;
  }
  @keyframes pulse-ring {
    from { opacity: 0; transform: scale(.82); }
    35%  { opacity: 1; }
    to   { opacity: 0; transform: scale(1.18); }
  }
</style>
```

Three iterations of 1.2 s fill 3.6 of the clip's 4 s.

## CSS staggers with custom properties

CSS staggers with custom properties reuse one keyframe set across many elements, each delayed by its index.

```html
<div class="clip dots" data-start="1" data-duration="3" data-track-index="3">
  <span style="--i:0"></span><span style="--i:1"></span><span style="--i:2"></span>
</div>
<style>
  .dots span { display: inline-block; width: 18px; height: 18px; margin-right: 10px; border-radius: 50%;
    background: currentColor; animation: dot-pop 900ms ease-out both; animation-delay: calc(var(--i) * 120ms); }
  @keyframes dot-pop { from { opacity: 0; transform: translateY(18px) scale(.75); } to { opacity: 1; transform: none; } }
</style>
```

## WAAPI pattern with element.animate

The WAAPI pattern creates the animation at init with a delay equal to the clip's start, then pauses it.

```html
<div id="orb" class="orb"></div>
<script>
  const a = document.getElementById("orb").animate(
    [
      { transform: "translate3d(-160px,0,0) scale(.8)", opacity: 0 },
      { transform: "translate3d(0,0,0) scale(1)", opacity: 1, offset: 0.35 },
      { transform: "translate3d(120px,0,0) scale(1.08)", opacity: 1 },
    ],
    { duration: 3000, delay: 2000, easing: "cubic-bezier(.2,0,0,1)", fill: "both", iterations: 1 },
  );
  a.pause();
</script>
```

`offset` is a number from 0 to 1, never a percentage string. Staggers from data compute each delay from the index:

```js
document.querySelectorAll(".token").forEach((el, i) => {
  el.animate([{ transform: "translateY(24px)", opacity: 0 }, { transform: "none", opacity: 1 }],
    { duration: 620, delay: 1500 + i * 80, easing: "cubic-bezier(.2,0,0,1)", fill: "both" }).pause();
});
```

## Easing strings and linear() springs

Easing strings in both CSS and WAAPI are CSS timing functions: `linear`, `ease-out`, `cubic-bezier(x1, y1, x2, y2)`,
`steps(n, jump-end)`, and the `linear()` function, which draws any curve, including springs and bounces, as sampled
points: `linear(0, 0.6 20%, 1.08 45%, 0.98 70%, 1)`. Useful curves: `cubic-bezier(.16,1,.3,1)` for an expo-like
arrival, `cubic-bezier(.65,0,.35,1)` for a smooth in-out, `cubic-bezier(.7,0,.84,0)` for an exit that accelerates
away. In CSS the easing applies per keyframe interval; in WAAPI the `easing` option applies to the whole iteration
and a keyframe's own `easing` to its interval.

## Good uses for native animation

Good uses for native animation are motifs that belong to one element and have a fixed length.

| Use | Example |
|---|---|
| Film grain | a noise tile shifted in `steps()` |
| Shimmer | a gradient band moving across a card |
| Glow | `filter: drop-shadow()` breathing three times |
| Mask reveal | a `mask-position` slide |
| Background drift | a slow `background-position` move on a texture |
| Data-driven entrances | WAAPI tokens or bars, each delayed by index |

Avoid breathing or floating loops on titles and UI as a stand-in for real motion; they read as generated.

## Film grain overlay with finite iteration counts

Film grain uses finite iteration counts, never an infinite CSS keyframe loop: a seek-rendered video cannot loop
forever. The grain overlay example shifts a small noise image by steps, so each frame lands on a fixed offset.

```css
.grain { position: absolute; inset: -50%; pointer-events: none; opacity: .08;
  background: url("assets/noise-256.png"); animation: grain 1s steps(10) 12 both; }
@keyframes grain {
  0% { transform: translate(0,0); } 20% { transform: translate(-5%,3%); } 40% { transform: translate(4%,-6%); }
  60% { transform: translate(-3%,5%); } 80% { transform: translate(6%,2%); } 100% { transform: translate(0,0); }
}
```

Twelve one-second iterations cover a 12 s clip. Mark the layer `data-layout-ignore` so layout checks skip it.

## Verify native animation

```bash
npx hyperframes check --json                     # no errors
npx hyperframes keyframes --runtime all --json   # the native animations are listed with their times
npx hyperframes snapshot --at 0,1.9,2.1,3.9      # before, across and after the clip's start and end
```

A frame before the start must show the held state, not the bare element.

## Checklist

- [ ] Finite iteration counts that cover the clip; `fill-mode: both` or `fill: "both"`.
- [ ] CSS-animated timed elements have `class="clip"` and `data-start`; WAAPI clip starts expressed through `delay`.
- [ ] Animations use transforms, opacity and filters, not `left`, `top`, `width` or `height`.
- [ ] WAAPI `offset` values numeric; no `play()`, no hand-set `paused` play state.
- [ ] No property animated by both native animation and GSAP.
- [ ] Nothing triggered by hover, scroll or class changes from events.

## Gotchas

- **Symptom:** An element stays frozen on its first frame. **Cause:** `animation-play-state: paused` set by hand
  blocks the runtime's positioning. **Fix:** remove it and let the adapter pause.
- **Symptom:** Flicker or a snap back at the clip's edges. **Cause:** `fill` was `none` or `forwards` and a seek
  landed before the start. **Fix:** use `both`.
- **Symptom:** WAAPI motion starts too early. **Cause:** The clip starts at 4 s but the animation has no 4000 ms
  delay. **Fix:** set `delay` to the clip's start.
- **Symptom:** The same frame shows after the first loop. **Cause:** An infinite count. **Fix:** use a finite one
  computed from the duration.
- **Symptom:** Drift in the preview. **Cause:** A script called `play()` and the browser clock took over. **Fix:**
  delete the call.
- **Symptom:** A CSS transform fights GSAP. **Cause:** The same element is animated by both. **Fix:** give each its
  own element.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `left`, `top`, `width` or `height` in keyframes | transforms, opacity and filters |
| changing the DOM from `finished` or `animationend` | put the change on the timeline at a time |
| `offset: "35%"` | `offset: 0.35` |
| hover, focus or scroll triggers | state that depends on time alone |

## See also

`gsap`, `vfx`, `motion-design`.
