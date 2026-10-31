---
name: video-thumbnails
description: Designs and exports video thumbnails, posters and covers with HyperFrames - YouTube and Shorts thumbnail sizes and limits, Reels and feed covers and their grid crops, web player posters, frame 0 as the thumbnail, a still composition exported as a 4K PNG or a small JPG, variants compared side by side, and the design rules that make a thumbnail readable at phone size (one subject, a few words, contrast, safe corners, honest promise). Use when someone asks for a thumbnail, cover image, poster frame or preview image for a video, or wants the first frame of a video to work as its thumbnail.
metadata:
  tags:
  - thumbnail
  - poster
  - cover
  - youtube
  - shorts
  - reels
  - still-image
  - hyperframes
---

# Video thumbnails, posters and covers

A video thumbnail is the still image a platform shows before anyone presses play; a poster is the same thing for a
web player; a cover is the frame a feed or profile grid shows. HyperFrames builds them like any composition (HTML,
the brand's fonts and colours, the film's own assets) and exports them as images, so a thumbnail matches its video
exactly and can be versioned with variables. Checked against CLI 0.8.223; platform limits checked October 2026.

## When to use this skill

Use this skill when someone asks for a thumbnail, cover, poster or preview image, wants variants to test, or wants
the first frame of a video to work as its thumbnail on platforms that use it.

## Step 0: read the CLI and the canvas

```bash
npx hyperframes --version
grep -hoE 'data-(width|height)="[0-9]+"' index.html | sort -u    # the film's canvas
ls assets/fonts 2>/dev/null                                       # the brand fonts the still will use
```

Build the still in the film's own project, so it shares fonts, colours and assets.

## Sizes and limits per platform

Sizes and limits per platform change; verify on each platform's help page before a launch.

