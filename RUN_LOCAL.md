# My Workspace v1.3.0 Windows 11 실행 가이드

## 새 환경에서 실행

1. Python 3.11 이상이 설치되어 있는지 PowerShell에서 `py -3 --version`으로 확인합니다.
2. 기존 버전 서버가 실행 중이면 해당 터미널에서 `Ctrl+C`로 종료합니다.
3. 작업 브랜치의 프로젝트 루트에서 아래 명령을 실행합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-dev.txt
$env:EAW_DATA_DIR = Join-Path $env:LOCALAPPDATA ('MyWorkspace-v130-test-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m services.local_api.run
```

Edge 또는 Chrome에서 [My Workspace](http://127.0.0.1:8765/)를 엽니다. 앱 실행 주소는 `127.0.0.1:8765`입니다. 서버 종료는 실행한 터미널에서 `Ctrl+C`를 누릅니다. 기본 DB 경로는 `%LOCALAPPDATA%\EnterpriseAIWorkspace\workspace.db`이며 `EAW_DATA_DIR`를 지정하면 해당 폴더의 `workspace.db`를 사용합니다.

My Workspace는 이전 버전과 같은 기본 DB 경로를 사용합니다. 기존에 EAW_DATA_DIR을 설정했다면 같은 값을 사용하세요.

## 이전 버전 데이터 복사본으로 검증하기

1. 두 버전의 서버를 모두 종료합니다. 기존 실행 때 `EAW_DATA_DIR`를 지정했다면 아래 `$oldDataDir`을 실제 경로로 바꿉니다.
2. v1.3.0의 프로젝트 루트에서 아래 명령을 실행합니다. SQLite Backup API로 읽기 전용 원본의 커밋 데이터를 복사하고 복사본의 무결성을 검사합니다.

```powershell
$oldDataDir = Join-Path $env:LOCALAPPDATA 'EnterpriseAIWorkspace'
$oldDb = Join-Path $oldDataDir 'workspace.db'
$testDir = Join-Path $env:LOCALAPPDATA ('MyWorkspace-v130-upgrade-' + [guid]::NewGuid().ToString('N'))
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

3. v1.3.0은 시작 시 복사본에 스키마를 추가합니다. 기존 페이지·프로젝트·업무·캘린더와 사용자 정의 데이터베이스의 레코드·연결된 보기를 확인합니다.
4. 이전에 사용하던 Edge 또는 Chrome의 동일 프로필에서 같은 주소와 포트를 열면 브라우저에 저장된 즐겨찾기·탭·테마를 확인할 수 있습니다. 같은 주소를 쓰는 테스트에서도 브라우저 설정은 공유되므로, 독립 검증에는 별도 브라우저 프로필을 사용합니다.

롤백할 경우 v1.3.0을 종료하고 이전 버전을 원래 DB 또는 업데이트 전 백업 경로로 실행합니다. v1.3.0에서 DB 복사본에 저장한 작업은 그 복사본에 남습니다. 레코드와 보기의 변경 이력은 v1.3부터 기록합니다. 롤백은 업데이트 전 DB를 기준으로 진행하세요.

## 주요 기능 확인

| 기능 | 사용 방법 |
|---|---|
| 중첩·다중 블록 | 블록 도구에서 들여쓰기와 내어쓰기를 선택합니다. 왼쪽 블록 손잡이를 끌어 묶음을 이동합니다. 손잡이를 클릭한 뒤 Shift와 방향키로 범위를 선택하고 Ctrl+C 및 Ctrl+V를 사용합니다. |
| 사용자 정의 데이터베이스 | 사이드바 **내 데이터베이스**에서 데이터베이스를 만들고 속성·레코드·보기를 추가합니다. 타임라인과 캘린더는 날짜 속성, 보드는 그룹으로 쓸 선택 또는 체크박스 속성이 필요합니다. |
| 페이지에 보기 연결 | 페이지 아래 **보기 연결**에서 데이터베이스와 저장된 보기를 선택합니다. 연결된 보기에서 레코드를 누르면 원본 편집 창이 열립니다. |
| 레코드·보기 변경 이력 | 레코드 편집 또는 보기 설정의 **변경 이력**을 엽니다. 이전 버전을 선택해 현재 저장본과 비교하고 **이 버전 복원**을 누릅니다. |
| Markdown | 상단 **Markdown 가져오기**로 UTF-8 파일 또는 텍스트에서 새 페이지를 만들고, 페이지 도구의 **Markdown 저장**으로 파일을 내려받습니다. |
| CSV | **내 데이터베이스**에서 기존 스키마에 맞춰 가져오거나 해당 데이터베이스의 기본 속성을 저장합니다. 제목 열은 필수이며 메모 열은 선택입니다. 1회 최대 100행까지 가져옵니다. |

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
| 보드에서 카드 상태를 바꾸고 업무 캘린더에서 날짜 이동 | 표에서 같은 업무의 상태와 마감일이 함께 갱신됩니다. 업무 제목을 눌러 메모를 작성할 수 있습니다. |
| 페이지 링크 복사 → 제목 변경 → 상위 페이지 변경 | 복사했던 링크로 원래 페이지가 열립니다. `Ctrl+K`로 찾고, 휴지통 이동 및 복원 후 링크를 다시 엽니다. |
| 편집 중 서버 정지 → 초안 입력 → 서버 재시작 → 동일 탭에서 새로고침 | 복구 안내가 나타납니다. 저장 버튼으로 반영한 뒤 다시 열어 저장 여부를 확인합니다. |

Windows 11 실기에서는 **Microsoft 한글 IME**로 단어와 받침을 조합하며 커서 이동, Enter, 제목과 표 셀 입력을 확인합니다. 긴 한국어 문서에서 입력 반응과 저장 후 복원도 확인합니다. 세 업무 뷰의 드래그, 키보드 대체 경로, 완료 및 날짜 미지정 업무, 고대비와 탭 색상도 점검합니다.

[자동 검증 범위와 후속 기능](docs/RELEASE_v130.md)
