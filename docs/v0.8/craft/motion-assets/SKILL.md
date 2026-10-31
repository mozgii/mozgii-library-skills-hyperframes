---
name: motion-assets
description: Designs and builds reusable motion graphics assets for HyperFrames videos - interface mockups (glass panels, HUDs, dashboards, terminals, data tables), characters and mascots in Lottie, 3D product objects in Three.js, procedural backgrounds in shaders or canvas, morphing icon systems and technical line drawings - choosing the technique, the asset brief, the quality tests and the seek contract each must meet. Use when a video needs a custom visual component that the registry does not have, such as a product UI recreation, a mascot, an animated icon set or a signature background.
metadata:
  tags:
  - motion-graphics
  - assets
  - ui-mockups
  - lottie
  - threejs
  - svg
  - icons
  - backgrounds
---

# Motion graphics assets

Motion graphics assets are reusable visual components for video: an interface recreated for a product demo, a
mascot, a 3D object, an icon set that morphs, a signature background. Each is built once as a self-contained piece
(often its own scene file or registry-style component) and reused across scenes and videos. This skill covers how to
brief, choose a technique, build and judge one.

## When to use this skill

Use this skill when a video needs a custom component the registry does not have: a product's UI rebuilt to animate,
a character, an animated icon family, a 3D product shot, a data diagram, or a background that carries the brand.
Search first: `npx hyperframes catalog --query "<the asset, in English>" --json`.

## Step 0: read the tools the asset will use

```bash
npx hyperframes --version
grep -rhoE '(gsap|three|lottie-web|dotlottie-web)@[0-9.]+' --include='*.html' . | sort -u   # what the project already loads
npx hyperframes catalog --query "<the asset, in English>" --json | jq '.tier'               # search before building
```

Reuse the versions the project loads rather than adding a second copy of a library.

## Step 1: the asset brief

Step 1 writes a short brief before any code.

- **What it is and where it appears:** "a dashboard panel for the 0:12 to 0:20 beat, right half of the frame".
- **What it must say:** the one idea or number it carries.
- **States:** the rest state, the entrance, any change of state (a value updating, a click), the exit.
- **Brand inputs:** colour tokens, type, corner radius, depth from `design.md`.
- **Reuse:** one video or many; variables it should expose (labels, values, colours).

## Step 2: choose the technique

Step 2 chooses the technique by what the asset is.

| Asset | Technique | Why |
|---|---|---|
| Product UI, dashboards, terminals, tables, cards | HTML and CSS with GSAP | crisp text, exact layout, editable copy |
| Characters, mascots, complex icon animation | Lottie from an animation tool | timeline lives in the file; designers can edit it |
| 3D product objects, sculptures, exploded views | Three.js | real lighting and camera |
| Procedural environments, plasma, fluid, nebula | WebGL shader | per-pixel maths |
| Particles, constellations, flow fields | Canvas 2D | many objects, cheap |
| Icon systems, logo builds, diagram morphs, line drawings | SVG with MorphSVG and DrawSVG | resolution-free, morphable |

Pairing two techniques is common: a shader background behind an HTML panel, a Lottie character over a 3D stage.
Code for each: [references/asset-techniques.md](references/asset-techniques.md),
[references/ui-elements.md](references/ui-elements.md), [references/visual-techniques.md](references/visual-techniques.md).

## Step 3: build to the seek contract

Step 3 builds the asset so it renders correctly from any frame.

- Colours from CSS variables (`var(--accent)`), copy and values from variables, sizes relative to the canvas.
- Motion on the scene's paused timeline; `fromTo` inside scene files.
- 3D, canvas and shaders draw from the timeline or `hf-seek` time; randomness seeded.
- Lottie players with `autoplay: false`, pushed to `window.__hfLottie`; state changes as separate timed clips.
- Assets loaded from `assets/`; heavy setup registered as a `window.__hf.buildReady` promise.
- Real things come from their source: the product's real screens, the brand's real logo. Draw only what has no source.

## Interface recreations for product demos

Interface recreations for product demos rebuild only what moves. Show static parts as screenshots placed at measured
positions, and rebuild in HTML the elements that change state (a counter, a toggle, a list that fills, a cursor's
target). Perform each change as an interaction: the cursor moves, clicks, and the screen responds; a demo holds one
framing for 7 to 10 s while the UI acts.

## Worked example: a reusable stat panel

A stat panel for a dashboard beat, built as one scene file so any film can mount it with its own label and value. It
takes the brief above literally: the rest state is the panel with its number, the change of state is the count, and
colours, copy and value all come in from outside. A missing value falls back to the declared default, so a mount with
no overrides still renders something readable.

