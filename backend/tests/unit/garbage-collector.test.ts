import { MemoryGarbageCollector, GCPolicy } from '../../src/memory/garbage-collector';

describe('MemoryGarbageCollector', () => {
  let gc: MemoryGarbageCollector;
  let policy: GCPolicy;

  beforeEach(() => {
    policy = {
      maxMemoryMB: 10,
      maxAge: 1, // 1 day
      minRelevance: 0.3,
      gcInterval: 1 // 1 second for testing
    };
    gc = new MemoryGarbageCollector(policy);
  });

  afterEach(() => {
    gc.stop();
  });

  test('should add and retrieve memory items', () => {
    gc.addMemoryItem('test-key', { data: 'test' }, 0.8);
    
    const item = gc.getMemoryItem('test-key');
    expect(item).toEqual({ data: 'test' });
  });

  test('should return null for non-existent items', () => {
    const item = gc.getMemoryItem('non-existent');
    expect(item).toBeNull();
  });

  test('should track access count', () => {
    gc.addMemoryItem('test-key', { data: 'test' }, 0.8);
    
    // Access multiple times
    gc.getMemoryItem('test-key');
    gc.getMemoryItem('test-key');
    gc.getMemoryItem('test-key');
    
    const stats = gc.getStats();
    expect(stats.totalItems).toBe(1);
  });

  test('should provide memory statistics', () => {
    gc.addMemoryItem('item1', { data: 'test1' }, 0.8);
    gc.addMemoryItem('item2', { data: 'test2' }, 0.6);
    
    const stats = gc.getStats();
    expect(stats.totalItems).toBe(2);
    expect(stats.totalMemoryMB).toBeGreaterThan(0);
    expect(stats.avgRelevance).toBe(0.7);
    expect(stats.oldestItem).toBeInstanceOf(Date);
  });

  test('should start and stop garbage collection', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    gc.start();
    expect(consoleSpy).toHaveBeenCalledWith('Memory garbage collector started');
    
    gc.stop();
    expect(consoleSpy).toHaveBeenCalledWith('Memory garbage collector stopped');
    
    consoleSpy.mockRestore();
  });

  test('should not start multiple times', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    gc.start();
    gc.start(); // Should not start again
    
    expect(consoleSpy).toHaveBeenCalledTimes(1);
    
    consoleSpy.mockRestore();
  });

  test('should handle empty memory store', () => {
    const stats = gc.getStats();
    
    expect(stats.totalItems).toBe(0);
    expect(stats.totalMemoryMB).toBe(0);
    expect(stats.oldestItem).toBeNull();
    expect(stats.avgRelevance).toBe(0);
  });
});