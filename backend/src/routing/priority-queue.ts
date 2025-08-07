/**
 * T-Developer Priority Queue System
 * 우선순위 기반 태스크 큐 시스템
 */

import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';

export interface QueueItem<T> {
  id: string;
  priority: number;
  data: T;
  addedAt: Date;
  attempts: number;
  lastAttempt?: Date;
}

export interface QueueStats {
  size: number;
  processing: number;
  completed: number;
  failed: number;
  avgWaitTime: number;
  avgProcessTime: number;
}

/**
 * Priority Queue Implementation
 */
export class PriorityQueue<T> extends EventEmitter {
  private logger: Logger;
  private queue: QueueItem<T>[];
  private processing: Map<string, QueueItem<T>>;
  private maxSize: number;
  private maxRetries: number;
  private stats: QueueStats;
  private waitTimes: number[];
  private processTimes: number[];
  private readonly MAX_STAT_SAMPLES = 1000;
  
  constructor(options: {
    maxSize?: number;
    maxRetries?: number;
    name?: string;
  } = {}) {
    super();
    
    this.logger = new Logger(`PriorityQueue:${options.name || 'default'}`);
    this.queue = [];
    this.processing = new Map();
    this.maxSize = options.maxSize || 10000;
    this.maxRetries = options.maxRetries || 3;
    
    this.stats = {
      size: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      avgWaitTime: 0,
      avgProcessTime: 0
    };
    
    this.waitTimes = [];
    this.processTimes = [];
  }
  
  /**
   * Add item to queue
   */
  enqueue(item: T, priority: number = 5): string {
    if (this.queue.length >= this.maxSize) {
      throw new Error('Queue is full');
    }
    
    const queueItem: QueueItem<T> = {
      id: this.generateId(),
      priority,
      data: item,
      addedAt: new Date(),
      attempts: 0
    };
    
    // Insert in priority order (higher priority first)
    const insertIndex = this.findInsertIndex(priority);
    this.queue.splice(insertIndex, 0, queueItem);
    
    this.stats.size = this.queue.length;
    
    this.logger.debug(`Item ${queueItem.id} enqueued with priority ${priority}`);
    this.emit('item:enqueued', queueItem);
    
    return queueItem.id;
  }
  
  /**
   * Remove and return highest priority item
   */
  dequeue(): QueueItem<T> | null {
    if (this.queue.length === 0) {
      return null;
    }
    
    const item = this.queue.shift()!;
    item.attempts++;
    item.lastAttempt = new Date();
    
    // Move to processing
    this.processing.set(item.id, item);
    
    // Update stats
    this.stats.size = this.queue.length;
    this.stats.processing = this.processing.size;
    
    // Record wait time
    const waitTime = Date.now() - item.addedAt.getTime();
    this.recordWaitTime(waitTime);
    
    this.logger.debug(`Item ${item.id} dequeued (attempt ${item.attempts})`);
    this.emit('item:dequeued', item);
    
    return item;
  }
  
  /**
   * Peek at highest priority item without removing
   */
  peek(): QueueItem<T> | null {
    return this.queue[0] || null;
  }
  
  /**
   * Mark item as completed
   */
  complete(itemId: string): void {
    const item = this.processing.get(itemId);
    
    if (!item) {
      this.logger.warn(`Item ${itemId} not found in processing`);
      return;
    }
    
    this.processing.delete(itemId);
    
    // Update stats
    this.stats.processing = this.processing.size;
    this.stats.completed++;
    
    // Record process time
    const processTime = Date.now() - item.lastAttempt!.getTime();
    this.recordProcessTime(processTime);
    
    this.logger.debug(`Item ${itemId} completed`);
    this.emit('item:completed', item);
  }
  
  /**
   * Mark item as failed
   */
  fail(itemId: string, error?: Error): void {
    const item = this.processing.get(itemId);
    
    if (!item) {
      this.logger.warn(`Item ${itemId} not found in processing`);
      return;
    }
    
    this.processing.delete(itemId);
    
    // Check if should retry
    if (item.attempts < this.maxRetries) {
      // Re-queue with slightly lower priority
      const newPriority = Math.max(1, item.priority - 1);
      this.queue.push({ ...item, priority: newPriority });
      this.queue.sort((a, b) => b.priority - a.priority);
      
      this.logger.debug(
        `Item ${itemId} failed (attempt ${item.attempts}/${this.maxRetries}), re-queuing`
      );
      this.emit('item:requeued', item);
    } else {
      // Max retries reached
      this.stats.failed++;
      this.logger.error(`Item ${itemId} failed after ${item.attempts} attempts`, error);
      this.emit('item:failed', { item, error });
    }
    
    // Update stats
    this.stats.processing = this.processing.size;
    this.stats.size = this.queue.length;
  }
  
  /**
   * Get queue size
   */
  size(): number {
    return this.queue.length;
  }
  
  /**
   * Check if queue is empty
   */
  isEmpty(): boolean {
    return this.queue.length === 0;
  }
  
  /**
   * Check if queue is full
   */
  isFull(): boolean {
    return this.queue.length >= this.maxSize;
  }
  
