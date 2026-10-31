---
title: Video types and their story shapes
author: MOZGII, Inc.
lang: en
---

# Video types and their story shapes

Each kind of short film has a usual length, a beat shape, devices that suit it and tells that give away a generated
one. Choose the type from the request, then fit its shape to the chosen storyline. Every type below uses the same
card: length, shape, what makes it work, tells.

## Lengths at a glance

These ranges are starting points; the story decides the final length.

| Type | Length | Beats |
|---|---|---|
| Social ad or hook clip | 6 to 15 s | 3 to 4 |
| Launch or feature film | 20 to 45 s | 5 to 7 |
| Changelog video | 15 to 40 s | 4 to 6 |
| Data story | 20 to 45 s | 4 to 6 |
| Explainer | 30 to 90 s | 5 to 9 |
| Tutorial | 30 to 120 s | one per step plus 2 |
| Music video | the track | one per section |

## Launch, promo and feature films

**Length and shape.** 20 to 45 s, in seven beats: the hook, tension, the reveal, proof, the payoff, the claim and the end card.

**What makes it work.** People pass on a launch film because of a real result, so anything presented as the product
must actually be the product.

- Interface sources, in order of preference: the person's own recording or screenshots; design frames rebuilt as
  states of a single app; walking through the flow yourself; a capture of the feature page; the product docs for the
  labels in use today. A screen you cannot get becomes a labelled placeholder, and the reply says so. A single made-up
  button costs the trust of every viewer who knows the product.
- Locate, enlarge, put back: show enough of the real interface for the viewer to place the task, lift the one panel
  or field forward at 1.6 to 2x (text at least 26 px at 1080p), let it do its job, then return it to its place so the
  viewer knows where the result lives. Panning across a still screenshot shows the product doing nothing.
- The cursor is the cause. Make it large (4 to 7% of the frame), bring it in from outside the frame, and let each
  click trigger the next change on that same frame.
- The end card is animated, not pasted: the mark arrives in the final 5 to 10% of the film, the lockup takes 15 to 30%
  of the frame width, it is carried or wiped in, and the call to action stays 1.5 to 3 s.

**Tells.** An opener of typing into an empty prompt box; three feature cards; a title over a darkened screenshot; a
dashboard nobody built; a logo parked in a corner.

## Explainers and how-it-works films

**Length and shape.** 30 to 90 s, built around one concrete example followed from its start to its end; a tour of
facts is not an explainer.

**Ground it first.** The opening belongs to the viewer's world: a person, a place, a question they would actually
ask. The abstract part (a diagram, a model) appears inside that situation as its answer, and the closing comes back
to the same person.

**What makes it work.**

- Devices: a machine whose operation is the idea, which the camera travels through; a single diagram that gains one
  part per beat, each part appearing as it is named; a chain of transformations, each step morphing from the last; a
  worked example where one real input passes through every step.
- Information shapes: a single number arriving, a myth crossed out, before and after, many items gathering into
  groups, ordered steps, one item picked from many. Choose the shape before the picture, so lines that sound alike
  still look different.
- Words: with narration, reveal each part on the word that names it and keep a scene to around 19 spoken words.
  Without narration, use large lines of up to about 10 words, each held for 0.5 s plus 0.3 s per word, and put labels on the
  things they name.

**Tells.** Bullet slides, icons inside circles, the full diagram shown at once, a voice reading out the screen.

## Data stories and number films

**Length and shape.** 20 to 45 s, one number per beat. Each number is set up by the scene before it, then turned
into something physical: a total that rises as a skyline, a percentage that becomes a crowd of people.

**What makes it work.**

- The number is the largest element in the frame and uses tabular figures, which stop a count-up from wobbling. A
  count-up lasts 1.2 to 1.6 s and then holds.
- Charts build in the order people read them: frame and axis, a reference line, the data drawing on, then a
  single annotation where the point is. One series in colour, the others grey, and no legend.
- Only real data, rounded the same way throughout, with a small line naming the source. A single data module feeds
  every figure in the film.

**Tells.** Dashboards, pie charts, KPI cards in a grid, every number counting up together, figures without a source.

