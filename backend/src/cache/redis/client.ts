import Redis from 'ioredis';

export interface RedisConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
  maxRetriesPerRequest?: number;
  retryDelayOnFailover?: number;
}

export class RedisClient {
  private client!: Redis;
  private config: RedisConfig;
  
  constructor(config: RedisConfig) {
    this.config = config;
    this.initializeClient();
  }
  
  private initializeClient(): void {
    this.client = new Redis({
      host: this.config.host,
      port: this.config.port,
      password: this.config.password,
      db: this.config.db || 0,
      maxRetriesPerRequest: this.config.maxRetriesPerRequest || 3,
      lazyConnect: true
    });
    
    this.setupEventHandlers();
  }
  
  private setupEventHandlers(): void {
    this.client.on('connect', () => {
      console.log('✅ Redis connected');
    });
    
    this.client.on('error', (error) => {
      console.error('❌ Redis error:', error);
    });
    
    this.client.on('close', () => {
      console.log('🔌 Redis connection closed');
    });
  }
  
  async connect(): Promise<void> {
    await this.client.connect();
  }
  
  async disconnect(): Promise<void> {
    await this.client.disconnect();
  }
  
  getClient(): Redis {
    return this.client;
  }
  
  async healthCheck(): Promise<{ status: string; latency: number }> {
    const start = Date.now();
    
    try {
      await this.client.ping();
      return {
        status: 'healthy',
        latency: Date.now() - start
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        latency: Date.now() - start
      };
    }
  }
  
  // Basic operations
  async set(key: string, value: any, ttl?: number): Promise<void> {
    const serialized = JSON.stringify(value);
    if (ttl) {
      await this.client.setex(key, ttl, serialized);
    } else {
      await this.client.set(key, serialized);
    }
  }
  
  async get<T>(key: string): Promise<T | null> {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }
  
  async del(key: string): Promise<void> {
    await this.client.del(key);
  }
  
  async exists(key: string): Promise<boolean> {
    const result = await this.client.exists(key);
    return result === 1;
  }
  
  async expire(key: string, seconds: number): Promise<void> {
    await this.client.expire(key, seconds);
  }
  
  async ttl(key: string): Promise<number> {
    return await this.client.ttl(key);
  }
}