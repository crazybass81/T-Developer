# T-Developer Documentation

## 📚 Documentation Overview

T-Developer는 AWS Bedrock Agent 기반의 엔터프라이즈급 AI 멀티 에이전트 개발 플랫폼입니다.

## 🚀 Latest Updates (v2.0.0)

### ✨ Enterprise Backend Complete
- **보안**: JWT 인증, RBAC, API 키 관리, 보안 스캔
- **인프라**: SQLAlchemy, Celery, WebSocket, OpenTelemetry
- **에이전트**: Security & Test Agent 추가, Agno 통합 (3μs/6.5KB)
- **AWS**: Agent Squad, Bedrock AgentCore, Step Functions 완전 통합

## 🏗️ Architecture Documentation

### Core Architecture
- [System Architecture](./architecture/system-architecture.md) - 전체 시스템 설계 및 구성요소
- [Enterprise Architecture](./architecture/enterprise-architecture.md) - 엔터프라이즈 기능 및 설계
- [Multi-Agent Framework](./architecture/multi-agent-framework.md) - 9+2 에이전트 아키텍처
- [Technology Stack](./architecture/technology-stack.md) - Agno + Agent Squad + Bedrock 통합

### Infrastructure
- [AWS Configuration](./deployment/aws-config-setup.md) - AWS 서비스 설정 가이드
- [Infrastructure as Code](./deployment/infrastructure.md) - CDK/CloudFormation 설정

## 🤖 Agent Documentation

### Core Agents (9개 + 2개 추가)
1. **[NL Input Agent](./agents/nl-input-agent.md)** - 자연어 입력 처리 ✅
2. **[UI Selection Agent](./agents/ui-selection-agent.md)** - UI 프레임워크 선택 ✅
3. **[Parser Agent](./agents/parser-agent.md)** - 코드 파싱 및 분석 ✅
4. **[Component Decision Agent](./agents/component-decision-agent.md)** - 컴포넌트 결정 ✅
5. **[Match Rate Agent](./agents/match-rate-agent.md)** - 매칭률 계산 ✅
6. **[Search Agent](./agents/search-agent.md)** - 컴포넌트 검색 ✅
7. **[Generation Agent](./agents/generation-agent.md)** - 코드 생성 ✅
8. **[Assembly Agent](./agents/assembly-agent.md)** - 서비스 조립 ✅
9. **[Download Agent](./agents/download-agent.md)** - 프로젝트 패키징 ✅

### Additional Agents (새로 추가)
10. **[Security Agent](./agents/security-agent.md)** - OWASP Top 10 보안 스캔 ✅
11. **[Test Agent](./agents/test-agent.md)** - 80%+ 커버리지 테스트 생성 ✅

### Agent Framework
- [Agent Base Classes](./agents/framework/base-classes.md) - 에이전트 기본 클래스
- [Agno Integration](./agents/framework/agno-integration.md) - 초경량 에이전트 프레임워크
- [Agent Lifecycle](./agents/framework/lifecycle.md) - 에이전트 생명주기 관리

## 🚀 Development Guides

### Getting Started
- [Quick Start Guide](./development/quick-start.md) - 5분 안에 시작하기
- [Environment Setup](./development/environment-setup.md) - 개발 환경 설정
- [Python Development](./development/python-guide.md) - Python 백엔드 개발

### Development Workflow
- [Coding Standards](./development/coding-standards.md) - 코딩 표준 및 규칙
- [Testing Guide](./development/testing-guide.md) - 85%+ 커버리지 달성
- [Security Best Practices](./development/security-guide.md) - 보안 개발 가이드

### API Documentation
- [REST API Reference](./api/rest-api.md) - REST API 완전 문서
- [WebSocket API](./api/websocket-api.md) - 실시간 통신 API
- [OpenAPI/Swagger](http://localhost:8000/docs) - 대화형 API 문서

## 📊 Project Status

### Implementation Progress
- **전체 완료율**: 95%+ ✅
- **엔터프라이즈 기능**: 100% 완료
- **보안 기능**: 100% 완료
- **테스트 커버리지**: 85%+
- **문서화**: 90% 완료

### Performance Metrics
| Metric | Target | Achieved | Status |
|--------|--------|----------|---------|
| Agent Creation | < 3μs | 2.8μs | ✅ |
| Memory per Agent | < 6.5KB | 6.2KB | ✅ |
| API Response | < 200ms | 180ms | ✅ |
| Code Coverage | > 80% | 85% | ✅ |
| Security Score | > 90/100 | 95/100 | ✅ |

## 🔧 Deployment & Operations

### Deployment
- [Production Deployment](./deployment/production.md) - 프로덕션 배포 가이드
- [Docker Deployment](./deployment/docker.md) - 컨테이너 배포
- [AWS ECS/Lambda](./deployment/aws-deployment.md) - AWS 서버리스 배포

### Monitoring & Operations
- [OpenTelemetry Setup](./deployment/opentelemetry.md) - 분산 트레이싱
- [CloudWatch Integration](./deployment/cloudwatch.md) - AWS 모니터링
- [Prometheus/Grafana](./deployment/metrics.md) - 메트릭 대시보드

## 🛡️ Security & Compliance

### Security Features
- **인증**: JWT with RS256, Token Blacklisting
- **인가**: Role-Based Access Control (4 tiers)
- **API 보안**: Rate Limiting, API Key Management
- **코드 보안**: OWASP Top 10 Scanning
- **데이터 보안**: Encryption at Rest/Transit

### Compliance
- GDPR Ready
- SOC 2 Type II (In Progress)
- ISO 27001 (Planned)

## 🎯 Quick Navigation

### For Developers
1. [Quick Start](./development/quick-start.md) - 개발 시작하기
2. [Agent Development](./agents/framework/base-classes.md) - 에이전트 개발
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

### AWS Documentation
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/)
- [AWS CloudWatch](https://docs.aws.amazon.com/cloudwatch/)

### Framework Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Celery](https://docs.celeryproject.org/)

### Monitoring Tools
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

## 📞 Support & Contributing

### Getting Help
- Check the [Troubleshooting Guide](./deployment/troubleshooting.md)
- Review [FAQ](./faq.md)
- Join our [Discord](https://discord.gg/t-developer)

### Contributing
- Follow [Coding Standards](./development/coding-standards.md)
- Run tests before submitting PRs
- Update documentation for new features
- Use conventional commits

### Contact
- **Email**: support@t-developer.com
- **GitHub Issues**: [Report Issues](https://github.com/your-org/T-DeveloperMVP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/T-DeveloperMVP/discussions)

---

**Last Updated**: January 2024  
**Version**: 2.0.0  
**Status**: Production Ready 🚀