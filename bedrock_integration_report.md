
# AWS Bedrock 통합 상태 보고서

## 연결 상태
- **상태**: success
- **리전**: us-east-1
- **사용 가능한 모델 수**: 91

## 모델 액세스 상태
- ❌ anthropic.claude-3-sonnet-20240229-v1:0: access_denied
- ❌ anthropic.claude-3-opus-20240229-v1:0: validation_error
- ❌ anthropic.claude-3-haiku-20240307-v1:0: access_denied
- ❌ amazon.nova-pro-v1:0: access_denied
- ❌ amazon.nova-lite-v1:0: access_denied

## 에이전트 통합 테스트
- **NL Input Agent**: failed
- **Component Decision Agent**: failed
- **전체 통합**: success

## 권장사항
- 다음 모델들에 대한 액세스를 요청하세요: anthropic.claude-3-sonnet-20240229-v1:0, anthropic.claude-3-haiku-20240307-v1:0, amazon.nova-pro-v1:0, amazon.nova-lite-v1:0
- 정기적으로 모델 성능과 비용을 모니터링하세요.
- 프로덕션 환경에서는 적절한 요청 제한을 설정하세요.