  /**
   * Clear the queue
   */
  clear(): void {
    const itemsCleared = this.queue.length;
    this.queue = [];
    this.processing.clear();
    
    this.stats.size = 0;
    this.stats.processing = 0;
    
    this.logger.info(`Queue cleared (${itemsCleared} items removed)`);
    this.emit('queue:cleared', itemsCleared);
  }
  
  /**
   * Get queue statistics
   */
  getStats(): QueueStats {
    return { ...this.stats };
  }
  
  /**
   * Get items by priority
   */
  getItemsByPriority(priority: number): QueueItem<T>[] {
    return this.queue.filter(item => item.priority === priority);
  }
  
  /**
   * Get processing items
   */
  getProcessingItems(): QueueItem<T>[] {
    return Array.from(this.processing.values());
  }
  
  /**
   * Remove specific item from queue
   */
  remove(itemId: string): boolean {
    const index = this.queue.findIndex(item => item.id === itemId);
    
    if (index !== -1) {
      this.queue.splice(index, 1);
      this.stats.size = this.queue.length;
      
      this.logger.debug(`Item ${itemId} removed from queue`);
      this.emit('item:removed', itemId);
      return true;
    }
    
    // Check if in processing
    if (this.processing.has(itemId)) {
      this.processing.delete(itemId);
      this.stats.processing = this.processing.size;
      
      this.logger.debug(`Item ${itemId} removed from processing`);
      this.emit('item:removed', itemId);
      return true;
    }
    
    return false;
  }
  
  /**
   * Update item priority
   */
  updatePriority(itemId: string, newPriority: number): boolean {
    const index = this.queue.findIndex(item => item.id === itemId);
    
    if (index === -1) {
      return false;
    }
    
    const item = this.queue[index];
    item.priority = newPriority;
    
    // Re-sort queue
    this.queue.sort((a, b) => b.priority - a.priority);
    
    this.logger.debug(`Item ${itemId} priority updated to ${newPriority}`);
    this.emit('item:priority:updated', { itemId, newPriority });
    
    return true;
  }
  
  /**
   * Batch enqueue items
   */
  batchEnqueue(items: Array<{ data: T; priority: number }>): string[] {
    const ids: string[] = [];
    
    for (const { data, priority } of items) {
      if (this.queue.length >= this.maxSize) {
        this.logger.warn('Queue full, stopping batch enqueue');
        break;
      }
      
      const id = this.enqueue(data, priority);
      ids.push(id);
    }
    
    return ids;
  }
  
  /**
   * Find insert index for priority
   */
  private findInsertIndex(priority: number): number {
    // Binary search for insertion point
    let left = 0;
    let right = this.queue.length;
    
    while (left < right) {
      const mid = Math.floor((left + right) / 2);
      
      if (this.queue[mid].priority > priority) {
        left = mid + 1;
      } else {
        right = mid;
      }
    }
    
    return left;
  }
  
  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Record wait time
   */
  private recordWaitTime(time: number): void {
    this.waitTimes.push(time);
    
    if (this.waitTimes.length > this.MAX_STAT_SAMPLES) {
      this.waitTimes.shift();
    }
    
    // Update average
    const sum = this.waitTimes.reduce((a, b) => a + b, 0);
    this.stats.avgWaitTime = this.waitTimes.length > 0 
      ? sum / this.waitTimes.length 
      : 0;
  }
  
  /**
   * Record process time
   */
  private recordProcessTime(time: number): void {
    this.processTimes.push(time);
    
    if (this.processTimes.length > this.MAX_STAT_SAMPLES) {
      this.processTimes.shift();
    }
    
    // Update average
    const sum = this.processTimes.reduce((a, b) => a + b, 0);
    this.stats.avgProcessTime = this.processTimes.length > 0 
      ? sum / this.processTimes.length 
      : 0;
  }
}

/**
 * Priority Queue Manager for multiple queues
 */
export class PriorityQueueManager {
  private queues: Map<string, PriorityQueue<any>>;
  private logger: Logger;
  
  constructor() {
    this.queues = new Map();
    this.logger = new Logger('PriorityQueueManager');
  }
  
  /**
   * Create a new queue
   */
  createQueue<T>(name: string, options?: {
    maxSize?: number;
    maxRetries?: number;
  }): PriorityQueue<T> {
    if (this.queues.has(name)) {
      throw new Error(`Queue ${name} already exists`);
    }
    
    const queue = new PriorityQueue<T>({ ...options, name });
    this.queues.set(name, queue);
    
    this.logger.info(`Queue ${name} created`);
    return queue;
  }
  
  /**
   * Get a queue
   */
  getQueue<T>(name: string): PriorityQueue<T> | undefined {
    return this.queues.get(name);
  }
  
  /**
   * Delete a queue
   */
  deleteQueue(name: string): boolean {
    const queue = this.queues.get(name);
    
    if (queue) {
      queue.clear();
      this.queues.delete(name);
      this.logger.info(`Queue ${name} deleted`);
      return true;
    }
    
    return false;
  }
  
  /**
   * Get all queue stats
   */
  getAllStats(): Map<string, QueueStats> {
    const stats = new Map<string, QueueStats>();
    
    for (const [name, queue] of this.queues) {
      stats.set(name, queue.getStats());
    }
    
    return stats;
  }
}

// Export singleton manager
export const queueManager = new PriorityQueueManager();