import { Router } from 'express';
import { MemoryManager, MemoryPoolManager } from '../performance/memory-manager';

const router = Router();
const memoryManager = new MemoryManager();

// 버퍼 풀 예시
const bufferPool = new MemoryPoolManager({
  factory: () => Buffer.alloc(1024),
  reset: (buffer) => buffer.fill(0),
  initialSize: 10,
  maxSize: 50
});

// 메모리 상태 조회
router.get('/status', (req, res) => {
  const status = memoryManager.getMemoryStatus();
  res.json({
    success: true,
    data: {
      memory: status,
      bufferPool: bufferPool.getStats(),
      timestamp: new Date().toISOString()
    }
  });
});

// 힙 스냅샷 생성
router.post('/snapshot', async (req, res) => {
  try {
    const filename = req.body.filename;
    const snapshotPath = await memoryManager.createHeapSnapshot(filename);
    
    res.json({
      success: true,
      data: {
        snapshotPath,
        message: 'Heap snapshot created successfully'
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 강제 가비지 컬렉션
router.post('/gc', (req, res) => {
  if (!global.gc) {
    return res.status(400).json({
      success: false,
      error: 'Garbage collection not exposed. Run with --expose-gc flag.'
    });
  }
  
  const before = process.memoryUsage();
  global.gc();
  const after = process.memoryUsage();
  
  const freed = {
    rss: (before.rss - after.rss) / 1024 / 1024,
    heapUsed: (before.heapUsed - after.heapUsed) / 1024 / 1024,
    heapTotal: (before.heapTotal - after.heapTotal) / 1024 / 1024,
    external: (before.external - after.external) / 1024 / 1024
  };
  
  res.json({
    success: true,
    data: {
      before: {
        rss: before.rss / 1024 / 1024,
        heapUsed: before.heapUsed / 1024 / 1024,
        heapTotal: before.heapTotal / 1024 / 1024,
        external: before.external / 1024 / 1024
      },
      after: {
        rss: after.rss / 1024 / 1024,
        heapUsed: after.heapUsed / 1024 / 1024,
        heapTotal: after.heapTotal / 1024 / 1024,
        external: after.external / 1024 / 1024
      },
      freed,
      message: 'Garbage collection completed'
    }
  });
});

// 메모리 부하 테스트
router.post('/stress', (req, res) => {
  const { size = 10, count = 100 } = req.body;
  const arrays = [];
  
  try {
    for (let i = 0; i < count; i++) {
      arrays.push(new Array(size * 1024 * 1024).fill(i));
    }
    
    const status = memoryManager.getMemoryStatus();
    
    // 배열 정리
    arrays.length = 0;
    
    res.json({
      success: true,
      data: {
        message: `Created ${count} arrays of ${size}MB each`,
        memoryAfter: status,
        totalAllocated: size * count
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 버퍼 풀 테스트
router.post('/buffer-pool/test', (req, res) => {
  const { count = 10 } = req.body;
  const buffers = [];
  
  try {
    // 버퍼 획득
    for (let i = 0; i < count; i++) {
      buffers.push(bufferPool.acquire());
    }
    
    const statsAfterAcquire = bufferPool.getStats();
    
    // 버퍼 반환
    buffers.forEach(buffer => bufferPool.release(buffer));
    
    const statsAfterRelease = bufferPool.getStats();
    
    res.json({
      success: true,
      data: {
        message: `Tested buffer pool with ${count} buffers`,
        statsAfterAcquire,
        statsAfterRelease
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

export default router;