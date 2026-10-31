---
title: SVG filter effects for video
author: MOZGII, Inc.
lang: en
---

# SVG filter effects for video

SVG filter effects chain image-processing primitives (noise, displacement, colour matrices, blur, morphology, compositing) to make glass, liquid text, neon, heat shimmer and holographic looks that CSS alone cannot. Filter attributes such as `baseFrequency`, `scale` or `stdDeviation` animate on the GSAP timeline through `attr:` tweens, so they seek like any tween. `tl` is the scene's paused timeline, registered after its tweens.

## Contents

The sections of this page:

- The SVG filter pipeline
- Primitive reference
- Complete effect recipes
- Performance notes for SVG filters

## The SVG filter pipeline

SVG filters are a directed acyclic graph of image processing primitives. Each primitive takes one or more image inputs and produces one output. Chain them to build composite effects.

```html
<!-- Hidden SVG defs — place once per composition, outside the clip hierarchy -->
<svg style="position:absolute;width:0;height:0;overflow:hidden;" aria-hidden="true">
  <defs>
    <filter id="my-filter" x="-20%" y="-20%" width="140%" height="140%"
            color-interpolation-filters="sRGB">
      <!-- primitives go here -->
      <feGaussianBlur stdDeviation="4"/>
    </filter>
  </defs>
</svg>

<!-- Apply to any element -->
<div style="filter: url(#my-filter);font:800 120px/1.2 var(--font-display);">
  Filtered content
</div>
```

**Filter region:** The `x/y/width/height` attributes define the region the filter can paint outside the element's bounding box. For effects that bloom outward (glow, blur), use `-25% -25% 150% 150%`. For contained effects (color grade), use `0% 0% 100% 100%`.

**`color-interpolation-filters="sRGB"`**: always include this. Without it, blends happen in linearRGB which changes the appearance of color-based effects.

## Primitive reference

The primitive reference describes each filter primitive with its key attributes.

### feTurbulence: Noise Generator

Generates Perlin or fractal noise. The foundation of displacement, grain, fire, water, and cloud effects.

```xml
<!-- type: "fractalNoise", or "turbulence" for a sharper look -->
<!-- baseFrequency: spatial frequency; lower means larger features -->
<!-- numOctaves: detail levels; more is finer and slower -->
<!-- seed: a fixed seed gives deterministic output -->
<!-- stitchTiles: prevents edge seams on tiled textures -->
<feTurbulence
  type="fractalNoise"
  baseFrequency="0.02"
  numOctaves="4"
  seed="42"
  stitchTiles="stitch"
  result="noise"
/>
```

**baseFrequency guide:**
| Value | Feature size | Use for |
|---|---|---|
| 0.005–0.015 | Very large blobs | Fluid, lava, volumetric fog |
| 0.02–0.04 | Medium features | Water, clouds, smoke |
| 0.05–0.10 | Small features | Fabric texture, skin, rough surface |
| 0.3–0.8 | Fine grain | Film grain, noise overlay |

**GSAP animation of feTurbulence:**
```js
const turb = document.querySelector('#my-filter feTurbulence');
// Animating baseFrequency evolves the noise shape
tl.to(turb, {
  attr: { baseFrequency: '0.04 0.02' }, // can be anisotropic
  duration: 3.0,
  ease: 'sine.inOut'
}, 0);
// Animating seed snaps the noise pattern — useful for glitch effects
tl.to(turb, { attr: { seed: 99 }, duration: 0.0, ease: 'steps(1)' }, 1.5);
```

### feDisplacementMap: Warp/Distort

Displaces `SourceGraphic` pixels using a noise map. Creates liquid, warp, distortion, heat shimmer.

```xml
<feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="3"
              seed="7" result="warpNoise"/>
<!-- in: what to distort; in2: the displacement map; scale: strength in pixels -->
<!-- xChannelSelector and yChannelSelector: the noise channel that drives each axis -->
<feDisplacementMap
  in="SourceGraphic"
  in2="warpNoise"
  scale="40"
  xChannelSelector="R"
  yChannelSelector="G"
  result="warped"
/>
```

**Animate the scale for dynamic distortion intensity:**
```js
const dm = document.querySelector('#liquid-filter feDisplacementMap');
tl.fromTo(dm, { attr: { scale: 0 } }, { attr: { scale: 60 }, duration: 1.5, ease: 'power2.out' }, 0);
tl.to(dm, { attr: { scale: 0 }, duration: 0.8, ease: 'power2.in' }, 4.0);
```

**Ink wash reveal:** Combine with feTurbulence to create an organic ink-spreading reveal:
```xml
<feTurbulence type="turbulence" baseFrequency="0.03" numOctaves="5" seed="12" result="ink"/>
<feDisplacementMap in="SourceGraphic" in2="ink" scale="80" result="spread"/>
<feComposite in="spread" in2="SourceGraphic" operator="in" result="out"/>
```

