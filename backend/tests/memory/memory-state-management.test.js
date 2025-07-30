const { MemoryHierarchy } = require('../../src/agno/memory/memory-hierarchy');
const { ContextManager } = require('../../src/agno/memory/context-manager');
const { StateManager } = require('../../src/memory/state-manager');
const { PersistenceLayer } = require('../../src/memory/persistence-layer');

describe('Task 1.8: Memory and State Management System', () => {
  describe('Memory Hierarchy Integration', () => {
    let memoryHierarchy;

    beforeEach(() => {
      memoryHierarchy = new MemoryHierarchy();
    });

    test('should handle cross-level memory operations', async () => {
      await memoryHierarchy.store('L1', 'key1', 'value1');
      await memoryHierarchy.store('L3', 'key2', 'value2');
      await memoryHierarchy.store('L5', 'key3', 'value3');

      expect(await memoryHierarchy.get('key1')).toBe('value1');
      expect(await memoryHierarchy.get('key2')).toBe('value2');
      expect(await memoryHierarchy.get('key3')).toBe('value3');
    });

    test('should promote frequently accessed items', async () => {
      await memoryHierarchy.store('L5', 'frequent', 'data');
      
      for (let i = 0; i < 5; i++) {
        await memoryHierarchy.get('frequent');
      }

      const stats = memoryHierarchy.getStats();
      expect(stats.promotions).toBeGreaterThan(0);
    });
  });

  describe('Context Manager Integration', () => {
    let contextManager;

    beforeEach(() => {
      contextManager = new ContextManager();
    });

    test('should manage conversation context', async () => {
      const sessionId = 'session1';
      
      await contextManager.addMessage(sessionId, {
        role: 'user',
        content: 'Hello, I need help with coding'
      });

      await contextManager.addMessage(sessionId, {
        role: 'assistant',
        content: 'I can help you with coding tasks'
      });

      const context = await contextManager.getContext(sessionId);
      expect(context.messages).toHaveLength(2);
      expect(context.tokenCount).toBeGreaterThan(0);
    });

    test('should handle context trimming', async () => {
      const sessionId = 'session2';
      
      for (let i = 0; i < 20; i++) {
        await contextManager.addMessage(sessionId, {
          role: i % 2 === 0 ? 'user' : 'assistant',
          content: `Message ${i}`
        });
      }

      const context = await contextManager.getContext(sessionId);
      expect(context.messages.length).toBeLessThan(20);
    });
  });

  describe('State Manager', () => {
    let stateManager;

    beforeEach(() => {
      stateManager = new StateManager();
    });

    test('should save and retrieve agent state', () => {
      const agentId = 'agent1';
      const state = { status: 'active', data: { count: 5 } };

      const snapshotId = stateManager.saveState(agentId, state);
      expect(snapshotId).toBeDefined();

      const retrieved = stateManager.getState(agentId);
      expect(retrieved).toEqual(state);
    });

    test('should maintain state history', () => {
      const agentId = 'agent2';
      
      stateManager.saveState(agentId, { version: 1 });
      stateManager.saveState(agentId, { version: 2 });
      stateManager.saveState(agentId, { version: 3 });

      const history = stateManager.getStateHistory(agentId);
      expect(history).toHaveLength(3);
      expect(history[2].state.version).toBe(3);
    });

    test('should restore previous state versions', () => {
      const agentId = 'agent3';
      
      stateManager.saveState(agentId, { data: 'v1' });
      stateManager.saveState(agentId, { data: 'v2' });
      stateManager.saveState(agentId, { data: 'v3' });

      const restored = stateManager.restoreState(agentId, 1);
      expect(restored).toBe(true);

      const current = stateManager.getState(agentId);
      expect(current.data).toBe('v1');
    });
  });

  describe('Persistence Layer', () => {
    let persistence;

    beforeEach(() => {
      persistence = new PersistenceLayer({
        batchSize: 5,
        flushInterval: 100
      });
    });

    test('should save and load data', async () => {
      const key = 'test-key';
      const data = { message: 'test data' };

      await persistence.save(key, data, { immediate: true });
      const loaded = await persistence.load(key);

      expect(loaded).toEqual(data);
    });

    test('should handle TTL expiration', async () => {
      const key = 'ttl-key';
      const data = { temp: true };

      await persistence.save(key, data, { ttl: 50, immediate: true });
      
      await new Promise(resolve => setTimeout(resolve, 60));
      
      const loaded = await persistence.load(key);
      expect(loaded).toBeNull();
    });
  });

  describe('Integration Tests', () => {
    test('should integrate memory hierarchy with context management', async () => {
      const memoryHierarchy = new MemoryHierarchy();
      const contextManager = new ContextManager();
      const sessionId = 'integration-session';
      
      await contextManager.addMessage(sessionId, {
        role: 'user',
        content: 'Complex integration test'
      });

      const context = await contextManager.getContext(sessionId);
      await memoryHierarchy.store('L2', `context:${sessionId}`, context);

      const stored = await memoryHierarchy.get(`context:${sessionId}`);
      expect(stored.messages).toHaveLength(1);
      expect(stored.messages[0].content).toBe('Complex integration test');
    });

    test('should persist agent state across memory levels', async () => {
      const stateManager = new StateManager();
      const memoryHierarchy = new MemoryHierarchy();
      const persistence = new PersistenceLayer();
      
      const agentId = 'persistent-agent';
      const state = { 
        level: 'L3',
        data: { processed: 100, errors: 0 }
      };

      const snapshotId = stateManager.saveState(agentId, state);
      await memoryHierarchy.store('L3', `state:${agentId}`, state);
      await persistence.save(`agent:${agentId}`, { snapshotId, state }, { immediate: true });

      expect(stateManager.getState(agentId)).toEqual(state);
      expect(await memoryHierarchy.get(`state:${agentId}`)).toEqual(state);
      
      const persisted = await persistence.load(`agent:${agentId}`);
      expect(persisted.state).toEqual(state);
    });
  });
});