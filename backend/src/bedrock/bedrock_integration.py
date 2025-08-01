# AWS Bedrock 통합 검증 및 설정

import boto3
import json
import os
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import asyncio
from dataclasses import dataclass

@dataclass
class BedrockModelInfo:
    model_id: str
    model_name: str
    provider: str
    input_modalities: List[str]
    output_modalities: List[str]
    supported_features: List[str]
    max_tokens: int
    pricing_per_1k_tokens: float

class BedrockIntegration:
    """AWS Bedrock 통합 및 검증 클래스"""
    
    def __init__(self):
        self.region = os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
        self.bedrock_client = None
        self.bedrock_runtime = None
        self.available_models = {}
        
    async def initialize(self) -> Dict[str, Any]:
        """Bedrock 클라이언트 초기화 및 검증"""
        
        try:
            # Bedrock 클라이언트 생성
            self.bedrock_client = boto3.client(
                'bedrock',
                region_name=self.region
            )
            
            # Bedrock Runtime 클라이언트 생성
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
            
            # 연결 테스트
            connection_test = await self._test_connection()
            
            # 사용 가능한 모델 조회
            models = await self._list_available_models()
            
            # 모델 액세스 권한 확인
            access_status = await self._check_model_access()
            
            return {
                'status': 'success',
                'connection': connection_test,
                'available_models': models,
                'access_status': access_status,
                'region': self.region
            }
            
        except NoCredentialsError:
            return {
                'status': 'error',
                'error': 'AWS credentials not found',
                'solution': 'Configure AWS credentials using aws configure or environment variables'
            }
        except ClientError as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_code': e.response['Error']['Code']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Unexpected error: {str(e)}'
            }
    
    async def _test_connection(self) -> Dict[str, Any]:
        """Bedrock 연결 테스트"""
        
        try:
            # 기본 API 호출로 연결 테스트
            response = self.bedrock_client.list_foundation_models()
            
            return {
                'status': 'connected',
                'models_count': len(response.get('modelSummaries', [])),
                'timestamp': response['ResponseMetadata']['HTTPHeaders']['date']
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _list_available_models(self) -> List[BedrockModelInfo]:
        """사용 가능한 Bedrock 모델 목록 조회"""
        
        try:
            response = self.bedrock_client.list_foundation_models()
            models = []
            
            for model_summary in response.get('modelSummaries', []):
                model_info = BedrockModelInfo(
                    model_id=model_summary['modelId'],
                    model_name=model_summary['modelName'],
                    provider=model_summary['providerName'],
                    input_modalities=model_summary.get('inputModalities', []),
                    output_modalities=model_summary.get('outputModalities', []),
                    supported_features=model_summary.get('supportedFeatures', []),
                    max_tokens=self._get_model_max_tokens(model_summary['modelId']),
                    pricing_per_1k_tokens=self._get_model_pricing(model_summary['modelId'])
                )
                models.append(model_info)
                self.available_models[model_info.model_id] = model_info
            
            return models
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    async def _check_model_access(self) -> Dict[str, Any]:
        """모델별 액세스 권한 확인"""
        
        # T-Developer에서 사용할 주요 모델들
        required_models = [
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-opus-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0',
            'amazon.nova-pro-v1:0',
            'amazon.nova-lite-v1:0'
        ]
        
        access_status = {}
        
        for model_id in required_models:
            try:
                # 간단한 테스트 호출로 액세스 확인
                test_result = await self._test_model_access(model_id)
                access_status[model_id] = test_result
                
            except Exception as e:
                access_status[model_id] = {
                    'status': 'no_access',
                    'error': str(e)
                }
        
        return access_status
    
    async def _test_model_access(self, model_id: str) -> Dict[str, Any]:
        """특정 모델의 액세스 권한 테스트"""
        
        try:
            # 최소한의 테스트 요청
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
            
            return {
                'status': 'accessible',
                'response_size': len(response['body'].read()),
                'content_type': response['contentType']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'AccessDeniedException':
                return {
                    'status': 'access_denied',
                    'error': 'Model access not granted',
                    'solution': 'Request model access in AWS Bedrock console'
                }
            elif error_code == 'ValidationException':
                return {
                    'status': 'validation_error',
                    'error': e.response['Error']['Message']
                }
            else:
                return {
                    'status': 'error',
                    'error': str(e),
                    'error_code': error_code
                }
    
    def _get_model_max_tokens(self, model_id: str) -> int:
        """모델별 최대 토큰 수 반환"""
        
        token_limits = {
            'anthropic.claude-3-opus-20240229-v1:0': 200000,
            'anthropic.claude-3-sonnet-20240229-v1:0': 200000,
            'anthropic.claude-3-haiku-20240307-v1:0': 200000,
            'amazon.nova-pro-v1:0': 300000,
            'amazon.nova-lite-v1:0': 300000,
            'amazon.titan-text-premier-v1:0': 32000,
            'cohere.command-r-plus-v1:0': 128000
        }
        
        return token_limits.get(model_id, 4096)
    
    def _get_model_pricing(self, model_id: str) -> float:
        """모델별 1K 토큰당 가격 (USD)"""
        
        # 2024년 기준 대략적인 가격 (실제 가격은 AWS 콘솔에서 확인)
        pricing = {
            'anthropic.claude-3-opus-20240229-v1:0': 0.015,
            'anthropic.claude-3-sonnet-20240229-v1:0': 0.003,
            'anthropic.claude-3-haiku-20240307-v1:0': 0.00025,
            'amazon.nova-pro-v1:0': 0.0008,
            'amazon.nova-lite-v1:0': 0.00006,
            'amazon.titan-text-premier-v1:0': 0.0005
        }
        
        return pricing.get(model_id, 0.001)
    
    async def test_agent_integration(self) -> Dict[str, Any]:
        """T-Developer 에이전트와의 통합 테스트"""
        
        test_results = {}
        
        # 1. NL Input Agent 테스트
        nl_test = await self._test_nl_agent_integration()
        test_results['nl_input_agent'] = nl_test
        
        # 2. Component Decision Agent 테스트
        decision_test = await self._test_decision_agent_integration()
        test_results['component_decision_agent'] = decision_test
        
        # 3. 전체 통합 테스트
        integration_test = await self._test_full_integration()
        test_results['full_integration'] = integration_test
        
        return test_results
    
    async def _test_nl_agent_integration(self) -> Dict[str, Any]:
        """NL Input Agent와 Bedrock 통합 테스트"""
        
        try:
            # Claude-3 Sonnet으로 자연어 처리 테스트
            model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": "다음 프로젝트 설명을 분석해주세요: '실시간 채팅 기능이 있는 웹 애플리케이션을 만들고 싶습니다. 사용자 인증과 파일 업로드 기능도 필요합니다.'"
                    }
                ]
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            return {
                'status': 'success',
                'model_used': model_id,
                'response_length': len(response_body['content'][0]['text']),
                'tokens_used': response_body['usage']['input_tokens'] + response_body['usage']['output_tokens']
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_decision_agent_integration(self) -> Dict[str, Any]:
        """Component Decision Agent와 Bedrock 통합 테스트"""
        
        try:
            # Claude-3 Opus로 의사결정 테스트
            model_id = 'anthropic.claude-3-opus-20240229-v1:0'
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "messages": [
                    {
                        "role": "user",
                        "content": """
                        다음 컴포넌트들 중에서 실시간 채팅 애플리케이션에 가장 적합한 것을 선택하고 근거를 제시해주세요:
                        
                        1. Socket.IO - WebSocket 기반 실시간 통신
                        2. WebRTC - P2P 실시간 통신
                        3. Server-Sent Events - 단방향 실시간 통신
                        
                        성능, 확장성, 구현 복잡도를 고려해서 평가해주세요.
                        """
                    }
                ]
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            return {
                'status': 'success',
                'model_used': model_id,
                'decision_quality': 'high' if 'Socket.IO' in response_body['content'][0]['text'] else 'medium',
                'tokens_used': response_body['usage']['input_tokens'] + response_body['usage']['output_tokens']
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_full_integration(self) -> Dict[str, Any]:
        """전체 시스템 통합 테스트"""
        
        try:
            # 여러 모델을 사용한 복합 테스트
            models_to_test = [
                'anthropic.claude-3-sonnet-20240229-v1:0',
                'amazon.nova-pro-v1:0'
            ]
            
            test_results = {}
            
            for model_id in models_to_test:
                if model_id in self.available_models:
                    result = await self._run_integration_test(model_id)
                    test_results[model_id] = result
            
            return {
                'status': 'success',
                'models_tested': len(test_results),
                'results': test_results
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_integration_test(self, model_id: str) -> Dict[str, Any]:
        """개별 모델 통합 테스트"""
        
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": "T-Developer 시스템에서 사용할 수 있는 간단한 응답을 해주세요."
                    }
                ]
            })
            
            start_time = asyncio.get_event_loop().time()
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            response_body = json.loads(response['body'].read())
            
            return {
                'status': 'success',
                'response_time_ms': response_time * 1000,
                'tokens_used': response_body['usage']['input_tokens'] + response_body['usage']['output_tokens'],
                'response_quality': 'good' if len(response_body['content'][0]['text']) > 50 else 'poor'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def generate_setup_report(self) -> str:
        """Bedrock 설정 상태 보고서 생성"""
        
        initialization_result = await self.initialize()
        integration_test = await self.test_agent_integration()
        
        report = f"""
# AWS Bedrock 통합 상태 보고서

## 연결 상태
- **상태**: {initialization_result['status']}
- **리전**: {self.region}
- **사용 가능한 모델 수**: {len(initialization_result.get('available_models', []))}

## 모델 액세스 상태
"""
        
        if 'access_status' in initialization_result:
            for model_id, status in initialization_result['access_status'].items():
                status_icon = "✅" if status['status'] == 'accessible' else "❌"
                report += f"- {status_icon} {model_id}: {status['status']}\n"
        
        report += f"""
## 에이전트 통합 테스트
- **NL Input Agent**: {integration_test.get('nl_input_agent', {}).get('status', 'not_tested')}
- **Component Decision Agent**: {integration_test.get('component_decision_agent', {}).get('status', 'not_tested')}
- **전체 통합**: {integration_test.get('full_integration', {}).get('status', 'not_tested')}

## 권장사항
"""
        
        # 권장사항 생성
        if initialization_result['status'] == 'error':
            report += "- AWS 자격 증명을 확인하고 Bedrock 서비스 액세스 권한을 설정하세요.\n"
        
        if 'access_status' in initialization_result:
            denied_models = [
                model_id for model_id, status in initialization_result['access_status'].items()
                if status['status'] == 'access_denied'
            ]
            
            if denied_models:
                report += f"- 다음 모델들에 대한 액세스를 요청하세요: {', '.join(denied_models)}\n"
        
        report += "- 정기적으로 모델 성능과 비용을 모니터링하세요.\n"
        report += "- 프로덕션 환경에서는 적절한 요청 제한을 설정하세요.\n"
        
        return report

# 사용 예시 및 테스트 실행
async def main():
    """Bedrock 통합 테스트 실행"""
    
    bedrock = BedrockIntegration()
    
    print("🔍 AWS Bedrock 통합 상태 확인 중...")
    
    # 초기화 및 연결 테스트
    init_result = await bedrock.initialize()
    print(f"초기화 결과: {init_result['status']}")
    
    if init_result['status'] == 'success':
        # 에이전트 통합 테스트
        print("\n🤖 에이전트 통합 테스트 실행 중...")
        integration_result = await bedrock.test_agent_integration()
        
        for agent_name, result in integration_result.items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {agent_name}: {result['status']}")
    
    # 보고서 생성
    print("\n📋 상태 보고서 생성 중...")
    report = await bedrock.generate_setup_report()
    
    # 보고서 저장
    with open('bedrock_integration_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Bedrock 통합 확인 완료!")
    print("📄 상세 보고서: bedrock_integration_report.md")

if __name__ == "__main__":
    asyncio.run(main())