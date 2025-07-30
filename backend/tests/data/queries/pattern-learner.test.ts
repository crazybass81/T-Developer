import { QueryPatternLearner } from '../../../src/data/ml/query-pattern-learner';

describe('QueryPatternLearner', () => {
  const learner = new QueryPatternLearner();

  test('learns from executed query', async () => {
    const query = {
      query: {
        TableName: 'TestTable',
        KeyConditionExpression: '#pk = :pk',
        ExpressionAttributeValues: { ':pk': 'USER#123' }
      },
      executionTime: 150,
      timestamp: new Date(),
      userId: 'user123'
    };

    await learner.learnFromQuery(query);

    // Pattern should be stored internally
    expect(learner['patterns'].size).toBe(1);
  });

  test('predicts next queries based on context', async () => {
    const context = {
      userId: 'user123',
      timestamp: new Date(),
      sessionId: 'session456'
    };

    const predictions = await learner.predictNextQueries(context);

    expect(predictions).toBeInstanceOf(Array);
    expect(predictions.length).toBeGreaterThan(0);
    expect(predictions[0]).toHaveProperty('probability');
    expect(predictions[0]).toHaveProperty('expectedResponseTime');
  });

  test('suggests adaptive indexing', async () => {
    // Add some patterns first
    for (let i = 0; i < 150; i++) {
      await learner.learnFromQuery({
        query: {
          TableName: 'TestTable',
          ExpressionAttributeValues: { ':pk': `USER#${i}` }
        },
        executionTime: 100 + i,
        timestamp: new Date()
      });
    }

    const suggestions = await learner.suggestAdaptiveIndexing();

    expect(suggestions).toBeInstanceOf(Array);
    if (suggestions.length > 0) {
      expect(suggestions[0]).toHaveProperty('pattern');
      expect(suggestions[0]).toHaveProperty('indexDefinition');
      expect(suggestions[0]).toHaveProperty('priority');
    }
  });

  test('extracts entity type from query', () => {
    const query = {
      query: {
        ExpressionAttributeValues: { ':pk': 'PROJECT#456' }
      },
      executionTime: 100,
      timestamp: new Date()
    };

    const pattern = learner['extractPattern'](query);

    expect(pattern.entityType).toBe('PROJECT');
  });
});