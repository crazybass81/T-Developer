// backend/src/api/routes/health.routes.ts
import { Router } from 'express';
import { HealthController } from '../controllers/health.controller';

const router = Router();
const healthController = new HealthController();

router.get('/health', healthController.getHealth.bind(healthController));
router.get('/ready', healthController.getReadiness.bind(healthController));

export default router;