```html
<!-- compositions/stat-panel.html -->
<template>
  <style>
    #root { position: absolute; inset: 0; }
    #sp-card { position: absolute; inset: 8%; padding: 6%; border-radius: 28px; background: var(--panel, #151922);
               color: var(--ink, #f4f1ea); display: flex; flex-direction: column; justify-content: center; gap: 4%; }
    #sp-label { font: 600 34px/1.2 "Inter", sans-serif; opacity: .72; }
    #sp-value { font: 800 148px/1 "Inter", sans-serif; font-variant-numeric: tabular-nums; color: var(--accent, #ff5a36); }
    #sp-rule  { height: 8px; border-radius: 4px; background: var(--accent, #ff5a36); transform-origin: 0 50%; }
  </style>
  <div id="root" data-composition-id="stat-panel" data-width="960" data-height="1080"
       data-composition-variables='[{"id":"label","type":"string","label":"Label","default":"Weekly installs"},
                                    {"id":"value","type":"number","label":"Value","default":0}]'>
    <div id="sp-card" role="group" aria-labelledby="sp-label">
      <div id="sp-label" data-var-text="label">Weekly installs</div>
      <div id="sp-value">0</div>
      <div id="sp-rule"></div>
    </div>
  </div>
  <script>
    const { value = 0 } = window.__hyperframes.getVariables();
    const target = Number.isFinite(Number(value)) ? Number(value) : 0;
    const out = document.getElementById("sp-value");
    const n = { v: 0 };
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#sp-card", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "expo.out" }, 0.2);
    tl.fromTo("#sp-rule", { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: "power3.out" }, 0.5);
    tl.fromTo(n, { v: 0 }, { v: target, duration: 1.4, ease: "power3.out",
      onUpdate: () => { out.textContent = Math.round(n.v).toLocaleString("en-US"); } }, 0.5);
    window.__timelines["stat-panel"] = tl;
  </script>
</template>
```

Mount it where the beat needs it, with the values for this film:

```html
<div id="stat-panel" data-composition-src="compositions/stat-panel.html" data-composition-id="stat-panel"
     data-track-kind="graphics" data-track-index="2" data-start="12" data-duration="8" data-width="960" data-height="1080"
     style="position:absolute;right:0;top:0;width:50%;height:100%"
     data-variable-values='{"label":"Weekly installs","value":48210}'></div>
```

The count starts from a `fromTo`, so seeking backwards lands on the right number; the digits are tabular, so they hold
still; ids carry the `sp-` prefix, so two assets can share a film. `label` and `value` are declared on the scene root's
`data-composition-variables`, so a mount's `data-variable-values` has something to override and the defaults fill in
for a mount that sets neither.

## Quality tests

Quality tests judge an asset before it goes into a film.

- **Art department test:** would it pass as made by a studio's art department, or does it look like a template?
- **Simplicity test:** remove one element; if nothing is lost, keep it removed.
- **Motion test:** does each moving part move for a reason, with an ease that fits its role?
- **Craft test:** aligned to a grid, consistent radii and strokes, real copy instead of lorem ipsum, readable at phone
  size (`npx hyperframes snapshot --review` includes a 360 px wide sheet).

## Verify the asset

```bash
npx hyperframes check --json                        # no errors, nothing off the canvas
npx hyperframes snapshot --at 12.1,13,14.2,19.9     # entrance, count, landed value, last frame
npx hyperframes render --quality draft -c compositions/stat-panel.html -o /tmp/asset.mp4   # the asset alone
npx hyperframes snapshot --review                   # includes the 360 px wide sheet
```

Mount the asset a second time with other values: a hard-coded label or colour shows up at once.

## Checklist

- [ ] Registry searched; the brief written.
- [ ] Technique chosen for what the asset is; pairings deliberate.
- [ ] Colours, copy and values from variables; nothing hard-coded to one video.
- [ ] Seek contract met for every layer; snapshots at several times look right.
- [ ] Real product screens and logos used where they exist.
- [ ] Passes the four quality tests.

## Gotchas

- **Symptom:** A 3D or canvas asset stays frozen. **Cause:** No `hf-seek` listener, or no draw call inside it.
  **Fix:** draw from the event's time in the listener.
- **Symptom:** A Lottie character switches state late or not at all. **Cause:** Script called `play()` or
  `playSegments()`. **Fix:** use timed clips.
- **Symptom:** Mockup text is blurry. **Cause:** A screenshot was scaled up. **Fix:** rebuild the text in HTML or
  capture at 2x.
- **Symptom:** The asset breaks in vertical. **Cause:** Fixed pixel positions. **Fix:** lay it out relative to the
  canvas and test at 1080×1920.

## Anti-patterns

| Do not | Do instead |
|---|---|
| building before searching the registry | `catalog --query` first |
| rebuilding a whole product screen | screenshots for what stays still, HTML for what changes |
| lorem ipsum in a mockup | real copy |
| drawing a brand's logo by hand | the brand's real file |

## References

- [references/ui-elements.md](references/ui-elements.md): ten interface elements with code: glass panel, HUD, neon border, readouts, rings, roadmap, mesh background, data table, terminal, node network.
- [references/asset-techniques.md](references/asset-techniques.md): shader, Three.js, Lottie and morphing SVG assets, and how to pair them.
- [references/visual-techniques.md](references/visual-techniques.md): eleven scene techniques from path drawing to audio-reactive motion.

## See also

`vfx`, `threejs`, `lottie`, `data-in-motion`, `video-design-system`.
