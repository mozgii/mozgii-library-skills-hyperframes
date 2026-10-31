---
name: talking-head-edits
description: Edits talking-head, interview, podcast and presenter footage in HyperFrames - a tighter cut from the word transcript (long pauses, filler words and named stretches removed, frame-accurate, click-free), captions made after the cut, a verbatim caption rail with one earned word set behind the speaker, designed cards (titles, lower thirds, number callouts, pull quotes) synced to what is said, the speaker shrunk to picture-in-picture or split screen while a card holds, punch-ins and B-roll on the sentence, and presenter clips placed as media. Use when someone gives a recording of a person speaking and wants it cut, captioned, packaged or turned into a short.
metadata:
  tags:
  - talking-head
  - interview
  - podcast
  - jump-cut
  - transcript
  - b-roll
  - lower-third
  - hyperframes
---

# Talking-head edits

Talking-head edits are the jobs people bring with a recording of someone speaking: remove the pauses and fillers,
caption it, put designed cards around it, make a vertical short from it. HyperFrames keeps the footage untouched as a
`<video>` clip and builds everything else as HTML over it, so every card stays editable. The cut itself is made with
FFmpeg from the word transcript before the composition is built. Checked against CLI 0.8.223 and FFmpeg 7 to 9.

## When to use this skill

Use this skill when the input is footage of a person talking (an interview, a podcast clip, a founder video, a
lecture, a presenter recorded for a product video) and the request is to tighten it, caption it, package it with
graphics, or cut a short from it. For captions alone on any audio, `hyperframes-captions` holds the caption craft;
for a film built from scratch, `video-storyboard`.

## Step 0: read the tools the cut needs

```bash
npx hyperframes --version
ffmpeg -version | head -1      # FFmpeg 7 to 9
python3 --version              # 3.10 or later for the cut script
```

The cut script uses the standard library only, so nothing else needs installing.

## The order of work

The order of work decides whether captions land on the words. Each step reads the output of the one before.

1. **Transcribe the source** with word timings (`npx hyperframes transcribe interview.mp4 --model small.en --json`;
   a non-English speaker needs `small`, `medium` or `large-v3` with `--language`).
2. **Read the transcript.** Fix names and terms the model missed; note where the face and any on-screen text sit.
3. **Cut** pauses, fillers and stretches the person named (next section). The cut writes a retimed transcript.
4. **Caption and package the cut**, never the source: captions timed to the source drift off the words after a cut.
5. **Check** with `npx hyperframes check --json` and snapshots at every card and every splice.

## Cutting pauses and fillers from the transcript

Cutting from the transcript turns word timings into a list of kept ranges, then splices those ranges with FFmpeg. The
script `scripts/cut_from_transcript.py` (Python 3.10+, FFmpeg on PATH, standard library only) does both:

```bash
python3 scripts/cut_from_transcript.py --input assets/interview.mp4 --transcript assets/transcript.json \
  --cut-silence 0.8 --remove-fillers "um,uh,erm" --plan            # show the kept segments, encode nothing
python3 scripts/cut_from_transcript.py --input assets/interview.mp4 --transcript assets/transcript.json \
  --cut-silence 0.8 --remove-fillers "um,uh,erm" --remove "41.2-47.9" --out assets/interview-cut.mp4
```

When a script from `scripts/` is not on disk (a pack install), read that script from the library that served this page and save it first.

It writes `interview-cut.mp4` and `interview-cut.words.json`, the transcript retimed to the cut, ready for captions.
The rules it follows are the ones that matter in any tool:

| Rule | Value | Why |
|---|---|---|
| Pause threshold | 0.6 to 1.0 s; 0.8 s is a natural default | shorter cuts make speech breathless |
| Padding kept around speech | 0.15 s on each side of a cut pause | word onsets and breaths survive |
| Shortest kept piece | 0.2 s | slivers read as glitches |
| Audio fade at each splice | 30 ms in and out | a hard splice clicks |
| Intermediate audio | uncompressed PCM, encoded once at the end | AAC pads every piece with priming silence, a gap at each cut |
| Video | re-encoded with a keyframe every second, constant frame rate | stream copy snaps cuts to sparse keyframes and can swallow a cut |

