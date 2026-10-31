---
title: HyperFrames environment and troubleshooting
author: MOZGII, Inc.
lang: en
---

# HyperFrames environment and troubleshooting

The HyperFrames environment is Node.js 22 or later, FFmpeg and FFprobe, and a pinned Chrome build the CLI downloads.
This page covers diagnosing it, pointing the CLI at existing binaries, sandboxes that block Chrome, upgrades,
telemetry and disk cleanup.

## Doctor checks

Doctor checks report each part of the environment as ok, warn or fail: CLI version against npm, Node.js, CPU, memory,
disk, renderer environment variables, FFmpeg and FFprobe with codecs, Chrome, Docker, and `/dev/shm` in containers.

```bash
npx hyperframes doctor
npx hyperframes doctor --json | jq -e '.ok' >/dev/null      # gate on the payload; the command always exits 0
npx hyperframes doctor --json | jq -e '.checks | map(select(.name | IN("FFprobe", "FFmpeg"))) | (length == 2) and (map(.ok) | all)'
```

The top-level `ok` also counts optional tools (Docker, local voice providers). For a local render, FFmpeg, FFprobe
and Chrome are what matter.

## Chrome for rendering

Chrome for rendering is a pinned build, because pixel output drifts between Chrome versions.

```bash
npx hyperframes browser ensure     # find or download the pinned Chrome
npx hyperframes browser path       # print its path for scripts
npx hyperframes browser clear      # remove the cached download
```

## FFmpeg without a package manager

FFmpeg without a package manager works through two environment variables or a project-local folder.

```bash
export HYPERFRAMES_FFMPEG_PATH="/opt/ffmpeg/bin/ffmpeg"
export HYPERFRAMES_FFPROBE_PATH="/opt/ffmpeg/bin/ffprobe"
npx hyperframes doctor --json
```

On Windows point them at `ffmpeg.exe` and `ffprobe.exe`. Alternatively place the binaries in `.hyperframes/bin/`
(`.exe` on Windows); `PATH` is searched before that folder, so use the variables to force one build. Installers:
`brew install ffmpeg` on macOS, `winget install Gyan.FFmpeg` on Windows, the distribution package on Linux.

## Sandboxes that block Chrome

Sandboxes that block Chrome make every Chromium die at startup. Seatbelt-style sandboxes on macOS (some agent
`workspace-write` modes) block Chromium's Mach port rendezvous. Lint, transcription and audio still work; only
rendering does not. Say so, deliver the checked composition, and render outside the sandbox, with `--docker`, or in the
cloud. Do not build a substitute rasteriser out of image tools.

## Upgrades and pinned project scripts

Upgrades compare the installed CLI with npm's latest.

```bash
npx hyperframes upgrade --check --json          # {current, latest, updateAvailable}
npx hyperframes@latest upgrade --project .      # rewrite npx hyperframes@<version> pins in package.json
npx hyperframes skills                          # reinstall the upstream agent skills after a major upgrade
```

## Telemetry

Telemetry in the CLI sends usage counters. Signed out, they carry a random install id; since 0.8.216 a signed-in
CLI identifies its events by your HyperFrames user id, so signed-in usage is not anonymous. Turn it off with
`npx hyperframes telemetry disable`, `HYPERFRAMES_NO_TELEMETRY=1` or `DO_NOT_TRACK=1`; `telemetry status` shows the
state. Since 0.8.217 a project's `.env` file only sets the CLI's own settings (such as the opt-outs), not arbitrary
environment variables.

## Disk cleanup

`clean` deletes leftovers of renders that died and caches the CLI can rebuild. Finished outputs, source files and
anything a render in progress is using are left alone.

```bash
npx hyperframes clean --dry-run
npx hyperframes clean
npx hyperframes clean --snapshots     # also discard snapshot evidence
```

Never delete `.hyperframes` as a whole: it holds project history.
