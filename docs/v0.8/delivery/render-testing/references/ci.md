---
title: Continuous integration for video projects
author: MOZGII, Inc.
lang: en
---

# Continuous integration for video projects

Continuous integration for video projects runs the HyperFrames checks, snapshots and renders on every change, so a
broken scene is caught before review. The example is a GitHub Actions workflow on Ubuntu; the same steps work on any
CI runner with Node.js 22 or later and FFmpeg.

## Contents

The sections of this page:

- Workflow file
- Pinning the CLI version
- Caching Chrome and fonts
- Rendering in Docker on CI
- What to publish as artefacts
- Telemetry in CI

## Workflow file

The workflow file below checks the project, snapshots key frames, renders a draft and verifies it. Action versions
were current at the time of writing.

```yaml
name: video
on: [pull_request]
jobs:
  check-and-render:
    runs-on: ubuntu-latest
    env:
      HYPERFRAMES_NO_TELEMETRY: "1"
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with: { node-version: "22" }
      - name: Install FFmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg
      - uses: actions/cache@v6
        with:
          path: |
            ~/.cache/hyperframes
            ~/.cache/puppeteer
          key: hyperframes-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - name: Environment
        run: |
          npx --yes hyperframes@0.8.223 browser ensure
          npx hyperframes@0.8.223 doctor --json | jq -e '[.checks[] | select(.name=="FFmpeg" or .name=="FFprobe")] | all(.ok)'
      - name: Check
        run: |
          npx hyperframes@0.8.223 check --json --strict > check.json
          jq -e '.ok and (.browserSkipped | not)' check.json
      - name: Snapshots
        run: npx hyperframes@0.8.223 snapshot --review --output artifacts/review
      - name: Draft render
        run: |
          npx hyperframes@0.8.223 render --quality draft --strict --output artifacts/draft.mp4
          bash .ci/verify_render.sh artifacts/draft.mp4 "$(jq -r '.duration' <(npx hyperframes@0.8.223 info --json))"
      - uses: actions/upload-artifact@v7
        if: always()
        with: { name: video-artifacts, path: "check.json\nartifacts/" }
```

Copy `scripts/verify_render.sh` into the repository (here as `.ci/verify_render.sh`). Check the field name that
`info --json` prints for duration on your CLI version, or pass the root `data-duration` directly.

## Pinning the CLI version

Pinning the CLI version (`npx hyperframes@0.8.223`) keeps CI from changing behaviour when a new release lands. Upgrade
on purpose: `npx hyperframes@latest upgrade --project .` rewrites pinned versions in `package.json`, then rerun CI and
review the snapshot diffs.

## Caching Chrome and fonts

Caching Chrome and fonts saves minutes per run. The pinned Chrome download and the compiler's font cache
(`~/.cache/hyperframes/fonts`) are safe to cache; `npx hyperframes browser path` prints where Chrome lives if your
runner uses a different cache directory.

## Rendering in Docker on CI

Rendering in Docker on CI (`npx hyperframes render --docker --strict`) gives byte-identical output across hosts, at the
cost of a slower first run while the image downloads. Use it for the final render and for determinism tests that
compare against files rendered on other machines. The runner must have Docker; `doctor` reports it.

## What to publish as artefacts

What to publish as artefacts: `check.json` (findings with selectors, times and boxes), the review sheets
(`review-beats.jpg`, seam strips, the phone sheet), compare sheets against the baseline, and the draft render. Review
the sheets in the pull request; do not treat a green run as visual approval.

## Telemetry in CI

Telemetry in CI sends usage counters, tied to a HyperFrames user id when the job is signed in (0.8.216 on). Set
`HYPERFRAMES_NO_TELEMETRY=1` (or `DO_NOT_TRACK=1`) in the job environment to turn it off.
