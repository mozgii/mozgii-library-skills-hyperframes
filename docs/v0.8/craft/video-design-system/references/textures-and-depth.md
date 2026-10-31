---
title: Textures and depth layers for video
author: MOZGII, Inc.
lang: en
---

# Textures and depth layers for video

Textures and depth layers are the background atmosphere of a video frame: grain, glows, ghost type, grids, scan lines, vignettes, particles and glass. They keep a frame from feeling empty while content enters, and grain also breaks up H.264 banding. Every snippet here is static or driven by the composition timeline with finite repeats, so it renders the same every time. In the snippets, `tl` is the scene's paused timeline and `SCENE_DURATION` is the scene's length in seconds, a constant you declare once beside `tl`.

## Contents

The sections of this page:

- Depth layer system
- Grain overlay
- Radial glow
- Ghost text
- Grid lines and registration marks
- Scan lines
- Vignette
- Particle systems
- Glass morphism
- Texture anti-patterns

## Depth layer system

A depth layer system gives every composition four layers. Assign elements deliberately, not arbitrarily.

```
Layer 0 — Environment (z-index: 0–10)
  Background color / video / image
  Shader plates, gradient fields
  Full-frame grain overlay

Layer 1 — Atmosphere (z-index: 10–20)
  Radial glows (accent-colored)
  Ghost text (3–8% opacity, huge, slow drift)
  Pattern tiles, grid lines
  Particle systems

Layer 2 — Content (z-index: 20–40)
  Primary message: headlines, stats, product shots
  Secondary: body text, supporting elements

Layer 3 — HUD (z-index: 40–60)
  Captions, subtitles
  Corner tags, version badges
  Progress bars, timers
```

Each layer moves at a different velocity: environment = nearly static, atmosphere = slow drift, content = normal animation, HUD = instant.

## Grain overlay

Grain is the single most effective treatment for preventing H.264 banding and making dark compositions feel cinematic rather than digital.

### SVG feTurbulence (best quality)

```html
<svg id="grain" style="position:absolute; inset:0; width:100%; height:100%;
     pointer-events:none; z-index:50; opacity:0.055; mix-blend-mode:screen;">
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3"
                  stitchTiles="stitch" result="noiseOut"/>
    <feColorMatrix type="saturate" values="0" in="noiseOut"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#noise)"/>
</svg>
```

**Opacity guide:**
| Aesthetic | Opacity |
|---|---|
| Barely there (clean corporate) | 0.020–0.035 |
| Subtle (standard dark) | 0.045–0.065 |
| Film grain (editorial, warm) | 0.070–0.095 |
| Heavy (noir, cinematic) | 0.10–0.14 |

**Blend modes:** `screen` for dark backgrounds (brightens grain), `multiply` for light backgrounds (darkens grain), `overlay` for neutral.

**Animated grain (rolling, alive):** static SVG grain is sufficient for almost all compositions. When grain must move, step a noise tile across the frame on the timeline. Never advance it from an `onUpdate` counter: a render seeks, it does not count frames.

```html
<div class="grain-rolling"></div>
<style>
.grain-rolling {
  position: absolute; inset: 0;
  pointer-events: none; z-index: 50; opacity: 0.055; mix-blend-mode: screen;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23g)'/%3E%3C/svg%3E");
}
</style>
<script>
  // 12 jumps a second, each by the same off-grid offset, so the position depends only on the time
  const grainSteps = Math.round(SCENE_DURATION * 12);
  tl.fromTo('.grain-rolling',
    { backgroundPosition: '0px 0px' },
    { backgroundPosition: `${grainSteps * 83}px ${grainSteps * 47}px`, duration: SCENE_DURATION, ease: `steps(${grainSteps})` },
    0
  );
</script>
```

## Radial glow

A radial glow is the foundational depth element: one accent-coloured radial gradient, low opacity, breathing scale animation. This is what makes dark compositions feel alive rather than dead.

```css
.glow-primary {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--glow) 0%, transparent 70%);
  pointer-events: none;
}
```

```js
// Breathing animation — slow, continuous, ambient
const breathDuration = 4.5;
const repeatCount = Math.ceil(SCENE_DURATION / (breathDuration * 2));

tl.to(".glow-primary", {
  scale: 1.18,
  opacity: 0.45,
  duration: breathDuration,
  ease: "sine.inOut",
  yoyo: true,
  repeat: repeatCount
}, 0);
```

### Glow placement guide

| Style | Position | Size | Opacity |
|---|---|---|---|
| Hero center | 50% 50% | 700–900px | 25–35% |
| Accent corner | 0% 100% | 400–500px | 30–40% |
| Split accent | 20% 50% + 80% 50% | 350px each | 20–25% each |
| Bottom ambience | 50% 90% | 600–800px | 20–28% |
| Multi-glow layered | Primary 50% 50% + secondary 20% 80% | 800px + 400px | 28% + 20% |

Never use more than 3 glows simultaneously, they lose definition and flatten the depth.

## Ghost text

Ghost text is huge type at 3–8% opacity that creates visual depth without competing with content. Classic in editorial and tech designs.

