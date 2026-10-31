---
name: video-fonts
description: Gets fonts right in rendered video - the families HyperFrames bundles, @font-face rules to woff2 files in assets/fonts, subsetting and converting fonts with fontTools, variable font axes as animation, CJK, Arabic and emoji coverage, waiting for fonts before measuring or splitting text, OpenType features for numbers, font licences for video, and finding a fresh pairing in the Google Fonts catalogue. Use when a video needs a brand or custom font, when text renders in the wrong font or with fake bold, when non-Latin text shows boxes, or when choosing typefaces.
metadata:
  tags:
  - fonts
  - typography
  - font-face
  - woff2
  - variable-fonts
  - cjk
  - licensing
  - hyperframes
---

# Fonts for video

Fonts for video must be present on the render machine at the moment each frame is captured, in exactly the weights
and scripts the text uses. A font that loads late shifts line breaks; a missing weight renders as synthetic bold; a
missing script renders as boxes. This skill makes the font set explicit. Checked against HyperFrames CLI 0.8.223.

## When to use this skill

Use this skill when a video needs a brand or custom font, when text renders in the wrong face, a fake bold or a
fallback, when Chinese, Japanese, Arabic or emoji characters show boxes, or when choosing a type pairing.

## Step 0: read the font tools and their floor

```bash
python3 --version                                                     # 3.11 or later
python3 -c 'import fontTools; print(fontTools.version)'               # 4.68 or later
python3 -c 'import brotli; print(brotli.__version__)'                 # 1.2.1 or later
npx hyperframes --version                                             # the bundled families ship with it
```

An older result: upgrade before touching a font file (`python3 -m pip install -U "fonttools[woff]>=4.68"`).

## How HyperFrames resolves fonts

HyperFrames resolves fonts in three ways.

| Source | How | Notes |
|---|---|---|
| Bundled families | write the family name in CSS | Archivo Black, EB Garamond, IBM Plex Mono, Inter, JetBrains Mono, Lato, League Gothic, Montserrat, Noto Sans JP, Nunito, Open Sans, Oswald, Outfit, Playfair Display, Poppins, Roboto, Source Code Pro, Space Mono |
| Project files | `@font-face` with `src: url("assets/fonts/x.woff2")` | any family, any script; the reliable path for brands |
| Installed fonts | `@font-face` with `src: local("Exact Full Name")` | only on machines that have the font: avoid for shared or cloud renders |

Each bundled family ships Latin glyphs in a handful of weights (for Inter: 400, 700 and 900). For other weights and scripts
of those families the compiler fetches Google Fonts and caches them in `~/.cache/hyperframes/fonts`. Common system
families (Helvetica, Arial, Times, Menlo) are swapped for the nearest bundled family. Any other family without
`@font-face` fails lint (`font_family_without_font_face`).

## Declaring a brand font

Declaring a brand font takes one `@font-face` per weight and style actually used, in the file that uses it.

```html
<style>
  @font-face { font-family: "Brand Sans"; src: url("assets/fonts/BrandSans-Regular.woff2") format("woff2");
               font-weight: 400; font-style: normal; font-display: block; }
  @font-face { font-family: "Brand Sans"; src: url("assets/fonts/BrandSans-Black.woff2") format("woff2");
               font-weight: 900; font-style: normal; font-display: block; }
  @font-face { font-family: "Brand Sans"; src: url("assets/fonts/BrandSans-Italic.woff2") format("woff2");
               font-weight: 400; font-style: italic; font-display: block; }
  h1 { font-family: "Brand Sans", "Inter", sans-serif; font-weight: 900; }
</style>
```

- Use only the weights the font ships. Asking for 600 from a family with 400 and 700 renders a synthetic bold.
- Name files by family, weight and style so an upright and an italic "Regular" never collide.
- In scene files, the `@font-face` rule goes inside the `<template>` with the scene's other styles.
- A variable font needs one rule with a weight range: `font-weight: 100 900;`.

