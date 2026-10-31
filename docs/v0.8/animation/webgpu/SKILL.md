---
name: webgpu
description: Builds WebGPU layers for HyperFrames video with TypeGPU or raw WebGPU and WGSL - a device created once, a render function of time called from the hf-seek event, e.detail.waitUntil(device.queue.onSubmittedWorkDone()) so capture waits for the GPU, full-screen fragment shaders, alpha modes for overlays, and fallbacks when WebGPU is missing. Use when a video needs GPU shaders, liquid glass, particle compute or WGSL effects, or when a WebGPU canvas captures stale or blank frames.
metadata:
  tags:
  - webgpu
  - typegpu
  - wgsl
  - shaders
  - gpu
  - hyperframes
---

# WebGPU and TypeGPU for video

WebGPU is the browser's modern GPU API; TypeGPU is a TypeScript toolkit over it that writes shaders and buffers with
types. HyperFrames supports both through an adapter that publishes the frame time (`window.__hfTypegpuTime`) and fires
the same `hf-seek` event as Three.js. Checked against typegpu 0.12.9 (MIT).

## When to use this skill

Use this skill for GPU effects the DOM cannot draw: WGSL fragment shaders, liquid glass over footage, compute-driven
particles, fluid backgrounds. Prefer WebGL (`threejs`, `vfx`) when the render machine may lack WebGPU.

## Step 0: read the toolkit and the GPU on the render machine

```bash
grep -rhoE 'typegpu@[0-9.]+' --include='*.html' . | sort -u    # a CDN pin
npm ls typegpu --depth=0 2>/dev/null                           # a bundled project
npx hyperframes doctor --json | jq .ok                         # the render machine is ready
npx hyperframes render --quality draft --browser-gpu -o /tmp/gpu.mp4   # a real adapter, or the visible error
```

TypeGPU is pre-1.0, so read the docs for the exact version the project pins.

## The seek contract for GPU layers

The seek contract for GPU layers has four rules.

1. Initialise the device asynchronously once; register GSAP timelines synchronously before any `await`, or at the end
   of the callback that builds them.
2. Render from the event's time: a function `render(t)` with no state carried between frames.
3. In the `hf-seek` listener, call `render(e.detail.time)` and then, synchronously,
   `e.detail.waitUntil(device.queue.onSubmittedWorkDone())` so capture waits for the GPU.
4. Check for WebGPU and fail visibly: the adapter does not check for you.

## Full-screen shader pattern

The full-screen shader pattern draws one triangle that covers the canvas and computes colour per pixel from a time
uniform.

```html
<canvas id="gpu" width="1920" height="1080" style="position:absolute;inset:0;width:100%;height:100%"></canvas>
<script type="module">
  const canvas = document.getElementById("gpu");
  if (!navigator.gpu) throw new Error("WebGPU unavailable in this browser");
  const adapter = await navigator.gpu.requestAdapter();
  if (!adapter) throw new Error("No GPU adapter");
  const device = await adapter.requestDevice();
  const ctx = canvas.getContext("webgpu");
  const format = navigator.gpu.getPreferredCanvasFormat();
  ctx.configure({ device, format, alphaMode: "premultiplied" });

  const code = /* wgsl */ `
    struct Vo { @builtin(position) pos: vec4f, @location(0) uv: vec2f };
    @group(0) @binding(0) var<uniform> time: f32;
    @vertex fn vs(@builtin(vertex_index) i: u32) -> Vo {
      let p = array<vec2f, 3>(vec2f(-1., -1.), vec2f(3., -1.), vec2f(-1., 3.));
      let uv = array<vec2f, 3>(vec2f(0., 1.), vec2f(2., 1.), vec2f(0., -1.));
      return Vo(vec4f(p[i], 0., 1.), uv[i]);
    }
    @fragment fn fs(v: Vo) -> @location(0) vec4f {
      let w = 0.5 + 0.5 * sin(v.uv.x * 6.0 + time * 1.2) * cos(v.uv.y * 4.0 - time * 0.8);
      return vec4f(mix(vec3f(0.04, 0.05, 0.08), vec3f(1.0, 0.35, 0.21), w * 0.6), 1.0);
    }`;
  const module = device.createShaderModule({ code });
  const pipeline = device.createRenderPipeline({ layout: "auto",
    vertex: { module, entryPoint: "vs" }, fragment: { module, entryPoint: "fs", targets: [{ format }] } });
  const ubo = device.createBuffer({ size: 16, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  const bind = device.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: ubo } }] });

  function render(t) {
    device.queue.writeBuffer(ubo, 0, new Float32Array([t]));
    const enc = device.createCommandEncoder();
    const pass = enc.beginRenderPass({ colorAttachments: [{ view: ctx.getCurrentTexture().createView(),
      loadOp: "clear", clearValue: { r: 0, g: 0, b: 0, a: 0 }, storeOp: "store" }] });
    pass.setPipeline(pipeline); pass.setBindGroup(0, bind); pass.draw(3); pass.end();
    device.queue.submit([enc.finish()]);
  }
  window.addEventListener("hf-seek", (e) => {
    render(e.detail.time);
    e.detail.waitUntil(device.queue.onSubmittedWorkDone());
  });
  render(window.__hfTypegpuTime ?? 0);
</script>
```

