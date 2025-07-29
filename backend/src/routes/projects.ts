import express from 'express';
import { APISecurityMiddleware } from '../security/api-security';

const router = express.Router();

// All routes require API key with projects:read scope
router.use(APISecurityMiddleware.apiKeyAuth(['projects:read']));

// GET /api/projects
router.get('/', (req, res) => {
  res.json({
    projects: [
      { id: 'proj_1', name: 'Sample Project', status: 'active' }
    ],
    user: req.user?.id
  });
});

// POST /api/projects (requires write scope)
router.post('/', 
  APISecurityMiddleware.apiKeyAuth(['projects:write']),
  (req, res) => {
    res.json({
      message: 'Project created',
      projectId: `proj_${Date.now()}`,
      data: req.body
    });
  }
);

// DELETE /api/projects/:id (requires admin scope)
router.delete('/:id',
  APISecurityMiddleware.apiKeyAuth(['admin:all']),
  (req, res) => {
    res.json({
      message: 'Project deleted',
      projectId: req.params.id
    });
  }
);

export default router;