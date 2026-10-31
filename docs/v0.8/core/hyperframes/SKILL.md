---
name: hyperframes
description: Writes and edits HyperFrames compositions, the HTML files that HyperFrames renders to MP4 by seeking a paused timeline frame by frame. Covers the render contract, clip timing attributes, scene sub-compositions, variables, media elements, fonts and determinism. Use when making, editing, animating or fixing any HTML-based video, title card, overlay, explainer, promo or social clip with HyperFrames.
metadata:
  tags:
  - hyperframes
  - video
  - html
  - composition
  - gsap
  - timeline
  - render
---

# HyperFrames compositions

HyperFrames makes video out of an HTML page. Headless Chrome loads the page, the renderer moves one paused timeline
to the time of each frame, screenshots it, and FFmpeg encodes the screenshots. Since each frame depends on its time
and nothing else, rendering a project twice gives the same file. This skill is the set of rules a composition has to
obey; the command loop is in `hyperframes-cli` and motion craft in `motion-design`.

Checked against the `hyperframes` CLI 0.8.223 and GSAP 3.15.0. The CLI needs Node.js 22 or later and FFmpeg.

## Step 0: confirm the toolchain

```bash
npx hyperframes --version     # 0.8.223 when this skill was checked
node --version                # v22 or later
ffmpeg -version | head -1
```

## Which skill handles the request

| The request | Skill |
|---|---|
| A new video, title card, lower third, explainer, promo or vertical clip; timing, layout, copy, colour or motion edits; a render that is blank, frozen, flickering or unlike the preview | this one |
| A deck presented live, with slides and speaker notes | `hyperframes-slideshow` |
| A Remotion project to port | `remotion-to-hyperframes` |
| Commands, flags, render options | `hyperframes-cli` |

## How a frame gets rendered

The renderer seeks; it never plays. Frame `n` at `fps` frames per second is the timeline set to `n / fps` seconds,
given time to settle, then captured. Between two captures nothing moves by itself. Anything that runs on the wall
clock, on `requestAnimationFrame`, on timers or on the network therefore shows a wrong state, or a different state
in each render.

| Works with seeking | Breaks seeking |
|---|---|
| a paused GSAP timeline that the runtime moves | `tl.play()`, `video.play()`, `audio.pause()` |
| CSS `@keyframes`, WAAPI, Lottie and anime.js through their adapters | `setTimeout`, `setInterval` or `requestAnimationFrame` used as a clock |
| a seeded PRNG | `Math.random()` with no seed, `Date.now()`, `performance.now()` |
| files kept in the project's `assets/` | loading data or media over the network while rendering |
| a repeat count worked out from the duration | `repeat: -1`, `iterations: Infinity` |

## Project layout

`npx hyperframes init <dir>` creates a project: a root composition plus one file per scene.

```
my-video/
├── index.html           root composition: variables, one host per scene, the audio
├── compositions/        one scene per file, each wrapped in <template>
│   └── intro.html
├── assets/              media, fonts (assets/fonts/), transcripts
├── hyperframes.json     registry and install paths
└── .hyperframes/        history, snapshots, caches: never delete it
```

Unless the request says otherwise, a new video is 1920×1080 and runs at 30 fps. Write asset paths as `assets/...` with no leading slash,
including inside scene files.

## The composition contract, rule by rule

The renderer relies on these rules. `npx hyperframes check --json` flags most breaches and prints a `Fix:` line for
each.

| Area | Rule |
|---|---|
| Timed elements | each one carries `class="clip"`, `data-start` and `data-duration` (seconds) and is visible over `[start, start + duration)`; a state reached exactly at the end is never drawn, so finish it one frame earlier |
| Film length | the root's `data-duration`; anything later is cut off, and a film that ends early freezes on its last frame |
| Timelines | each composition makes one paused timeline and, after adding its tweens, registers it as `window.__timelines["<data-composition-id>"] = tl` |
| Determinism | no `Date.now()`, no unseeded `Math.random()`, no fetches, timers or `repeat: -1` |
| Clip visibility | the runtime shows and hides clips, so `display`, `visibility` and `autoAlpha` are never tweened on a `.clip`; animate a child instead |
| Transforms | an element that GSAP transforms gets no CSS `transform`; put the start state in a `fromTo`, and move with transforms rather than `left`, `top`, `width` or `height` |
| Media playback | no `play()`, `pause()` or `currentTime` on media; a `<video>` is `muted` unless it has `data-has-audio="true"`; music and voice are their own `<audio>` elements |
| Audio mix | an `<audio>` without an `id` is dropped from the mix; media never carries `crossorigin` |
| Fonts | only the bundled families work by name; others need `@font-face` pointing into `assets/fonts/` |
| Paint order | CSS `z-index`; `data-track-index` is only a Studio lane |
| Scene files | styles, markup and scripts all sit inside `<template>`; the scene's root is styled as `#root` |
| Layout opt-outs | deliberate overflow or overlap is marked `data-layout-allow-overflow` or `data-layout-allow-overlap` |

