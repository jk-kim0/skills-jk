#!/usr/bin/env bats

setup() {
  repo="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$repo/.hermes" "$repo/bin" "$repo/fake-bin"

  printf "agent:\n  name: hermes\n" > "$repo/.hermes/config.yaml"
  printf "TELEGRAM_BOT_TOKEN=op://Employee/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN\n" > "$repo/.env.1password"

  cp "$BATS_TEST_DIRNAME/../hermes-sync-env" "$repo/bin/hermes-sync-env"
  chmod +x "$repo/bin/hermes-sync-env"

  cat > "$repo/fake-bin/op" <<'END_OF_FAKE_OP'
#!/usr/bin/env bash
set -o nounset -o errexit -o pipefail

if [[ ${1:-} != "run" || ${2:-} != "--env-file" || ${4:-} != "--" ]]; then
  printf "unsupported args: %s\n" "$*" 1>&2
  exit 2
fi

env_file=$3
shift 4

while IFS= read -r line || [[ -n "$line" ]]; do
  line=${line%%#*}
  line=${line#"${line%%[![:space:]]*}"}
  line=${line%"${line##*[![:space:]]}"}
  [[ -z "$line" || "$line" != *"="* ]] && continue

  key=${line%%=*}
  value=${line#*=}
  if [[ "$value" == "op://Employee/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN" ]]; then
    export "$key=fake-telegram-bot-token-for-tests-only"
  else
    export "$key=$value"
  fi
done < "$env_file"

exec "$@"
END_OF_FAKE_OP
  chmod +x "$repo/fake-bin/op"
}

@test "sync defaults to repo-local Hermes env" {
  run env -u HERMES_HOME PATH="$repo/fake-bin:$PATH" "$repo/bin/hermes-sync-env"

  [ "$status" -eq 0 ]
  [ -f "$repo/.hermes/.env" ]
  grep -q "TELEGRAM_BOT_TOKEN=fake-telegram-bot-token-for-tests-only" "$repo/.hermes/.env"
  [ ! -e "$repo/.env" ]
}
