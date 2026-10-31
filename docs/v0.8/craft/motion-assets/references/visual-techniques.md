---
title: Visual techniques for video scenes
author: MOZGII, Inc.
lang: en
---

# Visual techniques for video scenes

Visual techniques are the building blocks a scene can mix: SVG path drawing, canvas procedural art, CSS 3D, per-word kinetic type, Lottie, footage, typing, variable font axes, motion paths, velocity-matched cuts and audio-reactive motion. A strong beat uses two or three of them, not one fade. `tl` is the scene's paused timeline.

## Contents

The sections of this page:

- SVG path drawing
- Canvas 2D procedural art
- CSS 3D transforms
- Per-word kinetic typography
- Lottie in a scene
- Video compositing
- Character-by-character typing
- Variable font axis animation
- Motion along a path
- Velocity-matched transitions
- Audio-reactive animation
- Choosing techniques by energy

## SVG path drawing

SVG path drawing makes a path draw itself, like someone tracing with a pen. Use for revealing diagrams, arrows, connector lines, or brand marks.

```html
<svg viewBox="0 0 400 200">
  <path
    class="draw-path"
    d="M 50 100 L 200 50 L 350 100"
    stroke="#c84f1c"
    stroke-width="4"
    fill="none"
    stroke-linecap="round"
  />
</svg>
<style>
  .draw-path {
    /* the path is 316.2 long: a smaller dash leaves its tail showing before the draw starts */
    stroke-dasharray: 317;
    stroke-dashoffset: 317;
  }
</style>
<script>
  tl.to(".draw-path", { strokeDashoffset: 0, duration: 0.7, ease: "power2.out" }, 0.5);
</script>
```

Use `path.getTotalLength()` to calculate the dasharray value dynamically.

## Canvas 2D procedural art

Canvas 2D procedural art covers noise, particle fields and data visualisations that change over time. Drive it with a GSAP proxy.

```html
<canvas id="proc-canvas" width="1920" height="1080"></canvas>
<script>
  var canvas = document.getElementById("proc-canvas");
  var ctx = canvas.getContext("2d");

  function hash(x, y) {
    const mixed = Math.imul(x ^ 0x2AC5E3B1, 0x4F2B71A3) ^ Math.imul(y ^ 0x6C1F3A9D, 0x1D8E6A35);
    const folded = Math.imul(mixed ^ mixed >>> 15, 0x5B3E8C27);
    return ((folded ^ folded >>> 16) >>> 0) / 4294967296;
  }

  function drawFrame(t) {
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, 1920, 1080);
    for (var i = 0; i < 200; i++) {
      var x = hash(i, 0) * 1920;
      var y = hash(i, 1) * 1080;
      var brightness = hash(i, Math.floor(t * 10)) * 255;
      ctx.fillStyle = "rgba(255, 255, 255, " + brightness / 255 + ")";
      ctx.beginPath();
      ctx.arc(x, y, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  var proxy = { time: 0 };
  tl.to(
    proxy,
    {
      time: 5,
      duration: 5,
      ease: "none",
      onUpdate: function () {
        drawFrame(proxy.time);
      },
    },
    0,
  );
</script>
```

The `hash()` function is deterministic, same frame renders identically every time.

## CSS 3D transforms

CSS 3D transforms use perspective rotations to create depth. Use for product showcases, card flips, architectural reveals.

```html
<style>
  .card-3d { position: relative; width: 640px; height: 360px; }
  .face {
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    border-radius: 24px; background: var(--surface); font: 800 80px/1 var(--font-display);
    backface-visibility: hidden; /* or the back face shows through, mirrored */
  }
</style>
<div class="stage" style="perspective: 900px;">
  <div class="card-3d" style="transform-style: preserve-3d;">
    <div class="face front">Product</div>
    <div class="face back" data-layout-allow-overlap style="transform: rotateY(180deg);">Details</div>
  </div>
</div>
<script>
  tl.to(".card-3d", { rotationY: 360, rotationX: 15, duration: 1.2, ease: "sine.inOut" }, 0);
</script>
```

Always set `perspective` on the parent, `transform-style: preserve-3d` on the animated element.

## Per-word kinetic typography

