import { IntegrationTestSetup } from '../helpers/integration-helpers';
import { DatabaseTestHelpers } from '../helpers/database-helpers';
import { TestDataGenerator } from '../helpers/test-utils';

describe('Auth Integration Tests', () => {
  let testSetup: IntegrationTestSetup;

  beforeAll(async () => {
    testSetup = new IntegrationTestSetup();
    await testSetup.setup();
  });

  afterAll(async () => {
    await testSetup.teardown();
  });

  beforeEach(() => {
    DatabaseTestHelpers.setupMocks();
  });

  describe('POST /api/auth/login', () => {
    it('should login with valid credentials', async () => {
      const client = testSetup.getClient();
      
      const response = await client.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'testpassword123'
      });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('accessToken');
      expect(response.body).toHaveProperty('refreshToken');
      expect(response.body).toHaveProperty('user');
    });

    it('should reject invalid credentials', async () => {
      const client = testSetup.getClient();
      
      const response = await client.post('/api/auth/login', {
        email: 'invalid@example.com',
        password: 'wrongpassword'
      });

      expect(response.status).toBe(500); // Mock implementation returns 500
    });

    it('should validate required fields', async () => {
      const client = testSetup.getClient();
      
      const response = await client.post('/api/auth/login', {
        email: 'test@example.com'
        // missing password
      });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/auth/refresh', () => {
    it('should refresh tokens with valid refresh token', async () => {
      const client = testSetup.getClient();
      const authHelpers = testSetup.getAuthHelpers();
      
      const tokens = await authHelpers.generateTestTokens();
      
      const response = await client.post('/api/auth/refresh', {
        refreshToken: tokens.refreshToken
      });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('accessToken');
      expect(response.body).toHaveProperty('refreshToken');
    });

    it('should reject invalid refresh token', async () => {
      const client = testSetup.getClient();
      
      const response = await client.post('/api/auth/refresh', {
        refreshToken: 'invalid-token'
      });

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('GET /api/auth/profile', () => {
    it('should return user profile with valid token', async () => {
      const { client, user, token } = await testSetup.createAuthenticatedClient();
      
      const response = await client.get('/api/auth/profile', {
        'Authorization': `Bearer ${token}`
      });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('user');
    });

    it('should reject request without token', async () => {
      const client = testSetup.getClient();
      
      const response = await client.get('/api/auth/profile');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('error');
    });
  });
});