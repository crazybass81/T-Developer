// backend/src/api/controllers/health.controller.ts
import { Request, Response } from 'express';
import { config } from '../../core/config';

export class HealthController {
  async getHealth(req: Request, res: Response): Promise<void> {
    const health = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: config.app.version,
      environment: config.app.env,
      services: {
        api: 'running',
        database: 'pending',
        cache: 'pending'
      }
    };

    res.json(health);
  }

  async getReadiness(req: Request, res: Response): Promise<void> {
    // TODO: Add actual readiness checks
    res.json({ ready: true });
  }
}
