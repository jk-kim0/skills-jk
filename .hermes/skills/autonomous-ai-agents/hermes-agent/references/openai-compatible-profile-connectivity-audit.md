# OpenAI-compatible profile connectivity audit

Use this when a user asks to confirm a Hermes profile/model connection, especially a custom OpenAI-compatible or LiteLLM-compatible provider such as Kimi/Moonshot behind an internal gateway.

## Goal

Confirm the active profile, provider, model, credential presence, endpoint reachability, and a real model call without exposing secrets in chat, documents, or commits.

## Evidence-gathering sequence

1. Locate the active Hermes home and config paths.
   - Prefer `hermes config path` and `hermes config env-path` when available.
   - If a named profile is involved, also inspect `$HERMES_HOME/profiles/<name>/config.yaml` and `$HERMES_HOME/profiles/<name>/.env`.
   - Do not assume `~/.hermes`; repo-local or profile-specific `HERMES_HOME` is common.

2. Identify active model selection, not just provider registration.
   - Check the profile's top-level `model.provider` and `model.default` / equivalent active model fields.
   - A `providers.<name>` entry only registers a backend; it does not prove the profile is using it.

3. Redact before reporting.
   - Never print API keys, auth headers, tokens, credential pool values, or internal connection strings.
   - Report only existence and a masked/redacted form such as `[REDACTED]`, plus non-sensitive names like provider id and model id.

4. Run a minimal real Hermes call through the named profile.
   - Example shape: `hermes -p <profile> chat -q 'Reply with exactly: KIMI_OK' -Q`
   - Use a deterministic expected reply so success is unambiguous.

5. For OpenAI-compatible/LiteLLM endpoints, optionally verify `/v1/models`.
   - Use the configured base URL and authorization from config/env, but keep them out of logs and summaries.
   - Report HTTP status and visible model IDs only.
   - Model-list success alone is not enough; keep the real Hermes call as the final connectivity proof.

6. Summarize in a user-safe way.
   - Include: profile name, provider id, model id, real-call result, `/v1/models` HTTP status/model count if checked.
   - Exclude: raw URL if internal/sensitive, auth header, API key/token, full config snippets containing secrets.

## Example safe summary

- Hermes profile: `kimi`
- Provider id: `querypie-kimi`
- Active model: `kimi-k2.6`
- Real Hermes call: succeeded (`KIMI_OK`)
- OpenAI-compatible models endpoint: HTTP 200, 3 model IDs visible
- Secrets/endpoints: redacted and not preserved

## Pitfalls

- Do not copy config blocks verbatim; they often contain credentials or internal endpoints.
- Do not preserve connection details in context handoffs or repository docs.
- Do not infer success from config presence. Always perform a small model call when the user asks whether the connection works.
- If a gateway/CLI session was already running before config changes, remember that config/profile changes may require a new Hermes process or gateway restart before they apply.