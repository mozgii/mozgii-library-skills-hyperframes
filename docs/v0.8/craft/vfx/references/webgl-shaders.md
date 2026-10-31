---
title: WebGL shader effects for video
author: MOZGII, Inc.
lang: en
---

# WebGL shader effects for video

WebGL shader effects draw per-pixel images (plasma, fluid warps, god rays, aurora, star fields, fire, ripples) on a canvas inside a HyperFrames composition. A shader renders correctly in a seek-driven video only when every frame is computed from a time uniform set by the timeline, with no frame-to-frame state. This page holds the contract, a boilerplate, a GLSL function library and recipes.

## Contents

The sections of this page:

- HyperFrames contract for shaders
- Minimal WebGL boilerplate
- Essential GLSL library functions
- VFX shader recipes
- Passing palette colours as uniforms
- Multi-pass rendering
- Shadertoy port checklist

## HyperFrames contract for shaders

The HyperFrames contract for shaders is the set of rules that keeps a shader seekable.

Every WebGL shader in a composition must follow these rules or it will render incorrectly during seek and capture.

**Time source:** `event.detail.time` from the `hf-seek` event. Never `performance.now()` or `Date.now()`.

**Pixel ratio:** Always `1`. Never device pixel ratio.

**Synchronous setup:** Compile shaders, create buffers, set uniforms synchronously at page load.

**Initial render:** Call render once at page load using `window.__hfThreeTime || 0`.

**No animation loop as the clock:** no `requestAnimationFrame` loop or timer drives the shader; every frame is drawn from the time in the `hf-seek` event.

## Minimal WebGL boilerplate

The minimal WebGL boilerplate below sets up a full-screen quad, compiles a fragment shader, and draws it for the time in each `hf-seek` event.

```html
<canvas id="vfx-canvas" style="position:absolute; inset:0; width:100%; height:100%;"></canvas>

<script>
(function() {
  const canvas = document.getElementById('vfx-canvas');
  // Match composition dimensions exactly
  const W = 1920, H = 1080;
  canvas.width = W;
  canvas.height = H;

  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  if (!gl) return;

  // ── Vertex shader — full-screen quad ─────────────────────────────────
  const VS = `
    attribute vec2 a_pos;
    varying vec2 v_uv;
    void main() {
      v_uv = a_pos * 0.5 + 0.5;
      gl_Position = vec4(a_pos, 0.0, 1.0);
    }
  `;

  // ── Fragment shader — THE VFX LIVES HERE ─────────────────────────────
  const FS = `
    precision highp float;
    uniform float u_time;
    uniform vec2  u_resolution;
    varying vec2  v_uv;

    void main() {
      vec2 uv = v_uv;
      // ... effect ...
      gl_FragColor = vec4(uv, 0.5 + 0.5 * sin(u_time), 1.0);
    }
  `;

  // ── Compile ──────────────────────────────────────────────────────────
  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog);
  gl.useProgram(prog);

  // ── Full-screen quad ─────────────────────────────────────────────────
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'a_pos');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  // ── Uniforms ─────────────────────────────────────────────────────────
  const uTime = gl.getUniformLocation(prog, 'u_time');
  const uRes  = gl.getUniformLocation(prog, 'u_resolution');
  gl.uniform2f(uRes, W, H);

  // ── Render function ──────────────────────────────────────────────────
  function render(t) {
    gl.viewport(0, 0, W, H);
    gl.uniform1f(uTime, t);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  // ── HyperFrames integration ──────────────────────────────────────────
  window.addEventListener('hf-seek', (e) => render(e.detail.time));
  render(window.__hfThreeTime || 0);
})();
</script>
```

## Essential GLSL library functions

Include these at the top of every fragment shader. They are the building blocks of all VFX.

**Noise guide:** Use `softNoise` when you need smooth organic motion without directional artifacts. Use `noise` (value noise) when performance is critical and slight grid alignment is acceptable. Use `worley` for cellular/tissue patterns.

