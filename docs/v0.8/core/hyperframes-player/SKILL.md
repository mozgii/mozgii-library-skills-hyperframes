---
name: hyperframes-player
description: Embeds HyperFrames compositions in a website or web app with the hyperframes-player web component (@hyperframes/player) - script or npm install, attributes, the play, pause and seek API, events, playing a range or looping a section, posters and muted autoplay, React, Next.js and Vue usage, many players on one page, sending live data into a composition with setRuntimeData, the opaque sandbox for untrusted compositions, and falling back to a rendered MP4. Use when someone wants to show a HyperFrames video live in a page, build a preview or template gallery, control playback from their own UI, or embed compositions instead of video files.
metadata:
  tags:
  - hyperframes
  - player
  - web-component
  - embed
  - react
  - nextjs
  - preview
  - interactive
---

# HyperFrames player

The HyperFrames player is the `<hyperframes-player>` custom element from `@hyperframes/player`. It loads a
composition's HTML in a sandboxed iframe inside its shadow DOM, scales it to the element's box, and drives the
composition's timeline the way a `<video>` element drives a file: play, pause, seek, rate, volume, events. The
composition plays live in the viewer's browser, so text stays sharp at any size and the page can change its data.
Checked against `@hyperframes/player` 0.8.223.

## When to use this skill

Use this skill to show a composition inside a web page or app (a landing page hero, a template gallery, a preview
pane in your own editor, a docs page), to control playback from your own buttons, or to feed live values into a
composition. To produce a file use `render-and-export`; to edit compositions from code use `hyperframes-automation`.

## Step 0: read the player version the page loads

```bash
npm ls @hyperframes/player --depth=0 2>/dev/null                              # a bundled app
grep -rhoE '@hyperframes/player@[0-9.]+' --include='*.html' . | sort -u       # a script tag
npx hyperframes --version                                                     # the CLI that built the composition
```

Pin one exact version: every `@hyperframes/*` package is released together.

## Player or rendered video

The choice between the live player and a rendered video file depends on who watches and where.

| Need | Use | Because |
|---|---|---|
| A file for social platforms, email, a CMS | a rendered MP4 (`npx hyperframes render`) | plays everywhere, no script |
| Values that change per viewer or per click | the player with `setRuntimeData` or variables | no render per version |
| A preview inside your own editor or gallery | the player | seek, scrub and edit without encoding |
| Heavy WebGL, many videos, weak devices | a rendered MP4, or the player with `type="video/mp4"` | the viewer's GPU does not have to keep up |
| Search engines and link previews | a rendered MP4 plus a poster | crawlers do not run compositions |

## Add the player to a page

Adding the player to a page takes one script and one element. Pin the version in the URL.

```html
<script src="https://cdn.jsdelivr.net/npm/@hyperframes/player@0.8.223/dist/hyperframes-player.global.js"></script>

<hyperframes-player
  src="/videos/launch/index.html"
  controls
  poster="/videos/launch/poster.jpg"
  style="display:block;width:100%;max-width:960px;aspect-ratio:16/9"></hyperframes-player>
```

With a bundler, `npm install @hyperframes/player` and `import "@hyperframes/player";` once; the import registers the
element. The composition folder (its `index.html`, `compositions/` and `assets/`) must be served over HTTP from a
path the page can reach; `file://` pages cannot load it. Asset paths inside the composition resolve against the
composition's own URL.

## Attributes

Attributes configure the player; most also exist as properties.

| Attribute | Meaning |
|---|---|
| `src` | URL of the composition HTML, or of a video file when `type` is set |
| `type` | a `video/...` type: plays `src` as a plain video behind the same API |
| `srcdoc` | the composition HTML as a string; wins over `src` |
| `width`, `height` | the composition's native size, for the aspect ratio only (default 1920×1080) |
| `controls` | built-in play, scrub, speed, time and volume controls |
| `autoplay`, `muted`, `loop` | start when ready (needs `muted` without a user gesture), mute, restart at the end |
| `poster` | image shown before the first play |
| `playback-rate`, `volume` | speed multiplier; volume 0 to 1 |
| `range-start`, `range-end` | play only the film's seconds `[start, end)`; parks on `range-start` and loops there with `loop` |
| `audio-locked` | force muted playback and hide volume controls |
| `low-power-idle` | a paused player polls once per second rather than every 80 ms; worth it when a page holds many players |
| `disable-click-to-play` | a click on the player no longer toggles playback, so the page can handle it |
| `no-load-timeout` | a slow load is not failed after 8 s; the page decides how long to wait |
| `assets-loading-ui` | `none` hides the loading card; asset events still fire |
| `sandbox-origin` | `opaque` isolates the composition from the page (next sections) |

