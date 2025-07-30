import { ShardManager, ShardConfig } from '../../../src/data/partitioning/shard-manager';

describe('ShardManager', () => {
  const config: ShardConfig = {
    shardCount: 4,
    hashFunction: 'murmur3',
    replicationFactor: 2,
    consistencyLevel: 'eventual'
  };
  
  const shardManager = new ShardManager(config);
  
  test('initializes shards correctly', () => {
    const stats = shardManager.getShardStatistics();
    
    expect(stats.totalShards).toBe(4);
    expect(stats.activeShards).toBe(4);
  });
  
  test('gets shard for key consistently', () => {
    const key1 = 'USER#123';
    const key2 = 'USER#456';
    
    const shard1a = shardManager.getShardForKey(key1);
    const shard1b = shardManager.getShardForKey(key1);
    const shard2 = shardManager.getShardForKey(key2);
    
    expect(shard1a.id).toBe(shard1b.id);
    expect(shard1a.id).toBeDefined();
    expect(shard2.id).toBeDefined();
  });
  
  test('hash functions produce different results', () => {
    const key = 'TEST_KEY';
    
    const murmur3Hash = shardManager['murmur3Hash'](key);
    const md5Hash = shardManager['md5Hash'](key);
    const sha256Hash = shardManager['sha256Hash'](key);
    
    expect(murmur3Hash).not.toBe(md5Hash);
    expect(md5Hash).not.toBe(sha256Hash);
    expect(murmur3Hash.length).toBe(8);
  });
  
  test('adds new shard successfully', async () => {
    const initialStats = shardManager.getShardStatistics();
    
    const newShard = await shardManager.addShard();
    
    const finalStats = shardManager.getShardStatistics();
    
    expect(newShard.id).toBeDefined();
    expect(finalStats.totalShards).toBe(initialStats.totalShards + 1);
  });
  
  test('calculates load balance correctly', () => {
    const stats = shardManager.getShardStatistics();
    
    expect(stats.loadBalance).toBeGreaterThanOrEqual(0);
    expect(stats.loadBalance).toBeLessThanOrEqual(1);
  });
  
  test('calculates midpoint correctly', () => {
    const start = '00000000';
    const end = 'ffffffff';
    
    const midpoint = shardManager['calculateMidpoint'](start, end);
    
    expect(midpoint).toBe('7fffffff');
  });
});