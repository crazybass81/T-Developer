import { Router, Request, Response } from 'express';
import { CacheManager } from './cache-manager';
import { SecurityMiddleware } from '../security/security-middleware';

const router = Router();
const security = new SecurityMiddleware();

let cacheManager: CacheManager;

export function initializeCacheRoutes(cache: CacheManager) {
  cacheManager = cache;
  return router;
}

// Get cache statistics
router.get('/stats', security.authenticate(), security.authorize(['system:admin']), async (req: Request, res: Response) => {
  try {
    const stats = await cacheManager.getStats();
    
    res.json({
      success: true,
      stats
    });
  } catch (error: any) {
    console.error('Cache stats error:', error);
    res.status(500).json({ error: 'Failed to get cache stats' });
  }
});

// Get cached item
router.get('/items/:key', security.authenticate(), security.authorize(['project:read']), async (req: Request, res: Response) => {
  try {
    const { key } = req.params;
    const value = await cacheManager.get(key);
    
    if (value === null) {
      return res.status(404).json({ error: 'Cache key not found' });
    }
    
    res.json({
      success: true,
      key,
      value,
      cached: true
    });
  } catch (error: any) {
    console.error('Cache get error:', error);
    res.status(500).json({ error: 'Failed to get cached item' });
  }
});

// Set cache item
router.post('/items', security.authenticate(), security.authorize(['project:write']), async (req: Request, res: Response) => {
  try {
    const { key, value, ttl } = req.body;
    
    if (!key || value === undefined) {
      return res.status(400).json({ error: 'key and value are required' });
    }
    
    await cacheManager.set(key, value, { ttl });
    
    res.json({
      success: true,
      message: 'Item cached successfully',
      key,
      ttl: ttl || 3600
    });
  } catch (error: any) {
    console.error('Cache set error:', error);
    res.status(500).json({ error: 'Failed to cache item' });
  }
});

// Delete cache item
router.delete('/items/:key', security.authenticate(), security.authorize(['project:write']), async (req: Request, res: Response) => {
  try {
    const { key } = req.params;
    await cacheManager.del(key);
    
    res.json({
      success: true,
      message: 'Cache item deleted successfully',
      key
    });
  } catch (error: any) {
    console.error('Cache delete error:', error);
    res.status(500).json({ error: 'Failed to delete cache item' });
  }
});

// Invalidate cache pattern
router.post('/invalidate', security.authenticate(), security.authorize(['system:admin']), async (req: Request, res: Response) => {
  try {
    const { pattern } = req.body;
    
    if (!pattern) {
      return res.status(400).json({ error: 'pattern is required' });
    }
    
    const deletedCount = await cacheManager.deletePattern(pattern);
    
    res.json({
      success: true,
      message: 'Cache pattern invalidated',
      pattern,
      deletedCount
    });
  } catch (error: any) {
    console.error('Cache invalidate error:', error);
    res.status(500).json({ error: 'Failed to invalidate cache pattern' });
  }
});

// Warm cache
router.post('/warm', security.authenticate(), security.authorize(['system:admin']), async (req: Request, res: Response) => {
  try {
    const { keys, fetcher } = req.body;
    
    if (!Array.isArray(keys)) {
      return res.status(400).json({ error: 'keys array is required' });
    }
    
    // Mock fetcher for demo
    const mockFetcher = async (key: string) => ({
      key,
      data: `warmed-data-${key}`,
      timestamp: new Date().toISOString()
    });
    
    await cacheManager.warmCache(keys, mockFetcher, { ttl: 3600 });
    
    res.json({
      success: true,
      message: 'Cache warmed successfully',
      keys,
      count: keys.length
    });
  } catch (error: any) {
    console.error('Cache warm error:', error);
    res.status(500).json({ error: 'Failed to warm cache' });
  }
});

export default router;