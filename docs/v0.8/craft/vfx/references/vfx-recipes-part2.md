---
title: "VFX recipes: text, shapes and backgrounds"
author: MOZGII, Inc.
lang: en
---

# VFX recipes for HyperFrames: text, shapes and backgrounds

VFX recipes are complete effect implementations: transitions, backgrounds, text effects, data emphasis and camera tricks, each deterministic and driven by the scene's paused GSAP timeline. Each recipe is a fragment of a scene: `tl` is that scene's paused timeline, registered after all its tweens, and `SCENE_DURATION` is the scene's length in seconds. All pseudo-random values come from the seeded generator `seededRandom` below, never `Math.random()`. A recipe's energy and duration say where it fits in a film. The examples read these tokens, declared on `:root` or the scene root: `--accent`, `--accent-2`, `--accent-muted`, `--bg`, `--surface`, `--border`, `--text-primary`, `--text-secondary`, `--text-dim`, `--font-display`, `--font-body`, `--font-mono`, plus `--accent-rgb`, `--accent-2-rgb` and `--bg-rgb` written as bare channels (`255,90,54`) so `rgba(var(--accent-rgb), 0.3)` can add its own alpha.

```js
function seededRandom(seed) {
  let count = seed | 0;
  return function next() {
    count = count + 0x2AC5E3B1 | 0;           // an odd step visits every 32-bit value once
    const spread = Math.imul(count, 0x4F2B71A3);
    const mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
    return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296;   // 0 up to 1
  };
}
```

## Contents

The sections of this page:

- Gradient wipe text mask
- Morphing SVG blob
- Word scatter kinetic type
- Film leader countdown
- Refraction glass pane
- Streak speed lines
- Counter ring progress
- Compositing principles for VFX
- MorphSVG shape transition
- Glitch block corruption
- Ink wash reveal
- Geometric SVG tile background
- Constellation canvas background
- Flowing noise field canvas background

## Gradient wipe text mask

A gradient wipe text mask is a medium-energy text entrance (0.5 to 0.8 s) that reveals letters through a moving soft-edged mask.

Text is revealed by a gradient mask that sweeps left-to-right. Smooth, elegant, premium. Works beautifully for headline entrances.

```html
<style>
.gradient-wipe-text {
  background: linear-gradient(
    to right,
    var(--text-primary) 0%,
    var(--text-primary) 50%,
    transparent 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  background-position: 100% 0;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>

<div class="gradient-wipe-text" id="wipe-text">TRANSFORM</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to('#wipe-text', {
  backgroundPosition: '0% 0',
  duration: 0.7,
  ease: 'power3.inOut'
}, 0);
</script>
```

## Morphing SVG blob

A morphing SVG blob is a medium-energy background or accent shape that changes outline over a scene.

An SVG path morphs between organic shapes using GSAP MorphSVG or CSS d-property animation. Creates living, breathing background elements.

```html
<svg viewBox="0 0 200 200" style="position:absolute;width:600px;height:600px;opacity:0.3;">
  <path id="blob-path" fill="var(--accent)"
    d="M 100,40 C 130,30 160,50 170,80 C 180,110 165,140 140,155 C 115,170 80,165 60,145 C 40,125 35,95 50,70 C 65,45 70,50 100,40 Z"/>
</svg>

<script>
// Target shapes — pre-computed organic paths (deterministic, not random)
const shapes = [
  'M 100,40 C 130,30 160,50 170,80 C 180,110 165,140 140,155 C 115,170 80,165 60,145 C 40,125 35,95 50,70 C 65,45 70,50 100,40 Z',
  'M 100,35 C 140,25 170,55 175,90 C 180,125 155,155 120,165 C 85,175 55,155 42,125 C 29,95 40,60 65,45 C 90,30 60,45 100,35 Z',
  'M 100,45 C 120,25 155,40 165,70 C 175,100 165,135 135,150 C 105,165 70,160 52,135 C 34,110 38,75 58,55 C 78,35 80,65 100,45 Z'
];

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Cycle through shapes
shapes.slice(1).forEach((shape, i) => {
  tl.to('#blob-path', {
    attr: { d: shape },
    duration: 3,
    ease: 'sine.inOut'
  }, i * 3);
});
// Return to start
tl.to('#blob-path', {
  attr: { d: shapes[0] },
  duration: 3,
  ease: 'sine.inOut'
}, shapes.length * 3 - 3);
</script>
```