### feColorMatrix: Color Grading

```xml
<!-- Saturation boost -->
<feColorMatrix type="saturate" values="2.0"/>

<!-- Hue rotation -->
<feColorMatrix type="hueRotate" values="45"/>

<!-- Full matrix — the most powerful: R' = [a b c d e] · [R G B A 1] -->
<!-- Row by row: R = 1.2*R - 0.1; G unchanged; B = 0.8*B + 0.1, slightly tinted warm; A unchanged -->
<feColorMatrix type="matrix" values="
  1.2  0.0  0.0  0    -0.1
  0.0  1.0  0.0  0     0.0
  0.0  0.0  0.8  0     0.1
  0    0    0    1     0
"/>
```

**Film look LUT simulation:**
```xml
<!-- Filmic contrast: crushed blacks, rolled highlights -->
<feComponentTransfer>
  <feFuncR type="gamma" amplitude="1.1" exponent="0.85" offset="0.02"/>
  <feFuncG type="gamma" amplitude="1.0" exponent="0.9"  offset="0.01"/>
  <feFuncB type="gamma" amplitude="0.9" exponent="0.95" offset="0.02"/>
</feComponentTransfer>
```

### feGaussianBlur: Blur

```xml
<feGaussianBlur stdDeviation="8"/>               <!-- uniform blur -->
<feGaussianBlur stdDeviation="16 4"/>            <!-- horizontal blur stronger -->
<feGaussianBlur stdDeviation="0" result="sharp"/><!-- pass-through (chain start) -->
```

**Animate stdDeviation for focus rack / motion blur:**
```js
const blur = document.querySelector('#blur-filter feGaussianBlur');
tl.fromTo(blur, { attr: { stdDeviation: 24 } }, { attr: { stdDeviation: 0 }, duration: 0.7, ease: 'expo.out' });
```

### feBlend: Layer Blending

```xml
<!-- Screen blend of glow layer over source -->
<feBlend in="SourceGraphic" in2="glowLayer" mode="screen"/>
<!-- Available modes: normal, multiply, screen, overlay, darken, lighten,
     color-dodge, color-burn, hard-light, soft-light, difference, exclusion -->
```

### feMorphology: Grow/Shrink Shapes

```xml
<feMorphology operator="dilate" radius="3"/>  <!-- expands bright areas = glow halo -->
<feMorphology operator="erode"  radius="2"/>  <!-- shrinks shapes = outline effect -->
```

**Neon glow via dilate + screen blend:**
```xml
<filter id="neon-glow">
  <feMorphology operator="dilate" radius="4" result="fat"/>
  <feGaussianBlur in="fat" stdDeviation="8" result="glow"/>
  <feColorMatrix in="glow" type="saturate" values="3" result="vivid"/>
  <feBlend in="SourceGraphic" in2="vivid" mode="screen"/>
</filter>
```

### feComposite: Alpha Compositing

```xml
<!-- Clip warped image to original alpha shape -->
<feComposite in="warped" in2="SourceGraphic" operator="in"/>
<!-- Operators: over, in, out, atop, xor, arithmetic -->
```

### feFlood + feComposite: Color Overlay

```xml
<!-- Add a color tint -->
<feFlood flood-color="#7C3AED" flood-opacity="0.3" result="tint"/>
<feComposite in="tint" in2="SourceGraphic" operator="in" result="tinted"/>
<feBlend in="SourceGraphic" in2="tinted" mode="normal"/>
```

## Complete effect recipes

Complete effect recipes combine primitives into finished looks.

### Glass Refraction Card

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="glass" x="-5%" y="-5%" width="110%" height="110%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.008" numOctaves="2"
                    seed="21" result="glassNoise"/>
      <feDisplacementMap in="SourceGraphic" in2="glassNoise"
                         scale="12" xChannelSelector="R" yChannelSelector="G"
                         result="distorted"/>
      <feGaussianBlur in="distorted" stdDeviation="0.5" result="blurred"/>
      <feBlend in="SourceGraphic" in2="blurred" mode="normal" result="blend"/>
    </filter>
  </defs>
</svg>

<div class="glass-card" style="filter: url(#glass); backdrop-filter: blur(20px);
     background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
     border-radius: 20px; padding: 48px;">
  <h2 class="headline">Content</h2>
