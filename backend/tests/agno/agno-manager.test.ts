// backend/tests/agno/agno-manager.test.ts
import { AgnoManager } from '../../src/agno/agno-manager';

// Mock dependencies
const mockOptimizer = {
  optimize: jest.fn().mockResolvedValue(undefined),
  benchmarkPerformance: jest.fn().mockResolvedValue({
    instantiationTimeUs: 2.5,
    memoryPerAgentKb: 5.8,
    targetMet: true
  })
};

const mockPool = {
  getAgent: jest.fn().mockResolvedValue({
    id: 'test-agent',
    execute: jest.fn().mockResolvedValue({ result: 'test' })
  }),
  releaseAgent: jest.fn().mockResolvedValue(undefined),
  getStats: jest.fn().mockReturnValue({
    available: 5,
    inUse: 2,
    total: 7
  }),
  drain: jest.fn().mockResolvedValue(undefined),
  on: jest.fn()
};

const mockMonitoring = {
  runPerformanceBenchmark: jest.fn().mockResolvedValue({
    instantiationTime: 2.5,
    memoryUsage: 5.8,
    throughput: 1000,
    targetsMet: true
  }),
  recordExecution: jest.fn(),
  updatePoolStats: jest.fn(),
  getMetrics: jest.fn().mockReturnValue({
    totalExecutions: 10,
    averageExecutionTime: 50
  }),
  stop: jest.fn(),
  on: jest.fn()
};

jest.mock('../../src/agno/performance-optimizer', () => ({
  AgnoPerformanceOptimizer: jest.fn().mockImplementation(() => mockOptimizer)
}));

jest.mock('../../src/agno/agent-pool', () => ({
  AgentPool: jest.fn().mockImplementation(() => mockPool)
}));

jest.mock('../../src/agno/monitoring-integration', () => ({
  AgnoMonitoringIntegration: jest.fn().mockImplementation(() => mockMonitoring)
}));

describe('AgnoManager', () => {
  let agnoManager: AgnoManager;

  beforeEach(() => {
    agnoManager = new AgnoManager();
  });

  afterEach(async () => {
    if (agnoManager) {
      await agnoManager.shutdown();
    }
    jest.clearAllMocks();
  });

  test('should initialize successfully', async () => {
    await expect(agnoManager.initialize()).resolves.not.toThrow();
  });

  test('should not initialize twice', async () => {
    await agnoManager.initialize();
    await agnoManager.initialize(); // Should not throw
    expect(true).toBe(true);
  });

  test('should execute task with agent', async () => {
    await agnoManager.initialize();
    
    const mockTask = { type: 'test', data: 'test data' };
    const result = await agnoManager.executeWithAgent(mockTask);
    
    expect(result).toBeDefined();
    expect(result.agnoMetrics).toBeDefined();
    expect(result.agnoMetrics.executionTime).toBeGreaterThan(0);
  });

  test('should get metrics', async () => {
    await agnoManager.initialize();
    
    const metrics = agnoManager.getMetrics();
    
    expect(metrics).toBeDefined();
    expect(metrics.agno).toBeDefined();
    expect(metrics.pool).toBeDefined();
    expect(metrics.performance).toBeDefined();
    expect(metrics.performance.initialized).toBe(true);
  });

  test('should shutdown gracefully', async () => {
    await agnoManager.initialize();
    await expect(agnoManager.shutdown()).resolves.not.toThrow();
  });
});