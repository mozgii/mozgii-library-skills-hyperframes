---
name: video-copywriting
description: Writes the words of a programmatic video - narration scripts paced to speech rate, opening lines, hook-story-proof-call structure, on-screen copy limits per element, spoken forms of numbers and acronyms for text-to-speech, plain language for global audiences, and keeping a person's exact copy when they want it kept. Use when writing or editing a voiceover script, titles, captions or calls to action for a video, when TTS mispronounces something, or when on-screen text is too long to read.
metadata:
  tags:
  - copywriting
  - narration
  - script
  - voiceover
  - tts
  - plain-language
  - video
---

# Copywriting for video

Copywriting for video is writing for a viewer who cannot reread. Every line is on screen or in the ear for a fixed
time, so it must be short, concrete and in the order the pictures need. This skill covers the narration script, the
on-screen copy and the spoken forms text-to-speech needs.

## When to use this skill

Use this skill when writing or tightening a voiceover script, headlines, captions, stat labels or calls to action,
when a TTS voice reads a number or name wrongly, or when on-screen text fails the reading-time check.

## Step 0: read how the film will speak

```bash
npx hyperframes --version
npx hyperframes tts --list | head -20      # voices, when TTS reads the script
ls SCRIPT*.md SCRIPT*.txt 2>/dev/null      # an existing script: keep or improve
```

Know the mode (below) before touching a word.

## Two modes: keep or improve

Two modes decide how much you may change.

- **Keep:** the person supplied exact copy (a legal line, a slogan, a quote). Change nothing; only fit it: size, line
  breaks, timing. Flag any line that cannot be read in its time and ask.
- **Improve:** the person gave a brief or rough copy. Rewrite for clarity and length, keeping every fact.

When unsure, ask which mode applies.

## Script length from speech rate

Script length follows speech rate: about 2.2 to 2.5 words a second for natural narration.

| Video | Words |
|---|---|
| 15 s | 33 to 37 |
| 30 s | 65 to 75 |
| 60 s | 130 to 150 |
| 90 s | about 155 for a fast-cut film, up to 200 for an explainer |

Each scene gets roughly 19 spoken words, about 9 s. The script should feel shorter than the video: silence between sentences
is room for the pictures. A voiceover longer than its visuals forces idle motion; cut words, not motion.

## Structure: hook, story, proof, call

Structure for most product and launch videos has four parts; short pieces drop some.

1. **Hook:** the opening line, which must create tension, curiosity or surprise in the first seconds. Vary the type: a
   bold claim, a question, a contrast, a number.
2. **Story:** what the thing does and for whom, concretely.
3. **Proof:** real numbers, real customers, a demo.
4. **Call:** what to do next, with an active verb ("Start free at example dot com").

A 15 s social ad is often hook, proof, call. If the opening is "Welcome to..." or "Introducing...", start over.

## Writing for the ear

Writing for the ear differs from writing for the page.

- Contractions ("it's", "you'll"); mixed sentence lengths; one idea per sentence.
- One phrase per thing that appears on screen, so each reveal has a cue word.
- Read it aloud. If it sounds like a brochure, rewrite it.
- Write what the voice should say, not what the screen shows: the visual can show "$1.9T" while the voice says
  "nearly two trillion dollars".

## Spoken forms for text-to-speech

Spoken forms for text-to-speech replace symbols the voice would misread. Keep a separate spoken script with these
substitutions; the creative script keeps the written forms.

| On screen | In the spoken script |
|---|---|
| 135+ | more than one hundred thirty-five |
| $1.9T | nearly two trillion dollars |
| 99.999% | ninety-nine point nine nine nine percent |
| 10x | ten times |
| API, SDK, CLI | A P I, S D K, C L I |
| example.com | example dot com |
| v2.4 | version two point four |
| GSAP | G-Sap (or whatever the brand says) |
| @handle | the person's name; TTS reads handles letter by letter |

## On-screen copy limits

On-screen copy limits keep text readable in the time it has.

| Element | Max words | Max characters | Notes |
|---|---|---|---|
| Hero headline | 5 to 7 | 35 | one to three words is strongest |
| Subheadline | 8 to 12 | 60 | one complete thought |
| Body line | 15 to 25 | 120 | only with more than 3 s on screen |
| Stat label | 1 to 3 | 20 | the number carries it |
| Call to action | 2 to 4 | 22 | verb first: "Start free", "See how" |
| Caption line, vertical | 6 to 10 | 40 | matches 2 to 3 words a second |
| Quote | 10 to 20 | 100 | attribution on its own smaller line |

A line must be readable in about two thirds of its time on screen. Hold rule: 0.5 s plus 0.3 s per word, and at
least 2 s for the closing line.

## Worked example: a 15-second vertical spot from brief to timed copy

