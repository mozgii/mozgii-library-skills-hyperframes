---
name: hyperframes-cli
description: Runs the HyperFrames command line tool through the whole loop - scaffold with init and capture, check with lint and check, look at frames with snapshot and keyframes, edit clips with timeline, preview in Studio, render locally, in Docker or in the cloud, share a link with publish, and recover when Chrome or FFmpeg fail. Use when running any npx hyperframes command, reading its JSON output, or fixing a failed preview or render.
metadata:
  tags:
  - hyperframes
  - cli
  - render
  - preview
  - lint
  - check
  - snapshot
  - ffmpeg
---

# HyperFrames CLI

The HyperFrames CLI is the `hyperframes` npm package, run as `npx hyperframes <command>`. It scaffolds projects,
checks them, captures frames, serves the Studio editor and renders video. Checked against version 0.8.223.
It needs Node.js 22 or later and FFmpeg; it downloads a pinned Chrome on first use.

Each command answers `--help`, and most accept `--json`. When one fails it prints `✗ ...` followed by a `Fix:` line,
and the exit code is non-zero (2 for a flag that fails validation); with `--json`, every failure comes back in one
envelope shape.

## When to use this skill

Use this skill whenever a step runs the CLI: starting a project, checking a draft, looking at frames, handing over a
preview, rendering, or diagnosing a broken environment. What to write in the HTML is in `hyperframes`.

## Step 0: read the CLI and the machine

```bash
npx hyperframes --version
npm ls hyperframes --depth=0 2>/dev/null     # the version a project pins, if any
npx hyperframes doctor --json | jq .ok       # Chrome and FFmpeg; gate on this field
```

`render --start` and `--end`, and `beats <file>`, need 0.8.222 or later.

## Which command answers which question

Most of the work is asking the project a question and acting on the answer. Find the question, then run the command
beside it (each with `npx hyperframes`):

| You want to know or do | Run |
|---|---|
| Is this machine ready? Chrome, FFmpeg, versions | `doctor --json`, `browser ensure`, `upgrade` |
| A new project, from nothing or from a website | `init <dir>`; `capture <url>`; agent skills with `skills` |
| What is in this project? | `info`, `compositions`, `timeline --json`; a topic's docs with `docs <topic>` |
| Is the HTML well formed? (while writing) | `lint` |
| May it render? (the gate) | `check --json` |
| What does a frame, a path or the sound look like? | `snapshot`, `keyframes`, `compare`, `audio` |
| How close is this to an original video? | `diff <original> <render or .>`: SSIM, worst moments, cuts, duration, sound offset; non-zero exit under the bar |
| The numbers of one video: cuts, curves, look, face | `measure <subcommand>`: `probe`, `cuts`, `events`, `frames`, `extract`, `curve`, `energy`, `look`, `face`, `sync` |
| Move, trim or split a clip as Studio would | `timeline` with `move`, `trim`, `split`, `set`, `duplicate`, `delete`, `apply`, `undo`, `ids` |
| A ready-made block or component | `catalog` to browse, `add` to install (see `hyperframes-registry`) |
| Voice, words, cut-outs, beats, loudness, treatment | `tts`, `transcribe`, `remove-background`, `beats`, `normalize-audio`, `media-treatment` (see `hyperframes-media`) |
| Let a person watch it | `preview`, `play`, `present` |
| The video file, here or hosted | `render`; `cloud`, `lambda`, `cloudrun` |
| A shareable link | `publish` (sign in first with `auth login`) |
| Plans and credits | `billing subscribe`, `billing top-up --needed <credits>`: opens the page and waits until the account shows the change |
| Disk, speed, privacy | `clean`, `benchmark`, `telemetry` |

`validate`, `inspect` and `layout` are kept only as deprecated aliases of `check`; use `check`. `npx hyperframes help
<command>` prints one command's usage, and a mistyped command or flag gets the closest match suggested (0.8.212 on).

## The loop from draft to render

The loop from draft to render has five steps.

1. **Lint while writing.** Run `npx hyperframes lint` once the first draft exists and again whenever the structure
   changes; `--verbose` adds the info-level findings.
2. **Gate with check.** `npx hyperframes check --json` runs lint, then one Chrome session that audits runtime errors,
   layout, motion and contrast. Fix every error. If lint fails, the browser stage is skipped, `browserSkipped` is
   `true` and the output names the lint error as the reason; a report of "0 samples" means no frame was audited.
3. **Look at frames.** `npx hyperframes snapshot` writes PNGs under `.hyperframes/artifacts/snapshots/`. Read them.
   With several scenes, snapshot the middle of each, plus a frame just before and just after each cut.
