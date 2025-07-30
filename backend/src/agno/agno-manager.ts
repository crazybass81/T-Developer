import { AgnoPerformanceOptimizer } from './performance-optimizer';
import { AgentPool } from './agent-pool';
import { AgnoMonitoringIntegration } from './monitoring-integration';
import { EventEmitter } from 'events';

export class AgnoManager extends EventEmitter {
  private optimizer: AgnoPerformanceOptimizer;
  private agentPool: AgentPool;
  private monitoring: AgnoMonitoringIntegration;
  private initialized = false;

  constructor() {
    super();
    this.optimizer = new AgnoPerformanceOptimizer();
    this.agentPool = new AgentPool({
      minSize: 10,
      maxSize: 100,
      preWarm: true
    });
    this.monitoring = new AgnoMonitoringIntegration();
    
    this.setupEventHandlers();
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    console.log('🚀 Initializing Agno Framework...');
    
    // 성능 최적화
    await this.optimizer.optimize();
    
    // 성능 벤치마크
    const benchmark = await this.optimizer.benchmarkPerformance();
    console.log('📊 Agno Performance:', benchmark);
    
    // 모니터링 벤치마크
    const monitoringBenchmark = await this.monitoring.runPerformanceBenchmark();
    
    this.initialized = true;
    this.emit('initialized', { benchmark, monitoringBenchmark });
    
    console.log('✅ Agno Framework initialized');
  }

  async executeWithAgent(task: any): Promise<any> {
    const startTime = performance.now();
    let agent;
    
    try {
      // 풀에서 에이전트 획득
      agent = await this.agentPool.getAgent();
      
      // 태스크 실행
      const result = await agent.execute(task);
      
      // 성공 메트릭 기록
      const duration = performance.now() - startTime;
      this.monitoring.recordExecution(duration, true);
      
      return {
        ...result,
        agnoMetrics: {
          executionTime: duration,
          agentId: agent.id,
          poolStats: this.agentPool.getStats()
        }
      };
      
    } catch (error) {
      // 실패 메트릭 기록
      const duration = performance.now() - startTime;
      this.monitoring.recordExecution(duration, false);
      throw error;
      
    } finally {
      // 에이전트 반환
      if (agent && agent.poolId) {
        await this.agentPool.releaseAgent(agent.poolId);
      }
    }
  }

  private setupEventHandlers(): void {
    // 에이전트 풀 이벤트
    this.agentPool.on('agentCreated', (event) => {
      console.log(`⚡ Agent created in ${event.duration}ms`);
    });

    this.agentPool.on('cleanup', (event) => {
      console.log(`🧹 Pool cleanup: ${event.removed} agents removed`);
    });

    // 모니터링 이벤트
    this.monitoring.on('metricsCollected', (metrics) => {
      this.monitoring.updatePoolStats(this.agentPool.getStats());
    });

    // 풀 통계 주기적 업데이트
    setInterval(() => {
      this.monitoring.updatePoolStats(this.agentPool.getStats());
    }, 10000); // 10초마다
  }

  getMetrics(): any {
    return {
      agno: this.monitoring.getMetrics(),
      pool: this.agentPool.getStats(),
      performance: {
        initialized: this.initialized,
        uptime: process.uptime()
      }
    };
  }

  async shutdown(): Promise<void> {
    console.log('🛑 Shutting down Agno Framework...');
    
    this.monitoring.stop();
    await this.agentPool.drain();
    
    console.log('✅ Agno Framework shutdown complete');
  }
}