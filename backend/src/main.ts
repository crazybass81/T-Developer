import dotenv from 'dotenv';
dotenv.config({ path: '../.env' });
import express from 'express';
import { initializeBedrockRuntime } from './bedrock';
import { initializeSessionSystem } from './session';

async function bootstrap() {
  const app = express();
  const port = process.env.PORT || 3000;
  
  // Initialize Bedrock runtime
  const runtimeManager = await initializeBedrockRuntime();
  
  // Initialize session system
  const { sessionMiddleware } = initializeSessionSystem();
  
  // Basic middleware
  app.use(express.json());
  
  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      services: {
        bedrock: 'running',
        agentcore: 'initialized'
      }
    });
  });
  
  // Session endpoints
  app.post('/api/sessions', sessionMiddleware.createSessionEndpoint.bind(sessionMiddleware));
  app.delete('/api/sessions/:sessionId', sessionMiddleware.terminateSessionEndpoint.bind(sessionMiddleware));
  app.get('/api/sessions/metrics', sessionMiddleware.getSessionMetrics.bind(sessionMiddleware));
  
  // Test endpoint for agent execution
  app.post('/api/execute', sessionMiddleware.middleware(), async (req, res) => {
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