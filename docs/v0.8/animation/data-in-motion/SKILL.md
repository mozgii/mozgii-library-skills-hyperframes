---
name: data-in-motion
description: Animates numbers, charts and maps for video in HyperFrames - count-ups, bar and line charts built in SVG and drawn in reading order, one highlighted series, chart libraries such as D3 driven from a GSAP tween instead of their own transitions, map libraries (MapLibre, Mapbox, Leaflet, Google Maps) registered for readiness, and baked basemaps for real places. Use when a video shows statistics, KPIs, a chart, a data story, a route or a map.
metadata:
  tags:
  - data-visualization
  - charts
  - d3
  - svg
  - maps
  - maplibre
  - numbers
  - hyperframes
---

# Data, charts and maps in motion

Data in motion is a chart or number built for a viewer who gets three seconds and cannot pause. A web dashboard asks
the reader to explore; a video chart says one thing, draws it in reading order, and holds it. This skill covers
numbers, SVG charts, chart libraries and maps in HyperFrames.

## When to use this skill

Use this skill for statistics, KPIs, growth curves, comparisons, rankings, data stories, routes and maps in a video.

## Step 0: read the chart and map versions

```bash
grep -rhoE '(d3|gsap|maplibre-gl|mapbox-gl|leaflet)@[0-9]+\.[0-9]+\.[0-9]+' --include='*.html' . | sort -u
npm ls d3 gsap --depth=0 2>/dev/null
npx hyperframes --version
```

The D3 pattern below was checked against 7.9.0; the d3 and map readiness hooks ship with the CLI.

## One number at a time

Show one figure at a time, and make it count:

| Rule | Detail |
|---|---|
| Size | the figure is the largest element in the frame |
| Digits | tabular figures (`font-variant-numeric: tabular-nums`), so digits keep their width and a count-up never wobbles |
| Count-up timing | A count-up runs 1.2 to 1.6 s and then stops dead, ending on a beat or a hard stop |
| Something physical | every figure comes with an object sized by it: a filling bar, a ring, a shape scaled to the value |
| Honesty | real data only, rounded identically everywhere, credited by a small source line on screen |
| One source | a single data module (a JSON object or variables) feeds every figure in the film |
| Continuity | figures for one concept over time (Q1 to Q4) stay in the same visual space; only the value changes |

## Charts as pictures

A video chart builds in the order a viewer reads it: the frame and axis first, then a reference line, then the data
drawing on, and last a single note on the point that matters.

- The series that carries the point gets the accent colour; every other series goes grey. The title states the
  takeaway.
- Labels sit on the marks themselves. Legends, gridlines and dense ticks stay out.
- Pie charts, twin axes and six-panel dashboards do not work at video speed; two or three related figures side by
  side is the most a frame can hold.
- Objects can travel between beats: the last bar turns into the floor of the next scene, or a line becomes the path
  the camera flies along.

## Bar chart in SVG

A bar chart in SVG grows each bar from its baseline with a stagger, then labels the highlighted bar. This is a
complete `index.html`: the takeaway as the title, the axis first, the bars next, the note last, one count-up, and a
source line.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0f1115; color: #f4f1ea;
            font-family: Inter, Arial, sans-serif; }
    #takeaway { position: absolute; left: 160px; top: 100px; margin: 0; font-size: 64px; font-weight: 800; }
    #figure { position: absolute; right: 160px; top: 60px; font-size: 140px; font-weight: 800; color: #ff5a36;
              font-variant-numeric: tabular-nums; }
    #source { position: absolute; left: 160px; bottom: 60px; font-size: 22px; color: #9aa0ad; }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="6" data-width="1920" data-height="1080">
    <h1 id="takeaway">Q4 beat every other quarter</h1>
    <div id="figure">+0%</div>
    <svg id="chart" viewBox="0 0 1200 600" style="position:absolute;left:360px;top:260px;width:1200px;height:600px">
      <line id="axis" x1="0" y1="560" x2="1200" y2="560" stroke="#3a3f4a" stroke-width="3"/>
      <g id="bars"></g>
      <text id="callout" fill="#ff5a36" font-weight="700" font-size="40"></text>
    </svg>
    <div id="source" data-layout-ignore>Source: example data</div>
  </div>
  <script>
    const DATA = [{ k: "Q1", v: 42 }, { k: "Q2", v: 55 }, { k: "Q3", v: 61 }, { k: "Q4", v: 88 }];
    const max = 100, bw = 180, gap = 100, g = document.getElementById("bars");
    DATA.forEach((d, i) => {
      const h = (d.v / max) * 520, x = i * (bw + gap) + 60;
      g.insertAdjacentHTML("beforeend",
        `<rect class="bar" x="${x}" y="${560 - h}" width="${bw}" height="${h}" rx="10" fill="${i === 3 ? "#ff5a36" : "#5b6170"}"/>`);
    });

    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#axis", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.2);
    tl.fromTo("#bars .bar", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.7,
      ease: "power3.out", stagger: 0.12 }, 1.0);

    const c = document.getElementById("callout");
    c.textContent = "Q4: 88"; c.setAttribute("x", 3 * (bw + gap) + 60); c.setAttribute("y", 560 - 0.88 * 520 - 24);
    tl.fromTo(c, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }, 1.9);

    const figure = document.getElementById("figure"), count = { v: 0 };
    tl.to(count, { v: 44, duration: 1.4, ease: "power2.out",
      onUpdate: () => { figure.textContent = `+${Math.round(count.v)}%`; } }, 1.0);

    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
