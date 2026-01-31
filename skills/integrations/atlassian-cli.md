---
name: atlassian-cli
description: Jira 이슈 조회, Confluence 페이지 조회/검색 시 사용
tags: [jira, confluence, atlassian, cli, integration]
---

# Atlassian CLI

## 개요

Atlassian 서비스에 접근하기 위한 CLI 도구입니다.

| 서비스 | CLI 명령어 | 위치 |
|--------|------------|------|
| Confluence | `confluence` | `/usr/local/bin/confluence` |
| Jira | `jira` | (설정 필요) |

## Confluence CLI

### 사용 가능한 명령어

```bash
confluence <command> [args]
```

| 명령어 | 설명 |
|--------|------|
| `spaces` | 전체 글로벌 스페이스 목록 조회 |
| `search <query>` | 페이지 검색 |
| `page <pageId>` | 특정 페이지 내용 조회 |

### 사용 예시

#### 스페이스 목록 조회

```bash
confluence spaces
```

출력:
```
Key             Name                                     Status
-----------------------------------------------------------------
QueryPie        Product                                  current
QM              QueryPie ACP Manual                      current
Security        Security                                 current
```

#### 페이지 검색

```bash
confluence search "API 가이드"
```

출력:
```
ID           Title                                              Space
--------------------------------------------------------------------------------
12345678     API 사용 가이드                                    QueryPie
```

#### 페이지 내용 조회

```bash
confluence page 12345678
```

출력:
```
Title: API 사용 가이드
Space: Product
ID: 12345678

Content:
------------------------------------------------------------
페이지 본문 내용이 여기에 표시됩니다...
```

## Jira CLI

(추후 설정 예정)

## 설정 방법

### Confluence CLI 설치

1. API 토큰 생성: https://id.atlassian.com/manage-profile/security/api-tokens

2. CLI 스크립트 생성:

```bash
cat > /usr/local/bin/confluence << 'SCRIPT'
#!/bin/bash
set -o errexit -o nounset -o pipefail

CREDS='your-email@example.com:YOUR_API_TOKEN'
BASE_URL="https://your-site.atlassian.net/wiki"

api_call() {
  curl -s --user "$CREDS" "${BASE_URL}$1"
}

cmd="${1:-help}"

if [[ "$cmd" == "spaces" ]]; then
  api_call "/rest/api/space?limit=100&type=global" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fmt = '{:<15} {:<40} {:<10}'
print(fmt.format('Key', 'Name', 'Status'))
print('-' * 65)
for s in data.get('results', []):
    print(fmt.format(s['key'], s['name'][:38], s['status']))
"

elif [[ "$cmd" == "search" ]]; then
  query="\${2:-}"
  if [[ -z "\$query" ]]; then
    echo "Usage: confluence search <query>"
    exit 1
  fi
  encoded=\$(python3 -c "import urllib.parse; print(urllib.parse.quote('''\$query'''))")
  api_call "/rest/api/content/search?cql=text~\${encoded}&limit=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fmt = '{:<12} {:<50} {:<15}'
print(fmt.format('ID', 'Title', 'Space'))
print('-' * 80)
for p in data.get('results', []):
    space = p.get('_expandable', {}).get('space', '').split('/')[-1]
    print(fmt.format(p['id'], p['title'][:48], space))
"

elif [[ "$cmd" == "page" ]]; then
  page_id="\${2:-}"
  if [[ -z "\$page_id" ]]; then
    echo "Usage: confluence page <pageId>"
    exit 1
  fi
  api_call "/rest/api/content/\${page_id}?expand=body.storage,space" | python3 -c "
import sys, json, html, re
data = json.load(sys.stdin)
body_html = data.get('body', {}).get('storage', {}).get('value', '')
body = re.sub(r'<[^>]+>', ' ', body_html)
body = html.unescape(body)
body = re.sub(r'\s+', ' ', body).strip()
print('Title:', data.get('title', 'Unknown'))
print('Space:', data.get('space', {}).get('name', 'Unknown'))
print('ID:', data.get('id', 'Unknown'))
print()
print('Content:')
print('-' * 60)
print(body[:3000])
"

else
  echo "Usage: confluence <command> [args]"
  echo ""
  echo "Commands:"
  echo "  spaces              List all global spaces"
  echo "  search <query>      Search pages"
  echo "  page <pageId>       View page content"
fi
SCRIPT

chmod +x /usr/local/bin/confluence
```

3. 환경 변수 설정 (선택):

```bash
# ~/.zshrc 또는 ~/.bashrc
export ATLASSIAN_SITE="your-site"
export ATLASSIAN_EMAIL="your-email@example.com"
```

## 주의사항

- API 토큰은 스크립트에 직접 포함되어 있음 (보안 주의)
- 출력은 터미널 가독성을 위해 포맷팅됨
- 페이지 내용은 3000자로 truncate됨

## 참고 링크

- [Atlassian API 토큰 관리](https://id.atlassian.com/manage-profile/security/api-tokens)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