## Word scatter kinetic type

Word scatter kinetic type is a very high energy text effect (0.6 to 1.2 s) where words fly in from seeded positions and lock into a line.

Each word of a headline enters from a different direction and slams into its final position. High energy, editorial, dynamic.

```html
<style>
.word-scatter-wrap {
  display: flex; flex-wrap: wrap; gap: 0.3em;
  overflow: visible;
}
.scatter-word {
  display: inline-block;
  will-change: transform;
}
</style>

<div class="word-scatter-wrap" id="scatter">
  <span class="scatter-word">BUILD</span>
  <span class="scatter-word">THE</span>
  <span class="scatter-word">FUTURE</span>
</div>

<script>
const words = document.querySelectorAll('.scatter-word');
const rng = seededRandom(88);

// Pre-compute start positions (deterministic)
const starts = Array.from(words).map(() => ({
  x: (rng() - 0.5) * 800,
  y: (rng() - 0.5) * 600,
  rotation: (rng() - 0.5) * 60
}));

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

words.forEach((word, i) => {
  tl.fromTo(word,
    { x: starts[i].x, y: starts[i].y, rotation: starts[i].rotation, opacity: 0 },
    {
      x: 0, y: 0, rotation: 0, opacity: 1,
      duration: 0.5,
      ease: 'back.out(1.7)'
    },
    i * 0.05
  );
});
</script>
```

## Film leader countdown

A film leader countdown is a very high energy opener (3 to 5 s) with a sweeping clock hand over numbers.

Mimics the look of a 35mm film countdown leader with frame flicker, countdown numbers, and scan lines. Instantly communicates "cinematic."

```html
<style>
.film-leader {
  position: absolute; inset: 0;
  background: var(--bg);
  display: flex; align-items: center; justify-content: center;
}
.film-circle-outer {
  position: absolute;
  width: 60%; aspect-ratio: 1;
  border-radius: 50%;
  border: 4px solid rgba(255,255,255,0.2);
}
.film-crosshair::before,
.film-crosshair::after {
  content: '';
  position: absolute;
  background: rgba(255,255,255,0.25);
}
.film-crosshair::before {
  width: 2px; height: 100%;
  left: 50%; transform: translateX(-50%);
}
.film-crosshair::after {
  width: 100%; height: 2px;
  top: 50%; transform: translateY(-50%);
}
.film-count {
  font-size: 280px;
  font-weight: 900;
  color: rgba(255,255,255,0.9);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  font-family: var(--font-display);
}
.film-flicker { position: absolute; inset: 0; background: white; opacity: 0; pointer-events: none; }
</style>

<div class="film-leader" id="film-leader">
  <div class="film-circle-outer"></div>
  <div class="film-crosshair" style="position:absolute;inset:0;"></div>
  <div class="film-count" id="film-count">5</div>
  <div class="film-flicker" id="film-flicker"></div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

const countEl = document.querySelector('#film-count');

const flicker = document.querySelector('#film-flicker');

// Count down 5 → 1 with a frame flicker on each count.
// Digit and flicker are functions of time, so any seek shows the right frame (never tl.call)
const leader = { t: 0 };
tl.to(leader, { t: 2.8, duration: 2.8, ease: "none",
  onUpdate: () => {
    countEl.textContent = 5 - Math.min(4, Math.floor(leader.t / 0.6));
    const sinceCount = leader.t % 0.6;
    flicker.style.opacity = sinceCount < 0.08 ? 0.7 * (1 - sinceCount / 0.08) : 0;
  } }, 0);

// Leader out: flash to white, then composition begins
tl.to('#film-flicker', { opacity: 1, duration: 0.05, ease: 'steps(1)' }, 2.8);
tl.to('#film-leader', { opacity: 0, duration: 0.1 }, 2.9);
</script>
```

## Refraction glass pane

A refraction glass pane is a low-energy UI element: a frosted card that bends the background behind it.

