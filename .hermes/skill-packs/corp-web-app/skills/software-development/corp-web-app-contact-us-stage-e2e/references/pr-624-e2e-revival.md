# PR #624 E2E revival notes

Context: PR #624 originally pruned invalid docs/E2E claims in `corp-web-app`. The user later clarified that the website was working and asked to revive E2E tests so they perform real validation against `https://stage.querypie.com/`.

Useful observations:

- Direct Contact Us hosted submission worked against stage when the spec filled a complete valid form and waited long enough.
- Passing command:
  ```bash
  cd tests
  BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts e2e/contact-us.spec.ts --reporter=line
  ```
- Verified result in-session: `5 passed`.
- Full runner also passed:
  ```bash
  cd tests
  BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts --reporter=line
  ```
  Verified result in-session: `13 passed`.

Contact Us submit details that mattered:

- Fill required text fields:
  - First Name: `JK`
  - Last Name: `Test`
  - Business Email: `jk+test@querypie.com` or `CONTACT_US_E2E_EMAIL`
  - Company Name: `QueryPie`
  - Department / Title: `Engineering`
  - Questions / Additional Information: overrideable via `CONTACT_US_E2E_MESSAGE`
- Fill optional phone: `010-1234-5678`
- Select Inquiry Type: `Request for Product Demo`
- Check product: `AI Platform QueryPie AIP`
- Select Planned Implementation Date: `Within 3 months`
- Check marketing/news checkbox if using the complete submit helper
- After clicking `Proceed`, wait up to about 45 seconds for `Submission Complete`.

Why UTM and submit were split:

- The UTM spec variant that first visited `/?utm_*`, verified `utm-attribution`, navigated to `/company/contact-us`, and then submitted the form did not reach `Submission Complete` within 45 seconds during the session.
- Direct Contact Us submission passed, so deleting submit coverage was wrong.
- Stable final split:
  - `contact-us.spec.ts`: real hosted submit completion
  - `utm-tracking.spec.ts`: UTM cookie generation, first/recent behavior, cookie persistence after Contact Us navigation, and Contact Us form gating/enabled-state with UTM present

PR hygiene lesson:

- After changing the E2E scope, update the PR body. In this session the body still claimed “real submit removed” and old pass counts (`4 passed`), which became stale after reviving submit coverage.
