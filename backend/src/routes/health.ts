import { Router } from 'express';
import { OrchestratorHealthCheck } from '../monitoring/orchestrator-health-check';

const router = Router();

// Global health check instance (will be initialized by orchestrator)
let healthChecker: OrchestratorHealthCheck | null = null;

export function initializeHealthCheck(orchestrator: any): void {
  healthChecker = new OrchestratorHealthCheck(orchestrator);
}

// Health check endpoint
router.get('/health', async (req, res) => {
  try {
    if (!healthChecker) {
      return res.status(503).json({
        status: 'unhealthy',
        error: 'Health checker not initialized',
        timestamp: new Date().toISOString()
      });
    }

    const health = await healthChecker.checkHealth();
    const statusCode = health.status === 'healthy' ? 200 : 503;
    
    res.status(statusCode).json(health);
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Metrics endpoint
router.get('/metrics', async (req, res) => {
  try {
    if (!healthChecker) {
      return res.status(503).json({ error: 'Health checker not initialized' });
    }

    const metrics = await healthChecker.collectMetrics();
    res.json(metrics);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Agent health endpoint
router.get('/agents/health', async (req, res) => {
  try {
    if (!healthChecker) {
      return res.status(503).json({ error: 'Health checker not initialized' });
    }

    const agents = await healthChecker.checkAgentHealth();
    res.json({ agents });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export { router as healthRouter, healthChecker };