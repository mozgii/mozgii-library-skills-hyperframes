---
title: "Building motion assets: shaders, 3D, Lottie and SVG"
author: MOZGII, Inc.
lang: en
---

# Building motion assets: shaders, 3D, Lottie and SVG

Building motion assets means making reusable visual pieces (procedural environments, 3D objects, characters, icon systems, data morphs, technical drawings) with one of four techniques: WebGL shaders, Three.js, Lottie, or morphing SVG. Every asset follows the seek contract: drawn from the timeline's time, seeded, local files only. `tl` is the scene's paused timeline, registered after its tweens.

## Contents

The sections of this page:

- WebGL shader assets
- Three.js 3D assets
- Lottie assets
- Morphing SVG assets
- Technique pairing matrix

## WebGL shader assets

WebGL shader assets suit full-screen procedural environments, fluid systems, plasma fields, and any effect requiring per-pixel computation over large areas.

**HyperFrames WebGL contract:**
```js
// Time comes ONLY from hf-seek — never performance.now() or Date.now()
window.addEventListener('hf-seek', (e) => {
  gl.uniform1f(uTime, e.detail.time);
  render();
});

// Pixel ratio fixed for deterministic export
canvas.width = 1080;   // exact pixels — not CSS size
canvas.height = 1920;  // exact pixels
// NO renderer.setPixelRatio — raw WebGL, 1:1 always

// All geometry set up synchronously at init, not per-frame
```

### Minimal Shader Asset Boilerplate

```html
<canvas id="shader-asset" style="position:absolute;inset:0;width:100%;height:100%;"></canvas>

<script>
(function initShaderAsset() {
  const canvas = document.getElementById('shader-asset');
  canvas.width = 1080;
  canvas.height = 1920;

  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

  const vert = `
    attribute vec2 a_position;
    void main() { gl_Position = vec4(a_position, 0.0, 1.0); }
  `;

  const frag = `
    precision highp float;
    uniform float u_time;
    uniform vec2  u_resolution;
    // Design token colors passed as uniforms
    uniform vec3  u_accent;
    uniform vec3  u_bg;

    // ---- GLSL utilities ----
    // Cubing modulo 1019 reshuffles whole numbers; the products stay exact in a float
    float shuffle(float n) {
      n = mod(n + 211.0, 1019.0);
      return mod(mod(n * n, 1019.0) * n, 1019.0);
    }
    vec3 cornerSlope(vec3 corner) {
      float a = shuffle(shuffle(shuffle(corner.x) + corner.y) + corner.z);
      float b = shuffle(a + 389.0);
      float c = shuffle(b + 389.0);
      return vec3(a, b, c) / 509.5 - 1.0; // signed, so the noise swings around 0
    }

    float noise(vec3 p) {
      vec3 i = floor(p), f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      return mix(
        mix(mix(dot(cornerSlope(i),f), dot(cornerSlope(i+vec3(1,0,0)),f-vec3(1,0,0)), f.x),
            mix(dot(cornerSlope(i+vec3(0,1,0)),f-vec3(0,1,0)),
                dot(cornerSlope(i+vec3(1,1,0)),f-vec3(1,1,0)), f.x), f.y),
        mix(mix(dot(cornerSlope(i+vec3(0,0,1)),f-vec3(0,0,1)),
                dot(cornerSlope(i+vec3(1,0,1)),f-vec3(1,0,1)), f.x),
            mix(dot(cornerSlope(i+vec3(0,1,1)),f-vec3(0,1,1)),
                dot(cornerSlope(i+vec3(1,1,1)),f-vec3(1,1,1)), f.x), f.y), f.z);
    }

    float fbm(vec3 p) {
      float v = 0.0, a = 0.5;
      for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p *= 2.1;
        a *= 0.5;
      }
      return v;
    }
    // ---- end utilities ----

    void main() {
      vec2 uv = gl_FragCoord.xy / u_resolution;
      vec2 p = uv * 2.0 - 1.0;
      p.x *= u_resolution.x / u_resolution.y;

      // Your effect here — replace with specific recipe
      float n = 0.5 + 0.5 * fbm(vec3(p * 2.0, u_time * 0.3)); // fbm is signed: map it to 0-1
      vec3 col = mix(u_bg, u_accent, smoothstep(0.3, 0.7, n));

      gl_FragColor = vec4(col, 1.0);
    }
  `;

  // Compile shader
  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }

  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, vert));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, frag));
  gl.linkProgram(prog);
  gl.useProgram(prog);

  // Full-screen quad
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
  const pos = gl.getAttribLocation(prog, 'a_position');
  gl.enableVertexAttribArray(pos);
  gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

  // Uniforms
  const uTime = gl.getUniformLocation(prog, 'u_time');
  const uRes  = gl.getUniformLocation(prog, 'u_resolution');
  const uAccent = gl.getUniformLocation(prog, 'u_accent');
  const uBg   = gl.getUniformLocation(prog, 'u_bg');

  gl.uniform2f(uRes, canvas.width, canvas.height);

  // Parse CSS token to [r, g, b] 0-1 range
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1,3),16)/255;
    const g = parseInt(hex.slice(3,5),16)/255;
    const b = parseInt(hex.slice(5,7),16)/255;
    return [r, g, b];
  }

  // Read design tokens from CSS variables
  const style = getComputedStyle(document.documentElement);
  const accentColor = hexToRgb(style.getPropertyValue('--accent').trim());
  const bgColor = hexToRgb(style.getPropertyValue('--bg').trim());
  gl.uniform3fv(uAccent, accentColor);
  gl.uniform3fv(uBg, bgColor);

  function render() {
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  // Initial render
  gl.uniform1f(uTime, 0);
  render();

  // Seek-safe time source
  window.addEventListener('hf-seek', (e) => {
    gl.uniform1f(uTime, e.detail.time);
    render();
  });
})();
</script>
```

