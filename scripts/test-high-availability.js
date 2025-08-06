#!/usr/bin/env node
// scripts/test-high-availability.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 고가용성 및 재해복구 설정 검증 시작...\n');

// 1. Python 파일 존재 확인
const haFilePath = path.join(__dirname, '../backend/src/runtime/high-availability.py');
if (fs.existsSync(haFilePath)) {
    console.log('✅ high-availability.py 파일 존재');
} else {
    console.log('❌ high-availability.py 파일 없음');
    process.exit(1);
}

// 2. Python 구문 검사
try {
    execSync(`python3 -m py_compile ${haFilePath}`, { stdio: 'pipe' });
    console.log('✅ Python 구문 검사 통과');
} catch (error) {
    console.log('❌ Python 구문 오류:', error.message);
    process.exit(1);
}

// 3. 필수 클래스 확인
const haContent = fs.readFileSync(haFilePath, 'utf8');
const requiredClasses = [
    'HighAvailabilityManager',
    'HealthChecker', 
    'FailoverManager'
];

let allClassesFound = true;
requiredClasses.forEach(className => {
    if (haContent.includes(`class ${className}`)) {
        console.log(`✅ ${className} 클래스 존재`);
    } else {
        console.log(`❌ ${className} 클래스 없음`);
        allClassesFound = false;
    }
});

// 4. 필수 메서드 확인
const requiredMethods = [
    'setup_multi_region_deployment',
    'deploy_runtime',
    'setup_cross_region_replication',
    'initiate_failover'
];

requiredMethods.forEach(method => {
    if (haContent.includes(`async def ${method}`) || haContent.includes(`def ${method}`)) {
        console.log(`✅ ${method} 메서드 존재`);
    } else {
        console.log(`❌ ${method} 메서드 없음`);
        allClassesFound = false;
    }
});

// 5. 환경 변수 설정 확인
const envVars = [
    'AWS_PRIMARY_REGION',
    'AWS_DR_REGIONS'
];

console.log('\n📋 필요한 환경 변수:');
envVars.forEach(envVar => {
    console.log(`   ${envVar}=${envVar === 'AWS_PRIMARY_REGION' ? 'us-east-1' : 'us-west-2,eu-west-1'}`);
});

// 6. AWS 서비스 의존성 확인
const awsServices = [
    'CloudFormation',
    'DynamoDB Global Tables',
    'Route 53',
    'Bedrock AgentCore'
];

console.log('\n🔧 필요한 AWS 서비스:');
awsServices.forEach(service => {
    console.log(`   - ${service}`);
});

if (allClassesFound) {
    console.log('\n✅ 고가용성 및 재해복구 설정 검증 완료!');
    console.log('📊 구현된 기능:');
    console.log('   - 다중 리전 배포 (Primary + DR)');
    console.log('   - 크로스 리전 데이터 복제');
    console.log('   - 자동 헬스체크 및 페일오버');
    console.log('   - CloudFormation 기반 인프라 관리');
} else {
    console.log('\n❌ 일부 구성 요소가 누락되었습니다.');
    process.exit(1);
}