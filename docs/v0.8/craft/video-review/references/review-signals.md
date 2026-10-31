---
title: Review signals for video
author: MOZGII, Inc.
lang: en
---

# Review signals for video

Review signals are the concrete things in the frames or the code that show whether a dimension of a film is weak or
strong. Use them to write P0 and P1 notes, not to score. Each dimension lists weak signals, strong signals and the
usual fix.

## Contents

The sections of this page:

- Motion quality
- Technique at the peak
- Visual originality
- Typography
- Entrance choreography
- Transitions
- Emotional arc
- Sound and sync
- Depth

## Motion quality

Motion quality is whether eases, durations and holds feel chosen.

- Weak: `power2.out` at 0.5 s on every tween; titles that keep moving after landing; breathing loops on UI; exits as
  long as entrances.
- Strong: eases by role (`expo.out` arrivals, `power2.inOut` camera, `power3.in` exits); landed titles dead still;
  overlap of 30 to 50%; one motion signature per kind of element.
- Fix: retime by role, cut exits to half, remove loops that stand in for motion.

## Technique at the peak

Technique at the peak is whether the film's most important moment uses its strongest means.

- Weak: the payoff is the same fade and slide as every other beat.
- Strong: the payoff gets the boldest move: an object becoming the world, a 3D turn, a shader transition, a number
  made physical.
- Fix: spend one big technique at the peak (`vfx`, `threejs`, `hyperframes-transitions`) and simplify elsewhere.

## Visual originality

Visual originality is whether the film looks like this brand rather than a template.

- Weak: purple-to-blue gradients, neon on dark, identical card grids, everything centred, emoji icons.
- Strong: the brand's palette at video strength, a layout grid used consistently, real product screens and imagery.
- Fix: apply `design.md` exactly; replace stock patterns with the brand's own material.

## Typography

Typography is whether type has hierarchy and character at video size.

- Weak: two similar sans faces; 400 against 700; web sizes; text under 28 px meant to be read.
- Strong: two voices across categories; 300 against 900; headlines 4 to 9% of frame height; one accent word.
- Fix: see `video-design-system` step 3 and `video-fonts`.

## Entrance choreography

Entrance choreography is the order and variety of arrivals in a scene.

- Weak: everything enters at once, or one by one in DOM order, all from `y: 30`.
- Strong: importance order; three or more entrance kinds per scene; staggers within 0.5 s; reveals timed to the words.
- Fix: reorder by importance, vary direction and treatment, tie reveals to cue words.

## Transitions

Transitions are how beats hand over.

- Weak: a different transition on every seam; crossfades between unrelated worlds; empty frames before a transition.
- Strong: one primary and one or two accents; each caused by something on screen; cuts on the fastest frame.
- Fix: see `hyperframes-transitions`.

## Emotional arc

The emotional arc is whether the film builds to something.

- Weak: every beat the same energy; no hold before the payoff; the logo is the only ending.
- Strong: a named rhythm with contrast; a 0.3 to 0.75 s hold before the payoff; a last line held at least 2 s.
- Fix: write the rhythm (`fast-fast-SLOW-fast-PEAK-hold`) and retime to it.

## Sound and sync

Sound and sync is whether audio supports the picture.

- Weak: silence over 15 s; the same whoosh on every cut; hits early; voice buried under music; peaks clipping.
- Strong: a bed under the story; few effects with causes on screen; hits one frame after the picture; voice clear;
  loudness about −14 to −16 LUFS for social.
- Fix: see `audio-sync`; measure with `npx hyperframes audio <video> --json`.

## Depth

Depth is whether frames have layers.

- Weak: one flat layer on a solid ground; empty frames while content enters.
- Strong: background, midground and foreground moving at different speeds; texture breaking up flat areas.
- Fix: add a background layer from `video-design-system` textures; separate speeds per layer.
