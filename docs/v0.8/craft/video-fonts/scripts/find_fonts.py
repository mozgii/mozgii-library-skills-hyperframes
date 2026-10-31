#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
"""List Google Fonts families by category, newest and most popular first, to look past the usual choices.

Usage:
    python3 find_fonts.py [--category "Sans Serif"|Serif|Display|Monospace|Handwriting] [--since 2020] [--limit 15]
                          [--variable] [--min-weight 800] [--metadata metadata.json]

Reads https://fonts.google.com/metadata/fonts (or a saved copy). Prints popularity rank, VAR for variable fonts,
the family and its weights. Needs only the Python 3.9+ standard library.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

OVERUSED = {"Inter", "Roboto", "Open Sans", "Lato", "Poppins", "Montserrat", "Playfair Display", "Nunito", "Outfit",
            "Sora", "Syne", "Cormorant Garamond", "EB Garamond", "Source Sans 3", "PT Sans", "Noto Sans"}


def load(path: str | None) -> list[dict]:
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    else:
        with urllib.request.urlopen("https://fonts.google.com/metadata/fonts", timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    return data.get("familyMetadataList", [])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--category", default=None)
    ap.add_argument("--since", type=int, default=2018)
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--variable", action="store_true")
    ap.add_argument("--min-weight", type=int, default=0)
    ap.add_argument("--include-overused", action="store_true")
    ap.add_argument("--metadata", default=None)
    a = ap.parse_args()
    rows = []
    for fam in load(a.metadata):
        name = fam.get("family", "")
        if not a.include_overused and name in OVERUSED:
            continue
        if a.category and fam.get("category") != a.category:
            continue
        if "latin" not in (fam.get("subsets") or []):
            continue
        if fam.get("dateAdded", "0000")[:4] < str(a.since):
            continue
        if a.variable and not fam.get("axes"):
            continue
        weights = sorted({int(k.rstrip("i")) for k in (fam.get("fonts") or {}) if k.rstrip("i").isdigit()})
        if a.min_weight and (not weights or max(weights) < a.min_weight):
            continue
        rows.append((fam.get("popularity", 99999), "VAR" if fam.get("axes") else "   ", name, weights))
    for pop, var, name, weights in sorted(rows)[: a.limit]:
        print(f"{pop:5d} | {var} | {name}  {weights}")


if __name__ == "__main__":
    main()
