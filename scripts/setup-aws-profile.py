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
        print("📋 AWS 자격 증명 설정 방법:")
        print("1. aws configure 실행")
        print("2. Access Key ID와 Secret Access Key 입력")
        print("3. 기본 리전을 us-east-1로 설정")
        return False

if __name__ == "__main__":
    if setup_aws_profile():
        print("\n📋 필요한 IAM 정책:")
        print(create_iam_policy())
        print("\n⚠️  이 정책을 IAM 사용자에게 연결하세요.")