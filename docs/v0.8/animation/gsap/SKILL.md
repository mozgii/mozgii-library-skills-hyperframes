---
name: gsap
description: Writes GSAP 3 animation for seek-rendered video in HyperFrames - paused timelines registered on window.__timelines, the position parameter, fromTo for entrances, eases, staggers, labels, finite repeats, function-based values, and plugins (SplitText, DrawSVG, MorphSVG, MotionPath, TextPlugin, ScrambleText, CustomEase) that are now free. Use when writing or debugging any GSAP tween or timeline in a video composition, or when motion renders differently from the preview.
metadata:
  tags:
  - gsap
  - animation
  - timeline
  - easing
  - stagger
  - splittext
  - hyperframes
---

# GSAP for video

GSAP is the default animation engine for HyperFrames. In a video, a GSAP timeline is never played: it is created
paused, registered, and seeked by the renderer to each frame's time. Everything below follows from that. Checked
against GSAP 3.15.0. Since version 3.13 every GSAP plugin, including SplitText, MorphSVG and
DrawSVG, ships in the public `gsap` package at no charge under GSAP's own standard licence.

## When to use this skill

Use this skill when writing tweens or timelines in a composition, choosing eases and staggers, splitting text,
drawing SVG lines, or when a GSAP animation looks right in preview and wrong in the render.

## Step 0: read the GSAP version the film loads

```bash
grep -rhoE 'gsap@[0-9]+\.[0-9]+\.[0-9]+' --include='*.html' . | sort -u   # pinned in script tags
npm ls gsap --depth=0 2>/dev/null                                       # a bundled project
```

Below 3.13 SplitText, MorphSVG and DrawSVG are not in the public package. Every plugin tag must carry the same
version as the core tag.

## The timeline contract for video