The `width` and `height` attributes do not set the display size: size the element with CSS (`width` and
`aspect-ratio`) or its container.

## Control playback from JavaScript

Controlling playback from JavaScript uses the same names as a media element.

```js
const player = document.querySelector("hyperframes-player");
player.addEventListener("ready", (e) => console.log("duration", e.detail.duration));
document.querySelector("#play").onclick = () => (player.paused ? player.play() : player.pause());
document.querySelector("#chapter-2").onclick = () => player.seek(12.5);
player.playbackRate = 1.5;
player.muted = true;
console.log(player.currentTime, player.duration, player.ready, player.compositionWidth);
```

| Event | Detail | Fires |
|---|---|---|
| `ready` | `{ duration, compositionWidth, compositionHeight }` | composition loaded and timeline found |
| `timeupdate` | `{ currentTime }` | about 10 times a second while the position changes |
| `play`, `pause`, `ended` | none | playback state changed; `ended` only without `loop` |
| `durationchange`, `resize` | new duration or size | after `ready` |
| `scenes` | `{ scenes }` | the runtime reported its scene list (build chapter buttons from it) |
| `rangeclamped` | `{ rangeStart, rangeEnd, duration }` | a range past the film was cut, or an empty one ignored |
| `error` | `{ message }` | load or runtime error |
| `playbackerror` | `{ source, error }` | the browser blocked playback, usually unmuted autoplay |

Listen for `ended` rather than comparing `currentTime` with `range-end`: at the end the player holds the last frame
before the range end.

## Loop a section of a film

Looping a section of a film plays one stretch, such as a hero loop cut from a longer launch film, without a separate
render:

```html
<hyperframes-player src="/videos/launch/index.html" autoplay muted loop
  range-start="8" range-end="14" low-power-idle disable-click-to-play></hyperframes-player>
```

## React, Next.js and Vue

React, Next.js and Vue use the element like any custom element once the package is imported in browser code.

```tsx
"use client";                                         // Next.js App Router: the element needs the browser
import { useEffect, useRef } from "react";
import "@hyperframes/player";

export function Preview({ src, onEnd }: { src: string; onEnd: () => void }) {
  const ref = useRef<HTMLElement & { play(): void; seek(t: number): void }>(null);
  useEffect(() => {
    const el = ref.current;
    el?.addEventListener("ended", onEnd);
    return () => el?.removeEventListener("ended", onEnd);
  }, [onEnd]);
  return <hyperframes-player ref={ref} src={src} controls style={{ width: "100%", aspectRatio: "16 / 9" }} />;
}
```

