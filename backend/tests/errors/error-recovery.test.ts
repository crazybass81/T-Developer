import { ErrorRecoveryManager, RetryStrategy } from '../../src/errors/error-recovery';

describe('ErrorRecoveryManager', () => {
  let recoveryManager: ErrorRecoveryManager;

  beforeEach(() => {
    recoveryManager = new ErrorRecoveryManager();
  });

  test('attempts recovery with retry strategy', async () => {
    const error = new Error('TimeoutError');
    error.name = 'TimeoutError';
    
    const mockOperation = jest.fn().mockResolvedValue('success');

    const result = await recoveryManager.attemptRecovery(error, {
      operation: mockOperation,
      attempt: 0
    });

    expect(result).toBe('success');
  });

  test('fails after max retries', async () => {
    const error = new Error('TimeoutError');
    error.name = 'TimeoutError';
    
    const mockOperation = jest.fn().mockRejectedValue(error);

    await expect(
      recoveryManager.attemptRecovery(error, {
        operation: mockOperation,
        attempt: 3
      })
    ).rejects.toThrow('TimeoutError');
  });
});