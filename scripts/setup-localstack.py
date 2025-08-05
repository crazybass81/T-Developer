#!/usr/bin/env python3
"""
LocalStack AWS 서비스 초기화 스크립트
"""

import boto3
import json
import time
from botocore.config import Config

LOCALSTACK_URL = 'http://localhost:4566'
config = Config(region_name='us-east-1', retries={'max_attempts': 10})

def create_s3_buckets():
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL, config=config)
    buckets = ['t-developer-artifacts', 't-developer-components', 't-developer-templates']
    
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"✅ S3 버킷 생성: {bucket}")
        except Exception as e:
            print(f"⚠️ 버킷 생성 실패 {bucket}: {e}")

def create_secrets():
    sm = boto3.client('secretsmanager', endpoint_url=LOCALSTACK_URL, config=config)
    secrets = {
        't-developer/dev/api-keys': {'OPENAI_API_KEY': 'sk-test-xxx', 'ANTHROPIC_API_KEY': 'sk-ant-test-xxx'}
    }
    
    for secret_name, secret_value in secrets.items():
        try:
            sm.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
            print(f"✅ Secret 생성: {secret_name}")
        except Exception as e:
            print(f"⚠️ Secret 생성 실패: {e}")

if __name__ == "__main__":
    print("🚀 LocalStack 초기화 시작...")
    time.sleep(5)
    create_s3_buckets()
    create_secrets()
    print("✅ LocalStack 초기화 완료!")