# 사내 GitHub 개인 계정 초기 저장소 구축 가이드 — v0.6

**상태:** 사내 GitHub 원격 저장소 미연결/미생성. 이 패키지는 합성 데이터 기반 PoC입니다.

## 0. 사전 승인과 인증

1. GitHub 웹 브라우저 주소를 보고 회사 승인된 GHES 또는 Enterprise Cloud인지 IT 담당자와 확인합니다. GitHub.com도 Enterprise Cloud일 수 있으므로 **사내 계정이라는 사실만으로 사내 호스팅이라고 판단하지 않습니다.**
2. 개인 계정 소유 Private 저장소 생성이 회사 정책상 허용되는지, AI-assisted 소스 및 OSS 라이브러리 반입/업로드가 허용되는지 확인합니다.
3. Git for Windows/Python 개발 도구 및 사내 인증 수단(SSH 또는 HTTPS/Git Credential Manager/PAT)은 회사 승인 방식만 사용합니다. 토큰을 채팅, 명령행 URL, Git 파일에 입력하지 않습니다.
4. 실제 업무 데이터, 사내 원본 코드, 인증 정보, 내부 서버 정보는 본 저장소로 전송하지 않습니다. 공유 전에는 `scripts/check_before_commit.py`와 수동 리뷰를 모두 실행합니다.

## 1. 회사 GitHub 웹에서 빈 Private 저장소 생성

- 우상단 `+` → `New repository` (보이는 UI는 버전에 따라 상이).
- Owner: 회사에서 사용이 승인된 **본인 개인 계정**.
- Repository name: `enterprise-ai-workspace`.
- Visibility: `Private`. `Internal`/`Public`으로 변경하지 않습니다.
- Description: `Security-first local-first knowledge workspace (synthetic-data PoC)`.
- 기존 소스와 충돌하지 않도록 README, .gitignore, license 자동 추가는 생략하여 빈 저장소로 시작합니다.
- 초기에는 Pages, Actions, Webhooks, 외부 App, 자동 배포를 활성화하지 않습니다.

## 2. 현재 프로젝트 파일을 사내 Windows PC에 준비

- 승인된 방식으로 v0.6 패키지를 내려받아 *회사 정책이 허용하는 개발 경로*에 압축 해제합니다.
- 압축 해제 경로에 실제 사용자 문서가 섞이지 않도록 별도의 소스코드 폴더를 유지합니다.
- 사내 VS Code 터미널(Windows PowerShell)에서 프로젝트 루트로 이동합니다.
- **아래 내용은 직접 검토 후 순서대로 실행합니다.**

```powershell
git --version
python --version
git init -b main
# 사내 개발 계정에 이미 Git user.name/user.email이 구성됐는지 확인
git config user.name
git config user.email
# 누락된 경우 사내 Git 정책에 맞게 설정: git config user.name "..." 등

git add .
python scripts/check_before_commit.py
git diff --cached --check
git status --short
git diff --cached --stat
# 목록과 Diff를 사람이 직접 검토
git diff --cached
# 이상 없을 때에만 최초 Commit
git commit -m "chore: bootstrap security-first template workspace PoC"
```

※ `git init -b main`이 사내 설치 Git 버전에서 지원되지 않으면 `git init` 후 `git branch -M main`을 사용합니다.

## 3. 검증된 원격 주소 연결과 최초 Push

브라우저 주소·인증서·회사 정책을 대조하고, 빈 저장소에 나타나는 Clone URL을 그대로 사용합니다. `github.com` 또는 다른 도메인을 추정해서 입력하지 마세요.

```powershell
# 실제 저장소 웹 페이지에 나온 HTTPS 또는 SSH Clone URL 사용
git remote add origin <APPROVED_COMPANY_REPO_CLONE_URL>
git remote -v
# remote 주소가 승인된 사내 GitHub를 가리키는지 다시 확인
git push -u origin main
```

- 위 `<...>`는 **실제 Clone URL로 치환해야 하는 자리표시자**입니다(그대로 실행 불가).
- 원격이 일반 GitHub.com이라면 GHES가 아닌지, 회사가 해당 Enterprise Cloud 업로드를 승인했는지 먼저 확인합니다.
- `git push`가 인증/권한/정책 문제로 실패하면 자격증명 보안 설정이나 Branch Rule을 우회하지 말고 IT 담당자에게 문의합니다.

## 4. 초기 업로드 후 저장소 설정

- Settings → Branches/Rulesets에서 `main` 보호: force-push/삭제 금지, 이후 PR 기반 Merge 및 승인된 Reviewers 적용. 초기 커밋을 올린 후 회사 정책에 따라 활성화합니다.
- Issues와 Pull Requests를 활성화하고 제공된 템플릿을 사용합니다.
- 비밀 스캔과 감사 로그는 기업에서 제공하는 허용 기능을 활성화하되, 로그/인덱스가 어디에 저장되는지 확인합니다.
- Release/CI/Runner는 승인 전까지 보류합니다. GitHub에 소스가 올라간 것만으로 사용자 설치용 제품이 배포된 것은 아닙니다.

## 5. 후속 개발 작업 예시

```powershell
git switch -c feat/local-workspace-editor
# 변경 후 검증 및 테스트
python -m pytest -q
git add .
python scripts/check_before_commit.py
git diff --cached --check
git diff --cached
git commit -m "feat(local): introduce structured page editor"
git push -u origin feat/local-workspace-editor
# 웹 UI에서 Pull Request 생성, 승인된 리뷰를 거친 후 Merge
```

## 6. 확인해야 할 사항

- [확인 필요] GitHub Enterprise Server vs Enterprise Cloud / 승인된 호스트 및 API 접근 방식
- [확인 필요] 개인 Private 저장소 생성 허용 / 부서 내 공유 정책
- [확인 필요] Git CLI 설치와 SSH/HTTPS 인증 방법
- [확인 필요] Branch Protection/PR Review/Runner 실행 권한
- [확인 필요] 외부 AI-assisted 소스코드의 회사 내부 반입·사용·유지보수 승인

### 참고
- GitHub 공식 저장소 생성: https://docs.github.com/en/enterprise-cloud@latest/repositories/creating-and-managing-repositories/creating-a-new-repository
- GitHub 인증 방식: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github
- GitHub 브랜치 보호: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
