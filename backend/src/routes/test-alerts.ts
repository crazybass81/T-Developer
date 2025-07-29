import { Router } from 'express';
import { alertManager, alertTemplates } from '../monitoring/alerting';

const router = Router();

router.post('/cpu-alert', async (req, res) => {
  const usage = req.body.usage || 95;
  await alertManager.sendAlert(alertTemplates.highCPU(usage));
  res.json({ message: `CPU alert sent for ${usage}% usage` });
});

router.post('/memory-alert', async (req, res) => {
  const usage = req.body.usage || 98;
  await alertManager.sendAlert(alertTemplates.highMemory(usage));
  res.json({ message: `Memory alert sent for ${usage}% usage` });
});

router.post('/agent-failure', async (req, res) => {
  const agentName = req.body.agentName || 'test-agent';
  const error = req.body.error || 'Connection timeout';
  await alertManager.sendAlert(alertTemplates.agentFailure(agentName, error));
  res.json({ message: `Agent failure alert sent for ${agentName}` });
});

export default router;