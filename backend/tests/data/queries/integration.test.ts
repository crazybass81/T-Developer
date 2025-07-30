import { DynamoQueryBuilder, QueryExecutor } from '../../../src/data/queries/query-builder';
import { QueryOptimizer } from '../../../src/data/optimization/query-optimizer';
import { ProjectQueryService } from '../../../src/data/queries/project-query-service';

describe('Query System Integration', () => {
  const mockDocClient = {
    send: jest.fn()
  };

  const executor = new QueryExecutor(mockDocClient);
  const optimizer = new QueryOptimizer();
  const projectService = new ProjectQueryService(executor, optimizer, 'T-Developer-Main');

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('complete query flow with optimization', async () => {
    mockDocClient.send.mockResolvedValue({
      Items: [
        {
          ProjectId: 'proj123',
          ProjectName: 'Test Project',
          OwnerId: 'user123',
          Status: 'active',
          CreatedAt: '2024-01-01T00:00:00Z'
        }
      ],
      Count: 1
    });

    const projects = await projectService.getProjectsByUser('user123', 'active');

    expect(projects).toHaveLength(1);
    expect(projects[0].ProjectId).toBe('proj123');
    expect(mockDocClient.send).toHaveBeenCalledWith(
      expect.objectContaining({
        input: expect.objectContaining({
          TableName: 'T-Developer-Main',
          IndexName: 'GSI1'
        })
      })
    );
  });

  test('query builder with executor integration', async () => {
    mockDocClient.send.mockResolvedValue({
      Items: [{ AgentId: 'agent1', AgentType: 'nl-input' }],
      Count: 1
    });

    const query = new DynamoQueryBuilder('T-Developer-Main')
      .wherePartitionKey('PK', 'PROJECT#123')
      .andSortKey('SK', 'begins_with', 'AGENT#')
      .build();

    const result = await executor.query(query);

    expect(result.items).toHaveLength(1);
    expect((result.items[0] as any).AgentId).toBe('agent1');
  });

  test('optimizer improves query performance', async () => {
    const originalQuery = {
      TableName: 'T-Developer-Main',
      KeyConditionExpression: '#pk = :pk',
      ExpressionAttributeNames: { '#pk': 'PK' },
      ExpressionAttributeValues: { ':pk': 'USER#123' }
    };

    const optimized = await optimizer.optimizeQuery(originalQuery);

    expect(optimized.Limit).toBeDefined();
    expect(optimized.TableName).toBe(originalQuery.TableName);
  });
});