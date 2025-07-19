"""
TaskStore - DynamoDB 기반 작업 저장소

작업(Task) 정보를 DynamoDB에 저장하고 조회하는 기능을 제공합니다.
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class TaskStore:
    """
    DynamoDB 기반 작업 저장소
    
    작업 정보를 저장하고 조회하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """TaskStore 초기화"""
        self.region = settings.AWS_REGION
        self.table_name = f"{settings.DYNAMODB_TABLE_PREFIX}Tasks"
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self._ensure_table_exists()
        logger.info(f"TaskStore initialized with table: {self.table_name}")
    
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
                        {'AttributeName': 'task_id', 'KeyType': 'HASH'}  # 파티션 키
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'task_id', 'AttributeType': 'S'},
                        {'AttributeName': 'status', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'StatusIndex',
                            'KeySchema': [
                                {'AttributeName': 'status', 'KeyType': 'HASH'}
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
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
                return table
            else:
                logger.error(f"Error accessing DynamoDB table: {e}")
                raise
    
    def save_task(self, task):
        """
        작업 정보 저장
        
        Args:
            task: Task 객체
        """
        try:
            task_dict = task.to_dict()
            self.table.put_item(Item=task_dict)
            logger.info(f"Task {task.task_id} saved to DynamoDB")
        except Exception as e:
            logger.error(f"Error saving task {task.task_id}: {e}")
            raise
    
    def get_task(self, task_id: str):
        """
        작업 정보 조회
        
        Args:
            task_id: 작업 ID
            
        Returns:
            Task 객체 또는 None
        """
        try:
            response = self.table.get_item(Key={'task_id': task_id})
            if 'Item' in response:
                from core.task import Task
                return Task.from_dict(response['Item'])
            else:
                logger.warning(f"Task {task_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            raise
    
    def update_task(self, task):
        """
        작업 정보 업데이트
        
        Args:
            task: Task 객체
        """
        try:
            self.save_task(task)
            logger.info(f"Task {task.task_id} updated in DynamoDB")
        except Exception as e:
            logger.error(f"Error updating task {task.task_id}: {e}")
            raise
    
    def find_tasks_by_status(self, status: str) -> List[Any]:
        """
        상태별 작업 목록 조회
        
        Args:
            status: 작업 상태
            
        Returns:
            Task 객체 목록
        """
        try:
            # GSI를 사용하여 상태별 조회
            # 실제 구현에서는 GSI를 사용하는 것이 효율적이지만,
            # 간단한 구현을 위해 스캔 후 필터링
            response = self.table.scan(
                FilterExpression="#status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": status}
            )
            
            tasks = []
            if 'Items' in response:
                from core.task import Task
                for item in response['Items']:
                    tasks.append(Task.from_dict(item))
            
            logger.info(f"Found {len(tasks)} tasks with status {status}")
            return tasks
        except Exception as e:
            logger.error(f"Error finding tasks by status {status}: {e}")
            return []
    
    def find_related_tasks(self, query: str, limit: int = 5) -> List[Any]:
        """
        관련 작업 검색
        
        Args:
            query: 검색어
            limit: 최대 결과 수
            
        Returns:
            Task 객체 목록
        """
        try:
            # 실제 구현에서는 ElasticSearch나 DynamoDB GSI를 사용하는 것이 효율적이지만,
            # 간단한 구현을 위해 스캔 후 필터링
            response = self.table.scan()
            
            # 검색어를 공백으로 분리하여 키워드 목록 생성
            keywords = query.lower().split()
            
            # 관련 작업 필터링
            related_tasks = []
            from core.task import Task
            
            if 'Items' in response:
                for item in response['Items']:
                    # GLOBAL_CONTEXT는 제외
                    if item.get('task_id') == 'GLOBAL_CONTEXT':
                        continue
                    
                    # 요청 내용에 키워드가 포함되어 있는지 확인
                    request = item.get('request', '').lower()
                    if any(keyword in request for keyword in keywords):
                        related_tasks.append(Task.from_dict(item))
            
            # 최신순으로 정렬
            related_tasks.sort(key=lambda x: x.created_at, reverse=True)
            
            # 최대 결과 수 제한
            related_tasks = related_tasks[:limit]
            
            logger.info(f"Found {len(related_tasks)} related tasks for query: {query}")
            return related_tasks
        except Exception as e:
            logger.error(f"Error finding related tasks for query {query}: {e}")
            return []
    
    def get_global_context(self) -> Dict[str, Any]:
        """
        글로벌 컨텍스트 조회
        
        Returns:
            글로벌 컨텍스트 정보
        """
        try:
            response = self.table.get_item(Key={'task_id': 'GLOBAL_CONTEXT'})
            if 'Item' in response:
                return response['Item']
            else:
                # 기본 글로벌 컨텍스트 반환
                logger.warning("Global context not found, returning default")
                return {
                    'framework': 'FastAPI',
                    'coding_style': 'PEP8',
                    'test_framework': 'pytest',
                    'deployment_target': 'AWS Lambda'
                }
        except Exception as e:
            logger.error(f"Error getting global context: {e}")
            # 오류 발생 시 기본값 반환
            return {
                'framework': 'FastAPI',
                'coding_style': 'PEP8',
                'test_framework': 'pytest',
                'deployment_target': 'AWS Lambda'
            }
    
    def save_global_context(self, context: Dict[str, Any]) -> None:
        """
        글로벌 컨텍스트 저장
        
        Args:
            context: 글로벌 컨텍스트 정보
        """
        try:
            # task_id를 GLOBAL_CONTEXT로 설정
            context['task_id'] = 'GLOBAL_CONTEXT'
            
            # 기존 컨텍스트가 있으면 병합
            existing_context = self.get_global_context()
            if existing_context and isinstance(existing_context, dict):
                # 기존 task_id는 유지
                existing_context.update(context)
                context = existing_context
            
            # DynamoDB에 저장
            self.table.put_item(Item=context)
            logger.info("Global context saved to DynamoDB")
        except Exception as e:
            logger.error(f"Error saving global context: {e}")
            raise