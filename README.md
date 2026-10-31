# HyperFrames skills

A library of 35 Claude skills for making video with [HyperFrames](https://github.com/heygen-com/hyperframes), the
open-source framework that turns HTML into MP4 by stepping a paused timeline to each frame's time, and with the web animation
stack it drives: GSAP, anime.js, Lottie, Three.js, WebGPU, CSS and the Web Animations API. The skills cover the whole
job: planning the story, the composition contract, the CLI, motion and design craft, footage, captions and sound,
rendering, embedding and automation, platform formats, thumbnails, testing and performance.

Every skill is a folder under `docs/v0.8/<group>/<name>/` with a `SKILL.md` and, where useful, `references/*.md` (opened
only when a task needs the detail) and `scripts/`. Each skill stands alone: it works without any other skill from
this library being installed; mentions of other skills are pointers, not requirements. The `SKILL.md` front matter
uses only the portable keys (`name`, `description`, `metadata`), so the same folder works in Claude Code, claude.ai
and the Skills API.

Facts were checked against the versions current at release (October 2026): `hyperframes` CLI and the
`@hyperframes/*` packages 0.8.223, GSAP 3.15.0, anime.js 4.5.0, lottie-web 5.13.0, @lottiefiles/dotlottie-web
0.82.0, three 0.187.0, typegpu 0.12.9, Tailwind CSS 4.3.3 (HyperFrames pins the browser runtime at 4.2.4), Remotion
4.0.539, fontTools 4.68 (the security floor), FFmpeg 7 to 9.

- `library.json`: name `hyperframes`, title, version and the self-test minimum
- `questions.json`: the self-test; each question names a phrase its answering file holds
- `sources.json`: every source read as context, with the commit read, its licence and the files it informed
- `versions.json`: every package the skills name, the version they were checked against and the date it was read
  from its registry
- `.gitignore`: `dist/` (built packs) and `.DS_Store`

## Use these skills

Use a skill by giving Claude its folder; take one skill or all of them.

- **Claude Code, for you:** copy a folder such as `docs/v0.8/animation/gsap/` to `~/.claude/skills/gsap/`.
- **Claude Code, for one project:** copy it to `.claude/skills/gsap/` in that project and commit it.
- **claude.ai and Claude Desktop:** zip the folder so the zip holds one folder named like the skill with `SKILL.md`
  inside (`gsap.zip` containing `gsap/SKILL.md`), then upload it under Settings, Capabilities, Skills.
- **The Skills API:** upload the same folder as a custom skill.

Claude reads each skill's `description` and loads the skill when a request matches it, so there is nothing to
invoke by hand; in Claude Code you can also type `/gsap`. Scripts run with the tools named at the top of each script
(Python 3.10 or later, and 3.11 or later for `subset_fonts.sh`, whose fontTools floor needs it; FFmpeg; Node.js 22 or
later for the HyperFrames CLI).

## Skills

### HyperFrames core

- `hyperframes`: the composition contract: clips, timing attributes, scenes, variables, media, frame sources, fonts, determinism, the work loop.
- `hyperframes-cli`: every CLI job: init, capture, lint, check, snapshot, timeline edits, preview, render, troubleshooting.
- `hyperframes-registry`: finding, installing and wiring the ~450 ready-made blocks and components.
- `hyperframes-media`: TTS, transcripts, background removal, loudness, beats, grades and looks, sourcing music, sounds and logos.
- `hyperframes-captions`: captions, karaoke and kinetic subtitles from word timings, plus SRT and WebVTT delivery.
- `hyperframes-transitions`: choosing and building CSS and WebGL shader transitions by energy, mood and position.
- `hyperframes-slideshow`: live presentations with slides, fragments, hotspots and presenter notes.
- `hyperframes-player`: embedding compositions in web pages and apps with the player web component, its API and live data.
- `hyperframes-automation`: rendering from code and at scale: the Node render API, cloud, AWS Lambda, Cloud Run, templates, the SDK.
- `website-to-hyperframes`: a URL to a finished video: capture, brand notes, script, storyboard, voiceover, build.
- `design-to-hyperframes`: Figma and design-tool handoffs: assets, brand tokens, editable components, storyboards as motion.
- `remotion-to-hyperframes`: porting Remotion and other animation code, with a blocker scan and SSIM comparison.

### Animation runtimes

- `gsap`: GSAP timelines for seek-rendered video: fromTo, eases, staggers, finite repeats, plugins.
- `animejs`: anime.js v4 in HyperFrames, and porting v3 code.
- `lottie`: lottie-web and dotLottie players that seek frame-accurately.
- `threejs`: deterministic Three.js scenes, GLTF animation and seeded particles.
- `css-animations`: CSS keyframes and the Web Animations API (`element.animate`) that seek correctly.
- `tailwind`: Tailwind CSS v4 in compositions: browser runtime, @theme, static classes, compiling.
- `webgpu`: WebGPU and TypeGPU layers drawn from seek time, with GPU completion barriers.
- `data-in-motion`: numbers, SVG charts, D3 and maps built for viewers who cannot pause.

### Planning, craft and design

- `video-storyboard`: the one idea, three storylines, hooks, beats per video type, STORYBOARD.md and a stills board.
- `motion-design`: eases by role, timing, holds, springs, beat grids, cuts, rhythm and motion feedback fixes.
- `video-design-system`: design.md, palettes and tokens, type, named styles, textures and brand checks.
- `video-fonts`: bundled fonts, @font-face, subsetting, variable axes, non-Latin scripts and font licences.
- `vfx`: custom effects: WebGL shaders, SVG filters, canvas, compositing, text marks, and built-in motion blur and looks.
- `motion-assets`: reusable motion graphics: UI mockups, characters, 3D objects, icon systems, backgrounds.
- `video-copywriting`: narration scripts, on-screen copy limits, spoken forms for TTS, plain language.
- `video-thumbnails`: thumbnails, posters and covers: platform sizes, still compositions, 4K export, variants.
- `video-review`: reviewing a film with review sheets and ranked, fixable notes.

### Footage and sound

- `talking-head-edits`: interviews and talking heads: cuts from the transcript, captions on the cut, cards, picture-in-picture.
- `audio-sync`: timing to voice and beats, audio-reactive motion, effects, ducking and loudness.

### Delivery and production

- `render-and-export`: formats, codecs, quality and bitrate, alpha, HDR, verification and FFmpeg finishing.
- `platform-formats`: canvas sizes, safe zones and lengths per platform, and adapting 16:9 to vertical.
- `render-testing`: check gates, motion assertions, visual regression, determinism and file verification in CI.
- `render-performance`: faster, stable renders: workers, GPU, heavy assets, timeouts and cloud rendering.

## Scripts

- `talking-head-edits/scripts/cut_from_transcript.py`: cuts pauses, fillers and ranges from a clip by its word transcript, click-free, and retimes the transcript.
- `remotion-to-hyperframes/scripts/lint_remotion_source.py`: scans Remotion source for patterns that block a port.
- `remotion-to-hyperframes/scripts/ssim_diff.sh` and `render-testing/scripts/ssim_diff.sh`: per-frame SSIM between two renders.
- `render-testing/scripts/verify_render.sh`: duration, streams, decoding, black frames, silence and loudness of a render.
- `render-testing/scripts/determinism_check.sh`: renders a project twice and compares frame hashes.
- `audio-sync/scripts/extract_audio_bands.py`: per-frame loudness and frequency bands for audio-reactive motion.
- `video-fonts/scripts/subset_fonts.sh`: subsets fonts to the characters a project uses.
- `video-fonts/scripts/find_fonts.py`: lists Google Fonts families by category, recency and popularity.

## Sources

Every text and script in this library is the own work of MOZGII, Inc. The sources below were read as context: they showed what
the skills should cover and which facts are true, and each fact was checked against the versions above. No wording,
example or code was copied from any of them, whatever its licence, so no third-party notice applies. The shaders and
the noise, hash and random-number functions were written for this library; gradient noise, cellular noise and domain
warping are general techniques, not anyone's code. The sources are listed as thanks and as a map for the next upgrade;
`sources.json` records the exact commit read. Licences are as each project published them when it was read.

| Source | Licence | Used for |
|---|---|---|
| [HyperFrames repository](https://github.com/heygen-com/hyperframes) (HeyGen): CLI and runtime source, docs, and the official agent skills (figma, media-use, slideshow, remotion-to-hyperframes and the hyperframes, CLI and registry skills) | Apache-2.0 | read as context for the composition contract, CLI flags, adapters, frame sources, lint rules, measured motion and caption figures, story and video-type facts, render, review and mixing facts, Figma import and transcript cut behaviour; the text and scripts are our own, facts checked against the CLI 0.8.223 source |
| [@hyperframes/player](https://github.com/heygen-com/hyperframes/tree/main/packages/player), [@hyperframes/producer](https://github.com/heygen-com/hyperframes/tree/main/packages/producer), [@hyperframes/sdk](https://github.com/heygen-com/hyperframes/tree/main/packages/sdk) | Apache-2.0 (repository) | read as context for player attributes, events and sandbox, render job options and SDK methods; checked against the 0.8.223 packages |
| [HyperFrames deploy docs](https://github.com/heygen-com/hyperframes/tree/main/docs/deploy) | Apache-2.0 (repository) | read as context for cloud, AWS Lambda and Cloud Run facts |
| [@hyperframes/shader-transitions](https://github.com/heygen-com/hyperframes/tree/main/packages/shader-transitions) | MIT | read as context for shader names and `init()` options |
| [HyperFrames docs](https://hyperframes.heygen.com) | Apache-2.0 (repository) | read to cross-check commands |
| [GSAP docs](https://gsap.com/docs/v3/) | GSAP standard no-charge licence (library); docs not openly licensed | linked; API facts verified against the 3.15.0 package |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | reviewed for scope and coverage at the commit in `sources.json`; nothing copied |
| [anime.js](https://animejs.com/documentation/) | MIT | v4 API facts, checked against the 4.5.0 bundle |
| [lottie-web](https://github.com/airbnb/lottie-web), [dotlottie-web](https://github.com/LottieFiles/dotlottie-web) | MIT | player options |
| [three.js](https://threejs.org/docs/) | MIT | renderer, loader and mixer API |
| [TypeGPU](https://docs.swmansion.com/TypeGPU/) | MIT | WebGPU toolkit facts |
| [Tailwind CSS docs](https://tailwindcss.com/docs) | MIT (code); docs linked | v4 syntax and upgrade notes |
| [MDN Web Docs](https://developer.mozilla.org/) | CC-BY-SA 2.5 | linked for WAAPI, CSS animations, `linear()` easing, custom elements, WebGPU; not copied |
| [Remotion docs](https://www.remotion.dev/docs), [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion License (source-available); skills repo has no licence file | linked; API names used for the port map; skill topics reviewed for scope at the commit in `sources.json`; nothing copied |
| [Figma REST API](https://www.figma.com/developers/api) | Figma developer terms | linked for token scopes |
| [D3](https://d3js.org), [MapLibre GL JS](https://maplibre.org) | ISC, BSD-3-Clause | linked |
| [FFmpeg documentation](https://ffmpeg.org/documentation.html) | LGPL/GPL (software); docs linked | filter and option names, tested locally with FFmpeg 9 |
| [fontTools](https://github.com/fonttools/fonttools) | MIT | `pyftsubset` usage |
| [Google Fonts](https://fonts.google.com) | families under SIL OFL 1.1 (mostly) | the font metadata endpoint and pairing suggestions |
| [Anthropic skills repository](https://github.com/anthropics/skills) | per skill (Apache-2.0 for example skills) | skill structure reference |
| [Claude Code skills docs](https://code.claude.com/docs/en/skills.md), [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Anthropic documentation | the skill standard (front matter, size, progressive loading) |
| [YouTube thumbnail help](https://support.google.com/youtube/answer/72431), [YouTube recommended upload encoding settings](https://support.google.com/youtube/answer/1722171) | proprietary | linked for thumbnail sizes and bitrate guidance |
| [BBC subtitle guidelines](https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/), [Netflix timed text style guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977) | proprietary | linked for subtitle reading rules |
| [EBU R128](https://tech.ebu.ch/publications/r128) | EBU publication | loudness targets |
| [Openverse](https://openverse.org) | per work (CC0, CC BY and others) | named as a sound-effect source; nothing copied |
| [Shadertoy](https://www.shadertoy.com) | per shader (default CC BY-NC-SA 3.0) | the porting checklist; no shader copied |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | AGPL-3.0 | surveyed for scope only; nothing copied |
| [terminalskills/skills](https://github.com/terminalskills/skills) | Apache-2.0 | surveyed for scope only |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills), [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills), [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills), [claudeskills.info video skills](https://claudeskills.info/best/video-skills/) | MIT; no licence; no licence; no licence | lists used to find other video and animation skills and the topics creators ask for |
