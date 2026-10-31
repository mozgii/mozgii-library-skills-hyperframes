---
name: render-testing
description: Tests HyperFrames videos and their renders - the check gate in CI, motion sidecar assertions, snapshot regression against a baseline, frame-by-frame determinism checks with framemd5, verifying output files with ffprobe (duration, streams, black frames, silence, loudness), SSIM comparisons, Docker renders for byte-identical output, and batch render manifests. Use when setting up CI for video projects, when proving a change did not break other scenes, when renders differ between machines, or before delivering any render.
metadata:
  tags:
  - testing
  - ci
  - render
  - determinism
  - snapshot
  - ffprobe
  - ssim
  - hyperframes
---

# Testing renders

Testing renders proves three things: the composition is valid (it passes `check`), the picture is what was intended
(snapshots and motion assertions), and the output file is right (streams, duration, decodes, sound). Because
HyperFrames renders deterministically, the same project should produce the same frames every time, which makes
regression tests practical. Checked against CLI 0.8.223.

## When to use this skill

Use this skill when setting up CI for a video project, when a change to one scene might affect others, when renders
differ between machines, and before delivering any render.

## Step 0: read the tools the tests call

```bash
npx hyperframes --version
ffmpeg -version | head -1
jq --version                  # the gates below read JSON
docker --version              # only for byte-identical renders
```

Pin the CLI in CI (`npx hyperframes@0.8.223`): a floating version changes behaviour under you.

## Which test answers which question

Pick the layer from what could have gone wrong; run the cheapest that can catch it.

| You changed or fear | Run | Why the others lose |
|---|---|---|
| Markup, ids, timing | `check --strict` | seconds to run; renders catch this far later |
| The order or arrival of what must happen | a `.motion.json` sidecar | states the intent; a frame compare only says something changed |
| One scene, and whether others moved | `diff` or `compare` against a baseline | `check` passes on a scene that merely looks wrong |
| Canvas, WebGL, particles, randomness | `determinism_check.sh` | stills can match by luck across two runs |
| Renders differing between machines | `--docker` | fonts, GPU and Chrome versions differ outside it |
| The delivered file | `verify_render.sh` | every other layer tests the project, not the file |

## Layer 1: the check gate

The check gate is `npx hyperframes check` with strict flags in CI.

```bash
npx hyperframes doctor --json | jq -e '[.checks[] | select(.name=="FFmpeg" or .name=="FFprobe")] | all(.ok)'
npx hyperframes check --json --strict > check.json   # warnings fail too
jq -e '.ok and (.browserSkipped | not)' check.json   # a skipped browser stage is not a pass
```

`browserSkipped: true` means lint failed or Chrome did not start, so layout, motion and contrast were never checked.

## Layer 2: motion assertions

Motion assertions state what must happen on screen, in a `<name>.motion.json` next to the composition; `check` runs
them on the seeked timeline and fails with `motion_appears_late`, `motion_out_of_order`, `motion_off_frame` or
`motion_frozen`.

```json
{ "assertions": [
  { "kind": "appearsBy", "selector": "#headline", "bySec": 0.6 },
  { "kind": "before", "a": "#headline", "b": "#cta" },
  { "kind": "staysInFrame", "selector": ".card" },
  { "kind": "keepsMoving", "withinSelector": "#demo", "maxStaticSec": 2 } ] }
```

Write one sidecar per scene that matters; they are the cheapest regression tests a video has.

## Layer 3: visual regression

Visual regression compares stills of the new version against a baseline at fixed times.

```bash
npx hyperframes snapshot --at 0.5,3,6.2,9 --output baseline/       # once, on the approved version
npx hyperframes snapshot --at 0.5,3,6.2,9 --output current/
npx hyperframes compare baseline-project/ . --at 6.2 --labels before,after --out compare.png   # side by side
```

For a numeric gate, `hyperframes diff` scores a render, or the project itself, against a baseline render:

```bash
npx hyperframes diff baseline.mp4 renders/draft.mp4 --min-mean 0.97 --json    # non-zero exit under the bars
npx hyperframes diff baseline.mp4 . --at 0.5,3,6.2,9                          # chosen moments, with no render
```

The report covers SSIM with its lowest moments, cuts that one film has and the other lacks, both lengths and any sound
offset; the default bars are mean 0.92, 5th percentile 0.85 and worst cell 0.75, so calibrate tighter ones on known-good runs. Where the CLI is not
available, or only FFmpeg is, the fallbacks are `snapshot --against baseline.mp4` for side-by-side frames and the
script for the number:

