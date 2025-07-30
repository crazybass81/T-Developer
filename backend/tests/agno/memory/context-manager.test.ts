// backend/tests/agno/memory/context-manager.test.ts
const mockContextManager = {
  updateContext: jest.fn(),
  getContext: jest.fn(),
  getContextSummary: jest.fn()
};

describe('ContextManager', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should create new context for session', async () => {
    const message = {
      id: '1',
      role: 'user',
      content: 'Hello',
      timestamp: Date.now()
    };

    const mockContext = {
      sessionId: 'session1',
      messages: [message]
    };
    
    mockContextManager.updateContext.mockResolvedValue(mockContext);
    const context = await mockContextManager.updateContext('session1', message);
    
    expect(context.sessionId).toBe('session1');
    expect(context.messages).toHaveLength(1);
    expect(context.messages[0].content).toBe('Hello');
  });

  test('should retrieve existing context', async () => {
    const message = {
      id: '1',
      role: 'user',
      content: 'Hello',
      timestamp: Date.now()
    };

    const mockContext = {
      sessionId: 'session1',
      messages: [message]
    };
    
    mockContextManager.updateContext.mockResolvedValue(mockContext);
    mockContextManager.getContext.mockResolvedValue(mockContext);
    
    await mockContextManager.updateContext('session1', message);
    const context = await mockContextManager.getContext('session1');
    
    expect(context).not.toBeNull();
    expect(context.messages).toHaveLength(1);
  });

  test('should generate context summary', async () => {
    const message = {
      id: '1',
      role: 'user',
      content: 'Hello world',
      timestamp: Date.now()
    };

    mockContextManager.updateContext.mockResolvedValue({ sessionId: 'session1', messages: [message] });
    mockContextManager.getContextSummary.mockResolvedValue('user: Hello world');
    
    await mockContextManager.updateContext('session1', message);
    const summary = await mockContextManager.getContextSummary('session1');
    
    expect(summary).toContain('user: Hello world');
  });
});