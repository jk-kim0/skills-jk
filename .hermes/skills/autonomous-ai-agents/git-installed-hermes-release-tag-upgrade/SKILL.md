---
name: git-installed-hermes-release-tag-upgrade
description: Audit and upgrade a git-installed Hermes checkout to a chosen stable release tag, including release discovery, real install-layout detection, tag checkout, editable reinstall, and post-upgrade verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, upgrade, git-install, release, tag, maintenance]
---

# Upgrade git-installed Hermes to a stable release tag

Use when Hermes is installed from a git checkout and the user wants to know:
- current installed version
- latest stable release tag
- whether there is a good upgrade target
- or wants the checkout moved to a specific release tag

This is especially useful when the user previously pinned Hermes to a stable tag and does **not** want to run on moving `main`.

Important first lesson: do not assume the source checkout lives at `~/.hermes/hermes-agent`. In some setups the checkout is `~/.hermes` itself and the CLI is an editable install from that directory.

## Goals

1. Identify the current installed Hermes version and git state
2. Discover recent upstream release tags and determine the latest stable release
3. Check whether local untracked/dirty files would block tag checkout
4. Clean local residue when the user wants it discarded
5. Move the checkout to the requested tag
6. Verify `hermes --version`, repo `HEAD`, and tag alignment

## Current installation layout to expect

Do not hardcode one layout. Detect the real install first.

Observed layouts:
- checkout at `~/.hermes` itself, editable-installed into `~/.hermes/venv`
- checkout at `~/.hermes/hermes-agent`, with runtime/config still under `~/.hermes`

Useful probes:

```bash
readlink ~/.local/bin/hermes || true
~/.local/bin/hermes --version || true
python3 - <<'PY'
import importlib.metadata as md
try:
    dist = md.distribution('hermes-agent')
    print(dist.read_text('direct_url.json'))
except Exception as e:
    print(e)
PY
```

Interpretation:
- if `direct_url.json` points at `file:///Users/<user>/.hermes` with `editable: true`, then the repo checkout is `~/.hermes`
- if the CLI shim imports directly from `~/.hermes/venv/bin/python3`, verify whether the checkout and `HERMES_HOME` are the same directory before applying repo-path assumptions

## 1. Inspect current installed version

Run:

```bash
readlink ~/.local/bin/hermes || true
~/.local/bin/hermes --version || true
~/.hermes/venv/bin/python - <<'PY'
import importlib.metadata as md
try:
    dist = md.distribution('hermes-agent')
    print('version=', dist.version)
    print('direct_url=', dist.read_text('direct_url.json'))
except Exception as e:
    print(e)
PY
cd ~/.hermes
git rev-parse --show-toplevel
git branch --show-current || true
git rev-parse HEAD
git describe --tags --always --dirty || true
git status --short --branch
git tag --points-at HEAD || true
git tag --sort=-version:refname | sed -n '1,30p'
```

Important interpretation:
- if `git branch --show-current` is empty and status shows `## HEAD (no branch)`, the install is already pinned to a detached tag
- if `hermes --version` shows something like `Hermes Agent v0.10.0 (2026.4.16)`, keep both the semantic version and release-date tag in the report
- if `git describe` returns something like `v2026.4.16-1081-g<sha>`, the checkout is not exactly on the release tag even if the runtime still reports that release version

## 2. Discover upstream stable releases

Refresh tags first:

```bash
cd ~/.hermes/hermes-agent
git fetch --tags origin --prune
```

Then inspect release tags and GitHub Releases:

```bash
git ls-remote --heads origin main
git tag --sort=-version:refname | sed -n '1,40p'
env -u GITHUB_TOKEN gh release list --repo NousResearch/hermes-agent --limit 15
```

For candidate versions, inspect release metadata:

```bash
env -u GITHUB_TOKEN gh release view v2026.5.7 --repo NousResearch/hermes-agent \
  --json tagName,name,isDraft,isPrerelease,publishedAt,targetCommitish,url
```

How to choose the upgrade target:
- prefer the newest release where:
  - `isDraft=false`
  - `isPrerelease=false`
- ignore ad-hoc pre-releases such as desktop/test installer tags
- recommend the latest normal release tag unless the user explicitly wants a more conservative intermediate step

## 3. Check whether local files would block checkout

Before switching tags, inspect local residue:

```bash
cd ~/.hermes
git status --short --branch
git ls-files --others --exclude-standard
```

Common untracked residue observed in this install style:
- `ui-tui/dist/`
- `ui-tui/packages/hermes-ink/dist/`
- `web/public/ds-assets/`
- generated `web/public/fonts/*.woff2`

If the user wants to discard local residue, clean it with:

```bash
git clean -fd
```

Then verify:

```bash
git status --short --branch
git ls-files --others --exclude-standard
```

Practical lesson:
- in this repo, release-tag checkout can be blocked by untracked build artifacts and generated assets
- cleaning these first is often necessary before moving from one tag to another

## 4. Move to the target tag

Once the tree is clean:

```bash
cd ~/.hermes
git fetch --tags origin --prune
git checkout --detach v2026.5.7
```

Expected result:
- detached HEAD at the release commit
- `git describe --tags` should equal the target tag
- `git status --short --branch` should show `## HEAD (no branch)` with no dirt

For an editable install, tag checkout alone is not enough when package metadata or dependencies need to line up with the target release. Reinstall into the existing venv after checkout.

First verify pip availability:

```bash
~/.hermes/venv/bin/python -m pip --version || ~/.hermes/venv/bin/python -m ensurepip --upgrade
```

If pip fails with a `--user` install error inside the venv, inspect `pip config list -v` for `global.user='true'` and override it for the reinstall:

```bash
PIP_USER=0 ~/.hermes/venv/bin/python -m pip install --no-user -e ~/.hermes
```

Practical lesson:
- some Hermes venvs can exist without an importable `pip` module even though the CLI still runs
- user-level pip config can force `--user` and break venv reinstalls unless overridden

## 5. Verify the installed CLI now points at the new tag

Run:

```bash
readlink ~/.local/bin/hermes
~/.local/bin/hermes --version
~/.hermes/venv/bin/python -m pip show hermes-agent | sed -n '1,20p'
~/.hermes/venv/bin/python - <<'PY'
import importlib.metadata as md
print(md.distribution('hermes-agent').read_text('direct_url.json'))
PY
cd ~/.hermes
git rev-parse HEAD
git tag --points-at HEAD
```

Expected result:
- symlink still points into the Hermes venv under `~/.hermes`
- `hermes --version` reports the upgraded version, e.g. `Hermes Agent v0.13.0 (2026.5.7)`
- `git tag --points-at HEAD` prints the same target tag
- package metadata shows the matching editable source path and upgraded package version

## Reporting format

Report:
- previous installed version
- chosen upgrade target and why
- whether local untracked residue had to be removed
- resulting `hermes --version`
- resulting repo HEAD SHA
- resulting tag at HEAD

## Important lessons

- A git-installed Hermes should usually be pinned to a release tag, not blindly updated to `main`, when the user explicitly wants stable behavior.
- `hermes --version` may still say `Update available: N commits behind`; that is normal for a stable tag pin and not itself a problem.
- The application code under `~/.hermes/hermes-agent` is distinct from `HERMES_HOME` runtime data; upgrading the app checkout does not automatically imply changing runtime config/state.
- Untracked build outputs can accumulate in the Hermes source checkout and should be cleaned before switching tags if the user wants them discarded.
- Verify both the CLI-reported version and the git tag at `HEAD`; checking only one is weaker evidence.
