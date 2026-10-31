---
name: hyperframes-automation
description: Automates HyperFrames video production from code and at scale - choosing between the CLI, the Node render API (@hyperframes/producer with createRenderJob and executeRenderJob), managed cloud rendering, AWS Lambda and Google Cloud Run; templates with variables for personalised videos; batch renders from rows or JSONL; webhooks, idempotent retries and cancellation; a render service; and editing compositions headlessly with @hyperframes/sdk (openComposition, setText, setStyle, setTiming, serialize). Use when someone wants to render videos from a backend, an API or CI, make thousands of personalised videos, deploy rendering to their own cloud, or change composition HTML from a script or an agent without opening the editor.
metadata:
  tags:
  - hyperframes
  - automation
  - api
  - producer
  - sdk
  - aws-lambda
  - cloud-run
  - personalized-video
---

# HyperFrames automation

HyperFrames automation means producing video without a person at the keyboard: a backend renders on request, a
batch turns a spreadsheet into personalised videos, an agent edits a composition's text and timing from code. Every
path starts from the same project folder; what changes is who runs Chrome and FFmpeg and how much of the pipeline your
code controls. Checked against `hyperframes` CLI, `@hyperframes/producer` and `@hyperframes/sdk` 0.8.223.

## When to use this skill

Use this skill when renders are started by code (a web app, a queue worker, CI), when one template must become many
videos, when rendering must run in your own AWS or Google Cloud account or on a managed service, or when a script or
agent must change composition HTML. Day-to-day rendering by a person is `hyperframes-cli`; embedding a live
composition in a page is `hyperframes-player`.

## Step 0: read the versions your service runs

```bash
npm ls hyperframes @hyperframes/producer @hyperframes/sdk @hyperframes/aws-lambda @hyperframes/gcp-cloud-run --depth=0 2>/dev/null
npx hyperframes --version
npx hyperframes doctor --json | jq .ok     # Chrome and FFmpeg on this host
```

Keep every `@hyperframes/*` package on one version. A Lambda client newer than its stack stops with
`STACK_TOO_OLD`, so deploy the stack first, then upgrade the client.

## Pick the rendering surface

Pick the rendering surface by who must operate it; take the highest level that does the job.

| Need | Start with | You operate |
|---|---|---|
| Render in CI or a shell script | `npx hyperframes render` | the machine running it |
| Render from a Node service, with progress and cancel | `@hyperframes/producer` | the service and its Chrome and FFmpeg |
| No infrastructure at all | `npx hyperframes cloud render` (managed) | nothing beyond the request |
| Many parallel renders in your AWS account | `npx hyperframes lambda ...` | a Lambda, Step Functions and S3 stack |
| Many parallel renders in your Google Cloud project | `npx hyperframes cloudrun ...` | a Cloud Run, Workflows and storage stack |
| Custom frame capture | `@hyperframes/engine` | capture, encode and orchestration |

The ladder runs CLI, then Producer, then Engine: each step right gives more control and more responsibility. Cloud,
Lambda and Cloud Run decide where the same pipeline runs.

## Templates: one composition, many videos

A template is a composition with declared variables, so one project renders many versions without editing HTML.
Declare variables on `<html data-composition-variables='[...]'>`, bind them (`data-var-text`, `var(--id)`, or
`window.__hyperframes.getVariables()` in script), and pass values per render.

```bash
npx hyperframes render --variables '{"name":"Ada","plan":"Pro"}' --strict-variables -o renders/ada.mp4
npx hyperframes render --batch rows.json --output "renders/{name}.mp4" --strict-variables
```

- Always pass `--strict-variables` in automation: it rejects undeclared keys and wrong types before any render.
- Variables carry data, not files: pass a media URL or an `assets/` path, never base64 media.
- Text bound with `data-var-text` is set as text. Never build composition HTML by joining user input into markup;
  use variables or the SDK's `setText`.

Declaring, binding and the batch rows format: the `hyperframes` skill's variables reference.

## Render from Node with the producer

Rendering from Node with `@hyperframes/producer` runs the whole pipeline (compile, capture, encode, mix) inside your
process, with progress callbacks and an abort signal. Install it next to your service (`npm install
@hyperframes/producer`); the host needs Chrome and FFmpeg as for the CLI.

