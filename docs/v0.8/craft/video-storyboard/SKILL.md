---
name: video-storyboard
description: Plans a short video before anything is built - the one idea and the viewer, three distinct storylines to pick from, the first two seconds, beats with their share of the running time, the shape of each video type (launch, explainer, data story, music video, character short, vertical clip, 3D piece, tutorial), a STORYBOARD.md the HyperFrames tools can parse, and a board of stills the person approves. Use when someone asks for a new promo, launch, explainer, ad, recap or music video, asks for a storyboard, script outline or concept, or when a draft has good motion but no story.
metadata:
  tags:
  - storyboard
  - storytelling
  - planning
  - concept
  - hooks
  - narrative
  - video
  - hyperframes
---

# Video storyboards

A storyboard decides what a film says before a single scene exists. Changing a sentence in a plan costs seconds;
changing a built scene costs a render loop. The usual failure of a programmatic video is polished motion with nothing
to say: features listed one after another, a row of three cards, a logo, a web address. This skill is the planning
step. Motion craft lives in `motion-design`, words in `video-copywriting`, the build in `hyperframes`.

## Does this film need a storyboard?

A storyboard pays off when the film has to carry an argument across several beats. Decide first:

| Request | Plan it? | Why |
|---|---|---|
| Launch, promo, explainer, recap, changelog or pull-request video, data story, narrative music video, longer than about 15 s | yes, the whole skill | several beats must add up to one point |
| One kinetic line, a single map move, a highlight on one image | no | the request already is the story |
| An edit to a project that exists, captions or overlays on footage | no | the story was decided when the footage was shot |
| The person brought a script, a board or a reference film | only the gaps | their plan wins; fill what it leaves open |

## Step 0: the brief the plan rests on

Every later choice is checked against a short brief, so write it first. Here is a filled one for a fictional
bookkeeping app, Ledgerly, launching bank-statement import:

```text
Claim:      You can now drop a bank statement and get categorised entries.
Takeaway:   "I don't type my statements in any more."   (the viewer's words, not a slogan)
Viewer:     a freelancer closing the month on the 30th, 11 pm
Their task: get March's 214 card payments into the books
Carried:    one real PDF statement, from drop to the finished ledger
Sources:    product page, release notes, the PM's message of 2 Oct
Assumed:    25-35 s, 16:9, music bed and no voice, stock music (free) not a paid track
```

Four rules keep the brief honest:

- **One claim.** A whole release is too much; take its headline feature.
- **One concrete thread.** A single real input (a file, a query, a number) enters in the hook and comes out in the
  payoff. For an explainer, the thread is one worked example.
- **Every on-screen claim has a source.** Never compute a claim the source did not state: "40 min to 2 min" does not
  license "20x faster". Example numbers carry an "illustrative" label. A screen you cannot capture is shown as a
  labelled placeholder rather than drawn.
- **Ask only what only the person knows**: real screens you cannot reach, whether there is a voice or music alone,
  words that must stay verbatim. Everything else goes in the "Assumed" line, with any paid item next to its free
  alternative.

When the film will be built here, read the tools the plan leans on:

```bash
npx hyperframes --version     # the STORYBOARD.md parser ships with it
ls STORYBOARD.md STORYLINES.md 2>/dev/null
```

## Three storylines, each a different film

Change two things to get a new storyline: what happens in it (the device) and how the camera and the edit carry it
(the form). Swap only the copy and you have the same film under another title. Before choosing, list five or more
device-and-form pairings in a line each, cross out any the subject is too thin for, and keep the three that differ the
most. At least one of the three should be braver than your first instinct.

Start from what the subject already has. Each row names a trait to look for, the device it suggests, a form that
suits it, and how the Ledgerly brief would use it:

| The subject has... | Device | A form that fits | Ledgerly as this storyline |
|---|---|---|---|
| a familiar deadline | someone's evening, the clock, a text that makes the deadline real | hand-off chain: each shot ends on the object that opens the next | 11 pm on the 30th, a "books due" text, the PDF carried shot to shot into the app |
| a pain you can see | the old way in its own scene, then the quiet new way | match cut: one shape holds while the world around it changes | a stack of paper receipts becomes the ledger's row of entries |
| a striking figure in its sources | a real figure the film earns first, then turns into a physical thing | infinite zoom: a detail grows into the next world | "214 payments" as 214 tiles, zooming into one that becomes its category |
| beautiful output | the ending shown first, then the camera backs away to where it started | one unbroken move with no cuts, travelling between worlds | the finished March ledger, pulled back to the drop zone it came from |
| an input people recognise | a what-if question with the real input in the blank | several panes playing at once that fold into the one that matters | "What if this statement filled in your books?" over four bank PDFs |
| an abstract process | a character (mascot or cursor) doing the job, every cut caused by an action | beat cuts: hard cuts with the music, type and colour blocks swapping each half beat | the cursor drags rows to categories in time with the track |
| a mechanism worth showing | a machine or model, toured by the camera; how it runs is the point | any of the above; the tour is usually one unbroken move | the import as a sorting machine the camera rides through |

