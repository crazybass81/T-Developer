import { ErrorSystem } from '../../src/errors';

describe('ErrorSystem Integration', () => {
  let errorSystem: ErrorSystem;

  beforeEach(() => {
    errorSystem = new ErrorSystem();
  });

  test('tracks errors and generates metrics', () => {
    const error = new Error('Test error');
    const context = { endpoint: '/api/test', userId: 'user123' };

    errorSystem.trackError(error, context);

    const metrics = errorSystem.tracker.getMetrics();
    expect(metrics.errorCount).toBe(1);
    expect(metrics.errorsByType['Error']).toBe(1);
  });

  test('analyzes error patterns', () => {
    // Generate multiple errors
    for (let i = 0; i < 60; i++) {
      errorSystem.trackError(new Error('Recurring error'), { endpoint: '/api/test' });
    }

    const patterns = errorSystem.analyzer.analyzePatterns();
    expect(patterns).toHaveLength(1);
    expect(patterns[0].type).toBe('recurring');
  });

  test('attempts error recovery', async () => {
    const error = new Error('TimeoutError');
    error.name = 'TimeoutError';
    
    const mockOperation = jest.fn().mockResolvedValue('recovered');

    const result = await errorSystem.attemptRecovery(error, {
      operation: mockOperation,
      attempt: 0
    });

    expect(result).toBe('recovered');
  });
});