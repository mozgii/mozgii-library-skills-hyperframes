---
title: HyperFrames lint rules and fixes
author: MOZGII, Inc.
lang: en
---

# HyperFrames lint rules and fixes

HyperFrames lint rules are static checks that `npx hyperframes lint` and the first stage of `npx hyperframes check`
run over `index.html` and every file in `compositions/`. While a lint error remains, `check` skips the browser audits
(layout, motion, contrast), and `browserSkipped: true` in its JSON means those sections are empty, not clean.

## Errors you meet first

The errors you meet first and their fixes:

| Rule | Cause | Fix |
|---|---|---|
| `video_missing_muted` | a timed `<video>` has neither `muted` nor `data-has-audio="true"` | add one of them |
| `gsap_css_transform_conflict` | CSS `transform` on an element GSAP transforms | move the start state into `gsap.fromTo` |
| `gsap_animates_clip_element` | GSAP tweens `visibility`, `display` or `autoAlpha` on a `.clip` element; moves and opacity do not trigger it | delete that tween, or put those properties on a child element |
| `video_nested_in_timed_element` | a `<video>` and its wrapper are both timed | time one of them |
| `media_missing_id` | an `<audio>` has no `id` | add an `id` |
| `media_crossorigin_breaks_preview` | `crossorigin` on media | remove it and keep the file in `assets/` |
| `gsap_timeline_registered_before_async_build` | the timeline was registered, then built in an async callback | register at the end of the callback |
| `standalone_composition_wrapped_in_template` | `index.html` uses `<template>` | only scene files use `<template>` |
| `subcomposition_linked_style_names_root_id` | a linked stylesheet styles `#root` | use an inline `<style>`, or select a child |
| `subcomposition_root_styled_by_class` | a scene root is styled by class | style it as `#root` |
| `subcomposition_blanks_before_host` | a scene's slot ends before it should | lengthen the host's `data-duration` |
| `clip_ends_past_root_duration` | a clip ends after the video | raise the root's `data-duration` |
| `linked_clips_out_of_sync`, `linked_clip_orphan` | linked members differ, or one lost its partner | retime all members together; unlink from all |
| `font_family_without_font_face` | a non-bundled family has no `@font-face` | add `@font-face` to a file in `assets/fonts/` |
| `nested_clip_never_visible` | a nested clip's window never meets its parent's | move it inside the parent's window |
| `missing_data_no_timeline` | a root or host has no timeline | add `data-no-timeline`; otherwise each render stalls for 45 s |

## Warnings about files

`missing_stylesheet_asset` (0.8.222 on) is a warning about a `url()` inside a project stylesheet that points at nothing.
A browser reads such a path from the folder the `.css` file sits in, not from the page, so a font or image goes missing
and the render carries on with a fallback. Make the path relative to the `.css` file (`../assets/fonts/x.ttf` from
`styles/main.css`) or add the file. If the file sits one level up, the lint message already prints the right path.

## Browser findings from check

Browser findings come from the second stage of `check`, which loads the composition once and seeks a grid of times.

| Finding | Meaning |
|---|---|
| `sweep_static` | 3 s or more of video in which no frame differs: seeking has no effect on the page |
| `content_overlap`, `text_occluded` | text held on top of other text, or covered by an element |
| `canvas_overflow`, `escaped_container` | text off the canvas or out of its box |
| `canvas_covered` | a single opaque element hides all other clips through most of the film |
| contrast | WCAG AA failure; the finding carries `suggestedColor` |
| `motion_appears_late`, `motion_out_of_order`, `motion_off_frame`, `motion_frozen` | a `*.motion.json` assertion failed |

Craft warnings never fail the run, `--strict` included: `line_unread` (a line leaves before it can be read),
`dead_stretch` (over 3 s in which nothing changes), `text_below_floor`, `first_frame_empty` (social players use frame
0 as the thumbnail) and `film_silent` (longer than 15 s without sound).

## Shader lint

Shader lint inspects the GLSL written into a composition. To clear `shader_unbounded_cosine_pow`, limit the cosine to
`[0, 1]` on both sides before it reaches `pow(1.0 - cosine, exponent)`; a `max` that only sets the floor leaves the
problem in place. Then preview and render on the affected GPU, because
software rendering can miss invalid pixels that hardware produces.
