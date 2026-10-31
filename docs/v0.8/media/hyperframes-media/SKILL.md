---
name: hyperframes-media
description: Prepares media for HyperFrames videos with the CLI's media tools - text-to-speech narration with Kokoro (hyperframes tts), word-level transcripts with Whisper or Parakeet (hyperframes transcribe), transparent cutouts of people (hyperframes remove-background), loudness matching (normalize-audio), beat grids and audio analysis, colour grades and looks on footage (media-treatment), and sourcing music, sound effects, logos and images into the project (media-use). Use when generating a voiceover, transcribing speech for captions, cutting a person out of video, choosing a voice or Whisper model, matching loudness, grading footage, or finding background music, a sound effect or a brand logo for a video.
metadata:
  tags:
  - hyperframes
  - tts
  - kokoro
  - whisper
  - transcription
  - background-removal
  - loudness
  - grading
---

# HyperFrames media preparation

HyperFrames media preparation turns raw inputs into files a composition can place: narration audio, word timings,
transparent video, level-matched sound and graded footage. `tts`, `transcribe`, `remove-background` and the audio
tools run on the local machine and download their model on first use; `media-use` can also reach HeyGen's catalogs and
paid models. Renders never fetch media: every file sits in the project first.
Checked against CLI 0.8.223.

## When to use this skill

Use this skill when a video needs a voiceover from text, captions from speech, a person over a new background or text
behind them, consistent loudness across clips, a beat grid for cutting to music, or a fix for dark, flat footage.

## Step 0: read the CLI and what this machine can run

```bash
npx hyperframes --version                  # `beats <file>` needs 0.8.222 or later
npx hyperframes media-use doctor           # ffmpeg, ffprobe, bundled sounds, the heygen CLI; changes nothing
npx hyperframes auth status                # signed in or not, before any catalog or paid step
npx hyperframes remove-background --info   # detected providers
python3 --version                          # Kokoro needs 3.10 or later
```

`media-use doctor` fails only on a missing ffmpeg, ffprobe or sound library. It reports trouble with HeyGen too, with a
fix, but still exits 0.

## The tools at a glance

The tools at a glance, with the model each uses and what it writes:

| Need | Command | Model or engine | Output |
|---|---|---|---|
| Voiceover from text | `npx hyperframes tts` | Kokoro-82M, 54 voices | WAV |
| Word timings from speech | `npx hyperframes transcribe` | Parakeet when installed, else Whisper | `[{id,text,start,end}]` JSON, SRT, VTT |
| Person cutout | `npx hyperframes remove-background` | u2net human segmentation | VP9 alpha WebM, ProRes 4444 MOV, PNG |
| Loudness | `npx hyperframes normalize-audio` | FFmpeg loudnorm measurement | `data-volume` written to the HTML |
| Beat grid | `npx hyperframes beats [project or file]` | beat tracker | `beats/<audio>.json` for a project; printed times for a file |
| Audio facts | `npx hyperframes audio <file>` | analysis | onsets, loudness, silence, envelope, sections |
| Colour grade or look | `npx hyperframes media-treatment` | built-in grading and effects | `data-color-grading` on the element |
| Music, sound effects, logos, images | `npx hyperframes media-use resolve` | catalogs, open libraries, local generators | a file under `.media/` |
| A new image, shot, voice, avatar clip or track | `npx hyperframes media-use generate` | HeyGen models, paid in credits | the file at `--out` |

## Narration with tts

Narration with `tts` synthesises speech locally with Kokoro.

```bash
npx hyperframes tts "Every frame is a function of time." -o assets/voice/intro.wav
npx hyperframes tts ./script.txt --voice bf_emma --speed 0.95 -o assets/voice/full.wav
npx hyperframes tts --list                                      # bundled voices
npx hyperframes tts "La reunión empieza a las nueve" --voice ef_dora -o assets/voice/es.wav
```

- The default voice is `af_heart`. A voice id's first letter picks its language, listed here by language name:
  American English `a`, Brazilian Portuguese `p`, British English `b`, French `f`, Hindi `h`, Italian `i`,
  Japanese `j`, Mandarin `z`, Spanish `e`.
- Non-English phonemisation needs `espeak-ng` installed system-wide.
- Kokoro needs Python 3.10 or later with `pip install kokoro-onnx soundfile`.
- `--speed` 0.7 to 0.8 for tutorials, 1.0 natural, 1.1 to 1.2 for upbeat intros.
- Kokoro returns no word timings: transcribe the WAV for captions.

Voices by use and pacing rules: [references/voices-and-pacing.md](references/voices-and-pacing.md).

## Transcripts with transcribe

Transcripts with `transcribe` give every word a start and end time. Always pass `--model`: the default `small.en`
translates non-English speech into English.

```bash
npx hyperframes transcribe assets/voice/intro.wav --model small.en --json      # known English
npx hyperframes transcribe interview.mp4 --model small --language es --json    # known Spanish
npx hyperframes transcribe song.mp3 --model medium.en --json                   # speech over music
npx hyperframes transcribe talk.mp4 --model small.en --to srt --output assets/talk.srt
npx hyperframes transcribe existing.vtt                                        # import SRT, VTT or Whisper JSON
```

