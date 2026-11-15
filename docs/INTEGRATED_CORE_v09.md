# Integrated Local Core v0.9 — 아키텍처 및 변경 명세

## 0. 구현 상태 및 경계

실행됨: `Browser (localhost)` → `FastAPI (loopback only)` → `SQLite (%LOCALAPPDATA%)`. 서버가 외부 서비스에 호출하는 작업 없음. Local Private 자료의 중앙 업로드/동기화 기능 없음. 실제 Shared Workspace는 설계만 유지.

## 1. 주요 워크플로

1. **템플릿 → 문서:** 기존 80종 중 선택 → 필수 필드 입력 → SQLite 저장 → Page Tree의 Root 또는 선택한 Parent에 배치.
2. **문서 계층:** Document 자체가 Page 역할. `documents.parent_id` nullable FK. 이동은 `expected_revision` 검사 후 변경. 자기 자신·하위 페이지를 상위로 삼는 순환 거부.
3. **프로젝트 → Task:** Project에 여러 Task 연결. Task는 프로젝트 없이도 존재하며 단일 문서(`document_id`)에 연결 가능. Task 생성/수정은 단일 Source of Truth.
4. **Task Database View:** 하나의 `tasks` 테이블을 Table/Board로 투영. Status·Priority·Due On·Document Link를 사용. 컬럼 사용자 정의/관계형 DB 기능은 미지원.
5. **Calendar:** `calendar_events` 저장 + `tasks.due_on` 조회 Projection을 합쳐 월/주/일 표시. Task Due Date는 Event Table에 중복 입력하지 않음. 일정은 로컬 전용.
6. **Home Dashboard:** 로컬 API로 문서/프로젝트/미완료 Task 수, 향후 2주간 일정 표시. 대시보드에 별도 저장하지 않음.

## 2. 데이터 모델

- `documents`: 기존 필드 + `parent_id` nullable FK `documents(id)`.
- `projects`: id UUID, title, description, status[planned/active/on_hold/completed], revision, created_at, updated_at.
- `tasks`: id UUID, project_id nullable FK, document_id nullable FK, title, status[todo/in_progress/blocked/done/archived], priority[low/medium/high], due_on nullable YYYY-MM-DD, revision, timestamps.
- `calendar_events`: id UUID, title, start_at, end_at, start_date, end_date, all_day, timezone, document_id, task_id, revision, timestamps.

`start_at/end_at`은 종일 일정에서는 날짜(종료일 **exclusive**), 시간 일정에서는 UTC ISO 8601 시각. `start_date/end_date`는 해당 일정의 시간대 달력 날짜 범위이고, 종료일은 exclusive. UI는 종일 종료일을 포함 표시로 보여주고 API로 보낼 때 +1일 처리합니다.

현 UI 기본 시간대는 **Asia/Seoul**입니다. 일자 검색은 화면상 이 시간대를 기준으로 합니다. Windows 환경에 IANA 시간대 DB가 없으면 `Asia/Seoul` UTC+09:00 fallback을 사용하며, 과거 DST/향후 법 개정까지 정밀 반영하는 범용 Time Zone Engine은 아닙니다. 다른 IANA Zone 지원에는 승인된 시간대 DB가 필요할 수 있습니다.

## 3. API (로컬 전용)

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/health` | 상태/버전 |
| GET | `/api/v1/templates`, `/api/v1/template-catalog/stats` | 템플릿 검색·통계 |
| GET/POST | `/api/v1/documents` | 문서 조회/생성; 생성에 `parent_id` 지원 |
| GET/PUT | `/api/v1/documents/{id}` | 문서 조회/수정 |
| GET | `/api/v1/pages/tree` | 문서 계층 목록 |
| PUT | `/api/v1/pages/{id}/move` | 상위 페이지 이동 + Revision |
| GET/POST | `/api/v1/projects` | 프로젝트 목록/생성 |
| PUT | `/api/v1/projects/{id}` | 수정 + Revision |
| GET/POST | `/api/v1/tasks` | 업무 목록/생성 |
| GET/PUT | `/api/v1/tasks/{id}` | 업무 조회/수정 + Revision |
| GET | `/api/v1/calendar/feed?start=&end=` | 일정 + 업무 마감일 투영 |
| GET/POST | `/api/v1/calendar/events?start=&end=` | 개인 일정 목록/생성 |
| GET/PUT | `/api/v1/calendar/events/{id}` | 일정 조회/수정 + Revision |

모든 변경 API는 JSON Content-Type + `X-EAW-Request: local-template-editor`와 loopback Host/Origin 검사, 요청 크기 제한을 적용합니다. 동시 변경 시 **409 Conflict**, 참조·날짜 검증 실패 시 **422**.

## 4. 보안과 미구현 사항

- 음성·영상·캡처·미디어·임의 파일 첨부·외부 웹 자산·인쇄용 Export·클라우드·Webhook 엔드포인트 없음.
- 텍스트는 `textContent`로 출력해 임의 HTML 실행을 피함; 요청 데이터는 Pydantic(추가 필드 거부) 및 SQLite 바인딩으로 처리.
- `Cache-Control: no-store`, CSP(이미지/미디어/iframe 차단), 마이크·카메라 차단 헤더를 유지.
- **미구현:** 다중 사용자 인증, 데이터 암호화, 파일 보호·OS DLP, 서버 RBAC/ACL, 백업/복원, 감사 로그, SSRF 차단(외부 호출 API가 없음).
- 로컬 프로세스가 가진 권한으로 DB 파일을 접근하는 다른 프로그램의 위험은 회사 Endpoint 정책이 관리해야 함.

## 5. 검증 / 품질

- 기존 v0.8 회귀 테스트 + 신규 API/DB 통합 테스트: `tests/test_integrated_workspace_v09.py`.
- 기존 SQLite 문서 → 새 계층 컬럼 추가 후 보존 테스트.
- 변경 충돌/계층 순환/존재하지 않는 참조/잘못된 날짜/외부 Origin/금지 API 부재 테스트.
- Synthetic DOM browser smoke: 페이지 탐색, 80종 로딩, 문서 생성, Page Tree, Project, Task Table/Board, Calendar 일정/마감일. 정책상 브라우저 직접 URL 탐색이 제한된 테스트 환경에서는 DOM + in-process FastAPI bridge 검증으로 대체했으며 실제 Windows Chrome/Edge E2E는 **미검증**.
