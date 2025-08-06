import { Router } from 'express';
import { APISecurityMiddleware } from '../security/api-security';

const router = Router();

// 보안 헤더 적용
router.use(APISecurityMiddleware.securityHeaders());

// User-Agent 검증
router.use(APISecurityMiddleware.validateUserAgent());

// API 키 인증이 필요한 엔드포인트
router.get('/projects', 
  APISecurityMiddleware.apiKeyAuth(['projects:read']),
  (req, res) => {
    res.json({
      message: 'Projects retrieved successfully',
      user: req.user?.userId,
      scopes: req.user?.scopes
    });
  }
);

// JWT 인증이 필요한 엔드포인트
router.post('/projects',
  APISecurityMiddleware.jwtAuth(['projects:write']),
  (req, res) => {
    res.json({
      message: 'Project created successfully',
      user: req.user?.userId,
      data: req.body
    });
  }
);

// IP 화이트리스트가 적용된 관리자 엔드포인트
router.get('/admin/stats',
  APISecurityMiddleware.ipWhitelist(['127.0.0.1', '::1']),
  APISecurityMiddleware.apiKeyAuth(['admin:all']),
  (req, res) => {
    res.json({
      message: 'Admin statistics',
      timestamp: new Date().toISOString()
    });
  }
);

export default router;