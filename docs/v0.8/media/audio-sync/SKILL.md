---
name: audio-sync
description: Syncs picture and sound in HyperFrames videos - the voice or the music as the clock, word timings for reveals, beat grids from hyperframes beats, hits timed a few frames early, audio-reactive motion from extracted frequency bands, music beds, sound effects with causes on screen, ducking with data-automation volume lanes, effect chains, and loudness targets with normalize-audio. Use when cutting to music, timing animation to narration, adding music or sound effects, making visuals react to audio, fixing levels, or checking the sound of a rendered video.
metadata:
  tags:
  - audio
  - music
  - beats
  - sound-design
  - audio-reactive
  - loudness
  - ducking
  - hyperframes
---

# Audio sync and sound for video

Syncing picture to sound starts with one decision, what the picture follows, and then puts each change on that
mark: spoken words when there is a narrator, beats when music leads. Viewers judge a film by its sound as much as by
its frames, and a silent film longer than 15 s feels unfinished before anyone notices a single picture. HyperFrames
runs one Web Audio graph for both preview and render, so the levels, fades, automation and effects you write as
attributes sound the same in the file as in the preview. Checked against CLI 0.8.223.

## When to use this skill

Use this skill when timing motion to a voiceover or a track, adding music or effects, making visuals react to audio,
ducking music under speech, or checking the loudness of a render.

## Step 0: read the tools the mix depends on

```bash
npx hyperframes --version     # `beats <file>` needs 0.8.222 or later
ffmpeg -version | head -1     # measures the render
python3 -c 'import numpy; print(numpy.__version__)'   # only for extract_audio_bands.py
```

Without numpy, run the band script through `uv run --no-project --with numpy`.

## Pick the clock

Pick the clock before timing anything.

| Film | Clock | How to time it |
|---|---|---|
| Narrated | the voice | each beat begins on the word it hangs on, and on-screen text arrives with the spoken word it repeats; word times from `npx hyperframes transcribe <voice> --model small.en --json` |
| Music only | the track | payoffs on strong beats; cuts follow the motion rather than every drum hit |
| Silent, or a platform that plays muted | reading speed | text and pictures carry the film; hold each line long enough to read |

## Beats from the music

Beats from the music come from the CLI.

```bash
npx hyperframes beats --json                                   # the project's music <audio>, writes beats/<file>.json
npx hyperframes beats assets/music.mp3 --json                  # one file directly (0.8.222 on): prints beatTimes, writes nothing
npx hyperframes audio assets/music.mp3 --only beats,downbeats,bpm --json
npx hyperframes audio assets/music.mp3 --only sections,onsets,moments --json   # for calm or irregular music
```

Mark the bed `data-timeline-role="music"` (or put `music`, `bgm` or `soundtrack` in its id). A beat time minus a
scene's `data-start` is the time inside that scene. Beat times are reliable where the music has a steady pulse. Over
calm or loose music the tracker may report a tempo that is not there, frequently twice the real one; look at
`bpmConfidence`, and when it is low, cut on changes of phrase and energy instead.

## Landing on a hit

To land on a hit, start before it. A move whose end must meet a beat begins 40 to 190 ms ahead of it; a reaction to
the beat begins 0 to 45 ms after. The hit is an instant change with `tl.set`, because an eased hit loses its punch.
Work out each beat from its index (`offset + i * 60 / bpm`); adding a rounded beat length again and again builds up
drift. Text the viewer must read stays up for one beat or longer, and a single visual treatment wears out after
roughly 6 s.

```js
const beat = (i) => BEATS[i] - SCENE_START;             // from beats/<music>.json
tl.fromTo("#logo", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.18, ease: "power4.out" }, beat(16) - 0.12);
tl.set("#flash", { opacity: 1 }, beat(16));
tl.to("#flash", { opacity: 0, duration: 0.25, ease: "power2.out" }, beat(16) + 0.03);
```

## Worked example: a logo landing on beat 8 of a 120 BPM bed

This complete `index.html` lands a logo on the ninth beat of the bed (index 8). The numbers come from
`npx hyperframes beats assets/music.mp3 --json`, which printed `"bpm": 120` and a first beat at `0.485` for this track.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0b0d12;
            font-family: Inter, Arial, sans-serif; }
    #logo { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
    #logo span { font-size: 160px; font-weight: 800; color: #f4f1ea; }
    #lead { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
    #lead span { font-size: 72px; color: #c9c6bd; }
    #flash { position: absolute; inset: 0; background: #ffffff; opacity: 0; }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="8" data-width="1920" data-height="1080">
    <div id="lead"><span>Your books, done by Friday</span></div>
    <div id="logo"><span>Ledgerly</span></div>
    <div id="flash"></div>
    <audio id="bed" class="clip" src="assets/music.mp3" data-start="0" data-duration="8" data-track-index="0"
           data-volume="0.8" data-fade-out="1" data-timeline-role="music"></audio>
  </div>
  <script>
    const FIRST_BEAT = 0.485, BPM = 120;
    const beat = (i) => FIRST_BEAT + i * 60 / BPM;      // from the index, so nothing drifts

    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#lead span", { y: 30 }, { y: -30, duration: beat(8), ease: "none" }, 0);
    tl.set("#lead", { opacity: 0 }, beat(8));
    tl.fromTo("#logo span", { scale: 0.6, opacity: 0 },
      { scale: 1, opacity: 1, duration: 0.18, ease: "power4.out" }, beat(8) - 0.12);   // the move starts early
    tl.set("#flash", { opacity: 0.8 }, beat(8));                                       // the hit is instant
    tl.to("#flash", { opacity: 0, duration: 0.25, ease: "power2.out" }, beat(8) + 0.03);

    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
