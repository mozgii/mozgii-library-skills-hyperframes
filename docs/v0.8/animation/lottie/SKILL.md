---
name: lottie
description: Places Lottie and dotLottie animations (After Effects exports, icons, characters, logo reveals) in HyperFrames so they seek frame-accurately - lottie-web loadAnimation and @lottiefiles/dotlottie-web players with autoplay false, instances pushed to window.__hfLottie, local assets, renderer choice, colour theming and looping across a clip. Use when a composition embeds a .json or .lottie animation, when porting @remotion/lottie, or when a Lottie stutters, freezes or renders blank.
metadata:
  tags:
  - lottie
  - dotlottie
  - after-effects
  - bodymovin
  - animation
  - hyperframes
---

# Lottie for video

Lottie is a JSON format for vector animation exported from After Effects (through Bodymovin) and other tools; dotLottie
(`.lottie`) is its zipped form with assets and themes. Both fit video well because the timeline lives in the file:
HyperFrames only needs a paused player it can seek. Checked against lottie-web 5.13.0 and
@lottiefiles/dotlottie-web 0.82.0 (both MIT).

## When to use this skill

Use this skill when a composition embeds a Lottie or dotLottie file, when porting `@remotion/lottie`, or when a Lottie
in a video stutters, freezes on frame 0 or renders blank.

## Step 0: read the player versions

```bash
grep -rhoE '(lottie-web|dotlottie-web)@[0-9.]+' --include='*.html' . | sort -u   # script tags
npm ls lottie-web @lottiefiles/dotlottie-web --depth=0 2>/dev/null               # a bundled project
ls lib/dotlottie-web 2>/dev/null                                                 # self-hosted ESM and WASM
```

Take `index.js` and `dotlottie-player.wasm` from one release, and never mix files across versions.

## Pick the player

The file you were given and the job it does decide the player.

| When | Use | Why the others lose |
|---|---|---|
| A `.json` export that must stay sharp at any size | lottie-web, `renderer: "svg"` | one classic script and no WASM; dotLottie draws into a fixed-size canvas |
| A busy `.json` with many layers | lottie-web, `renderer: "canvas"` | SVG costs more per frame when the layer count climbs |
| A `.lottie` file, or themes inside the file | dotlottie-web | lottie-web reads JSON, not the zipped format |
| An export that uses effects the player cannot draw | a transparent video from the source tool, as a `<video class="clip">` | a player drops what it does not support |
| Film sound | an `<audio class="clip">` | the render mixes media elements; a dotLottie's `volume` option (0.82.0) only sets the player's own sound |

Version 0.82.0 of dotlottie-web removed the experimental MP4 video assets that 0.80.0 added, so a `.lottie` that
embeds MP4 needs re-exporting, or pin 0.81.0 for that file.

## The adapter contract

The adapter contract for Lottie has four rules.

1. Load the animation from a file inside the project (`assets/...`), never a remote URL at render time.
2. Create the player with `autoplay: false` and always set `loop` explicitly.
3. Push every player onto `window.__hfLottie`.
4. Never call `play()`, `stop()` or `goToAndPlay()`; the adapter calls `goToAndStop()` (or the dotLottie equivalent)
   on every seek.

## lottie-web pattern

The lottie-web pattern renders a JSON animation into a container.

```html
<div id="logo-lottie" style="width:640px;height:640px"></div>
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.13.0/build/player/lottie.min.js"></script>
<script>
  const anim = lottie.loadAnimation({
    container: document.getElementById("logo-lottie"),
    renderer: "svg", loop: false, autoplay: false,
    path: "assets/logo-reveal.json",
  });
  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(anim);
</script>
```

`renderer: "svg"` keeps vectors sharp at any size; `"canvas"` is lighter for busy animations with many layers.

## dotLottie pattern

The dotLottie pattern loads the ESM build and its WASM from project files. Take both `dist/index.js` and
`dist/dotlottie-player.wasm` out of a single pinned `@lottiefiles/dotlottie-web` release and put them in
`lib/dotlottie-web/`. The package's CommonJS entry will not load as a classic script.

```html
<div id="badge-wrap" data-composition-id="badge" data-no-timeline data-start="1" data-duration="3" style="position:absolute;right:120px;top:120px;width:360px;height:360px">
  <canvas id="badge-canvas" width="720" height="720" style="width:100%;height:100%"></canvas>
</div>
<script type="module">
  import { DotLottie } from "./lib/dotlottie-web/index.js";
  const wasm = new URL("./lib/dotlottie-web/dotlottie-player.wasm", import.meta.url);
  DotLottie.setWasmUrl(wasm.href);                      // the WASM comes from the project, never a CDN
  const badge = new DotLottie({
    canvas: document.querySelector("#badge-canvas"),
    src: "assets/badge-check.lottie",
    autoplay: false,                                     // the adapter seeks it; it must never run on its own
    loop: false,
    renderConfig: { freezeOnOffscreen: false, autoResize: false },
  });
  window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
  window.__hf.buildReady.badge = new Promise((done) => { badge.addEventListener("load", done); badge.addEventListener("loadError", done); });
  (window.__hfLottie ??= []).push(badge);               // register so capture can seek it
</script>
```

