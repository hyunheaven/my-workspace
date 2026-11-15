# My Workspace v1.0.0

초기 개발을 마무리한 Windows 11용 로컬 작업 공간입니다. 템플릿을 선택하면 바로 편집할 수 있는 새 페이지가 열립니다.

- **템플릿 라이브러리** — 기존 152종과 새로 작성한 120종, 총 272종. 미리보기, 추천, 인기 주제, 컬렉션·태그 검색, 즐겨찾기.
- **페이지 편집** — 인라인 편집, 표, 체크리스트, `/` 명령, 자동 저장, 복제, 이력 복원, 페이지 즐겨찾기와 최근 목록.
- **문서 검색** — 제목, 본문, 표 셀, 기존 템플릿 입력값을 검색합니다.
- **테마** — 색상 10종과 배경 10종. 페이지별 색상·배경, 페이지 탭과 사이드바 메뉴 색상을 각각 선택할 수 있습니다.
- **페이지 태그** — 문서마다 태그를 추가·삭제하고 태그를 눌러 관련 문서를 필터링합니다.
- **업무 관리** — 페이지 트리, 프로젝트, 업무 표·보드 및 개인 캘린더.

## Windows에서 시작

ZIP을 새 폴더에 풀고 PowerShell에서 프로젝트 루트로 이동합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-dev.txt
$env:EAW_DATA_DIR = Join-Path $env:LOCALAPPDATA 'MyAIWorkspace-v100-test'
.\.venv\Scripts\python.exe -m services.local_api.run
```

[앱 열기](http://127.0.0.1:8765/)

- [Windows 실행 및 기존 DB 복사본으로 검증](RUN_LOCAL.md)
- [변경 사항, 참고 자료 및 검증 결과](docs/RELEASE_v100.md)
- [개발 계획](PROJECT_PLAN.md)

회사 관리 PC에서는 승인된 패키지 설치 경로를 사용하세요. 사내 실사용 승인 전에는 합성 데이터로 검증합니다.
