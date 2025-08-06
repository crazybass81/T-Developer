
import { CacheManager, CacheNamespace } from '../src/performance/caching';

describe('CacheManager', () => {
  let cacheManager: CacheManager;
  
  beforeEach(() => {
    cacheManager = new CacheManager();
  });
  
  test('should set and get cache value', async () => {
    const testValue = { id: 1, name: 'test' };
    
    await cacheManager.set(CacheNamespace.PROJECT, 'test-key', testValue);
    const result = await cacheManager.get(CacheNamespace.PROJECT, 'test-key');
    
    expect(result).toEqual(testValue);
  });
  
  test('should return null for non-existent key', async () => {
    const result = await cacheManager.get(CacheNamespace.PROJECT, 'non-existent');
    expect(result).toBeNull();
  });
  
  test('should invalidate cache', async () => {
    const testValue = { id: 1, name: 'test' };
    
    await cacheManager.set(CacheNamespace.PROJECT, 'test-key', testValue);
    await cacheManager.invalidate(CacheNamespace.PROJECT, 'test-key');
    
    const result = await cacheManager.get(CacheNamespace.PROJECT, 'test-key');
    expect(result).toBeNull();
  });
  
  test('should provide cache statistics', () => {
    const stats = cacheManager.getStats();
    
    expect(stats).toHaveProperty('hits');
    expect(stats).toHaveProperty('misses');
    expect(stats).toHaveProperty('errors');
    expect(stats).toHaveProperty('hitRate');
  });
});
