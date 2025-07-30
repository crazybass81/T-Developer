import dotenv from 'dotenv';
dotenv.config({ path: '../.env' });
import express from 'express';
import cors from 'cors';
import { initializeBedrockRuntime } from './bedrock';
import { initializeSessionSystem } from './session';
import { SecurityMiddleware } from './security/security-middleware';
import authRoutes from './security/auth-routes';
import { initializeDynamoDB } from './data';
import { initializeDataRoutes } from './data/dynamodb/data-routes';
import { initializeCaching } from './cache';
import { initializeCacheRoutes } from './cache/cache-routes';

async function bootstrap() {
  const app = express();
  const port = process.env.PORT || 3000;
  
  // Initialize systems
  const runtimeManager = await initializeBedrockRuntime();
  const { sessionMiddleware } = initializeSessionSystem();
  const security = new SecurityMiddleware();
  const { singleTable, queryOptimizer, transactionManager } = initializeDynamoDB();
  const { cacheManager, cacheMiddleware } = initializeCaching();
  
  // Security middleware
  app.use(security.securityHeaders());
  app.use(security.rateLimiter());
  app.use(cors(security.corsOptions()));
  app.use(express.json());
  app.use(security.validateInput());
  app.use(security.requestLogger());
  
  // Authentication routes
  app.use('/auth', authRoutes);
  
  // Data routes
  const dataRoutes = initializeDataRoutes(singleTable, queryOptimizer, transactionManager);
  app.use('/api/data', dataRoutes);
  
  // Cache routes
  const cacheRoutes = initializeCacheRoutes(cacheManager);
  app.use('/api/cache', cacheRoutes);
  
  // Add cache middleware to data routes
  app.use('/api/data', cacheMiddleware.apiCache(300));
  
  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      services: {
        bedrock: 'running',
        agentcore: 'initialized',
        security: 'enabled',
        authentication: 'active',
        dynamodb: 'connected',
        cache: 'active'
      }
    });
  });
  
  // Session endpoints
  app.post('/api/sessions', sessionMiddleware.createSessionEndpoint.bind(sessionMiddleware));
  app.delete('/api/sessions/:sessionId', sessionMiddleware.terminateSessionEndpoint.bind(sessionMiddleware));
  app.get('/api/sessions/metrics', sessionMiddleware.getSessionMetrics.bind(sessionMiddleware));
  
  // Test endpoint for agent execution (protected)
  app.post('/api/execute', security.authenticate(), security.authorize(['agent:execute']), sessionMiddleware.middleware(), async (req, res) => {
    try {
      // Use the session ID from our session system
      const result = await runtimeManager.executeInSession(req.sessionId!, req.body);
      
      res.json({
        success: true,
        sessionId: req.sessionId,
        result
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });
  
  app.listen(port, () => {
    console.log(`🚀 T-Developer backend running on port ${port}`);
  });
}

bootstrap().catch(console.error);