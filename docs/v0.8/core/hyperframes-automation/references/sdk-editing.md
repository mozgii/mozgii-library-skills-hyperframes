---
title: Editing compositions with the HyperFrames SDK
author: MOZGII, Inc.
lang: en
---

# Editing compositions with the HyperFrames SDK

The HyperFrames SDK (`@hyperframes/sdk`) is a headless editing engine for composition HTML: it parses a composition,
gives every element a stable id, applies typed edits, emits JSON patches, keeps undo history and serializes the
result. It runs in Node or a browser without Studio or React, so a script can change a headline with
`openComposition(html)`, one typed edit and `comp.serialize()`. Checked against version 0.8.223.

## Contents

The sections of this page:

- Opening a composition and element ids
- Finding elements
- Typed edit methods
- Variables from the SDK
- Animation edits
- Batches and dispatch
- Persistence adapters
- Undo, redo and patches
- Override mode for templates
- Gotchas when editing from code

## Opening a composition and element ids

Opening a composition with `openComposition(html, options)` is async: it parses the HTML and stamps a `data-hf-id`
on every element that lacks one, so later edits target the same element even after text or position changes. Every
edit names an element by that id, never by a selection or a mouse position, which makes edits safe for agents and
back-end jobs. Serialize with `comp.serialize()` and release the session with `comp.dispose()`.

```ts
import { openComposition } from "@hyperframes/sdk";
const comp = await openComposition(html);
const ids = comp.getElements().filter((e) => e.tag === "img").map((e) => e.id);
const updated = comp.serialize();
comp.dispose();
```

Save the serialized HTML once after the first open: the stamped ids are part of it, and the next session finds the
same ids.

## Finding elements

Finding elements uses `comp.find(query)`, which returns scoped ids for every element matching all given fields.

| Field | Matches |
|---|---|
| `tag` | the exact tag name |
| `text` | a substring of the element's text |
| `name` | the exact `data-name` attribute |
| `track` | the exact track index |
| `composition` | elements inside the sub-composition host with that id |

Elements inside a mounted scene have a scoped id `"hf-HOST/hf-LEAF"` (deeper nesting adds segments). Always pass the
scoped id that `find()` or `getElements()` returned; a bare leaf id fails when the same leaf id appears in two scenes.
`comp.getElement(id)` returns one snapshot or `null`.

## Typed edit methods

Typed edit methods are the readable way to change a composition; each becomes one operation and one patch.

| Method | Changes |
|---|---|
| `setText(id, text)` | the element's text |
| `setStyle(id, { color, fontSize, ... })` | inline styles, camelCase names |
| `setAttribute(id, name, value)` | one attribute, such as `src` |
| `setTiming(id, { start, duration })` | the clip's `data-start` and `data-duration` |
| `setHold(id, { start, end, fill })` | an elastic hold: during the pause the element either stops on one frame or repeats |
| `addElement(parentId, index, html)` | inserts markup; returns the new id |
| `removeElement(id)` | removes the element |

## Variables from the SDK

Variables from the SDK can be read, set, declared and validated: `listVariables()`, `getVariableValue(id)`,
`setVariableValue(id, value)`, `declareVariable(...)`, `getVariableDeclarations()`, `getVariableValues()`,
`validateVariableValues(values)` and `getVariableUsage()`. `setPreviewVariables(values)` changes what a preview
shows without writing values into the file. Validate a row with `validateVariableValues` before queueing its render.

## Animation edits

Animation edits change the composition's GSAP timeline as data: `addGsapTween(target, spec)` returns an animation
id, `setGsapTween(animationId, spec)` changes it, `removeGsapTween(animationId)` removes it, and
`getAllAnimationIds()` lists them. `getElementTimings()` reads every element's timing. Review motion added this way
in a preview: a tween that is valid data can still look wrong.

## Batches and dispatch

Batches group several edits into one undo entry, one persistence write and one `change` event:
`comp.batch(() => { ...edits... })`. `comp.dispatch(op)` applies a data-shaped operation (`{ type: "setStyle", ... }`),
which suits agents that produce edits as JSON; `comp.can(op)` checks whether an operation is allowed first.

## Persistence adapters

A persistence adapter writes each edit as it is made; bursts of quick edits are merged and saved in the order they
happened.

```ts
import { openComposition } from "@hyperframes/sdk";
import { createFsAdapter } from "@hyperframes/sdk/adapters/fs";

const adapter = createFsAdapter({ root: "./renders/acme-q3" });
const comp = await openComposition(template, { persistPath: "index.html", persist: adapter });
comp.on("persist:error", ({ error }) => process.exitCode = (console.error(`save failed: ${error.message}`), 1));
for (const [id, text] of Object.entries({ "hf-title": "Q3 at Acme", "hf-kicker": "Revenue up 18%" })) {
  comp.setText(id, text);           // each edit is queued for the adapter
}
await comp.flush();                  // block until every queued write has landed
comp.dispose();
```

| Import | Adapter |
|---|---|
| `@hyperframes/sdk/adapters/fs` | writes to a folder and keeps up to 20 versions under `.hf-versions/` |
| `@hyperframes/sdk/adapters/memory` | in memory, for tests and short sessions |
| `@hyperframes/sdk/adapters/headless` | no preview, for agents, CI and servers |
| `@hyperframes/sdk/adapters/iframe` | drives a live preview iframe |

Persistence failures arrive as `persist:error` events, not thrown errors: always listen for them.

## Undo, redo and patches

Undo, redo and patches come built in: a standalone session keeps history (`undo()`, `redo()`, `canUndo()`,
`canRedo()`), coalescing edits of the same kind on the same element within 300 ms so a slider drag is one entry.
Every committed change emits a `patch` event with RFC 6902 `patches` and `inversePatches`, its `origin` and `opTypes`;
store those for audit logs or collaboration, and replay them with `applyPatches()`. Pass `history: false` when the
host application owns undo; autosave keeps working.

## Override mode for templates

Override mode stores only what one instance changed on top of a shared base template. Open the base with
`overrides: storedDelta`; read the current delta with `comp.getOverrides()` and save it per customer or per project.
Keys look like `"hf-title.text"`, `"hf-logo.attr.src"`, `"hf-cta.style.color"`; inserted elements are kept with
their position. The base file never changes, so fixing the template fixes every instance that did not override that
field.

## Gotchas when editing from code

Gotchas when editing compositions from code:

- **Edits land on the wrong scene.** A bare leaf id was used inside a sub-composition; use the scoped id.
- **Ids change between runs.** The stamped HTML was never saved; serialize and save after the first open.
- **Lost writes at exit.** The process exited before `flush()` finished.
- **Silent autosave failure.** No `persist:error` listener.
- **A valid edit looks broken.** The SDK checks structure, not design: run `npx hyperframes check --json` and look at
  snapshots after automated edits.