### Sci-Fi Grid Floor Shader

```glsl
// Drop into frag shader — replaces the main body above
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution;
  vec2 p = uv * 2.0 - 1.0;
  p.x *= u_resolution.x / u_resolution.y;

  // Perspective grid
  float y = p.y + 0.4;
  vec2 grid = fract(p / max(y, 0.001) * 4.0 + vec2(0.0, u_time * 0.5));
  float line = min(
    smoothstep(0.0, 0.03, grid.x) * smoothstep(1.0, 0.97, grid.x),
    smoothstep(0.0, 0.03, grid.y) * smoothstep(1.0, 0.97, grid.y)
  );
  line = 1.0 - line;

  // Horizon glow
  float horizon = exp(-abs(p.y + 0.4) * 8.0);
  vec3 gridColor = mix(u_bg, u_accent, line * 0.8 + horizon * 0.4);

  // Vignette
  float vig = 1.0 - dot(uv - 0.5, uv - 0.5) * 1.5;
  gl_FragColor = vec4(gridColor * vig, 1.0);
}
```

### Plasma Energy Field Shader

```glsl
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution;
  vec2 p = uv * 2.0 - 1.0;

  float t = u_time * 0.4;

  // Layered sine plasma
  float v = 0.0;
  v += sin(p.x * 4.0 + t);
  v += sin(p.y * 3.0 - t * 0.7);
  v += sin((p.x + p.y) * 2.5 + t * 1.1);
  v += sin(length(p) * 5.0 - t * 1.3);
  v = (v + 4.0) / 8.0; // normalize 0-1

  // Map to palette
  vec3 col = mix(u_bg, u_accent, v);
  col = mix(col, vec3(1.0), pow(v, 8.0) * 0.6); // bright core

  gl_FragColor = vec4(col, 1.0);
}
```

## Three.js 3D assets

Three.js 3D assets suit product shots, geometric sculptures, environment renders, and dynamic lighting scenes.

**Always invoke the `threejs` skill for renderer setup and hf-seek integration.** The patterns below complement that skill with asset-specific design.

**HyperFrames Three.js contract:**
```js
// Timeline-driven time — never use clock.getDelta() for determinism
window.addEventListener('hf-seek', (e) => {
  const t = e.detail.time;
  mixer.setTime(t);       // AnimationMixer if present
  mesh.rotation.y = t * rotSpeed;
  renderer.render(scene, camera);
});

// GSAP can also drive Three.js via proxy
const proxy = { t: 0 };
const tl = gsap.timeline({ paused: true });
tl.to(proxy, {
  t: totalDuration,
  duration: totalDuration,
  ease: 'none',
  onUpdate() {
    mesh.rotation.y = proxy.t * rotSpeed;
    renderer.render(scene, camera);
  }
}, 0);
window.__timelines = window.__timelines || {};
window.__timelines["<composition-id>"] = tl;
```

### 3D Product Orb: Glass Sphere

`RoomEnvironment` is an addon, not a member of `THREE`, so this asset is a module script and needs the import map from the `threejs` skill above it.

