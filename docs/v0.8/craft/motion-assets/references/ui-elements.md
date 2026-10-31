---
title: UI elements for motion graphics
author: MOZGII, Inc.
lang: en
---

# UI elements for motion graphics

UI elements for motion graphics are interface-style components built for video rather than for clicking: glass dashboard panels, HUD frames, neon borders, metric readouts, progress rings, roadmaps, gradient mesh backgrounds, data tables, terminals and node networks. Each uses colour tokens as CSS variables and animates on the scene's paused timeline (`tl`, registered after its tweens). Inside a scene file, write entrances as `fromTo` rather than `from`. The examples read these tokens, declared on `:root` or the scene root: `--accent`, `--accent-2`, `--accent-muted`, `--bg`, `--surface`, `--border`, `--text-primary`, `--text-secondary`, `--text-dim`, `--font-display`, `--font-body`, `--font-mono`, plus `--accent-rgb`, `--accent-2-rgb` and `--bg-rgb` written as bare channels (`255,90,54`) so `rgba(var(--accent-rgb), 0.3)` can add its own alpha.

## Contents

The sections of this page:

- Glass dashboard panel
- HUD frame
- Neon glow border
- Multi-metric data readout
- Progress ring stack
- Roadmap timeline
- Gradient mesh background
- Data table entrance
- Terminal output
- Particle node network

## Glass dashboard panel

A glass dashboard panel is the standard frame for data-forward scenes. Multiple depth layers prevent the "floating glass slab" problem most implementations suffer from.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <filter id="panel-grain" x="-2%" y="-2%" width="104%" height="104%">
      <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="1"
                    seed="31" result="noise"/>
      <feColorMatrix in="noise" type="saturate" values="0" result="bwNoise"/>
      <feBlend in="SourceGraphic" in2="bwNoise" mode="overlay"/>
    </filter>
  </defs>
</svg>

<style>
.glass-panel {
  position: relative;
  border-radius: var(--panel-radius, 20px);
  overflow: hidden;
  /* Layer 1: background blur — the actual glass */
  backdrop-filter: blur(32px) saturate(1.4) brightness(1.1);
  -webkit-backdrop-filter: blur(32px) saturate(1.4) brightness(1.1);
  background: rgba(255,255,255,0.035);

  /* Layer 2: border system */
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow:
    /* Outer glow — accent color */
    0 0 0 1px rgba(var(--accent-rgb), 0.08),
    /* Depth shadow */
    0 24px 80px rgba(0,0,0,0.5),
    0 8px 24px rgba(0,0,0,0.3),
    /* Inner top edge highlight */
    inset 0 1px 0 rgba(255,255,255,0.12),
    /* Inner bottom edge shadow */
    inset 0 -1px 0 rgba(0,0,0,0.15);
}

/* Layer 3: surface gradient — adds apparent thickness */
.glass-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(
    145deg,
    rgba(255,255,255,0.07) 0%,
    transparent 40%,
    rgba(255,255,255,0.02) 100%
  );
  pointer-events: none;
}

/* Layer 4: noise grain — adds physical texture */
.glass-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0.04;
  /* fractal-noise tile, 200 px, generated once by the browser; no image file needed */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23g)'/%3E%3C/svg%3E");
  pointer-events: none;
}

.glass-panel-content {
  position: relative;
  z-index: 1;
  padding: var(--panel-padding, 32px);
}
</style>

<div class="glass-panel">
  <div class="glass-panel-content">
    <div style="font:600 32px/1.3 var(--font-body);color:var(--text-secondary);">Monthly revenue</div>
    <div style="font:800 96px/1.1 var(--font-display);color:var(--text-primary);">$2.8M</div>
  </div>
</div>
```

## HUD frame

A HUD frame gives a military or tech look with corner brackets, scan lines and data readouts. Works for sci-fi, AI, and technical compositions.

```html
<style>
.hud-frame {
  position: relative;
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  background: rgba(var(--bg-rgb), 0.85);
}

/* Corner brackets — top-left */
.hud-frame::before {
  content: '';
  position: absolute;
  top: -2px; left: -2px;
  width: 20px; height: 20px;
  border-top: 2px solid var(--accent);
  border-left: 2px solid var(--accent);
  box-shadow: -2px -2px 8px rgba(var(--accent-rgb), 0.4);
}

