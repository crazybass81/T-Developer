import express from 'express';
import { 
  AdvancedDebugger, 
  ExecutionTracer, 
  EnhancedConsole,
  createDebugProxy,
  debuggingMiddleware 
} from '../dev/debugging-tools';

const router = express.Router();
const tracer = new ExecutionTracer();
const advancedDebugger = new AdvancedDebugger();

// 향상된 콘솔 설치
const enhancedConsole = new EnhancedConsole();
enhancedConsole.install();

// 디버깅 미들웨어 적용
router.use(debuggingMiddleware());

// 데모 클래스
class DemoService {
  @tracer.trace({ log: true, logArgs: true, logResult: true })
  async processData(data: any) {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { processed: true, data };
  }

  async slowOperation() {
    await new Promise(resolve => setTimeout(resolve, 500));
    return 'completed';
  }
}

// 프로파일링 데모
router.get('/profile', async (req, res) => {
  try {
    await advancedDebugger.startProfiling('demo-profile');
    
    const service = new DemoService();
    const results = [];
    
    for (let i = 0; i < 10; i++) {
      results.push(await service.slowOperation());
    }
    
    const profile = await advancedDebugger.stopProfiling('demo-profile');
    
    res.json({
      message: 'Profiling completed',
      results,
      profile: {
        totalTime: profile.totalTime,
        hotspots: profile.hotspots.slice(0, 5)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 실행 추적 데모
router.post('/trace', async (req, res) => {
  try {
    const service = new DemoService();
    
    const result = await tracer.traceExecution(
      'demo-operation',
      async () => {
        return await service.processData(req.body);
      },
      { userId: 'demo-user' }
    );
    
    res.json({
      message: 'Tracing completed',
      result
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 디버그 프록시 데모
router.get('/proxy', (req, res) => {
  const data = { count: 0, items: [] };
  const proxiedData = createDebugProxy(data, 'DemoData');
  
  proxiedData.count = 5;
  proxiedData.items.push('item1', 'item2');
  
  res.json({
    message: 'Debug proxy demo completed',
    data: proxiedData
  });
});

// 메모리 스냅샷 데모
router.get('/snapshot', async (req, res) => {
  try {
    const filename = await advancedDebugger.takeHeapSnapshot('demo');
    
    res.json({
      message: 'Heap snapshot taken',
      filename
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;