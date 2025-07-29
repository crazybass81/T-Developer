import { AuthManager } from '../../src/utils/auth';
import { TestDataGenerator } from './test-utils';

export class AuthTestHelpers {
  private authManager = new AuthManager();

  async createTestUser(overrides?: any) {
    const userData = TestDataGenerator.user(overrides);
    const hashedPassword = await this.authManager.hashPassword('testpassword123');
    
    return {
      ...userData,
      password: hashedPassword
    };
  }

  async generateTestTokens(userOverrides?: any) {
    const user = TestDataGenerator.user(userOverrides);
    return this.authManager.generateTokens({
      userId: user.id,
      email: user.email,
      role: user.role as 'user' | 'admin'
    });
  }

  createAuthHeaders(token: string) {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  mockAuthenticatedRequest(userOverrides?: any) {
    const user = TestDataGenerator.user(userOverrides);
    return {
      user,
      headers: this.createAuthHeaders('mock-token')
    };
  }
}