# 1Password Item

Hermes uses 1Password as its secret store.

Primary approach:
- Store actual secret values in the personal 1Password item `Employee/skills-jk-hermes-local`.
- Use Secure Note custom fields named exactly like `.env` keys.
- Keep secret references in a local `.env.1password` file.
- Run `bin/hermes-sync-env` only when secrets change. This materializes a local Git-ignored `.env` file and is the step that may require 1Password authorization.
- Run Hermes from the local `.env` file so normal reads do not call 1Password: `HERMES_HOME="$PWD/.hermes" bash -lc 'set -a; source .env; set +a; hermes'`.

Allowed memory:
- Environment variable names.
- `.env` key names.
- 1Password vault name: `Employee`.
- 1Password item title: `skills-jk-hermes-local`.
- 1Password secret references, such as `op://Employee/skills-jk-hermes-local/OPENAI_API_KEY`.
- Rotation and verification instructions.
- Local sync workflow using `bin/hermes-sync-env`.

Forbidden memory:
- Actual token values.
- Actual API key values.
- Service account token values.
- Session cookie values.

Deferred approach:
- 1Password Environments are not the default for this personal setup.
- Revisit Environments if they become available and useful for the workflow.
