---
name: motion-design
description: Directs motion for programmatic video - ease by role, durations and holds, overlap and stagger, springs, beat grids for music, titles that land and stay still, cuts on the fastest frame, scene build-breathe-resolve, rhythm plans, motion feedback fixes, and the defaults that make a film look machine-made. Use when choosing eases, durations and staggers, timing motion to music, or when a HyperFrames or web-animation video feels flat, generic, too fast, too busy or like slides; for the story and the beat plan use video-storyboard.
metadata:
  tags:
  - motion-design
  - easing
  - timing
  - choreography
  - rhythm
  - storytelling
  - animation
---

# Motion design for video

Motion reads as intended when five choices are made on purpose: the curve, the duration, the order, the hold and the
cut. The figures on this page come from frame-by-frame study of professional launch films. Treat them as defaults;
a reference film from the person, or a moment designed to break the rule, overrides them.

Use this page while planning a film's motion, picking eases, durations and staggers, syncing to music, or acting on
notes like "feels generated", "too fast", "like slides" or "the titles keep moving". The story and beat plan come
first, from `video-storyboard`.

## Step 0: read what the film animates with

The ease names below are GSAP's; check the version the project loads before relying on a plugin or a named ease:

```bash
grep -rhoE 'gsap(@|/)[0-9]+\.[0-9]+\.[0-9]+' --include='*.html' . | sort -u     # CDN tags in compositions
npm ls gsap 2>/dev/null | grep gsap                                              # a bundled project
```

## Ease by role

Every move has a role, and the role picks the curve. Landing should take longer than leaving.

| Role | First choice | Also good | Avoid |
|---|---|---|---|
| Something arrives | `expo.out` | `power4.out` | any `.in` ease, which feels sluggish on an entrance |
| Camera move, colour flood | `power2.inOut` | `sine.inOut` | `.out` alone, which stops like a wall |
| Something leaves or zooms through | `power3.in` | `power2.in` | `.out` on an exit, which looks reluctant |
| Playful overshoot | `back.out(1.4)` | `elastic.out(1, 0.5)` | overshoot on opacity or colour |
| Spin, progress bar, constant speed | `"none"` | | any curve: the even speed is the point |

A film where every tween is `power2.out` at 0.5 s looks generated at once. Give each scene at least three different
eases.

## Timing numbers

The pace inside a scene comes from durations, overlaps and staggers:

| What | Value | Note |
|---|---|---|
| A fast move | 0.3 to 0.6 s | blur its fastest frame: 6 to 12 px for elements the size of text, 15 to 20 px when the whole frame moves |
| An exit | 40 to 50% shorter than its entrance | one continuous motion; no slide, pause, then leave |
| Overlap | start the next element when the previous is 30 to 50% through | strictly one-after-another feels robotic; everything together feels cheap |
| Stagger, letters | one frame apart | |
| Stagger, words | 60 to 120 ms | |
| Stagger, list items | 40 to 80 ms | the whole stagger stays under 0.5 s |
| First motion | 0.1 to 0.3 s after the start | frame 0 still shows content: it is the thumbnail |

Order a stagger by importance rather than by the order in the DOM; the first thing to move is read as the most
important. When entrances feel like glitches, they are too quick: adding roughly a second to the whole film often
cures it.

## Worked example: one scene timed by the rules

A headline lands word by word, a subtitle overlaps it, a card arrives with a playful overshoot and leaves faster than
it came. The timeline is paused and registered for HyperFrames to seek:

