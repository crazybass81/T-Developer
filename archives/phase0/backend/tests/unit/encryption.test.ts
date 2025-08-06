import { EncryptionService, DataMasking } from '../../src/security/encryption';
import crypto from 'crypto';

// Mock AWS KMS for testing
jest.mock('@aws-sdk/client-kms', () => ({
  KMSClient: jest.fn().mockImplementation(() => ({
    send: jest.fn()
  })),
  GenerateDataKeyCommand: jest.fn(),
  DecryptCommand: jest.fn()
}));

describe('EncryptionService', () => {
  let encryptionService: EncryptionService;

  beforeEach(() => {
    encryptionService = new EncryptionService();
  });

  describe('Symmetric Encryption', () => {
    it('should encrypt and decrypt data correctly', () => {
      const plaintext = 'sensitive data';
      const password = 'test-password';

      const encrypted = encryptionService.encryptSymmetric(plaintext, password);
      expect(encrypted).toBeDefined();
      expect(encrypted).not.toBe(plaintext);

      const decrypted = encryptionService.decryptSymmetric(encrypted, password);
      expect(decrypted).toBe(plaintext);
    });

    it('should fail with wrong password', () => {
      const plaintext = 'sensitive data';
      const password = 'test-password';
      const wrongPassword = 'wrong-password';

      const encrypted = encryptionService.encryptSymmetric(plaintext, password);
      
      expect(() => {
        encryptionService.decryptSymmetric(encrypted, wrongPassword);
      }).toThrow();
    });
  });

  describe('Hash Function', () => {
    it('should generate consistent hash', () => {
      const data = 'test data';
      const hash1 = encryptionService.hash(data);
      const hash2 = encryptionService.hash(data);

      expect(hash1).toBe(hash2);
      expect(hash1).toHaveLength(64); // SHA-256 hex length
    });

    it('should generate different hashes for different data', () => {
      const hash1 = encryptionService.hash('data1');
      const hash2 = encryptionService.hash('data2');

      expect(hash1).not.toBe(hash2);
    });
  });

  describe('Secure Token Generation', () => {
    it('should generate tokens of correct length', () => {
      const token32 = encryptionService.generateSecureToken(32);
      const token64 = encryptionService.generateSecureToken(64);

      expect(token32).toBeDefined();
      expect(token64).toBeDefined();
      expect(token32.length).toBeGreaterThan(0);
      expect(token64.length).toBeGreaterThan(token32.length);
    });

    it('should generate unique tokens', () => {
      const token1 = encryptionService.generateSecureToken();
      const token2 = encryptionService.generateSecureToken();

      expect(token1).not.toBe(token2);
    });
  });
});

describe('DataMasking', () => {
  describe('Email Masking', () => {
    it('should mask email addresses correctly', () => {
      expect(DataMasking.maskEmail('user@example.com')).toBe('u**r@example.com');
      expect(DataMasking.maskEmail('a@test.com')).toBe('*@test.com');
      expect(DataMasking.maskEmail('ab@test.com')).toBe('**@test.com');
      expect(DataMasking.maskEmail('invalid-email')).toBe('***');
    });
  });

  describe('Phone Masking', () => {
    it('should mask phone numbers correctly', () => {
      expect(DataMasking.maskPhone('123-456-7890')).toBe('******7890');
      expect(DataMasking.maskPhone('555-1234')).toBe('****1234');
      expect(DataMasking.maskPhone('123')).toBe('***');
    });
  });

  describe('Object Masking', () => {
    it('should mask sensitive fields in objects', () => {
      const data = {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '555-1234',
        profile: {
          email: 'john.work@company.com'
        }
      };

      const masked = DataMasking.maskObject(data, ['email', 'phone', 'profile.email']);

      expect(masked.name).toBe('John Doe');
      expect(masked.email).toBe('j**n@example.com');
      expect(masked.phone).toBe('***1234');
      expect(masked.profile.email).toBe('j*******k@company.com');
    });

    it('should handle missing fields gracefully', () => {
      const data = { name: 'John' };
      const masked = DataMasking.maskObject(data, ['email', 'missing.field']);

      expect(masked).toEqual(data);
    });
  });
});