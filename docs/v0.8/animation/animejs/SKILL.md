---
name: animejs
description: Writes anime.js v4 animation that HyperFrames can seek - animate and createTimeline with autoplay false, instances pushed to window.__hfAnime, v4 ease names, staggers, seeded randomness with createSeededRandom, splitText, SVG drawables and morphs - and ports v3 anime() code to v4. Use when a composition uses anime.js, when porting anime.js examples into a video, or when anime.js motion renders frozen or out of sync.
metadata:
  tags:
  - animejs
  - anime.js
  - animation
  - hyperframes
  - svg
  - stagger
---

# anime.js for video

anime.js runs in HyperFrames through a runtime adapter that seeks every registered instance to the frame's time in
milliseconds. The composition creates the animations; HyperFrames owns the clock. Checked against anime.js 4.5.0
(MIT licence). GSAP stays the main authoring path; use anime.js when the person asks for it
or when porting existing anime.js code.

## When to use this skill

Use this skill when a composition contains anime.js, when porting an anime.js example or site animation into a video,
or when anime.js motion renders frozen, blank or out of step with GSAP.

## Step 0: read the anime.js version the film loads

```bash
grep -rhoE 'animejs@[0-9]+\.[0-9]+\.[0-9]+' --include='*.html' . | sort -u   # pinned in script tags
npm ls animejs --depth=0 2>/dev/null                                        # a bundled project
npx hyperframes --version                                                   # the runtime adapter
```

A 3.x result means v3 call shapes: port them first (below). `createSpring()` is deprecated from 4.5, so use
`anime.spring`, and the `dist/bundles/` paths start at 4.1.

## The adapter contract

The adapter contract for anime.js has four rules.

1. Create animations and timelines synchronously at init.
2. Pass `autoplay: false`; v4 autoplays by default.
3. Push every instance onto `window.__hfAnime`. v4 has no global list of running animations, so an instance that is
   not pushed is never seeked.
4. Keep durations and loop counts finite; no wall-clock callbacks, no unseeded randomness.

## Basic animation

A basic animation uses the v4 global `anime` namespace: `anime.animate(targets, params)`.

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@4.5.0/dist/bundles/anime.umd.min.js"></script>
<script>
  window.__hfAnime = window.__hfAnime || [];
  const mark = anime.animate(".mark", {
    x: 280, rotate: "1turn", opacity: [0, 1],
    duration: 1200, delay: 400, ease: "outExpo", autoplay: false,
  });
  window.__hfAnime.push(mark);
</script>
```

Times are milliseconds. A clip that starts later in the video needs its offset in `delay` (or a timeline position),
because the adapter seeks composition time.

## Timelines

Timelines in v4 come from `anime.createTimeline()`, and `add()` takes `(targets, params, position)`.

```js
const tl = anime.createTimeline({ autoplay: false, defaults: { ease: "outCubic" } });
tl.add(".title", { y: [40, 0], opacity: [0, 1], duration: 650 }, 300)
  .add(".accent", { scaleX: [0, 1], duration: 450 }, "-=250")
  .add(".tag", { opacity: [0, 1], duration: 300 }, "<<+=100");
window.__hfAnime.push(tl);
```

## Eases, staggers and seeded randomness

Eases, staggers and seeded randomness use v4 names.

| v4 | Notes |
|---|---|
| `ease: "outExpo"`, `"inOutQuad"`, `"outElastic(1, .5)"`, `"linear"` | v3's `easing: "easeOutExpo"` is gone |
| `delay: anime.stagger(80, { from: "center" })` | staggers by index |
| `ease: anime.spring({ bounce: 0.3, duration: 600 })` | a spring ease; `stiffness`, `damping`, `mass` also work. `createSpring()` is deprecated in 4.5 and logs a warning |
| `const rand = anime.createSeededRandom(42)` | seeded random numbers, same on every render |

Never use `anime.random()` or `Math.random()` for render-critical values.

## Text and SVG helpers

Text and SVG helpers in v4 split text and draw or morph SVG.

```js
const { words } = anime.splitText("#headline", { words: { wrap: "clip" } });
window.__hfAnime.push(anime.animate(words, { y: ["100%", "0%"], duration: 600, delay: anime.stagger(60), ease: "outExpo", autoplay: false }));

const [path] = anime.svg.createDrawable("#signature");
window.__hfAnime.push(anime.animate(path, { draw: ["0 0", "0 1"], duration: 1600, ease: "inOutQuad", autoplay: false }));
```

Split text after fonts load, as with any splitter; register at the end of that callback.

## Porting anime.js v3 code

Porting anime.js v3 code to v4 changes the call shapes.

| v3 | v4 |
|---|---|
| `anime({ targets: ".a", translateX: 250 })` | `anime.animate(".a", { x: 250 })` |
| `anime.timeline({...}).add({ targets, ... }, offset)` | `anime.createTimeline({...}).add(targets, {...}, position)` |
| `easing: "easeOutExpo"` | `ease: "outExpo"` |
| `direction: "alternate"`, `loop: true` | `alternate: true`, `loop: <finite count>` |
| `anime.running` | gone: push to `window.__hfAnime` yourself |
| bundles under `lib/` | bundles under `dist/bundles/` (since 4.1) |

## Verify the anime.js layer

```bash
npx hyperframes check --json                     # no errors, browser stage run
npx hyperframes keyframes --runtime all --json   # the anime.js tweens are listed at the times you planned
npx hyperframes snapshot --at 0.2,1.5,3          # the frames differ, so the adapter is seeking
```

Nothing listed by `keyframes` means an instance was never pushed to `window.__hfAnime`.

## Checklist

- [ ] Every instance created with `autoplay: false` and pushed to `window.__hfAnime`.
- [ ] Created synchronously, or pushed at the end of the callback that creates it.
- [ ] Finite `loop` counts; offsets in `delay` or timeline positions match the clip's start.
- [ ] Randomness from `anime.createSeededRandom`.
- [ ] `npx hyperframes check --json` passes and `keyframes --runtime all` shows the anime.js tweens.

## Gotchas

- **Symptom:** Animation plays ahead of the video. **Cause:** `autoplay` was left at its v4 default of `true`.
  **Fix:** pass `autoplay: false` on every instance.
- **Symptom:** Nothing moves and no error appears. **Cause:** The instance was never pushed to `window.__hfAnime`.
  **Fix:** push it right after creating it.
- **Symptom:** `anime is not a function`. **Cause:** v3 code against a v4 bundle; the v4 global is a namespace.
  **Fix:** call `anime.animate()` and port the shapes with the table above.
- **Symptom:** Half the motion freezes. **Cause:** Mixing the UMD bundle and an ESM import loads anime.js twice, and
  only one set was pushed. **Fix:** load one build, or push both sets.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `loop: true` on a clip | a finite `loop` count worked out from the clip's length |
| `anime.random()` or `Math.random()` in values | `anime.createSeededRandom(42)` |
| creating instances in a timer or a late promise | create them at init, or push at the end of the callback that builds them |
| `easing: "easeOutExpo"` from old examples | `ease: "outExpo"` |

## See also

`hyperframes`, `gsap`, `motion-design`.
