import { IndexManager } from '../../../src/data/management/index-manager';

describe('IndexManager', () => {
  const mockDynamoDB = {
    send: jest.fn()
  };

  const mockCloudWatch = {
    send: jest.fn()
  };

  const indexManager = new IndexManager(mockDynamoDB as any, mockCloudWatch as any);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('analyzes index usage', async () => {
    mockDynamoDB.send.mockResolvedValue({
      Table: {
        GlobalSecondaryIndexes: [
          { IndexName: 'GSI1' },
          { IndexName: 'GSI2' }
        ]
      }
    });

    mockCloudWatch.send.mockResolvedValue({
      Datapoints: [
        { Sum: 100, Average: 10 },
        { Sum: 200, Average: 20 }
      ]
    });

    const report = await indexManager.analyzeIndexUsage('TestTable', 7);

    expect(report.tableName).toBe('TestTable');
    expect(report.period).toBe(7);
    expect(report.indexes).toHaveLength(2);
    expect(report.recommendations).toBeDefined();
  });

  test('detects unused indexes', async () => {
    mockDynamoDB.send.mockResolvedValue({
      Table: {
        GlobalSecondaryIndexes: [
          { IndexName: 'UnusedGSI' }
        ]
      }
    });

    mockCloudWatch.send.mockResolvedValue({
      Datapoints: [] // No usage data
    });

    const unusedIndexes = await indexManager.detectUnusedIndexes('TestTable', 30);

    expect(unusedIndexes).toHaveLength(1);
    expect(unusedIndexes[0].indexName).toBe('UnusedGSI');
    expect(unusedIndexes[0].recommendation).toContain('removing');
  });
});