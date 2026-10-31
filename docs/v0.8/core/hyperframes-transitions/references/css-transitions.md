---
title: CSS scene transitions code
author: MOZGII, Inc.
lang: en
---

# CSS scene transitions code

A CSS scene transition is a handful of GSAP tweens on two scene containers (opacity, transforms, `clip-path`, filters)
plus, for some kinds, full-frame overlay elements, all placed on the root timeline at a start time `T`. Every snippet
on this page assumes three names: `A` for the outgoing scene's selector, `B` for the incoming scene's selector and
`T` for the start time in seconds, and two small helpers defined once in the template.

## Template every snippet plugs into

One root composition holds the scenes as untimed, full-frame `div`s (no `class="clip"`, no `data-start`); the root
alone carries timing. The first scene is visible at load, later scenes start at `opacity: 0`, and the helpers keep
the swap and the clean-up in one place:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #0d0d10; }
    .scene { position: absolute; inset: 0; overflow: hidden; }
    .later { opacity: 0; }
    .overlay { position: absolute; pointer-events: none; opacity: 0; z-index: 50; }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-start="0" data-duration="9">
    <section id="intro" class="scene" style="background:#14161b"><!-- first scene --></section>
    <section id="detail" class="scene later" style="background:#efe9df"><!-- next scene --></section>
    <!-- overlays a transition needs go here, e.g. <div id="cover-1" class="overlay"></div> -->
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    const A = "#intro", B = "#detail", T = 4.2;
    // Hard swap at time t: hide A, show B. Reversible because it is a timeline set, not a callback.
    const swap = (t) => { tl.set(A, { opacity: 0 }, t); tl.set(B, { opacity: 1 }, t); };
    // Put z-index and clip-path back to normal at time t after a transition that changed them.
    const settle = (t, ...sel) => sel.forEach((s) => tl.set(s, { zIndex: "auto", clipPath: "none" }, t));
    // ... one transition from the sections below ...
    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
```

## Rules that prevent real bugs

- **Overlays cover the whole frame.** Cover panels are 1920×1080, never thin strips; light-leak layers are bigger
  than the frame (2400 px or more) so their edges never show.
- **RGB glitch copies** use normal blending at about 35% opacity. `mix-blend-mode: multiply` disappears on dark
  backgrounds.
- **Overexposure** pushes `filter: brightness()` on the scene itself; a white overlay alone looks flat.
- **VHS tape** clones the real scene (`cloneNode(true)`) into strips wider than the frame (2020 px placed at
  `left: -50px`), with red and blue copies above them, offsets drawn from a seeded PRNG.
- **Stacking:** gravity drop, zoom out and diagonal split put the outgoing scene on top (`zIndex: 10`) so it can leave
  while the incoming scene waits underneath (`zIndex: 1`).
- **Page burn** hides the outgoing scene with `tl.set` at the burn's end, never in `onComplete`, which does not
  reverse; its `onUpdate` puts `clipPath: "none"` back when progress is 0, so seeking backwards works.
- **Clock wipe** needs a 9-point polygon with intermediate edge points and one tween per quadrant.
- **Grid dissolve** cycles five palette colours across the cells, not a single colour.
- **Blind counts by energy:** calm 4 horizontal or 6 vertical; medium 6 to 8 horizontal or 8 vertical; high 12 to 16.
- **Leave out in CSS:** star iris (polygon interpolation breaks), tilt-shift (no selective blur), lens flare (reads as
  a flat shape) and hinge or door (distorts too quickly).

## Blur amounts by energy

Every blur-based transition scales with the film's energy: about 20 to 30 px for calm pieces, often with a hold of
0.3 to 0.5 s at peak blur; 8 to 15 px for medium; 3 to 6 px with no hold for high energy.

## Push transitions

A push moves both scenes the same way at once, so the new scene reads as the next item in a sequence.

### Push Slide

```js
const pushX = (dir = 1, d = 0.5, ease = "power3.inOut") => {
  tl.fromTo(B, { x: 1920 * dir, opacity: 1 }, { x: 0, duration: d, ease }, T);
  tl.to(A, { x: -1920 * dir, duration: d, ease }, T);
};
pushX(1);            // from the right; pushX(-1) comes from the left
```

### Vertical Push

```js
tl.fromTo(B, { y: 1080, opacity: 1 }, { y: 0, duration: 0.5, ease: "power3.inOut" }, T);
tl.to(A, { y: -1080, duration: 0.5, ease: "power3.inOut" }, T);
```

### Elastic Push

The incoming scene overshoots, swings back and settles; the outgoing scene accelerates away.

```js
tl.to(A, { x: -1920, duration: 0.45, ease: "power3.in" }, T);
tl.fromTo(B, { x: 1920, opacity: 1 }, { x: 0, duration: 0.75, ease: "back.out(1.6)" }, T + 0.08);
```

### Squeeze

The outgoing scene collapses towards one edge while the incoming one unfolds from the other.

```js
tl.to(A, { scaleX: 0, transformOrigin: "0% 50%", duration: 0.4, ease: "power3.inOut" }, T);
tl.fromTo(B, { scaleX: 0, transformOrigin: "100% 50%", opacity: 1 }, { scaleX: 1, duration: 0.4, ease: "power3.inOut" }, T + 0.1);
tl.set(A, { opacity: 0, scaleX: 1 }, T + 0.5);
```

## Radial and shape transitions

A shape cut with `clip-path` grows on the incoming scene until it fills the frame.

### Circle Iris

A circle opens from a point, the centre by default or the spot that was clicked:

```js
const iris = (cx = 50, cy = 50, d = 0.5) => {
  tl.set(B, { opacity: 1, zIndex: 10 }, T);
  tl.fromTo(B, { clipPath: `circle(0% at ${cx}% ${cy}%)` },
    { clipPath: `circle(150% at ${cx}% ${cy}%)`, duration: d, ease: "power2.out" }, T);
  tl.set(A, { opacity: 0 }, T + d);
  settle(T + d + 0.01, B);
};
iris(72, 64, 0.45);   // open from a button at 72% / 64%
```

### Diamond Iris

```js
tl.set(B, { opacity: 1, zIndex: 10 }, T);
tl.fromTo(B, { clipPath: "polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%)" },
  { clipPath: "polygon(50% -25%, 125% 50%, 50% 125%, -25% 50%)", duration: 0.5, ease: "power2.out" }, T);
