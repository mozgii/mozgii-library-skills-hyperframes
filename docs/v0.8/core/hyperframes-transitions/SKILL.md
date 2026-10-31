---
name: hyperframes-transitions
description: Chooses and builds scene transitions for HyperFrames videos - hard cuts, match cuts, CSS transitions (push, iris, zoom, dissolve, blur, blinds, light leak, glitch, shutter, grid) and WebGL shader transitions from @hyperframes/shader-transitions - picked by energy, mood and narrative position, with the CSS rules shader capture needs. Use when moving between scenes, when a video feels like slides or jump cuts, or when adding crossfades, wipes, reveals or shader transitions.
metadata:
  tags:
  - hyperframes
  - transitions
  - scenes
  - webgl
  - shaders
  - gsap
  - cuts
---

# HyperFrames scene transitions

Every seam between two scenes tells the viewer how they relate. A hard cut means "now"; a push means "the next
point"; a blur crossfade means "stay with me"; zooming through a button means "we are going inside". Choose the
transition from what the content is doing, then build it in CSS and GSAP, take a registry block, or use a WebGL
shader. Checked against `@hyperframes/shader-transitions` 0.8.223 and GSAP 3.15.0.

Reach for this skill whenever a composition has two or more scenes, whenever a film "feels like slides", and for any
request for a crossfade, wipe, iris, zoom, glitch, light leak or shader transition.

## Step 0: is the shader package loaded, and which version?

```bash
grep -rhoE '@hyperframes/shader-transitions@[0-9.]+' --include='*.html' . | sort -u
grep -rn 'HyperShader.init' --include='*.html' . | head
```

No match means the film uses CSS transitions only, which is fine; mixing the two in one film is covered below.

## Rules for every seam

- A film should use between 3 and 5 kinds of transition. Fewer looks monotonous, more looks like a demo reel.
- Something on screen should cause each transition: an object that grows into the next world, a click that opens an
  iris, a move that whips into the next shot.
- Hard cuts are for punch-ins inside a scene. Between beats, no more than a third of the seams are hard cuts.
- Cut where a move is fastest, keeping direction and speed the same on both sides.
- A crossfade claims continuity, so two different worlds never crossfade.
- The outgoing scene stays whole until the transition begins: the transition is how it leaves. Emptying a scene with
  exit tweens and then transitioning from a blank frame wastes the seam.
- Mirror the eases across the seam (`power3.in` leaving, `power3.out` arriving) so the speed carries over.

## Transitions made from objects on screen

The strongest seams are built from something the viewer is already watching. They were measured frame by frame in
well-made launch films, and they sort by what on screen sets them off:

**A click or a button**

- *Iris from the click*: a `clip-path: circle()` grows from the point that was clicked and reveals the next world, taking 0.15 s.
- *Zoom through a button*: first the camera travels to the button under blur for 0.6 s; then, on a hard ease-in, the
  button swells from about 8% of the frame to about 250% in 0.35 s, and its fill becomes the next shot.

**An object that changes shape or place**

- *Morph*: a container stretches until it is the next one, for example an icon card turning into an input box, from
  about 110 px wide to about 880 px, over 0.2 s on `power3.out`, while a horizontal blur drops from 12 px to 0.
- *Object becomes the world*: a card or pill outgrows the frame on an ease-in-out lasting 0.65 s, its corner radius shrinking
  as it grows; the surroundings blur by about 15 px and fade within 0.3 s.
- *Carry across*: the finished result shrinks from scale 1 to 0.6, its blur peaking at 6 px halfway, and comes to rest
  in the next app as that app builds around it.

**A fast move**

- *Whip*: a smear, sideways or up and down, lasting 0.13 to 0.3 s; the incoming element lands soft and sharpens in about
  0.13 s.

**One stage that stays**

- *Colour flood*: the hero object does not move; only the background turns a new colour, in about 0.4 s on
  `power2.inOut`.
- *Blur swap*: on the way out, opacity goes to 0 while blurring by 8 px, over 0.13 to 0.2 s; on the way in, the blur clears
  in 0.13 s; the background never cuts.

**A cut that should look meant**

- *Dip cut*: the outgoing shot darkens by about 40% across the last 3 frames, then the hard cut lands.

## Picking a transition: energy, mood, position

Pick in three passes. Energy sets the primary transition, used on 60 to 70% of the seams; mood picks the one or two
accents; position decides where the accents go.

**Energy** (the primary, its duration and eases):

| Film energy | CSS primary | Shader primary | Duration | Eases |
|---|---|---|---|---|
| Calm: wellness, luxury, brand story | blur crossfade, focus pull | `cross-warp-morph`, `thermal-distortion` | 0.5 to 0.8 s | `sine.inOut`, `power1` |
| Medium: explainer, SaaS, corporate | push slide, staggered blocks | `whip-pan`, `cinematic-zoom` | 0.3 to 0.5 s | `power2`, `power3` |
| High: launch, sports, music | zoom through, overexposure | `ridged-burn`, `glitch`, `chromatic-split` | 0.15 to 0.3 s | `power4`, `expo` |

**Mood** (the accents):

