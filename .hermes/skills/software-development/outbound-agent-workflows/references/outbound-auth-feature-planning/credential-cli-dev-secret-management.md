# Credential CLI for Dev Secret Manager planning

Use this reference when documenting or planning Outbound Agent credential-management CLI work for OAuth/client credentials.
Canonical credential storage, `secretRef`, Secret Manager, KMS, 1Password, and incident-response boundaries live in `../../domain-model-design-docs/references/credential-encryption-key-management.md`; do not repeat that storage rationale here.

## CLI responsibility

- Treat GCP OAuth Client ID/Secret creation as a human administrator action in Google Cloud Console.
- Treat 1Password as the approved human-managed source of the manually created OAuth client credential.
- The CLI should read the approved 1Password source and configure, verify, or report on the approved Dev server Secret Manager target.
- The CLI should not create/delete Google OAuth clients, modify consent screen settings, or regenerate client secrets by default.
- Git keeps only `secretRef`, schema, owner, rotation, approval, and drift metadata. It must not keep plaintext values or encrypted credential blobs.

## Recommended initial implementation stack

For this repo, prefer TypeScript for the first CLI implementation because the app already uses Next.js/TypeScript/Vitest/npm scripts.

Suggested shape:

```text
front/package.json
  scripts:
    credentials: "tsx ../tools/credentials/cli.ts"
tools/credentials/
  cli.ts
  schemas.ts
  sources/onepassword.ts
  targets/vercel-env.ts
  targets/tencent-secret-manager.ts
  targets/aws-secret-manager.ts
  targets/env-file.ts
  validators/redaction.ts
```

Consider Go later only if a standalone cross-platform binary becomes important. Rust is usually too much for the initial planning/MVP CLI unless the user explicitly asks for it.

## Core command set

```text
dev-secret plan      # redacted source/target diff preview
dev-secret apply     # write 1Password source credential to approved Dev Secret Manager
dev-secret verify    # verify source/target/runtime read/fingerprint
dev-secret status    # read-only status report
dev-secret audit     # stale legacy fallback, access policy, old-version audit
```

`apply`, `verify`, and `status` are the core functions. `plan` and `audit` reduce operational mistakes and should be considered early.

## Safety and output rules

- Default write-capable commands to dry-run.
- Require explicit `--apply` and approval evidence such as `--approved-change <ticket-or-pr-url>` for non-interactive use.
- Never output raw client ID, client secret, token, raw env file, or 1Password reveal output.
- Use only redacted suffixes, short fingerprints, field labels, version ids, principal ids, and secret refs in logs and PR text.
- `--verbose` must still not reveal plaintext.
- Break-glass plaintext reveal is out of scope for the CLI and belongs to separate 1Password/cloud-console approval flows.

## Verification dimensions

For `verify`, cover:

- credential reference schema;
- allowed target prefix/environment boundary;
- 1Password source field presence;
- Secret Manager target field presence;
- source-target redacted fingerprint match;
- enabled/current version state;
- runtime identity read access;
- OAuth callback URI metadata compatibility, without auto-modifying Google Console.

## Deployment-impact wording for PRs

When updating a PR body or feature-plan impact section for credential-reference work, make the deployability answer explicit:

- Existing/legacy deployment can still be deployable if CI/CD already copies GitHub repository secrets into the actual runtime source the app reads, such as Vercel environment variables or a VM env file.
- GitHub repository secrets by themselves are not a runtime source for the Next.js app.
- `legacy-runtime-secret/v1` is a transitional inventory/envelope for current deployment reality, not the new standard source path.
- `credential-reference/v1` should point to approved sources such as 1Password for local or Tencent/AWS/Vault/approved env source for server environments.
- A PR that only adds schema/CLI dry-run support does not create/update Tencent Secret Manager, Vercel env, GitHub secrets, or VM env files; say so directly.
- The new Secret Manager path is not deployable until write/read/verify adapters and runtime loader integration exist.
