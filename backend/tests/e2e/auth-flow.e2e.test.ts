import { E2ETestEnvironment } from './setup';
import { TestClient } from '../helpers/test-server';

describe('Authentication Flow E2E Tests', () => {
  let testEnv: E2ETestEnvironment;
  let client: TestClient;

  beforeAll(async () => {
    testEnv = new E2ETestEnvironment();
    await testEnv.setup();
    client = new TestClient('http://localhost:8080');
  }, 60000); // 60초 타임아웃

  afterAll(async () => {
    await testEnv.teardown();
  }, 30000);

  describe('Complete Authentication Flow', () => {
    it('should complete full login -> access protected resource -> refresh token flow', async () => {
      // 1. Login
      const loginResponse = await client.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'testpassword123'
      });

      expect(loginResponse.status).toBe(200);
      expect(loginResponse.body).toHaveProperty('accessToken');
      expect(loginResponse.body).toHaveProperty('refreshToken');

      const { accessToken, refreshToken } = loginResponse.body as any;

      // 2. Access protected resource
      const profileResponse = await client.get('/api/auth/profile', {
        'Authorization': `Bearer ${accessToken}`
      });

      expect(profileResponse.status).toBe(200);
      expect(profileResponse.body).toHaveProperty('user');

      // 3. Refresh token
      const refreshResponse = await client.post('/api/auth/refresh', {
        refreshToken
      });

      expect(refreshResponse.status).toBe(200);
      expect(refreshResponse.body).toHaveProperty('accessToken');
      expect(refreshResponse.body).toHaveProperty('refreshToken');

      // 4. Use new token
      const newProfileResponse = await client.get('/api/auth/profile', {
        'Authorization': `Bearer ${(refreshResponse.body as any).accessToken}`
      });

      expect(newProfileResponse.status).toBe(200);
    });

    it('should handle rate limiting on login attempts', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'wrongpassword'
      };

      // Make multiple failed login attempts
      const attempts = [];
      for (let i = 0; i < 6; i++) {
        attempts.push(client.post('/api/auth/login', loginData));
      }

      const responses = await Promise.all(attempts);
      
      // Should eventually get rate limited
      const rateLimitedResponse = responses.find(r => r.status === 429);
      expect(rateLimitedResponse).toBeDefined();
    });
  });

  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await client.get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('timestamp');
    });
  });
});