# Vercel Marketplace / Storage resource diagnostics

Use this when a Vercel project is backed by a Marketplace storage/integration resource such as Neon and the user wants future CLI/API diagnosis to be possible from repository docs.

## Pattern

1. Record non-secret identifiers in the repo infra README, not only in the PR body.
   - Vercel team/project slug
   - Vercel team ID
   - Vercel project ID
   - Production URL
   - Root directory, framework, Node.js version, install/build commands, production branch
   - Marketplace/storage resource name and ID, for example `store_...`
   - External provider resource ID when available, for example Neon project ID/name
   - Region/plan/auth status when available
   - Store-project connection ID, connected environments, and synced env var names

2. Do not record secret values.
   - Never commit `DATABASE_URL`, passwords, tokens, or raw connection strings.
   - It is safe and useful to record secret names and whether they are synced to the Vercel Project.
   - If a storage resource exposes many secrets but the runtime only uses one env var, document that boundary explicitly.

3. Useful CLI/API probes:

```bash
vercel project inspect <project-name> --scope <team-slug>
vercel api /v10/projects/<project-id>/env --scope <team-slug>
vercel api /v10/storage/stores/<store-id> --scope <team-slug>
```

`vercel project inspect` gives project settings such as ID, owner, root directory, Node.js version, framework, install/build commands.

`/v10/projects/<project-id>/env` gives current Vercel project env entry structure: key, type, targets, gitBranch, env ID, timestamps. Sensitive values are not returned.

`/v10/storage/stores/<store-id>` gives Marketplace/storage resource status and project linkage. For Neon-style resources, useful fields include:

```text
store.id
store.name
store.ownerId
store.type
store.billingState
store.status
store.ownership
store.usageQuotaExceeded
store.metadata.region
store.metadata.auth
store.projectsMetadata[].projectId
store.projectsMetadata[].name
store.projectsMetadata[].latestDeployment
store.projectsMetadata[].environments
store.projectsMetadata[].environmentVariables
store.projectsMetadata[].id
store.secrets[].name
```

## README section shape

Prefer a section named like `생성된 리소스 현황 메모` / `Created resource diagnostics note` inside the environment-specific infra README. Include exact commands future agents can copy/paste.

Example skeleton:

```md
## 생성된 리소스 현황 메모

아래 값은 secret이 아니며, Vercel CLI/API로 리소스를 다시 찾거나 장애 분석을 시작할 때 사용하는 식별자다. 실제 connection string, credential, token은 repository에 기록하지 않는다.

### Vercel Project

```text
Vercel team/project: <team>/<project>
Vercel team ID: <team_...>
Vercel project ID: <prj_...>
Production URL: https://<project>.vercel.app
Root Directory: <subdir>
Framework: Next.js
Node.js Version: 24.x
Install Command: npm install
Build Command: npm run build
Production Branch: main
```

CLI 확인 명령:

```bash
vercel project inspect <project> --scope <team>
vercel api /v10/projects/<project-id>/env --scope <team>
```

### Marketplace / Storage resource

```text
Resource name: <name>
Resource ID: <store_...>
External resource ID: <provider-id>
Status: available
Region: <region>
Plan: <plan>
```

CLI/API 확인 명령:

```bash
vercel api /v10/storage/stores/<store-id> --scope <team>
```
```

## Pitfalls

- PR bodies are not durable enough for future operations. Put durable resource IDs and copy/paste diagnostic commands in the tracked environment README.
- Vercel CLI may not provide a list subcommand for integration resources; `vercel api /v10/storage/stores/<store-id>` is a practical read-only diagnostic path when the store ID is known.
- Do not use a linked local `.vercel` directory as the source of truth for documentation. Query the project/resource and record only stable non-secret identifiers.
