import { AuthManager } from '../../src/utils/auth';
import { AuthTestHelpers } from '../helpers/auth-helpers';
import { mockEnvironment } from '../helpers/test-utils';

describe('AuthManager', () => {
  let authManager: AuthManager;
  let authHelpers: AuthTestHelpers;
  let restoreEnv: () => void;

  beforeAll(() => {
    restoreEnv = mockEnvironment({
      JWT_ACCESS_SECRET: 'test-access-secret',
      JWT_REFRESH_SECRET: 'test-refresh-secret'
    });
  });

  afterAll(() => {
    restoreEnv();
  });

  beforeEach(() => {
    authManager = new AuthManager();
    authHelpers = new AuthTestHelpers();
  });

  describe('generateTokens', () => {
    it('should generate access and refresh tokens', async () => {
      const payload = {
        userId: 'user123',
        email: 'test@example.com',
        role: 'user' as const
      };

      const tokens = await authManager.generateTokens(payload);

      expect(tokens.accessToken).toBeDefined();
      expect(tokens.refreshToken).toBeDefined();
      expect(typeof tokens.accessToken).toBe('string');
      expect(typeof tokens.refreshToken).toBe('string');
    });
  });

  describe('verifyAccessToken', () => {
    it('should verify valid access token', async () => {
      const payload = {
        userId: 'user123',
        email: 'test@example.com',
        role: 'user' as const
      };

      const tokens = await authManager.generateTokens(payload);
      const verified = await authManager.verifyAccessToken(tokens.accessToken);

      expect(verified.userId).toBe(payload.userId);
      expect(verified.email).toBe(payload.email);
      expect(verified.role).toBe(payload.role);
    });

    it('should reject invalid token', async () => {
      await expect(
        authManager.verifyAccessToken('invalid-token')
      ).rejects.toThrow('Invalid access token');
    });
  });

  describe('password hashing', () => {
    it('should hash and verify password', async () => {
      const password = 'testpassword123';
      const hash = await authManager.hashPassword(password);

      expect(hash).toBeDefined();
      expect(hash).not.toBe(password);

      const isValid = await authManager.verifyPassword(password, hash);
      expect(isValid).toBe(true);

      const isInvalid = await authManager.verifyPassword('wrongpassword', hash);
      expect(isInvalid).toBe(false);
    });
  });
});