```js
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

(function init3DOrb() {
  const canvas = document.getElementById('orb-canvas');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(1); // deterministic
  renderer.setSize(600, 600);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
  camera.position.set(0, 0, 4);

  // Glass sphere — MeshPhysicalMaterial for physically correct refraction
  const geometry = new THREE.SphereGeometry(1, 128, 128);
  const material = new THREE.MeshPhysicalMaterial({
    roughness: 0.0,
    metalness: 0.0,
    transmission: 1.0,      // glass-like transparency
    ior: 1.5,               // index of refraction (glass ≈ 1.5)
    thickness: 0.5,
    envMapIntensity: 2.0,
    color: new THREE.Color(0xffffff),
  });

  const sphere = new THREE.Mesh(geometry, material);
  scene.add(sphere);

  // 3-point light rig
  const keyLight = new THREE.DirectionalLight(0xffffff, 3);
  keyLight.position.set(3, 5, 5);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x4080ff, 1.5);
  fillLight.position.set(-3, -2, 3);
  scene.add(fillLight);

  // Rim light — uses accent color from design token
  const style = getComputedStyle(document.documentElement);
  const rimColor = new THREE.Color(style.getPropertyValue('--accent').trim());
  const rimLight = new THREE.DirectionalLight(rimColor, 4);
  rimLight.position.set(0, -4, -3);
  scene.add(rimLight);

  // Ambient environment
  scene.add(new THREE.AmbientLight(0x111122, 2));

  // Environment map for reflections
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  const envTexture = pmremGenerator.fromScene(new RoomEnvironment()).texture;
  scene.environment = envTexture;

  // Seek-safe render
  window.addEventListener('hf-seek', (e) => {
    const t = e.detail.time;
    sphere.rotation.y = t * 0.5;
    sphere.rotation.x = Math.sin(t * 0.3) * 0.2;
    renderer.render(scene, camera);
  });

  // Initial render
  renderer.render(scene, camera);
})();
```

### 3D Geometric Sculpture: Icosahedron

This fragment goes inside an asset set up like the orb above: `style`, `scene`, `camera` and `renderer` come from there, and the scene needs a light, because `MeshStandardMaterial` draws black without one.

```js
// Wireframe icosahedron with animated vertex displacement
const geo = new THREE.IcosahedronGeometry(1.2, 4);
const mat = new THREE.MeshStandardMaterial({
  color: new THREE.Color(style.getPropertyValue('--accent').trim()),
  wireframe: true,
  emissive: new THREE.Color(style.getPropertyValue('--accent').trim()),
  emissiveIntensity: 0.3
});
const mesh = new THREE.Mesh(geo, mat);
scene.add(mesh);

// Vertex displacement on seek
const posAttr = geo.attributes.position;
const basePositions = Float32Array.from(posAttr.array);

window.addEventListener('hf-seek', (e) => {
  const t = e.detail.time;
  for (let i = 0; i < posAttr.count; i++) {
    const bx = basePositions[i*3], by = basePositions[i*3+1], bz = basePositions[i*3+2];
    const dist = Math.sqrt(bx*bx + by*by + bz*bz);
    const disp = Math.sin(dist * 3.0 + t * 2.0) * 0.08;
    posAttr.setXYZ(i, bx * (1 + disp), by * (1 + disp), bz * (1 + disp));
  }
  posAttr.needsUpdate = true;
  geo.computeVertexNormals();
  mesh.rotation.y = t * 0.4;
  renderer.render(scene, camera);
});
```

### Exploding View: Multi-Part Assembly

This fragment also runs inside such an asset, with `mesh1`, `mesh2` and `mesh3` already added to `scene`.

```js
// Parts start assembled → GSAP drives separation → reassemble
const parts = [mesh1, mesh2, mesh3]; // pre-loaded meshes
const homePositions = parts.map(p => p.position.clone());
const explodeOffsets = [
  new THREE.Vector3(0, 0.8, 0),
  new THREE.Vector3(-0.8, -0.4, 0),
  new THREE.Vector3(0.8, -0.4, 0)
];

const proxy = { t: 0 };
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Explode phase
tl.to(proxy, {
  t: 1,
  duration: 1.5,
  ease: 'power2.out',
  onUpdate() {
    parts.forEach((part, i) => {
      part.position.lerpVectors(homePositions[i],
        homePositions[i].clone().add(explodeOffsets[i]), proxy.t);
    });
    renderer.render(scene, camera);
  }
}, 0);

// Hold
tl.to({}, { duration: 1.5 }, 1.5);

// Reassemble
tl.to(proxy, {
  t: 0,
  duration: 1.0,
  ease: 'power3.in',
  onUpdate() {
    parts.forEach((part, i) => {
      part.position.lerpVectors(homePositions[i],
        homePositions[i].clone().add(explodeOffsets[i]), proxy.t);
    });
    renderer.render(scene, camera);
  }
}, 3.0);
```

