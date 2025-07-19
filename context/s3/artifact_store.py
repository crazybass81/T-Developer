"""
ArtifactStore - S3 기반 아티팩트 저장소

계획, 코드 diff, 테스트 로그 등의 아티팩트를 S3에 저장하고 조회하는 기능을 제공합니다.
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional, Union, BinaryIO
import io

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class ArtifactStore:
    """
    S3 기반 아티팩트 저장소
    
    계획, 코드 diff, 테스트 로그 등의 아티팩트를 저장하고 조회하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """ArtifactStore 초기화"""
        self.region = settings.AWS_REGION
        self.bucket_name = settings.S3_BUCKET_NAME
        self.s3_client = boto3.client('s3', region_name=self.region)
        self._ensure_bucket_exists()
        logger.info(f"ArtifactStore initialized with bucket: {self.bucket_name}")
    
    def _ensure_bucket_exists(self):
        """
        버킷이 존재하는지 확인하고, 없으면 생성
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creating S3 bucket: {self.bucket_name}")
                
                # us-east-1 리전은 LocationConstraint를 지정하지 않음
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': self.region
                        }
                    )
                
                # 버킷 버전 관리 활성화
                self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={
                        'Status': 'Enabled'
                    }
                )
                
                logger.info(f"S3 bucket {self.bucket_name} created with versioning enabled")
            else:
                logger.error(f"Error accessing S3 bucket: {e}")
                raise
    
    def save_artifact(self, key: str, content: Union[str, bytes]) -> str:
        """
        아티팩트 저장
        
        Args:
            key: 아티팩트 키 (S3 객체 키)
            content: 아티팩트 내용 (문자열 또는 바이트)
            
        Returns:
            아티팩트 URI (s3://bucket/key)
        """
        try:
            # 문자열인 경우 바이트로 변환
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content
            )
            
            logger.info(f"Artifact saved to S3: {key}")
            return f"s3://{self.bucket_name}/{key}"
        except Exception as e:
            logger.error(f"Error saving artifact {key}: {e}")
            raise
    
    def get_artifact(self, key: str) -> str:
        """
        아티팩트 조회
        
        Args:
            key: 아티팩트 키 (S3 객체 키)
            
        Returns:
            아티팩트 내용 (문자열)
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # 바이트를 문자열로 변환
            content = response['Body'].read().decode('utf-8')
            
            logger.info(f"Artifact retrieved from S3: {key}")
            return content
        except Exception as e:
            logger.error(f"Error getting artifact {key}: {e}")
            raise
    
    def _get_artifact_binary(self, key: str) -> bytes:
        """
        아티팩트 바이너리 조회
        
        Args:
            key: 아티팩트 키 (S3 객체 키)
            
        Returns:
            아티팩트 내용 (바이트)
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            content = response['Body'].read()
            
            logger.info(f"Binary artifact retrieved from S3: {key}")
            return content
        except Exception as e:
            logger.error(f"Error getting binary artifact {key}: {e}")
            raise
    
    def list_artifacts(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        아티팩트 목록 조회
        
        Args:
            prefix: 아티팩트 키 접두어
            
        Returns:
            아티팩트 목록 (키, 크기, 수정일 등)
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            artifacts = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    artifacts.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            logger.info(f"Listed {len(artifacts)} artifacts with prefix: {prefix}")
            return artifacts
        except Exception as e:
            logger.error(f"Error listing artifacts with prefix {prefix}: {e}")
            return []
    
    def delete_artifact(self, key: str) -> bool:
        """
        아티팩트 삭제
        
        Args:
            key: 아티팩트 키 (S3 객체 키)
            
        Returns:
            삭제 성공 여부
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Artifact deleted from S3: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting artifact {key}: {e}")
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        아티팩트 접근을 위한 사전 서명된 URL 생성
        
        Args:
            key: 아티팩트 키 (S3 객체 키)
            expiration: URL 만료 시간 (초)
            
        Returns:
            사전 서명된 URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for artifact: {key}")
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL for artifact {key}: {e}")
            raise