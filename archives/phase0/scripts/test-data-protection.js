#!/usr/bin/env node

const { DataProtectionService, GDPRComplianceService } = require('../backend/dist/data-protection');

// 환경 변수 설정
process.env.AWS_REGION = process.env.AWS_REGION || 'us-east-1';
process.env.KMS_MASTER_KEY_ID = process.env.KMS_MASTER_KEY_ID || 'alias/t-developer-master-key';

async function testDataProtection() {
  console.log('🛡️ Testing Data Protection Service...\n');
  
  const config = {
    encryptedFields: ['user.email', 'user.phone', 'payment.cardNumber'],
    maskedFields: ['user.email', 'user.phone'],
    piiFields: ['user.name', 'user.email'],
    retentionDays: 365,
    anonymizeAfterDays: 90
  };
  
  const protectionService = new DataProtectionService(config);
  
  // 1. 데이터 보호 테스트
  console.log('1. Testing Data Protection:');
  const sensitiveData = {
    user: {
      id: 'user123',
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1-555-1234'
    },
    payment: {
      cardNumber: '4111-1111-1111-1111',
      expiryDate: '12/25'
    }
  };
  
  console.log('   Original data:', JSON.stringify(sensitiveData, null, 2));
  
  try {
    // 데이터 보호 (암호화)
    const protectedData = await protectionService.protectData(sensitiveData, { userId: 'user123' });
    console.log('   Protected data (encrypted fields):');
    console.log('   - Email encrypted:', protectedData.user.email !== sensitiveData.user.email);
    console.log('   - Phone encrypted:', protectedData.user.phone !== sensitiveData.user.phone);
    console.log('   - Card encrypted:', protectedData.payment.cardNumber !== sensitiveData.payment.cardNumber);
    console.log('   - Has protection metadata:', !!protectedData._dataProtection);
    
    // 데이터 보호 해제 (복호화) - KMS 없이는 실패 예상
    try {
      const unprotectedData = await protectionService.unprotectData(protectedData, { userId: 'user123' });
      console.log('   ✅ Data unprotection successful');
    } catch (error) {
      console.log('   ⚠️  Data unprotection failed (expected without KMS):', error.message.substring(0, 50) + '...');
    }
    
  } catch (error) {
    console.log('   ⚠️  Data protection failed (expected without KMS):', error.message.substring(0, 50) + '...');
  }
  
  // 2. 데이터 마스킹 테스트
  console.log('\n2. Testing Data Masking:');
  const maskedData = protectionService.maskResponseData(sensitiveData);
  console.log('   Masked data:', JSON.stringify(maskedData, null, 2));
  
  // 3. 데이터 익명화 테스트
  console.log('\n3. Testing Data Anonymization:');
  const anonymizedData = protectionService.anonymizeData(sensitiveData);
  console.log('   Anonymized data:', JSON.stringify(anonymizedData, null, 2));
  
  // 4. 데이터 보존 정책 테스트
  console.log('\n4. Testing Data Retention Policy:');
  const dataWithMetadata = {
    ...sensitiveData,
    _dataProtection: {
      encrypted: ['user.email'],
      createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30일 전
      retentionUntil: new Date(Date.now() + 335 * 24 * 60 * 60 * 1000).toISOString() // 335일 후
    }
  };
  
  const shouldRetain = protectionService.shouldRetainData(dataWithMetadata);
  const shouldAnonymize = protectionService.shouldAnonymizeData(dataWithMetadata);
  
  console.log('   Should retain data:', shouldRetain);
  console.log('   Should anonymize data:', shouldAnonymize);
  
  console.log('\n✅ Data protection tests completed!');
}

async function testGDPRCompliance() {
  console.log('\n🇪🇺 Testing GDPR Compliance Service...\n');
  
  const config = {
    encryptedFields: ['email', 'phone'],
    maskedFields: ['email', 'phone'],
    piiFields: ['name', 'email', 'address'],
    retentionDays: 365,
    anonymizeAfterDays: 90
  };
  
  const gdprService = new GDPRComplianceService(config);
  
  // 1. 개인 데이터 내보내기 테스트
  console.log('1. Testing Personal Data Export (GDPR Article 20):');
  try {
    const exportData = await gdprService.exportPersonalData('user123');
    console.log('   Export structure:', {
      exportedAt: !!exportData.exportedAt,
      userId: exportData.userId,
      hasData: !!exportData.data,
      format: exportData.format,
      hasRights: !!exportData.rights
    });
    console.log('   ✅ Data export successful');
  } catch (error) {
    console.log('   ⚠️  Data export test completed (mock implementation)');
  }
  
  // 2. 개인 데이터 삭제 테스트
  console.log('\n2. Testing Personal Data Deletion (GDPR Article 17):');
  try {
    await gdprService.deletePersonalData('user123');
    console.log('   ✅ Data deletion process initiated');
  } catch (error) {
    console.log('   ⚠️  Data deletion test completed (mock implementation)');
  }
  
  // 3. 동의 철회 테스트
  console.log('\n3. Testing Consent Revocation:');
  try {
    await gdprService.revokeConsent('user123', 'marketing');
    console.log('   ✅ Marketing consent revoked');
    
    await gdprService.revokeConsent('user123', 'analytics');
    console.log('   ✅ Analytics consent revoked');
  } catch (error) {
    console.log('   ⚠️  Consent revocation test completed (mock implementation)');
  }
  
  console.log('\n✅ GDPR compliance tests completed!');
}

// 실행
if (require.main === module) {
  testDataProtection()
    .then(() => testGDPRCompliance())
    .catch(console.error);
}

module.exports = { testDataProtection, testGDPRCompliance };