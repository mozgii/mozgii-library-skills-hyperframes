#!/usr/bin/env bash
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
# Verify a rendered video: it exists, decodes, has the expected duration and streams, and has no long black or
# silent stretches. Usage: verify_render.sh <video> <expected-seconds> [--no-audio] [--allow-gaps] [--tolerance 0.05]
# Exit 0 when every check passes, 1 otherwise. --allow-gaps reports black and silent stretches without failing, for a
# film with a deliberate fade or pause; a stretch covering 90% or more of the film still fails, because that is a
# broken render, not a pause. Needs ffmpeg and ffprobe on PATH.
case "${1:-}" in -h|--help) awk 'NR>3 { if (!/^#/) exit; sub(/^# ?/, ""); print }' "$0"; exit 0;; esac
set -uo pipefail
f="${1:?video}"; want="${2:?expected duration in seconds}"; shift 2
need_audio=1; tol=0.05; allow_gaps=0
for flag in "$@"; do
  if [ "${take_tol:-0}" = 1 ]; then tol="$flag"; take_tol=0; continue; fi
  [ "$flag" = --no-audio ] && need_audio=0
  [ "$flag" = --allow-gaps ] && allow_gaps=1
  [ "$flag" = --tolerance ] && take_tol=1
done
fail=0; ok() { printf 'ok    %s\n' "$1"; }; bad() { printf 'FAIL  %s\n' "$1"; fail=1; }
gap() { if [ "$allow_gaps" = 1 ]; then printf 'warn  %s\n' "$1"; else bad "$1"; fi; }
# Lines of "start end" in seconds: true when together they cover 90% or more of the film's duration in $dur.
nearly_all() { printf '%s\n' "$1" | awk -v d="$dur" '{sum+=$2-$1} END{exit !(d>0 && sum>=0.9*d)}'; }

[ -s "$f" ] && ok "file exists and is not empty ($(wc -c < "$f" | tr -d ' ') bytes)" || { bad "missing or empty: $f"; exit 1; }
dur=$(ffprobe -loglevel error -of default=noprint_wrappers=1:nokey=1 -show_entries format=duration "$f")
awk -v d="$dur" -v w="$want" -v t="$tol" 'BEGIN{exit !(d-w<=t && w-d<=t)}' && ok "duration $dur s (expected $want)" || bad "duration $dur s, expected $want ± $tol"
v=$(ffprobe -loglevel error -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt -select_streams v:0 -of csv=p=0 "$f")
[ -n "$v" ] && ok "video stream: $v" || bad "no video stream"
a=$(ffprobe -loglevel error -of csv=p=0 -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels "$f")
if [ "$need_audio" = 1 ]; then [ -n "$a" ] && ok "audio stream: $a" || bad "no audio stream"; fi
errs=$(ffmpeg -v error -i "$f" -f null - 2>&1 | head -5)
[ -z "$errs" ] && ok "decodes without errors" || bad "decode errors: $errs"
black_all=$(ffmpeg -hide_banner -i "$f" -vf "blackdetect=d=0.5:pix_th=0.05" -an -f null - 2>&1 | grep -o 'black_start:[0-9.]* black_end:[0-9.]*')
black=$(printf '%s\n' "$black_all" | head -3)
if [ -n "$black_all" ] && nearly_all "$(printf '%s\n' "$black_all" | sed -E 's/black_start:([0-9.]*) black_end:([0-9.]*)/\1 \2/')"; then
  bad "black for 90% or more of the film: $(echo $black)"
else
  [ -z "$black" ] && ok "no black stretch of 0.5 s or more" || gap "black stretches: $(echo $black)"
fi
if [ -n "$a" ]; then
  sil_log=$(ffmpeg -hide_banner -i "$f" -af "silencedetect=noise=-50dB:d=2" -vn -f null - 2>&1)
  sil=$(printf '%s\n' "$sil_log" | grep -o 'silence_start: [0-9.]*' | head -3)
  sil_spans=$(printf '%s\n' "$sil_log" | sed -nE 's/.*silence_(start|end): ([0-9.]+).*/\1 \2/p' \
    | awk -v d="$dur" '$1 == "start" {from = $2; open = 1} $1 == "end" {print from, $2; open = 0} END {if (open) print from, d}')
  if [ -n "$sil_spans" ] && nearly_all "$sil_spans"; then
    bad "silent for 90% or more of the film: $(echo $sil)"
  else
    [ -z "$sil" ] && ok "no silence of 2 s or more" || gap "silent stretches: $(echo $sil)"
  fi
  lufs=$(ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -vn -f null - 2>&1 | awk '/Integrated loudness/{f=1} f&&/I:/{print $2; exit}')
  [ -n "$lufs" ] && printf 'info  integrated loudness %s LUFS\n' "$lufs"
fi
exit $fail