/* Corner bracket — bottom-right */
.hud-frame::after {
  content: '';
  position: absolute;
  bottom: -2px; right: -2px;
  width: 20px; height: 20px;
  border-bottom: 2px solid var(--accent);
  border-right: 2px solid var(--accent);
  box-shadow: 2px 2px 8px rgba(var(--accent-rgb), 0.4);
}

.hud-scan-overlay {
  position: absolute; inset: 0;
  /* a CSS background cannot use an SVG pattern, so the lines are a repeating gradient */
  background: repeating-linear-gradient(to bottom, rgba(0,0,0,0.15) 0 2px, transparent 2px 4px);
  opacity: 0.3;
  pointer-events: none;
}

/* Status indicator dot */
.hud-status {
  position: absolute;
  top: 8px; right: 8px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent), 0 0 16px rgba(var(--accent-rgb), 0.5);
}
</style>

<div class="hud-frame" style="width:720px;height:360px;">
  <div class="hud-scan-overlay"></div>
  <div class="hud-status"></div>
  <div class="hud-frame-content" style="padding:48px;font:600 40px/1.4 var(--font-mono);color:var(--text-primary);">Link stable<br>Signal 98%</div>
</div>

<!-- Additional corner brackets (top-right, bottom-left), added by script -->
<script>
function addHudCorners(el) {
  const corners = [
    { top: -2, right: -2, borderTop: true, borderRight: true },
    { bottom: -2, left: -2, borderBottom: true, borderLeft: true }
  ];
  corners.forEach(c => {
    const div = document.createElement('div');
    div.style.cssText = `
      position: absolute;
      width: 20px; height: 20px;
      ${c.top !== undefined ? `top: ${c.top}px;` : `bottom: ${c.bottom}px;`}
      ${c.left !== undefined ? `left: ${c.left}px;` : `right: ${c.right}px;`}
      ${c.borderTop ? `border-top: 2px solid var(--accent);` : `border-bottom: 2px solid var(--accent);`}
      ${c.borderRight ? `border-right: 2px solid var(--accent);` : `border-left: 2px solid var(--accent);`}
    `;
    el.appendChild(div);
  });
}
document.querySelectorAll('.hud-frame').forEach(addHudCorners);
</script>
```

### HUD Entrance Animation

```js
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Frame materializes: corners first, then border fills in
gsap.set('.hud-frame', { clipPath: 'inset(0 100% 100% 0)' });

tl.to('.hud-frame', {
  clipPath: 'inset(0 0% 0% 0)',
  duration: 0.6,
  ease: 'power3.inOut'
}, 0);

// Status dot blinks on
tl.fromTo('.hud-status',
  { opacity: 0 },
  { opacity: 1, duration: 0.1, ease: 'steps(1)', repeat: 4, yoyo: true },
  0.5
);

