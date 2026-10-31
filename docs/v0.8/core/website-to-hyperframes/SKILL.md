---
name: website-to-hyperframes
description: Turns a website URL into a HyperFrames video - capture the site with hyperframes capture, read its screenshots, tokens, text and assets, write a brand DESIGN.md, a narration script and a beat storyboard, generate the voiceover, map word timings to beats, build one scene per beat and validate. Use when someone shares a link and wants a product tour, launch video, social ad or feature announcement made from that site.
metadata:
  tags:
  - hyperframes
  - website
  - capture
  - product-video
  - storyboard
  - voiceover
---

# Website to HyperFrames video

Website to HyperFrames video is a seven-step workflow that starts from a URL and ends with an approved preview. Each
step writes a file that gates the next one, so the brand, story and timing are settled before any scene is built.
Checked against CLI 0.8.223.

## When to use this skill

Use this skill when the subject of a video is a website or web product: "capture this site and make a 25-second
launch video", "turn this page into a 15-second ad for vertical feeds", "make a product tour from this URL". The work
starts from the page's URL with `npx hyperframes capture` (Step 1).

## Step 0: read the CLI and the machine before capturing

```bash
npx hyperframes --version
npx hyperframes doctor --json | jq .ok     # capture needs Chrome
curl -sI https://example.com | head -1     # the URL answers from here
```

A staging or local URL beats production when one exists.

## Video types from a website

Video types from a website have typical lengths and beat counts:

| Type | Length | Beats | Narration |
|---|---|---|---|
| Social ad | 10 to 15 s | 3 to 4 | an optional hook line |
| Launch teaser | 10 to 20 s | 2 to 4 | minimal, high energy |
| Feature announcement | 15 to 30 s | 3 to 5 | full |
| Brand reel | 20 to 45 s | 4 to 6 | optional, music first |
| Product demo | 30 to 60 s | 5 to 8 | full |

Match the site's main orientation: a mobile-first product often reads better in 1080×1920.

## Step 1: capture the website or landing page URL

Step 1 captures the site or landing page from its URL into the project with `npx hyperframes capture` and builds a
written summary.

```bash
npx hyperframes capture https://example.com -o product-video/capture --json
```

Treat a non-zero exit, `ok: false` or a `BLOCKED.md` in the output as a hard stop: use nothing from a blocked capture
and retry into a fresh folder. Then read, writing one or two sentences after each file: the scroll screenshots
(`screenshots/scroll-000.png` is the hero), `extracted/tokens.json`, `extracted/visible-text.txt`,
`extracted/asset-descriptions.md`, and when present `animations.json`, `lottie-manifest.json`,
`video-manifest.json` and `shaders.json`. Gate: print the site's name, top colours with roles, fonts, section count,
key assets and a one-line vibe. What each file holds: [references/capture-and-brand.md](references/capture-and-brand.md).

## Step 2: write DESIGN.md

Step 2 writes `DESIGN.md`, a brand cheat sheet of under 100 lines with six sections: Overview, Colors (exact hex from
`tokens.json` with roles), Typography, Elevation, Components (named as seen) and Do's and Don'ts. It is a reference,
not the creative plan. Template and token rules: [references/capture-and-brand.md](references/capture-and-brand.md).

## Step 3: write SCRIPT.md

Step 3 writes the narration script, the backbone of the video: scene lengths come from it. Use the site's real
features and exact numbers from `visible-text.txt`. Hold each scene to roughly 19 spoken words, and give everything
that appears a phrase of its own, so every reveal has a word to land on. Narration rules: `video-copywriting`.

## Step 4: write STORYBOARD.md

Step 4 writes per-beat direction: VO cue, visual description, the assets used, motion, transition into the next
beat, depth layers and sound. It starts with global direction and an asset audit table that assigns every useful
asset to a beat or marks it SKIP. Format: [references/storyboard-and-build.md](references/storyboard-and-build.md).

## Step 5: voiceover and timing

Step 5 generates the narration and turns word timings into beat times.