</div>
```

### Liquid Text Reveal

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="liquid-reveal" x="-10%" y="-20%" width="120%" height="140%">
      <feTurbulence id="liq-turb" type="fractalNoise" baseFrequency="0.03"
                    numOctaves="3" seed="5" result="noise"/>
      <feDisplacementMap id="liq-dm" in="SourceGraphic" in2="noise"
                         scale="0" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>

<div class="hero-title" style="filter: url(#liquid-reveal);">LAUNCH</div>

<script>
  const turb = document.querySelector('#liq-turb');
  const dm   = document.querySelector('#liq-dm');

  // Liquid morph in: scale from 80 → 0 as the text "crystallizes"
  tl.to(dm, { attr: { scale: 80 }, duration: 0, ease: 'steps(1)' }, 0);
  tl.to(dm, { attr: { scale: 0 }, duration: 1.2, ease: 'expo.out' }, 0.3);

  // Simultaneously evolve the noise pattern for organic feel
  tl.to(turb, { attr: { baseFrequency: '0.01' }, duration: 1.2, ease: 'expo.out' }, 0.3);
</script>
```

### Neon Glow Text (Pulsing)

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="neon" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur1"/>
      <feGaussianBlur in="SourceAlpha" stdDeviation="16" result="blur2"/>
      <feGaussianBlur in="SourceAlpha" stdDeviation="32" result="blur3"/>
      <feFlood flood-color="#00F5FF" flood-opacity="1" result="color"/>
      <feComposite in="color" in2="blur1" operator="in" result="glow1"/>
      <feComposite in="color" in2="blur2" operator="in" result="glow2"/>
      <feComposite in="color" in2="blur3" operator="in" result="glow3"/>
      <feMerge>
        <feMergeNode in="glow3"/>
        <feMergeNode in="glow2"/>
        <feMergeNode in="glow1"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
</svg>

<div class="neon-text" style="filter: url(#neon); color: #00F5FF; font-size: 160px;
     font-weight: 900; font-family: var(--font-display);">SIGNAL</div>

<script>
  // Pulse the glow itself: the flood colour feeds every blur, so its opacity sets how far the light reaches.
  const compDuration = 8;
  const pulseDuration = 1.0;
  tl.fromTo('#neon feFlood', { attr: { 'flood-opacity': 0.3 } }, { attr: { 'flood-opacity': 1 }, duration: pulseDuration, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(compDuration / pulseDuration) - 1) }, 0);
</script>
```

### Heat Shimmer / Desert Distortion

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="heat" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence id="heat-turb" type="fractalNoise"
                    baseFrequency="0.015 0.04" numOctaves="2" seed="8" result="noise"/>
      <feDisplacementMap id="heat-dm" in="SourceGraphic" in2="noise"
                         scale="14" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>

<div class="heat-target" style="filter: url(#heat); font: 900 200px/1 var(--font-display); color: var(--text-primary);">MIRAGE</div>

<script>
  const turb = document.querySelector('#heat-turb');
  // Slowly evolve baseFrequency to make the shimmer feel alive
  const compDuration = 8;
  const dur = 4;
  tl.to(turb, {
    attr: { baseFrequency: '0.018 0.05' },
    duration: dur,
    ease: 'sine.inOut',
    yoyo: true,
    repeat: Math.max(0, Math.floor(compDuration / dur) - 1)
  }, 0);
</script>
```

### Holographic / Iridescent Overlay

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="holo" x="-5%" y="-5%" width="110%" height="110%"
            color-interpolation-filters="sRGB">
      <!-- Shift hue based on time — animate hueRotate attribute -->
      <feColorMatrix id="holo-hue" type="hueRotate" values="0" result="shifted"/>
      <feComponentTransfer in="shifted" result="boosted">
        <feFuncR type="gamma" amplitude="1.3" exponent="0.8"/>
        <feFuncG type="gamma" amplitude="1.1" exponent="0.9"/>
        <feFuncB type="gamma" amplitude="1.4" exponent="0.75"/>
      </feComponentTransfer>
      <feBlend in="SourceGraphic" in2="boosted" mode="overlay"/>
    </filter>
  </defs>
</svg>

<div class="holo-element" style="filter: url(#holo);">
  <img src="assets/product.png" width="600" height="600" alt="Product"/>
</div>

<script>
  const hue = document.querySelector('#holo-hue');
  // Continuously rotate hue for iridescent effect
  const compDuration = 8;
  const cycleDur = 4.0;
  tl.to(hue, {
    attr: { values: 360 },
    duration: cycleDur,
    ease: 'none',
    repeat: Math.max(0, Math.floor(compDuration / cycleDur) - 1)
  }, 0);
</script>
```

## Performance notes for SVG filters

SVG filters run on the CPU rasteriser thread, so their cost grows with filter area and frame count. Expensive operations:
- Large blur radii (`stdDeviation > 20`) on large elements
- Multiple displacement maps in the same filter chain
- Filters on composited layers with many children

**For HyperFrames capture:** a slow filter never drops frames, because capture waits for each frame, but it does lengthen the render, and a large blur or turbulence area can stall it. Shrink the filter region (`x`, `y`, `width`, `height` on `<filter>`) or bake the effect to video.

**For preview:** If preview feels slow, reduce `stdDeviation` or `scale` values temporarily. Never ship degraded quality values.
