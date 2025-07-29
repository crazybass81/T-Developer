import express from 'express';
import { APISecurityMiddleware, DynamicRateLimiter } from '../security/api-security';

const router = express.Router();

// Apply security middleware globally
router.use(APISecurityMiddleware.securityHeaders());
router.use(DynamicRateLimiter.middleware());

// Public endpoint (no auth required)
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Protected endpoint with API key auth
router.get('/projects', 
  APISecurityMiddleware.apiKeyAuth(['projects:read']),
  (req, res) => {
    res.json({ 
      projects: [],
      user: req.user?.id 
    });
  }
);

// High-security endpoint with HMAC auth
router.post('/projects',
  APISecurityMiddleware.hmacAuth(),
  APISecurityMiddleware.apiKeyAuth(['projects:write']),
  (req, res) => {
    res.json({ 
      message: 'Project created',
      projectId: 'proj_' + Date.now()
    });
  }
);

// Admin-only endpoint
router.delete('/projects/:id',
  APISecurityMiddleware.apiKeyAuth(['admin:all']),
  APISecurityMiddleware.ipWhitelist(['127.0.0.1', '10.0.0.0/8']),
  (req, res) => {
    res.json({ 
      message: 'Project deleted',
      projectId: req.params.id
    });
  }
);

export default router;