---
name: video-review
description: Reviews a HyperFrames video the way a first-time viewer and a demanding motion director would - check warnings, review sheets of every beat, seam strips at every cut and a phone-width sheet, motion samples around the payoff, audio facts from the rendered file - then ranked notes (P0, P1, P2) with exact fixes and a REVIEW.md delivery note. Use when someone asks for feedback, a critique or a quality pass on a video, after check passes on any new film or timing change, before handing over a preview or rendering, and when output feels flat, generic or hard to read.
metadata:
  tags:
  - review
  - quality
  - critique
  - hyperframes
  - motion
  - snapshot
  - delivery
---

# Video review

The person who built a timeline knows what happens in it; a viewer gets one pass at full speed, quite often on a
phone screen. Review closes that gap. `check` reports what is broken, and review reports what is weak. Run a review once
`check` passes: for each new film, for each edit that shifts timing or layout, and before replying or rendering.

## Which pass finds what

| Pass | Finds | Tool |
|---|---|---|
| `check` | broken contract, errors, measurable craft warnings | `npx hyperframes check --json` |
| Review (this skill) | weak story, poor reads, generic motion, bad seams, sound gaps | sheets, motion samples, your judgement |
| Render testing | regressions, nondeterminism, broken files | `render-testing` |

Use this skill before a preview goes out, before a delivery render, when someone wants honest feedback before
publishing, and whenever a film is called flat, generic, busy, slow or hard to read.

## Step 0: collect the measured facts

Opinions come after numbers. Gather them in one go:

```bash
npx hyperframes check --json                                   # errors and craft warnings
npx hyperframes snapshot --review                              # beat sheet, seam strips, phone sheet
npx hyperframes snapshot --range 6.5,8 --frames 8              # frames around the hero move or payoff
npx hyperframes keyframes --shot hero.png --selector '#hero'   # a path that should arc or land
npx hyperframes audio renders/final.mp4 --json                 # is there sound, where it hits, how loud
```

The craft warnings from `check` are prompts to decide, not rules:

| Warning | Fires when | Usual decision |
|---|---|---|
| `line_unread` | a line leaves before it can be read | lengthen the hold or cut words |
| `dead_stretch` | more than 3 s pass with nothing changing | add a move or cut the time; a deliberate hold carries `data-hold` |
| `text_below_floor` | text smaller than 2.6% of the frame's shorter edge | enlarge it or drop it |
| `first_frame_empty` | frame 0 is blank, though social players use it as the thumbnail | pose content at 0 s |
| `film_silent` | a film over 15 s has no sound | add a bed, or say why it is silent |

Each warning is either fixed or kept with a stated reason. Where your eye and the numbers disagree, believe the
numbers: a 0.6 s line or a clipped label passes unnoticed on a sheet of stills. The audio facts are measured, not heard;
say so in the note.

Add the CLI version to the delivery note, so a later reader knows which checks ran: `npx hyperframes --version`.

## What the review sheets show

`snapshot --review` writes three sheets:

- **Beat sheet:** each scene shortly after it begins and at its middle, plus every element marked `data-beat`.
- **Seam strips:** frames from 0.2 s before to 0.2 s after every cut.
- **Phone sheet:** the beat frames at 360 px wide.

Open all three before writing a note.

## The stranger pass

Read the sheets as someone who never saw the brief. Each row is one pass through the sheets:

| Pass | Look for | It is a P0 when |
|---|---|---|
| Name it | one sentence per beat frame naming every object | an object needs explaining before anyone gets it ("those bars are mirrors") |
| Follow it | each beat causing the next | a stranger loses the story |
| Words off | the story told by the pictures alone | the pictures say something else |
| Plan match | each beat against its frame in `STORYBOARD.md` | a frame contradicts the plan |
| Read as itself | materials, faces, product screens | a product screen looks like a mockup |
| Separation | subject against ground, one focal point | two focal points fight in the hero shot |
| Framing | crops, edges, platform UI, collisions at seams | text sits under platform UI |
| Timing | reads against their word counts, pops without a move, jumps at cuts, one curve for all | a line cannot be read in its time |
| Phone | every read line at 360 px | a line is unreadable |
| Sound | a bed under any film over 15 s, hits in sync with their picture, no clipping | a hit lands a frame after its picture on the hero beat |

Then list every generated-looking default on screen (the list is in `motion-design`) and plan its removal.

## Notes ranked P0, P1, P2

Rank a problem by asking who would suffer from it:

