---
name: render-and-export
description: Renders and exports finished HyperFrames videos for delivery - choosing format and codec (H.264 MP4, HEVC, VP9 or ProRes 4444 with alpha, GIF, PNG sequence, HLS), quality presets, CRF and bitrate caps, frame rate, 4K supersampling, HDR or SDR, colour tagging, audio format and loudness, then verifying the file with ffprobe and finishing with FFmpeg (faststart, trims, concat, subtitle tracks, platform re-encodes). Use when rendering a final file, when a platform rejects an upload, when an export looks banded, washed out, too large or out of sync, or when transparent video is needed.
metadata:
  tags:
  - render
  - export
  - ffmpeg
  - codecs
  - h264
  - prores
  - webm
  - alpha
  - hls
  - delivery
---

# Rendering and exporting video

Rendering and exporting turns an approved composition into a file a platform or person can use. HyperFrames renders
with `npx hyperframes render` (Chrome captures frames, FFmpeg encodes); FFmpeg and ffprobe then check and finish the
file. Checked against HyperFrames CLI 0.8.223 and FFmpeg 7 to 9 (the commands use options stable across those versions).

## When to use this skill

Use this skill for the delivery render, transparent overlays for an editor, GIFs for docs, streaming packages, platform
re-encodes, and for exports that look banded, washed out, too large, or out of sync.

## Step 0: read the encoders on this machine

```bash
npx hyperframes --version
ffmpeg -version | head -1                                  # 7 to 9 for the commands below
ffmpeg -hide_banner -encoders | grep -E 'h264_|hevc_|libvpx-vp9|prores'   # what `--gpu` and each format can use
```

`render --start` and `--end` need CLI 0.8.222 or later.

## Pick the output

Pick the output by where the file goes.

| Destination | Command | Result |
|---|---|---|
| Upload to a platform, send to a person | `render --quality delivery -o final.mp4` | H.264 MP4, 8-bit 4:2:0 |
| Transparent overlay for a web page | `render --format webm -o overlay.webm` | VP9 with alpha |
| Transparent overlay for an editor (Premiere, Resolve, Final Cut) | `render --format mov -o overlay.mov` | ProRes 4444 with alpha |
| Compositing in After Effects, Nuke, Fusion | `render --format png-sequence -o frames/` | RGBA PNG per frame |
| README, docs, pull request | `render --format gif --fps 15 -o demo.gif` | palette GIF, no audio |
| Streaming on your own site | `render --format hls -o stream/` | `master.m3u8` and TS segments |
| Reproducible output across machines | `render --docker --strict -o final.mp4` | byte-identical frames |

## Quality presets and encoder settings

Quality presets cover most needs; encoder flags override them for a delivery spec.

| Preset | Use |
|---|---|
| `draft` | fast iteration; visibly compressed |
| `looks` (default) | first real encode, CRF 16 |
| `delivery` (same as `high`) | final files |

```bash
npx hyperframes render --quality delivery --crf 18 -o final.mp4                       # quality target
npx hyperframes render --video-bitrate 12M --keyframe-interval 2 -o final.mp4         # fixed bitrate, GOP 2 s
npx hyperframes render --crf 18 --max-bitrate 20M --buffer-size 40M -o final.mp4      # capped CRF for streaming
```

CRF for H.264: 16 to 18 looks transparent, 20 to 23 is web quality, each +6 roughly halves the size. `--crf` and
`--video-bitrate` exclude each other. Codec trade-offs and bitrate tables:
[references/codec-guide.md](references/codec-guide.md).

## Size, frame rate and HDR

Size, frame rate and HDR are render flags too.

- `--fps 60` doubles render time; `--fps 30000/1001` gives NTSC 29.97. Default: the root's `data-fps`, else 30.
- `--resolution 4k` supersamples a 1920×1080 composition to 3840×2160 with Chrome's device scale factor: vector text
  and shapes become sharp at 4K; bitmaps only as sharp as their source. The aspect must match; not with `--hdr`.
- `--hdr` forces HDR MP4 output; `--sdr` forces SDR when sources are HDR.

## Verify every render

Verify every render before calling it done: the file exists, is not empty, has the expected streams and duration,
and looks right when decoded.

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries \
  stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,sample_rate,channels -of json renders/final.mp4
