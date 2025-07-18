"""
ProjectStore - DynamoDB 기반 프로젝트 저장소

이 모듈은 DynamoDB를 사용하여 프로젝트 정보를 저장하고 관리하는 기능을 제공합니다.
"""
import logging
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, List, Optional, Any

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
        
        # DynamoDB 리소스 생성
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        
        # 테이블 존재 확인 및 생성
        self._ensure_table_exists()
        
        logger.info(f"ProjectStore initialized with table: {self.table_name}")
    
    def _ensure_table_exists(self) -> None:
        """
        테이블이 존재하는지 확인하고, 없으면 생성
        """
        try:
            # 테이블 존재 여부 확인
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            logger.info(f"Table {self.table_name} already exists")
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # 테이블 생성
            logger.info(f"Creating table {self.table_name}")
            
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'project_id',
                        'KeyType': 'HASH'  # 파티션 키
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'project_id',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
            # 테이블 생성 완료 대기
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            logger.info(f"Table {self.table_name} created successfully")
    
    def save_project(self, project_data: Dict[str, Any]) -> str:
        """
        프로젝트 정보 저장
        
        Args:
            project_data: 저장할 프로젝트 정보
            
        Returns:
            저장된 프로젝트 ID
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # 프로젝트 ID가 없으면 이름을 ID로 사용
            if 'project_id' not in project_data:
                project_data['project_id'] = project_data['name'].lower().replace(' ', '-')
            
            # 프로젝트 정보 저장
            table.put_item(Item=project_data)
            
            logger.info(f"Project {project_data['project_id']} saved successfully")
            return project_data['project_id']
        
        except Exception as e:
            logger.error(f"Failed to save project: {str(e)}", exc_info=True)
            raise
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        프로젝트 정보 조회
        
        Args:
            project_id: 조회할 프로젝트 ID
            
        Returns:
            프로젝트 정보 (없으면 None)
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # 프로젝트 조회
            response = table.get_item(Key={'project_id': project_id})
            
            # 결과 반환
            if 'Item' in response:
                return response['Item']
            else:
                logger.warning(f"Project {project_id} not found")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}", exc_info=True)
            raise
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        모든 프로젝트 목록 조회
        
        Returns:
            프로젝트 목록
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # 모든 프로젝트 스캔
            response = table.scan()
            
            # 결과 반환
            projects = response.get('Items', [])
            logger.info(f"Found {len(projects)} projects")
            return projects
        
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}", exc_info=True)
            raise
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> None:
        """
        프로젝트 정보 업데이트
        
        Args:
            project_id: 업데이트할 프로젝트 ID
            updates: 업데이트할 필드와 값
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # 업데이트 표현식 생성
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in updates.items():
                if key != 'project_id':  # 키는 업데이트 불가
                    update_expression += f"{key} = :{key.replace('-', '_')}, "
                    expression_attribute_values[f":{key.replace('-', '_')}"] = value
            
            # 마지막 쉼표 제거
            update_expression = update_expression[:-2]
            
            # 프로젝트 업데이트
            if expression_attribute_values:
                table.update_item(
                    Key={'project_id': project_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values
                )
                
                logger.info(f"Project {project_id} updated successfully")
        
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {str(e)}", exc_info=True)
            raise
    
    def delete_project(self, project_id: str) -> None:
        """
        프로젝트 삭제
        
        Args:
            project_id: 삭제할 프로젝트 ID
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # 프로젝트 삭제
            table.delete_item(Key={'project_id': project_id})
            
            logger.info(f"Project {project_id} deleted successfully")
        
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {str(e)}", exc_info=True)
            raise