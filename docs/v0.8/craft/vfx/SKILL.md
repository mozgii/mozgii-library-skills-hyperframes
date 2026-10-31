---
name: vfx
description: Builds custom visual effects for HyperFrames video when no registry item fits - WebGL fragment shaders (plasma, fluid, aurora, god rays, fire, portals), SVG filter chains (displacement, glass, liquid text, neon, heat shimmer), Canvas 2D particles and procedural backgrounds, CSS compositing, glitch, rack focus, marker highlights on text - and the built-in runtime effects (shutter motion blur, data-vfx-chain warps, ASCII, halftone, CRT and tape looks on footage), all seekable and seeded. Use when a video needs a one-off effect, motion blur, a visual peak, a texture, a stylised look on footage or text emphasis that the catalog does not have, or when porting a Shadertoy shader.
metadata:
  tags:
  - vfx
  - webgl
  - glsl
  - shaders
  - svg-filters
  - canvas
  - particles
  - glitch
  - compositing
---

# Visual effects for video

Visual effects for video are custom images CSS layout cannot make on its own: per-pixel shaders, SVG filter chains,
canvas particles, compositing tricks and marks drawn on text. In HyperFrames each effect must be a pure function of
the timeline's time, with seeded randomness, so every frame renders alone and identically. Search the registry first
(`npx hyperframes catalog --query "<the effect, in English>" --json`); build here only what it lacks. Checked against
CLI 0.8.223.

## When to use this skill

Use this skill for a one-off effect, a film's visual peak, a background atmosphere, a glitch, a rack focus, or a
highlight mark on a word, and when porting a shader from Shadertoy or GLSL Sandbox.

## Step 0: read the CLI and what the render machine can draw

```bash
npx hyperframes --version     # the built-in effects ship with it
npx hyperframes doctor --json | jq .ok
npx hyperframes render --quality draft -o /tmp/probe.mp4   # the summary line says `software gpu` or not
```

On a software GPU, heavy shaders can stall: prefer a built-in effect, or bake the effect to video.

## Pick the technique

Pick the technique by what the effect touches.

| Effect | Technique | Reference |
|---|---|---|
| Full-frame per-pixel images: plasma, fluid, aurora, nebula, fire, lens warps | WebGL fragment shader | [references/webgl-shaders.md](references/webgl-shaders.md) |
| Distortion, glow or colour on an HTML element, text or video | SVG filter | [references/svg-filters.md](references/svg-filters.md) |
| Many moving objects, particles, procedural lines | Canvas 2D | [references/vfx-recipes-part2.md](references/vfx-recipes-part2.md) |
| Wipes, reveals, flips, masks, tickers | CSS and GSAP | [references/vfx-recipes-part1.md](references/vfx-recipes-part1.md) |
| A mark on one word: sweep, circle, burst, scribble | CSS, SVG and GSAP | [references/text-emphasis.md](references/text-emphasis.md) |
| A GPU effect over footage, compute particles | WebGPU | `webgpu` |
| A 3D object or scene | Three.js | `threejs` |
| Motion blur, wave warps, displacement, ASCII, halftone, CRT and tape looks | built-in runtime effects from attributes | [references/runtime-effects.md](references/runtime-effects.md) |

Pure CSS and GSAP cost nothing extra; reach for WebGL only when the effect needs per-pixel maths.

## Built-in effects before custom code

Built-in effects are the ones the HyperFrames runtime draws from an attribute, so check them before writing a
shader. `data-motion-blur="on"` on the root gives real shutter blur on fast moves; `data-vfx-chain` gives per-pixel
wave warps, displacement maps and fractal noise that repaint on every seek; the `effects` section of
`data-color-grading` gives footage and images looks such as ASCII, halftone, two-ink print, tape damage, CRT
curvature and pixelate (also for hiding an email address in a screen recording). Attributes, tiers, costs and
limits: [references/runtime-effects.md](references/runtime-effects.md).

## The seek contract for effects

The seek contract for effects keeps them renderable.

1. Drive every effect from the timeline: tween a uniform, a filter attribute (`attr:`) or a progress value, and draw
   in `onUpdate` or in an `hf-seek` listener.
2. No `requestAnimationFrame` loop, no `performance.now()`, no state carried from the previous frame.
3. Seed every random value with a seeded generator, or hash it from coordinates in a shader.
4. Canvas: reset transforms each draw (`ctx.setTransform(1, 0, 0, 1, 0, 0)`) before `clearRect`.
5. Repeats are finite and computed from the scene's duration.

```js
// a shader's time comes from the timeline
const u = { t: 0 };
tl.to(u, { t: SCENE_DURATION, duration: SCENE_DURATION, ease: "none",
  onUpdate: () => { gl.uniform1f(uTime, u.t); drawFrame(); } }, 0);
```

## Compositing vocabulary

