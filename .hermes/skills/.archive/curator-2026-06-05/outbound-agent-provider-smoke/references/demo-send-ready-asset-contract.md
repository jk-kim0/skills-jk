# Demo send-ready asset contract

Session learning from `querypie/outbound-agent` PR #193 follow-up.

When documenting a working email-sending demo, the product expectation is not merely that OAuth and provider send code exist. The demo should be described as ready only when every asset needed to send an email after sender authentication is present or explicitly required to be filled.

## Asset chain to check

- Team/user context for the demo.
- Team Email Sender / `SenderIdentity` connected through OAuth.
- Sales Person persona linked to the selected sender.
- Company and Product assets used by the sales narrative.
- Campaign.
- Audience or Contact List with intentional demo recipients.
- Email Template or generated message content.
- Recipient preview / SendRun state.
- Approval and actual send path, including evidence to collect.

## Documentation pattern

For documentation/OpenSpec PRs, avoid silently implementing or assuming missing seed data unless the user explicitly asks for implementation. Instead:

1. State the baseline principle: all assets needed for demo email send must be complete.
2. Add an explicit inspection step for missing assets.
3. Require missing assets to be filled before the demo is considered send-ready.
4. Reflect the requirement in both the canonical demo scenario document and relevant OpenSpec use-case/contract specs so docs do not drift.

This belongs with provider smoke readiness because it gates whether OAuth-authenticated demo sending can happen with minimal post-auth setup.