```bash
npx hyperframes tts SCRIPT-spoken.txt --voice af_nova -o assets/narration.wav
npx hyperframes transcribe assets/narration.wav --model small.en --json
```

Audition two or three voices on the first sentence before generating the whole script. Save the exact spoken text,
with pronunciation fixes (`API` as "A P I", `$2T` as "two trillion"), separately from the creative script. For each
beat, set start to its first word's `start` and end to its last word's `end` plus 0.3 to 0.5 s, then update the
storyboard and the scene hosts' `data-start` and `data-duration`.

## Step 6: build the scenes

Step 6 builds one scene per beat with the `hyperframes` contract: the static hero frame first, snapshot it, then
entrances timed to the VO cues, mid-scene activity, and the transition. After each scene, check that every asset the
storyboard assigned appears in the HTML by file name, and that captured fonts are loaded with `@font-face` from the
project rather than a web font service. Build rules: [references/storyboard-and-build.md](references/storyboard-and-build.md).

## Step 7: validate and deliver

Step 7 runs the checks and hands over the preview.

```bash
npx hyperframes check --json
npx hyperframes snapshot --review
npx hyperframes preview --background
```

Give the person `http://localhost:<port>/#project/<project-name>`, not the `index.html` path. Render only when they
approve or ask for the file.

## Verify the film against the capture

```bash
test ! -f product-video/capture/BLOCKED.md && echo "capture usable"
npx hyperframes check --json                     # no errors
npx hyperframes snapshot --review                # every beat, every seam, the phone sheet
grep -rlE 'fonts.googleapis|fonts.gstatic' compositions index.html   # expect nothing: fonts come from the project
```

Check each number on screen against `extracted/visible-text.txt`.

## Checklist

- [ ] Capture succeeded (`ok: true`, no `BLOCKED.md`, usable assets and text).
- [ ] `DESIGN.md` uses exact hex values and only weights the brand font ships.
- [ ] Script uses real features and numbers; scenes about 19 words or fewer.
- [ ] Every beat's times come from the transcript, not estimates.
- [ ] Every assigned asset is referenced; real screenshots shown rather than rebuilt pages.
- [ ] `check` clean, review sheets read, preview URL handed over.

## Gotchas

- **Symptom:** Cookie banners and paywalls in the capture. **Cause:** Production pages often carry them, and A/B
  overlays too. **Fix:** capture a staging or local URL when one exists.
- **Symptom:** The wrong accent colour. **Cause:** Default link blue `#0000EE` and the reds and greens of status
  messages were taken for the brand. **Fix:** take the captured colour that appears in the most roles.
- **Symptom:** Icons where words should be. **Cause:** An icon font such as Font Awesome or icomoon was used as body
  type. **Fix:** never use one as the display or body face.
- **Symptom:** Fake bold. **Cause:** A weight the brand font does not include. **Fix:** stick to the weights it ships;
  asking for 600 or 700 without the files gives synthetic bold.
- **Symptom:** The page looks slightly wrong. **Cause:** Rebuilt HTML drifts from the real layout. **Fix:** show the
  screenshots and rebuild only what moves.
- **Symptom:** An empty capture that says ok. **Cause:** A "very little text content" note plus an empty asset catalog
  means the capture failed, whatever its status says. **Fix:** capture again into a fresh folder.

## Anti-patterns

| Do not | Do instead |
|---|---|
| using anything from a blocked capture | retry into a fresh folder |
| estimating beat times | take them from the transcript |
| loading fonts from a web font service | `@font-face` from the project |
| rendering before approval | hand over the preview URL with `#project/<name>` |

## References

- [references/capture-and-brand.md](references/capture-and-brand.md): capture flags and files, reading order, DESIGN.md template.
- [references/storyboard-and-build.md](references/storyboard-and-build.md): storyboard format, asset audit, per-scene build loop.

## See also

`video-storyboard`, `hyperframes`, `hyperframes-cli`, `video-copywriting`, `motion-design`, `video-review`.
