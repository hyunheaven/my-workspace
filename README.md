# My Workspace v1.3.0

개인 PC에서 문서, 업무, 일정을 정리하는 로컬 작업 공간입니다. Windows 11을 대상으로 개발했습니다. 템플릿을 선택하면 편집할 수 있는 새 페이지가 열립니다.

- **템플릿 라이브러리** — 기존 152종과 새로 작성한 120종, 총 272종. 미리보기, 추천, 인기 주제, 컬렉션·태그 검색, 즐겨찾기.
- **페이지 편집** — 블록 편집, 표, 체크리스트, 번호 목록, 페이지 링크, `/` 명령, 자동 저장, 초안 복구, 실행 취소·다시 실행.
- **중첩 블록과 파일 교환** — 하위 블록 접기, 여러 블록 선택·복사·붙여넣기, Markdown·CSV 가져오기와 저장.
- **사용자 정의 데이터베이스** — 속성, 관계·롤업·사칙연산 수식, 표·보드·캘린더·타임라인·갤러리, 페이지에 연결된 보기.
- **데이터베이스 변경 이력** — 레코드와 저장된 보기의 변경 내역을 비교하고 이전 버전을 복원합니다.
- **페이지 탐색** — 하위 페이지, 즐겨찾기, 최근 목록, 위치 변경, ID 기반 링크, 휴지통과 복원.
- **문서와 업무 검색** — `Ctrl+K`로 페이지·업무·사용자 정의 데이터베이스와 레코드를 검색합니다.
- **테마** — 색상 10종과 배경 10종. 페이지별 색상·배경, 페이지 탭과 사이드바 메뉴 색상을 각각 선택할 수 있습니다.
- **페이지 태그** — 문서마다 태그를 추가·삭제하고 태그를 눌러 관련 문서를 필터링합니다.
- **업무 관리** — 한 업무 데이터베이스의 표·보드·캘린더, 뷰별 설정, 업무 상세 메모.

## GitHub 저장소 주소

기존 로컬 복제본에서 새 저장소 주소를 사용하려면 프로젝트 루트의 PowerShell에서 실행하세요.

```powershell
git remote set-url origin https://github.com/hyunheaven/my-workspace.git
```

새로 복제할 때는 [My Workspace 저장소](https://github.com/hyunheaven/my-workspace)의 **Code**에서 Clone URL을 복사하세요.

## Windows에서 시작

PowerShell에서 소스의 프로젝트 루트로 이동합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-dev.txt
$env:EAW_DATA_DIR = Join-Path $env:LOCALAPPDATA 'MyWorkspace-v130-test'
.\.venv\Scripts\python.exe -m services.local_api.run
```

[앱 열기](http://127.0.0.1:8766/)

- [Windows 실행 및 기존 DB 복사본으로 검증](RUN_LOCAL.md)
- [v1.3.0 변경 사항과 검증 범위](docs/RELEASE_v130.md)
- [개발 계획](PROJECT_PLAN.md)