## TypeGPU in brief

TypeGPU in brief: `tgpu.init()` returns a root that wraps the device; buffers are declared with typed schemas
(`d.f32`, `d.vec2f`, structs), and shaders can be written in WGSL strings or as TypeScript functions TypeGPU compiles.
The seek rules are identical: a `render(t)` that writes the time into a uniform, submits, and hands
`onSubmittedWorkDone()` to `waitUntil`. Load it as an ES module (`https://cdn.jsdelivr.net/npm/typegpu@0.12.9/+esm`)
or bundle it; check the current API in the TypeGPU docs, as it is pre-1.0 and changes between minor versions.

## Alpha modes and compositing

Alpha modes and compositing decide whether HTML shows through the GPU canvas.

| `alphaMode` | Use |
|---|---|
| `"opaque"` | the GPU canvas draws the whole frame (background shader, footage plus effect) |
| `"premultiplied"` | an overlay: transparent where alpha is 0, so layers below show through |

With premultiplied alpha, output colours already multiplied by alpha (`vec4f(rgb * a, a)`).

## Footage as a GPU texture

Footage as a GPU texture copies the current video frame each render with `copyExternalImageToTexture` or imports it
with `importExternalTexture`. Headless capture can fail to provide decoded video frames to the GPU; for production
renders, extract the frames you need with FFmpeg and load them as image textures, or use a transparent overlay above a
normal `<video>` clip instead.

## Frosted glass with a downsample pass

Frosted glass with a downsample pass blurs cheaply: render the background into a texture at about one sixth of the
resolution (bilinear filtering averages pixels), then sample the small texture for the frosted interior and the full
texture for sharp edges and refraction. One Gaussian pass at full size is too weak and too slow for heavy frost.

## Verify the GPU layer

```bash
npx hyperframes snapshot --at 0.5,2,4 -o /tmp/gpu-a
npx hyperframes snapshot --at 0.5,2,4 -o /tmp/gpu-b
for f in /tmp/gpu-a/*.png; do cmp "$f" "/tmp/gpu-b/$(basename "$f")"; done   # silent means the same pixels
grep -rn 'onSubmittedWorkDone' compositions index.html                           # present in the listener
```

Seek backwards in Studio: a frame that shows the previous time means `waitUntil` is missing.

## Checklist

- [ ] Device created once; GSAP timelines registered synchronously.
- [ ] `render(t)` depends on `t` only; randomness seeded or hashed from coordinates.
- [ ] `waitUntil(device.queue.onSubmittedWorkDone())` called synchronously in the `hf-seek` listener.
- [ ] WebGPU availability checked, with a visible error; render machine confirmed to support it.
- [ ] Alpha mode matches the layer's role.

## Gotchas

- **Symptom:** The captured frame is one behind: the canvas shows the previous frame. **Cause:** The GPU work was not
  registered with `waitUntil`. **Fix:** call `e.detail.waitUntil(device.queue.onSubmittedWorkDone())` synchronously in
  the `hf-seek` listener.
- **Symptom:** Black instead of transparent. **Cause:** `alphaMode: "opaque"` on an overlay, or colours not
  premultiplied. **Fix:** use `"premultiplied"` and output `vec4f(rgb * a, a)`.
- **Symptom:** It works in preview and is blank in the render. **Cause:** The render machine's headless Chrome has no
  WebGPU adapter. **Fix:** run with `--browser-gpu`, render in an environment with a GPU, or fall back to WebGL.
- **Symptom:** The timeline is missing. **Cause:** GSAP tweens were created after an `await` and registered too late.
  **Fix:** register synchronously, or at the end of the callback that builds them.

## Anti-patterns

| Do not | Do instead |
|---|---|
| state carried between frames | a `render(t)` that depends on `t` alone |
| decoded video frames as textures in production renders | frames extracted with FFmpeg, or an overlay above a normal `<video>` clip |
| one full-size Gaussian pass for heavy frost | a downsampled texture at about one sixth of the resolution |
| assuming WebGPU exists | check, and fail with a visible error |

## See also

`threejs`, `vfx`, `render-performance`.