The forms carry their own costs: an unbroken move needs every world laid out in advance, a hand-off chain needs a
matching object at every seam, an infinite zoom needs art that holds up when scaled, beat cuts need a track with a
clear grid, a match cut needs a shape that recurs, and the many-panes form makes the early frames busy. Three options
that all cut plainly from scene to scene mean the forms were never tried.

Each storyline goes on a card. The card holds a name; the device and form paired in a phrase; two sentences on the
picture and the feeling it leaves; the opening two seconds, word for word; the beats on one line
(`hook -> ... -> end card`); one line of look and one of sound. Open with the one you recommend and the reason in a clause; save all three cards in
`STORYLINES.md`, because a later turn may switch.

- **Someone is there to answer:** present the cards and stop until they choose. Taking the opening of one card and
  the middle of another still makes one storyline, not two.
- **The request was for the finished file, or said not to pause:** build the recommended card and give the other two
  a line each in the reply.

## Opening seconds and frame 0

Most players show frame 0 as the thumbnail before anyone presses play, so it is never black and never a logo alone.
No other stretch of the film carries as much as the first two seconds. Ways in that work: the feature already busy
on something the viewer knows, an everyday moment where the need shows up, a question with the real input inside it,
or the problem on screen. Next, let the old way fail where the viewer can see it, and bring the product in as the
relief. An empty prompt box being typed into as the very first shot marks the film as generated. Hook patterns, hook
budgets per platform and narrative arcs: [references/hooks-and-arcs.md](references/hooks-and-arcs.md).

## Beat plan for a 35-second launch

A beat is one step of the story with a single job and its own slice of the running time. When a launch runs near
35 s, the proof gets the biggest slice, about 40%. The payoff takes about 20%, the tension about 12%, and the hook, the
reveal, the claim and the end card about 8% each. Scale the slices to the length and let the device bend them. Here is
the Ledgerly launch laid out on that split:

| Ledgerly at | Beat | Its job, in this film |
|---|---|---|
| 0-4 s | hook | the 11 pm message and the unopened statement: world and need, or the feature already mid-task |
| 4-7.8 s | tension | the old way failing in view: 214 rows typed by hand, one typo highlighted |
| 7.8-10 s | reveal | "Ledgerly reads statements" as a title; a reveal sits about 20 to 30% into the film |
| 10-24 s | proof | the actual job done in the product's own screens, as 3 to 6 verbs with a beat each: drop, match, review, post |
| 24-31 s | payoff | the categorised March ledger arrives already moving; the single biggest moment, 60 to 80% in |
| 31-35 s | claim, then end card | the claim in one line; the mark flies in, and the name and call to action hold for 2 to 3 s |

During the proof, clear the screen down to the cursor's targets and the evidence for the line on screen. Speed the
process up; give the payoff real time at normal speed. Length comes from the story: most feature launches run 20 to
45 s, and when a request names a length, treat it as a range to land inside, never a target to pad toward. The beat shapes for
explainers, data stories, music videos, character shorts, vertical clips, 3D pieces, tutorials and changelogs:
[references/video-types.md](references/video-types.md).

## STORYBOARD.md: the file the HyperFrames parser reads

`STORYBOARD.md` sits at the project root, and `@hyperframes/core/storyboard` parses it. YAML front matter holds the
film-wide direction (`format`, `duration`, `message`, `arc`, `audience`); each frame is a `## Frame N - Title`
heading followed by `- key: value` bullets, and keys the parser does not know are kept as extra data. Give every
frame a `reads` line (what the viewer must take in, in order, each with a time window) and a `sound` line, so whoever
builds and whoever reviews test against the same plan.

The Ledgerly launch, first two frames:

```markdown
---
format: 1920x1080
duration: 35s
message: "Drop a bank statement, get your books done"
arc: Hook -> Tension -> Reveal -> Proof -> Payoff -> End card
audience: freelancers doing their own bookkeeping
---

## Frame 1 - Hook (0-4.0s)
- scene: 11:04 pm on the 30th; a 9-page PDF statement sits on an empty desk
- duration: 4.0s
- transition_in: cut
- status: outline
- reads: the clock and the date (0.0-2.0s); "214 payments to enter" lands (2.0-4.0s)
- sound: low bed starts on a downbeat; a single clock tick

## Frame 2 - Tension (4.0-7.8s)
- scene: a spreadsheet fills one row at a time while the clock races
- duration: 3.8s
- transition_in: match cut on the PDF page edge
- status: outline
- reads: rows creep in (4.0-5.8s); "Row 12 of 214" lands (5.8-7.8s)
- sound: keyboard taps speed up; the bed thins out
```