Read the `--plan` output before encoding: a kept total far below the source length usually means the transcript is
missing words. Filler removal is risky on words that are also real ("like", "so", "right"); remove only true
fillers unless the person lists more.

## Jump cuts that do not look broken

Jump cuts that do not look broken hide the splice with a change of framing. On every second or third cut, punch in
the footage wrapper by 8 to 15% (or back out), so the jump reads as an edit rather than a skipped frame. Animate a
wrapper `div` around the `<video>`, never the timed `<video>` itself:

```html
<div id="a-roll" style="position:absolute;inset:0;overflow:hidden">
  <video id="talk" class="clip" src="assets/interview-cut.mp4" data-start="0" data-duration="38.4"
         data-track-index="1" playsinline data-has-audio="true"
         style="width:100%;height:100%;object-fit:cover"></video>
</div>
<script>
  const CUTS = [3.2, 7.9, 12.6];                    // splice times in the cut file, from the plan's segment lengths
  CUTS.forEach((t, i) => {
    tl.set("#a-roll", { scale: i % 2 ? 1 : 1.12, transformOrigin: "50% 35%" }, t);   // instant reframe on the splice
  });
</script>
```

Keep the speaker's eyes in the same third of the frame across a punch-in (`transformOrigin` near the face).

## Caption rail and the one embed

Two caption roles share a talking head. The rail is the running line of word-for-word captions; an embed is a single
large word placed behind the speaker at the peak moment. The rail is the default on every talking head: readable, under or beside
the speaker, one group at a time. Promote at most one word per beat to an embed, never two at once, and never the
whole transcript. Set every line behind the speaker and the words disappear, and the peak moment has nothing left to
mark it.

- An embed needs a cutout of the speaker over the word: `npx hyperframes remove-background interview-cut.mp4 -o
  assets/talk-cutout.webm`, stacked video, then word, then cutout, all with the same `data-start`.
- A word reads best 30 to 55% covered by the speaker; measure over the word's own window, because heads move.
- Two speakers or hard cuts make the matte flicker: split the clip per shot or per speaker first.
- Over bright daylight footage use dark, opaque type; light screen-blended type washes out.

Grouping, styles and karaoke: `hyperframes-captions`.

## Designed cards synced to the transcript

Designed cards are titles, lower thirds, number callouts and pull quotes timed to the words that name them. Find the
word in the retimed transcript and start the card 0.1 to 0.2 s before it.

| Card | Starts | Holds | Speaker meanwhile |
|---|---|---|---|
| Lower third (name, role) | when the name is said or in the first 3 s | 3 to 5 s | full frame |
| Number callout | 0.15 s before the number is spoken | until the sentence ends, at least 2 s | shrinks to a corner or a split |
| Pull quote | on the first word of the line | the line plus 1 s | dims or shrinks |
| Chapter title | on a topic change, in a cut pause | 1.5 to 2.5 s | hidden or blurred |

Card density follows length: roughly one card every 12 to 20 s on a five-minute clip, more in a 30 s short. Check
every card against the face: `npx hyperframes snapshot --at <card times>` and look.

## Picture-in-picture and split layouts

Picture-in-picture and split layouts share the frame between the speaker and a card. Move the speaker by animating
the wrapper's `scale` and position, so the footage keeps playing underneath:

```js
tl.to("#a-roll", { scale: 0.34, x: 560, y: 300, borderRadius: 24, duration: 0.6, ease: "power3.inOut" }, 14.8)
  .to("#a-roll", { scale: 1, x: 0, y: 0, borderRadius: 0, duration: 0.5, ease: "power3.inOut" }, 21.0);
```

