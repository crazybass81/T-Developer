import { IntegrationTestSetup } from '../helpers/integration-helpers';

describe('Health Check Integration Tests', () => {
  let testSetup: IntegrationTestSetup;

  beforeAll(async () => {
    testSetup = new IntegrationTestSetup();
    await testSetup.setup();
  });

  afterAll(async () => {
    await testSetup.teardown();
  });

  describe('GET /health', () => {
    it('should return health status', async () => {
      const client = testSetup.getClient();
      
      const response = await client.get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('requestId');
    });
  });

  describe('GET /nonexistent', () => {
    it('should return 404 for unknown routes', async () => {
      const client = testSetup.getClient();
      
      const response = await client.get('/nonexistent');

      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error', 'Not Found');
      expect(response.body).toHaveProperty('path', '/nonexistent');
      expect(response.body).toHaveProperty('requestId');
    });
  });
});