## Clip timing attributes

These `data-*` attributes put an element on the timeline:

| Attribute | Meaning |
|---|---|
| `data-start` | start in seconds, relative to the file that declares it; `"intro + 0.5"` means half a second after clip `intro` ends |
| `data-duration` | length in seconds; media without it runs for its full length, an `<img>` without it for 3 s |
| `data-track-index` | the Studio lane; clips sharing a lane must not overlap |
| `data-media-start` | how far into the source media to begin, in seconds |
| `data-playback-rate` | a constant speed from 0.1 to 10 |
| `data-volume`, `data-fade-in`, `data-fade-out` | gain (1 is 0 dB, up to 3.98 for +12 dB) and fades at the edges |
| `data-has-audio="true"` | a `<video>` plays its own sound |
| `data-composition-id`, `data-composition-src` | a composition's id; the scene file a host loads |
| `data-width`, `data-height` | a composition's canvas size |
| `data-variable-values` | variable values for one scene host, as a JSON object |
| `data-hidden` | hidden in preview and render, and easy to undo |
| `data-no-timeline` | on the root of a still composition: there is no timeline to wait for |

A relative start with a mistake in it (an unknown id, missing spaces, a loop between clips) quietly becomes 0, so
take a snapshot of anything placed that way. Every attribute and its edge cases:
[references/composition-format.md](references/composition-format.md).

## Root composition example

`index.html` is an ordinary HTML document. Its top-level `div` holds the film's id, size and length, and it mounts a
host for each scene:

```html
<!doctype html>
<html data-composition-variables='[{"id":"headline","type":"string","label":"Headline","default":"Ship faster"}]'>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-width="1920" data-height="1080"
         data-start="0" data-duration="10">
      <div id="intro" data-composition-src="compositions/intro.html" data-composition-id="intro"
           data-track-kind="graphics" data-track-index="1" data-start="0" data-duration="3.5"
           data-width="1920" data-height="1080"></div>
      <div id="demo" data-composition-src="compositions/demo.html" data-composition-id="demo"
           data-track-kind="graphics" data-track-index="1" data-start="3.5" data-duration="6.5"
           data-width="1920" data-height="1080"></div>
      <audio id="bed" class="clip" src="assets/bed.mp3" data-start="0" data-duration="10"
             data-track-index="5" data-volume="0.55" data-fade-in="0.4" data-fade-out="1.5"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
```

## Scene sub-composition example

A scene lives in `compositions/` and keeps all of its content inside `<template>`; anything outside the template is
thrown away.

```html
<template>
  <style>
    #root { position: absolute; inset: 0; background: #0b0d12; }
    #intro-title { font: 800 120px/1 "Inter", sans-serif; color: #f4f1ea; }
  </style>
  <div id="root" data-composition-id="intro" data-width="1920" data-height="1080">
    <div class="scene-content">
      <h1 id="intro-title" class="clip" data-start="0.3" data-duration="3.2" data-var-text="headline">Ship faster</h1>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#intro-title",
      { opacity: 0, filter: "blur(8px)" },
      { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 0.3);
    window.__timelines["intro"] = tl;
  </script>
</template>
```

### Scene wiring: one id, three places

The host's id, the `data-composition-id` on the scene root and the key under `window.__timelines` must be the same
string. When they differ, the scene stays static and each render then waits 45 s per scene before giving up.

### Use `fromTo`, not `from`, inside a scene

A host seeks its scene afresh every time the scene comes on screen. A `from` tween stores its starting values only
once, at load, so later seeks start from the wrong place; `fromTo` states both ends and survives any seek.

### Other scene rules

