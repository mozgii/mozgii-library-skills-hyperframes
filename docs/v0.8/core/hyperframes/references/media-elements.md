---
title: Video, audio and images in HyperFrames
author: MOZGII, Inc.
lang: en
---

# Video, audio and images in HyperFrames

Video, audio and image elements in HyperFrames are timed clips whose playback the runtime owns. The runtime finds
media at any nesting depth, seeks and decodes it for each frame, and mixes every `<audio>` and every
`<video data-has-audio="true">` into the soundtrack.

## Adding a clip the way Studio does

A clip written by hand stays editable in Studio when it carries what Studio itself writes on a drop:

| Part | Value |
|---|---|
| identity and timing | `id`, `class="clip"`, `data-start` set to the time asked for (an explicit value, not a default of 0), `data-track-index` |
| video that keeps its sound | `playsinline data-has-audio="true"` |
| silent footage | `muted playsinline` |
| audio | `data-volume="1"` |
| box | `position: absolute; left: 0; top: 0`, the canvas's width and height, `object-fit: contain` |
| stacking | a `z-index` equal to the count of top-level clips in the file plus one |

If the new clip ends after the root's `data-duration`, lengthen the root; otherwise the clip's end is cut off.

```html
<video id="broll-1" class="clip" src="assets/broll-1.mp4" muted playsinline
       data-start="4" data-duration="6" data-media-start="12.5" data-track-index="0"
       style="position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover;z-index:1"></video>
<audio id="voice" class="clip" src="assets/voice.wav" data-start="0.4" data-track-index="6" data-volume="1"></audio>
```

## Trims, speed and holds

Trims, speed changes and holds are attributes, not script.

| Need | How |
|---|---|
| Start partway into the source | `data-media-start="12.5"` |
| Constant speed | `data-playback-rate="0.5"` (0.1 to 10; sound keeps its pitch) |
| Speed ramp | `data-automation` on the media with a `rate` lane; `t` counts clip seconds and `v` runs from 0.1 to 10 |
| Freeze mid-source | export a still with FFmpeg and place it as its own `<img>` clip |
| Hold the last frame | let the clip's slot run past the media's end |

## Moving, cropping and zooming footage

Moving, cropping and zooming footage is done on a wrapper, never on the timed media element. The runtime sets the
active clip's own `opacity` and visibility, and lint fails `gsap_animates_clip_element` when GSAP animates `visibility`,
`display` or `autoAlpha` on the clip.

```html
<div id="pip" style="position:absolute;inset:0;overflow:hidden;z-index:5">
  <video id="talk" class="clip" src="assets/talk.mp4" playsinline data-has-audio="true"
         data-start="0" data-duration="20" data-track-index="0" style="width:100%;height:100%;object-fit:cover"></video>
</div>
```

```js
tl.to("#pip", { left: 1360, top: 700, width: 500, height: 280, borderRadius: 16, duration: 1, ease: "power3.inOut" }, 10);
```

For a punch-in, tween `scale` and `x`/`y` on the wrapper. For a mask reveal, tween `clip-path` on the wrapper. Time a
`<video>` or its wrapper, never both (`video_nested_in_timed_element`).

## Linked clips: one source on two tracks

Studio's Detach audio turns one clip into two linked clips: a muted `<video>` plus an `<audio>` of the same file;
both carry the same `data-link` and `data-sync-origin`, and Studio then moves, trims and splits the pair together.

- One `<video data-has-audio="true">` is simpler; split into linked clips only when the sound needs a track, level or
  effect chain of its own.
- All members share identical `data-start`, `data-duration`, `data-media-start` and `data-playback-rate` values.
- Unlink by removing `data-link` from every member (`linked_clip_orphan` otherwise).

## Text behind a person

Text behind a person stacks three layers by `z-index`: the original video, the headline, and a transparent cutout of
the person made with `npx hyperframes remove-background talk.mp4 -o talk.webm`. Start both videos at the same
`data-start` and `data-media-start` so they decode in sync; a cutout mounted later can land a frame off the base.
`check` treats a `<video>` as opaque, so mark the cutout `data-layout-allow-occlusion` and judge from snapshots.

## Images and formats that render reliably

Images and video render reliably in these forms:

- Images: PNG, JPEG, WebP, SVG; size them close to their on-screen pixels (a 6000 px photo shown at 800 px costs memory
  in every worker).
- Video: H.264 MP4 for opaque footage; VP9 WebM with alpha or ProRes 4444 MOV for transparent overlays. Codecs Chrome
  cannot decode (HEVC, ProRes, AV1) get a playable proxy by default in `preview`, `play`, `check` and `publish`;
  `snapshot` makes one only with `--proxy`. `render` has no such flag and decodes the original.
- Colour looks on footage (grades, LUTs, grain, vignettes) go through `npx hyperframes media-treatment`, not CSS
  filters, so preview and render match.

## Media gotchas

Media gotchas are the mistakes that produce silent or blank clips.

- **No sound from a video.** It has `muted` or lacks `data-has-audio="true"`; a timed `<video>` with neither fails lint.
- **Audio missing from the mix.** The `<audio>` has no `id` (`media_missing_id`).
- **Preview breaks on a remote file.** `crossorigin` on media breaks preview (`media_crossorigin_breaks_preview`);
  download the file into `assets/` instead.
- **A clip plays from the start after a seek.** Script called `play()` or set `currentTime`; remove it.
- **Black panel where footage should be.** Snapshot each scene with video after a render and confirm footage shows.