```glsl
precision highp float;
uniform float u_time;
uniform vec2  u_resolution;
varying vec2  v_uv;

// ── Repeatable random numbers from whole numbers ───────────────────────
// Cubing modulo 1019 reshuffles 0..1018 with no repeats, and every product
// stays small enough for a float to hold it exactly. Fractions are dropped.
float shuffle(float n) {
  n = mod(floor(n) + 211.0, 1019.0);
  return mod(mod(n * n, 1019.0) * n, 1019.0);
}
float randomOf(float n) { return shuffle(n) / 1019.0; }
float randomOf(vec2 cell) { return shuffle(shuffle(cell.x) + cell.y) / 1019.0; }
vec2 randomPairOf(vec2 cell) {
  float first = shuffle(shuffle(cell.x) + cell.y);
  return vec2(first, shuffle(first + 389.0)) / 1019.0;
}

// ── Value noise: a random height at each grid corner, blended smoothly ──
float noise(vec2 p) {
  vec2 cell = floor(p);
  vec2 blend = smoothstep(0.0, 1.0, p - cell);
  float low  = mix(randomOf(cell),              randomOf(cell + vec2(1, 0)), blend.x);
  float high = mix(randomOf(cell + vec2(0, 1)), randomOf(cell + vec2(1, 1)), blend.x);
  return mix(low, high, blend.y);
}

// ── Layered noise: six octaves, each finer and turned, about 0 to 1 ────
float fbm(vec2 p) {
  const mat2 TURN = mat2(0.6, 0.8, -0.8, 0.6);
  float total = 0.0, weight = 0.5;
  for (int octave = 0; octave < 6; octave++) {
    total += weight * noise(p);
    weight *= 0.5;
    p = TURN * p * 2.03 + vec2(13.0, 7.0);
  }
  return total;
}

// ── Color space conversion ─────────────────────────────────────────────
vec3 hsl2rgb(vec3 hsl) {
  // How far the hue sits from red, green and blue on the wheel, 0 to 0.5
  vec3 away = abs(fract(hsl.x - vec3(0.0, 1.0, 2.0) / 3.0 + 0.5) - 0.5);
  vec3 pure = clamp(2.0 - 6.0 * away, 0.0, 1.0);
  float chroma = hsl.y * (1.0 - abs(2.0 * hsl.z - 1.0));
  return hsl.z + chroma * (pure - 0.5);
}
vec3 rgb2hsl(vec3 rgb) {
  float top = max(rgb.r, max(rgb.g, rgb.b));
  float low = min(rgb.r, min(rgb.g, rgb.b));
  float light = (top + low) * 0.5;
  float spread = top - low;
  if (spread <= 0.0) return vec3(0.0, 0.0, light);
  float sat = spread / (1.0 - abs(2.0 * light - 1.0));
  // One hue sector per primary: the top channel picks the sector
  vec3 sectors = vec3(0.0, 2.0, 4.0) + (rgb.gbr - rgb.brg) / spread;
  float hue = rgb.r == top ? sectors.r : rgb.g == top ? sectors.g : sectors.b;
  return vec3(fract(hue / 6.0), sat, light);
}

// ── SDF primitives ─────────────────────────────────────────────────────
float sdCircle(vec2 p, float r) { return length(p) - r; }
float sdBox(vec2 p, vec2 halfSize) {
  vec2 past = abs(p) - halfSize;           // how far past each pair of sides
  float inside = max(past.x, past.y);
  float outside = length(vec2(max(past.x, 0.0), max(past.y, 0.0)));
  return inside > 0.0 ? outside : inside;
}
float sdLine(vec2 p, vec2 a, vec2 b) {
  vec2 run = b - a;
  float along = clamp(dot(p - a, run) / dot(run, run), 0.0, 1.0);  // 0 at a, 1 at b
  return distance(p, mix(a, b, along));
}

// ── Blend modes ────────────────────────────────────────────────────────
vec3 blendScreen(vec3 base, vec3 top)     { return 1.0 - (1.0-base)*(1.0-top); }
vec3 blendOverlay(vec3 base, vec3 top) {
  return mix(2.0*base*top, 1.0-2.0*(1.0-base)*(1.0-top), step(0.5, base));
}
vec3 blendColorDodge(vec3 base, vec3 top) { return base / (1.0 - top + 0.001); }
vec3 blendMultiply(vec3 base, vec3 top)   { return base * top; }

// ── Easing functions ───────────────────────────────────────────────────
float easeOut(float t, float k) { return 1.0 - pow(1.0 - t, k); }
float easeIn(float t, float k)  { return pow(t, k); }
float easeInOut(float t, float k) {
  return t < 0.5 ? 0.5 * easeIn(2.0 * t, k) : 1.0 - 0.5 * easeIn(2.0 - 2.0 * t, k);
}
float elasticOut(float t) { return 1.0 - exp(-7.0 * t) * cos(14.0 * t); }  // a damped wobble

// ── Soft noise: slopes on two turned grids, about -1 to 1 ──────────────
// Each grid corner holds a random slope. One grid shows its axes in slow
// motion, so a second grid, turned about 38 degrees, hides them.
float cornerSlope(vec2 corner, vec2 toPoint) {
  float heading = 6.2832 * randomOf(corner);
  return dot(vec2(cos(heading), sin(heading)), toPoint);
}
float slopeGrid(vec2 p) {
  vec2 cell = floor(p), f = p - cell;
  vec2 blend = smoothstep(0.0, 1.0, f);
  float low  = mix(cornerSlope(cell, f),
                   cornerSlope(cell + vec2(1, 0), f - vec2(1, 0)), blend.x);
  float high = mix(cornerSlope(cell + vec2(0, 1), f - vec2(0, 1)),
                   cornerSlope(cell + vec2(1, 1), f - vec2(1, 1)), blend.x);
  return mix(low, high, blend.y);
}
float softNoise(vec2 p) {
  const mat2 TURN = mat2(0.79, 0.62, -0.62, 0.79);
  return slopeGrid(p) + slopeGrid(TURN * p + vec2(23.0, 11.0));
}

// ── Cellular noise: 0 on a cell's moving seed, 1 on the wall between cells
// Use for: tissue, scales, cracked earth, organic surfaces
float worley(vec2 p) {
  vec2 home = floor(p);
  float nearest = 9.0, second = 9.0;
  for (int row = -1; row <= 1; row++) {
    for (int column = -1; column <= 1; column++) {
      vec2 cell = home + vec2(float(column), float(row));
      vec2 luck = randomPairOf(cell);
      float angle = 6.2832 * luck.x + u_time * 0.4;
      vec2 seed = cell + 0.3 + 0.4 * luck + 0.15 * vec2(cos(angle), sin(angle));
      float away = distance(p, seed);
      second = min(second, max(nearest, away));
      nearest = min(nearest, away);
    }
  }
  return 2.0 * nearest / (nearest + second);  // the two distances match on a wall
}

// ── Domain warp: noise pushes the place noise is read from, twice over ─
// noisePair = two unrelated noise values at one point
// result.x  = warped noise value (use for color mapping)
// result.yz = the first push (use for secondary color mixing)
vec2 noisePair(vec2 p) { return vec2(fbm(p), fbm(p + vec2(31.7, 17.9))); }
vec3 domainWarp(vec2 uv, float t) {
  vec2 firstPush = noisePair(uv + t * vec2(0.09, -0.04));
  vec2 secondPush = noisePair(uv + 3.5 * firstPush + t * vec2(-0.13, 0.11));
  return vec3(fbm(uv + 3.5 * secondPush), firstPush);
}
```

