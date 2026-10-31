---
name: remotion-to-hyperframes
description: Ports existing video code into HyperFrames and proves the port frame by frame - Remotion compositions first (Sequence, interpolate, spring, TransitionSeries, staticFile, Lottie, fonts, props), also canvas, p5.js, Three.js, Lottie and plain HTML or CSS animation, or renders from other tools as media. Includes a blocker scan for React state and effects and an SSIM comparison script. Use when asked to port, convert, migrate or reuse a Remotion project or other animation code as HyperFrames.
metadata:
  tags:
  - hyperframes
  - remotion
  - migration
  - port
  - react
  - ssim
  - comparison
---

# Remotion to HyperFrames

A Remotion component computes its frame from `useCurrentFrame()`; a HyperFrames composition is HTML whose paused GSAP
timeline gets seeked. Both are pure functions of the frame, which is why most Remotion code ports cleanly. React state
and side effects are what resist. This skill ports the code, then proves the port against the original render.
Checked against Remotion 4.0.539 and HyperFrames CLI 0.8.223.

Only start a port when someone asks to port, convert, migrate or reuse existing video code; a passing mention of
Remotion is not a request. New videos are built with `hyperframes`.

## Step 0: read the versions on both sides

```bash
node -p "require('remotion/package.json').version"     # in the Remotion project
npx hyperframes --version                              # in the HyperFrames project
```

## Native, hosted or media: choosing per part

Each part of the source comes in at the most editable level it can reach, and the notes record which level it got:

| Source part | Level | What you do | What stays editable in Studio |
|---|---|---|---|
| Remotion (most of it), simple Motion Canvas, HTML/CSS/GSAP animation | native | rewrite as HTML and GSAP, then compare frames | every element, variables, registry items |
| Browser code able to draw whatever frame it is asked for: Lottie, canvas, WebGL, p5.js, Three.js | hosted | keep the code; HyperFrames supplies the time | timing, position, parameters you expose |
| Output from tools that only make video: Manim, After Effects, Blender, Python scripts | media | render a file and place it as a clip | cut, placement, layering; never the pixels |

Code that depends on the real clock, on live physics or on the network has only one route in: as media.

## Step 1: scan the source for blockers

```bash
python3 scripts/lint_remotion_source.py path/to/remotion/src          # exits 1 when a blocker is found
python3 scripts/lint_remotion_source.py path/to/remotion/src --json   # for tooling
```

When a script from `scripts/` is not on disk (a pack install), read that script from the library that served this page and save it first.

| Finding | Severity | What to do |
|---|---|---|
| `useState` or `useReducer` that changes what is drawn | blocker | host the component, or refactor it to derive everything from the frame |
| `useEffect` with dependencies | blocker | the same |
| async `calculateMetadata` | blocker | resolve the values once and write them in, or host |
| React UI kits: MUI, Chakra, Mantine, antd, Radix, shadcn, NextUI | blocker | host, or rebuild the few pieces in use as HTML |
| `@remotion/lambda`, `@remotion/cloudrun` | warning | remove; render with `hyperframes render`, `lambda` or `cloudrun` |
| `delayRender`, `useMemo`, `useCallback`, pure custom hooks | warning | remove the wrapper or inline its body |

A blocker is never quietly approximated. More on each: [references/limitations.md](references/limitations.md).

## Step 2: rewrite under the HyperFrames contract

| Remotion | HyperFrames |
|---|---|
| a `Sequence` scene | one sub-composition; `from` and `durationInFrames` become `data-start` and `data-duration` in seconds (`frame / fps`) |
| `interpolate`, `spring` | a tween at an absolute time on the scene's paused timeline |
| `staticFile("x.png")` | the file copied to `assets/x.png` |
| props, `defaultProps` | `data-composition-variables`, bound through `data-var-text`, `data-var-src` or `var(--id)` |
| a component used several times | one scene file mounted several times with `data-variable-values` |

Remotion's render page applies `box-sizing: border-box` to everything, but a browser's default is `content-box`. Put
`* { box-sizing: border-box; }` once in the root `<style>`, or every element with padding or a border grows by that
much. The full API table is in [references/api-map.md](references/api-map.md); timing, springs and easing are in
[references/timing.md](references/timing.md). If the source used a named visual, look for it in the registry
before building it by hand: `npx hyperframes catalog --query "<the visual, in English>" --json`.

## Worked example: one Remotion title scene, ported

The source, a 30 fps scene that fades a title in over frames 10 to 25 and sits from frame 0 for 90 frames:

```tsx
export const Title: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [10, 25], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
    <h1 style={{ opacity, fontSize: 120 }}>{text}</h1>
  </AbsoluteFill>;
};
// <Sequence from={0} durationInFrames={90}><Title text="Ship faster" /></Sequence>
```

The port: 90 frames is `data-duration="3"`, frames 10 to 25 are 0.333 s to 0.833 s, and the prop becomes a variable:

```html
<template>
  <style>
    #root { position: absolute; inset: 0; display: flex; justify-content: center; align-items: center; }
    #title-text { font-size: 120px; margin: 0; }
  </style>
  <div id="root" data-composition-id="title" data-width="1920" data-height="1080"
       data-composition-variables='[{"id":"headline","type":"string","label":"Headline","default":"Ship faster"}]'>
    <h1 id="title-text" data-var-text="headline">Ship faster</h1>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#title-text", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "none" }, 10 / 30);
    window.__timelines["title"] = tl;
  </script>
</template>
```

`interpolate` without an easing is linear, so the tween uses `ease: "none"`; clamping is GSAP's normal behaviour at
the tween's ends. A variable declared in a scene belongs to each mount, so the host passes its value with
`data-variable-values='{"headline":"Ship faster"}'`; a root `--variables` value does not replace it.