## Lottie assets

Lottie assets suit animated characters, mascots, complex icon animations, UI mockups, and kinetic type loops.

**Always invoke the `lottie` skill for player setup and `window.__hfLottie` registration.**

**HyperFrames Lottie contract:**
```js
// Registration in window.__hfLottie (not window.__timelines); the runtime's adapter then sets every frame itself,
// so a Lottie needs no hf-seek listener of its own
window.__hfLottie = window.__hfLottie || [];
window.__hfLottie.push(player);
```

### Character Asset Pattern

```html
<div id="character-lottie" style="position:absolute; width:400px; height:400px;"></div>

<script>
(function initCharacter() {
  const player = lottie.loadAnimation({
    container: document.getElementById('character-lottie'),
    renderer: 'svg',           // SVG renderer — scalable, CSS-stylable
    loop: true,                // the idle cycle repeats; HyperFrames still sets every frame
    autoplay: false,
    path: './assets/character-idle.json'
  });

  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(player);
})();
</script>
```

### Lottie + GSAP Timeline Sync

Lottie and GSAP stay in sync when each Lottie state is its own timed clip: HyperFrames seeks every registered player,
so switching from an idle loop to a reaction is a cut between two clips, never `play()`, `stop()` or `playSegments()`
from script.

```html
<!-- Each wrapper is its own composition: the adapter counts from the nearest composition's start, so a plain clip
     would show the reaction already partway through when it appears -->
<div id="char-idle" data-composition-id="char-idle" data-no-timeline data-start="0" data-duration="2" data-track-index="3" data-width="400" data-height="400"><div id="idle-lottie" style="width:400px;height:400px"></div></div>
<div id="char-react" data-composition-id="char-react" data-no-timeline data-start="2" data-duration="3" data-track-index="3" data-width="400" data-height="400"><div id="react-lottie" style="width:400px;height:400px"></div></div>
<script>
  window.__hfLottie = window.__hfLottie || [];
  for (const [id, path, loop] of [["idle-lottie", "assets/char-idle.json", true], ["react-lottie", "assets/char-react.json", false]]) {
    window.__hfLottie.push(lottie.loadAnimation({ container: document.getElementById(id), renderer: "svg",
      loop, autoplay: false, path }));
  }
</script>
```

Export idle and reaction as separate files (or separate markers rendered to separate files) from the animation tool.

### Lottie Color Theming

```js
// Replace Lottie colors with design token values at runtime
// Use lottie-colorify or manual layer targeting

player.addEventListener('DOMLoaded', () => {
  // Get accent color from CSS token
  const accentHex = getComputedStyle(document.documentElement)
    .getPropertyValue('--accent').trim();

  // Target specific layers by name
  const layers = player.renderer.elements;
  layers.forEach(layer => {
    if (layer.data && layer.data.nm === 'accent-fill') {
      // Inject color — Lottie SVG renderer creates standard SVG elements
      const fills = layer.baseElement.querySelectorAll('[fill]');
      fills.forEach(el => el.setAttribute('fill', accentHex));
    }
  });
});
```

## Morphing SVG assets

Morphing SVG assets suit icon systems, data visualisation transitions, animated logos, and organic shape shifts.

**Key tool:** GSAP `MorphSVGPlugin`, free in the public `gsap` package since 3.13. Copy `dist/MorphSVGPlugin.min.js` from the same `gsap` version as the core into the project, load it after the core, and call `gsap.registerPlugin(MorphSVGPlugin)` before the first tween.

**HyperFrames contract:** All morphing driven by GSAP timeline registered in `window.__timelines`. No CSS animations, no SMIL.

### Morphing Icon System

```html
<svg id="icon-morph" viewBox="0 0 100 100" width="120" height="120">
  <!-- One visible path; the targets stay hidden and untouched, so any state can be reached twice -->
  <path id="icon-shape" d="M 30,20 L 30,80 L 80,50 Z" fill="var(--accent)"/>
  <path id="icon-play" d="M 30,20 L 30,80 L 80,50 Z" style="display:none"/>
  <path id="icon-pause" d="M 25,20 L 40,20 L 40,80 L 25,80 Z M 60,20 L 75,20 L 75,80 L 60,80 Z" style="display:none"/>
  <path id="icon-check" d="M 10,52 L 22,40 L 40,58 L 78,18 L 90,30 L 40,82 Z" style="display:none"/>
</svg>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

function morphTo(targetId, at) {
  tl.to('#icon-shape', { morphSVG: '#' + targetId, duration: 0.4, ease: 'power2.inOut' }, at);
}

// Timeline sequence: play → check → play
morphTo('icon-check', 1.0);
morphTo('icon-play', 2.5);
</script>
```

