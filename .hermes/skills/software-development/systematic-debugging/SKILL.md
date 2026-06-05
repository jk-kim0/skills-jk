---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior. 4-phase root cause investigation — NO fixes without understanding the problem first.
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, writing-plans, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

Special CI contract check:
- If a CI failure comes from a repository source-based test (for example a Node test that regex-matches source files), inspect the exact assertion before changing product code.
- Determine whether the product behavior/regression is real, or whether the test encoded an overly rigid implementation shape.
- When the intended behavior is still correct and only the source shape evolved, prefer the smallest test update that preserves the behavioral contract.
- Example pattern: a test expected `previewModeEnabled ? [internalFooterColumn]`, but a follow-up safely evolved it to `[{ ...internalFooterColumn, mobileLayout: "single" as const }]`. The correct fix was to relax the matcher, not revert the product change.
- Example pattern: source-contract tests for shared JSX primitives may assert a prop-less tag such as `<PlatformPageShell>` or `<PlatformContentSection className="...">`. If a valid follow-up adds behavior-neutral attributes/props such as `data-*` debug markers while preserving the same primitive and class contract, update the matcher to allow optional props rather than removing the marker or weakening the whole test.
- When CI failure comes from a test assertion around mocked function calls, read the assertion output carefully before changing product code. If the received call contains the intended data but the matcher is unstable because of nested `expect.objectContaining`, masked secret rendering, or mock-call tuple typing, prefer a test-side shape that records typed calls directly or compares a stable exact object. Do not weaken the behavioral contract to merely “called”. See `references/vitest-mock-call-verification.md` for an example pattern.
- When a GitHub Actions failure comes from Prisma schema drift or migration status checks, distinguish unapplied migration history from app deploy success: inspect the failed job log, schema-check artifacts, deploy workflow migration steps, and any manual migration workflow before proposing fixes. See `references/github-actions-prisma-migration-status.md` for the investigation and reporting pattern.
- When CI fails only in Next.js production build / TypeScript typecheck after local focused tests and lint passed, read the exact build type error before changing UI or schema code. A common root cause is overly narrow inference from `as const` registries, such as `new Set(CONST_OPTIONS.map(...))` becoming `Set<literal-union>` and rejecting a runtime `string` in `.has(value)`. Fix the type boundary at the validation helper, for example by widening to `new Set<string>(...)`, then rerun the focused test and lint/typecheck or wait for CI. Do not treat unrelated local dependency/runtime setup failures as the root cause of the CI error.
- When `gh pr checks --watch` exits non-zero but its printed table appears mostly green, do not infer final status from the watcher output alone. Re-query `gh pr view <pr> --json headRefOid,mergeStateStatus,statusCheckRollup` and `gh pr checks <pr>` for the current head SHA, because aggregate jobs such as `Front app CI` or `CI result` can be omitted or visually buried in the watcher table. Open the exact failed job log before applying another fix.

Next.js middleware/App Router rewrite regression check:
- When a bug involves `middleware.ts` rewriting an unprefixed route to a localized App Router route, do not stop after checking the middleware unit test or `x-middleware-rewrite` header.
- Also probe the exact deployed URL and compare unprefixed vs locale-prefixed variants on the target environment.
- Inspect the downstream `route.ts` handler to see whether it parses `new URL(request.url).pathname`; after a middleware rewrite, that handler may still see the original unprefixed URL even though `x-matched-path` shows the localized route.
- Treat middleware tests and route-handler direct-call tests as incomplete unless there is coverage for the real chain: unprefixed request -> middleware rewrite/redirect -> handler behavior.

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**WHEN a CLI/helper appears to disagree with a web console/UI:**

- First verify the CLI and UI are observing the same scope, filters, and execution mode before assuming the parser or API is broken.
- Re-run the helper with and without optional filters that change the data scope (for example sitemap-specific filters vs the unfiltered Page indexing screen).
- If there are multiple collection paths (for example direct saved-session HTML scraping vs live browser DOM/CDP scraping), compare both and note which one reads static HTML vs fully rendered DOM.
- Cross-check authoritative adjacent APIs or list commands for inventory mismatches (for example registered sitemap list vs sitemap options parsed from frontend markup).
- Report the distinction explicitly: “CLI can read the unfiltered UI, but this option makes it inspect a narrower filtered view” is a root cause, not just a workaround.

**Action:** Use `search_files` to trace references:

### 6. For browser layout bugs, measure document overflow before changing CSS

**WHEN the symptom is mobile right-side blank space, horizontal scrolling, clipped sticky behavior, clipped modal/dialog content, a popup extending beyond the viewport, or "there is empty space on one side":**

Do not guess from screenshots or visible content alone.
Measure the actual overflow first and identify the exact offending element.

