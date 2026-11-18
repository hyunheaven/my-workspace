# My AI Workspace v0.11 — UI 및 템플릿 설계

## 변경 요약
- **제품명:** My AI Workspace. 기존 SQLite DB 경로는 이전 문서 호환을 위해 변경하지 않음.
- **정보 구조:** 밝은 Sidebar, 개인 페이지 트리, 상단 Breadcrumb, 중앙 Page Canvas.
- **블록 사용성:** 9종 안전한 블록, `+` 버튼, `⋮⋮` 메뉴, 빈 문단 `/` 메뉴, 수동 저장 및 조심스러운 자동 저장.
- **Template Library:** 기존 80종 + 독자적으로 작성한 72종 = **152종**. 15개 부서/분야. 추천/인기 분야 기반 분류와 검색 필터.
- **권한·보안:** Local SQLite 개인 데이터만 사용. 기존 API, 문서 ID, 템플릿 ID, DB 파일 위치 유지.

## Notion Marketplace 조사 범위
공식 무료 업무·프로젝트·회의·엔터프라이즈 카테고리, 추천/인기 카테고리의 **업무 목적**을 검토했으나, 페이지 본문·템플릿 원문·스크린샷·디자인 자산·브랜딩은 가져오지 않았음.

참고: https://www.notion.com/ko/templates
https://www.notion.com/ko/templates/category/free-work-templates
https://www.notion.com/ko/templates/category/free-projects-templates
https://www.notion.com/ko/templates/category/free-meetings-templates
https://www.notion.com/help/intro-to-workspaces

**주의:** `recommended`는 이 앱에서 직접 선별한 추천, `popular_category`는 공식 마켓플레이스에서 자주 보이는 범주를 참고한 자체 분류다. 외부 마켓플레이스의 정량적 인기 순위를 의미하지 않는다.

## 미구현
- Tiptap/ProseMirror Rich Text, Inline Database, 실제 Drag & Drop, 블록 간 선택 및 붙여넣기, 문서 History/Restore, 동시 편집·SSO·중앙 검색·AI.
- 'Notion과 똑같은 화면'은 목표가 아니며, 동일한 문제를 해결하는 **독자적인 디자인**을 유지한다.
- 외부 API·녹음·화상회의·첨부·외부 임베드·외부 네트워크 데이터 전송.

## 로컬 검증
- 현재 소스는 외부 공개 대상이 아니며 개인 PC에서 합성 데이터만 사용한다.
- Windows 11 로컬 E2E와 패키지 호환성, 라이선스를 확인합니다.