The timeline contract for video has four parts.

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#title", { y: 48, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "expo.out" }, 0.3);
  tl.fromTo("#rule", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power3.out" }, 0.45);
  window.__timelines["intro"] = tl;   // key = the composition's data-composition-id
</script>
```

1. Create the timeline with `{ paused: true }` and never call `play()`, `restart()` or `reverse()`.
2. Register it on `window.__timelines` under the composition's `data-composition-id`, after the tweens are added.
3. Build it synchronously, or register at the end of the async callback that builds it.
4. Place tweens at absolute seconds with the position parameter; the clip's `data-duration` sets length, never an
   empty tween.

## Tween methods

Tween methods differ in where the start state comes from.

| Method | Start state | Use in video |
|---|---|---|
| `tl.fromTo(el, from, to, t)` | written in the call | entrances and anything a scene re-seeks |
| `tl.to(el, vars, t)` | the current value | exits and changes from a known CSS state |
| `tl.from(el, vars, t)` | recorded once at creation | avoid inside scenes; it drifts on seek-back |
| `tl.set(el, vars, t)` | none, instant | hard switches at a time (a caption kill, a scene swap) |

`from` and `fromTo` render their start state immediately (`immediateRender: true`). On a clip that starts after 0,
that can flash the start state at load; `fromTo` with the start written in the call, or `immediateRender: false`,
avoids it.

## The position parameter

The position parameter, the third argument, places a tween on the timeline.

| Value | Meaning |
|---|---|
| `2.4` | at 2.4 s (preferred in video: absolute and readable) |
| `"<"`, `"<0.2"` | with, or 0.2 s after, the previous tween's start |
| `">"`, `">-0.1"` | at, or 0.1 s before, the previous tween's end |
| `"+=0.5"`, `"-=0.2"` | relative to the timeline's current end |
| `"hero"`, `"hero+=0.3"` | at, or after, a label made with `tl.addLabel("hero", 4)` |

Absolute times match transcript and beat times directly; relative positions are fine inside one group of tweens.

## Properties to animate

Properties to animate in video are transforms, opacity, colours, filters and clip paths.

| GSAP property | CSS effect |
|---|---|
| `x`, `y`, `xPercent`, `yPercent` | translate |
| `scale`, `scaleX`, `scaleY` | scale |
| `rotation`, `rotationX`, `rotationY`, `skewX` | rotate and skew (3D with `transformPerspective`) |
| `transformOrigin`, `svgOrigin` | pivot (never both on one SVG element) |
| `opacity`, `color`, `backgroundColor` | fade and colour |
| `filter: "blur(8px)"`, `clipPath`, `"--custom-prop"` | blur, masks, CSS variables |

Never set a CSS `transform` on an element GSAP transforms: GSAP owns `transform` and the two fight. Never tween
`display`, `visibility` or `autoAlpha` on a HyperFrames `.clip`. A `<span>` needs `display: inline-block` for
transforms.

## Eases

Eases give a move its character. Use them by role, and vary them within a scene.

| Role | Eases |
|---|---|
| An arrival that settles | `expo.out`, `power4.out`, `power3.out` |
| A camera move or colour flood | `power2.inOut`, `sine.inOut` |
| An exit or zoom through | `power3.in`, `power2.in` |
| A playful overshoot | `back.out(1.4)`, `elastic.out(1, 0.5)` |
| Constant speed (rotation, progress, scroll) | `"none"` |

Custom curves: `CustomEase.create("brand", "M0,0 C0.2,0 0,1 1,1")` after registering CustomEase. Motion craft (timings,
holds, springs, overlap): `motion-design`.

## Staggers and function-based values

Staggers and function-based values animate many elements from one call.

```js
tl.fromTo(".word", { opacity: 0, filter: "blur(6px)" },
  { opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out", stagger: 0.067 }, 1.2);
tl.fromTo(".bar", { scaleY: 0 }, { scaleY: (i, el) => Number(el.dataset.value) / 100,
  transformOrigin: "50% 100%", duration: 0.8, ease: "power3.out", stagger: { each: 0.06, from: "start" } }, 2);
```

`stagger: { from: "random" }` uses GSAP's own random order, which is not seeded: use `from: "center"`, `"edges"`, an
index, or compute the order with a seeded PRNG.

## Finite repeats

Finite repeats replace `repeat: -1`, which video cannot render. Compute the count from the time available:

```js
const cycle = 1.2, available = 8;
tl.to("#pulse", { scale: 1.06, duration: cycle / 2, yoyo: true, ease: "sine.inOut",
  repeat: Math.max(0, Math.floor(available / (cycle / 2)) - 1) }, 2);
```

## Plugins

Plugins load from the same CDN version and are registered once.

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/SplitText.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/DrawSVGPlugin.min.js"></script>
<script>gsap.registerPlugin(SplitText, DrawSVGPlugin);</script>
```

SplitText, DrawSVG, MorphSVG, MotionPath, TextPlugin, ScrambleText and CustomEase patterns for video:
[references/plugins.md](references/plugins.md). Drop-in effects (typewriter, counters, highlight sweeps):
[references/effects.md](references/effects.md).

## Verify the timeline

```bash
npx hyperframes check --json                 # no errors
npx hyperframes keyframes --json --selector '#title'   # property, time, value and ease of each keyframe
npx hyperframes snapshot --at 0,0.5,1        # frame 0 holds the start state, later frames move
grep -rnE 'repeat: *-1|\.play\(\)|Math\.random' compositions index.html   # expect nothing
```

Scrub backwards in Studio once: state set in a callback shows up there first.

## Checklist

- [ ] One paused timeline per composition, registered under its `data-composition-id` after its tweens.
- [ ] Entrances use `fromTo`; no CSS `transform` on GSAP-transformed elements.
- [ ] Tweens at absolute seconds that match the script, beats or transcript.
- [ ] No `repeat: -1`, no unseeded random staggers, no `Math.random()` in values.
- [ ] Two timelines never animate the same property of one element.
- [ ] Layout measured once before building tweens, never inside `onUpdate`.
- [ ] Plugins loaded at the same version as core and registered.

## Gotchas

- **Symptom:** Animation renders at its end state on frame 0. **Cause:**
  The timeline was created without `paused: true` and ran on its own clock. **Fix:** create it with `{ paused: true
  }`.
- **Symptom:** Nothing moves and no error appears. **Cause:** The `window.__timelines` key differs from
  `data-composition-id`. **Fix:** use one string in both.
- **Symptom:** An element flies off screen. **Cause:** CSS centred it with `transform: translate(-50%, -50%)` and GSAP
  replaced the transform. **Fix:** centre with flexbox or grid, or use `xPercent: -50, yPercent: -50` in GSAP.
- **Symptom:** Wrong state after scrubbing back. **Cause:** A scene used `from`, or state was changed in `onComplete`
  or `tl.call`. **Fix:** use `fromTo` and `tl.set` at a time.
- **Symptom:** SplitText lines break differently in render. **Cause:** Text was split before the web font loaded.
  **Fix:** split after `document.fonts.ready` and register the timeline at the end of that callback.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `tl.play()`, `restart()` or `reverse()` | leave the timeline paused; the renderer seeks it |
| an empty tween to pad the length | the clip's `data-duration` |
| `stagger: { from: "random" }` | `from: "center"`, `"edges"`, an index, or an order from a seeded PRNG |
| measuring layout in `onUpdate` | measure once before building tweens |
| `left` and `top` for movement | `x` and `y` |

## References

- [references/plugins.md](references/plugins.md): SplitText, DrawSVG, MorphSVG, MotionPath, TextPlugin, ScrambleText, CustomEase in seek-rendered video.
- [references/effects.md](references/effects.md): typewriter with cursor, count-up numbers, word rotation, highlight sweeps, progress bars.

## See also

`hyperframes`, `motion-design`, `hyperframes-transitions`.
