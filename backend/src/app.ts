import express from 'express';
import { corsOptions, securityHeaders, requestId } from './middleware/security';
import healthRoutes from './api/routes/health.routes';
import { config } from './core/config';
import logger from './config/logger';

const app = express();

// Basic middleware
app.use(express.json());
app.use(corsOptions);
app.use(securityHeaders);
app.use(requestId);

// Routes
app.use('/api', healthRoutes);

// Error handling
app.use((err: any, req: any, res: any, next: any) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = config.server.port;
app.listen(PORT, () => {
  logger.info(`🚀 T-Developer server running on port ${PORT}`);
  logger.info(`Environment: ${config.app.env}`);
});

export default app;