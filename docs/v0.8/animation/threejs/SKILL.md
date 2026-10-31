---
name: threejs
description: Builds deterministic Three.js and WebGL scenes for HyperFrames video - a renderer drawn from the hf-seek event time instead of a requestAnimationFrame loop, fixed size and pixel ratio, GLTF models with AnimationMixer.setTime, camera moves as functions of time, seeded particles, and loaders that finish before capture. Use when a video needs 3D objects, product spins, camera flights, particles or shader planes, or when a Three.js layer renders blank or jittery.
metadata:
  tags:
  - threejs
  - three.js
  - webgl
  - 3d
  - gltf
  - hyperframes
  - particles
---

# Three.js for video

Three.js runs in HyperFrames through an adapter that publishes the frame's time and fires an `hf-seek` event; the
composition renders its scene for exactly that time. The adapter also waits on Three.js's default loading manager
when it finds `window.THREE`, so models and textures loaded through it finish before capture. Checked against three
0.187.0 (MIT).

## When to use this skill

Use this skill for 3D in a video: a product spin, an orbiting logo, a camera flight, particles, a shader plane, a GLTF
character, or a 3D layer that renders blank or jitters between renders.

## Step 0: read the three version the film loads

```bash
grep -rhoE 'three@[0-9]+\.[0-9]+\.[0-9]+' --include='*.html' . | sort -u   # CDN URLs in the import map
npm ls three --depth=0 2>/dev/null                                         # a bundled project
grep -n 'REVISION = ' node_modules/three/build/three.core.js 2>/dev/null   # a self-hosted copy
```

Coming from an older revision, read the Migration Guide on the three.js wiki first. From r186 to r187: PMREMs now use
cube render targets and `CubeUVReflectionMapping` is gone, so materials lit by an environment map can look slightly
different and baselines need a fresh look; `setViewport()` and `setScissor()` no longer scale by pixel ratio while a
render target is bound; `iridescenceThicknessRange` gives way to `iridescenceThicknessMinimum` and
`iridescenceThicknessMaximum`. From r185 to r186: `Object3D` gained `dispose()`, so a subclass with its own must call
`super.dispose()`, and `Source` became `TextureSource`.

## Pick how the scene gets its time

The source of the time decides where the code goes.

| When | Use | Why the others lose |
|---|---|---|
| One layer with its own motion, nothing shared with the 2D scene | an `hf-seek` listener | the plain path; a timeline adds nothing here |
| Camera or objects must share eases and times with HTML elements | plain numbers tweened on the GSAP timeline, drawn on update | a listener would need the eases written twice |
| Existing code already renders "the scene at time t", and the host may be moved or trimmed | a frame source on a host with `data-no-timeline` | start, trim and speed reach `t` with no code change |
| A heavy simulation that cannot be computed from `t` | bake it to video and place the file | a seek-rendered frame cannot depend on the frame before it |

## The seek contract for 3D

The seek contract for 3D has five rules.

1. Draw from the time in `e.detail.time` (or `window.__hfThreeTime`), never from `Clock`, `performance.now()` or deltas.
2. Render inside the `hf-seek` listener and once at load; no `requestAnimationFrame` loop or `setAnimationLoop` as the
   clock.
