Repo-specific implementation facts and workflow constraints for skills-jk, querypie-docs, corp-web-v2, corp-web-japan, corp-web-app, QueryPie runner operations, and QueryPie Vercel operations have been moved from global memory into repo-context skills under `.hermes/skills/`; load the relevant skill before substantial work in that area.
§
For searching all historical file paths in a git repo and filtering by substring, the user uses the one-liner: git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep '<substring>'.
§
For this user, when they say 'repo 의 workspace 정리' or similar, interpret it as repo-local cleanup only: clean the current repository's stale worktrees/branches and local residue, not the whole ~/workspace. Keep going across follow-up turns until the repo is as clean as safely possible, including cleaning root-local residue and fast-forwarding root main to origin/main when safe.
§
In corp-web-app Tailwind migration planning after PR 817/841/845, the preferred implementation path is moving route subtrees from `src/app/(legacy)/**` to `src/app/(tailwind)/**` so URL routes stay unchanged while Tailwind layout/global CSS boundaries apply; per-page `TailwindLayout` wrapper opt-in inside legacy is no longer the default.
§
In the current skills-jk environment, skill_manage(action='patch') for github-pr-workflow failed on 2026-05-26 with OSError [Errno 28] No space left on device while writing .SKILL.md.tmp; future skill-library updates may need disk cleanup before patching large skills.
§
This user's workstation has Python3 + available subprocess scripting module for bulk git operations in large PR-heavy repos.
§
On this user's macOS environment, oh-my-codex (OMX) v0.18.5 is installed globally via nvm npm at `/Users/jk/.nvm/versions/node/v22.10.0/bin/omx`; `omx setup --merge-agents` configured user-scope Codex files under `/Users/jk/.codex`, preserving existing user-managed MCP servers. Codex CLI is Homebrew-owned at `/opt/homebrew/bin/codex` and authenticated via ChatGPT.