---
name: hyperframes-slideshow
description: Builds HyperFrames slideshows presented live instead of rendered - slides as top-level scenes, a JSON island listing slides, fragment reveals, branching hotspots and presenter notes, served with hyperframes present - and ports an existing web page into a deck. Use when the person wants a presentation, pitch deck or talk with HyperFrames motion rather than an MP4.
metadata:
  tags:
  - hyperframes
  - slideshow
  - presentation
  - deck
  - present
  - fragments
---

# HyperFrames slideshows

A deck in HyperFrames is an ordinary composition with one extra piece: a JSON island naming which scenes are slides
and how they link. What you hand over is a deck running in the browser through `npx hyperframes present`, with
presenter mode, notes and navigation. There is no video file. Every rule of the `hyperframes` composition contract
still holds. Checked against CLI 0.8.223.

## Step 0: read the CLI and find any island

```bash
npx hyperframes --version
grep -rln 'application/hyperframes-slideshow+json' --include='*.html' . # an existing deck
```

No match means this is a new deck, or a video project that needs the island added.

## Deck or video?

| The person wants | Build |
|---|---|
| A talk, pitch, keynote, or scenes to click through live | a slideshow (this skill) |
| A web page turned into a presentation | a slideshow, porting the page (below) |
| A file to upload or send | a video (`hyperframes`); a deck is never rendered to MP4 |
| Stills of some slides for a document | a slideshow, then `snapshot --at` per slide |

## How a deck differs from a video project

- **Slides are top-level scenes.** Each has `data-composition-id`, `data-start`, `data-duration`, `data-label`,
  `data-width` and `data-height`, and no master root composition wraps them.
- **Moving between slides seeks.** Nothing plays during navigation, so every resting state has to look finished when
  the timeline jumps straight to it.
- **Slide text is large.** Anything the audience must read is 40 px or more at 1920×1080.
- **Search before drawing.** For a named visual, `npx hyperframes catalog --query "<the visual, in English>" --json`
  ranks the whole registry without installing anything.

## Worked example: a pitch with a branch slide

Three main slides and one detail slide reachable from a hotspot. The island sits near the top of `<body>` as literal
HTML; `present` reads the file without running it, so a script must never generate the island.

```html
<body>
  <script type="application/hyperframes-slideshow+json">
    {
      "slides": [
        { "sceneId": "opening", "notes": "Let the 214 sink in before clicking." },
        {
          "sceneId": "pain",
          "fragments": [8.5, 11.0],
          "hotspots": [
            { "id": "why-hours", "label": "How did we measure 6 hours?", "target": "method",
              "region": { "x": 60, "y": 70, "w": 30, "h": 15 } }
          ]
        },
        { "sceneId": "ask" }
      ],
      "slideSequences": [
        { "id": "method", "label": "Measurement method", "slides": [{ "sceneId": "method-detail" }] }
      ]
    }
  </script>

  <div id="opening" data-composition-id="opening" data-label="Opening" data-start="0" data-duration="6"
       data-width="1920" data-height="1080"><!-- slide content --></div>
  <div id="pain" data-composition-id="pain" data-label="The pain" data-start="6" data-duration="8"
       data-width="1920" data-height="1080"><!-- reveals at 8.5 s and 11.0 s --></div>
  <div id="ask" data-composition-id="ask" data-label="The ask" data-start="14" data-duration="5"
       data-width="1920" data-height="1080"></div>
  <div id="method-detail" data-composition-id="method-detail" data-label="Method" data-start="19"
       data-duration="5" data-width="1920" data-height="1080"></div>
</body>
```

The `pain` slide runs from 6 to 14 s on the timeline, so its fragments at 8.5 and 11.0 are absolute times inside that
range, not offsets from the slide's start.

## Island fields

| Field | What it holds | Rule |
|---|---|---|
| `sceneId` | the slide's scene | equals its `data-composition-id`; `startTime` and `endTime` may be given instead |
| `notes` | presenter notes | shown only to the presenter |
| `fragments` | the click stops inside a slide | absolute times on the timeline clock (the one `data-start` uses), within the slide; each click seeks to the next; a slide without fragments opens on a rest frame inside it |
| `hotspots` | clickable areas that branch | `target` is the `id` of a sequence; `region` is a box in percent, left out for a whole-slide button; Back returns to the slide with the hotspot |
| `slideSequences` | branch slides | scenes listed here only, never in the main `slides` list |
| `ttsScript`, `ttsAudioUrl`, `ttsDurationMs` | reserved | not wired up yet; leave them out |

