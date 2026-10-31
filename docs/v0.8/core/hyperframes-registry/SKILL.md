---
name: hyperframes-registry
description: Finds, installs and wires ready-made HyperFrames registry items - blocks (whole scenes such as transitions, lower thirds, charts, code reveals, 3D stages) and components (snippets such as caption styles, grain, camera shake, text effects) - with hyperframes catalog and hyperframes add, then mounts or merges them into a composition. Use when someone asks for a ready-made effect, transition, caption style, lower third, chart or overlay, before hand-building any named visual, and when wiring an installed item or editing hyperframes.json.
metadata:
  tags:
  - hyperframes
  - registry
  - catalog
  - blocks
  - components
  - transitions
  - captions
---

# HyperFrames registry

The HyperFrames registry is a public catalog of about 450 ready-made items. `add` copies an item into your project as
plain source that you then own: trim it, restyle it to the brand, change its timing. For any named effect, starting
from an item is quicker than writing it and usually looks better. Checked against CLI 0.8.223.

Search here before hand-writing any named visual (a glitch, film grain, a whip pan, a bar chart race, a karaoke
caption style, a code diff), and whenever an item has to be installed, mounted or merged. The usual path is two
commands: `npx hyperframes catalog --query "film grain" --json`, then `npx hyperframes add <name>`. There is no
`hyperframes registry` command.

## Step 0: read the CLI and the install paths

```bash
npx hyperframes --version
cat hyperframes.json 2>/dev/null     # paths.blocks, paths.components, paths.assets
npx hyperframes catalog --query "lower third" --json | jq '{tier, dropped, unindexed}'
```

Search works offline from the cached manifest; `add` always downloads, so it needs the network.

## Block or component?

An item is one of two kinds, and the kind decides how it joins your film:

| | Block | Component |
|---|---|---|
| What it is | a complete scene with its own timeline, size and duration | a piece of markup and CSS, sometimes with script |
| Where `add` writes it | `compositions/<name>.html` | `compositions/components/<name>.html` |
| How it joins the film | mounted by a host `div` with `data-composition-src` | its parts copied into one of your scenes |
| Size and duration | its own; a mount may be shorter, never longer | the host scene's |
| Pick it when | the beat is the item: a title card, a chart scene, a transition | the item decorates a beat you are building: a caption style, a cursor, a camera shake |

## What the catalog holds

A few real items per family, to know what to search for:

| Family | Kind | Items |
|---|---|---|
| Scene transitions | block | `whip-pan`, `transitions-push`, `flash-through-white`, `sdf-iris` |
| Lower thirds and overlays | block | `lt-kicker-name`, `lt-soft-pill`, `news-ticker`, `camcorder-hud` |
| Titles and kinetic type | block | `glass-shard-title`, `wireframe-portal-title`, `hw-write-title` |
| Chat, social and app cards | block | `claude-exchange`, `x-post`, `slack-notification-ad`, `macos-notification` |
| Code, charts, data and maps | block | `code-typing`, `heatmap`, `world-map`, `bar-chart-race` |
| 3D, shaders and backgrounds | block | `product-turntable`, `mesh-gradient`, `starfield`, `aurora` |
| Text effects and motion primitives | component | `per-word-rise`, `headline-slam`, `blur-in`, `count-up` |
| Caption styles | component | `caption-pill-karaoke`, `caption-kinetic-slam`, `caption-highlight` |
| Cursors and camera | component | `cursor-drag-drop`, `oversized-cursor`, `push-in`, `camera-shake` |
| Product demo props | component | `device-frame-stage`, `comparison-split`, `browser-device-stage` |
| Textures and passes | component | `grain-overlay`, `ordered-dither-pass`, `ascii-render-pass` |

## Searching the catalog for a ready-made effect

`npx hyperframes catalog --query` ranks every item against a plain description of what the beat has to do, so a
search for film grain, a glitch or a transition finds something to install rather than write:

```bash
npx hyperframes catalog --query "reveal a headline one line at a time" --json
npx hyperframes catalog --type block --tag transition --json
npx hyperframes catalog --tag caption-style --json
npx hyperframes catalog --query "camera push" --tag camera --json
```

### Searching in English for a film in another language

The index is built from English text. A query typed in another script gets `No searchable words in query` back; that
message means the words were not understood, not that the catalog lacks the effect. Translate the description and
search again.

### Search tiers and what the JSON reports

- Searching runs on your machine and sends nothing anywhere.
- The default `words` tier only finds items whose text shares your words. `--on-device` ranks items by what they mean;
  it needs a single download of about 33 MB first. Mention that option and let the person choose; never switch it on for them.
- The `--json` envelope reports which `tier` answered, how many items were `dropped` (ranked but not installable) and
  how many are `unindexed`.
