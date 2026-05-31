# Vercel GitHub Actions deploy workflows

Use this reference when adding repository-managed Vercel deploy scripts or GitHub Actions workflows based on another QueryPie web repository.

## Naming rule

The GitHub Actions workflow name should be legible in PR checks without opening the workflow file:

- Start with a verb, usually `Deploy`.
- Include the exact Vercel project name.
- Include the deployment target: `Preview`, `Production`, or a named custom environment.

Examples:

```yaml
name: Deploy outbound-dev Preview
name: Deploy corp-web-japan Production
```

Avoid names that hide the project or target:

```yaml
name: Vercel
name: Deploy
name: Preview Deploy
```

## Adaptation checklist

When copying a deploy pattern from an existing repo such as `corp-web-japan`, explicitly re-check and replace:

1. `VERCEL_PROJECT_ID` / project name mapping.
2. `VERCEL_ORG_ID` or team scope.
3. Vercel target flag: `--target preview` / `--prod` / custom environment.
4. App root directory and install/build commands for monorepos.
5. GitHub workflow `name:` and job `name:` as displayed in the Checks UI.
6. GitHub environment and secret names.
7. Branch/event filters, especially whether `pull_request` should deploy Preview and whether `main` should deploy Production.
8. Any PR comment step that posts or updates the Vercel deployment URL.

## Verification

Before reporting completion:

```bash
env -u GITHUB_TOKEN gh pr checks <pr-number> --repo <owner>/<repo>
```

Confirm that the check list includes the expected readable name, for example:

```text
Deploy outbound-dev Preview  pass  ...
Vercel                       pass  ...
```

If both Preview and Production workflows exist, their names must be distinguishable from the first word group shown in GitHub checks.
