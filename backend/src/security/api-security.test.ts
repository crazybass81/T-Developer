import { APIKeyManager, HMACValidator, ScopeManager } from './api-security';
import crypto from 'crypto';

describe('APIKeyManager', () => {
  test('generates valid API key', () => {
    const key = APIKeyManager.generateAPIKey();
    expect(key).toMatch(/^sk_[A-Za-z0-9_-]{43}$/);
  });

  test('validates API key format', () => {
    const validKey = 'sk_' + 'a'.repeat(43);
    const invalidKey = 'invalid_key';
    
    expect(APIKeyManager.validateKeyFormat(validKey)).toBe(true);
    expect(APIKeyManager.validateKeyFormat(invalidKey)).toBe(false);
  });

  test('hashes API key consistently', () => {
    const key = 'sk_test123';
    const hash1 = APIKeyManager.hashAPIKey(key);
    const hash2 = APIKeyManager.hashAPIKey(key);
    
    expect(hash1).toBe(hash2);
    expect(hash1).toHaveLength(64);
  });
});

describe('HMACValidator', () => {
  test('generates and validates signature', () => {
    const secret = 'test-secret';
    const method = 'POST';
    const path = '/api/test';
    const timestamp = Math.floor(Date.now() / 1000);
    const body = { test: 'data' };

    const signature = HMACValidator.generateSignature(secret, method, path, timestamp, body);
    expect(signature).toHaveLength(64);

    const mockReq = {
      method,
      path,
      body,
      headers: {
        'x-signature': signature,
        'x-timestamp': timestamp.toString()
      }
    } as any;

    expect(HMACValidator.validateRequest(mockReq, secret)).toBe(true);
  });

  test('rejects expired timestamp', () => {
    const mockReq = {
      method: 'GET',
      path: '/api/test',
      headers: {
        'x-signature': 'valid-signature',
        'x-timestamp': (Math.floor(Date.now() / 1000) - 400).toString()
      }
    } as any;

    expect(HMACValidator.validateRequest(mockReq, 'secret')).toBe(false);
  });
});

describe('ScopeManager', () => {
  test('validates scopes correctly', () => {
    const userScopes = ['projects:read', 'projects:write'];
    const requiredScopes = ['projects:read'];
    
    expect(ScopeManager.validateScopes(requiredScopes, userScopes)).toBe(true);
    expect(ScopeManager.validateScopes(['projects:delete'], userScopes)).toBe(false);
  });

  test('admin scope grants all permissions', () => {
    const adminScopes = ['admin:all'];
    const anyRequiredScopes = ['projects:delete', 'billing:write'];
    
    expect(ScopeManager.validateScopes(anyRequiredScopes, adminScopes)).toBe(true);
  });
});