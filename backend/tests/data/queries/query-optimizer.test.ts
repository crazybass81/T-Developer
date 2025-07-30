import { QueryOptimizer, QueryPerformanceMonitor } from '../../../src/data/optimization/query-optimizer';

describe('QueryOptimizer', () => {
  const optimizer = new QueryOptimizer();

  test('analyzes query and provides recommendations', async () => {
    const query = {
      TableName: 'TestTable',
      KeyConditionExpression: '#pk = :pk',
      ExpressionAttributeValues: { ':pk': 'USER#123' }
    };

    const analysis = await optimizer.analyzeQuery(query);

    expect(analysis.estimatedRCU).toBeGreaterThan(0);
    expect(analysis.indexEfficiency).toBeDefined();
    expect(analysis.recommendations).toContainEqual(
      expect.objectContaining({
        type: 'PROJECTION',
        message: 'Add ProjectionExpression to reduce data transfer'
      })
    );
  });

  test('optimizes query by adding projection', async () => {
    const originalQuery = {
      TableName: 'TestTable',
      KeyConditionExpression: '#pk = :pk'
    };

    const optimized = await optimizer.optimizeQuery(originalQuery);

    expect(optimized.Limit).toBeDefined();
  });

  test('generates cache key consistently', () => {
    const query = {
      TableName: 'TestTable',
      ExpressionAttributeValues: { ':pk': 'USER#123' }
    };

    const key1 = optimizer.getCacheKey(query);
    const key2 = optimizer.getCacheKey(query);

    expect(key1).toBe(key2);
    expect(key1).toHaveLength(64); // SHA256 hex length
  });
});

describe('QueryPerformanceMonitor', () => {
  const monitor = new QueryPerformanceMonitor();

  test('tracks query metrics', async () => {
    await monitor.trackQuery('test-query', 150, 25, 5);

    const metrics = monitor.getMetrics();
    const queryMetrics = metrics.get('test-query');

    expect(queryMetrics).toBeDefined();
    expect(queryMetrics!.executionCount).toBe(1);
    expect(queryMetrics!.averageExecutionTime).toBe(150);
    expect(queryMetrics!.totalItemsReturned).toBe(25);
  });

  test('calculates average execution time correctly', async () => {
    await monitor.trackQuery('avg-test', 100, 10);
    await monitor.trackQuery('avg-test', 200, 20);

    const metrics = monitor.getMetrics().get('avg-test');

    expect(metrics!.executionCount).toBe(2);
    expect(metrics!.averageExecutionTime).toBe(150);
    expect(metrics!.totalItemsReturned).toBe(30);
  });
});