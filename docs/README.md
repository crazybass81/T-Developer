# T-Developer Documentation

## 📚 Documentation Overview

T-Developer는 AWS Agent Squad + Agno Framework + Bedrock AgentCore 기반의 AI 멀티 에이전트 개발 플랫폼입니다.

## 🏗️ Architecture Documentation

### Core Architecture
- [System Architecture](./architecture/system-architecture.md) - 전체 시스템 설계 및 구성요소
- [Multi-Agent Framework](./architecture/multi-agent-framework.md) - 9개 핵심 에이전트 아키텍처
- [Technology Stack](./architecture/technology-stack.md) - Agno + Agent Squad + Bedrock 통합

### Infrastructure
- [AWS Configuration](./deployment/aws-config-setup.md) - AWS 서비스 설정 가이드
- [Infrastructure as Code](./deployment/infrastructure.md) - CDK/Terraform 설정

## 🤖 Agent Documentation

### Core Agents (9개)
- [NL Input Agent](./agents/nl-input-agent.md) - 자연어 입력 처리 (100% 완료)
- [UI Selection Agent](./agents/ui-selection-agent.md) - UI 프레임워크 선택 (100% 완료)
- [Parser Agent](./agents/parser-agent.md) - 코드 파싱 및 분석 (62.5% 완료)
- [Component Decision Agent](./agents/component-decision-agent.md) - 컴포넌트 결정 (50% 완료)
- [Match Rate Agent](./agents/match-rate-agent.md) - 매칭률 계산 (50% 완료)
- [Search Agent](./agents/search-agent.md) - 컴포넌트 검색 (37.5% 완료)
- [Generation Agent](./agents/generation-agent.md) - 코드 생성 (75% 완료)
- [Assembly Agent](./agents/assembly-agent.md) - 서비스 조립 (50% 완료)
- [Download Agent](./agents/download-agent.md) - 프로젝트 패키징 (31.25% 완료)

### Agent Framework
- [Agent Base Classes](./agents/framework/base-classes.md) - 에이전트 기본 클래스
- [Agent Communication](./agents/framework/communication.md) - 에이전트 간 통신
- [Agent Lifecycle](./agents/framework/lifecycle.md) - 에이전트 생명주기 관리

## 🚀 Development Guides

### Getting Started
- [Quick Start Guide](./development/quick-start.md) - 빠른 시작 가이드
- [Development Environment](./development/environment-setup.md) - 개발 환경 설정
- [UV Package Manager](./development/uv-guide.md) - UV 패키지 매니저 사용법

### Development Workflow
- [Coding Standards](./development/coding-standards.md) - 코딩 표준 및 규칙
- [Testing Guide](./development/testing-guide.md) - 테스트 전략 및 실행
- [Migration Guide](./development/migration-guide.md) - pip → uv 마이그레이션

### API Documentation
- [REST API Reference](./api/rest-api.md) - REST API 문서
- [WebSocket API](./api/websocket-api.md) - WebSocket API 문서
- [Agent API](./api/agent-api.md) - 에이전트 API 문서

## 📊 Project Status

### Implementation Progress
- [Implementation Status](./project/implementation-status.md) - 전체 구현 현황 (72.6% 완료)
- [Phase Progress](./project/phase-progress.md) - 단계별 진행 상황
- [Milestone Tracking](./project/milestones.md) - 마일스톤 추적

### Quality Metrics
- **Overall Progress**: 72.6% (63/144 SubTasks 완료)
- **NL Input Agent**: 100% 완료 ✅
- **UI Selection Agent**: 100% 완료 ✅
- **Generation Agent**: 75% 완료
- **Parser Agent**: 62.5% 완료

## 🔧 Deployment & Operations

### Deployment
- [Production Deployment](./deployment/production.md) - 프로덕션 배포 가이드
- [CI/CD Pipeline](./deployment/cicd.md) - 지속적 통합/배포
- [Monitoring & Logging](./deployment/monitoring.md) - 모니터링 및 로깅

### Operations
- [Health Monitoring](./deployment/health-monitoring.md) - 시스템 헬스 모니터링
- [Performance Tuning](./deployment/performance.md) - 성능 최적화
- [Troubleshooting](./deployment/troubleshooting.md) - 문제 해결 가이드

## 🎯 Quick Navigation

### For Developers
1. [Quick Start](./development/quick-start.md) - 개발 시작하기
2. [Agent Framework](./agents/framework/base-classes.md) - 에이전트 개발
3. [Testing Guide](./development/testing-guide.md) - 테스트 작성

### For DevOps
1. [AWS Setup](./deployment/aws-config-setup.md) - AWS 환경 설정
2. [Infrastructure](./deployment/infrastructure.md) - 인프라 구성
3. [Monitoring](./deployment/monitoring.md) - 모니터링 설정

### For Architects
1. [System Architecture](./architecture/system-architecture.md) - 시스템 아키텍처
2. [Multi-Agent Design](./architecture/multi-agent-framework.md) - 멀티 에이전트 설계
3. [Technology Integration](./architecture/technology-stack.md) - 기술 스택 통합

## 🔗 External Resources

- [Agno Framework Documentation](https://agno.com/docs)
- [AWS Agent Squad GitHub](https://github.com/aws-samples/agent-squad)
- [AWS Bedrock AgentCore](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)

## 📞 Support & Contributing

### Getting Help
- Check the [Troubleshooting Guide](./deployment/troubleshooting.md)
- Review [Implementation Status](./project/implementation-status.md)
- Consult the [Testing Guide](./development/testing-guide.md)

### Contributing
- Follow [Coding Standards](./development/coding-standards.md)
- Run tests before submitting PRs
- Update documentation for new features
- Use UV package manager for dependencies

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Active Development (72.6% Complete)