## VFX shader recipes

VFX shader recipes are fragment shaders to drop into the boilerplate; each reads `u_time` and `u_resolution`.

### Plasma / Energy Field

```glsl
void main() {
  vec2 uv = v_uv * 2.0 - 1.0;
  uv.x *= u_resolution.x / u_resolution.y;

  float t = u_time * 0.6;

  // Three overlapping sine waves in different directions
  float v1 = sin(uv.x * 4.0 + t);
  float v2 = sin(uv.y * 3.0 - t * 0.7);
  float v3 = sin((uv.x + uv.y) * 3.5 + t * 0.5);
  float v4 = sin(length(uv) * 5.0 - t * 1.2);

  float v = (v1 + v2 + v3 + v4) * 0.25;

  // Map to color
  vec3 col = hsl2rgb(vec3(v * 0.5 + 0.5, 0.8, 0.55));

  // Vignette
  float vig = 1.0 - smoothstep(0.5, 1.4, length(uv));
  col *= vig;

  gl_FragColor = vec4(col, 1.0);
}
```

### Fluid / Liquid Warp

```glsl
void main() {
  vec2 uv = v_uv;
  float t = u_time * 0.35;

  // Noise bends the coordinates the next noise reads: this is the liquid feel
  vec2 bend = noisePair(uv + t * vec2(0.08, -0.05));
  vec2 swell = noisePair(uv + bend + t * vec2(-0.12, 0.10));
  float depth = fbm(uv + swell);

  // Pull accent colors from uniforms (pass as vec3 uniform)
  vec3 accent  = vec3(0.486, 0.227, 0.929);
  vec3 accent2 = vec3(0.024, 0.714, 0.831);
  vec3 ground  = vec3(0.035, 0.035, 0.055);

  vec3 col = mix(ground, accent, smoothstep(0.25, 0.65, depth));
  col = mix(col, accent2, 0.8 * smoothstep(0.42, 0.68, bend.x));
  col += accent * 0.35 * swell.y * swell.y;

  gl_FragColor = vec4(col, 1.0);
}
```

