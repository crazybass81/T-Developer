#!/usr/bin/env node

/**
 * LocalStack 연결 및 서비스 검증 스크립트
 */

const net = require('net');

const LOCALSTACK_SERVICES = [
  { name: 'LocalStack Main', port: 4566 },
  { name: 'LocalStack Edge', port: 4571 }
];

async function checkPort(port) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    
    socket.setTimeout(3000);
    
    socket.on('connect', () => {
      socket.destroy();
      resolve(true);
    });
    
    socket.on('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    
    socket.on('error', () => {
      resolve(false);
    });
    
    socket.connect(port, 'localhost');
  });
}

async function testLocalStackServices() {
  console.log('🔍 LocalStack 서비스 연결 테스트...\n');
  
  let allHealthy = true;
  
  for (const service of LOCALSTACK_SERVICES) {
    const isHealthy = await checkPort(service.port);
    const status = isHealthy ? '✅ 연결됨' : '❌ 연결 실패';
    
    console.log(`${service.name} (포트 ${service.port}): ${status}`);
    
    if (!isHealthy) {
      allHealthy = false;
    }
  }
  
  console.log('\n📋 LocalStack 서비스 상태:');
  if (allHealthy) {
    console.log('✅ 모든 LocalStack 서비스가 정상 작동 중입니다!');
    console.log('\n🚀 다음 단계:');
    console.log('1. python scripts/setup-localstack.py 실행');
    console.log('2. LocalStack 웹 UI 확인: http://localhost:4566');
  } else {
    console.log('❌ 일부 LocalStack 서비스에 연결할 수 없습니다.');
    console.log('\n🔧 해결 방법:');
    console.log('1. docker-compose up -d 실행');
    console.log('2. Docker Desktop이 실행 중인지 확인');
    console.log('3. 포트 충돌 확인 (4566, 4571)');
  }
  
  return allHealthy;
}

// 스크립트 실행
if (require.main === module) {
  testLocalStackServices()
    .then((success) => {
      process.exit(success ? 0 : 1);
    })
    .catch((error) => {
      console.error('❌ 테스트 실행 중 오류:', error);
      process.exit(1);
    });
}

module.exports = { testLocalStackServices };