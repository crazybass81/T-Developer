// Task 1.15: 로깅 및 모니터링 - Main exports
export { Logger, logger } from './logger';
export { MetricsCollector, metrics } from './metrics-collector';
export { HealthChecker, healthChecker } from './health-checker';
export { AlertManager, alertManager, HealthAlerter, healthAlerter } from './alerting';

// Integrated monitoring system
import { logger } from './logger';
import { metrics } from './metrics-collector';
import { healthChecker } from './health-checker';
import { alertManager, healthAlerter } from './alerting';

export class MonitoringSystem {
  async initialize(): Promise<void> {
    // Start health monitoring
    setInterval(async () => {
      try {
        const healthStatus = await healthChecker.runChecks();
        
        // Log health status
        await logger.info('Health check completed', { status: healthStatus.status });
        
        // Record metrics
        metrics.recordCount('health.checks.total', Object.keys(healthStatus.checks).length);
        metrics.recordCount('health.checks.healthy', 
          Object.values(healthStatus.checks).filter(c => c.status).length
        );
        
        // Send alerts if needed
        await healthAlerter.checkAndAlert(healthStatus);
        
      } catch (error) {
        await logger.error('Health check failed', { error: error instanceof Error ? error.message : 'Unknown error' });
        await alertManager.critical('Health Check System Failed', 'Unable to perform health checks');
      }
    }, 30000); // Every 30 seconds

    await logger.info('Monitoring system initialized');
  }

  async recordAgentExecution(agentName: string, duration: number, success: boolean): Promise<void> {
    // Log execution
    await logger.info('Agent execution completed', {
      agentName,
      duration,
      success
    });

    // Record metrics
    metrics.recordDuration('agent.execution.duration', duration, { agentName });
    metrics.recordCount('agent.execution.total', 1, { agentName });
    metrics.recordCount(`agent.execution.${success ? 'success' : 'failure'}`, 1, { agentName });

    // Alert on failures
    if (!success) {
      await alertManager.warning('Agent Execution Failed', `Agent ${agentName} failed to execute`, {
        agentName,
        duration
      });
    }
  }

  async recordSystemMetrics(): Promise<void> {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    // Memory metrics
    metrics.recordMemory('system.memory.heap_used', memUsage.heapUsed);
    metrics.recordMemory('system.memory.heap_total', memUsage.heapTotal);
    metrics.recordMemory('system.memory.rss', memUsage.rss);

    // CPU metrics (convert microseconds to seconds)
    metrics.recordDuration('system.cpu.user', cpuUsage.user / 1000000);
    metrics.recordDuration('system.cpu.system', cpuUsage.system / 1000000);
  }
}

// Global monitoring system
export const monitoring = new MonitoringSystem();