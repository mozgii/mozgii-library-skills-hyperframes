---
title: FFmpeg recipes for finishing video
author: MOZGII, Inc.
lang: en
---

# FFmpeg recipes for finishing video

FFmpeg recipes for finishing video are the commands used after a render: preparing a file for the web, trimming and
joining, replacing or mixing audio, measuring and normalising loudness, adding subtitles, making posters and GIFs, and
re-encoding for a platform. Every command writes a new file; keep the original render.

## Contents

The sections of this page:

- Inspecting a file
- Web playback with faststart
- Trimming without and with re-encoding
- Joining clips
- Replacing and mixing audio
- Measuring and normalising loudness
- Adding subtitle tracks
- Posters, thumbnails and contact sheets
- High-quality GIF
- Re-encoding for a platform
- Scaling and padding to a new aspect

## Inspecting a file

Inspecting a file lists its streams and their properties.

```bash
ffprobe -v error -show_format -show_streams -of json final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt,codec_name -of csv=p=0 final.mp4
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4
```

## Web playback with faststart

Web playback with faststart moves the MP4 index (the `moov` atom) to the front so playback starts before the whole
file downloads. It copies streams, so it is fast and lossless.

```bash
ffmpeg -i final.mp4 -c copy -movflags +faststart final-web.mp4
```

## Trimming without and with re-encoding

Trimming without re-encoding is instant but cuts on keyframes; re-encoding cuts on the exact frame.

```bash
ffmpeg -ss 2 -to 12 -i final.mp4 -c copy cut-fast.mp4                                   # keyframe-accurate
ffmpeg -i final.mp4 -ss 2 -to 12 -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k cut-exact.mp4   # frame-accurate
```

For HyperFrames projects, a different length is usually better as a change to the root `data-duration` and a new
render.

## Joining clips

Joining clips with the concat demuxer needs identical codecs, sizes and frame rates; the filter joins anything.

```bash
printf "file '%s'\n" intro.mp4 main.mp4 outro.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -c:a aac joined-reencoded.mp4
```

## Replacing and mixing audio

Replacing and mixing audio keeps the video stream as is.

```bash
ffmpeg -i final.mp4 -i new-mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest replaced.mp4
ffmpeg -i final.mp4 -i music.mp3 -filter_complex "[1:a]volume=0.2[m];[0:a][m]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac mixed.mp4
ffmpeg -i final.mp4 -i music.mp3 -filter_complex \
  "[1:a][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[duck];[0:a][duck]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac ducked.mp4                    # music ducks under the voice
```

Inside a HyperFrames project, prefer `data-volume`, fades and `normalize-audio` so the mix renders with the picture.

## Measuring and normalising loudness

Measuring and normalising loudness uses the EBU R128 `loudnorm` filter. A first pass measures; a second applies the
measured values for an accurate, linear result.

```bash
ffmpeg -hide_banner -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=summary -f null - 2>&1 | tail -12
ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=-19.2:measured_TP=-3.1:measured_LRA=6.5:measured_thresh=-29.4:offset=0.3:linear=true \
  -c:v copy -c:a aac -b:a 256k loud-14.mp4
```

Replace the `measured_*` and `offset` values with those the first pass printed.

## Adding subtitle tracks

Adding subtitle tracks gives players a switchable track; burning in draws text into the picture.

```bash
ffmpeg -i final.mp4 -i final.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=eng final-subs.mp4
ffmpeg -i final.mp4 -vf "subtitles=final.srt" -c:v libx264 -crf 18 -c:a copy final-burned.mp4
```

## Posters, thumbnails and contact sheets

Posters, thumbnails and contact sheets come from decoded frames.

```bash
ffmpeg -ss 3.5 -i final.mp4 -frames:v 1 -q:v 2 poster.jpg
ffmpeg -i final.mp4 -vf "fps=1,scale=480:-1,tile=6x4" -frames:v 1 contact.png        # one frame a second
```

## High-quality GIF

A high-quality GIF uses a generated palette; HyperFrames' own `--format gif` does this for you.

```bash
ffmpeg -i final.mp4 -vf "fps=15,scale=960:-1:flags=lanczos,palettegen=stats_mode=diff" -y palette.png
ffmpeg -i final.mp4 -i palette.png -lavfi "fps=15,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4" -y demo.gif
```

## Re-encoding for a platform

Re-encoding for a platform matches a published spec: constant frame rate, `yuv420p`, BT.709 tags, AAC 48 kHz.

```bash
ffmpeg -i final.mp4 -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 18 -preset slow -r 30 -fps_mode cfr \
  -g 60 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart upload.mp4
ffmpeg -i final.mov -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le -c:a pcm_s16le master-4444.mov   # ProRes 4444 for editors
ffmpeg -i final.mp4 -c:v libvpx-vp9 -crf 32 -b:v 0 -row-mt 1 -c:a libopus web.webm
```

## Scaling and padding to a new aspect

Scaling and padding to a new aspect is a last resort; rebuilding the layout for the new canvas looks far better
(`platform-formats`).

```bash
ffmpeg -i final.mp4 -vf "scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:color=0x0b0d12" -c:a copy vertical-letterbox.mp4
ffmpeg -i final.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy vertical-centre-crop.mp4
```
