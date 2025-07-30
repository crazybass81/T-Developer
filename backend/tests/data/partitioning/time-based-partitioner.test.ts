import { TimeBasedPartitioner, PartitionMetrics } from '../../../src/data/partitioning/time-based-partitioner';

describe('TimeBasedPartitioner', () => {
  test('generates partition key with monthly strategy', () => {
    const partitioner = new TimeBasedPartitioner('monthly');
    const date = new Date('2024-03-15');
    
    const key = partitioner.generatePartitionKey('USER', date);
    
    expect(key).toBe('USER#2024-03');
  });
  
  test('generates partition key with daily strategy', () => {
    const partitioner = new TimeBasedPartitioner('daily');
    const date = new Date('2024-03-15');
    
    const key = partitioner.generatePartitionKey('PROJECT', date);
    
    expect(key).toBe('PROJECT#2024-03-15');
  });
  
  test('gets partitions for date range', () => {
    const partitioner = new TimeBasedPartitioner('monthly');
    const start = new Date('2024-01-15');
    const end = new Date('2024-03-15');
    
    const partitions = partitioner.getPartitionsForRange(start, end);
    
    expect(partitions).toEqual(['2024-01', '2024-02', '2024-03']);
  });
  
  test('detects hot partitions', async () => {
    const partitioner = new TimeBasedPartitioner();
    const metrics: PartitionMetrics[] = [
      { partitionKey: 'partition-1', consumedRCU: 100, consumedWCU: 50, itemCount: 1000 },
      { partitionKey: 'partition-2', consumedRCU: 2000, consumedWCU: 1500, itemCount: 5000 },
      { partitionKey: 'partition-3', consumedRCU: 150, consumedWCU: 75, itemCount: 1200 }
    ];
    
    const hotPartitions = await partitioner.detectHotPartitions('TestTable', metrics);
    
    expect(hotPartitions).toHaveLength(1);
    expect(hotPartitions[0].partitionKey).toBe('partition-2');
    expect(hotPartitions[0].recommendation).toContain('splitting');
  });
  
  test('archives old partitions', async () => {
    const partitioner = new TimeBasedPartitioner();
    
    const result = await partitioner.archiveOldPartitions('TestTable', 30);
    
    expect(result.totalPartitions).toBeGreaterThanOrEqual(0);
    expect(result.archived).toBeDefined();
    expect(result.failed).toBeDefined();
    expect(result.bytesArchived).toBeGreaterThanOrEqual(0);
  });
});