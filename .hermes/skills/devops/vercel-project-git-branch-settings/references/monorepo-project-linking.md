# Monorepo Vercel project creation and Git linking notes

Use this when creating a Vercel project for one app inside a monorepo, such as `apps/finance`.

## Pattern

- Create one Vercel project per app.
- Set `rootDirectory` to the app path, e.g. `apps/finance`.
- Use explicit framework/build settings:
  - `framework`: `nextjs`
  - `installCommand`: `npm install`
  - `buildCommand`: `npm run build`
- Verify project JSON after creation, especially:
  - `id`
  - `name`
  - `framework`
  - `rootDirectory`
  - `installCommand`
  - `buildCommand`
  - `nodeVersion`
  - `link`

## Environment variables loaded only in interactive shells

If `VERCEL_TOKEN` / `VERCEL_TEAM_ID` are defined by zsh startup files and not visible in the non-interactive tool environment, run the Vercel commands through `zsh -ic '...'`.

Check presence only; never print token values:

```bash
zsh -ic 'if [[ -n "$VERCEL_TOKEN" ]]; then echo VERCEL_TOKEN_PRESENT; fi; if [[ -n "$VERCEL_TEAM_ID" ]]; then echo VERCEL_TEAM_ID_PRESENT; fi'
```

## GitHub link failure mode

A Vercel token can create and inspect projects but still fail to link a GitHub repository:

```text
Failed to link <owner/repo>. You need to add a Login Connection to your GitHub account first.
```

Interpretation:

- The Vercel token and team id are usable.
- The project can exist and have the correct root directory.
- Vercel cannot attach the GitHub repository until the Vercel account has a GitHub Login Connection / Git integration authorization for that repo.

Action:

- Report the prerequisite clearly.
- Ask the user to add the GitHub Login Connection in Vercel.
- Do not waste time retrying API payload variants after both `POST /v9/projects/{id}/link` and `vercel git connect` fail with this same message.

## Local artifact cleanup

`vercel link` can create app-local files such as:

- `apps/<site>/.vercel/`
- `apps/<site>/.gitignore` containing `.vercel`

If the command was only used for probing and these files are not intended for commit, delete them before finalizing.
