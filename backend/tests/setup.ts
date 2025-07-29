import { jest } from '@jest/globals';

// Global test setup
beforeAll(async () => {
  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.LOG_LEVEL = 'error';
  process.env.DYNAMODB_ENDPOINT = 'http://localhost:8000';
  process.env.REDIS_HOST = 'localhost';
});

afterAll(async () => {
  // Cleanup after all tests
  jest.clearAllMocks();
});

// Mock AWS SDK
jest.mock('@aws-sdk/client-dynamodb');
jest.mock('@aws-sdk/lib-dynamodb');
jest.mock('@aws-sdk/client-bedrock');
jest.mock('@aws-sdk/client-s3');