- Search keeps working offline from the cached manifest. `add` always downloads, so it needs the network even when the
  item was installed once already.

## Installing an item

`add` writes the item's files, installs anything it depends on first, and prints a snippet for mounting it:

```bash
npx hyperframes add data-chart --json
npx hyperframes add caption-clip-wipe --json
npx hyperframes add lt-clean-bar --vars '{"name":"Ada Moreno","role":"Research"}' --json   # per-mount values
npx hyperframes add transition --json                                                       # every block tagged transition
```

The install folders are read from `hyperframes.json` (`paths.blocks`, `paths.components`, `paths.assets`); when the
file is missing, `add` creates it with the defaults.

## Mounting a block

A block is mounted by a host `div` whose `data-composition-id` equals the id inside the block file:

```html
<div id="data-chart" data-composition-src="compositions/data-chart.html" data-composition-id="data-chart"
     data-track-kind="graphics" data-track-index="2" data-start="2" data-duration="8"
     data-width="1920" data-height="1080" data-variable-values='{"title":"Weekly installs"}'></div>
```

- Keep the host's `data-duration` within the block's own length.
- To place a block in part of the frame, style the host (`position:absolute; right:0; width:40%`).
- The runtime seeks the block's timeline itself, shifted by the host's `data-start`; the host's timeline never refers
  to it.
- Blocks that cut on beats read their hit times from the `beats/<audio>.json` that `npx hyperframes beats` writes,
  after subtracting the mount's `data-start` from each beat time.

## Merging a component

A component is merged by hand, following the comment block at the top of the installed file: its markup goes inside
your composition root, its CSS into your `<style>`, its setup script ahead of your timeline code, and any timeline
calls into your timeline at times you pick. It inherits the host scene's size and duration.

## Making an item your own

- Choose the biggest item that covers the beat and edit it down; once installed, it is your code.
- Leave its ids and class prefixes exactly as installed, so two items can never clash.
- Change colours and fonts through the item's variables, pointed at the brand's values, rather than editing literals.
- Run `npx hyperframes check --json` once it is wired in, and snapshot the frames where it plays.

## When nothing fits: reporting a catalog gap

Say so before building the effect by hand. `catalog --query` prints a ready report line (`report_gap` in the JSON):
`npx hyperframes feedback --search-miss "<query>" --wanted "<the move you needed>" --tier <tier>`. Describe the
effect you wanted rather than inventing an item name.

## Contributing an item upstream

New blocks and components reach the public registry as a pull request to the HyperFrames repository. A block goes in
`registry/blocks/<name>/`, a component in `registry/components/<name>/`, each as `<name>.html` with a
`registry-item.json` beside it (name, type `hyperframes:block` or `hyperframes:component`, title, description, tags,
and for a block its dimensions and duration). Give every element id a two- or three-letter prefix taken from the
item's name so it cannot clash in someone else's project, expose colours, fonts and copy as variables, and make the
item pass `npx hyperframes check --json` inside a demo composition. The repository's contributing guide and quality
bar set the rules; read both first.

## Verify the wiring

```bash
npx hyperframes check --json                    # clean after wiring
npx hyperframes snapshot --range 2,10 --frames 6  # the mounted block plays inside its window (data-start 2, duration 8)
grep -n 'data-composition-id="data-chart"' index.html compositions/data-chart.html   # the two ids match
```

## Gotchas

- **Symptom:** the mounted block is empty. **Cause:** the host's `data-composition-id` differs from the id in the
  block file. **Fix:** copy the id from the block file.
- **Symptom:** two items break each other. **Cause:** prefixed ids were renamed to generic ones and now collide.
  **Fix:** restore the installed prefixes.
- **Symptom:** `add` fails on a plane. **Cause:** only manifests are cached; item files download on every `add`.
  **Fix:** install while online.
- **Symptom:** the same tag lists different items a month later. **Cause:** the registry keeps growing. **Fix:** write
  the exact item names into the plan.

## Anti-patterns

| Do not | Do instead |
|---|---|
| hand-writing a named effect before searching | `catalog --query` with an English description of the beat |
| renaming an item's prefixed ids | leave them, so two items cannot clash |
| editing colour literals in an item | set them through the item's variables |
| inventing an item name in a gap report | describe the effect you wanted |

## Checklist

- [ ] Searched with an English description of the beat before writing the effect.
- [ ] Each block's host id equals its `data-composition-id`; the mount is no longer than the block.
- [ ] Component parts merged in the right places; prefixed ids kept.
- [ ] Brand colours and fonts set through the item's variables.
- [ ] `check --json` clean after wiring; the mounted frames snapshotted.

## References

- [references/wiring-examples.md](references/wiring-examples.md): a block and a component wired end to end, and custom install paths.

## See also

`hyperframes`, `hyperframes-transitions`, `hyperframes-captions`.