```html
<script>
  const tl = gsap.timeline({ paused: true });
  // Headline: per-word blur-in, 0.13 s each, 0.067 s apart, no movement.
  tl.fromTo("#headline .word",
    { opacity: 0, filter: "blur(6px)" },
    { opacity: 1, filter: "blur(0px)", duration: 0.13, stagger: 0.067, ease: "power2.out" }, 0.2);
  // Subtitle starts while the headline is about 40% through.
  tl.fromTo("#subtitle", { opacity: 0, y: 24 },
    { opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }, 0.35);
  // Card: overshoot on position and scale only; opacity has no bounce.
  tl.fromTo("#card", { y: 80, scale: 0.92 },
    { y: 0, scale: 1, duration: 0.6, ease: "back.out(1.4)" }, 0.6);
  tl.fromTo("#card", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power1.out" }, 0.6);
  // Hold: 4 headline words need 0.5 + 0.3 * 4 = 1.7 s readable before anything leaves.
  // Exit: 0.35 s against a 0.6 s entrance, accelerating away.
  tl.to("#card", { y: -60, opacity: 0, duration: 0.35, ease: "power3.in" }, 2.6);
  window.__timelines = window.__timelines || {};
  window.__timelines["scene-1"] = tl;
</script>
```

Four eases appear in one scene, the exit is about 40% shorter than the entrance, and the headline never moves after
it lands.

## Title entrances that land and hold

A title has three phases: it enters, it holds, it leaves. While it holds it is completely still; the motion passes to
something else (the next element, the camera, the world behind it). Pick the entrance from what kind of title it is,
and change it from title to title within one film:

| The title is... | Entrance | The numbers |
|---|---|---|
| a person's or product's name | letter by letter | each letter 0.1 s after the last, opacity from 0.3 to 1 with a slight blur |
| a sentence with one variable word | slot roll on that word | the word cycles through options at about 0.1 s per roll |
| a short punch line | the whole line comes into focus | blur from 8 px to 0 in 0.13 to 0.2 s |
| a quiet statement | word by word, pale grey darkening to full ink | no movement; 0.07 to 0.1 s between words |
| a headline | word by word, out of blur | per word `blur(6px)` to 0 and opacity 0 to 1 over 0.13 s, each word 0.067 s after the last, no translate |

The hold is set by reading time: a line meant to be read stays 0.3 s per word on top of a 0.5 s base, so a six-word
line needs 2.3 s, and the last line of the film stays at least 2 s. To leave, it blurs and fades in 0.13 to 0.25 s, either one word at a
time or carried out by the scene's own move. For size, a title takes 4 to 9% of the frame height and a quieter line 2.5 to
4%; one word may carry the accent colour.

## Springs by damping ratio

A spring's character is set by one number, its damping ratio. Choose by the feel the element needs:

| Feel wanted | Damping ratio | Fits |
|---|---|---|
| cartoon | below 0.3 | a mascot landing after a jump |
| playful | 0.4 to 0.6 | a sticker or badge popping onto a card |
| premium, under control | 0.7 to 0.85 | a product card settling into place |
| no overshoot | 1.0 | a data panel or a table |

Only position and scale may overshoot; opacity and colour never do. Among GSAP's built-in eases, `back.out(1.4)` and
`elastic.out(1, 0.5)` come nearest to a spring. Writing the spring in closed form, as a function of time, lets any
single frame be rendered on its own; formulas are in [references/easing-and-timing.md](references/easing-and-timing.md).

## Cuts, holds and rhythm

Rhythm is contrast between shot lengths. A sketch for a 20-second promo, written down before any build:
`fast-fast-SLOW-fast-SHADER-hold`. The ranges behind those words:

- montage shots: 0.13 to 0.8 s each;
- ordinary shots: 1.8 to 3 s on average, with motion inside them;
- a product demo: one framing kept for 7 to 10 s while the interface does the work;
- the hold before a payoff: 0.3 to 0.75 s, after which the payoff runs at normal speed.

Place a cut on the frame where a move is fastest, and keep its direction and speed matched across the cut. When a click
opens a new screen, the cut falls on the rebound of the click, and the new screen arrives a touch oversized and settles. Beat
grids for music, the build-breathe-resolve shape of a scene and rhythm templates are in
[references/choreography.md](references/choreography.md).

Motion that may keep running is motion with a reason: a 3D world turning, a background stage orbiting slowly at 3 to
5 degrees per second, a character acting, footage playing, or the product's interface at work.

