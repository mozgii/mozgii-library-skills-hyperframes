---
title: "VFX recipes: transitions, entrances and data"
author: MOZGII, Inc.
lang: en
---

# VFX recipes for HyperFrames: transitions, entrances and data

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

- Diagonal slice reveal
- Venetian blinds split
- Magnetic field lines background
- Cascade grid reveal
- Liquid mercury blob background
- Kinetic number ticker
- Chromatic aberration text
- Depth-of-field rack focus
- Particle burst on a data point
- 3D card flip
- Scan line sweep
- Aurora gradient background
- Shockwave ring

## Diagonal slice reveal

A diagonal slice reveal is a high-energy transition (0.6 to 0.9 s) that cuts the frame along a diagonal and slides the halves apart.

The incoming scene enters as a diagonal slash cuts across the frame, the new content filling from one side. Cinematic, aggressive, directional.

```html
<style>
.slice-container { position: relative; overflow: hidden; width: 100%; height: 100%; }
.slice-outgoing, .slice-incoming {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font: 800 120px/1 var(--font-display);
}
.slice-outgoing { background: var(--surface); color: var(--text-primary); }
.slice-incoming {
  background: var(--accent); color: var(--bg);
  clip-path: polygon(-20% 0%, -20% 0%, -40% 100%, -40% 100%);
}
</style>

<div class="slice-container">
  <div class="slice-outgoing">Before</div>
  <div class="slice-incoming" id="slice-in">After</div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// The slash sweeps left-to-right: polygon goes from left-edge to right-edge
tl.fromTo('#slice-in',
  { clipPath: 'polygon(-20% 0%, -20% 0%, -40% 100%, -40% 100%)' },
  {
    clipPath: 'polygon(-20% 0%, 120% 0%, 100% 100%, -40% 100%)',
    duration: 0.7,
    ease: 'power3.inOut'
  }, 0
);
// Outgoing scene slides away opposite direction
tl.to('.slice-outgoing', {
  x: '8%', opacity: 0, duration: 0.5, ease: 'power2.in'
}, 0);
</script>
```

**Adapt for 9:16:** Use a shallower diagonal angle (more horizontal sweep). Keep the clip-path polygon within the safe zone boundaries.

## Venetian blinds split

A venetian blinds split is a medium-to-high energy transition (0.5 to 0.8 s) that opens the next scene through staggered strips.

The outgoing scene breaks into horizontal strips (like venetian blinds) that flip open to reveal the incoming scene below. Staggered timing makes it feel mechanical and precise.

```html
<style>
.blinds-wrap {
  position: relative; overflow: hidden; width: 100%; height: 100%;
  --outgoing-snapshot: url("assets/outgoing-frame.png"); /* the last frame of the outgoing scene */
}
.incoming-scene {
  position: absolute; inset: 0; opacity: 0; background: var(--bg); color: var(--text-primary);
  display: flex; align-items: center; justify-content: center; font: 800 120px/1 var(--font-display);
}
.blind-strip {
  position: absolute; left: 0; width: 100%;
  overflow: hidden;
  transform-origin: top center;
  backface-visibility: hidden;
}
</style>

<div class="blinds-wrap">
  <div class="incoming-scene">Next scene</div>
</div>

<script>
const STRIP_COUNT = 8;
const wrap = document.querySelector('.blinds-wrap');
const totalH = wrap.offsetHeight;
const stripH = totalH / STRIP_COUNT;

// Build strips dynamically — each clones the outgoing content
const strips = Array.from({ length: STRIP_COUNT }, (_, i) => {
  const div = document.createElement('div');
  div.className = 'blind-strip';
  div.style.top = `${i * stripH}px`;
  div.style.height = `${stripH}px`;
  // Clone outgoing scene snapshot — or use background-position hack
  div.style.backgroundImage = 'var(--outgoing-snapshot)';
  div.style.backgroundSize = `100% ${totalH}px`;
  div.style.backgroundPosition = `0 -${i * stripH}px`;
  wrap.appendChild(div);
  return div;
});

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// GSAP's stagger has no seed and from: 'random' changes on every load, so shuffle once with the seeded PRNG
const rng = seededRandom(42);
const order = strips.map((_, i) => i);
for (let i = order.length - 1; i > 0; i--) {
  const j = Math.floor(rng() * (i + 1));
  [order[i], order[j]] = [order[j], order[i]];
}

order.forEach((stripIndex, slot) => {
  tl.to(strips[stripIndex], { scaleY: 0, duration: 0.4, ease: 'power2.in' }, slot * 0.05);
});

// Incoming content fades up underneath
tl.fromTo('.incoming-scene',
  { opacity: 0 },
  { opacity: 1, duration: 0.3, ease: 'power1.out' },
  0.25
);
</script>
```

