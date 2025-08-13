# T-Developer Operations Runbook

## 목차

1. [시스템 개요](#시스템-개요)
2. [일상 운영 절차](#일상-운영-절차)
3. [장애 대응 가이드](#장애-대응-가이드)
4. [성능 모니터링](#성능-모니터링)
5. [백업 및 복구](#백업-및-복구)
6. [보안 운영](#보안-운영)
7. [스케일링 가이드](#스케일링-가이드)
8. [비상 연락처](#비상-연락처)

## 시스템 개요

### 아키텍처 구성요소

```
┌─────────────────────────────────────────────────────────────────┐
│                        T-Developer System                        │
├─────────────────────────────────────────────────────────────────┤
│ Load Balancer (ALB)                                             │
├─────────────────────────────────────────────────────────────────┤
│ ECS Fargate Cluster                                             │
│ ├── Analysis Group (NL Input, UI Selection, Parser)            │
│ ├── Decision Group (Component Decision, Match Rate, Search)    │
│ └── Generation Group (Generation, Assembly, Download)          │
├─────────────────────────────────────────────────────────────────┤
│ Data Layer                                                      │
│ ├── S3 Bucket (Generated Projects)                            │
│ ├── DynamoDB (Metadata)                                       │
│ └── Secrets Manager (API Keys)                                │
├─────────────────────────────────────────────────────────────────┤
│ Monitoring & Logging                                           │
│ ├── CloudWatch Metrics & Alarms                               │
│ ├── CloudWatch Logs                                           │
│ └── X-Ray Tracing                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 핵심 지표 (SLI/SLO)

| 지표 | SLO | 측정 방법 |
|------|-----|----------|
| 가용성 | 99.5% | ALB 헬스체크 성공률 |
| 응답시간 | < 45초 (P95) | 파이프라인 전체 실행시간 |
| 에러율 | < 2% | 생성 실패 / 전체 요청 |
| 동시 사용자 | 100명 | 활성 세션 수 |

## 일상 운영 절차

### 🌅 일일 점검 (매일 오전 9시)

```bash
#!/bin/bash
# Daily Health Check Script

echo "=== T-Developer Daily Health Check $(date) ==="

# 1. ECS 서비스 상태 확인
echo "1. ECS Service Status:"
aws ecs describe-services \
  --cluster t-developer-cluster-production \
  --services t-developer-service-production \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' \
  --output table

# 2. CloudWatch 알람 상태 확인
echo "2. CloudWatch Alarms:"
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --alarm-names $(aws cloudwatch describe-alarms \
    --query 'MetricAlarms[?contains(AlarmName, `t-developer`)].AlarmName' \
    --output text) \
  --output table

# 3. 최근 24시간 에러 로그 확인
echo "3. Recent Error Logs:"
aws logs filter-log-events \
  --log-group-name /ecs/t-developer-production \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --filter-pattern "ERROR" \
  --query 'events[0:10].{Time:timestamp,Message:message}' \
  --output table

# 4. S3 스토리지 사용량
echo "4. Storage Usage:"
aws s3 ls s3://t-developer-projects-production --recursive --human-readable --summarize | tail -2

# 5. 어제 생성된 프로젝트 수
echo "5. Projects Generated Yesterday:"
aws dynamodb scan \
  --table-name t-developer-metadata-production \
  --filter-expression "created_at BETWEEN :start AND :end" \
  --expression-attribute-values '{
    ":start": {"S": "'$(date -d 'yesterday' '+%Y-%m-%d')'"},
    ":end": {"S": "'$(date '+%Y-%m-%d')'"}
  }' \
  --select COUNT \
  --output text

echo "=== Health Check Complete ==="
```

### 📊 주간 리포트 (매주 월요일)

```bash
#!/bin/bash
# Weekly Report Script

echo "=== T-Developer Weekly Report $(date) ==="

# 성능 지표 수집
echo "Performance Metrics (Last 7 days):"

# 평균 응답시간
aws cloudwatch get-metric-statistics \
  --namespace T-Developer/Pipeline \
  --metric-name PipelineExecutionTime \
  --start-time $(date -d '7 days ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 86400 \
  --statistics Average

# 성공률
aws cloudwatch get-metric-statistics \
  --namespace T-Developer/Pipeline \
  --metric-name GenerationSuccess \
  --start-time $(date -d '7 days ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 86400 \
  --statistics Sum

# 사용자 수
aws dynamodb scan \
  --table-name t-developer-metadata-production \
  --projection-expression "user_id" | \
  jq '.Items | map(.user_id.S) | unique | length'

echo "=== Weekly Report Complete ==="
```

### 🔧 월간 유지보수 (매월 첫째주)

1. **보안 패치 적용**
   ```bash
   # ECR 이미지 보안 스캔 결과 확인
   aws ecr describe-image-scan-findings \
     --repository-name t-developer-backend-production
   ```

2. **로그 정리**
   ```bash
   # 30일 이상 된 로그 정리
   aws logs describe-log-groups | \
   jq -r '.logGroups[] | select(.logGroupName | contains("t-developer")) | .logGroupName' | \
   xargs -I {} aws logs put-retention-policy --log-group-name {} --retention-in-days 30
   ```

3. **비용 최적화**
   ```bash
   # 미사용 S3 객체 정리 (7일 이상)
   aws s3api list-objects-v2 \
     --bucket t-developer-projects-production \
     --query 'Contents[?LastModified < `'$(date -d '7 days ago' --iso-8601)'`]'
   ```

## 장애 대응 가이드

### 🚨 P0: 서비스 완전 장애 (< 5분 대응)

**증상**: 모든 요청 실패, 서비스 접근 불가

**즉시 대응**:
```bash
# 1. 서비스 상태 확인
aws ecs describe-services --cluster t-developer-cluster-production --services t-developer-service-production

# 2. ALB 타겟 헬스 확인
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...

# 3. 긴급 롤백 (필요시)
./scripts/emergency_rollback.sh

# 4. 스케일 업 (트래픽 증가로 인한 경우)
aws ecs update-service --cluster t-developer-cluster-production --service t-developer-service-production --desired-count 10
```

### 🟠 P1: 서비스 성능 저하 (< 15분 대응)

**증상**: 응답시간 > 60초, 일부 요청 실패

**대응 절차**:
```bash
# 1. 현재 리소스 사용률 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=t-developer-service-production \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Maximum

# 2. 에러 로그 확인
aws logs tail /ecs/t-developer-production --since 1h

# 3. 캐시 상태 확인 및 클리어
curl -X POST http://internal-load-balancer/admin/clear-cache

# 4. 스케일링
aws ecs update-service --desired-count $(($(aws ecs describe-services --cluster t-developer-cluster-production --services t-developer-service-production --query 'services[0].desiredCount') + 2))
```

### 🟡 P2: 특정 기능 오류 (< 30분 대응)

**증상**: 특정 에이전트 실패, 부분적 기능 장애

**대응 절차**:
1. 장애 에이전트 식별
2. 개별 에이전트 재시작
3. 패치 배포 계획 수립

### 🔥 긴급 롤백 스크립트

```bash
#!/bin/bash
# emergency_rollback.sh

set -euo pipefail

CLUSTER_NAME="t-developer-cluster-production"
SERVICE_NAME="t-developer-service-production"

echo "🚨 EMERGENCY ROLLBACK INITIATED"

# 현재 태스크 정의 가져오기
CURRENT_TASK_DEF=$(aws ecs describe-services \
  --cluster "$CLUSTER_NAME" \
  --services "$SERVICE_NAME" \
  --query 'services[0].taskDefinition' \
  --output text)

# 이전 버전 계산
CURRENT_REVISION=$(echo "$CURRENT_TASK_DEF" | sed 's/.*://')
PREVIOUS_REVISION=$((CURRENT_REVISION - 1))
PREVIOUS_TASK_DEF="${CURRENT_TASK_DEF%:*}:$PREVIOUS_REVISION"

echo "Rolling back from $CURRENT_TASK_DEF to $PREVIOUS_TASK_DEF"

# 롤백 실행
aws ecs update-service \
  --cluster "$CLUSTER_NAME" \
  --service "$SERVICE_NAME" \
  --task-definition "$PREVIOUS_TASK_DEF"

# 알림 전송
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:t-developer-alerts-production" \
  --message "🚨 EMERGENCY ROLLBACK: Service rolled back to $PREVIOUS_TASK_DEF"

echo "✅ Rollback initiated. Monitoring deployment..."

# 롤백 완료 대기
aws ecs wait services-stable \
  --cluster "$CLUSTER_NAME" \
  --services "$SERVICE_NAME"

echo "✅ Rollback completed successfully"
```

## 성능 모니터링

### 핵심 대시보드

1. **실시간 대시보드**: https://console.aws.amazon.com/cloudwatch/home#dashboards:name=t-developer-dashboard-production

2. **주요 지표**:
   - **파이프라인 실행시간**: 목표 < 45초
   - **에이전트별 실행시간**: 각각 < 10초
   - **메모리 사용률**: < 80%
   - **CPU 사용률**: < 70%
   - **에러율**: < 2%

### 성능 이슈 대응

**느린 응답시간 (> 60초)**:
```bash
# 1. 병목 에이전트 식별
aws logs filter-log-events \
  --log-group-name /ecs/t-developer-production \
  --filter-pattern "execution_time" \
  --start-time $(date -d '1 hour ago' +%s)000

# 2. 리소스 모니터링
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization

# 3. 캐시 성능 확인
curl http://load-balancer/metrics/cache
```

**높은 에러율 (> 5%)**:
```bash
# 에러 패턴 분석
aws logs filter-log-events \
  --log-group-name /ecs/t-developer-production \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000 | \
  jq '.events[].message' | sort | uniq -c | sort -nr
```

## 백업 및 복구

### 데이터 백업

**DynamoDB 백업**:
```bash
# 온디맨드 백업 생성
aws dynamodb create-backup \
  --table-name t-developer-metadata-production \
  --backup-name "manual-backup-$(date +%Y%m%d-%H%M%S)"

# 백업 목록 확인
aws dynamodb list-backups \
  --table-name t-developer-metadata-production
```

**S3 백업**:
```bash
# 교차 리전 복제 확인
aws s3api get-bucket-replication \
  --bucket t-developer-projects-production
```

### 재해 복구 절차

1. **데이터베이스 복구**:
   ```bash
   aws dynamodb restore-table-from-backup \
     --target-table-name t-developer-metadata-production-restored \
     --backup-arn arn:aws:dynamodb:...
   ```

2. **애플리케이션 재배포**:
   ```bash
   ./scripts/deploy.sh --environment production --force
   ```

3. **DNS 전환** (재해 발생 시):
   ```bash
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z123456789 \
     --change-batch file://dns-failover.json
   ```

## 보안 운영

### 일일 보안 점검

```bash
#!/bin/bash
# Security Daily Check

echo "=== Security Daily Check ==="

# 1. 실패한 로그인 시도
aws logs filter-log-events \
  --log-group-name /ecs/t-developer-production \
  --filter-pattern "authentication failed" \
  --start-time $(date -d '24 hours ago' +%s)000

# 2. 비정상적인 API 사용 패턴
aws logs filter-log-events \
  --log-group-name /ecs/t-developer-production \
  --filter-pattern "rate_limit_exceeded" \
  --start-time $(date -d '24 hours ago' +%s)000

# 3. 보안 그룹 변경사항
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*t-developer*" \
  --query 'SecurityGroups[].{GroupId:GroupId,Name:GroupName,Rules:IpPermissions}'

echo "=== Security Check Complete ==="
```

### 월간 보안 감사

```bash
# 보안 스캔 실행
python monitoring/setup_monitoring.py --security-audit

# 취약점 스캔
aws ecr start-image-scan \
  --repository-name t-developer-backend-production \
  --image-id imageTag=latest
```

### 보안 인시던트 대응

1. **의심스러운 활동 감지 시**:
   ```bash
   # 즉시 API 키 로테이션
   aws secretsmanager rotate-secret \
     --secret-id t-developer/production/api-keys
   
   # 관련 세션 무효화
   curl -X POST http://load-balancer/admin/invalidate-sessions
   ```

2. **데이터 유출 의심 시**:
   ```bash
   # 즉시 S3 버킷 접근 차단
   aws s3api put-bucket-policy \
     --bucket t-developer-projects-production \
     --policy file://emergency-deny-policy.json
   ```

## 스케일링 가이드

### 오토 스케일링 정책

**현재 설정**:
- 최소: 2 태스크
- 최대: 20 태스크  
- 목표 CPU: 70%
- 스케일 아웃: CPU > 70% (2분)
- 스케일 인: CPU < 50% (5분)

### 수동 스케일링

**트래픽 급증 예상 시**:
```bash
# 사전 스케일 업
aws ecs update-service \
  --cluster t-developer-cluster-production \
  --service t-developer-service-production \
  --desired-count 10

# RDS 인스턴스 스케일 업 (필요시)
aws rds modify-db-instance \
  --db-instance-identifier t-developer-prod \
  --db-instance-class db.r5.2xlarge \
  --apply-immediately
```

**부하 테스트**:
```bash
# K6로 부하 테스트 실행
k6 run --vus 100 --duration 10m tests/load-test.js

# 결과 모니터링
watch -n 5 'aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --start-time $(date -d "10 minutes ago" --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 60 \
  --statistics Average'
```

## 비상 연락처

### 기술팀 연락처

| 역할 | 이름 | 연락처 | 대응 시간 |
|------|------|--------|----------|
| DevOps Lead | 김개발 | +82-10-1234-5678 | 24/7 |
| Backend Lead | 이백엔드 | +82-10-2345-6789 | 평일 9-18시 |
| 시스템 관리자 | 박인프라 | +82-10-3456-7890 | 24/7 |
| 보안 담당자 | 최보안 | +82-10-4567-8901 | 평일 9-18시 |

### 외부 지원

| 서비스 | 연락처 | 지원 내용 |
|--------|--------|----------|
| AWS Support | +1-206-266-4064 | 인프라 이슈 |
| PagerDuty | alerts@company.pagerduty.com | 알람 관리 |
| Slack #ops | #t-developer-ops | 실시간 소통 |

### 에스컬레이션 절차

1. **P0 장애**: 즉시 DevOps Lead 연락 + Slack #ops 알림
2. **P1 장애**: 15분 내 해결 안되면 Backend Lead 연락
3. **보안 이슈**: 즉시 보안 담당자 + 경영진 보고
4. **데이터 유실**: 즉시 전 팀 알림 + 고객 공지 준비

## 체크리스트

### 배포 전 체크리스트

- [ ] 모든 테스트 통과 확인
- [ ] 보안 스캔 완료
- [ ] 백업 완료 확인
- [ ] 롤백 계획 준비
- [ ] 모니터링 대시보드 준비
- [ ] 팀 알림 완료

### 장애 대응 체크리스트

- [ ] 증상 정확히 파악
- [ ] 고객 영향도 평가
- [ ] 대응팀 소집
- [ ] 즉시 대응 조치
- [ ] 근본 원인 분석
- [ ] 재발 방지책 수립
- [ ] 사후 보고서 작성

### 월간 점검 체크리스트

- [ ] 보안 패치 적용
- [ ] 백업 무결성 확인
- [ ] 성능 지표 리뷰
- [ ] 비용 최적화 검토
- [ ] 문서 업데이트
- [ ] 팀 교육 실시

---

**마지막 업데이트**: 2024년 1월 15일  
**다음 리뷰 예정**: 2024년 2월 15일  
**문서 버전**: v2.0
