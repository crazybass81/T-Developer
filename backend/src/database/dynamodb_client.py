"""
DynamoDB Client
AWS DynamoDB 클라이언트 및 테이블 관리
"""

import logging
import os
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB 클라이언트 래퍼"""

    def __init__(self):
        """DynamoDB 클라이언트 초기화"""
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.testing = os.getenv("TESTING", "false").lower() == "true"

        if self.testing:
            # 테스트 환경에서는 로컬 DynamoDB 사용
            self.client = boto3.client(
                "dynamodb",
                endpoint_url="http://localhost:8000",
                region_name="us-east-1",
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
            self.resource = boto3.resource(
                "dynamodb",
                endpoint_url="http://localhost:8000",
                region_name="us-east-1",
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
        else:
            # 프로덕션/개발 환경
            self.client = boto3.client("dynamodb", region_name=self.region)
            self.resource = boto3.resource("dynamodb", region_name=self.region)

        # 테이블 이름 프리픽스
        self.table_prefix = f"t-developer-{self.environment}"

        # 테이블 정의
        self.tables = {
            "projects": f"{self.table_prefix}-projects",
            "users": f"{self.table_prefix}-users",
            "agents": f"{self.table_prefix}-agents",
            "sessions": f"{self.table_prefix}-sessions",
        }

        # 테이블 생성 (개발/테스트 환경에서만)
        if self.environment in ["development", "testing"]:
            self._create_tables_if_not_exists()

    def _create_tables_if_not_exists(self):
        """필요한 테이블이 없으면 생성"""

        # Projects 테이블
        self._create_table(
            self.tables["projects"],
            [
                {"AttributeName": "project_id", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            [
                {"AttributeName": "project_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "N"},
                {"AttributeName": "user_id", "AttributeType": "S"},
            ],
            [
                {
                    "IndexName": "UserIndex",
                    "Keys": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )

        # Users 테이블
        self._create_table(
            self.tables["users"],
            [{"AttributeName": "user_id", "KeyType": "HASH"}],
            [
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            [
                {
                    "IndexName": "EmailIndex",
                    "Keys": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )

        # Agents 테이블
        self._create_table(
            self.tables["agents"],
            [
                {"AttributeName": "agent_id", "KeyType": "HASH"},
                {"AttributeName": "version", "KeyType": "RANGE"},
            ],
            [
                {"AttributeName": "agent_id", "AttributeType": "S"},
                {"AttributeName": "version", "AttributeType": "N"},
            ],
        )

        # Sessions 테이블
        self._create_table(
            self.tables["sessions"],
            [{"AttributeName": "session_id", "KeyType": "HASH"}],
            [{"AttributeName": "session_id", "AttributeType": "S"}],
        )

    def _create_table(
        self,
        table_name: str,
        key_schema: List[Dict],
        attribute_definitions: List[Dict],
        global_secondary_indexes: Optional[List[Dict]] = None,
    ):
        """테이블 생성"""
        try:
            # 테이블이 이미 존재하는지 확인
            self.client.describe_table(TableName=table_name)
            logger.info(f"Table {table_name} already exists")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # 테이블이 없으면 생성
                create_params = {
                    "TableName": table_name,
                    "KeySchema": key_schema,
                    "AttributeDefinitions": attribute_definitions,
                    "BillingMode": "PAY_PER_REQUEST",  # On-demand billing
                }

                if global_secondary_indexes:
                    # GSI에 대한 ProvisionedThroughput 제거 (PAY_PER_REQUEST 모드에서는 불필요)
                    for gsi in global_secondary_indexes:
                        if "ProvisionedThroughput" in gsi:
                            del gsi["ProvisionedThroughput"]
                    create_params["GlobalSecondaryIndexes"] = global_secondary_indexes

                try:
                    self.client.create_table(**create_params)
                    logger.info(f"Created table {table_name}")

                    # 테이블이 활성화될 때까지 대기
                    waiter = self.client.get_waiter("table_exists")
                    waiter.wait(TableName=table_name)
                except ClientError as create_error:
                    logger.error(f"Error creating table {table_name}: {create_error}")
            else:
                logger.error(f"Error checking table {table_name}: {e}")

    def get_table(self, table_type: str):
        """테이블 객체 반환"""
        table_name = self.tables.get(table_type)
        if not table_name:
            raise ValueError(f"Unknown table type: {table_type}")
        return self.resource.Table(table_name)

    # CRUD Operations
    async def put_item(self, table_type: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """아이템 저장"""
        table = self.get_table(table_type)
        try:
            response = table.put_item(Item=item)
            return response
        except ClientError as e:
            logger.error(f"Error putting item to {table_type}: {e}")
            raise

    async def get_item(self, table_type: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """아이템 조회"""
        table = self.get_table(table_type)
        try:
            response = table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Error getting item from {table_type}: {e}")
            raise

    async def query(
        self,
        table_type: str,
        key_condition_expression: Any,
        filter_expression: Optional[Any] = None,
        index_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """쿼리 실행"""
        table = self.get_table(table_type)
        try:
            query_params = {"KeyConditionExpression": key_condition_expression}

            if filter_expression:
                query_params["FilterExpression"] = filter_expression

            if index_name:
                query_params["IndexName"] = index_name

            response = table.query(**query_params)
            return response.get("Items", [])
        except ClientError as e:
            logger.error(f"Error querying {table_type}: {e}")
            raise

    async def delete_item(self, table_type: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """아이템 삭제"""
        table = self.get_table(table_type)
        try:
            response = table.delete_item(Key=key)
            return response
        except ClientError as e:
            logger.error(f"Error deleting item from {table_type}: {e}")
            raise

    async def update_item(
        self,
        table_type: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """아이템 업데이트"""
        table = self.get_table(table_type)
        try:
            update_params = {
                "Key": key,
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_attribute_values,
                "ReturnValues": "ALL_NEW",
            }

            if expression_attribute_names:
                update_params["ExpressionAttributeNames"] = expression_attribute_names

            response = table.update_item(**update_params)
            return response.get("Attributes", {})
        except ClientError as e:
            logger.error(f"Error updating item in {table_type}: {e}")
            raise


# Singleton instance
_dynamodb_client = None


def get_dynamodb_client() -> DynamoDBClient:
    """DynamoDB 클라이언트 인스턴스 반환"""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient()
    return _dynamodb_client
