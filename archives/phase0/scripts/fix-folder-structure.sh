#!/bin/bash

echo "🔧 T-Developer 폴더 구조 정리 및 문서 매칭"
echo "============================================="

# Phase 2 데이터 레이어 구조 완성
echo "📁 Phase 2 데이터 레이어 구조 생성..."

# DynamoDB 관련 구조
mkdir -p backend/src/data/dynamodb/{client,single-table-design,query-optimizer,transaction-manager}
mkdir -p backend/src/data/partitioning/{time-based,hot-partition-manager}
mkdir -p backend/src/data/optimization/{query-optimizer,performance-monitor}

# 캐싱 시스템 구조  
mkdir -p backend/src/cache/{architecture,invalidation,distributed,optimization}
mkdir -p backend/src/cache/redis/{cluster-manager,performance-optimizer}

# 데이터 모델링
mkdir -p backend/src/data/models/{domain,validation,migration}
mkdir -p backend/src/data/migration/{schema-evolution,rollback-recovery}

# Repository 패턴
mkdir -p backend/src/data/repositories/{base,implementations}
mkdir -p backend/src/data/access/{abstraction,transaction}

# 실시간 데이터 처리
mkdir -p backend/src/streaming/{event-streaming,change-data-capture,synchronization}

# Phase 1 누락된 구조 보완
echo "📁 Phase 1 구조 보완..."

# 워크플로우 시스템 세분화
mkdir -p backend/src/workflow/{parallel-execution,dependency-management,state-sync,recovery}

# 라우팅 시스템 세분화  
mkdir -p backend/src/routing/{intelligent-router,load-balancer,priority-manager,metrics}

# 보안 시스템 세분화
mkdir -p backend/src/security/{input-validation,api-security,encryption,audit-logging,testing}

# 설정 관리 세분화
mkdir -p backend/src/config/{environment,feature-flags,secrets,audit}

# 성능 벤치마크 세분화
mkdir -p backend/src/benchmarks/{agent-performance,system-load,memory-profiling,integration-tests}

# 테스트 구조 정리
echo "📁 테스트 구조 정리..."
mkdir -p backend/tests/{data,cache,workflow,routing,security,config,benchmarks}
mkdir -p backend/tests/data/{dynamodb,models,repositories,migration}
mkdir -p backend/tests/cache/{redis,strategies,distributed}

# 문서 구조 정리
echo "📁 문서 구조 정리..."
mkdir -p docs/{phase1,phase2,architecture,api,deployment}
mkdir -p docs/phase1/{infrastructure,agents,performance,security}
mkdir -p docs/phase2/{data-layer,caching,migration,streaming}

# 스크립트 구조 정리
echo "📁 스크립트 구조 정리..."
mkdir -p scripts/{phase1,phase2,testing,deployment}
mkdir -p scripts/phase1/{setup,testing,completion}
mkdir -p scripts/phase2/{data-setup,migration,testing}

echo "✅ 폴더 구조 정리 완료"

# 구조 검증
echo "🔍 구조 검증..."
echo "Phase 1 핵심 디렉토리:"
ls -la backend/src/{agents,orchestration,routing,workflow,security,config,benchmarks} 2>/dev/null | grep "^d" | wc -l
echo "Phase 2 핵심 디렉토리:"  
ls -la backend/src/{data,cache,streaming} 2>/dev/null | grep "^d" | wc -l

echo "📋 구조 매칭 완료!"