## Music videos and other films edited to a song

**Length and shape.** The length of the track. The song's sections become chapters, and its energy sets how often
the picture cuts.

**What makes it work.**

- Map the song before planning shots: `npx hyperframes audio <track> --only sections,onsets,moments --json` returns
  the intro, verses, choruses, bridge and outro.
- Verses get longer shots, the chorus gets a new picture on each strong beat, and a breakdown holds one image. Each
  chorus comes back to a home stage and goes bigger than the last; the final shot echoes the first.
- Every lyric phrase gets a picture of its meaning lasting 1.4 to 4 s. Lyrics appear on screen only on request, set
  as type and held for at least one beat.
- A physical look (watercolour, cut paper, risograph, film grain) carries a music film further than effects do.

**Tells.** A spectrum analyser as the main image, any one treatment lasting past about 6 s, a cut on every single beat.

## Character shorts and mascot films

**Length and shape.** Usually 15 to 45 s. The character gives each transition a reason and the film its humour: it
hauls the result into frame, throws away its first attempt, consults the manual.

**What makes it work.**

- A change of mood passes through a take: anticipation, squash, the new expression, a settle. Expressions never jump
  straight from one to the next.
- Parts move at different times and by different amounts (the head leads, the arms follow). Code that moves every part
  together on a single curve reads as a machine. Contact makes it believable: feet planted, props held, eyes on their
  target.
- One action per read: steer the eye, play the action quickly, then hold on the reaction. A caption describing the
  action adds nothing.
- Treat the rig as parameters that change over time, so write moods as keyed states the rig eases between. A hand-drawn boil
  redraws its outlines roughly 12 times per second, with jitter seeded from `Math.floor(t * 12)`, which keeps every render
  identical.
- A blink or idle breath gives a character life; the same breathing loop on a title is a tell.

## Vertical social clips

**Length and shape.** 6 to 30 s at 1080×1920 for a phone feed, recomposed from landscape and never squashed.

**What makes it work.**

- Frame 0 doubles as thumbnail and hook, so it already shows a face, the result or a single bold line.
- Viewers decide in about a second, so the change or the question lands in the first beat. Many watch without sound:
  caption the speech and let the picture carry the hook.
- One centred subject, stacked vertically; type about 1.35x its landscape size; a word cap per line (around 5 English
  words for a claim). Drop words; never make the type smaller.
- Shots of 1 to 2 s, a new beat every 2 to 4 s, and the payoff before the viewer swipes away. Safe zones for each app
  are in `platform-formats`.

**Tells.** A landscape frame letterboxed into the middle, small type, a slow opening.

## 3D, simulation and generative pieces

**Length and shape.** 15 to 60 s, worth the effort when an object, a set or a working model is the payoff.

**What makes it work.**

- A single hero object beats a crowd of them. Fly into it rather than circling it; cutaways, exploded views and labels
  carrying real figures make a simulation explain something.
- Run the simulation once at load and store the results in arrays, then read the state for time `t`; any frame can
  then render by itself. Seed every random number.
- Real product interfaces stay flat; only generated content may tilt in 3D.
- Lighting: warm key, cool rim, dark environment. Rotate the environment so highlights travel across the object.

**Tells.** A slow orbit around a floating object with nothing to learn from it.

## Tutorials and walkthroughs

**Length and shape.** 30 to 120 s: the outcome first, the steps with holds, a recap at the end.

**What makes it work.**

- The finished result appears in the opening seconds, so viewers know where the steps are heading.
- One step per beat, named by a short title; the frame zooms to the control the step uses and holds while it works.
- The software's real labels stay as they are; the recap card lists the steps in the viewer's own words.

**Tells.** Steps that flash by without a hold, invented menu names.

## Changelog and pull-request videos

**Length and shape.** 15 to 40 s, stating what changed and why it matters.

**What makes it work.** Take the headline change rather than the full list, then follow one user through one task
the change improves: the old way failing, the new way working, the version number and where to get it. Every claim
comes from the pull request, the release notes or the docs.

**Tells.** A scrolling list of every change, version numbers with no story.
