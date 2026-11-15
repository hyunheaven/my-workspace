## v0.8 템플릿 공급망 정책
- 무료 Notion 템플릿 전체 복제/전재/재배포는 기능 범위 밖이며 권한이 확인되지 않음.
- UI에는 허용된 고정 원본 템플릿만 포함. 외부 Marketplace 자동 접근, 페이지 임베드, 링크 미리보기, 이미지/오디오/동영상 첨부 기능을 구현하지 않음.
- 기업 내부 라이선스·저작권 승인 전 제3자 템플릿 추가 금지. 검토되지 않은 외부 링크를 런타임에 여는 기능도 금지.

# Security Feature Allowlist / Denylist — v0.5

## 원칙
- 민감 자료 유출 가능성을 **0**으로 보장하지 않는다. UI 숨김과 정책 문서만으로는 DLP가 성립하지 않는다.
- 초기 실행형 PoC는 Local Private 모드이고, 공유/API/임베드/AI/미디어 라우트가 존재하지 않는다.
- 기능 추가는 `Security Review + Threat Model + Test + Human Approval` 절차 통과 필요.

## Allowlist (현재 구현)
- 승인된 내부 고정 Template Catalog 읽기 및 필터
- 텍스트/선택 입력값의 로컬 SQLite 저장, 문서 목록·조회·Revision 충돌 검증
- 부서/직무군/직무별 검색 및 구체적 업무 기록

## Denylist (현재 API 미구현)
- 오디오 녹음·업로드·재생·편집, 마이크 접근
- 비디오 촬영·업로드·재생·편집, 카메라·화면캡처 API
- 외부 URL 임베드, iframe, 스크립트, 사용자 정의 HTML, CDN
- 파일 업로드/첨부·자동 링크 미리보기·외부 이미지·파일 변환
- 이메일/Webhook/API Connector, 외부 LLM, Cloud AI, 외부 Analytics/Telemetry
- 문서 Export, 대량 Download, 자동 동기화, 로컬 문서 자동 Publish
- Dynamic template package installation, arbitrary script/macros

## 후속 Shared Workspace 보안 게이트
- 중앙 SSO/OIDC, 권한 기반 Teamspace, 서버 RBAC+ACL, Resource-level authorization 및 Search filtering
- `Local PRIVATE → Shared` 전환은 사용자의 명시적 Publish + 대상 + 민감도/분류 검토 + Confirm + Audit
- **기밀 자료 분류 정책**: 회사 승인 이전 기밀/고객/개인정보 사용 금지; 추후 DLP 분류·공유 가능 등급은 회사 정책으로 정의
- 위험도 높은 기능의 클라이언트 표시 여부와 관계없이 Backend/API/Worker에서 우회 방지

## 잔여 위험과 회사 통제 필요
1. Windows 사용자의 로컬 SQLite DB 직접 열람 또는 복사
2. OS/브라우저의 스크린샷, 인쇄, 클립보드, 접근성 API
3. 로컬 악성 코드·관리자 권한·물리적 데이터 유출
4. 사내 GitHub 코드·Issue·첨부·Log·Actions·AI 도구를 통한 정보 유출
5. 화면 표시에 따른 육안 노출, 정상 권한 보유 사용자의 오용

→ 회사 DLP/EDR, BitLocker, OS 계정/ACL, App Control, 코드 서명, 프록시/Firewall, 감사·백업/복구 정책 필요. 브라우저 보안 헤더로 운영체제 유출 경로까지 차단한다고 주장하면 안 된다.

## 참조
- OWASP ASVS 5.0: https://asvs.owasp.org/
- Microsoft App Control for Business: https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/wdac-and-applocker-overview
- Tiptap OSS: https://tiptap.dev/docs/editor/getting-started/overview

## v0.9 구현 범위 추가
- Local Page Tree, Project/Task Database, Personal Calendar 및 Dashboard는 **로컬 SQLite 데이터만** 처리하고 외부 전송 기능을 추가하지 않는다.
- Calendar Event와 Task의 문서 연결은 로컬 데이터 참조만 허용하며 미디어·외부 예약 링크·외부 Calendar Sync·ICS Export는 제공하지 않는다.
- 동일 사용자 환경의 localhost API·SQLite가 고도의 기밀 데이터 DLP를 보장하지는 않는다. 실제 사내 데이터 도입 전 OS/회사 정책 검토 필수.
- Shared Server/SSO/AI/RAG 및 사용자별 권한·감사 로그는 현재 구현 범위 밖이다.
