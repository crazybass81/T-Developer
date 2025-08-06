const { EnvCrypto } = require('../backend/dist/utils/crypto');

async function main() {
  const crypto = new EnvCrypto();
  
  try {
    await crypto.generateKey();
    console.log('\n📋 다음 단계:');
    console.log('1. .env.key 파일을 안전한 곳에 백업');
    console.log('2. .gitignore에 .env.key 추가 확인');
    console.log('3. 민감한 환경 변수 암호화 실행');
  } catch (error) {
    console.error('❌ 키 생성 실패:', error);
    process.exit(1);
  }
}

main();