A UI element that appears to be made of thick refractive glass. Light bends differently through it. CSS only, backdrop-filter + SVG border refraction.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="glass-refract" x="-2%" y="-2%" width="104%" height="104%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="1"
                    seed="37" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise"
                        scale="2" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>

<style>
.glass-pane {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(24px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.15),
    inset 0 -1px 0 rgba(0,0,0,0.2),
    0 20px 60px rgba(0,0,0,0.4),
    0 1px 3px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
}
.glass-pane::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255,255,255,0.08) 0%,
    transparent 50%,
    rgba(255,255,255,0.03) 100%
  );
  border-radius: inherit;
  pointer-events: none;
}
.glass-pane-inner {
  filter: url(#glass-refract);
}
</style>

<div class="glass-pane" style="width:720px;">
  <div class="glass-pane-inner" style="padding:48px;font:700 64px/1.2 var(--font-display);color:var(--text-primary);">
    Through the glass
  </div>
</div>
```

## Streak speed lines

Streak speed lines are a high-energy motion emphasis (0.2 to 0.5 s) of seeded lines that sell a fast move.

Speed lines radiate from a focal point, communicating extreme velocity. Used to punctuate arrivals or superhero-level moments.

```html
<canvas id="streaks-canvas" style="position:absolute;inset:0;pointer-events:none;opacity:0;"></canvas>

<script>
const canvas = document.querySelector('#streaks-canvas');
const ctx = canvas.getContext('2d');
canvas.width = 1080;
canvas.height = 1920;

const CX = 540, CY = 960;
const rng = seededRandom(42);
const LINE_COUNT = 60;

const lines = Array.from({ length: LINE_COUNT }, () => {
  const angle = rng() * Math.PI * 2;
  const inner = 80 + rng() * 200;
  const length = 400 + rng() * 800;
  const width = 0.5 + rng() * 3;
  return { angle, inner, length, width };
});

function drawStreaks(alpha) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  lines.forEach(l => {
    const x1 = CX + Math.cos(l.angle) * l.inner;
    const y1 = CY + Math.sin(l.angle) * l.inner;
    const x2 = CX + Math.cos(l.angle) * (l.inner + l.length);
    const y2 = CY + Math.sin(l.angle) * (l.inner + l.length);

    const grad = ctx.createLinearGradient(x1, y1, x2, y2);
    grad.addColorStop(0, `rgba(255,255,255,${alpha * 0.9})`);
    grad.addColorStop(1, 'rgba(255,255,255,0)');

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = grad;
    ctx.lineWidth = l.width;
    ctx.stroke();
  });
}

