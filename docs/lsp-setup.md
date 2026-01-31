# LSP (Language Server Protocol) 설정

Claude Code에서 코드 분석 기능을 향상시키기 위한 LSP 설정 현황입니다.

## 설치 현황 (2026-01-31)

| 언어 | 언어 서버 | 버전 | 상태 |
|------|----------|------|------|
| TypeScript | typescript-language-server | 5.1.3 | ✅ 설치됨 |
| Python | pyright | 1.1.408 | ✅ 설치됨 |
| Go | gopls | 0.21.0 | ✅ 설치됨 |
| Kotlin | kotlin-language-server | 1.3.13 | ✅ 설치됨 |

## 설치 방법

각 언어 서버는 다음 패키지 매니저로 설치합니다:

| 언어 | 패키지 매니저 | 명령어 |
|------|--------------|--------|
| TypeScript | npm | `npm install -g typescript-language-server typescript` |
| Python | pip | `pip install pyright` |
| Go | go install | `go install golang.org/x/tools/gopls@latest` |
| Kotlin | Homebrew | `brew install kotlin-language-server` |

## PATH 설정

Python (pyright)은 사용자 디렉토리에 설치되므로 PATH 추가가 필요합니다:

```bash
# ~/.zshrc에 추가
export PATH="$PATH:/Users/jk/Library/Python/3.9/bin"
```

Go (gopls)는 기본적으로 `~/go/bin`에 설치됩니다.

## Claude Code 플러그인

Claude Code에서 LSP를 활용하려면 `/plugins` 명령으로 플러그인을 설치합니다:

- `typescript-lsp@claude-plugins-official`
- `pyright-lsp@claude-plugins-official`
- `gopls-lsp@claude-plugins-official`
- `kotlin-lsp@claude-plugins-official`

## LSP가 제공하는 기능

- 실시간 타입 에러/문법 에러 진단
- Go to Definition (정의로 이동)
- Find References (참조 찾기)
- 코드 자동완성
- 호버 시 타입 정보 표시
