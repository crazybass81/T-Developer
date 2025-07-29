import boto3
import json
from botocore.config import Config

# LocalStack 설정
LOCALSTACK_URL = 'http://localhost:4566'
config = Config(region_name='us-east-1')

def test_s3():
    """S3 서비스 테스트"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL, config=config)
    
    try:
        # 버킷 목록 조회
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print(f"✅ S3 버킷 목록: {buckets}")
        
        # 테스트 파일 업로드
        s3.put_object(
            Bucket='t-developer-artifacts',
            Key='test.txt',
            Body='Hello LocalStack!'
        )
        print("✅ S3 파일 업로드 성공")
        
    except Exception as e:
        print(f"❌ S3 테스트 실패: {e}")

def test_secrets_manager():
    """Secrets Manager 테스트"""
    sm = boto3.client('secretsmanager', endpoint_url=LOCALSTACK_URL, config=config)
    
    try:
        # 시크릿 조회
        response = sm.get_secret_value(SecretId='t-developer/dev/api-keys')
        secrets = json.loads(response['SecretString'])
        print(f"✅ Secrets Manager 조회 성공: {list(secrets.keys())}")
        
    except Exception as e:
        print(f"❌ Secrets Manager 테스트 실패: {e}")

def test_lambda():
    """Lambda 서비스 테스트"""
    lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_URL, config=config)
    
    try:
        # 함수 목록 조회
        response = lambda_client.list_functions()
        functions = [func['FunctionName'] for func in response['Functions']]
        print(f"✅ Lambda 함수 목록: {functions}")
        
        # 함수 호출 테스트
        if functions:
            invoke_response = lambda_client.invoke(
                FunctionName=functions[0],
                Payload=json.dumps({'test': 'data'})
            )
            print("✅ Lambda 함수 호출 성공")
            
    except Exception as e:
        print(f"❌ Lambda 테스트 실패: {e}")

def main():
    print("🧪 LocalStack 서비스 테스트 시작...")
    
    test_s3()
    test_secrets_manager()
    test_lambda()
    
    print("\n✅ LocalStack 테스트 완료!")

if __name__ == "__main__":
    main()