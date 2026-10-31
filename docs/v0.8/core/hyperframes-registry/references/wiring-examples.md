---
title: HyperFrames registry wiring examples
author: MOZGII, Inc.
lang: en
---

# HyperFrames registry wiring examples

HyperFrames registry wiring examples show an installed block and an installed component connected to a project, plus
a custom install layout. Item names are real catalog entries at the time of writing; check `catalog --json` for the
current set.

## Wiring a chart block

Wiring a chart block mounts a whole scene over existing footage.

```bash
npx hyperframes add data-chart --json
```

```html
<div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-start="0" data-duration="20">
  <video id="a-roll" class="clip" src="assets/a-roll.mp4" playsinline data-has-audio="true"
         data-start="0" data-duration="20" data-track-index="0"></video>
  <div id="data-chart" data-composition-src="compositions/data-chart.html" data-composition-id="data-chart"
       data-track-kind="graphics" data-track-index="1" data-start="2" data-duration="15"
       data-width="1920" data-height="1080" style="position:absolute;inset:0 0 0 auto;width:40%"></div>
</div>
```

The block keeps its own timeline. Several blocks can sit side by side with overlapping or separate times; each is
seeked in sync.

## Wiring a grain overlay component

Wiring a grain overlay component copies a full-frame layer and its CSS into a scene.

```bash
npx hyperframes add grain-overlay --json
```

```html
<div id="grain-overlay" data-layout-ignore
     style="position:absolute;inset:0;pointer-events:none;z-index:100">
  <div class="grain-texture"></div>
</div>
```

Copy the `.grain-texture` rule and its `@keyframes` from the installed file into your `<style>`. The grain animates
with CSS keyframes, which HyperFrames seeks, so no timeline call is needed. `data-layout-ignore` keeps the layout
audit from flagging a decorative layer.

## Wiring a component that needs timeline calls

A component that needs timeline calls exposes a setup function or a set of tweens in its comment header. The usual
shape: wrap the target in the markup it expects, paste its CSS, run its setup before your timeline code, then place
its tweens at your chosen times.

```js
// from the component's header: wrap the headline, then sweep a highlight across it
tl.fromTo("#headline .shimmer", { xPercent: -120 }, { xPercent: 120, duration: 0.9, ease: "power2.inOut" }, 1.4);
```

## Custom install paths

Custom install paths come from `hyperframes.json`:

```json
{
  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": { "blocks": "scenes", "components": "scenes/components", "assets": "assets" }
}
```

With this file, `npx hyperframes add data-chart` writes `scenes/data-chart.html` and prints a mount snippet with that
path.
