---
title: Porting Remotion timing, springs and easing
author: MOZGII, Inc.
lang: en
---

# Porting Remotion timing, springs and easing

Porting Remotion timing is the part of a port viewers notice most: a wrong ease or a spring that settles late reads as
"off" even when every element is in place. This page converts frame maths to GSAP tweens and explains how to read
SSIM results.

## Contents

The sections of this page:

- Frames to seconds
- Linear interpolate
- Multi-point interpolate
- Springs as GSAP eases
- Easing equivalents
- Colour and number tweens
- Reading SSIM results

## Frames to seconds

Frames to seconds is one division done at translation time: `seconds = frame / fps`. At 30 fps, frame 15 is 0.5 s
and frame 90 is 3 s. Write literal seconds into the HTML; do not compute them at runtime from a frame counter.

## Linear interpolate

A linear `interpolate` becomes one tween with `ease: "none"`.

```tsx
const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
```

```js
tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 1, ease: "none" }, 0);
```

GSAP holds values at a tween's ends, which matches `clamp`. Remotion's default extrapolation is `extend`; for
`extend`, widen the input range before emitting the tween.

## Multi-point interpolate

A multi-point `interpolate` becomes one tween per segment, each starting at its segment's first frame.

```tsx
const opacity = interpolate(frame, [0, 15, 75, 90], [0, 1, 1, 0]);
```

```js
tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "none" }, 0);
tl.to(el, { opacity: 0, duration: 0.5, ease: "none" }, 2.5);
```

A flat segment (1 to 1) needs no tween.

## Springs as GSAP eases

Springs as GSAP eases are approximations; Remotion's `spring()` is a physical simulation and GSAP's eases are curves.

| Remotion `spring` config | GSAP | Duration |
|---|---|---|
| `{ damping: 12, stiffness: 100, mass: 1 }` (snappy) | `back.out(1.4)` | about 0.7 s |
| `{ damping: 14, stiffness: 90, mass: 1 }` (calmer) | `back.out(1.2)` | about 0.7 s |
| `{ damping: 8, stiffness: 200 }` (bouncy) | `back.out(2)` or `elastic.out(1, 0.5)` | about 0.6 s |
| `{ overshootClamping: true }` | `power3.out` | about 0.6 s |
| default config (`damping: 10`, `stiffness: 100`) | start from `back.out(1.6)` and tune by eye | about 0.8 s |

When the match must be exact, compute the spring in closed form from the tween's progress, which keeps every frame
renderable on its own:

```js
// underdamped spring from 0 to 1; zeta = damping ratio, w0 = natural frequency (rad/s)
function spring01(t, { stiffness = 100, damping = 10, mass = 1 } = {}) {
  const w0 = Math.sqrt(stiffness / mass), zeta = damping / (2 * Math.sqrt(stiffness * mass));
  if (zeta >= 1) return 1 - (1 + w0 * t) * Math.exp(-w0 * t);
  const wd = w0 * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + (zeta * w0 / wd) * Math.sin(wd * t));
}
const p = { t: 0 };
tl.to(p, { t: 1.2, duration: 1.2, ease: "none",
  onUpdate: () => gsap.set(el, { scale: spring01(p.t, { stiffness: 100, damping: 12 }) }) }, 0.4);
```

## Easing equivalents

Easing equivalents between Remotion and GSAP. A GSAP `powerN` ease has degree N plus one: `power1` is quadratic,
`power2` cubic, `power3` quartic, `power4` quintic.

| Remotion | GSAP |
|---|---|
| `Easing.linear` | `"none"` |
| `Easing.out(Easing.quad)` | `"power1.out"` |
| `Easing.out(Easing.cubic)` | `"power2.out"` |
| `Easing.inOut(Easing.cubic)` | `"power2.inOut"` |
| `Easing.out(Easing.poly(n))` | `"power<n-1>.out"` for n from 1 to 5 |
| `Easing.bezier(a, b, c, d)` | `CustomEase.create("c", "M0,0 C a,b c,d 1,1")` (CustomEase plugin) |
| `Easing.out(Easing.back(s))` | `"back.out(s)"`; Remotion's default `s` is 1.70158 |
| `Easing.back(s)` | `"back.in(s)"` |
| `Easing.elastic(b)` | `"elastic.out(b, 0.3)"` |
| `Easing.bounce` | `"bounce.out"` |
| `Easing.out(Easing.exp)` | `"expo.out"` |
| `Easing.out(Easing.sin)` | `"sine.out"` |

## Colour and number tweens

Colour and number tweens port directly. `interpolateColors` becomes a tween on `color`, `backgroundColor` or
`borderColor`. A frame-driven counter becomes a tween of a plain object written to `textContent`:

```js
const counter = { v: 0 };
tl.to(counter, { v: 12480, duration: 1.5, ease: "power2.out",
  onUpdate: () => { el.textContent = Math.round(counter.v).toLocaleString("en-US"); } }, 0.6);
```

`power2.out` equals Remotion's `1 - (1 - t) ** 3`. Compare the shown number at matching times, not only the final value.

## Reading SSIM results

Reading SSIM results tells you whether the port is faithful. SSIM (structural similarity) is 1.0 for identical
frames.

| Port | Typical mean SSIM |
|---|---|
| Static title card | 0.97 or higher |
| Multi-scene with springs | 0.95 to 0.985 |
| Data-driven scenes with counters | 0.95 |

- Set a pass threshold about 0.02 below the measured 5th percentile of a known-good port; do not tighten it to fit one
  lucky run.
- The minimum frame shows where structure broke: open that frame from both renders.
- Mismatched pixel formats (full-range against limited-range `yuv420p`) cost about 0.05 SSIM on their own; render both
  sides to `yuv420p`.
- Font fallback costs about 0.025 mean SSIM and shows as shifted text in every frame.
