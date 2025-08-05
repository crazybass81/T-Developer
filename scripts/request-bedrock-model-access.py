#!/usr/bin/env python3
# AWS Bedrock 모델 액세스 요청 자동화 스크립트

import boto3
import json
import time
from typing import List, Dict, Any
from botocore.exceptions import ClientError

class BedrockModelAccessManager:
    """Bedrock 모델 액세스 관리"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.bedrock_client = boto3.client('bedrock', region_name=region)
        
        # T-Developer에서 필요한 핵심 모델들
        self.required_models = [
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-opus-20240229-v1:0', 
            'anthropic.claude-3-haiku-20240307-v1:0',
            'amazon.nova-pro-v1:0',
            'amazon.nova-lite-v1:0',
            'amazon.titan-text-premier-v1:0'
        ]
    
    def check_current_access(self) -> Dict[str, Any]:
        """현재 모델 액세스 상태 확인"""
        
        print("🔍 현재 Bedrock 모델 액세스 상태 확인 중...")
        
        access_status = {}
        
        try:
            # 사용 가능한 모든 모델 조회
            response = self.bedrock_client.list_foundation_models()
            available_models = {model['modelId']: model for model in response['modelSummaries']}
            
            for model_id in self.required_models:
                if model_id in available_models:
                    model_info = available_models[model_id]
                    access_status[model_id] = {
                        'available': True,
                        'provider': model_info['providerName'],
                        'status': 'accessible'
                    }
                else:
                    access_status[model_id] = {
                        'available': False,
                        'status': 'access_required'
                    }
            
            return {
                'success': True,
                'total_models_available': len(available_models),
                'required_models_status': access_status
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.response['Error']['Code']
            }
    
    def generate_access_request_guide(self) -> str:
        """모델 액세스 요청 가이드 생성"""
        
        status = self.check_current_access()
        
        if not status['success']:
            return f"❌ 오류 발생: {status['error']}"
        
        guide = """
# AWS Bedrock 모델 액세스 요청 가이드

## 🎯 T-Developer에서 필요한 모델들

다음 모델들에 대한 액세스가 필요합니다:

"""
        
        for model_id, info in status['required_models_status'].items():
            if info['available']:
                guide += f"✅ **{model_id}** - 이미 액세스 가능\n"
            else:
                guide += f"❌ **{model_id}** - 액세스 요청 필요\n"
        
        guide += """

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
"""
        
        return guide
    
    def estimate_monthly_costs(self) -> Dict[str, Any]:
        """월간 예상 비용 계산"""
        
        # T-Developer 사용 패턴 기반 예상 사용량
        estimated_usage = {
            'anthropic.claude-3-sonnet-20240229-v1:0': {
                'input_tokens': 1000000,  # 1M tokens/month
                'output_tokens': 200000,  # 200K tokens/month
                'price_per_1k_input': 0.003,
                'price_per_1k_output': 0.015
            },
            'anthropic.claude-3-opus-20240229-v1:0': {
                'input_tokens': 200000,   # 200K tokens/month
                'output_tokens': 50000,   # 50K tokens/month  
                'price_per_1k_input': 0.015,
                'price_per_1k_output': 0.075
            },
            'anthropic.claude-3-haiku-20240307-v1:0': {
                'input_tokens': 2000000,  # 2M tokens/month
                'output_tokens': 400000,  # 400K tokens/month
                'price_per_1k_input': 0.00025,
                'price_per_1k_output': 0.00125
            },
            'amazon.nova-pro-v1:0': {
                'input_tokens': 500000,   # 500K tokens/month
                'output_tokens': 100000,  # 100K tokens/month
                'price_per_1k_input': 0.0008,
                'price_per_1k_output': 0.0032
            },
            'amazon.nova-lite-v1:0': {
                'input_tokens': 3000000,  # 3M tokens/month
                'output_tokens': 600000,  # 600K tokens/month
                'price_per_1k_input': 0.00006,
                'price_per_1k_output': 0.00024
            }
        }
        
        total_cost = 0
        cost_breakdown = {}
        
        for model_id, usage in estimated_usage.items():
            input_cost = (usage['input_tokens'] / 1000) * usage['price_per_1k_input']
            output_cost = (usage['output_tokens'] / 1000) * usage['price_per_1k_output']
            model_total = input_cost + output_cost
            
            cost_breakdown[model_id] = {
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': model_total
            }
            
            total_cost += model_total
        
        return {
            'total_monthly_cost_usd': round(total_cost, 2),
            'cost_breakdown': cost_breakdown,
            'note': '실제 비용은 사용량에 따라 달라질 수 있습니다'
        }

def main():
    """메인 실행 함수"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Bedrock 모델 액세스 관리')
    parser.add_argument('--check', action='store_true', help='현재 액세스 상태만 확인')
    parser.add_argument('--costs', action='store_true', help='예상 비용 계산')
    parser.add_argument('--region', default='us-east-1', help='AWS 리전')
    
    args = parser.parse_args()
    
    manager = BedrockModelAccessManager(region=args.region)
    
    if args.check:
        # 액세스 상태만 확인
        status = manager.check_current_access()
        
        if status['success']:
            print(f"✅ 총 {status['total_models_available']}개 모델 사용 가능")
            
            accessible_count = sum(1 for info in status['required_models_status'].values() 
                                 if info['available'])
            total_required = len(status['required_models_status'])
            
            print(f"📊 필수 모델 액세스: {accessible_count}/{total_required}")
            
            for model_id, info in status['required_models_status'].items():
                status_icon = "✅" if info['available'] else "❌"
                print(f"  {status_icon} {model_id}")
        else:
            print(f"❌ 오류: {status['error']}")
    
    elif args.costs:
        # 비용 예상
        costs = manager.estimate_monthly_costs()
        
        print(f"💰 예상 월간 비용: ${costs['total_monthly_cost_usd']}")
        print("\n📊 모델별 비용 분석:")
        
        for model_id, cost_info in costs['cost_breakdown'].items():
            print(f"  • {model_id}: ${cost_info['total_cost']:.2f}")
    
    else:
        # 전체 가이드 생성
        guide = manager.generate_access_request_guide()
        
        # 파일로 저장
        with open('bedrock_access_guide.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("📋 Bedrock 모델 액세스 가이드가 생성되었습니다!")
        print("📄 파일: bedrock_access_guide.md")
        
        # 비용 정보도 출력
        costs = manager.estimate_monthly_costs()
        print(f"\n💰 예상 월간 비용: ${costs['total_monthly_cost_usd']}")

if __name__ == "__main__":
    main()