```

Generate the bars once at init; the timeline is built synchronously after them. The rest of the film holds from 2.4 s
on, which is the three seconds the viewer gets to read the result.

## Line chart that draws in

A line chart that draws in reveals its path with a dash offset and moves a dot along the end.

```js
const path = document.querySelector("#trend");           // <path id="trend" pathLength="100" stroke-dasharray="100 120">
tl.fromTo(path, { strokeDashoffset: 110 }, { strokeDashoffset: 0, duration: 1.6, ease: "power2.inOut" }, 1);
```

With MotionPath, a marker follows the same path in step with the reveal (see `gsap`).

## Chart libraries driven by the timeline

Chart libraries driven by the timeline keep their drawing code but never their own transitions. Tween a progress
value on the GSAP timeline and redraw from it in `onUpdate`:

```js
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";
const x = d3.scaleLinear([0, 100], [0, 1200]);
const p = { v: 0 };
tl.to(p, { v: 1, duration: 1.4, ease: "power3.out", onUpdate: () => {
  d3.select("#bars").selectAll("rect").data(DATA).join("rect")
    .attr("y", (d, i) => i * 70).attr("height", 52).attr("width", (d) => x(d.v * p.v)).attr("fill", "#5b6170");
} }, 1);
```

When existing code uses D3 transitions, the HyperFrames d3 adapter waits for transitions pushed to `window.__hfD3`
to end before capture, but they still run on the browser clock: convert them to the pattern above for frame accuracy.
Registry charts come first: `npx hyperframes catalog --query chart --json`.

## Maps in a video

Maps in a video come in two kinds: diagram maps (outlines, borders, pins) and real places (a city, a route on
satellite imagery).

- Diagram maps: draw SVG from GeoJSON (Natural Earth outlines) and animate strokes, fills and pins with GSAP.
- Real places: tile servers can hand back different imagery from one render to the next. Record the camera move to a
  video file once, place that file, and draw borders, pins and labels over it as live SVG from known coordinates.
- Live map libraries can be registered for readiness so capture waits for tiles and style: push MapLibre maps to
  `window.__hfMaplibre`, Mapbox GL maps to `window.__hfMapbox`, Leaflet maps to `window.__hfLeaflet`, Google Maps to
  `window.__hfGoogleMaps`. Drive the camera (`jumpTo` with values from a tween), never `flyTo`, which runs on its own
  clock.
- Credit the imagery on screen in small type ("© OpenStreetMap contributors", the tile provider) and mark it
  `data-layout-ignore` so the text-size check skips it.

## Verify the numbers and the drawing order

```bash
npx hyperframes check --json                 # contrast and overflow on the real labels
npx hyperframes snapshot --at 0.9,1.4,2.2,4  # axis first, data next, the note last, then a hold
grep -rnE 'flyTo|\.transition\(' compositions index.html   # expect nothing
```

Read each figure in the last snapshot against the data source, not against the script.

## Checklist

- [ ] Every figure comes from one data source, with a source line on screen.
- [ ] One message per chart, in its title; one highlighted series.
- [ ] Charts draw in reading order: axis, reference, data, annotation.
- [ ] Count-ups 1.2 to 1.6 s with tabular figures, then a hold.
- [ ] Library charts redraw from a GSAP tween; no library transitions or `flyTo`.
- [ ] Map tiles baked to video for real places; credits on screen.

## Gotchas

- **Symptom:** Digits jitter during a count. **Cause:** Proportional figures. **Fix:** set `font-variant-numeric:
  tabular-nums`.
- **Symptom:** Viewers read none of the numbers. **Cause:** Every number counts up at once. **Fix:** stagger them by
  the narration.
- **Symptom:** Bars grow from the middle or float above the axis. **Cause:** `transformOrigin` was missing, or sat in
  the `to` values, where GSAP measures an SVG bar already scaled to zero. **Fix:** set `transformOrigin: "50% 100%"` in
  the `from` values of the `fromTo`.
- **Symptom:** The map differs between renders. **Cause:** Live tiles or `flyTo`. **Fix:** bake the move to video, or
  drive `jumpTo` from the timeline.

## Anti-patterns

| Do not | Do instead |
|---|---|
| pie charts, twin axes, six-panel dashboards | two or three related figures side by side at most |
| legends and dense ticks | labels on the marks themselves |
| D3 transitions or `flyTo` | a GSAP tween of a progress value, redrawn in `onUpdate` |
| figures typed separately into each scene | one data module feeding every figure |

## See also

`gsap`, `motion-design`, `video-design-system`, `hyperframes-registry`.
