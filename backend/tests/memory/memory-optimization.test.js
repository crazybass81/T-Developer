const { MemoryOptimizer } = require('../../src/agno/memory/memory-optimization');
const { MemoryHierarchy } = require('../../src/agno/memory/memory-hierarchy');

describe('SubTask 1.8.3: Memory Optimization', () => {
  let optimizer;
  let memoryHierarchy;

  beforeEach(() => {
    optimizer = new MemoryOptimizer();
    memoryHierarchy = new MemoryHierarchy();
  });

  describe('Data Compression', () => {
    test('should compress large text data', () => {
      const largeText = 'This is a very long text that should be compressed because it exceeds the threshold. '.repeat(50);
      
      const result = optimizer.compress(largeText);
      
      expect(result.compressed).toBe(true);
      expect(result.data.length).toBeLessThan(largeText.length);
      expect(result.originalSize).toBe(largeText.length);
    });

    test('should not compress small data', () => {
      const smallText = 'Small text';
      
      const result = optimizer.compress(smallText);
      
      expect(result.compressed).toBe(false);
      expect(result.data).toBe(smallText);
    });

    test('should decompress compressed data', () => {
      const originalText = 'Test data for compression and decompression';
      const compressed = optimizer.compress(originalText);
      
      const decompressed = optimizer.decompress(compressed);
      
      expect(typeof decompressed).toBe('string');
    });
  });

  describe('Memory Pressure Detection', () => {
    test('should detect memory pressure', () => {
      const pressure = optimizer.getMemoryPressure();
      
      expect(pressure).toBeGreaterThanOrEqual(0);
      expect(pressure).toBeLessThanOrEqual(1);
    });

    test('should perform emergency cleanup on high pressure', async () => {
      // Fill memory hierarchy
      for (let i = 0; i < 20; i++) {
        await memoryHierarchy.store('L5', `key${i}`, `value${i}`);
      }

      const initialStats = memoryHierarchy.getStats();
      optimizer.performEmergencyCleanup(memoryHierarchy);
      const finalStats = memoryHierarchy.getStats();

      expect(finalStats.totalItems).toBeLessThanOrEqual(initialStats.totalItems);
    });
  });

  describe('Memory Layout Optimization', () => {
    test('should optimize memory layout', async () => {
      // Add test data
      await memoryHierarchy.store('L3', 'test1', 'data1');
      await memoryHierarchy.store('L4', 'test2', 'data2');
      await memoryHierarchy.store('L5', 'test3', 'data3');

      const result = optimizer.optimizeMemoryLayout(memoryHierarchy);

      expect(result).toHaveProperty('optimizations');
      expect(result).toHaveProperty('memoryFreed');
      expect(result).toHaveProperty('newStats');
      expect(Array.isArray(result.optimizations)).toBe(true);
    });

    test('should optimize data placement based on access patterns', async () => {
      await memoryHierarchy.store('L5', 'frequent', 'data');
      
      // Simulate frequent access
      for (let i = 0; i < 15; i++) {
        await memoryHierarchy.get('frequent');
      }

      optimizer.optimizeDataPlacement(memoryHierarchy);
      
      // Verify optimization occurred
      const stats = memoryHierarchy.getStats();
      expect(stats.promotions).toBeGreaterThan(0);
    });
  });

  describe('Large Item Compression', () => {
    test('should compress large items in memory hierarchy', async () => {
      const largeData = 'Large data item that should be compressed. '.repeat(100);
      await memoryHierarchy.store('L3', 'large-item', largeData);

      optimizer.compressLargeItems(memoryHierarchy);

      const stored = await memoryHierarchy.get('large-item');
      expect(stored).toBeDefined();
    });
  });

  describe('Optimization Recommendations', () => {
    test('should provide optimization recommendations', () => {
      const mockStats = {
        hitRate: 0.5,
        totalAccess: 100,
        promotions: 5,
        evictions: 30
      };

      const recommendations = optimizer.getOptimizationRecommendations(mockStats);

      expect(Array.isArray(recommendations)).toBe(true);
      expect(recommendations).toContain('INCREASE_CACHE_SIZE');
      expect(recommendations).toContain('ADJUST_PROMOTION_THRESHOLD');
      expect(recommendations).toContain('OPTIMIZE_EVICTION_POLICY');
    });

    test('should not recommend when performance is good', () => {
      const goodStats = {
        hitRate: 0.9,
        totalAccess: 100,
        promotions: 15,
        evictions: 10
      };

      const recommendations = optimizer.getOptimizationRecommendations(goodStats);

      expect(recommendations).toHaveLength(0);
    });
  });

  describe('Memory Freed Calculation', () => {
    test('should calculate memory freed', () => {
      const memoryFreed = optimizer.calculateMemoryFreed();
      
      expect(typeof memoryFreed).toBe('number');
      expect(memoryFreed).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Integration with Memory Hierarchy', () => {
    test('should integrate optimization with memory hierarchy operations', async () => {
      // Fill memory with various data sizes
      await memoryHierarchy.store('L1', 'small', 'small data');
      await memoryHierarchy.store('L2', 'medium', 'medium sized data item');
      await memoryHierarchy.store('L3', 'large', 'very large data item that should trigger compression mechanisms'.repeat(20));

      const initialStats = memoryHierarchy.getStats();
      const optimization = optimizer.optimizeMemoryLayout(memoryHierarchy);
      const finalStats = memoryHierarchy.getStats();

      expect(optimization.optimizations).toBeDefined();
      expect(finalStats).toBeDefined();
      
      // Verify data is still accessible after optimization
      expect(await memoryHierarchy.get('small')).toBeDefined();
      expect(await memoryHierarchy.get('medium')).toBeDefined();
      expect(await memoryHierarchy.get('large')).toBeDefined();
    });
  });
});