4. **Hand over a preview.** Start `npx hyperframes preview --background`, make sure the URL returns HTTP 200, and
   send the person `http://localhost:<port>/#project/<project-name>`. Then stop, unless they wanted the file straight
   away or said not to stop.
5. **Render.** `npx hyperframes render --quality looks --output out.mp4`; use `draft` during iteration and `delivery`
   for the last one. Check that the file has bytes and that `ffprobe` reports the root's `data-duration`, then look
   at frames decoded from it.

Green checks by themselves never trigger a render; the person's approval does.

## Starting a project

Starting a project uses `init` for a blank or example project and `capture` for a website.

```bash
npx hyperframes init my-video --non-interactive          # blank 1920x1080; non-TTY shells do this anyway
npx hyperframes init my-video --resolution portrait      # 1080x1920; also square, landscape-4k, portrait-4k
npx hyperframes init my-video --video clip.mp4           # copies the clip and transcribes it
npx hyperframes init my-video --audio voice.mp3 --model small.en
npx hyperframes init my-video --tailwind                 # Tailwind v4 browser runtime
npx hyperframes init my-video --example kinetic-type     # only when an example is asked for
npx hyperframes capture https://example.com -o site-video --json
```

Examples: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`,
`product-promo`, `nyt-graph`. `--skip-transcribe` skips Whisper on supplied media; `--skip-skills` skips installing
agent skills.

## Looking at frames

A snapshot shows you the video's frames without a render.

```bash
npx hyperframes snapshot                         # 5 evenly spaced frames
npx hyperframes snapshot --at 1.2,4,7.5          # exact instants
npx hyperframes snapshot --range 3,5 --frames 8  # 8 frames inside seconds 3-5
npx hyperframes snapshot --composition intro     # frames inside one scene (an id, not a selector)
npx hyperframes snapshot --zoom "#cta"           # a sharp high-density crop of one element
npx hyperframes snapshot --review                # beat sheet, seam strips at every cut, phone-width sheet
npx hyperframes keyframes --json --selector '#title'   # every keyframe: property, time, value, ease
```

Details of `check`, motion sidecars and `snapshot --review`: [references/check-and-snapshot.md](references/check-and-snapshot.md).

## Rendering

Rendering writes the video. Defaults: MP4, H.264, `--quality looks` (CRF 16), the root's `data-fps` or 30.

```bash
npx hyperframes render --quality draft --output draft.mp4      # fast iteration
npx hyperframes render --quality delivery --fps 60 -o final.mp4
npx hyperframes render --format webm -o overlay.webm           # transparent VP9; mov gives ProRes 4444
npx hyperframes render --format gif --fps 15 -o demo.gif       # no audio, 1-bit transparency
npx hyperframes render -c compositions/intro.html -o intro.mp4 # one scene file
npx hyperframes render --start 12 --end 18 -o span.mp4         # one span as its own MP4, starting at 0 (0.8.222 on)
npx hyperframes render --docker --strict -o final.mp4          # reproducible across machines
npx hyperframes render --batch rows.json --output "renders/{name}.mp4"
```

On a laptop, half a minute of film usually takes one to two minutes to render, so keep the render in the
foreground. Every flag, the summary line and
cloud targets: [references/render-flags.md](references/render-flags.md). Codec and platform choices:
`render-and-export`.

## Editing clips from the CLI

Editing clips from the CLI makes the same edits Studio makes, so the project stays in Studio's shape.

```bash
npx hyperframes timeline --json                               # clips with #id refs, absStart, absEnd, file
npx hyperframes timeline move '#outro' 9 --plan --json        # preview the edit (+2 moves it 2 s later)
npx hyperframes timeline move '#outro' 9 --json               # apply it; prints a receipt
npx hyperframes timeline undo receipt.json                    # revert that edit
```

More verbs and batch plans: [references/timeline-edits.md](references/timeline-edits.md).

## Sharing a link with publish

`publish` sends the project up and answers with a lasting `hyperframes.studio` URL. The link does not depend on your
machine: no local server keeps running and no tunnel is opened. Ask the person before publishing: it sends the whole
project, media included, to a hosted service.

```bash
npx hyperframes publish --yes                       # unattended runs need --yes
npx hyperframes publish --update <url-or-id>         # update the same link (signed in)
```

A link published while signed out holds a claim token, and anyone with the link may take ownership of the project
after signing in: guard it like a password. For a link you own, sign in first with `npx hyperframes auth login`
(since 0.8.218 the HyperFrames CLI no longer shares its login with the HeyGen CLI, so sign in again once after
upgrading; a `HEYGEN_API_KEY` still works); `--public` makes a
claimed project visible to anyone.

## When a command fails

When a command fails, match the symptom:

| Symptom | Fix |
|---|---|
| FFmpeg not found | install it, or set `HYPERFRAMES_FFMPEG_PATH` and `HYPERFRAMES_FFPROBE_PATH` |
| Chrome missing or will not start | `npx hyperframes browser ensure`; then `npx hyperframes doctor --json` and gate on `.ok` |
| Chrome dies at once inside an agent sandbox | the sandbox blocks Chromium; render outside it, with `--docker`, or in the cloud |
| `capture` fails or writes `BLOCKED.md` | trust none of the partial output; capture again with a fresh `-o` folder |
| Footage in a rare codec shows as blank | `preview`, `play`, `check` and `publish` proxy it by default, so leave `--proxy` on; `snapshot` needs `--proxy`; `render` has no such flag and decodes the original |
| A heavy page times out before it is ready | give `check` or `snapshot` a longer `--timeout`, and `render` a longer `--browser-timeout` |
| Renders crawl on a Linux server | the summary line says `screenshot` capture on `software gpu`: that is the slow path |
| Disk tight | `npx hyperframes clean --dry-run`, then `clean`; never delete `.hyperframes` |

Diagnosis in depth: [references/environment.md](references/environment.md).

## Verify a run of the loop

```bash
npx hyperframes check --json | jq -e '.ok and (.browserSkipped | not)'
npx hyperframes render --quality draft -o /tmp/draft.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 /tmp/draft.mp4   # bytes, and the root's duration
ffmpeg -v error -ss 1 -i /tmp/draft.mp4 -frames:v 1 -y /tmp/frame.png                 # look at a decoded frame
```

A pass here says the toolchain works; the picture still needs your eyes.

## Checklist

- [ ] `lint` clean, then `check --json` with no errors and `browserSkipped: false`.
- [ ] Snapshots read: each scene's middle, the frames around every cut, the first frame.
- [ ] Preview URL includes `#project/<name>` and answers 200; the person approved it.
- [ ] The rendered file is there with bytes in it, and its `ffprobe` duration equals the root `data-duration`.
- [ ] Decoded frames of the render looked at, not only the preview.

