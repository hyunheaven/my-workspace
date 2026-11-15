# My AI Workspace v0.12 검증 결과

검증일은 2026년 11월 15일입니다. v0.11 원본 ZIP의 소스와 그 스키마로 만든 합성 SQLite 데이터, 새 합성 데이터로 검증했습니다.

| 검사 | 결과 | 확인한 내용 |
|---|---|---|
| Python `unittest` | 8건 통과, 152종 템플릿 하위 검사 포함 | 모든 템플릿을 편집 가능한 페이지로 생성, 템플릿 원본 보존, 중복 생성 및 오래된 리비전 충돌 처리, 쓰기 오류 시 롤백, 페이지 500개를 넘는 트리, 입력 검증. |
| 이전 버전 회귀 검사 | 26건 통과 | 기존 테스트 함수와 어설션을 로컬 fixture 어댑터에서 실행했습니다. v0.11 원본과 최종 v0.12에서 모두 통과했습니다. |
| SQLite 마이그레이션 | 통과 | v0.11 문서와 필드값, 페이지 계층·블록, 업무·프로젝트·일정 링크 보존. 재시작 후 저장과 이력 유지. `integrity_check` 결과 `ok`, `foreign_key_check` 결과 0건. |
| 실제 Chromium 브라우저 | 통과 | 템플릿 두 번 클릭 → 페이지 1건 → 편집기로 이동 및 트리 등록 → 제목·표·체크리스트 수정 → `/h2`로 소제목 삽입 → 자동 저장 → 초기 리비전 확인. 서버를 종료하고 동일 DB로 재실행한 후 페이지 재열기, 이동 직전 편집 자동 저장, 문서·프로젝트·업무 표/보드·캘린더 동작을 확인했습니다. |
| 공유 데스크톱 Chromium | 통과 | 별도 합성 DB에서 원클릭 생성, 제목·표·체크리스트 편집, 이력 확인, 브라우저 새로고침 뒤 편집 상태 유지. |
| 독립 보안 검토 | 통과 | 루프백·Host·Origin·요청 마커·콘텐츠 유형 제한, 외부 서비스용 경로 부재, 텍스트 렌더링, 캐시 제한. 브라우저가 기록한 15개 요청 URL은 모두 테스트 서버의 루프백 주소였고 미처리 페이지 오류는 0건이었습니다. |

## 실행 환경 및 범위

- Linux, Python 3.12.14, SQLite 3.53.1, Chromium 156.0.8078.79, Playwright 1.62.0.
- 기존 런타임 FastAPI 0.141.1, Uvicorn 0.52.1, Pydantic 2.13.4, HTTPX 0.28.1 사용. 이 환경에 pytest가 없었으며 공개 PyPI에서 테스트 의존성을 설치하는 작업은 승인된 미러 또는 오프라인 wheel 사용 기준에 따라 자동 검토에서 거부됐습니다. 기존 26개 검사는 fixture 어댑터에서 실행했습니다.
- Windows 11 실기, `requirements-dev.txt` 고정 버전 조합, 회사 승인 환경의 DLP·App Control·백업 운영은 확인이 필요합니다. 이력에는 편집 이전 텍스트가 보관되며 자동 정리 정책은 후속 과제입니다. 로컬 서버는 동일 OS 사용자 프로세스를 별도 인증하지 않습니다.

## 다시 실행하기

앱과 테스트에 필요한 승인 패키지를 준비한 후 소스 루트에서 실행합니다.

```shell
python -m pytest -q
python -m unittest discover -s tests -p test_template_pages_v012.py -v
python tests/browser/workspace_v012.py --chromium "/path/to/chromium" --screenshots ./qa-screenshots
```

브라우저 검사는 Playwright와 로컬에 설치된 Chromium 또는 Chromium 기반 브라우저 실행 파일을 사용합니다. 임시 DB와 별도 루프백 포트를 사용합니다. Windows 11 실행과 기존 DB 복사 절차는 [실행 가이드](../RUN_LOCAL.md)를 참고하세요.

## 검증 화면

| 화면 | 캡처 |
|---|---|
| 152종 템플릿 갤러리 | [01-template-gallery.png](evidence/01-template-gallery.png) |
| 빈 문단의 블록 명령 | [02-slash-command.png](evidence/02-slash-command.png) |
| 편집 및 자동 저장이 완료된 Project Plan | [03-edited-page.png](evidence/03-edited-page.png) |
| 초기 리비전 조회 | [04-page-history.png](evidence/04-page-history.png) |
