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

// Mock AWS SDK
jest.mock('@aws-sdk/client-dynamodb');
jest.mock('@aws-sdk/lib-dynamodb');
jest.mock('@aws-sdk/client-s3');

// Mock Redis
jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => ({
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
    exists: jest.fn(),
    expire: jest.fn(),
    disconnect: jest.fn()
  }));
});

// 전역 타임아웃 설정
jest.setTimeout(10000);