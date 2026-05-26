# HuggingFace cache attribution on shared Mac hosts

Use this reference when a shared Mac build/LLM host has a large `~/.cache/huggingface` and the user asks which GitHub repository created or uses it.

## Observed Mac Studio LLM1 example

Large cache:

```text
/Users/qp-test/.cache/huggingface                         390G
/Users/qp-test/.cache/huggingface/hub                     390G
/Users/qp-test/.cache/huggingface/hub/models--mlx-community--GLM-5-4bit 390G
```

The model was `mlx-community/GLM-5-4bit`, with snapshot ref:

```text
97b2af2010d640c7c0fa441f0e665e5092c16c07
```

Recent file mtimes clustered around the model download window. In that same period, shell history showed a local clone and run of:

```text
https://github.com/exo-explore/exo.git
cd exo
uv run exo
```

The local checkout was:

```text
/Users/qp-test/Workspace/exo
origin https://github.com/exo-explore/exo.git
```

The repo contained HuggingFace download/search code such as:

```text
src/exo/download/download_utils.py  -> huggingface_hub.snapshot_download
src/exo/master/api.py               -> HuggingFace / mlx-community model search
resources/inference_model_cards/*   -> mlx-community model cards
```

GitHub Actions runner work directories and `_diag` logs did not show HuggingFace/GLM usage, so the cache was attributed to the local `exo-explore/exo` run rather than the Actions runner fleet.

## Investigation pattern

1. Measure the cache by namespace/model:

```sh
du -xhd 2 ~/.cache/huggingface 2>/dev/null | sort -h | tail -n 80
find ~/.cache/huggingface -maxdepth 4 -mindepth 1 -print0 2>/dev/null |
  xargs -0 stat -f '%m %Sm %N' -t '%Y-%m-%d %H:%M:%S' 2>/dev/null |
  sort -nr | head -n 80
```

2. Identify HuggingFace model IDs from cache paths:

```text
models--ORG--MODEL  =>  ORG/MODEL
```

3. Cross-check GitHub runner evidence before blaming CI:

```sh
grep -RIlE 'huggingface|HF_HOME|TRANSFORMERS_CACHE|snapshot_download|from_pretrained|mlx-community|<model-name>' \
  ~/actions-runner/_diag 2>/dev/null
```

4. Search local workspace/repos and shell history for the model/cache tooling:

```sh
grep -niE '<model-name>|huggingface|hf_hub|snapshot_download|from_pretrained|mlx-community|exo' \
  ~/.zsh_history ~/.bash_history 2>/dev/null | tail -n 160

grep -RInE '<model-name>|huggingface_hub|snapshot_download|from_pretrained|HF_HOME|TRANSFORMERS_CACHE' \
  ~/Workspace ~/actions-runner/_work 2>/dev/null | head -n 200
```

5. For candidate repos, confirm GitHub identity:

```sh
git -C <candidate-repo> remote -v
git -C <candidate-repo> log -1 --format='%h %ad %s' --date=iso-strict
```

## Reporting guidance

Separate these cases explicitly:

- `created by local interactive repo/tool run` — e.g. local `exo-explore/exo` clone and `uv run exo`.
- `created by GitHub Actions runner job` — requires `_work`/`_diag` or workflow evidence.
- `created by desktop app` — e.g. LM Studio stores models under `.lmstudio`, not necessarily HuggingFace cache.

If attribution is circumstantial, state the confidence and evidence. Do not delete model caches unless the user explicitly asks; large model caches may be expensive to redownload.
