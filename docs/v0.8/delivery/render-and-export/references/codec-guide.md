---
title: Codecs, containers and bitrates for video delivery
author: MOZGII, Inc.
lang: en
---

# Codecs, containers and bitrates for video delivery

Codecs compress the picture; containers hold the picture, sound and subtitles in one file. This page compares the
codecs a programmatic video is delivered in, explains pixel formats and alpha, gives bitrate guides by resolution, and
covers colour tags and HDR.

## Contents

The sections of this page:

- Codecs compared
- Pixel formats and chroma subsampling
- Transparent video
- Bitrate guides
- Rate control: CRF, bitrate and caps
- Colour tags and range
- HDR delivery
- GIF and animated images

## Codecs compared

Codecs compared for delivery:

| Codec | Container | Strength | Weakness | Use |
|---|---|---|---|---|
| H.264 (AVC) | MP4 | plays everywhere | larger than newer codecs at equal quality | default delivery |
| H.265 (HEVC) | MP4, MOV | about 30 to 50% smaller; 10-bit; HDR | patchy browser support | Apple devices, HDR, archives |
| VP9 | WebM | alpha channel; good web support | slow encodes | transparent overlays for the web |
| AV1 | MP4, WebM | smallest files | slow encodes; older hardware cannot decode | large-scale web streaming |
| ProRes 422 HQ, 4444 | MOV | edit-friendly, near lossless; 4444 has alpha | very large files | hand-off to editors and colourists |
| PNG sequence | folder | lossless RGBA per frame | huge, no audio | compositing |

## Pixel formats and chroma subsampling

Pixel formats and chroma subsampling decide how colour is stored. `yuv420p` (8-bit, 4:2:0) is what every player
accepts: colour is stored at half resolution in both directions, so thin saturated lines (a 1 px red rule) smear.
Make coloured rules 3 px or more, or deliver `yuv444p` or ProRes 4444 to editors. 10-bit (`yuv420p10le`) removes most
banding but needs HEVC, AV1 or ProRes and a player that handles it.

## Transparent video

Transparent video needs a codec with an alpha channel.

| Need | Format | Command |
|---|---|---|
| Overlay in a web page or another HyperFrames composition | VP9 WebM | `npx hyperframes render --format webm` |
| Overlay in an editing app | ProRes 4444 MOV | `npx hyperframes render --format mov` |
| Frames for compositing | PNG sequence | `npx hyperframes render --format png-sequence` |

The composition needs a transparent ground (no full-frame background). HEVC with alpha exists on Apple platforms but
is not a portable delivery format. GIF has only 1-bit transparency.

## Bitrate guides

Bitrate guides for H.264 SDR uploads, in line with what large video platforms publish for upload quality (check the
platform's current help page):

| Resolution | 24 to 30 fps | 48 to 60 fps |
|---|---|---|
| 1280×720 | 5 Mbps | 7.5 Mbps |
| 1920×1080 | 8 Mbps | 12 Mbps |
| 2560×1440 | 16 Mbps | 24 Mbps |
| 3840×2160 | 35 to 45 Mbps | 53 to 68 Mbps |

Audio for uploads: AAC-LC, 48 kHz, stereo, 192 to 384 kbps. Motion graphics with flat colour compress well; noisy
footage and grain need the higher end. For a website hero loop, 2 to 4 Mbps at 1080p is usually enough.

## Rate control: CRF, bitrate and caps

Rate control decides how the encoder spends bits.

- **CRF** (`--crf 18`): constant quality; the file size varies with content. Best for uploads, where the platform
  re-encodes anyway.
- **Target bitrate** (`--video-bitrate 10M`): predictable size; quality varies. Use when a spec names a bitrate.
- **Capped CRF** (`--crf 18 --max-bitrate 20M --buffer-size 40M`): constant quality with a ceiling, for streaming.
- **Keyframe interval** (`--keyframe-interval 2`): a keyframe at least every 2 s, which some ad and streaming specs
  require and which makes seeking smoother.

## Colour tags and range

Colour tags and range tell players how to interpret pixel values. Web and HD video is BT.709 primaries, transfer and
matrix, limited ("TV") range. Untagged or mis-tagged files look washed out or crushed on some players. Check with
ffprobe (`color_space`, `color_primaries`, `color_transfer`, `color_range`) and fix tags without re-encoding where the
pixels are already right:

```bash
ffmpeg -i in.mp4 -c copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0 out.mp4
```

## HDR delivery

HDR delivery happens automatically when HDR footage is in the composition and the output is MP4, or with `--hdr`;
`--sdr` forces SDR. HDR needs 10-bit HEVC with PQ or HLG transfer, a platform that accepts it, and screens that show
it. Mixed HDR and SDR material should be tested on a real HDR display. Shader transitions and some treatments drop
the root background colour with HDR media; paint it on a full-bleed child.

## GIF and animated images

GIF and animated images suit docs and pull requests, not delivery. HyperFrames' GIF output uses a two-pass palette,
caps at 30 fps (15 is a good choice), has no audio and 1-bit transparency. A silent looping MP4 or WebM is usually
five to ten times smaller at better quality wherever video is allowed.