`status` climbs from `outline` to `built` (layout confirmed) to `animated`. Once a frame's scene file exists, `src`
points at it; `poster` gives the second to show on its tile. The windows in `reads` must not overlap, and each one
needs time for its words: roughly 0.3 s per word plus 0.5 s, with at least 2 s for the last line.

## Stills board for sign-off

A stills board turns the plan into pictures the person can mark up before any motion exists. Pose each frame inside
the root composition at its key moment, with the real copy, fonts and colours, and capture all of them in a single
run. `--no-end` leaves out the extra final frame. Every run empties its `-o` folder first, so a single redone frame
must never be snapshotted into the board folder:

```bash
npx hyperframes snapshot --at 1.2,3.6,7.0,11.5,16.0,21.5 --no-end -o boards/stills
```

Build `boards/storyboard.html` with one card per frame (the still, `NN: name`, its time range, a line of action),
then stop until the person gives the go. Feedback on a frame changes that frame alone. Afterwards, return the moving
film to `index.html` and give the board a page of its own; frozen frames inside the preview play like a slideshow.

## Generated-film tells to ban

These are the patterns a plan slides into when nobody makes a decision:

- a single dark canvas with small interface pieces floating in it from start to finish, rather than several worlds;
- a row of three cards, or the feature list turned into slides;
- each scene arriving with the identical entrance, or one move repeated beat after beat;
- a small logo parked in a corner from the first frame, rather than one weighty arrival near the end;
- "Introducing", "Meet" or the logo as the opening line;
- narration that reads out the sentence already on screen.

When a first render shows one, name it, pick a replacement that comes out of the subject or the brand identity, and add it to a "banned"
line in the plan so later turns stay clear of it.

## Verify the plan before building

This check reads the `reads` windows of a STORYBOARD.md and flags any that overlap or are too short for their words
(each needs 0.3 s for every word on top of a 0.5 s base):

```bash
python3 - STORYBOARD.md <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
bad = 0
for frame, body in re.findall(r"^##+ (Frame[^\n]*)\n(.*?)(?=^##+ |\Z)", text, re.M | re.S):
    m = re.search(r"^- reads:\s*(.+)$", body, re.M)
    if not m:
        print(f"{frame}: no reads line"); bad += 1; continue
    end_prev = None
    for words, a, b in re.findall(r"([^;()]+)\((\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)s\)", m.group(1)):
        a, b, n = float(a), float(b), len(words.split())
        if end_prev is not None and a < end_prev:
            print(f"{frame}: window at {a}s overlaps the one before"); bad += 1
        if b - a < 0.3 * n + 0.5:
            print(f"{frame}: '{words.strip()}' needs {0.3 * n + 0.5:.1f}s, has {b - a:.1f}s"); bad += 1
        end_prev = b
print("ok" if not bad else f"{bad} problem(s)"); sys.exit(1 if bad else 0)
PY
```

Then check by eye: the beats add up to the length range, the payoff sits 60 to 80% in, and frame 0 shows content.

## Gotchas

- **Symptom:** the person cannot tell the three storylines apart. **Cause:** only the copy differs. **Fix:** change
  the device or the form of two of them.
- **Symptom:** every beat flashes by in under 2 s. **Cause:** six beats squeezed into 12 s. **Fix:** cut beats; never
  shorten holds below reading time.
- **Symptom:** the client asks where "3x faster" came from. **Cause:** a number derived from the source rather than
  stated in it. **Fix:** remove it or label it illustrative.
- **Symptom:** the preview plays as a slideshow after the board was made. **Cause:** posed stills left in
  `index.html`. **Fix:** restore the moving film and keep the board in a separate page.
- **Symptom:** captions drift off the words on footage. **Cause:** captions were made before the cut. **Fix:** cut
  first, then caption the cut file (`talking-head-edits`).

## Anti-patterns

| Do not | Do instead |
|---|---|
| three storylines that differ in copy only | change the device or the form |
| padding toward a named length | treat it as a range to land inside |
| computing a claim the source did not state | use the stated figure, or label it illustrative |
| snapshotting one redone frame into the board folder | every run empties `-o`, so capture all frames in one run |

## Checklist

- [ ] Brief written: claim, takeaway, viewer and task, carried input, sources, assumptions.
- [ ] Three storylines with different devices or forms; one recommended; the pick recorded in `STORYLINES.md`.
- [ ] Frame 0 shows content, and the hook works with the sound off.
- [ ] Beats fit the length range; the payoff is 60 to 80% in and plays at normal speed.
- [ ] Every frame of STORYBOARD.md has `reads` and `sound`; the Verify script prints `ok`.
- [ ] The person approved the storyline (and the stills, when a board was made), or asked not to be stopped.

## References

- [references/hooks-and-arcs.md](references/hooks-and-arcs.md): hook patterns, hook budgets per platform, narrative arcs with their lengths.
- [references/video-types.md](references/video-types.md): beats, devices and tells for each type of video.

## See also

`motion-design`, `video-copywriting`, `video-design-system`, `hyperframes`, `website-to-hyperframes`.
