#!/usr/bin/env bash
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
# Subset every .ttf/.otf/.woff2 in a folder to the characters a HyperFrames project uses.
# Usage: subset_fonts.sh <project-dir> <fonts-in-dir> [fonts-out-dir]
# Needs: python3 3.11+ with fonttools[woff] 4.68+ (python3 -m pip install "fonttools[woff]>=4.68"), the security floor.
# The text comes from index.html and compositions/*.html with tags stripped, plus Basic Latin and common punctuation,
# so copy edits that stay in Latin still render. Re-run after copy or variable values change.
case "${1:-}" in -h|--help) awk 'NR>3 { if (!/^#/) exit; sub(/^# ?/, ""); print }' "$0"; exit 0;; esac
set -euo pipefail
project="${1:?project dir}"; in_dir="${2:?fonts input dir}"; out_dir="${3:-$project/assets/fonts}"
mkdir -p "$out_dir"
text_file="$(mktemp)"; trap 'rm -f "$text_file"' EXIT
python3 - "$project" > "$text_file" <<'PY'
import html, re, sys
from pathlib import Path
root = Path(sys.argv[1])
files = [root / "index.html", *sorted((root / "compositions").rglob("*.html"))]
chars = set()
for f in files:
    if f.exists():
        t = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", f.read_text(encoding="utf-8"), flags=re.I)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        chars.update(t)
        chars.update("".join(re.findall(r'"default"\s*:\s*"([^"]*)"', f.read_text(encoding="utf-8"))))
chars.update(chr(c) for c in range(0x20, 0x7F))
chars.update("–—‘’“”•…€")
sys.stdout.write("".join(sorted(c for c in chars if c.isprintable())))
PY
for font in "$in_dir"/*.{ttf,otf,woff2}; do
  [ -e "$font" ] || continue
  base="$(basename "${font%.*}")"
  pyftsubset "$font" --text-file="$text_file" --layout-features='*' --flavor=woff2 \
    --output-file="$out_dir/$base.woff2"
  printf '%s -> %s (%s bytes)\n' "$(basename "$font")" "$out_dir/$base.woff2" "$(wc -c < "$out_dir/$base.woff2" | tr -d ' ')"
done
