---
name: hyperframes-captions
description: Builds captions, subtitles, karaoke lyrics and word-by-word kinetic captions in HyperFrames from a word-level transcript - grouping words, fitting text, placement for landscape and vertical video, exit guarantees, per-word emphasis, captions behind a speaker, and SRT or WebVTT sidecars for players. Use when adding any text synced to speech or music, choosing a caption style, fixing captions that overlap or linger, or delivering subtitle files.
metadata:
  tags:
  - hyperframes
  - captions
  - subtitles
  - karaoke
  - srt
  - webvtt
  - transcript
  - accessibility
---

# HyperFrames captions and subtitles

HyperFrames captions are timed text groups built from a word-level transcript and animated on a GSAP timeline, so
they render into the picture (burned in). Subtitles for players are sidecar files (SRT, WebVTT) that viewers can turn
off. Most social video needs burned-in captions, because most of it is watched without sound; long-form and
accessibility delivery also needs a sidecar. Checked against CLI 0.8.223 and GSAP 3.15.0.

## When to use this skill

Use this skill for any text that follows speech or music: captions on a talking head, karaoke lyrics, kinetic word
captions for a vertical clip, a subtitle file for a player, or a fix for captions that overlap, clip or stay on screen.

## Step 0: read the tools the captions depend on

```bash
npx hyperframes --version
npx hyperframes models --help | head -5                   # Parakeet and Whisper model commands
grep -rhoE 'gsap@[0-9.]+' --include='*.html' . | sort -u  # the timeline that animates the groups
```

Pick the transcription model for the language before anything else.

## From audio to caption groups

From audio to caption groups takes four steps.

1. **Get word timings.** `npx hyperframes transcribe assets/voice.wav --model small.en --json` (pick the model for the
   language; see `hyperframes-media`). The result is `[{id, text, start, end}, ...]`.
2. **Read and clean the transcript.** Drop `♪` and `�` tokens, fillers under 0.1 s, and words inside a trailing
   silence. More than 20% junk means the transcription failed: retry with a larger model.
3. **Group the words.** Group size follows the energy: 2 to 3 words for high energy, 3 to 5 for conversation, 4 to 6
   for a calm read. Start a new group when a sentence ends, when the gap before the next word reaches 150 ms, or when
   the group is full.
4. **Build one element per group** inside a single captions scene, with an entrance, an optional per-word highlight,
   and a hard exit.

Each timed entry holds exactly one word. Pair transcript words with caption words by their index; pairing by
spelling sends a word that occurs twice to the timing of its other occurrence.

## Captions scene structure

The captions scene structure is one sub-composition host with `data-track-kind="captions"` that holds every group, so
Studio shows them on one track. Ready-made styles: `npx hyperframes catalog --tag caption-style --json`.

```html
<div id="captions" data-composition-src="compositions/captions.html" data-composition-id="captions"
     data-track-kind="captions" data-track-index="9" data-width="1080" data-height="1920"
     data-start="0" data-duration="42"></div>
```

## Building groups on the timeline

Building groups on the timeline turns the grouped transcript into elements and tweens. The groups are written into
the HTML (not generated at seek time) or generated once, synchronously, before the timeline is registered.

