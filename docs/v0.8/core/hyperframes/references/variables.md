---
title: HyperFrames variables and batch renders
author: MOZGII, Inc.
lang: en
---

# HyperFrames variables and batch renders

HyperFrames variables make one composition render many versions: a headline, a price, a brand colour, a theme or a
swapped image, with no edit to the HTML. A variable is declared once, bound to elements, and overridden per render or
per mount.

## Contents

The sections of this page:

- Declaring variables
- Binding variables without script
- Overriding variables at render time
- Per-mount values on scene hosts
- Batch renders from rows: one video per customer

## Declaring variables

Variables are declared as a JSON array on the composition's `<html>` element with `data-composition-variables`. Each
entry has `id`, `type`, `label` and `default`.

| Type | Extra fields | Checked at render |
|---|---|---|
| `string` | `placeholder`, `maxLength` | `typeof` is string |
| `number` | `min`, `max`, `step`, `unit` | `typeof` is number |
| `color` | none (hex string) | `typeof` is string |
| `boolean` | none | `typeof` is boolean |
| `enum` | `options: [{value, label}]` | value is one of the options |

```html
<html data-composition-variables='[
  {"id":"headline","type":"string","label":"Headline","default":"Hello","maxLength":40},
  {"id":"accent","type":"color","label":"Accent","default":"#ff5a36"},
  {"id":"theme","type":"enum","label":"Theme","default":"dark",
   "options":[{"value":"dark","label":"Dark"},{"value":"light","label":"Light"}]}
]'>
```

Give every variable a sensible `default`. Preview and Studio use the defaults, so a composition without them does not
look right until a render passes values.

## Binding variables without script

Variable bindings connect a declared value to an element with no JavaScript.

- `data-var-text="headline"` replaces the element's text.
- `data-var-src="hero"` replaces an image or media `src`; keep a real fallback `src` on media that has audio.
- `var(--accent)` in CSS reads a variable as a custom property.

For logic (choosing a layout from a theme, formatting a number), read the values once at init:

```js
const { headline, theme } = window.__hyperframes.getVariables();
document.body.dataset.theme = theme;
```

Read once at the top of the script, not inside `onUpdate` or a frame loop: each call allocates a new object.

## Overriding variables at render time

Render-time overrides are a JSON object keyed by variable id. Missing keys fall through to the defaults.

```bash
npx hyperframes render --variables '{"headline":"Q4 Report","theme":"light"}' --output q4.mp4
npx hyperframes render --variables-file ./vars.json --output q4.mp4
npx hyperframes render --variables-file ./vars.json --strict-variables   # fail on unknown keys or wrong types
```

Use `--strict-variables` in CI so a typo in a key fails the render instead of silently using the default.

## Per-mount values on scene hosts

Per-mount values let one scene file appear several times with different content. Each host passes its own object:

```html
<div id="plan-solo" data-composition-id="plan-solo" data-composition-src="compositions/plan.html"
     data-start="1.5" data-duration="2.5" data-width="1920" data-height="1080"
     data-variable-values='{"title":"Solo","price":"€12"}'></div>
<div id="plan-studio" data-composition-id="plan-studio" data-composition-src="compositions/plan.html"
     data-start="4" data-duration="2.5" data-width="1920" data-height="1080"
     data-variable-values='{"title":"Studio","price":"€49"}'></div>
```

Variables declared by a scene belong to each mount separately. The Variables panel in Studio and batch renders only
ever write root variables; a block that must change per batch row gets its value from a root variable passed down
into the host.

## Batch renders from rows: one video per customer

A batch render produces one video per row of variables: the same video with a different headline, price or name for
each customer, rendered from one rows file with `--batch rows.json`.

```json
{ "rows": [ { "name": "alpha", "headline": "Hello", "price": "$19" }, { "name": "beta", "headline": "Welcome", "price": "$29" } ] }
```

```bash
npx hyperframes render --batch rows.json --output "renders/{name}.mp4" --batch-concurrency 1 --strict-variables
```

- `--batch` cannot be combined with `--variables` or `--variables-file`.
- Output templates take `{index}` and row keys made of letters, digits, `_`, `.` or `-`; values must be strings,
  numbers or booleans. Missing placeholders and colliding outputs are errors.
- `--batch-concurrency` defaults to 1; each render already runs several Chrome workers.
- `--batch-fail-fast` stops after the first failure.
- The run writes `manifest.json` in the output folder with each row's status, output, error and timing. A batch is
  done when no row failed and every output exists, is non-empty and has the expected duration.
