import Redis, { Cluster } from 'ioredis';

export interface CacheConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
  keyPrefix?: string;
  ttl?: number;
  cluster?: boolean;
  nodes?: Array<{ host: string; port: number }>;
}

export class RedisClient {
  private client: Redis | Cluster;
  private config: CacheConfig;

  constructor(config: CacheConfig) {
    this.config = config;
    
    if (config.cluster && config.nodes) {
      this.client = new Cluster(config.nodes, {
        redisOptions: {
          password: config.password,
          keyPrefix: config.keyPrefix
        }
      });
    } else {
      this.client = new Redis({
        host: config.host,
        port: config.port,
        password: config.password,
        db: config.db || 0,
        keyPrefix: config.keyPrefix,
        retryDelayOnFailover: 100,
        maxRetriesPerRequest: 3
      });
    }
  }

  async get<T>(key: string): Promise<T | null> {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    const serialized = JSON.stringify(value);
    const expiry = ttl || this.config.ttl || 3600;
    await this.client.setex(key, expiry, serialized);
  }

  async del(key: string): Promise<void> {
    await this.client.del(key);
  }

  async exists(key: string): Promise<boolean> {
    return (await this.client.exists(key)) === 1;
  }

  async mget<T>(keys: string[]): Promise<(T | null)[]> {
    const values = await this.client.mget(...keys);
    return values.map(v => v ? JSON.parse(v) : null);
  }

  async mset<T>(items: Array<{ key: string; value: T; ttl?: number }>): Promise<void> {
    const pipeline = this.client.pipeline();
    
    items.forEach(({ key, value, ttl }) => {
      const serialized = JSON.stringify(value);
      const expiry = ttl || this.config.ttl || 3600;
      pipeline.setex(key, expiry, serialized);
    });
    
    await pipeline.exec();
  }

  async invalidatePattern(pattern: string): Promise<number> {
    const keys = await this.client.keys(pattern);
    if (keys.length === 0) return 0;
    
    await this.client.del(...keys);
    return keys.length;
  }

  async disconnect(): Promise<void> {
    await this.client.disconnect();
  }
}