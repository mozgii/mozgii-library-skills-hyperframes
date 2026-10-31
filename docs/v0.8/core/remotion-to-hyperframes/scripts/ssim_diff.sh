#!/usr/bin/env bash
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
# Per-frame SSIM between two renders of the same video.
# Usage: ssim_diff.sh <reference.mp4> <candidate.mp4> <out-dir> [threshold]
# Writes <out-dir>/ssim.log (one line per frame) and prints mean, min, worst frame and pass/fail.
# Needs ffmpeg and ffprobe on PATH. Both inputs are scaled to the reference size and converted to yuv420p.
case "${1:-}" in -h|--help) awk 'NR>3 { if (!/^#/) exit; sub(/^# ?/, ""); print }' "$0"; exit 0;; esac
set -euo pipefail
ref="${1:?reference video}"; cand="${2:?candidate video}"; out="${3:?output dir}"; threshold="${4:-0.95}"
mkdir -p "$out"
dims=$(ffprobe -loglevel error -of csv=p=0:s=x -show_entries stream=height,width -select_streams v:0 "$ref")
ffmpeg -hide_banner -loglevel error -i "$ref" -i "$cand" -filter_complex \
  "[0:v]format=yuv420p,setpts=PTS-STARTPTS[a];[1:v]scale=${dims/x/:},format=yuv420p,setpts=PTS-STARTPTS[b];[a][b]ssim=stats_file=$out/ssim.log" \
  -f null -
awk -v thr="$threshold" '
  match($0, /All:[0-9.]+/) {
    v = substr($0, RSTART + 4, RLENGTH - 4) + 0; n++; total += v
    if (n == 1 || v < low) { low = v; lowframe = $1 }
  }
  END {
    if (n == 0) { print "no frames compared"; exit 2 }
    avg = total / n; verdict = (avg >= thr) ? "PASS" : "FAIL"
    printf "frames %d  mean %.4f  min %.4f (%s)  threshold %.2f  %s\n", n, avg, low, lowframe, thr, verdict
    exit (verdict == "PASS") ? 0 : 1
  }' "$out/ssim.log"
