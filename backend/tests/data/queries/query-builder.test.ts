import { DynamoQueryBuilder, QueryExecutor } from '../../../src/data/queries/query-builder';

describe('DynamoQueryBuilder', () => {
  test('builds basic query', () => {
    const query = new DynamoQueryBuilder('TestTable')
      .wherePartitionKey('PK', 'USER#123')
      .build();

    expect(query.TableName).toBe('TestTable');
    expect(query.KeyConditionExpression).toBe('#pk = :pk');
    expect(query.ExpressionAttributeNames!['#pk']).toBe('PK');
    expect(query.ExpressionAttributeValues![':pk']).toBe('USER#123');
  });

  test('builds query with sort key', () => {
    const query = new DynamoQueryBuilder('TestTable')
      .wherePartitionKey('PK', 'PROJECT#456')
      .andSortKey('SK', 'begins_with', 'AGENT#')
      .build();

    expect(query.KeyConditionExpression).toBe('#pk = :pk AND begins_with(#sk, :sk)');
    expect(query.ExpressionAttributeValues![':sk']).toBe('AGENT#');
  });

  test('builds query with filter and index', () => {
    const query = new DynamoQueryBuilder('TestTable')
      .useIndex('GSI1')
      .wherePartitionKey('GSI1PK', 'USER#789')
      .filter('#status = :status', { ':status': 'active' })
      .limit(50)
      .build();

    expect(query.IndexName).toBe('GSI1');
    expect(query.FilterExpression).toBe('#status = :status');
    expect(query.Limit).toBe(50);
  });
});

describe('QueryExecutor', () => {
  const mockDocClient = {
    send: jest.fn()
  };

  const executor = new QueryExecutor(mockDocClient);

  test('executes query and returns formatted result', async () => {
    mockDocClient.send.mockResolvedValue({
      Items: [{ id: '1', name: 'test' }],
      Count: 1,
      ScannedCount: 1
    });

    const result = await executor.query({ TableName: 'Test' });

    expect(result.items).toHaveLength(1);
    expect(result.count).toBe(1);
    expect(result.items[0]).toEqual({ id: '1', name: 'test' });
  });

  test('handles pagination in queryAll', async () => {
    mockDocClient.send
      .mockResolvedValueOnce({
        Items: [{ id: '1' }],
        LastEvaluatedKey: { PK: 'key1' }
      })
      .mockResolvedValueOnce({
        Items: [{ id: '2' }]
      });

    const result = await executor.queryAll({ TableName: 'Test' });

    expect(result).toHaveLength(2);
    expect(mockDocClient.send).toHaveBeenCalledTimes(3);
  });
});