---
title: Built-in HyperFrames effects - motion blur, VFX chains, media looks, HTML in canvas
author: MOZGII, Inc.
lang: en
---

# Built-in HyperFrames effects: motion blur, VFX chains, media looks, HTML in canvas

The HyperFrames runtime can draw four kinds of effect from attributes alone, with no shader of your own: shutter
motion blur on fast movers, chains of per-pixel kernels (`data-vfx-chain`), looks on images and footage (ASCII,
halftone, tape damage, CRT and more) through `data-color-grading`, and live DOM copied into a canvas for WebGL. All
of them are deterministic, so the preview and the render agree. Checked against CLI 0.8.223.

## Which built-in effect to use

| You want | Use | Cost |
|---|---|---|
| Fast moves that smear like a real shutter | `data-motion-blur` on the root | low (filter tier) to one extra paint per frame (capture tier) |
| Footage or an image restyled: halftone, two-ink print, ASCII, CRT, glitch | the `effects` section of `data-color-grading`, via `media-treatment` | low, except blur, bloom and Kuwahara on large layers |
| Part of a frame hidden or treated: a blurred face, a pixelated email | a clipped second copy of the media with the look on it | as above |
| Text or a layer warped per pixel, with noise or displacement | `data-vfx-chain` | high: forces screenshot capture, often one worker |
| Real DOM as a texture inside a 3D scene or shader | HTML in canvas (`drawElementImage()`) | depends on the scene |

## Motion blur with data-motion-blur

Fast-moving elements get smeared along their path, as a film camera's shutter would smear them. Nothing is blurred
until the root composition carries `data-motion-blur="on"`, and that one attribute controls both preview and render:

```html
<div id="root" data-motion-blur="on" data-motion-blur-shutter="360"
     data-composition-id="main" data-width="1920" data-height="1080" data-duration="12"></div>
```

