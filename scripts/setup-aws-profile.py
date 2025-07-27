#!/usr/bin/env python3
# scripts/setup-aws-profile.py
import boto3
import json
import os

def create_iam_policy():
    """T-Developer에 필요한 IAM 정책 생성"""
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:*",
                    "lambda:*",
                    "dynamodb:*",
                    "s3:*",
                    "cloudwatch:*",
                    "logs:*",
                    "iam:PassRole"
                ],
                "Resource": "*"
            }
        ]
    }
    
    return json.dumps(policy_document, indent=2)

def setup_aws_profile():
    """AWS 프로필 설정 확인"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS 계정 확인: {identity['Account']}")
        print(f"✅ 사용자 ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"❌ AWS 자격 증명 오류: {e}")
        print("💡 해결 방법:")
        print("1. AWS CLI 설치 확인: aws --version")
        print("2. AWS 자격 증명 설정: aws configure")
        print("3. 또는 환경 변수 설정:")
        print("   export AWS_ACCESS_KEY_ID=your-key")
        print("   export AWS_SECRET_ACCESS_KEY=your-secret")
        return False

if __name__ == "__main__":
    print("🔧 AWS 프로필 설정 확인 중...")
    
    if setup_aws_profile():
        print("\n📋 필요한 IAM 정책:")
        print(create_iam_policy())
        print("\n📝 다음 단계:")
        print("1. AWS Console에서 IAM 사용자 생성")
        print("2. 위 정책을 사용자에게 연결")
        print("3. Access Key/Secret Key 생성")
        print("4. aws configure 실행")
    else:
        print("\n⚠️  AWS 설정을 완료한 후 다시 실행하세요.")