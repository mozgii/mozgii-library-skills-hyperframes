---
name: platform-formats
description: Chooses canvas size, aspect ratio, frame rate, length and safe zones for where a video will play - YouTube, Shorts, TikTok, Instagram Reels and feed, LinkedIn, X, websites, presentations and event screens - and adapts one HyperFrames composition from 16:9 to 9:16, 1:1 or 4:5 with layout, type and pacing changes. Use when a video is for a named platform, when making vertical or square versions, when captions or calls to action are hidden by app buttons, or when choosing between landscape and portrait.
metadata:
  tags:
  - aspect-ratio
  - vertical-video
  - safe-zones
  - social-media
  - youtube
  - tiktok
  - reels
  - formats
---

# Video formats for platforms

Video formats for platforms set the canvas a composition is built on: width and height, frame rate, length, and the
margins the platform's own buttons cover. Decide them before the first scene, because layout, type size and pacing all
follow from the canvas. Platform limits change often; the numbers below were current at the time of writing, so check
each platform's help pages before a launch.

## When to use this skill

Use this skill when a video is for a named platform, when someone asks for a vertical, square or 4:5 version, when
calls to action or captions sit under app buttons, or when choosing between landscape and portrait.

## Step 0: read the canvas the project already has

```bash
npx hyperframes --version
grep -hoE 'data-(width|height|fps)="[0-9/]+"' index.html | sort -u    # the root's size and frame rate
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 assets/source.mp4   # footage to match
```

Decide the target before the first scene: a canvas change later means rebuilding the layout.

## Canvas presets

Canvas presets in HyperFrames come from `init --resolution` and `render --resolution`.

| Preset | Size | Ratio | Typical use |
|---|---|---|---|
| `landscape` (`1080p`) | 1920×1080 | 16:9 | YouTube, websites, presentations, LinkedIn |
| `portrait` | 1080×1920 | 9:16 | Shorts, TikTok, Reels, Stories |
| `square` (`1080p-square`) | 1080×1080 | 1:1 | feeds, thumbnails |
| `landscape-4k`, `portrait-4k`, `square-4k` | 3840×2160, 2160×3840, 2160×2160 | as above | high-end delivery, event screens |
| custom 4:5 | 1080×1350 | 4:5 | Instagram and other portrait feeds |
| custom 21:9 | 2560×1080 | 21:9 | cinematic films, stage screens |

A custom size is `data-width` and `data-height` on the root. `render --resolution` supersamples an integer scale of the
composition's own aspect (for example a 1920×1080 composition at `4k`); it cannot change the aspect.

## Platform guide

The platform guide lists common targets. Treat lengths and limits as guides to verify.

| Platform | Canvas | Length that works | Notes |
|---|---|---|---|
| YouTube | 1920×1080 or 3840×2160, 24 to 60 fps | any | sound on; hook within about 3 s; upload a sidecar SRT |
| YouTube Shorts | 1080×1920 | under 60 s works best (uploads up to 3 min) | loops; captions burned in |
| TikTok | 1080×1920 | 15 to 60 s | sound often on; heavy bottom and right UI |
| Instagram Reels | 1080×1920 | 15 to 90 s | the feed shows a 4:5 crop of the centre |
| Instagram and other feeds | 1080×1350 (4:5) or 1080×1080 | 10 to 60 s | often muted: captions and on-screen text carry it |
| LinkedIn | 1920×1080, 1080×1080 or 1080×1350 | 30 to 90 s | mostly muted; upload SRT captions |
| X | 1920×1080 or 1080×1080 | up to 20 min (125 min with Premium or verified) | muted autoplay |
| Website hero | 1920×1080 or wider, often a silent loop | 6 to 20 s | small file (H.264 or VP9 at modest bitrate), loopable end |
| Presentation or event screen | the screen's native size, often 16:9 or 21:9 | any | test on the screen; no platform UI |

## Upload limits the platforms document

Upload limits come from each platform's own documentation where a page could be read on 2026-10-31. These are API
and help-page figures; an account or app can differ, so look at the upload screen before a launch.

