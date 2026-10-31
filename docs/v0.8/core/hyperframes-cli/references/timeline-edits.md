---
title: HyperFrames timeline edits and project history
author: MOZGII, Inc.
lang: en
---

# HyperFrames timeline edits and project history

HyperFrames timeline edits are CLI commands that move, trim, split, duplicate, delete or retune clips the same way the
Studio editor does, so the HTML stays in the shape Studio expects. Each edit can be previewed, prints a receipt and can
be undone.

## Timeline verbs

The timeline verbs and the values each reads:

| Verb | Reads | Example |
|---|---|---|
| `move` | a time (absolute, or `+2` / `-1` relative), `--overwrite` | `timeline move '#outro' 9` |
| `trim` | `--start`, `--end`, `--duration`, `--overwrite` | `timeline trim '#broll' --end 7.5` |
| `split` | a time | `timeline split '#talk' 12.4` |
| `delete` | `--start`, `--end` (delete a range) | `timeline delete '#sfx-3'` |
| `set` | `--volume`, `--rate`, `--track` | `timeline set '#music' --volume 0.5` |
| `duplicate` | `--at` | `timeline duplicate '#badge' --at 14` |
| `ids` | none | `timeline ids` stamps stable ids on clips that lack one |

Refs are the `#id` values that `timeline --json` prints. Add `--plan --json` to see the change without writing it.

## Refusals and durations

The CLI refuses edits that would damage the timeline: a clip may not end up overlapping another clip on the same lane
(add `--overwrite`, or shift the other clip out of the way first), and it may not run beyond the end of its
composition. No command changes `data-duration`: raise the
root's duration by hand before moving a clip past the end.

## Batch plans and receipts

A batch plan applies several edits at once, atomically:

```json
[
  { "verb": "move", "ref": "#outro", "time": "9" },
  { "verb": "trim", "ref": "#broll", "end": "7.5" }
]
```

```bash
npx hyperframes timeline apply plan.json --plan --json   # dry run
npx hyperframes timeline apply plan.json --json          # write; prints a receipt
npx hyperframes timeline undo receipt.json               # revert exactly that change
```

Save each receipt; it is the undo handle.

## Project history

Project history keeps every write under `.hyperframes/` so changes can be undone and the person's own edits seen.

```bash
npx hyperframes history begin --who agent --label "tighten intro"
npx hyperframes history --since mine --who agent     # what the person changed since your last turn
npx hyperframes history undo --who agent             # revert your last change when a check fails
npx hyperframes history end
```

Build on the person's edits; never hand-edit back over them. Never delete `.hyperframes`: it holds the history.
