import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { BedrockRuntimeClient } from '@aws-sdk/client-bedrock-runtime';
import Redis from 'ioredis';
import { EventEmitter } from 'events';

interface PoolConfig {
  min: number;
  max: number;
  acquireTimeoutMillis: number;
  idleTimeoutMillis: number;
  reapIntervalMillis: number;
}

interface ConnectionMetrics {
  total: number;
  active: number;
  idle: number;
  pending: number;
  created: number;
  destroyed: number;
}

export class ConnectionPool<T> extends EventEmitter {
  private connections: Set<T> = new Set();
  private available: T[] = [];
  private pending: Array<{ resolve: (conn: T) => void; reject: (err: Error) => void }> = [];
  private config: PoolConfig;
  private createConnection: () => Promise<T>;
  private destroyConnection: (conn: T) => Promise<void>;
  private validateConnection: (conn: T) => Promise<boolean>;
  private metrics: ConnectionMetrics = {
    total: 0, active: 0, idle: 0, pending: 0, created: 0, destroyed: 0
  };

  constructor(
    config: PoolConfig,
    createFn: () => Promise<T>,
    destroyFn: (conn: T) => Promise<void>,
    validateFn: (conn: T) => Promise<boolean>
  ) {
    super();
    this.config = config;
    this.createConnection = createFn;
    this.destroyConnection = destroyFn;
    this.validateConnection = validateFn;
    
    this.startReaper();
    this.warmUp();
  }

  async acquire(): Promise<T> {
    if (this.available.length > 0) {
      const conn = this.available.pop()!;
      this.metrics.active++;
      this.metrics.idle--;
      return conn;
    }

    if (this.connections.size < this.config.max) {
      const conn = await this.createConnection();
      this.connections.add(conn);
      this.metrics.total++;
      this.metrics.active++;
      this.metrics.created++;
      return conn;
    }

    return new Promise((resolve, reject) => {
      this.pending.push({ resolve, reject });
      this.metrics.pending++;
      
      setTimeout(() => {
        const index = this.pending.findIndex(p => p.resolve === resolve);
        if (index >= 0) {
          this.pending.splice(index, 1);
          this.metrics.pending--;
          reject(new Error('Connection acquire timeout'));
        }
      }, this.config.acquireTimeoutMillis);
    });
  }

  async release(connection: T): Promise<void> {
    if (!this.connections.has(connection)) return;

    if (this.pending.length > 0) {
      const { resolve } = this.pending.shift()!;
      this.metrics.pending--;
      resolve(connection);
      return;
    }

    this.available.push(connection);
    this.metrics.active--;
    this.metrics.idle++;
  }

  private async warmUp(): Promise<void> {
    const promises = [];
    for (let i = 0; i < this.config.min; i++) {
      promises.push(this.createConnection().then(conn => {
        this.connections.add(conn);
        this.available.push(conn);
        this.metrics.total++;
        this.metrics.idle++;
        this.metrics.created++;
      }));
    }
    await Promise.all(promises);
  }

  private startReaper(): void {
    setInterval(async () => {
      const toDestroy = this.available.filter(() => 
        this.available.length > this.config.min
      ).slice(0, this.available.length - this.config.min);

      for (const conn of toDestroy) {
        const index = this.available.indexOf(conn);
        if (index >= 0) {
          this.available.splice(index, 1);
          this.connections.delete(conn);
          await this.destroyConnection(conn);
          this.metrics.total--;
          this.metrics.idle--;
          this.metrics.destroyed++;
        }
      }
    }, this.config.reapIntervalMillis);
  }

  getMetrics(): ConnectionMetrics {
    return { ...this.metrics };
  }
}

export class DynamoDBPool {
  private pool: ConnectionPool<DynamoDBDocumentClient>;

  constructor() {
    this.pool = new ConnectionPool(
      {
        min: 5,
        max: 50,
        acquireTimeoutMillis: 5000,
        idleTimeoutMillis: 300000,
        reapIntervalMillis: 60000
      },
      this.createClient,
      this.destroyClient,
      this.validateClient
    );
  }

  private async createClient(): Promise<DynamoDBDocumentClient> {
    const client = new DynamoDBClient({
      region: process.env.AWS_REGION,
      maxAttempts: 3
    });
    return DynamoDBDocumentClient.from(client);
  }

  private async destroyClient(client: DynamoDBDocumentClient): Promise<void> {
    client.destroy();
  }

  private async validateClient(client: DynamoDBDocumentClient): Promise<boolean> {
    try {
      return true;
    } catch {
      return false;
    }
  }

  async getClient(): Promise<DynamoDBDocumentClient> {
    return this.pool.acquire();
  }

  async releaseClient(client: DynamoDBDocumentClient): Promise<void> {
    return this.pool.release(client);
  }
}

export class RedisPool {
  private pool: ConnectionPool<Redis>;

  constructor() {
    this.pool = new ConnectionPool(
      {
        min: 3,
        max: 20,
        acquireTimeoutMillis: 3000,
        idleTimeoutMillis: 180000,
        reapIntervalMillis: 30000
      },
      this.createClient,
      this.destroyClient,
      this.validateClient
    );
  }

  private async createClient(): Promise<Redis> {
    return new Redis({
      host: process.env.REDIS_HOST,
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3
    });
  }

  private async destroyClient(client: Redis): Promise<void> {
    client.disconnect();
  }

  private async validateClient(client: Redis): Promise<boolean> {
    try {
      await client.ping();
      return true;
    } catch {
      return false;
    }
  }

  async getClient(): Promise<Redis> {
    return this.pool.acquire();
  }

  async releaseClient(client: Redis): Promise<void> {
    return this.pool.release(client);
  }
}

export class BedrockPool {
  private pool: ConnectionPool<BedrockRuntimeClient>;

  constructor() {
    this.pool = new ConnectionPool(
      {
        min: 2,
        max: 10,
        acquireTimeoutMillis: 10000,
        idleTimeoutMillis: 600000,
        reapIntervalMillis: 120000
      },
      this.createClient,
      this.destroyClient,
      this.validateClient
    );
  }

  private async createClient(): Promise<BedrockRuntimeClient> {
    return new BedrockRuntimeClient({
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1',
      maxAttempts: 3
    });
  }

  private async destroyClient(client: BedrockRuntimeClient): Promise<void> {
    client.destroy();
  }

  private async validateClient(client: BedrockRuntimeClient): Promise<boolean> {
    return true;
  }

  async getClient(): Promise<BedrockRuntimeClient> {
    return this.pool.acquire();
  }

  async releaseClient(client: BedrockRuntimeClient): Promise<void> {
    return this.pool.release(client);
  }
}

export class PoolManager {
  private static instance: PoolManager;
  private dynamoPool: DynamoDBPool;
  private redisPool: RedisPool;
  private bedrockPool: BedrockPool;

  private constructor() {
    this.dynamoPool = new DynamoDBPool();
    this.redisPool = new RedisPool();
    this.bedrockPool = new BedrockPool();
  }

  static getInstance(): PoolManager {
    if (!PoolManager.instance) {
      PoolManager.instance = new PoolManager();
    }
    return PoolManager.instance;
  }

  getDynamoPool(): DynamoDBPool {
    return this.dynamoPool;
  }

  getRedisPool(): RedisPool {
    return this.redisPool;
  }

  getBedrockPool(): BedrockPool {
    return this.bedrockPool;
  }
}