The result lands in `assets/transcript.json` (the JSON output gives the path), and the next run replaces that file,
so give each source's transcript its own name. The default engine is `auto`: Parakeet when installed (`npx hyperframes models install parakeet`; faster, 25
European languages, detects the language itself), Whisper otherwise or for other languages; `--engine whisper` forces
Whisper. When the project already has caption HTML, importing a corrected transcript (`npx hyperframes transcribe
fixed.json --dir ./my-video`) replaces the words and keeps the caption code. Model sizes and quality checks:
[references/transcription.md](references/transcription.md).

## Cutouts with remove-background

Cutouts with `remove-background` separate a person from their background, for overlays and text behind the subject.

```bash
npx hyperframes remove-background talk.mp4 -o assets/talk-cutout.webm                # VP9 with alpha (default)
npx hyperframes remove-background talk.mp4 -o assets/talk-cutout.mov                 # ProRes 4444 for editors
npx hyperframes remove-background portrait.jpg -o assets/portrait.png
npx hyperframes remove-background talk.mp4 -o assets/fg.webm --background-output assets/plate.webm
npx hyperframes remove-background talk.mp4 -o assets/fg.webm --quality best --device cpu
npx hyperframes remove-background --info                                             # detected providers
```

`--quality` sets only the VP9 CRF: `fast` 30, `balanced` 18 (default), `best` 12. Higher quality keeps the cutout's
colour closer to its source, which matters when it sits over that same source. The first run downloads about 168 MB;
on CPU it runs at about 2 frames per second at 1080p.

## Loudness with normalize-audio

Loudness with `normalize-audio` measures a clip and writes the gain that hits a target, or matches one clip to
another.

```bash
npx hyperframes normalize-audio --target voice --lufs=-16 --write     # absolute target (default -16 LUFS)
npx hyperframes normalize-audio --reference voice --target music --write --json
```

Write a negative value with `=` (`--lufs=-16`). Without `--write` it only reports. Mixing levels and platform
targets: `audio-sync`.

## Beats and audio analysis

Beats and audio analysis give times to cut and animate on.

```bash
npx hyperframes beats --json                                   # the project's music <audio>, writes beats/<audio>.json
npx hyperframes beats assets/music.mp3 --json                  # one audio or video file: prints beatTimes, writes nothing (0.8.222 on)
npx hyperframes audio assets/music.mp3 --only beats,downbeats,bpm --json
npx hyperframes audio assets/music.mp3 --only sections,onsets,moments --json
```

Given a project folder, `beats` reads the `<audio>` marked `data-timeline-role="music"` (or with `music`, `bgm` or
`soundtrack` in its id); given a file, it analyses that file. A track with no steady beat fails and writes nothing. On calm music the tracker can
invent a tempo, often double: check `bpmConfidence`.

## Grades and looks on footage

Grades and looks on footage go through `media-treatment`, which writes a `data-color-grading` attribute the renderer
applies identically in preview and render. CSS filters on footage do not match across both.

```bash
npx hyperframes media-treatment --capabilities --json                    # families and controls
npx hyperframes media-treatment --capability wheels --json               # one family's ranges
npx hyperframes media-treatment --selector '#hero' --analyze --json      # measure the clip
npx hyperframes media-treatment --selector '#hero' --grading grade.json --apply
npx hyperframes media-treatment --selector '#hero' --clear
npx hyperframes grade-compare --for frame.png --grades grades.json --out grades.png
```

Pass `--file compositions/<scene>.html` for media inside a scene. On Windows PowerShell write JSON to a file instead of
inline. Details: [references/grading.md](references/grading.md).

## Sourcing music, sound effects, logos and images with media-use

Sourcing music, sound effects, logos and images goes through `npx hyperframes media-use`, which finds, makes or
imports one asset, saves it under `.media/`, records it in `.media/manifest.jsonl`, and reuses it the next time the
same thing is asked for. It never edits the composition: reference the printed file yourself.

```bash
npx hyperframes auth status                                                              # before any catalog or paid step
npx hyperframes media-use candidates --type bgm --intent "calm piano under narration"   # what exists, downloads nothing
npx hyperframes media-use resolve --type sfx --intent "soft whoosh"                      # open-licence or bundled sound
npx hyperframes media-use resolve --type logo --entity github --intent "GitHub logo"     # official brand mark
npx hyperframes media-use resolve --type image --from ./photo.jpg                        # bring in your own file
npx hyperframes media-use resolve --type sfx --intent "click" --local-only               # nothing from the network
npx hyperframes media-use generate --type music --prompt "warm lo-fi" --seconds 30 --out assets/music.mp3 --plan   # the estimate; spends nothing
```

