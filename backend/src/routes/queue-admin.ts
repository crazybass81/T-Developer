import { Router } from 'express';
import { QueueManager } from '../performance/job-queue';

export function createQueueAdminRoutes(queueManager: QueueManager): Router {
  const router = Router();
  
  // 큐 상태 조회
  router.get('/queues/:name/stats', async (req, res) => {
    try {
      const stats = await queueManager.getQueueStats(req.params.name);
      res.json(stats);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });
  
  // 작업 상태 조회
  router.get('/queues/:name/jobs/:id', async (req, res) => {
    try {
      const status = await queueManager.getJobStatus(req.params.name, req.params.id);
      res.json(status);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });
  
  return router;
}