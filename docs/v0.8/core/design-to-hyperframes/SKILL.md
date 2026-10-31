---
name: design-to-hyperframes
description: Brings an existing design into a HyperFrames video - Figma files through hyperframes figma (frozen SVG or PNG assets, brand colours and fonts as variables, frames as editable HTML components linked to those tokens), Figma storyboard frames rebuilt as motion between states instead of slides, product screens rebuilt as live UI that clicks and responds, and drafts from design tools (Claude Design, Open Design) checked and finished as working projects. Use when someone pastes a figma.com link, shares a design file, mockups, a brand kit or a design-tool export, or asks to animate their design.
metadata:
  tags:
  - figma
  - design-handoff
  - design-tokens
  - components
  - storyboard
  - brand
  - hyperframes
---

# Design to HyperFrames

A design that already exists (a Figma file, a set of mockups, a brand kit, a draft from a design tool) should become
a film that looks like the design and moves properly. The deciding question for every piece is whether anything
inside it changes on screen: if not, it stays an image; if so, it is rebuilt in HTML. All imports run while you
build and leave local files in the project, so rendering never contacts the design tool. Checked against CLI 0.8.223.

## Which path fits the design you were given

| You were given | Path | First command |
|---|---|---|
| A figma.com link to a file or a frame | tokens, then assets and components | `npx hyperframes figma tokens <fileKey>` |
| A Figma section of storyboard frames | match elements across frames, animate between states | tokens, then `figma asset` per element |
| Screenshots or mockups of a product | rebuild the parts that act as live UI, freeze the rest | none: build in HTML |
| A project folder from a design tool | treat it as an existing project and finish it | `npx hyperframes lint` |
| A live website | not this skill: `website-to-hyperframes` | `npx hyperframes capture <url>` |
| A brand guide with no frames | not this skill: `video-design-system` | none |

## Picture or HTML: sorting each piece

Sort every piece before importing anything. The signal is change: a piece whose content, colour, layout or state
changes during the film must be HTML.

| Stays an image (asset) | Becomes HTML |
|---|---|
| logos, icons, illustrations, textured artwork | an illustration whose parts move independently |
| a screenshot that makes its point as a still | a screen that performs an interaction or gets re-cropped |
| a component where exact pixels matter more than editing | text, colours, layout or toggle states that change |
| storyboard frames kept only as a look reference | storyboard frames whose meaning is the motion between them |

Animating a pile of finished screenshots because the design tool exported them never works: an image of a form
cannot be typed into, and viewers see the slideshow at once.

## Step 0: check the Figma token

Every `hyperframes figma` command reads a personal access token from `FIGMA_TOKEN`, in the shell or in the project's
`.env`. Check for it before the first import:

```bash
[ -n "$FIGMA_TOKEN" ] || grep -qs '^FIGMA_TOKEN=' .env && echo "token present" || echo "no FIGMA_TOKEN"
```

When it is missing, explain how to create one and stop. In Figma: Settings, Security, Personal access tokens, with
read-only scopes **File metadata** and **File content**, plus **Library content** (the styles fallback of `tokens`
needs it on plans below Enterprise) and **Variables** on Enterprise. The person sets the variable themselves. Never
ask for the token in the chat and never write it into a project file.

Errors the commands return, in the order you usually meet them:

| You see | Why | Do |
|---|---|---|
| `NO_TOKEN` | `FIGMA_TOKEN` is not set | create and set it as above |
| `BAD_TOKEN` | the token is wrong, expired or revoked (Figma replies 403 `Invalid token`) | create a new token |
| `ref has no node id` | the link is to a file, not to a layer | copy the layer's link, which carries `?node-id=` |
| `FORBIDDEN` (403) | a scope is missing, or this account cannot see the file | add the scope named in the message |
| `REQUIRES_ENTERPRISE` (403) | the variables API is Enterprise only | nothing: published styles were read instead |
| `RATE_LIMITED` (429) | Figma's per-minute limit, after the CLI's own retries | wait a minute or send fewer nodes per call |

Read the CLI version too, since the `figma` commands ship with it:

```bash
npx hyperframes --version
```

## Worked example: a Figma launch file to a 20-second film

The file key here is `AbC123`; the brand mark is node `3-14`, a hero illustration `3-15`, the pricing card frame
`10-20`. Tokens come first so every later import links to them:

```bash
# 1. Brand variables (or published styles below Enterprise): writes figma-tokens.json and a binding index,
#    and prints entries for the root's data-composition-variables.
npx hyperframes figma tokens AbC123

# 2. The mark as SVG, so its paths can be animated one by one.
npx hyperframes figma asset 'AbC123:3-14' --format svg --description "Ledgerly logo" --entity "Ledgerly"

# 3. Raster art at 2x; several nodes of one file go in one request.
npx hyperframes figma asset 'AbC123:3-15' 'AbC123:3-16' --format png --scale 2

# 4. The pricing card as editable HTML at exact Figma geometry.
npx hyperframes figma component 'https://www.figma.com/design/AbC123/Launch?node-id=10-20'

# 5. Gates before animating.
npx hyperframes lint && npx hyperframes check --json
```

What each import leaves behind:

- **Assets** are frozen under `.media/images/`, each with its origin written to `.media/manifest.jsonl`; the command
  prints an `<img>` snippet to paste. Running it again reuses the file unless the design changed. Pick SVG for logos
  and vectors (they scale and animate path by path) and PNG at 2x for raster art. `--entity` tags a brand mark so it
  can be found again later.
