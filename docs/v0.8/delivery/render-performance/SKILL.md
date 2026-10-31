---
name: render-performance
description: Makes HyperFrames renders and previews fast and stable - workers and memory, GPU encode and browser GPU flags, the BeginFrame and screenshot capture paths, reading the render summary timings, benchmark presets, heavy compositions (big images, many videos, blur and SVG filters, WebGL), buildReady promises, timeouts, Docker shared memory, iterating with draft renders, single-scene renders and snapshots, and cloud renders for long videos. Use when a render is slow, runs out of memory, times out, or stalls, or when planning renders for long or many videos.
metadata:
  tags:
  - performance
  - render
  - workers
  - gpu
  - memory
  - benchmark
  - hyperframes
  - optimisation
---

# Render performance

Render performance is how long a render takes and whether it finishes. HyperFrames renders by running Chrome workers
that seek and capture frames in parallel while FFmpeg encodes. Time goes into four stages the render summary reports:
compile, setup, capture and encode. A 30 s 1080p film usually renders in a minute or two on a laptop. Checked against
CLI 0.8.223.

## When to use this skill

Use this skill when a render or preview is slow, crashes, runs out of memory or times out, and when planning renders
for long videos, 4K, 60 fps or large batches.

## Step 0: read the machine before tuning it

```bash
npx hyperframes --version
npx hyperframes doctor --json | jq .ok     # also reports /dev/shm in Docker
npx hyperframes render --quality draft -o /tmp/probe.mp4   # the summary line names capture path, GPU and stage times
```

Tune against that summary line, never against a guess.

## Read the summary line first

Read the summary line first: after a render, the second line names the capture path, GPU mode and stage times, for
example `beginframe capture · software gpu · compile 0.7s · setup 1.1s · capture 8.1s · encode 5.8s`.

| What it says | Meaning | Action |
|---|---|---|
| `capture` dominates | the frame loop is the cost | simplify heavy layers, add workers, use GPU |
| `encode` dominates | the encoder is the cost | `--gpu` hardware encode, or a lighter preset while iterating |
| `encode (during capture)` | encoding overlapped capture | do not add it to wall time |
| `screenshot capture` and `software gpu` on Linux | BeginFrame did not run: the slow path | use chrome-headless-shell, drop `--resolution` upscale, or render with GPU |
| two capture paths joined by a bar | workers took different paths | heavy content behaves differently per worker; check with one worker |

## Workers and memory

Workers and memory trade speed for RAM: each worker is a Chrome of about 256 MB, more for heavy pages.

```bash
npx hyperframes render --workers auto -o out.mp4      # default
npx hyperframes render --workers 2 -o out.mp4         # low memory, or many big videos
npx hyperframes benchmark --runs 3 --json             # 5 presets: fps, quality and worker counts compared
```

`benchmark` renders the project with preset matrices (`30fps draft 2w`, `30fps standard 2w`, `30fps high 2w`,
`30fps standard 4w`, `60fps standard 4w`) and reports speed and file size, to find the fastest acceptable setting for a
machine. In Docker, give the container enough shared memory (`--shm-size=2g`); `doctor` reports `/dev/shm`.

## GPU flags

GPU flags speed up the two GPU-able stages.

- `--gpu`: hardware FFmpeg encoding (NVENC, VideoToolbox, VAAPI, QSV). Large win on long or 4K renders.
- `--browser-gpu` / `--no-browser-gpu`: host GPU for Chrome and WebGL capture; auto locally, off in Docker. WebGL and
  WebGPU scenes on software GL can stall.
- HLS output rejects `--gpu`.

## Iterate cheaply

Iterate cheaply by not rendering whole films while editing.

| Need | Cheapest tool |
|---|---|
| See a frame | `npx hyperframes snapshot --at 4.2` |
| See one stretch of motion | `snapshot --range 3,5 --frames 8` or `keyframes --shot` |
| See one scene moving | `render -c compositions/intro.html --quality draft -o intro.mp4` |
| Watch the whole thing | Studio preview (`preview`), no encode |
| A real encode to share | `render --quality draft`, then `looks` |

Render at 30 fps while iterating even when the final is 60.

## Heavy compositions