Per-word kinetic typography shows words one by one, synced to transcript timestamps. The core technique for narration-driven videos.

```html
<div class="headline">
  <span class="word w-0">Anything</span>
  <span class="word w-1">a</span>
  <span class="word w-2">browser</span>
  <span class="word w-3">can</span>
  <span class="word w-4">render</span>
</div>
<style>
  .word {
    display: inline-block;
    opacity: 0;
    margin: 0 0.12em;
  }
</style>
<script>
  // Word onset times from transcript.json (seconds relative to beat start)
  var timings = [0.0, 0.23, 0.28, 0.63, 0.78];
  var slides = [80, 60, 50, 25, 12]; // horizontal slide decay (px)

  document.querySelectorAll(".word").forEach(function (word, i) {
    tl.fromTo(
      word,
      { x: slides[i], y: 14, opacity: 0 },
      { x: 0, y: 0, opacity: 1, duration: 0.35, ease: "power2.out" },
      timings[i],
    );
  });
</script>
```

The slide distance DECAYS per word (80→12px), mimics a camera settling.

## Lottie in a scene

Lottie in a scene plays vector animation inside a composition: logos, characters, icons. The player is created paused
and registered, and HyperFrames seeks it; a wrapper carries any GSAP entrance so the player and the tween never fight.

```html
<div id="badge-wrap" style="width:500px;height:500px"><div id="badge" style="width:100%;height:100%"></div></div>
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.13.0/build/player/lottie.min.js"></script>
<script>
  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(lottie.loadAnimation({
    container: document.getElementById("badge"), renderer: "svg",
    loop: false, autoplay: false, path: "assets/badge.json",
  }));
  tl.fromTo("#badge-wrap", { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 0.2);
</script>
```

Never use `autoplay`, `play()` or a `speed` attribute: the adapter sets the frame from composition time. The `lottie`
skill covers dotLottie files and theming.

## Video compositing

Video compositing places real footage inside a composition. Silent footage is `muted playsinline`; footage with sound is `playsinline data-has-audio="true"`.

```html
<div class="video-frame" style="width:680px;height:840px;border-radius:16px;overflow:hidden;">
  <video
    id="footage"
    src="assets/clip.mp4" class="clip" data-start="0" data-duration="6"
    muted
    playsinline
    style="width:100%;height:100%;object-fit:cover;"
  ></video>
</div>
<script>
  // Video playback is controlled by the framework — don't call play() manually
  tl.fromTo(".video-frame", { scale: 0.9, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power2.out" }, 0);
</script>
```

The HyperFrames runtime handles video seeking and playback.

## Character-by-character typing

Character-by-character typing types a command or code line one character at a time. Drive it from a tween's progress,
not from `tl.call()` callbacks: seeking does not replay callbacks in order, so a render that jumps to a frame would show
the wrong text.

```html
<div class="terminal-line">
  <span class="prompt">❯</span> <span class="typed" id="typed-text"></span><span id="caret"
    style="width:11px;height:22px;background:currentColor;display:inline-block;vertical-align:-3px"></span>
</div>
<script>
  const CMD = "npx hyperframes init";
  const typed = document.getElementById("typed-text");
  const p = { n: 0 };
  tl.to(p, { n: CMD.length, duration: CMD.length / 14, ease: "none",
    onUpdate: () => { typed.textContent = CMD.slice(0, Math.round(p.n)); } }, 0.4);
  // caret blinks after typing ends: finite steps at fixed times
  const end = 0.4 + CMD.length / 14;
  for (let k = 0; k < 6; k++) tl.set("#caret", { opacity: k % 2 ? 1 : 0 }, end + k * 0.4);
</script>
```

GSAP's TextPlugin does the same with `text: { value: CMD }` (see `gsap`).

## Variable font axis animation

Variable font axis animation tweens font-variation-settings to reshape glyphs in real-time. Works with variable fonts that have axes like optical size (opsz), weight (wght), softness (SOFT).