**Making it brand-aware:** Add `uniform vec3 u_accent; uniform vec3 u_accent2; uniform vec3 u_bg;` and set them from JS using the palette tokens.

### Chromatic Aberration on Texture

```glsl
uniform sampler2D u_texture;

void main() {
  vec2 uv = v_uv;
  float t = u_time;

  // Aberration strength — animate from 0 to max and back
  float strength = 0.012 * sin(t * 2.0) * 0.5 + 0.008;

  // Direction from center
  vec2 dir = uv - 0.5;

  // Sample R, G, B at offset UVs
  float r = texture2D(u_texture, uv + dir * strength * 1.0).r;
  float g = texture2D(u_texture, uv                       ).g;
  float b = texture2D(u_texture, uv - dir * strength * 0.8).b;

  gl_FragColor = vec4(r, g, b, 1.0);
}
```

### Volumetric Light Rays (God Rays)

```glsl
void main() {
  vec2 uv = v_uv;
  vec2 lightPos = vec2(0.5, 1.0); // light source at top-center: v_uv.y is 1 at the top
  float t = u_time;

  float dist = distance(uv, lightPos);

  // Walk from this pixel toward the light; the steps near the pixel count most
  float light = 0.0;
  for (int i = 1; i <= 64; i++) {
    float along = float(i) / 64.0;
    vec2 p = mix(uv, lightPos, along * 0.8);
    // Fine noise blocks parts of the light and cuts it into shafts
    float open = smoothstep(0.4, 0.7, 1.0 - noise(p * 14.0 + vec2(t * 0.1, 0.0)));
    light += open * exp(-2.6 * along);
  }
  light *= 0.072;

  // Combine with warm white light color
  vec3 rayColor = vec3(1.0, 0.92, 0.78) * light;

  // Vignette the whole thing
  float vign = 1.0 - smoothstep(0.5, 1.2, dist);
  gl_FragColor = vec4(rayColor * vign, light * 0.9);
}
```

**Use as:** Additive layer (`mix-blend-mode: screen`) over a dark composition background.

### Film Burn Transition (Outgoing)

```glsl
uniform float u_progress; // 0 → 1 during transition

void main() {
  vec2 uv = v_uv;

  // Burn wavefront — noise-driven edge
  float burnNoise = fbm(uv * 3.5 + u_time * 0.5);
  float burnEdge = u_progress * 1.4 - 0.2;
  float burn = smoothstep(burnEdge - 0.05, burnEdge + 0.05, uv.x + burnNoise * 0.3);

  // Ember color at the burn edge
  float ember = smoothstep(burnEdge - 0.12, burnEdge, uv.x + burnNoise * 0.3);
  vec3 fireCol = mix(vec3(1.0, 0.5, 0.0), vec3(1.0, 0.9, 0.0), ember);

  // The scorched area is near-black with texture
  vec3 scorch = vec3(0.04, 0.02, 0.01) * (0.5 + 0.5 * burnNoise);

  vec3 col = mix(fireCol, scorch, burn);
  float alpha = 1.0 - burn * 0.95;

  gl_FragColor = vec4(col, alpha);
}
```

### Aurora Borealis Background

```glsl
void main() {
  vec2 uv = v_uv;
  float t = u_time * 0.25;

  // Curtain shape — vertically banded
  float curtain = fbm(vec2(uv.x * 2.0 + t * 0.3, t * 0.1));

  // Vertical gradient — aurora lives in upper third
  float band = smoothstep(0.3, 0.7, uv.y) * smoothstep(1.0, 0.6, uv.y);

  // Color shifts across green → cyan → purple
  vec3 green  = vec3(0.0, 0.9, 0.4);
  vec3 cyan   = vec3(0.0, 0.8, 1.0);
  vec3 purple = vec3(0.5, 0.1, 0.9);

  float hShift = fbm(vec2(uv.x * 1.5, t * 0.2)) * 2.0;
  vec3 col = mix(mix(green, cyan, hShift), purple, hShift * 0.5);

  col *= curtain * band * 1.8;

  // Deep space background
  vec3 bg = vec3(0.02, 0.02, 0.06);
  col += bg;

  gl_FragColor = vec4(col, 1.0);
}
```

