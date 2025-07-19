#!/usr/bin/env python3
"""
T-Developer 프로젝트 테이블 생성 스크립트

DynamoDB에 Projects 테이블을 생성합니다.
"""
import boto3
import logging
import os
import sys
from botocore.exceptions import ClientError

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_projects_table():
    """
    DynamoDB Projects 테이블 생성
    - ProjectStore를 위한 테이블 생성
    """
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    table_name = f"{settings.DYNAMODB_TABLE_PREFIX}Projects"
    
    try:
        # 테이블이 이미 존재하는지 확인
        table = dynamodb.Table(table_name)
        table.load()
        logger.info(f"Table {table_name} already exists")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # 테이블 생성
            logger.info(f"Creating table {table_name}")
            table = dynamodb.create_table(
                TableName=table_name,
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
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            logger.info(f"Table {table_name} created successfully")
            return table
        else:
            logger.error(f"Error creating table: {e}")
            raise

def main():
    """
    프로젝트 테이블 생성 메인 함수
    """
    logger.info("Creating T-Developer Projects table")
    
    # DynamoDB 테이블 생성
    create_projects_table()
    
    logger.info("T-Developer Projects table creation completed")

if __name__ == "__main__":
    main()