# My AI Workspace v1.0.0 첫 정식 릴리스

우측 상단 **테마 → 워크스페이스 색상 → 고대비**를 선택합니다. 현재 페이지 설정에서도 고대비를 개별적으로 쓸 수 있습니다. 검은 바탕, 밝은 텍스트, 노란색 주요 버튼과 청록색 키보드 포커스를 사용합니다.

v0.15 개발판의 기능을 그대로 사용합니다. v1.0.0은 첫 정식 배포용 버전 번호입니다.

## Windows 실행

[Windows 실행 가이드](../RUN_LOCAL.md)에 따라 ZIP을 새 폴더에 풉니다. 처음 실행할 때 Python 가상환경과 의존성을 설치합니다. v0.15 데이터가 필요하면 별도 SQLite 복사본을 만듭니다.

## GitHub 배포 준비

Windows용 ZIP을 GitHub Release로 배포할 수 있습니다. 대상 저장소의 Clone URL과 공개 범위를 확인합니다. 저장소에는 실행용 소스, 문서와 합성 테스트를 올립니다. ZIP은 Release 자산으로 따로 첨부합니다.

### 빈 원격 저장소

Git bundle과 Windows ZIP을 같은 위치에 내려받은 후, 그 위치에서 다음 명령을 실행합니다. Clone URL은 대상 저장소의 Code 화면에서 복사합니다.

```powershell
git clone -b main .\My_AI_Workspace_v1.0.0.bundle .\My_AI_Workspace
Set-Location .\My_AI_Workspace
git log -2 --oneline
git remote set-url origin (Read-Host '대상 저장소의 Clone URL')
git remote -v
git ls-remote --refs origin
```

`git ls-remote`가 성공하고 ref 출력이 비어 있으면 아래 명령으로 브랜치와 태그를 함께 올립니다.

```powershell
git push --atomic -u origin main refs/tags/v1.0.0
```

기존 커밋이나 태그가 있는 원격은 기본 브랜치의 커밋을 확인한 뒤 그 브랜치에서 작업 브랜치와 PR을 만듭니다. 로컬 번들은 배포 ZIP을 기반으로 구성한 첫 정식 릴리스 이전 개발 이력을 포함합니다.

### Windows ZIP 첨부

브랜치와 태그가 원격에 올라간 뒤 GitHub에서 **Releases → Draft a new release**를 엽니다. 기존 태그 `v1.0.0`을 선택하고 `My_AI_Workspace_v1.0.0_Windows11.zip`을 첨부해 초안을 확인합니다. GitHub CLI를 쓸 때도 기존 태그를 검증하는 옵션을 사용할 수 있습니다. [GitHub CLI Release 명령](https://cli.github.com/manual/gh_release_create)

## 검증

Windows 11 실기 검증은 남아 있습니다. ZIP의 `docs/evidence-v015/`에는 동일 기능의 v0.15 개발판에서 촬영한 Linux 브라우저 검증 화면이 있습니다.

- Linux Chromium에서 고대비 색상을 앱 전체 및 개별 페이지에 적용하고, 새 브라우저 세션에서 페이지 설정이 유지되는 것을 확인했습니다. 템플릿·페이지 편집 회귀 시나리오도 통과했습니다.
- Python unittest 15건과 기존 fixture 어댑터 검사 26건을 통과했습니다.
