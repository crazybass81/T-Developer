import { AgentRegistry } from '../orchestration/agent-registry';

interface HealthMetrics {
  active_agents: number;
  queued_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  avg_response_time: number;
  memory_usage: number;
  uptime: number;
}

interface AgentHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  last_check: string;
  response_time?: number;
  error?: string;
}

export class OrchestratorHealthCheck {
  private orchestrator: any;
  private metrics: HealthMetrics;
  private startTime: Date;
  private responseTimes: number[] = [];

  constructor(orchestrator: any) {
    this.orchestrator = orchestrator;
    this.startTime = new Date();
    this.metrics = {
      active_agents: 0,
      queued_tasks: 0,
      completed_tasks: 0,
      failed_tasks: 0,
      avg_response_time: 0,
      memory_usage: 0,
      uptime: 0
    };
  }

  async checkHealth(): Promise<{
    status: 'healthy' | 'unhealthy';
    timestamp: string;
    metrics: HealthMetrics;
    agents: AgentHealth[];
  }> {
    const metrics = await this.collectMetrics();
    const agents = await this.checkAgentHealth();
    
    return {
      status: this.isHealthy(metrics, agents) ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      metrics,
      agents
    };
  }

  async collectMetrics(): Promise<HealthMetrics> {
    const memUsage = process.memoryUsage();
    
    this.metrics = {
      active_agents: this.orchestrator?.agent_registry?.listAgents()?.length || 0,
      queued_tasks: this.orchestrator?.task_queue?.size || 0,
      completed_tasks: this.orchestrator?.completed_count || 0,
      failed_tasks: this.orchestrator?.failed_count || 0,
      avg_response_time: this.calculateAvgResponseTime(),
      memory_usage: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
      uptime: Math.round((Date.now() - this.startTime.getTime()) / 1000) // seconds
    };

    return this.metrics;
  }

  async checkAgentHealth(): Promise<AgentHealth[]> {
    if (!this.orchestrator?.agent_registry) {
      return [];
    }

    const agents = await this.orchestrator.agent_registry.listAgents();
    const healthChecks = await Promise.allSettled(
      agents.map(agent => this.checkSingleAgent(agent))
    );

    return healthChecks.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      }
      return {
        name: agents[index].name,
        status: 'unhealthy' as const,
        last_check: new Date().toISOString(),
        error: result.reason?.message || 'Health check failed'
      };
    });
  }

  private async checkSingleAgent(agent: any): Promise<AgentHealth> {
    const startTime = Date.now();
    
    try {
      // Simple ping test
      const instance = await this.orchestrator.agent_registry.getAgent(agent.name);
      const responseTime = Date.now() - startTime;
      
      return {
        name: agent.name,
        status: 'healthy',
        last_check: new Date().toISOString(),
        response_time: responseTime
      };
    } catch (error) {
      return {
        name: agent.name,
        status: 'unhealthy',
        last_check: new Date().toISOString(),
        error: error.message
      };
    }
  }

  private isHealthy(metrics: HealthMetrics, agents: AgentHealth[]): boolean {
    // Health criteria
    const memoryThreshold = 1024; // 1GB
    const responseTimeThreshold = 5000; // 5s
    const unhealthyAgentThreshold = 0.2; // 20%

    if (metrics.memory_usage > memoryThreshold) return false;
    if (metrics.avg_response_time > responseTimeThreshold) return false;

    const unhealthyAgents = agents.filter(a => a.status === 'unhealthy').length;
    const unhealthyRatio = agents.length > 0 ? unhealthyAgents / agents.length : 0;
    
    return unhealthyRatio <= unhealthyAgentThreshold;
  }

  private calculateAvgResponseTime(): number {
    if (this.responseTimes.length === 0) return 0;
    
    const sum = this.responseTimes.reduce((a, b) => a + b, 0);
    return Math.round(sum / this.responseTimes.length);
  }

  recordResponseTime(time: number): void {
    this.responseTimes.push(time);
    // Keep only last 100 measurements
    if (this.responseTimes.length > 100) {
      this.responseTimes.shift();
    }
  }

  incrementCompleted(): void {
    if (this.orchestrator) {
      this.orchestrator.completed_count = (this.orchestrator.completed_count || 0) + 1;
    }
  }

  incrementFailed(): void {
    if (this.orchestrator) {
      this.orchestrator.failed_count = (this.orchestrator.failed_count || 0) + 1;
    }
  }
}