`freezeOnOffscreen: false` matters: a player that freezes when off screen will not draw for headless capture. The
`buildReady` promise holds the render until the file has loaded or failed, because render-ready does not wait for a
player on its own. The wrapper is its own small composition so the animation starts with it, as the next section
explains.

## Timing a Lottie inside a clip

Timing a Lottie inside a clip depends on the enclosing composition, not on the clip: the adapter counts from the
start of the nearest `data-composition-id` above the player. A plain `class="clip"` wrapper with `data-start="1"` only
decides when the animation is visible, so a one-second animation there is already on its last frame when it appears.
To start the animation with its clip, make the wrapper its own composition (`data-composition-id`, `data-no-timeline`,
`data-start`, `data-duration`, as above) or put the player in a scene file whose host carries the start.

When the clip is longer than the animation and the animation should repeat, set `loop: true` and let the clip's
duration bound it; when it should play once and hold, set `loop: false`. To change speed or start partway through,
export a trimmed animation from the source tool rather than fighting the player in script.

## Theming a Lottie to the brand

Theming a Lottie to the brand changes its colours without re-exporting.

- dotLottie files can carry themes; pick one with the `themeId` option or `setTheme()`. Since 0.82.0 `themeId` and
  `animationId` passed to the constructor apply on load; on older builds set them after load instead.
- For lottie-web, edit colours in the JSON before loading: colours are `[r, g, b, a]` arrays in 0 to 1 under `"c": {"k": [...]}`
  in fill and stroke items. Write a small script that maps old colours to the brand's, and keep the edited file in
  `assets/`.

## Checking a Lottie before using it

Checking a Lottie before using it avoids surprises from After Effects features the player does not support
(some effects, expressions, certain masks and blend modes). Open the file in a web player such as the LottieFiles
viewer, scrub it, then snapshot it in the composition at several times.

## Verify the Lottie in the film

```bash
npx hyperframes check --json                 # no errors
npx hyperframes snapshot --at 1.1,2.5,3.9    # start, middle and end of the clip: each differs and draws
grep -rnE 'autoplay: *true|\.play\(\)|https?://[^"]*\.(json|lottie)' compositions index.html   # expect nothing
```

With `loop: false` the adapter keeps showing the final frame once the file runs out, so a clip longer than the file is safe.
A blank last snapshot then means the file itself ends empty (an exit animation), or the player never loaded.

## Checklist

- [ ] The file lives in `assets/`; nothing loads from the network at render time.
- [ ] `autoplay: false`, `loop` set on purpose, player pushed to `window.__hfLottie`.
- [ ] No `play()` or `stop()` calls anywhere.
- [ ] dotLottie uses local ESM and WASM files and `freezeOnOffscreen: false`.
- [ ] dotLottie registers a `window.__hf.buildReady` promise that settles on `load` or `loadError`.
- [ ] Snapshots at the start, middle and end of the clip look right.

## Gotchas

- **Symptom:** Stutter in the render only. **Cause:** Script called `play()` and fought the adapter's seeks. **Fix:**
  remove every playback call.
- **Symptom:** A blank canvas in the render. **Cause:** A remote `src` or a CDN WASM the render environment could not
  fetch, or a player that froze off screen. **Fix:** load both from the project and set `freezeOnOffscreen: false`.
- **Symptom:** A dotLottie canvas is blank in a `render --quality draft` file, and the render still exits 0. **Cause:**
  The player never loaded: with a damaged `.lottie` or a wrong path, `isLoaded` stays false and `totalFrames` stays 0,
  so the adapter has nothing to seek, at every quality. Draft is not the reason; it changes only the encoder preset and
  the capture JPEG quality. **Fix:** log the player's `loadError` event, repair the file or path, confirm with
  `snapshot`, then judge the look at `--quality looks` or `delivery`, never from a draft. A file that loads late gives
  a smaller version of this: the first frames are blank, then the animation appears, because capture started before
  the player was ready. Register a `window.__hf.buildReady` promise that settles on `load` or `loadError`, as in the
  dotLottie pattern.
- **Symptom:** The Lottie draws in the wrong place. **Cause:** The container had no fixed size when the player
  measured it. **Fix:** size it in CSS.
- **Symptom:** Effects are missing. **Cause:** The After Effects export used features the web player does not render.
  **Fix:** simplify in the source, or export video.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `playSegments()` to change state | separate timed clips, one per state |
| fighting the player for speed or a late start | export a trimmed animation from the source tool |
| leaving `loop` unset | set it on purpose, every time |
| a CDN WASM URL | `DotLottie.setWasmUrl()` pointing at the project's file |

## See also

`hyperframes`, `motion-assets`, `remotion-to-hyperframes`.
