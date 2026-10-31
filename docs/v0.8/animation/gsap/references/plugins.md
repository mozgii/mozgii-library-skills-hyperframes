---
title: GSAP plugins in seek-rendered video
author: MOZGII, Inc.
lang: en
---

# GSAP plugins in seek-rendered video

GSAP plugins add text splitting, SVG drawing, shape morphing, path motion, text replacement and custom eases. All of
them ship in the `gsap` npm package and on the CDN at the same version as the core (3.15.0 here). Each plugin is
loaded with its own script and registered once with `gsap.registerPlugin()`. In video, plugin tweens obey the same
rules as any tween: placed on the paused timeline, finite, seekable.

## Contents

The sections of this page:

- SplitText for words, lines and characters
- DrawSVG for line drawing
- MorphSVG for shape morphs
- MotionPath for movement along a path
- TextPlugin for typed and replaced text
- ScrambleText for decoding text
- CustomEase and CustomBounce

## SplitText for words, lines and characters

SplitText splits an element's text into word, line or character elements that can be staggered. Split after fonts
have loaded, so line breaks match the render, and register the timeline at the end of that callback.

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/SplitText.min.js"></script>
<script>
  gsap.registerPlugin(SplitText);
  const tl = gsap.timeline({ paused: true });
  document.fonts.ready.then(() => {
    const split = SplitText.create("#headline", { type: "lines,words", mask: "lines" });
    tl.fromTo(split.lines, { yPercent: 110 }, { yPercent: 0, duration: 0.7, ease: "expo.out", stagger: 0.08 }, 0.4);
    tl.fromTo(split.words, { opacity: 0.25 }, { opacity: 1, duration: 0.3, stagger: 0.05 }, 0.6);
    window.__timelines["intro"] = tl;   // register last
  });
</script>
```

- `mask: "lines"` wraps each line in a clipping element, which makes clean line reveals.
- Leave `autoSplit` off in video: the frame size never changes, and a re-split after the timeline is built would
  orphan the tweens.
- Splitting replaces the element's children; keep `data-var-text` bindings on a parent, or split after variables
  are applied.

## DrawSVG for line drawing

DrawSVG animates how much of an SVG stroke is visible, for signatures, diagrams, underlines and route lines.

```js
gsap.registerPlugin(DrawSVGPlugin);
tl.fromTo("#route", { drawSVG: "0%" }, { drawSVG: "100%", duration: 1.6, ease: "power2.inOut" }, 1);
tl.fromTo("#underline", { drawSVG: "50% 50%" }, { drawSVG: "0% 100%", duration: 0.5, ease: "expo.out" }, 2.2);
```

Without the plugin, the same effect uses `stroke-dasharray` and `stroke-dashoffset` with `pathLength="100"`. To hide a
line with round caps completely, make the gap longer than the whole path (`stroke-dasharray="100 120"`, `stroke-dashoffset="110"`), or a dot
remains at the end on some curves.

## MorphSVG for shape morphs

MorphSVG morphs one SVG path into another even when the point counts differ, for icon changes and blob shapes.

```js
gsap.registerPlugin(MorphSVGPlugin);
tl.to("#icon-play", { morphSVG: "#icon-pause", duration: 0.5, ease: "power3.inOut" }, 3);
tl.to("#blob", { morphSVG: { shape: "#blob-b", shapeIndex: "auto" }, duration: 1.2, ease: "sine.inOut" }, 4);
```

Convert circles and rectangles first with `MorphSVGPlugin.convertToPath("circle, rect")`. Use `shapeIndex` to stop a
morph from twisting.

## MotionPath for movement along a path

MotionPath moves an element along an SVG path or a list of points, optionally rotating it to follow the path.

```js
gsap.registerPlugin(MotionPathPlugin);
tl.to("#plane", { duration: 3, ease: "power1.inOut",
  motionPath: { path: "#flight", align: "#flight", alignOrigin: [0.5, 0.5], autoRotate: true } }, 1);
```

Combine with DrawSVG on the same path to draw the trail behind the moving element.

## TextPlugin for typed and replaced text

TextPlugin replaces an element's text over a tween, which makes typewriter effects deterministic.

```js
gsap.registerPlugin(TextPlugin);
const line = "npx hyperframes render";
tl.to("#cmd", { text: { value: line }, duration: line.length / 14, ease: "none" }, 1);
```

14 characters a second reads as fast typing; 8 to 12 conversational; 3 to 5 dramatic.

## ScrambleText for decoding text

ScrambleText reveals text through random characters, for technical or "decoding" moments. Its randomness is not
seeded, so frames can differ between renders; use it only where that variance is invisible, or build the effect with a
seeded PRNG instead (see the effects reference).

```js
gsap.registerPlugin(ScrambleTextPlugin);
tl.to("#code", { scrambleText: { text: "ACCESS GRANTED", chars: "01", speed: 0.4 }, duration: 1.2 }, 2);
```

## CustomEase and CustomBounce

CustomEase defines an ease from an SVG path or cubic-bezier, for a brand's signature motion or a curve ported from
After Effects or CSS.

```js
gsap.registerPlugin(CustomEase);
CustomEase.create("brand-out", "0.16, 1, 0.3, 1");          // cubic-bezier shorthand
CustomEase.create("hop", "M0,0 C0.3,0 0.2,1.2 0.6,1 0.8,0.95 0.9,1 1,1");
tl.fromTo("#card", { y: 80 }, { y: 0, duration: 0.6, ease: "brand-out" }, 1);
```

CustomBounce (with CustomEase loaded) makes a bounce ease and its matching squash ease for a landing object.