### Data Visualization Morphing

```html
<div id="data-total" style="position:absolute;left:96px;top:64px;font:800 96px/1 var(--font-display);color:var(--text-primary);font-variant-numeric:tabular-nums;">847</div>
<svg id="dataviz" viewBox="0 0 400 300" style="width:100%;height:100%;">
  <!-- Bar chart state — Q1 data -->
  <path id="bars-q1"
    d="M 40,240 L 40,120 L 80,120 L 80,240 Z
       M 120,240 L 120,80 L 160,80 L 160,240 Z
       M 200,240 L 200,160 L 240,160 L 240,240 Z"
    fill="var(--accent)" opacity="0.8"/>

  <!-- Line chart state — Q2 data (same path element, different d) -->
  <path id="bars-q2"
    d="M 40,240 L 40,100 L 80,100 L 80,240 Z
       M 120,240 L 120,60 L 160,60 L 160,240 Z
       M 200,240 L 200,140 L 240,140 L 240,240 Z"
    fill="var(--accent-2)" opacity="0.8" style="display:none"/>
</svg>

<script>
const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Morph Q1 bars into Q2 bars — appears as data updating; #bars-q2 stays hidden, only its shape is read
tl.to('#bars-q1', {
  morphSVG: '#bars-q2',
  fill: 'var(--accent-2)',
  duration: 0.8,
  ease: 'power3.inOut'
}, 2.0);

// Counter updates alongside morph
const q1Total = 847;
const q2Total = 1204;
const proxy = { val: q1Total };
tl.to(proxy, {
  val: q2Total,
  duration: 0.8,
  ease: 'power3.inOut',
  onUpdate() {
    document.querySelector('#data-total').textContent = Math.round(proxy.val).toLocaleString('en-US');
  }
}, 2.0);
</script>
```

### SVG Stroke Drawing: Technical Schematic

```html
<svg id="schematic" viewBox="0 0 800 600">
  <g stroke="var(--accent)" stroke-width="1.5" fill="none" opacity="0.7">
    <!-- Circuit traces -->
    <path id="trace-1" d="M 50,300 L 200,300 L 200,150 L 400,150"/>
    <path id="trace-2" d="M 400,150 L 600,150 L 600,300 L 750,300"/>
    <path id="trace-3" d="M 400,150 L 400,300 L 400,450"/>
    <!-- Nodes -->
    <circle id="node-1" cx="200" cy="300" r="6" fill="var(--accent)"/>
    <circle id="node-2" cx="400" cy="150" r="8" fill="var(--accent)"/>
    <circle id="node-3" cx="600" cy="300" r="6" fill="var(--accent)"/>
  </g>
</svg>

<script>
// Initialize all paths as undrawn
const traces = document.querySelectorAll('#schematic path');
traces.forEach(path => {
  const len = path.getTotalLength();
  gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
});
gsap.set('#schematic circle', { scale: 0, transformOrigin: 'center' });

const tl = gsap.timeline({ paused: true });
// After the last tween, register tl under this scene's data-composition-id

// Draw traces sequentially
traces.forEach((trace, i) => {
  tl.to(trace, {
    strokeDashoffset: 0,
    duration: 0.8,
    ease: 'power2.inOut'
  }, i * 0.4);
});

// Pop nodes at their trace endpoints
document.querySelectorAll('#schematic circle').forEach((node, i) => {
  tl.to(node, {
    scale: 1,
    duration: 0.3,
    ease: 'back.out(2)'
  }, i * 0.4 + 0.6);
});
</script>
```

## Technique pairing matrix

The technique pairing matrix combines two techniques for one asset goal.

| Asset Goal | Primary | Secondary | Combine How |
|---|---|---|---|
| Character in 3D environment | Lottie | Three.js | Lottie SVG over Three.js canvas via z-index |
| Organic 3D sculpture with shader surface | Three.js | WebGL | Three.js with `ShaderMaterial` for custom surface |
| Data chart that morphs between states | Morphing SVG | Canvas 2D | SVG for shape, Canvas for particle burst at transition |
| Futuristic UI with live data | CSS/SVG | WebGL | CSS layout, WebGL shader as background |
| Icon that transforms meaning | Morphing SVG | Lottie | GSAP MorphSVG for path, Lottie for micro-motion detail |
| Logo reveal with depth | Three.js | SVG stroke | 3D text geometry + SVG trace animation on flat layers |
| Procedural background loop | WebGL | Canvas 2D | WebGL full-screen, Canvas 2D for overlaid particles |