| Attribute | Default | What it sets |
|---|---|---|
| `data-motion-blur` | unset | `on` switches it on; `off` excludes a subtree |
| `data-motion-blur-shutter` | `240` | shutter angle from 0 to 720 degrees; a wider angle smears further (720 matches the editor's "Strong") |
| `data-motion-blur-samples` | at least 32 | a fixed sample count per frame, 2 to 64; when unset the count follows the length of the smear |
| `data-motion-blur-events` | off | `on` lets timeline callbacks run while samples are taken; required when motion comes from `onUpdate` or a `render(t)` function |
| `data-motion-blur-tier` | `auto` | `capture` or `filter` pins the drawing method |

What gets blurred: elements moving quickly in 2D (translation, scale, rotation) driven by GSAP, CSS animations or
WAAPI. Slow movers and still content remain crisp, and a mover carries its own glow and shadow with it.

### Filter tier and capture tier

There are two ways to draw the smear:

- **Filter** lays averaged copies of the mover along its path through an SVG filter. Any Chrome can do it, it works
  over WebGL, and it is nearly free, but rotations and zooms are only softened rather than streaked.
- **Capture** grabs each mover through Chrome's HTML-in-canvas API and paints it repeatedly along the path, so a spin
  smears around its arc and a zoom streaks outward from the centre.

`auto` picks filter when movers only translate and capture as soon as one rotates or scales.

### When capture falls back to filter

The choice is made once, on the first frame. Capture drops to filter when any of these is true:

- the composition contains a WebGL or WebGPU canvas;
- something uses `backface-visibility: hidden` in 3D;
- the root has a transform, an opacity under 1 or a blend mode;
- an iframe, object, embed or custom element sits in the root;
- another capture canvas is nested inside (a VFX chain, for one);
- the browser has no HTML in canvas.

`npx hyperframes check` names the problem: `motion_blur_filter_fallback` (with its cause), `motion_blur_no_movers`
(nothing moved fast enough, or motion came from a callback and `data-motion-blur-events` is missing) and
`motion_blur_unverified`. Inside the page, `window.__hfMotionBlur.report()` returns the state, the tier and the
reason.

### What motion blur costs and where it stops

The filter tier is close to free. Capture adds roughly one more paint for each blurred frame: an 8 s test took about
9.8 s with blur and 5.3 s without. The limits:

- HDR renders and distributed renders (Lambda, Cloud Run) switch it off;
- renders with different worker counts differ very slightly (around 60 dB PSNR);
- it ignores CSS `zoom`, `position: fixed`, `foreignObject`, very short WAAPI animations and large translucent
  movers; under capture, a mover ends up drawn over still content that ought to hide it;
- when the browser has no HTML in canvas, the preview falls back to the filter tier, so a spin can look softer in preview than in the
  file; pin a tier when the two must match exactly.

For fast moves, this blur beats a hand-tuned `filter: blur()`, because it follows the real path and speed.

## Looks on images and footage

A look restyles an `<img>`, `<video>` or canvas at render time through the `effects` section of
`data-color-grading`, next to `adjust` (correction) and `details` (grain, vignette). The source file is untouched, so
a look can be dialled down, animated or removed later.

| Family | Looks |
|---|---|
| Essentials | blur, pixelate, bloom |
| Retro and glitch | scanlines, tape damage, film artifacts, digital glitch, CRT curvature, chroma softening, channel separation |
| Print | ordered dither, halftone, mono screen, two-ink print |
| Art | Kuwahara paint, engraving, crosshatch, ASCII in several styles |

Ask the CLI for the list, preview a look, then apply it:

```bash
npx hyperframes media-treatment --capabilities --json                                   # current looks and their ranges
npx hyperframes media-treatment --selector '#product' --grading '{"preset":"two-ink-print"}' --dry-run --json
npx hyperframes media-treatment --selector '#product' --grading '{"preset":"two-ink-print"}' --apply
```

- The list of looks keeps growing, so read `--capabilities` rather than hard-coding names.
- A flat object such as `{"exposure":0.15}` draws nothing; `lint` tells you which section the key belongs in.
- Go all the way or not at all: ASCII at half strength looks like a bug.
- Blur, bloom and Kuwahara are slow on large layers.
- Looks apply to standard dynamic range only, and an HDR source is shown in SDR while previewing.

### Animating a look

The runtime exposes custom properties that the registered timeline can tween: `--hf-color-grading-ascii`, `-bloom`,
`-blur`, `-dither`, `-exposure`, `-intensity`, `-kuwahara`, `-pixelate` and `-lut-intensity`. Give the start value in
the element's inline style, then tween it:

```js
tl.to("#plate", { "--hf-color-grading-pixelate": 0.5, duration: 3, ease: "power2.inOut" }, 0.3);
```

`--hf-color-grading-intensity` scales the correction, wheels, curves, selections and LUT, but not the effect families.

### Treating one region of the frame

A look always covers its whole layer and picks pixels by their values, never by where they are. To blur a face or
pixelate an email address in a screen recording, stack a second copy of the media on top, cut it down to the region
with `clip-path`, and put the look on that copy; for a moving subject use a cutout layer instead. A fixed `clip-path`
is only good when the subject hardly moves.

## Per-pixel kernels with data-vfx-chain

`data-vfx-chain` attaches a chain of WebGL2 kernels (wave warp, displacement map, fractal noise) to an element. On
every seek the runtime repaints the chain from the time and the parameters, byte for byte the same each time. The
chain is JSON on the element; parameters that animate are CSS custom properties called `--vfx-<nodeId>-<key>`, which
GSAP can tween:

```html
<div id="title-warp" class="clip" data-start="0" data-duration="6"
     data-vfx-chain='{"version":1,"nodes":[{"type":"wave-warp","id":"w1","params":{"waveType":1,"direction":0,"speed":1,"pinning":1,"phase":0}}]}'
     style="position:absolute;left:360px;top:390px;width:1200px;height:300px;--vfx-w1-height:21;--vfx-w1-width:93.4">
  <canvas layoutsubtree class="hf-vfx-src"><div class="hf-vfx-in" style="width:1200px;height:300px;font:900 220px/300px sans-serif;color:#fff;text-align:center">WAVES</div></canvas>
  <canvas class="hf-vfx-out" data-layout-allow-occlusion></canvas>
</div>
```

| Kernel kind | Example | Needs |
|---|---|---|
| Reads its own layer | `wave-warp`, `displacement-map` | a `.hf-vfx-src` capture canvas holding exactly one `.hf-vfx-in` child with an explicit pixel size; `inset: 0` shrinks to 0×0 in the canvas and silently captures nothing |
| Generator | `fractal-noise` | nothing but position and time; no capture canvas |

- Any chain switches the render to screenshot capture, and capturing kernels also hold the render to one worker.
  Expect slower renders, and add a chain only where per-pixel work is the point.
- Effects meant to run before the chain go on `.hf-vfx-in`; effects meant to run after it go on the host.
- An ordinary browser preview of a capturing chain needs `chrome://flags/#canvas-draw-element` in a Chrome that
  supports it; otherwise the console shows an error naming the flag.
- In a composition that also has shader transitions, a capturing chain may paint from an outdated texture outside the
  transitions.

## HTML in canvas for WebGL textures

Chrome's experimental `drawElementImage()` copies rendered DOM into a canvas, and that canvas can then feed a Three.js
texture or a shader: a real interface on the screen of a 3D device, a scene dragged through a distortion. The render
engine turns the feature on when it starts Chrome, and uses its usual capture when the API is absent or unsafe for
the composition.

- Start from a catalog block that already detects support and falls back:
  `npx hyperframes catalog --query "html in canvas device" --json`.
- In your own code, test support on a canvas with `layoutsubtree` (`"layoutSubtree" in canvas` and
  `typeof ctx.drawElementImage === "function"`) and keep a plain fallback.
- When the DOM changes, capture again and set `texture.needsUpdate = true`.
- Filters, backdrop filters, masks, blend modes and some 3D transforms push the fallback path.
- Judge the result in a rendered file, not only in the preview.