## Running the deck

```bash
npx hyperframes check --json        # also checks sceneIds, hotspot targets, fragment ranges, overlapping main slides
npx hyperframes present ./my-deck   # prints the URL to hand over
npx hyperframes snapshot --at 2,9,15   # stills of chosen slides
```

Hand the URL over with one instruction: the audience tab opens from the Present button or the P key. Opening the
project's `index.html` should already give a working deck, a `<hyperframes-slideshow>` wrapped around
`<hyperframes-player src="...">`; the raw composition may move to a subfolder for that. The component already provides
Present (P), previous and next, the slide counter, a global mute, fullscreen, swipe, hotspots, presenter notes that
can be edited and are kept per deck, and stopping media when a slide is left. Do not build your own versions of these.

Screen sharing differs by app. Google Meet can share the audience tab directly, and the tab goes on rendering while
hidden. Zoom needs the tab pulled out into a window of its own, and that window is what you share; a window covered completely by others
freezes. Opening a deck straight from the player bundle, without `present`, takes extra work this skill does not cover.

## Turning a web page into a deck

A port keeps what the page looks like and how it behaves:

- Carry over its look, motion, interactions and media, and port its widgets and players instead of imitating them.
- Movement the page tied to scrolling, the wheel or a camera layer turns into a camera move from focal point to
  focal point as the presenter navigates. The page itself never visibly scrolls, and moves go straight to their target without
  reversals the source did not have.
- Treat screenshots, posts, charts, code and every image containing readable text as evidence: preserve the aspect with
  `object-fit: contain` and check all four edges for cropping.
- Each copied `<video>` or `<audio>` gets `data-start` and `data-duration`, plus `data-has-audio="true"` when its
  sound should play, and loses any `preload="none"`. Custom media controls read the native element's events and
  `currentTime`, never a timer of their own.
- Slides stacked and hidden need all three of `opacity: 0`, `visibility: hidden` and `pointer-events: none`;
  otherwise an invisible slide on top eats the clicks.

## Verify the deck

```bash
npx hyperframes check --json                    # clean, including the slideshow checks
npx hyperframes snapshot --at 8.5,11.0          # each fragment stop looks finished when seeked to directly
grep -c 'application/hyperframes-slideshow+json' index.html compositions/*.html 2>/dev/null   # one island per composition
```

Open the URL from `present`, press P, and click through every slide and hotspot once.

## Gotchas

- **Symptom:** the MP4 of a deck holds only the first slide. **Cause:** `render` takes just the first scene of a deck
  and drops the rest without a warning. **Fix:** present the deck live; use `snapshot --at` for stills.
- **Symptom:** a click stops on a half-finished animation. **Cause:** the fragment time falls mid-tween. **Fix:** move
  it to a point where everything has come to rest.
- **Symptom:** clicks on one slide do nothing. **Cause:** a hidden slide stacked above lacks `pointer-events: none`.
  **Fix:** hide with opacity, visibility and pointer events together.
- **Symptom:** the presenter sees no slides at all. **Cause:** the island was generated by a script. **Fix:** write
  it as literal HTML.

## Anti-patterns

| Do not | Do instead |
|---|---|
| rendering a deck to MP4 | present it live; `snapshot --at` for stills |
| building your own Present button or counter | use what the component provides |
| generating the island in a script | literal HTML; `present` reads the file without running it |
| fragment times relative to the slide | absolute times on the timeline clock |

## Checklist

- [ ] Every slide is a top-level scene with a `data-label`.
- [ ] The island is literal HTML; each `sceneId` and hotspot `target` resolves.
- [ ] Each fragment stop looks right when seeked to directly.
- [ ] `check --json` clean; slide text at least 40 px at 1080p.
- [ ] The URL from `present` handed over, with the Present or P instruction.

## See also

`hyperframes`, `motion-design`, `video-design-system`.