### Particle Nebula / Star Field

```glsl
void main() {
  vec2 uv = v_uv;
  float t = u_time;

  vec3 col = vec3(0.0);
  float aspect = u_resolution.x / u_resolution.y;

  // Layer 1: star field (tiny, many)
  for (int i = 0; i < 80; i++) {
    float id = float(i) * 4.0;
    vec2 starPos = vec2(randomOf(id), randomOf(id + 1.0));
    float size = 0.001 + randomOf(id + 2.0) * 0.002;
    float twinkle = 0.6 + 0.4 * sin(t * (2.0 + randomOf(id + 3.0)) + float(i));
    float star = size / (length((uv - starPos) * vec2(aspect, 1.0)) + 0.001);
    col += vec3(0.9, 0.95, 1.0) * star * twinkle * 0.4;
  }

  // Layer 2: nebula (large, fbm-based)
  vec2 p = uv * 2.0 - 1.0;
  float neb = fbm(p * 1.5 + vec2(t * 0.05, 0.0));
  neb = pow(max(neb - 0.4, 0.0), 1.5);
  col += vec3(0.3, 0.1, 0.6) * neb * 0.8;
  col += vec3(0.1, 0.3, 0.7) * fbm(p * 2.5 - vec2(0.0, t * 0.03)) * 0.4;

  // Deep space black base
  col = clamp(col, 0.0, 1.0);
  gl_FragColor = vec4(col, 1.0);
}
```

### Fire / Combustion

**Category:** Atmosphere · **Energy:** Very High · **Duration:** Loops  
Rising velocity field + fbm turbulence + Worley ember sparks. Requires `fbm` + `worley` from the library above.

```glsl
uniform vec3 u_fire_base; // brand accent or vec3(0.8,0.1,0.0) default
void main() {
  vec2 uv = v_uv;
  float t = u_time * 0.8;

  // Rising velocity — uv.y offset creates upward flow
  vec2 warpUV = uv;
  warpUV.y -= t * 0.28;
  warpUV.x += (fbm(warpUV * 2.0 + t * 0.3) - 0.5) * 0.3;

  // Core fire body — brighter at base
  float fire = fbm(warpUV * 3.5);
  fire *= 1.0 - uv.y * 1.25; // fade toward top
  fire = pow(max(fire, 0.0), 1.3);

  // Ember sparks via Worley cellular noise
  vec2 sparkUV = uv * 9.0; sparkUV.y -= t * 1.6;
  float sparks = smoothstep(0.6, 0.0, worley(sparkUV)) * (1.0 - uv.y);

  // Fire palette: void → red → orange → yellow → white-hot
  vec3 col = vec3(0.0);
  col = mix(col, u_fire_base,              smoothstep(0.0, 0.3, fire));
  col = mix(col, vec3(1.0, 0.4, 0.0),     smoothstep(0.2, 0.5, fire));
  col = mix(col, vec3(1.0, 0.8, 0.1),     smoothstep(0.4, 0.7, fire));
  col = mix(col, vec3(1.0, 0.98, 0.85),   smoothstep(0.65, 0.85, fire));
  col += vec3(1.0, 0.7, 0.2) * sparks * 1.5;

  gl_FragColor = vec4(col, fire + sparks * 0.5);
}
```
**Use as:** Additive layer (`mix-blend-mode: screen`) or full-canvas background. Pass `u_fire_base` from brand palette.

### Water Ripple (with Refraction)

**Category:** Atmosphere / Transition · **Energy:** Low–Medium  
Layered sine ripples + gradient-derived normal map for refraction. Use over video or image for an underwater lens effect.