```html
<div class="ghost-text" aria-hidden="true" style="
  position: absolute;
  font-size: 400px;
  font-weight: 900;
  color: var(--text-primary);
  opacity: 0.04;
  white-space: nowrap;
  top: 50%;
  left: -5%;
  transform: translateY(-50%);
  pointer-events: none;
  user-select: none;
">FUTURE</div>
```

```js
// Slow horizontal drift
tl.to(".ghost-text", {
  x: "-3%",
  duration: SCENE_DURATION,
  ease: "none"
}, 0);
```

Use the primary theme word, brand name, or a single concept word. Never full sentences. Mark with `aria-hidden="true"` and `data-layout-ignore` to exclude from contrast/overflow audits.

```html
<div class="ghost-text" aria-hidden="true" data-layout-ignore style="...">
```

## Grid lines and registration marks

Grid lines and registration marks suit Swiss Pulse, technical and data compositions. They create an implied structure that doesn't need to be visible at full opacity to work.

```css
.grid-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 5;
  background-image:
    linear-gradient(to right, rgb(255 255 255 / 5%) 0 1px, transparent 1px 100%),
    linear-gradient(to bottom, rgb(255 255 255 / 5%) 0 1px, transparent 1px 100%);
  background-size: 120px 120px;
}

.registration-mark {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 0;
}
```

Registration marks at corners reinforce the "designed" quality. Keep them small (16–24px) and subtle (<15% opacity).

## Scan lines

Scan lines suit Deconstructed and retro-tech looks: horizontal lines that suggest CRT or terminal displays.

```css
.scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 3px,
    rgba(0, 0, 0, 0.08) 3px,
    rgba(0, 0, 0, 0.08) 4px
  );
  pointer-events: none;
  z-index: 48;
}
```

Use sparingly, 4–8% effective opacity on the lines. Heavy scan lines look like a filter, not a design choice.

## Vignette

A vignette darkens the edges of a composition, focuses attention on center, creates cinematic depth. Essential for full-frame video or image backgrounds.

```css
.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 50%,
    rgba(0, 0, 0, 0.55) 100%
  );
  pointer-events: none;
  z-index: 8;
}
```

| Intensity | Center transparent | Edge opacity |
|---|---|---|
| Light (subject clear) | 55–65% | 0.35–0.45 |
| Standard | 45–55% | 0.50–0.65 |
| Heavy (dramatic, noir) | 30–45% | 0.65–0.80 |

## Particle systems

Particle systems suit Data Drift, ambient tech pieces and atmosphere layers. They are seeded, never random at render time.

```js
// Seeded position generator
function seededRandom(seed) {
  let count = seed | 0;
  return function next() {
    count = count + 0x2AC5E3B1 | 0;           // an odd step visits every 32-bit value once
    const spread = Math.imul(count, 0x4F2B71A3);
    const mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
    return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296;   // 0 up to 1
  };
}

const rand = seededRandom(42); // fixed seed = deterministic

const particles = [];
for (let i = 0; i < 40; i++) {
  const p = document.createElement('div');
  p.className = 'particle';
  Object.assign(p.style, {
    position: 'absolute',
    width: `${2 + rand() * 4}px`,
    height: `${2 + rand() * 4}px`,
    borderRadius: '50%',
    background: 'var(--accent)',
    opacity: 0.3 + rand() * 0.4,
    left: `${rand() * 100}%`,
    top: `${rand() * 100}%`,
  });
  document.querySelector('.atmosphere').appendChild(p);
  particles.push(p);
}

// Deterministic drift
particles.forEach((p, i) => {
  const seed = i * 137.508;
  const dur = 6 + (seed % 5);
  tl.to(p, {
    x: Math.sin(seed) * 60,
    y: Math.cos(seed) * 40,
    duration: dur,
    ease: "sine.inOut",
    yoyo: true,
    repeat: Math.ceil(SCENE_DURATION / (dur * 2))
  }, 0);
});
```

Mark the container: `data-layout-ignore`: particles will intentionally overflow their container.

## Glass morphism

Glass morphism suits clean corporate compositions with depth layers: cards feel like frosted glass floating over a background.

```css
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(24px) saturate(1.4);
  -webkit-backdrop-filter: blur(24px) saturate(1.4);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-card, 20px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}
```

**Dark glass variant:**
```css
.glass-dark {
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

Note: `backdrop-filter` requires a background below it. Works correctly in HyperFrames because the composition renders in Chrome.

## Texture anti-patterns

Texture anti-patterns are the texture mistakes common in generated compositions. Avoid:

| Pattern | Problem | Instead |
|---|---|---|
| Full-screen linear gradient on dark bg | H.264 banding, visible stairstepping | Radial gradient + grain |
| Gradient text (`background-clip: text`) | AI design tell, overdone | Colored text + glow; or SVG clip-path |
| Repeating cyan-on-dark glow | Overused "tech" aesthetic | Tint the glow to the actual brand accent |
| Static decoratives (no GSAP animation) | Feels dead during content staggering | Every atmosphere element breathes, drifts, or pulses |
| Identical opacity on all layers | No depth, everything feels flat | Layer 0: 3–6%, Layer 1: 8–15%, Layer 2: full opacity |
| Left-edge accent stripe on cards | AI card default | Full-border glass, radial inner highlight, or bottom-edge only |
