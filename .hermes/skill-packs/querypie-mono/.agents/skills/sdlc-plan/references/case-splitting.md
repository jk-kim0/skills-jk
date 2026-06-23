# Case Splitting

Do not split plan-stage work into build tasks.

Split a large idea into separate SDLC cases only when each case can have its own plan and design.

Use case splitting after current-state evidence is summarized and the user has refined the idea.

Create a case group when one idea becomes multiple cases.

## Case and PR Boundary

An approved case should normally fit one trunk-based PR.

Use this as a planning boundary, not as a build-stage cleanup rule. If the work appears to need
multiple PRs, review whether the idea should become multiple cases before creating or approving the
case.

One case should be reviewable as one PR when:

- one PR description can explain the problem, scope, and expected outcome
- reviewers can understand the change intent without mixing unrelated goals
- test, review, release, and rollback decisions stay in one coherent scope
- the branch can stay short-lived enough for trunk-based development
- multiple build tasks can still be reviewed as one case-level change

If this is not true, propose a case split.

Each case split proposal should include:

- original idea
- split rationale
- linked case candidates
- dependencies
- recommended order
- deferred impact
- human approval status

## Split Heuristics

Split when cases can be approved, deferred, designed, or released independently.

Do not split only by implementation layer such as `front`, `api`, or `db`.

Keep one case when the work shares the same user problem, release decision, and design tradeoff.

Split when one candidate case is too large to review and merge as one trunk-based PR.

Do not split merely because one PR will contain several build tasks or several commits.

## Why Record Split Results

Recording the split preserves the original problem after the work becomes several independent
cases.

It prevents later stages from losing why each case exists, which case must happen first, and what
impact is deferred when one case is postponed.
