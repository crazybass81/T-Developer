import { encryptEnvFile } from '../backend/src/utils/crypto';

async function main() {
  try {
    await encryptEnvFile();
    
    console.log('\n📋 암호화 완료:');
    console.log('- 원본: .env');
    console.log('- 암호화된 파일: .env.encrypted');
    console.log('\n⚠️  주의사항:');
    console.log('- .env.key 파일을 절대 커밋하지 마세요');
    console.log('- 프로덕션에서는 .env.encrypted 사용');
    
  } catch (error) {
    console.error('❌ 암호화 실패:', error);
    process.exit(1);
  }
}

main();