# Codex CLI 0.130 custom Responses providers

## When this applies

Use this reference when checking whether Codex CLI can use an OpenAI-compatible custom endpoint, especially an internal proxy or gateway.

## Config shape

Codex CLI does not read Hermes `providers:` YAML. It uses `~/.codex/config.toml` with `model_provider` and `[model_providers.<id>]`.

Example:

```toml
model = "custom-model"
model_provider = "custom-responses"
model_reasoning_effort = "high"

[model_providers.custom-responses]
name = "Custom Responses Provider"
base_url = "https://example.internal/v1"
experimental_bearer_token = "<test-token>"
wire_api = "responses"
```

Prefer `env_key` for real secrets when available; `experimental_bearer_token` is useful for quick internal-key probes but stores the token in config.

## Verification recipe

Use a temporary `CODEX_HOME` before touching the user's real Codex config:

```bash
tmp=$(mktemp -d)
cat > "$tmp/config.toml" <<'TOML'
model = "custom-model"
model_provider = "custom-responses"

[model_providers.custom-responses]
name = "Custom Responses Provider"
base_url = "https://example.internal/v1"
experimental_bearer_token = "<test-token>"
wire_api = "responses"
TOML
CODEX_HOME="$tmp" codex exec --skip-git-repo-check --ignore-rules -C "$PWD" -o "$tmp/out.txt" "답변은 pong 한 단어만 출력." </dev/null
cat "$tmp/out.txt"
```

If Codex prints `Warning: no last agent message; wrote empty content`, the provider was accepted but the Responses streaming shape is not Codex-compatible enough for final-message extraction.

## Direct endpoint probes

Non-streaming Responses probe:

```bash
python3 - <<'PY'
import json, urllib.request, urllib.error
url='https://example.internal/v1/responses'
body={'model':'custom-model','input':'답변은 pong 한 단어만 출력.','stream': False}
req=urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer <test-token>'})
try:
    print(urllib.request.urlopen(req, timeout=60).read().decode('utf-8','replace')[:4000])
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode('utf-8','replace')[:2000])
PY
```

Streaming event-tail probe:

```bash
python3 - <<'PY'
import json, urllib.request, collections
url='https://example.internal/v1/responses'
body={'model':'custom-model','input':'답변은 pong 한 단어만 출력.','stream': True}
req=urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer <test-token>'})
last=collections.deque(maxlen=30)
types=[]
with urllib.request.urlopen(req, timeout=90) as r:
    for raw in r:
        line=raw.decode('utf-8','replace').rstrip('\n')
        if line.startswith('data:'):
            last.append(line[:1200])
            try: types.append(json.loads(line[5:].strip()).get('type'))
            except Exception: pass
print('types tail:', types[-20:])
for line in last: print(line)
PY
```

## Known custom Responses provider finding

On 2026-05-16, Hermes accepted `custom-responses` with:

```yaml
model:
  provider: custom-responses
  default: custom-model
providers:
  custom-responses:
    base_url: https://example.internal/v1
    key: <test-token>
```

Codex CLI 0.130.0 also parsed the equivalent TOML provider and sent requests, but `codex exec` produced no final assistant message. Direct non-stream `/v1/responses` returned a normal assistant `message`, while streaming returned `response.output_text.delta` and `response.completed` but lacked enough finalization events for Codex to materialize the last agent message. The likely server-side fix is to emit Codex/OpenAI-compatible streaming completion events such as `response.output_text.done`, `response.content_part.done`, and message/output item done events for the assistant message before `response.completed`.
