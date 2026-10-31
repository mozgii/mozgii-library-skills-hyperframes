---
title: Transcription models and transcript quality
author: MOZGII, Inc.
lang: en
---

# Transcription models and transcript quality

Transcription models turn speech into words with timings; transcript quality decides whether captions make sense.
This page covers Whisper model sizes, the language rule, accepted input formats, the quality check every transcript
needs, and importing results from hosted APIs.

## Contents

The sections of this page:

- Whisper model sizes
- The language rule for Whisper
- Accepted transcript formats
- Transcript quality check
- Unspaced scripts
- Importing from hosted APIs

## Whisper model sizes

Whisper model sizes trade speed for accuracy.

| Model | Size | Speed | Use |
|---|---|---|---|
| `tiny`, `tiny.en` | 75 MB | fastest | smoke tests |
| `base`, `base.en` | 142 MB | fast | short, clean clips |
| `small`, `small.en` | 466 MB | moderate | most speech |
| `medium`, `medium.en` | 1.5 GB | slow | speech over music, noisy rooms |
| `large-v3` | 3.1 GB | slowest | production quality, many languages |

## The language rule for Whisper

The language rule for Whisper: models ending in `.en` translate any speech into English, silently.

1. Known English: `--model small.en` (`medium.en` over music).
2. Known other language: `--model small --language <iso-code>`, no `.en`.
3. Unknown language: `--model small` and let Whisper detect it.

`--language` also drops segments in other languages from mixed audio.

## Accepted transcript formats

Accepted transcript formats are normalised by `npx hyperframes transcribe <file>` into one flat word array.

| Format | Extension | Word-level |
|---|---|---|
| whisper.cpp JSON | `.json` | yes |
| OpenAI-style verbose JSON with word timestamps | `.json` | yes |
| A normalised word array | `.json` | yes |
| SubRip subtitles | `.srt` | no, phrase-level |
| WebVTT subtitles | `.vtt` | no, phrase-level |

```json
[
  { "id": "w0", "text": "Ship", "start": 0.12, "end": 0.41 },
  { "id": "w1", "text": "faster.", "start": 0.45, "end": 0.98 }
]
```

Phrase-level SRT and VTT work for subtitles but cannot drive per-word effects such as karaoke.

## Transcript quality check

The transcript quality check is reading the words before building captions. A transcript fails when:

- more than 20% of entries are `♪` or `�` tokens;
- it holds nonsense words that nobody said;
- "Thank you." or a repeated line appears over silence at the end (a Whisper habit);
- many words span under 0.05 s (alignment broke).

On failure, retry one size up (`medium.en` after `small.en`); if that fails, ask for lyrics or a script, or use a
hosted API. Then clean the array:

```js
const words = raw.filter((w) =>
  w.text && w.text.trim() &&
  !/^[♪�♪-♯]+$/.test(w.text) &&
  !(/^(huh|uh|um|ah|oh)$/i.test(w.text) && w.end - w.start < 0.1));
```

Any word whose start time falls inside the closing silence is invented; remove it. FFmpeg finds the silences:

```bash
ffmpeg -hide_banner -i assets/voice.wav -af silencedetect=noise=-35dB:d=0.6 -f null - 2>&1 | grep silence_
```

Real speech usually sits around −16 to −26 dB, so −35 dB separates it from room tone.

## Unspaced scripts

Unspaced scripts (Chinese, Japanese, Thai) come back from local models as one long "word" per sentence, sometimes in
the wrong character set (Traditional for Simplified). Break each segment into short phrases, share its duration
among them in proportion to their length in characters, and compare the characters with the speech.

## Importing from hosted APIs

Importing from hosted APIs gives better accuracy on hard audio. Request word timestamps, save the JSON, import it:

```bash
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file=@assets/voice.mp3 -F model=whisper-1 \
  -F response_format=verbose_json -F "timestamp_granularities[]=word" \
  -o transcript-api.json
npx hyperframes transcribe transcript-api.json
```

Groq serves the same request shape at `https://api.groq.com/openai/v1/audio/transcriptions` with
`model=whisper-large-v3`. Keep the key in the environment.