## Step 3: compare frame by frame

```bash
npx remotion render src/index.ts MyComp out/original.mp4                 # in the Remotion project
npx hyperframes render --quality delivery --output out/port.mp4          # in the HyperFrames project
npx hyperframes diff out/original.mp4 out/port.mp4 --sbs                # the score, plus an original-beside-port video
npx hyperframes diff out/original.mp4 . --at 0.5,2,4.1,6                # chosen moments of the project, with no render
```

`diff` compares the two films on every frame and reports SSIM, where it dropped furthest, any cut one film has and the
other lacks, the length of each, and how far the sound sits off. Its exit code fails the step under the default bars
(mean 0.92, 5th percentile 0.85, worst cell 0.75), which `--min-mean`, `--min-p05` and `--min-cell` change; `--drawn
x,y,w,h` scores one element's box alone, and `--json` gives one result for tooling. The sheet and log land in `.hyperframes/diff/<yours>` unless `--out` says otherwise.

Two fallbacks stay useful. `snapshot --at 0.5,2,4.1,6 --against out/original.mp4` puts both frames side by side for
your eyes, and `bash scripts/ssim_diff.sh out/original.mp4 out/port.mp4 out/diff` needs only FFmpeg, for a machine
without the CLI or a threshold of your own.

Take samples inside every scene and on both sides of every cut, and hunt for a single element that arrives late or in
the wrong colour, not just for overall likeness. Both renders need the same size, frame rate and pixel format
(`yuv420p`); otherwise SSIM falls for reasons nobody can see. On the Remotion side, render with
`Config.setVideoImageFormat("png")` and `Config.setColorSpace("bt709")`, or the comparison measures the two encoders
(about 0.05 SSIM). Thresholds and how to read the numbers: [references/timing.md](references/timing.md).

## Step 4: TRANSLATION_NOTES.md

Write `TRANSLATION_NOTES.md`: for every imported part its level and the things a person can still change in Studio,
everything that did not carry over exactly (a dropped volume ramp, an approximated transition, a substituted font),
and the comparison results. The closing reply summarises the same.

## Hosted parts and media parts

A hosted part keeps its code while HyperFrames owns the clock. On each `hf-seek` event it paints the frame matching the
time in the event: no `requestAnimationFrame` loop acting as a clock, no unseeded randomness, and a `data-duration` on
the root when nothing else fixes the length. Ready adapters exist for CSS animations, WAAPI, Lottie, anime.js and
Three.js; see `lottie`, `threejs`, `animejs`, `css-animations`.

A media part needs only a clip: `<video class="clip" data-has-audio="true" src="assets/x.mp4" ...>`, or `muted` when
it has no sound.

## Verify the port

```bash
python3 scripts/lint_remotion_source.py path/to/remotion/src     # every blocker has a decision
npx hyperframes check --json                                     # no errors
npx hyperframes diff out/original.mp4 out/port.mp4; echo "diff exit $?"   # 0 means every bar passed
```

Then open the worst moments `diff` names, in both films: an overall score can hide one late element.

## Gotchas

- **Symptom:** every box is slightly larger after the port. **Cause:** the global `box-sizing: border-box` rule is
  missing. **Fix:** add `* { box-sizing: border-box; }` to the root's `<style>`.
- **Symptom:** springs bounce differently. **Cause:** GSAP has no exact `spring()`. **Fix:** start from the mapped
  `back.out` values and tune by eye, or compute a closed-form spring of `t` in `onUpdate`.
- **Symptom:** a value stops where Remotion kept going. **Cause:** `extrapolate: "extend"`, while GSAP holds values
  at a tween's ends. **Fix:** widen the input range by hand before writing the tween.
- **Symptom:** a counter is ahead of the original. **Cause:** a different ease. **Fix:** match it (cubic out is
  `power2.out`) and compare the displayed number at the same times.
- **Symptom:** SSIM is about 0.05 low on every frame. **Cause:** different encoders or colour spaces. **Fix:** PNG
  frames and bt709 on the Remotion side; same size, rate and `yuv420p` on both.
- **Symptom:** a licence question at review. **Cause:** Remotion is source-available, with a company licence for bigger
  teams. **Fix:** port your own compositions freely, and never copy Remotion's library code into the port.

## Anti-patterns

| Do not | Do instead |
|---|---|
| approximating a blocker quietly | host the component, or refactor it to derive everything from the frame |
| frame counters at runtime | convert frames to seconds once, while translating |
| comparing with different encoders | same size, rate and `yuv420p`; PNG frames and bt709 on the Remotion side |
| reading only the mean SSIM | open the worst moments and check every cut |

## Checklist

- [ ] Blocker scan run; each blocker hosted or refactored, none approximated.
- [ ] Frames converted to seconds once, while translating.
- [ ] `box-sizing: border-box` set globally in the root.
- [ ] Props exposed as variables; reused components mounted with their own values.
- [ ] `diff` passes, or each failure is explained; side-by-side sheets read for every scene and cut.
- [ ] `TRANSLATION_NOTES.md` written.

## References

- [references/api-map.md](references/api-map.md): Remotion APIs and what replaces them.
- [references/timing.md](references/timing.md): frames to seconds, interpolate, springs, easing, counters, SSIM thresholds.
- [references/limitations.md](references/limitations.md): blockers, hosting a component, what cannot be ported.
- `scripts/lint_remotion_source.py`: the blocker and warning scan.
- `scripts/ssim_diff.sh`: SSIM per frame between two renders, the FFmpeg-only fallback to `hyperframes diff`.

## See also

`hyperframes`, `gsap`, `render-testing`.