// Content fades in after frame establishes
tl.fromTo('.hud-frame-content',
  { opacity: 0, y: 8 },
  { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' },
  0.6
);
```

## Neon glow border

A neon glow border uses three layers of glow, which avoids the flat "box-shadow only" look most implementations use.

```html
<svg style="position:absolute;width:0;height:0;" aria-hidden="true">
  <defs>
    <!-- Layer 1: tight inner glow -->
    <filter id="neon-tight" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
      <feColorMatrix in="blur" type="saturate" values="2" result="vivid"/>
      <feMerge><feMergeNode in="vivid"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <!-- Layer 2: wide outer bloom -->
    <filter id="neon-bloom" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur"/>
      <feColorMatrix in="blur" type="saturate" values="3" result="vivid"/>
      <feMerge><feMergeNode in="vivid"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
</svg>

<style>
.neon-border-container {
  position: relative;
  width: 400px; height: 300px; /* the two SVG layers stretch to this box */
}

/* Layer 1: SVG path border — main stroke */
.neon-border-svg {
  position: absolute; inset: -2px;
  pointer-events: none;
  filter: url(#neon-tight);
}

/* Layer 2: bloom glow underneath */
.neon-border-bloom {
  position: absolute; inset: -2px;
  pointer-events: none;
  filter: url(#neon-bloom);
  opacity: 0.6;
}

/* Layer 3: CSS border for crisp top edge */
.neon-border-content {
  position: relative; box-sizing: border-box; height: 100%; padding: 32px;
  border-radius: 16px; border: 1px solid var(--accent);
  font: 700 48px/1.2 var(--font-display); color: var(--text-primary);
}
</style>

<div class="neon-border-container">
  <!-- Bloom layer (behind) -->
  <svg class="neon-border-bloom" viewBox="0 0 400 300" preserveAspectRatio="none">
    <rect x="2" y="2" width="396" height="296" rx="16"
          fill="none" stroke="var(--accent)" stroke-width="3"/>
  </svg>
  <!-- Sharp layer (front) -->
  <svg class="neon-border-svg" viewBox="0 0 400 300" preserveAspectRatio="none">
    <rect id="neon-rect" x="2" y="2" width="396" height="296" rx="16"
          fill="none" stroke="var(--accent)" stroke-width="1.5"
          stroke-dasharray="1384" stroke-dashoffset="1384"/>
  </svg>

  <!-- Content -->
  <div class="neon-border-content">Live now</div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Border draws itself in, rotating around the frame
tl.to('#neon-rect', {
  strokeDashoffset: 0,
  duration: 1.2,
  ease: 'power2.inOut'
}, 0);

// Pulse the glow after draw completes
tl.to('.neon-border-bloom', {
  opacity: 0.3,
  duration: 1.5,
  ease: 'sine.inOut',
  yoyo: true,
  repeat: 10
}, 1.3);
</script>
```

## Multi-metric data readout

A multi-metric data readout is a telemetry-style metric display with multiple counters and a live sparkline.

```html
<style>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: rgba(var(--accent-rgb), 0.12);
  border-radius: 16px;
  overflow: hidden;
}

.metric-cell {
  background: var(--surface);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-label {
  font-size: 28px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-dim);
  font-family: var(--font-mono, 'JetBrains Mono');
}

.metric-value {
  font-size: 48px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
  line-height: 1;
  font-family: var(--font-display);
}

.metric-delta {
  font-size: 28px;
  font-family: var(--font-mono, 'JetBrains Mono');
}
.metric-delta.up { color: #22C55E; }
.metric-delta.down { color: #EF4444; }

.metric-sparkline {
  margin-top: 12px;
  height: 32px;
}
</style>

<div class="metric-grid" id="metric-grid">
  <div class="metric-cell">
    <span class="metric-label">Revenue</span>
    <span class="metric-value" id="m-revenue">$0</span>
    <span class="metric-delta up" id="m-rev-delta">—</span>
    <svg class="metric-sparkline" id="spark-revenue" viewBox="0 0 120 32"></svg>
  </div>
  <div class="metric-cell">
    <span class="metric-label">Users</span>
    <span class="metric-value" id="m-users">0</span>
    <span class="metric-delta up" id="m-usr-delta">—</span>
  </div>
  <div class="metric-cell">
    <span class="metric-label">Uptime</span>
    <span class="metric-value" id="m-uptime">0.00%</span>
    <span class="metric-delta" id="m-upt-delta">—</span>
  </div>
</div>

<script>
const metrics = [
  { id: 'm-revenue', target: 2847000, prefix: '$', suffix: '', deltaId: 'm-rev-delta', delta: '+23.4%', dir: 'up' },
  { id: 'm-users', target: 48291, prefix: '', suffix: '', deltaId: 'm-usr-delta', delta: '+1,204 today', dir: 'up' },
  { id: 'm-uptime', target: 99.98, prefix: '', suffix: '%', deltaId: 'm-upt-delta', delta: '30d avg', dir: '' }
];

function seededRandom(seed) {
  let count = seed | 0;
  return function next() {
    count = count + 0x2AC5E3B1 | 0;           // an odd step visits every 32-bit value once
    const spread = Math.imul(count, 0x4F2B71A3);
    const mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
    return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296;   // 0 up to 1
  };
}

// Sparkline data — seeded deterministic values
const rng = seededRandom(456);
function genSparkline(count) {
  return Array.from({ length: count }, () => 0.2 + rng() * 0.8);
}

function drawSparkline(svgId, data) {
  const svg = document.getElementById(svgId);
  if (!svg) return;
  const w = 120, h = 32;
  const max = Math.max(...data), min = Math.min(...data);
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / (max - min)) * h;
    return `${x},${y}`;
  }).join(' ');

  svg.innerHTML = `
    <polyline points="${pts}" fill="none"
      stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>
    <polyline points="0,${h} ${pts} ${w},${h}" fill="rgba(var(--accent-rgb),0.12)"
      stroke="none"/>
  `;
}

drawSparkline('spark-revenue', genSparkline(20));

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Staggered metric entrance
metrics.forEach((m, i) => {
  const proxy = { val: 0 };
  const el = document.getElementById(m.id);
  const deltaEl = document.getElementById(m.deltaId);

  tl.to(proxy, {
    val: m.target,
    duration: 1.4,
    ease: 'power3.out',
    onUpdate() {
      const v = proxy.val;
      if (m.suffix === '%') {
        el.textContent = m.prefix + v.toFixed(2) + m.suffix;
      } else {
        el.textContent = m.prefix + Math.round(v).toLocaleString('en-US') + m.suffix;
      }
    }
  }, i * 0.15);

  // The delta is built hidden and switched on by the timeline, so it also goes away on a backward seek
  deltaEl.textContent = m.delta;
  deltaEl.className = `metric-delta ${m.dir}`;
  gsap.set(deltaEl, { opacity: 0 });
  tl.set(deltaEl, { opacity: 1 }, i * 0.15 + 1.4);
});
</script>
```

## Progress ring stack

A progress ring stack is a set of concentric rings, each showing a different metric. Visually rich, data-forward.

```html
<svg id="ring-stack" viewBox="0 0 240 240" style="width:320px;height:320px;">
  <!-- Ring tracks (background) -->
  <circle cx="120" cy="120" r="105" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
  <circle cx="120" cy="120" r="87"  fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
  <circle cx="120" cy="120" r="69"  fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>

  <!-- Animated arcs -->
  <circle id="ring-a" cx="120" cy="120" r="105" fill="none"
          stroke="var(--accent)" stroke-width="8" stroke-linecap="round"
          stroke-dasharray="659.7" stroke-dashoffset="659.7"
          transform="rotate(-90 120 120)"/>
  <circle id="ring-b" cx="120" cy="120" r="87" fill="none"
          stroke="var(--accent-2)" stroke-width="8" stroke-linecap="round"
          stroke-dasharray="546.6" stroke-dashoffset="546.6"
          transform="rotate(-90 120 120)"/>
  <circle id="ring-c" cx="120" cy="120" r="69" fill="none"
          stroke="var(--accent-muted)" stroke-width="8" stroke-linecap="round"
          stroke-dasharray="433.5" stroke-dashoffset="433.5"
          transform="rotate(-90 120 120)"/>

  <!-- Center label -->
  <text x="120" y="110" text-anchor="middle" fill="var(--text-primary)"
        font-size="38" font-weight="700" font-family="var(--font-display)">87</text>
  <!-- 21 units in a 240 viewBox drawn at 320 px is 28 px on screen -->
  <text x="120" y="142" text-anchor="middle" fill="var(--text-secondary)"
        font-size="21" font-family="var(--font-body)">Overall</text>
</svg>

<script>
// Circumferences: 2π × r
const rings = [
  { id: 'ring-a', circ: 659.7, pct: 0.87 },
  { id: 'ring-b', circ: 546.6, pct: 0.64 },
  { id: 'ring-c', circ: 433.5, pct: 0.91 }
];

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

rings.forEach((ring, i) => {
  const target = ring.circ * (1 - ring.pct);
  tl.to(`#${ring.id}`, {
    strokeDashoffset: target,
    duration: 1.5,
    ease: 'power2.out',
    delay: i * 0.15
  }, 0);
});
</script>
```

## Roadmap timeline

A roadmap timeline reveals steps in sequence, with nodes joined by drawn path lines.

```html
<svg id="timeline-svg" viewBox="0 0 60 600" style="position:absolute;left:40px;top:0;width:60px;height:600px;">
  <!-- Vertical spine -->
  <line id="spine" x1="30" y1="0" x2="30" y2="600"
        stroke="rgba(var(--accent-rgb),0.2)" stroke-width="1.5" stroke-dasharray="4 4"/>

  <!-- Animated fill line -->
  <line id="spine-fill" x1="30" y1="0" x2="30" y2="0"
        stroke="var(--accent)" stroke-width="2"/>

  <!-- Node circles -->
  <circle id="node-0" cx="30" cy="60"  r="8" fill="var(--bg)" stroke="var(--accent)" stroke-width="2"/>
  <circle id="node-1" cx="30" cy="220" r="8" fill="var(--bg)" stroke="var(--accent)" stroke-width="2" opacity="0.3"/>
  <circle id="node-2" cx="30" cy="380" r="8" fill="var(--bg)" stroke="var(--accent)" stroke-width="2" opacity="0.3"/>
  <circle id="node-3" cx="30" cy="540" r="8" fill="var(--bg)" stroke="var(--accent)" stroke-width="2" opacity="0.3"/>
</svg>

<div class="timeline-content-0" style="position:absolute;left:130px;top:36px;font:600 40px/1.2 var(--font-body);color:var(--text-primary);">Research</div>
<div class="timeline-content-1" style="position:absolute;left:130px;top:196px;font:600 40px/1.2 var(--font-body);color:var(--text-primary);">Prototype</div>
<div class="timeline-content-2" style="position:absolute;left:130px;top:356px;font:600 40px/1.2 var(--font-body);color:var(--text-primary);">Beta</div>
<div class="timeline-content-3" style="position:absolute;left:130px;top:516px;font:600 40px/1.2 var(--font-body);color:var(--text-primary);">Launch</div>

<script>
const nodeYs = [60, 220, 380, 540];

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

nodeYs.forEach((y, i) => {
  // Spine grows to next node
  tl.to('#spine-fill', {
    attr: { y2: y },
    duration: 0.6,
    ease: 'power2.inOut'
  }, i * 1.5);

  // Node activates
  tl.to(`#node-${i}`, {
    opacity: 1,
    fill: 'var(--accent)',
    duration: 0.2,
    ease: 'power2.out'
  }, i * 1.5 + 0.5);

  // Node pulse
  tl.to(`#node-${i}`, {
    attr: { r: 11 },
    duration: 0.15,
    ease: 'power3.out',
    yoyo: true,
    repeat: 1
  }, i * 1.5 + 0.5);

  // Content block enters
  tl.fromTo(`.timeline-content-${i}`,
    { opacity: 0, x: 20 },
    { opacity: 1, x: 0, duration: 0.4, ease: 'power2.out' },
    i * 1.5 + 0.6
  );
});
</script>
```

## Gradient mesh background

A gradient mesh background is a CSS mesh gradient that shifts slowly. No WebGL needed for subtle, elegant backgrounds.

```html
<style>
.mesh-bg {
  position: absolute; inset: 0;
  /* 4-point radial gradient mesh */
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%,
      color-mix(in oklch, var(--accent) 25%, var(--bg)) 0%,
      transparent 70%
    ),
    radial-gradient(ellipse 60% 80% at 80% 80%,
      color-mix(in oklch, var(--accent-2) 20%, var(--bg)) 0%,
      transparent 70%
    ),
    radial-gradient(ellipse 70% 50% at 60% 20%,
      color-mix(in oklch, var(--accent) 10%, var(--bg)) 0%,
      transparent 60%
    ),
    var(--bg);
}

