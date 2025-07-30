// Test setup for messaging tests
import { jest } from '@jest/globals';

// Global test setup
beforeAll(() => {
  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.AWS_REGION = 'us-east-1';
  process.env.AGENT_TASKS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/agent-tasks';
  process.env.NOTIFICATIONS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/notifications';
  process.env.DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/123/dlq';
});

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});

// Mock console methods to reduce test noise
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};