## Converting and subsetting fonts

Converting and subsetting fonts makes them small and safe to ship. fontTools does both, and its floor is a security
one: use 4.68 or later. Version 4.63 predates the SECURITY fixes in 4.64 (paths outside the filesystem root, glyph
names used as filenames, external XML entities), and 4.68 requires `brotli` 1.2.1 or later, which fixes the critical
out-of-bounds write in the Brotli decoder, GHSA-9v8h-qqgm-4m35. WOFF2 is Brotli inside, so a font from a stranger is
exactly the input that bug needs. fontTools has needed Python 3.11 since 4.66.

```bash
python3 -m pip install "fonttools[woff]>=4.68"
pyftsubset BrandSans-Black.otf --output-file=assets/fonts/BrandSans-Black.woff2 --flavor=woff2 \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201E,U+2022,U+2026,U+20AC" \
  --layout-features="kern,liga,tnum,lnum,case"
pyftsubset BrandSans-Black.otf --output-file=assets/fonts/BrandSans-Black-sub.woff2 --flavor=woff2 \
  --text-file=all-copy.txt --layout-features="*"     # only the characters the video uses
```

Since 4.66 `pyftsubset` keeps the input's flavor when `--flavor` is left out, so a WOFF2 stays WOFF2 and
`--flavor=none` forces plain TTF or OTF; write `--flavor=woff2` as above to get the same output from any input.

Subsetting to the video's own text is safe because the copy is fixed at render time; re-run it when copy or variables
change. [scripts/subset_fonts.sh](scripts/subset_fonts.sh) subsets every font in a folder to the text of a project.

When a script from `scripts/` is not on disk (a pack install), read that script from the library that served this page and save it first.

## Waiting for fonts before measuring

Waiting for fonts before measuring keeps layout stable: text measured or split before its font loads is measured in
the fallback face. Measure, split or fit text inside `document.fonts.ready`, and register the timeline at the end:

```js
const tl = gsap.timeline({ paused: true });
document.fonts.ready.then(() => {
  const { fontSize } = window.__hyperframes.fitTextFontSize(title.textContent,
    { fontFamily: "Brand Sans", fontWeight: 900, maxWidth: 1600 });
  title.style.fontSize = fontSize + "px";
  tl.fromTo(title, { opacity: 0 }, { opacity: 1, duration: 0.3 }, 0.3);
  window.__timelines["intro"] = tl;
});
```

## Variable font axes as motion

Variable font axes as motion animate weight, width or optical size smoothly, which no static font can do.

```js
tl.fromTo("#word", { fontVariationSettings: '"wght" 200, "wdth" 75' },
  { fontVariationSettings: '"wght" 900, "wdth" 125', duration: 0.6, ease: "expo.out" }, 1.2);
```

Check the axes a font has (`fc-query font.ttf`, or the Google Fonts axis list). Animating weight changes text width;
fix the container width or animate width (`wdth`) against it.

## Non-Latin scripts and emoji

Non-Latin scripts and emoji need their own font files.

- Chinese, Japanese and Korean: a Noto Sans or Serif CJK family for the language (Noto Sans JP is bundled for
  Japanese; add SC, TC or KR files for the others). Subset them: full CJK fonts are 5 to 20 MB.
- Arabic and Hebrew: a font with the script, `dir="rtl"` on the text, and check that GSAP splitting by character does
  not break Arabic joining (split by word instead).
- Thai, Devanagari and other complex scripts: split by word or grapheme cluster, never by code point.
- Emoji: the render machine's emoji font decides the look and may be missing on Linux. Ship a colour emoji font
  (Noto Color Emoji, OFL) or use SVG icons; emoji as stand-ins for icons look generated.

## OpenType features for numbers and code

OpenType features for numbers and code are often off by default:

