import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { config } from './config/environment';
import { logger } from './config/logger';
import { AgentOrchestrator } from './orchestration/agent-orchestrator';
import { setupRoutes } from './routes';
import { errorHandler } from './middleware/error-handler';

async function bootstrap() {
  const app = express();

  // Security middleware
  app.use(helmet());
  app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true
  }));

  // Body parsing
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true }));

  // Health check
  app.get('/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0'
    });
  });

  // Initialize Agent Orchestrator
  const orchestrator = new AgentOrchestrator();
  await orchestrator.initialize();

  // Setup routes
  setupRoutes(app, orchestrator);

  // Error handling
  app.use(errorHandler);

  const port = config.port || 3000;
  app.listen(port, () => {
    logger.info(`T-Developer backend running on port ${port}`);
  });
}

bootstrap().catch(error => {
  logger.error('Failed to start application:', error);
  process.exit(1);
});