---
title: Subtitle formats and delivery
author: MOZGII, Inc.
lang: en
---

# Subtitle formats and delivery

Subtitle formats are the text files players read beside a video: SubRip (SRT), WebVTT (VTT) and Advanced SubStation
(ASS). This page covers what each looks like, the reading-speed rules broadcasters use, and the FFmpeg commands that
attach a sidecar to an MP4 or burn it into the picture.

## Contents

The sections of this page:

- SubRip SRT
- WebVTT
- ASS for styled burn-in
- Reading speed and line rules
- Writing sidecars from a transcript
- Muxing a subtitle track into MP4 or MKV
- Burning subtitles into the picture
- What platforms accept

## SubRip SRT

SubRip (SRT) is the most widely accepted subtitle format: numbered cues, `HH:MM:SS,mmm` times with a comma, a blank
line between cues, UTF-8 text.

```
1
00:00:00,400 --> 00:00:02,100
Every frame is a function of time.

2
00:00:02,300 --> 00:00:04,800
So every render is the same.
```

## WebVTT

WebVTT is the web's subtitle format, read by the HTML `<track>` element and most streaming players. It starts with a
`WEBVTT` header, uses a dot in times, and allows cue settings for position.

```
WEBVTT

00:00:00.400 --> 00:00:02.100 line:85% align:center
Every frame is a function of time.

00:00:02.300 --> 00:00:04.800
So every render is the same.
```

## ASS for styled burn-in

ASS (Advanced SubStation Alpha) carries fonts, colours, outlines and positions per style, which makes it the usual
input for styled burn-in with FFmpeg's `subtitles` filter (libass). Players rarely accept it as a delivery format;
convert to SRT or VTT for sidecars. In HyperFrames, styled captions are better built as HTML (`hyperframes-captions`),
so ASS matters mainly when a pipeline outside HyperFrames burns subtitles.

## Reading speed and line rules

Reading speed and line rules come from broadcast subtitling guidelines (the BBC and Netflix timed-text style guides
are the common references):

- at most two lines per cue, about 37 to 42 characters per line;
- reading speed about 15 to 17 characters a second for adults (lower for children's content);
- a cue lasts at least about 5/6 of a second and at most about 7 seconds;
- a short gap (2 frames or more) between consecutive cues so the change is visible;
- break lines at natural phrase boundaries, never between an article and its noun.

Burned-in social captions are shorter by design (2 to 6 words per group) and are not bound by these rules.

## Writing sidecars from a transcript

Writing sidecars from a transcript uses the same word timings as the burned-in captions:

```bash
npx hyperframes transcribe assets/voice.wav --model small.en --to srt --output renders/final.srt
npx hyperframes transcribe assets/voice.wav --model small.en --to vtt --output renders/final.vtt
```

Shift every cue by the voiceover's `data-start` when the voice does not begin at 0. FFmpeg converts between formats:
`ffmpeg -i final.srt final.vtt`.

## Muxing a subtitle track into MP4 or MKV

Muxing adds a subtitle track that viewers can switch on, without re-encoding the video.

```bash
# MP4 needs the mov_text codec
ffmpeg -i final.mp4 -i final.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=eng final-subs.mp4
# MKV keeps SRT or ASS as they are
ffmpeg -i final.mp4 -i final.srt -map 0 -map 1 -c copy final-subs.mkv
```

## Burning subtitles into the picture

Burning subtitles into the picture re-encodes the video with the text drawn in, for platforms that ignore sidecars.

```bash
ffmpeg -i final.mp4 -vf "subtitles=final.srt:force_style='FontName=Inter,FontSize=22,Outline=2'" \
  -c:v libx264 -crf 18 -preset slow -c:a copy final-burned.mp4
```

The filter needs an FFmpeg built with libass (`ffmpeg -filters | grep subtitles`).

## What platforms accept

What platforms accept as caption uploads, as a rule of thumb: YouTube takes SRT, VTT and several other formats;
LinkedIn takes SRT; Facebook takes SRT; Vimeo takes SRT and VTT. TikTok, Instagram Reels and YouTube Shorts rely on
auto-captions or burned-in text, so burn captions in for those. Check each platform's help pages before a launch, as
upload options change.
