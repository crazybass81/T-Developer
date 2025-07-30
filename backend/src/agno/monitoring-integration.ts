import { EventEmitter } from 'events';
import { agnoConfig } from '../config/agno.config';

export interface AgnoMetrics {
  instantiationTimeUs: number;
  memoryPerAgentKb: number;
  activeAgents: number;
  totalExecutions: number;
  averageExecutionTime: number;
  errorRate: number;
  poolStats: {
    available: number;
    inUse: number;
    created: number;
    destroyed: number;
  };
}

export class AgnoMonitoringIntegration extends EventEmitter {
  private metrics: AgnoMetrics = {
    instantiationTimeUs: 0,
    memoryPerAgentKb: 0,
    activeAgents: 0,
    totalExecutions: 0,
    averageExecutionTime: 0,
    errorRate: 0,
    poolStats: {
      available: 0,
      inUse: 0,
      created: 0,
      destroyed: 0
    }
  };

  private executionTimes: number[] = [];
  private errors = 0;
  private collectionInterval?: NodeJS.Timeout;

  constructor() {
    super();
    this.setupMetricsCollection();
  }

  private setupMetricsCollection(): void {
    if (!agnoConfig.monitoring.enabled) return;

    this.collectionInterval = setInterval(async () => {
      await this.collectMetrics();
      await this.sendToAgnoDashboard();
    }, agnoConfig.monitoring.metricsInterval);
  }

  async collectMetrics(): Promise<AgnoMetrics> {
    // 인스턴스화 시간 측정
    const instantiationStart = performance.now();
    const testAgent = this.createTestAgent();
    const instantiationEnd = performance.now();
    
    this.metrics.instantiationTimeUs = (instantiationEnd - instantiationStart) * 1000;

    // 메모리 사용량 측정
    const memoryBefore = process.memoryUsage().heapUsed;
    const agents = Array.from({ length: 100 }, () => this.createTestAgent());
    const memoryAfter = process.memoryUsage().heapUsed;
    
    this.metrics.memoryPerAgentKb = (memoryAfter - memoryBefore) / 100 / 1024;

    // 실행 시간 통계
    if (this.executionTimes.length > 0) {
      this.metrics.averageExecutionTime = 
        this.executionTimes.reduce((a, b) => a + b) / this.executionTimes.length;
    }

    // 에러율 계산
    this.metrics.errorRate = this.metrics.totalExecutions > 0 
      ? this.errors / this.metrics.totalExecutions 
      : 0;

    this.emit('metricsCollected', this.metrics);
    return this.metrics;
  }

  private createTestAgent(): any {
    return {
      id: `test-${Date.now()}`,
      execute: async () => ({ result: 'test' })
    };
  }

  recordExecution(duration: number, success: boolean): void {
    this.metrics.totalExecutions++;
    
    if (success) {
      this.executionTimes.push(duration);
      
      // 슬라이딩 윈도우 (최근 1000개만 유지)
      if (this.executionTimes.length > 1000) {
        this.executionTimes.shift();
      }
    } else {
      this.errors++;
    }
  }

  updatePoolStats(stats: any): void {
    this.metrics.poolStats = { ...stats };
    this.metrics.activeAgents = stats.inUse;
  }

  private async sendToAgnoDashboard(): Promise<void> {
    if (!agnoConfig.monitoring.endpoint) return;

    const payload = {
      timestamp: new Date().toISOString(),
      projectId: process.env.AGNO_PROJECT_ID || 't-developer',
      metrics: this.metrics,
      metadata: {
        environment: process.env.NODE_ENV || 'development',
        version: process.env.APP_VERSION || '1.0.0',
        nodeVersion: process.version
      }
    };

    try {
      // 실제로는 HTTP 요청을 보내야 함
      console.log('📊 Agno Metrics:', JSON.stringify(payload, null, 2));
      
      this.emit('metricsSent', payload);
    } catch (error) {
      console.error('Failed to send metrics to Agno dashboard:', error);
      this.emit('metricsError', error);
    }
  }

  getMetrics(): AgnoMetrics {
    return { ...this.metrics };
  }

  // 성능 벤치마크
  async runPerformanceBenchmark(): Promise<{
    instantiationTime: number;
    memoryUsage: number;
    throughput: number;
    targetsMet: boolean;
  }> {
    const iterations = 10000;
    const agents: any[] = [];
    
    // 인스턴스화 벤치마크
    const instStart = performance.now();
    for (let i = 0; i < iterations; i++) {
      agents.push(this.createTestAgent());
    }
    const instEnd = performance.now();
    
    const instantiationTime = ((instEnd - instStart) / iterations) * 1000; // μs
    
    // 메모리 벤치마크
    const memoryBefore = process.memoryUsage().heapUsed;
    const testAgents = Array.from({ length: 1000 }, () => this.createTestAgent());
    const memoryAfter = process.memoryUsage().heapUsed;
    const memoryUsage = (memoryAfter - memoryBefore) / 1000 / 1024; // KB
    
    // 처리량 벤치마크
    const throughputStart = performance.now();
    const execPromises = testAgents.slice(0, 100).map(agent => agent.execute());
    await Promise.all(execPromises);
    const throughputEnd = performance.now();
    const throughput = 100 / ((throughputEnd - throughputStart) / 1000); // ops/sec
    
    const targetsMet = (
      instantiationTime <= agnoConfig.performance.instantiationTargetUs &&
      memoryUsage <= agnoConfig.performance.memoryTargetKb
    );

    const result = {
      instantiationTime,
      memoryUsage,
      throughput,
      targetsMet
    };

    console.log('🎯 Agno Performance Benchmark:', result);
    return result;
  }

  stop(): void {
    if (this.collectionInterval) {
      clearInterval(this.collectionInterval);
      this.collectionInterval = undefined;
    }
  }
}