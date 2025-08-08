"""
AWS Secrets Manager 통합
IAM Role 기반 시크릿 관리
"""

import os
import json
import boto3
from typing import Optional, Dict, Any
from functools import lru_cache

class SecretsManager:
    """
    AWS Secrets Manager와 로컬 환경 변수를 통합 관리
    """
    
    def __init__(self):
        self.use_aws = os.getenv('USE_AWS_SECRETS', 'false').lower() == 'true'
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        if self.use_aws:
            try:
                # IAM Role을 통한 자동 인증
                self.sm_client = boto3.client('secretsmanager', region_name=self.region)
                self.ssm_client = boto3.client('ssm', region_name=self.region)
                self._test_connection()
            except Exception as e:
                print(f"Warning: Cannot connect to AWS ({e}). Falling back to local env.")
                self.use_aws = False
    
    def _test_connection(self):
        """AWS 연결 테스트"""
        try:
            # IAM Role이 있는지 확인
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"Connected to AWS as: {identity.get('Arn')}")
            return True
        except:
            return False
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        시크릿 가져오기 (캐시 적용)
        
        1. AWS Secrets Manager (프로덕션)
        2. 환경 변수 (로컬 개발)
        3. 기본값 (테스트)
        """
        
        # 1. AWS Secrets Manager 시도
        if self.use_aws:
            try:
                response = self.sm_client.get_secret_value(
                    SecretId=f't-developer/{secret_name}'
                )
                
                # JSON 형식 시크릿 처리
                if 'SecretString' in response:
                    secret = response['SecretString']
                    try:
                        # JSON인 경우 파싱
                        return json.loads(secret)
                    except:
                        # 일반 문자열
                        return secret
                        
            except self.sm_client.exceptions.ResourceNotFoundException:
                print(f"Secret not found in AWS: t-developer/{secret_name}")
            except Exception as e:
                print(f"Error getting secret from AWS: {e}")
        
        # 2. 환경 변수에서 가져오기
        env_name = secret_name.upper().replace('-', '_')
        env_value = os.getenv(env_name)
        if env_value:
            return env_value
        
        # 3. 로컬 .env 파일에서 가져오기
        env_file = '/home/ec2-user/T-DeveloperMVP/backend/.env'
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith(f'{env_name}='):
                        return line.split('=', 1)[1].strip()
        
        # 4. 기본값 반환 (개발/테스트용)
        defaults = {
            'openai-api-key': 'sk-local-development',
            'anthropic-api-key': 'sk-ant-local-development',
            'database-url': 'postgresql://postgres:postgres@localhost:5432/t_developer',
            'redis-url': 'redis://localhost:6379/0'
        }
        
        return defaults.get(secret_name)
    
    def get_parameter(self, param_name: str) -> Optional[str]:
        """
        Parameter Store에서 파라미터 가져오기
        """
        
        if self.use_aws:
            try:
                response = self.ssm_client.get_parameter(
                    Name=f'/t-developer/{param_name}'
                )
                return response['Parameter']['Value']
            except Exception as e:
                print(f"Error getting parameter: {e}")
        
        # 환경 변수 폴백
        return os.getenv(param_name.upper().replace('-', '_'))
    
    def get_all_secrets(self) -> Dict[str, Any]:
        """
        모든 필요한 시크릿 가져오기
        """
        secrets = {
            'openai_api_key': self.get_secret('openai-api-key'),
            'anthropic_api_key': self.get_secret('anthropic-api-key'),
            'database_url': self.get_secret('database-url'),
            'redis_url': self.get_secret('redis-url'),
        }
        
        # None 값 필터링
        return {k: v for k, v in secrets.items() if v is not None}
    
    def create_secret(self, secret_name: str, secret_value: str, description: str = None):
        """
        새 시크릿 생성 (관리자용)
        """
        if not self.use_aws:
            print("Cannot create secret: AWS not configured")
            return False
        
        try:
            response = self.sm_client.create_secret(
                Name=f't-developer/{secret_name}',
                Description=description or f'