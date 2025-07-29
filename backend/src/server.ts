import './config/tracing'; // Initialize tracing first
import app from './app';
import { logger } from './config/logger';

const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  logger.info(`T-Developer backend server started`, {
    port: PORT,
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});