```

Check it on the frame either side of the hit: `npx hyperframes snapshot --at 4.3,4.5,5 --no-end` shows the lead line, the
flash, then the logo holding.

## Audio-reactive motion

Audio-reactive motion modulates visuals with the sound's energy. Extract per-frame bands once:

```bash
python3 scripts/extract_audio_bands.py assets/music.mp3 --fps 30 --bands 8 -o assets/audio-bands.json
# without numpy installed: uv run --no-project --with numpy python scripts/extract_audio_bands.py ...
```

When a script from `scripts/` is not on disk (a pack install), read that script from the library that served this page and save it first.

Then use it in one of two seek-safe ways: shape tweens at build time (louder phrases enter bigger), or read the frame
for the current time in one long tween's `onUpdate`. Never one `tl.call()` per frame: seeking does not replay
callbacks. Patterns and limits: [references/audio-reactive.md](references/audio-reactive.md).

## Music, effects and levels

Music, effects and levels follow a few rules.

- Story films longer than roughly 15 s carry a music bed plus sounds for what visibly happens, except when the
  person wants silence or the film is made to play muted.
- Bring the music in on its strongest bar rather than its quiet intro. Stock tracks are often loops of 15 to 30 s;
  loop the bed with a 0.4 s fade at the start and a 1.5 s fade at the end.
- Keep effects few, each triggered by something on screen: a click for a real cursor click, a whoosh for a cut or a
  card flying past, a soft tick for typing, a pop when a number lands, a single riser into the payoff.
- Offset each effect so its loudest point comes one frame later than the picture it belongs to
  (`npx hyperframes audio <file> --json` reports where a file peaks). Alternate two or three takes of any sound that
  repeats.
- Under a voice, music sits at roughly 0.14 to 0.35 volume and dips whenever someone speaks; effects sit 3 to 6 dB
  above the bed.
- Mix about −14 to −16 LUFS integrated for social and streaming; true peak at or below −1 dBTP.

Attributes for fades, ducking lanes, effect chains and buses: [references/mixing.md](references/mixing.md).

## Verify the sound

Checking the sound uses measurement, because an agent cannot listen.

```bash
npx hyperframes normalize-audio --target voice --lufs=-16 --write
npx hyperframes normalize-audio --reference voice --target music --write
npx hyperframes audio renders/final.mp4 --json                 # sound present, hits, loudness of the render
ffmpeg -hide_banner -i renders/final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```

Say in the delivery note that the sound was measured, not heard.

## Checklist

- [ ] The clock chosen: voice, music or reading speed.
- [ ] Reveals on their words; payoffs on strong beats, started 40 to 190 ms early.
- [ ] Beats computed from indexes; calm music cut on phrases, not invented beats.
- [ ] Audio-reactive motion seek-safe and subtle (5% scale or less on text).
- [ ] Bed ducked under speech; effects few, each with a cause.
- [ ] Render measured: about −14 to −16 LUFS, true peak −1 dBTP or lower, no clipping.

## Gotchas

- **Symptom:** reactive motion moves in preview but is frozen in the render. **Cause:** one `tl.call()` per frame;
  seeking never replays callbacks. **Fix:** read the frame in `onUpdate`, or shape tweens at build time.
- **Symptom:** cuts slide off the beat after a minute. **Cause:** a rounded beat length added over and over. **Fix:**
  compute every beat from its index.
- **Symptom:** the music is missing from the render. **Cause:** its `<audio>` has no `id`. **Fix:** give it one.
- **Symptom:** the narrator is hard to follow. **Cause:** voice and music both near 1.0. **Fix:** duck the bed with a
  volume lane.
- **Symptom:** music dips twice as far as planned. **Cause:** a GSAP volume tween on a track that also has a lane or
  `data-volume`. **Fix:** keep one; lint flags the pair.

## Anti-patterns

| Do not | Do instead |
|---|---|
| a `tl.call()` per frame for reactive motion | one long tween whose `onUpdate` reads the frame, or tweens shaped at build time |
| adding a rounded beat length again and again | `offset + i * 60 / bpm` from the beat's index |
| a sound for everything on screen | few effects, each with a visible cause |
| reporting that a mix sounds good | report the measured LUFS and peak, and say it was measured, not heard |

## References

- [references/audio-reactive.md](references/audio-reactive.md): band data, build-time shaping, per-frame `onUpdate`, mapping bands to properties, limits.
- [references/mixing.md](references/mixing.md): volume, fades, `data-automation` lanes, `data-fx-chain` effects, buses, ducking and loudness.
- `scripts/extract_audio_bands.py`: per-frame RMS and frequency bands as JSON.

## See also

`hyperframes-media`, `motion-design`, `hyperframes-captions`, `render-and-export`.
