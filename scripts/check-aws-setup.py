#!/usr/bin/env python3
# scripts/check-aws-setup.py
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_aws_account():
    """AWS 계정 생성 확인"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS 계정 생성: 완료")
        print(f"   계정 ID: {identity['Account']}")
        return True
    except Exception:
        print("❌ AWS 계정 생성: 미완료")
        return False

def check_iam_user():
    """IAM 사용자 생성 확인"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        arn = identity['Arn']
        
        if ':user/' in arn:
            print("✅ IAM 사용자 생성: 완료")
            print(f"   사용자 ARN: {arn}")
            return True
        else:
            print("⚠️  IAM 사용자 생성: Root 계정 사용 중 (권장하지 않음)")
            return False
    except Exception:
        print("❌ IAM 사용자 생성: 미완료")
        return False

def check_iam_permissions():
    """필요한 권한 정책 연결 확인"""
    required_services = ['bedrock', 'lambda', 'dynamodb', 's3', 'cloudwatch', 'logs']
    passed_services = []
    
    for service in required_services:
        try:
            if service == 'bedrock':
                client = boto3.client('bedrock')
                client.list_foundation_models()
            elif service == 'lambda':
                client = boto3.client('lambda')
                client.list_functions(MaxItems=1)
            elif service == 'dynamodb':
                client = boto3.client('dynamodb')
                client.list_tables()
            elif service == 's3':
                client = boto3.client('s3')
                client.list_buckets()
            elif service == 'cloudwatch':
                client = boto3.client('cloudwatch')
                client.list_metrics(MaxRecords=1)
            elif service == 'logs':
                client = boto3.client('logs')
                client.describe_log_groups(limit=1)
            
            passed_services.append(service)
        except ClientError as e:
            if e.response['Error']['Code'] in ['AccessDenied', 'UnauthorizedOperation']:
                continue
            else:
                passed_services.append(service)
        except Exception:
            continue
    
    if len(passed_services) >= 4:  # 최소 4개 서비스 접근 가능하면 OK
        print("✅ 필요한 권한 정책 연결: 완료")
        print(f"   접근 가능한 서비스: {', '.join(passed_services)}")
        return True
    else:
        print("❌ 필요한 권한 정책 연결: 미완료")
        print(f"   접근 가능한 서비스: {', '.join(passed_services)}")
        return False

def check_access_keys():
    """Access Key/Secret Key 생성 확인"""
    try:
        # 자격 증명이 있으면 STS 호출이 성공함
        sts = boto3.client('sts')
        sts.get_caller_identity()
        print("✅ Access Key/Secret Key 생성: 완료")
        return True
    except NoCredentialsError:
        print("❌ Access Key/Secret Key 생성: 미완료")
        return False
    except Exception:
        print("❌ Access Key/Secret Key 생성: 오류")
        return False

def check_aws_configure():
    """aws configure 실행 확인"""
    try:
        import configparser
        import os
        
        aws_config_path = os.path.expanduser('~/.aws/config')
        aws_credentials_path = os.path.expanduser('~/.aws/credentials')
        
        config_exists = os.path.exists(aws_config_path)
        credentials_exists = os.path.exists(aws_credentials_path)
        
        if config_exists and credentials_exists:
            print("✅ aws configure 실행: 완료")
            return True
        else:
            print("❌ aws configure 실행: 미완료")
            return False
    except Exception:
        print("❌ aws configure 실행: 확인 불가")
        return False

def main():
    print("🔍 AWS 설정 완료 상태 체크...")
    print("=" * 50)
    
    checks = [
        ("AWS 계정 생성", check_aws_account),
        ("IAM 사용자 생성", check_iam_user),
        ("필요한 권한 정책 연결", check_iam_permissions),
        ("Access Key/Secret Key 생성", check_access_keys),
        ("aws configure 실행", check_aws_configure)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 모든 AWS 설정이 완료되었습니다! ({passed}/{total})")
    else:
        print(f"⚠️  AWS 설정이 부분적으로 완료되었습니다. ({passed}/{total})")
        print("미완료 항목을 확인하고 설정을 완료해주세요.")

if __name__ == "__main__":
    main()