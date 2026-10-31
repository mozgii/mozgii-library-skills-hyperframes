#!/usr/bin/env bash
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
# Render a HyperFrames project twice and compare every decoded frame by hash.
# Usage: determinism_check.sh <project-dir> [extra render flags...]
# Prints the first differing frames, if any. Exit 0 when both renders are frame-identical.
# Needs npx (HyperFrames CLI), ffmpeg on PATH. Uses --quality draft by default to keep it quick.
case "${1:-}" in -h|--help) awk 'NR>3 { if (!/^#/) exit; sub(/^# ?/, ""); print }' "$0"; exit 0;; esac
set -euo pipefail
proj="${1:?project dir}"; shift || true
out="$(mktemp -d)"; trap 'rm -rf "$out"' EXIT
for run in a b; do
  npx hyperframes render "$proj" --quality draft --output "$out/$run.mp4" --quiet "$@"
  ffmpeg -v error -i "$out/$run.mp4" -map 0:v -f framemd5 "$out/$run.md5"
done
if diff -q <(grep -v '^#' "$out/a.md5") <(grep -v '^#' "$out/b.md5") >/dev/null; then
  echo "identical: $(grep -vc '^#' "$out/a.md5") frames"
else
  echo "renders differ; first differing frames (stream, dts, pts, duration, size, hash):"
  diff <(grep -v '^#' "$out/a.md5") <(grep -v '^#' "$out/b.md5") | grep '^<' | head -5
  exit 1
fi
