# Development Roadmap — v0.9

## 현재 구현됨 (Synthetic-only PoC)

- [x] 80종 독자 Template Catalog + 검색/필터
- [x] Getting Started + Home Dashboard
- [x] 로컬 문서 SQLite CRUD + Revision
- [x] Page Tree + parent move + cycle guard
- [x] Projects + Task Database Table/Board + 문서 링크
- [x] Calendar 월/주/일 + 종일/시간 일정 생성/수정 + Task 마감일 투영
- [x] 이전 로컬 DB Migration 및 기본 보안 회귀 테스트
- [ ] Windows 11 E2E 테스트와 의존성 라이선스 검토
- [ ] 작업 브랜치와 테스트 결과를 PR로 검토

## 다음 PR 순서

| PR | 범위 | Acceptance Gate |
|---|---|---|
| PR-01 | v0.9 코어/테스트/문서 GitHub 반영 | 대상 저장소와 변경 내용 검토 |
| PR-02 | Migration 관리 및 데이터 무결성/복구 프로토타입 | 기존 데이터 보존·롤백 시나리오·백업 정책 검토 |
| PR-03 | Rich Block Editor(Tiptap OSS) + Page Tree UX 개선 | 의존성 호환성·라이선스 확인, sanitize/텍스트 검증, 자동 저장 충돌 대응 |
| PR-04 | 사용자 정의 Database Properties + Table/Board/Calendar View 계약 | 필드 변경 Migration, Relation/Formula는 보류 |
| PR-05 | Calendar 반복 일정·시간대·Task 연계 강화 | RFC5545 기반 독자 구현, DST 경계·권한 테스트 |
| PR-06 | Central Teamspace/SSO/ACL/RBAC + Publish Copy PoC | 별도 서버 환경 확인, 인증·인가·검색 비노출·감사 로그 통과 |
| PR-07 | Yjs 실시간 협업 + 공유 문서 버전 복구 | 중복/충돌/권한 철회/네트워크 장애 검증 |
| PR-08 | 승인된 내부 AI/RAG/Automation | 출처·권한·프롬프트 인젝션·평가 게이트 통과 |

미디어·외부 Cloud·임의 파일 업로드·제3자 무단 복제는 기본적으로 개발 대상에서 제외한다.
