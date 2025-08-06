#!/usr/bin/env node

/**
 * 개발 데이터 시드 스크립트
 */

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient } = require('@aws-sdk/lib-dynamodb');

// DynamoDB 클라이언트 설정
const client = new DynamoDBClient({
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.DYNAMODB_ENDPOINT || 'http://localhost:8000',
  credentials: {
    accessKeyId: 'local',
    secretAccessKey: 'local'
  }
});

const docClient = DynamoDBDocumentClient.from(client);

async function seedDevelopmentData() {
  console.log('🌱 개발 데이터 생성 시작...\n');
  
  try {
    // TypeScript 컴파일 확인
    const { execSync } = require('child_process');
    console.log('📦 TypeScript 컴파일 중...');
    execSync('npx tsc src/utils/data-generator.ts --outDir dist --target es2020 --module commonjs --esModuleInterop', {
      cwd: 'backend',
      stdio: 'inherit'
    });
    
    // 컴파일된 모듈 로드
    const { DevelopmentDataGenerator } = require('../backend/dist/utils/data-generator');
    const generator = new DevelopmentDataGenerator(docClient);
    
    // 병렬로 데이터 생성
    await Promise.all([
      generator.generateProjects(50),
      generator.generateComponents(100)
    ]);
    
    console.log('\n✅ 모든 개발 데이터 생성 완료!');
    console.log('📊 생성된 데이터:');
    console.log('   - 프로젝트: 50개');
    console.log('   - 컴포넌트: 100개');
    console.log('   - 현실적인 메트릭과 관계 포함');
    
  } catch (error) {
    console.error('❌ 데이터 생성 중 오류:', error.message);
    process.exit(1);
  }
}

// 스크립트 실행
if (require.main === module) {
  seedDevelopmentData();
}

module.exports = { seedDevelopmentData };