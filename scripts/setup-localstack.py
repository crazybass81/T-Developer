import boto3
import json
import time
from botocore.config import Config

# LocalStack 설정
config = Config(
    region_name='us-east-1',
    retries={'max_attempts': 10, 'mode': 'standard'}
)

# LocalStack 엔드포인트
LOCALSTACK_URL = 'http://localhost:4566'

def create_s3_buckets():
    """S3 버킷 생성"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL, config=config)
    
    buckets = [
        't-developer-artifacts',
        't-developer-components',
        't-developer-templates',
        't-developer-test-data'
    ]
    
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"✅ S3 버킷 생성: {bucket}")
            
            # 버킷 정책 설정
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket}/*"
                }]
            }
            s3.put_bucket_policy(
                Bucket=bucket,
                Policy=json.dumps(bucket_policy)
            )
        except Exception as e:
            print(f"⚠️  버킷 생성 실패 {bucket}: {e}")

def create_secrets():
    """Secrets Manager 시크릿 생성"""
    sm = boto3.client('secretsmanager', endpoint_url=LOCALSTACK_URL, config=config)
    
    secrets = {
        't-developer/dev/api-keys': {
            'OPENAI_API_KEY': 'sk-test-xxx',
            'ANTHROPIC_API_KEY': 'sk-ant-test-xxx'
        },
        't-developer/dev/database': {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 't_developer',
            'DB_USER': 'developer',
            'DB_PASSWORD': 'devpassword'
        }
    }
    
    for secret_name, secret_value in secrets.items():
        try:
            sm.create_secret(
                Name=secret_name,
                SecretString=json.dumps(secret_value)
            )
            print(f"✅ Secret 생성: {secret_name}")
        except Exception as e:
            print(f"⚠️  Secret 생성 실패: {e}")

def create_lambda_functions():
    """Lambda 함수 스텁 생성"""
    lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_URL, config=config)
    
    functions = [
        {
            'FunctionName': 't-developer-nl-processor',
            'Runtime': 'nodejs18.x',
            'Role': 'arn:aws:iam::123456789012:role/lambda-role',
            'Handler': 'index.handler',
            'Code': {'ZipFile': b'exports.handler = async (event) => { return { statusCode: 200, body: "OK" }; };'},
            'Timeout': 300,
            'MemorySize': 512
        }
    ]
    
    for func in functions:
        try:
            lambda_client.create_function(**func)
            print(f"✅ Lambda 함수 생성: {func['FunctionName']}")
        except Exception as e:
            print(f"⚠️  Lambda 생성 실패: {e}")

def setup_cloudwatch():
    """CloudWatch 로그 그룹 생성"""
    logs = boto3.client('logs', endpoint_url=LOCALSTACK_URL, config=config)
    
    log_groups = [
        '/aws/lambda/t-developer-agents',
        '/aws/ecs/t-developer-api',
        '/t-developer/application'
    ]
    
    for log_group in log_groups:
        try:
            logs.create_log_group(logGroupName=log_group)
            print(f"✅ 로그 그룹 생성: {log_group}")
        except Exception as e:
            print(f"⚠️  로그 그룹 생성 실패: {e}")

def main():
    print("🚀 LocalStack 초기화 시작...")
    
    # LocalStack 준비 대기
    time.sleep(10)
    
    create_s3_buckets()
    create_lambda_functions()
    create_secrets()
    setup_cloudwatch()
    
    print("\n✅ LocalStack 초기화 완료!")
    print("📋 사용 가능한 서비스:")
    print("- S3: http://localhost:4566")
    print("- Lambda: http://localhost:4566")
    print("- Secrets Manager: http://localhost:4566")
    print("- CloudWatch: http://localhost:4566")

if __name__ == "__main__":
    main()