## Magnetic field lines background

A magnetic field lines background is a medium-energy looping atmosphere of SVG curves that draw and undraw around a centre.

Animated field lines using SVG paths that emanate from a source point and bend organically. No WebGL required. Hypnotic ambient motion.

```html
<svg id="field-lines" style="position:absolute;inset:0;width:100%;height:100%;opacity:0.4;" 
     viewBox="0 0 1080 1920" preserveAspectRatio="xMidYMid slice">
  <defs>
    <filter id="field-blur">
      <feGaussianBlur stdDeviation="1.5"/>
    </filter>
  </defs>
  <!-- Lines generated by script -->
</svg>

<script>
const svg = document.querySelector('#field-lines');
const ns = 'http://www.w3.org/2000/svg';
const rng = seededRandom(77);
const LINE_COUNT = 24;
const W = 1080, H = 1920;
const CX = W / 2, CY = H * 0.4; // source point

const paths = Array.from({ length: LINE_COUNT }, (_, i) => {
  const angle = (i / LINE_COUNT) * Math.PI * 2;
  const r = rng();
  const path = document.createElementNS(ns, 'path');
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', 'var(--accent)');
  path.setAttribute('stroke-width', `${0.5 + r * 1.5}`);
  path.setAttribute('filter', 'url(#field-blur)');
  svg.appendChild(path);

  // Build a curved field line from center outward
  const endX = CX + Math.cos(angle) * (600 + r * 400);
  const endY = CY + Math.sin(angle) * (800 + r * 600);
  const cpX = CX + Math.cos(angle + 0.3) * 200;
  const cpY = CY + Math.sin(angle + 0.3) * 300;
  const d = `M ${CX} ${CY} Q ${cpX} ${cpY} ${endX} ${endY}`;
  path.setAttribute('d', d);
  return path;
});

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Animate strokeDashoffset for a drawing-in effect
paths.forEach((path, i) => {
  const len = path.getTotalLength();
  gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
  tl.to(path, {
    strokeDashoffset: 0,
    duration: 1.5 + (i % 3) * 0.4,
    ease: 'power2.inOut',
    repeat: Math.max(0, Math.floor(SCENE_DURATION / 1.5) - 1), // finite: never -1
    yoyo: true
  }, i * 0.08);
});
</script>
```

## Cascade grid reveal

A cascade grid reveal is a high-energy content entrance (0.8 to 1.4 s) that brings cells in as a diagonal wave.

Content tiles fall into place in a staggered grid pattern. Each cell appears from above with a slight physics-feel bounce. Feels like a scoreboard or dashboard coming online.

