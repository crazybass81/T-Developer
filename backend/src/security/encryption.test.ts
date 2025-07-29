import { EncryptionService, DataMasking } from './encryption';

describe('EncryptionService', () => {
  let encryptionService: EncryptionService;

  beforeEach(() => {
    process.env.AWS_REGION = 'us-east-1';
    process.env.KMS_MASTER_KEY_ID = 'test-key-id';
    encryptionService = new EncryptionService();
  });

  test('symmetric encryption/decryption', () => {
    const plaintext = 'sensitive data';
    const password = 'test-password';
    
    const encrypted = encryptionService.encryptSymmetric(plaintext, password);
    const decrypted = encryptionService.decryptSymmetric(encrypted, password);
    
    expect(decrypted).toBe(plaintext);
    expect(encrypted).not.toBe(plaintext);
  });

  test('hash generation', () => {
    const data = 'test data';
    const hash = encryptionService.hash(data);
    
    expect(hash).toHaveLength(64);
    expect(encryptionService.hash(data)).toBe(hash);
  });

  test('secure token generation', () => {
    const token = encryptionService.generateSecureToken();
    expect(token).toHaveLength(43); // base64url encoded 32 bytes
    
    const shortToken = encryptionService.generateSecureToken(16);
    expect(shortToken).toHaveLength(22); // base64url encoded 16 bytes
  });
});

describe('DataMasking', () => {
  test('email masking', () => {
    expect(DataMasking.maskEmail('test@example.com')).toBe('t**t@example.com');
    expect(DataMasking.maskEmail('a@example.com')).toBe('*@example.com');
    expect(DataMasking.maskEmail('invalid')).toBe('***');
  });

  test('phone masking', () => {
    expect(DataMasking.maskPhone('123-456-7890')).toBe('******7890');
    expect(DataMasking.maskPhone('123')).toBe('***');
  });

  test('credit card masking', () => {
    expect(DataMasking.maskCreditCard('1234-5678-9012-3456')).toBe('************3456');
    expect(DataMasking.maskCreditCard('123')).toBe('***');
  });

  test('object masking', () => {
    const obj = {
      name: 'John Doe',
      email: 'john@example.com',
      phone: '123-456-7890',
      nested: {
        cardNumber: '1234-5678-9012-3456'
      }
    };

    const masked = DataMasking.maskObject(obj, ['email', 'phone', 'nested.cardNumber']);
    
    expect(masked.name).toBe('John Doe');
    expect(masked.email).toBe('j***@example.com');
    expect(masked.phone).toBe('******7890');
    expect(masked.nested.cardNumber).toBe('************3456');
  });
});