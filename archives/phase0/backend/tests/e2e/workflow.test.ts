import { E2ETestEnvironment } from './setup';
import { TestClient } from '../helpers/test-server';

describe('E2E Workflow Tests', () => {
  let testEnv: E2ETestEnvironment;
  let client: TestClient;

  beforeAll(async () => {
    testEnv = new E2ETestEnvironment();
    await testEnv.setup();
    client = new TestClient('http://localhost:8080');
  }, 60000);

  afterAll(async () => {
    await testEnv.teardown();
  }, 30000);

  test('should complete full project workflow', async () => {
    // 1. 프로젝트 생성
    const createResponse = await client.post('/api/projects', {
      name: 'E2E Test Project',
      description: 'Full workflow test'
    });
    
    expect(createResponse.status).toBe(201);
    const projectId = createResponse.body.id;

    // 2. 프로젝트 상태 확인
    const statusResponse = await client.get(`/api/projects/${projectId}`);
    expect(statusResponse.status).toBe(200);
    expect(statusResponse.body.name).toBe('E2E Test Project');
  });
});