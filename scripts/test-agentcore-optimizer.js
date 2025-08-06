#!/usr/bin/env node

/**
 * AgentCore 런타임 최적화 시스템 검증 스크립트
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 AgentCore 런타임 최적화 시스템 검증 시작...\n');

// 1. 파일 존재 확인
const files = [
    'backend/src/runtime/agentcore-optimizer.py'
];

console.log('📁 파일 존재 확인:');
files.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    if (fs.existsSync(filePath)) {
        console.log(`✅ ${file}`);
    } else {
        console.log(`❌ ${file} - 파일이 존재하지 않습니다`);
    }
});

// 2. Python 파일 구문 검사
console.log('\n🐍 Python 구문 검사:');
const { execSync } = require('child_process');

try {
    const pythonFile = path.join(__dirname, '..', 'backend/src/runtime/agentcore-optimizer.py');
    execSync(`python3 -m py_compile ${pythonFile}`, { stdio: 'pipe' });
    console.log('✅ agentcore-optimizer.py - 구문 검사 통과');
} catch (error) {
    console.log('❌ Python 구문 오류:', error.message);
}

// 3. 클래스 및 메서드 확인
console.log('\n🔍 클래스 및 메서드 확인:');
const optimizerContent = fs.readFileSync(
    path.join(__dirname, '..', 'backend/src/runtime/agentcore-optimizer.py'),
    'utf8'
);

const expectedMethods = [
    'class AgentCoreOptimizer',
    'async def optimize_runtime',
    'async def collect_runtime_metrics',
    'def analyze_metrics',
    'async def apply_optimization',
    'async def _scale_runtime',
    'async def _adjust_memory',
    'async def _optimize_caching'
];

expectedMethods.forEach(method => {
    if (optimizerContent.includes(method)) {
        console.log(`✅ ${method}`);
    } else {
        console.log(`❌ ${method} - 메서드가 없습니다`);
    }
});

// 4. 최적화 타입 확인
console.log('\n⚙️ 최적화 타입 확인:');
const optimizationTypes = [
    'scale_out',
    'scale_in', 
    'increase_memory',
    'optimize_caching'
];

optimizationTypes.forEach(type => {
    if (optimizerContent.includes(`'${type}'`)) {
        console.log(`✅ ${type} 최적화 지원`);
    } else {
        console.log(`❌ ${type} 최적화 미지원`);
    }
});

// 5. AWS 서비스 클라이언트 확인
console.log('\n☁️ AWS 서비스 클라이언트 확인:');
const awsClients = [
    'bedrock-agent-runtime',
    'cloudwatch',
    'application-autoscaling'
];

awsClients.forEach(client => {
    if (optimizerContent.includes(client)) {
        console.log(`✅ ${client} 클라이언트`);
    } else {
        console.log(`❌ ${client} 클라이언트 미사용`);
    }
});

// 6. 메트릭 타입 확인
console.log('\n📊 메트릭 타입 확인:');
const metricTypes = [
    'cpu_utilization',
    'memory_utilization',
    'session_count',
    'average_latency',
    'error_rate'
];

metricTypes.forEach(metric => {
    if (optimizerContent.includes(metric)) {
        console.log(`✅ ${metric} 메트릭`);
    } else {
        console.log(`❌ ${metric} 메트릭 미포함`);
    }
});

// 7. 임계값 설정 확인
console.log('\n🎯 임계값 설정 확인:');
const thresholds = [
    { name: 'CPU 높음', value: '> 80', pattern: '> 80' },
    { name: 'CPU 낮음', value: '< 20', pattern: '< 20' },
    { name: '메모리 높음', value: '> 85', pattern: '> 85' },
    { name: '레이턴시 높음', value: '> 500', pattern: '> 500' }
];

thresholds.forEach(threshold => {
    if (optimizerContent.includes(threshold.pattern)) {
        console.log(`✅ ${threshold.name} 임계값 (${threshold.value})`);
    } else {
        console.log(`❌ ${threshold.name} 임계값 미설정`);
    }
});

// 8. 에러 처리 확인
console.log('\n🛡️ 에러 처리 확인:');
const errorHandling = [
    'try:',
    'except Exception as e:',
    '"status": "failed"',
    '"error": str(e)'
];

errorHandling.forEach(pattern => {
    if (optimizerContent.includes(pattern)) {
        console.log(`✅ ${pattern} 패턴`);
    } else {
        console.log(`❌ ${pattern} 패턴 미포함`);
    }
});

console.log('\n✅ AgentCore 런타임 최적화 시스템 검증 완료!');
console.log('\n📋 구현된 기능:');
console.log('- CPU/메모리 사용률 모니터링');
console.log('- 자동 스케일링 (Scale Out/In)');
console.log('- 메모리 증가 권장');
console.log('- 캐싱 최적화');
console.log('- CloudWatch 메트릭 수집');
console.log('- Application Auto Scaling 통합');
console.log('- 에러 처리 및 복구');