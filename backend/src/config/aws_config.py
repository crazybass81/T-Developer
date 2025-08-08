"""
AWS Configuration with IAM Role
IAM Role을 통한 자동 인증 및 시크릿 관리
"""

import os
import json
import boto3
from typing import Optional, Dict, Any
from functools import lru_cache

class AWSConfig:
    """
    AWS 서비스 설정 및 시크릿 관리
    IAM Role을 통해 자동으로 인증됨
    """
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # IAM Role을 통한 자동 인증
        self.sm_client = boto3.client('secretsmanager', region_name=self.region)
        self.ssm_client = boto3.client('ssm', region_name=self.region)
        self.s3_client = boto3.client('s3', region_name=self.region)
        
        # 시크릿 캐시
        self._secrets_cache = {}
        
        # 연결 테스트
        self._verify_connection()
    
    def _verify_connection(self):
        """AWS 연결 확인"""
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ Connected to AWS as: {identity.get('Arn')}")
            
            # IAM Role 이름 확인
            role_arn = identity.get('Arn')
            if 'AmazonQ-Admin-Role' in role_arn:
                print("✅ Using AmazonQ-Admin-Role")
            
            return True
        except Exception as e:
            print(f"⚠️ AWS connection error: {e}")
            return False
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_key: str) -> Optional[Any]:
        """
        Secrets Manager에서 시크릿 가져오기
        
        Args:
            secret_key: 시크릿 키 (예: 'DB_PASSWORD', 'JWT_SECRET')
        
        Returns:
            시크릿 값
        """
        
        # 전체 시크릿 가져오기 (한 번만)
        if not self._secrets_cache:
            try:
                secret_id = f"t-developer/{self.environment}/secrets"
                response = self.sm_client.get_secret_value(SecretId=secret_id)
                
                if 'SecretString' in response:
                    self._secrets_cache = json.loads(response['SecretString'])
                    print(f"✅ Loaded secrets from: {secret_id}")
            except Exception as e:
                print(f"❌ Error loading secrets: {e}")
                self._secrets_cache = {}
        
        # 캐시에서 가져오기
        value = self._secrets_cache.get(secret_key)
        
        # 없으면 환경 변수에서 가져오기
        if value is None:
            value = os.getenv(secret_key)
        
        # 기본값
        if value is None:
            defaults = {
                'DB_PASSWORD': 'postgres',
                'REDIS_PASSWORD': '',
                'JWT_SECRET': 'development-secret',
                'OPENAI_API_KEY': 'sk-development',
                'ANTHROPIC_API_KEY': 'sk-ant-development'
            }
            value = defaults.get(secret_key)
        
        return value
    
    def get_parameter(self, param_name: str) -> Optional[str]:
        """
        Parameter Store에서 파라미터 가져오기
        """
        try:
            param_path = f"/t-developer/{self.environment}/{param_name}"
            response = self.ssm_client.get_parameter(Name=param_path)
            return response['Parameter']['Value']
        except self.ssm_client.exceptions.ParameterNotFound:
            print(f"Parameter not found: {param_path}")
        except Exception as e:
            print(f"Error getting parameter: {e}")
        
        # 환경 변수 폴백
        return os.getenv(param_name.upper())
    
    def get_database_url(self) -> str:
        """데이터베이스 URL 생성"""
        password = self.get_secret('DB_PASSWORD') or 'postgres'
        host = os.getenv('DB_HOST', 'postgres')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 't_developer')
        
        return f"postgresql://postgres:{password}@{host}:{port}/{database}"
    
    def get_redis_url(self) -> str:
        """Redis URL 생성"""
        password = self.get_secret('REDIS_PASSWORD') or ''
        host = os.getenv('REDIS_HOST', 'redis')
        port = os.getenv('REDIS_PORT', '6379')
        
        if password:
            return f"redis://:{password}@{host}:{port}/0"
        return f"redis://{host}:{port}/0"
    
    def get_all_config(self) -> Dict[str, Any]:
        """모든 설정 가져오기"""
        return {
            'environment': self.environment,
            'region': self.region,
            'database_url': self.get_database_url(),
            'redis_url': self.get_redis_url(),
            'jwt_secret': self.get_secret('JWT_SECRET'),
            'jwt_refresh_secret': self.get_secret('JWT_REFRESH_SECRET'),
            'encryption_key': self.get_secret('ENCRYPTION_KEY'),
        }
    
    def create_or_update_secret(self, secret_dict: Dict[str, str]):
        """
        시크릿 생성 또는 업데이트 (관리자용)
        """
        try:
            secret_id = f"t-developer/{self.environment}/secrets"
            
            # 기존 시크릿 가져오기
            try:
                response = self.sm_client.get_secret_value(SecretId=secret_id)
                existing = json.loads(response['SecretString'])
                existing.update(secret_dict)
                secret_dict = existing
            except self.sm_client.exceptions.ResourceNotFoundException:
                pass
            
            # 시크릿 생성 또는 업데이트
            try:
                self.sm_client.update_secret(
                    SecretId=secret_id,
                    SecretString=json.dumps(secret_dict)
                )
                print(f"✅ Updated secret: {secret_id}")
            except self.sm_client.exceptions.ResourceNotFoundException:
                self.sm_client.create_secret(
                    Name=secret_id,
                    SecretString=json.dumps(secret_dict),
                    Description=f"T-Developer {self.environment} secrets"
                )
                print(f"✅ Created secret: {secret_id}")
            
            # 캐시 무효화
            self._secrets_cache = {}
            return True
            
        except Exception as e:
            print(f"❌ Error managing secret: {e}")
            return False


# 글로벌 인스턴스
aws_config = AWSConfig()

# 사용 예시
if __name__ == "__main__":
    # 설정 확인
    config = aws_config.get_all_config()
    print("\n📋 Current Configuration:")
    for key, value in config.items():
        if 'secret' in key.lower() or 'password' in key.lower():
            print(f"  {key}: ***hidden***")
        else:
            print(f"  {key}: {value}")