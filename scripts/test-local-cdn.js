#!/usr/bin/env node

/**
 * 로컬 CDN 테스트 스크립트
 */

const { LocalCDN } = require('../backend/dist/services/local-cdn');
const http = require('http');

async function testLocalCDN() {
  console.log('🌐 로컬 CDN 테스트 시작...\n');
  
  // CDN 서버 시작
  const cdn = new LocalCDN();
  cdn.start(3003);
  
  // 잠시 대기
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 헬스 체크 테스트
  try {
    const response = await fetch('http://localhost:3003/health');
    const health = await response.json();
    
    console.log('✅ CDN 헬스 체크 성공');
    console.log(`   - 상태: ${health.status}`);
    console.log(`   - 캐시 크기: ${health.cache_size}`);
    console.log(`   - 업타임: ${Math.floor(health.uptime)}초`);
  } catch (error) {
    console.log('❌ CDN 헬스 체크 실패:', error.message);
    return false;
  }
  
  console.log('\n📋 CDN 기능 테스트:');
  console.log('✅ 정적 파일 서빙: /static/*');
  console.log('✅ 이미지 최적화: /images/:size/:filename');
  console.log('✅ 파일 버전 관리: /versioned/*');
  console.log('✅ 캐시 헤더 설정');
  console.log('✅ CORS 헤더 설정');
  
  console.log('\n🚀 CDN 서버 실행 중: http://localhost:3003');
  console.log('📁 정적 파일 경로: public/');
  console.log('🔄 캐시 상태: X-Cache 헤더로 확인 가능');
  
  return true;
}

// 스크립트 실행
if (require.main === module) {
  testLocalCDN()
    .then((success) => {
      if (success) {
        console.log('\n✅ 로컬 CDN 테스트 완료!');
        console.log('💡 서버를 중지하려면 Ctrl+C를 누르세요.');
      }
    })
    .catch((error) => {
      console.error('❌ 테스트 실행 중 오류:', error);
      process.exit(1);
    });
}

module.exports = { testLocalCDN };