The brief says Ledgerly reads a bank statement and matches every row in 90 seconds, for freelancers doing their own
books, and the call is to start free. Mode: improve. A 15 s social ad is hook, proof, call, so it gets 33 to 37 spoken
words.

The creative script keeps the written forms:

> It's 11 pm, and 214 payments still need typing in. Drop the statement into Ledgerly. Ninety seconds later, every row
> is matched. Your books are done. Start free at ledgerly.example.

The spoken script writes what the voice says, and counts 35 words by `wc -w`:

> It's eleven P M, and two hundred fourteen payments still need typing in. Drop the statement into Ledgerly. Ninety
> seconds later, every row is matched. Your books are done. Start free at ledgerly dot example.

The on-screen copy says what the voice does not, and each line clears the hold rule of 0.5 s plus 0.3 s per word:

| Time | Element | Copy | Words | Hold needed | Time on screen |
|---|---|---|---|---|---|
| 0 to 3.5 s | hero headline | 214 payments left | 3 | 1.4 s | 3.5 s |
| 3.5 to 7.5 s | subheadline | Drop in your statement | 4 | 1.7 s | 4 s |
| 7.5 to 11.5 s | stat label | 90 s, every row matched | 5 | 2.0 s | 4 s |
| 11.5 to 15 s | call to action | Start free | 2 | 2.0 s (closing line) | 3.5 s |

The same lines as a composition: one clip per line, cut on the voice, each with a slow push on the text inside it, so
frame 0 already shows the hook:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0f1115; color: #f4f1ea;
            font-family: Inter, Arial, sans-serif; }
    .line { position: absolute; left: 96px; right: 96px; top: 760px; font-size: 104px; font-weight: 800; line-height: 1.1; }
    .line span { display: inline-block; }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="15" data-width="1080" data-height="1920">
    <div id="l1" class="clip line" data-start="0" data-duration="3.5" data-track-index="1"><span>214 payments left</span></div>
    <div id="l2" class="clip line" data-start="3.5" data-duration="4" data-track-index="2"><span>Drop in your statement</span></div>
    <div id="l3" class="clip line" data-start="7.5" data-duration="4" data-track-index="1"><span>90 s, every row matched</span></div>
    <div id="l4" class="clip line" data-start="11.5" data-duration="3.5" data-track-index="2"><span>Start free</span></div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    [["#l1", 0, 3.5], ["#l2", 3.5, 4], ["#l3", 7.5, 4], ["#l4", 11.5, 3.5]].forEach(([id, at, slot]) => {
      tl.fromTo(`${id} span`, { scale: 0.92 }, { scale: 1, transformOrigin: "0% 50%", duration: slot, ease: "none" }, at);
    });
    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
```

## Plain language for every viewer

Plain language for every viewer means short sentences, common verbs, numbers people parse at a glance, and no idioms
that do not travel. Rules, number formats for global audiences and accessibility checks:
[references/plain-language.md](references/plain-language.md).

## Verify the words against the clock

```bash
wc -w SCRIPT-spoken.txt                                              # 30 s film: 65 to 75 words
npx hyperframes tts SCRIPT-spoken.txt -o /tmp/vo.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/vo.wav   # the real spoken length
npx hyperframes check --json | grep -c line_unread                   # expect 0
```

Read the script aloud once as well: a word count finds length, not rhythm.

## Checklist

- [ ] Mode known: keep or improve.
- [ ] Word count fits the duration at about 2.2 to 2.5 words a second; scenes about 19 words or fewer.
- [ ] The opening line is specific and not a greeting.
- [ ] A spoken script exists with numbers, acronyms and URLs written as said.
- [ ] Every on-screen element within its limits and hold time.
- [ ] Facts and figures from the source, unchanged.

## Gotchas

- **Symptom:** The voice spells a word. **Cause:** It saw capitals or a handle. **Fix:** write the spoken form.
- **Symptom:** Narration runs long after TTS. **Cause:** The voice is slower than estimated. **Fix:** time from the
  transcript, then trim.
- **Symptom:** Copy changed that should not have. **Cause:** The mode was "keep". **Fix:** restore it exactly.
- **Symptom:** Text is cut off in vertical. **Cause:** Copy written for 1920 px wide. **Fix:** shorten it or fit it
  with `fitTextFontSize`.

## Anti-patterns

| Do not | Do instead |
|---|---|
| opening on "Welcome to" or "Introducing" | a claim, a question, a contrast or a number |
| narration that repeats the words on screen | say what the picture does not |
| written forms in the spoken script | a separate spoken script |
| cutting motion to fit a long voiceover | cut words |

## References

- [references/plain-language.md](references/plain-language.md): sentence rules, accessible verbs, numbers, dates and times for global audiences, cultural neutrality, accessibility.

## See also

`video-storyboard`, `hyperframes-media`, `hyperframes-captions`, `motion-design`, `website-to-hyperframes`.