```html
<style>
.cascade-grid {
  display: grid;
  grid-template-columns: repeat(var(--cols, 3), 1fr);
  gap: var(--gap, 16px);
}
.cascade-cell {
  padding: 48px; border-radius: 12px; background: var(--surface);
  font: 700 56px/1.2 var(--font-display); color: var(--text-primary);
}
</style>

<div class="cascade-grid" id="cascade">
  <div class="cascade-cell">Plan</div><div class="cascade-cell">Draft</div><div class="cascade-cell">Build</div>
  <div class="cascade-cell">Test</div><div class="cascade-cell">Ship</div><div class="cascade-cell">Learn</div>
</div>

<script>
const cells = document.querySelectorAll('.cascade-cell');
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.fromTo(cells,
  { opacity: 0, y: -40 },
  {
    opacity: 1,
    y: 0,
    duration: 0.5,
    ease: 'back.out(1.4)',
    stagger: {
      amount: 0.6,
      grid: 'auto',
      from: 'start',
      axis: 'y'
    }
  },
  0
);
</script>
```

## Liquid mercury blob background

A liquid mercury blob background is a medium-to-high energy loop of metaballs that merge and split.

SVG filter + CSS radial gradient creates a metallic blob that morphs shape organically. No canvas needed. Works beautifully as a hero background or accent element.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="mercury-filter" color-interpolation-filters="sRGB"
            x="-30%" y="-30%" width="160%" height="160%">
      <feTurbulence id="mercury-turb" type="fractalNoise"
                   baseFrequency="0.012" numOctaves="3" seed="55" result="noise"/>
      <feDisplacementMap id="mercury-dm" in="SourceGraphic" in2="noise"
                        scale="60" xChannelSelector="R" yChannelSelector="G"
                        result="warped"/>
      <feColorMatrix in="warped" type="saturate" values="0" result="grey"/>
      <feComponentTransfer in="grey" result="contrast">
        <feFuncR type="gamma" amplitude="2.0" exponent="0.6" offset="0.1"/>
        <feFuncG type="gamma" amplitude="2.0" exponent="0.6" offset="0.1"/>
        <feFuncB type="gamma" amplitude="2.2" exponent="0.5" offset="0.15"/>
      </feComponentTransfer>
      <feBlend in="warped" in2="contrast" mode="overlay"/>
    </filter>
  </defs>
</svg>