tl.set(A, { opacity: 0 }, T + 0.5);
settle(T + 0.51, B);
```

### Diagonal Split

The outgoing scene sits on top and shrinks into a triangle in one corner, uncovering the incoming scene.

```js
tl.set(B, { opacity: 1, zIndex: 1 }, T);
tl.set(A, { zIndex: 10, clipPath: "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)" }, T);
tl.to(A, { clipPath: "polygon(70% 0%, 100% 0%, 100% 30%, 100% 30%)", duration: 0.5, ease: "power3.inOut" }, T);
tl.set(A, { opacity: 0 }, T + 0.5);
settle(T + 0.5, A, B);
```

## Scale and zoom transitions

### Zoom Through

The camera rushes past the outgoing scene and the incoming one arrives from far behind.

```js
tl.to(A, { scale: 2.4, filter: "blur(10px)", opacity: 0, duration: 0.4, ease: "power3.in" }, T);
tl.fromTo(B, { scale: 0.6, filter: "blur(10px)", opacity: 0 },
  { scale: 1, filter: "blur(0px)", opacity: 1, duration: 0.45, ease: "power3.out" }, T + 0.15);
```

### Zoom Out

The outgoing scene, on top, shrinks away to show the incoming scene that was waiting underneath.

```js
tl.set(B, { opacity: 1, zIndex: 1 }, T);
tl.set(A, { zIndex: 10, transformOrigin: "50% 50%" }, T);
tl.to(A, { scale: 0.25, opacity: 0, duration: 0.4, ease: "power3.in" }, T);
settle(T + 0.4, A, B);
```

## 3D transitions

### 3D Card Flip

A half turn around the Y axis. The scene wrappers need `backface-visibility: hidden; transform-style: preserve-3d;`
and their parent `perspective: 1200px`.

```js
tl.set(B, { rotationY: -180, opacity: 1 }, T);
tl.to([A, B], { rotationY: "+=180", duration: 0.6, ease: "power2.inOut" }, T);
tl.set(A, { opacity: 0, rotationY: 0 }, T + 0.6);
```

## Dissolve transitions

Dissolves blend one scene into the next and so say "this continues".

### Crossfade

```js
tl.to(A, { opacity: 0, duration: 0.5, ease: "power2.inOut" }, T);
tl.fromTo(B, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, T);
```

### Blur Crossfade

A dissolve with a slight scale shift and blur; `px` follows the energy table above, `hold` adds a pause at peak blur
for calm films:

```js
const blurCross = (px = 10, d = 0.5, hold = 0) => {
  tl.to(A, { filter: `blur(${px}px)`, scale: 1.03, opacity: 0, duration: d, ease: "power2.inOut" }, T);
  tl.fromTo(B, { filter: `blur(${px}px)`, scale: 0.97, opacity: 0 },
    { opacity: 1, duration: d * 0.6, ease: "power1.inOut" }, T + d * 0.4);
  tl.to(B, { filter: "blur(0px)", scale: 1, duration: d, ease: "power2.out" }, T + d + hold);
};
blurCross(25, 0.6, 0.4);   // calm; blurCross(10) for medium, blurCross(5, 0.35) for high energy
```

### Focus Pull

The outgoing scene drifts out of focus while the incoming one appears sharp, like a lens racking focus.

```js
const focusPull = (px = 15, d = 0.5) => {
  tl.to(A, { filter: `blur(${px}px)`, duration: d, ease: "power1.in" }, T);
  tl.to(A, { opacity: 0, duration: d * 0.6, ease: "power2.in" }, T + d * 0.5);
  tl.fromTo(B, { opacity: 0 }, { opacity: 1, duration: d * 0.6, ease: "power2.out" }, T + d * 0.5);
};
focusPull(30, 0.8);   // calm, slow rack; focusPull() for medium
```

### Color Dip

Fade down to the background colour, hold a moment, fade up the new scene.

```js
tl.to(A, { opacity: 0, duration: 0.2, ease: "power2.in" }, T);
tl.fromTo(B, { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, T + 0.3);
```

## Blur transitions

### Blur Through

The heaviest blur: the picture dissolves into abstract colour before the next scene resolves out of it.

```js
tl.to(A, { filter: "blur(30px)", scale: 1.08, duration: 0.5, ease: "power1.in" }, T);
tl.to(A, { opacity: 0, duration: 0.3, ease: "power1.in" }, T + 0.3);
tl.fromTo(B, { filter: "blur(30px)", scale: 0.92, opacity: 0 }, { opacity: 1, duration: 0.25, ease: "none" }, T + 0.5);
tl.to(B, { filter: "blur(0px)", scale: 1, duration: 0.7, ease: "power1.out" }, T + 0.75);
```

### Directional Blur

Blur plus skew and travel, so the cut feels like fast sideways motion. Halve the skew and travel and double the
duration for calm films.

```js
const smear = (px = 12, skew = 8, dx = 200, d = 0.4) => {
  tl.to(A, { filter: `blur(${px}px)`, skewX: -skew, x: -dx, opacity: 0, duration: d, ease: "power3.in" }, T);
  tl.fromTo(B, { filter: `blur(${px}px)`, skewX: skew, x: dx, opacity: 0 },
    { filter: "blur(0px)", skewX: 0, x: 0, opacity: 1, duration: d, ease: "power3.out" }, T + d * 0.4);
};
smear();
```

## Cover transitions

Full-frame panels or strips cross the frame, and the scenes swap while they cover it.

### Staggered Color Blocks

Two or more full-frame panels in palette colours slide across one after another; five panels with a 0.04 s stagger
make the dense variant.

```js
const covers = ["#cover-1", "#cover-2"];           // 1920x1080 overlays in palette colours
covers.forEach((c, i) => {
  tl.fromTo(c, { x: -1920, opacity: 1 }, { x: 0, duration: 0.25, ease: "power3.inOut" }, T + i * 0.06);
  tl.to(c, { x: 1920, duration: 0.25, ease: "power3.inOut" }, T + 0.3 + i * 0.06);
});
swap(T + 0.26);                                    // the first panel has landed and covers the frame
```

### Horizontal Blinds

Full-width strips (`width: 1920px`) slide in one after another. Six strips of 180 px use a 0.03 s stagger; twelve of
90 px use 0.018 s.

```js
const blinds = (n, stagger, axis = "x") => {
  const far = axis === "x" ? 1920 : 1080;
  for (let i = 0; i < n; i++) {
    const s = `#blind-${i}`;
    tl.fromTo(s, { [axis]: -far, opacity: 1 }, { [axis]: 0, duration: 0.2, ease: "power3.inOut" }, T + i * stagger);
    tl.to(s, { [axis]: far, duration: 0.2, ease: "power3.inOut" }, T + 0.25 + n * stagger + i * stagger);
  }
  swap(T + 0.2 + (n - 1) * stagger);                // every strip is in place
};
blinds(6, 0.03);
```

### Vertical Blinds

Tall, narrow strips moving on Y: `blinds(8, 0.025, "y")` with strips of `height: 1080px`.

## Light transitions

Light transitions flood the frame with light and swap the scenes at the brightest moment.

### Light Leak

A flat warm tint plus two or three bright radial-gradient layers, all larger than the frame, drift across:

```js
// #leak-tint: full-frame amber at low opacity; #leak-a, #leak-b: 2400x1500 radial gradients
tl.to("#leak-tint", { opacity: 0.45, duration: 0.3, ease: "power1.in" }, T);
["#leak-a", "#leak-b"].forEach((s, i) =>
  tl.fromTo(s, { x: -200, opacity: 0 }, { x: 260 + i * 80, opacity: 0.85, duration: 0.55, ease: "sine.inOut" }, T + i * 0.08));
swap(T + 0.45);
tl.to(["#leak-tint", "#leak-a", "#leak-b"], { opacity: 0, duration: 0.4, ease: "power2.out", stagger: 0.05 }, T + 0.5);
```

### Overexposure Burn

The scene blows out with `filter: brightness()`, a white layer comes up, the swap happens at full white, and the
white falls away from the new scene.

```js
tl.to(A, { filter: "brightness(3)", scale: 1.06, duration: 0.4, ease: "power2.in" }, T);
tl.to("#white", { opacity: 1, duration: 0.4, ease: "power2.in" }, T + 0.15);
swap(T + 0.55);
tl.set(A, { filter: "brightness(1)", scale: 1 }, T + 0.55);
tl.to("#white", { opacity: 0, duration: 0.35, ease: "power2.out" }, T + 0.55);
```

### Film Burn

Amber, orange and red radial layers bleed in from one edge at slightly different times.

```js
["#burn-amber", "#burn-orange", "#burn-red"].forEach((s, i) => {
  tl.fromTo(s, { x: 0, opacity: 0 }, { x: -250 - i * 120, opacity: 1, duration: 0.42, ease: "power1.in" }, T + i * 0.05);
  tl.to(s, { opacity: 0, duration: 0.3, ease: "power2.out" }, T + 0.45 + i * 0.05);
});
swap(T + 0.35);
```

## Distortion transitions

Distortions break the image apart and fit tense, technical or retro films.

### Glitch

Red, green and blue tinted copies (normal blend, about 35% opacity) jump by large offsets for a few frames while the
scene itself jitters. Offsets come from a seeded PRNG so every render matches:

```js
let seed = 7;
const rnd = () => {   // -1..1, deterministic
  seed = seed + 0x2AC5E3B1 | 0;
  const mixed = Math.imul(seed ^ seed >>> 14, 0x4F2B71A3);
  return ((mixed ^ mixed >>> 16) >>> 0) / 2147483648 - 1;
};
for (let k = 0; k < 6; k++) {
  const t = T + k * 0.03;
  ["#rgb-r", "#rgb-g", "#rgb-b"].forEach((s) => tl.set(s, { opacity: 0.35, x: rnd() * 60, y: rnd() * 20 }, t));
  tl.set(A, { x: rnd() * 30 }, t);
}
swap(T + 0.18);
tl.set(["#rgb-r", "#rgb-g", "#rgb-b"], { opacity: 0, x: 0, y: 0 }, T + 0.21);
tl.set(A, { x: 0 }, T + 0.21);
```

### Chromatic Aberration

The colour copies start aligned, spread to about ±80 px as the scene fades, then close up on the new scene.

```js
tl.set(["#rgb-r", "#rgb-g", "#rgb-b"], { opacity: 0.6, x: 0, y: 0 }, T);
tl.to("#rgb-r", { x: -80, duration: 0.3, ease: "power2.in" }, T);
tl.to("#rgb-b", { x: 80, duration: 0.3, ease: "power2.in" }, T);
tl.to("#rgb-g", { y: 30, duration: 0.3, ease: "power2.in" }, T);
swap(T + 0.3);
tl.to(["#rgb-r", "#rgb-g", "#rgb-b"], { x: 0, y: 0, opacity: 0, duration: 0.3, ease: "power2.out" }, T + 0.3);
```

### Ripple

Fast side-to-side shake (up to ±30 px) with a slight scale wobble (0.97 to 1.03) and blur that grows to the swap,
then the incoming scene settles as the wobble dies down.

```js
const wobble = [30, -26, 22, -18, 14, -9, 5, 0];
wobble.forEach((dx, k) => {
  const target = k < 4 ? A : B;
  const blur = k < 4 ? (k + 1) * 2 : (7 - k) * 1.5;
  tl.to(target, { x: dx, scale: 1 + dx / 1000, filter: `blur(${Math.max(blur, 0)}px)`, duration: 0.04, ease: "none" }, T + k * 0.04);
});
swap(T + 0.16);
```

### VHS Tape

Split a clone of the real scene into 20 horizontal strips of 54 px (each clipped with `clip-path`), make the strips
2020 px wide at `left: -50px`, and shift each one sideways by its own seeded random offset at its own random moments.
Red and blue copies of each strip sit above it at 35% opacity. Build from clones of the scene, never from a picture
of it.

## Mechanical transitions

### Shutter

Two half-frame panels close from top and bottom, the scenes swap while they meet, and the panels open again.

```js
// #shut-top starts at y -540, #shut-bottom at y 540; both 1920x540
tl.to(["#shut-top", "#shut-bottom"], { y: 0, opacity: 1, duration: 0.25, ease: "power3.in" }, T);
swap(T + 0.25);
tl.to("#shut-top", { y: -540, duration: 0.25, ease: "power3.out" }, T + 0.3);
tl.to("#shut-bottom", { y: 540, duration: 0.25, ease: "power3.out" }, T + 0.3);
```

### Clock Wipe

A hand sweeps round from 12 o'clock. The polygon keeps nine points throughout, so GSAP can interpolate it; each
quadrant is its own linear tween:

```js
const q = 0.1;                                                  // seconds per quadrant
const C = "50% 50%", N = "50% 0%";
const steps = [
  [C, N, N, N, N, N, N, N, N],
  [C, N, "100% 0%", "100% 50%", "100% 50%", "100% 50%", "100% 50%", "100% 50%", "100% 50%"],
  [C, N, "100% 0%", "100% 50%", "100% 100%", "50% 100%", "50% 100%", "50% 100%", "50% 100%"],
  [C, N, "100% 0%", "100% 50%", "100% 100%", "50% 100%", "0% 100%", "0% 50%", "0% 50%"],
  [C, N, "100% 0%", "100% 50%", "100% 100%", "50% 100%", "0% 100%", "0% 50%", "0% 0%"],
].map((pts) => `polygon(${pts.join(", ")})`);
tl.set(B, { opacity: 1, zIndex: 10, clipPath: steps[0] }, T);
steps.slice(1).forEach((shape, i) => tl.to(B, { clipPath: shape, duration: q, ease: "none" }, T + i * q));
tl.set(A, { opacity: 0 }, T + 4 * q + 0.02);
settle(T + 4 * q + 0.02, B);
```

## Grid transitions

### Grid Dissolve

Coloured cells cover the frame in a ripple from the centre, the scenes swap at half coverage, and the cells clear in
the same ripple. Standard: 12 cells (4×3, 480×270 each). Dense: 120 cells (12×10, 160×108 each) at 0.75 opacity with
a tighter ripple. Build the cells once, synchronously, before registering the timeline:

```js
const cols = 4, rows = 3, w = 1920 / cols, h = 1080 / rows;
const palette = ["#ff5a36", "#ffd23f", "#3bceac", "#0ead69", "#540d6e"];
const cells = [];
for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
  const el = document.createElement("div");
  el.className = "overlay";
  Object.assign(el.style, { left: `${c * w}px`, top: `${r * h}px`, width: `${w}px`, height: `${h}px`,
    background: palette[(r * cols + c) % palette.length] });
  document.getElementById("root").appendChild(el);
  cells.push({ el, dist: Math.hypot(c + 0.5 - cols / 2, r + 0.5 - rows / 2) });
}
cells.sort((p, q2) => p.dist - q2.dist);
cells.forEach(({ el, dist }) => {
  tl.to(el, { opacity: 1, duration: 0.12, ease: "power1.out" }, T + dist * 0.08);
  tl.to(el, { opacity: 0, duration: 0.12, ease: "power1.in" }, T + 0.35 + dist * 0.08);
});
swap(T + cells[cells.length >> 1].dist * 0.08 + 0.12);   // half the cells are fully in
```

## Gravity and morph transitions

### Gravity Drop

The outgoing scene falls out of the frame with a small tilt, uncovering the incoming scene behind it.

```js
tl.set(B, { opacity: 1, zIndex: 1 }, T);
tl.set(A, { zIndex: 10 }, T);
tl.to(A, { y: 1250, rotation: 5, duration: 0.5, ease: "power3.in" }, T);
tl.set(A, { opacity: 0, y: 0, rotation: 0 }, T + 0.5);
settle(T + 0.5, A, B);
```

### Morph Circle

A circle in the next scene's background colour grows from the centre until it fills the frame; the new content then
appears on top.

```js
// #blob: a 100 px circle centred in the frame, background set to the incoming scene's colour
tl.fromTo("#blob", { scale: 0, opacity: 1 }, { scale: 30, duration: 0.5, ease: "power3.in" }, T);
swap(T + 0.42);
tl.to("#blob", { opacity: 0, duration: 0.15, ease: "power2.out" }, T + 0.5);
```

## Destruction transitions

### Page Burn

The outgoing page burns away from a corner and black shows through the holes before the next scene appears. Keep it
for hero moments; it is the most dramatic transition here. Three parts work together:

1. **The fire front:** a radius growing from a corner, made ragged by a deterministic noise function of angle and
   progress.
2. **The clip:** an SVG clip-path with `fill-rule: evenodd` cuts the burning area out of the outgoing scene, so text,
   images and lines all burn with the page. No clones and no falling debris.
3. **The char line:** a `<canvas>` above the scene paints a dark radial fringe along the burn edge.

```js
// Smooth value noise: hash two neighbouring integers, blend with a smoothstep.
const hash = (n) => { const a = Math.imul(n ^ 0x2AC5E3B1, 0x4F2B71A3), b = Math.imul(a ^ a >>> 15, 0x1D8E6A35); return ((b ^ b >>> 16) >>> 0) / 4294967296; };
const smoothNoise = (x) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return hash(i) * (1 - u) + hash(i + 1) * u; };
const flameRadius = (angle, p, maxR) =>
  p * maxR + 48 * smoothNoise(angle * 3 + p * 4) + 22 * smoothNoise(angle * 8 + p * 9) + 9 * smoothNoise(angle * 15 + p * 15);

const BURN = 1.6, burn = { p: 0 };
tl.to(burn, {
  p: 1, duration: BURN, ease: "none",
  onUpdate() {
    const page = document.querySelector(A);
    page.style.clipPath = burn.p <= 0 ? "none" : clipFor(burn.p);   // clipFor builds the evenodd path from flameRadius
    drawCharLine(burn.p);                                          // canvas fringe at the same radius
  },
}, T);
tl.set(A, { opacity: 0, clipPath: "none" }, T + BURN);              // reversible end, never onComplete

// The new scene stays dark during the burn, then rises out of black near the end.
const rise = T + BURN * 0.9;
tl.fromTo(B, { opacity: 0 }, { opacity: 1, duration: 1.2, ease: "power1.out" }, rise);
tl.fromTo(`${B} h1`, { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power1.out" }, rise + 0.5);
tl.fromTo(`${B} p`, { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "power1.out" }, rise + 0.7);
```

`onUpdate` advances the clip and the char line on every seek, and the closing `tl.set` hides the page in a way GSAP
reverses when someone scrubs backwards, restoring the outgoing scene to full opacity.
