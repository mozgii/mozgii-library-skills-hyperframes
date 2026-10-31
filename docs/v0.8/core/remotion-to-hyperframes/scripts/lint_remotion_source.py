#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright 2026 MOZGII, Inc. (https://mozgii.com/)
"""Scan a Remotion source tree for patterns that block or complicate a HyperFrames port.

Usage:
    python3 lint_remotion_source.py <src-dir> [--json]

Exit code 1 when any blocker is found, 0 otherwise. Needs only the Python 3.9+ standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BLOCKERS = [
    ("use-state", re.compile(r"\buseState\s*\("), "useState drives visuals: refactor to a function of time, or host"),
    ("use-reducer", re.compile(r"\buseReducer\s*\("), "useReducer drives visuals: refactor or host"),
    ("use-effect-deps", re.compile(r"\buseEffect\s*\([\s\S]{0,400}?,\s*\[[^\]\s][^\]]*\]\s*\)"),
     "useEffect with dependencies: refactor or host"),
    ("async-metadata", re.compile(r"calculateMetadata\s*[:=]\s*async\b|async\s+function\s+calculateMetadata"),
     "async calculateMetadata: resolve values once, or host"),
    ("ui-kit", re.compile(r"from\s+['\"](@mui/|@chakra-ui/|@mantine/|antd|@radix-ui/|@nextui-org/|@/components/ui)"),
     "React UI kit: host, or rebuild the used parts as HTML"),
]
WARNINGS = [
    ("lambda", re.compile(r"@remotion/(lambda|cloudrun)"), "distributed rendering config: drop and note it"),
    ("delay-render", re.compile(r"\b(delayRender|continueRender)\s*\("), "delayRender: drop; use a buildReady promise if needed"),
    ("memo", re.compile(r"\b(useMemo|useCallback)\s*\("), "memo wrapper: drop the wrapper"),
    ("custom-hook", re.compile(r"\bfunction\s+use[A-Z]\w*\s*\(|const\s+use[A-Z]\w*\s*=\s*\("), "custom hook: inline if pure"),
    ("extend", re.compile(r"extrapolate(Left|Right)\s*:\s*['\"]extend['\"]"), "extend extrapolation: widen the input range"),
]
EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs"}


def scan(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in sorted(p for p in root.rglob("*") if p.suffix in EXTS and "node_modules" not in p.parts):
        text = path.read_text(encoding="utf-8", errors="replace")
        for kind, rules in (("blocker", BLOCKERS), ("warning", WARNINGS)):
            for rule_id, pattern, message in rules:
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    findings.append({"kind": kind, "rule": rule_id, "file": str(path.relative_to(root)),
                                     "line": line, "message": message})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.src.is_dir():
        print(f"not a directory: {args.src}", file=sys.stderr)
        return 2
    findings = scan(args.src)
    blockers = [f for f in findings if f["kind"] == "blocker"]
    if args.json:
        print(json.dumps({"ok": not blockers, "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['kind']:8} {f['rule']:16} {f['file']}:{f['line']}  {f['message']}")
        print(f"\nsummary: {len(blockers)} blocking, {len(findings) - len(blockers)} to note")
    return int(bool(blockers))


if __name__ == "__main__":
    raise SystemExit(main())
