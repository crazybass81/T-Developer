#!/usr/bin/env python3
import boto3
import json

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
        print("💡 해결 방법: aws configure 명령으로 자격 증명을 설정하세요")
        return False

if __name__ == "__main__":
    print("🔍 AWS 계정 설정 확인 중...")
    
    if setup_aws_profile():
        print("\n📋 필요한 IAM 정책:")
        print(create_iam_policy())
        print("\n✅ AWS 설정이 완료되었습니다!")
    else:
        print("\n❌ AWS 설정을 완료한 후 다시 실행하세요")
        exit(1)