.mesh-point-1,
.mesh-point-2 {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  mix-blend-mode: screen;
  pointer-events: none;
}
.mesh-point-1 {
  width: 500px; height: 500px;
  top: -100px; left: -100px;
  background: radial-gradient(circle, rgba(var(--accent-rgb), 0.15), transparent 70%);
}
.mesh-point-2 {
  width: 600px; height: 600px;
  bottom: -150px; right: -150px;
  background: radial-gradient(circle, rgba(var(--accent-2-rgb, var(--accent-rgb)), 0.10), transparent 70%);
}
</style>

<div class="mesh-bg">
  <div class="mesh-point-1" id="mesh-pt-1"></div>
  <div class="mesh-point-2" id="mesh-pt-2"></div>
</div>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Slow drift — mesh points move gently for life feel
tl.to('#mesh-pt-1', {
  x: 60, y: 80,
  duration: 12,
  ease: 'sine.inOut',
  yoyo: true, repeat: 5
}, 0);

tl.to('#mesh-pt-2', {
  x: -80, y: -60,
  duration: 10,
  ease: 'sine.inOut',
  yoyo: true, repeat: 6
}, 0);
</script>
```

## Data table entrance

A data table entrance scans rows in with a data-loading feel. Every row gets a micro-entrance.

```html
<style>
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono, 'JetBrains Mono');
  font-size: 28px;
}

