# T-Developer AWS 인프라 구성

## 📋 개요

T-Developer Evolution System을 위한 AWS 인프라를 Terraform으로 관리합니다.

## 🏗️ 인프라 구성도

```
T-Developer AWS Infrastructure
├── VPC (172.31.0.0/16)
├── Security Groups (6개)
│   ├── Evolution Engine
│   ├── Agents Runtime
│   ├── Database
│   ├── Safety System
│   ├── Monitoring
│   └── Emergency
├── S3 Buckets (2개)
│   ├── Evolution Storage
│   └── Agents Artifacts
├── DynamoDB
│   └── Evolution State
└── CloudWatch/SNS
    ├── Log Groups (3개)
    └── Alert Topics (2개)
```

## 🚀 배포 방법

### 1. 초기 배포
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 2. 환경 설정
```bash
# 배포된 리소스 확인
terraform output

# Bedrock Agent 정보 Parameter Store에 저장
aws ssm put-parameter --name "/t-developer/bedrock/agent_id" --value "NYZHMLSDOJ" --type "String"
aws ssm put-parameter --name "/t-developer/bedrock/agent_alias_id" --value "IBQK7SYNGG" --type "String"
```

## 📊 배포된 리소스 (Day 1 완료)

### 네트워크 및 보안
- **VPC**: `vpc-021655951c69fab62`
- **Security Groups**: 6개 (포트별 접근 제어)
- **Network ACL**: Evolution 트래픽 전용
- **WAF**: Evolution Dashboard 보호

### 컴퓨팅 및 스토리지
- **IAM Role**: `t-developer-evolution-role-development`
- **S3 Buckets**: Evolution + Agents (AES256 암호화)
- **DynamoDB**: Evolution State (Point-in-Time Recovery)

### 모니터링 및 알림
- **CloudWatch Log Groups**: Evolution, Safety, Registry
- **SNS Topics**: Safety/Emergency alerts
- **Parameter Store**: 설정 관리

### AI 서비스
- **Bedrock Agent**: `NYZHMLSDOJ` (Claude Sonnet 4)
- **Agent Alias**: `IBQK7SYNGG` (Production)

## 🔒 보안 설정

### 네트워크 보안
- SSH: VPC 내부 접근만 허용 (172.31.0.0/16)
- API: Evolution Engine은 VPC 내부에서만 접근
- HTTPS: Evolution Dashboard는 공개 접근 (필요시)

### 데이터 보안
- S3: 서버 측 암호화 (AES256) + 버전 관리
- DynamoDB: 자동 암호화 + 백업 활성화
- CloudWatch: 30-90일 로그 보관

### 접근 제어
- IAM: 최소 권한 원칙 적용
- Security Groups: 포트별 세밀한 제어
- WAF: 웹 애플리케이션 방화벽

## 🔧 관리 명령어

### 리소스 상태 확인
```bash
# 전체 상태
terraform show

# 특정 리소스
aws ec2 describe-security-groups --group-ids sg-xxxxx
aws s3 ls | grep t-developer
aws dynamodb describe-table --table-name t-developer-evolution-state-development
```

### 보안 검증
```bash
# Security Group 규칙 확인
aws ec2 describe-security-groups --query 'SecurityGroups[?contains(GroupName, `t-developer`)]'

# S3 암호화 확인
aws s3api get-bucket-encryption --bucket t-developer-evolution-development-e7f02f38

# DynamoDB 백업 확인
aws dynamodb describe-continuous-backups --table-name t-developer-evolution-state-development
```

### 리소스 정리
```bash
# 주의: 모든 리소스가 삭제됩니다!
terraform destroy
```

## 📈 모니터링

### CloudWatch 대시보드
- Evolution Engine 메트릭
- Safety System 알람
- 리소스 사용률

### 알림 설정
- Safety Alerts: 악성 패턴 감지
- Emergency Alerts: 긴급 상황 발생

## 🔄 업데이트 및 확장

### Day 2 예정 작업
- AWS Secrets Manager 통합
- Parameter Store 계층 구조
- KMS 키 관리
- 환경별 분리 (dev/staging/prod)

### 확장 계획
- ECS 클러스터 (Agent 배포용)
- ElastiCache (성능 최적화)
- Application Load Balancer
- Route 53 (DNS 관리)

## ⚠️ 주의사항

### 비용 관리
- S3: 수명 주기 정책 설정 필요
- DynamoDB: On-Demand 요금제 사용
- CloudWatch: 로그 보관 기간 최적화

### 보안 주의
- IAM 키 노출 금지
- Security Group 규칙 최소화
- 정기적인 접근 로그 검토

### 백업 및 복구
- Terraform State 백업
- DynamoDB Point-in-Time Recovery 활용
- S3 Cross-Region Replication 고려

---

**생성일**: 2025-08-13
**버전**: 1.0.0
**상태**: Day 1 Infrastructure Complete ✅
