## v0.8 실행 구현
- 정적 카탈로그: `services/local_api/catalog.json` 총 **80종** (기존 17, 새 원본 63).
- 새 메타데이터: `section` (`업무` 74, `학습` 3, `개인` 3), `source_type=original`, `redistribution=internal_review_required`.
- 15개 부서/분야, 기존 `department/job_family/job_role` 필터 + 키워드 검색.
- 시작하기(별도 UI 페이지)를 홈에서 제공. 이는 Template 건수에 포함하지 않음.
- 사용자 값은 기존 SQLite로만 저장, 외부 파일·Notion·AI API와 연결되지 않음.
- `/api/v1/templates`는 `section`, `department`, `job_family`, `job_role`, `q` 필터 지원.
- `/api/v1/template-catalog/stats`는 부서/범주별 수를 제공하며 `third_party_imported=0`을 명확하게 보고.
- 각 Template은 검토 전 **구조 예시**이며, 법무·보안 검토 전 외부 배포 및 실제 기밀 활용은 금지.
- 향후 Calendar 업무 템플릿은 실제 Calendar 이벤트와 자동 연동하지 않음 (기능 미구현).

# Template Library Specification — v0.5

## 목적
부서(Department), 직무군(Job Family), 직무(Job Role), 업무 시나리오별 템플릿을 제공한다. 템플릿 자체는 영업비밀을 포함하지 않는 승인된 구조와 도움말만 가진다. 실제 Notion의 유료 템플릿·브랜드·콘텐츠를 재사용하지 않는다.

## 기본 스키마
- `id`: 불변 안정 ID, 재사용 금지
- `version`: 정수, 기존 문서 불변성 및 마이그레이션 근거
- `department`, `job_family`, `job_role`: 다중 조건 검색용 Metadata
- `name`, `description`: 공개 가능한 업무 설명
- `fields`: `id`, `label`, `type`, `required`, `placeholder`, 제한된 `options`
- 초기 허용 유형: `text`, `multiline`, `select`, `date`(필요시 확장)
- 렌더러는 텍스트를 DOM Text Node로만 처리하며 임의 HTML·Script 실행은 금지

## 배포 정책
- P0: 코드 저장소의 고정 카탈로그만 로드; 원격 템플릿 마켓플레이스 및 자동 템플릿 설치 없음
- P1: 내부 승인 관리자만 템플릿을 등록/승인/버전업; 작성자와 승인자 분리; 변경 이력 감사
- P2: 사내 정체성/부서별 승인된 템플릿 노출(서버 인가 필수), 내부 AI 작성 가이드 승인 후 제공
- 템플릿 권한은 문서 권한과 별도: 템플릿 카탈로그 사용 가능하다고 공유 문서를 읽을 권한이 생기지 않음

## 샘플 템플릿
R&D: Experiment Log, Technical Decision Record, Root Cause Analysis, Literature Review.
IT: ADR, Incident Review, API Specification.
Project: Project Plan, Weekly Status Report.
Quality/Manufacturing: CAPA, Process Improvement.
Business/Sales: Requirements Analysis, Account Plan.
Finance/HR: Budget Planning, Onboarding Checklist.
General: Meeting Notes, Work Handover.

## 수용 기준
1. 부서/직무군/직무 필터가 교차 적용되어 해당 템플릿만 보인다.
2. 승인된 필드 외 입력은 Server가 422로 거부한다.
3. 미디어 URL은 Template 필드로 생성되지 않는다(사용자 텍스트에 URL 문자열 입력은 차단 범위 밖).
4. 템플릿 버전이 문서에 기록되고, 문서가 수정돼도 참조 템플릿 ID는 변하지 않는다.
5. 추후 사내 승인 프로세스와 보안 등급별 템플릿 접근을 통합한다.
