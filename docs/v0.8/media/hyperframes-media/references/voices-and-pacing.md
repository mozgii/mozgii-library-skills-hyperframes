---
title: Narration voices and pacing
author: MOZGII, Inc.
lang: en
---

# Narration voices and pacing

Narration voices and pacing decide how a voiceover sounds and how long each scene runs. This page lists Kokoro voice
picks, speed settings, how to feed long scripts, and the cloud voice services teams use when a local voice is not
enough.

## Kokoro voices by use

Kokoro voices are chosen by content type. `npx hyperframes tts --list` prints the full bundled set of 54.

| Content | Voices |
|---|---|
| Product demo | `af_heart`, `af_nova` |
| Tutorial or how-to | `am_adam`, `bf_emma` |
| Marketing or promo | `af_sky`, `am_michael` |
| Documentation | `bf_emma`, `bm_george` |
| Casual or social | `af_heart`, `af_sky` |
| Non-English | `ef_dora` (Spanish), `jf_alpha` (Japanese), `zf_xiaobei` (Mandarin) |

`--lang` overrides the language the voice prefix implies. Valid codes: `en-us`, `en-gb`, `es`, `fr-fr`, `hi`, `it`,
`pt-br`, `ja`, `zh`.

## Speech rate and scene length

Speech rate sets scene length, so write the script before timing the scenes.

- Synthetic narration reads about 2.2 words a second (130 to 150 words a minute for a natural human read).
- Budget around 19 words (9 s) per scene, letting no more than two scenes stretch to 26 words (12 s).
- A film of 30 to 90 s holds roughly 155 words or fewer, and no film should pass about 400.
- When the narration outlasts the pictures, the pictures fill time with idle motion. Cut words from the script rather
  than slowing the motion.
- Write the voiceover as separate phrases, one per thing that appears, so each reveal has a cue point.

## Speed settings

Speed settings in `tts --speed` multiply the voice's natural rate.

| Speed | Use |
|---|---|
| 0.7 to 0.8 | complex tutorials, accessibility versions |
| 1.0 | natural pace (default) |
| 1.1 to 1.2 | intros, upbeat promos |
| 1.5 and above | rarely; listen before using |

## Long scripts

Long scripts go in a `.txt` file passed as the text argument: `npx hyperframes tts ./script.txt -o assets/voice/full.wav`.
Past about five minutes of speech, split the script by scene and synthesise one file per scene: retakes are cheaper
and each scene's audio length is known.

## Cloud voice services

Cloud voice services give more natural voices, cloning and sometimes word timestamps, at a cost and with an account.
ElevenLabs, OpenAI's speech endpoint, Google's Gemini and Cloud speech models, and HeyGen's voices are common choices.
Whatever the source:

- keep API keys in the environment or a secret store, never in a composition or a request file in the repo;
- save the result into `assets/` before the render;
- when the service returns no word timestamps, run `npx hyperframes transcribe <file> --model small.en` to get them;
- keep one narrator per channel or series so videos sound like one product.
