// backend/src/agno/memory/memory-hierarchy.ts
import { EventEmitter } from 'events';
import { randomUUID } from 'crypto';

export enum MemoryLevel {
  L1_WORKING = 1,    // 작업 메모리 (즉시 접근)
  L2_SESSION = 2,    // 세션 메모리 (대화 컨텍스트)
  L3_SHORT_TERM = 3, // 단기 메모리 (최근 상호작용)
  L4_LONG_TERM = 4,  // 장기 메모리 (지식 베이스)
  L5_PERSISTENT = 5  // 영구 메모리 (데이터베이스)
}

export interface MemoryEntry {
  id: string;
  level: MemoryLevel;
  key: string;
  value: any;
  timestamp: number;
  accessCount: number;
  ttl?: number;
  metadata?: Record<string, any>;
}

export class MemoryHierarchy extends EventEmitter {
  private stores: Map<MemoryLevel, MemoryStore> = new Map();
  private accessStats: Map<string, AccessStats> = new Map();
  
  constructor() {
    super();
    this.initializeStores();
  }
  
  private initializeStores(): void {
    this.stores.set(MemoryLevel.L1_WORKING, new WorkingMemoryStore());
    this.stores.set(MemoryLevel.L2_SESSION, new SessionMemoryStore());
    this.stores.set(MemoryLevel.L3_SHORT_TERM, new ShortTermMemoryStore());
    this.stores.set(MemoryLevel.L4_LONG_TERM, new LongTermMemoryStore());
    this.stores.set(MemoryLevel.L5_PERSISTENT, new PersistentMemoryStore());
  }
  
  async get(key: string): Promise<any> {
    // L1부터 순차 검색
    for (let level = MemoryLevel.L1_WORKING; level <= MemoryLevel.L5_PERSISTENT; level++) {
      const store = this.stores.get(level);
      const value = await store?.get(key);
      
      if (value !== undefined) {
        // 상위 레벨로 승격
        if (level > MemoryLevel.L1_WORKING) {
          await this.promote(key, value, level);
        }
        
        this.recordAccess(key, level);
        return value;
      }
    }
    
    return undefined;
  }
  
  async set(key: string, value: any, level: MemoryLevel = MemoryLevel.L1_WORKING): Promise<void> {
    const store = this.stores.get(level);
    await store?.set(key, value);
    
    // 하위 레벨에서 제거
    for (let l = MemoryLevel.L1_WORKING; l < level; l++) {
      await this.stores.get(l)?.delete(key);
    }
  }
  
  private async promote(key: string, value: any, fromLevel: MemoryLevel): Promise<void> {
    const targetLevel = Math.max(MemoryLevel.L1_WORKING, fromLevel - 1);
    await this.set(key, value, targetLevel);
  }
  
  private recordAccess(key: string, level: MemoryLevel): void {
    const stats = this.accessStats.get(key) || { count: 0, lastAccess: 0, level };
    stats.count++;
    stats.lastAccess = Date.now();
    this.accessStats.set(key, stats);
  }
  
  async optimize(): Promise<void> {
    // 메모리 압축 및 재배치
    for (const [level, store] of this.stores) {
      await store.optimize();
    }
  }
}

abstract class MemoryStore {
  protected data: Map<string, MemoryEntry> = new Map();
  
  abstract get(key: string): Promise<any>;
  abstract set(key: string, value: any): Promise<void>;
  abstract delete(key: string): Promise<void>;
  abstract optimize(): Promise<void>;
}

class WorkingMemoryStore extends MemoryStore {
  private maxSize = 100;
  
  async get(key: string): Promise<any> {
    return this.data.get(key)?.value;
  }
  
  async set(key: string, value: any): Promise<void> {
    if (this.data.size >= this.maxSize) {
      this.evictLRU();
    }
    
    this.data.set(key, {
      id: randomUUID(),
      level: MemoryLevel.L1_WORKING,
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1
    });
  }
  
  async delete(key: string): Promise<void> {
    this.data.delete(key);
  }
  
  async optimize(): Promise<void> {
    // LRU 정리
    this.evictLRU();
  }
  
  private evictLRU(): void {
    const entries = Array.from(this.data.entries());
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    
    const toRemove = entries.slice(0, Math.floor(this.maxSize * 0.2));
    toRemove.forEach(([key]) => this.data.delete(key));
  }
}

class SessionMemoryStore extends MemoryStore {
  private sessionTTL = 8 * 60 * 60 * 1000; // 8시간
  
  async get(key: string): Promise<any> {
    const entry = this.data.get(key);
    if (!entry) return undefined;
    
    if (Date.now() - entry.timestamp > this.sessionTTL) {
      this.data.delete(key);
      return undefined;
    }
    
    return entry.value;
  }
  
  async set(key: string, value: any): Promise<void> {
    this.data.set(key, {
      id: randomUUID(),
      level: MemoryLevel.L2_SESSION,
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1,
      ttl: this.sessionTTL
    });
  }
  
  async delete(key: string): Promise<void> {
    this.data.delete(key);
  }
  
  async optimize(): Promise<void> {
    const now = Date.now();
    for (const [key, entry] of this.data) {
      if (now - entry.timestamp > this.sessionTTL) {
        this.data.delete(key);
      }
    }
  }
}

class ShortTermMemoryStore extends MemoryStore {
  async get(key: string): Promise<any> {
    return this.data.get(key)?.value;
  }
  
  async set(key: string, value: any): Promise<void> {
    this.data.set(key, {
      id: randomUUID(),
      level: MemoryLevel.L3_SHORT_TERM,
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1
    });
  }
  
  async delete(key: string): Promise<void> {
    this.data.delete(key);
  }
  
  async optimize(): Promise<void> {
    // 접근 빈도 기반 정리
    const entries = Array.from(this.data.entries());
    entries.sort((a, b) => a[1].accessCount - b[1].accessCount);
    
    if (entries.length > 1000) {
      const toRemove = entries.slice(0, entries.length - 1000);
      toRemove.forEach(([key]) => this.data.delete(key));
    }
  }
}

class LongTermMemoryStore extends MemoryStore {
  async get(key: string): Promise<any> {
    return this.data.get(key)?.value;
  }
  
  async set(key: string, value: any): Promise<void> {
    this.data.set(key, {
      id: randomUUID(),
      level: MemoryLevel.L4_LONG_TERM,
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1
    });
  }
  
  async delete(key: string): Promise<void> {
    this.data.delete(key);
  }
  
  async optimize(): Promise<void> {
    // 압축 및 인덱싱
  }
}

class PersistentMemoryStore extends MemoryStore {
  async get(key: string): Promise<any> {
    // DynamoDB 조회 시뮬레이션
    return this.data.get(key)?.value;
  }
  
  async set(key: string, value: any): Promise<void> {
    this.data.set(key, {
      id: randomUUID(),
      level: MemoryLevel.L5_PERSISTENT,
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1
    });
  }
  
  async delete(key: string): Promise<void> {
    this.data.delete(key);
  }
  
  async optimize(): Promise<void> {
    // 데이터베이스 최적화
  }
}

interface AccessStats {
  count: number;
  lastAccess: number;
  level: MemoryLevel;
}