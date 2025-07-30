// backend/tests/agno/agno-core.test.ts
import { AgnoPerformanceOptimizer } from '../../src/agno/performance-optimizer';
import { AgentPool } from '../../src/agno/agent-pool';
import { AgnoMonitoringIntegration } from '../../src/agno/monitoring-integration';

describe('Agno Core Components', () => {
  describe('AgnoPerformanceOptimizer', () => {
    let optimizer: AgnoPerformanceOptimizer;

    beforeEach(() => {
      optimizer = new AgnoPerformanceOptimizer();
    });

    test('should optimize successfully', async () => {
      await expect(optimizer.optimize()).resolves.not.toThrow();
    });

    test('should benchmark performance', async () => {
      const result = await optimizer.benchmarkPerformance();
      
      expect(result).toBeDefined();
      expect(result.instantiationTimeUs).toBeGreaterThan(0);
      expect(result.memoryPerAgentKb).toBeGreaterThan(0);
      expect(typeof result.targetMet).toBe('boolean');
    });

    test('should get pooled agent', () => {
      const agent = optimizer.getPooledAgent();
      expect(agent).toBeDefined();
      expect(agent.id).toBeDefined();
      expect(agent.execute).toBeDefined();
    });
  });

  describe('AgentPool', () => {
    let pool: AgentPool;

    beforeEach(() => {
      pool = new AgentPool({ minSize: 2, maxSize: 5, preWarm: false });
    });

    afterEach(() => {
      // Skip drain in tests to avoid timeout
    });

    test('should get agent from pool', async () => {
      const agent = await pool.getAgent();
      
      expect(agent).toBeDefined();
      expect(agent.id).toBeDefined();
      expect(agent.poolId).toBeDefined();
    });

    test('should release agent back to pool', async () => {
      const agent = await pool.getAgent();
      await expect(pool.releaseAgent(agent.poolId)).resolves.not.toThrow();
    });

    test('should provide pool stats', () => {
      const stats = pool.getStats();
      
      expect(stats).toBeDefined();
      expect(typeof stats.available).toBe('number');
      expect(typeof stats.inUse).toBe('number');
      expect(typeof stats.total).toBe('number');
    });
  });

  describe('AgnoMonitoringIntegration', () => {
    let monitoring: AgnoMonitoringIntegration;

    beforeEach(() => {
      monitoring = new AgnoMonitoringIntegration();
    });

    afterEach(() => {
      monitoring.stop();
    });

    test('should collect metrics', async () => {
      const metrics = await monitoring.collectMetrics();
      
      expect(metrics).toBeDefined();
      expect(metrics.instantiationTimeUs).toBeGreaterThan(0);
      expect(typeof metrics.memoryPerAgentKb).toBe('number');
    });

    test('should record execution', () => {
      expect(() => {
        monitoring.recordExecution(100, true);
        monitoring.recordExecution(200, false);
      }).not.toThrow();
    });

    test('should run performance benchmark', async () => {
      const result = await monitoring.runPerformanceBenchmark();
      
      expect(result).toBeDefined();
      expect(result.instantiationTime).toBeGreaterThan(0);
      expect(result.memoryUsage).toBeGreaterThan(0);
      expect(result.throughput).toBeGreaterThan(0);
      expect(typeof result.targetsMet).toBe('boolean');
    });
  });
});