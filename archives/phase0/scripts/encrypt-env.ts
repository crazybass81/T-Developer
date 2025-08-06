const { encryptEnvFile } = require('../backend/src/utils/crypto');

async function main() {
  try {
    await encryptEnvFile();
    console.log('\n📋 암호화 완료:');
    console.log('- .env.encrypted 파일이 생성되었습니다');
    console.log('- 원본 .env 파일은 그대로 유지됩니다');
    console.log('- 프로덕션에서는 .env.encrypted를 사용하세요');
  } catch (error) {
    console.error('❌ 암호화 실패:', error);
    process.exit(1);
  }
}

main();