- **P0, the viewer loses the message or the contract breaks.** Text that is wrong or cannot be read, an element that
  is broken, a generated-film tell in the hero shot. A price that reads "$19" when the brief says "$29" is P0.
- **P1, the film is weaker than it could be.** A stretch where nothing happens, a payoff that lands without force, a
  seam that jumps. A camera that idles for two seconds before the reveal is P1.
- **P2, polish only a careful editor would catch.** A sound hit a frame late, a drop shadow a little heavy.

Each note is one line, rank first, then where the frame is, what is seen there, the fix, and what the fix must not
disturb:

```text
<rank> | <time> <place> | seen: <problem> | do: <exact change> | protect: <what stays>
```

## Worked example: notes on a 20-second launch film

```text
P0 | 00:00.0 frame 0       | seen: plain navy, no product        | do: pose the product shot at 0 s                  | protect: the fade that starts at 0.1 s
P0 | 00:04.2 scene 2 title | seen: 6 words on screen for 0.6 s   | do: hold 2.3 s, move the card to 6.5 s            | protect: the blur entrance
P1 | 00:11.8 seam 3/4      | seen: direction reverses on the cut | do: cut on the fastest frame, both moves leftward | protect: the cut point
P2 | 00:17.0 end card      | seen: whoosh 2 frames late          | do: shift it 0.08 s earlier                       | protect: its level
```

Every P0 gets fixed; a P1 gets fixed when it is worth what it costs. Sweep the list three times, in this order:
wording, then timing, then detail. Afterwards snapshot only the parts that changed, a single time, and run a second
pass only if a P0 is still open. A mark out of 10 is useless, because it does not point at a frame. A film that feels
busy loses roughly a third of its motion; the moves that guide the eye stay. If a fix will not take, grab a frame just
before the problem and one just after it, note every difference between them, and edit just the line responsible.

A second reviewer finds what the author cannot see. Hand a fresh agent or a colleague only `STORYBOARD.md` and the
three sheets, request P0 and P1 lines written the same way, and keep the editing to yourself. Before fixing, commit
or copy the project; a fix that backfires can then be rolled back.

## REVIEW.md: the delivery note

`REVIEW.md` goes at the project root, and its short form goes into the reply. The next session reads it before
touching anything:

```markdown
# Review: Ledgerly launch, 30 s, 2026-10-30
- Calls made: storyline B (ending first); A and C not built, kept in STORYLINES.md.
- Measured: check clean; audio peaks -1.2 dBTP, integrated -14 LUFS. Looked at only: colour on a phone.
  Not checked: sound by ear (measured, not heard).
- Weakest shot: 11-14 s, the import progress; with more time, show real rows landing.
- Warnings kept: dead_stretch at 24-27 s (data-hold on the payoff, on purpose).
```

## Verify the review

```bash
npx hyperframes check --json | grep -c '"severity": *"error"'    # expect 0 (or read the JSON)
test -f REVIEW.md && echo "delivery note written"
```

Then snapshot each frame named in a P0 line again and confirm the change is visible.

## Gotchas

- **Symptom:** the client sees a glitch the preview never showed. **Cause:** only the preview was reviewed; decoded
  render frames can differ (codecs, GPU paths). **Fix:** review frames from the render too.
- **Symptom:** the second version feels busier, not better. **Cause:** fixing flatness by adding motion. **Fix:**
  better eases, holds and one bigger move.
- **Symptom:** "7/10" in the notes and nothing changes. **Cause:** scoring instead of noting. **Fix:** write lines
  that name a time, a place and a change.

## Anti-patterns

| Do not | Do instead |
|---|---|
| a mark out of 10 | a line that names a time, a place and a change |
| reviewing the preview only | review frames from the render too |
| adding motion to fix flatness | better eases, holds and one bigger move |
| arguing with a measurement by eye | believe the numbers where they disagree |

## Checklist

- [ ] `check` free of errors; each craft warning fixed or kept with a reason.
- [ ] Beat, seam and phone sheets read; motion sampled around the payoff.
- [ ] Every beat named in one stranger's sentence; the story readable with the words covered.
- [ ] Notes written as `rank | time place | seen | do | protect`, ranked P0 to P2.
- [ ] Every P0 fixed and snapshotted again.
- [ ] `REVIEW.md` written.

## References

- [references/review-signals.md](references/review-signals.md): weak and strong signals in nine dimensions, with a fix for each weak one.

## See also

`motion-design`, `render-testing`, `hyperframes-cli`, `video-design-system`.
