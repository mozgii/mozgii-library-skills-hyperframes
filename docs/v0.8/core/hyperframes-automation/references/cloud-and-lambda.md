---
title: HyperFrames on AWS Lambda and Google Cloud Run
author: MOZGII, Inc.
lang: en
---

# HyperFrames on AWS Lambda and Google Cloud Run

HyperFrames on AWS Lambda and Google Cloud Run splits one render into chunks that many workers capture in parallel,
then joins them, inside your own cloud account. Use it for long videos, many videos at once, or renders that must
stay in your infrastructure. Checked against the `hyperframes` CLI 0.8.223.

## Contents

The sections of this page:

- What distributed rendering cannot do
- Deploying the Lambda stack
- Permissions for Lambda
- Uploading a project once with sites
- Rendering one video on Lambda
- Batches on Lambda
- Concurrency and cost on Lambda
- Lambda from your own code
- Deploying and rendering on Cloud Run
- Remotion Lambda users

## What distributed rendering cannot do

Distributed rendering (Lambda and Cloud Run) has limits the local renderer does not:

- frame rates 24, 25, 30 and 60 only;
- SDR only: no HDR output;
- no HLS output; MP4 (H.264 or H.265), MOV, WebM and PNG sequences are supported;
- page motion blur is off;
- the execution input (variables and options) is capped at 256 KiB on Step Functions: pass media by URL.

For one short render, the deploy and upload overhead outweighs the gain: render locally.

## Deploying the Lambda stack

Deploying the Lambda stack needs AWS credentials (any chain the AWS SDK resolves: environment, profile, SSO), the AWS
SAM CLI, and `@hyperframes/aws-lambda` installed globally at the same version as the CLI. The stack is one Lambda
function behind a Step Functions workflow (plan, then a map of render chunks, then assemble) with an S3 bucket.

```bash
npm install -g hyperframes@0.8.223 @hyperframes/aws-lambda@0.8.223
npx hyperframes lambda deploy --stack-name=hf-prod --region=us-east-1 --memory=10240
npx hyperframes lambda destroy --stack-name=hf-prod                    # removes the stack
```

- `deploy` writes `.hyperframes/lambda-stack-<stack-name>.json` in the current folder. Every later `lambda` command
  reads that file, so they must be run from the same folder and given the same `--stack-name`; otherwise they fail
with "no stack state".
- The video chunks run on an arm64 container image by default; `--video-arch x86_64` keeps x86, and is required with
  `--chrome-source chrome-headless-shell`.
- Upgrade order matters: deploy the stack again first, then upgrade the CLI or SDK that launches renders. A client
  newer than its stack refuses to start with `STACK_TOO_OLD`.
- Teams that want to read the CloudFormation first can deploy the published SAM template directly, or use the
  `HyperframesRenderStack` CDK construct from `@hyperframes/aws-lambda/cdk`.

## Permissions for Lambda

Permissions for Lambda come from built-in policy documents, which avoid the first-deploy "not authorized to perform
iam:CreateRole" error:

```bash
npx hyperframes lambda policies user                              # inline policy for the deploying IAM user
npx hyperframes lambda policies role                              # trust relationship and policy for a service role
npx hyperframes lambda policies validate ./infra/hf-deploy.json   # fails when a checked-in policy lacks an action
```

The generated documents use `Resource: "*"`; narrow them to the deployed ARNs after the first deploy. Code that
starts renders with its own role needs `states:StartExecution` and `states:DescribeStateMachine` on the state
machine, plus read and write on the bucket.

## Uploading a project once with sites

A site is a content-addressed upload of a project: `npx hyperframes lambda sites create ./welcome` hashes every file,
uploads only files the bucket does not already hold, and prints a site id. Pass `--site-id <id>` to each render to
skip hashing and uploading. Shared files expire 30 days after they were last written; a render that reuses a file
older than 7 days refreshes it, so files in use never expire. A render whose site files expired and cannot be
re-uploaded stops with `SITE_FILES_MISSING`: run `sites create` again.

## Rendering one video on Lambda

