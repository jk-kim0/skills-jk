---
name: docker-registry-image-parity-verification
description: Verify whether a multi-platform Docker image in one registry is actually identical to an image/tag in another registry, using buildx imagetools inspect, digest comparison, and auth checks.
---

# Docker registry image parity verification

Use this when a user asks whether an image was really copied/published from one registry to another (for example `ireg.querypie.io` -> `docker.io`) and the tag may already exist at the destination.

## Why this skill exists

A destination tag existing is NOT enough to conclude the expected image was uploaded.
For multi-platform images, you must compare:
- top-level index/manifest-list digest
- per-platform child manifest digests
- whether attestation manifests are present or missing

A tag can exist on Docker Hub while still pointing to different amd64/arm64 manifests than the source release image.

## Core rules

1. First inspect the source image tag.
2. Then inspect the destination image tag.
3. Compare digests before concluding success.
4. If push fails, separate:
   - source image existence
   - destination tag existence
   - destination auth/push authorization
5. Do not assume `imagetools create` succeeded just because the destination tag now exists; it may have pre-existed.

## Commands

Inspect source and target:

```bash
docker buildx imagetools inspect <source-ref>
docker buildx imagetools inspect <target-ref>
```

Examples:

```bash
docker buildx imagetools inspect ireg.querypie.io/release/querypie:11.6.2
docker buildx imagetools inspect docker.io/querypie/querypie:11.6.2
```

## What to compare

From each `imagetools inspect` output, record:
- `Digest:` line for the image index / manifest list
- each child manifest digest under `Manifests:`
- `Platform:` for each child manifest
- whether `unknown/unknown` attestation manifests exist

### Success criteria

Treat the copy/publication as truly identical only when:
- source index digest == target index digest
- child manifest digests match for `linux/amd64` and `linux/arm64`
- attestation presence also matches when the requirement is “all multi-platform image content” rather than only runnable platforms

### Important nuance

- `docker.io/querypie/querypie-tools:11.6.2` may be identical to source even if it includes attestation manifests.
- `docker.io/querypie/querypie:11.6.2` may exist and expose `linux/amd64` + `linux/arm64`, but still not match the source release image if the digest differs.

## Fast structured comparison with Python

Use a small script to avoid manual reading mistakes:

```bash
python3 - <<'PY'
import subprocess, re
pairs=[
    ('<source-ref>', '<target-ref>'),
]
for src,tgt in pairs:
    def inspect(ref):
        p=subprocess.run(['docker','buildx','imagetools','inspect',ref],capture_output=True,text=True,check=False)
        out=(p.stdout or '') + (p.stderr or '')
        digest=re.search(r'Digest:\s+(sha256:[0-9a-f]+)', out)
        manifests=re.findall(r'Name:\s+[^@]+@(sha256:[0-9a-f]+)\n\s+MediaType:.*?\n\s+Platform:\s+([^\n]+)', out, re.S)
        return digest.group(1) if digest else None, manifests, out, p.returncode
    sd, sm, so, src_rc = inspect(src)
    td, tm, to, tgt_rc = inspect(tgt)
    print('SRC', src, src_rc, sd)
    print('TGT', tgt, tgt_rc, td)
    print('INDEX_EQUAL', sd == td)
    print('SRC_MANIFESTS', sm)
    print('TGT_MANIFESTS', tm)
    print()
PY
```

## Auth diagnosis

If push/copy fails with Docker Hub, check whether docker.io credentials actually exist.

Read Docker config:

```bash
read_file ~/.docker/config.json
```

Key checks:
- `auths` may contain only the source registry
- `credsStore` may be set (for example `desktop`), so Docker Hub creds may be in the native keychain instead of `config.json`

Check Docker Desktop/native keychain entry:

```bash
printf 'https://index.docker.io/v1/' | docker-credential-desktop get
```

If you get:

```text
credentials not found in native keychain
```

then Docker Hub auth is missing on this machine.

## Interpreting push failures

Typical failure:

```text
insufficient_scope: authorization failed
```

Interpretation:
- source pull may still be fine
- target tag may already exist from an earlier upload
- your attempted copy did NOT complete successfully
- you cannot claim parity unless digest comparison proves it

## Build tag / release metadata extraction from a pulled image

Use this when the user asks to pull a Docker Hub image and confirm its build tag, version, or release metadata rather than comparing two registries.

1. Pull the requested image first:

```bash
docker pull <image-ref>
```

2. Inspect Docker metadata for digest, labels, env, and architecture:

```bash
docker image inspect <image-ref>
```

3. If Docker metadata has no `Labels`, `BUILD_TAG`, or version env, inspect likely in-container metadata files. For QueryPie application images, `/app/version` is the canonical file observed for release/build metadata:

```bash
docker run --rm --entrypoint /bin/sh <image-ref> -lc 'cat /app/version'
```

Typical `/app/version` fields to report:
- `version` — the build tag, for example `11.6.3-fc0a230`
- `builtAt`
- `commitDate`
- `gitTreeState`
- `components` commit map

4. Use `docker buildx imagetools inspect <image-ref>` when the user may care about the multi-platform index digest and per-platform child manifest digests, even if the task is only build-tag confirmation.

Pitfall: do not stop at Docker image `RepoTags` or `RepoDigests`; QueryPie build tags may be absent from labels/env and present only inside `/app/version`.

## Recommended reporting format

Report separately for each image:
- whether the target tag exists
- whether it matches the source exactly
- if not, whether the mismatch is top-level digest, child manifests, or attestation presence
- whether auth prevented corrective push
- for build-tag checks, the pulled image digest plus the in-container build tag/version source path, e.g. `/app/version`

Example conclusion style:
- `querypie-tools:11.6.2` exists on Docker Hub and matches source exactly.
- `querypie:11.6.2` exists on Docker Hub but does NOT match the source release image; the tag points to different amd64/arm64 manifests.
- Therefore the full 11.6.2 release set is not fully synced.

## Pitfalls

- Do not conclude success from “tag found”.
- Do not conclude failure from a failed push if the destination may already have been uploaded earlier.
- For OCI indexes, attestation manifests often appear as `unknown/unknown`; mention whether they match when the user explicitly asked for all multi-platform content.
- Docker Hub credentials may be absent even when source-registry credentials exist and pulls succeed.
