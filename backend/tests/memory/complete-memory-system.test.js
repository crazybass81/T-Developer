const { MemoryHierarchy } = require('../../src/agno/memory/memory-hierarchy');
const { ContextManager } = require('../../src/agno/memory/context-manager');
const { StateManager } = require('../../src/memory/state-manager');
const { PersistenceLayer } = require('../../src/memory/persistence-layer');
const { MemoryOptimizer } = require('../../src/agno/memory/memory-optimization');
const { MemoryAnalytics } = require('../../src/agno/memory/memory-analytics');

describe('Task 1.8: Complete Memory and State Management System', () => {
  let memoryHierarchy, contextManager, stateManager, persistence, optimizer, analytics;

  beforeEach(() => {
    memoryHierarchy = new MemoryHierarchy();
    contextManager = new ContextManager();
    stateManager = new StateManager();
    persistence = new PersistenceLayer();
    optimizer = new MemoryOptimizer();
    analytics = new MemoryAnalytics();
  });

  describe('SubTask 1.8.1: Memory Hierarchy', () => {
    test('should manage 5-level memory hierarchy', async () => {
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

  describe('SubTask 1.8.2: Context Management', () => {
    test('should manage conversation context', async () => {
      const sessionId = 'session1';
      
      await contextManager.addMessage(sessionId, {
        role: 'user',
        content: 'Hello'
      });

      const context = await contextManager.getContext(sessionId);
      expect(context.messages).toHaveLength(1);
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

  describe('SubTask 1.8.3: Memory Optimization', () => {
    test('should compress large data', () => {
      const largeText = 'Large text data '.repeat(100);
      const result = optimizer.compress(largeText);
      
      expect(result.compressed).toBe(true);
      expect(result.data.length).toBeLessThan(largeText.length);
    });

    test('should optimize memory layout', async () => {
      await memoryHierarchy.store('L3', 'test1', 'data1');
      await memoryHierarchy.store('L4', 'test2', 'data2');

      const result = optimizer.optimizeMemoryLayout(memoryHierarchy);

      expect(result).toHaveProperty('optimizations');
      expect(result).toHaveProperty('memoryFreed');
      expect(result).toHaveProperty('newStats');
    });
  });

  describe('SubTask 1.8.4: Memory Analytics', () => {
    test('should record and analyze access patterns', () => {
      analytics.recordAccess('key1', 'L1', 'hit', 10);
      analytics.recordAccess('key1', 'L1', 'hit', 15);
      analytics.recordAccess('key2', 'L3', 'miss', 50);

      const report = analytics.generateReport();
      
      expect(report.summary.totalAccesses).toBe(3);
      expect(report.summary.hitRate).toBeCloseTo(0.67, 1);
      expect(report.topKeys).toHaveLength(2);
    });

    test('should generate alerts for performance issues', () => {
      analytics.recordAccess('slow-key', 'L5', 'hit', 150); // High latency
      
      expect(analytics.alerts).toHaveLength(1);
      expect(analytics.alerts[0].type).toBe('HIGH_LATENCY');
    });
  });

  describe('State Management Integration', () => {
    test('should manage agent state with versioning', () => {
      const agentId = 'agent1';
      const state1 = { version: 1, data: 'first' };
      const state2 = { version: 2, data: 'second' };

      stateManager.saveState(agentId, state1);
      stateManager.saveState(agentId, state2);

      expect(stateManager.getState(agentId)).toEqual(state2);
      
      const history = stateManager.getStateHistory(agentId);
      expect(history).toHaveLength(2);
    });

    test('should restore previous state versions', () => {
      const agentId = 'agent2';
      
      stateManager.saveState(agentId, { data: 'v1' });
      stateManager.saveState(agentId, { data: 'v2' });
      stateManager.saveState(agentId, { data: 'v3' });

      const restored = stateManager.restoreState(agentId, 1);
      expect(restored).toBe(true);

      const current = stateManager.getState(agentId);
      expect(current.data).toBe('v1');
    });
  });

  describe('Persistence Layer Integration', () => {
    test('should persist data with TTL', async () => {
      await persistence.save('ttl-key', { data: 'temp' }, { ttl: 50, immediate: true });
      
      let loaded = await persistence.load('ttl-key');
      expect(loaded.data).toBe('temp');
      
      await new Promise(resolve => setTimeout(resolve, 60));
      
      loaded = await persistence.load('ttl-key');
      expect(loaded).toBeNull();
    });

    test('should handle batch operations', async () => {
      const keys = ['batch1', 'batch2', 'batch3'];
      
      for (const key of keys) {
        await persistence.save(key, { data: key });
      }

      await persistence.flush();

      for (const key of keys) {
        const loaded = await persistence.load(key);
        expect(loaded.data).toBe(key);
      }
    });
  });

  describe('Complete System Integration', () => {
    test('should integrate all memory components', async () => {
      const sessionId = 'integration-test';
      const agentId = 'test-agent';
      
      // Add conversation context
      await contextManager.addMessage(sessionId, {
        role: 'user',
        content: 'Integration test message'
      });

      // Store context in memory hierarchy
      const context = await contextManager.getContext(sessionId);
      await memoryHierarchy.store('L2', `context:${sessionId}`, context);

      // Save agent state
      const state = { sessionId, status: 'active', context };
      const snapshotId = stateManager.saveState(agentId, state);

      // Persist to storage
      await persistence.save(`agent:${agentId}`, { snapshotId, state }, { immediate: true });

      // Record analytics
      analytics.recordAccess(`context:${sessionId}`, 'L2', 'hit', 25);

      // Optimize memory
      const optimization = optimizer.optimizeMemoryLayout(memoryHierarchy);

      // Verify all components work together
      expect(await memoryHierarchy.get(`context:${sessionId}`)).toBeDefined();
      expect(stateManager.getState(agentId)).toEqual(state);
      expect(await persistence.load(`agent:${agentId}`)).toBeDefined();
      expect(optimization.optimizations).toBeDefined();
      
      const report = analytics.generateReport();
      expect(report.summary.totalAccesses).toBe(1);
    });

    test('should handle memory pressure scenarios', async () => {
      // Fill memory with test data
      for (let i = 0; i < 50; i++) {
        await memoryHierarchy.store('L1', `key${i}`, `value${i}`);
        stateManager.saveState(`agent${i}`, { id: i });
        analytics.recordAccess(`key${i}`, 'L1', 'hit', Math.random() * 100);
      }

      // Trigger optimization
      const optimization = optimizer.optimizeMemoryLayout(memoryHierarchy);
      
      // Generate analytics report
      const report = analytics.generateReport();

      // Verify system handles pressure
      expect(optimization.optimizations).toBeDefined();
      expect(report.summary.totalAccesses).toBe(50);
      expect(report.recommendations).toBeDefined();
      
      const memStats = memoryHierarchy.getStats();
      const stateStats = stateManager.getStats();
      
      expect(memStats.totalItems).toBeGreaterThan(0);
      expect(stateStats.activeStates).toBe(50);
    });

    test('should maintain performance under load', async () => {
      const startTime = Date.now();
      
      // Simulate high load
      const operations = [];
      for (let i = 0; i < 100; i++) {
        operations.push(
          memoryHierarchy.store('L3', `load-key-${i}`, `load-value-${i}`)
        );
      }
      
      await Promise.all(operations);
      
      const duration = Date.now() - startTime;
      
      // Verify performance (should complete within reasonable time)
      expect(duration).toBeLessThan(1000); // 1 second
      
      const stats = memoryHierarchy.getStats();
      expect(stats.totalItems).toBe(100);
    });
  });
});