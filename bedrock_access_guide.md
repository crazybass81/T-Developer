
# AWS Bedrock 모델 액세스 요청 가이드

## 🎯 T-Developer에서 필요한 모델들

다음 모델들에 대한 액세스가 필요합니다:

✅ **anthropic.claude-3-sonnet-20240229-v1:0** - 이미 액세스 가능
✅ **anthropic.claude-3-opus-20240229-v1:0** - 이미 액세스 가능
✅ **anthropic.claude-3-haiku-20240307-v1:0** - 이미 액세스 가능
✅ **amazon.nova-pro-v1:0** - 이미 액세스 가능
✅ **amazon.nova-lite-v1:0** - 이미 액세스 가능
✅ **amazon.titan-text-premier-v1:0** - 이미 액세스 가능


## 📋 액세스 요청 단계

### 1. AWS 콘솔 접속
1. [AWS Bedrock 콘솔](https://console.aws.amazon.com/bedrock/)에 접속
2. 좌측 메뉴에서 **"Model access"** 클릭

### 2. 모델 액세스 요청
다음 모델들에 대해 액세스를 요청하세요:

#### Anthropic Claude 모델들
- `anthropic.claude-3-sonnet-20240229-v1:0` - 범용 고성능 모델
- `anthropic.claude-3-opus-20240229-v1:0` - 최고 성능 모델 (복잡한 분석용)
- `anthropic.claude-3-haiku-20240307-v1:0` - 빠른 응답 모델

#### Amazon Nova 모델들  
- `amazon.nova-pro-v1:0` - AWS 네이티브 고성능 모델
- `amazon.nova-lite-v1:0` - AWS 네이티브 경량 모델

#### Amazon Titan 모델들
- `amazon.titan-text-premier-v1:0` - 텍스트 생성 모델

### 3. 요청 승인 대기
- 대부분의 모델은 **즉시 승인**됩니다
- 일부 고성능 모델(Claude-3 Opus)은 검토가 필요할 수 있습니다
- 승인 상태는 콘솔에서 확인 가능합니다

### 4. 액세스 확인
```bash
# 스크립트로 액세스 상태 재확인
python3 scripts/request-bedrock-model-access.py --check
```

## 💡 각 모델의 용도

| 모델 | 용도 | 특징 |
|------|------|------|
| Claude-3 Sonnet | NL Input Agent, 일반적인 분석 | 균형잡힌 성능과 비용 |
| Claude-3 Opus | Component Decision Agent, 복잡한 의사결정 | 최고 성능, 높은 비용 |
| Claude-3 Haiku | 빠른 응답이 필요한 작업 | 빠른 속도, 저비용 |
| Nova Pro | AWS 네이티브 고성능 작업 | AWS 최적화, 좋은 성능 |
| Nova Lite | 간단한 작업, 대량 처리 | 매우 저비용 |

## 🔧 문제 해결

### 액세스가 거부되는 경우
1. AWS 계정이 Bedrock 서비스를 사용할 수 있는지 확인
2. IAM 권한에 `bedrock:*` 권한이 있는지 확인
3. 올바른 리전(us-east-1)을 사용하고 있는지 확인

### 특정 모델이 보이지 않는 경우
1. 리전을 확인 (일부 모델은 특정 리전에서만 사용 가능)
2. AWS 계정 유형 확인 (일부 모델은 엔터프라이즈 계정에서만 사용 가능)

## 📞 지원

문제가 지속되면 AWS Support에 문의하거나 팀 Slack 채널에서 도움을 요청하세요.
