import Redis, { Cluster, ClusterOptions } from 'ioredis';
import { EventEmitter } from 'events';

export interface ClusterNode {
  host: string;
  port: number;
  role?: 'master' | 'slave';
}

export interface ClusterConfig {
  nodes: ClusterNode[];
  options: ClusterOptions;
  healthCheckInterval: number;
}

export class RedisClusterManager extends EventEmitter {
  private cluster: Cluster;
  private healthTimer: NodeJS.Timer;
  private nodeStatus: Map<string, boolean> = new Map();

  constructor(private config: ClusterConfig) {
    super();
    this.initializeCluster();
    this.startHealthMonitoring();
  }

  private initializeCluster(): void {
    this.cluster = new Cluster(
      this.config.nodes.map(node => ({ host: node.host, port: node.port })),
      {
        ...this.config.options,
        enableReadyCheck: true,
        enableOfflineQueue: true,
        maxRetriesPerRequest: 3,
        retryDelayOnFailover: 100,
        clusterRetryStrategy: (times) => Math.min(times * 100, 3000)
      }
    );

    this.cluster.on('connect', () => this.emit('connected'));
    this.cluster.on('ready', () => this.emit('ready'));
    this.cluster.on('error', (error) => this.emit('error', error));
    this.cluster.on('node error', (error, node) => {
      this.nodeStatus.set(node, false);
      this.emit('nodeError', { error, node });
    });
  }

  private startHealthMonitoring(): void {
    this.healthTimer = setInterval(async () => {
      const nodes = this.cluster.nodes('all');
      
      for (const node of nodes) {
        try {
          await node.ping();
          this.nodeStatus.set(`${node.options.host}:${node.options.port}`, true);
        } catch (error) {
          this.nodeStatus.set(`${node.options.host}:${node.options.port}`, false);
        }
      }
    }, this.config.healthCheckInterval);
  }

  async get(key: string): Promise<any> {
    try {
      const value = await this.cluster.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    const serialized = JSON.stringify(value);
    
    if (ttl) {
      await this.cluster.setex(key, ttl, serialized);
    } else {
      await this.cluster.set(key, serialized);
    }
  }

  async del(key: string): Promise<number> {
    return await this.cluster.del(key);
  }

  async mget(keys: string[]): Promise<any[]> {
    const values = await this.cluster.mget(...keys);
    return values.map(v => v ? JSON.parse(v) : null);
  }

  async mset(pairs: Array<{ key: string; value: any; ttl?: number }>): Promise<void> {
    const pipeline = this.cluster.pipeline();
    
    pairs.forEach(({ key, value, ttl }) => {
      const serialized = JSON.stringify(value);
      if (ttl) {
        pipeline.setex(key, ttl, serialized);
      } else {
        pipeline.set(key, serialized);
      }
    });
    
    await pipeline.exec();
  }

  getHealthStatus(): Record<string, boolean> {
    return Object.fromEntries(this.nodeStatus);
  }

  async shutdown(): Promise<void> {
    if (this.healthTimer) {
      clearInterval(this.healthTimer);
    }
    await this.cluster.disconnect();
  }
}