<div id="mercury-blob" style="
  position: absolute;
  width: 600px; height: 600px;
  left: 50%; top: 50%;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 40%,
    rgba(255,255,255,0.9) 0%,
    rgba(200,200,220,0.7) 30%,
    rgba(120,120,160,0.5) 60%,
    rgba(60,60,80,0.3) 100%
  );
  filter: url(#mercury-filter);
">
</div>

<script>
const turb = document.querySelector('#mercury-turb');
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to(turb, {
  attr: { baseFrequency: '0.018' },
  duration: 8,
  ease: 'sine.inOut',
  yoyo: true,
  repeat: 10
}, 0);

tl.fromTo('#mercury-blob',
  { xPercent: -50, yPercent: -50, scale: 1 },
  { xPercent: -50, yPercent: -50, scale: 1.08, duration: 4, ease: 'sine.inOut', yoyo: true, repeat: 20 },
  0
);
</script>
```

## Kinetic number ticker

A kinetic number ticker is a high-energy data showcase (0.8 to 2 s per count) where digits roll like an odometer.

Numbers count from 0 to target with a slot-machine flutter effect. Each digit appears to cycle through values before landing. Essential for data/stats scenes.

```html
<style>
.ticker-wrap {
  display: inline-flex;
  align-items: baseline;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  overflow: hidden;
}
.ticker-digit {
  position: relative;
  display: inline-block;
  overflow: hidden;
  height: 1.2em;
}
.ticker-reel {
  display: flex;
  flex-direction: column;
  transform: translateY(0%);
}
.ticker-reel span {
  display: block;
  height: 1.2em;
  line-height: 1.2em;
}
</style>

<div class="ticker-wrap" id="ticker"></div>

<script>
function buildTicker(el, targetValue, prefix = '', suffix = '') {
  const digits = String(Math.round(targetValue)).split('');

  el.innerHTML = '';
  if (prefix) el.insertAdjacentHTML('beforeend', `<span>${prefix}</span>`);

  const reels = digits.map((digit, di) => {
    const wrap = document.createElement('div');
    wrap.className = 'ticker-digit';
    const reel = document.createElement('div');
    reel.className = 'ticker-reel';

    // Build reel with 0-9 then target digit repeated
    const nums = [...Array(10).keys(), parseInt(digit)];
    nums.forEach(n => {
      const span = document.createElement('span');
      span.textContent = n;
      reel.appendChild(span);
    });

    wrap.appendChild(reel);
    el.appendChild(wrap);
    return reel;
  });

  if (suffix) el.insertAdjacentHTML('beforeend', `<span>${suffix}</span>`);

  return reels;
}

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

const reels = buildTicker(document.querySelector('#ticker'), 2847, '$', 'M');

reels.forEach((reel, i) => {
  // Each reel scrolls to show the landing digit (index 10)
  // 11 items total, land on index 10 = -10 * height
  tl.to(reel, {
    y: '-' + (10 / 11 * 100) + '%',
    duration: 0.6 + i * 0.12,
    ease: 'expo.out',
    delay: i * 0.06
  }, 0);
});
</script>
```

## Chromatic aberration text

Chromatic aberration text is a medium-energy text effect (0.3 to 0.8 s) that splits a word into offset red, green and blue copies.

Text splits into RGB channels that are offset from each other, creating a glitch/holo feel. Pure CSS, no canvas needed.

```html
<style>
.chroma-text {
  position: relative;
  display: inline-block;
  color: var(--text-primary);
}
.chroma-red,
.chroma-cyan {
  position: absolute;
  top: 0; left: 0;
  mix-blend-mode: screen;
  pointer-events: none;
}
.chroma-red { color: #FF003C; }
.chroma-cyan { color: #00F5FF; }
</style>

<!-- Two real spans: GSAP targets elements, and a ::before or ::after is not one -->
<div class="chroma-text" id="chroma">SIGNAL<span class="chroma-red" aria-hidden="true" data-layout-allow-overlap data-layout-allow-overflow>SIGNAL</span><span class="chroma-cyan" aria-hidden="true" data-layout-allow-overlap data-layout-allow-overflow>SIGNAL</span></div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Entrance: channels converge from offset to center
tl.fromTo('#chroma .chroma-red',
  { x: -20, opacity: 0 },
  { x: -4, opacity: 0.8, duration: 0.6, ease: 'power3.out' }, 0
);
tl.fromTo('#chroma .chroma-cyan',
  { x: 20, opacity: 0 },
  { x: 4, opacity: 0.8, duration: 0.6, ease: 'power3.out' }, 0
);

// Optional: glitch pulse after settle
tl.to(['#chroma .chroma-red', '#chroma .chroma-cyan'], {
  x: (i) => i === 0 ? -8 : 8,
  duration: 0.05,
  ease: 'steps(1)',
  yoyo: true,
  repeat: 5
}, 1.0);
</script>
```

## Depth-of-field rack focus

A depth-of-field rack focus is a medium-energy camera effect (0.6 to 1.2 s) that shifts sharpness from one layer to another.

The foreground blurs out as midground content sharpens, simulating a camera focus pull. Uses staggered `feGaussianBlur` on depth layers.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="dof-blur" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur id="dof-gb" stdDeviation="0"/>
    </filter>
  </defs>
</svg>

<style>
.scene-layer { position: absolute; inset: 0; display: flex; justify-content: center; font-family: var(--font-display); }
.foreground { align-items: flex-end; padding-bottom: 120px; box-sizing: border-box; font-size: 160px; color: var(--accent); }
.midground { align-items: flex-start; padding-top: 160px; box-sizing: border-box; font-size: 96px; color: var(--text-primary); }
</style>

<!-- The foreground starts sharp and blurs out; the midground starts blurred and sharpens -->
<div class="scene-layer midground" id="mg" style="filter:blur(16px);">The team in the room</div>
<div class="scene-layer foreground" id="fg" style="filter:url(#dof-blur);">Close up</div>

<script>
const gb = document.querySelector('#dof-gb');
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Rack from foreground to midground
tl.to(gb, { attr: { stdDeviation: 18 }, duration: 0.7, ease: 'power2.inOut' }, 0);
tl.to('#mg', { filter: 'blur(0px)', duration: 0.7, ease: 'power2.out' }, 0.15);
tl.to('#fg', { opacity: 0.4, duration: 0.5, ease: 'power1.in' }, 0.2);
tl.to('#mg', { scale: 1.04, duration: 0.8, ease: 'power2.out' }, 0);
</script>
```

## Particle burst on a data point

A particle burst on a data point is a high-energy emphasis (0.4 to 0.8 s) that throws seeded particles out from a number as it lands.

A number or stat is revealed with a radial particle burst from its center. Particles are pre-seeded for determinism. Pure Canvas 2D.

```html
<canvas id="burst-canvas" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;"></canvas>

<script>
const canvas = document.querySelector('#burst-canvas');
const ctx = canvas.getContext('2d');
canvas.width = 1080;
canvas.height = 1920;

// A canvas fillStyle cannot read var(), so resolve the token once here
const accentRgb = getComputedStyle(document.documentElement).getPropertyValue('--accent-rgb').trim();

const rng = seededRandom(314);
const PARTICLE_COUNT = 80;
const CX = 540, CY = 960; // center point

const particles = Array.from({ length: PARTICLE_COUNT }, () => {
  const angle = rng() * Math.PI * 2;
  const speed = 200 + rng() * 600;
  const size = 2 + rng() * 6;
  const life = 0.5 + rng() * 0.5;
  return { angle, speed, size, life, x: CX, y: CY, alpha: 1 };
});

// Register in GSAP timeline via a proxy object
const proxy = { t: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to(proxy, {
  t: 1,
  duration: 0.8,
  ease: 'power2.out',
  onUpdate() {
    const progress = proxy.t;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      if (progress > p.life) return;
      const localP = progress / p.life;
      const dist = localP * p.speed;
      const px = CX + Math.cos(p.angle) * dist;
      const py = CY + Math.sin(p.angle) * dist;
      const alpha = 1 - localP;
      ctx.beginPath();
      ctx.arc(px, py, p.size * (1 - localP * 0.5), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${accentRgb}, ${alpha})`;
      ctx.fill();
    });
  }
}, 0);
</script>
```

## 3D card flip

A 3D card flip is a medium-energy transition (0.6 to 1 s) that turns a card in perspective to show its back.

An element rotates in 3D space, flipping to reveal a different face. Uses CSS perspective + transform-style: preserve-3d. Crisp and spatial.

```html
<style>
.flip-scene {
  perspective: 1200px;
  width: 720px; height: 420px; /* the card fills this, so it needs a size */
}
.flip-card {
  position: relative;
  width: 100%; height: 100%;
  transform-style: preserve-3d;
  transform: rotateY(0deg);
}
.flip-front, .flip-back {
  position: absolute; inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  display: flex; align-items: center; justify-content: center;
  border-radius: 24px; font: 800 96px/1 var(--font-display);
  background: var(--surface); color: var(--text-primary);
}
.flip-back {
  transform: rotateY(180deg);
  background: var(--accent); color: var(--bg);
}
</style>

