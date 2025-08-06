export { AgnoMonitoringIntegration, AgnoMetrics } from './monitoring-integration';

// Mock Agno Agent Pool for development
export class MockAgentPool {
  private stats = {
    available: 5,
    inUse: 3,
    total: 8,
    created: 8,
    destroyed: 0
  };

  getStats() {
    return { ...this.stats };
  }

  simulateActivity() {
    this.stats.inUse = Math.floor(Math.random() * 10) + 1;
    this.stats.available = Math.max(0, this.stats.total - this.stats.inUse);
  }

  async createAgent(): Promise<{ id: string; created: number }> {
    const agent = {
      id: `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      created: Date.now()
    };
    
    this.stats.created++;
    this.stats.total++;
    this.stats.inUse++;
    this.stats.available = Math.max(0, this.stats.total - this.stats.inUse);
    
    return agent;
  }

  async releaseAgent(agentId: string): Promise<void> {
    this.stats.inUse = Math.max(0, this.stats.inUse - 1);
    this.stats.available = Math.max(0, this.stats.total - this.stats.inUse);
  }

  async destroyAgent(agentId: string): Promise<void> {
    this.stats.destroyed++;
    this.stats.total = Math.max(0, this.stats.total - 1);
    this.stats.available = Math.max(0, this.stats.total - this.stats.inUse);
  }
}

// Agno configuration
export const AgnoConfig = {
  performance: {
    instantiation_target_us: 3,
    memory_target_kb: 6.5,
    enable_optimizations: true,
    use_native_extensions: true
  },
  monitoring: {
    enabled: true,
    endpoint: process.env.AGNO_MONITORING_URL || 'https://agno.com/metrics',
    api_key: process.env.AGNO_API_KEY,
    metrics_interval: 30,
    custom_metrics: [
      'agent_instantiation_time',
      'memory_usage_per_agent',
      'total_active_agents'
    ]
  },
  resources: {
    max_agents: 10000,
    max_memory_per_agent_kb: 10,
    agent_timeout_seconds: 300
  }
};