# Codex CLI gpt-5.4 / gpt-5.5 and service_tier notes

Captured from a macOS Codex CLI 0.130.0 setup using `~/.codex/config.toml`.

## service_tier behavior

Observed outcomes:

- `service_tier = "standard"` fails config parsing:
  - `Error loading config.toml: unknown variant 'standard', expected 'fast' or 'flex' in 'service_tier'`
- `service_tier = "fast"` parses and runs, but it explicitly selects fast/priority mode and is not appropriate when the user asks for normal/non-fast mode.
- `service_tier = "flex"` can pass local config parsing but may fail at runtime/API request time:
  - `Unsupported service_tier: flex`
- For normal/non-fast mode in this observed setup, omit the `service_tier` line entirely.

Verification used:

```sh
codex --help
codex exec 'Reply with exactly: OK'
```

The second command is important because `codex --help` only proves config parsing; it does not prove the service tier is accepted by the API.

## Model selection notes

Local `~/.codex/models_cache.json` for Codex CLI 0.130.0 reported:

- `gpt-5.5`: "Frontier model for complex coding, research, and real-world work."
- `gpt-5.4`: "Strong model for everyday coding."
- Both support reasoning efforts: `low`, `medium`, `high`, `xhigh`.
- Both are marked `supported_in_api: true`.
- Both support search and parallel tool calls.
- `gpt-5.5` was verified with:

```sh
codex exec -m gpt-5.5 'Reply with exactly: OK-5.5'
```

Recommended default for this user's repo-heavy workflow:

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"

[profiles.fast]
model = "gpt-5.4-mini"
model_reasoning_effort = "low"

[profiles.balanced]
model = "gpt-5.4"
model_reasoning_effort = "medium"

[profiles.deep]
model = "gpt-5.5"
model_reasoning_effort = "high"

[profiles.deep_xhigh]
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
```

Use `gpt-5.5` for complex codebase work, PR follow-up, large refactors, and debugging. Keep `gpt-5.4` as a balanced fallback for routine coding or when stability/predictability matters more than frontier model quality.
