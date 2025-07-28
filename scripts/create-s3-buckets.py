import boto3
import json
from botocore.exceptions import ClientError

def create_bucket_if_not_exists(s3_client, bucket_name, region):
    """S3 버킷이 없으면 생성"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ 버킷이 이미 존재함: {bucket_name}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ 버킷 생성 완료: {bucket_name}")
                
                # 버킷 정책 설정
                set_bucket_policy(s3_client, bucket_name)
                
            except ClientError as e:
                print(f"❌ 버킷 생성 실패: {e}")
        else:
            print(f"❌ 버킷 확인 실패: {e}")

def set_bucket_policy(s3_client, bucket_name):
    """버킷 정책 설정"""
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCloudFrontAccess",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )

def main():
    region = 'us-east-1'
    s3_client = boto3.client('s3', region_name=region)
    
    buckets = [
        't-developer-artifacts',
        't-developer-components',
        't-developer-templates',
        't-developer-backups'
    ]
    
    for bucket in buckets:
        create_bucket_if_not_exists(s3_client, bucket, region)

if __name__ == "__main__":
    main()