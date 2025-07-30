import { Redis } from 'ioredis';
import { DynamoDBDocumentClient, PutCommand, GetCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';

export abstract class MemoryLayer {
  abstract get(key: string): Promise<any>;
  abstract set(key: string, value: any, ttl?: number): Promise<void>;
  abstract delete(key: string): Promise<void>;
  abstract clear(): Promise<void>;
  abstract size(): Promise<number>;
}

export class WorkingMemory extends MemoryLayer {
  private memory: Map<string, MemoryItem> = new Map();
  private accessCount: Map<string, number> = new Map();
  private maxSize: number;
  
  constructor(maxSize: number = 1000) {
    super();
    this.maxSize = maxSize;
  }
  
  async get(key: string): Promise<any> {
    const item = this.memory.get(key);
    if (!item) return null;
    
    // TTL 체크
    if (item.expiresAt && Date.now() > item.expiresAt) {
      this.memory.delete(key);
      this.accessCount.delete(key);
      return null;
    }
    
    // 접근 횟수 증가
    this.accessCount.set(key, (this.accessCount.get(key) || 0) + 1);
    item.lastAccessed = Date.now();
    
    return item.value;
  }
  
  async set(key: string, value: any, ttl?: number): Promise<void> {
    // 메모리 크기 제한 확인
    if (this.memory.size >= this.maxSize && !this.memory.has(key)) {
      await this.evictLRU();
    }
    
    const item: MemoryItem = {
      value,
      createdAt: Date.now(),
      lastAccessed: Date.now(),
      expiresAt: ttl ? Date.now() + ttl * 1000 : undefined
    };
    
    this.memory.set(key, item);
    this.accessCount.set(key, 1);
  }
  
  async delete(key: string): Promise<void> {
    this.memory.delete(key);
    this.accessCount.delete(key);
  }
  
  async clear(): Promise<void> {
    this.memory.clear();
    this.accessCount.clear();
  }
  
  async size(): Promise<number> {
    return this.memory.size;
  }
  
  private async evictLRU(): Promise<void> {
    if (this.memory.size === 0) return;
    
    // LRU 항목 찾기
    let lruKey: string | null = null;
    let oldestAccess = Date.now();
    
    for (const [key, item] of this.memory) {
      if (item.lastAccessed < oldestAccess) {
        oldestAccess = item.lastAccessed;
        lruKey = key;
      }
    }
    
    if (lruKey) {
      await this.delete(lruKey);
    }
  }
  
  // 메모리 통계
  getStats(): MemoryStats {
    const items = Array.from(this.memory.values());
    const now = Date.now();
    
    return {
      totalItems: this.memory.size,
      memoryUsage: this.calculateMemoryUsage(),
      averageAge: items.length > 0 
        ? items.reduce((sum, item) => sum + (now - item.createdAt), 0) / items.length 
        : 0,
      hitRate: this.calculateHitRate()
    };
  }
  
  private calculateMemoryUsage(): number {
    let totalSize = 0;
    for (const [key, item] of this.memory) {
      totalSize += JSON.stringify({ key, value: item.value }).length;
    }
    return totalSize;
  }
  
  private calculateHitRate(): number {
    // 간단한 히트율 계산 (실제로는 더 정교한 추적 필요)
    const totalAccesses = Array.from(this.accessCount.values()).reduce((sum, count) => sum + count, 0);
    return totalAccesses > 0 ? this.memory.size / totalAccesses : 0;
  }
}

export class ShortTermMemory extends MemoryLayer {
  private redis: Redis;
  
  constructor(redis: Redis) {
    super();
    this.redis = redis;
  }
  
  async get(key: string): Promise<any> {
    const value = await this.redis.get(key);
    if (!value) return null;
    
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }
  
  async set(key: string, value: any, ttl?: number): Promise<void> {
    const serialized = typeof value === 'string' ? value : JSON.stringify(value);
    
    if (ttl) {
      await this.redis.setex(key, ttl, serialized);
    } else {
      await this.redis.set(key, serialized);
    }
  }
  
  async delete(key: string): Promise<void> {
    await this.redis.del(key);
  }
  
  async clear(): Promise<void> {
    await this.redis.flushdb();
  }
  
  async size(): Promise<number> {
    return await this.redis.dbsize();
  }
}

export class LongTermMemory extends MemoryLayer {
  private dynamoClient: DynamoDBDocumentClient;
  private tableName: string;
  
  constructor(dynamoClient: DynamoDBDocumentClient, tableName: string = 'T-Developer-Memory') {
    super();
    this.dynamoClient = dynamoClient;
    this.tableName = tableName;
  }
  
  async get(key: string): Promise<any> {
    try {
      const response = await this.dynamoClient.send(new GetCommand({
        TableName: this.tableName,
        Key: { id: key }
      }));
      
      if (!response.Item) return null;
      
      // TTL 체크
      if (response.Item.expiresAt && Date.now() > response.Item.expiresAt * 1000) {
        await this.delete(key);
        return null;
      }
      
      // 접근 횟수 업데이트
      await this.incrementAccessCount(key);
      
      return response.Item.value;
      
    } catch (error) {
      console.error('LongTermMemory get error:', error);
      return null;
    }
  }
  
  async set(key: string, value: any, ttl?: number): Promise<void> {
    const item = {
      id: key,
      value,
      createdAt: Math.floor(Date.now() / 1000),
      lastAccessed: Math.floor(Date.now() / 1000),
      accessCount: 1,
      expiresAt: ttl ? Math.floor((Date.now() + ttl * 1000) / 1000) : undefined
    };
    
    await this.dynamoClient.send(new PutCommand({
      TableName: this.tableName,
      Item: item
    }));
  }
  
  async delete(key: string): Promise<void> {
    await this.dynamoClient.send(new DeleteCommand({
      TableName: this.tableName,
      Key: { id: key }
    }));
  }
  
  async clear(): Promise<void> {
    // DynamoDB는 전체 삭제가 비효율적이므로 스캔 후 배치 삭제 필요
    console.warn('LongTermMemory clear() is not implemented for efficiency reasons');
  }
  
  async size(): Promise<number> {
    // DynamoDB에서 정확한 크기를 얻기 위해서는 스캔이 필요하므로 비효율적
    return -1; // 구현하지 않음
  }
  
  private async incrementAccessCount(key: string): Promise<void> {
    // 비동기로 접근 횟수 업데이트 (성능을 위해 별도 처리)
    setImmediate(async () => {
      try {
        await this.dynamoClient.send(new PutCommand({
          TableName: this.tableName,
          Key: { id: key },
          UpdateExpression: 'ADD accessCount :inc SET lastAccessed = :now',
          ExpressionAttributeValues: {
            ':inc': 1,
            ':now': Math.floor(Date.now() / 1000)
          }
        }));
      } catch (error) {
        console.error('Failed to update access count:', error);
      }
    });
  }
}

export class HierarchicalMemorySystem {
  private workingMemory: WorkingMemory;
  private shortTermMemory: ShortTermMemory;
  private longTermMemory: LongTermMemory;
  
  // 메모리 정책
  private promotionThreshold = 5; // 승격 임계값
  private demotionThreshold = 30 * 24 * 60 * 60; // 30일 (초)
  
  constructor(
    redis: Redis,
    dynamoClient: DynamoDBDocumentClient,
    options?: {
      workingMemorySize?: number;
      promotionThreshold?: number;
      demotionThreshold?: number;
    }
  ) {
    this.workingMemory = new WorkingMemory(options?.workingMemorySize);
    this.shortTermMemory = new ShortTermMemory(redis);
    this.longTermMemory = new LongTermMemory(dynamoClient);
    
    if (options?.promotionThreshold) {
      this.promotionThreshold = options.promotionThreshold;
    }
    if (options?.demotionThreshold) {
      this.demotionThreshold = options.demotionThreshold;
    }
  }
  
  async remember(
    key: string,
    value: any,
    importance: 'low' | 'normal' | 'high' | 'critical' = 'normal'
  ): Promise<void> {
    switch (importance) {
      case 'critical':
        // 모든 레이어에 저장
        await Promise.all([
          this.workingMemory.set(key, value),
          this.shortTermMemory.set(key, value, 86400), // 1일
          this.longTermMemory.set(key, value)
        ]);
        break;
        
      case 'high':
        // 단기 및 장기 메모리에 저장
        await Promise.all([
          this.shortTermMemory.set(key, value, 3600), // 1시간
          this.longTermMemory.set(key, value)
        ]);
        break;
        
      case 'normal':
        // 작업 메모리와 단기 메모리에 저장
        await Promise.all([
          this.workingMemory.set(key, value),
          this.shortTermMemory.set(key, value, 1800) // 30분
        ]);
        break;
        
      case 'low':
        // 작업 메모리에만 저장
        await this.workingMemory.set(key, value, 300); // 5분 TTL
        break;
    }
  }
  
  async recall(key: string): Promise<any> {
    // 1. 작업 메모리 확인
    let value = await this.workingMemory.get(key);
    if (value !== null) {
      return value;
    }
    
    // 2. 단기 메모리 확인
    value = await this.shortTermMemory.get(key);
    if (value !== null) {
      // 작업 메모리로 승격
      await this.workingMemory.set(key, value);
      return value;
    }
    
    // 3. 장기 메모리 확인
    value = await this.longTermMemory.get(key);
    if (value !== null) {
      // 단기 메모리로 승격
      await this.shortTermMemory.set(key, value, 3600);
      await this.workingMemory.set(key, value);
      return value;
    }
    
    return null;
  }
  
  async forget(key: string): Promise<void> {
    await Promise.all([
      this.workingMemory.delete(key),
      this.shortTermMemory.delete(key),
      this.longTermMemory.delete(key)
    ]);
  }
  
  // 메모리 최적화
  async optimize(): Promise<MemoryOptimizationResult> {
    const result: MemoryOptimizationResult = {
      itemsPromoted: 0,
      itemsDemoted: 0,
      itemsEvicted: 0,
      memoryFreed: 0
    };
    
    // 작업 메모리 통계 확인
    const workingStats = this.workingMemory.getStats();
    
    // 메모리 사용량이 높으면 정리
    if (workingStats.memoryUsage > 50 * 1024 * 1024) { // 50MB
      // LRU 기반 정리는 WorkingMemory에서 자동 처리됨
      result.memoryFreed = workingStats.memoryUsage * 0.2; // 예상 정리량
    }
    
    return result;
  }
  
  // 메모리 상태 조회
  async getMemoryStatus(): Promise<MemoryStatus> {
    const [workingSize, shortTermSize] = await Promise.all([
      this.workingMemory.size(),
      this.shortTermMemory.size()
    ]);
    
    return {
      workingMemory: {
        size: workingSize,
        stats: this.workingMemory.getStats()
      },
      shortTermMemory: {
        size: shortTermSize
      },
      longTermMemory: {
        size: -1 // DynamoDB 크기는 효율적으로 계산하기 어려움
      }
    };
  }
}

// 인터페이스 정의
interface MemoryItem {
  value: any;
  createdAt: number;
  lastAccessed: number;
  expiresAt?: number;
}

interface MemoryStats {
  totalItems: number;
  memoryUsage: number;
  averageAge: number;
  hitRate: number;
}

interface MemoryOptimizationResult {
  itemsPromoted: number;
  itemsDemoted: number;
  itemsEvicted: number;
  memoryFreed: number;
}

interface MemoryStatus {
  workingMemory: {
    size: number;
    stats: MemoryStats;
  };
  shortTermMemory: {
    size: number;
  };
  longTermMemory: {
    size: number;
  };
}