## Fixing motion notes

What a person says about motion is rarely the literal change to make. Read the note, then change only what it asks:

| The note | What it usually means | Change |
|---|---|---|
| "it feels flat" | everything moves alike | mix eases and directions, add depth layers, give one element a far larger move |
| "it feels like slides" | each scene starts from scratch | let an object already on screen lead into the next scene; cut while a move is in flight |
| "the titles move" | drift left on after the landing | land each title, then freeze it until its exit |
| "speed this up" | the beat is too long | quicken the content and trim that same time off the beat, so every later beat starts earlier |
| "too fast" | the camera rushes | run zooms and pans at 0.7 times their present speed and touch nothing else |

## Machine-made defaults

Viewers spot these patterns as generated:

- loops that breathe, float or pulse, standing in for real motion on titles or UI;
- titles that keep drifting or growing after landing, including a slow creep in scale or a late slow push;
- bouncing UI elements and click rings;
- an identical entrance for every scene, or every element fading up 30 px;
- a single ease and a single duration across the film.

## Planning a film's motion

After the beats are fixed, describe each one as an experience ("the number slams in and the wave ripples"), give
every element a motion verb, then a rhythm, then the transitions. The verb list and depth layers are in
[references/choreography.md](references/choreography.md).

## Verify the motion

```bash
# Eases in use: expect at least three per scene, and no single ease on every tween.
grep -ohE 'ease: *"[^"]+"' compositions/*.html index.html 2>/dev/null | sort | uniq -c | sort -rn
# Infinite loops do not belong on titles or UI in a seek-rendered film.
grep -nE 'repeat: *-1|infinite' compositions/*.html index.html 2>/dev/null
npx hyperframes snapshot --at 0,1,2,3 -o /tmp/motion-check      # frame 0 has content; titles still once landed
```

## Gotchas

- **Symptom:** the film feels generated though nothing is wrong. **Cause:** one ease and one duration everywhere.
  **Fix:** assign eases by role and vary durations.
- **Symptom:** "the titles keep moving". **Cause:** a slow scale or drift left on after the landing. **Fix:** end the
  title tween at the landing and move the camera or background instead.
- **Symptom:** entrances flicker like glitches. **Cause:** durations below about 0.3 s on large elements. **Fix:**
  lengthen them, or slow the whole film by about a second.
- **Symptom:** a cut feels like a jump. **Cause:** it falls on a slow frame or reverses direction. **Fix:** cut on the
  fastest frame with matching direction and speed.
- **Symptom:** text fades with a wobble. **Cause:** a bouncy ease on opacity. **Fix:** overshoot on position and
  scale only.

## Anti-patterns

| Do not | Do instead |
|---|---|
| one ease and one duration across a film | eases by role, at least three per scene |
| a slow creep on a title after it lands | freeze the title and pass the motion to the camera or background |
| overshoot on opacity or colour | overshoot on position and scale only |
| fixing flatness by adding motion | better eases, holds and one far larger move |

## Checklist

- [ ] Eases picked by role; three or more per scene.
- [ ] Exits shorter than entrances; overlaps of 30 to 50%; every stagger under 0.5 s.
- [ ] Titles land and hold still; a line to be read held for its 0.5 s base and 0.3 s a word.
- [ ] Frame 0 has content; the first motion starts 0.1 to 0.3 s in.
- [ ] Cuts on the fastest frame, direction and speed matched.
- [ ] The rhythm written down, with a hold before the payoff.
- [ ] None of the machine-made defaults left.

## References

- [references/easing-and-timing.md](references/easing-and-timing.md): frames and seconds, curves and their CSS equivalents, closed-form springs, beat arithmetic.
- [references/choreography.md](references/choreography.md): directing beats, motion verbs, depth layers, rhythm templates, velocity-matched cuts, GSAP rules that matter.

## See also

`video-storyboard`, `gsap`, `hyperframes-transitions`, `audio-sync`, `video-review`.
