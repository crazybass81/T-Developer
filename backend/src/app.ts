import express from 'express';
import { loggingMiddleware } from './middleware/logging';
import { metricsMiddleware, metricsEndpoint } from './config/metrics';
import { agentMetricsMiddleware } from './middleware/metrics';
import { tracingMiddleware } from './config/tracing';
import { logger } from './config/logger';
import testRoutes from './routes/test';
import monitoringRoutes from './routes/monitoring';
import testAlertRoutes from './routes/test-alerts';
import { apmEndpoints, apmService } from './monitoring/apm';
import { alertManager } from './monitoring/alerting';

const app = express();

app.use(express.json());
app.use(loggingMiddleware);
app.use(metricsMiddleware());
app.use(agentMetricsMiddleware());
app.use(tracingMiddleware());

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 't-developer-backend'
  });
});

app.get('/metrics', metricsEndpoint());

app.use('/test', testRoutes);
app.use('/api/monitoring', monitoringRoutes);
app.use('/test/alerts', testAlertRoutes);

apmEndpoints(app);

// Start APM monitoring
apmService.start(5000);

app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Unhandled error', error, {
    requestId: req.requestId,
    url: req.url,
    method: req.method
  });
  
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.requestId
  });
});

export default app;