- Do not `add()` a scene's timeline into the root's. The runtime already drives each scene, and nesting makes it
  seek twice.
- Ids must be unique on the assembled page; prefix them with the scene name (`#intro-title`).
- On a `.clip` element, never tween `visibility`, `display` or `autoAlpha`: the runtime owns those, and lint stops
  the render with `gsap_animates_clip_element`. Opacity, filters and transforms on a clip pass that rule. Timed
  media is different: to zoom or move a `<video>`, animate a wrapper.

## Layout before animation

Build the hero frame of each scene first, the moment when everything is visible, as plain HTML and CSS, and add the
motion afterwards. Laying elements out at their animated starting positions hides collisions until the render.

1. Give the scene a content container that fills it: `width: 100%; height: 100%; padding: Npx; display: flex;
   flex-direction: column; gap: Npx; box-sizing: border-box`. Reserve `position: absolute` for decoration.
2. Snapshot the hero moment (`npx hyperframes snapshot --at <t>`) and fix overlap and overflow.
3. Write entrances as `fromTo` tweens that finish at the CSS position, and exits that begin from it.

Let `max-width` wrap text; use `<br>` only in display titles where each word is deliberately its own line. Safe
areas and the layout opt-outs: [references/layout-and-safe-areas.md](references/layout-and-safe-areas.md).

## Variables for parametrized videos

One composition can render many versions (a headline, a price, a theme) with no HTML edits. Declare the variables on
`<html data-composition-variables='[...]'>`, bind them through `data-var-text`, `data-var-src` or `var(--id)`, and
override them when rendering with `npx hyperframes render --variables '{"headline":"Q4"}'`, or for one scene host
with `data-variable-values`. Types, batch renders and rules: [references/variables.md](references/variables.md).

## Video and audio elements

Media elements are timed like other clips, but the runtime controls their playback. Footage without sound is
`<video class="clip" muted playsinline>`; footage that keeps its sound is
`<video class="clip" playsinline data-has-audio="true">`. Music and narration each get an
`<audio class="clip" id="...">`. To zoom, crop or move footage, animate a wrapping `div` and leave the timed
`<video>` alone. More, including linked clips: [references/media-elements.md](references/media-elements.md).

## Frame sources for code that draws from time

Some scene code already has a "draw the frame at time t" function: a canvas renderer, a p5 sketch, a WebGL loop
rewritten that way. Register it with the runtime as a frame source rather than driving it from a dummy GSAP
timeline. Register before the runtime finishes starting, on the timed host, and put `data-no-timeline` on that host
(and on a root that has no timeline); without it lint reports `missing_timeline_registry` and each render stalls for
45 s.

```js
const unregister = window.__hyperframes.registerFrameSource({
  element: document.getElementById("sketch"),        // host with data-start, data-duration, data-no-timeline
  ready: loadTextures(),                              // capture waits for this promise
  render: (t, signal) => drawSketch(t),               // t: source time in seconds; may return a promise
  dispose: () => releaseSketch(),
});
```

Given the same `t`, `render` must produce the same pixels, whatever order frames arrive in and however often.
Moving, trimming or re-timing the host in an editor needs no code change. Scenes that overlap each need a source of
their own.

## Fonts in compositions

Eighteen families ship with HyperFrames and resolve by name: Archivo Black, EB Garamond, IBM Plex Mono, Inter,
JetBrains Mono, Lato, League Gothic, Montserrat, Noto Sans JP, Nunito, Open Sans, Oswald, Outfit, Playfair Display,
Poppins, Roboto, Source Code Pro, Space Mono. Every other family needs an `@font-face` rule pointing at a file in
`assets/fonts/`; without one, lint fails with `font_family_without_font_face`. Loading, subsetting and licences are
in `video-fonts`.

## The work loop

From first draft to the approved render, the commands run in this order:

```bash
npx hyperframes init my-video --non-interactive   # new project (1920x1080, 30 fps)
npx hyperframes lint                              # after the first pass and after structural changes
npx hyperframes check --json                      # the gate: lint, runtime, layout, motion, contrast
npx hyperframes snapshot --at 1,4,8               # capture frames, then look at the PNGs
npx hyperframes preview --background              # Studio; share http://localhost:<port>/#project/<name>
npx hyperframes render --quality looks --output out.mp4   # once the person approves the preview
```

