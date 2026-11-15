# GitHub Enterprise Environment Check — v0.5

**상태:** GHES vs GHEC 아직 미확인. 이 문서는 회사의 어떤 내부 URL/계정/토큰도 요청하거나 기록하지 않는다.

1. 사내 GitHub 관리자 또는 IT 담당자에게 관리형 환경(GitHub Enterprise Server / GitHub Enterprise Cloud), 사내 AI 도구 접근 허용 범위 및 저장소 생성 권한 확인.
2. 회사 보안 정책에 따른 Private/Internal 가시성, SSO, 코드 리뷰, Branch Protection/Rulesets, Secret Scanning, Self-hosted Runner의 허용 범위 확인.
3. GitHub Enterprise Cloud인 경우 GitHub.com에 호스팅되는 외부 Cloud라는 점을 구별하고, 소스코드 전송 승인 필요성을 별도로 점검.
4. 저장소에는 합성 테스트 데이터, 코드, 공개 가능한 개발 문서만 등록. 실제 업무 문서, 로컬 SQLite, 첨부파일, 인증키/Token, 개인 정보 금지.
5. GitHub Actions/외부 Marketplace Actions는 정책 승인 전 비활성화. 로컬 테스트 후 수동 리뷰.
6. 승인 전 프로젝트 패키지를 사내 GitHub에 자동으로 Push하지 않는다.

공식 문서:
- https://docs.github.com/ko/enterprise-cloud@latest/get-started/learning-about-github/githubs-plans
- https://docs.github.com/en/enterprise-server@3.20/admin/concepts/enterprise-best-practices/use-innersource
