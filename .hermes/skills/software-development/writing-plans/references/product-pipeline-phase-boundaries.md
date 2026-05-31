# Product/data-pipeline planning phase boundaries

Use this reference when writing early design or implementation-planning docs for products whose value depends on a multi-stage data pipeline and a later external action workflow.

## Core lesson

Do not collapse discovery/qualification work and external execution work into one undifferentiated pipeline. Separate them explicitly so reviewers can validate data quality before the system takes actions that contact real people or affect external systems.

## Recommended structure

### 1. Discovery / qualification pipeline

Purpose: find and refine the target object before any external action.

Typical steps:
- campaign or job setup
- source discovery / ingestion
- candidate entity creation
- profile enrichment
- fit or priority scoring
- research summary / evidence extraction
- qualification review

Output: a qualified target that is ready for the next pipeline, not an already executed action.

For outbound-sales products, this means `Lead Candidate` -> `Qualified Prospect`. The Discovery pipeline should produce enough evidence for a reviewer to decide whether the lead is worth contacting.

### 2. Execution / response pipeline

Purpose: act only on qualified targets, then collect and classify the result.

Typical steps:
- action/message plan generation
- human approval, if the action has external or reputational risk
- execution
- response/event ingestion
- outcome / conversion classification
- human follow-up task creation
- feedback loop

For outbound-sales products, this means only `qualified_for_outreach` prospects can enter message generation, outreach approval, actual contact, response ingestion, conversion detection, and follow-up.

## Planning guidance

When writing the doc:
- Name the phase boundary explicitly.
- Define the input and output of each phase.
- Add distinct states for candidate, qualified target, execution-ready item, executed item, response received, converted, and closed.
- Keep UI screens aligned with the split: candidate intake/review screens should be separate from approval/execution/inbox screens.
- Keep implementation phases aligned with the split: build the discovery model and review flow before connecting external execution providers.
- If the user says the goal is to prove core functionality quickly, defer budget/cost/optimization features unless they directly affect safety or the proof of operation.

## Pitfalls

- Do not create message drafts or execution tasks for every discovered candidate by default. Drafting should be downstream of qualification unless the user explicitly wants draft quality reviewed during discovery.
- Do not treat a verified contact method as permission to act. Contactability is a discovery signal; execution still needs the execution pipeline's policy and approval gates.
- Do not let cost/budget controls dominate an MVP whose purpose is functional validation. Track processing/status metrics first; add budget/cost management later when scale or paid-channel operation becomes part of the requirement.