<div class="flip-scene">
  <div class="flip-card" id="flip">
    <div class="flip-front">Question</div>
    <div class="flip-back" data-layout-allow-overlap>Answer</div>
  </div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Flip around Y axis
tl.fromTo('#flip',
  { rotateY: 0 },
  { rotateY: 180, duration: 0.8, ease: 'power2.inOut' }, 0
);

// Add a slight Z push at the midpoint for depth feel
tl.to('#flip', { z: 80, duration: 0.4, ease: 'power2.out' }, 0);
tl.to('#flip', { z: 0, duration: 0.4, ease: 'power2.in' }, 0.4);
</script>
```

## Scan line sweep

A scan line sweep is a medium-to-high energy text entrance (0.4 to 1.2 s) where a bright line passes and leaves text behind it.

A bright horizontal scan line sweeps downward, leaving content revealed below it. Military/tech/sci-fi feel. Pure CSS gradient + GSAP.

```html
<style>
.scanline-container { position: relative; overflow: hidden; }
.scanline-bar {
  position: absolute;
  left: 0; right: 0;
  height: 3px;
  background: linear-gradient(to right,
    transparent,
    var(--accent) 20%,
    rgba(255,255,255,0.9) 50%,
    var(--accent) 80%,
    transparent
  );
  box-shadow: 0 0 20px var(--accent), 0 0 60px rgba(var(--accent-rgb), 0.4);
  top: -3px;
  z-index: 10;
}
.scanline-content {
  clip-path: inset(0 0 100% 0);
}
</style>

