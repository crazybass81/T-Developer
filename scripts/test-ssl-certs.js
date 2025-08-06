#!/usr/bin/env node

/**
 * SSL 인증서 생성 및 검증 테스트 스크립트
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CERT_DIR = path.join(process.cwd(), 'certs');

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function checkCertificateValidity(certPath) {
  try {
    const result = execSync(`openssl x509 -in ${certPath} -text -noout`, { encoding: 'utf8' });
    return result.includes('localhost') && result.includes('T-Developer');
  } catch (error) {
    return false;
  }
}

async function testSSLCertificates() {
  console.log('🔐 SSL 인증서 테스트 시작...\n');
  
  const requiredFiles = [
    'rootCA.crt',
    'rootCA.key', 
    'server.crt',
    'server.key',
    'server.pem'
  ];
  
  let allFilesExist = true;
  
  // 파일 존재 확인
  console.log('📁 인증서 파일 존재 확인:');
  for (const file of requiredFiles) {
    const filePath = path.join(CERT_DIR, file);
    const exists = checkFileExists(filePath);
    const status = exists ? '✅ 존재' : '❌ 없음';
    
    console.log(`  ${file}: ${status}`);
    
    if (!exists) {
      allFilesExist = false;
    }
  }
  
  if (!allFilesExist) {
    console.log('\n❌ 일부 인증서 파일이 없습니다.');
    console.log('🔧 해결 방법: bash scripts/generate-ssl-certs.sh 실행');
    return false;
  }
  
  // 인증서 유효성 검증
  console.log('\n🔍 인증서 유효성 검증:');
  const serverCertPath = path.join(CERT_DIR, 'server.crt');
  const isValid = checkCertificateValidity(serverCertPath);
  
  if (isValid) {
    console.log('✅ 서버 인증서가 유효합니다 (localhost, T-Developer)');
  } else {
    console.log('❌ 서버 인증서가 유효하지 않습니다');
    return false;
  }
  
  // 파일 크기 확인
  console.log('\n📊 인증서 파일 크기:');
  for (const file of requiredFiles) {
    const filePath = path.join(CERT_DIR, file);
    const stats = fs.statSync(filePath);
    console.log(`  ${file}: ${(stats.size / 1024).toFixed(2)} KB`);
  }
  
  console.log('\n✅ 모든 SSL 인증서 테스트 통과!');
  console.log('\n🚀 다음 단계:');
  console.log('1. Root CA를 시스템에 신뢰할 인증서로 추가');
  console.log('2. USE_HTTPS=true 환경 변수로 HTTPS 서버 실행');
  console.log('3. https://localhost 접속 테스트');
  
  return true;
}

// 스크립트 실행
if (require.main === module) {
  testSSLCertificates()
    .then((success) => {
      process.exit(success ? 0 : 1);
    })
    .catch((error) => {
      console.error('❌ 테스트 실행 중 오류:', error);
      process.exit(1);
    });
}

module.exports = { testSSLCertificates };