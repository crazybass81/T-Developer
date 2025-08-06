#!/usr/bin/env node

const { EncryptionService, DataMasking, EncryptionMiddleware } = require('../backend/src/security/encryption');

async function testEncryption() {
  console.log('🔐 Testing Encryption System...\n');
  
  const encryptionService = new EncryptionService();
  
  // 1. 필드 암호화/복호화 테스트
  console.log('1. Field Encryption/Decryption Test:');
  const originalText = 'sensitive-user-data-12345';
  console.log(`   Original: ${originalText}`);
  
  const encrypted = encryptionService.encryptField(originalText);
  console.log(`   Encrypted: ${encrypted.substring(0, 50)}...`);
  
  const decrypted = encryptionService.decryptField(encrypted);
  console.log(`   Decrypted: ${decrypted}`);
  console.log(`   ✅ Match: ${originalText === decrypted}\n`);
  
  // 2. 해시 테스트
  console.log('2. Hash Test:');
  const password = 'mySecretPassword123';
  const hash1 = encryptionService.hash(password);
  const hash2 = encryptionService.hash(password);
  console.log(`   Password: ${password}`);
  console.log(`   Hash: ${hash1}`);
  console.log(`   ✅ Consistent: ${hash1 === hash2}\n`);
  
  // 3. 토큰 생성 테스트
  console.log('3. Secure Token Generation Test:');
  const token1 = encryptionService.generateSecureToken();
  const token2 = encryptionService.generateSecureToken();
  console.log(`   Token 1: ${token1}`);
  console.log(`   Token 2: ${token2}`);
  console.log(`   ✅ Unique: ${token1 !== token2}\n`);
  
  // 4. 데이터 마스킹 테스트
  console.log('4. Data Masking Test:');
  const testData = {
    email: 'john.doe@example.com',
    phone: '+1-555-123-4567',
    creditCard: '4532-1234-5678-9012',
    user: {
      personalEmail: 'jane@company.com'
    }
  };
  
  console.log('   Original Data:', JSON.stringify(testData, null, 2));
  
  const maskedData = DataMasking.maskObject(testData, ['email', 'phone', 'creditCard', 'user.personalEmail']);
  console.log('   Masked Data:', JSON.stringify(maskedData, null, 2));
  
  // 개별 마스킹 테스트
  console.log('\n   Individual Masking Tests:');
  console.log(`   Email: ${testData.email} → ${DataMasking.maskEmail(testData.email)}`);
  console.log(`   Phone: ${testData.phone} → ${DataMasking.maskPhone(testData.phone)}`);
  console.log(`   Card: ${testData.creditCard} → ${DataMasking.maskCreditCard(testData.creditCard)}`);
  
  console.log('\n✅ All encryption tests completed successfully!');
}

// 에러 처리
testEncryption().catch(error => {
  console.error('❌ Encryption test failed:', error.message);
  process.exit(1);
});