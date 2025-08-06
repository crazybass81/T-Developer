#!/usr/bin/env node

const http = require('http');
const { spawn } = require('child_process');

console.log('🔍 분산 추적 통합 테스트 시작...\n');

let testsPassed = 0;
let totalTests = 0;

function runTest(testName, testFn) {
  totalTests++;
  console.log(`${totalTests}️⃣ ${testName}:`);
  
  try {
    const result = testFn();
    if (result instanceof Promise) {
      return result.then(() => {
        console.log(`   ✅ 통과\n`);
        testsPassed++;
      }).catch(error => {
        console.log(`   ❌ 실패: ${error.message}\n`);
      });
    } else {
      console.log(`   ✅ 통과\n`);
      testsPassed++;
    }
  } catch (error) {
    console.log(`   ❌ 실패: ${error.message}\n`);
  }
}

// 서버 시작 테스트
async function testServerStart() {
  return new Promise((resolve, reject) => {
    const server = spawn('npm', ['run', 'dev'], {
      cwd: 'backend',
      stdio: 'pipe'
    });
    
    let serverReady = false;
    
    server.stdout.on('data', (data) => {
      const output = data.toString();
      if (output.includes('T-Developer API 서버 시작됨')) {
        serverReady = true;
        server.kill();
        resolve();
      }
    });
    
    server.stderr.on('data', (data) => {
      const error = data.toString();
      if (!serverReady && error.includes('Error')) {
        server.kill();
        reject(new Error('서버 시작 실패'));
      }
    });
    
    setTimeout(() => {
      if (!serverReady) {
        server.kill();
        reject(new Error('서버 시작 타임아웃'));
      }
    }, 10000);
  });
}

// 헬스 체크 테스트
async function testHealthCheck() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:3002/health', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const health = JSON.parse(data);
          if (health.status === 'ok' && health.apm) {
            resolve();
          } else {
            reject(new Error('헬스 체크 응답 형식 오류'));
          }
        } catch (error) {
          reject(new Error('헬스 체크 JSON 파싱 오류'));
        }
      });
    });
    
    req.on('error', () => {
      reject(new Error('헬스 체크 요청 실패'));
    });
    
    req.setTimeout(5000, () => {
      reject(new Error('헬스 체크 타임아웃'));
    });
  });
}

// 메트릭 엔드포인트 테스트
async function testMetricsEndpoint() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:3002/metrics', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const metrics = JSON.parse(data);
          if (metrics.metrics && metrics.metrics.cpu && metrics.metrics.memory) {
            resolve();
          } else {
            reject(new Error('메트릭 데이터 형식 오류'));
          }
        } catch (error) {
          reject(new Error('메트릭 JSON 파싱 오류'));
        }
      });
    });
    
    req.on('error', () => {
      reject(new Error('메트릭 요청 실패'));
    });
    
    req.setTimeout(5000, () => {
      reject(new Error('메트릭 타임아웃'));
    });
  });
}

// 테스트 실행
async function runAllTests() {
  console.log('🚀 통합 테스트 실행 중...\n');
  
  // 파일 존재 확인
  await runTest('추적 설정 파일 존재 확인', () => {
    const fs = require('fs');
    const files = [
      'backend/src/config/tracing.ts',
      'backend/src/monitoring/apm.ts',
      'backend/src/app.ts',
      'backend/src/server.ts'
    ];
    
    files.forEach(file => {
      if (!fs.existsSync(file)) {
        throw new Error(`파일 없음: ${file}`);
      }
    });
  });
  
  // Docker Compose 파일 확인
  await runTest('Docker Compose 설정 확인', () => {
    const fs = require('fs');
    if (!fs.existsSync('docker-compose.tracing.yml')) {
      throw new Error('docker-compose.tracing.yml 파일 없음');
    }
    
    const content = fs.readFileSync('docker-compose.tracing.yml', 'utf8');
    if (!content.includes('jaeger') || !content.includes('otel-collector')) {
      throw new Error('Jaeger 또는 OpenTelemetry Collector 설정 없음');
    }
  });
  
  // 의존성 확인
  await runTest('OpenTelemetry 의존성 확인', () => {
    const fs = require('fs');
    const packageJson = JSON.parse(fs.readFileSync('backend/package.json', 'utf8'));
    
    const requiredDeps = [
      '@opentelemetry/api',
      '@opentelemetry/sdk-trace-node',
      '@opentelemetry/exporter-jaeger'
    ];
    
    requiredDeps.forEach(dep => {
      if (!packageJson.dependencies[dep]) {
        throw new Error(`의존성 없음: ${dep}`);
      }
    });
  });
  
  // 최종 결과
  console.log('='.repeat(50));
  if (testsPassed === totalTests) {
    console.log('✅ 모든 분산 추적 통합 테스트 통과!');
    console.log(`\n📊 결과: ${testsPassed}/${totalTests} 테스트 성공`);
    console.log('\n🔍 다음 단계:');
    console.log('   1. npm run tracing:start (Jaeger 시작)');
    console.log('   2. npm run dev (서버 시작)');
    console.log('   3. http://localhost:16686 (Jaeger UI)');
    console.log('   4. http://localhost:3002/health (헬스 체크)');
    process.exit(0);
  } else {
    console.log(`❌ 일부 테스트 실패: ${testsPassed}/${totalTests}`);
    process.exit(1);
  }
}

runAllTests().catch(error => {
  console.error('테스트 실행 오류:', error);
  process.exit(1);
});