```glsl
uniform sampler2D u_texture;
void main() {
  vec2 uv = v_uv;
  float t = u_time;

  // Concentric ripple layers from center
  float d = length(uv - 0.5) * 8.0;
  vec2 grad = vec2(
    cos(d - t * 4.0) * 0.012 + (fbm(uv * 5.0 + t * 0.2) - 0.5) * 0.006,
    sin(d * 1.3 - t * 3.2) * 0.010 + (fbm(uv * 5.0 + vec2(1.7,3.4) + t*0.2) - 0.5) * 0.006
  );

  // Refracted scene sample
  vec4 scene = texture2D(u_texture, clamp(uv + grad, 0.01, 0.99));

  // Surface shine at ripple peaks
  float ripple = sin(d - t * 4.0) * 0.5 + 0.5;
  float shine = pow(ripple, 6.0) * 0.35;
  vec3 col = mix(scene.rgb, vec3(0.3, 0.6, 0.9), 0.12) + shine;

  gl_FragColor = vec4(col, 1.0);
}
```
**Use as:** A lens over an image or a video. HyperFrames never fills `u_texture`, and `data-composition-src` only mounts a scene as DOM, so the shader sees no scene until your code uploads one with `texImage2D`.

Add this to the boilerplate after `gl.useProgram(prog)`:

```js
const tex = gl.createTexture();
gl.bindTexture(gl.TEXTURE_2D, tex);
gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); // v_uv starts at the bottom, image rows at the top
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
gl.uniform1i(gl.getUniformLocation(prog, 'u_texture'), 0);
const upload = (source) => gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);

// An image: upload once, and hold capture until it has decoded.
const still = new Image();
still.src = 'assets/scene.jpg';
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady['ripple-scene'] = still.decode().then(() => {
  upload(still);
  render(window.__hfThreeTime || 0);
});
```

**For a video:** skip the image block, put a timed `<video>` under the canvas, and call `upload(video)` as the first line of `render(t)`. During a render the runtime swaps the decoded frame in for that upload and fires `hf-seek` again once the frame is in place. In the preview the video seeks on its own, so also redraw when it catches up:

```js
for (const type of ['loadeddata', 'seeked']) {
  video.addEventListener(type, () => render(window.__hfThreeTime || 0));
}
```

**For a sub-composition:** `texImage2D` cannot read a mounted scene. Draw its DOM into a canvas with HTML in canvas and upload that canvas; see [runtime-effects.md](runtime-effects.md). `check` then reports the source under the shader as `text_occluded` and `canvas_covered`, so judge this one in the rendered file.

### Portal Warp

**Category:** Transition / Peak VFX · **Energy:** Very High  
Radial spiral UV distortion + event horizon glow ring. Brand-aware via `u_accent` uniform.

```glsl
uniform vec3 u_accent;
void main() {
  vec2 uv = v_uv * 2.0 - 1.0;
  float aspect = u_resolution.x / u_resolution.y;
  uv.x *= aspect;
  float dist = length(uv);
  float t = u_time;

  float angle = atan(uv.y, uv.x);
  float warpAngle = angle + t * 0.9 + 0.5 / (dist + 0.05);
  float rings = sin(dist * 14.0 - t * 3.5) * 0.5 + 0.5;
  rings *= sin(warpAngle * 5.0) * 0.5 + 0.5;

  // Radial fade — portal opens from center
  float radFade = 1.0 - smoothstep(0.0, 0.85, dist * aspect);

  // Event horizon ring at r ≈ 0.3
  float horizon = smoothstep(0.06, 0.0, abs(dist - 0.30));

  vec3 col = mix(vec3(0.0, 0.0, 0.04), u_accent, rings * radFade);
  col += u_accent * horizon * 4.0;   // bright horizon ring
  col += softNoise(uv * 3.0 + t * 0.5) * 0.08; // surface shimmer

  gl_FragColor = vec4(col, radFade + horizon * 0.5);
}
```
**Integration:** Use as a full-screen transition layer at energy peak. Animate `u_progress` (add as uniform) from 0→1 during scene change to expand the portal.

### Domain Warp Fluid Background

**Category:** Atmosphere · **Energy:** Medium  
Ultra-organic background using `domainWarp()`: the most visually complex pattern achievable without Three.js.

```glsl
uniform vec3 u_col1; // accent
uniform vec3 u_col2; // accent-2
uniform vec3 u_col3; // bg
void main() {
  vec2 uv = v_uv;
  float t = u_time * 0.18;
  vec3 warp = domainWarp(uv, t);

  vec3 col = mix(u_col3, u_col1, smoothstep(0.25, 0.65, warp.x));
  col = mix(col, u_col2, 0.8 * smoothstep(0.42, 0.68, warp.y));
  col += u_col1 * 0.3 * warp.z * warp.z;

  // Vignette
  vec2 vig = v_uv * 2.0 - 1.0;
  col *= 1.0 - dot(vig, vig) * 0.25;

  gl_FragColor = vec4(col, 1.0);
}
```
**Porting a warp shader:** map `iTime` → `u_time`, pass the palette in as uniforms, and check its licence first (see the port checklist).

