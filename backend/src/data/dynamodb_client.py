"""
T-Developer MVP - DynamoDB Client

DynamoDB 연결 및 기본 데이터 작업
"""

import boto3
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime

@dataclass
class TableConfig:
    table_name: str
    partition_key: str
    sort_key: Optional[str] = None
    gsi_configs: List[Dict[str, str]] = None

class DynamoDBClient:
    """DynamoDB 클라이언트"""
    
    def __init__(self):
        # 로컬 개발환경 지원
        if os.getenv('NODE_ENV') == 'development':
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000',
                region_name='us-east-1',
                aws_access_key_id='local',
                aws_secret_access_key='local'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb')
        
        self.table_configs = {
            'projects': TableConfig(
                table_name='T-Developer-Projects',
                partition_key='PK',
                sort_key='SK'
            ),
            'agents': TableConfig(
                table_name='T-Developer-Agents',
                partition_key='PK',
                sort_key='SK'
            ),
            'sessions': TableConfig(
                table_name='T-Developer-Sessions',
                partition_key='PK',
                sort_key='SK'
            )
        }
    
    async def create_tables_if_not_exist(self):
        """테이블이 없으면 생성"""
        for config in self.table_configs.values():
            await self._create_table_if_not_exist(config)
    
    async def _create_table_if_not_exist(self, config: TableConfig):
        """단일 테이블 생성"""
        try:
            table = self.dynamodb.Table(config.table_name)
            table.load()
            print(f"Table {config.table_name} already exists")
        except Exception:
            # 테이블 생성
            key_schema = [
                {'AttributeName': config.partition_key, 'KeyType': 'HASH'}
            ]
            
            attribute_definitions = [
                {'AttributeName': config.partition_key, 'AttributeType': 'S'}
            ]
            
            if config.sort_key:
                key_schema.append({'AttributeName': config.sort_key, 'KeyType': 'RANGE'})
                attribute_definitions.append({'AttributeName': config.sort_key, 'AttributeType': 'S'})
            
            table = self.dynamodb.create_table(
                TableName=config.table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode='PAY_PER_REQUEST'
            )
            
            # 테이블 생성 완료 대기
            table.wait_until_exists()
            print(f"Created table {config.table_name}")
    
    async def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """아이템 저장"""
        try:
            config = self.table_configs.get(table_name)
            if not config:
                raise ValueError(f"Unknown table: {table_name}")
            
            table = self.dynamodb.Table(config.table_name)
            
            # 타임스탬프 자동 추가
            item['CreatedAt'] = datetime.utcnow().isoformat()
            item['UpdatedAt'] = datetime.utcnow().isoformat()
            
            table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error putting item: {str(e)}")
            return False
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """아이템 조회"""
        try:
            config = self.table_configs.get(table_name)
            if not config:
                raise ValueError(f"Unknown table: {table_name}")
            
            table = self.dynamodb.Table(config.table_name)
            response = table.get_item(Key=key)
            
            return response.get('Item')
            
        except Exception as e:
            print(f"Error getting item: {str(e)}")
            return None
    
    async def query_items(
        self, 
        table_name: str, 
        partition_key_value: str,
        sort_key_condition: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """아이템 쿼리"""
        try:
            config = self.table_configs.get(table_name)
            if not config:
                raise ValueError(f"Unknown table: {table_name}")
            
            table = self.dynamodb.Table(config.table_name)
            
            key_condition = f"{config.partition_key} = :pk"
            expression_values = {':pk': partition_key_value}
            
            if sort_key_condition and config.sort_key:
                key_condition += f" AND {sort_key_condition}"
            
            response = table.query(
                KeyConditionExpression=key_condition,
                ExpressionAttributeValues=expression_values,
                Limit=limit
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"Error querying items: {str(e)}")
            return []
    
    async def update_item(
        self, 
        table_name: str, 
        key: Dict[str, Any], 
        updates: Dict[str, Any]
    ) -> bool:
        """아이템 업데이트"""
        try:
            config = self.table_configs.get(table_name)
            if not config:
                raise ValueError(f"Unknown table: {table_name}")
            
            table = self.dynamodb.Table(config.table_name)
            
            # 업데이트 표현식 생성
            update_expression = "SET "
            expression_values = {}
            
            for field, value in updates.items():
                update_expression += f"{field} = :{field}, "
                expression_values[f":{field}"] = value
            
            # UpdatedAt 자동 추가
            update_expression += "UpdatedAt = :updated_at"
            expression_values[':updated_at'] = datetime.utcnow().isoformat()
            
            table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating item: {str(e)}")
            return False

# 전역 클라이언트 인스턴스
db_client = DynamoDBClient()

async def initialize_database():
    """데이터베이스 초기화"""
    await db_client.create_tables_if_not_exist()
    print("Database initialization completed")