ffmpeg -v error -i renders/final.mp4 -f null - && echo "decodes cleanly"
ffmpeg -v error -ss 4.2 -i renders/final.mp4 -frames:v 1 -y check-4.2s.png      # look at decoded frames
```

The duration must equal the root's `data-duration`. More checks and a script: `render-testing`.

## Worked example: a five-second card to a checked web file

This walkthrough takes a composition to a file ready for a web page, and stops at the first check that fails. Start
with a one-file project:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0f1115;
            display: flex; align-items: center; justify-content: center; font-family: Inter, Arial, sans-serif; }
    #card { font-size: 120px; font-weight: 800; color: #f4f1ea; }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="5" data-width="1920" data-height="1080">
    <div id="card">Books done</div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#card", { scale: 0.94 }, { scale: 1, duration: 5, ease: "none" }, 0);   // on screen from frame 0
    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
```

Then render, finish and prove the file. `want` is the stream the destination needs, and 5 is the root's `data-duration`:

```bash
#!/usr/bin/env bash
set -euo pipefail
npx hyperframes render --quality delivery --crf 18 -o renders/final.mp4
ffmpeg -v error -y -i renders/final.mp4 -c copy -movflags +faststart renders/final-web.mp4

f=renders/final-web.mp4 want="h264,1920,1080,yuv420p"
got=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt -of csv=p=0 "$f")
[ "$got" = "$want" ] || { echo "wrong stream: $got"; exit 1; }

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
awk -v d="$dur" 'BEGIN { exit !(d >= 4.95 && d <= 5.05) }' || { echo "wrong length: $dur"; exit 1; }

ffmpeg -v error -i "$f" -f null -
atoms=$(ffprobe -v trace "$f" 2>&1 | grep -oE "type:'(moov|mdat)'")
[ "${atoms%%$'\n'*}" = "type:'moov'" ] || { echo "index is not at the front"; exit 1; }
echo "ready: $f"
```

When a check stops the script, its message names the failed property; the gotchas below say what causes each one.

## Finishing with FFmpeg

Finishing with FFmpeg covers jobs after the render: moving the index to the front for web playback, trims, joining,
adding subtitle tracks, loudness, platform re-encodes and posters. Recipes:
[references/ffmpeg-recipes.md](references/ffmpeg-recipes.md).

```bash
ffmpeg -i final.mp4 -c copy -movflags +faststart final-web.mp4     # starts playing before it fully downloads
```

## Audio in the export

Audio in the export is AAC in MP4. Target about −14 LUFS integrated for streaming and social (−16 for some podcasts
and spoken content), true peak at or below −1 dBTP. Set levels in the composition with
`npx hyperframes normalize-audio` before rendering, and measure the rendered file (see `audio-sync`).

## Checklist

- [ ] Format and codec chosen for the destination.
- [ ] `delivery` quality or an explicit CRF or bitrate for the final file.
- [ ] Frame rate matches footage and platform; 4K via supersampling when needed.
- [ ] ffprobe shows the expected codec, pixel format, size, frame rate, audio and duration.
- [ ] The file decodes without errors; decoded frames looked at.
- [ ] Faststart applied for web delivery; loudness measured.

## Gotchas

- **Symptom:** Washed out or too dark on some players. **Cause:** Colour tags are missing, or the video is full range.
  **Fix:** tag BT.709 limited range (see the FFmpeg recipes).
- **Symptom:** Banding in dark gradients. **Cause:** An 8-bit encode of a smooth ramp. **Fix:** add grain, raise the
  bitrate, or deliver 10-bit HEVC or ProRes to editors.
- **Symptom:** A transparent WebM shows black in some apps. **Cause:** Only some players read VP9 alpha. **Fix:** give
  editors ProRes 4444.
- **Symptom:** A huge GIF. **Cause:** Too many frames for the format. **Fix:** lower `--fps` (15), shorten it, or ship
  an MP4 or WebM loop instead.
- **Symptom:** A platform rejects the file. **Cause:** Odd dimensions or a frame rate it does not accept. **Fix:** use
  even sizes and standard rates.
- **Symptom:** Audio drifts out of sync after re-encoding. **Cause:** A variable frame rate from another tool.
  **Fix:** re-encode with `-fps_mode cfr`.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `--crf` with `--video-bitrate` | one or the other; they exclude each other |
| trusting the preview for delivery | decode frames from the file and look at them |
| `--hdr` with `--resolution` | one of them; they cannot combine |
| uploading without `+faststart` | move the index to the front for web delivery |

## References

- [references/codec-guide.md](references/codec-guide.md): codecs and containers, pixel formats, alpha, bitrate guides by resolution, colour and HDR.
- [references/ffmpeg-recipes.md](references/ffmpeg-recipes.md): faststart, trims, concat, audio replace and mix, loudness, subtitles, posters, GIF and platform re-encodes.

## See also

`hyperframes-cli`, `render-testing`, `platform-formats`, `audio-sync`, `render-performance`.