```ts
import { createRenderJob, executeRenderJob, RenderCancelledError } from "@hyperframes/producer";

const job = createRenderJob({
  fps: 30,
  quality: "high",                       // "draft" | "standard" | "high"
  format: "mp4",                         // "mp4" | "webm" | "mov" | "gif" | "png-sequence" | "hls"
  variables: { name: "Ada", plan: "Pro" },
  strictness: "strict",                  // correctness warnings block the render
});
const controller = new AbortController();
try {
  await executeRenderJob(job, "./templates/welcome", "./renders/ada.mp4",
    (j, message) => console.log(`${Math.round(j.progress)}% ${message}`), controller.signal);
} catch (err) {
  if (err instanceof RenderCancelledError) console.log("cancelled");
  else throw err;
}
```

- `entryFile` picks another entry composition; `fps` takes `{ num: 30000, den: 1001 }` for 29.97.
- `crf`, `videoBitrate`, `maxBitrate`, `bufferSize`, `keyframeIntervalSeconds`, `workers`, `useGpu`, `hdrMode` and
  `outputResolution` mirror the CLI's render flags.
- `format: "hls"` writes a playlist directory; HLS is SDR only and refuses GPU encoding.
- `debug: true` keeps `render.log` in the render's working directory.
- Run one render per worker process or container and queue the rest: each render already starts several Chrome
  workers, so parallel renders in one process exhaust memory.

`startServer({ port })` starts the package's own HTTP render service, and `@hyperframes/producer/distributed` exposes
the three distributed steps (`plan`, `renderChunk`, `assemble`) for an orchestrator you run yourself.

## Managed cloud rendering

Managed cloud rendering (`npx hyperframes cloud render`) uploads the project, renders it on HeyGen's service and
downloads the file; no local Chrome or FFmpeg. For unattended use, sign in once with an API key read from the
environment (`echo "$HEYGEN_API_KEY" | npx hyperframes auth login --api-key`), never a key written into a script.

```bash
npx hyperframes cloud render . --dry-run --json                  # what will upload; nothing is sent
npx hyperframes cloud render . --variables-file vars.json --strict-variables \
  --callback-url https://example.com/hooks/render --no-wait --idempotency-key "order-1842"
npx hyperframes cloud render --asset-id <asset_id> --variables '{"name":"Lin"}'   # re-use the upload
npx hyperframes cloud get <render_id>
```

- `--idempotency-key` makes a retried request safe: without it, a retry after a dropped connection creates a
  duplicate upload and render.
- Any media file the project refers to that weighs 5 MB or more is uploaded as an asset and fetched through a
  **public, unsigned URL**. Keep confidential footage out of managed cloud renders, or render it yourself.
- The project archive limit is about 200 MB; list exclusions in `.hyperframesignore`, never an asset the composition needs.

## Your own cloud: AWS Lambda and Cloud Run

Your own cloud means the render stack runs in your AWS account or Google Cloud project, split across many workers.
Both take the same variables and batch files, accept only 24, 25, 30 and 60 fps, render SDR only, and have no HLS.

```bash
npx hyperframes lambda deploy --stack-name=hf-prod --region=us-east-1     # needs AWS credentials and SAM CLI
npx hyperframes lambda sites create ./welcome                              # upload once; prints a site id
npx hyperframes lambda render-batch ./welcome --batch recipients.jsonl --width 1920 --height 1080 \
  --max-concurrent 10 --strict-variables --dry-run --json                  # validate, start nothing
npx hyperframes lambda render ./welcome --site-id <id> --width 1920 --height 1080 \
  --variables '{"name":"Ada"}' --output-key renders/ada.mp4 --wait
```

Each line of `recipients.jsonl` is `{"outputKey": "renders/ada.mp4", "variables": {...}}`. Deploy, permissions,
concurrency, costs, Cloud Run and the programmatic SDKs: [references/cloud-and-lambda.md](references/cloud-and-lambda.md).

## Edit compositions from code with the SDK

Editing compositions from code uses `@hyperframes/sdk`: open the HTML, find elements, change text, styles, timing,
attributes and variables, then serialize. It needs no browser and no editor, which suits agents, back-office tools
and bulk changes across many projects.

