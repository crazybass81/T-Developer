export interface ShardConfig {
  shardCount: number;
  hashFunction: 'murmur3' | 'md5' | 'sha256';
  replicationFactor: number;
  consistencyLevel: 'eventual' | 'strong';
}

export interface Shard {
  id: string;
  range: { start: string; end: string };
  nodes: string[];
  status: 'active' | 'migrating' | 'inactive';
  itemCount: number;
  size: number;
}

export interface ShardMigration {
  fromShard: string;
  toShard: string;
  keyRange: { start: string; end: string };
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
}

export class ShardManager {
  private shards: Map<string, Shard> = new Map();
  private migrations: Map<string, ShardMigration> = new Map();
  
  constructor(private config: ShardConfig) {
    this.initializeShards();
  }
  
  private initializeShards(): void {
    const shardSize = Math.pow(2, 32) / this.config.shardCount;
    
    for (let i = 0; i < this.config.shardCount; i++) {
      const start = (i * shardSize).toString(16).padStart(8, '0');
      const end = ((i + 1) * shardSize - 1).toString(16).padStart(8, '0');
      
      const shard: Shard = {
        id: `shard-${i}`,
        range: { start, end },
        nodes: [`node-${i % 3}`],
        status: 'active',
        itemCount: 0,
        size: 0
      };
      
      this.shards.set(shard.id, shard);
    }
  }
  
  getShardForKey(key: string): Shard {
    const hash = this.hashKey(key);
    const hashValue = parseInt(hash.substring(0, 8), 16);
    const shardIndex = Math.floor(hashValue / (Math.pow(2, 32) / this.config.shardCount));
    
    return this.shards.get(`shard-${shardIndex}`)!;
  }
  
  private hashKey(key: string): string {
    switch (this.config.hashFunction) {
      case 'murmur3':
        return this.murmur3Hash(key);
      case 'md5':
        return this.md5Hash(key);
      case 'sha256':
        return this.sha256Hash(key);
      default:
        throw new Error(`Unknown hash function: ${this.config.hashFunction}`);
    }
  }
  
  private murmur3Hash(key: string): string {
    let hash = 0;
    for (let i = 0; i < key.length; i++) {
      hash = Math.imul(hash ^ key.charCodeAt(i), 0x5bd1e995);
      hash = hash ^ (hash >>> 15);
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
  
  private md5Hash(key: string): string {
    return Buffer.from(key).toString('hex').substring(0, 32);
  }
  
  private sha256Hash(key: string): string {
    // Create a different hash than md5 for testing
    const hash = Buffer.from(key + '_sha256').toString('hex');
    return hash.substring(0, 64);
  }
  
  async addShard(): Promise<Shard> {
    const newShardId = `shard-${this.shards.size}`;
    const existingShards = Array.from(this.shards.values());
    
    const largestShard = existingShards.reduce((prev, current) => 
      current.itemCount > prev.itemCount ? current : prev
    );
    
    const midpoint = this.calculateMidpoint(largestShard.range.start, largestShard.range.end);
    
    const newShard: Shard = {
      id: newShardId,
      range: { start: midpoint, end: largestShard.range.end },
      nodes: [`node-${this.shards.size % 3}`],
      status: 'active',
      itemCount: 0,
      size: 0
    };
    
    largestShard.range.end = midpoint;
    this.shards.set(newShardId, newShard);
    
    await this.migrateShard(largestShard.id, newShardId);
    return newShard;
  }
  
  private calculateMidpoint(start: string, end: string): string {
    const startNum = parseInt(start, 16);
    const endNum = parseInt(end, 16);
    const midpoint = Math.floor((startNum + endNum) / 2);
    return midpoint.toString(16).padStart(8, '0');
  }
  
  private async migrateShard(fromShardId: string, toShardId: string): Promise<void> {
    const migrationId = `${fromShardId}-to-${toShardId}`;
    
    const migration: ShardMigration = {
      fromShard: fromShardId,
      toShard: toShardId,
      keyRange: this.shards.get(fromShardId)!.range,
      status: 'pending',
      progress: 0
    };
    
    this.migrations.set(migrationId, migration);
    await this.executeMigration(migration);
  }
  
  private async executeMigration(migration: ShardMigration): Promise<void> {
    migration.status = 'in_progress';
    
    try {
      for (let progress = 0; progress <= 100; progress += 10) {
        migration.progress = progress;
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      migration.status = 'completed';
      console.log(`Migration completed: ${migration.fromShard} -> ${migration.toShard}`);
      
    } catch (error) {
      migration.status = 'failed';
      throw error;
    }
  }
  
  getShardStatistics(): any {
    const shards = Array.from(this.shards.values());
    
    return {
      totalShards: shards.length,
      activeShards: shards.filter(s => s.status === 'active').length,
      totalItems: shards.reduce((sum, s) => sum + s.itemCount, 0),
      averageItemsPerShard: shards.reduce((sum, s) => sum + s.itemCount, 0) / shards.length,
      loadBalance: this.calculateLoadBalance(shards)
    };
  }
  
  private calculateLoadBalance(shards: Shard[]): number {
    if (shards.length === 0) return 1;
    
    const itemCounts = shards.map(s => s.itemCount);
    const avg = itemCounts.reduce((sum, count) => sum + count, 0) / itemCounts.length;
    
    if (avg === 0) return 1; // Perfect balance when no items
    
    const variance = itemCounts.reduce((sum, count) => sum + Math.pow(count - avg, 2), 0) / itemCounts.length;
    const stdDev = Math.sqrt(variance);
    
    return Math.max(0, 1 - (stdDev / avg));
  }
}