| Platform | Documented | Not confirmed |
|---|---|---|
| TikTok | Content Posting API: MP4 (recommended), WebM or MOV; H.264 (recommended), H.265, VP8 or VP9; 23 to 60 fps; 360 to 4096 px per side; up to 4 GB; up to 10 minutes through that API, and each creator's cap comes from `max_video_post_duration_sec` | app uploads: third-party guides report up to 60 minutes from the camera roll and disagree on file size |
| Instagram Reels | Graph API publishing: MOV or MP4 with the moov atom at the front and no edit lists; H.264 or HEVC, progressive, closed GOP, 4:2:0; AAC at 48 kHz or lower; 23 to 60 fps; 9:16 recommended; 3 s to 15 min; up to 300 MB | app uploads: third-party guides report 20 minutes |
| X | X API changelog, 1 Sep 2026 (https://docs.x.com/changelog): Post video up to 20 minutes and 8 GB, Premium or verified up to 125 minutes and 16 GB; the older 140 s and 512 MB is the Direct Message limit (10 minutes and 1 GB with Premium). Media best practices page: H.264 High, AAC-LC, YUV 4:2:0, 60 fps or less; subscribed users get 1080p playback and unsubscribed users 720p | X's help page reportedly still says 140 s. Premium videos of 2 to 4 hours at 720p: confirmed by search results only. The same best practices page says "must be between `32x32` and `1280x1024`", which conflicts with its own 1080p line: test a real upload before relying on either |

Instagram's moov rule is why web and social files get `-movflags +faststart` after the render. Every 24, 25, 30 or
60 fps render sits inside the 23 to 60 fps window; 29.97 does too.

## Safe zones

Safe zones are the margins kept clear of crops and app interface.

- **Every format:** content inside the 90% action-safe box; key text inside the 80% title-safe box.
- **Vertical 1080×1920:** keep the top 200 px and the bottom 250 to 400 px free of key text and calls to action, and
  about 120 px on the right where like and share buttons sit. The window from y=200 to y=1670 is safe on all major
  apps; captions go about 600 to 700 px from the bottom.
- **Reels shown in a 4:5 feed:** keep the essential frame inside the centre 1080×1350.
- `npx hyperframes check --caption-zone "x0=0;y0=.82;x1=1;y1=1;severity=error"` reserves a band and fails text placed
  in it; mark intended copy with `data-layout-allow-caption-zone`.

## Adapting landscape to vertical

Adapting landscape to vertical rebuilds the layout instead of cropping it.

- Side-by-side columns become a stack; a three-column grid becomes one column of three rows.
- A wide left-anchored headline becomes a full-width, stacked headline; split screens become top and bottom.
- Supporting visuals become a full-bleed background or move below the text.
- Type scales by role against landscape: display and headlines to about 0.8, because the frame is only 1080 wide; body
  by about 1.15 (32 to 40 px) and captions and labels by about 1.4 (28 to 36 px), for the phone in the hand.
- Holds shorten 15 to 20% and transitions 20 to 30%; drop one or two scenes for the same length.
- Swap effects that need width (side-by-side splits, wide lens warps) for scale, push and whip moves.

Per-orientation layout, type scales and patterns: [references/orientations.md](references/orientations.md).

## One composition, several formats

One composition, several formats is easiest with layout that depends on the canvas, not fixed pixels: content
containers that fill their scene with padding, sizes from `fitTextFontSize`, and a variable or class for orientation.

```html
<html data-composition-variables='[{"id":"format","type":"enum","label":"Format","default":"landscape",
  "options":[{"value":"landscape","label":"16:9"},{"value":"portrait","label":"9:16"}]}]'>
```

```js
const { format } = window.__hyperframes.getVariables();
document.documentElement.dataset.format = format;   /* CSS: [data-format="portrait"] .grid { grid-template-columns: 1fr; } */
```

The root's `data-width` and `data-height` cannot come from a variable, so keep one root file per canvas (for example
`index.html` and `index-vertical.html` mounting the same scene files) and render each:

```bash
npx hyperframes render -o renders/landscape.mp4
npx hyperframes render -c index-vertical.html --variables '{"format":"portrait"}' -o renders/vertical.mp4
```

## Frame rate choice

Frame rate choice: 30 fps for social and web; 24 for a film look; 25 for PAL regions; 29.97 (`30000/1001`) to match
NTSC camera footage; 60 for screen recordings and fast UI motion (double the render time). Match the footage you cut in.

## Verify the format

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 renders/vertical.mp4
npx hyperframes check --caption-zone "x0=0;y0=.82;x1=1;y1=1;severity=error" --json   # nothing key under the app bar
npx hyperframes snapshot --review                                                    # the phone sheet, at 360 px wide
```

Check the first line against the table, and read the phone sheet for anything under the right-hand buttons.

## Checklist

- [ ] Platform and canvas decided before the first scene.
- [ ] Length fits the platform's sweet spot; the hook fits its budget.
- [ ] Key text, captions and calls to action inside the platform's safe zone.
- [ ] Vertical versions rebuilt, not cropped; display down to about 0.8, body and captions up.
- [ ] Muted platforms carry the message in on-screen text and burned-in captions.
- [ ] Frame rate matches footage and target.

## Gotchas

- **Symptom:** The call to action sits under the like button. **Cause:** Vertical bottom and right margins were
  ignored. **Fix:** keep it inside y=200 to y=1670 and clear of the right 120 px.
- **Symptom:** Reels are cropped in the feed. **Cause:** Essential content sits outside the centre 4:5 area. **Fix:**
  keep it inside the centre 1080×1350.
- **Symptom:** A 4K render looks soft. **Cause:** The composition was built at 1080p and upscaled bitmaps. **Fix:**
  supersample with `--resolution` and use images at the larger size.
- **Symptom:** Banding after the platform's re-encode. **Cause:** Dark gradients at a low bitrate. **Fix:** add grain,
  raise the bitrate, avoid near-black ramps.

## Anti-patterns

| Do not | Do instead |
|---|---|
| cropping 16:9 to make a vertical version | rebuild the layout: columns become a stack |
| fixed pixel layouts in a multi-format film | containers that fill the scene, and `fitTextFontSize` |
| treating a third-party limit as a promise | check the upload screen before a launch |
| sound-dependent copy on muted feeds | on-screen text and burned-in captions |

## References

- [references/orientations.md](references/orientations.md): layout philosophy, safe areas, type scales and patterns for 9:16, 16:9, 4:5, 1:1 and 21:9, and multi-format projects.

## See also

`render-and-export`, `hyperframes-captions`, `video-thumbnails`, `motion-design`, `hyperframes-cli`.
