
import express from 'express';
import { CacheManager, CacheNamespace, httpCacheMiddleware } from '../performance/caching';

const router = express.Router();
const cacheManager = new CacheManager();

// 캐시 테스트 데이터
const testData = [
  { id: 1, name: 'Project Alpha', status: 'active' },
  { id: 2, name: 'Project Beta', status: 'completed' },
  { id: 3, name: 'Project Gamma', status: 'pending' }
];

// 캐시된 프로젝트 목록 (5분 캐시)
router.get('/projects', httpCacheMiddleware({ ttl: 300 }), (req, res) => {
  // 실제로는 데이터베이스에서 조회
  setTimeout(() => {
    res.json({
      success: true,
      data: testData,
      cached: false,
      timestamp: new Date().toISOString()
    });
  }, 100); // 100ms 지연 시뮬레이션
});

// 수동 캐시 설정/조회
router.post('/cache/set', async (req, res) => {
  const { key, value, ttl } = req.body;
  
  try {
    await cacheManager.set(CacheNamespace.API_RESPONSE, key, value, undefined, ttl);
    res.json({ success: true, message: 'Cache set successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/cache/get/:key', async (req, res) => {
  const { key } = req.params;
  
  try {
    const value = await cacheManager.get(CacheNamespace.API_RESPONSE, key);
    res.json({ 
      success: true, 
      data: value,
      found: value !== null
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 캐시 통계
router.get('/cache/stats', (req, res) => {
  const stats = cacheManager.getStats();
  res.json({ success: true, stats });
});

// 캐시 무효화
router.delete('/cache/invalidate/:key', async (req, res) => {
  const { key } = req.params;
  
  try {
    await cacheManager.invalidate(CacheNamespace.API_RESPONSE, key);
    res.json({ success: true, message: 'Cache invalidated' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
