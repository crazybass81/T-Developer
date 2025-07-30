// Global test setup
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn()
};

// Mock AWS SDK
jest.mock('@aws-sdk/lib-dynamodb', () => ({
  QueryCommand: jest.fn().mockImplementation((params) => ({ input: params })),
  DynamoDBDocumentClient: {
    from: jest.fn()
  }
}));

jest.mock('@aws-sdk/client-dynamodb', () => ({
  DynamoDBClient: jest.fn(),
  DescribeTableCommand: jest.fn()
}));

jest.mock('@aws-sdk/client-cloudwatch', () => ({
  CloudWatchClient: jest.fn(),
  GetMetricStatisticsCommand: jest.fn()
}));