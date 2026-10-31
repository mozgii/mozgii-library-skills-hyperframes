#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
"""Cut a talking-head clip from its word transcript: remove long pauses, filler words and given time ranges, join the
remaining pieces with short audio fades, and write a transcript retimed to the cut.

Needs Python 3.10+ and ffmpeg/ffprobe on PATH. Standard library only.

usage:
  python3 cut_from_transcript.py --input talk.mp4 --transcript transcript.json --out talk-cut.mp4 \
      [--cut-silence 0.8] [--remove-fillers "um,uh,erm"] [--remove "12.4-15.0,40-41.2"] [--plan]

The transcript is a JSON list of {"text", "start", "end"} in seconds, or an object {"words": [...]}.
--plan prints the pieces that would be kept, as JSON, and encodes nothing.
Writes <out> and <out stem>.words.json; exits 1 when the output length differs from the plan by 0.25 s or more.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SPEECH_MARGIN = 0.15   # seconds of room left before and after speech when a pause is removed
SHORTEST_PIECE = 0.2   # kept pieces shorter than this are dropped too
SPLICE_FADE = 0.03     # audio fade on each side of every join, so the cut does not click

Span = tuple[float, float]


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


def read_words(path: Path) -> list[Word]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("words", []) if isinstance(raw, dict) else raw
    words = []
    for item in items:
        start, end = float(item["start"]), float(item["end"])
        if end > start:
            words.append(Word(str(item.get("text", item.get("word", ""))).strip(), start, end))
    words.sort(key=lambda w: w.start)
    return words


def media_info(path: Path) -> tuple[float, bool, bool]:
    """Return (duration in seconds, has video, has audio)."""
    out = subprocess.run(
        ["ffprobe", "-loglevel", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    info = json.loads(out)
    kinds = {s.get("codec_type") for s in info.get("streams", []) if s.get("disposition", {}).get("attached_pic") != 1}
    return float(info["format"]["duration"]), "video" in kinds, "audio" in kinds


def normalise(token: str) -> str:
    return re.sub(r"[^\w']", "", token.lower())


def parse_ranges(spec: str) -> list[Span]:
    spans = []
    for chunk in (c.strip() for c in spec.split(",")):
        if chunk:
            left, right = chunk.split("-", 1)
            spans.append((float(left), float(right)))
    return spans


def unwanted(words: list[Word], length: float, pause: float | None, fillers: set[str], ranges: str) -> list[Span]:
    """Every span to remove: explicit ranges, filler words, and the inside of pauses longer than `pause`."""
    spans = parse_ranges(ranges)
    spans += [(w.start, w.end) for w in words if normalise(w.text) in fillers]
    if pause is not None:
        bounds = [0.0] + [t for w in words for t in (w.start, w.end)] + [length]
        for gap_start, gap_end in zip(bounds[0::2], bounds[1::2]):     # silence between speech, edges included
            if gap_end - gap_start > pause:
                spans.append((gap_start + SPEECH_MARGIN, gap_end - SPEECH_MARGIN))
    return spans


def subtract(whole: Span, holes: list[Span]) -> list[Span]:
    """The parts of `whole` not covered by any hole, longest-first order not assumed."""
    pieces = [whole]
    for h0, h1 in holes:
        if h1 <= h0:
            continue
        nxt = []
        for p0, p1 in pieces:
            if h1 <= p0 or h0 >= p1:
                nxt.append((p0, p1))
                continue
            if h0 > p0:
                nxt.append((p0, h0))
            if h1 < p1:
                nxt.append((h1, p1))
        pieces = nxt
    return [(round(a, 3), round(b, 3)) for a, b in sorted(pieces) if b - a >= SHORTEST_PIECE]


def shift_words(words: list[Word], pieces: list[Span]) -> list[dict]:
    """Words lying wholly inside a kept piece, moved to their time in the cut."""
    out, elapsed = [], 0.0
    for a, b in pieces:
        out += [{"text": w.text, "start": round(w.start - a + elapsed, 3), "end": round(w.end - a + elapsed, 3)}
                for w in words if a <= w.start and w.end <= b]
        elapsed += b - a
    return out


def filter_graph(pieces: list[Span], video: bool, audio: bool) -> tuple[str, list[str]]:
    """One trim per kept piece, fades at the inner joins, then a single concat."""
    parts, labels = [], []
    last = len(pieces) - 1
    for i, (a, b) in enumerate(pieces):
        if video:
            parts.append(f"[0:v:0]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
            labels.append(f"[v{i}]")
        if audio:
            fade = min(SPLICE_FADE, (b - a) / 4)
            chain = f"[0:a:0]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS"
            if i > 0:
                chain += f",afade=t=in:st=0:d={fade:.3f}"
            if i < last:
                chain += f",afade=t=out:st={b - a - fade:.3f}:d={fade:.3f}"
            parts.append(chain + f"[a{i}]")
            labels.append(f"[a{i}]")
    outs = (["[v]"] if video else []) + (["[a]"] if audio else [])
    parts.append("".join(labels) + f"concat=n={len(pieces)}:v={int(video)}:a={int(audio)}" + "".join(outs))
    return ";".join(parts), outs


def render(src: Path, pieces: list[Span], dest: Path, video: bool, audio: bool) -> None:
    graph, outs = filter_graph(pieces, video, audio)
    staging = dest.with_name(dest.stem + ".part" + dest.suffix)
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
           "-filter_complex", graph]
    for label in outs:
        cmd += ["-map", label]
    if video:
        cmd += ["-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", str(staging)]
    subprocess.run(cmd, check=True)
    staging.replace(dest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True, help="the source clip")
    parser.add_argument("--transcript", type=Path, required=True, help="word transcript JSON")
    parser.add_argument("--out", type=Path, help="the cut file to write")
    parser.add_argument("--cut-silence", type=float, help="remove pauses longer than this many seconds")
    parser.add_argument("--remove-fillers", default="", help="comma-separated filler words, e.g. um,uh,erm")
    parser.add_argument("--remove", default="", help="time ranges to remove, e.g. 12.4-15,40-41.2")
    parser.add_argument("--plan", action="store_true", help="print the kept pieces and stop")
    args = parser.parse_args(argv)

    for tool in ("ffprobe",) if args.plan else ("ffprobe", "ffmpeg"):
        if shutil.which(tool) is None:
            print(f"error: {tool} not found on PATH", file=sys.stderr)
            return 2
    if not args.plan and args.out is None:
        print("error: --out is required unless --plan is given", file=sys.stderr)
        return 2

    words = read_words(args.transcript)
    length, has_video, has_audio = media_info(args.input)
    fillers = {normalise(f) for f in args.remove_fillers.split(",") if f.strip()}
    holes = [(max(0.0, a), min(length, b)) for a, b in unwanted(words, length, args.cut_silence, fillers, args.remove)]
    pieces = subtract((0.0, length), holes)
    if not pieces:
        print("error: nothing left to keep", file=sys.stderr)
        return 1

    planned = sum(b - a for a, b in pieces)
    report: dict[str, object] = {"segments": pieces, "kept_s": round(planned, 3), "total_s": round(length, 3)}
    if args.plan:
        print(json.dumps(report))
        return 0

    render(args.input, pieces, args.out, has_video, has_audio)
    words_path = args.out.with_suffix(".words.json")
    words_path.write_text(json.dumps(shift_words(words, pieces), indent=1), encoding="utf-8")
    actual = media_info(args.out)[0]
    report.update({"out": str(args.out), "words": str(words_path), "produced_s": round(actual, 3)})
    print(json.dumps(report))
    return 0 if abs(actual - planned) < 0.25 else 1


if __name__ == "__main__":
    sys.exit(main())