| You need | Free | Paid in credits | On your machine, when the person asks |
|---|---|---|---|
| Music, `bgm` | over 10k tracks in HeyGen's catalog, once signed in | a generated track | MusicGen |
| Sound effects, `sfx` | Openverse (CC0 or CC BY), then 21 bundled sounds offline | | |
| `image`, `icon` | over 75k items in HeyGen's asset search, once signed in | generated images | FLUX through mflux, if installed |
| Logos, `logo` | theSVG, then the GitHub organisation avatar, then the site's favicon | | |
| Voiceover, `voice` | Voice Turbo from HeyGen, once signed in | the rest of HeyGen's voices, cloned voices | `npx hyperframes tts` (Kokoro) |
| A presenter, `video` | | avatar video | LTX for generic clips, if installed |
| Grades, `grade`, `lut` | built-in presets, a look library, or a LUT made from what `--intent` describes | | |

- **Sign in before catalog use.** The HeyGen music catalog, asset search and Voice Turbo need a sign-in, which is
  free: run `npx hyperframes auth status`, and when it shows none, ask the person to run
  `npx hyperframes auth login`. `sfx`, `logo`, `grade` and `lut` work without one. A host app that sets
  `HEYGEN_API_BASE` pays for its own calls and needs no sign-in.
- **Credits.** `media-use generate` produces stills, video shots, talking photos, speech and tracks through the
  HyperFrames sign-in, with no `heygen` CLI; a call that needs more refuses with `api_key_required`. Direct `heygen` commands bill
  that CLI's own login instead. Add `--plan` to read a call's estimated credits without spending them, and
  `--max-credits <n>` to hold it under a limit the person set. Ask the person before a paid generation.
- **Billing.** A refused call says what it needs: `402` or `insufficient_credit` asks for more credits, and
  `hf_usage_exhausted` says the plan's allowance has run out. `npx hyperframes billing top-up --needed 180` or `billing subscribe` opens
  the page, and the command holds (600 s by default) until the payment shows on the account, so the person pays and
  the run then continues.
- `--local-only` skips every network provider. Local tools are for when the person asks, not a quiet fallback for a
  missing sign-in.
- Credits for CC BY sounds are collected in `.media/audio/sfx/CREDITS.md`; deliver that file with the film.
- Check every logo against the brand's own files before it goes on screen.

## Verify the prepared media

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/voice/intro.wav   # the length you planned
npx hyperframes normalize-audio --target voice --lufs=-16                           # reports, writes nothing
tail -3 .media/manifest.jsonl                                                       # each sourced file is recorded
npx hyperframes check --json
```

Read the transcript itself: a clean exit from `transcribe` says nothing about the words.

## Checklist

- [ ] Every media file lives in `assets/`; nothing is fetched at render time.
- [ ] `transcribe` ran with an explicit `--model` that matches the language.
- [ ] The transcript was read: no runs of `♪`, no invented "Thank you." over silence.
- [ ] Voice and music levels set with `normalize-audio`, not guessed.
- [ ] Cutouts start at the same `data-start` and `data-media-start` as their source.
- [ ] Footage looks fixed through `media-treatment`, not CSS filters.
- [ ] Sourced sounds and images recorded in `.media/`; CC BY credits kept; sign-in checked; paid generations approved.

## Gotchas

- **Symptom:** English captions for Spanish speech. **Cause:** The `.en` models translate. **Fix:** use `small`,
  `medium` or `large-v3` with `--language`.
- **Symptom:** A transcript is overwritten. **Cause:** Each run writes `assets/transcript.json`. **Fix:** rename it
  before transcribing the next file.
- **Symptom:** Cutout fades do nothing. **Cause:** The runtime forces `opacity: 1` on a timed clip. **Fix:** fade an
  untimed wrapper.
- **Symptom:** A robotic Spanish or Japanese voice. **Cause:** `espeak-ng` is missing, or the voice prefix does not
  match the language. **Fix:** install it, or pick a voice whose first letter is that language.
- **Symptom:** Mic arms vanish from the cutout. **Cause:** The matte drops thin objects near the body and flickers on
  held props. **Fix:** check the frames.
- **Symptom:** A catalog search for music returns nothing. **Cause:** No sign-in. **Fix:** run `npx hyperframes auth
  status`, then have the person sign in.

## Anti-patterns

| Do not | Do instead |
|---|---|
| CSS filters on footage | `media-treatment`, which matches in preview and render |
| a media URL in the composition | a file in the project; renders never fetch |
| reaching for a local generator when sign-in is missing | ask the person to sign in; use local tools when they ask |
| an unapproved paid generation | read `--plan`, then ask |
| a redrawn logo | `--type logo`, checked against the brand's own files |

## References

- [references/voices-and-pacing.md](references/voices-and-pacing.md): Kokoro voices by use, speed, long scripts, cloud voice options.
- [references/transcription.md](references/transcription.md): Whisper model sizes, language rules, quality checks, external APIs.
- [references/grading.md](references/grading.md): grading families, animating a grade, comparing grades, LUTs.

## See also

`hyperframes-captions`, `audio-sync`, `video-copywriting`.