const proxy = { alpha: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to(proxy, {
  alpha: 1,
  duration: 0.15,
  ease: 'power3.out',
  onUpdate: () => drawStreaks(proxy.alpha)
}, 0);

tl.to(proxy, {
  alpha: 0,
  duration: 0.3,
  ease: 'power2.in',
  onUpdate: () => drawStreaks(proxy.alpha)
}, 0.15);

tl.to(canvas, { opacity: 1, duration: 0 }, 0);
tl.to(canvas, { opacity: 0, duration: 0.1 }, 0.45);
</script>
```

## Counter ring progress

A counter ring is a medium-energy metric showcase (1 to 2 s): a circular stroke fills while the number counts.

An SVG arc draws itself around a center metric, like a loading ring that reveals a percentage or score. Clean, satisfying, data-forward.

```html
<svg id="ring-progress" viewBox="0 0 200 200" style="width:300px;height:300px;">
  <circle cx="100" cy="100" r="85"
          fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12"/>
  <circle id="ring-arc" cx="100" cy="100" r="85"
          fill="none" stroke="var(--accent)" stroke-width="12"
          stroke-linecap="round"
          stroke-dasharray="534" stroke-dashoffset="534"
          transform="rotate(-90 100 100)"/>
  <text x="100" y="95" text-anchor="middle" fill="var(--text-primary)"
        font-size="48" font-weight="700" font-family="var(--font-display)">
    <tspan id="ring-pct">0%</tspan>
  </text>
  <text x="100" y="125" text-anchor="middle" fill="var(--text-secondary)"
        font-size="19" font-family="var(--font-body)">of goal</text>
</svg>

<script>
// Circumference = 2π × 85 ≈ 534
const CIRC = 2 * Math.PI * 85;
const TARGET_PCT = 87; // 87%

const arc = document.querySelector('#ring-arc');
const pctEl = document.querySelector('#ring-pct');
const proxy = { pct: 0 };

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to(proxy, {
  pct: TARGET_PCT,
  duration: 1.6,
  ease: 'power2.out',
  onUpdate() {
    const offset = CIRC * (1 - proxy.pct / 100);
    arc.setAttribute('stroke-dashoffset', offset);
    pctEl.textContent = Math.round(proxy.pct) + '%';
  }
}, 0);
</script>
```

## Compositing principles for VFX

Compositing principles combine layers with blend modes, canvas and filter chains so effects read as one image.

### Blend Mode Stack for Depth

```css
/* Layer order for maximum depth perception */
.layer-0-environment { mix-blend-mode: normal; }            /* deepest — no blend */
.layer-1-atmosphere  { mix-blend-mode: screen; opacity: 0.4; }   /* adds glow without muddying */
.layer-2-content     { mix-blend-mode: normal; }            /* critical — always normal */
.layer-3-hud         { mix-blend-mode: overlay; opacity: 0.6; }  /* subtle color unification */
```

### Canvas + HTML Compositing

```html
<!-- Canvas sits under HTML content via z-index -->
<canvas id="bg-canvas" width="1920" height="1080" style="position:absolute;inset:0;z-index:1;"></canvas>
<div class="content-layer" style="position:relative;z-index:2;font:800 120px/1.2 var(--font-display);color:var(--text-primary);">
  HTML composites over the canvas
</div>
<script>
  const bg = document.getElementById('bg-canvas').getContext('2d');
  bg.fillStyle = '#20304a';
  bg.fillRect(0, 0, 1920, 1080);
</script>
```

### Filter Chain for Film Look

```xml
<!-- The region matches the element, or the grain fills the default 10% margin around it as a grey band -->
<filter id="film-grade" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
  <!-- 1. Film grain -->
  <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="1" seed="9" result="grain"/>
  <feColorMatrix in="grain" type="saturate" values="0" result="bwGrain"/>
  <feBlend in="SourceGraphic" in2="bwGrain" mode="overlay" result="grained"/>
  <!-- 2. Color grade -->
  <feComponentTransfer in="grained" result="graded">
    <feFuncR type="gamma" amplitude="1.05" exponent="0.88" offset="0.02"/>
    <feFuncG type="gamma" amplitude="0.98" exponent="0.92" offset="0.01"/>
    <feFuncB type="gamma" amplitude="0.92" exponent="0.98" offset="0.03"/>
  </feComponentTransfer>
  <!-- 3. Slight vignette via feFlood + radial clip -->
  <feFlood flood-color="black" flood-opacity="0.15" result="dark"/>
  <feComposite in="dark" in2="SourceGraphic" operator="in" result="vignette"/>
  <feBlend in="graded" in2="vignette" mode="multiply"/>
</filter>
```

## MorphSVG shape transition

A MorphSVG shape transition is a medium-to-high energy shape animation (0.8 to 2 s) that morphs one outline into another.

**Requires:** GSAP MorphSVG plugin (CDN load below)

Morphs one SVG path into another. Works on any `<path>` element. Used for logo reveals, blob transitions, icon state changes, and abstract shape animation between scenes.

```html
<!-- Load MorphSVG plugin alongside GSAP -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/MorphSVGPlugin.min.js"></script>

<svg viewBox="0 0 200 200" width="400" height="400" style="position:absolute;overflow:visible;">
  <!-- Start shape: circle -->
  <path id="morph-shape" fill="var(--accent)" opacity="0.9"
    d="M 100,20 A 80,80 0 1,1 99.9,20 Z"/>

  <!-- Target shapes — hidden, used only as morph targets -->
  <path id="target-star" style="display:none;"
    d="M 100,15 L 118,70 L 175,70 L 128,103 L 146,158 L 100,125 L 54,158 L 72,103 L 25,70 L 82,70 Z"/>
  <path id="target-blob" style="display:none;"
    d="M 100,30 C 145,20 175,55 170,95 C 165,135 140,165 100,168 C 60,171 30,145 28,105 C 26,65 55,40 100,30 Z"/>
</svg>

<script>
gsap.registerPlugin(MorphSVGPlugin);

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Entrance: circle fades in
tl.fromTo('#morph-shape', { opacity: 0, scale: 0.8 }, { opacity: 0.9, scale: 1, duration: 0.5, ease: 'back.out(1.4)' }, 0);

// Morph circle → star
tl.to('#morph-shape', {
  morphSVG: '#target-star',
  duration: 1.0,
  ease: 'power2.inOut'
}, 1.0);

// Morph star → blob
tl.to('#morph-shape', {
  morphSVG: '#target-blob',
  duration: 1.2,
  ease: 'elastic.out(1, 0.6)'
}, 2.5);

// Or morph to a raw path string directly:
// morphSVG: 'M 100,50 C 150,0 200,100 100,150 ...'
</script>
```

**Note:** MorphSVG requires paths with compatible node counts for smooth morphing. If shapes have different node counts, MorphSVG auto-adjusts but results may be less precise. Use the `shapeIndex` option to control alignment.

## Glitch block corruption

Glitch block corruption is a very high energy digital effect (0.2 to 0.6 s) that displaces seeded blocks of the frame.

Canvas 2D block-slice displacement. Copies horizontal strips of the composition at random offsets + adds RGB channel split. Maximum digital disruption with zero WebGL.

```html
<!-- A frame of the scene, exported as an image: a canvas can draw an image or a video, never a div -->
<img id="glitch-still" src="assets/glitch-still.png" alt="" style="display:none;">
<canvas id="glitch-source" style="display:none;"></canvas>
<canvas id="glitch-canvas" style="position:absolute;inset:0;pointer-events:none;"></canvas>

<script>
const src = document.getElementById('glitch-source');
const out = document.getElementById('glitch-canvas');
const W = 1080, H = 1920;
[src, out].forEach(c => { c.width = W; c.height = H; });

const srcCtx = src.getContext('2d');
const outCtx = out.getContext('2d');

// Export the still first (snapshot --at <time> into a spare folder, then copy it to assets/).
// buildReady makes capture wait until it is decoded and drawn into the source canvas.
const still = document.getElementById('glitch-still');
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady['glitch-still'] = still.decode().then(() => {
  srcCtx.drawImage(still, 0, 0, W, H);
});

function drawGlitch(progress) {
  outCtx.clearRect(0, 0, W, H);
  if (progress <= 0) return;

  // A new generator per draw: the same progress gives the same blocks in any seek order
  const rng = seededRandom(777 + Math.round(progress * 1000));

  // Base: copy source clean
  outCtx.drawImage(src, 0, 0);

  const blockCount = Math.floor(2 + rng() * 10 * progress);

  for (let i = 0; i < blockCount; i++) {
    const y = Math.floor(rng() * H);
    const h = Math.floor(3 + rng() * 50);
    const xShift = (rng() - 0.5) * 160 * progress;
    const yShift = (rng() - 0.5) * 8 * progress;

    // Slice copy at offset
    outCtx.drawImage(src, 0, y, W, h, xShift, y + yShift, W, h);

    // RGB channel split on some slices
    if (rng() > 0.6) {
      outCtx.globalCompositeOperation = 'screen';
      outCtx.fillStyle = `rgba(255, 0, 50, ${0.25 * progress})`;
      outCtx.fillRect(xShift + 6, y, W, h);
      outCtx.fillStyle = `rgba(0, 200, 255, ${0.2 * progress})`;
      outCtx.fillRect(xShift - 6, y, W, h);
      outCtx.globalCompositeOperation = 'source-over';
    }
  }

  // Horizontal scan artifact lines
  const lineCount = Math.floor(rng() * 4 * progress);
  for (let i = 0; i < lineCount; i++) {
    const ly = Math.floor(rng() * H);
    outCtx.fillStyle = `rgba(255, 255, 255, ${0.15 * progress})`;
    outCtx.fillRect(0, ly, W, 1 + Math.floor(rng() * 3));
  }
}

const proxy = { p: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Glitch pulse: ramp up → hold → decay
tl.to(proxy, { p: 1.0, duration: 0.08, ease: 'steps(3)', onUpdate: () => drawGlitch(proxy.p) }, 0);
tl.to(proxy, { p: 0.7, duration: 0.15, ease: 'power1.out', onUpdate: () => drawGlitch(proxy.p) }, 0.08);
tl.to(proxy, { p: 0.0, duration: 0.25, ease: 'power2.in', onUpdate: () => drawGlitch(proxy.p) }, 0.23);
</script>
```

## Ink wash reveal

An ink wash reveal is a medium-energy content entrance (0.8 to 1.5 s) that spreads content in through an organic mask.

SVG `feDisplacementMap` applied to an HTML element creates an organic ink-spreading reveal. The element appears to crystallize out of liquid. Applies to text, images, cards, any DOM element.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="ink-wash" x="-15%" y="-15%" width="130%" height="130%">
      <feTurbulence id="ink-turb" type="turbulence"
                    baseFrequency="0.035" numOctaves="4" seed="13" result="noise"/>
      <feDisplacementMap id="ink-dm" in="SourceGraphic" in2="noise"
                         scale="120" xChannelSelector="R" yChannelSelector="G"
                         result="spread"/>
      <feGaussianBlur in="spread" stdDeviation="2" result="soft"/>
      <feComposite in="soft" in2="SourceGraphic" operator="over"/>
    </filter>
  </defs>
</svg>

<!-- Any element can receive the ink-wash reveal -->
<div id="ink-target" style="filter: url(#ink-wash); opacity: 0;">
  <h1 style="font-size: 120px; font-weight: 900; color: var(--text-primary);">EMERGE</h1>
</div>

<script>
const turb = document.querySelector('#ink-turb');
const dm   = document.querySelector('#ink-dm');

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Phase 1: element fades in while maximally distorted (displacement = 120)
tl.to('#ink-target', { opacity: 1, duration: 0.1 }, 0);

// Phase 2: displacement scale collapses to 0 — element "crystallizes" out of ink
tl.fromTo(dm, { attr: { scale: 120 } }, { attr: { scale: 0 }, duration: 1.2, ease: 'expo.out' }, 0.1);

// Phase 3: noise frequency evolves simultaneously for organic texture
tl.fromTo(turb,
  { attr: { baseFrequency: '0.035' } },
  { attr: { baseFrequency: '0.008' }, duration: 1.2, ease: 'expo.out' },
  0.1
);

// Optional: hold with subtle breathing after reveal
tl.to(dm, { attr: { scale: 4 }, duration: 3, ease: 'sine.inOut', yoyo: true, repeat: 3 }, 1.4);
</script>
```

**Adapt for transition use:** Apply to the incoming scene container. Start at `scale: 200`, collapse to 0 over 1.0s for a full-scene ink-wash transition.

## Geometric SVG tile background

A geometric SVG tile background is a low-energy ambient pattern that drifts once across the scene.

A repeating geometric SVG pattern that fills the full canvas. Zero performance cost, crisp at any resolution. Repeating tiles usually look cheap, so keep this for a deliberately technical world such as a blueprint or a data room, and use organic noise for everything else.

**Pattern A, Fine grid (precision / technical mood):**
```html
<svg id="bg-tile" style="position:absolute;inset:0;width:100%;height:100%;z-index:0;" aria-hidden="true">
  <defs>
    <pattern id="grid-pat" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M 80 0 L 0 0 0 80" fill="none"
            stroke="var(--border)" stroke-width="0.5" opacity="0.4"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid-pat)"/>
</svg>
<script>
// Subtle slow drift gives the grid life
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id
// Animate pattern offset via GSAP proxy
const patProxy = { x: 0, y: 0 };
const gridPat = document.querySelector('#grid-pat');
tl.to(patProxy, {
  x: 80, y: 40,
  duration: SCENE_DURATION, ease: 'none',  // one pass across the scene; never repeat: -1
  onUpdate() { gridPat.setAttribute('x', patProxy.x); gridPat.setAttribute('y', patProxy.y); }
}, 0);
</script>
```

**Pattern B, Dot matrix (editorial / minimal mood):**
```html
<svg id="bg-dots" style="position:absolute;inset:0;width:100%;height:100%;z-index:0;" aria-hidden="true">
  <defs>
    <pattern id="dot-pat" x="0" y="0" width="48" height="48" patternUnits="userSpaceOnUse">
      <circle cx="24" cy="24" r="1.5" fill="var(--border)" opacity="0.35"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#dot-pat)"/>
</svg>
```

**Pattern C, Diagonal hatch (kinetic / impact mood):**
```html
<svg id="bg-hatch" style="position:absolute;inset:0;width:100%;height:100%;z-index:0;" aria-hidden="true">
  <defs>
    <pattern id="hatch-pat" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="20"
            stroke="var(--accent-muted)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#hatch-pat)" opacity="0.3"/>
</svg>
```

**Pattern D, Hexagonal mesh (tech / data mood):**
```html
<svg id="bg-hex" style="position:absolute;inset:0;width:100%;height:100%;z-index:0;" aria-hidden="true">
  <defs>
    <pattern id="hex-pat" x="0" y="0" width="60" height="104"
             patternUnits="userSpaceOnUse">
      <!-- Flat-top hexagon path, 30px radius -->
      <path d="M30,2 L58,17 L58,47 L30,62 L2,47 L2,17 Z"
            fill="none" stroke="var(--border)" stroke-width="0.8" opacity="0.3"/>
      <path d="M30,54 L58,69 L58,99 L30,114 L2,99 L2,69 Z"
            fill="none" stroke="var(--border)" stroke-width="0.8" opacity="0.3"/>
      <path d="M60,28 L88,43 L88,73 L60,88 L32,73 L32,43 Z"
            fill="none" stroke="var(--border)" stroke-width="0.8" opacity="0.3"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#hex-pat)"/>
</svg>
```

**Usage rules:**
- Always `z-index: 0`: tile is the ground layer
- Keep opacity 0.2–0.4 on stroke, never compete with content
- Use `var(--border)` or `var(--accent-muted)` for color, never hardcode hex
- Combine with a radial glow on top for depth: `background: radial-gradient(ellipse 60% 50% at 50% 50%, var(--accent-muted) 0%, transparent 70%)`

## Constellation canvas background

A constellation canvas background is a medium-energy ambient field of seeded points joined by lines when close.

A Canvas 2D particle field with connecting lines between nearby nodes. Breathes and shifts slowly. Ideal as the background layer for tech, data, and science compositions. Fully deterministic and seek-safe.

```html
<canvas id="constellation-canvas"
  style="position:absolute;inset:0;width:100%;height:100%;z-index:0;"
  width="1920" height="1080">
</canvas>

<script>
function seededRandom(seed) {
  let count = seed | 0;
  return function next() {
    count = count + 0x2AC5E3B1 | 0;           // an odd step visits every 32-bit value once
    const spread = Math.imul(count, 0x4F2B71A3);
    const mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
    return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296;   // 0 up to 1
  };
}

const canvas = document.getElementById('constellation-canvas');
const ctx = canvas.getContext('2d');
const W = 1920, H = 1080;

const rng = seededRandom(42);
const NODE_COUNT = 80;
const CONNECT_DIST = 220;

// Fixed node positions — deterministic
const nodes = Array.from({ length: NODE_COUNT }, (_, i) => ({
  x: rng() * W,
  y: rng() * H,
  r: 1.5 + rng() * 2,         // base radius
  phase: rng() * Math.PI * 2  // breathing phase offset
}));

function drawFrame(t) {
  ctx.clearRect(0, 0, W, H);

  // Connections
  for (let i = 0; i < NODE_COUNT; i++) {
    for (let j = i + 1; j < NODE_COUNT; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < CONNECT_DIST) {
        const alpha = (1 - dist / CONNECT_DIST) * 0.18;
        ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.stroke();
      }
    }
  }

  // Nodes — pulsing radius driven by t
  nodes.forEach(n => {
    const pulse = 1 + 0.35 * Math.sin(t * 0.8 + n.phase);
    const alpha = 0.4 + 0.3 * Math.sin(t * 0.5 + n.phase);
    ctx.fillStyle = `rgba(148, 163, 184, ${alpha})`;
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.r * pulse, 0, Math.PI * 2);
    ctx.fill();
  });
}

const proxy = { t: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

const DURATION = 30; // match your composition duration
tl.to(proxy, {
  t: DURATION,
  duration: DURATION,
  ease: 'none',
  onUpdate() { drawFrame(proxy.t); }
}, 0);

// Initial frame
drawFrame(0);
</script>
```

**Adapt the color:** replace `rgba(148, 163, 184, ...)` with your `var(--accent)` parsed as RGB. For `#7C3AED` (purple accent): `rgba(124, 58, 237, alpha)`.

**Variants:**
- Reduce `NODE_COUNT` to 30 + increase `CONNECT_DIST` to 350 → sparse, elegant
- Add slow overall drift: inside `drawFrame` compute a local `const x = n.x + Math.sin(t * 0.1 + n.phase) * 40` (and the same for `y`) and draw edges and nodes with it; never write it back to the node, because that carries state between frames
- Layer with a dot-matrix SVG tile at 20% opacity beneath for double-depth

## Flowing noise field canvas background

A flowing noise field canvas background is a low-energy ambient flow of lines following a noise field.

Animated Perlin-style noise rendered as a flowing color field. Creates the impression of liquid, smoke, or energy without WebGL. Deterministic via seeded hash function.

```html
<canvas id="noise-canvas"
  style="position:absolute;inset:0;width:100%;height:100%;z-index:0;opacity:0.6;"
  width="480" height="270"> <!-- Low-res: upscaled by CSS, fast to draw -->
</canvas>

<script>
// Seeded smooth noise — no external libs needed
function hash21(x, y) {
  const mixed = Math.imul(x ^ 0x2AC5E3B1, 0x4F2B71A3) ^ Math.imul(y ^ 0x6C1F3A9D, 0x1D8E6A35);
  const folded = Math.imul(mixed ^ mixed >>> 15, 0x5B3E8C27);
  return ((folded ^ folded >>> 16) >>> 0) / 4294967296;
}
function smoothNoise(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y);
  const fx = x - ix, fy = y - iy;
  const ux = fx * fx * (3 - 2 * fx); // smoothstep
  const uy = fy * fy * (3 - 2 * fy);
  return (
    hash21(ix,   iy  ) * (1-ux) * (1-uy) +
    hash21(ix+1, iy  ) * ux     * (1-uy) +
    hash21(ix,   iy+1) * (1-ux) * uy     +
    hash21(ix+1, iy+1) * ux     * uy
  );
}

const canvas = document.getElementById('noise-canvas');
const ctx = canvas.getContext('2d');
const W = 480, H = 270;
const imgData = ctx.createImageData(W, H);

// Accent color: parse from design tokens (example: deep purple accent)
// R=60, G=20, B=120 — replace with your accent RGB
const [AR, AG, AB] = [60, 20, 120];

function drawFrame(t) {
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const nx = x / 60;
      const ny = y / 60;
      // FBM: 3 octaves of smooth noise
      let v = smoothNoise(nx + t * 0.12,       ny + t * 0.07);
      v    += smoothNoise(nx * 2 + t * 0.23,   ny * 2 - t * 0.15) * 0.5;
      v    += smoothNoise(nx * 4 - t * 0.18,   ny * 4 + t * 0.21) * 0.25;
      v /= 1.75; // normalize

      const idx = (y * W + x) * 4;
      imgData.data[idx]   = AR * v;      // R
      imgData.data[idx+1] = AG * v;      // G
      imgData.data[idx+2] = AB * v;      // B
      imgData.data[idx+3] = 220;         // A — adjust for opacity
    }
  }
  ctx.putImageData(imgData, 0, 0);
}

const proxy = { t: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

const DURATION = 20;
tl.to(proxy, {
  t: DURATION * 0.8,  // fractional to avoid visible loop jump
  duration: DURATION,
  ease: 'none',
  onUpdate() { drawFrame(proxy.t); }
}, 0);

drawFrame(0);
</script>
```

**Performance note:** 480×270 canvas upscaled via CSS `width: 100%; height: 100%` renders at 1/16 the pixel cost of full-res. The blur from upscaling is a feature, it makes noise smoother. For sharper detail, use 960×540.