3. Fix the canvas size to the composition and the pixel ratio to 1 (or the render's integer scale).
4. Load models, textures and HDRIs from `assets/`; heavy async setup registers a `window.__hf.buildReady["key"]`
   promise so capture waits for it.
5. Every state is a function of `t`: no physics or particles that accumulate from the previous frame.

## Basic scene

A basic scene draws one mesh whose rotation is a function of time.

```html
<canvas id="three-layer" style="position:absolute;inset:0;width:100%;height:100%"></canvas>
<script type="importmap">
  { "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.187.0/examples/jsm/" } }
</script>
<script type="module">
  import * as THREE from "three";
  window.THREE = THREE;                 // a module sets no global; the adapter's load wait looks for this one
  const canvas = document.getElementById("three-layer");
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1920, 1080, false);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1920 / 1080, 0.1, 100);
  camera.position.set(0, 0, 6);
  const mesh = new THREE.Mesh(new THREE.IcosahedronGeometry(1.4, 4),
    new THREE.MeshStandardMaterial({ color: 0x64d2ff, roughness: 0.38 }));
  scene.add(mesh, new THREE.HemisphereLight(0xffffff, 0x223344, 2));

  function renderAt(t) {
    mesh.rotation.y = t * 0.7;
    mesh.rotation.x = Math.sin(t * 0.6) * 0.16;
    renderer.render(scene, camera);
  }
  window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
  renderAt(window.__hfThreeTime ?? 0);
</script>
```

Set `data-duration` on the root when no GSAP timeline defines the length.

The import map gives `three` and `three/addons/` one URL each, and it must come before the first module script. Addons
such as `GLTFLoader` import the bare name `three`, which a browser cannot resolve without the map. Point the map at
`build/three.module.js`, which imports `three.core.js` from beside it, so a local copy needs both files.
`build/three.module.min.js` is not in the npm package; jsDelivr generates it, and it breaks as soon as the project
self-hosts from `node_modules`.

## Driving 3D from a GSAP timeline

Driving 3D from a GSAP timeline lets the camera and objects share eases and times with the rest of the scene. Tween
plain numbers on the timeline and render on update:

```js
const cam = { z: 9, orbit: 0 };
tl.to(cam, { z: 5, duration: 2.4, ease: "power2.inOut" }, 0.5);
tl.to(cam, { orbit: Math.PI / 3, duration: 4, ease: "sine.inOut" }, 1.5);
tl.eventCallback("onUpdate", () => {
  camera.position.set(Math.sin(cam.orbit) * cam.z, 0.6, Math.cos(cam.orbit) * cam.z);
  camera.lookAt(0, 0, 0);
  renderer.render(scene, camera);
});
```

A slow orbit of 3 to 5 degrees a second keeps a 3D stage alive without drawing attention.

## A 3D scene as a frame source

A 3D scene as a frame source suits a layer whose code is already "render the scene at time t" and needs no GSAP:
register that function with `window.__hyperframes.registerFrameSource({ element, ready, render })` on a timed host
marked `data-no-timeline`, pass the loaders' promise as `ready`, and the runtime calls `render(t)` for every frame,
with the host's start, trim and speed already applied to `t`. Moving the host in Studio then retimes the 3D without
code changes.

## GLTF models and animation clips

GLTF models and animation clips load through `GLTFLoader` and are seeked with `AnimationMixer.setTime`.

```js
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";     // resolved by the import map above
let mixer;
window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady["robot"] = new GLTFLoader().loadAsync("assets/robot.glb").then((gltf) => {
  scene.add(gltf.scene);
  mixer = new THREE.AnimationMixer(gltf.scene);
  mixer.clipAction(gltf.animations[0]).play();      // play() only enables the action; setTime drives it
});
function renderAt(t) { if (mixer) mixer.setTime(t); renderer.render(scene, camera); }
```

Compress big models with Draco or Meshopt offline, and keep textures at the size they appear on screen.

## Seeded particles

Seeded particles place points with a seeded PRNG and move them by formula, so any frame can be drawn alone.

```js
function seededRandom(seed) { let count = seed | 0; return () => { count = count + 0x2AC5E3B1 | 0;
  const spread = Math.imul(count, 0x4F2B71A3), mixed = Math.imul((spread << 11 | spread >>> 21) ^ count, 0x1D8E6A35);
  return ((mixed ^ mixed >>> 16) >>> 0) / 4294967296; }; }
const rand = seededRandom(7), N = 4000, base = new Float32Array(N * 3), pos = new Float32Array(N * 3);
for (let i = 0; i < N * 3; i++) base[i] = (rand() - 0.5) * 12;
const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
scene.add(new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.02, color: 0xffffff })));
function placeAt(t) {
  for (let i = 0; i < N; i++) {
    pos[i * 3] = base[i * 3] + Math.sin(t * 0.3 + i) * 0.2;
    pos[i * 3 + 1] = ((base[i * 3 + 1] + t * 0.4 + 6) % 12) - 6;     // drift up, wrap: still a function of t
    pos[i * 3 + 2] = base[i * 3 + 2];
  }
  geo.attributes.position.needsUpdate = true;
}
```

## Verify the 3D layer

```bash
npx hyperframes check --json                               # no errors
npx hyperframes snapshot --at 0.5,2,4 -o /tmp/three-a
npx hyperframes snapshot --at 0.5,2,4 -o /tmp/three-b
for f in /tmp/three-a/*.png; do cmp "$f" "/tmp/three-b/$(basename "$f")"; done   # silent means the same pixels
grep -rnE 'requestAnimationFrame|setAnimationLoop|new THREE\.Clock' compositions index.html   # expect nothing
```

A blank frame with no console error usually means the listener never called `renderer.render()`.

## Checklist

- [ ] Rendering happens in `hf-seek` and at load, from the event's time.
- [ ] Canvas size equals the composition; pixel ratio fixed.
- [ ] Every asset local; async loads registered as `buildReady` promises.
- [ ] Particles, camera and mixers are functions of `t`; randomness seeded.
- [ ] Snapshots at three times match a second snapshot run.

## Gotchas

- **Symptom:** `Failed to resolve module specifier "three"`. **Cause:** An addon imports the bare name `three` and the
  page has no import map, or the map comes after a module script. **Fix:** put the map first, with `three` and
  `three/addons/` at one version.
- **Symptom:** A blank canvas. **Cause:** The seek handler changed the scene but never called `renderer.render()`.
  **Fix:** render inside the listener.
- **Symptom:** Frames differ between renders. **Cause:** A `requestAnimationFrame` loop or `Clock` delta advanced the
  scene. **Fix:** draw from `e.detail.time`.
- **Symptom:** Soft or wrongly sized output. **Cause:** `devicePixelRatio` leaked into the renderer. **Fix:** set it
  to 1.
- **Symptom:** The model is missing in early frames. **Cause:** The GLTF loaded after capture started. **Fix:**
  register a `buildReady` promise, or set `window.THREE` so the adapter sees the loading manager.
- **Symptom:** Post-processing trails differ. **Cause:** Effects that read the previous frame (motion trails, temporal
  AA) cannot be seeked. **Fix:** disable them or rebuild the effect from `t`.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `three.module.min.js` in the import map | `build/three.module.js`, with `three.core.js` beside it |
| mixing two three versions in the map | one version for `three` and `three/addons/` |
| physics or particles that accumulate | every state a function of `t` |
| textures far larger than they appear | resize them; compress models with Draco or Meshopt offline |

## See also

`webgpu`, `vfx`, `motion-assets`, `render-performance`.
