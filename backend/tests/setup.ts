// Jest 테스트 환경 설정
import { mockEnvironment } from './helpers/test-utils';

// 테스트 환경 변수 설정
const testEnvVars = {
  NODE_ENV: 'test',
  AWS_REGION: 'us-east-1',
  JWT_ACCESS_SECRET: 'test-jwt-secret',
  JWT_REFRESH_SECRET: 'test-refresh-secret',
  REDIS_HOST: 'localhost',
  REDIS_PORT: '6379'
};

// 전역 환경 변수 설정
Object.entries(testEnvVars).forEach(([key, value]) => {
  process.env[key] = value;
});

// 테스트 후 정리
afterEach(() => {
  jest.clearAllMocks();
});

// 전역 타임아웃 설정
jest.setTimeout(10000);