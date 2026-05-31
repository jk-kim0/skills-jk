# Outbound Agent: SendRun approval lock decision example

Use this as a concrete pattern when a Product Owner accepts an Open/TBD decision about an approval boundary that must prevent runtime drift.

## Decision shape

Canonical record:

- `openspec/changes/<change-id>/design.md`

Accepted policy summary:

- The approver must see the sender, template/version or immutable template snapshot, and recipient preview/count before approval.
- The approval transition is the lock boundary for sender, template/message content, Contact List source, and recipient snapshot.
- After approval and during sending, the target list, message content, and sender must not change.
- Actual send / batch-send code must not perform sender fallback or late assignment. If the SendRun has no approval-time locked sender, provider calls must be blocked before ledger/provider work proceeds.

## Files to sweep

For a docs/OpenSpec-only decision PR, update these surfaces together when they exist:

- `openspec/changes/<change-id>/design.md`: change `Status: Open` / `Decision: TBD` to `Status: Accepted`, mark accepted/rejected alternatives, and add implementation impacts.
- `openspec/changes/<change-id>/specs/uc-*/spec.md`: user-facing approval scenario should state that approval UI shows sender/template/recipient preview and locks the send inputs.
- `openspec/changes/<change-id>/specs/contract-*/spec.md`: implementation contract should add SHALL / SHALL NOT requirements and scenarios for immutable approved/sending SendRun inputs and no batch-time fallback.
- `openspec/changes/<change-id>/tasks.md`: mark the decision-recording/spec reflection completed, but leave implementation regression-test and guard removal as unchecked follow-up if code was not changed.
- Existing implementation plan / feature docs: update only the concise current conclusion and implementation guard. Do not duplicate the full decision table outside the canonical design log.

## Useful wording

Contract wording:

```md
SendRun approval은 sender/template/recipient preview를 확인하고 sender, template/version, recipient snapshot을 lock하는 경계여야 하며(SHALL), actual send batch 시점에 sender fallback 또는 late assignment를 수행하지 않아야 한다(SHALL NOT).
```

Scenario wording:

```md
#### Scenario: approved SendRun keeps locked sender and recipients

- GIVEN SendRun이 approved 또는 sending 상태임
- WHEN Team sender 설정 또는 Contact List Entry가 변경됨
- THEN 해당 SendRun의 locked sender identity와 recipient snapshot은 변경되지 않음
- AND send chunk action은 batch 시점 sender fallback 또는 late assignment를 수행하지 않음
```

## Pitfall

Do not treat approval confirmation copy as sufficient. The point of this class of decision is that the approval boundary and the actual send execution boundary must use the same immutable inputs, otherwise a reviewer can approve one sender/recipient/message and the system can send another.
