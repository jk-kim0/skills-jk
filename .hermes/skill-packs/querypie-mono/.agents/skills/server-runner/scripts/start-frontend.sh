#!/bin/bash
# Frontend 기동 전체 절차: QDS 검증 → persistent runner 실행 → HTTP 200 확인
set -euo pipefail

SESSION=querypie-front
LOG=/tmp/querypie-front.log
REPO_ROOT=$(git rev-parse --show-toplevel)
TOKENS_CSS="apps/front/packages/design-system/tokens/dist/css/tokens.css"
FRONTEND_COMMAND="cd '$REPO_ROOT' && make -C tools/playwright-tests frontend > '$LOG' 2>&1"

echo "=== Frontend 기동 ==="

# 0) 의존성 설치 (node_modules 없으면)
if [ ! -d "apps/front/node_modules" ]; then
  echo "node_modules 없음 → pnpm install"
  make -C tools/playwright-tests frontend-install
fi

# 1) proto 산출물 검증 (로컬 변경 또는 현재 브랜치 커밋 변경이 있으면 재빌드)
PROTO_CHANGED=$(git status --porcelain --untracked-files=all -- libs/proto 2>/dev/null | head -1)
[ -z "$PROTO_CHANGED" ] && PROTO_CHANGED=$(git diff --name-only develop...HEAD -- libs/proto 2>/dev/null | head -1)
if [ ! -d "apps/front/node_modules/@querypie/proto/common" ] || [ -n "$PROTO_CHANGED" ]; then
  echo "proto 빌드 필요 (산출물 없음 또는 libs/proto 변경) → build:proto"
  make -C tools/playwright-tests frontend-proto
fi

# 2) QDS 토큰 검증
if [ ! -s "$TOKENS_CSS" ]; then
  echo "⚠️ QDS tokens.css 비어있음 → 재빌드"
  (cd "apps/front/packages/design-system/tokens" && pnpm build)
fi

# 3) persistent runner 실행
if command -v tmux >/dev/null 2>&1; then
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "기존 tmux 세션 사용: $SESSION (로그: $LOG)"
  else
    echo "Frontend 시작 중... tmux 세션: $SESSION (로그: $LOG)"
    tmux new-session -d -s "$SESSION" "$FRONTEND_COMMAND"
  fi
elif command -v screen >/dev/null 2>&1; then
  if screen -ls | grep -q "[.]$SESSION[[:space:]]"; then
    echo "기존 screen 세션 사용: $SESSION (로그: $LOG)"
  else
    echo "Frontend 시작 중... screen 세션: $SESSION (로그: $LOG)"
    screen -dmS "$SESSION" bash -lc "$FRONTEND_COMMAND"
  fi
else
  echo "tmux/screen 없음. 장시간 실행되는 frontend는 일반 셸 background로 띄우지 않습니다."
  echo "tmux 또는 screen을 설치하거나 IDE에서 frontend를 직접 실행하세요."
  exit 1
fi

# 4) 포트 열릴 때까지 대기 (최대 5분)
echo "포트 4001 대기 중..."
for i in $(seq 1 300); do
  if lsof -i :4001 -P 2>/dev/null | grep -q LISTEN; then
    echo "포트 열림. 빌드 완료 대기 중..."
    break
  fi
  sleep 1
done

# 5) compiled successfully + HTTP 200 확인
for i in $(seq 1 120); do
  if grep -q "compiled successfully" "$LOG" 2>/dev/null; then
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:4001 2>/dev/null)
    if [ "$HTTP" = "200" ]; then
      echo "✅ Frontend 정상 기동 — localhost:4001 (HTTP 200)"
      exit 0
    fi
  fi
  sleep 1
done

# 6) 실패
echo "❌ Frontend 기동 실패. 로그:"
tail -20 "$LOG"
exit 1