```html
<style>
  /* Load the captured local variable font — do NOT use Google Fonts @import.
     Point the @font-face at a variable font file in assets/fonts/. */
  @font-face {
    font-family: "Fraunces";
    src: url("assets/fonts/Fraunces-Variable.woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: block;
  }
  .wordmark {
    --opsz: 144;
    --wght: 440;
    font-family: "Fraunces", serif;
    font-variation-settings:
      "opsz" var(--opsz),
      "wght" var(--wght);
    font-size: 200px;
  }
</style>
<div class="wordmark">Fraunces</div>
<script>
  tl.to(".wordmark", { "--opsz": 72, "--wght": 300, duration: 0.45, ease: "power2.out" }, 0);
</script>
```

The glyph subtly reshapes as axes animate, optical size adjusts detail, weight changes thickness.

## Motion along a path

Motion along a path moves an element along any SVG path with MotionPathPlugin. Use for sliders following curves, particles along trajectories, guided reveals.

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/MotionPathPlugin.min.js"></script>
<div class="dot" style="width:20px;height:20px;background:#2a8a7c;border-radius:50%;"></div>
<script>
  gsap.registerPlugin(MotionPathPlugin);
  tl.to(
    ".dot",
    {
      motionPath: { path: "M 12 300 C 280 280 520 80 820 50 S 1200 48 1308 38" },
      duration: 1.5,
      ease: "power2.out",
    },
    0,
  );
</script>
```

## Velocity-matched transitions

Velocity-matched transitions exit one beat and enter the next with matched velocities, creates perceived continuous motion. `beatDuration` is the outgoing beat's length in seconds.

```javascript
// EXIT (in outgoing composition): accelerating with blur
tl.to(
  ".content",
  {
    y: -150,
    filter: "blur(30px)",
    opacity: 0,
    duration: 0.33,
    ease: "power2.in", // accelerates
  },
  beatDuration - 0.33,
);

// ENTRY (in incoming composition): decelerating from blur
gsap.set(".content", { y: 150, filter: "blur(30px)" });
tl.to(
  ".content",
  {
    y: 0,
    filter: "blur(0px)",
    duration: 1.0,
    ease: "power2.out", // decelerates
  },
  0,
);
```

The fastest point of both curves meets at the cut, the viewer perceives smooth camera motion. Match ease families: `.in` for exits, `.out` for entries.

## Audio-reactive animation

Audio-reactive animation drives a property from pre-extracted audio levels: bass pulses a logo, treble brightens a
glow. Extract per-frame bands once with the `audio-sync` skill's script, embed the JSON, and read the frame for the
current time inside one long tween's `onUpdate`, which is a pure function of time and so seeks correctly. Never build it
from one `tl.call()` per frame.

```js
// AUDIO = { fps: 30, frames: [{ rms: 0.4, bands: [0.82, 0.45, ...] }, ...] }
const clock = { t: 0 }, D = AUDIO.frames.length / AUDIO.fps;
tl.to(clock, { t: D, duration: D, ease: "none", onUpdate: () => {
  const f = AUDIO.frames[Math.min(AUDIO.frames.length - 1, Math.floor(clock.t * AUDIO.fps))];
  gsap.set(".logo", { scale: 1 + f.bands[0] * 0.04 });                       // 3 to 4% on bass
  gsap.set(".cta", { filter: `drop-shadow(0 0 ${Math.round(f.bands[f.bands.length - 1] * 24)}px #00c3ff)` });
} }, 0);
```

Keep text and logos subtle (5% scale or less, 30% glow or less); backgrounds can take 10 to 30%. Avoid equaliser bars,
spectrum analysers, strobing and rainbow cycling: the audio gives timing and intensity, the brand gives the look.

## Choosing techniques by energy

Choosing techniques by energy pairs the techniques that suit each kind of video.

| Video energy                   | Techniques to combine                                           |
| ------------------------------ | --------------------------------------------------------------- |
| High impact (launches, promos) | Per-word typography + velocity transitions + counter animations |
| Cinematic (tours, stories)     | SVG path drawing + video compositing + 3D transforms            |
| Technical (dev tools, APIs)    | Character typing + Canvas 2D procedural + MotionPath            |
| Premium (luxury, enterprise)   | Variable font animation + Lottie + slow velocity transitions    |
| Data-driven (stats, metrics)   | Canvas 2D procedural + counter animations + SVG path drawing    |
