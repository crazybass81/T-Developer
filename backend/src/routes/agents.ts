import express from 'express';
import { APISecurityMiddleware } from '../security/api-security';

const router = express.Router();

// Execute agent (requires agents:execute scope)
router.post('/execute',
  APISecurityMiddleware.apiKeyAuth(['agents:execute']),
  (req, res) => {
    res.json({
      message: 'Agent execution started',
      executionId: `exec_${Date.now()}`,
      agent: req.body.agentName
    });
  }
);

// Monitor agents (requires agents:monitor scope)
router.get('/status',
  APISecurityMiddleware.apiKeyAuth(['agents:monitor']),
  (req, res) => {
    res.json({
      agents: [
        { name: 'nl-input', status: 'idle' },
        { name: 'ui-selection', status: 'running' }
      ]
    });
  }
);

// High-security agent operations (HMAC required)
router.post('/deploy',
  APISecurityMiddleware.hmacAuth(),
  APISecurityMiddleware.apiKeyAuth(['admin:all']),
  (req, res) => {
    res.json({
      message: 'Agent deployed',
      deploymentId: `deploy_${Date.now()}`
    });
  }
);

export default router;