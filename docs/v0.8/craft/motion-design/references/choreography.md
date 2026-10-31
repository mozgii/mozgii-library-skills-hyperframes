---
title: Choreography, beats and rhythm
author: MOZGII, Inc.
lang: en
---

# Choreography, beats and rhythm

Choreography is the order, speed and direction of everything that moves in a scene; beats are the scenes of a film;
rhythm is how their lengths and energies alternate. This page holds the planning format for beats and the rules that
keep choreography rendering correctly.

## Contents

The sections of this page:

- Each beat is an experience
- Motion verbs
- Depth layers
- Scene structure: build, breathe, resolve
- Rhythm templates
- Velocity-matched cuts
- Load-bearing animation rules

## Each beat is an experience

Each beat is an experience, not a layout. Describe what the viewer feels before the pixels.

- Weak: "Navy background. '$1.9T' in white, 280 px. Logo top-left."
- Strong: "We are already flying over a dark field. A light ribbon sweeps across like an aurora. '$1.9T' slams in so
  hard the ribbon ripples."

A beat block has a concept (two or three sentences: the world, the metaphor, the feeling), mood references (design
movements or film moments, not hex codes), choreography (a verb per element), the transition out, depth layers and
sound cues.

## Motion verbs

Motion verbs name how each element moves; an element without a verb is not designed yet.

| Energy | Verbs | Example |
|---|---|---|
| High | slams, crashes, punches, stamps, shatters | "$1.9T" slams in from the left at −5° |
| Medium | cascades, slides, drops, fills, draws | three cards cascade in 0.3 s apart |
| Low | types on, floats in, morphs, counts up, fades in | the counter counts up from 0 to 135K |

## Depth layers

Depth layers give every frame a background, a middle and a foreground.

- Background: radial glow, oversized ghost type, a colour panel, grain, a slow texture; never a dead flat fill.
- Midground: the message (cards, numbers, footage, code).
- Foreground: rules, labels, registration marks, small mono metadata.

Two or three layers moving at different speeds read as depth. A frame with three elements looks empty; seven to ten
(two of them decoration) looks produced.

## Scene structure: build, breathe, resolve

Scene structure has three phases.

- Build (first 30%): elements enter, staggered by importance.
- Breathe (30 to 70%): content visible, with one real action (the UI working, a number landing, a camera move).
- Resolve (last 30%): the decisive end, or the transition into the next beat.

Spread the reveals through the scene, each piece appearing on the word of narration that names it; everything on screen in the first quarter and then
frozen reads as a slideshow.

## Rhythm templates

Rhythm templates by video type:

| Video | Pattern |
|---|---|
| Social ad, 15 s | hook, PUNCH, hold, CTA |
| Launch teaser, 10 to 20 s | SLAM, proof, SLAM, hold |
| Product demo, 30 to 60 s | slow build, BUILD, PEAK, breathe, CTA |
| Brand reel, 20 to 45 s | drift, build, PEAK, drift, resolve |
| Explainer, 60 to 120 s | question, steps with holds, recap, CTA |

A 5 to 7 beat brand reel usually spends one or two big transitions (the hero reveal and the call to action) and keeps
the rest simple.

## Velocity-matched cuts

Velocity-matched cuts make a cut feel like one continuous move: the outgoing beat exits with an accelerating ease and
a blur ramp, the incoming one enters with a decelerating ease and the blur clearing, and their fastest moments meet at
the cut.

| Move | Out | In |
|---|---|---|
| Upward | `y: -150`, blur 30 px, 0.33 s `power2.in` | `y: 150 → 0`, blur 30 → 0, 1 s `power2.out` |
| Whip | `x: -400`, blur 24 px, 0.3 s `power3.in` | `x: 400 → 0`, blur 24 → 0, 0.3 s `power3.out` |
| Blur through | blur 20 px, 0.3 s | blur 20 → 0, 0.25 s `power3.out` |
| Zoom through | scale 1 → 1.2, blur 20 px, 0.2 s `power3.in` | scale 0.75 → 1, blur 20 → 0, 0.5 s `expo.out` |

## Load-bearing animation rules

Load-bearing animation rules are the ones that lint cannot catch but that break renders.

- **One transform tween per element at a time.** An entrance `y` and a Ken Burns `scale` on the same image fight; put
  the entrance on a wrapper and the scale on the child, or combine them in one `fromTo`.
- **`fromTo` inside scenes.** `from` writes its start state at construction and drifts when the scene is re-seeked.
- **Ambient motion on the timeline.** A bare `gsap.to()` outside the registered timeline runs on wall-clock time and
  does not render; add it to `tl` with a finite repeat.
- **Hard-kill at boundaries.** Anything that must be gone after a fade gets
  `tl.set(el, { opacity: 0, visibility: "hidden" }, end)` (not on a `.clip` itself).
- **No iframes for captured content.** Iframes do not seek with the timeline; use screenshots.
