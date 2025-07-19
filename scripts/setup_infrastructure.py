#!/usr/bin/env python3
"""
T-Developer 인프라 설정 스크립트

DynamoDB 테이블과 S3 버킷을 생성합니다.
"""
import boto3
import logging
import os
import sys
import json
from botocore.exceptions import ClientError

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dynamodb_table():
    """
    DynamoDB 테이블 생성
    - TaskStore를 위한 테이블 생성
    """
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    table_name = f"{settings.DYNAMODB_TABLE_PREFIX}Tasks"
    
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
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            logger.info(f"Table {table_name} created successfully")
            return table
        else:
            logger.error(f"Error creating table: {e}")
            raise

def create_s3_bucket():
    """
    S3 버킷 생성
    - ArtifactStore를 위한 버킷 생성
    """
    s3 = boto3.client('s3', region_name=settings.AWS_REGION)
    bucket_name = settings.S3_BUCKET_NAME
    
    try:
        # 버킷이 이미 존재하는지 확인
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # 버킷 생성
            logger.info(f"Creating bucket {bucket_name}")
            
            # us-east-1 리전은 LocationConstraint를 지정하지 않음
            if settings.AWS_REGION == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': settings.AWS_REGION
                    }
                )
            
            # 버킷 버전 관리 활성화
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
            
            logger.info(f"Bucket {bucket_name} created successfully with versioning enabled")
        else:
            logger.error(f"Error creating bucket: {e}")
            raise

def setup_global_context():
    """
    글로벌 컨텍스트 설정
    - 기본 프로젝트 설정을 DynamoDB에 저장
    """
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    table_name = f"{settings.DYNAMODB_TABLE_PREFIX}Tasks"
    table = dynamodb.Table(table_name)
    
    # 글로벌 컨텍스트 정의
    global_context = {
        'task_id': 'GLOBAL_CONTEXT',
        'framework': 'FastAPI',
        'coding_style': 'PEP8',
        'test_framework': 'pytest',
        'deployment_target': 'AWS Lambda',
        'created_at': '2023-01-01T00:00:00Z',
        'status': 'ACTIVE'
    }
    
    try:
        # 글로벌 컨텍스트 저장
        table.put_item(Item=global_context)
        logger.info("Global context saved to DynamoDB")
    except ClientError as e:
        logger.error(f"Error saving global context: {e}")
        raise

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
    인프라 설정 메인 함수
    """
    logger.info("Starting T-Developer infrastructure setup")
    
    # DynamoDB 테이블 생성
    create_dynamodb_table()
    
    # Projects 테이블 생성
    create_projects_table()
    
    # S3 버킷 생성
    create_s3_bucket()
    
    # 글로벌 컨텍스트 설정
    setup_global_context()
    
    logger.info("T-Developer infrastructure setup completed")

if __name__ == "__main__":
    main()