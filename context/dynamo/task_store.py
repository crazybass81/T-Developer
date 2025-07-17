"""
TaskStore - DynamoDB를 사용한 작업 저장소

이 모듈은 DynamoDB를 사용하여 T-Developer 작업 정보를 저장하고 검색하는 기능을 제공합니다.
"""
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, List, Optional, Any

from config import settings
from core.task import Task, TaskStatus

# 로깅 설정
logger = logging.getLogger(__name__)

class TaskStore:
    """
    DynamoDB를 사용한 작업 저장소
    
    작업 정보를 저장하고 검색하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """TaskStore 초기화"""
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table_name = settings.CONTEXT_STORAGE["dynamo"]["task_table"]
        self._ensure_table_exists()
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"TaskStore initialized with table: {self.table_name}")
    
    def save_task(self, task: Task) -> None:
        """
        작업 정보 저장
        
        Args:
            task: 저장할 작업 객체
        """
        logger.info(f"Saving task {task.task_id}")
        
        # 작업 객체를 딕셔너리로 변환
        task_dict = task.to_dict()
        
        # DynamoDB에 저장
        try:
            self.table.put_item(Item=task_dict)
            logger.info(f"Task {task.task_id} saved successfully")
        except Exception as e:
            logger.error(f"Failed to save task {task.task_id}: {str(e)}", exc_info=True)
            raise
    
    def update_task(self, task: Task) -> None:
        """
        작업 정보 업데이트
        
        Args:
            task: 업데이트할 작업 객체
        """
        logger.info(f"Updating task {task.task_id}")
        
        # 작업 객체를 딕셔너리로 변환
        task_dict = task.to_dict()
        
        # DynamoDB에 업데이트
        try:
            self.save_task(task)  # 간단하게 전체 항목 덮어쓰기
            logger.info(f"Task {task.task_id} updated successfully")
        except Exception as e:
            logger.error(f"Failed to update task {task.task_id}: {str(e)}", exc_info=True)
            raise
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        작업 정보 조회
        
        Args:
            task_id: 조회할 작업 ID
            
        Returns:
            조회된 작업 객체 또는 None
        """
        logger.info(f"Getting task {task_id}")
        
        try:
            response = self.table.get_item(Key={"task_id": task_id})
            
            if "Item" in response:
                task_dict = response["Item"]
                return Task.from_dict(task_dict)
            else:
                logger.warning(f"Task {task_id} not found")
                return None
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {str(e)}", exc_info=True)
            raise
    
    def find_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        상태별 작업 목록 조회
        
        Args:
            status: 조회할 작업 상태
            
        Returns:
            조회된 작업 객체 목록
        """
        logger.info(f"Finding tasks with status {status}")
        
        try:
            # GSI를 사용하여 상태별 조회 (실제 구현에서는 GSI 생성 필요)
            # 여기서는 스캔으로 대체
            response = self.table.scan(
                FilterExpression=Attr("status").eq(status.value)
            )
            
            tasks = []
            for item in response.get("Items", []):
                tasks.append(Task.from_dict(item))
            
            logger.info(f"Found {len(tasks)} tasks with status {status}")
            return tasks
        except Exception as e:
            logger.error(f"Failed to find tasks by status {status}: {str(e)}", exc_info=True)
            raise
    
    def find_related_tasks(self, query: str) -> List[Dict[str, Any]]:
        """
        관련 작업 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            관련 작업 정보 목록
        """
        logger.info(f"Finding tasks related to: {query[:50]}...")
        
        # 검색어를 키워드로 분리
        keywords = [kw.lower() for kw in query.split() if len(kw) > 3]
        
        try:
            # 실제 구현에서는 효율적인 검색 방법 사용 (예: GSI, ElasticSearch 등)
            # 여기서는 간단한 스캔으로 대체
            response = self.table.scan()
            
            related_tasks = []
            for item in response.get("Items", []):
                request = item.get("request", "").lower()
                
                # 키워드 매칭
                if any(kw in request for kw in keywords):
                    related_tasks.append({
                        "task_id": item.get("task_id"),
                        "request": item.get("request"),
                        "status": item.get("status"),
                        "created_at": item.get("created_at")
                    })
            
            # 최근 작업 우선 정렬 (최대 5개)
            related_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            related_tasks = related_tasks[:5]
            
            logger.info(f"Found {len(related_tasks)} related tasks")
            return related_tasks
        except Exception as e:
            logger.error(f"Failed to find related tasks: {str(e)}", exc_info=True)
            return []
    
    def get_global_context(self) -> Dict[str, Any]:
        """
        글로벌 컨텍스트 조회
        
        Returns:
            글로벌 컨텍스트 정보
        """
        logger.info("Getting global context")
        
        try:
            # 글로벌 컨텍스트는 특별한 task_id로 저장
            response = self.table.get_item(Key={"task_id": "GLOBAL_CONTEXT"})
            
            if "Item" in response:
                return response["Item"].get("context", {})
            else:
                # 기본 글로벌 컨텍스트
                return {
                    "framework": "FastAPI (Python)",
                    "coding_style": "PEP8",
                    "test_framework": "pytest",
                    "deployment_target": "AWS Lambda"
                }
        except Exception as e:
            logger.error(f"Failed to get global context: {str(e)}", exc_info=True)
            # 오류 시 기본값 반환
            return {
                "framework": "FastAPI (Python)",
                "coding_style": "PEP8"
            }
    
    def _ensure_table_exists(self) -> None:
        """
        DynamoDB 테이블 존재 확인 및 생성
        """
        client = boto3.client('dynamodb', region_name=settings.AWS_REGION)
        
        try:
            # 테이블 존재 확인
            client.describe_table(TableName=self.table_name)
            logger.info(f"Table {self.table_name} already exists")
        except client.exceptions.ResourceNotFoundException:
            # 테이블 생성
            logger.info(f"Creating table {self.table_name}")
            
            try:
                client.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'task_id',
                            'KeyType': 'HASH'  # 파티션 키
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'task_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # 테이블 생성 완료 대기
                waiter = client.get_waiter('table_exists')
                waiter.wait(TableName=self.table_name)
                logger.info(f"Table {self.table_name} created successfully")
            except Exception as e:
                logger.error(f"Failed to create table {self.table_name}: {str(e)}", exc_info=True)
                raise