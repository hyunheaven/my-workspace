# My AI Workspace v0.15 Windows 11 실행 가이드

## 새 환경에서 실행

1. Python 3.11 이상이 설치되어 있는지 PowerShell에서 `py -3 --version`으로 확인합니다.
2. ZIP을 기존 v0.14와 별도의 폴더에 풉니다. v0.14 서버가 실행 중이면 해당 터미널에서 `Ctrl+C`로 종료합니다.
3. v0.15 소스 폴더에서 아래 명령을 실행합니다. 회사 관리 PC에서는 반입 승인 후 승인된 패키지 미러 또는 오프라인 wheel을 사용합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-dev.txt
$env:EAW_DATA_DIR = Join-Path $env:LOCALAPPDATA 'MyAIWorkspace-v015-test'
.\.venv\Scripts\python.exe -m services.local_api.run
```

Edge 또는 Chrome에서 [My AI Workspace](http://127.0.0.1:8765/)를 엽니다. 앱 실행 주소는 `127.0.0.1:8765`입니다. 서버 종료는 실행한 터미널에서 `Ctrl+C`를 누릅니다. 기본 DB 경로는 `%LOCALAPPDATA%\EnterpriseAIWorkspace\workspace.db`이며 `EAW_DATA_DIR`를 지정하면 해당 폴더의 `workspace.db`를 사용합니다.

## v0.14 데이터로 검증하기

1. v0.14와 v0.15 서버를 모두 종료합니다. v0.14에서 `EAW_DATA_DIR`를 지정한 경우 아래 `$oldDataDir`을 그때 사용한 경로로 바꿉니다.
2. v0.15 폴더에서 아래 명령을 실행해 별도의 SQLite 복사본을 만듭니다. 이 과정은 원본을 읽기 전용으로 열고 SQLite Backup API로 커밋된 데이터를 옮긴 뒤 복사본의 무결성을 검사합니다.

```powershell
$oldDataDir = Join-Path $env:LOCALAPPDATA 'EnterpriseAIWorkspace'
$oldDb = Join-Path $oldDataDir 'workspace.db'
$testDir = Join-Path $env:LOCALAPPDATA ('MyAIWorkspace-v015-upgrade-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testDir -ErrorAction Stop | Out-Null
$testDb = Join-Path $testDir 'workspace.db'

@'
from contextlib import closing
from pathlib import Path
import sqlite3
import sys

source = Path(sys.argv[1]).resolve(strict=True)
target = Path(sys.argv[2]).resolve()
with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as old:
    with closing(sqlite3.connect(target)) as backup:
        old.backup(backup)
        if backup.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise SystemExit("SQLite integrity check failed.")
        if backup.execute("PRAGMA foreign_key_check").fetchone():
            raise SystemExit("SQLite foreign key check failed.")
print("Verified SQLite backup:", target)
'@ | .\.venv\Scripts\python.exe - $oldDb $testDb

if ($LASTEXITCODE -ne 0) {
    throw 'SQLite 복사본 검사에 실패했습니다. 원본 경로와 오류를 확인하세요.'
}

$env:EAW_DATA_DIR = $testDir
.\.venv\Scripts\python.exe -m services.local_api.run
```

3. v0.15 시작 시 복사본에 마이그레이션을 적용합니다. 브라우저에서 기존 페이지의 제목·본문·상하 관계와 프로젝트, 업무, 캘린더 항목을 확인합니다.
4. 템플릿 페이지를 생성하고 제목·본문·체크박스·표 셀을 수정한 뒤 저장 완료 상태를 확인합니다. 같은 `EAW_DATA_DIR`로 서버를 재시작하고 페이지를 다시 열어 보존 여부를 확인합니다.

v0.14로 돌아갈 경우 v0.15를 종료하고 v0.14 소스에서 기존 DB 경로를 다시 지정하여 실행합니다. v0.15 복사본에서 새로 저장한 변경사항은 v0.14 원본과 별도로 보관됩니다.

## 핵심 사용자 흐름

| 동작 | 확인할 결과 |
|---|---|
| 템플릿 라이브러리에서 Project Plan 또는 새 템플릿 선택 | 페이지가 생성되어 왼쪽 트리에 표시됩니다. 미리보기에서 구성도 확인할 수 있습니다. |
| 페이지 제목, 본문, 체크리스트 및 표 수정 | 저장 상태가 바뀌고 페이지를 다시 열어도 편집값이 표시됩니다. |
| 빈 문단에서 `/` 입력 | 블록 유형을 선택할 수 있습니다. 방향키로 이동하고 `Enter`로 선택하며 `Esc`로 닫습니다. |
| `Enter`, `Shift+Enter`, `Ctrl+S` | 일반 텍스트는 새 블록 또는 같은 블록 내 줄바꿈으로 편집할 수 있고, 단축키로 즉시 저장할 수 있습니다. |
| 페이지 이력 열기 | 저장 내용을 확인하고 선택한 버전을 새 리비전으로 복원합니다. |
| 상단 테마 열기 | 앱의 색상과 새 페이지 기본 배경, 현재 페이지의 색상·배경·탭 색상, 사이드바 메뉴 색상을 각각 선택합니다. |
| 페이지에 태그 추가 | 제목 아래 태그를 입력하고 추가합니다. 태그를 누르면 해당 태그가 있는 페이지를 찾습니다. |
| 기존 메뉴 기능 확인 | 문서 목록, 프로젝트, 업무 테이블·보드, 캘린더 및 대시보드가 열립니다. |

브라우저 자동 검증과 Windows 11 실기 검증 상태는 [테스트 결과](docs/RELEASE_v015.md)를 참고합니다.