### Cellular / Organic Tissue

**Category:** Atmosphere / Accent · **Energy:** Low–Medium  
Worley noise creates organic cell patterns, skin, scales, cracked earth, biological structures.

```glsl
uniform vec3 u_cell_col;  // cell interior color (brand-aware)
uniform vec3 u_edge_col;  // edge/vein color
void main() {
  vec2 uv = v_uv;
  float t = u_time * 0.2;

  // Multi-scale Worley — coarse cells + fine detail
  float w1 = worley(uv * 4.0 + t * 0.1);
  float w2 = worley(uv * 9.0 - t * 0.07) * 0.5;

  // Cell walls sit where w1 reaches 1, midway between two seeds
  float cell = w1 * 0.7 + w2 * 0.3;
  float edge = smoothstep(0.84, 0.98, w1);

  // Interior FBM variation — each cell has its own organic texture
  float interior = fbm(uv * 6.0 + t * 0.05) * (1.0 - edge);

  vec3 col = mix(u_cell_col * (0.7 + interior * 0.5), u_edge_col, edge);

  // Pulsing brightness across cells
  col *= 0.85 + 0.15 * sin(cell * 12.0 + t);

  gl_FragColor = vec4(col, 1.0);
}
```

## Passing palette colours as uniforms

Passing palette colours as uniforms makes shaders brand-aware: read the colour tokens and set them as uniforms:

```js
// Parse CSS variable to vec3 float for GLSL
function cssColorToVec3(hex) {
  const r = parseInt(hex.slice(1,3), 16) / 255;
  const g = parseInt(hex.slice(3,5), 16) / 255;
  const b = parseInt(hex.slice(5,7), 16) / 255;
  return [r, g, b];
}

const style = getComputedStyle(document.documentElement);
const accent = style.getPropertyValue('--accent').trim();

const uAccent = gl.getUniformLocation(prog, 'u_accent');
gl.uniform3fv(uAccent, new Float32Array(cssColorToVec3(accent)));
```

Add to the fragment shader: `uniform vec3 u_accent;`

## Multi-pass rendering

Multi-pass rendering serves effects that read from another render pass (blur, glow, bloom); each pass must be recomputed from the current time, never from the previous frame:

```js
// Create two framebuffers and ping-pong between them
const fbo = [createFBO(gl, W, H), createFBO(gl, W, H)];
let ping = 0;

function createFBO(gl, w, h) {
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); // WebGL 1 needs both for a 1920x1080 texture
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  const fb = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  return { tex, fb };
}

function render(t) {
  // Pass 1: render base effect to FBO
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo[ping].fb);
  // ... draw base effect ...

  // Pass 2: apply post-process (blur, glow) to screen
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.bindTexture(gl.TEXTURE_2D, fbo[ping].tex);
  // ... draw post-process pass ...

  ping = 1 - ping;
}
```

**Important for HyperFrames:** Multi-pass is fine since the capture engine calls render synchronously at each seek time. The framebuffer state is fully reconstructed each seek call.

## Shadertoy port checklist

A Shadertoy port checklist for any shader taken from Shadertoy or GLSL Sandbox (check the shader's licence first; many are CC BY-NC-SA):

```
[ ] iTime        → u_time       (add uniform float u_time)
[ ] iResolution  → u_resolution (add uniform vec2 u_resolution)
[ ] iChannel0    → u_texture    (add uniform sampler2D u_texture, if used)
[ ] iMouse       → remove       (no interactivity in video composition)
[ ] mainImage()  → void main()  (rename entry point)
[ ] fragCoord    → v_uv * u_resolution (or use v_uv directly)
[ ] Add hf-seek handler: window.addEventListener('hf-seek', e => { gl.uniform1f(uTime, e.detail.time); render(); })
[ ] Add initial render: render(window.__hfThreeTime || 0)
[ ] Replace any Math.random() with deterministic seed — shaders are fine (GPU runs stateless)
[ ] Add u_accent / u_bg uniforms and set from cssColorToVec3() for brand awareness
```
