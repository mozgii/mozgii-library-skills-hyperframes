---
title: HyperFrames composition format
author: MOZGII, Inc.
lang: en
---

# HyperFrames composition format

The HyperFrames composition format is plain HTML with `data-*` attributes for timing and one paused timeline per
composition. This page holds the detail behind the contract in the `hyperframes` skill. The CLI prints the upstream
reference in the terminal with `npx hyperframes docs compositions`, `docs data-attributes` and `docs troubleshooting`.

## Contents

The sections of this page:

- Root composition and scene files
- Timing rules for clips
- Relative starts and nesting
- Scene hosts and slots
- Track kinds in Studio
- Reading the timeline from the CLI
- Root-level gotchas

## Root composition and scene files

The root composition is `index.html`, a normal document. Its top-level `div` carries `data-composition-id`,
`data-start="0"`, `data-duration`, `data-width` and `data-height`. A scene file in `compositions/` is a fragment:
everything (styles, markup, scripts) sits inside one `<template>`, and its root `div` has the same
`data-composition-id` as the host that mounts it.

| Part | Root (`index.html`) | Scene (`compositions/*.html`) |
|---|---|---|
| Wrapper | none; `<template>` here hides everything | `<template>` around the whole file |
| Root style selector | any | `#root` (inline `<style>`; a linked sheet cannot style the root by id) |
| Root size | `data-width` × `data-height` | `position: absolute; inset: 0`, never fixed pixels |
| Timeline key | the root's `data-composition-id` | the scene's `data-composition-id` |
| Variables | on `<html data-composition-variables>` | on the scene file's `<html>` or root element, local to each mount |

A scene's timeline cannot reach elements outside its own file, so a tween in `intro.html` never targets `#demo-card`.

## Timing rules for clips

Timing rules decide when each clip is on screen.

| Rule | Consequence |
|---|---|
| Visibility runs over the half-open interval `[start, start + duration)` | a state reached exactly at `start + duration` never appears in a frame |
| `data-start` counts from the start of the file that declares it | inside a scene, time 0 is the moment the host's `data-start` arrives |
| Media without `data-duration` | `<video>` and `<audio>` run their full length; an `<img>` stays 3 s |
| Timed children of the root | the runtime stretches them to the full frame; an untimed full-bleed background must set `position: absolute; inset: 0` itself or it has no size |
| Paused timelines | only the root timeline of a composition is created paused, nested ones are not; `tl.play()` is never called |
- Variables cannot change the root's `data-duration`.

## Relative starts and nesting

`data-start="intro + 0.5"` is a relative start: the clip begins 0.5 s after the clip whose id is `intro` finishes,
and the spaces around `+` are mandatory. When the expression is wrong (a misspelling, an id that does not exist, two
clips pointing at each other) it falls back to 0 without any message, so confirm such clips with a snapshot.

Nesting does not shift time. A clip inside another timed element still measures its `data-start` from the
composition, and it is visible only during the part of its window that overlaps the outer element's window. When the two windows never meet, `timeline` warns `never visible` and lint
reports `nested_clip_never_visible`.

## Scene hosts and slots

A scene host is the `div` in `index.html` that mounts a scene file with `data-composition-src`. Its `data-duration` is
the scene's slot.

- When the scene's own timeline is shorter than the slot, its final frame stays on screen for the rest of the slot.
- When the slot ends before the video does, the area turns empty from that point
  (`subcomposition_blanks_before_host`).
- Host id, the scene's `data-composition-id` and the `window.__timelines` key are spelled identically. If the host id
  differs, the scene shows static frames and renders stall for 45 s on each scene.
- A scene timeline is never `add()`ed to the root timeline; the runtime already seeks every scene on its own.

## Track kinds in Studio

Studio sorts clips into lanes by their track kind. Scene hosts and overlay hosts are `data-track-kind="graphics"`;
all caption groups live under a single host marked `data-track-kind="captions"`. Video and audio lanes come from the
tag. `data-track-index` picks the lane; clips on one lane must not overlap. Neither attribute changes paint order:
that is CSS `z-index`.

## Reading the timeline from the CLI

The timeline command reads the project files statically and prints what plays when.

```bash
npx hyperframes timeline              # one block per track kind, with 40-column bars
npx hyperframes timeline --json       # rows with absStart, absEnd, file, src, durationSource, nested, host
```

Use `absStart` and `absEnd` (main-timeline seconds) to compare clips across nesting, not `start` and `end`, which are
local. `durationSource` says where a length came from: `authored`, `media` (ffprobe), `default` (3 s image),
`inner` (summed children) or `pending` (the source could not be probed). The command looks one level deep; a scene
nested further down is listed with `children=unread`.

This one-liner prints every clip playing at 12.5 s:

```bash
npx hyperframes timeline --json | jq --argjson t 12.5 '[.timeline.tracks[].rows[] | select(.absStart<=$t and .absEnd>$t) | {id,file}]'
```

## Root-level gotchas

Root-level gotchas are the mistakes that break a whole video rather than one clip.

- With shader transitions or HDR media in the film, the root loses its background fill; paint the colour on a child
  that covers the whole frame.
- A composition with no timeline (a still card) needs `data-no-timeline` on its root, or every render waits 45 s
  (`missing_data_no_timeline`).
- A clip that ends past the root's `data-duration` never plays its tail (`clip_ends_past_root_duration`): raise the
  root's duration first. No CLI timeline edit changes `data-duration` for you.
