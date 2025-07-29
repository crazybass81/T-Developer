import { mockEnvironment } from './helpers/test-utils';
import { DatabaseTestHelpers } from './helpers/database-helpers';

// Global test setup
beforeAll(() => {
  // Set test environment variables
  const restoreEnv = mockEnvironment({
    NODE_ENV: 'test',
    JWT_ACCESS_SECRET: 'test-access-secret',
    JWT_REFRESH_SECRET: 'test-refresh-secret',
    AWS_REGION: 'us-east-1',
    REDIS_HOST: 'localhost',
    REDIS_PORT: '6379'
  });

  // Store restore function globally for cleanup
  (global as any).restoreEnv = restoreEnv;
});

beforeEach(() => {
  // Setup database mocks for each test
  DatabaseTestHelpers.setupMocks();
});

afterAll(() => {
  // Restore original environment
  if ((global as any).restoreEnv) {
    (global as any).restoreEnv();
  }
});