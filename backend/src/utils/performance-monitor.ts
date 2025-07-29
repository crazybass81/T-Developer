import { MetricsHelper } from '../config/metrics';
import { logger } from '../config/logger';

export class PerformanceMonitor {
  private static timers: Map<string, number> = new Map();
  
  static startTimer(id: string): void {
    this.timers.set(id, Date.now());
  }
  
  static endTimer(id: string): number {
    const start = this.timers.get(id);
    if (!start) {
      logger.warn(`Timer ${id} not found`);
      return 0;
    }
    
    const duration = Date.now() - start;
    this.timers.delete(id);
    return duration;
  }
  
  static measureAgentExecution<T>(
    agentName: string,
    fn: () => Promise<T>,
    model?: string
  ): Promise<T> {
    const timerId = `agent_${agentName}_${Date.now()}`;
    this.startTimer(timerId);
    
    return fn()
      .then(result => {
        const duration = this.endTimer(timerId);
        MetricsHelper.recordAgentExecution(agentName, duration / 1000, 'success', undefined, model);
        return result;
      })
      .catch(error => {
        const duration = this.endTimer(timerId);
        MetricsHelper.recordAgentExecution(agentName, duration / 1000, 'failure', undefined, model);
        throw error;
      });
  }
  
  static updateCacheMetrics(cacheType: string, hits: number, total: number): void {
    const hitRate = total > 0 ? (hits / total) * 100 : 0;
    MetricsHelper.updateCacheHitRate(cacheType, hitRate);
  }
}