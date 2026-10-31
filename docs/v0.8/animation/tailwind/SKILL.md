---
name: tailwind
description: Uses Tailwind CSS v4 in HyperFrames compositions - the pinned @tailwindcss/browser runtime from hyperframes init --tailwind, window.__tailwindReady before frame 0, CSS-first @theme and @utility blocks, static class tokens the runtime can scan, v3 to v4 renames, and compiling to a stylesheet for offline renders. Use when a project was scaffolded with Tailwind, when writing utility classes in composition HTML, when styles are missing in a render, or when migrating v3 Tailwind into a video.
metadata:
  tags:
  - tailwind
  - tailwindcss
  - css
  - hyperframes
  - styling
---

# Tailwind CSS for video

Tailwind CSS v4 styles HyperFrames compositions through its browser runtime, which scans the page's classes and
writes CSS for them. `npx hyperframes init --tailwind` pins the runtime (`@tailwindcss/browser@4.2.4` in CLI 0.8.223;
the latest Tailwind is 4.3.3), and renders wait for `window.__tailwindReady` before frame 0. Use Tailwind for layout
and look that do not change; anything timed belongs to GSAP or another runtime that can seek.

## When to use this skill

Use this skill for a project created with `--tailwind`, for utility classes in composition HTML, for missing styles in
a render, or when bringing v3 Tailwind habits into a v4 video project.

## Step 0: read the Tailwind runtime the film loads

```bash
grep -rhoE '@tailwindcss/browser@[0-9.]+' --include='*.html' . | sort -u   # the pin in the script tag
npm ls tailwindcss @tailwindcss/cli --depth=0 2>/dev/null                  # a compiled setup
npx hyperframes --version                                                  # the pin `init --tailwind` writes
```

A project scaffolded by the CLI stays on the CLI's pin until someone changes it on purpose.

## Version contract

The version contract keeps renders reproducible.

- Keep the pinned runtime script the CLI wrote; never swap in `cdn.tailwindcss.com` (that is the v3 Play CDN).
- Upgrading the pin is a project decision: change the version in the script tag, then re-check every scene.
- For offline, locked-down or production renders, compile Tailwind to a stylesheet and link it instead of the runtime.

## Theme and custom utilities in v4

Theme and custom utilities in v4 live in CSS, in a `<style type="text/tailwindcss">` block.

```html
<style type="text/tailwindcss">
  @theme {
    --color-ink: #0b0d12;
    --color-paper: #f4f1ea;
    --color-accent: oklch(0.7 0.19 35);
    --font-display: "Inter", sans-serif;
  }
  @utility headline-balance { text-wrap: balance; letter-spacing: -0.01em; }
</style>
```

No `@tailwind base/components/utilities`, no `tailwind.config.js`. `@config` and `@plugin` abort the browser compile.

## A Tailwind scene

A Tailwind scene keeps fixed video dimensions and lets GSAP animate.

```html
<section id="hero" class="clip absolute inset-0 grid place-items-center bg-ink text-paper"
         data-start="0" data-duration="5" data-track-index="1">
  <div class="w-[1280px] text-center">
    <p class="mb-6 font-mono text-[28px] uppercase tracking-[0.18em] text-accent">Render-ready Tailwind</p>
    <h1 id="hero-title" class="headline-balance text-[120px] font-black leading-none">Utility classes, exact frames.</h1>
  </div>
</section>
```

Use pixel sizes in brackets (`text-[120px]`, `w-[1280px]`): the frame is fixed, so responsive breakpoints and
viewport units add nothing.

## Static class tokens

Static class tokens are required because the runtime only generates CSS for classes it can see. Never assemble a
render-critical class at seek time (`"bg-" + color + "-500"`). Vary items with CSS variables or data variants:

```html
<span class="inline-block translate-y-[calc(var(--i)*6px)]" style="--i:2"></span>
<div data-tone="rose" class="bg-blue-500 data-[tone=rose]:bg-rose-500"></div>
```

## v3 habits that break in v4

v3 habits that break in v4, and their replacements:

| v3 | v4 |
|---|---|
| `tailwind.config.js` theme | `@theme` in CSS |
| `@tailwind base; ...` | not needed with the browser runtime |
| `shadow-sm`, `rounded-sm`, `blur-sm` | `shadow-xs`, `rounded-xs`, `blur-xs` (scale shifted down one step) |
| `outline-none` | `outline-hidden` |
| `flex-shrink-*`, `flex-grow-*` | `shrink-*`, `grow-*` |
| bare `border` was grey | bare `border` is `currentColor`: write `border-white/20` |
| `bg-opacity-50` | `bg-black/50` |

`@apply` inside a plain `<style>` block is not processed by the runtime; write the classes in HTML or use a
`text/tailwindcss` block.

## Compiling for offline renders

Compiling for offline renders produces a normal stylesheet from the same classes.

```bash
npx @tailwindcss/cli -i ./tailwind.css -o ./assets/tailwind.out.css --minify
```

`tailwind.css` holds `@import "tailwindcss";` plus the `@theme` and `@utility` rules, and `@source` lines if the
scanner must look in scene files. Link the output in `index.html` and remove the runtime script.

## Verify Tailwind in the render

```bash
npx hyperframes check --json                           # contrast and layout on the real styles
npx hyperframes snapshot --at 0                        # frame 0 is styled
grep -rn 'cdn.tailwindcss.com' --include='*.html' .    # expect nothing: that is the v3 Play CDN
grep -rnE '"(bg|text|border)-" *\+' compositions index.html   # expect nothing: assembled class names
```

Look at the first frame at full size: an unstyled flash appears there before anywhere else.

## Checklist

- [ ] Pinned runtime kept, or compiled CSS linked; never the v3 Play CDN.
- [ ] Theme in `@theme`, custom classes in `@utility`; no config file.
- [ ] Every class written in full in the HTML.
- [ ] Fixed pixel sizes; no hover, focus or breakpoint variants for visible content.
- [ ] Tweens on Tailwind-styled elements set start states in `fromTo`, not in a `translate-*` class.

## Gotchas

- **Symptom:** An unstyled first frame. **Cause:** The runtime had not finished. **Fix:** keep the pinned script that
  sets `window.__tailwindReady`.
- **Symptom:** Measurements come out wrong. **Cause:** They were taken before Tailwind applied. **Fix:** measure after
  `__tailwindReady`.
- **Symptom:** An element lands in the wrong place. **Cause:** A `translate-*` class writes the CSS `translate`
  property, which adds to GSAP's `transform`, so the element ends offset by both. **Fix:** set the start position in
  the tween instead.
- **Symptom:** Faint borders vanish. **Cause:** v4's bare `border` uses the text colour. **Fix:** set the colour
  explicitly.

## Anti-patterns

| Do not | Do instead |
|---|---|
| swapping in the latest runtime without re-checking | treat the pin as a project decision and re-check every scene |
| `tailwind.config.js` | `@theme` and `@utility` in CSS |
| `@apply` in a plain `<style>` | write the classes in HTML, or use a `text/tailwindcss` block |
| responsive breakpoints and viewport units | pixel sizes in brackets; the frame is fixed |

## See also

`hyperframes`, `video-design-system`.