| Layout | Use when |
|---|---|
| Full frame with overlay cards | the face carries the moment |
| Corner picture-in-picture | a chart or screen needs most of the frame |
| Split (speaker one side, card the other) | a landscape explainer with a card per claim |
| Stack (card above, speaker below) | vertical 9:16 with data |

Use `border-radius` with `overflow: hidden` on the wrapper; a `clip-path` on a scaled wrapper is cheaper to render
than a mask.

## B-roll on the sentence

B-roll is footage or a screen recording laid over the speaker while their voice continues. Cut it in on the first
word of the sentence it illustrates and out at the sentence end, never mid-word. Give each B-roll clip `muted` and its
own `data-start`, keep the speaker's `<video>` running underneath for the sound, and keep a B-roll shot to 2 to 5 s.

## A vertical short from a long recording

A vertical short from a long recording picks one self-contained moment of 20 to 60 s: a claim and its proof, a
question and its answer. Find it in the transcript first, cut it with `--remove` ranges or by trimming with
`data-media-start`, then build at 1080×1920 with the speaker framed on the face (`object-fit: cover` and
`object-position` on the face), captions in the safe band, and the hook line in the first second. Platform safe zones:
`platform-formats`.

## Presenter and avatar clips as media

A presenter clip made in another tool (an AI avatar, a recorded host) is placed like any footage: download it into
`assets/` before the render, place it as a `<video class="clip" data-has-audio="true">`, and remove its background
when titles must pass behind it. A render never depends on a download.

## Verify the cut

```bash
python3 scripts/cut_from_transcript.py --input assets/interview.mp4 --transcript assets/transcript.json \
  --cut-silence 0.8 --plan                                           # kept total close to the speech you expect
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/interview-cut.mp4   # matches the plan
npx hyperframes check --json
npx hyperframes snapshot --at 3.2,7.9,12.6                           # a frame at each splice, faces clear of cards
```

Listen for clicks if you can; otherwise say the splices were checked by their fades, not by ear.

## Checklist

- [ ] Transcript made with the right model for the language and corrected for names and numbers.
- [ ] The cut planned with `--plan`, read, then encoded; captions and cards built on the cut's transcript.
- [ ] No click or gap at splices; framing changes on jump cuts.
- [ ] One rail of verbatim captions; at most one embed per beat; nothing covers the face.
- [ ] Cards start on the words that name them and hold long enough to read.
- [ ] The video works muted and with sound; the last caption or card clears before the end.

## Gotchas

- **Symptom:** Captions drift after the cut. **Cause:** They were timed to the source. **Fix:**
  caption the cut file with its retimed transcript.
- **Symptom:** A click at every cut. **Cause:** No fade at the splices, or audio encoded per piece before joining.
  **Fix:** fade the audio 30 ms in and out at each splice and encode the audio once, after joining.
- **Symptom:** A cut vanished. **Cause:** Stream copy (`-c copy`) snapped to keyframes. **Fix:** re-encode the pieces.
- **Symptom:** The speaker's sound disappears. **Cause:** The `<video>` lacks `data-has-audio="true"`. **Fix:** add
  it.
- **Symptom:** Text behind the speaker flickers. **Cause:** Two people or a camera cut inside the matte's window.
  **Fix:** split the clip first.
- **Symptom:** "Like" was removed from "I'd like to". **Cause:** A filler list that includes real words. **Fix:**
  remove only true fillers.

## Anti-patterns

| Do not | Do instead |
|---|---|
| animating the timed `<video>` | animate a wrapper `div` around it |
| captioning before cutting | cut first; each step reads the output of the one before |
| every line behind the speaker | one rail, and at most one embed per beat |
| depending on a download at render time | place the file in `assets/` first |

## See also

`hyperframes-captions`, `hyperframes-media`, `platform-formats`, `audio-sync`, `hyperframes`.
