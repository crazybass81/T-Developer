/**
 * API Routes Index
 * Phase 2: Main API router with authentication
 */

import { Router } from 'express';
import { userRoutes } from './user.routes';
import { authRoutes } from './auth.routes';
import { checkDatabaseConnections } from '../../services/database.service';

const router = Router();

// Health check endpoint
router.get('/health', async (req, res) => {
  try {
    const dbStatus = await checkDatabaseConnections();
    
    res.json({
      status: 'healthy',
      version: process.env.npm_package_version || '0.1.0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      services: {
        postgres: dbStatus.postgres ? 'connected' : 'disconnected',
        redis: dbStatus.redis ? 'connected' : 'disconnected',
        dynamodb: dbStatus.dynamodb ? 'connected' : 'disconnected',
      },
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: 'Service unavailable',
      timestamp: new Date().toISOString(),
    });
  }
});

// API info endpoint
router.get('/', (req, res) => {
  res.json({
    message: 'T-Developer API v1',
    phase: 'Phase 2 - Authentication & Security',
    version: '0.2.0',
    endpoints: {
      health: '/api/v1/health',
      auth: '/api/v1/auth',
      users: '/api/v1/users',
    },
    documentation: 'https://api.t-developer.com/docs',
  });
});

// Feature routes
router.use('/auth', authRoutes);
router.use('/users', userRoutes);

export const apiRouter = router;