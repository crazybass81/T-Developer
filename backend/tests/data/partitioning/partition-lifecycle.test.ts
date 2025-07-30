import { PartitionLifecycleManager, PartitionLifecycleConfig } from '../../../src/data/partitioning/partition-lifecycle';
import { TimeBasedPartitioner } from '../../../src/data/partitioning/time-based-partitioner';

describe('PartitionLifecycleManager', () => {
  const mockS3Client = {
    send: jest.fn()
  };
  
  const partitioner = new TimeBasedPartitioner();
  
  const config: PartitionLifecycleConfig = {
    retentionDays: 30,
    archiveToS3: true,
    compressionEnabled: true,
    autoCleanup: true
  };
  
  const lifecycleManager = new PartitionLifecycleManager(
    partitioner,
    mockS3Client as any,
    config
  );
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('initializes with default rules', () => {
    const stats = lifecycleManager.getLifecycleStatistics();
    
    expect(stats.totalRules).toBeGreaterThan(0);
  });
  
  test('adds custom lifecycle rule', () => {
    const initialStats = lifecycleManager.getLifecycleStatistics();
    
    lifecycleManager.addRule({
      name: 'test-rule',
      condition: (partition) => partition.size > 1000,
      action: 'compress',
      schedule: '0 0 * * *'
    });
    
    const finalStats = lifecycleManager.getLifecycleStatistics();
    
    expect(finalStats.totalRules).toBe(initialStats.totalRules + 1);
  });
  
  test('creates upcoming partitions', async () => {
    await lifecycleManager.createUpcomingPartitions('TestTable', 7);
    
    // Should complete without errors
    expect(true).toBe(true);
  });
  
  test('executes lifecycle rules', async () => {
    await lifecycleManager.executeLifecycleRules('TestTable');
    
    // Should complete without errors
    expect(true).toBe(true);
  });
  
  test('archives partition with compression', async () => {
    const partition = {
      id: 'test-partition',
      itemCount: 1000,
      size: 1024 * 1024,
      createdAt: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000) // 40 days ago
    };
    
    await lifecycleManager.archivePartition(partition);
    
    expect(mockS3Client.send).toHaveBeenCalled();
    expect((partition as any).status).toBe('archived');
    expect((partition as any).archivedAt).toBeDefined();
  });
  
  test('compresses data correctly', async () => {
    const originalData = Buffer.from('test data');
    
    const compressed = await lifecycleManager['compressData'](originalData);
    
    expect(compressed).toBeInstanceOf(Buffer);
    expect(compressed.length).toBeGreaterThan(0);
  });
  
  test('exports partition data', async () => {
    const partition = {
      id: 'test-partition',
      itemCount: 100
    };
    
    const data = await lifecycleManager['exportPartitionData'](partition);
    
    expect(data).toBeInstanceOf(Buffer);
    expect(data.length).toBeGreaterThan(0);
    
    const parsed = JSON.parse(data.toString());
    expect(parsed.partitionId).toBe('test-partition');
    expect(parsed.items).toHaveLength(100);
  });
  
  test('restores partition from snapshot', async () => {
    // First create a snapshot
    const partition = {
      id: 'restore-test-partition',
      itemCount: 50,
      size: 1024
    };
    
    // Mock S3 response
    mockS3Client.send.mockResolvedValue({
      Body: {
        async *[Symbol.asyncIterator]() {
          const data = JSON.stringify({
            partitionId: partition.id,
            items: Array.from({ length: 50 }, (_, i) => ({ id: i }))
          });
          yield Buffer.from(data);
        }
      }
    });
    
    // Create snapshot manually for test
    lifecycleManager['snapshots'].set(partition.id, {
      partitionId: partition.id,
      timestamp: new Date(),
      itemCount: partition.itemCount,
      size: partition.size,
      location: 's3://t-developer-archives/test-key.json',
      compressed: false
    });
    
    await lifecycleManager.restorePartition(partition.id);
    
    expect(mockS3Client.send).toHaveBeenCalled();
  });
});