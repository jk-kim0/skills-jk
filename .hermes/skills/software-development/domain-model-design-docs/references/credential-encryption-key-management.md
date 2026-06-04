# Credential Reference and Secret Manager Reference

Use this reference when drafting or reviewing Outbound Agent feature docs/OpenSpec around credential references, Secret Manager storage, runtime secret loading, key rotation, and user OAuth token custody.

## Naming

- Prefer `Credential Reference` / `secretRef` for the final Outbound Agent design: git stores only the reference, schema, owner, and rotation metadata.
- Use `Credential Encryption Key` / `CEK` only when describing how Secret Manager/KMS/Vault/1Password protects credential values internally.
- Use `Key Encryption Key` / `KEK` only for the technical envelope-encryption role that wraps or unwraps a data encryption key.
- Avoid vague names like `Master Key` for this feature.

## Storage boundary

| Credential class | Examples | Recommended storage | Git-tracked content | Operator access |
| --- | --- | --- | --- | --- |
| System operation credential | OAuth client secret, LLM gateway credential, crawling provider app key, smoke-test credential | Secret Manager / Vercel env / 1Password local item | `secretRef`, schema, owner, rotation metadata only | PR may review metadata; plaintext access prohibited |
| Runtime platform secret | DB password, session signing secret, deployment runtime secret | KMS, Secret Manager, Vault, deployment secret store | Reference only when needed | Infra-scoped access only |
| User personal OAuth credential | Gmail/Microsoft refresh token, delegated mailbox token, user consent token | AWS/Tencent Secrets Manager, Vault, or KMS-envelope-encrypted DB row | DB/reference metadata only, not git inventory | Application-only read/write/refresh/revoke; no operator plaintext access |
| Ephemeral token | Access token, short-lived provider token | Memory/cache only or encrypted short-TTL store | None | No manual handling |

## Suitability conclusion

If a dev/server/runtime environment has a Secret Manager or equivalent managed secret store, store the credential value directly in that secret store and keep only `secretRef` plus schema metadata in git.

Git-tracked encrypted credential files are no longer the default design. They are at most a constrained fallback for low-risk local-only sandbox credentials when no Secret Manager exists, but Outbound Agent local development is now decided to use 1Password instead.

User personal OAuth tokens are never suitable for git-tracked encrypted files. User tokens are dynamic, privacy-sensitive, tied to consent/revoke/reconnect lifecycle, and should be managed automatically by the application through a separate secret boundary.

## Environment decisions

- Local development uses 1Password.
- Vercel dev/preview may use Vercel Sensitive Environment Variables; stricter environments should use external Secret Manager plus OIDC/federation where possible.
- Tencent Cloud dev/prod VMs should use Tencent Cloud Secrets Manager + KMS + CAM role; root-only env files are dev fallback only.
- GitHub secrets are CI-only fallback, not local/dev server/runtime credential sources.
- Before using or configuring a Secret Manager for Vercel dev server or Tencent Cloud dev server, first recommend the environment-specific option to the user and get explicit approval. Until approved, do not create or modify Vercel project env, Tencent Secrets Manager entries, KMS keys, CAM roles, GitHub secrets, or VM env files.

## Secret Manager or key compromise response

If a Secret Manager/KMS key, secret read principal, or provider credential is exposed, git re-encryption is not the primary incident response because git should not contain encrypted secret blobs.

Required incident path:

1. Enumerate affected `secretRef` paths, secret versions, principals, and access time ranges.
2. Disable or revoke affected secret versions and principals.
3. Rotate or revoke the underlying provider credentials where possible.
4. Store the replacement credential as a new Secret Manager version/item.
5. Update git metadata only if the `secretRef`, required field schema, owner, or rotation policy changed.
6. Run redacted smoke tests to verify runtime can read the new version without printing plaintext.
7. For credentials that cannot be provider-rotated, record residual risk and decide whether to replace service accounts or accept risk.

## OpenSpec/doc requirements to include

- Plaintext credentials SHALL NOT be stored in git-tracked files, PR bodies, issue comments, logs, shell history, images, or browser bundles.
- Encrypted credential blobs SHALL NOT be the default git-tracked storage for system credentials when a Secret Manager exists.
- Git-tracked credential reference files SHALL include `secretRef`, `requiredFields`, environment, provider, owner, and rotation metadata.
- Local development SHALL use 1Password as the credential source.
- GitHub secrets SHALL be CI-only fallback and SHALL NOT be local/dev server/runtime credential sources.
- User/team dynamic OAuth refresh tokens SHALL NOT use git-tracked files as the default store.
- System-operation credentials and user OAuth token secret boundaries SHALL be separate.
- User OAuth credential plaintext SHALL NOT be exposed to developers/operators; runtime access should be application-only and audited.

## Legacy runtime-secret envelope pattern

When the repository already depends on GitHub repo secrets, Vercel env vars, or VM `.env` files, model those as migration technical debt rather than pretending they are the target secret architecture.

Use a transitional envelope type such as `legacy-runtime-secret/v1` only to preserve existing deployments while a safer store is selected. The envelope must not contain the secret value. It may contain:

- `legacySourceRef`, for example `github-actions-secret://...`, `vercel-env://...`, or `env-file:///...#KEY`.
- runtime reference locations and required field schema.
- technical-debt status, target state, removal condition, and owner.
- `migrationMode: do-not-break-current-deployment` or an equivalent explicit flag.
- redacted validation policy.

Constraints:

- New credentials should default to `credential-reference/v1` plus an approved Secret Manager/1Password/Vercel-sensitive-env source, not `legacy-runtime-secret/v1`.
- Do not create or modify real GitHub secrets, Vercel env vars, VM env files, KMS keys, CAM roles, or secret-manager entries without explicit user approval.
- PRs and docs must keep values redacted and should describe only source references, schemas, and migration state.

## Implementation handoff checklist

- Add schema validation for YAML/JSON credential reference files.
- Add redacted smoke command that resolves `secretRef` and never prints plaintext.
- Add allowed scheme/prefix validation for `secretRef` per environment.
- Add stale secret version/reference drift checks.
- Keep user OAuth token storage design as a separate managed-secret or KMS-envelope-encrypted DB track.