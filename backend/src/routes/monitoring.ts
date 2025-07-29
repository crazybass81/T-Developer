import { Router } from 'express';
import { alertManager, alertTemplates } from '../monitoring/alerting';

const router = Router();

router.get('/alerts', (req, res) => {
  const limit = parseInt(req.query.limit as string) || 20;
  const alerts = alertManager.getRecentAlerts(limit);
  res.json(alerts);
});

router.get('/alerts/critical', (req, res) => {
  const criticalAlerts = alertManager.getCriticalAlerts();
  res.json(criticalAlerts);
});

export default router;