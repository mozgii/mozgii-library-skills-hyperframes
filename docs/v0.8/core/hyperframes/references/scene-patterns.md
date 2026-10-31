---
title: HyperFrames scene patterns
author: MOZGII, Inc.
lang: en
---

# HyperFrames scene patterns

HyperFrames scene patterns are small, tested shapes for common pieces of a video: a title card, picture-in-picture,
a run of slides on one track and a lower third. Each follows the composition contract; adapt sizes and eases to the
brand.

## Title card pattern

A title card is a full-frame clip with one or two lines that enter, hold dead still, and leave.

```html
<div id="title-card" class="clip" data-start="0" data-duration="4" data-track-index="2"
     style="position:absolute;inset:0;display:grid;place-items:center;background:#101114;z-index:10">
  <h1 id="title-card-line" style="font:800 112px/1.05 Inter,sans-serif;color:#f5f2ea;max-width:1400px;text-align:center">
    The quiet launch
  </h1>
</div>
```

```js
tl.fromTo("#title-card-line", { opacity: 0, filter: "blur(8px)" },
  { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 0.3);
tl.to("#title-card-line", { opacity: 0, filter: "blur(6px)", duration: 0.2, ease: "power2.in" }, 3.6);
```

The line is readable for 3.1 s, longer than the 2 s minimum for a final line and well over 0.5 s + 0.3 s per word.

## Picture-in-picture pattern

Picture-in-picture shrinks full-frame footage into a corner while other content takes the frame. Animate an untimed
wrapper; the timed `<video>` fills it.

```html
<div id="pip-frame" style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;z-index:50">
  <video id="pip-video" class="clip" src="assets/talk.mp4" playsinline data-has-audio="true"
         data-start="0" data-duration="40" data-track-index="0" style="width:100%;height:100%;object-fit:cover"></video>
</div>
```

```js
tl.to("#pip-frame", { left: 1360, top: 700, width: 500, height: 282, borderRadius: 18, duration: 0.9, ease: "power3.inOut" }, 10);
tl.to("#pip-frame", { left: 60, duration: 0.6, ease: "power2.inOut" }, 30);
```

Animating `left`, `top`, `width` and `height` on the wrapper is acceptable here because it reflows only one box; for
long or heavy moves use `scale` and `x`/`y`.

## Slides on one track

Slides on one track are sibling clips with back-to-back time ranges on the same `data-track-index`. The runtime
mounts and unmounts each by its range; give each one entrance and let the next slide's arrival be the exit.

```html
<section id="slide-1" class="clip slide" data-start="0" data-duration="6" data-track-index="3">...</section>
<section id="slide-2" class="clip slide" data-start="6" data-duration="5" data-track-index="3">...</section>
<section id="slide-3" class="clip slide" data-start="11" data-duration="7" data-track-index="3">...</section>
```

For a deck that is presented live rather than rendered, use `hyperframes-slideshow`.

## Lower third pattern

A lower third is a name and role band over footage, kept inside the 80% title-safe box and clear of captions.

```html
<div id="lt" class="clip" data-start="2" data-duration="5" data-track-index="4"
     style="position:absolute;left:144px;bottom:160px;z-index:20">
  <div id="lt-bar" style="height:6px;width:420px;background:#ff5a36;transform-origin:left center"></div>
  <div id="lt-name" style="font:700 54px Inter,sans-serif;color:#fff;margin-top:18px">Ada Moreno</div>
  <div id="lt-role" style="font:500 30px Inter,sans-serif;color:#cfd3da">Head of Research</div>
</div>
```

```js
tl.fromTo("#lt-bar", { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "expo.out" }, 2.1);
tl.fromTo("#lt-name", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 2.25);
tl.fromTo("#lt-role", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 2.4);
tl.to(["#lt-name", "#lt-role", "#lt-bar"], { opacity: 0, duration: 0.25, ease: "power2.in", stagger: 0.04 }, 6.6);
```

Before hand-building a lower third, search the registry (`npx hyperframes catalog --query "lower third" --json`).
