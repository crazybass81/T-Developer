import { TestDataGenerator, waitFor, MockTimer, mockEnvironment } from '../helpers/test-utils';

describe('TestDataGenerator', () => {
  test('should generate project data', () => {
    const project = TestDataGenerator.project();
    
    expect(project).toHaveProperty('id');
    expect(project).toHaveProperty('userId', 'user_test_123');
    expect(project).toHaveProperty('name', 'Test Project');
    expect(project).toHaveProperty('status', 'analyzing');
    expect(project.id).toMatch(/^proj_\d+_[a-z0-9]+$/);
  });

  test('should generate agent execution data', () => {
    const execution = TestDataGenerator.agentExecution();
    
    expect(execution).toHaveProperty('id');
    expect(execution).toHaveProperty('agentName', 'TestAgent');
    expect(execution).toHaveProperty('status', 'completed');
    expect(execution.id).toMatch(/^exec_\d+_[a-z0-9]+$/);
  });

  test('should apply overrides', () => {
    const project = TestDataGenerator.project({ name: 'Custom Project' });
    expect(project.name).toBe('Custom Project');
  });
});

describe('waitFor', () => {
  test('should resolve when condition is met', async () => {
    let counter = 0;
    const condition = () => ++counter >= 3;
    
    await expect(waitFor(condition, 1000, 50)).resolves.toBeUndefined();
  });

  test('should timeout when condition is not met', async () => {
    const condition = () => false;
    
    await expect(waitFor(condition, 100, 10)).rejects.toThrow('Timeout waiting for condition');
  });
});

describe('MockTimer', () => {
  test('should track and clear timers', () => {
    const timer = new MockTimer();
    const fn = jest.fn();
    
    timer.setTimeout(fn, 100);
    timer.clearAll();
    
    // 타이머가 정리되었는지 확인하기 위해 잠시 대기
    setTimeout(() => {
      expect(fn).not.toHaveBeenCalled();
    }, 150);
  });
});

describe('mockEnvironment', () => {
  test('should mock and restore environment variables', () => {
    const originalValue = process.env.TEST_VAR;
    
    const restore = mockEnvironment({ TEST_VAR: 'test_value' });
    expect(process.env.TEST_VAR).toBe('test_value');
    
    restore();
    expect(process.env.TEST_VAR).toBe(originalValue);
  });
});