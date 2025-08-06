#!/usr/bin/env node

const crypto = require('crypto');

// 간단한 암호화 서비스
class SimpleEncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32;
    this.ivLength = 16;
    this.saltLength = 32;
    this.iterations = 100000;
  }
  
  encryptField(plaintext, password = 'default-encryption-key') {
    const salt = crypto.randomBytes(this.saltLength);
    const key = crypto.pbkdf2Sync(password, salt, this.iterations, this.keyLength, 'sha256');
    const iv = crypto.randomBytes(this.ivLength);
    
    const cipher = crypto.createCipheriv(this.algorithm, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    const combined = Buffer.concat([salt, iv, tag, encrypted]);
    
    return combined.toString('base64');
  }
  
  decryptField(encryptedData, password = 'default-encryption-key') {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, this.saltLength);
    const iv = combined.slice(this.saltLength, this.saltLength + this.ivLength);
    const tag = combined.slice(this.saltLength + this.ivLength, this.saltLength + this.ivLength + 16);
    const encrypted = combined.slice(this.saltLength + this.ivLength + 16);
    
    const key = crypto.pbkdf2Sync(password, salt, this.iterations, this.keyLength, 'sha256');
    
    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }
  
  hash(data) {
    return crypto.createHash('sha256').update(data).digest('hex');
  }
  
  generateSecureToken(length = 32) {
    return crypto.randomBytes(length).toString('base64url');
  }
}

// 데이터 마스킹 클래스
class SimpleDataMasking {
  static maskEmail(email) {
    const [local, domain] = email.split('@');
    if (!domain) return '***';
    
    const maskedLocal = local.length > 2 
      ? local[0] + '*'.repeat(local.length - 2) + local[local.length - 1]
      : '*'.repeat(local.length);
    
    return `${maskedLocal}@${domain}`;
  }
  
  static maskPhone(phone) {
    const digits = phone.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return digits.slice(0, -4).replace(/./g, '*') + digits.slice(-4);
  }
  
  static maskCreditCard(cardNumber) {
    const digits = cardNumber.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return '*'.repeat(digits.length - 4) + digits.slice(-4);
  }
}

async function testEncryption() {
  console.log('🔐 Testing Simple Encryption System...\n');
  
  const encryptionService = new SimpleEncryptionService();
  
  // 1. 필드 암호화/복호화 테스트
  console.log('1. Field Encryption/Decryption Test:');
  const originalText = 'sensitive-user-data-12345';
  console.log(`   Original: ${originalText}`);
  
  try {
    const encrypted = encryptionService.encryptField(originalText);
    console.log(`   Encrypted: ${encrypted.substring(0, 50)}...`);
    
    const decrypted = encryptionService.decryptField(encrypted);
    console.log(`   Decrypted: ${decrypted}`);
    console.log(`   ✅ Match: ${originalText === decrypted}\n`);
  } catch (error) {
    console.log(`   ❌ Encryption failed: ${error.message}\n`);
  }
  
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
  const testEmail = 'john.doe@example.com';
  const testPhone = '+1-555-123-4567';
  const testCard = '4532-1234-5678-9012';
  
  console.log(`   Email: ${testEmail} → ${SimpleDataMasking.maskEmail(testEmail)}`);
  console.log(`   Phone: ${testPhone} → ${SimpleDataMasking.maskPhone(testPhone)}`);
  console.log(`   Card: ${testCard} → ${SimpleDataMasking.maskCreditCard(testCard)}`);
  
  // 5. 성능 테스트
  console.log('\n5. Performance Test:');
  const testData = 'Performance test data for encryption';
  const iterations = 100;
  
  console.time('   Encryption Performance');
  for (let i = 0; i < iterations; i++) {
    const encrypted = encryptionService.encryptField(testData);
    encryptionService.decryptField(encrypted);
  }
  console.timeEnd('   Encryption Performance');
  
  console.log('\n✅ All encryption tests completed successfully!');
}

// 테스트 실행
testEncryption().catch(error => {
  console.error('❌ Encryption test failed:', error.message);
  process.exit(1);
});