For modal/dialog overflow specifically, check both the dialog primitive defaults and the option/content layout:
- default max width may be too narrow for selection grids, creating unnecessary vertical height;
- missing `max-height` lets the popup extend beyond the viewport;
- missing internal `overflow-y-auto` prevents users from reaching all options/actions;
- fix the dialog surface contract first, e.g. wider content for grids plus `max-h-[calc(100dvh-2rem)] overflow-y-auto`, instead of only shrinking child items.

Useful browser-console probe:

```js
(() => {
  const all = [...document.querySelectorAll('body *')];
  const offenders = all
    .map((el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        tag: el.tagName.toLowerCase(),
        className: (el.className || '').toString().slice(0, 160),
        text: (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100),
        left: Math.round(r.left),
        right: Math.round(r.right),
        width: Math.round(r.width),
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        overflowX: cs.overflowX,
        whiteSpace: cs.whiteSpace,
        display: cs.display,
      };
    })
    .filter((x) => x.right > window.innerWidth + 1 || x.left < -1 || x.scrollWidth > x.clientWidth + 1)
    .sort((a, b) => (b.scrollWidth - b.clientWidth) - (a.scrollWidth - a.clientWidth));

  return {
    viewportWidth: window.innerWidth,
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
    offenders: offenders.slice(0, 40),
  };
})()
```

What to look for:
- `documentElement.scrollWidth > clientWidth` confirms true horizontal overflow
- a footer/sidebar/nav/list wrapper can be the real cause even if the user noticed it while scrolling the main content
- common causes are:
  - `white-space: nowrap` on long labels
  - narrow multi-column grid/flex layouts on mobile
  - children whose minimum content width plus gap exceeds the viewport

Follow-up rule:
- once you find the offender, inspect the source CSS/layout contract before fixing
- prefer removing the structural cause (for example, a mobile 2-column grid that cannot fit nowrap labels) over masking it with `overflow-x: hidden`

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying
- For cross-repository UI ports, trace the full implementation contract, not only the component file: route shell, layout wrappers, global CSS cascade/layers, theme/font variables, sibling client components, and static assets. Matching JSX/className strings is not proof of a faithful port; verify browser computed styles on the exact reference and target URLs.

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

#### Next.js + Prisma auth cookie schema-migration 500s

When a deployed Next.js App Router app returns 500 only for some previously authenticated users after a user-id/schema migration, inspect stale session cookies before changing route code. If Vercel logs show Prisma `P2007` / `invalid input syntax for type uuid` from `prisma.user.findUnique({ where: { id } })`, reproduce with the exact cookie value and add a guard that rejects invalid session-cookie id formats before the typed DB query. Treat invalid session ids as unauthenticated state and verify the deployed URL redirects/renders login rather than 500. See `references/nextjs-prisma-session-cookie-schema-migration.md`.

#### User-facing identifier leakage in callback/status UI

When a bug report shows a UUID, database id, or opaque internal id in a toast/banner/status message after an OAuth callback or other redirect-return flow, trace both sides of the return contract before fixing copy:

1. Inspect the callback/route that builds the redirect URL and identify which query parameters carry status, reason/error, and success metadata.
2. Inspect the destination page/component that turns those query parameters into user-facing text.
3. Do not overload a generic error-oriented parameter such as `reason` with a success identifier; add a semantic success parameter such as `senderEmail`, `accountEmail`, or another user-comprehensible label.
4. Use the domain display identifier in the UI (email address, name, slug, label) and keep UUID/database ids for lookup, relations, logs, and audit links only.
5. Add a regression test at the redirect boundary that asserts the success location contains the user-facing identifier and does not contain the internal id.
6. If the product has UI guides or OpenSpec-style contracts, update them with the broader rule so future implementations do not reintroduce internal ids as labels.

#### URL-source coverage for sitemap and public-route E2E

When a sitemap/stage URL-health E2E passes but users report first-party 404s, first verify whether the broken URL was actually part of the test input. A test that only checks sitemap `<loc>` entries is a sitemap health check, not a whole-site dead-link check. It can miss legal/pricing aliases, app handoff routes, legacy publication URLs, and first-party MDX/TSX/JSON links omitted from the sitemap.

Before changing route code, classify the URL source:
- archived/live sitemap `<loc>` entry
- explicit critical public entrypoint
- repo-authored first-party content/navigation link
- external handoff/allowlisted URL

For Next.js middleware/App Router chains, do not stop at `x-middleware-rewrite`. Probe the exact deployed unprefixed URL and inspect the downstream route handler. If the handler parses locale from `new URL(request.url).pathname`, it may still see the original unprefixed path after middleware rewrite and return 404. Prefer route params or explicit support for both prefixed and unprefixed forms.

Use `references/sitemap-e2e-url-source-blind-spots.md` for the full investigation checklist and test design pattern.

#### Controlled failure output for aggregate E2E validations

When a Playwright E2E test intentionally validates a large external contract (for example, sitemap URL health) and already prints a useful `Summary`/`Errors` section, the final aggregate failure should prioritize actionable diagnostics over assertion stack noise.

