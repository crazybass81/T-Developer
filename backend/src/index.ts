/**
 * T-Developer Backend Entry Point
 * Phase 0: Project Initialization
 */

import express, { Express, Request, Response } from 'express';
import { config, validateConfig } from './config/config';
import { logger } from './utils/logger';
import { errorHandler } from './middlewares/errorHandler';
import { requestLogger } from './middlewares/requestLogger';
import { setupSecurity } from './middlewares/security';
import { apiRouter } from './api/routes';
import { initializeDatabases, closeDatabaseConnections } from './services/database.service';

const app: Express = express();
const PORT = config.port || 3000;

// Validate configuration
validateConfig();

// Security middleware
setupSecurity(app);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Root endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({
    message: 'T-Developer Backend API',
    version: '0.2.0',
    phase: 'Phase 2 - Authentication & Security Complete',
    docs: '/api/v1',
  });
});

// API routes
app.use('/api/v1', apiRouter);

// 404 handler
app.use('*', (req: Request, res: Response) => {
  res.status(404).json({
    status: 'error',
    message: `Route ${req.originalUrl} not found`,
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// Initialize and start server
const startServer = async () => {
  try {
    // Initialize databases
    await initializeDatabases();
    
    // Start HTTP server
    const server = app.listen(PORT, () => {
      logger.info(`🚀 T-Developer Backend Server running on port ${PORT}`);
      logger.info(`📍 Environment: ${config.env}`);
      logger.info(`🔧 Phase 2: Authentication & Security Complete`);
    });

    // Graceful shutdown
    const shutdown = async (signal: string) => {
      logger.info(`${signal} signal received: closing HTTP server`);
      
      server.close(async () => {
        logger.info('HTTP server closed');
        await closeDatabaseConnections();
        process.exit(0);
      });
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));
    
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();

export default app;