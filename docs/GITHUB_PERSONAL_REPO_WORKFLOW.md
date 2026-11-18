# My Workspace 로컬 저장소 작업

Windows PowerShell에서 작업합니다.

```powershell
git status --short --branch
git remote -v
git switch -c feat/my-change
```

변경한 파일을 추가한 뒤 검사합니다.

```powershell
python scripts/check_before_commit.py
git diff --cached --check
git diff --cached
```

검토 후 커밋하고, 원격 반영이 필요하면 대상 저장소와 공개 범위를 확인한 뒤 작업 브랜치로 PR을 엽니다. 앱 실행과 기존 DB 복사본 검증은 [로컬 실행 가이드](../RUN_LOCAL.md)를 참고합니다.