<div class="scanline-container" id="scan-wrap">
  <div class="scanline-bar" id="scan-bar"></div>
  <div class="scanline-content" id="scan-content" style="padding:48px;font:800 120px/1.1 var(--font-display);color:var(--text-primary);">
    Access granted
  </div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

const height = document.querySelector('#scan-wrap').offsetHeight;

// Bar sweeps top to bottom, on a transform: top would snap to whole pixels
tl.fromTo('#scan-bar',
  { y: 0 },
  { y: height + 3, duration: 0.9, ease: 'power1.inOut' }, 0
);

// Content reveals as bar passes (clip-path follows bar position)
tl.to('#scan-content', {
  clipPath: 'inset(0 0 0% 0)',
  duration: 0.9,
  ease: 'power1.inOut'
}, 0);

// Bar fades out at end
tl.to('#scan-bar', { opacity: 0, duration: 0.15, ease: 'power1.in' }, 0.8);
</script>
```

## Aurora gradient background

An aurora gradient background is a low-to-medium energy loop of soft colour bands drifting across the frame.

A slow-breathing multi-color gradient that drifts across the frame. No canvas, no WebGL, pure CSS background-position animation. Zero CPU cost.

```html
<style>
.aurora-bg {
  position: absolute; inset: 0;
  background: linear-gradient(
    135deg,
    var(--bg) 0%,
    color-mix(in oklch, var(--accent) 30%, var(--bg)) 25%,
    color-mix(in oklch, var(--accent-2) 20%, var(--bg)) 50%,
    color-mix(in oklch, var(--accent) 15%, var(--bg)) 75%,
    var(--bg) 100%
  );
  background-size: 300% 300%;
  background-position: 0% 50%;
}
</style>

<div class="aurora-bg" id="aurora"></div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

tl.to('#aurora', {
  backgroundPosition: '100% 50%',
  duration: 8,
  ease: 'sine.inOut',
  yoyo: true,
  repeat: 10
}, 0);
</script>
```

## Shockwave ring

A shockwave ring is a very high energy emphasis (0.5 to 0.8 s): a ring expands from an impact point and fades.

A circular ring expands from a point like a shockwave, then dissolves. Used at the peak moment of a composition, when a stat hits, a headline lands.

```html
<style>
.shockwave-ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid var(--accent);
  width: 60px; height: 60px;
  left: 50%; top: 50%;
  opacity: 1;
  pointer-events: none;
}
</style>

<!-- Stack multiple rings for layered effect -->
<div class="shockwave-ring" id="ring-1"></div>
<div class="shockwave-ring" id="ring-2" style="border-color:rgba(var(--accent-rgb),0.5);"></div>
<div class="shockwave-ring" id="ring-3" style="border-color:rgba(var(--accent-rgb),0.25);"></div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

['#ring-1', '#ring-2', '#ring-3'].forEach((id, i) => {
  tl.fromTo(id,
    { xPercent: -50, yPercent: -50, scale: 0, opacity: 1 },
    { xPercent: -50, yPercent: -50, scale: 12, opacity: 0, duration: 0.7, ease: 'power2.out' },
    i * 0.1
  );
});
</script>
```