| Mood | CSS | Shader |
|---|---|---|
| Warm, inviting | light leak, blur crossfade, focus pull, film burn | `light-leak`, `cross-warp-morph` |
| Cold, clinical | squeeze, zoom out, blinds, shutter, grid dissolve | `gravitational-lens` |
| Editorial | push slide, vertical push, diagonal split, shutter | `whip-pan` |
| Tech | grid dissolve, staggered blocks, blinds, chromatic aberration | `glitch`, `chromatic-split` |
| Tense | glitch, VHS, ripple | `ridged-burn`, `domain-warp` |
| Playful | elastic push, 3D flip, circle iris, morph circle | `ripple-waves`, `swirl-vortex` |
| Dramatic | zoom through, gravity drop, overexposure, dip to black | `cinematic-zoom` |
| Retro | film burn, light leak, VHS, clock wipe | none |

**Position** (where the boldest choice pays):

| Where in the film | What goes there |
|---|---|
| The opening seam | the most distinctive transition, 0.4 to 0.6 s; it sets the film's visual language |
| Between related points | the primary, kept consistent, around 0.3 s |
| A change of topic | something unlike the primary: blocks, shutter, squeeze |
| The climax or hero reveal | the boldest accent |
| Winding down | gentle again: blur crossfade, 0.5 to 0.7 s |
| The outro | slowest and simplest: crossfade or dip to black, 0.6 to 1 s |

## Building a CSS transition

A CSS transition is two scene containers tweened on the root timeline at a time `T`. Every CSS transition follows
the pattern of this push slide:

```js
const outgoing = "#scene1", incoming = "#scene2", T = 4.6;
tl.to(outgoing, { x: -1920, duration: 0.5, ease: "power3.inOut" }, T);
tl.fromTo(incoming, { x: 1920, opacity: 1 }, { x: 0, duration: 0.5, ease: "power3.inOut" }, T);
```

The template and code for each CSS transition: [references/css-transitions.md](references/css-transitions.md).
Ready-made versions in the registry: `npx hyperframes catalog --tag transition --json`.

## Building a shader transition

`@hyperframes/shader-transitions` captures each scene into a texture, blends the two with a fragment shader on a
WebGL canvas, and hands back a GSAP timeline:

```html
<script src="https://cdn.jsdelivr.net/npm/@hyperframes/shader-transitions@0.8.223/dist/index.global.js"></script>
<script>
  const tl = gsap.timeline({ paused: true });
  // scene tweens here
  HyperShader.init({
    bgColor: "#101820",                 // the scenes' own background colour
    accentColor: "#f2aa4c",
    scenes: ["opening", "features", "close"],
    transitions: [
      { time: 3.5, shader: "cross-warp-morph", duration: 0.75 },
      { time: 9.2, shader: "whip-pan", duration: 0.5, ease: "power3.inOut" },
    ],
    timeline: tl,
  });
  window.__timelines["main"] = tl;
</script>
```

When a film uses shaders, use them on every seam: `init()` throws unless `scenes.length === transitions.length + 1`,
so each neighbouring pair of scenes needs its entry. The shader list, the options and the CSS rules capture depends on:
[references/shader-transitions.md](references/shader-transitions.md).

## Verify the seams

```bash
npx hyperframes snapshot --review                       # seam strips: 0.2 s either side of every cut
npx hyperframes snapshot --range 4.5,4.7 --frames 6     # one seam in detail (T = 4.6)
```

Read every seam strip: no jump in position or colour, no blank frame, and the outgoing scene whole until `T`.

## Gotchas

- **Symptom:** the transition plays over an empty frame. **Cause:** exit tweens cleared the scene before the seam.
  **Fix:** delete those exits and let the transition take the scene out.
- **Symptom:** a shader transition shows black. **Cause:** the scene has no explicit `background-color`, or
  `bgColor` does not match it. **Fix:** set both to the same colour.
- **Symptom:** dark fringes around shapes in shader captures. **Cause:** a gradient uses the `transparent` keyword.
  **Fix:** use the same colour at zero alpha.
- **Symptom:** a visible jump at a cut. **Cause:** the two states differ at the seam. **Fix:** snapshot at T-0.1 and
  T+0.1 and line them up.
- **Symptom:** scrubbing backwards breaks a transition. **Cause:** state set in `onComplete`. **Fix:** `tl.set` at a
  time instead.

## Anti-patterns

| Do not | Do instead |
|---|---|
| exit tweens that empty a scene before the seam | let the transition take the scene out |
| a crossfade between two different worlds | a cut, a whip, or a move caused by something on screen |
| a shader on some seams and CSS swaps on others in one composition | one kind for the composition; a registry transition block for a single moment |
| a new transition kind at every seam | one primary on most seams and one or two accents |

## Checklist

- [ ] One primary on most seams, one or two accents; 3 to 5 kinds across the film.
- [ ] Each transition has a cause on screen or a reason in the story.
- [ ] Between beats, hard cuts on at most one seam in three; different worlds never crossfade.
- [ ] The outgoing content is whole when the transition starts.
- [ ] A shader film uses shaders on every seam and follows the capture rules.
- [ ] Seam strips read at every cut: no jump, no blank frame.

## References

- [references/css-transitions.md](references/css-transitions.md): the template, hard rules and code for 30 CSS transitions.
- [references/shader-transitions.md](references/shader-transitions.md): the shader package, its 14 shaders, options and capture rules.

## See also

`motion-design`, `hyperframes-registry`, `vfx`.