Compositing vocabulary from editing and compositing tools maps onto web primitives:

| Compositing idea | In the browser |
|---|---|
| Grade | `feColorMatrix`, `feComponentTransfer`, or `media-treatment` for footage |
| Merge over, multiply, screen | `z-index` with `mix-blend-mode` |
| Luma or alpha matte | `mask-image`, `feComposite operator="in"` |
| Roto mask | `clip-path`, SVG `clipPath` |
| Displacement | `feDisplacementMap` fed by `feTurbulence` |
| Directional motion blur | `feGaussianBlur stdDeviation="16 0"`, or `data-motion-blur="on"` on the root |
| Depth of field | layers with different blur |
| Film grain | `feTurbulence` blended in overlay, or a stepped noise tile |
| Pre-comp | a scene sub-composition |

## Principles for effects

Principles for effects that read as craft, not decoration:

- **Layered reality:** environment, atmosphere, subject, camera (vignette, grain, lens) as separate layers.
- **Motivated:** every effect has a cause on screen (heat shimmer from heat, a flare from a light). If you cannot say
  why it happens, it is decoration.
- **Invisible at its best:** grain and a soft rack focus are felt, not noticed.
- **One peak:** in a 30 s film, one effect is the moment people rewind for; everything else supports it.
- **No visible grids:** repeating tiles, hexagons and even dot arrays look cheap; organic noise does not.

## Porting a shader

Porting a shader from Shadertoy or GLSL Sandbox renames its inputs (`iTime` to `u_time`, `iResolution` to
`u_resolution`), removes mouse and backbuffer inputs, and replaces frame-feedback passes with maths of time. Check the
licence first: Shadertoy shaders default to CC BY-NC-SA 3.0, which forbids commercial use, unless the author states
otherwise. The full checklist is at the end of the WebGL reference.

## Verify the effect

```bash
npx hyperframes snapshot --at 1,3,5 -o /tmp/vfx-a
npx hyperframes snapshot --at 1,3,5 -o /tmp/vfx-b
for f in /tmp/vfx-a/*.png; do cmp "$f" "/tmp/vfx-b/$(basename "$f")"; done   # silent means the same pixels
npx hyperframes check --json
grep -rnE 'requestAnimationFrame|performance\.now|Math\.random' compositions index.html   # expect nothing
```

Compare a frame reached by seeking backwards as well: an effect with hidden state differs only then.

## Checklist

- [ ] The registry had nothing that fits; the effect has a reason on screen.
- [ ] Driven by the timeline or `hf-seek`; no clocks, rAF loops or frame feedback.
- [ ] Randomness seeded; repeats finite.
- [ ] Shader colours come from the palette tokens as uniforms.
- [ ] Snapshots at three times match a second run; `check` passes.
- [ ] Ported shaders' licences allow the use.

## Gotchas

- **Symptom:** A shader is frozen or random in the render. **Cause:** Time came from rAF or `performance.now()`.
  **Fix:** tween a uniform on the timeline.
- **Symptom:** A canvas drifts across seeks. **Cause:** Transforms accumulated. **Fix:** reset them before each draw.
- **Symptom:** An SVG filter slows the render. **Cause:** Large blur or turbulence areas on the CPU rasteriser.
  **Fix:** shrink the filter region (`x`, `y`, `width`, `height` on `<filter>`) or bake the effect.
- **Symptom:** An effect differs between machines. **Cause:** GPU differences in precision. **Fix:** use `highp`
  floats and check on the render host.

## Anti-patterns

| Do not | Do instead |
|---|---|
| a shader for a wipe or a mask | CSS and GSAP, which cost nothing extra |
| a custom blur for fast moves | `data-motion-blur="on"` on the root |
| an effect with no cause on screen | give it a reason, or remove it |
| a Shadertoy shader with no licence check | default CC BY-NC-SA 3.0 forbids commercial use |
| repeating tiles and even dot grids | organic noise |

## References

- [references/webgl-shaders.md](references/webgl-shaders.md): the shader contract, WebGL boilerplate, GLSL noise and SDF library, 12 shader recipes, Shadertoy port checklist.
- [references/svg-filters.md](references/svg-filters.md): filter primitives and five complete SVG effects.
- [references/vfx-recipes-part1.md](references/vfx-recipes-part1.md): 13 recipes for transitions, entrances, data and camera effects.
- [references/vfx-recipes-part2.md](references/vfx-recipes-part2.md): 13 recipes for text, shapes, glitch and procedural backgrounds, plus compositing.
- [references/text-emphasis.md](references/text-emphasis.md): highlight, circle, burst, scribble and sketchout marks.
- [references/runtime-effects.md](references/runtime-effects.md): motion blur, media looks, `data-vfx-chain` kernels and HTML in canvas.

## See also

`hyperframes-registry`, `webgpu`, `threejs`, `motion-design`.
