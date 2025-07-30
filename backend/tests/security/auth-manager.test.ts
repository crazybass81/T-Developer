import { AuthManager } from '../../src/security/auth-manager';

describe('AuthManager', () => {
  let authManager: AuthManager;
  
  beforeEach(() => {
    authManager = new AuthManager();
  });
  
  describe('Password Management', () => {
    test('should hash password correctly', async () => {
      const password = 'testPassword123';
      const hash = await authManager.hashPassword(password);
      
      expect(hash).toBeDefined();
      expect(hash).not.toBe(password);
      expect(hash.length).toBeGreaterThan(50);
    });
    
    test('should verify password correctly', async () => {
      const password = 'testPassword123';
      const hash = await authManager.hashPassword(password);
      
      const isValid = await authManager.verifyPassword(password, hash);
      expect(isValid).toBe(true);
      
      const isInvalid = await authManager.verifyPassword('wrongPassword', hash);
      expect(isInvalid).toBe(false);
    });
  });
  
  describe('Token Management', () => {
    test('should generate valid tokens', () => {
      const user = {
        id: 'user123',
        email: 'test@example.com',
        role: 'user' as const,
        permissions: ['project:read']
      };
      
      const tokens = authManager.generateTokens(user);
      
      expect(tokens.accessToken).toBeDefined();
      expect(tokens.refreshToken).toBeDefined();
      expect(typeof tokens.accessToken).toBe('string');
      expect(typeof tokens.refreshToken).toBe('string');
    });
    
    test('should verify token correctly', () => {
      const user = {
        id: 'user123',
        email: 'test@example.com',
        role: 'user' as const,
        permissions: ['project:read']
      };
      
      const tokens = authManager.generateTokens(user);
      const payload = authManager.verifyToken(tokens.accessToken);
      
      expect(payload.userId).toBe(user.id);
      expect(payload.email).toBe(user.email);
      expect(payload.role).toBe(user.role);
      expect(payload.permissions).toEqual(user.permissions);
    });
    
    test('should reject invalid token', () => {
      expect(() => {
        authManager.verifyToken('invalid.token.here');
      }).toThrow('Invalid token');
    });
  });
});