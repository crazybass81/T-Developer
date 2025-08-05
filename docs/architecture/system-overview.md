# T-Developer MVP 시스템 아키텍처

## 개요
T-Developer MVP는 Agno Framework + AWS Agent Squad + Bedrock AgentCore 기반의 AI 멀티 에이전트 개발 플랫폼입니다.

## 9개 핵심 에이전트
1. NL Input Agent - 자연어 입력 처리
2. UI Selection Agent - UI 프레임워크 선택
3. Parser Agent - 코드 파싱 및 분석
4. Component Decision Agent - 컴포넌트 결정
5. Match Rate Agent - 매칭률 계산
6. Search Agent - 컴포넌트 검색
7. Generation Agent - 코드 생성
8. Assembly Agent - 서비스 조립
9. Download Agent - 프로젝트 패키징

## 아키텍처 다이어그램
```
Web Interface → Agent Squad → Agno Framework → Bedrock AgentCore
```