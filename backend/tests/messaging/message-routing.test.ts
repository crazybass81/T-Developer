// Test 1.14.4: MessageRouter tests
import { MessageRouter, MessageFilter, AgentMessageRouter } from '../../src/messaging/message-routing';

describe('MessageRouter', () => {
  let router: MessageRouter;

  beforeEach(() => {
    router = new MessageRouter();
  });

  test('should route message based on rules', () => {
    router.addRule({
      condition: (msg) => msg.type === 'urgent',
      destination: 'urgent-queue',
      priority: 100
    });

    const destinations = router.route({ type: 'urgent', data: 'test' });
    
    expect(destinations).toEqual(['urgent-queue']);
  });

  test('should return default destination when no rules match', () => {
    const destinations = router.route({ type: 'unknown' });
    
    expect(destinations).toEqual(['default']);
  });

  test('should sort rules by priority', () => {
    router.addRule({
      condition: () => true,
      destination: 'low-priority',
      priority: 10
    });
    
    router.addRule({
      condition: () => true,
      destination: 'high-priority',
      priority: 100
    });

    const destinations = router.route({ type: 'test' });
    
    expect(destinations[0]).toBe('high-priority');
  });
});

describe('MessageFilter', () => {
  let filter: MessageFilter;

  beforeEach(() => {
    filter = new MessageFilter();
  });

  test('should pass message through all filters', () => {
    filter.addFilter('type-check', (msg) => msg.type === 'valid');
    filter.addFilter('data-check', (msg) => msg.data !== null);

    const result = filter.filter({ type: 'valid', data: 'test' });
    
    expect(result).toBe(true);
  });

  test('should reject message if any filter fails', () => {
    filter.addFilter('type-check', (msg) => msg.type === 'valid');
    filter.addFilter('data-check', (msg) => msg.data !== null);

    const result = filter.filter({ type: 'invalid', data: 'test' });
    
    expect(result).toBe(false);
  });
});

describe('AgentMessageRouter', () => {
  let router: AgentMessageRouter;

  beforeEach(() => {
    router = new AgentMessageRouter();
  });

  test('should route high priority agent tasks', () => {
    const destinations = router.route({
      type: 'agent-task',
      priority: 'high',
      data: 'urgent task'
    });
    
    expect(destinations).toContain('high-priority-queue');
  });

  test('should route regular agent tasks', () => {
    const destinations = router.route({
      type: 'agent-task',
      priority: 'normal',
      data: 'regular task'
    });
    
    expect(destinations).toContain('agent-tasks-queue');
  });

  test('should route error messages to error queue', () => {
    const destinations = router.route({
      type: 'agent-task',
      error: 'Something went wrong'
    });
    
    expect(destinations).toContain('error-queue');
  });
});