- Attach event listeners through a ref; custom element events are DOM events, not React props.
- In TypeScript, declare the element in `JSX.IntrinsicElements` (or import the package's `HyperframesPlayer` type)
  so `<hyperframes-player>` type-checks.
- In Next.js, import the package only from a client component, or with `next/dynamic` and `ssr: false`; importing it
  in a server component fails because custom elements need `window`.
- In Vue, tell the compiler it is a custom element (`compilerOptions.isCustomElement: tag => tag === "hyperframes-player"`)
  and bind with `:src`.

## Send live data into a composition

Sending live data into a composition uses a named channel: the page calls `player.setRuntimeData(channel, payload)`
and the composition registers a handler for that channel. Channel names are lowercase letters, digits and hyphens.
The payload is cloned and kept, and delivered once the composition's runtime is ready, so the call may come before
`ready`.

```js
// in the page
player.addEventListener("runtimedataapplied", (e) => console.log("applied", e.detail.channel));
player.addEventListener("runtimedataerror", (e) => console.error(e.detail.message));
player.setRuntimeData("headline", { text: "Welcome back, Ada" });
```

```js
// in the composition, before its timeline is built
window.__hyperframes.registerRuntimeDataHandler("headline", ({ text }) => {
  document.getElementById("headline").textContent = text;
});
```

Live data changes only what the viewer's browser shows. A rendered file takes its values from variables at render
time (`--variables`), so keep the two paths fed from the same data when both exist.

## Untrusted compositions and the opaque sandbox

The opaque sandbox matters when the page embeds compositions it did not write (user uploads, a template marketplace).
By default the player's iframe keeps `allow-same-origin`, so editor integrations can reach the composition's DOM;
that is a trusted-content mode in which composition code can also reach the embedding page. For anything you did not
write, set `sandbox-origin="opaque"`: scripts still run, but the composition cannot read the parent page, and
`iframeElement.contentDocument` is unavailable. Changing the attribute reloads the composition. Serve untrusted
compositions from a separate origin as well.

## Many players on one page

Many players on one page (a gallery of templates) each run a live document, so budget them.

- Show posters and create or start a player only when its card scrolls into view (an `IntersectionObserver`).
- Add `low-power-idle` to every paused player.
- Keep only one player playing at a time; pause the others on `play`.
- For heavy compositions, use the rendered MP4 with `type="video/mp4"` in the gallery and the live player on the
  detail page; the API and events stay the same.

## Verify the embed

```bash
curl -sI http://localhost:3000/videos/launch/index.html | head -1             # 200 over HTTP, never file://
curl -sI http://localhost:3000/videos/launch/assets/hero.mp4 | head -1        # assets resolve beside it
grep -n 'sandbox-origin' src/ -r                                              # every untrusted embed is opaque
```

Then in the browser console: `document.querySelector("hyperframes-player").ready` is `true`, `error` and
`playbackerror` have not fired, and a muted autoplay really starts.

## Checklist

- [ ] Player script version pinned; the composition folder served over HTTP.
- [ ] Display size set with CSS; `width`/`height` attributes match the composition's native size.
- [ ] Autoplay only with `muted`; `playbackerror` handled.
- [ ] Event listeners attached through a ref or `addEventListener`, and removed on unmount.
- [ ] `sandbox-origin="opaque"` on any composition the page did not write.
- [ ] A poster and a rendered MP4 exist for crawlers, previews and weak devices.

## Gotchas

- **Symptom:** A blank player. **Cause:** The page opened from `file://`, or `src` points at a folder without its
  `assets/`. **Fix:** serve the whole composition folder over HTTP.
- **Symptom:** Autoplay does nothing. **Cause:** Unmuted autoplay is blocked. **Fix:** add `muted` or start on a
  click.
- **Symptom:** `iframeElement.contentWindow` is null. **Cause:** The code passed the player element where an iframe
  was expected. **Fix:** read `player.iframeElement`, and only in the default same-origin mode.
- **Symptom:** Next.js build error `window is not defined`. **Cause:** The package was imported in a server component.
  **Fix:** import it from a client component, or with `next/dynamic` and `ssr: false`.
- **Symptom:** The page slows down with many players. **Cause:** Every paused player still polls. **Fix:** use
  `low-power-idle` and lazy creation.
- **Symptom:** Live data shows in the page but not in the MP4. **Cause:** Renders read variables, not runtime data.
  **Fix:** feed `--variables` from the same data.

## Anti-patterns

| Do not | Do instead |
|---|---|
| comparing `currentTime` with `range-end` | listen for `ended` |
| sizing with `width` and `height` attributes | CSS on the element or its container |
| the default sandbox for user uploads | `sandbox-origin="opaque"`, served from a separate origin |
| every card playing live in a gallery | posters, one player playing at a time, MP4 with `type="video/mp4"` for heavy pieces |

## See also

`hyperframes`, `hyperframes-automation`, `render-and-export`, `hyperframes-slideshow`.
