"""
ArtifactStore - S3를 사용한 아티팩트 저장소

이 모듈은 AWS S3를 사용하여 T-Developer 아티팩트(계획, 로그, 결과물 등)를 저장하고 검색하는 기능을 제공합니다.
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Any, BinaryIO, Union

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class ArtifactStore:
    """
    S3를 사용한 아티팩트 저장소
    
    계획, 로그, 결과물 등의 아티팩트를 저장하고 검색하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """ArtifactStore 초기화"""
        self.s3 = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket_name = settings.CONTEXT_STORAGE["s3"]["bucket"]
        self._ensure_bucket_exists()
        logger.info(f"ArtifactStore initialized with bucket: {self.bucket_name}")
    
    def save_artifact(self, key: str, content: Union[str, bytes, BinaryIO]) -> str:
        """
        아티팩트 저장
        
        Args:
            key: 저장할 객체 키 (경로 포함)
            content: 저장할 내용 (문자열, 바이트 또는 파일 객체)
            
        Returns:
            저장된 객체의 S3 URI
        """
        logger.info(f"Saving artifact to {key}")
        
        try:
            # 문자열인 경우 바이트로 변환
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # S3에 저장
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content
            )
            
            s3_uri = f"s3://{self.bucket_name}/{key}"
            logger.info(f"Artifact saved to {s3_uri}")
            return s3_uri
        except Exception as e:
            logger.error(f"Failed to save artifact to {key}: {str(e)}", exc_info=True)
            raise
    
    def get_artifact(self, key: str) -> str:
        """
        아티팩트 조회
        
        Args:
            key: 조회할 객체 키 (경로 포함)
            
        Returns:
            조회된 내용 (문자열)
        """
        logger.info(f"Getting artifact from {key}")
        
        try:
            # S3에서 조회
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # 응답 본문을 문자열로 변환
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Artifact retrieved from {key} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Failed to get artifact from {key}: {str(e)}", exc_info=True)
            raise
    
    def get_artifact_binary(self, key: str) -> bytes:
        """
        바이너리 아티팩트 조회
        
        Args:
            key: 조회할 객체 키 (경로 포함)
            
        Returns:
            조회된 내용 (바이트)
        """
        logger.info(f"Getting binary artifact from {key}")
        
        try:
            # S3에서 조회
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # 응답 본문을 바이트로 반환
            content = response['Body'].read()
            logger.info(f"Binary artifact retrieved from {key} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Failed to get binary artifact from {key}: {str(e)}", exc_info=True)
            raise
    
    def list_artifacts(self, prefix: str) -> List[Dict[str, Any]]:
        """
        아티팩트 목록 조회
        
        Args:
            prefix: 조회할 객체 접두사 (경로)
            
        Returns:
            조회된 객체 정보 목록
        """
        logger.info(f"Listing artifacts with prefix {prefix}")
        
        try:
            # S3 객체 목록 조회
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            artifacts = []
            for obj in response.get('Contents', []):
                artifacts.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'uri': f"s3://{self.bucket_name}/{obj['Key']}"
                })
            
            logger.info(f"Found {len(artifacts)} artifacts with prefix {prefix}")
            return artifacts
        except Exception as e:
            logger.error(f"Failed to list artifacts with prefix {prefix}: {str(e)}", exc_info=True)
            return []
    
    def delete_artifact(self, key: str) -> bool:
        """
        아티팩트 삭제
        
        Args:
            key: 삭제할 객체 키 (경로 포함)
            
        Returns:
            삭제 성공 여부
        """
        logger.info(f"Deleting artifact {key}")
        
        try:
            # S3에서 삭제
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Artifact {key} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete artifact {key}: {str(e)}", exc_info=True)
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        미리 서명된 URL 생성
        
        Args:
            key: 객체 키 (경로 포함)
            expiration: URL 만료 시간 (초)
            
        Returns:
            미리 서명된 URL
        """
        logger.info(f"Generating presigned URL for {key} (expires in {expiration}s)")
        
        try:
            # 미리 서명된 URL 생성
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Presigned URL generated for {key}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {key}: {str(e)}", exc_info=True)
            raise
    
    def _ensure_bucket_exists(self) -> None:
        """
        S3 버킷 존재 확인 및 생성
        """
        try:
            # 버킷 존재 확인
            self.s3.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            
            if error_code == '404':
                # 버킷 생성
                logger.info(f"Creating bucket {self.bucket_name}")
                
                try:
                    # 리전이 us-east-1이 아닌 경우 LocationConstraint 설정
                    if settings.AWS_REGION == 'us-east-1':
                        self.s3.create_bucket(
                            Bucket=self.bucket_name
                        )
                    else:
                        self.s3.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': settings.AWS_REGION
                            }
                        )
                    
                    # 버전 관리 활성화
                    self.s3.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={
                            'Status': 'Enabled'
                        }
                    )
                    
                    logger.info(f"Bucket {self.bucket_name} created successfully with versioning enabled")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {str(create_error)}", exc_info=True)
                    raise
            else:
                logger.error(f"Failed to check bucket {self.bucket_name}: {str(e)}", exc_info=True)
                raise