---
title: Mixing sound in HyperFrames
author: MOZGII, Inc.
lang: en
---

# Mixing sound in HyperFrames

A HyperFrames mix is written as attributes on `<audio>` and `<video>` elements: level, fades, automation lanes,
effect chains and group buses. One Web Audio graph serves both preview and render, so scrubbing in the preview plays
the mix exactly as the file will contain it.

## Contents

The sections of this page:

- Level and fades
- Automation lanes
- Ducking music under a voice
- Effect chains
- Group buses
- Loudness targets
- Sound effect placement

## Level and fades

Level and fades are three attributes.

| Attribute | Meaning |
|---|---|
| `data-volume` | the track's gain: 1 means unity (0 dB), and the ceiling is 3.98, which is +12 dB |
| `data-fade-in`, `data-fade-out` | fade length at the clip's start and end, in seconds |
| `data-playback-rate` | a fixed speed between 0.1 and 10 that keeps pitch; linked video and audio need the same value |

A crossfade between two tracks is two clips on different lanes that overlap, each with a fade.

## Automation lanes

Automation lanes are envelopes in `data-automation`, with times in seconds from the clip's start.

```html
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="30" data-track-index="7"
  data-automation='{"version":1,"lanes":[{"target":"volume","points":[{"t":0,"v":1},{"t":2.3,"v":1},{"t":2.6,"v":0.35},{"t":11.8,"v":0.35},{"t":12.2,"v":1}]}]}'></audio>
```

- `target` is `volume`, `rate` (a speed ramp that overrides `data-playback-rate`) or `fx.<nodeId>.<param>`.
- A volume lane multiplies `data-volume`: set the level in one place.
- Before its first point a lane keeps that point's value, and after its last point it keeps the last value; put an
  explicit point at `t: 0` anyway so the start is obvious.
- `curve` from −1 to 1 bends the segment after a point; at most 512 points per lane.
- Do not also tween volume with GSAP on a track with a lane or `data-volume`; lint flags it.

## Ducking music under a voice

Ducking music under a voice lowers the bed while anyone speaks: full level before the voice, about 0.3 to 0.4 during
speech, back up after. Build the lane from transcript times, with 0.2 to 0.3 s ramps so the dip is not heard as a
jump. Pauses shorter than about 1 s stay ducked.

```js
// words: [{start, end}, ...] from the transcript, shifted by the voice's data-start relative to the music
function duckLane(words, { low = 0.35, ramp = 0.25, gap = 1.0 } = {}) {
  const spans = [];
  for (const w of words) {
    const last = spans[spans.length - 1];
    if (last && w.start - last.end < gap) last.end = w.end; else spans.push({ start: w.start, end: w.end });
  }
  const pts = [{ t: 0, v: 1 }];
  for (const s of spans) pts.push({ t: Math.max(0, s.start - ramp), v: 1 }, { t: s.start, v: low },
    { t: s.end, v: low }, { t: s.end + ramp, v: 1 });
  return JSON.stringify({ version: 1, lanes: [{ target: "volume", points: pts }] });
}
```

Write the result into the HTML (the lane is static data, not computed at seek time).

## Effect chains

Effect chains are `data-fx-chain` JSON on an element (quotes written as `&quot;` inside a double-quoted attribute).
Node types: `gain`, `highpass`, `lowpass`, `peaking`, `lowshelf`, `highshelf`, `compressor`, `limiter`, `gate`,
`saturate`, `delay`, `reverb`, `chorus`, `phaser`, `bitcrush`. Give every node an `id` so automation can target it.

```json
{"version":1,"nodes":[
  {"type":"highpass","id":"hp","label":"Remove rumble","params":{"frequency":80}},
  {"type":"peaking","id":"clarity","params":{"frequency":3000,"gain":2.5,"q":1}},
  {"type":"limiter","id":"lim","params":{"limit":-1}}]}
```

| It sounds | Reach for |
|---|---|
| hum, rumble | `highpass` at 80 Hz |
| boomy | `peaking` at 200 Hz, cut 4 dB |
| muffled | `peaking` at 250 Hz, cut 3 dB |
| the words get lost | `peaking` at 3 kHz, boost 2.5 dB, or duck the music instead |
| harsh | `peaking` at 3.2 kHz, cut 3 dB |
| peaks clip | a `limiter` as the final node |

Compressor, limiter, gate and bitcrush cannot be automated; automate a `gain` before them. Reverb and delay make the
rendered tail longer than the source.

## Group buses

Group buses treat clips as one submix: give them the same `data-audio-group="voiceover"` and add
`<hf-audio-group id="voiceover"></hf-audio-group>` (closed with a separate end tag) for one effect chain, one volume
and one automation clock. Keep one role per group: voiceover, music, effects.

## Loudness targets

Loudness targets for delivery:

| Destination | Integrated loudness | True peak |
|---|---|---|
| Social and streaming platforms | about −14 LUFS | −1 dBTP |
| Spoken content, podcasts | −16 LUFS | −1 dBTP |
| Broadcast (EBU R128) | −23 LUFS | −1 dBTP |
| Broadcast (ATSC A/85, US) | −24 LKFS | −2 dBTP |

`npx hyperframes normalize-audio --target <id> --lufs=-16 --write` sets one clip's gain to a target (default −16);
with `--reference <id>` it matches one clip to another. Measure the rendered mix with FFmpeg's `ebur128` or
`loudnorm` filters (see `render-and-export`).

## Sound effect placement

An effect belongs with its picture. In life, light reaches us before sound, so viewers forgive a slightly late sound
far more readily than an early one: position the clip so that its loudest moment falls one frame after the event on
screen. Files rarely peak at their first sample; `npx hyperframes audio sfx.mp3 --json` says where the peak is. Phone
speakers barely reproduce a bed whose energy sits mostly below 150 Hz, so check the mix on small speakers or through a
high-pass preview.