Heavy compositions slow every frame. The usual causes and fixes:

| Cause | Fix |
|---|---|
| Images far larger than shown | resize to about display size (2x for zoom-ins), use WebP or JPEG |
| Many simultaneous videos | fewer concurrent clips, pre-render composites to one file, H.264 sources at display size |
| Unusual codecs (ProRes, HEVC 10-bit) as sources | transcode sources to H.264; `render` has no `--proxy` flag and decodes the original |
| Large blur filters, backdrop blur on full frame | smaller blur areas, blur a downscaled copy, bake static blurs to images |
| SVG filters on big regions | shrink the filter region, bake to video if static |
| Layout measured in `onUpdate` | measure once before building tweens |
| WebGL compile at first seek | compile at init and register a `window.__hf.buildReady["key"]` promise |
| Huge DOM (thousands of nodes) | canvas for particles; fewer split characters |

## Timeouts

Timeouts fire when a page is not ready in time. `render --browser-timeout 120` raises the navigation timeout (default
60 s) for pages with many videos, fonts or assets; `check --timeout 30000` and `snapshot --timeout` raise the
render-ready wait. A scene that always times out at 45 s usually has a host id that differs from its timeline key, or
a still composition without `data-no-timeline`: fix the cause rather than raising timeouts.

## Long videos and many videos

Long videos and many videos move off the laptop.

- Hosted rendering: `npx hyperframes cloud render` (no local Chrome or FFmpeg).
- Your own cloud: `lambda render` on AWS or `cloudrun render` on GCP split a render across many machines; accepted
  frame rates are 24, 25, 30 and 60.
- Batches: `render --batch rows.json --batch-concurrency 1`; raise concurrency carefully, as each render already uses
  several workers.
- Long-running local renders beyond a tool's timeout: run detached with `HYPERFRAMES_RENDER_DETACHED=1`, log to a file,
  and wait for `Render (complete|failed)` in the log.

## Disk and caches

Disk and caches fill up with renders and snapshots. `npx hyperframes clean --dry-run` lists what can go, `clean`
removes leftovers of dead renders and caches that rebuild; it never deletes outputs, sources or history. Never delete
`.hyperframes` by hand.

## Verify a speed-up

```bash
time npx hyperframes render --quality draft -o /tmp/before.mp4   # before the change
time npx hyperframes render --quality draft -o /tmp/after.mp4    # after it: same flags, same machine
npx hyperframes benchmark --runs 3 --json                        # the settings compared side by side
```

A change counts only when the same stage in the summary line went down and the frames still look the same.

## Checklist

- [ ] The summary line read; the slowest stage identified.
- [ ] Workers and memory fit the machine; `benchmark` run once per machine for long projects.
- [ ] GPU encode and browser GPU used where available.
- [ ] Iteration done with snapshots, single-scene and draft renders.
- [ ] Heavy assets resized and transcoded; blur and filter areas small.
- [ ] Long or many renders moved to cloud, Lambda or Cloud Run.

## Gotchas

- **Symptom:** Out of memory with many workers. **Cause:** Each Chrome needs its own memory. **Fix:** lower
  `--workers`.
- **Symptom:** Linux renders ten times slower than the laptop. **Cause:** The screenshot path with software GL.
  **Fix:** see the summary hint: use chrome-headless-shell, drop the `--resolution` upscale, or render with a GPU.
- **Symptom:** Timeouts after adding a scene. **Cause:** A host id mismatch makes each scene wait 45 s. **Fix:** match
  host id, scene id and timeline key.
- **Symptom:** 4K takes four times as long. **Cause:** It has four times the pixels. **Fix:** supersample only the
  final render.

## Anti-patterns

| Do not | Do instead |
|---|---|
| raising timeouts for a 45 s stall | fix the host id or add `data-no-timeline` |
| rendering whole films while editing | snapshots, single-scene and draft renders |
| many renders in parallel on one machine | `--batch-concurrency 1`, or move to the cloud |
| deleting `.hyperframes` by hand | `clean --dry-run`, then `clean` |

## See also

`hyperframes-cli`, `hyperframes-automation`, `render-and-export`, `render-testing`, `vfx`.