```css
.stat, .timer, .table td { font-variant-numeric: tabular-nums; }   /* digits align and do not jitter */
.fraction { font-variant-numeric: diagonal-fractions; }
.unit { font-variant-caps: all-small-caps; }
code { font-variant-ligatures: none; }
```

Keep these features when subsetting (`--layout-features="tnum,frac,smcp,liga"` or `*`).

## Font licences for video

Font licences for video decide what you may ship. SIL Open Font License fonts (most of Google Fonts, Noto, Inter,
JetBrains Mono, Geist) allow embedding, subsetting and use in videos; keep the licence file next to the fonts in
`assets/fonts/`. A commercial desktop licence usually covers rendering text into video, but publishing the font files
with a project (a public repo, a published HyperFrames project, a template) normally needs a web or app licence:
check the foundry's terms before committing font files.

## Finding a pairing

Finding a pairing starts from the voice of the content (institutional, technical, loud, editorial, warm,
speculative), not the category. Registers with suggested open-licence families:
[references/font-pairings.md](references/font-pairings.md). To look beyond the familiar choices,
`python3 scripts/find_fonts.py` lists recent, popular Google Fonts families by category from the public metadata.

## Verify the fonts

```bash
npx hyperframes check --json | grep -c font_family_without_font_face   # expect 0
head -c 4 assets/fonts/BrandSans-Black.woff2; echo                     # prints wOF2
bash scripts/subset_fonts.sh . assets/fonts-src /tmp/fonts-sub         # every font subsets without an error
npx hyperframes snapshot --at 1,4                                      # the brand face, no boxes, no fake bold
```

Zoom into a snapshot on the heaviest weight: synthetic bold shows as smeared stems.

## Checklist

- [ ] Every family is bundled or has `@font-face` to a file in `assets/fonts/`.
- [ ] Only shipped weights and styles are used; one rule per weight and style.
- [ ] Fonts subset to the needed characters, features kept.
- [ ] Text measured, fitted or split after `document.fonts.ready`.
- [ ] Non-Latin and emoji characters have fonts on every render machine.
- [ ] Licence files kept next to the fonts; publishing rights checked.

## Gotchas

- **Symptom:** Fake bold. **Cause:** A weight the font does not ship. **Fix:** use a shipped weight or a variable
  font.
- **Symptom:** Line breaks differ in the render. **Cause:** Text was measured in the fallback face before the font
  loaded. **Fix:** measure inside `document.fonts.ready`.
- **Symptom:** Boxes instead of characters. **Cause:** The subset dropped them, or the script has no font. **Fix:**
  re-subset with the full text.
- **Symptom:** It works locally and looks wrong in the cloud. **Cause:** The font came from `local()` or the system.
  **Fix:** ship the file.
- **Symptom:** Captured site fonts lose characters. **Cause:** Font files were copied without their `unicode-range`
  rules. **Fix:** copy the rules too.
- **Symptom:** `pyftsubset` fails after an upgrade on an old Python. **Cause:** fontTools needs Python 3.11 from 4.66.
  **Fix:** move to Python 3.11 or later rather than pinning below the security floor.

## Anti-patterns

| Do not | Do instead |
|---|---|
| `pip install fonttools` with no floor | `"fonttools[woff]>=4.68"` |
| `src: local(...)` for shared or cloud renders | a file in `assets/fonts/` |
| splitting Arabic or Thai by character | split by word or grapheme cluster |
| emoji as stand-ins for icons | SVG icons, or a shipped colour emoji font |
| publishing a commercial font's files | check the foundry's terms first |

## References

- [references/font-pairings.md](references/font-pairings.md): registers, open-licence families and pairing recipes.
- `scripts/subset_fonts.sh`: subset every font in a folder to the text used by a project.
- `scripts/find_fonts.py`: list Google Fonts families by category, recency and popularity.

## See also

`video-design-system`, `hyperframes`, `website-to-hyperframes`.
