import { HotPartitionManager } from '../../../src/data/partitioning/hot-partition-manager';

describe('HotPartitionManager', () => {
  const mockCloudWatch = {
    send: jest.fn()
  };
  
  const mockDynamoDB = {
    send: jest.fn()
  };
  
  const manager = new HotPartitionManager(mockCloudWatch as any, mockDynamoDB as any);
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('starts and stops monitoring', () => {
    manager.startMonitoring('TestTable');
    expect(manager['monitoringInterval']).toBeDefined();
    
    manager.stopMonitoring();
    expect(manager['monitoringInterval']).toBeUndefined();
  });
  
  test('rebalances hot partition with split strategy', async () => {
    const hotPartition = {
      partitionKey: 'hot-partition-1',
      consumedRCU: 2000,
      consumedWCU: 1500,
      itemCount: 15000
    };
    
    const result = await manager.rebalanceHotPartition('TestTable', hotPartition);
    
    expect(result.strategy).toBe('SPLIT');
    expect(result.originalPartition).toBe('hot-partition-1');
    expect(result.newPartitions).toHaveLength(2);
    expect(result.success).toBe(true);
  });
  
  test('selects appropriate rebalancing strategy', () => {
    const highItemCount = { itemCount: 15000, consumedRCU: 500, consumedWCU: 300 };
    const highRCU = { itemCount: 5000, consumedRCU: 1500, consumedWCU: 300 };
    const highWCU = { itemCount: 5000, consumedRCU: 300, consumedWCU: 1500 };
    const moderate = { itemCount: 5000, consumedRCU: 300, consumedWCU: 300 };
    
    expect(manager['selectRebalancingStrategy'](highItemCount)).toBe('SPLIT');
    expect(manager['selectRebalancingStrategy'](highRCU)).toBe('CACHE');
    expect(manager['selectRebalancingStrategy'](highWCU)).toBe('REDISTRIBUTE');
    expect(manager['selectRebalancingStrategy'](moderate)).toBe('THROTTLE');
  });
  
  test('calculates priority correctly', () => {
    const partition = { consumedRCU: 1000, consumedWCU: 500 };
    
    const priority = manager['calculatePriority'](partition);
    
    expect(priority).toBe(1500);
  });
  
  test('distributes items evenly across partitions', () => {
    const items = Array.from({ length: 100 }, (_, i) => ({ id: i }));
    const partitions = ['partition-A', 'partition-B'];
    
    const distribution = manager['distributeItems'](items, partitions);
    
    expect(distribution).toHaveLength(2);
    expect(distribution[0].length + distribution[1].length).toBe(100);
    expect(Math.abs(distribution[0].length - distribution[1].length)).toBeLessThanOrEqual(1);
  });
});