Rendering one video on Lambda names the canvas size and, for templates, the variables:

```bash
npx hyperframes lambda render ./welcome --site-id <id> --width 1920 --height 1080 --fps 30 \
  --quality high --variables '{"name":"Ada"}' --strict-variables --output-key renders/ada.mp4 --wait
npx hyperframes lambda progress <render-id>                       # status, frames, cost so far
```

Without `--wait` the command returns a render id at once. `--output-resolution 4k` supersamples without changing the
layout; `--codec h265` gives HEVC in MP4; `--max-bitrate` and `--buffer-size` cap MP4 bitrate per chunk.

## Batches on Lambda

Batches on Lambda start one execution per line of a JSONL file, after uploading the project once.

```jsonl
{"outputKey":"renders/ada.mp4","variables":{"name":"Ada","accent":"#ff4d67"}}
{"outputKey":"renders/lin.mp4","variables":{"name":"Lin","accent":"#36b37e"},"executionName":"welcome-lin"}
```

```bash
npx hyperframes lambda render-batch ./welcome --batch recipients.jsonl --width 1920 --height 1080 \
  --strict-variables --dry-run --json                             # validate every row; nothing starts
npx hyperframes lambda render-batch ./welcome --batch recipients.jsonl --width 1920 --height 1080 \
  --max-concurrent 10
```

The command prints one manifest row per line; a row that fails to start does not stop the others. `--max-concurrent`
(default 50) limits executions in flight.

## Concurrency and cost on Lambda

By default Lambda concurrency comes from the account. Without a reservation, a render plans for as much as 90% of
whatever concurrency the account has not reserved (256 chunks at most), so other functions keep some headroom. `--concurrency=N` on
`deploy` reserves N executions for the function and caps every render at N chunks; `--concurrency=none` removes a
reservation. A stack deployed with an older CLI has a reservation of 8 and keeps it until you change it. Cost is Lambda
GB-seconds (billed time times memory) plus a small fee per Step Functions state transition; `lambda progress` shows
the running total.

## Lambda from your own code

Lambda from your own code uses the SDK in `@hyperframes/aws-lambda` (`renderToLambda` and progress helpers), with the
same site, variables and output-key options as the CLI. Store the returned render id with your job record, poll
progress or react to completion, and copy the output from S3 to your own storage.

## Deploying and rendering on Cloud Run

Deploying on Cloud Run needs a Google Cloud project with billing, `gcloud` signed in to it, Terraform 1.5 or later,
and `@hyperframes/gcp-cloud-run` installed beside the CLI. Outside a checkout of the HyperFrames repository, pass a
renderer image built from its Cloud Run Dockerfile with `--image`.

```bash
npx hyperframes cloudrun deploy --project my-gcp-project --region us-central1
npx hyperframes cloudrun sites create ./welcome
npx hyperframes cloudrun render ./welcome --width 1920 --height 1080 --variables '{"name":"Ada"}' --wait
npx hyperframes cloudrun render-batch ./welcome --batch recipients.jsonl --width 1920 --height 1080 --max-concurrent 10
npx hyperframes cloudrun progress <execution-name>
npx hyperframes cloudrun destroy --project my-gcp-project         # deletes the stack AND its render bucket
```

`deploy` switches on the needed APIs, builds and pushes the renderer image where possible, runs the Terraform module
that ships with the CLI, and records the bucket, service URL and workflow name in `~/.hyperframes/`. `--cpu`, `--memory`, `--max-instances` and
`--timeout` size the service. From Node, `@hyperframes/gcp-cloud-run/sdk` exposes `deploySite`, `renderToCloudRun`
and `getRenderProgress`. Copy every output you need before `destroy`.

## Remotion Lambda users

Remotion Lambda users map their props directly: `defaultProps` becomes a `default` in `data-composition-variables`,
`inputProps` becomes `--variables` (or the SDK's `variables`), and `props.title` becomes `data-var-text="title"`, a
CSS variable or `window.__hyperframes.getVariables().title`. Porting the composition itself: the
`remotion-to-hyperframes` skill.