If the default `expect(...).toBe(...)` output obscures the real failures with `expect(received)` and `at ...spec.ts` frames, replace only the final aggregate assertion with a helper that:
- formats a controlled message containing the validation rule, summary counts, and failed item lines
- throws `new Error(message)`
- overrides the error stack with the same controlled message before throwing, so Playwright reports the controlled message without source stack frames

Do not use this for unexpected programming errors where a stack trace is valuable. See `references/playwright-controlled-e2e-failures.md` for a concrete TypeScript pattern and verification notes.

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs
- **`session_search`** — When the user references a prior session, recover the previous investigation instead of re-deriving it from scratch

### Mobile/browser layout overflow triage

When the user reports a right-side blank gutter, unexpected horizontal scroll, or content that shifts sideways on mobile, do not assume the visible page body is the source.

Investigate in this order:

1. Measure the real page overflow first:
   - `window.innerWidth`
   - `document.documentElement.clientWidth`
   - `document.documentElement.scrollWidth`
   - `document.body.scrollWidth`
2. Enumerate candidate overflowing elements by scanning for nodes whose bounding box extends beyond the viewport or whose `scrollWidth > clientWidth`.
3. Inspect computed layout on the worst offenders:
   - `display`, `gridTemplateColumns`, `gap`
   - `whiteSpace`, `overflowX`, `flexWrap`
4. Verify whether the cause is global chrome such as a header/footer rather than the route's main content.

For global chrome bugs such as header/footer content disappearing on mobile:
- Test the exact user-visible environment first (production/stage/preview/local) and record the URL + viewport + computed style evidence.
- Then test latest main or the current candidate branch with the same DOM probe. If production still has `display: none` but stage/latest main is already fixed, report it as a deployment/version gap instead of creating a duplicate code fix.
- Use a route that can render without unrelated credentials or data services when validating site-wide chrome. For example, prefer a repo-local static/semistatic route to validate footer behavior rather than a legacy Blob-backed dynamic route that may fail locally for missing storage credentials.
- Confirm visible DOM data, not just source code: count links/text in the footer/header, inspect `getComputedStyle(nav).display`, and capture a mobile screenshot when visual proof is required.

Common mobile root cause pattern:
- narrow viewport
- multi-column grid retained on mobile
- `white-space: nowrap` on long localized links
- grid column minimums + gap exceed the container width


Additional mobile layout pitfall:
- there may be no horizontal overflow at all, yet the page still looks wrong because a top-level page section lost its mobile side padding
- symptom: content cards or intro blocks expand to the full viewport width (`left: 0`, `right: viewport`), while sibling sections still keep `px-6`-style gutters
- this indicates a container contract mismatch, not an overflow bug
- fix the page-level section wrapper first; do not patch each child card/grid independently unless the page container contract is already correct

Typical symptom signature:
- page body looks fine near the top
- `main` or `footer` has larger `scrollWidth` than `clientWidth`
- one grid column starts within the viewport but ends past the right edge
- OR `documentElement.scrollWidth === clientWidth`, but the affected page section and its cards all measure exactly `window.innerWidth` with `padding-left/right: 0px`

Useful browser probe:
```js
() => {
  const all = [...document.querySelectorAll('body *')];
  return {
    viewport: window.innerWidth,
    docScrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    offenders: all
      .map((el) => {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return {
          tag: el.tagName.toLowerCase(),
          className: String(el.className || '').slice(0, 120),
          text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
          left: Math.round(r.left),
          right: Math.round(r.right),
          width: Math.round(r.width),
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          display: cs.display,
          whiteSpace: cs.whiteSpace,
          overflowX: cs.overflowX,
          flexWrap: cs.flexWrap,
          gridTemplateColumns: cs.gridTemplateColumns,
        };
      })
      .filter((x) => x.right > window.innerWidth + 1 || x.scrollWidth > x.clientWidth + 1)
      .slice(0, 40),
  };
}
```

### Hermes/TUI-specific checks

For Hermes CLI/TUI issues, always verify the live execution path before changing code:

- Confirm whether the TUI is running from `--dev` source or a built `dist/entry.js` bundle.
- Check whether the observed behavior is controlled by runtime config toggles (for example `display.tui_statusbar`) rather than code.
- Trace the label/data source all the way back to env and session state (for example `HERMES_CWD`, cwd, or repo detection helpers) before assuming the renderer is wrong.
- If the user says “we changed this earlier”, search the prior session first; the root cause may already be documented there.
- For Hermes TUI memory regressions, compare the suspect commit against the immediate previous commit in a detached worktree, build both, and measure the live Node RSS under the same launch context.
- When testing TUI regressions, keep the Python gateway environment constant. A broken gateway startup (for example using system `python3` instead of the Hermes venv) can make an OOM disappear and mislead you into blaming or exonerating the wrong TUI code path.
- If the regression only appears when the gateway is healthy, treat it as a TUI-plus-gateway interaction bug rather than a pure formatter/rendering bug. Isolate whether the trigger is in hook/state updates (for example repo-info hooks) or in the gateway event stream.

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
