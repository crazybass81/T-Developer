import { TestServer, TestClient } from '../helpers/test-server';
import { TestDataGenerator } from '../helpers/test-utils';

describe('API Integration Tests', () => {
  let testServer: TestServer;
  let testClient: TestClient;
  let port: number;

  beforeAll(async () => {
    testServer = new TestServer();
    port = await testServer.start();
    testClient = new TestClient(`http://localhost:${port}`);

    // 기본 라우트 설정
    testServer.getApp().get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    testServer.getApp().post('/api/projects', (req, res) => {
      const project = TestDataGenerator.project(req.body);
      res.status(201).json(project);
    });
  });

  afterAll(async () => {
    await testServer.stop();
  });

  test('should respond to health check', async () => {
    const response = await testClient.get('/health');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'ok');
    expect(response.body).toHaveProperty('timestamp');
  });

  test('should create project via API', async () => {
    const projectData = { name: 'Integration Test Project' };
    const response = await testClient.post('/api/projects', projectData);
    
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body).toHaveProperty('name', 'Integration Test Project');
  });
});