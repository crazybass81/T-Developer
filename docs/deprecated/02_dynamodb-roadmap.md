# DynamoDB 사용 계획서

## 🎯 현재 상태
- ✅ DynamoDB 클라이언트 초기화됨 (`production_pipeline.py`)
- ⚠️ 실제 테이블 사용은 아직 구현되지 않음
- ✅ AWS 권한 설정 완료

## 📊 테이블 설계

### 1. 에이전트 실행 상태 테이블
```yaml
Table: t-developer-agent-executions
Partition Key: execution_id (String)
Sort Key: agent_name (String)
Attributes:
  - project_id: String
  - status: String (PENDING, RUNNING, COMPLETED, FAILED)
  - start_time: Number (timestamp)
  - end_time: Number (timestamp)
  - input_data: String (JSON)
  - output_data: String (JSON)
  - error_message: String
  - retry_count: Number
```

### 2. 파이프라인 세션 테이블
```yaml
Table: t-developer-pipeline-sessions
Partition Key: session_id (String)
Attributes:
  - user_id: String
  - project_name: String
  - pipeline_type: String (SIMPLE, PRODUCTION)
  - status: String (ACTIVE, COMPLETED, FAILED, ABANDONED)
  - current_agent: String
  - progress: Number (0-9)
  - created_at: Number (timestamp)
  - last_updated: Number (timestamp)
  - metadata: String (JSON)
```

### 3. 사용자 프로젝트 히스토리
```yaml
Table: t-developer-user-projects
Partition Key: user_id (String)
Sort Key: project_id (String)
Attributes:
  - project_name: String
  - description: String
  - tech_stack: String (JSON)
  - download_count: Number
  - last_accessed: Number (timestamp)
  - file_path: String
  - size_mb: Number
```

### 4. 시스템 메트릭스
```yaml
Table: t-developer-metrics
Partition Key: date (String, YYYY-MM-DD)
Sort Key: metric_name (String)
Attributes:
  - value: Number
  - count: Number
  - avg_response_time: Number
  - error_rate: Number
  - agent_name: String
  - hour: Number (0-23)
```

## 🔄 단계별 구현 계획

### Phase 1: 기본 상태 저장 (현재 → 1개월)
```python
# 파이프라인 실행 시작
await save_pipeline_session({
    "session_id": project_id,
    "status": "ACTIVE",
    "current_agent": "nl_input",
    "progress": 0
})

# 각 에이전트 완료 시
await update_agent_execution({
    "execution_id": f"{project_id}-{agent_name}",
    "status": "COMPLETED",
    "output_data": json.dumps(result.output_data)
})
```

### Phase 2: 실패 복구 시스템 (1-2개월)
```python
# 실패한 파이프라인 복구
failed_sessions = await get_failed_sessions()
for session in failed_sessions:
    if session['last_updated'] < 1_hour_ago:
        await resume_pipeline(session['session_id'])
```

### Phase 3: 사용자 히스토리 (2-3개월)
```python
# 사용자별 프로젝트 관리
await save_user_project({
    "user_id": user_id,
    "project_id": project_id,
    "project_name": "My Todo App",
    "tech_stack": ["React", "Node.js", "MongoDB"]
})
```

### Phase 4: 고급 메트릭스 (3-6개월)
```python
# 실시간 메트릭스 수집
await record_metric({
    "metric_name": "agent_execution_time",
    "agent_name": "generation",
    "value": execution_time,
    "timestamp": datetime.now()
})
```

## 🛠️ 구현 우선순위

### 필수 (High Priority)
1. **파이프라인 세션 관리** - 장시간 실행 추적
2. **에이전트 상태 저장** - 실패 지점 파악
3. **기본 메트릭스** - 성능 모니터링

### 중요 (Medium Priority)
4. **사용자 히스토리** - 재사용성 향상
5. **실패 복구** - 안정성 개선

### 선택적 (Low Priority)
6. **고급 분석** - 사용 패턴 분석
7. **A/B 테스팅** - 에이전트 성능 비교

## 💰 비용 최적화

### DynamoDB 비용 구조
- **온디맨드**: 사용량 기반, 예측 불가능한 워크로드에 적합
- **프로비전드**: 예측 가능한 워크로드, 비용 절약 가능

### 권장 설정
```yaml
# 개발/테스트 환경
BillingMode: ON_DEMAND
DeletionProtection: false

# 프로덕션 환경  
BillingMode: PROVISIONED
ReadCapacityUnits: 5
WriteCapacityUnits: 5
AutoScaling: enabled
DeletionProtection: true
```

## 🔒 보안 고려사항

### 데이터 암호화
- **전송 중**: HTTPS/TLS 1.2+
- **저장 시**: DynamoDB 암호화 활성화
- **민감 데이터**: AWS KMS로 추가 암호화

### 접근 제어
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem", 
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/t-developer-*"
    }
  ]
}
```

## 🚀 배포 전략

### 테스트 환경
- 테이블명: `t-developer-dev-*`
- 낮은 용량으로 시작
- 실험적 기능 테스트

### 프로덕션 환경
- 테이블명: `t-developer-prod-*`
- 백업 활성화
- 모니터링 알람 설정

---
**📝 참고**: DynamoDB는 현재 초기화만 되어있고 실제 사용되지 않습니다. 
위 계획에 따라 단계적으로 도입할 예정입니다.