| Where | Size to make | Notes |
|---|---|---|
| YouTube video thumbnail | 3840×2160 recommended (16:9), minimum width 640 | JPG or PNG; up to 50 MB from a computer, 2 MB from the mobile app |
| YouTube Shorts thumbnail | 2160×3840 recommended (9:16), minimum height 640 | custom Shorts thumbnails only from YouTube Studio on a computer, verified accounts |
| Instagram Reels cover | 1080×1920 | third-party guides report a centred 3:4 crop on the profile grid (not confirmed on Instagram's own pages): keep the subject and words inside the middle 1080×1440 |
| Feeds that show the first frame (many autoplay feeds) | the video's own size | frame 0 is the thumbnail: design it |
| Web page player poster | the video's aspect, at its display size times 2 | `poster="..."` on `<video>` or `<hyperframes-player>`; a compressed JPG or WebP |

Keep a 1280×720 JPG under 2 MB as well: it uploads from any device and suits link previews.

## Frame 0 as the thumbnail

Frame 0 as the thumbnail means the video's first frame already shows the subject and the hook: never black, never a
logo alone, never an empty background waiting for an entrance. Start motion 0.1 to 0.3 s in from a frame that
already reads. `npx hyperframes check` warns with `first_frame_empty` when frame 0 paints nothing but background.

## Build a thumbnail as a still composition

A still composition is a composition with no timeline: its root carries `data-no-timeline`, so nothing waits for a
GSAP registration. Build it in the same project as the video so it shares fonts, colours and assets.

```html
<!doctype html>
<html>
  <head><style>
    @font-face { font-family: "Brand"; src: url("assets/fonts/Brand-Black.woff2") format("woff2"); font-weight: 900; }
    #thumb { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0d1117; }
    #thumb img.subject { position: absolute; right: 0; bottom: 0; height: 100%; }
    #thumb h1 { position: absolute; left: 96px; top: 140px; width: 980px; margin: 0;
      font: 900 190px/0.92 "Brand", sans-serif; color: #fff; text-transform: uppercase;
      text-shadow: 0 10px 40px rgba(0,0,0,.6); }
    #thumb h1 em { font-style: normal; color: #ffd60a; }
  </style></head>
  <body>
    <div id="thumb" data-composition-id="thumb" data-width="1920" data-height="1080" data-duration="1" data-no-timeline>
      <img class="subject" src="assets/presenter-cutout.png" alt="">
      <h1 data-var-text="headline">Render <em>10x</em> faster</h1>
    </div>
  </body>
</html>
```

Author at 1920×1080 (or 1080×1920 for vertical) and export larger: the layout stays the same and vector text
stays sharp. A cutout of the person or object (`npx hyperframes remove-background portrait.jpg -o
assets/presenter-cutout.png`) lets the words sit beside or behind the subject.

## Export the image

Exporting the image uses `snapshot` at time 0. `--zoom` with an exact region and `--zoom-scale` raises the pixel
density without changing the layout, so a 1920×1080 composition exports at 3840×2160.

```bash
npx hyperframes snapshot thumbs/youtube --at 0 --no-end --zoom "0,0,1920,1080" --zoom-scale 2 -o exports/yt
ffmpeg -y -i exports/yt/<file>.png -vf scale=1280:-1 -q:v 3 exports/yt-1280.jpg     # small upload copy
ffprobe -v error -show_entries stream=width,height -of csv=p=0 exports/yt-1280.jpg
```

Read the PNG the command wrote (its path is printed) before converting. For per-customer or per-episode thumbnails,
declare the headline as a variable and render the still once per row, as with any template.

## Design rules that read at phone size

Design rules for thumbnails come from how they are seen: about 160 to 360 px wide, next to a title, among dozens of
others.

1. **One subject, large.** A face with a clear expression, or one object, filling 40 to 60% of the frame.
2. **Three to five words at most**, and not the title repeated: the thumbnail and the title make one promise
   together. Type is huge and heavy (cap height 15 to 25% of the frame height), one accent word in the brand colour.
3. **Contrast first.** Light on dark or dark on light, an outline or soft shadow on words over photos; check it at
   the size people see it.
4. **Keep the bottom-right corner clear**: players draw the duration badge there. Keep words off the extreme edges.
5. **The promise is true.** The frame shows something the video delivers; misleading thumbnails cost trust and can
   break platform policy.
6. **A series looks like a series**: the same type, layout and colour logic each episode, so regular viewers spot it.

Test at real size before handing over:

```bash
ffmpeg -y -i exports/yt-1280.jpg -vf scale=240:-1 exports/yt-small.png    # look at this file: can you read it?
```

## Variants to compare

Variants to compare put two to four thumbnail versions on one labelled sheet, so the person picks with the options
side by side. Make each variant its own small project folder (or render one template with different variables),
then:

```bash
npx hyperframes compare thumbs/a thumbs/b thumbs/c --labels "Face,Result,Number" --at 0 --out exports/variants.png
```

Change one thing per variant (the subject, the words, or the colour), so the result says which change mattered.
YouTube Studio's Test and Compare can then run the chosen two or three against real viewers.

## Verify the export

```bash
ffprobe -v error -show_entries stream=width,height -of csv=p=0 exports/yt-1280.jpg   # 1280,720
ls -l exports/yt-1280.jpg                                                            # under 2 MB
npx hyperframes check --json | grep -c first_frame_empty                             # expect 0
```

Then open the 240 px copy from the design rules and read it at that size.

## Checklist

- [ ] Size and format match the platform table; a small JPG copy exists for mobile upload.
- [ ] One large subject; three to five words that add to the title rather than repeat it.
- [ ] Readable at 240 px wide; the bottom-right corner clear.
- [ ] Fonts loaded from `assets/fonts/`, so the export uses the brand font, not a fallback.
- [ ] Vertical covers keep the subject and words inside the 3:4 grid crop.
- [ ] The video's frame 0 also reads as a thumbnail.

## Gotchas

- **Symptom:** A blurry upscale. **Cause:** The image was resized up after export. **Fix:** export at the target
  density with `--zoom-scale`.
- **Symptom:** A fallback font in the export. **Cause:** A family that is neither bundled nor declared with
  `@font-face` to `assets/fonts/`. **Fix:** add the rule and the file.
- **Symptom:** Text is hidden on the profile grid. **Cause:** The words sat near the top or bottom of a 9:16 cover.
  **Fix:** keep them inside the middle 1080×1440.
- **Symptom:** The mobile upload is rejected. **Cause:** A 4K PNG over 2 MB. **Fix:** upload the 1280-wide JPG.
- **Symptom:** An empty first frame. **Cause:** An entrance starts from opacity 0 at frame 0. **Fix:** start from a
  visible state.

## Anti-patterns

| Do not | Do instead |
|---|---|
| the title repeated on the thumbnail | three to five words that add to it |
| several subjects | one subject, filling 40 to 60% of the frame |
| text in the bottom-right corner | keep it clear for the duration badge |
| a promise the video does not keep | show something it delivers |

## See also

`video-design-system`, `platform-formats`, `video-fonts`, `hyperframes-media`, `hyperframes`.
