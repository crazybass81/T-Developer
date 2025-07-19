"""
ProjectStore - DynamoDB 기반 프로젝트 저장소

프로젝트 정보를 DynamoDB에 저장하고 조회하는 기능을 제공합니다.
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class ProjectStore:
    """
    DynamoDB 기반 프로젝트 저장소
    
    프로젝트 정보를 저장하고 조회하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """ProjectStore 초기화"""
        self.region = settings.AWS_REGION
        self.table_name = f"{settings.DYNAMODB_TABLE_PREFIX}Projects"
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self._ensure_table_exists()
        logger.info(f"ProjectStore initialized with table: {self.table_name}")
    
    def _ensure_table_exists(self):
        """
        테이블이 존재하는지 확인하고, 없으면 생성
        
        Returns:
            DynamoDB 테이블 객체
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table: {self.table_name}")
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'project_id', 'KeyType': 'HASH'}  # 파티션 키
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'project_id', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                # 테이블 생성 완료 대기
                table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
                logger.info(f"Table {self.table_name} created successfully")
                return table
            else:
                logger.error(f"Error accessing DynamoDB table: {e}")
                raise
    
    def save_project(self, project: Dict[str, Any]):
        """
        프로젝트 정보 저장
        
        Args:
            project: 프로젝트 정보 딕셔너리
        """
        try:
            self.table.put_item(Item=project)
            logger.info(f"Project {project['project_id']} saved to DynamoDB")
        except Exception as e:
            logger.error(f"Error saving project {project.get('project_id')}: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        프로젝트 정보 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            프로젝트 정보 딕셔너리 또는 None
        """
        try:
            response = self.table.get_item(Key={'project_id': project_id})
            if 'Item' in response:
                return response['Item']
            else:
                logger.warning(f"Project {project_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            raise
    
    def update_project(self, project: Dict[str, Any]):
        """
        프로젝트 정보 업데이트
        
        Args:
            project: 프로젝트 정보 딕셔너리
        """
        try:
            self.save_project(project)
            logger.info(f"Project {project['project_id']} updated in DynamoDB")
        except Exception as e:
            logger.error(f"Error updating project {project['project_id']}: {e}")
            raise
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        프로젝트 목록 조회
        
        Returns:
            프로젝트 정보 딕셔너리 목록
        """
        try:
            response = self.table.scan()
            projects = response.get('Items', [])
            
            # 생성일 기준 내림차순 정렬
            projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logger.info(f"Found {len(projects)} projects")
            return projects
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []
    
    def delete_project(self, project_id: str) -> bool:
        """
        프로젝트 삭제
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            self.table.delete_item(Key={'project_id': project_id})
            logger.info(f"Project {project_id} deleted from DynamoDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False