```html
<template>
  <style>
    #root { position: absolute; inset: 0; }
    .cap { position: absolute; left: 0; right: 0; bottom: 640px; text-align: center; overflow: visible;
           font: 900 78px/1.05 "Outfit", sans-serif; color: #fff; text-transform: uppercase;
           text-shadow: 0 4px 18px rgba(0,0,0,.55); opacity: 0; }
    .cap .w { display: inline-block; margin: 0 .14em; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920"></div>
  <script>
    const WORDS = [ /* cleaned transcript: {id, text, start, end} */ ];
    const GROUPS = groupWords(WORDS, { max: 3, pauseBreak: 0.15 });
    const root = document.getElementById("root");
    const tl = gsap.timeline({ paused: true });

    GROUPS.forEach((g, gi) => {
      const el = document.createElement("div");
      el.className = "cap"; el.id = `cap-${gi}`;
      el.innerHTML = g.words.map((w, wi) => `<span class="w" id="cap-${gi}-${wi}">${w.text}</span>`).join("");
      root.appendChild(el);
      const { fontSize } = window.__hyperframes.fitTextFontSize(g.text.toUpperCase(),
        { fontFamily: "Outfit", fontWeight: 900, maxWidth: 900 });
      el.style.fontSize = fontSize + "px";

      const start = Math.max(0.1, g.start);
      tl.fromTo(el, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.14, ease: "power3.out" }, start);
      g.words.forEach((w, wi) => tl.fromTo(`#cap-${gi}-${wi}`, { color: "#ffffff" },
        { color: "#ffd23f", duration: 0.05 }, w.start));
      tl.to(el, { opacity: 0, duration: 0.12, ease: "power2.in" }, g.end - 0.12);
      tl.set(el, { opacity: 0, visibility: "hidden" }, g.end);   // hard kill
    });

    function groupWords(words, { max, pauseBreak }) {
      const out = []; let cur = [];
      words.forEach((w, i) => {
        cur.push(w);
        const next = words[i + 1];
        const endSentence = /[.!?]$/.test(w.text);
        if (!next || cur.length >= max || endSentence || next.start - w.end >= pauseBreak) {
          out.push({ words: cur, start: cur[0].start, end: cur[cur.length - 1].end, text: cur.map(x => x.text).join(" ") });
          cur = [];
        }
      });
      return out;
    }
    window.__timelines["captions"] = tl;
  </script>
