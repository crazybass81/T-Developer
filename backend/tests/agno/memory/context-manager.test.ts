// backend/tests/agno/memory/context-manager.test.ts
import { ContextManager, Message } from '../../../src/agno/memory/context-manager';

describe('ContextManager', () => {
  let contextManager: ContextManager;

  beforeEach(() => {
    contextManager = new ContextManager();
  });

  test('should create new context for session', async () => {
    const message: Message = {
      id: '1',
      role: 'user',
      content: 'Hello',
      timestamp: Date.now()
    };

    const context = await contextManager.updateContext('session1', message);
    
    expect(context.sessionId).toBe('session1');
    expect(context.messages).toHaveLength(1);
    expect(context.messages[0].content).toBe('Hello');
  });

  test('should retrieve existing context', async () => {
    const message: Message = {
      id: '1',
      role: 'user',
      content: 'Hello',
      timestamp: Date.now()
    };

    await contextManager.updateContext('session1', message);
    const context = await contextManager.getContext('session1');
    
    expect(context).not.toBeNull();
    expect(context!.messages).toHaveLength(1);
  });

  test('should return null for non-existent context', async () => {
    const context = await contextManager.getContext('nonexistent');
    expect(context).toBeNull();
  });

  test('should generate context summary', async () => {
    const message: Message = {
      id: '1',
      role: 'user',
      content: 'Hello world',
      timestamp: Date.now()
    };

    await contextManager.updateContext('session1', message);
    const summary = await contextManager.getContextSummary('session1');
    
    expect(summary).toContain('user: Hello world');
  });
});