Render once the person has approved the preview, asked for the file, or asked not to be stopped. Clean checks on
their own do not justify a render.

## Editing an existing project

Read the project before changing it:

- `npx hyperframes timeline --json` lists every clip with `absStart`, `absEnd`, `file` and `src`; read it rather
  than opening each file.
- Take colours, fonts and eases from the source files exactly; never retype hex values from memory.
- Change only what was asked, and leave the timing of other clips as it is.
- Studio rewrites the GSAP script in the file when the person edits motion there, so the file may have changed since
  your last turn.

## Verify a composition

```bash
npx hyperframes check --json              # no errors; weigh every warning
npx hyperframes snapshot --at 0,2,5,9.9   # frame 0 has content; each scene shows; the last frame is right
npx hyperframes timeline --json           # clip starts and ends match the plan
```

Look at a snapshot at each scene's midpoint and at every cut before handing over.

## Gotchas

- **Symptom:** a scene renders blank and every render waits 45 s per scene. **Cause:** the host id, the scene root's
  `data-composition-id` and the timeline key differ. **Fix:** use one string in all three places.
- **Symptom:** a scene is blank or frozen although the ids match. **Cause:** the timeline was registered before an
  async build finished, or `visibility` was tweened on a `.clip`. **Fix:** register after the build; animate a child.
- **Symptom:** the wrong state flashes as a scene starts. **Cause:** a `from` tween drew its start state at load.
  **Fix:** `fromTo`, or `immediateRender: false` on a `from` whose clip starts after 0.
- **Symptom:** the whole film is blank. **Cause:** `<template>` around `index.html`, which only scene files use
  (`standalone_composition_wrapped_in_template`). **Fix:** remove it from the root.
- **Symptom:** the root's background colour vanishes. **Cause:** with shader transitions or HDR media the root's
  fill is dropped. **Fix:** paint a full-bleed child with `position: absolute; inset: 0`.
- **Symptom:** a transform on a `<span>` has no effect. **Cause:** inline elements ignore transforms. **Fix:**
  `display: inline-block`.
- **Symptom:** stutter that differs between renders. **Cause:** layout measured inside `onUpdate`, or two timelines
  on one property. **Fix:** measure once at build time; give each property one owner.

## Anti-patterns

| Do not | Do instead |
|---|---|
| a `<template>` around `index.html` | `<template>` in scene files only |
| `add()` a scene's timeline into the root's | let the runtime drive each scene |
| hex values retyped from memory | copy colours, fonts and eases from the source files |
| rendering because the checks are green | render after the person approves the preview or asks for the file |
| laying out at the animated start positions | build the hero frame first, then write the entrances |

## Checklist

- [ ] Every timed element has `class="clip"`, `data-start` and `data-duration`.
- [ ] The root's `data-duration` reaches the end of the last clip.
- [ ] Each composition registers one paused timeline under its own `data-composition-id`, after its tweens.
- [ ] Host id, scene `data-composition-id` and timeline key are identical for every scene.
- [ ] Scenes use `fromTo`; no CSS `transform` on elements GSAP transforms.
- [ ] No unseeded randomness, clocks, timers, network or infinite repeats.
- [ ] Video is `muted` or has `data-has-audio="true"`; every `<audio>` has an `id`; no `crossorigin`.
- [ ] Fonts outside the bundled set have `@font-face` into `assets/fonts/`.
- [ ] `npx hyperframes check --json` has no errors and every warning was weighed.
- [ ] Snapshots read at each scene's midpoint and at every cut.

## References

- [references/composition-format.md](references/composition-format.md): every attribute, timing edge cases, linked clips.
- [references/variables.md](references/variables.md): declaring, binding and overriding variables; batch renders.
- [references/media-elements.md](references/media-elements.md): video, audio, images, trims, speed, linked clips.
- [references/layout-and-safe-areas.md](references/layout-and-safe-areas.md): safe areas, density, layout opt-outs.
- [references/lint-rules.md](references/lint-rules.md): the lint errors met first and how to fix them.
- [references/scene-patterns.md](references/scene-patterns.md): title cards, picture-in-picture, slide sequences, lower thirds.

## See also

`hyperframes-cli`, `motion-design`, `gsap`, `hyperframes-transitions`, `hyperframes-captions`, `render-and-export`.
