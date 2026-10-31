---
title: Remotion to HyperFrames API map
author: MOZGII, Inc.
lang: en
---

# Remotion to HyperFrames API map

The Remotion to HyperFrames API map lists each Remotion API and what replaces it in a HyperFrames project. "Drop"
means the HyperFrames runtime already does the job. "Host" means the original code stays and HyperFrames feeds it
the time (see the limitations reference).

## Contents

The sections of this page:

- Composition root
- Sequencing
- Timing and animation
- Media
- Transitions
- Lottie
- Fonts
- Props and schemas
- React patterns
- Rendering infrastructure

## Composition root

The composition root in Remotion is `<Composition>`; in HyperFrames it is the root `div` of `index.html`.

| Remotion | HyperFrames |
|---|---|
| `<Composition id durationInFrames fps width height>` | root `div` with `data-composition-id`, `data-start="0"`, `data-duration` = frames / fps, `data-fps`, `data-width`, `data-height` |
| `defaultProps` | `data-composition-variables` defaults |
| `schema` (zod) | variable types; validation happens at translation time |
| `calculateMetadata`, synchronous | compute once, write the values in |
| `calculateMetadata`, async | host, or resolve once offline |
| `registerRoot` | drop |
| `<AbsoluteFill style>` | `<div style="position:absolute;inset:0;...">` |
| render page `* { box-sizing: border-box }` | that rule, written a single time in the root's `<style>` |

## Sequencing

Sequencing in Remotion nests time; in HyperFrames, each scene has a host with a start and a slot.

| Remotion | HyperFrames |
|---|---|
| `<Sequence from={F} durationInFrames={D}>` | a host `div` with `data-composition-src`, `data-start` = F / fps, `data-duration` = D / fps |
| `<Series>` with `<Series.Sequence>` | sibling hosts with back-to-back starts, or `data-start="prev + 0"` |
| `<Loop durationInFrames>` | a finite GSAP repeat computed from the slot |
| `<Freeze frame>` | drop; place a still or hold the scene's last frame |
| a nested `Sequence` | a clip whose `data-start` is local to its scene file |

## Timing and animation

Timing and animation in Remotion are functions of `frame`; in HyperFrames they are tweens at absolute seconds.

| Remotion | HyperFrames |
|---|---|
| `useCurrentFrame()` | drop; the timeline is seeked |
| `useVideoConfig()` | read `data-fps`, `data-duration`, `data-width` from the root |
| `interpolate(frame, [a,b], [x,y])` | `tl.fromTo(el, {p:x}, {p:y, duration:(b-a)/fps, ease:"none"}, a/fps)` |
| multi-point `interpolate` | one tween per segment at each segment's start |
| `spring({fps, frame, config})` | `back.out(N)` or `elastic.out`; see the timing reference |
| `interpolateColors` | a colour tween; GSAP interpolates colours |
| `Easing.*` | GSAP eases; see the timing reference |

## Media

Media in Remotion are React components; in HyperFrames they are timed elements the runtime plays.

| Remotion | HyperFrames |
|---|---|
| `<Audio src volume>` | `<audio class="clip" id data-start data-duration data-volume>` |
| `startFrom`, `endAt` | `data-media-start` and `data-duration` |
| `playbackRate` | `data-playback-rate` |
| a volume callback (ramp) | `data-fade-in`, `data-fade-out`, or an automation lane; note what changed |
| `<Video>`, `<OffthreadVideo>` | `<video class="clip" playsinline>` plus `data-has-audio="true"` when the file has an audio stream, else `muted` |
| `<Img>` | `<img>` |
| `<IFrame>` | `<iframe>`; check frames carefully |
| `staticFile("x.png")` | `assets/x.png` |
| `delayRender`, `continueRender` | drop; heavy setup registers a `window.__hf.buildReady["key"]` promise |

Check for an audio stream with `ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 file.mp4`;
empty output means silent.

## Transitions

Transitions in Remotion come from `@remotion/transitions`; in HyperFrames they are tweens or shader transitions.

| Remotion | HyperFrames |
|---|---|
| `<TransitionSeries>` with `fade()` | opacity crossfade tweens at the seam |
| `slide()`, `wipe()`, `clockWipe()`, `flip()` | the matching CSS transition or a shader from `@hyperframes/shader-transitions` |
| `linearTiming({durationInFrames})` | duration in seconds, `ease: "none"` |
| `springTiming({config})` | duration in seconds, `back.out` |

In a `TransitionSeries`, the transition overlaps the two sequences, so the total length is the sum of the sequences
minus the transitions. Keep that arithmetic when computing `data-start` values.

## Lottie

Lottie in Remotion is `@remotion/lottie`; in HyperFrames it is `lottie-web` or dotLottie registered on
`window.__hfLottie` with `autoplay: false` (see the `lottie` skill).

## Fonts

Fonts in Remotion often come from `@remotion/google-fonts` or `loadFont()`; in HyperFrames, use a bundled family by
name or an `@font-face` rule to a file in `assets/fonts/`. Download the exact font files the original used; a
fallback font changes line breaks and fails the comparison.

## Props and schemas

Props and schemas map to variables.

| Remotion | HyperFrames |
|---|---|
| a scalar prop | a variable of type `string`, `number`, `boolean` or `color` |
| an enum prop | a variable of type `enum` with `options` |
| an array of items (`stats[]`) | repeated markup or one scene file mounted per item with `data-variable-values` |
| zod defaults | variable `default` values |

## React patterns

React patterns translate when they are pure functions of the frame.

| Remotion | HyperFrames |
|---|---|
| a pure, prop-driven subcomponent | repeated HTML, or a scene file mounted per instance |
| `useState`, `useReducer` driving visuals | host, or refactor to derive from the frame |
| `useEffect` with dependencies | host, or refactor |
| `useEffect(fn, [])` one-time setup | run the setup synchronously at init |
| `useMemo`, `useCallback` | drop the wrapper |
| a custom hook that derives from the frame | inline its body as tweens |

## Rendering infrastructure

Rendering infrastructure in Remotion (`@remotion/lambda`, `@remotion/cloudrun`, `renderMedia`) is configuration, not
content. Drop it and render with `npx hyperframes render`, `lambda render` or `cloudrun render`; note the change.