- **Components** land in `compositions/components/<name>/` as HTML at Figma's geometry. A fill bound to a token you
  already imported is written as `var(--brand-slug, #0066FF)`, so one variable re-brands every component. A fill
  bound to a token not yet imported stays a literal with `data-figma-unresolved`: import that library's tokens, then
  import the component again.
- **Shapes that have no clean HTML form** (vector networks, boolean shapes) are rasterised for you.
- **Team-library variables** live in the library's own file. Ask once which file that is; never guess a match by hex.
- **Batch size:** keep to about 4 large frames per call; beyond about 12 node ids Figma's image export times out.

Check every hero component against Figma's own render of the same node (`figma asset <node> --format png`). When the
two differ and you cannot fix it, report the drift rather than hand-editing the import; text metrics are the usual
cause.

## Figma storyboards: frames are states, not slides

A storyboard section in Figma describes how elements change over time. When the same element appears in two frames,
the film moves that element from its first state to its second. Showing the frames one after another as stills is
the mistake to avoid.

How to read the section:

- **Scenes.** Every node the size of a frame counts as a scene, whatever its type or name. Order scenes by their x
  position, left to right.
- **Pairing.** For each pair of neighbouring scenes, pair children by name; for the rest, pair by similar size and
  position. Paired children tween their geometry; where the pixels themselves changed, crossfade two exports on the
  same spot. Export each element once, not one still per frame.
- **Leftovers.** A child with no partner enters or leaves on its scene's beat.
- **Notes.** Text placed under the strip describes motion for the scene above it and never appears in the film.
- **Product screens.** Scenes that show one interface in successive states become live DOM: code the parts that
  change, freeze the rest, and play each change as an interaction (cursor travels, clicks, the screen answers) rather
  than as a tween.
- **Fallback.** Only scenes that share no element with their neighbours are shown as stills.

## Product screens rebuilt as live UI

A product screen in a film is rebuilt only as far as the beat needs it: the field that receives text, the button
that changes state, the list that fills up. Keep the real labels, values and layout from the design, and freeze
everything else as an image underneath. After zooming, no text is smaller than 26 px at 1080p, and product interfaces
are never tilted into 3D. Mockup techniques are in `motion-assets`.

## Motion and shaders from Figma

Figma motion and shader fills are out of reach of the REST token. A Figma Motion timeline can be read through a
compatible Figma connector and converted (with the helpers in `@hyperframes/core/figma`) into a GSAP timeline that is paused,
finite and registered on `window.__timelines`. Named eases outside the supported set become linear; tell the person
which. When a track will not convert, and for every shader fill (the export flattens shaders to their base colour),
have the person export that frame natively from Figma, PNG or MP4, and add the file as an asset or a `<video class="clip">`.
Compare a converted motion with Figma's own export frame by frame before calling it faithful.

## Drafts from design tools

A draft from Claude Design, Open Design or a similar tool fixes layout, palette, type and scene direction, but it is
not yet a film. Ask the tool for a working HyperFrames project rather than separate mockups, save it, and continue as
with any existing project: `npx hyperframes timeline --json` to read it, `npx hyperframes lint` and
`npx hyperframes check --json` to gate it, remote fonts and media replaced by files under `assets/`, and the preview
watched in motion, since stills hide timing. A usable handoff has a clear direction, real assets or clearly labelled
placeholders, editable source for anything that may change, local fonts and media, and a project that opens.

## Verify the import

```bash
npx hyperframes lint && npx hyperframes check --json                     # both clean
grep -rn 'figma.com' --include='*.html' . | grep -v '^./.media/'         # expect nothing in compositions
grep -rln 'data-figma-unresolved' compositions/ || echo "all tokens resolved"
```

Then watch the preview in motion; stills cannot show whether storyboard states animate into each other.

## Gotchas

- **Symptom:** the film plays like a slide deck of the Figma frames. **Cause:** storyboard frames were shown as
  stills. **Fix:** pair elements across frames and animate between their states.
- **Symptom:** changing the brand colour leaves components unchanged. **Cause:** components were imported before the
  tokens, so their fills are literals. **Fix:** run `figma tokens`, then import the components again.
- **Symptom:** `figma tokens` returns 403 on a Professional plan. **Cause:** the token lacks the Library content
  scope the styles fallback needs. **Fix:** add the scope.
- **Symptom:** imported text wraps at a different width from Figma. **Cause:** different font metrics. **Fix:** load
  the same font files with `@font-face`.
- **Symptom:** a batch export times out. **Cause:** too many large frames in one call. **Fix:** send about 4 at a time.

## Anti-patterns

| Do not | Do instead |
|---|---|
| importing components before tokens | `figma tokens` first, so fills link to variables |
| hand-editing an import to hide drift | report the drift, usually text metrics |
| matching a library variable by hex | ask which file holds the team library |
| tilting a product interface into 3D | keep it flat, and keep text at 26 px or more after zooming |

## Checklist

- [ ] Every piece sorted into image or HTML by whether anything inside it changes.
- [ ] Tokens imported before components; any remaining `data-figma-unresolved` has a stated reason.
- [ ] Storyboard frames animate between states; stills only for scenes that share nothing.
- [ ] No Figma URL, token or remote asset in the compositions; everything under `assets/` or `.media/`.
- [ ] Hero components compared with Figma's render; drift reported.
- [ ] `lint` and `check --json` clean; the film watched in motion.

## See also

`video-design-system`, `motion-assets`, `video-fonts`, `website-to-hyperframes`, `hyperframes`.
