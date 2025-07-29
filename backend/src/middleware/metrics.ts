import { Request, Response, NextFunction } from 'express';
import { MetricsHelper } from '../config/metrics';
import { logger } from '../config/logger';

export function agentMetricsMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const originalSend = res.send;
    
    res.send = function(data) {
      // Extract agent execution data from response
      if (req.path.includes('/agents/') && data) {
        try {
          const responseData = typeof data === 'string' ? JSON.parse(data) : data;
          
          if (responseData.agentName && responseData.duration) {
            MetricsHelper.recordAgentExecution(
              responseData.agentName,
              responseData.duration / 1000, // Convert to seconds
              responseData.success ? 'success' : 'failure',
              responseData.tokensUsed,
              responseData.model
            );
          }
        } catch (error) {
          logger.warn('Failed to extract agent metrics', { error: error.message });
        }
      }
      
      return originalSend.call(this, data);
    };
    
    next();
  };
}

export function projectMetricsCollector() {
  // Update active projects count every 30 seconds
  setInterval(async () => {
    try {
      // This would typically query your database
      // For now, using mock data
      MetricsHelper.updateActiveProjects('analyzing', 5);
      MetricsHelper.updateActiveProjects('building', 3);
      MetricsHelper.updateActiveProjects('completed', 12);
    } catch (error) {
      logger.error('Failed to update project metrics', error);
    }
  }, 30000);
}