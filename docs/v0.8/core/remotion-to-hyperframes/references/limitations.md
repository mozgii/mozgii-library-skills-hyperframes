---
title: Remotion port limitations and hosting
author: MOZGII, Inc.
lang: en
---

# Remotion port limitations and hosting

Remotion port limitations are the source patterns that cannot become plain HTML and GSAP without changing behaviour.
Hosting is the way to bring such code in anyway: keep it, and drive it from HyperFrames time.

## Why state and effects block a port

State and effects block a port because HyperFrames renders by seeking to arbitrary times in any order. A component
whose look at frame 120 depends on `useState` updates made at frames 0 to 119 has no way to produce frame 120 on its
own. Effects with dependencies have the same problem. The fix is to make the visual a function of time only.

## Refactoring state into a function of time

Refactoring state into a function of time replaces accumulated state with a formula.

```tsx
// Remotion, stateful: a typewriter that appends one char per 2 frames in an effect
const [text, setText] = useState("");
useEffect(() => { if (frame % 2 === 0) setText(full.slice(0, frame / 2)); }, [frame]);
```

```js
// HyperFrames, pure: the visible length is a function of time
const p = { n: 0 };
tl.to(p, { n: full.length, duration: full.length * 2 / 30, ease: "none",
  onUpdate: () => { el.textContent = full.slice(0, Math.floor(p.n)); } }, 1.0);
```

## Hosting a component

Hosting a component keeps its drawing code and replaces its clock. Render the component's output into a canvas or a
DOM node from the time in each `hf-seek` event:

```html
<canvas id="sim" width="1920" height="1080"></canvas>
<script>
  const ctx = document.getElementById("sim").getContext("2d");
  function drawAt(t) {
    // derive everything from t: positions, colours, counts; seeded randomness only
    ctx.clearRect(0, 0, 1920, 1080);
    /* ... */
  }
  window.addEventListener("hf-seek", (e) => drawAt(e.detail.time));
  drawAt(0);
</script>
```

A React component can be hosted too: render it with React into a container on each seek, passing the time (or
`Math.round(time * fps)` as `frame`) as a prop, with no state carried between seeks. Set `data-duration` on the root
when no GSAP timeline defines the length.

## What cannot be ported

What cannot be ported, even hosted:

- simulations that depend on the previous frame (physics, particles with accumulated velocity) unless they can be
  re-run from 0 to `t` on each seek fast enough, or baked to video;
- anything that reads the network, the clock or live input during rendering;
- UI kits whose look depends on their own animation clocks (ripples, hover states).

Bring these in as media: render them once in their own tool and place the video.

## Warnings that are dropped

Warnings that are dropped do not change the picture: `@remotion/lambda` and `@remotion/cloudrun` imports,
`delayRender` and `continueRender`, `useMemo` and `useCallback` wrappers. Note each in `TRANSLATION_NOTES.md`.
