# Outbound Agent Sales Person Email Sender Selection Flow

Use this reference when a Sales Person creation flow depends on a reusable Team Settings Email Sender or another external entity that may need to be created mid-form.

## Product decision captured

When creating a Sales Person, Email Sender selection/addition should be the first form step because adding a missing sender navigates the user to Team Settings and can lose in-progress Sales Person form data.

The Sales Person creation screen should:

- Put Email Sender selection before Company, Display Name, Role Title, and other persona fields.
- Use a dropdown trigger to choose an existing Team Settings Email Sender.
- Include an explicit dropdown action such as `+ Add an Email Sender` when the desired sender is not listed.
- Route the add action to the Team Settings Email Sender creation/settings surface.
- Avoid showing long explanatory policy copy on the Sales Person form; keep the Sales Person screen focused on the action the user must take now.

The Team Settings Email Sender screen should carry the explanatory copy instead, because that is where sender ownership/reuse policy is configured:

> Sales Person email is selected from Team Settings Email Senders. The same Email Sender can be reused by multiple Sales Person personas. Add Email Sender in Team Settings first if the address is not listed.

## Generalizable UI/spec lesson

For OpenSpec-backed UI contracts, if a required selector can force navigation to create the missing dependency, record the dependency selector as the first form step and move explanatory policy copy to the owning configuration surface. This prevents the UI contract from encouraging users to fill fields that may be discarded.

## Surfaces to update together

- Change design doc: accepted decision/rationale.
- UC spec: user-facing flow order and scenario for missing sender.
- Contract spec: dropdown trigger/panel/option/add-action requirements.
- Feature/UI docs: screen overview and any page-specific docs.
- Tests: selector ordering, add-action visibility, and removal/relocation of stale Sales Person screen copy when applicable.