```ts
import { readFile, writeFile } from "node:fs/promises";
import { openComposition } from "@hyperframes/sdk";

const comp = await openComposition(await readFile("index.html", "utf8"));
const [title] = comp.find({ text: "Spring sale" });
if (title) {
  comp.batch(() => {                                   // one undo entry, one change event
    comp.setText(title, "Summer sale");
    comp.setStyle(title, { color: "#ffd60a" });
    comp.setTiming(title, { start: 0.4, duration: 3.2 });
  });
}
await writeFile("index.html", comp.serialize());
comp.dispose();
```

Element ids, sub-compositions, persistence adapters, undo and patches:
[references/sdk-editing.md](references/sdk-editing.md). After any automated edit, run `npx hyperframes check --json`
before rendering.

## A personalised video pipeline

A personalised video pipeline turns rows of data into checked files. The order that holds up:

1. Build and approve one template by hand; render it once with a realistic row and `--strict-variables`.
2. Validate every row against the declared variables before any render (`--dry-run` on the batch commands).
3. Render with a stable key per row (output name, `executionName`, or `--idempotency-key`) so retries do not duplicate.
4. Verify each output: exists, non-empty, duration equals the template's `data-duration` (`render-testing`).
5. Deliver through your own storage; presigned links expire, so store the file, not the link.

## Verify a batch before it runs

```bash
npx hyperframes render --variables '{"name":"Ada"}' --strict-variables -o /tmp/one.mp4   # one realistic row
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/one.mp4                   # equals data-duration
npx hyperframes lambda render-batch ./welcome --batch recipients.jsonl --width 1920 --height 1080 \
  --strict-variables --dry-run --json                                                     # every row, nothing starts
```

Feed the template one row with a wrong type as well: `--strict-variables` must refuse it.

## Checklist

- [ ] The highest-level surface that does the job; the reason written down.
- [ ] Every automated render passes `--strict-variables` or `strictness: "strict"`.
- [ ] Credentials come from the environment or the platform's role, never from code or variables.
- [ ] Retries carry a stable key; failures are reported per row, not by stopping the whole batch silently.
- [ ] Each output verified for streams and duration before delivery.
- [ ] Confidential media kept out of managed cloud renders.

## Gotchas

- **Symptom:** Duplicate renders after a retry. **Cause:** A cloud render was resent without `--idempotency-key`.
  **Fix:** pass a stable key per row.
- **Symptom:** The service runs out of memory. **Cause:** Several producer renders in one process. **Fix:** queue
  them, one render per worker process or container.
- **Symptom:** A batch row failed quietly. **Cause:** Nobody read the manifest. **Fix:** read `manifest.json` (local)
  or the per-row manifest (Lambda, Cloud Run).
- **Symptom:** Lambda says "no stack state". **Cause:** Lambda commands read `.hyperframes/lambda-stack-<name>.json`
  in the folder where `deploy` ran. **Fix:** run them from there with the same `--stack-name`.
- **Symptom:** `destroy` deleted the renders. **Cause:** Cloud Run's `destroy` removes its bucket. **Fix:** copy
  outputs out first.
- **Symptom:** Execution input too large. **Cause:** A Step Functions input is capped at 256 KiB. **Fix:** pass media
  by URL.

## Anti-patterns

| Do not | Do instead |
|---|---|
| joining user input into composition HTML | variables, or the SDK's `setText` |
| base64 media in variables | a media URL or an `assets/` path |
| API keys in scripts or variables | the environment or the platform's role |
| storing presigned links | store the file; links expire |
| confidential footage in managed cloud renders | render it yourself: assets of 5 MB or more go through public, unsigned URLs |

## References

- [references/cloud-and-lambda.md](references/cloud-and-lambda.md): Lambda deploy, permissions, concurrency, costs and SDK; Cloud Run deploy, render and teardown.
- [references/sdk-editing.md](references/sdk-editing.md): the SDK's queries, edit methods, persistence, undo and patches.

## See also

`hyperframes-cli`, `hyperframes-player`, `render-and-export`, `render-testing`, `render-performance`.
