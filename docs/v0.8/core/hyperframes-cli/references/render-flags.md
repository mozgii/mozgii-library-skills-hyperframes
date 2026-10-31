---
title: HyperFrames render flags and targets
author: MOZGII, Inc.
lang: en
---

# HyperFrames render flags and targets

HyperFrames render flags control the output file of `npx hyperframes render`: format, quality, frame rate, size,
encoder settings, workers and strictness. This page lists them as of CLI 0.8.223 and covers the hosted and
self-hosted cloud targets.

## Contents

The sections of this page:

- Output, format and quality flags: MP4, transparent WebM or MOV, GIF
- Encoder flags
- Speed and environment flags
- Strictness and variables flags
- Reading the render summary line
- Rendering in the cloud, on Lambda or on Cloud Run

## Output, format and quality flags: MP4, transparent WebM or MOV, GIF

Output, format and quality flags choose what file is written: MP4, a transparent WebM or MOV overlay, a GIF, a PNG
sequence or HLS.

| Flag | Values | Default | Notes |
|---|---|---|---|
| `dir` (positional) | path | current folder | the project |
| `--composition`, `-c` | file | `index.html` | render one scene file |
| `--output`, `-o` | path | `renders/<project>_<date>_<time>.<ext>` inside the project folder, wherever you run it from (0.8.219 on) | pass it for a stable name |
| `--format` | `mp4`, `webm`, `mov`, `gif`, `png-sequence`, `hls` | `mp4` | WebM and MOV keep transparency |
| `--quality` | `draft`, `looks`, `delivery` (also `standard`, `high`) | `looks` | `looks` is CRF 16; `delivery` equals `high` |
| `--start`, `--end` | seconds | whole film | render only that span as an MP4 that starts at 0 and carries the span's audio (0.8.222 on); MP4 only, SDR only, at exactly 24, 25, 30 or 60 fps |
| `--fps` | any rate from 1 to 240, or a fraction like `30000/1001` | the root's `data-fps`, or 30 when it has none | 60 fps doubles render time |
| `--resolution` | `landscape`, `portrait`, `square`, `landscape-4k`, `portrait-4k`, `square-4k`, aliases `1080p`, `4k`, `uhd` | none | supersamples through Chrome's device scale factor; the aspect has to match and the scale has to be a whole number; cannot combine with `--hdr` |
| `--gif-loop` | 0 to 65535 | 0 (forever) | GIF only |
| `--hls-segment-seconds` | 1 to 60 | 4 | HLS only; also locks the GOP so each segment starts on a keyframe |

Format notes:

- A transparent overlay video exports with `--format webm` (VP9 with alpha) or `--format mov` (ProRes 4444 with
  alpha): WebM and MOV keep transparency.
- `gif` uses a two-pass palette, caps at 30 fps (15 is a good choice), has no audio and only 1-bit transparency.
- `png-sequence` writes RGBA frames to a folder for compositing in After Effects, Nuke or Fusion.
- `hls` writes `master.m3u8`, video and audio playlists and MPEG-TS segments; SDR only, no `--gpu`, not on Lambda or
  Cloud Run.

## Encoder flags

Encoder flags override the quality preset for MP4 delivery specs.

| Flag | Example | Notes |
|---|---|---|
| `--crf` | `18` | 0 to 51, lower is better; not with `--video-bitrate` |
| `--video-bitrate` | `10M`, `5000k` | target bitrate; not with `--crf` |
| `--max-bitrate` | `8M` | MP4 only: peak cap on top of the CRF target |
| `--buffer-size` | `16M` | MP4 only, needs `--max-bitrate` (default twice it) |
| `--keyframe-interval` | `2` | MP4 only: the longest gap between keyframes, in seconds |
| `--hdr`, `--sdr` | flag | force HDR (MP4 only) or SDR output |

## Speed and environment flags

Speed and environment flags trade time, memory and reproducibility.

| Flag | Default | Notes |
|---|---|---|
| `--workers` | `auto` | each worker is a Chrome of about 256 MB |
| `--gpu` | off | hardware FFmpeg encode: NVENC, VideoToolbox, VAAPI or QSV |
| `--browser-gpu`, `--no-browser-gpu` | auto on your machine, off inside Docker | lets Chrome and WebGL capture use the host's GPU |
| `--docker` | off | byte-identical output across hosts |
| `--browser-timeout` | 60 s | navigation timeout for heavy entry pages |
| `--quiet` | off | less output |

## Strictness and variables flags

Strictness and variables flags make renders fail loudly in CI.

| Flag | Effect |
|---|---|
| `--strict` | fail on lint errors |
| `--strict-all` | fail on lint errors and warnings |
| `--variables '{...}'`, `--variables-file vars.json` | override declared variables |
| `--strict-variables` | fail on undeclared keys or wrong types |
| `--batch rows.json` | one render per row; see the `hyperframes` variables reference |

## Reading the render summary line

The second line of the summary tells you how frames were captured, which GPU mode ran and how long each stage took, for example
`beginframe capture · software gpu · compile 0.7s · setup 1.1s · capture 8.1s · encode 5.8s`. `capture` is the frame
loop; `setup` is calibration and session start; `encode (during capture)` says encoding ran at the same time as
capture, so its seconds are already inside the total. `screenshot capture` with `software gpu` on Linux is the slow path: BeginFrame did not run
(it needs chrome-headless-shell and no `--resolution` upscale).

## Rendering in the cloud, on Lambda or on Cloud Run

Cloud rendering moves the work off the machine. Pick by who must own the infrastructure.

```bash
npx hyperframes auth login                         # hosted rendering: sign in (again once after upgrading to 0.8.218+)
npx hyperframes cloud render . --dry-run --json    # check the upload (limit about 200 MB)
npx hyperframes cloud render --quality high --fps 60
npx hyperframes cloud list && npx hyperframes cloud get <render-id>

npx hyperframes lambda deploy                      # your AWS account: Lambda, Step Functions, S3
npx hyperframes lambda sites create ./my-project
npx hyperframes lambda render ./my-project --width 1920 --height 1080 --wait
npx hyperframes lambda destroy

npx hyperframes cloudrun deploy --project <gcp-project> --region us-central1   # your GCP project
npx hyperframes cloudrun render ./my-project --width 1920 --height 1080 --wait
```

- Lambda and Cloud Run accept only 24, 25, 30 and 60 fps and no HLS output.
- For a project near the upload limit, list what is sent with `--dry-run --json` and exclude build leftovers with a
  `.hyperframesignore`; never drop an asset only because it is large.
- Lambda is not worth its deploy overhead for one short render.
