/**
 * Shard Manager for Horizontal Partitioning
 * Manages data distribution across multiple shards
 */

import crypto from 'crypto';

export interface ShardConfig {
  shardId: string;
  minHash: string;
  maxHash: string;
  weight: number;
  enabled: boolean;
}

export class ShardManager {
  private shards: Map<string, ShardConfig> = new Map();
  private totalWeight: number = 0;

  public addShard(config: ShardConfig): void {
    this.shards.set(config.shardId, config);
    if (config.enabled) {
      this.totalWeight += config.weight;
    }
  }

  public getShardForKey(key: string): string | null {
    const hash = this.hash(key);
    
    for (const [shardId, config] of this.shards) {
      if (config.enabled && hash >= config.minHash && hash <= config.maxHash) {
        return shardId;
      }
    }
    
    return null;
  }

  public distributeData(keys: string[]): Map<string, string[]> {
    const distribution = new Map<string, string[]>();
    
    for (const key of keys) {
      const shardId = this.getShardForKey(key);
      if (shardId) {
        if (!distribution.has(shardId)) {
          distribution.set(shardId, []);
        }
        distribution.get(shardId)!.push(key);
      }
    }
    
    return distribution;
  }

  private hash(key: string): string {
    return crypto.createHash('md5').update(key).digest('hex');
  }

  public getShardStats(): Array<{ shardId: string; keyCount: number; enabled: boolean }> {
    const stats: Array<{ shardId: string; keyCount: number; enabled: boolean }> = [];
    
    for (const [shardId, config] of this.shards) {
      stats.push({
        shardId,
        keyCount: 0, // Would be calculated from actual data
        enabled: config.enabled
      });
    }
    
    return stats;
  }
}