## Gotchas

- **Symptom:** A CI step passes on a machine with no Chrome. **Cause:** `doctor --json` always exits 0. **Fix:** gate
  on its `ok` field, not the exit code.
- **Symptom:** A wait loop on a render never ends. **Cause:** `pgrep -f` matches its own loop, and the render was
  detached. **Fix:** run long renders in the foreground; if one must run detached, set
  `HYPERFRAMES_RENDER_DETACHED=1`, log to a file and wait with `until grep -qE 'Render (complete|failed)' render.log;
  do sleep 5; done`.
- **Symptom:** Studio opens with no project. **Cause:** The preview URL lacks `#project/<name>`. **Fix:** send the
  link with the hash.
- **Symptom:** The render is not where you looked. **Cause:** Without `--output`, renders go to
  `renders/<project>_<date>_<time>.mp4` in the project folder, from whatever directory the command runs (0.8.219 on).
  **Fix:** pass `--output` for a stable name.
- **Symptom:** You cannot tell which element the person means by "change this". **Cause:** Nothing read Studio's
  selection. **Fix:** run `npx hyperframes preview --context --json --context-fields selection`; `no-selection` means
  ask the person to click it.
- **Symptom:** JSON paths show `$HOME`. **Cause:** The CLI redacts the home folder in JSON. **Fix:** leave it; do not
  try to undo it.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `validate`, `inspect` or `layout` | `check`; the old names are deprecated aliases |
| reading "0 samples" as clean | treat `browserSkipped: true` as not audited |
| deleting `.hyperframes` | `clean --dry-run`, then `clean` |
| `publish` without asking | ask first: the whole project, media included, goes to a hosted service |
| rendering after every small edit | `snapshot` while iterating, `draft` for a real encode |

## References

- [references/render-flags.md](references/render-flags.md): every `render` flag, quality presets, the summary line, cloud, Lambda, Cloud Run.
- [references/check-and-snapshot.md](references/check-and-snapshot.md): audits, severities, motion sidecars, review sheets.
- [references/timeline-edits.md](references/timeline-edits.md): timeline verbs, plans, receipts, project history.
- [references/environment.md](references/environment.md): doctor, browser, FFmpeg, sandboxes, upgrades, telemetry, clean.

## See also

`hyperframes`, `hyperframes-automation`, `render-and-export`, `render-performance`.