.data-table thead tr {
  border-bottom: 1px solid rgba(var(--accent-rgb), 0.3);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 28px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-dim);
  font-weight: 500;
}

.data-table td {
  padding: 14px 16px;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.data-table .value-positive { color: #22C55E; }
.data-table .value-negative { color: #EF4444; }
.data-table .value-accent   { color: var(--accent); }
</style>

<table class="data-table" id="data-table">
  <thead>
    <tr>
      <th>Metric</th><th>Current</th><th>Target</th><th>Delta</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Conversion</td><td class="value-accent">4.7%</td><td>5.0%</td><td class="value-positive">+6.3%</td></tr>
    <tr><td>Avg. Session</td><td class="value-accent">3m 42s</td><td>4m 00s</td><td class="value-positive">+4.5%</td></tr>
    <tr><td>Bounce Rate</td><td class="value-accent">31.2%</td><td>28.0%</td><td class="value-negative">+3.2%</td></tr>
    <tr><td>Revenue</td><td class="value-accent">$284.7K</td><td>$300K</td><td class="value-positive">+5.4%</td></tr>
  </tbody>
</table>

<script>
const rows = document.querySelectorAll('#data-table tbody tr');
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Header scans in
tl.fromTo('#data-table thead tr',
  { opacity: 0, x: -12 },
  { opacity: 1, x: 0, duration: 0.4, ease: 'power2.out' },
  0
);

// Rows enter with stagger — data loading feel
tl.fromTo(rows,
  { opacity: 0, x: -8 },
  { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out', stagger: 0.08 },
  0.3
);

// Add scan line flash per row. GSAP cannot parse rgba(var(...)), so resolve the token first
const accentRgb = getComputedStyle(document.documentElement).getPropertyValue('--accent-rgb').trim();
rows.forEach((row, i) => {
  tl.fromTo(row, {
    backgroundColor: `rgba(${accentRgb}, 0.12)`
  }, {
    backgroundColor: `rgba(${accentRgb}, 0)`,
    duration: 0.4,
    ease: 'power2.out'
  }, 0.3 + i * 0.08);
});
</script>
```

## Terminal output

Terminal output gives a developer look: code types itself with a blinking cursor. Works for product demos and technical compositions.

```html
<style>
.terminal {
  background: #0A0A0A;
  border-radius: 12px;
  font-family: var(--font-mono, 'JetBrains Mono'), monospace;
  font-size: 28px;
  line-height: 1.8;
  overflow: hidden;
}

.terminal-titlebar {
  background: #1A1A1A;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.term-dot { width: 12px; height: 12px; border-radius: 50%; }
.term-dot-r { background: #FF5F57; }
.term-dot-y { background: #FEBC2E; }
.term-dot-g { background: #28C840; }

.terminal-body {
  padding: 24px;
  color: #E0E0E0;
}

.term-line { display: block; white-space: pre; }
.term-prompt { color: var(--accent); }
.term-comment { color: #666; }
.term-success { color: #22C55E; }
.term-cursor {
  display: inline-block;
  width: 2px; height: 1.2em;
  background: var(--accent);
  vertical-align: text-bottom;
  margin-left: 1px;
}
</style>

<div class="terminal" id="terminal">
  <div class="terminal-titlebar">
    <div class="term-dot term-dot-r"></div>
    <div class="term-dot term-dot-y"></div>
    <div class="term-dot term-dot-g"></div>
  </div>
  <div class="terminal-body" id="terminal-body">
    <span class="term-cursor" id="term-cursor"></span>
  </div>
</div>

<script>
const lines = [
  { text: '$ npx hyperframes init --template cinematic', type: 'prompt', delay: 0 },
  { text: '  Creating project...', type: 'comment', delay: 0.8 },
  { text: '  ✓ Design schema loaded', type: 'success', delay: 1.4 },
  { text: '  ✓ Motion director ready', type: 'success', delay: 1.8 },
  { text: '  ✓ 54 effects installed', type: 'success', delay: 2.2 },
  { text: '$ _', type: 'prompt', delay: 2.8 }
];

const SCENE_DURATION = 6; // the scene's length in seconds
const body = document.getElementById('terminal-body');
const cursor = document.getElementById('term-cursor');
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

lines.forEach(line => {
  const span = document.createElement('span');
  span.className = `term-line term-${line.type}`;
  span.textContent = '';
  body.insertBefore(span, cursor);

  // Type each character
  let charIndex = 0;
  tl.to({}, {
    duration: line.text.length * 0.03,
    ease: 'none',
    onUpdate() {
      const progress = this.progress();
      const newIndex = Math.floor(progress * line.text.length);
      if (newIndex !== charIndex) {
        charIndex = newIndex;
        span.textContent = line.text.slice(0, charIndex);
      }
    }
  }, line.delay);
  tl.set(span, { textContent: line.text }, line.delay + line.text.length * 0.03);
});

// Cursor blinks
tl.to('#term-cursor', {
  opacity: 0,
  duration: 0.5,
  ease: 'steps(1)',
  repeat: Math.max(0, Math.floor(SCENE_DURATION / 0.5) - 1), // finite: never -1
  yoyo: true
}, 0);
</script>
```

## Particle node network

A particle node network draws nodes joined by edges that appear when nodes are close. Used for network/graph compositions, AI/ML visualization, relationship diagrams.

```html
<canvas id="network-canvas" style="position:absolute;inset:0;width:100%;height:100%;"></canvas>

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

(function initNetwork() {
  const canvas = document.getElementById('network-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = 1080;
  canvas.height = 1920;

  const rng = seededRandom(717);
  const NODE_COUNT = 12;
  const EDGE_DIST = 350;

  // Seeded node positions — deterministic
  const nodes = Array.from({ length: NODE_COUNT }, (_, i) => ({
    x: 100 + rng() * 880,
    y: 200 + rng() * 1520,
    r: 4 + rng() * 8,
    // Each node has a fixed velocity for idle drift
    vx: (rng() - 0.5) * 0.4,
    vy: (rng() - 0.5) * 0.4,
    baseX: 0, baseY: 0, // set after creation
  }));
  nodes.forEach(n => { n.baseX = n.x; n.baseY = n.y; });

  // Get accent color from CSS token
  const style = getComputedStyle(document.documentElement);
  const accentHex = style.getPropertyValue('--accent').trim();

  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `${r},${g},${b}`;
  }
  const accentRgb = hexToRgb(accentHex);

  function draw(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update node positions with idle drift (sine-based for seek-safety)
    nodes.forEach((n, i) => {
      n.x = n.baseX + Math.sin(t * n.vx * 5 + i) * 20;
      n.y = n.baseY + Math.cos(t * n.vy * 5 + i * 1.3) * 20;
    });

    // Draw edges
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.sqrt(dx*dx + dy*dy);

        if (dist < EDGE_DIST) {
          const alpha = (1 - dist / EDGE_DIST) * 0.4;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = `rgba(${accentRgb}, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${accentRgb}, 0.7)`;
      ctx.fill();
      // Glow
      const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 4);
      grad.addColorStop(0, `rgba(${accentRgb}, 0.3)`);
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r * 4, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
    });
  }

  draw(0);

  window.addEventListener('hf-seek', (e) => {
    draw(e.detail.time);
  });
})();
</script>
```
