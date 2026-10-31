#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
"""Per-frame loudness and frequency bands from an audio or video file, for audio-reactive animation.

Usage:
    python3 extract_audio_bands.py <input> [-o audio-bands.json] [--fps 30] [--bands 8] [--smooth 0.35]

Writes JSON: {"fps": 30, "totalFrames": N, "duration": s, "bandEdgesHz": [...],
              "frames": [{"rms": 0..1, "bands": [0..1, ...]}, ...]}
Band 0 is the lowest (bass). Each series is scaled so its 95th percentile is 1.0, meaning "loud for this band".
Needs ffmpeg on PATH and numpy (python3 -m pip install numpy).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

RATE = 44_100                 # decode rate, Hz
WINDOW = 4_096                # analysis window: 44100 / 4096 is roughly 10.8 Hz between bins
BAND_RANGE = (30.0, 16_000.0)  # the part of the spectrum that carries rhythm and melody


def read_mono(path: str) -> np.ndarray:
    """Decode any media file to mono float32 samples at RATE."""
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH")
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-map", "0:a:0",
         "-ar", str(RATE), "-ac", "1", "-f", "f32le", "pipe:1"],
        capture_output=True,
    )
    if proc.returncode != 0:
        sys.exit("ffmpeg could not decode the audio: " + proc.stderr.decode("utf-8", "replace")[:400])
    return np.frombuffer(proc.stdout, dtype="<f4")


def frame_centres(n_samples: int, fps: float) -> np.ndarray:
    """Sample index at the middle of every video frame."""
    count = int(np.ceil(n_samples * fps / RATE))
    return ((np.arange(count) + 0.5) * RATE / fps).astype(np.int64)


def measure(samples: np.ndarray, fps: float, n_bands: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (rms per frame, band energy per frame and band, band edges in Hz)."""
    half = WINDOW // 2
    padded = np.pad(samples, (half, half))
    centres = frame_centres(samples.size, fps) + half
    span = max(1, int(RATE / fps) // 2)                      # loudness looks at one frame's worth of audio

    edges = np.geomspace(*BAND_RANGE, num=n_bands + 1)
    bin_hz = np.fft.rfftfreq(WINDOW, d=1.0 / RATE)
    band_of_bin = np.digitize(bin_hz, edges) - 1               # -1 or n_bands means "outside every band"
    taper = np.hanning(WINDOW).astype(np.float32)

    loud = np.empty(centres.size)
    energy = np.zeros((centres.size, n_bands))
    for i, c in enumerate(centres):
        chunk = padded[c - half:c + half]
        core = padded[c - span:c + span]
        loud[i] = np.sqrt(np.mean(np.square(core, dtype=np.float64)))
        spectrum = np.abs(np.fft.rfft(chunk * taper))
        for b in range(n_bands):
            hit = spectrum[band_of_bin == b]
            energy[i, b] = hit.mean() if hit.size else 0.0
    return loud, energy, edges


def scale(series: np.ndarray) -> np.ndarray:
    """Divide by the 95th percentile and clip to 0..1; silent series stay at 0."""
    top = float(np.percentile(series, 95)) if series.size else 0.0
    return np.clip(series / top, 0.0, 1.0) if top > 0 else np.zeros_like(series)


def hold_release(series: np.ndarray, keep: float) -> np.ndarray:
    """Rise at once, fall gradually: each frame keeps `keep` of the previous value when that is higher."""
    out = series.copy()
    for i in range(1, out.shape[0]):
        out[i] = np.maximum(out[i], keep * out[i - 1] + (1.0 - keep) * out[i])
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", metavar="MEDIA", help="the audio or video to analyse")
    parser.add_argument("--fps", default=30.0, type=float, help="video frame rate (default 30)")
    parser.add_argument("--bands", default=8, type=int, help="how many frequency bands (default 8)")
    parser.add_argument("-o", "--output", default="audio-bands.json", help="JSON file to write")
    parser.add_argument("--smooth", type=float, default=0.35,
                        help="release smoothing 0..0.95; 0 is none, 0.35 removes flicker and keeps hits sharp")
    args = parser.parse_args(argv)
    if args.fps <= 0 or args.bands < 1 or not 0.0 <= args.smooth < 1.0:
        parser.error("--fps must be > 0, --bands >= 1, --smooth in [0, 1)")

    global np                     # imported here so --help works without numpy
    try:
        import numpy as np
    except ImportError:
        sys.exit("numpy not found: python3 -m pip install numpy")

    samples = read_mono(args.input)
    if samples.size == 0:
        sys.exit("no audio samples decoded")
    loud, energy, edges = measure(samples, args.fps, args.bands)
    loud = scale(loud)
    energy = np.column_stack([scale(energy[:, b]) for b in range(args.bands)])
    if args.smooth > 0:
        loud = hold_release(loud, args.smooth)
        energy = hold_release(energy, args.smooth)

    result = {
        "fps": args.fps,
        "totalFrames": int(loud.size),
        "duration": round(samples.size / RATE, 4),
        "bandEdgesHz": [round(float(e), 1) for e in edges],
        "frames": [{"rms": round(float(r), 4), "bands": [round(float(v), 4) for v in row]}
                   for r, row in zip(loud, energy)],
    }
    Path(args.output).write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {args.output}: {loud.size} frames at {args.fps:g} fps, {args.bands} bands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
