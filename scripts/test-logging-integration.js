#!/usr/bin/env node

const { spawn } = require('child_process');
const http = require('http');

console.log('🧪 로깅 시스템 통합 테스트 중...\n');

// 테스트 서버 시작
console.log('1️⃣ 테스트 서버 시작 중...');
const server = spawn('npm', ['run', 'dev'], {
  cwd: 'backend',
  stdio: ['pipe', 'pipe', 'pipe']
});

let serverReady = false;
let logOutput = '';

server.stdout.on('data', (data) => {
  const output = data.toString();
  logOutput += output;
  
  if (output.includes('Server running on port')) {
    serverReady = true;
    console.log('   ✅ 서버 시작됨');
    runTests();
  }
});

server.stderr.on('data', (data) => {
  logOutput += data.toString();
});

// 테스트 실행
async function runTests() {
  console.log('\n2️⃣ HTTP 요청 테스트 중...');
  
  try {
    // Health check 요청
    await makeRequest('GET', '/health');
    console.log('   ✅ Health check 요청 완료');
    
    // 여러 요청으로 로깅 테스트
    await makeRequest('GET', '/api/public/test');
    await makeRequest('POST', '/api/auth/login');
    console.log('   ✅ 다양한 엔드포인트 요청 완료');
    
    // 로그 출력 확인
    console.log('\n3️⃣ 로그 출력 확인:');
    
    const logChecks = [
      { pattern: 'Request started', name: '요청 시작 로그' },
      { pattern: 'Request completed', name: '요청 완료 로그' },
      { pattern: 'method', name: 'HTTP 메서드 로깅' },
      { pattern: 'statusCode', name: '상태 코드 로깅' },
      { pattern: 'duration', name: '응답 시간 로깅' }
    ];
    
    logChecks.forEach(check => {
      const found = logOutput.includes(check.pattern);
      console.log(`   ${found ? '✅' : '❌'} ${check.name}`);
    });
    
    console.log('\n✅ 로깅 시스템 통합 테스트 완료!');
    
  } catch (error) {
    console.error('❌ 테스트 실패:', error.message);
  } finally {
    // 서버 종료
    server.kill();
    process.exit(0);
  }
}

function makeRequest(method, path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 3002,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': `test-${Date.now()}`
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve({ statusCode: res.statusCode, data }));
    });
    
    req.on('error', reject);
    req.setTimeout(5000, () => reject(new Error('Request timeout')));
    
    if (method === 'POST') {
      req.write(JSON.stringify({ test: 'data' }));
    }
    
    req.end();
  });
}

// 타임아웃 설정
setTimeout(() => {
  if (!serverReady) {
    console.log('❌ 서버 시작 타임아웃');
    server.kill();
    process.exit(1);
  }
}, 10000);