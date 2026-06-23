#!/bin/bash
# API 헬스체크 — 최대 120초 대기, 컨테이너 종료 감지
set -euo pipefail

echo "=== API 헬스체크 ==="

for i in {1..60}; do
  if curl -s http://localhost:8080/actuator/health 2>/dev/null | grep -q "UP"; then
    echo "✅ API 정상 실행 중"
    exit 0
  fi
  if ! docker ps --filter "name=bambi-api" --filter "status=running" -q | grep -q .; then
    echo "❌ API 컨테이너가 종료되었습니다."
    echo ""
    echo "--- 최근 로그 ---"
    docker logs bambi-api --tail 50
    exit 1
  fi
  printf "  대기 중... (%d/60)\r" "$i"
  sleep 2
done

echo "❌ API 헬스체크 타임아웃 (120초)"
exit 1
