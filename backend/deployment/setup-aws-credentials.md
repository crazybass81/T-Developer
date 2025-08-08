# AWS 자격 증명 설정 가이드

## 자격 증명 설정 방법

### 방법 1: AWS Access Key 사용

1. AWS Console에 로그인
2. IAM → Users → Your User → Security credentials
3. Access keys → Create access key
4. 아래 명령 실행:

```bash
cd /home/ec2-user/T-DeveloperMVP/backend/deployment
./aws-setup.sh
```

옵션 1을 선택하고 다음 정보 입력:
- AWS Access Key ID: YOUR_ACCESS_KEY
- AWS Secret Access Key: YOUR_SECRET_KEY
- Default Region: us-east-1 (또는 원하는 리전)

### 방법 2: EC2 IAM Role 사용 (권장)

1. AWS Console → EC2 → Instances
2. 현재 인스턴스 선택
3. Actions → Security → Modify IAM role
4. 다음 권한이 있는 Role 연결:
   - AmazonEC2FullAccess
   - AmazonECSFullAccess
   - AWSLambda_FullAccess
   - AmazonS3FullAccess
   - CloudFormationFullAccess
   - IAMFullAccess

### 방법 3: 임시 자격 증명 (테스트용)

```bash
# 환경 변수로 설정
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

## 필요한 AWS 권한

T-Developer 배포를 위해 다음 권한이 필요합니다:

### Lambda 배포
- lambda:*
- iam:CreateRole, iam:AttachRolePolicy
- logs:CreateLogGroup
- s3:CreateBucket, s3:PutObject
- cloudformation:*

### ECS 배포
- ecs:*
- ecr:*
- ec2:DescribeVpcs, ec2:DescribeSubnets
- elasticloadbalancing:*
- iam:CreateRole, iam:AttachRolePolicy

### 기타
- dynamodb:*
- secretsmanager:*
- ssm:*
- bedrock:InvokeModel

## 자격 증명 확인

```bash
# 자격 증명 확인
aws sts get-caller-identity

# 리전 확인
aws configure get region
```

## 배포 명령

자격 증명 설정 후:

### Lambda 배포
```bash
cd /home/ec2-user/T-DeveloperMVP/backend/deployment/lambda
make deploy ENV=development
```

### ECS 배포
```bash
cd /home/ec2-user/T-DeveloperMVP/backend/deployment/ecs
./deploy.sh development
```

## 주의사항

1. **보안**: Access Key를 코드에 하드코딩하지 마세요
2. **권한**: 최소 권한 원칙을 따르세요
3. **로테이션**: Access Key를 정기적으로 교체하세요
4. **IAM Role**: EC2에서는 IAM Role 사용을 권장합니다

## 문제 해결

### "Invalid credentials" 오류
```bash
# 자격 증명 재설정
rm -rf ~/.aws
./aws-setup.sh
```

### "Access Denied" 오류
- IAM 사용자/Role에 필요한 권한이 있는지 확인
- Policy 연결 상태 확인

### Region 오류
```bash
# 기본 리전 설정
aws configure set region us-east-1
```