</template>
```

`tl.set` changes a value instantly with no tween, which is why it may set `visibility` on a caption group; a tween of
`visibility` on a `.clip` remains off limits.

## Rules for groups on screen

These rules keep captions readable while they play:

- Only one group is ever visible. Each group appears no later than its first word and disappears no earlier than its
  last.
- Text sitting there at exactly 0 s looks as if it was always on the frame, so the first caption arrives 0.1 to 0.3 s
  in.
- A group's last instruction is a hard kill, `tl.set(..., { opacity: 0, visibility: "hidden" }, end)`. Without it, a
  leftover group can linger under the next one.
- Fade either the group or its words. Fading both multiplies the two opacities and the text seems to pop.
- Put a gradient or `background-clip: text` fill on the inner span; on the transformed container it breaks.

## Fitting and placing captions

Fitting and placing captions depends on the frame.

| Frame | Max width | Base size | Position |
|---|---|---|---|
| 1920×1080 landscape | 1600 px | 78 px, min 42 | 80 to 120 px from the bottom |
| 1080×1920 vertical | 900 px | 78 px, min 42 | about 600 to 700 px from the bottom, above the platform UI |
| 1080×1080 square | 900 px | 64 px | about 140 px from the bottom |

- Use a full-width absolute container with `text-align: center`. `left: 50%; transform: translateX(-50%)` clips at the
  frame edges.
- `overflow: visible`, never `hidden`: hidden cuts scaled words and glows.
- When an emphasis word scales up, divide `maxWidth` by that scale.
- Give every group `position: absolute`. Stacked in a flex column, an invisible group keeps its height and pushes the
  next group down.
- Never cover the speaker's face; stay inside the 80% title-safe box.
- Over footage, pick the blend by the brightness behind the text (0 to 255): under 60 `screen`, 60 to 180 `overlay`,
  over 180 `normal` with an opaque colour. Over bright footage, plain subtitles sit on a scrim cut to the size of the
  text at 30 to 40% opacity; a bar across the whole width looks like broadcast clutter.
- Some footage has subtitles burned in partway through. Look over a contact sheet at 1 frame per second before
  choosing where captions go.

## Choosing a caption style

Choosing a caption style follows the tone of the transcript when nobody named one.

| Tone | Type | Motion | Colour | Size at 1080p |
|---|---|---|---|---|
| Hype, launch | heavy condensed, 800 to 900 | scale pop, `back.out(1.7)`, 0.1 to 0.2 s | bright on dark | 72 to 96 px |
| Corporate | clean sans, 600 to 700 | fade and slide, `power3.out`, 0.3 s | white, muted accent | 56 to 72 px |
| Tutorial | mono or clean sans, 500 to 600 | typewriter or fade | high contrast | 48 to 64 px |
| Storytelling | serif, 400 to 500 | slow fade, `power2.out`, 0.5 s | warm, muted | 44 to 56 px |
| Social | rounded sans, 700 to 800 | word by word, `elastic.out` | coloured pills | 56 to 80 px |

Give brand names, numbers, ALL-CAPS words and calls to action a stronger treatment than the words around them.
Techniques (karaoke, clip-path wipes, slam, scatter exits, marker highlights): [references/caption-styles.md](references/caption-styles.md).

## Text behind the speaker

Three layers ordered by `z-index` put a word behind a person: the footage at the bottom, the caption in the middle,
and on top a transparent cutout of the person made with `npx hyperframes remove-background`. Use it as an accent on
a talking head, not as the caption style. The word-for-word captions still carry the speech, and only at the
strongest moment does a single word, at most one word per beat and never two at once, appear large behind the
speaker. Putting the whole transcript there hides it.

- Any shake or punch-in moves the footage and the cutout together, so wrap both in one element and animate that.
- A big word stays legible when the person covers 30 to 55% of it. Below about 15% it seems to hover in front; above
  about 65% it disappears.
- Heads move, so check the coverage over each caption's own time window, comparing the rendered word boxes with the
  matte.
- `check` assumes every `<video>` is opaque; add `data-layout-allow-occlusion` to the cutout.

## Subtitle sidecar files

Subtitle sidecar files ship next to the video for players and platforms. `npx hyperframes transcribe <file> --to srt`
or `--to vtt` writes one from the same transcript. To correct words after captions exist, import the fixed
transcript with `npx hyperframes transcribe fixed.json --dir <project>`: it replaces the words and keeps the caption
code around them. Formats, line rules, muxing into MP4 and burning in with FFmpeg:
[references/subtitle-formats.md](references/subtitle-formats.md).

## Verify the captions

```bash
npx hyperframes check --json                     # contrast over the real footage, nothing off the canvas
npx hyperframes snapshot --at 0.3,5.1,5.2,41.9   # one group at a time, the first and the last included
npx hyperframes transcribe assets/voice.wav --model small.en --to vtt --output /tmp/check.vtt   # sidecar writes
```

Sample the end of a group and the start of the next: a leftover group shows up exactly there.

## Checklist

- [ ] Transcript made with the right model for the language, read, and cleaned.
- [ ] Groups follow the energy's word count and break on pauses and sentence ends.
- [ ] Exactly one group visible at any time; every group has a hard kill.
- [ ] Each group fitted with `fitTextFontSize`; nothing clipped at the edges or behind platform UI.
- [ ] Captions clear of faces and inside title-safe.
- [ ] Contrast passes `check` over the real footage, not over a flat colour.
- [ ] A sidecar SRT or VTT delivered where the platform or brief needs one.

## Gotchas

- **Symptom:** two groups overlap. **Cause:** no hard kill, or an exit that runs past the next entrance. **Fix:**
  add the `tl.set` kill at each group's end and end exits before the next start.
- **Symptom:** captions slide later and later. **Cause:** words paired by spelling, so a repeated word took another
  occurrence's time. **Fix:** pair by index.
- **Symptom:** each caption sits lower than the one before. **Cause:** groups in a flex column, where hidden groups
  keep their height. **Fix:** position every group absolutely.
- **Symptom:** a glow is sliced off at the edge. **Cause:** `overflow: hidden` on the container. **Fix:**
  `overflow: visible`.
- **Symptom:** a Spanish interview captioned in English. **Cause:** a `.en` Whisper model translated the speech.
  **Fix:** a multilingual model with the language set.
- **Symptom:** captions fall behind the words after silences were removed. **Cause:** they were timed on the uncut
  file. **Fix:** cut first, then caption the cut with its retimed transcript.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `left: 50%` with `translateX(-50%)` | a full-width absolute container with `text-align: center` |
| the whole transcript behind the speaker | a word-for-word rail, plus one word at the peak |
| fading a group and its words together | fade one of them |
| a bar across the whole width over bright footage | a scrim cut to the size of the text at 30 to 40% opacity |

## References

- [references/caption-styles.md](references/caption-styles.md): karaoke, emphasis, entrances and exits by energy, audio-reactive captions, marker highlights.
- [references/subtitle-formats.md](references/subtitle-formats.md): SRT, WebVTT and ASS, reading-speed rules, muxing and burning in.

## See also

`hyperframes-media`, `talking-head-edits`, `audio-sync`, `platform-formats`, `vfx`.