```bash
bash scripts/ssim_diff.sh baseline.mp4 renders/draft.mp4 diff/ 0.97     # per-frame SSIM, mean, worst frame
```

When a script from `scripts/` is not on disk (a pack install), read that script from the library that served this page and save it first.

Keep baselines outside `.hyperframes/artifacts`, which prunes old runs.

## Layer 4: determinism

Determinism means two renders of the same project are frame-identical. Test it when a scene uses canvas, WebGL,
particles or randomness:

```bash
bash scripts/determinism_check.sh ./my-video          # renders twice, compares every frame's hash
```

A difference means something reads the clock, unseeded randomness, the network, or state from a previous frame. Across
machines, small pixel differences can come from fonts, GPU and Chrome versions: render with `--docker` for
byte-identical output, and keep the pinned Chrome (`npx hyperframes browser ensure`).

## Layer 5: the output file

The output file is checked after every render.

```bash
bash scripts/verify_render.sh renders/final.mp4 12          # duration 12 s, streams, decode, black, silence, loudness
bash scripts/verify_render.sh renders/overlay.webm 6 --no-audio
bash scripts/verify_render.sh renders/teaser.mp4 12 --allow-gaps   # a deliberate fade or pause reports, not fails; 90% or more of the film still fails
```

Then look at decoded frames from the file, not only the preview: `ffmpeg -ss 4.2 -i final.mp4 -frames:v 1 f.png`.
Batch renders write `manifest.json`; a batch passes when no row failed and every output passes this check.

## Running it in CI

Running it in CI means installing Node 22, FFmpeg and the pinned Chrome, then running the layers in order and
publishing the artefacts (check JSON, snapshots, compare sheets). A full workflow file and caching notes:
[references/ci.md](references/ci.md).

## Verify the checks themselves

```bash
bash scripts/verify_render.sh renders/final.mp4 12; echo "good file: exit $?"      # expect 0
head -c 2000 renders/final.mp4 > /tmp/cut.mp4
bash scripts/verify_render.sh /tmp/cut.mp4 12; echo "cut file: exit $?"            # expect 1
ffmpeg -v error -y -f lavfi -i color=black:s=320x180:r=30:d=12 -f lavfi -i sine=d=12 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest /tmp/black.mp4
bash scripts/verify_render.sh /tmp/black.mp4 12 --allow-gaps; echo "black clip: exit $?"   # expect 1, even with --allow-gaps
npx hyperframes diff renders/final.mp4 renders/final.mp4; echo "same file: $?"     # expect 0
```

A gate that has never failed proves nothing, so feed each one a case it must refuse.

## Checklist

- [ ] `check --strict` passes with the browser stage run.
- [ ] Motion sidecars for the scenes that carry the story.
- [ ] Baseline for the approved version; `diff` or `compare` run after changes.
- [ ] Determinism checked for canvas, WebGL and randomness-heavy scenes.
- [ ] Every delivered file verified for duration, streams, decoding and sound.
- [ ] Renders that must match across machines made with `--docker`.

## Gotchas

- **Symptom:** "0 samples" in the check output. **Cause:** The browser stage did not run. **Fix:** fix lint first.
- **Symptom:** A motion test fails with `motion_selector_missing`. **Cause:** A typo in a motion selector. **Fix:**
  correct the selector; do not delete the assertion.
- **Symptom:** The baseline vanished. **Cause:** It lived in `.hyperframes/artifacts/snapshots`, which keeps only
  recent runs. **Fix:** keep baselines in your own folder.
- **Symptom:** Frame hashes differ on one machine only. **Cause:** Fonts or GPU differ. **Fix:** use Docker or the
  same pinned Chrome and fonts.
- **Symptom:** Duration is off by one frame. **Cause:** The root `data-duration` is not a multiple of the frame time.
  **Fix:** round it to frames.

## Anti-patterns

| Do not | Do instead |
|---|---|
| treating a skipped browser stage as a pass | require `.ok` and `browserSkipped` false |
| gating on `doctor`'s exit code | read its `ok` field or named checks |
| tightening a threshold to one lucky run | calibrate on several known-good runs |
| a green run as visual approval | read the sheets in the pull request |

## References

- [references/ci.md](references/ci.md): a CI workflow for checks, snapshots and renders, caching Chrome and fonts, artefacts.
- `scripts/verify_render.sh`: duration, streams, decode, black frames, silence and loudness of a render.
- `scripts/determinism_check.sh`: render twice and compare frame hashes.
- `scripts/ssim_diff.sh`: per-frame SSIM between a baseline and a new render, the FFmpeg-only fallback to `diff`.

## See also

`hyperframes-cli`, `render-and-export`, `video-review`, `render-performance`.
